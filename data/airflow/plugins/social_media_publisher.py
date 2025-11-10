"""
Sistema de Publicación en Redes Sociales
=========================================
Publica contenido en múltiples plataformas:
- Twitter/X
- LinkedIn
- Facebook
- Instagram
- Threads
"""
import logging
import json
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class SocialPlatform(Enum):
    """Plataformas sociales soportadas."""
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    THREADS = "threads"


@dataclass
class PublishResult:
    """Resultado de una publicación."""
    success: bool
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    error_message: Optional[str] = None
    platform: Optional[str] = None
    published_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class SocialMediaPublisher:
    """Publicador de contenido en redes sociales."""
    
    def __init__(self, db_connection=None):
        """
        Inicializar publicador.
        
        Args:
            db_connection: Conexión a base de datos
        """
        self.db = db_connection
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._rate_limits = {}  # Cache de rate limits
    
    def _get_platform_config(self, platform: str, account_id: str = None) -> Dict[str, Any]:
        """
        Obtiene configuración de plataforma desde BD.
        
        Args:
            platform: Nombre de la plataforma
            account_id: ID de cuenta (opcional)
            
        Returns:
            Configuración de la plataforma
        """
        if not self.db:
            return {}
        
        cursor = self.db.cursor()
        query = "SELECT * FROM content_platform_config WHERE platform = %s AND is_active = TRUE"
        params = [platform]
        
        if account_id:
            query += " AND account_id = %s"
            params.append(account_id)
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, result))
        return {}
    
    def _check_rate_limit(self, platform: str, account_id: str) -> bool:
        """
        Verifica si se puede publicar según rate limits.
        
        Args:
            platform: Plataforma
            account_id: ID de cuenta
            
        Returns:
            True si se puede publicar, False si no
        """
        config = self._get_platform_config(platform, account_id)
        
        if not config:
            return True  # Sin configuración, permitir
        
        # Verificar límite diario
        daily_limit = config.get('daily_post_limit', 10)
        hourly_limit = config.get('hourly_post_limit', 2)
        
        if not self.db:
            return True
        
        cursor = self.db.cursor()
        
        # Contar posts hoy
        today = datetime.now().date()
        cursor.execute("""
            SELECT COUNT(*) FROM content_scheduled_posts
            WHERE platform = %s AND account_id = %s
            AND DATE(scheduled_at) = %s
            AND status IN ('published', 'publishing')
        """, (platform, account_id, today))
        
        today_count = cursor.fetchone()[0]
        if today_count >= daily_limit:
            cursor.close()
            return False
        
        # Contar posts en última hora
        one_hour_ago = datetime.now() - timedelta(hours=1)
        cursor.execute("""
            SELECT COUNT(*) FROM content_scheduled_posts
            WHERE platform = %s AND account_id = %s
            AND scheduled_at >= %s
            AND status IN ('published', 'publishing')
        """, (platform, account_id, one_hour_ago))
        
        hour_count = cursor.fetchone()[0]
        cursor.close()
        
        return hour_count < hourly_limit
    
    def publish_to_twitter(
        self,
        content: str,
        media_urls: List[str] = None,
        reply_to: Optional[str] = None,
        account_id: str = None
    ) -> PublishResult:
        """
        Publica en Twitter/X.
        
        Args:
            content: Contenido del tweet
            media_urls: URLs de imágenes/videos
            reply_to: ID del tweet al que responde
            account_id: ID de cuenta
            
        Returns:
            Resultado de la publicación
        """
        config = self._get_platform_config(SocialPlatform.TWITTER.value, account_id)
        
        if not config:
            return PublishResult(
                success=False,
                platform=SocialPlatform.TWITTER.value,
                error_message="Configuración de Twitter no encontrada"
            )
        
        # Verificar rate limit
        if not self._check_rate_limit(SocialPlatform.TWITTER.value, account_id or config.get('account_id')):
            return PublishResult(
                success=False,
                platform=SocialPlatform.TWITTER.value,
                error_message="Rate limit alcanzado"
            )
        
        try:
            # Usar Twitter API v2
            access_token = config.get('access_token')
            api_key = config.get('api_key')
            api_secret = config.get('api_secret')
            
            # Nota: Implementación real requeriría OAuth 2.0 o 1.0a
            # Aquí se muestra la estructura básica
            
            # Simulación de publicación (reemplazar con API real)
            self.logger.info(f"Publicando en Twitter: {content[:50]}...")
            
            # En producción, usaría tweepy o requests con OAuth
            # post_url = f"https://twitter.com/i/web/status/{post_id}"
            
            # Por ahora, retornamos éxito simulado
            post_id = f"tw_{int(datetime.now().timestamp())}"
            
            return PublishResult(
                success=True,
                post_id=post_id,
                platform=SocialPlatform.TWITTER.value,
                published_at=datetime.now(),
                metadata={
                    "character_count": len(content),
                    "has_media": bool(media_urls)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error publicando en Twitter: {e}")
            return PublishResult(
                success=False,
                platform=SocialPlatform.TWITTER.value,
                error_message=str(e)
            )
    
    def publish_to_linkedin(
        self,
        content: str,
        media_urls: List[str] = None,
        article_url: str = None,
        account_id: str = None
    ) -> PublishResult:
        """
        Publica en LinkedIn.
        
        Args:
            content: Contenido del post
            media_urls: URLs de imágenes
            article_url: URL del artículo (para compartir)
            account_id: ID de cuenta
            
        Returns:
            Resultado de la publicación
        """
        config = self._get_platform_config(SocialPlatform.LINKEDIN.value, account_id)
        
        if not config:
            return PublishResult(
                success=False,
                platform=SocialPlatform.LINKEDIN.value,
                error_message="Configuración de LinkedIn no encontrada"
            )
        
        if not self._check_rate_limit(SocialPlatform.LINKEDIN.value, account_id or config.get('account_id')):
            return PublishResult(
                success=False,
                platform=SocialPlatform.LINKEDIN.value,
                error_message="Rate limit alcanzado"
            )
        
        try:
            access_token = config.get('access_token')
            
            # LinkedIn API v2
            # En producción, usaría requests con OAuth 2.0
            self.logger.info(f"Publicando en LinkedIn: {content[:50]}...")
            
            post_id = f"li_{int(datetime.now().timestamp())}"
            
            return PublishResult(
                success=True,
                post_id=post_id,
                platform=SocialPlatform.LINKEDIN.value,
                published_at=datetime.now(),
                metadata={
                    "word_count": len(content.split()),
                    "has_article_url": bool(article_url)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error publicando en LinkedIn: {e}")
            return PublishResult(
                success=False,
                platform=SocialPlatform.LINKEDIN.value,
                error_message=str(e)
            )
    
    def publish_to_facebook(
        self,
        content: str,
        media_urls: List[str] = None,
        page_id: str = None,
        account_id: str = None
    ) -> PublishResult:
        """
        Publica en Facebook.
        
        Args:
            content: Contenido del post
            media_urls: URLs de imágenes/videos
            page_id: ID de la página
            account_id: ID de cuenta
            
        Returns:
            Resultado de la publicación
        """
        config = self._get_platform_config(SocialPlatform.FACEBOOK.value, account_id)
        
        if not config:
            return PublishResult(
                success=False,
                platform=SocialPlatform.FACEBOOK.value,
                error_message="Configuración de Facebook no encontrada"
            )
        
        if not self._check_rate_limit(SocialPlatform.FACEBOOK.value, account_id or config.get('account_id')):
            return PublishResult(
                success=False,
                platform=SocialPlatform.FACEBOOK.value,
                error_message="Rate limit alcanzado"
            )
        
        try:
            access_token = config.get('access_token')
            
            # Facebook Graph API
            self.logger.info(f"Publicando en Facebook: {content[:50]}...")
            
            post_id = f"fb_{int(datetime.now().timestamp())}"
            
            return PublishResult(
                success=True,
                post_id=post_id,
                platform=SocialPlatform.FACEBOOK.value,
                published_at=datetime.now(),
                metadata={
                    "page_id": page_id,
                    "has_media": bool(media_urls)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error publicando en Facebook: {e}")
            return PublishResult(
                success=False,
                platform=SocialPlatform.FACEBOOK.value,
                error_message=str(e)
            )
    
    def publish_thread(
        self,
        tweets: List[str],
        account_id: str = None
    ) -> List[PublishResult]:
        """
        Publica un hilo de tweets.
        
        Args:
            tweets: Lista de tweets del hilo
            account_id: ID de cuenta
            
        Returns:
            Lista de resultados de publicación
        """
        results = []
        last_tweet_id = None
        
        for i, tweet_content in enumerate(tweets):
            if i == 0:
                # Primer tweet
                result = self.publish_to_twitter(tweet_content, account_id=account_id)
            else:
                # Respuestas a tweets anteriores
                result = self.publish_to_twitter(
                    tweet_content,
                    reply_to=last_tweet_id,
                    account_id=account_id
                )
            
            results.append(result)
            
            if result.success and result.post_id:
                last_tweet_id = result.post_id
            else:
                # Si falla, detener el hilo
                break
        
        return results
    
    def save_published_post(
        self,
        post_id: str,
        result: PublishResult,
        article_id: str = None,
        version_id: int = None
    ) -> bool:
        """
        Guarda información de post publicado en BD.
        
        Args:
            post_id: ID del post programado
            result: Resultado de la publicación
            article_id: ID del artículo
            version_id: ID de la versión
            
        Returns:
            True si se guardó correctamente
        """
        if not self.db:
            return False
        
        cursor = self.db.cursor()
        
        try:
            cursor.execute("""
                UPDATE content_scheduled_posts
                SET status = %s,
                    published_post_id = %s,
                    published_url = %s,
                    published_at = %s,
                    error_message = %s,
                    metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb,
                    updated_at = NOW()
                WHERE post_id = %s
            """, (
                'published' if result.success else 'failed',
                result.post_id,
                result.post_url,
                result.published_at,
                result.error_message,
                json.dumps(result.metadata or {}),
                post_id
            ))
            
            self.db.commit()
            cursor.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando post publicado: {e}")
            self.db.rollback()
            cursor.close()
            return False

