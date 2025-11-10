"""
Sistema de Notificaciones Avanzadas por Email
Templates de email, notificaciones personalizadas, multi-canal
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

logger = logging.getLogger("airflow.task")


class EmailNotificationService:
    """Servicio avanzado de notificaciones por email"""
    
    def __init__(
        self,
        smtp_host: str = None,
        smtp_port: int = None,
        smtp_user: str = None,
        smtp_password: str = None,
        from_email: str = None
    ):
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
        self.from_email = from_email or os.getenv("SMTP_FROM_EMAIL", "contracts@example.com")
    
    def send_contract_notification(
        self,
        to_email: str,
        to_name: str,
        notification_type: str,
        contract_data: Dict[str, Any],
        template_variables: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Envía notificación de contrato por email.
        
        Args:
            to_email: Email del destinatario
            to_name: Nombre del destinatario
            notification_type: Tipo de notificación
            contract_data: Datos del contrato
            template_variables: Variables adicionales para el template
            
        Returns:
            Dict con resultado del envío
        """
        # Obtener template de email
        email_template = self.get_email_template(notification_type)
        
        # Preparar variables
        variables = {
            "recipient_name": to_name,
            "contract_id": contract_data.get("contract_id"),
            "contract_title": contract_data.get("title"),
            "contract_type": contract_data.get("contract_type"),
            "signature_url": contract_data.get("esignature_url"),
            "expiration_date": contract_data.get("expiration_date"),
            **(template_variables or {})
        }
        
        # Generar contenido
        subject = self.render_template(email_template["subject"], variables)
        body_html = self.render_template(email_template["body_html"], variables)
        body_text = self.render_template(email_template["body_text"], variables)
        
        # Enviar email
        try:
            self.send_email(
                to_email=to_email,
                to_name=to_name,
                subject=subject,
                body_html=body_html,
                body_text=body_text
            )
            
            return {
                "sent": True,
                "to_email": to_email,
                "notification_type": notification_type,
                "sent_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return {
                "sent": False,
                "error": str(e),
                "to_email": to_email
            }
    
    def get_email_template(self, notification_type: str) -> Dict[str, str]:
        """Obtiene template de email por tipo"""
        templates = {
            "contract_created": {
                "subject": "Nuevo Contrato Creado: {{contract_title}}",
                "body_html": """
                <html>
                <body>
                    <h2>Hola {{recipient_name}},</h2>
                    <p>Se ha creado un nuevo contrato:</p>
                    <ul>
                        <li><strong>ID:</strong> {{contract_id}}</li>
                        <li><strong>Título:</strong> {{contract_title}}</li>
                        <li><strong>Tipo:</strong> {{contract_type}}</li>
                    </ul>
                    <p>El contrato está listo para ser enviado para firma.</p>
                </body>
                </html>
                """,
                "body_text": """
                Hola {{recipient_name}},
                
                Se ha creado un nuevo contrato:
                - ID: {{contract_id}}
                - Título: {{contract_title}}
                - Tipo: {{contract_type}}
                
                El contrato está listo para ser enviado para firma.
                """
            },
            "contract_sent_for_signature": {
                "subject": "Contrato Enviado para Firma: {{contract_title}}",
                "body_html": """
                <html>
                <body>
                    <h2>Hola {{recipient_name}},</h2>
                    <p>Se ha enviado un contrato para tu firma:</p>
                    <ul>
                        <li><strong>ID:</strong> {{contract_id}}</li>
                        <li><strong>Título:</strong> {{contract_title}}</li>
                    </ul>
                    <p><a href="{{signature_url}}">Firmar Contrato</a></p>
                </body>
                </html>
                """,
                "body_text": """
                Hola {{recipient_name}},
                
                Se ha enviado un contrato para tu firma:
                - ID: {{contract_id}}
                - Título: {{contract_title}}
                
                Firma aquí: {{signature_url}}
                """
            },
            "contract_signed": {
                "subject": "Contrato Firmado: {{contract_title}}",
                "body_html": """
                <html>
                <body>
                    <h2>Hola {{recipient_name}},</h2>
                    <p>El contrato <strong>{{contract_title}}</strong> ha sido firmado exitosamente.</p>
                    <p>ID del contrato: {{contract_id}}</p>
                </body>
                </html>
                """,
                "body_text": """
                Hola {{recipient_name}},
                
                El contrato {{contract_title}} ha sido firmado exitosamente.
                ID del contrato: {{contract_id}}
                """
            },
            "contract_expiring": {
                "subject": "Contrato Próximo a Expirar: {{contract_title}}",
                "body_html": """
                <html>
                <body>
                    <h2>Hola {{recipient_name}},</h2>
                    <p>El contrato <strong>{{contract_title}}</strong> expirará pronto.</p>
                    <ul>
                        <li><strong>Fecha de expiración:</strong> {{expiration_date}}</li>
                        <li><strong>ID:</strong> {{contract_id}}</li>
                    </ul>
                    <p>Por favor, revisa el contrato para renovación.</p>
                </body>
                </html>
                """,
                "body_text": """
                Hola {{recipient_name}},
                
                El contrato {{contract_title}} expirará pronto.
                Fecha de expiración: {{expiration_date}}
                ID: {{contract_id}}
                
                Por favor, revisa el contrato para renovación.
                """
            }
        }
        
        return templates.get(
            notification_type,
            templates["contract_created"]  # Default
        )
    
    def render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Renderiza template con variables"""
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result
    
    def send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        body_html: str,
        body_text: str
    ) -> None:
        """Envía email usando SMTP"""
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP no configurado, email no enviado")
            return
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{to_name} <{self.from_email}>"
        msg['To'] = to_email
        
        # Agregar partes
        part_text = MIMEText(body_text, 'plain')
        part_html = MIMEText(body_html, 'html')
        
        msg.attach(part_text)
        msg.attach(part_html)
        
        # Enviar
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)


def send_contract_email_notification(
    to_email: str,
    to_name: str,
    notification_type: str,
    contract_data: Dict[str, Any],
    template_variables: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Función helper para enviar notificación de contrato.
    
    Args:
        to_email: Email del destinatario
        to_name: Nombre del destinatario
        notification_type: Tipo de notificación
        contract_data: Datos del contrato
        template_variables: Variables adicionales
        
    Returns:
        Dict con resultado
    """
    service = EmailNotificationService()
    return service.send_contract_notification(
        to_email=to_email,
        to_name=to_name,
        notification_type=notification_type,
        contract_data=contract_data,
        template_variables=template_variables
    )

