"""
Sistema de Métricas en Tiempo Real.

Proporciona métricas y alertas en tiempo real del sistema de soporte.
"""
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque
import threading

logger = logging.getLogger(__name__)


@dataclass
class RealtimeMetric:
    """Métrica en tiempo real."""
    metric_name: str
    value: float
    timestamp: datetime
    unit: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class MetricAlert:
    """Alerta de métrica."""
    alert_id: str
    metric_name: str
    threshold_type: str  # "above", "below", "rate_change"
    threshold_value: float
    current_value: float
    severity: str  # "info", "warning", "critical"
    message: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class RealtimeMetricsCollector:
    """Colector de métricas en tiempo real."""
    
    def __init__(self, db_connection=None):
        """
        Inicializa colector.
        
        Args:
            db_connection: Conexión a BD (opcional)
        """
        self.db = db_connection
        self.metrics: Dict[str, deque] = {}  # Nombre -> deque de valores
        self.max_history = 1000  # Máximo de valores históricos
        self.alerts: List[MetricAlert] = []
        self.alert_callbacks: List[callable] = []
        self.running = False
        self.collect_thread: Optional[threading.Thread] = None
    
    def start_collection(self, interval_seconds: int = 60):
        """
        Inicia recolección automática.
        
        Args:
            interval_seconds: Intervalo en segundos
        """
        if self.running:
            return
        
        self.running = True
        
        def collect_loop():
            while self.running:
                try:
                    self.collect_all_metrics()
                except Exception as e:
                    logger.error(f"Error collecting metrics: {e}")
                time.sleep(interval_seconds)
        
        self.collect_thread = threading.Thread(target=collect_loop, daemon=True)
        self.collect_thread.start()
        
        logger.info(f"Started metrics collection with interval {interval_seconds}s")
    
    def stop_collection(self):
        """Detiene recolección."""
        self.running = False
        if self.collect_thread:
            self.collect_thread.join(timeout=5)
    
    def collect_all_metrics(self):
        """Recolecta todas las métricas."""
        if not self.db:
            return
        
        try:
            with self.db.cursor() as cur:
                # Tickets abiertos
                cur.execute("""
                    SELECT COUNT(*) FROM support_tickets
                    WHERE status IN ('open', 'assigned', 'in_progress')
                """)
                open_tickets = cur.fetchone()[0]
                self.record_metric("tickets_open", open_tickets)
                
                # Tickets críticos sin respuesta
                cur.execute("""
                    SELECT COUNT(*) FROM support_tickets
                    WHERE priority IN ('critical', 'urgent')
                    AND status NOT IN ('resolved', 'closed')
                    AND first_response_at IS NULL
                    AND created_at < NOW() - INTERVAL '1 hour'
                """)
                critical_unanswered = cur.fetchone()[0]
                self.record_metric("tickets_critical_unanswered", critical_unanswered)
                
                # Tiempo promedio de primera respuesta
                cur.execute("""
                    SELECT AVG(EXTRACT(EPOCH FROM (first_response_at - created_at))/60)
                    FROM support_tickets
                    WHERE first_response_at IS NOT NULL
                    AND created_at >= NOW() - INTERVAL '24 hours'
                """)
                row = cur.fetchone()
                avg_first_response = float(row[0]) if row[0] else 0.0
                self.record_metric("avg_first_response_minutes", avg_first_response)
                
                # Tasa de resolución del chatbot
                cur.execute("""
                    SELECT 
                        COUNT(*) FILTER (WHERE chatbot_resolved = true)::float / 
                        NULLIF(COUNT(*), 0) * 100
                    FROM support_tickets
                    WHERE created_at >= NOW() - INTERVAL '24 hours'
                    AND chatbot_attempted = true
                """)
                row = cur.fetchone()
                chatbot_rate = float(row[0]) if row[0] else 0.0
                self.record_metric("chatbot_resolution_rate", chatbot_rate)
                
                # Agentes activos
                cur.execute("""
                    SELECT COUNT(*) FROM support_agents
                    WHERE is_available = true
                """)
                active_agents = cur.fetchone()[0]
                self.record_metric("agents_active", active_agents)
                
                # Tickets por hora (última hora)
                cur.execute("""
                    SELECT COUNT(*) FROM support_tickets
                    WHERE created_at >= NOW() - INTERVAL '1 hour'
                """)
                tickets_last_hour = cur.fetchone()[0]
                self.record_metric("tickets_per_hour", tickets_last_hour)
                
        except Exception as e:
            logger.error(f"Error collecting metrics from DB: {e}")
    
    def record_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "",
        metadata: Dict[str, Any] = None
    ):
        """Registra una métrica."""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = deque(maxlen=self.max_history)
        
        metric = RealtimeMetric(
            metric_name=metric_name,
            value=value,
            timestamp=datetime.now(),
            unit=unit,
            metadata=metadata or {}
        )
        
        self.metrics[metric_name].append(metric)
        
        # Verificar alertas
        self._check_alerts(metric_name, value)
    
    def _check_alerts(self, metric_name: str, value: float):
        """Verifica alertas configuradas."""
        # Alertas predefinidas
        alerts_config = [
            {
                "metric": "tickets_critical_unanswered",
                "threshold_type": "above",
                "threshold_value": 5,
                "severity": "critical",
                "message": "Hay {value} tickets críticos sin respuesta"
            },
            {
                "metric": "avg_first_response_minutes",
                "threshold_type": "above",
                "threshold_value": 120,
                "severity": "warning",
                "message": "Tiempo promedio de primera respuesta: {value:.1f} minutos"
            },
            {
                "metric": "tickets_open",
                "threshold_type": "above",
                "threshold_value": 100,
                "severity": "warning",
                "message": "Hay {value} tickets abiertos"
            },
            {
                "metric": "chatbot_resolution_rate",
                "threshold_type": "below",
                "threshold_value": 30,
                "severity": "info",
                "message": "Tasa de resolución del chatbot: {value:.1f}%"
            }
        ]
        
        for alert_config in alerts_config:
            if alert_config["metric"] != metric_name:
                continue
            
            threshold_type = alert_config["threshold_type"]
            threshold_value = alert_config["threshold_value"]
            should_alert = False
            
            if threshold_type == "above" and value > threshold_value:
                should_alert = True
            elif threshold_type == "below" and value < threshold_value:
                should_alert = True
            
            if should_alert:
                alert = MetricAlert(
                    alert_id=f"alert-{metric_name}-{datetime.now().timestamp()}",
                    metric_name=metric_name,
                    threshold_type=threshold_type,
                    threshold_value=threshold_value,
                    current_value=value,
                    severity=alert_config["severity"],
                    message=alert_config["message"].format(value=value)
                )
                
                self.alerts.append(alert)
                
                # Mantener solo últimos 100 alertas
                if len(self.alerts) > 100:
                    self.alerts = self.alerts[-100:]
                
                # Llamar callbacks
                for callback in self.alert_callbacks:
                    try:
                        callback(alert)
                    except Exception as e:
                        logger.error(f"Error in alert callback: {e}")
    
    def get_metric(
        self,
        metric_name: str,
        last_n: int = 1
    ) -> List[RealtimeMetric]:
        """Obtiene métricas recientes."""
        if metric_name not in self.metrics:
            return []
        
        return list(self.metrics[metric_name])[-last_n:]
    
    def get_metric_value(self, metric_name: str) -> Optional[float]:
        """Obtiene último valor de métrica."""
        metrics = self.get_metric(metric_name, 1)
        return metrics[0].value if metrics else None
    
    def get_metric_trend(
        self,
        metric_name: str,
        minutes: int = 60
    ) -> Dict[str, Any]:
        """Obtiene tendencia de métrica."""
        if metric_name not in self.metrics:
            return {"trend": "no_data"}
        
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [
            m for m in self.metrics[metric_name]
            if m.timestamp >= cutoff
        ]
        
        if len(recent_metrics) < 2:
            return {"trend": "insufficient_data"}
        
        values = [m.value for m in recent_metrics]
        first_value = values[0]
        last_value = values[-1]
        
        change = last_value - first_value
        change_percentage = (change / first_value * 100) if first_value != 0 else 0
        
        if abs(change_percentage) < 2:
            trend = "stable"
        elif change > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        return {
            "trend": trend,
            "change": change,
            "change_percentage": change_percentage,
            "first_value": first_value,
            "last_value": last_value,
            "data_points": len(recent_metrics)
        }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Obtiene datos para dashboard."""
        return {
            "tickets_open": self.get_metric_value("tickets_open") or 0,
            "tickets_critical_unanswered": self.get_metric_value("tickets_critical_unanswered") or 0,
            "avg_first_response_minutes": self.get_metric_value("avg_first_response_minutes") or 0,
            "chatbot_resolution_rate": self.get_metric_value("chatbot_resolution_rate") or 0,
            "agents_active": self.get_metric_value("agents_active") or 0,
            "tickets_per_hour": self.get_metric_value("tickets_per_hour") or 0,
            "recent_alerts": [
                {
                    "metric": a.metric_name,
                    "severity": a.severity,
                    "message": a.message,
                    "timestamp": a.timestamp.isoformat()
                }
                for a in self.alerts[-10:]  # Últimas 10 alertas
            ],
            "trends": {
                "tickets_open": self.get_metric_trend("tickets_open", 60),
                "tickets_per_hour": self.get_metric_trend("tickets_per_hour", 60),
                "chatbot_resolution_rate": self.get_metric_trend("chatbot_resolution_rate", 60)
            }
        }
    
    def register_alert_callback(self, callback: callable):
        """Registra callback para alertas."""
        self.alert_callbacks.append(callback)

