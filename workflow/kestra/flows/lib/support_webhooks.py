"""
Sistema de Webhooks para Integraciones Externas.

Características:
- Webhooks configurables para eventos de tickets
- Retry automático con exponential backoff
- Signature verification (HMAC)
- Rate limiting
- Event filtering
"""
import logging
import hmac
import hashlib
import json
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type,
    )
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class WebhookConfig:
    """Configuración de webhook."""
    url: str
    secret: Optional[str] = None
    events: List[str] = None  # ticket.created, ticket.resolved, etc.
    enabled: bool = True
    timeout: int = 10
    retry_count: int = 3


@dataclass
class WebhookEvent:
    """Evento de webhook."""
    event_type: str
    ticket_id: str
    data: Dict[str, Any]
    timestamp: str
    signature: Optional[str] = None


class SupportWebhookManager:
    """Gestor de webhooks para tickets de soporte."""
    
    def __init__(self, webhooks: List[WebhookConfig]):
        """
        Inicializa el gestor de webhooks.
        
        Args:
            webhooks: Lista de configuraciones de webhooks
        """
        self.webhooks = [w for w in webhooks if w.enabled]
        
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
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """Genera firma HMAC para el payload."""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _verify_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Verifica firma HMAC."""
        expected = self._generate_signature(payload, secret)
        return hmac.compare_digest(expected, signature)
    
    def _send_webhook(
        self,
        webhook: WebhookConfig,
        event: WebhookEvent
    ) -> bool:
        """Envía un webhook."""
        if not REQUESTS_AVAILABLE:
            logger.warning("requests not available, cannot send webhook")
            return False
        
        payload = {
            "event": event.event_type,
            "ticket_id": event.ticket_id,
            "data": event.data,
            "timestamp": event.timestamp
        }
        
        payload_json = json.dumps(payload, sort_keys=True)
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SupportSystem/1.0"
        }
        
        # Agregar firma si hay secret
        if webhook.secret:
            signature = self._generate_signature(payload_json, webhook.secret)
            headers["X-Signature"] = signature
        
        try:
            response = self.session.post(
                webhook.url,
                data=payload_json,
                headers=headers,
                timeout=webhook.timeout
            )
            response.raise_for_status()
            
            logger.info(f"Webhook sent successfully to {webhook.url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send webhook to {webhook.url}: {e}")
            return False
    
    def _send_webhook_with_retry(
        self,
        webhook: WebhookConfig,
        event: WebhookEvent
    ) -> bool:
        """Envía webhook con retry."""
        if not TENACITY_AVAILABLE:
            return self._send_webhook(webhook, event)
        
        @retry(
            stop=stop_after_attempt(webhook.retry_count),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type(Exception)
        )
        def _retry_send():
            return self._send_webhook(webhook, event)
        
        try:
            return _retry_send()
        except Exception as e:
            logger.error(f"Failed to send webhook after retries: {e}")
            return False
    
    def trigger_event(
        self,
        event_type: str,
        ticket_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Dispara un evento a todos los webhooks configurados.
        
        Args:
            event_type: Tipo de evento (ticket.created, ticket.resolved, etc.)
            ticket_id: ID del ticket
            data: Datos del evento
            
        Returns:
            Dict con resultados por webhook
        """
        event = WebhookEvent(
            event_type=event_type,
            ticket_id=ticket_id,
            data=data,
            timestamp=datetime.now().isoformat()
        )
        
        results = {}
        
        for webhook in self.webhooks:
            # Verificar si el webhook está interesado en este evento
            if webhook.events and event_type not in webhook.events:
                continue
            
            result = self._send_webhook_with_retry(webhook, event)
            results[webhook.url] = {
                "success": result,
                "event_type": event_type,
                "timestamp": event.timestamp
            }
        
        return results


# Eventos predefinidos
EVENT_TICKET_CREATED = "ticket.created"
EVENT_TICKET_RESOLVED = "ticket.resolved"
EVENT_TICKET_ASSIGNED = "ticket.assigned"
EVENT_TICKET_ESCALATED = "ticket.escalated"
EVENT_TICKET_UPDATED = "ticket.updated"
EVENT_CHATBOT_RESOLVED = "chatbot.resolved"
EVENT_FEEDBACK_RECEIVED = "feedback.received"

