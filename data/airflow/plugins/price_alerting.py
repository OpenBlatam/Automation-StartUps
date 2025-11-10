"""
Sistema de Alertas Inteligentes para Automatización de Precios

Detecta y alerta sobre situaciones críticas:
- Cambios de precio extremos
- Fallos en extracción
- Discrepancias de mercado
- Problemas de publicación
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# Intentar importar notificaciones
try:
    from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False

try:
    from airflow.providers.email.operators.email import EmailOperator
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False


class AlertSeverity(Enum):
    """Niveles de severidad de alertas"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AlertRule:
    """Regla de alerta configurable"""
    name: str
    condition: callable
    severity: AlertSeverity
    message_template: str
    notify_slack: bool = True
    notify_email: bool = False
    threshold: Optional[float] = None


class PriceAlerting:
    """Sistema de alertas inteligentes para precios"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.alerts: List[Dict] = []
        self.rules = self._initialize_rules()
        self.slack_webhook = config.get('slack_webhook_url')
        self.email_recipients = config.get('email_recipients', [])
    
    def _initialize_rules(self) -> List[AlertRule]:
        """Inicializa reglas de alerta predefinidas"""
        rules = []
        
        # Alerta: Cambio de precio extremo
        rules.append(AlertRule(
            name="extreme_price_change",
            condition=lambda data: abs(data.get('price_change_percent', 0)) > 
                                  self.config.get('extreme_change_threshold', 30),
            severity=AlertSeverity.CRITICAL,
            message_template="🚨 Cambio de precio extremo: {product_name} - {price_change_percent:.2f}%",
            notify_slack=True,
            notify_email=True,
        ))
        
        # Alerta: Múltiples fallos de extracción
        rules.append(AlertRule(
            name="extraction_failures",
            condition=lambda data: data.get('extraction_failures', 0) > 
                                  self.config.get('max_extraction_failures', 3),
            severity=AlertSeverity.ERROR,
            message_template="⚠️ {extraction_failures} fuentes de extracción fallaron",
            notify_slack=True,
        ))
        
        # Alerta: Sin datos de competencia
        rules.append(AlertRule(
            name="no_competitor_data",
            condition=lambda data: data.get('competitor_prices_count', 0) == 0,
            severity=AlertSeverity.WARNING,
            message_template="⚠️ No se obtuvieron precios de competencia",
            notify_slack=True,
        ))
        
        # Alerta: Validación fallida
        rules.append(AlertRule(
            name="validation_failed",
            condition=lambda data: not data.get('validation_passed', True),
            severity=AlertSeverity.ERROR,
            message_template="❌ Validación de catálogo falló: {validation_errors}",
            notify_slack=True,
            notify_email=True,
        ))
        
        # Alerta: Publicación fallida
        rules.append(AlertRule(
            name="publish_failed",
            condition=lambda data: not data.get('publish_success', True),
            severity=AlertSeverity.CRITICAL,
            message_template="🚨 Fallo en publicación de catálogo: {publish_error}",
            notify_slack=True,
            notify_email=True,
        ))
        
        # Alerta: Discrepancia de mercado alta
        rules.append(AlertRule(
            name="high_market_discrepancy",
            condition=lambda data: data.get('market_discrepancy_percent', 0) > 
                                  self.config.get('max_market_discrepancy', 50),
            severity=AlertSeverity.WARNING,
            message_template="⚠️ Alta discrepancia con mercado: {market_discrepancy_percent:.2f}%",
            notify_slack=True,
        ))
        
        return rules
    
    def evaluate(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evalúa todas las reglas y genera alertas"""
        alerts = []
        
        for rule in self.rules:
            try:
                if rule.condition(data):
                    # Formatear mensaje
                    try:
                        message = rule.message_template.format(**data)
                    except KeyError:
                        message = rule.message_template
                    
                    alert = {
                        "rule": rule.name,
                        "severity": rule.severity.value,
                        "message": message,
                        "timestamp": datetime.utcnow().isoformat(),
                        "data": data,
                        "notify_slack": rule.notify_slack and bool(self.slack_webhook),
                        "notify_email": rule.notify_email and bool(self.email_recipients),
                    }
                    
                    alerts.append(alert)
                    self.alerts.append(alert)
                    
                    # Enviar notificaciones
                    if alert["notify_slack"]:
                        self._send_slack_alert(alert)
                    
                    if alert["notify_email"]:
                        self._send_email_alert(alert)
                    
            except Exception as e:
                logger.error(f"Error evaluando regla {rule.name}: {e}", exc_info=True)
        
        return alerts
    
    def _send_slack_alert(self, alert: Dict):
        """Envía alerta a Slack"""
        if not self.slack_webhook:
            return
        
        try:
            import requests
            
            severity_emoji = {
                "info": "ℹ️",
                "warning": "⚠️",
                "error": "❌",
                "critical": "🚨"
            }
            
            emoji = severity_emoji.get(alert["severity"], "⚠️")
            message = f"{emoji} *{alert['rule'].replace('_', ' ').title()}*\n{alert['message']}"
            
            payload = {
                "text": message,
                "username": "Price Automation Bot",
                "icon_emoji": ":money_with_wings:"
            }
            
            response = requests.post(self.slack_webhook, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Alerta enviada a Slack: {alert['rule']}")
            
        except Exception as e:
            logger.warning(f"Error enviando alerta a Slack: {e}")
    
    def _send_email_alert(self, alert: Dict):
        """Envía alerta por email"""
        if not self.email_recipients:
            return
        
        try:
            # Usar Airflow EmailOperator si está disponible
            # O implementar envío directo
            logger.info(f"Alerta por email (implementar): {alert['rule']}")
            # TODO: Implementar envío de email
        except Exception as e:
            logger.warning(f"Error enviando alerta por email: {e}")
    
    def get_alerts_summary(self) -> Dict:
        """Obtiene resumen de alertas"""
        if not self.alerts:
            return {"total": 0}
        
        by_severity = {}
        for alert in self.alerts:
            severity = alert["severity"]
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            "total": len(self.alerts),
            "by_severity": by_severity,
            "latest": self.alerts[-1] if self.alerts else None,
        }


def notify_slack(message: str, webhook_url: Optional[str] = None) -> bool:
    """Función helper para notificar a Slack"""
    try:
        import requests
        import os
        
        webhook = webhook_url or os.getenv('SLACK_WEBHOOK_URL')
        if not webhook:
            return False
        
        payload = {
            "text": message,
            "username": "Price Automation",
            "icon_emoji": ":money_with_wings:"
        }
        
        response = requests.post(webhook, json=payload, timeout=10)
        response.raise_for_status()
        return True
        
    except Exception as e:
        logger.warning(f"Error notificando a Slack: {e}")
        return False

