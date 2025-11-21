"""
Ejemplos de Uso del Sistema de Marketing de Contenido
======================================================
Scripts de ejemplo para usar el sistema manualmente.
"""
import psycopg2
import os
from datetime import datetime, timedelta
import sys

# Agregar plugins al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'plugins'))

from content_converter import ContentConverter, ContentFormat
from content_scheduler import ContentScheduler
from social_media_publisher import SocialMediaPublisher
from engagement_tracker import EngagementTracker


def get_db():
    """Obtiene conexión a BD."""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'your_database'),
        user=os.getenv('DB_USER', 'your_user'),
        password=os.getenv('DB_PASSWORD', 'your_password')
    )


def example_1_create_article():
    """Ejemplo 1: Crear un artículo."""
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO content_articles
            (article_id, title, content, author, source_url, status, published_at, tags)
            VALUES
            (
                'art-example-001',
                '10 Mejores Prácticas de Marketing Digital',
                'En este artículo exploraremos las mejores prácticas...\n\n1. Define tu audiencia\n2. Crea contenido de valor\n3. Mide tus resultados...',
                'María García',
                'https://example.com/blog/10-mejores-practicas',
                'published',
                NOW(),
                ARRAY['marketing', 'digital', 'best-practices']
            )
            ON CONFLICT (article_id) DO NOTHING
        """)
        
        db.commit()
        print("✅ Artículo creado: art-example-001")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        cursor.close()
        db.close()


def example_2_convert_article():
    """Ejemplo 2: Convertir artículo a múltiples formatos."""
    db = get_db()
    converter = ContentConverter(db)
    cursor = db.cursor()
    
    try:
        # Obtener artículo
        cursor.execute("""
            SELECT article_id, title, content, source_url, author, tags
            FROM content_articles
            WHERE article_id = 'art-example-001'
        """)
        
        article = cursor.fetchone()
        if not article:
            print("❌ Artículo no encontrado")
            return
        
        article_id, title, content, url, author, tags = article
        
        # Convertir
        versions = converter.convert_article(
            article_id=article_id,
            title=title,
            content=content,
            formats=[ContentFormat.TWITTER, ContentFormat.LINKEDIN, ContentFormat.NEWSLETTER],
            url=url,
            author=author,
            tags=tags or []
        )
        
        # Guardar
        saved_ids = converter.save_versions(versions)
        
        print(f"✅ Convertido: {len(saved_ids)} versiones creadas")
        for version in versions:
            print(f"  - {version.platform}: {version.character_count} caracteres")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        db.close()


def example_3_approve_and_schedule():
    """Ejemplo 3: Aprobar versiones y programar."""
    db = get_db()
    scheduler = ContentScheduler(db)
    cursor = db.cursor()
    
    try:
        # Aprobar versiones
        cursor.execute("""
            UPDATE content_versions
            SET status = 'approved',
                approved_by = 'admin',
                approved_at = NOW()
            WHERE article_id = 'art-example-001'
            AND status = 'pending'
        """)
        
        db.commit()
        print("✅ Versiones aprobadas")
        
        # Programar a múltiples plataformas
        post_ids = scheduler.schedule_article_to_platforms(
            article_id='art-example-001',
            platforms=['twitter', 'linkedin'],
            delay_hours=1,  # Esperar 1 hora
            stagger_hours=3  # 3 horas entre plataformas
        )
        
        print(f"✅ Programados {len(post_ids)} posts:")
        for post_id in post_ids:
            print(f"  - {post_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        cursor.close()
        db.close()


def example_4_publish_pending():
    """Ejemplo 4: Publicar posts programados."""
    db = get_db()
    publisher = SocialMediaPublisher(db)
    scheduler = ContentScheduler(db)
    
    try:
        # Obtener posts pendientes
        pending_posts = scheduler.get_pending_posts(limit=10)
        
        print(f"📝 Encontrados {len(pending_posts)} posts pendientes")
        
        for post in pending_posts:
            print(f"\n📤 Publicando: {post['post_id']} ({post['platform']})")
            
            # Actualizar estado
            scheduler.update_post_status(post['post_id'], 'publishing')
            
            # Publicar
            if post['platform'] == 'twitter':
                result = publisher.publish_to_twitter(
                    content=post['content'],
                    account_id=post.get('account_id')
                )
            elif post['platform'] == 'linkedin':
                result = publisher.publish_to_linkedin(
                    content=post['content'],
                    account_id=post.get('account_id')
                )
            else:
                print(f"  ⚠️ Plataforma {post['platform']} no implementada")
                continue
            
            if result.success:
                publisher.save_published_post(
                    post['post_id'],
                    result,
                    post.get('article_id'),
                    post.get('version_id')
                )
                print(f"  ✅ Publicado: {result.post_id}")
            else:
                scheduler.update_post_status(
                    post['post_id'],
                    'failed',
                    result.error_message
                )
                print(f"  ❌ Error: {result.error_message}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()


def example_5_track_engagement():
    """Ejemplo 5: Rastrear engagement."""
    db = get_db()
    tracker = EngagementTracker(db)
    
    try:
        print("📊 Rastreando engagement...")
        
        stats = tracker.track_all_pending_posts()
        
        print(f"\n📈 Estadísticas:")
        print(f"  Total: {stats['total']}")
        print(f"  Tracked: {stats['tracked']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Por plataforma: {stats.get('by_platform', {})}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()


def example_6_analyze_performance():
    """Ejemplo 6: Analizar performance."""
    db = get_db()
    tracker = EngagementTracker(db)
    
    try:
        print("📊 Analizando performance de artículos...")
        
        performance = tracker.get_article_performance('art-example-001', days=30)
        
        print(f"\n📈 Performance de art-example-001:")
        print(f"  Total posts: {performance['totals']['total_posts']}")
        print(f"  Total engagement: {performance['totals']['total_likes'] + performance['totals']['total_comments']}")
        print(f"  Total impressions: {performance['totals']['total_impressions']}")
        print(f"  Avg engagement rate: {performance['totals'].get('avg_engagement_rate', 0):.2f}%")
        
        print(f"\n📱 Por plataforma:")
        for platform, data in performance['platform_breakdown'].items():
            print(f"  {platform}:")
            print(f"    Posts: {data['total_posts']}")
            print(f"    Engagement rate: {data.get('avg_engagement_rate', 0):.2f}%")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()


def example_7_create_thread():
    """Ejemplo 7: Crear hilo de Twitter."""
    db = get_db()
    converter = ContentConverter(db)
    
    try:
        # Obtener artículo
        cursor = db.cursor()
        cursor.execute("""
            SELECT article_id, title, content, source_url
            FROM content_articles
            WHERE article_id = 'art-example-001'
        """)
        
        article = cursor.fetchone()
        if not article:
            print("❌ Artículo no encontrado")
            return
        
        article_id, title, content, url = article
        
        # Crear hilo
        thread_tweets = converter.create_twitter_thread(
            article_id=article_id,
            title=title,
            content=content,
            url=url
        )
        
        print(f"✅ Hilo creado: {len(thread_tweets)} tweets")
        for i, tweet in enumerate(thread_tweets, 1):
            print(f"\n📝 Tweet {i}/{len(thread_tweets)}:")
            print(f"  {tweet.content[:100]}...")
            print(f"  Caracteres: {tweet.character_count}")
        
        # Guardar
        saved_ids = converter.save_versions(thread_tweets)
        print(f"\n✅ Guardados: {len(saved_ids)} tweets")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Ejemplos de Marketing de Contenido")
    print("=" * 60)
    
    print("\n1. Crear artículo")
    example_1_create_article()
    
    print("\n2. Convertir artículo")
    example_2_convert_article()
    
    print("\n3. Aprobar y programar")
    example_3_approve_and_schedule()
    
    print("\n4. Publicar pendientes")
    # example_4_publish_pending()  # Descomentar para ejecutar
    
    print("\n5. Rastrear engagement")
    # example_5_track_engagement()  # Descomentar para ejecutar
    
    print("\n6. Analizar performance")
    # example_6_analyze_performance()  # Descomentar para ejecutar
    
    print("\n7. Crear hilo de Twitter")
    example_7_create_thread()

