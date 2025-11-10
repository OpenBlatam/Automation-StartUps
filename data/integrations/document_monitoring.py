"""
Sistema de Monitoreo y Alertas
===============================

Monitorea el sistema y envía alertas cuando hay problemas.
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Niveles de alerta"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Alerta del sistema"""
    level: AlertLevel
    message: str
    component: str
    timestamp: str
    details: Dict[str, Any] = None
    resolved: bool = False


class SystemMonitor:
    """Monitor del sistema"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics: Dict[str, deque] = {}
        self.alerts: List[Alert] = []
        self.alert_handlers: List[Callable] = []
        self.thresholds = {
            "error_rate": 0.1,  # 10%
            "avg_processing_time": 60.0,  # 60 segundos
            "queue_size": 100,
            "memory_usage": 0.9,  # 90%
            "disk_usage": 0.9  # 90%
        }
    
    def record_metric(self, name: str, value: float):
        """Registra una métrica"""
        if name not in self.metrics:
            self.metrics[name] = deque(maxlen=1000)  # Últimos 1000 valores
        
        self.metrics[name].append(value)
        
        # Verificar umbrales
        self._check_thresholds(name, value)
    
    def _check_thresholds(self, metric_name: str, value: float):
        """Verifica si se excede algún umbral"""
        threshold = self.thresholds.get(metric_name)
        if threshold is None:
            return
        
        if value > threshold:
            level = AlertLevel.WARNING
            if value > threshold * 1.5:
                level = AlertLevel.ERROR
            if value > threshold * 2:
                level = AlertLevel.CRITICAL
            
            self.create_alert(
                level=level,
                message=f"Métrica {metric_name} excede umbral: {value:.2f} > {threshold:.2f}",
                component=metric_name,
                details={"value": value, "threshold": threshold}
            )
    
    def create_alert(
        self,
        level: AlertLevel,
        message: str,
        component: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Crea una alerta"""
        alert = Alert(
            level=level,
            message=message,
            component=component,
            timestamp=datetime.now().isoformat(),
            details=details or {}
        )
        
        self.alerts.append(alert)
        
        # Mantener solo últimos 1000 alertas
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
        
        # Ejecutar handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Error en alert handler: {e}")
        
        # Log según nivel
        if level == AlertLevel.CRITICAL:
            self.logger.critical(message, extra=details)
        elif level == AlertLevel.ERROR:
            self.logger.error(message, extra=details)
        elif level == AlertLevel.WARNING:
            self.logger.warning(message, extra=details)
        else:
            self.logger.info(message, extra=details)
    
    def register_alert_handler(self, handler: Callable):
        """Registra un handler de alertas"""
        self.alert_handlers.append(handler)
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Obtiene resumen de métricas"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        summary = {}
        for metric_name, values in self.metrics.items():
            if not values:
                continue
            
            recent_values = [
                v for v in values
                # Asumir que los valores más recientes están al final
            ]
            
            if recent_values:
                summary[metric_name] = {
                    "current": recent_values[-1],
                    "average": sum(recent_values) / len(recent_values),
                    "min": min(recent_values),
                    "max": max(recent_values),
                    "count": len(recent_values)
                }
        
        return summary
    
    def get_active_alerts(self) -> List[Alert]:
        """Obtiene alertas activas (no resueltas)"""
        return [a for a in self.alerts if not a.resolved]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Obtiene estado de salud del sistema"""
        active_alerts = self.get_active_alerts()
        
        critical_count = sum(1 for a in active_alerts if a.level == AlertLevel.CRITICAL)
        error_count = sum(1 for a in active_alerts if a.level == AlertLevel.ERROR)
        warning_count = sum(1 for a in active_alerts if a.level == AlertLevel.WARNING)
        
        if critical_count > 0:
            status = "critical"
        elif error_count > 0:
            status = "unhealthy"
        elif warning_count > 0:
            status = "degraded"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "alerts": {
                "critical": critical_count,
                "error": error_count,
                "warning": warning_count,
                "info": sum(1 for a in active_alerts if a.level == AlertLevel.INFO)
            },
            "metrics_summary": self.get_metrics_summary(hours=1)
        }


def create_slack_alert_handler(webhook_url: str) -> Callable:
    """Crea handler para enviar alertas a Slack"""
    import requests
    
    def handler(alert: Alert):
        color_map = {
            AlertLevel.INFO: "#36a64f",
            AlertLevel.WARNING: "#ff9900",
            AlertLevel.ERROR: "#ff0000",
            AlertLevel.CRITICAL: "#8b0000"
        }
        
        payload = {
            "attachments": [{
                "color": color_map.get(alert.level, "#808080"),
                "title": f"Alert: {alert.level.value.upper()}",
                "text": alert.message,
                "fields": [
                    {"title": "Component", "value": alert.component, "short": True},
                    {"title": "Timestamp", "value": alert.timestamp, "short": True}
                ],
                "footer": "Document Processing System"
            }]
        }
        
        try:
            requests.post(webhook_url, json=payload, timeout=5)
        except Exception as e:
            logger.error(f"Error enviando alerta a Slack: {e}")
    
    return handler


def create_email_alert_handler(email_config: Dict[str, Any]) -> Callable:
    """Crea handler para enviar alertas por email"""
    def handler(alert: Alert):
        # Implementación simplificada
        # En producción usaría un servicio de email real
        if alert.level in [AlertLevel.ERROR, AlertLevel.CRITICAL]:
            logger.info(f"Enviando email para alerta: {alert.message}")
            # Aquí iría la lógica de envío de email
    
    return handler

