"""
Integración con Sistemas de Alertas Externos.

Proporciona integración con:
- PagerDuty
- Opsgenie
- Datadog
- New Relic
- Custom webhooks
"""
import logging
import os
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Severidades de alerta."""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Alert:
    """Alerta para sistemas externos."""
    title: str
    message: str
    severity: AlertSeverity
    source: str = "backup-system"
    timestamp: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class PagerDutyIntegration:
    """Integración con PagerDuty."""
    
    def __init__(self, integration_key: Optional[str] = None):
        """
        Inicializa integración con PagerDuty.
        
        Args:
            integration_key: Integration key de PagerDuty
        """
        self.integration_key = integration_key or os.getenv("PAGERDUTY_INTEGRATION_KEY")
        self.api_url = "https://events.pagerduty.com/v2/enqueue"
    
    def send_alert(self, alert: Alert) -> bool:
        """
        Envía alerta a PagerDuty.
        
        Args:
            alert: Alerta a enviar
        """
        if not self.integration_key:
            logger.warning("PagerDuty integration key not configured")
            return False
        
        try:
            # Mapear severidad
            severity_map = {
                AlertSeverity.CRITICAL: "critical",
                AlertSeverity.ERROR: "error",
                AlertSeverity.WARNING: "warning",
                AlertSeverity.INFO: "info"
            }
            
            payload = {
                "routing_key": self.integration_key,
                "event_action": "trigger",
                "payload": {
                    "summary": alert.title,
                    "source": alert.source,
                    "severity": severity_map.get(alert.severity, "warning"),
                    "custom_details": alert.details or {}
                }
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            
            logger.info(f"PagerDuty alert sent: {alert.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send PagerDuty alert: {e}")
            return False


class OpsgenieIntegration:
    """Integración con Opsgenie."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa integración con Opsgenie.
        
        Args:
            api_key: API key de Opsgenie
        """
        self.api_key = api_key or os.getenv("OPSGENIE_API_KEY")
        self.api_url = "https://api.opsgenie.com/v2/alerts"
    
    def send_alert(self, alert: Alert) -> bool:
        """Envía alerta a Opsgenie."""
        if not self.api_key:
            logger.warning("Opsgenie API key not configured")
            return False
        
        try:
            # Mapear severidad
            priority_map = {
                AlertSeverity.CRITICAL: "P1",
                AlertSeverity.ERROR: "P2",
                AlertSeverity.WARNING: "P3",
                AlertSeverity.INFO: "P4"
            }
            
            payload = {
                "message": alert.title,
                "description": alert.message,
                "priority": priority_map.get(alert.severity, "P3"),
                "source": alert.source,
                "details": alert.details or {}
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers={
                    "Authorization": f"GenieKey {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=10
            )
            response.raise_for_status()
            
            logger.info(f"Opsgenie alert sent: {alert.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Opsgenie alert: {e}")
            return False


class DatadogIntegration:
    """Integración con Datadog."""
    
    def __init__(self, api_key: Optional[str] = None, app_key: Optional[str] = None):
        """
        Inicializa integración con Datadog.
        
        Args:
            api_key: API key de Datadog
            app_key: Application key de Datadog
        """
        self.api_key = api_key or os.getenv("DATADOG_API_KEY")
        self.app_key = app_key or os.getenv("DATADOG_APP_KEY")
        self.api_url = "https://api.datadoghq.com/api/v1/events"
    
    def send_alert(self, alert: Alert) -> bool:
        """Envía alerta/evento a Datadog."""
        if not self.api_key:
            logger.warning("Datadog API key not configured")
            return False
        
        try:
            # Mapear severidad a nivel de alerta
            alert_type_map = {
                AlertSeverity.CRITICAL: "error",
                AlertSeverity.ERROR: "error",
                AlertSeverity.WARNING: "warning",
                AlertSeverity.INFO: "info"
            }
            
            payload = {
                "title": alert.title,
                "text": alert.message,
                "alert_type": alert_type_map.get(alert.severity, "warning"),
                "source_type_name": alert.source,
                "tags": [f"severity:{alert.severity.value}", "backup-system"]
            }
            
            if alert.details:
                payload["text"] += f"\n\nDetails: {alert.details}"
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers={
                    "DD-API-KEY": self.api_key,
                    "DD-APPLICATION-KEY": self.app_key,
                    "Content-Type": "application/json"
                },
                timeout=10
            )
            response.raise_for_status()
            
            logger.info(f"Datadog event sent: {alert.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Datadog event: {e}")
            return False


class MultiAlertManager:
    """Gestor de alertas multi-canal."""
    
    def __init__(self):
        """Inicializa gestor multi-canal."""
        self.integrations = {}
        
        # Inicializar integraciones disponibles
        pagerduty_key = os.getenv("PAGERDUTY_INTEGRATION_KEY")
        if pagerduty_key:
            self.integrations['pagerduty'] = PagerDutyIntegration(pagerduty_key)
        
        opsgenie_key = os.getenv("OPSGENIE_API_KEY")
        if opsgenie_key:
            self.integrations['opsgenie'] = OpsgenieIntegration(opsgenie_key)
        
        datadog_api_key = os.getenv("DATADOG_API_KEY")
        datadog_app_key = os.getenv("DATADOG_APP_KEY")
        if datadog_api_key:
            self.integrations['datadog'] = DatadogIntegration(datadog_api_key, datadog_app_key)
    
    def send_alert(
        self,
        alert: Alert,
        channels: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Envía alerta a múltiples canales.
        
        Args:
            alert: Alerta a enviar
            channels: Lista de canales (None = todos disponibles)
        
        Returns:
            Dict con resultados por canal
        """
        results = {}
        channels_to_use = channels or list(self.integrations.keys())
        
        for channel in channels_to_use:
            if channel not in self.integrations:
                logger.warning(f"Channel {channel} not available")
                results[channel] = False
                continue
            
            try:
                results[channel] = self.integrations[channel].send_alert(alert)
            except Exception as e:
                logger.error(f"Failed to send alert to {channel}: {e}")
                results[channel] = False
        
        return results
    
    def send_backup_failure_alert(
        self,
        backup_id: str,
        error: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """Envía alerta de fallo de backup."""
        alert = Alert(
            title=f"Backup Failed: {backup_id}",
            message=f"Backup {backup_id} failed: {error}",
            severity=AlertSeverity.ERROR,
            details=details or {}
        )
        return self.send_alert(alert)
    
    def send_critical_alert(
        self,
        title: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """Envía alerta crítica."""
        alert = Alert(
            title=title,
            message=message,
            severity=AlertSeverity.CRITICAL,
            details=details or {}
        )
        return self.send_alert(alert)

