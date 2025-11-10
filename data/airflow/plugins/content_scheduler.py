"""
Sistema de Programación de Publicaciones
==========================================
Programa publicaciones en redes sociales con optimización de timing.
"""
import logging
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


@dataclass
class ScheduledPost:
    """Post programado."""
    post_id: str
    article_id: str
    version_id: int
    platform: str
    account_id: str
    content: str
    scheduled_at: datetime
    status: str = "scheduled"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ContentScheduler:
    """Programador de contenido en redes sociales."""
    
    # Horarios óptimos por plataforma (UTC)
    OPTIMAL_TIMES = {
        "twitter": ["09:00", "13:00", "17:00", "21:00"],
        "linkedin": ["08:00", "12:00", "17:00"],
        "facebook": ["09:00", "15:00", "20:00"],
        "instagram": ["11:00", "14:00", "17:00", "20:00"],
    }
    
    def __init__(self, db_connection=None):
        """
        Inicializar programador.
        
        Args:
            db_connection: Conexión a base de datos
        """
        self.db = db_connection
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def calculate_optimal_time(
        self,
        platform: str,
        preferred_times: List[str] = None,
        timezone: str = "UTC",
        days_ahead: int = 7
    ) -> List[datetime]:
        """
        Calcula horarios óptimos para publicar.
        
        Args:
            platform: Plataforma
            preferred_times: Horarios preferidos (formato HH:MM)
            timezone: Zona horaria
            days_ahead: Días hacia adelante para calcular
            
        Returns:
            Lista de horarios óptimos
        """
        if preferred_times is None:
            preferred_times = self.OPTIMAL_TIMES.get(platform, ["12:00"])
        
        optimal_times = []
        base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for day in range(days_ahead):
            for time_str in preferred_times:
                hour, minute = map(int, time_str.split(":"))
                optimal_time = base_date + timedelta(days=day, hours=hour, minutes=minute)
                
                # Solo futuros
                if optimal_time > datetime.now():
                    optimal_times.append(optimal_time)
        
        return sorted(optimal_times)
    
    def find_available_slot(
        self,
        platform: str,
        account_id: str,
        preferred_time: datetime = None,
        timezone: str = "UTC"
    ) -> Optional[datetime]:
        """
        Encuentra un slot disponible para publicar.
        
        Args:
            platform: Plataforma
            account_id: ID de cuenta
            preferred_time: Hora preferida
            timezone: Zona horaria
            
        Returns:
            Hora disponible o None
        """
        if not self.db:
            return preferred_time or datetime.now() + timedelta(hours=1)
        
        cursor = self.db.cursor()
        
        # Obtener horarios óptimos
        optimal_times = self.calculate_optimal_time(platform, timezone=timezone)
        
        if preferred_time:
            # Priorizar hora preferida si está disponible
            optimal_times.insert(0, preferred_time)
        
        # Verificar slots ocupados
        for optimal_time in optimal_times:
            # Verificar si hay conflicto
            cursor.execute("""
                SELECT COUNT(*) FROM content_scheduled_posts
                WHERE platform = %s
                AND account_id = %s
                AND scheduled_at BETWEEN %s AND %s
                AND status NOT IN ('failed', 'cancelled')
            """, (
                platform,
                account_id,
                optimal_time - timedelta(minutes=30),
                optimal_time + timedelta(minutes=30)
            ))
            
            conflict_count = cursor.fetchone()[0]
            
            if conflict_count == 0:
                cursor.close()
                return optimal_time
        
        cursor.close()
        
        # Si no hay slot óptimo, usar el siguiente disponible
        if optimal_times:
            return optimal_times[0]
        
        return datetime.now() + timedelta(hours=1)
    
    def schedule_post(
        self,
        article_id: str,
        version_id: int,
        platform: str,
        account_id: str = None,
        scheduled_at: datetime = None,
        content: str = None,
        media_urls: List[str] = None,
        hashtags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Programa un post.
        
        Args:
            article_id: ID del artículo
            version_id: ID de la versión
            platform: Plataforma
            account_id: ID de cuenta
            scheduled_at: Hora programada (si None, calcula automáticamente)
            content: Contenido del post
            media_urls: URLs de medios
            hashtags: Hashtags
            metadata: Metadatos adicionales
            
        Returns:
            ID del post programado o None
        """
        if not self.db:
            self.logger.warning("No hay conexión a BD")
            return None
        
        cursor = self.db.cursor()
        
        # Obtener contenido si no se proporciona
        if not content:
            cursor.execute("""
                SELECT content, media_urls, hashtags
                FROM content_versions
                WHERE id = %s
            """, (version_id,))
            
            result = cursor.fetchone()
            if result:
                content = result[0]
                media_urls = result[1] or media_urls or []
                hashtags = result[2] or hashtags or []
        
        # Calcular hora de publicación si no se proporciona
        if not scheduled_at:
            scheduled_at = self.find_available_slot(platform, account_id or "")
        
        # Generar post_id
        post_id = f"{platform}_{article_id}_{int(scheduled_at.timestamp())}"
        
        try:
            cursor.execute("""
                INSERT INTO content_scheduled_posts
                (post_id, article_id, version_id, platform, account_id, account_name,
                 content, media_urls, hashtags, scheduled_at, timezone, status, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'scheduled', %s)
            """, (
                post_id,
                article_id,
                version_id,
                platform,
                account_id,
                account_id,  # account_name por defecto
                content,
                media_urls or [],
                hashtags or [],
                scheduled_at,
                "UTC",
                json.dumps(metadata or {})
            ))
            
            self.db.commit()
            cursor.close()
            
            self.logger.info(f"Post programado: {post_id} para {scheduled_at}")
            return post_id
            
        except Exception as e:
            self.logger.error(f"Error programando post: {e}")
            self.db.rollback()
            cursor.close()
            return None
    
    def schedule_article_to_platforms(
        self,
        article_id: str,
        platforms: List[str] = None,
        delay_hours: int = 0,
        stagger_hours: int = 2
    ) -> List[str]:
        """
        Programa un artículo a múltiples plataformas.
        
        Args:
            article_id: ID del artículo
            platforms: Lista de plataformas (si None, usa todas)
            delay_hours: Horas de delay antes de primera publicación
            stagger_hours: Horas entre publicaciones por plataforma
            
        Returns:
            Lista de post_ids programados
        """
        if not self.db:
            return []
        
        if platforms is None:
            platforms = ["twitter", "linkedin", "facebook"]
        
        cursor = self.db.cursor()
        
        # Obtener versiones del artículo
        cursor.execute("""
            SELECT id, platform, version_type
            FROM content_versions
            WHERE article_id = %s
            AND status = 'approved'
            ORDER BY platform
        """, (article_id,))
        
        versions = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        scheduled_posts = []
        base_time = datetime.now() + timedelta(hours=delay_hours)
        
        for version_row in versions:
            version = dict(zip(columns, version_row))
            platform = version['platform']
            
            if platform not in platforms:
                continue
            
            # Calcular hora de publicación con stagger
            scheduled_time = base_time + timedelta(
                hours=len(scheduled_posts) * stagger_hours
            )
            
            # Obtener account_id por defecto para la plataforma
            cursor.execute("""
                SELECT account_id FROM content_platform_config
                WHERE platform = %s AND is_active = TRUE
                LIMIT 1
            """, (platform,))
            
            account_result = cursor.fetchone()
            account_id = account_result[0] if account_result else None
            
            post_id = self.schedule_post(
                article_id=article_id,
                version_id=version['id'],
                platform=platform,
                account_id=account_id,
                scheduled_at=scheduled_time
            )
            
            if post_id:
                scheduled_posts.append(post_id)
        
        cursor.close()
        return scheduled_posts
    
    def get_pending_posts(
        self,
        platform: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Obtiene posts pendientes de publicar.
        
        Args:
            platform: Plataforma específica (opcional)
            limit: Límite de resultados
            
        Returns:
            Lista de posts pendientes
        """
        if not self.db:
            return []
        
        cursor = self.db.cursor()
        
        query = """
            SELECT * FROM content_scheduled_posts
            WHERE status = 'scheduled'
            AND scheduled_at <= NOW() + INTERVAL '1 hour'
        """
        params = []
        
        if platform:
            query += " AND platform = %s"
            params.append(platform)
        
        query += " ORDER BY scheduled_at ASC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        posts = [dict(zip(columns, row)) for row in results]
        cursor.close()
        
        return posts
    
    def update_post_status(
        self,
        post_id: str,
        status: str,
        error_message: str = None
    ) -> bool:
        """
        Actualiza estado de un post.
        
        Args:
            post_id: ID del post
            status: Nuevo estado
            error_message: Mensaje de error (si aplica)
            
        Returns:
            True si se actualizó correctamente
        """
        if not self.db:
            return False
        
        cursor = self.db.cursor()
        
        try:
            cursor.execute("""
                UPDATE content_scheduled_posts
                SET status = %s,
                    error_message = %s,
                    updated_at = NOW()
                WHERE post_id = %s
            """, (status, error_message, post_id))
            
            self.db.commit()
            cursor.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Error actualizando estado de post: {e}")
            self.db.rollback()
            cursor.close()
            return False

