"""
Módulo de Solicitud Automática de Feedback Post-Resolución.

Características:
- Envío automático de solicitudes de feedback después de resolución
- Múltiples intentos con delays
- Tracking de respuestas
- Integración con sistema de feedback
"""
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta

try:
    from .support_notifications_multi import (
        SupportNotificationManager,
        NotificationChannel,
        NotificationMessage
    )
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class FeedbackRequest:
    """Solicitud de feedback."""
    ticket_id: str
    customer_email: str
    sent_at: datetime
    channel: str
    feedback_token: str
    status: str  # pending, sent, responded, expired


class SupportFeedbackAutomation:
    """Automatizador de solicitudes de feedback."""
    
    # Configuración de delays
    FEEDBACK_DELAYS = {
        "first": timedelta(hours=1),   # 1 hora después de resolución
        "second": timedelta(days=1),    # 1 día después si no responde
        "third": timedelta(days=3)       # 3 días después (último intento)
    }
    
    def __init__(
        self,
        db_connection: Any = None,
        notification_manager: Optional[SupportNotificationManager] = None,
        feedback_base_url: str = "https://support.example.com/feedback"
    ):
        """
        Inicializa el automatizador de feedback.
        
        Args:
            db_connection: Conexión a BD
            notification_manager: Gestor de notificaciones
            feedback_base_url: URL base para links de feedback
        """
        self.db_connection = db_connection
        self.notification_manager = notification_manager
        self.feedback_base_url = feedback_base_url
    
    def generate_feedback_token(self, ticket_id: str, customer_email: str) -> str:
        """
        Genera token único para feedback.
        
        Args:
            ticket_id: ID del ticket
            customer_email: Email del cliente
            
        Returns:
            Token único
        """
        import hashlib
        import secrets
        
        # Combinar ticket_id + email + timestamp + random
        combined = f"{ticket_id}:{customer_email}:{datetime.now().isoformat()}:{secrets.token_urlsafe(8)}"
        token = hashlib.sha256(combined.encode()).hexdigest()[:32]
        return token
    
    def get_ticket_data(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos del ticket.
        
        Args:
            ticket_id: ID del ticket
            
        Returns:
            Dict con datos del ticket o None
        """
        if not self.db_connection:
            return None
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT 
                    ticket_id,
                    subject,
                    customer_email,
                    customer_name,
                    assigned_agent_name,
                    resolved_at,
                    status
                FROM support_tickets
                WHERE ticket_id = %s
            """, (ticket_id,))
            
            row = cursor.fetchone()
            cursor.close()
            
            if not row:
                return None
            
            return {
                "ticket_id": row[0],
                "subject": row[1],
                "customer_email": row[2],
                "customer_name": row[3],
                "assigned_agent_name": row[4],
                "resolved_at": row[5],
                "status": row[6]
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo datos del ticket {ticket_id}: {e}")
            return None
    
    def check_feedback_sent(self, ticket_id: str) -> bool:
        """
        Verifica si ya se envió solicitud de feedback.
        
        Args:
            ticket_id: ID del ticket
            
        Returns:
            True si ya se envió
        """
        if not self.db_connection:
            return False
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT COUNT(*)
                FROM support_satisfaction_surveys
                WHERE ticket_id = %s
                AND sent_at IS NOT NULL
            """, (ticket_id,))
            
            count = cursor.fetchone()[0]
            cursor.close()
            
            return count > 0
            
        except Exception as e:
            logger.error(f"Error verificando feedback enviado: {e}")
            return False
    
    def check_feedback_responded(self, ticket_id: str) -> bool:
        """
        Verifica si el cliente ya respondió el feedback.
        
        Args:
            ticket_id: ID del ticket
            
        Returns:
            True si ya respondió
        """
        if not self.db_connection:
            return False
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT COUNT(*)
                FROM support_ticket_feedback
                WHERE ticket_id = %s
            """, (ticket_id,))
            
            count = cursor.fetchone()[0]
            cursor.close()
            
            return count > 0
            
        except Exception as e:
            logger.error(f"Error verificando feedback respondido: {e}")
            return False
    
    def create_feedback_survey(
        self,
        ticket_id: str,
        customer_email: str,
        feedback_token: str
    ) -> bool:
        """
        Crea registro de encuesta de feedback.
        
        Args:
            ticket_id: ID del ticket
            customer_email: Email del cliente
            feedback_token: Token de feedback
            
        Returns:
            True si se creó correctamente
        """
        if not self.db_connection:
            return False
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO support_satisfaction_surveys (
                    ticket_id,
                    customer_email,
                    survey_type,
                    sent_at
                ) VALUES (
                    %s,
                    %s,
                    'post_resolution',
                    NOW()
                )
                ON CONFLICT (ticket_id) DO UPDATE
                SET sent_at = NOW()
                RETURNING id
            """, (ticket_id, customer_email))
            
            row = cursor.fetchone()
            self.db_connection.commit()
            cursor.close()
            
            return row is not None
            
        except Exception as e:
            logger.error(f"Error creando encuesta de feedback: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False
    
    def generate_feedback_email(
        self,
        ticket_data: Dict[str, Any],
        feedback_token: str
    ) -> Dict[str, str]:
        """
        Genera contenido del email de feedback.
        
        Args:
            ticket_data: Datos del ticket
            feedback_token: Token de feedback
            
        Returns:
            Dict con subject y body
        """
        ticket_id = ticket_data.get("ticket_id", "")
        customer_name = ticket_data.get("customer_name", "Cliente")
        agent_name = ticket_data.get("assigned_agent_name", "nuestro equipo")
        subject_text = ticket_data.get("subject", "tu consulta")
        
        feedback_url = f"{self.feedback_base_url}/{feedback_token}"
        
        subject = f"¿Cómo calificarías la resolución de tu ticket #{ticket_id}?"
        
        body = f"""Hola {customer_name},

