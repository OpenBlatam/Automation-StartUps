"""
Módulo de Notificaciones Automáticas de Actualizaciones de Status.

Características:
- Envío automático de notificaciones cuando cambia el status
- Notificaciones por email, SMS, WhatsApp
- Templates personalizables por tipo de status
- Preferencias del cliente
"""
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

try:
    from .support_notifications_multi import (
        SupportNotificationManager,
        NotificationChannel,
        NotificationConfig,
        NotificationMessage
    )
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class StatusNotificationConfig:
    """Configuración de notificación de status."""
    status: str
    notify_customer: bool = True
    notify_agent: bool = False
    channels: List[str] = None  # email, sms, whatsapp
    template: Optional[str] = None


class SupportStatusNotifier:
    """Notificador de actualizaciones de status."""
    
    # Configuración por defecto de notificaciones por status
    STATUS_CONFIGS = {
        "open": StatusNotificationConfig(
            status="open",
            notify_customer=True,
            channels=["email"],
            template="ticket_created"
        ),
        "assigned": StatusNotificationConfig(
            status="assigned",
            notify_customer=True,
            channels=["email"],
            template="ticket_assigned"
        ),
        "in_progress": StatusNotificationConfig(
            status="in_progress",
            notify_customer=True,
            channels=["email"],
            template="ticket_in_progress"
        ),
        "waiting_customer": StatusNotificationConfig(
            status="waiting_customer",
            notify_customer=True,
            channels=["email", "sms"],
            template="waiting_customer"
        ),
        "resolved": StatusNotificationConfig(
            status="resolved",
            notify_customer=True,
            channels=["email"],
            template="ticket_resolved"
        ),
        "closed": StatusNotificationConfig(
            status="closed",
            notify_customer=True,
            channels=["email"],
            template="ticket_closed"
        ),
        "escalated": StatusNotificationConfig(
            status="escalated",
            notify_customer=True,
            channels=["email", "sms"],
            template="ticket_escalated"
        )
    }
    
    def __init__(
        self,
        db_connection: Any = None,
        notification_manager: Optional[SupportNotificationManager] = None
    ):
        """
        Inicializa el notificador de status.
        
        Args:
            db_connection: Conexión a BD
            notification_manager: Gestor de notificaciones
        """
        self.db_connection = db_connection
        self.notification_manager = notification_manager
    
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
                    description,
                    customer_email,
                    customer_name,
                    status,
                    priority,
                    assigned_agent_name,
                    assigned_department,
                    created_at,
                    resolved_at
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
                "description": row[2],
                "customer_email": row[3],
                "customer_name": row[4],
                "status": row[5],
                "priority": row[6],
                "assigned_agent_name": row[7],
                "assigned_department": row[8],
                "created_at": row[9],
                "resolved_at": row[10]
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo datos del ticket {ticket_id}: {e}")
            return None
    
    def generate_notification_template(
        self,
        template_type: str,
        ticket_data: Dict[str, Any],
        old_status: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Genera template de notificación.
        
        Args:
            template_type: Tipo de template
            ticket_data: Datos del ticket
            old_status: Status anterior (opcional)
            
        Returns:
            Dict con subject y body
        """
        ticket_id = ticket_data.get("ticket_id", "")
        subject_text = ticket_data.get("subject", "Ticket de Soporte")
        customer_name = ticket_data.get("customer_name", "Cliente")
        agent_name = ticket_data.get("assigned_agent_name", "nuestro equipo")
        status = ticket_data.get("status", "")
        
        templates = {
            "ticket_created": {
                "subject": f"Ticket #{ticket_id} creado - {subject_text}",
                "body": f"""Hola {customer_name},

Hemos recibido tu ticket de soporte #{ticket_id}.

Asunto: {subject_text}

Nuestro equipo revisará tu solicitud y te responderá pronto.

Puedes seguir el estado de tu ticket en cualquier momento.

Saludos,
Equipo de Soporte"""
            },
            "ticket_assigned": {
                "subject": f"Ticket #{ticket_id} asignado a {agent_name}",
                "body": f"""Hola {customer_name},

Tu ticket #{ticket_id} ha sido asignado a {agent_name}, quien se encargará de ayudarte.

Asunto: {subject_text}

{agent_name} se pondrá en contacto contigo pronto.

Saludos,
Equipo de Soporte"""
            },
            "ticket_in_progress": {
                "subject": f"Ticket #{ticket_id} en progreso",
                "body": f"""Hola {customer_name},

Te informamos que estamos trabajando en tu ticket #{ticket_id}.

Asunto: {subject_text}

Te mantendremos informado sobre cualquier actualización.

Saludos,
Equipo de Soporte"""
            },
            "waiting_customer": {
                "subject": f"Ticket #{ticket_id} - Esperando tu respuesta",
                "body": f"""Hola {customer_name},

Necesitamos información adicional para continuar con tu ticket #{ticket_id}.

Asunto: {subject_text}

Por favor, responde a este mensaje con la información solicitada para que podamos ayudarte.

Saludos,
Equipo de Soporte"""
            },
            "ticket_resolved": {
                "subject": f"Ticket #{ticket_id} resuelto",
                "body": f"""Hola {customer_name},

Tu ticket #{ticket_id} ha sido resuelto.

Asunto: {subject_text}

Esperamos que tu problema haya quedado solucionado. Si necesitas algo más, no dudes en contactarnos.

Nos gustaría conocer tu opinión sobre la atención recibida. Pronto recibirás una encuesta de satisfacción.

Saludos,
Equipo de Soporte"""
            },
            "ticket_closed": {
                "subject": f"Ticket #{ticket_id} cerrado",
                "body": f"""Hola {customer_name},

Tu ticket #{ticket_id} ha sido cerrado.

Asunto: {subject_text}

Gracias por contactarnos. Si tienes alguna otra consulta, estaremos encantados de ayudarte.

Saludos,
Equipo de Soporte"""
            },
            "ticket_escalated": {
                "subject": f"Ticket #{ticket_id} - Escalado a supervisor",
                "body": f"""Hola {customer_name},

Tu ticket #{ticket_id} ha sido escalado a un supervisor para asegurar una atención prioritaria.

Asunto: {subject_text}

Un supervisor revisará tu caso y te contactará pronto.

Saludos,
Equipo de Soporte"""
            }
        }
        
        template = templates.get(template_type, templates["ticket_created"])
        
        return {
            "subject": template["subject"],
            "body": template["body"]
        }
    
    def send_status_notification(
        self,
        ticket_id: str,
        new_status: str,
        old_status: Optional[str] = None
    ) -> bool:
        """
        Envía notificación de cambio de status.
        
        Args:
            ticket_id: ID del ticket
            new_status: Nuevo status
            old_status: Status anterior (opcional)
            
        Returns:
            True si se envió correctamente
        """
        # Obtener configuración para este status
        config = self.STATUS_CONFIGS.get(new_status)
        if not config or not config.notify_customer:
            return False
        
        # Obtener datos del ticket
        ticket_data = self.get_ticket_data(ticket_id)
        if not ticket_data:
            return False
        
        # Generar contenido de notificación
        template_content = self.generate_notification_template(
            config.template or "ticket_created",
            ticket_data,
            old_status
        )
        
        # Crear mensaje
        message = NotificationMessage(
            recipient=ticket_data["customer_email"],
            subject=template_content["subject"],
            body=template_content["body"],
            metadata={
                "ticket_id": ticket_id,
                "status": new_status,
                "old_status": old_status,
                "template": config.template
            }
        )
        
        # Enviar notificación
        if self.notification_manager:
            channels = [
                NotificationChannel(ch) for ch in config.channels
                if ch in ["email", "sms", "whatsapp"]
            ]
            
            results = self.notification_manager.send_notification(message, channels)
            return any(results.values())
        
        # Si no hay notification_manager, registrar en BD para procesamiento posterior
        if self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("""
                    INSERT INTO support_ticket_history (
                        ticket_id,
                        field_changed,
                        old_value,
                        new_value,
                        changed_by,
                        change_reason,
                        metadata
                    ) VALUES (
                        %s,
                        'status_notification',
                        %s,
                        %s,
                        'system',
                        'Notificación de status pendiente',
                        %s
                    )
                """, (
                    ticket_id,
                    old_status,
                    new_status,
                    {
                        "notification_sent": False,
                        "channels": config.channels,
                        "template": config.template
                    }
                ))
                self.db_connection.commit()
                cursor.close()
                return True
            except Exception as e:
                logger.error(f"Error registrando notificación: {e}")
                return False
        
        return False
    
    def notify_on_status_change(
        self,
        ticket_id: str,
        old_status: str,
        new_status: str
    ) -> bool:
        """
        Notifica cuando cambia el status (para usar en triggers).
        
        Args:
            ticket_id: ID del ticket
            old_status: Status anterior
            new_status: Nuevo status
            
        Returns:
            True si se notificó
        """
        # Solo notificar si cambió realmente
        if old_status == new_status:
            return False
        
        return self.send_status_notification(ticket_id, new_status, old_status)

