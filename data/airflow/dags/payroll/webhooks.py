"""
Sistema de Webhooks para Nómina
Webhooks para eventos y notificaciones externas
"""

import logging
import hmac
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from enum import Enum

import requests

from .exceptions import PayrollError, ValidationError

logger = logging.getLogger(__name__)


class WebhookEventType(str, Enum):
    """Tipos de eventos de webhook"""
    PAYROLL_CALCULATED = "payroll.calculated"
    PAYROLL_APPROVED = "payroll.approved"
    PAYROLL_PAID = "payroll.paid"
    EXPENSE_APPROVED = "expense.approved"
    EXPENSE_REJECTED = "expense.rejected"
    APPROVAL_REQUESTED = "approval.requested"
    APPROVAL_APPROVED = "approval.approved"
    APPROVAL_REJECTED = "approval.rejected"
    ANOMALY_DETECTED = "anomaly.detected"
    MAINTENANCE_COMPLETED = "maintenance.completed"


class PayrollWebhookHandler:
    """Manejador de webhooks para nómina"""
    
    def __init__(
        self,
        webhook_url: str,
        secret_key: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Args:
            webhook_url: URL del webhook
            secret_key: Secret key para firmar webhooks (opcional)
            timeout: Timeout en segundos
        """
        self.webhook_url = webhook_url
        self.secret_key = secret_key
        self.timeout = timeout
    
    def send_webhook(
        self,
        event_type: WebhookEventType,
        data: Dict[str, Any],
        retry: bool = True,
        max_retries: int = 3
    ) -> bool:
        """Envía un webhook"""
        payload = {
            "event_type": event_type.value,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        # Firmar payload si hay secret key
        if self.secret_key:
            signature = self._generate_signature(json.dumps(payload))
            payload["signature"] = signature
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "PayrollSystem/1.0"
        }
        
        if self.secret_key:
            headers["X-Webhook-Signature"] = signature
        
        for attempt in range(max_retries if retry else 1):
            try:
                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                logger.info(f"Webhook sent successfully: {event_type.value}")
                return True
            except requests.exceptions.RequestException as e:
                logger.warning(f"Webhook attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to send webhook after {max_retries} attempts")
                    return False
        
        return False
    
    def _generate_signature(self, payload: str) -> str:
        """Genera firma HMAC para el payload"""
        if not self.secret_key:
            return ""
        
        return hmac.new(
            self.secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def verify_signature(
        self,
        payload: str,
        signature: str
    ) -> bool:
        """Verifica la firma de un webhook recibido"""
        if not self.secret_key:
            return False
        
        expected = self._generate_signature(payload)
        return hmac.compare_digest(expected, signature)


class PayrollWebhookReceiver:
    """Receptor de webhooks para nómina"""
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Args:
            secret_key: Secret key para verificar firmas
        """
        self.secret_key = secret_key
        self.handlers: Dict[WebhookEventType, Callable] = {}
    
    def register_handler(
        self,
        event_type: WebhookEventType,
        handler: Callable[[Dict[str, Any]], None]
    ) -> None:
        """Registra un handler para un tipo de evento"""
        self.handlers[event_type] = handler
    
    def process_webhook(
        self,
        payload: Dict[str, Any],
        signature: Optional[str] = None
    ) -> bool:
        """Procesa un webhook recibido"""
        # Verificar firma si hay secret key
        if self.secret_key and signature:
            payload_str = json.dumps(payload, sort_keys=True)
            if not self._verify_signature(payload_str, signature):
                raise ValidationError("Invalid webhook signature")
        
        # Extraer evento
        event_type_str = payload.get("event_type")
        if not event_type_str:
            raise ValidationError("Missing event_type in webhook payload")
        
        try:
            event_type = WebhookEventType(event_type_str)
        except ValueError:
            raise ValidationError(f"Unknown event type: {event_type_str}")
        
        # Ejecutar handler
        handler = self.handlers.get(event_type)
        if handler:
            try:
                handler(payload.get("data", {}))
                return True
            except Exception as e:
                logger.error(f"Error processing webhook handler: {e}")
                raise PayrollError(f"Webhook handler error: {e}")
        else:
            logger.warning(f"No handler registered for event type: {event_type}")
            return False
    
    def _verify_signature(self, payload: str, signature: str) -> bool:
        """Verifica la firma"""
        if not self.secret_key:
            return True  # Sin verificación si no hay secret
        
        expected = hmac.new(
            self.secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, signature)

