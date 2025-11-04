"""
Sistema de Alertas Inteligentes Avanzadas.

Alertas contextuales, predictivas y basadas en ML.
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Severidad de alerta."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertType(Enum):
    """Tipos de alerta."""
    VOLUME = "volume"
    PERFORMANCE = "performance"
    QUALITY = "quality"
    SLA = "sla"
    ANOMALY = "anomaly"
    SECURITY = "security"
    PREDICTIVE = "predictive"


@dataclass
class SmartAlert:
    """Alerta inteligente."""
    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    context: Dict[str, Any]
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    actions_taken: List[str] = None
    confidence: float = 1.0  # Confianza de la alerta (ML)
    
    def __post_init__(self):
        if self.actions_taken is None:
            self.actions_taken = []


class SmartAlertEngine:
    """Motor de alertas inteligentes."""
    
    def __init__(self, db_connection=None):
        """
        Inicializa motor de alertas.
        
        Args:
            db_connection: Conexión a BD (opcional)
        """
        self.db = db_connection
        self.active_alerts: List[SmartAlert] = []
        self.alert_history: List[SmartAlert] = []
        self.alert_rules: List[Dict[str, Any]] = []
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Inicializa reglas de alerta por defecto."""
        self.alert_rules = [
            {
                "rule_id": "volume_spike",
                "type": AlertType.VOLUME,
                "condition": lambda data: data.get("tickets_per_hour", 0) > 100,
                "severity": AlertSeverity.WARNING,
                "title": "Pico de Volumen Detectado",
                "message_template": "Se detectaron {tickets_per_hour} tickets en la última hora, {increase}% más que el promedio"
            },
            {
                "rule_id": "sla_breach_risk",
                "type": AlertType.SLA,
                "condition": lambda data: data.get("critical_unanswered", 0) > 5,
                "severity": AlertSeverity.CRITICAL,
                "title": "Riesgo de Incumplimiento de SLA",
                "message_template": "Hay {critical_unanswered} tickets críticos sin respuesta, riesgo de incumplimiento de SLA"
            },
            {
                "rule_id": "satisfaction_drop",
                "type": AlertType.QUALITY,
                "condition": lambda data: data.get("satisfaction_score", 5.0) < 3.0,
                "severity": AlertSeverity.WARNING,
                "title": "Caída en Satisfacción",
                "message_template": "Satisfacción del cliente: {satisfaction_score}/5, {drop}% por debajo del promedio"
            },
            {
                "rule_id": "response_time_anomaly",
                "type": AlertType.PERFORMANCE,
                "condition": lambda data: data.get("avg_response_time", 0) > 180,
                "severity": AlertSeverity.WARNING,
                "title": "Tiempo de Respuesta Alto",
                "message_template": "Tiempo promedio de respuesta: {avg_response_time} minutos"
            }
        ]
    
    def evaluate_alerts(self, metrics: Dict[str, Any]) -> List[SmartAlert]:
        """
        Evalúa métricas y genera alertas.
        
        Args:
            metrics: Diccionario con métricas actuales
            
        Returns:
            Lista de alertas generadas
        """
        alerts = []
        
        for rule in self.alert_rules:
            try:
                if rule["condition"](metrics):
                    alert = self._create_alert_from_rule(rule, metrics)
                    alerts.append(alert)
                    self.active_alerts.append(alert)
            except Exception as e:
                logger.error(f"Error evaluating alert rule {rule['rule_id']}: {e}")
        
        # Mantener solo últimos 1000 alertas activas
        if len(self.active_alerts) > 1000:
            self.active_alerts = self.active_alerts[-1000:]
        
        return alerts
    
    def _create_alert_from_rule(
        self,
        rule: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> SmartAlert:
        """Crea alerta desde regla."""
        alert_id = f"alert-{rule['rule_id']}-{datetime.now().timestamp()}"
        
        # Formatear mensaje
        message = rule["message_template"].format(**metrics)
        
        # Calcular confianza (simplificado - en producción usar ML)
        confidence = 0.9
        if rule["type"] == AlertType.PREDICTIVE:
            confidence = 0.7  # Menor confianza en predicciones
        
        alert = SmartAlert(
            alert_id=alert_id,
            alert_type=rule["type"],
            severity=rule["severity"],
            title=rule["title"],
            message=message,
            context=metrics.copy(),
            triggered_at=datetime.now(),
            confidence=confidence
        )
        
        logger.info(f"Alert triggered: {alert.title}")
        return alert
    
    def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """
        Reconoce una alerta.
        
        Args:
            alert_id: ID de la alerta
            user_id: ID del usuario que reconoce
            
        Returns:
            True si se reconoció correctamente
        """
        alert = next((a for a in self.active_alerts if a.alert_id == alert_id), None)
        
        if not alert:
            return False
        
        alert.acknowledged_by = user_id
        alert.acknowledged_at = datetime.now()
        
        logger.info(f"Alert {alert_id} acknowledged by {user_id}")
        return True
    
    def resolve_alert(self, alert_id: str, actions_taken: List[str] = None) -> bool:
        """
        Resuelve una alerta.
        
        Args:
            alert_id: ID de la alerta
            actions_taken: Acciones tomadas (opcional)
            
        Returns:
            True si se resolvió correctamente
        """
        alert = next((a for a in self.active_alerts if a.alert_id == alert_id), None)
        
        if not alert:
            return False
        
        alert.resolved_at = datetime.now()
        if actions_taken:
            alert.actions_taken = actions_taken
        
        # Mover a historial
        self.active_alerts.remove(alert)
        self.alert_history.append(alert)
        
        logger.info(f"Alert {alert_id} resolved")
        return True
    
    def get_active_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        alert_type: Optional[AlertType] = None
    ) -> List[SmartAlert]:
        """
        Obtiene alertas activas filtradas.
        
        Args:
            severity: Filtrar por severidad (opcional)
            alert_type: Filtrar por tipo (opcional)
            
        Returns:
            Lista de alertas activas
        """
        alerts = self.active_alerts
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if alert_type:
            alerts = [a for a in alerts if a.alert_type == alert_type]
        
        return sorted(alerts, key=lambda x: (
            0 if x.severity == AlertSeverity.EMERGENCY else
            1 if x.severity == AlertSeverity.CRITICAL else
            2 if x.severity == AlertSeverity.WARNING else 3
        ))
    
    def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Obtiene resumen de alertas.
        
        Args:
            hours: Horas hacia atrás
            
        Returns:
            Resumen de alertas
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_alerts = [
            a for a in self.alert_history + self.active_alerts
            if a.triggered_at >= cutoff
        ]
        
        by_severity = {}
        by_type = {}
        
        for alert in recent_alerts:
            severity = alert.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            atype = alert.alert_type.value
            by_type[atype] = by_type.get(atype, 0) + 1
        
        unresolved = sum(1 for a in self.active_alerts if not a.resolved_at)
        
        return {
            "period_hours": hours,
            "total_alerts": len(recent_alerts),
            "active_alerts": len(self.active_alerts),
            "unresolved_alerts": unresolved,
            "by_severity": by_severity,
            "by_type": by_type,
            "recent_critical": [
                {
                    "id": a.alert_id,
                    "title": a.title,
                    "severity": a.severity.value,
                    "triggered_at": a.triggered_at.isoformat()
                }
                for a in sorted(recent_alerts, key=lambda x: x.triggered_at, reverse=True)
                if a.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]
            ][:10]
        }
    
    def add_alert_rule(self, rule: Dict[str, Any]):
        """Agrega una regla de alerta personalizada."""
        self.alert_rules.append(rule)
        logger.info(f"Added alert rule: {rule.get('rule_id', 'custom')}")

