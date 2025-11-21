"""
Sistema de Notificaciones para Nómina
Envía notificaciones por email, Slack, webhooks, etc.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import date
from decimal import Decimal
import requests

from .exceptions import PayrollError

logger = logging.getLogger(__name__)


class PayrollNotifier:
    """Notificador de eventos de nómina"""
    
    def __init__(
        self,
        slack_webhook_url: Optional[str] = None,
        email_api_url: Optional[str] = None,
        webhook_url: Optional[str] = None,
    ):
        """
        Args:
            slack_webhook_url: URL de webhook de Slack
            email_api_url: URL de API para envío de emails
            webhook_url: URL de webhook genérico
        """
        self.slack_webhook_url = slack_webhook_url
        self.email_api_url = email_api_url
        self.webhook_url = webhook_url
    
    def notify_payroll_completed(
        self,
        employee_id: str,
        employee_name: str,
        period_start: date,
        period_end: date,
        net_pay: Decimal,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Notifica que el cálculo de nómina se completó"""
        message = (
            f"✅ Nómina procesada para {employee_name} ({employee_id})\n"
            f"Período: {period_start} a {period_end}\n"
            f"Pago Neto: ${net_pay:,.2f}"
        )
        
        if details:
            message += f"\nHoras: {details.get('hours', 0)}"
            message += f"\nDeducciones: ${details.get('deductions', 0):,.2f}"
        
        return self._send_notification(message, "payroll_completed", {
            "employee_id": employee_id,
            "employee_name": employee_name,
            "period_start": str(period_start),
            "period_end": str(period_end),
            "net_pay": float(net_pay),
            **({"details": details} if details else {})
        })
    
    def notify_payroll_error(
        self,
        employee_id: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Notifica un error en el procesamiento"""
        message = (
            f"❌ Error procesando nómina para {employee_id}\n"
            f"Error: {error_message}"
        )
        
        return self._send_notification(message, "payroll_error", {
            "employee_id": employee_id,
            "error_message": error_message,
            **({"context": context} if context else {})
        })
    
    def notify_expense_approved(
        self,
        employee_id: str,
        receipt_id: int,
        amount: Decimal,
        description: Optional[str] = None
    ) -> bool:
        """Notifica que un gasto fue aprobado"""
        message = (
            f"✅ Gasto aprobado\n"
            f"Empleado: {employee_id}\n"
            f"Recibo: {receipt_id}\n"
            f"Monto: ${amount:,.2f}"
        )
        
        if description:
            message += f"\nDescripción: {description}"
        
        return self._send_notification(message, "expense_approved", {
            "employee_id": employee_id,
            "receipt_id": receipt_id,
            "amount": float(amount),
            "description": description
        })
    
    def notify_expense_requires_review(
        self,
        employee_id: str,
        receipt_id: int,
        reason: str
    ) -> bool:
        """Notifica que un gasto requiere revisión manual"""
        message = (
            f"⚠️ Gasto requiere revisión\n"
            f"Empleado: {employee_id}\n"
            f"Recibo: {receipt_id}\n"
            f"Razón: {reason}"
        )
        
        return self._send_notification(message, "expense_review_required", {
            "employee_id": employee_id,
            "receipt_id": receipt_id,
            "reason": reason
        })
    
    def notify_batch_summary(
        self,
        total_processed: int,
        successful: int,
        failed: int,
        total_gross: Decimal,
        total_net: Decimal
    ) -> bool:
        """Notifica resumen de procesamiento por lotes"""
        message = (
            f"📊 Resumen de Procesamiento de Nómina\n"
            f"Procesados: {total_processed}\n"
            f"✅ Exitosos: {successful}\n"
            f"❌ Fallidos: {failed}\n"
            f"Total Bruto: ${total_gross:,.2f}\n"
            f"Total Neto: ${total_net:,.2f}"
        )
        
        return self._send_notification(message, "batch_summary", {
            "total_processed": total_processed,
            "successful": successful,
            "failed": failed,
            "total_gross": float(total_gross),
            "total_net": float(total_net)
        })
    
    def _send_notification(
        self,
        message: str,
        event_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """Envía notificación a todos los canales configurados"""
        success = True
        
        # Slack
        if self.slack_webhook_url:
            try:
                self._send_slack(message, data)
            except Exception as e:
                logger.error(f"Error sending Slack notification: {e}")
                success = False
        
        # Email
        if self.email_api_url:
            try:
                self._send_email(message, event_type, data)
            except Exception as e:
                logger.error(f"Error sending email notification: {e}")
                success = False
        
        # Webhook genérico
        if self.webhook_url:
            try:
                self._send_webhook(message, event_type, data)
            except Exception as e:
                logger.error(f"Error sending webhook notification: {e}")
                success = False
        
        return success
    
    def _send_slack(self, message: str, data: Dict[str, Any]) -> None:
        """Envía notificación a Slack"""
        payload = {
            "text": message,
            "attachments": [{
                "color": "good" if "✅" in message else "danger" if "❌" in message else "warning",
                "fields": [
                    {"title": k, "value": str(v), "short": True}
                    for k, v in data.items()
                ]
            }]
        }
        
        response = requests.post(
            self.slack_webhook_url,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
    
    def _send_email(self, message: str, event_type: str, data: Dict[str, Any]) -> None:
        """Envía notificación por email"""
        payload = {
            "subject": f"Payroll Notification: {event_type}",
            "body": message,
            "event_type": event_type,
            "data": data
        }
        
        response = requests.post(
            self.email_api_url,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
    
    def _send_webhook(self, message: str, event_type: str, data: Dict[str, Any]) -> None:
        """Envía notificación a webhook genérico"""
        payload = {
            "event_type": event_type,
            "message": message,
            "data": data,
            "timestamp": str(date.today())
        }
        
        response = requests.post(
            self.webhook_url,
            json=payload,
            timeout=10
        )
        response.raise_for_status()





