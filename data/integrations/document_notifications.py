"""
Sistema de Notificaciones Avanzado
===================================

Notificaciones multi-canal con templates y personalización.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging
import requests
import json

logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    """Canales de notificación"""
    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    WEBHOOK = "webhook"
    SMS = "sms"
    PUSH = "push"


@dataclass
class Notification:
    """Notificación"""
    channel: NotificationChannel
    recipient: str
    subject: Optional[str]
    message: str
    template: Optional[str] = None
    data: Dict[str, Any] = None
    priority: str = "normal"  # low, normal, high, urgent
    scheduled_at: Optional[str] = None


class NotificationService:
    """Servicio de notificaciones"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.templates = self._load_templates()
    
    def send_notification(self, notification: Notification) -> bool:
        """Envía notificación"""
        try:
            if notification.channel == NotificationChannel.EMAIL:
                return self._send_email(notification)
            elif notification.channel == NotificationChannel.SLACK:
                return self._send_slack(notification)
            elif notification.channel == NotificationChannel.TEAMS:
                return self._send_teams(notification)
            elif notification.channel == NotificationChannel.WEBHOOK:
                return self._send_webhook(notification)
            else:
                self.logger.warning(f"Canal no implementado: {notification.channel}")
                return False
        except Exception as e:
            self.logger.error(f"Error enviando notificación: {e}")
            return False
    
    def notify_document_processed(
        self,
        document: Dict[str, Any],
        recipients: List[str],
        channel: NotificationChannel = NotificationChannel.EMAIL
    ) -> List[bool]:
        """Notifica cuando un documento es procesado"""
        results = []
        
        template = self.templates.get("document_processed", {})
        message = self._render_template(template.get("message", ""), document)
        subject = self._render_template(template.get("subject", ""), document)
        
        for recipient in recipients:
            notification = Notification(
                channel=channel,
                recipient=recipient,
                subject=subject,
                message=message,
                template="document_processed",
                data=document
            )
            results.append(self.send_notification(notification))
        
        return results
    
    def notify_validation_errors(
        self,
        document_id: str,
        errors: List[str],
        recipients: List[str]
    ) -> List[bool]:
        """Notifica errores de validación"""
        results = []
        
        message = f"Documento {document_id} tiene errores de validación:\n"
        message += "\n".join(f"- {error}" for error in errors)
        
        for recipient in recipients:
            notification = Notification(
                channel=NotificationChannel.EMAIL,
                recipient=recipient,
                subject=f"Errores de Validación - {document_id}",
                message=message,
                priority="high"
            )
            results.append(self.send_notification(notification))
        
        return results
    
    def notify_quality_issues(
        self,
        document_id: str,
        quality_report: Dict[str, Any],
        recipients: List[str]
    ) -> List[bool]:
        """Notifica problemas de calidad"""
        issues = quality_report.get("issues", [])
        if not issues:
            return []
        
        message = f"Documento {document_id} tiene problemas de calidad:\n"
        message += "\n".join(f"- {issue}" for issue in issues)
        
        results = []
        for recipient in recipients:
            notification = Notification(
                channel=NotificationChannel.EMAIL,
                recipient=recipient,
                subject=f"Problemas de Calidad - {document_id}",
                message=message,
                priority="normal"
            )
            results.append(self.send_notification(notification))
        
        return results
    
    def _send_email(self, notification: Notification) -> bool:
        """Envía email"""
        webhook_url = self.config.get("email_webhook_url")
        if not webhook_url:
            self.logger.warning("Email webhook no configurado")
            return False
        
        payload = {
            "to": notification.recipient,
            "subject": notification.subject,
            "body": notification.message,
            "priority": notification.priority
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code in [200, 201, 202]
        except Exception as e:
            self.logger.error(f"Error enviando email: {e}")
            return False
    
    def _send_slack(self, notification: Notification) -> bool:
        """Envía notificación a Slack"""
        webhook_url = self.config.get("slack_webhook_url")
        if not webhook_url:
            self.logger.warning("Slack webhook no configurado")
            return False
        
        color_map = {
            "low": "#36a64f",
            "normal": "#36a64f",
            "high": "#ff9900",
            "urgent": "#ff0000"
        }
        
        payload = {
            "attachments": [{
                "color": color_map.get(notification.priority, "#36a64f"),
                "title": notification.subject or "Notificación",
                "text": notification.message,
                "footer": "Document Processing System",
                "ts": int(datetime.now().timestamp())
            }]
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Error enviando a Slack: {e}")
            return False
    
    def _send_teams(self, notification: Notification) -> bool:
        """Envía notificación a Microsoft Teams"""
        webhook_url = self.config.get("teams_webhook_url")
        if not webhook_url:
            self.logger.warning("Teams webhook no configurado")
            return False
        
        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": notification.subject,
            "themeColor": "0078D4",
            "title": notification.subject,
            "text": notification.message
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Error enviando a Teams: {e}")
            return False
    
    def _send_webhook(self, notification: Notification) -> bool:
        """Envía webhook genérico"""
        webhook_url = notification.recipient  # URL en recipient
        
        payload = {
            "subject": notification.subject,
            "message": notification.message,
            "data": notification.data,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code in [200, 201, 202]
        except Exception as e:
            self.logger.error(f"Error enviando webhook: {e}")
            return False
    
    def _load_templates(self) -> Dict[str, Dict[str, str]]:
        """Carga templates de notificaciones"""
        return {
            "document_processed": {
                "subject": "Documento Procesado: {{document_id}}",
                "message": """
                Documento procesado exitosamente:
                
                ID: {{document_id}}
                Tipo: {{document_type}}
                Archivo: {{original_filename}}
                Confianza: {{classification_confidence}}%
                
                Campos extraídos:
                {{#extracted_fields}}
                - {{key}}: {{value}}
                {{/extracted_fields}}
                """
            },
            "validation_error": {
                "subject": "Error de Validación: {{document_id}}",
                "message": "El documento {{document_id}} tiene errores de validación."
            },
            "quality_warning": {
                "subject": "Advertencia de Calidad: {{document_id}}",
                "message": "El documento {{document_id}} tiene problemas de calidad."
            }
        }
    
    def _render_template(self, template: str, data: Dict[str, Any]) -> str:
        """Renderiza template simple (simplificado)"""
        result = template
        for key, value in data.items():
            placeholder = f"{{{{key}}}}"
            result = result.replace(placeholder, str(value))
        
        return result

