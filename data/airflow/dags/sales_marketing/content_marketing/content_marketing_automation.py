"""
DAG de Automatización de Marketing de Contenido
=================================================
Orquesta todo el flujo:
1. Conversión de artículos a múltiples formatos
2. Programación de publicaciones
3. Publicación automática
4. Tracking de engagement
5. Análisis de performance
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import logging
import json
import sys
import os

# Agregar plugins al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'plugins'))

from content_converter import ContentConverter, ContentFormat
from social_media_publisher import SocialMediaPublisher, SocialPlatform
from engagement_tracker import EngagementTracker
from content_scheduler import ContentScheduler

logger = logging.getLogger(__name__)

# Configuración por defecto
default_args = {
    'owner': 'content-marketing',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# DAG principal
dag = DAG(
    'content_marketing_automation',
    default_args=default_args,
    description='Automatización completa de marketing de contenido',
    schedule_interval='0 * * * *',  # Cada hora
    start_date=days_ago(1),
    catchup=False,
    tags=['content', 'marketing', 'social-media', 'automation'],
)


def get_db_connection():
    """Obtiene conexión a base de datos."""
    import psycopg2
    from airflow.hooks.base import BaseHook
    
    try:
        conn = BaseHook.get_connection('postgres_default')
        return psycopg2.connect(
            host=conn.host,
            port=conn.port,
            database=conn.schema,
            user=conn.login,
            password=conn.password
        )
    except Exception as e:
        logger.error(f"Error obteniendo conexión a BD: {e}")
        return None


def convert_new_articles(**context):
    """Convierte artículos nuevos a múltiples formatos."""
    db = get_db_connection()
    if not db:
        logger.error("No se pudo conectar a BD")
        return
    
    converter = ContentConverter(db)
    cursor = db.cursor()
    
    try:
        # Obtener artículos nuevos sin versiones
        cursor.execute("""
            SELECT article_id, title, content, source_url, author, featured_image_url, tags
            FROM content_articles
            WHERE status = 'published'
            AND NOT EXISTS (
                SELECT 1 FROM content_versions
                WHERE content_versions.article_id = content_articles.article_id
            )
            ORDER BY published_at DESC
            LIMIT 10
        """)
        
        articles = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        converted_count = 0
        
        for article_row in articles:
            article = dict(zip(columns, article_row))
            
            try:
                # Convertir a múltiples formatos
                versions = converter.convert_article(
                    article_id=article['article_id'],
                    title=article['title'],
                    content=article['content'],
                    formats=[ContentFormat.TWITTER, ContentFormat.LINKEDIN, ContentFormat.NEWSLETTER],
                    url=article.get('source_url'),
                    author=article.get('author'),
                    featured_image=article.get('featured_image_url'),
                    tags=article.get('tags') or []
                )
                
                # Guardar versiones
                saved_ids = converter.save_versions(versions)
                converted_count += len(saved_ids)
                
                logger.info(f"Artículo {article['article_id']} convertido: {len(saved_ids)} versiones")
                
            except Exception as e:
                logger.error(f"Error convirtiendo artículo {article['article_id']}: {e}")
                continue
        
        cursor.close()
        db.close()
        
        logger.info(f"Total de artículos convertidos: {converted_count}")
        
    except Exception as e:
        logger.error(f"Error en conversión: {e}")
        if db:
            db.close()


def schedule_pending_versions(**context):
    """Programa versiones pendientes de aprobación."""
    db = get_db_connection()
    if not db:
        logger.error("No se pudo conectar a BD")
        return
    
    scheduler = ContentScheduler(db)
    cursor = db.cursor()
    
    try:
        # Obtener versiones aprobadas sin programar
        cursor.execute("""
            SELECT v.id, v.article_id, v.platform, v.version_type
            FROM content_versions v
            WHERE v.status = 'approved'
            AND NOT EXISTS (
                SELECT 1 FROM content_scheduled_posts sp
                WHERE sp.version_id = v.id
                AND sp.status NOT IN ('failed', 'cancelled')
            )
            ORDER BY v.created_at DESC
            LIMIT 20
        """)
        
        versions = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        scheduled_count = 0
        
        for version_row in versions:
            version = dict(zip(columns, version_row))
            
            try:
                # Obtener account_id por defecto
                cursor.execute("""
                    SELECT account_id FROM content_platform_config
                    WHERE platform = %s AND is_active = TRUE
                    LIMIT 1
                """, (version['platform'],))
                
                account_result = cursor.fetchone()
                account_id = account_result[0] if account_result else None
                
                # Programar post
                post_id = scheduler.schedule_post(
                    article_id=version['article_id'],
                    version_id=version['id'],
                    platform=version['platform'],
                    account_id=account_id
                )
                
                if post_id:
                    scheduled_count += 1
                    logger.info(f"Versión {version['id']} programada: {post_id}")
                
            except Exception as e:
                logger.error(f"Error programando versión {version['id']}: {e}")
                continue
        
        cursor.close()
        db.close()
        
        logger.info(f"Total de versiones programadas: {scheduled_count}")
        
    except Exception as e:
        logger.error(f"Error en programación: {e}")
        if db:
            db.close()


def publish_scheduled_posts(**context):
    """Publica posts programados."""
    db = get_db_connection()
    if not db:
        logger.error("No se pudo conectar a BD")
        return
    
    publisher = SocialMediaPublisher(db)
    scheduler = ContentScheduler(db)
    
    try:
        # Obtener posts pendientes
        pending_posts = scheduler.get_pending_posts(limit=50)
        
        published_count = 0
        failed_count = 0
        
        for post in pending_posts:
            try:
                # Actualizar estado a "publishing"
                scheduler.update_post_status(post['post_id'], 'publishing')
                
                # Publicar según plataforma
                platform = post['platform']
                result = None
                
                if platform == 'twitter':
                    result = publisher.publish_to_twitter(
                        content=post['content'],
                        media_urls=post.get('media_urls') or [],
                        account_id=post.get('account_id')
                    )
                elif platform == 'linkedin':
                    result = publisher.publish_to_linkedin(
                        content=post['content'],
                        media_urls=post.get('media_urls') or [],
                        account_id=post.get('account_id')
                    )
                elif platform == 'facebook':
                    result = publisher.publish_to_facebook(
                        content=post['content'],
                        media_urls=post.get('media_urls') or [],
                        account_id=post.get('account_id')
                    )
                
                if result and result.success:
                    # Guardar resultado
                    publisher.save_published_post(
                        post['post_id'],
                        result,
                        post.get('article_id'),
                        post.get('version_id')
                    )
                    published_count += 1
                    logger.info(f"Post {post['post_id']} publicado: {result.post_id}")
                else:
                    scheduler.update_post_status(
                        post['post_id'],
                        'failed',
                        result.error_message if result else "Error desconocido"
                    )
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Error publicando post {post.get('post_id')}: {e}")
                scheduler.update_post_status(post['post_id'], 'failed', str(e))
                failed_count += 1
        
        db.close()
        
        logger.info(f"Publicados: {published_count}, Fallidos: {failed_count}")
        
    except Exception as e:
        logger.error(f"Error en publicación: {e}")
        if db:
            db.close()


def track_engagement(**context):
    """Rastrea engagement de posts publicados."""
    db = get_db_connection()
    if not db:
        logger.error("No se pudo conectar a BD")
        return
    
    tracker = EngagementTracker(db)
    
    try:
        stats = tracker.track_all_pending_posts()
        
        logger.info(f"Tracking completado: {stats}")
        
        db.close()
        
    except Exception as e:
        logger.error(f"Error en tracking: {e}")
        if db:
            db.close()


def analyze_performance(**context):
    """Analiza performance de artículos."""
    db = get_db_connection()
    if not db:
        logger.error("No se pudo conectar a BD")
        return
    
    tracker = EngagementTracker(db)
    cursor = db.cursor()
    
    try:
        # Obtener artículos publicados en últimos 30 días
        cursor.execute("""
            SELECT DISTINCT article_id
            FROM content_scheduled_posts
            WHERE published_at >= NOW() - INTERVAL '30 days'
            AND status = 'published'
        """)
        
        articles = cursor.fetchall()
        
        for (article_id,) in articles:
            try:
                performance = tracker.get_article_performance(article_id, days=30)
                
                # Guardar análisis
                cursor.execute("""
                    INSERT INTO content_performance_analysis
                    (article_id, analysis_date, total_posts, total_platforms,
                     total_engagement, total_impressions, total_reach,
                     avg_engagement_rate, platform_breakdown)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (article_id, analysis_date)
                    DO UPDATE SET
                        total_posts = EXCLUDED.total_posts,
                        total_platforms = EXCLUDED.total_platforms,
                        total_engagement = EXCLUDED.total_engagement,
                        total_impressions = EXCLUDED.total_impressions,
                        total_reach = EXCLUDED.total_reach,
                        avg_engagement_rate = EXCLUDED.avg_engagement_rate,
                        platform_breakdown = EXCLUDED.platform_breakdown
                """, (
                    article_id,
                    datetime.now().date(),
                    performance['totals'].get('total_posts', 0),
                    len(performance['platform_breakdown']),
                    performance['totals'].get('total_likes', 0) +
                    performance['totals'].get('total_comments', 0) +
                    performance['totals'].get('total_shares', 0),
                    performance['totals'].get('total_impressions', 0),
                    performance['totals'].get('total_reach', 0),
                    performance['totals'].get('avg_engagement_rate'),
                    json.dumps(performance['platform_breakdown'])
                ))
                
            except Exception as e:
                logger.error(f"Error analizando artículo {article_id}: {e}")
                continue
        
        db.commit()
        cursor.close()
        db.close()
        
        logger.info(f"Análisis completado para {len(articles)} artículos")
        
    except Exception as e:
        logger.error(f"Error en análisis: {e}")
        if db:
            db.rollback()
            db.close()


# Tasks
convert_task = PythonOperator(
    task_id='convert_new_articles',
    python_callable=convert_new_articles,
    dag=dag,
)

schedule_task = PythonOperator(
    task_id='schedule_pending_versions',
    python_callable=schedule_pending_versions,
    dag=dag,
)

publish_task = PythonOperator(
    task_id='publish_scheduled_posts',
    python_callable=publish_scheduled_posts,
    dag=dag,
)

track_task = PythonOperator(
    task_id='track_engagement',
    python_callable=track_engagement,
    dag=dag,
)

analyze_task = PythonOperator(
    task_id='analyze_performance',
    python_callable=analyze_performance,
    dag=dag,
)

# Dependencies
convert_task >> schedule_task >> publish_task >> track_task >> analyze_task

