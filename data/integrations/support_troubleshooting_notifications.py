"""
Sistema de Notificaciones Avanzado para Troubleshooting
Soporta múltiples canales: email, SMS, push, Slack, Teams, etc.
"""

import json
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    """Canales de notificación soportados"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SLACK = "slack"
    TEAMS = "teams"
    DISCORD = "discord"
    WEBHOOK = "webhook"


class NotificationPriority(Enum):
    """Prioridad de notificación"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class NotificationConfig:
    """Configuración de notificación"""
    channel: NotificationChannel
    recipient: str
    template: Optional[str] = None
    priority: NotificationPriority = NotificationPriority.NORMAL
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TroubleshootingNotificationManager:
    """Gestiona notificaciones para eventos de troubleshooting"""
    
    def __init__(self):
        self.channel_handlers = {
            NotificationChannel.EMAIL: self._send_email,
            NotificationChannel.SMS: self._send_sms,
            NotificationChannel.SLACK: self._send_slack,
            NotificationChannel.TEAMS: self._send_teams,
            NotificationChannel.WEBHOOK: self._send_webhook,
        }
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """Carga plantillas de notificación"""
        self.templates = {
            "session_started": {
                "subject": "Sesión de troubleshooting iniciada",
                "body": "Hola {customer_name},\n\nHemos iniciado una sesión de troubleshooting para resolver tu problema: {problem_description}\n\nTe guiaremos paso a paso. Pronto recibirás las instrucciones del primer paso.\n\nSaludos,\nEquipo de Soporte"
            },
            "step_completed": {
                "subject": "Paso completado - Continuando",
                "body": "¡Excelente! Has completado el paso {step_number} exitosamente.\n\nContinuamos con el siguiente paso..."
            },
            "session_resolved": {
                "subject": "¡Problema resuelto!",
                "body": "Hola {customer_name},\n\n¡Excelente noticia! Has completado todos los pasos y tu problema debería estar resuelto.\n\nSi necesitas más ayuda, no dudes en contactarnos.\n\nSaludos,\nEquipo de Soporte"
            },
            "session_escalated": {
                "subject": "Ticket escalado a agente humano",
                "body": "Hola {customer_name},\n\nHemos escalado tu ticket a un agente humano que se pondrá en contacto contigo pronto.\n\nTicket ID: {ticket_id}\n\nSaludos,\nEquipo de Soporte"
            }
        }
    
    def send_notification(
        self,
        config: NotificationConfig,
        context: Dict
    ) -> Dict:
        """
        Envía una notificación
        
        Args:
            config: Configuración de la notificación
            context: Contexto con datos para la plantilla
            
        Returns:
            Resultado del envío
        """
        handler = self.channel_handlers.get(config.channel)
        if not handler:
            return {
                "success": False,
                "error": f"Channel {config.channel.value} not supported"
            }
        
        # Renderizar plantilla si existe
        if config.template and config.template in self.templates:
            template = self.templates[config.template]
            subject = template["subject"].format(**context)
            body = template["body"].format(**context)
        else:
            subject = context.get("subject", "Notificación")
            body = context.get("body", "")
        
        try:
            result = handler(config, subject, body, context)
            logger.info(f"Notificación enviada: {config.channel.value} -> {config.recipient}")
            return result
        except Exception as e:
            logger.error(f"Error enviando notificación: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _send_email(self, config: NotificationConfig, subject: str, body: str, context: Dict) -> Dict:
        """Envía email (implementación básica)"""
        # En producción, integrar con SendGrid, Mailgun, AWS SES, etc.
        logger.info(f"Email enviado a {config.recipient}: {subject}")
        return {
            "success": True,
            "channel": "email",
            "recipient": config.recipient,
            "message_id": f"email_{datetime.now().timestamp()}"
        }
    
    def _send_sms(self, config: NotificationConfig, subject: str, body: str, context: Dict) -> Dict:
        """Envía SMS (implementación básica)"""
        # En producción, integrar con Twilio, AWS SNS, etc.
        logger.info(f"SMS enviado a {config.recipient}: {body[:50]}...")
        return {
            "success": True,
            "channel": "sms",
            "recipient": config.recipient,
            "message_id": f"sms_{datetime.now().timestamp()}"
        }
    
    def _send_slack(self, config: NotificationConfig, subject: str, body: str, context: Dict) -> Dict:
        """Envía mensaje a Slack"""
        webhook_url = config.metadata.get("webhook_url")
        if not webhook_url:
            return {"success": False, "error": "Slack webhook URL not configured"}
        
        payload = {
            "text": subject,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{subject}*\n\n{body}"
                    }
                }
            ]
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.ok:
                return {
                    "success": True,
                    "channel": "slack",
                    "recipient": config.recipient
                }
            else:
                return {
                    "success": False,
                    "error": f"Slack API error: {response.status_code}"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _send_teams(self, config: NotificationConfig, subject: str, body: str, context: Dict) -> Dict:
        """Envía mensaje a Microsoft Teams"""
        webhook_url = config.metadata.get("webhook_url")
        if not webhook_url:
            return {"success": False, "error": "Teams webhook URL not configured"}
        
        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": subject,
            "themeColor": "0078D4",
            "title": subject,
            "text": body
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.ok:
                return {
                    "success": True,
                    "channel": "teams",
                    "recipient": config.recipient
                }
            else:
                return {
                    "success": False,
                    "error": f"Teams API error: {response.status_code}"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _send_webhook(self, config: NotificationConfig, subject: str, body: str, context: Dict) -> Dict:
        """Envía notificación vía webhook genérico"""
        webhook_url = config.metadata.get("webhook_url") or config.recipient
        if not webhook_url:
            return {"success": False, "error": "Webhook URL not provided"}
        
        payload = {
            "subject": subject,
            "body": body,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.ok:
                return {
                    "success": True,
                    "channel": "webhook",
                    "recipient": webhook_url
                }
            else:
                return {
                    "success": False,
                    "error": f"Webhook error: {response.status_code}"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def register_template(self, template_id: str, subject: str, body: str):
        """Registra una nueva plantilla"""
        self.templates[template_id] = {
            "subject": subject,
            "body": body
        }
        logger.info(f"Plantilla registrada: {template_id}")
    
    def send_bulk_notifications(
        self,
        configs: List[NotificationConfig],
        context: Dict
    ) -> List[Dict]:
        """Envía múltiples notificaciones"""
        results = []
        for config in configs:
            result = self.send_notification(config, context)
            results.append(result)
        return results



