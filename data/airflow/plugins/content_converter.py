"""
Sistema de Conversión de Contenido
==================================
Convierte artículos/blogs a múltiples formatos para redes sociales:
- Tweets (con hilos)
- LinkedIn posts
- Newsletters
- Facebook posts
- Instagram posts
"""
import logging
import re
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ContentFormat(Enum):
    """Formatos de contenido soportados."""
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    NEWSLETTER = "newsletter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    THREAD = "thread"


@dataclass
class ContentVersion:
    """Versión convertida de contenido."""
    article_id: str
    version_type: str
    platform: str
    content: str
    media_urls: List[str]
    hashtags: List[str]
    character_count: int
    word_count: int
    estimated_read_time: Optional[int] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ContentConverter:
    """Conversor de contenido a múltiples formatos."""
    
    # Límites de caracteres por plataforma
    PLATFORM_LIMITS = {
        ContentFormat.TWITTER: 280,
        ContentFormat.LINKEDIN: 3000,
        ContentFormat.FACEBOOK: 63206,
        ContentFormat.INSTAGRAM: 2200,
        ContentFormat.NEWSLETTER: None,  # Sin límite
    }
    
    def __init__(self, db_connection=None):
        """
        Inicializar conversor.
        
        Args:
            db_connection: Conexión a base de datos (opcional)
        """
        self.db = db_connection
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def extract_key_points(self, content: str, max_points: int = 5) -> List[str]:
        """
        Extrae puntos clave del contenido.
        
        Args:
            content: Contenido del artículo
            max_points: Número máximo de puntos a extraer
            
        Returns:
            Lista de puntos clave
        """
        # Buscar listas numeradas o con viñetas
        bullet_pattern = r'[-•*]\s+(.+?)(?=\n|$)'
        numbered_pattern = r'\d+[\.\)]\s+(.+?)(?=\n|$)'
        
        points = []
        
        # Extraer de listas con viñetas
        for match in re.finditer(bullet_pattern, content, re.MULTILINE):
            point = match.group(1).strip()
            if len(point) > 20 and len(point) < 200:  # Filtrar puntos muy cortos/largos
                points.append(point)
        
        # Extraer de listas numeradas
        for match in re.finditer(numbered_pattern, content, re.MULTILINE):
            point = match.group(1).strip()
            if len(point) > 20 and len(point) < 200:
                points.append(point)
        
        # Si no hay suficientes puntos, extraer oraciones importantes
        if len(points) < max_points:
            sentences = re.split(r'[.!?]\s+', content)
            # Filtrar oraciones muy cortas o muy largas
            important_sentences = [
                s.strip() for s in sentences
                if 50 < len(s.strip()) < 300
            ]
            points.extend(important_sentences[:max_points - len(points)])
        
        return points[:max_points]
    
    def extract_hashtags(self, content: str, existing_tags: List[str] = None) -> List[str]:
        """
        Extrae o genera hashtags del contenido.
        
        Args:
            content: Contenido del artículo
            existing_tags: Tags existentes del artículo
            
        Returns:
            Lista de hashtags
        """
        hashtags = []
        
        # Usar tags existentes si están disponibles
        if existing_tags:
            hashtags.extend([f"#{tag.replace(' ', '').replace('-', '')}" for tag in existing_tags[:5]])
        
        # Extraer palabras clave del contenido
        words = re.findall(r'\b\w{5,}\b', content.lower())
        word_freq = {}
        for word in words:
            if word not in ['esta', 'esto', 'este', 'estos', 'estas', 'tambien', 'siempre', 'nunca']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Obtener las palabras más frecuentes
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:3]
        hashtags.extend([f"#{word}" for word, _ in top_words])
        
        return list(set(hashtags))[:10]  # Máximo 10 hashtags
    
    def create_twitter_version(
        self,
        article_id: str,
        title: str,
        content: str,
        url: str = None,
        hashtags: List[str] = None
    ) -> ContentVersion:
        """
        Crea versión para Twitter.
        
        Args:
            article_id: ID del artículo
            title: Título del artículo
            content: Contenido del artículo
            url: URL del artículo
            hashtags: Hashtags a incluir
            
        Returns:
            Versión de Twitter
        """
        # Extraer punto clave principal
        key_points = self.extract_key_points(content, max_points=1)
        main_point = key_points[0] if key_points else title
        
        # Crear tweet
        tweet_content = f"{main_point}"
        
        # Agregar URL si está disponible
        if url:
            tweet_content += f"\n\n{url}"
        
        # Agregar hashtags
        if not hashtags:
            hashtags = self.extract_hashtags(content)
        
        if hashtags:
            hashtag_str = " ".join(hashtags[:3])  # Máximo 3 hashtags para Twitter
            tweet_content += f"\n\n{hashtag_str}"
        
        # Asegurar que no exceda el límite
        max_length = self.PLATFORM_LIMITS[ContentFormat.TWITTER]
        if len(tweet_content) > max_length:
            # Recortar manteniendo URL y hashtags
            available_length = max_length - len(url) - len(" ".join(hashtags[:3])) - 10
            tweet_content = main_point[:available_length] + "..."
            if url:
                tweet_content += f"\n\n{url}"
            if hashtags:
                tweet_content += f"\n\n{' '.join(hashtags[:3])}"
        
        return ContentVersion(
            article_id=article_id,
            version_type="twitter",
            platform="twitter",
            content=tweet_content,
            media_urls=[],
            hashtags=hashtags[:3],
            character_count=len(tweet_content),
            word_count=len(tweet_content.split()),
            metadata={"max_length": max_length}
        )
    
    def create_twitter_thread(
        self,
        article_id: str,
        title: str,
        content: str,
        url: str = None,
        hashtags: List[str] = None
    ) -> List[ContentVersion]:
        """
        Crea hilo de Twitter (múltiples tweets).
        
        Args:
            article_id: ID del artículo
            title: Título del artículo
            content: Contenido del artículo
            url: URL del artículo
            hashtags: Hashtags a incluir
            
        Returns:
            Lista de tweets del hilo
        """
        key_points = self.extract_key_points(content, max_points=10)
        tweets = []
        max_length = self.PLATFORM_LIMITS[ContentFormat.TWITTER]
        
        # Primer tweet con título
        first_tweet = f"🧵 {title}"
        if url:
            first_tweet += f"\n\n{url}"
        if len(first_tweet) > max_length:
            first_tweet = first_tweet[:max_length - 3] + "..."
        
        tweets.append(ContentVersion(
            article_id=article_id,
            version_type="thread",
            platform="twitter",
            content=first_tweet,
            media_urls=[],
            hashtags=[],
            character_count=len(first_tweet),
            word_count=len(first_tweet.split()),
            metadata={"thread_position": 1, "is_thread": True}
        ))
        
        # Tweets con puntos clave
        for i, point in enumerate(key_points, start=2):
            tweet_content = f"{i}/ {point}"
            if len(tweet_content) > max_length:
                tweet_content = tweet_content[:max_length - 3] + "..."
            
            tweets.append(ContentVersion(
                article_id=article_id,
                version_type="thread",
                platform="twitter",
                content=tweet_content,
                media_urls=[],
                hashtags=[],
                character_count=len(tweet_content),
                word_count=len(tweet_content.split()),
                metadata={"thread_position": i, "is_thread": True}
            ))
        
        # Último tweet con hashtags
        if hashtags:
            hashtags = self.extract_hashtags(content) if not hashtags else hashtags
            last_tweet = f"💡 Puntos clave del artículo anterior 👆"
            hashtag_str = " ".join(hashtags[:3])
            if len(last_tweet + "\n\n" + hashtag_str) <= max_length:
                last_tweet += f"\n\n{hashtag_str}"
            
            tweets.append(ContentVersion(
                article_id=article_id,
                version_type="thread",
                platform="twitter",
                content=last_tweet,
                media_urls=[],
                hashtags=hashtags[:3],
                character_count=len(last_tweet),
                word_count=len(last_tweet.split()),
                metadata={
                    "thread_position": len(tweets) + 1,
                    "is_thread": True,
                    "is_last": True
                }
            ))
        
        return tweets
    
    def create_linkedin_version(
        self,
        article_id: str,
        title: str,
        content: str,
        url: str = None,
        hashtags: List[str] = None,
        author: str = None
    ) -> ContentVersion:
        """
        Crea versión para LinkedIn.
        
        Args:
            article_id: ID del artículo
            title: Título del artículo
            content: Contenido del artículo
            url: URL del artículo
            hashtags: Hashtags a incluir
            author: Autor del artículo
            
        Returns:
            Versión de LinkedIn
        """
        # Extraer puntos clave
        key_points = self.extract_key_points(content, max_points=5)
        
        # Crear post de LinkedIn
        post_lines = [f"📝 {title}"]
        
        if author:
            post_lines.append(f"\nPor: {author}")
        
        post_lines.append("\n\nPuntos clave:")
        for i, point in enumerate(key_points, 1):
            post_lines.append(f"\n{i}. {point}")
        
        # Agregar excerpt o resumen
        excerpt_length = 300
        if len(content) > excerpt_length:
            excerpt = content[:excerpt_length] + "..."
            post_lines.append(f"\n\n{excerpt}")
        
        if url:
            post_lines.append(f"\n\nLeer más: {url}")
        
        # Agregar hashtags
        if not hashtags:
            hashtags = self.extract_hashtags(content)
        
        if hashtags:
            hashtag_str = " ".join(hashtags[:5])
            post_lines.append(f"\n\n{hashtag_str}")
        
        post_content = "".join(post_lines)
        
        # Asegurar que no exceda el límite
        max_length = self.PLATFORM_LIMITS[ContentFormat.LINKEDIN]
        if len(post_content) > max_length:
            # Mantener título, puntos clave y URL
            available_length = max_length - len(url) - len(" ".join(hashtags[:5])) - 200
            post_content = f"📝 {title}\n\nPuntos clave:\n"
            for i, point in enumerate(key_points[:3], 1):
                if len(post_content) + len(point) < available_length:
                    post_content += f"{i}. {point}\n"
            if url:
                post_content += f"\nLeer más: {url}"
            if hashtags:
                post_content += f"\n\n{' '.join(hashtags[:5])}"
        
        return ContentVersion(
            article_id=article_id,
            version_type="linkedin",
            platform="linkedin",
            content=post_content,
            media_urls=[],
            hashtags=hashtags[:5],
            character_count=len(post_content),
            word_count=len(post_content.split()),
            estimated_read_time=len(post_content.split()) // 200,  # ~200 palabras/minuto
            metadata={"max_length": max_length}
        )
    
    def create_newsletter_version(
        self,
        article_id: str,
        title: str,
        content: str,
        url: str = None,
        author: str = None,
        featured_image: str = None
    ) -> ContentVersion:
        """
        Crea versión para newsletter.
        
        Args:
            article_id: ID del artículo
            title: Título del artículo
            content: Contenido del artículo
            url: URL del artículo
            author: Autor del artículo
            featured_image: URL de imagen destacada
            
        Returns:
            Versión de newsletter
        """
        # Crear HTML para newsletter
        html_lines = []
        
        if featured_image:
            html_lines.append(f'<img src="{featured_image}" alt="{title}" style="max-width: 100%; height: auto;">')
        
        html_lines.append(f"<h1>{title}</h1>")
        
        if author:
            html_lines.append(f"<p><em>Por: {author}</em></p>")
        
        # Convertir saltos de línea a HTML
        content_html = content.replace('\n\n', '</p><p>').replace('\n', '<br>')
        html_lines.append(f"<p>{content_html}</p>")
        
        if url:
            html_lines.append(f'<p><a href="{url}">Leer artículo completo →</a></p>')
        
        html_content = "\n".join(html_lines)
        
        # Versión de texto plano
        text_lines = [title]
        if author:
            text_lines.append(f"\nPor: {author}\n")
        text_lines.append(content)
        if url:
            text_lines.append(f"\n\nLeer más: {url}")
        
        text_content = "\n".join(text_lines)
        
        return ContentVersion(
            article_id=article_id,
            version_type="newsletter",
            platform="email",
            content=text_content,
            media_urls=[featured_image] if featured_image else [],
            hashtags=[],
            character_count=len(text_content),
            word_count=len(text_content.split()),
            estimated_read_time=len(text_content.split()) // 200,
            metadata={
                "html_content": html_content,
                "has_image": bool(featured_image)
            }
        )
    
    def convert_article(
        self,
        article_id: str,
        title: str,
        content: str,
        formats: List[ContentFormat] = None,
        url: str = None,
        author: str = None,
        featured_image: str = None,
        tags: List[str] = None
    ) -> List[ContentVersion]:
        """
        Convierte un artículo a múltiples formatos.
        
        Args:
            article_id: ID del artículo
            title: Título del artículo
            content: Contenido del artículo
            formats: Formatos a generar (default: todos)
            url: URL del artículo
            author: Autor del artículo
            featured_image: URL de imagen destacada
            tags: Tags del artículo
            
        Returns:
            Lista de versiones convertidas
        """
        if formats is None:
            formats = [ContentFormat.TWITTER, ContentFormat.LINKEDIN, ContentFormat.NEWSLETTER]
        
        versions = []
        hashtags = self.extract_hashtags(content, tags)
        
        for format_type in formats:
            try:
                if format_type == ContentFormat.TWITTER:
                    version = self.create_twitter_version(
                        article_id, title, content, url, hashtags
                    )
                    versions.append(version)
                elif format_type == ContentFormat.LINKEDIN:
                    version = self.create_linkedin_version(
                        article_id, title, content, url, hashtags, author
                    )
                    versions.append(version)
                elif format_type == ContentFormat.NEWSLETTER:
                    version = self.create_newsletter_version(
                        article_id, title, content, url, author, featured_image
                    )
                    versions.append(version)
                elif format_type == ContentFormat.THREAD:
                    thread_tweets = self.create_twitter_thread(
                        article_id, title, content, url, hashtags
                    )
                    versions.extend(thread_tweets)
            except Exception as e:
                self.logger.error(f"Error convirtiendo a {format_type.value}: {e}")
                continue
        
        return versions
    
    def save_versions(self, versions: List[ContentVersion]) -> List[int]:
        """
        Guarda versiones en la base de datos.
        
        Args:
            versions: Lista de versiones a guardar
            
        Returns:
            Lista de IDs de versiones guardadas
        """
        if not self.db:
            self.logger.warning("No hay conexión a BD, no se guardaron versiones")
            return []
        
        saved_ids = []
        cursor = self.db.cursor()
        
        for version in versions:
            try:
                cursor.execute("""
                    INSERT INTO content_versions
                    (article_id, version_type, platform, content, media_urls, hashtags,
                     character_count, word_count, estimated_read_time, metadata, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
                    ON CONFLICT (article_id, version_type, platform)
                    DO UPDATE SET
                        content = EXCLUDED.content,
                        media_urls = EXCLUDED.media_urls,
                        hashtags = EXCLUDED.hashtags,
                        character_count = EXCLUDED.character_count,
                        word_count = EXCLUDED.word_count,
                        estimated_read_time = EXCLUDED.estimated_read_time,
                        metadata = EXCLUDED.metadata,
                        updated_at = NOW()
                    RETURNING id
                """, (
                    version.article_id,
                    version.version_type,
                    version.platform,
                    version.content,
                    version.media_urls,
                    version.hashtags,
                    version.character_count,
                    version.word_count,
                    version.estimated_read_time,
                    json.dumps(version.metadata) if version.metadata else '{}'
                ))
                
                result = cursor.fetchone()
                if result:
                    saved_ids.append(result[0])
            except Exception as e:
                self.logger.error(f"Error guardando versión {version.article_id}: {e}")
                continue
        
        self.db.commit()
        cursor.close()
        
        return saved_ids

