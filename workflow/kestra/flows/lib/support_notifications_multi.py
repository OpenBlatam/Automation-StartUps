"""
Sistema de Notificaciones Multicanal Avanzado.

Soporta:
- Email (SMTP, SendGrid, Mailgun, etc.)
- SMS (Twilio, AWS SNS, etc.)
- WhatsApp Business API
- Slack
- Microsoft Teams
- Push notifications
- Webhooks personalizados
"""
import logging
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    """Canales de notificación disponibles."""
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    SLACK = "slack"
    TEAMS = "teams"
    PUSH = "push"
    WEBHOOK = "webhook"


@dataclass
class NotificationConfig:
    """Configuración de notificación."""
    channel: NotificationChannel
    enabled: bool = True
    priority: int = 5  # 1-10, menor = más prioritario
    config: Dict[str, Any] = None


@dataclass
class NotificationMessage:
    """Mensaje de notificación."""
    recipient: str
    subject: Optional[str] = None
    body: str = ""
    html_body: Optional[str] = None
    metadata: Dict[str, Any] = None


class SupportNotificationManager:
    """Gestor de notificaciones multicanal."""
    
    def __init__(self, configs: List[NotificationConfig]):
        """
        Inicializa el gestor de notificaciones.
        
        Args:
            configs: Lista de configuraciones de canales
        """
        self.configs = {cfg.channel: cfg for cfg in configs if cfg.enabled}
        
        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
    
    def send_email(
        self,
        message: NotificationMessage,
        config: NotificationConfig
    ) -> bool:
        """Envía notificación por email."""
        if not REQUESTS_AVAILABLE:
            return False
        
        try:
            # Detectar proveedor de email
            api_url = config.config.get("api_url")
            
            if not api_url:
                # Fallback a SMTP
                return self._send_smtp(message, config)
            
            # Usar API de email (SendGrid, Mailgun, etc.)
            payload = {
                "to": message.recipient,
                "subject": message.subject,
                "text": message.body,
                "html": message.html_body
            }
            
            headers = {}
            if config.config.get("api_key"):
                headers["Authorization"] = f"Bearer {config.config['api_key']}"
            
            response = self.session.post(
                api_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info(f"Email sent to {message.recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def _send_smtp(
        self,
        message: NotificationMessage,
        config: NotificationConfig
    ) -> bool:
        """Envía email vía SMTP."""
        try:
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            import smtplib
            
            msg = MIMEMultipart("alternative")
            msg["Subject"] = message.subject
            msg["From"] = config.config.get("from_email", "support@example.com")
            msg["To"] = message.recipient
            
            part_text = MIMEText(message.body, "plain")
            msg.attach(part_text)
            
            if message.html_body:
                part_html = MIMEText(message.html_body, "html")
                msg.attach(part_html)
            
            smtp_host = config.config.get("smtp_host", os.getenv("SMTP_HOST"))
            smtp_port = config.config.get("smtp_port", 587)
            smtp_user = config.config.get("smtp_user", os.getenv("SMTP_USER"))
            smtp_password = config.config.get("smtp_password", os.getenv("SMTP_PASSWORD"))
            
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            if smtp_password:
                server.login(smtp_user, smtp_password)
            server.sendmail(msg["From"], [message.recipient], msg.as_string())
            server.quit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMTP email: {e}")
            return False
    
    def send_sms(
        self,
        message: NotificationMessage,
        config: NotificationConfig
    ) -> bool:
        """Envía notificación por SMS."""
        if not REQUESTS_AVAILABLE:
            return False
        
        try:
            provider = config.config.get("provider", "twilio")
            
            if provider == "twilio":
                api_url = f"https://api.twilio.com/2010-04-01/Accounts/{config.config['account_sid']}/Messages.json"
                
                payload = {
                    "From": config.config.get("from_number"),
                    "To": message.recipient,
                    "Body": message.body
                }
                
                response = self.session.post(
                    api_url,
                    data=payload,
                    auth=(config.config["account_sid"], config.config["auth_token"]),
                    timeout=10
                )
                response.raise_for_status()
                
                logger.info(f"SMS sent to {message.recipient}")
                return True
            
            elif provider == "aws_sns":
                # Implementar AWS SNS
                logger.warning("AWS SNS not yet implemented")
                return False
            
            return False
            
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
    
    def send_whatsapp(
        self,
        message: NotificationMessage,
        config: NotificationConfig
    ) -> bool:
        """Envía notificación por WhatsApp Business API."""
        if not REQUESTS_AVAILABLE:
            return False
        
        try:
            api_url = config.config.get("api_url", "https://graph.facebook.com/v18.0")
            phone_number_id = config.config.get("phone_number_id")
            access_token = config.config.get("access_token")
            
            url = f"{api_url}/{phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": message.recipient,
                "type": "text",
                "text": {
                    "body": message.body
                }
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            logger.info(f"WhatsApp message sent to {message.recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp: {e}")
            return False
    
    def send_notification(
        self,
        message: NotificationMessage,
        channels: Optional[List[NotificationChannel]] = None,
        priority_override: Optional[int] = None
    ) -> Dict[NotificationChannel, bool]:
        """
        Envía notificación por múltiples canales.
        
        Args:
            message: Mensaje a enviar
            channels: Lista de canales (None = todos los habilitados)
            priority_override: Prioridad override
            
        Returns:
            Dict con resultados por canal
        """
        results = {}
        channels_to_use = channels or list(self.configs.keys())
        
        # Ordenar por prioridad
        channels_to_use = sorted(
            channels_to_use,
            key=lambda c: self.configs.get(c, NotificationConfig(c)).priority
        )
        
        for channel in channels_to_use:
            if channel not in self.configs:
                continue
            
            config = self.configs[channel]
            priority = priority_override or config.priority
            
            try:
                if channel == NotificationChannel.EMAIL:
                    results[channel] = self.send_email(message, config)
                elif channel == NotificationChannel.SMS:
                    results[channel] = self.send_sms(message, config)
                elif channel == NotificationChannel.WHATSAPP:
                    results[channel] = self.send_whatsapp(message, config)
                elif channel == NotificationChannel.SLACK:
                    results[channel] = self._send_slack(message, config)
                elif channel == NotificationChannel.TEAMS:
                    results[channel] = self._send_teams(message, config)
                else:
                    results[channel] = False
                    
            except Exception as e:
                logger.error(f"Error sending {channel.value}: {e}")
                results[channel] = False
        
        return results
    
    def _send_slack(
        self,
        message: NotificationMessage,
        config: NotificationConfig
    ) -> bool:
        """Envía notificación a Slack."""
        webhook_url = config.config.get("webhook_url")
        if not webhook_url or not REQUESTS_AVAILABLE:
            return False
        
        payload = {
            "text": message.subject,
            "blocks": [{
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message.body
                }
            }]
        }
        
        try:
            response = self.session.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error sending Slack: {e}")
            return False
    
    def _send_teams(
        self,
        message: NotificationMessage,
        config: NotificationConfig
    ) -> bool:
        """Envía notificación a Microsoft Teams."""
        webhook_url = config.config.get("webhook_url")
        if not webhook_url or not REQUESTS_AVAILABLE:
            return False
        
        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": message.subject,
            "themeColor": "0078D4",
            "title": message.subject,
            "text": message.body
        }
        
        try:
            response = self.session.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error sending Teams: {e}")
            return False

