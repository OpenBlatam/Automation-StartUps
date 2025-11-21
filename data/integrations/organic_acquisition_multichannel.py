"""
Sistema Multi-Canal para Nurturing

Integración con SMS, WhatsApp, y otros canales además de email.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import requests
import os

logger = logging.getLogger(__name__)


class MultiChannelMessaging:
    """
    Gestor de mensajería multi-canal.
    """
    
    def __init__(self):
        """Inicializa el gestor multi-canal."""
        self.sms_api_key = os.getenv("SMS_API_KEY", "")
        self.sms_api_url = os.getenv("SMS_API_URL", "")
        self.whatsapp_api_key = os.getenv("WHATSAPP_API_KEY", "")
        self.whatsapp_api_url = os.getenv("WHATSAPP_API_URL", "")
        self.email_webhook = os.getenv("EMAIL_WEBHOOK_URL", "")
    
    def send_message(
        self,
        lead_id: str,
        email: str,
        phone: Optional[str],
        message_type: str,
        content: Dict[str, Any],
        preferred_channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envía mensaje por el canal preferido o disponible.
        
        Args:
            lead_id: ID del lead
            email: Email del lead
            phone: Teléfono del lead (opcional)
            message_type: Tipo de mensaje (nurturing, reminder, referral_invite)
            content: Contenido del mensaje
            preferred_channel: Canal preferido (email, sms, whatsapp)
        
        Returns:
            Dict con resultado del envío
        """
        # Determinar canal
        channel = self._determine_channel(
            email, phone, preferred_channel, message_type
        )
        
        # Enviar por canal
        if channel == "email":
            return self._send_email(email, content)
        elif channel == "sms" and phone:
            return self._send_sms(phone, content)
        elif channel == "whatsapp" and phone:
            return self._send_whatsapp(phone, content)
        else:
            # Fallback a email
            return self._send_email(email, content)
    
    def _determine_channel(
        self,
        email: str,
        phone: Optional[str],
        preferred: Optional[str],
        message_type: str
    ) -> str:
        """
        Determina el mejor canal para el mensaje.
        
        Reglas:
        - Reminders: SMS o WhatsApp (más directo)
        - Nurturing: Email (más contenido)
        - Referral invites: Email + SMS (más visibilidad)
        """
        if preferred:
            return preferred
        
        # Reglas por tipo de mensaje
        if message_type == "reminder":
            if phone:
                return "sms"  # SMS más directo para recordatorios
            return "email"
        
        elif message_type == "referral_invite":
            if phone:
                return "whatsapp"  # WhatsApp para referidos (más personal)
            return "email"
        
        else:  # nurturing, default
            return "email"
    
    def _send_email(
        self,
        email: str,
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Envía email."""
        if not self.email_webhook:
            return {"success": False, "error": "Email webhook no configurado"}
        
        try:
            payload = {
                "from": content.get("from", "marketing@tu-dominio.com"),
                "to": email,
                "subject": content.get("subject", ""),
                "text": content.get("text", ""),
                "html": content.get("html", content.get("text", ""))
            }
            
            response = requests.post(
                self.email_webhook,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            return {
                "success": True,
                "channel": "email",
                "message_id": response.json().get("message_id", "")
            }
            
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return {"success": False, "error": str(e), "channel": "email"}
    
    def _send_sms(
        self,
        phone: str,
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Envía SMS."""
        if not self.sms_api_url or not self.sms_api_key:
            return {"success": False, "error": "SMS API no configurada"}
        
        try:
            # Formatear teléfono
            phone_clean = phone.replace(" ", "").replace("-", "").replace("+", "")
            if not phone_clean.startswith("1"):
                phone_clean = "1" + phone_clean  # Asumiendo código de país
            
            payload = {
                "to": phone_clean,
                "message": content.get("text", ""),
                "from": content.get("from_number", "MARKETING")
            }
            
            headers = {
                "Authorization": f"Bearer {self.sms_api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.sms_api_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            return {
                "success": True,
                "channel": "sms",
                "message_id": response.json().get("sid", "")
            }
            
        except Exception as e:
            logger.error(f"Error enviando SMS: {e}")
            return {"success": False, "error": str(e), "channel": "sms"}
    
    def _send_whatsapp(
        self,
        phone: str,
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Envía mensaje por WhatsApp."""
        if not self.whatsapp_api_url or not self.whatsapp_api_key:
            return {"success": False, "error": "WhatsApp API no configurada"}
        
        try:
            # Formatear teléfono
            phone_clean = phone.replace(" ", "").replace("-", "").replace("+", "")
            
            payload = {
                "to": phone_clean,
                "type": "text",
                "text": {
                    "body": content.get("text", "")
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.whatsapp_api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.whatsapp_api_url}/messages",
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            return {
                "success": True,
                "channel": "whatsapp",
                "message_id": response.json().get("id", "")
            }
            
        except Exception as e:
            logger.error(f"Error enviando WhatsApp: {e}")
            return {"success": False, "error": str(e), "channel": "whatsapp"}
    
    def send_nurturing_sequence(
        self,
        lead_id: str,
        email: str,
        phone: Optional[str],
        sequence_step: int,
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Envía paso de secuencia de nurturing por canal apropiado.
        
        Para primeros pasos: Email (más contenido)
        Para recordatorios: SMS (más directo)
        """
        if sequence_step <= 2:
            # Primeros pasos: Email
            return self._send_email(email, content)
        else:
            # Pasos posteriores: SMS si disponible
            if phone:
                return self._send_sms(phone, {
                    "text": f"💡 {content.get('subject', 'Recordatorio')}\n\n{content.get('text', '')[:160]}...",
                    "from_number": "MARKETING"
                })
            return self._send_email(email, content)


# Schema SQL adicional para multi-canal
MULTICHANNEL_SCHEMA = """
-- Agregar columna de teléfono a organic_leads
ALTER TABLE organic_leads 
ADD COLUMN IF NOT EXISTS phone VARCHAR(32);

ALTER TABLE organic_leads 
ADD COLUMN IF NOT EXISTS preferred_channel VARCHAR(32) DEFAULT 'email';

-- Tabla de mensajes multi-canal
CREATE TABLE IF NOT EXISTS multichannel_messages (
    message_id SERIAL PRIMARY KEY,
    lead_id VARCHAR(128) NOT NULL REFERENCES organic_leads(lead_id) ON DELETE CASCADE,
    channel VARCHAR(32) NOT NULL CHECK (channel IN ('email', 'sms', 'whatsapp')),
    message_type VARCHAR(64) NOT NULL,
    content JSONB NOT NULL,
    status VARCHAR(32) DEFAULT 'sent' CHECK (status IN ('sent', 'delivered', 'failed', 'read')),
    external_message_id VARCHAR(128),
    sent_at TIMESTAMP NOT NULL DEFAULT NOW(),
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_multichannel_messages_lead ON multichannel_messages(lead_id);
CREATE INDEX IF NOT EXISTS idx_multichannel_messages_channel ON multichannel_messages(channel);
CREATE INDEX IF NOT EXISTS idx_multichannel_messages_sent ON multichannel_messages(sent_at DESC);
"""

