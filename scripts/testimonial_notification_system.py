#!/usr/bin/env python3
"""
Sistema de Notificaciones Avanzado
Notificaciones por email, Slack, webhook, etc.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Tipos de notificación"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    TEAMS = "teams"
    DISCORD = "discord"


@dataclass
class Notification:
    """Notificación"""
    type: NotificationType
    title: str
    message: str
    priority: str  # "low", "medium", "high", "urgent"
    timestamp: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class NotificationSystem:
    """Sistema de notificaciones avanzado"""
    
    def __init__(self):
        """Inicializa el sistema de notificaciones"""
        self.configs = {}
        self.notification_history: List[Notification] = []
    
    def configure_email(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_email: str
    ):
        """Configura notificaciones por email"""
        self.configs['email'] = {
            'smtp_server': smtp_server,
            'smtp_port': smtp_port,
            'username': username,
            'password': password,
            'from_email': from_email
        }
        logger.info("Notificaciones por email configuradas")
    
    def configure_slack(self, webhook_url: str):
        """Configura notificaciones por Slack"""
        self.configs['slack'] = {
            'webhook_url': webhook_url
        }
        logger.info("Notificaciones por Slack configuradas")
    
    def configure_webhook(self, webhook_url: str, headers: Optional[Dict[str, str]] = None):
        """Configura notificaciones por webhook"""
        self.configs['webhook'] = {
            'webhook_url': webhook_url,
            'headers': headers or {}
        }
        logger.info("Notificaciones por webhook configuradas")
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = False
    ) -> bool:
        """Envía notificación por email"""
        if 'email' not in self.configs:
            logger.warning("Email no configurado")
            return False
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            config = self.configs['email']
            msg = MIMEMultipart()
            msg['From'] = config['from_email']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
            server.quit()
            
            notification = Notification(
                type=NotificationType.EMAIL,
                title=subject,
                message=body,
                priority="medium"
            )
            self.notification_history.append(notification)
            
            logger.info(f"Email enviado a {to_email}")
            return True
        except Exception as e:
            logger.error(f"Error al enviar email: {e}")
            return False
    
    def send_slack(
        self,
        message: str,
        channel: Optional[str] = None,
        username: Optional[str] = None
    ) -> bool:
        """Envía notificación por Slack"""
        if 'slack' not in self.configs:
            logger.warning("Slack no configurado")
            return False
        
        try:
            import requests
            
            webhook_url = self.configs['slack']['webhook_url']
            payload = {
                "text": message,
                "username": username or "Testimonial Bot"
            }
            if channel:
                payload["channel"] = channel
            
            response = requests.post(webhook_url, json=payload)
            
            if response.status_code == 200:
                notification = Notification(
                    type=NotificationType.SLACK,
                    title="Slack Notification",
                    message=message,
                    priority="medium"
                )
                self.notification_history.append(notification)
                logger.info("Notificación enviada a Slack")
                return True
            else:
                logger.error(f"Error al enviar a Slack: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error al enviar a Slack: {e}")
            return False
    
    def send_webhook(
        self,
        payload: Dict[str, Any]
    ) -> bool:
        """Envía notificación por webhook"""
        if 'webhook' not in self.configs:
            logger.warning("Webhook no configurado")
            return False
        
        try:
            import requests
            
            config = self.configs['webhook']
            response = requests.post(
                config['webhook_url'],
                json=payload,
                headers=config.get('headers', {})
            )
            
            if response.status_code in [200, 201]:
                notification = Notification(
                    type=NotificationType.WEBHOOK,
                    title="Webhook Notification",
                    message=str(payload),
                    priority="medium"
                )
                self.notification_history.append(notification)
                logger.info("Notificación enviada por webhook")
                return True
            else:
                logger.error(f"Error en webhook: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error al enviar webhook: {e}")
            return False
    
    def notify_post_generated(
        self,
        post_data: Dict[str, Any],
        channels: Optional[List[str]] = None
    ):
        """Notifica cuando se genera un post"""
        channels = channels or ['email']
        
        platform = post_data.get('platform', 'N/A')
        score = post_data.get('engagement_prediction', {}).get('predicted_score', 0)
        
        message = f"""
Nueva publicación generada:
- Plataforma: {platform}
- Score de Engagement: {score}/100
- Longitud: {post_data.get('length', 0)} caracteres
- Hashtags: {len(post_data.get('hashtags', []))}
        """.strip()
        
        for channel in channels:
            if channel == 'email' and 'email' in self.configs:
                self.send_email(
                    to_email=self.configs['email']['from_email'],
                    subject=f"Nueva publicación generada para {platform}",
                    body=message
                )
            elif channel == 'slack' and 'slack' in self.configs:
                self.send_slack(message)
            elif channel == 'webhook' and 'webhook' in self.configs:
                self.send_webhook({
                    "event": "post_generated",
                    "data": post_data
                })
    
    def notify_post_published(
        self,
        platform: str,
        post_id: str,
        channels: Optional[List[str]] = None
    ):
        """Notifica cuando se publica un post"""
        channels = channels or ['email']
        
        message = f"Post publicado exitosamente en {platform}. ID: {post_id}"
        
        for channel in channels:
            if channel == 'slack' and 'slack' in self.configs:
                self.send_slack(message)
            elif channel == 'webhook' and 'webhook' in self.configs:
                self.send_webhook({
                    "event": "post_published",
                    "platform": platform,
                    "post_id": post_id
                })
    
    def notify_high_engagement(
        self,
        post_data: Dict[str, Any],
        threshold: float = 80.0,
        channels: Optional[List[str]] = None
    ):
        """Notifica cuando el engagement predicho es alto"""
        score = post_data.get('engagement_prediction', {}).get('predicted_score', 0)
        
        if score >= threshold:
            channels = channels or ['slack']
            message = f"🚀 ¡Excelente! Post con score de {score}/100 generado."
            
            for channel in channels:
                if channel == 'slack' and 'slack' in self.configs:
                    self.send_slack(message)
    
    def get_notification_history(self, limit: int = 50) -> List[Notification]:
        """Obtiene historial de notificaciones"""
        return self.notification_history[-limit:]


