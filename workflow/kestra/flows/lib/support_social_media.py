"""
Sistema de Integración con Redes Sociales para Soporte.

Permite gestionar tickets desde Twitter, Facebook, Instagram, LinkedIn, etc.
"""
import logging
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SocialPlatform(Enum):
    """Plataformas sociales soportadas."""
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    REDDIT = "reddit"


class SocialMessageType(Enum):
    """Tipos de mensajes sociales."""
    MENTION = "mention"
    DIRECT_MESSAGE = "direct_message"
    COMMENT = "comment"
    REVIEW = "review"
    POST = "post"


@dataclass
class SocialMessage:
    """Mensaje de red social."""
    platform: SocialPlatform
    message_id: str
    message_type: SocialMessageType
    author_id: str
    author_name: str
    author_username: str
    content: str
    url: str
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class SocialTicket:
    """Ticket creado desde red social."""
    ticket_id: str
    original_message: SocialMessage
    platform: SocialPlatform
    customer_email: Optional[str]
    customer_username: str
    priority: str
    status: str
    created_at: datetime
    metadata: Dict[str, Any]


class SocialMediaIntegration:
    """Integración con redes sociales."""
    
    def __init__(self, db_connection):
        """
        Inicializar integración.
        
        Args:
            db_connection: Conexión a base de datos
        """
        self.db = db_connection
    
    def create_ticket_from_social_message(self, message: SocialMessage, customer_email: Optional[str] = None) -> SocialTicket:
        """
        Crear ticket desde mensaje de red social.
        
        Args:
            message: Mensaje de red social
            customer_email: Email del cliente (si se conoce)
            
        Returns:
            Ticket creado
        """
        try:
            # Analizar contenido para determinar prioridad
            priority = self._analyze_priority(message.content)
            
            # Buscar email en base de datos
            if not customer_email:
                customer_email = self._find_customer_email(message.author_username, message.platform)
            
            # Generar ID de ticket
            ticket_id = f"SM-{message.platform.value.upper()}-{message.message_id[:8]}"
            
            # Crear ticket
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO support_tickets
                (ticket_id, customer_email, subject, description, priority, status, 
                 source, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                ticket_id,
                customer_email,
                f"[{message.platform.value.upper()}] {self._extract_subject(message.content)}",
                message.content,
                priority,
                "open",
                f"social_{message.platform.value}",
                {
                    "platform": message.platform.value,
                    "message_id": message.message_id,
                    "author_username": message.author_username,
                    "author_name": message.author_name,
                    "message_url": message.url,
                    "message_type": message.message_type.value,
                    "metadata": message.metadata
                },
                datetime.now()
            ))
            
            self.db.commit()
            
            # Guardar mensaje original
            self._save_original_message(message, ticket_id)
            
            return SocialTicket(
                ticket_id=ticket_id,
                original_message=message,
                platform=message.platform,
                customer_email=customer_email,
                customer_username=message.author_username,
                priority=priority,
                status="open",
                created_at=datetime.now(),
                metadata={"source": "social_media"}
            )
            
        except Exception as e:
            logger.error(f"Error creando ticket desde mensaje social: {e}")
            self.db.rollback()
            raise
    
    def _analyze_priority(self, content: str) -> str:
        """Analizar contenido para determinar prioridad."""
        content_lower = content.lower()
        
        # Palabras críticas
        critical_words = ["urgent", "urgente", "critical", "crítico", "emergency", "emergencia",
                         "broken", "roto", "down", "caído", "not working", "no funciona"]
        if any(word in content_lower for word in critical_words):
            return "critical"
        
        # Palabras de alta prioridad
        high_words = ["issue", "problema", "error", "bug", "failing", "fallando",
                     "help", "ayuda", "support", "soporte"]
        if any(word in content_lower for word in high_words):
            return "high"
        
        # Detectar emojis negativos
        negative_emojis = ["😠", "😡", "😤", "😢", "😭", "💔", "❌", "🚫"]
        if any(emoji in content for emoji in negative_emojis):
            return "high"
        
        # Detectar múltiples signos de exclamación
        if content.count("!") >= 3:
            return "high"
        
        return "medium"
    
    def _extract_subject(self, content: str, max_length: int = 100) -> str:
        """Extraer sujeto del contenido."""
        # Limpiar menciones y hashtags
        cleaned = re.sub(r'@\w+', '', content)
        cleaned = re.sub(r'#\w+', '', cleaned)
        
        # Tomar primeras palabras
        words = cleaned.split()
        if len(words) > 15:
            return ' '.join(words[:15]) + "..."
        
        return cleaned[:max_length]
    
    def _find_customer_email(self, username: str, platform: SocialPlatform) -> Optional[str]:
        """Buscar email del cliente en base de datos."""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT customer_email
                FROM support_tickets
                WHERE metadata->>'author_username' = %s
                OR metadata->>'platform' = %s
                LIMIT 1
            """, (username, platform.value))
            
            result = cursor.fetchone()
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Error buscando email: {e}")
            return None
    
    def _save_original_message(self, message: SocialMessage, ticket_id: str):
        """Guardar mensaje original."""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO support_social_messages
                (ticket_id, platform, message_id, message_type, author_id, author_name,
                 author_username, content, url, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                ticket_id,
                message.platform.value,
                message.message_id,
                message.message_type.value,
                message.author_id,
                message.author_name,
                message.author_username,
                message.content,
                message.url,
                message.metadata,
                message.created_at
            ))
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error guardando mensaje original: {e}")
            self.db.rollback()
    
    def respond_to_social_message(self, ticket_id: str, response_text: str, agent_id: str) -> Dict[str, Any]:
        """
        Responder a mensaje de red social.
        
        Args:
            ticket_id: ID del ticket
            response_text: Texto de respuesta
            agent_id: ID del agente
            
        Returns:
            Información de respuesta
        """
        try:
            # Obtener información del ticket
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT metadata, customer_email
                FROM support_tickets
                WHERE ticket_id = %s
            """, (ticket_id,))
            
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Ticket {ticket_id} no encontrado")
            
            metadata = result[0]
            customer_email = result[1]
            
            platform = metadata.get("platform")
            author_username = metadata.get("author_username")
            message_url = metadata.get("message_url")
            
            # Preparar respuesta
            response = {
                "ticket_id": ticket_id,
                "platform": platform,
                "to_username": author_username,
                "response_text": response_text,
                "agent_id": agent_id,
                "responded_at": datetime.now()
            }
            
            # Guardar respuesta
            cursor.execute("""
                INSERT INTO support_social_responses
                (ticket_id, platform, to_username, response_text, agent_id, responded_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                ticket_id,
                platform,
                author_username,
                response_text,
                agent_id,
                datetime.now()
            ))
            
            # Actualizar ticket
            cursor.execute("""
                UPDATE support_tickets
                SET status = 'in_progress',
                    assigned_to = %s,
                    updated_at = %s
                WHERE ticket_id = %s
            """, (agent_id, datetime.now(), ticket_id))
            
            self.db.commit()
            
            return response
            
        except Exception as e:
            logger.error(f"Error respondiendo mensaje social: {e}")
            self.db.rollback()
            raise
    
    def get_social_tickets(self, platform: Optional[SocialPlatform] = None, status: Optional[str] = None, limit: int = 50) -> List[SocialTicket]:
        """
        Obtener tickets de redes sociales.
        
        Args:
            platform: Plataforma (opcional)
            status: Estado (opcional)
            limit: Límite de resultados
            
        Returns:
            Lista de tickets
        """
        try:
            cursor = self.db.cursor()
            
            query = """
                SELECT t.ticket_id, t.customer_email, t.priority, t.status, t.metadata, t.created_at,
                       sm.content, sm.author_username
                FROM support_tickets t
                LEFT JOIN support_social_messages sm ON t.ticket_id = sm.ticket_id
                WHERE t.source LIKE 'social_%'
            """
            
            params = []
            
            if platform:
                query += " AND t.metadata->>'platform' = %s"
                params.append(platform.value)
            
            if status:
                query += " AND t.status = %s"
                params.append(status)
            
            query += " ORDER BY t.created_at DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            
            tickets = []
            for row in cursor.fetchall():
                metadata = row[4] or {}
                platform_value = metadata.get("platform", "unknown")
                
                try:
                    platform_enum = SocialPlatform(platform_value)
                except ValueError:
                    platform_enum = SocialPlatform.TWITTER
                
                tickets.append(SocialTicket(
                    ticket_id=row[0],
                    original_message=SocialMessage(
                        platform=platform_enum,
                        message_id=metadata.get("message_id", ""),
                        message_type=SocialMessageType.MENTION,
                        author_id="",
                        author_name=metadata.get("author_name", ""),
                        author_username=row[7] or metadata.get("author_username", ""),
                        content=row[6] or "",
                        url=metadata.get("message_url", ""),
                        created_at=row[5],
                        metadata=metadata
                    ),
                    platform=platform_enum,
                    customer_email=row[1],
                    customer_username=row[7] or "",
                    priority=row[2],
                    status=row[3],
                    created_at=row[5],
                    metadata=metadata
                ))
            
            return tickets
            
        except Exception as e:
            logger.error(f"Error obteniendo tickets sociales: {e}")
            raise
    
    def monitor_mentions(self, platform: SocialPlatform, keywords: List[str], callback: callable):
        """
        Monitorear menciones (simulado - requiere implementación real de API).
        
        Args:
            platform: Plataforma a monitorear
            keywords: Palabras clave
            callback: Función a llamar cuando se detecte mención
        """
        # Esta función requeriría integración real con APIs de redes sociales
        # Por ahora es un placeholder
        logger.info(f"Monitoreando {platform.value} para keywords: {keywords}")
        logger.warning("Esta función requiere integración real con APIs de redes sociales")
        
        # Ejemplo de uso:
        # - Twitter: Twitter API v2
        # - Facebook: Facebook Graph API
        # - Instagram: Instagram Basic Display API
        # - LinkedIn: LinkedIn API



