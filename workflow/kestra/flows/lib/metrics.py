"""
Módulo para exportación de métricas Prometheus y observabilidad.

Características:
- Métricas Prometheus estándar
- Exportación en formato text/plain
- Métricas personalizadas para workflows
- Soporte para labels y tags
"""
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Tipos de métricas Prometheus."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Metric:
    """Representa una métrica Prometheus."""
    name: str
    value: float
    metric_type: MetricType
    labels: Optional[Dict[str, str]] = None
    help_text: Optional[str] = None
    timestamp: Optional[int] = None
    
    def __post_init__(self):
        """Inicializa timestamp si no está presente."""
        if self.timestamp is None:
            self.timestamp = int(time.time() * 1000)  # milliseconds
    
    def to_prometheus(self) -> str:
        """
        Convierte la métrica al formato Prometheus text/plain.
        
        Returns:
            String en formato Prometheus
        """
        lines = []
        
        # Help text (opcional)
        if self.help_text:
            lines.append(f"# HELP {self.name} {self.help_text}")
        
        # Type (opcional pero recomendado)
        type_line = f"# TYPE {self.name} {self.metric_type.value}"
        lines.append(type_line)
        
        # Labels string
        labels_str = ""
        if self.labels:
            label_pairs = [f'{k}="{v}"' for k, v in self.labels.items()]
            labels_str = "{" + ",".join(label_pairs) + "}"
        
        # Metric line
        metric_line = f"{self.name}{labels_str} {self.value}"
        lines.append(metric_line)
        
        return "\n".join(lines)


class MetricsCollector:
    """Colector de métricas para workflows."""
    
    def __init__(self):
        """Inicializa el colector de métricas."""
        self.metrics: List[Metric] = []
        self.start_times: Dict[str, float] = {}
    
    def start_timer(self, operation: str) -> None:
        """
        Inicia un timer para una operación.
        
        Args:
            operation: Nombre de la operación
        """
        self.start_times[operation] = time.time()
    
    def record_duration(self, operation: str, labels: Optional[Dict[str, str]] = None) -> float:
        """
        Registra la duración de una operación.
        
        Args:
            operation: Nombre de la operación
            labels: Labels adicionales para la métrica
        
        Returns:
            Duración en segundos
        """
        if operation not in self.start_times:
            logger.warning(f"Timer not started for operation: {operation}")
            return 0.0
        
        duration = time.time() - self.start_times[operation]
        del self.start_times[operation]
        
        self.add_histogram(
            name=f"workflow_operation_duration_seconds",
            value=duration,
            labels={"operation": operation, **(labels or {})}
        )
        
        return duration
    
    def add_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[Dict[str, str]] = None,
        help_text: Optional[str] = None
    ) -> None:
        """
        Agrega una métrica counter.
        
        Args:
            name: Nombre de la métrica
            value: Valor a incrementar (default: 1.0)
            labels: Labels para segmentación
            help_text: Texto de ayuda
        """
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.COUNTER,
            labels=labels,
            help_text=help_text
        )
        self.metrics.append(metric)
    
    def add_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        help_text: Optional[str] = None
    ) -> None:
        """
        Agrega una métrica gauge.
        
        Args:
            name: Nombre de la métrica
            value: Valor actual
            labels: Labels para segmentación
            help_text: Texto de ayuda
        """
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            labels=labels,
            help_text=help_text
        )
        self.metrics.append(metric)
    
    def add_histogram(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        help_text: Optional[str] = None
    ) -> None:
        """
        Agrega una métrica histogram.
        
        Args:
            name: Nombre de la métrica
            value: Valor a registrar
            labels: Labels para segmentación
            help_text: Texto de ayuda
        """
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            labels=labels,
            help_text=help_text
        )
        self.metrics.append(metric)
    
    def export_prometheus(self) -> str:
        """
        Exporta todas las métricas en formato Prometheus.
        
        Returns:
            String con todas las métricas en formato Prometheus text/plain
        """
        if not self.metrics:
            return "# No metrics collected\n"
        
        lines = []
        for metric in self.metrics:
            lines.append(metric.to_prometheus())
        
        return "\n".join(lines) + "\n"
    
    def export_json(self) -> List[Dict[str, Any]]:
        """
        Exporta métricas en formato JSON.
        
        Returns:
            Lista de diccionarios con las métricas
        """
        return [
            {
                "name": m.name,
                "value": m.value,
                "type": m.metric_type.value,
                "labels": m.labels or {},
                "timestamp": m.timestamp
            }
            for m in self.metrics
        ]
    
    def clear(self) -> None:
        """Limpia todas las métricas recolectadas."""
        self.metrics.clear()
        self.start_times.clear()


# Instancia global para uso en workflows
_metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """
    Obtiene la instancia global del colector de métricas.
    
    Returns:
        Instancia de MetricsCollector
    """
    return _metrics_collector


def record_workflow_metric(
    name: str,
    value: float,
    metric_type: str = "counter",
    labels: Optional[Dict[str, str]] = None
) -> None:
    """
    Función de conveniencia para registrar una métrica.
    
    Args:
        name: Nombre de la métrica
        value: Valor
        metric_type: Tipo (counter, gauge, histogram)
        labels: Labels opcionales
    """
    collector = get_metrics_collector()
    
    metric_type_enum = MetricType(metric_type.lower())
    
    if metric_type_enum == MetricType.COUNTER:
        collector.add_counter(name, value, labels)
    elif metric_type_enum == MetricType.GAUGE:
        collector.add_gauge(name, value, labels)
    elif metric_type_enum == MetricType.HISTOGRAM:
        collector.add_histogram(name, value, labels)



