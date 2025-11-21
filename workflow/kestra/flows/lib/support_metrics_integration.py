"""
Sistema de Integración con Métricas Externas.

Integra con Prometheus, Grafana y otros sistemas de métricas.
"""
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    from prometheus_client import Counter, Gauge, Histogram, Summary, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class MetricExport:
    """Exportación de métrica."""
    metric_name: str
    value: float
    labels: Dict[str, str]
    timestamp: datetime
    metric_type: str  # "counter", "gauge", "histogram", "summary"


class MetricsExporter:
    """Exportador de métricas."""
    
    def __init__(self, enable_prometheus: bool = True, port: int = 8000):
        """
        Inicializa exportador.
        
        Args:
            enable_prometheus: Habilitar Prometheus
            port: Puerto para servidor Prometheus
        """
        self.enable_prometheus = enable_prometheus and PROMETHEUS_AVAILABLE
        self.port = port
        self.metrics: Dict[str, Any] = {}
        self._initialize_prometheus_metrics()
        
        if self.enable_prometheus:
            try:
                start_http_server(port)
                logger.info(f"Prometheus metrics server started on port {port}")
            except Exception as e:
                logger.warning(f"Could not start Prometheus server: {e}")
                self.enable_prometheus = False
    
    def _initialize_prometheus_metrics(self):
        """Inicializa métricas de Prometheus."""
        if not self.enable_prometheus:
            return
        
        # Counters
        self.metrics['tickets_total'] = Counter(
            'support_tickets_total',
            'Total number of tickets',
            ['status', 'priority', 'category']
        )
        
        self.metrics['tickets_resolved_total'] = Counter(
            'support_tickets_resolved_total',
            'Total number of resolved tickets',
            ['category', 'resolution_type']
        )
        
        self.metrics['chatbot_responses_total'] = Counter(
            'support_chatbot_responses_total',
            'Total chatbot responses',
            ['resolved', 'confidence_level']
        )
        
        # Gauges
        self.metrics['tickets_open'] = Gauge(
            'support_tickets_open',
            'Number of open tickets',
            ['priority', 'category']
        )
        
        self.metrics['tickets_critical_unanswered'] = Gauge(
            'support_tickets_critical_unanswered',
            'Number of critical tickets without response',
            ['hours_open']
        )
        
        self.metrics['avg_response_time_minutes'] = Gauge(
            'support_avg_response_time_minutes',
            'Average response time in minutes'
        )
        
        self.metrics['avg_resolution_time_minutes'] = Gauge(
            'support_avg_resolution_time_minutes',
            'Average resolution time in minutes'
        )
        
        self.metrics['customer_satisfaction_score'] = Gauge(
            'support_customer_satisfaction_score',
            'Average customer satisfaction score',
            ['category']
        )
        
        self.metrics['agents_active'] = Gauge(
            'support_agents_active',
            'Number of active agents'
        )
        
        self.metrics['agents_workload'] = Gauge(
            'support_agents_workload',
            'Average workload per agent',
            ['agent_id', 'department']
        )
        
        # Histograms
        self.metrics['response_time_histogram'] = Histogram(
            'support_response_time_seconds',
            'Response time distribution',
            buckets=[10, 30, 60, 120, 300, 600, 1800, 3600]
        )
        
        self.metrics['resolution_time_histogram'] = Histogram(
            'support_resolution_time_seconds',
            'Resolution time distribution',
            buckets=[300, 600, 1800, 3600, 7200, 14400, 28800, 86400]
        )
        
        # Summary
        self.metrics['ticket_priority_score'] = Summary(
            'support_ticket_priority_score',
            'Ticket priority score distribution'
        )
    
    def record_ticket_created(self, ticket_data: Dict[str, Any]):
        """Registra creación de ticket."""
        if not self.enable_prometheus:
            return
        
        self.metrics['tickets_total'].labels(
            status=ticket_data.get('status', 'unknown'),
            priority=ticket_data.get('priority', 'unknown'),
            category=ticket_data.get('category', 'unknown')
        ).inc()
    
    def record_ticket_resolved(self, ticket_data: Dict[str, Any]):
        """Registra resolución de ticket."""
        if not self.enable_prometheus:
            return
        
        resolution_type = 'chatbot' if ticket_data.get('chatbot_resolved') else 'manual'
        
        self.metrics['tickets_resolved_total'].labels(
            category=ticket_data.get('category', 'unknown'),
            resolution_type=resolution_type
        ).inc()
        
        # Registrar tiempo de resolución
        resolution_time = ticket_data.get('time_to_resolution_minutes', 0)
        if resolution_time:
            self.metrics['resolution_time_histogram'].observe(resolution_time * 60)  # Convertir a segundos
    
    def record_response_time(self, response_time_minutes: float):
        """Registra tiempo de respuesta."""
        if not self.enable_prometheus:
            return
        
        self.metrics['response_time_histogram'].observe(response_time_minutes * 60)  # Convertir a segundos
    
    def update_gauge(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """
        Actualiza un gauge.
        
        Args:
            metric_name: Nombre de la métrica
            value: Valor
            labels: Etiquetas (opcional)
        """
        if not self.enable_prometheus:
            return
        
        if metric_name in self.metrics:
            metric = self.metrics[metric_name]
            if labels:
                metric.labels(**labels).set(value)
            else:
                metric.set(value)
    
    def export_to_dict(self, db_connection=None) -> Dict[str, Any]:
        """
        Exporta métricas a diccionario (útil para APIs).
        
        Args:
            db_connection: Conexión a BD (opcional)
            
        Returns:
            Diccionario con métricas
        """
        metrics_dict = {}
        
        if db_connection:
            try:
                with db_connection.cursor() as cur:
                    # Tickets abiertos
                    cur.execute("""
                        SELECT COUNT(*) FROM support_tickets
                        WHERE status IN ('open', 'assigned', 'in_progress')
                    """)
                    metrics_dict['tickets_open'] = cur.fetchone()[0]
                    
                    # Tickets críticos sin respuesta
                    cur.execute("""
                        SELECT COUNT(*) FROM support_tickets
                        WHERE priority IN ('critical', 'urgent')
                        AND status NOT IN ('resolved', 'closed')
                        AND first_response_at IS NULL
                        AND created_at < NOW() - INTERVAL '1 hour'
                    """)
                    metrics_dict['tickets_critical_unanswered'] = cur.fetchone()[0]
                    
                    # Tiempo promedio de respuesta
                    cur.execute("""
                        SELECT AVG(EXTRACT(EPOCH FROM (first_response_at - created_at))/60)
                        FROM support_tickets
                        WHERE first_response_at IS NOT NULL
                        AND created_at >= NOW() - INTERVAL '24 hours'
                    """)
                    row = cur.fetchone()
                    metrics_dict['avg_response_time_minutes'] = float(row[0]) if row[0] else 0.0
                    
                    # Tiempo promedio de resolución
                    cur.execute("""
                        SELECT AVG(time_to_resolution_minutes)
                        FROM support_tickets
                        WHERE status = 'resolved'
                        AND created_at >= NOW() - INTERVAL '24 hours'
                    """)
                    row = cur.fetchone()
                    metrics_dict['avg_resolution_time_minutes'] = float(row[0]) if row[0] else 0.0
                    
                    # Satisfacción del cliente
                    cur.execute("""
                        SELECT AVG(satisfaction_score)
                        FROM support_ticket_feedback
                        WHERE submitted_at >= NOW() - INTERVAL '24 hours'
                    """)
                    row = cur.fetchone()
                    metrics_dict['customer_satisfaction_score'] = float(row[0]) if row[0] else 0.0
                    
                    # Agentes activos
                    cur.execute("""
                        SELECT COUNT(*) FROM support_agents
                        WHERE is_available = true
                    """)
                    metrics_dict['agents_active'] = cur.fetchone()[0]
                    
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
                    metrics_dict['chatbot_resolution_rate'] = float(row[0]) if row[0] else 0.0
                    
            except Exception as e:
                logger.error(f"Error exporting metrics: {e}")
        
        metrics_dict['timestamp'] = datetime.now().isoformat()
        metrics_dict['prometheus_enabled'] = self.enable_prometheus
        
        return metrics_dict
    
    def get_prometheus_metrics_url(self) -> str:
        """Obtiene URL de métricas de Prometheus."""
        return f"http://localhost:{self.port}/metrics"


class GrafanaIntegration:
    """Integración con Grafana."""
    
    @staticmethod
    def generate_dashboard_json(metrics: List[str]) -> Dict[str, Any]:
        """
        Genera JSON de dashboard de Grafana.
        
        Args:
            metrics: Lista de métricas a incluir
            
        Returns:
            JSON de dashboard de Grafana
        """
        panels = []
        
        for i, metric in enumerate(metrics):
            panel = {
                "id": i + 1,
                "title": metric.replace('_', ' ').title(),
                "type": "graph",
                "targets": [
                    {
                        "expr": metric,
                        "refId": "A"
                    }
                ],
                "gridPos": {
                    "h": 8,
                    "w": 12,
                    "x": (i % 2) * 12,
                    "y": (i // 2) * 8
                }
            }
            panels.append(panel)
        
        dashboard = {
            "dashboard": {
                "title": "Support System Metrics",
                "panels": panels,
                "time": {
                    "from": "now-6h",
                    "to": "now"
                },
                "refresh": "10s"
            }
        }
        
        return dashboard

