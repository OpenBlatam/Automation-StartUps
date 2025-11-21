"""
Módulo de Notificaciones para Sistema de Contratos
Incluye notificaciones por Slack, Email y otros canales
"""

from __future__ import annotations

import json
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger("airflow.task")


class ContractNotificationManager:
    """Gestor de notificaciones para contratos"""
    
    def __init__(self):
        self.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL", "")
        self.email_enabled = os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "false").lower() == "true"
        self.slack_enabled = bool(self.slack_webhook_url)
    
    def notify_contract_created(self, contract_id: str, contract_data: Dict[str, Any]) -> bool:
        """Notifica cuando se crea un contrato"""
        message = f"📄 *Nuevo Contrato Creado*\n"
        message += f"• ID: `{contract_id}`\n"
        message += f"• Título: {contract_data.get('title', 'N/A')}\n"
        message += f"• Tipo: {contract_data.get('contract_type', 'N/A')}\n"
        message += f"• Parte Principal: {contract_data.get('primary_party_name', 'N/A')}\n"
        message += f"• Estado: {contract_data.get('status', 'draft')}\n"
        
        return self._send_slack_notification(message)
    
    def notify_contract_sent_for_signature(self, contract_id: str, contract_data: Dict[str, Any]) -> bool:
        """Notifica cuando se envía un contrato para firma"""
        message = f"✍️ *Contrato Enviado para Firma*\n"
        message += f"• ID: `{contract_id}`\n"
        message += f"• Título: {contract_data.get('title', 'N/A')}\n"
        message += f"• Proveedor: {contract_data.get('provider', 'N/A')}\n"
        message += f"• URL: {contract_data.get('esignature_url', 'N/A')}\n"
        
        if contract_data.get('envelope_id'):
            message += f"• Envelope ID: `{contract_data.get('envelope_id')}`\n"
        
        return self._send_slack_notification(message)
    
    def notify_contract_signed(self, contract_id: str, contract_data: Dict[str, Any]) -> bool:
        """Notifica cuando un contrato es completamente firmado"""
        message = f"✅ *Contrato Firmado Completamente*\n"
        message += f"• ID: `{contract_id}`\n"
        message += f"• Título: {contract_data.get('title', 'N/A')}\n"
        message += f"• Firmado por: {contract_data.get('primary_party_name', 'N/A')}\n"
        message += f"• Fecha de Firma: {contract_data.get('signed_date', 'N/A')}\n"
        
        return self._send_slack_notification(message, color="good")
    
    def notify_contract_expiring_soon(self, contract_id: str, days_until_expiration: int, contract_data: Dict[str, Any]) -> bool:
        """Notifica cuando un contrato está próximo a expirar"""
        message = f"⚠️ *Contrato Próximo a Expirar*\n"
        message += f"• ID: `{contract_id}`\n"
        message += f"• Título: {contract_data.get('title', 'N/A')}\n"
        message += f"• Días hasta expiración: {days_until_expiration}\n"
        message += f"• Fecha de expiración: {contract_data.get('expiration_date', 'N/A')}\n"
        message += f"• Auto-renovar: {'Sí' if contract_data.get('auto_renew') else 'No'}\n"
        
        color = "warning" if days_until_expiration > 7 else "danger"
        return self._send_slack_notification(message, color=color)
    
    def notify_contract_renewed(self, original_contract_id: str, new_contract_id: str, renewal_data: Dict[str, Any]) -> bool:
        """Notifica cuando se renueva un contrato"""
        message = f"🔄 *Contrato Renovado*\n"
        message += f"• Contrato Original: `{original_contract_id}`\n"
        message += f"• Nuevo Contrato: `{new_contract_id}`\n"
        message += f"• Fecha de Renovación: {renewal_data.get('renewal_date', 'N/A')}\n"
        
        return self._send_slack_notification(message, color="good")
    
    def notify_signature_reminder(self, contract_id: str, signer_email: str, days_since_sent: int) -> bool:
        """Notifica recordatorio de firma pendiente"""
        message = f"⏰ *Recordatorio: Firma Pendiente*\n"
        message += f"• Contrato ID: `{contract_id}`\n"
        message += f"• Firmante: {signer_email}\n"
        message += f"• Días desde envío: {days_since_sent}\n"
        message += f"• Acción: Por favor revisa y firma el contrato\n"
        
        return self._send_slack_notification(message, color="warning")
    
    def _send_slack_notification(self, message: str, color: str = None) -> bool:
        """Envía notificación a Slack"""
        if not self.slack_enabled or not REQUESTS_AVAILABLE:
            return False
        
        try:
            payload = {
                "text": "Notificación de Sistema de Contratos",
                "attachments": [
                    {
                        "color": color or "#36a64f",
                        "text": message,
                        "footer": "Sistema de Gestión de Contratos",
                        "ts": int(datetime.now().timestamp())
                    }
                ]
            }
            
            response = requests.post(
                self.slack_webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info("Notificación Slack enviada exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error enviando notificación Slack: {e}")
            return False


def send_contract_notification(
    notification_type: str,
    contract_id: str,
    contract_data: Dict[str, Any],
    additional_data: Dict[str, Any] = None
) -> bool:
    """
    Función helper para enviar notificaciones de contratos.
    
    Args:
        notification_type: Tipo de notificación ('created', 'sent', 'signed', 'expiring', 'renewed', 'reminder')
        contract_id: ID del contrato
        contract_data: Datos del contrato
        additional_data: Datos adicionales según el tipo
        
    Returns:
        True si se envió exitosamente, False en caso contrario
    """
    manager = ContractNotificationManager()
    
    if notification_type == "created":
        return manager.notify_contract_created(contract_id, contract_data)
    elif notification_type == "sent":
        return manager.notify_contract_sent_for_signature(contract_id, contract_data)
    elif notification_type == "signed":
        return manager.notify_contract_signed(contract_id, contract_data)
    elif notification_type == "expiring":
        days = additional_data.get("days_until_expiration", 0) if additional_data else 0
        return manager.notify_contract_expiring_soon(contract_id, days, contract_data)
    elif notification_type == "renewed":
        original_id = additional_data.get("original_contract_id", "") if additional_data else ""
        new_id = additional_data.get("new_contract_id", "") if additional_data else ""
        return manager.notify_contract_renewed(original_id, new_id, contract_data)
    elif notification_type == "reminder":
        signer_email = additional_data.get("signer_email", "") if additional_data else ""
        days_since = additional_data.get("days_since_sent", 0) if additional_data else 0
        return manager.notify_signature_reminder(contract_id, signer_email, days_since)
    else:
        logger.warning(f"Tipo de notificación no reconocido: {notification_type}")
        return False