Recientemente resolvimos tu ticket #{ticket_id} sobre "{subject_text}".

Tu opinión es muy importante para nosotros. Nos encantaría saber cómo fue tu experiencia con {agent_name} y si tu problema se resolvió satisfactoriamente.

Por favor, tómate un momento para compartir tu feedback:

{feedback_url}

La encuesta toma menos de 2 minutos y nos ayuda a mejorar nuestro servicio.

Gracias por tu tiempo,
Equipo de Soporte"""
        
        return {
            "subject": subject,
            "body": body,
            "html_body": f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{ display: inline-block; padding: 12px 24px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .button:hover {{ background-color: #0056b3; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Hola {customer_name},</h2>
        <p>Recientemente resolvimos tu ticket <strong>#{ticket_id}</strong> sobre "{subject_text}".</p>
        <p>Tu opinión es muy importante para nosotros. Nos encantaría saber cómo fue tu experiencia con <strong>{agent_name}</strong> y si tu problema se resolvió satisfactoriamente.</p>
        <p>Por favor, tómate un momento para compartir tu feedback:</p>
        <p><a href="{feedback_url}" class="button">Compartir Feedback</a></p>
        <p>La encuesta toma menos de 2 minutos y nos ayuda a mejorar nuestro servicio.</p>
        <p>Gracias por tu tiempo,<br>Equipo de Soporte</p>
    </div>
</body>
</html>
"""
        }
    
    def send_feedback_request(
        self,
        ticket_id: str,
        attempt: str = "first"
    ) -> bool:
        """
        Envía solicitud de feedback.
        
        Args:
            ticket_id: ID del ticket
            attempt: Intento (first, second, third)
            
        Returns:
            True si se envió correctamente
        """
        # Verificar si ya respondió
        if self.check_feedback_responded(ticket_id):
            logger.info(f"Cliente ya respondió feedback para ticket {ticket_id}")
            return False
        
        # Obtener datos del ticket
        ticket_data = self.get_ticket_data(ticket_id)
        if not ticket_data:
            return False
        
        # Verificar que esté resuelto
        if ticket_data.get("status") != "resolved":
            return False
        
        customer_email = ticket_data.get("customer_email")
        if not customer_email:
            return False
        
        # Generar token
        feedback_token = self.generate_feedback_token(ticket_id, customer_email)
        
        # Crear registro de encuesta
        if not self.create_feedback_survey(ticket_id, customer_email, feedback_token):
            return False
        
        # Generar contenido
        email_content = self.generate_feedback_email(ticket_data, feedback_token)
        
        # Crear mensaje
        message = NotificationMessage(
            recipient=customer_email,
            subject=email_content["subject"],
            body=email_content["body"],
            html_body=email_content.get("html_body"),
            metadata={
                "ticket_id": ticket_id,
                "feedback_token": feedback_token,
                "attempt": attempt
            }
        )
        
        # Enviar notificación
        if self.notification_manager:
            results = self.notification_manager.send_notification(
                message,
                channels=[NotificationChannel.EMAIL]
            )
            return results.get(NotificationChannel.EMAIL, False)
        
        return False
    
    def auto_request_feedback_for_resolved_tickets(self) -> List[str]:
        """
        Solicita feedback automáticamente para tickets resueltos recientemente.
        
        Returns:
            Lista de ticket_ids procesados
        """
        if not self.db_connection:
            return []
        
        processed = []
        
        try:
            cursor = self.db_connection.cursor()
            
            # Buscar tickets resueltos en las últimas 24 horas
            cursor.execute("""
                SELECT 
                    ticket_id,
                    customer_email,
                    resolved_at
                FROM support_tickets
                WHERE status = 'resolved'
                AND resolved_at >= NOW() - INTERVAL '24 hours'
                AND resolved_at <= NOW() - INTERVAL '1 hour'
                AND NOT EXISTS (
                    SELECT 1 FROM support_ticket_feedback
                    WHERE support_ticket_feedback.ticket_id = support_tickets.ticket_id
                )
            """)
            
            for row in cursor.fetchall():
                ticket_id, customer_email, resolved_at = row
                
                # Verificar si ya se envió
                if self.check_feedback_sent(ticket_id):
                    continue
                
                # Enviar solicitud
                if self.send_feedback_request(ticket_id, "first"):
                    processed.append(ticket_id)
                    logger.info(f"Feedback solicitado para ticket {ticket_id}")
            
            cursor.close()
            return processed
            
        except Exception as e:
            logger.error(f"Error en auto-solicitud de feedback: {e}")
            return processed

