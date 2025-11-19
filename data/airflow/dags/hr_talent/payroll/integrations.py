"""
Integraciones con Sistemas Externos
QuickBooks, Stripe, sistemas de contabilidad, etc.
"""

import logging
from datetime import date
from decimal import Decimal
from typing import Dict, Any, Optional, List
import json
import requests

from .exceptions import PayrollError, ConfigurationError

logger = logging.getLogger(__name__)


class QuickBooksIntegration:
    """Integración con QuickBooks"""
    
    def __init__(
        self,
        access_token: str,
        realm_id: str,
        base_url: str = "https://sandbox-quickbooks.api.intuit.com"
    ):
        """
        Args:
            access_token: Token de acceso OAuth2
            realm_id: ID de la compañía
            base_url: URL base de la API (sandbox o producción)
        """
        self.access_token = access_token
        self.realm_id = realm_id
        self.base_url = base_url.rstrip('/')
    
    def create_payroll_expense(
        self,
        employee_name: str,
        amount: Decimal,
        expense_date: date,
        description: str,
        account_name: str = "Nómina"
    ) -> Optional[str]:
        """Crea un gasto de nómina en QuickBooks"""
        url = f"{self.base_url}/v3/company/{self.realm_id}/purchase"
        
        payload = {
            "PaymentType": "Cash",
            "AccountRef": {
                "name": account_name,
                "value": "1"  # Debe obtenerse de la cuenta real
            },
            "Line": [{
                "Amount": str(amount),
                "DetailType": "AccountBasedExpenseLineDetail",
                "AccountBasedExpenseLineDetail": {
                    "AccountRef": {
                        "name": account_name
                    }
                },
                "Description": description
            }],
            "TxnDate": expense_date.strftime("%Y-%m-%d"),
            "EntityRef": {
                "name": employee_name
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get("Purchase", {}).get("Id")
        except Exception as e:
            logger.error(f"Error creating QuickBooks expense: {e}")
            raise PayrollError(f"QuickBooks integration error: {e}")
    
    def sync_payroll_period(
        self,
        period_data: Dict[str, Any]
    ) -> bool:
        """Sincroniza un período de pago completo a QuickBooks"""
        try:
            # Crear gastos por cada empleado
            for employee_data in period_data.get("employees", []):
                self.create_payroll_expense(
                    employee_name=employee_data["name"],
                    amount=Decimal(str(employee_data["net_pay"])),
                    expense_date=period_data["pay_date"],
                    description=f"Nómina {period_data['period_start']} - {period_data['period_end']}"
                )
            
            return True
        except Exception as e:
            logger.error(f"Error syncing payroll period to QuickBooks: {e}")
            return False


class StripeIntegration:
    """Integración con Stripe para pagos"""
    
    def __init__(self, api_key: str):
        """
        Args:
            api_key: API key de Stripe
        """
        self.api_key = api_key
        self.base_url = "https://api.stripe.com/v1"
    
    def create_payout(
        self,
        employee_email: str,
        amount: Decimal,
        currency: str = "usd",
        description: Optional[str] = None
    ) -> Optional[str]:
        """Crea un payout en Stripe"""
        url = f"{self.base_url}/payouts"
        
        payload = {
            "amount": int(amount * 100),  # Stripe usa centavos
            "currency": currency,
            "destination": employee_email,  # Debe ser una cuenta conectada
            "description": description or f"Payroll payment for {employee_email}"
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            response = requests.post(url, data=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get("id")
        except Exception as e:
            logger.error(f"Error creating Stripe payout: {e}")
            return None


class AccountingIntegration:
    """Integración genérica con sistemas de contabilidad"""
    
    def __init__(
        self,
        api_url: str,
        api_key: str,
        provider: str = "generic"
    ):
        """
        Args:
            api_url: URL base de la API
            api_key: API key para autenticación
            provider: Proveedor (generic, xero, sage, etc.)
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.provider = provider
    
    def export_payroll_journal_entry(
        self,
        period_data: Dict[str, Any],
        journal_date: date
    ) -> bool:
        """Exporta período de pago como asiento contable"""
        url = f"{self.api_url}/journal-entries"
        
        # Preparar asiento contable
        entries = []
        
        # Débito: Gastos de nómina
        entries.append({
            "account": "Salaries Expense",
            "debit": float(period_data["total_gross_pay"]),
            "credit": 0.0,
            "description": "Payroll expenses"
        })
        
        # Crédito: Cuentas por pagar
        entries.append({
            "account": "Accounts Payable",
            "debit": 0.0,
            "credit": float(period_data["total_net_pay"]),
            "description": "Net payroll payable"
        })
        
        # Débito adicional: Deducciones
        if period_data["total_deductions"] > 0:
            entries.append({
                "account": "Payroll Deductions",
                "debit": float(period_data["total_deductions"]),
                "credit": 0.0,
                "description": "Payroll deductions"
            })
        
        payload = {
            "date": journal_date.isoformat(),
            "description": f"Payroll {period_data['period_start']} - {period_data['period_end']}",
            "entries": entries,
            "provider": self.provider
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error exporting journal entry: {e}")
            return False


class SlackIntegration:
    """Integración con Slack para notificaciones avanzadas"""
    
    def __init__(self, webhook_url: str):
        """
        Args:
            webhook_url: URL del webhook de Slack
        """
        self.webhook_url = webhook_url
    
    def send_payroll_summary(
        self,
        summary: Dict[str, Any],
        channel: Optional[str] = None
    ) -> bool:
        """Envía resumen de nómina a Slack con formato avanzado"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Resumen de Nómina"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Empleados:* {summary.get('employee_count', 0)}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Período:* {summary.get('period_start')} - {summary.get('period_end')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Bruto:* ${summary.get('total_gross_pay', 0):,.2f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Neto:* ${summary.get('total_net_pay', 0):,.2f}"
                    }
                ]
            }
        ]
        
        payload = {
            "blocks": blocks,
            "text": "Resumen de Nómina"
        }
        
        if channel:
            payload["channel"] = channel
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error sending Slack summary: {e}")
            return False

