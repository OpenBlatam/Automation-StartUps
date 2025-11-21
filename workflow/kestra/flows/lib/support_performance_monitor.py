"""
Monitor de Performance para Operaciones de Soporte.

Características:
- Tracking de tiempos de ejecución
- Métricas de performance
- Alertas de degradación
- Análisis de bottlenecks
"""
import logging
import time
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Métrica de performance."""
    operation_name: str
    duration_seconds: float
    timestamp: datetime
    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceStats:
    """Estadísticas de performance."""
    operation_name: str
    total_operations: int
    successful: int
    failed: int
    avg_duration: float
    min_duration: float
    max_duration: float
    p50_duration: float
    p95_duration: float
    p99_duration: float
    success_rate: float


class SupportPerformanceMonitor:
    """Monitor de performance para operaciones de soporte."""
    
    def __init__(
        self,
        db_connection: Any = None,
        enable_persistence: bool = False,
        alert_threshold_p95: Optional[float] = None,
        alert_threshold_failure_rate: float = 0.1
    ):
        """
        Inicializa el monitor de performance.
        
        Args:
            db_connection: Conexión a BD para persistir métricas
            enable_persistence: Habilitar persistencia en BD
            alert_threshold_p95: Umbral de alerta para P95 (segundos)
            alert_threshold_failure_rate: Umbral de tasa de fallos (0.0-1.0)
        """
        self.db_connection = db_connection
        self.enable_persistence = enable_persistence
        self.alert_threshold_p95 = alert_threshold_p95
        self.alert_threshold_failure_rate = alert_threshold_failure_rate
        
        # Métricas en memoria (últimas 1000 operaciones por tipo)
        self.metrics: Dict[str, List[PerformanceMetric]] = defaultdict(lambda: [])
        self.max_metrics_per_operation = 1000
    
    @contextmanager
    def track(self, operation_name: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Context manager para trackear una operación.
        
        Usage:
            with monitor.track("categorize_ticket", {"ticket_id": "123"}):
                # operación aquí
                pass
        """
        start_time = time.time()
        success = False
        error = None
        
        try:
            yield
            success = True
        except Exception as e:
            error = e
            raise
        finally:
            duration = time.time() - start_time
            self._record_metric(
                operation_name=operation_name,
                duration=duration,
                success=success,
                metadata=metadata or {},
                error=str(error) if error else None
            )
    
    def _record_metric(
        self,
        operation_name: str,
        duration: float,
        success: bool,
        metadata: Dict[str, Any],
        error: Optional[str] = None
    ):
        """Registra una métrica."""
        metric = PerformanceMetric(
            operation_name=operation_name,
            duration_seconds=duration,
            timestamp=datetime.now(),
            success=success,
            metadata={**metadata, "error": error} if error else metadata
        )
        
        # Agregar a lista (mantener solo últimas N)
        metrics_list = self.metrics[operation_name]
        metrics_list.append(metric)
        
        if len(metrics_list) > self.max_metrics_per_operation:
            metrics_list.pop(0)  # Eliminar más antiguo
        
        # Persistir si está habilitado
        if self.enable_persistence and self.db_connection:
            self._persist_metric(metric)
        
        # Verificar alertas
        self._check_alerts(operation_name)
    
    def _persist_metric(self, metric: PerformanceMetric):
        """Persiste métrica en BD."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO support_performance_metrics (
                    operation_name,
                    duration_seconds,
                    success,
                    metadata,
                    timestamp
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                metric.operation_name,
                metric.duration_seconds,
                metric.success,
                metric.metadata,
                metric.timestamp
            ))
            self.db_connection.commit()
            cursor.close()
        except Exception as e:
            logger.error(f"Error persistiendo métrica: {e}")
            if self.db_connection:
                self.db_connection.rollback()
    
    def _check_alerts(self, operation_name: str):
        """Verifica alertas de performance."""
        stats = self.get_stats(operation_name)
        
        if not stats or stats.total_operations < 10:
            return  # No hay suficientes datos
        
        # Alerta por P95 alto
        if self.alert_threshold_p95 and stats.p95_duration > self.alert_threshold_p95:
            logger.warning(
                f"⚠️ Performance degradada para {operation_name}: "
                f"P95={stats.p95_duration:.2f}s (umbral: {self.alert_threshold_p95}s)"
            )
        
        # Alerta por tasa de fallos alta
        if stats.success_rate < (1.0 - self.alert_threshold_failure_rate):
            logger.warning(
                f"⚠️ Alta tasa de fallos para {operation_name}: "
                f"{stats.failed}/{stats.total_operations} ({stats.success_rate*100:.1f}% éxito)"
            )
    
    def get_stats(
        self,
        operation_name: str,
        window_minutes: int = 60
    ) -> Optional[PerformanceStats]:
        """
        Obtiene estadísticas de performance para una operación.
        
        Args:
            operation_name: Nombre de la operación
            window_minutes: Ventana de tiempo en minutos
            
        Returns:
            PerformanceStats o None si no hay datos
        """
        metrics = self.metrics.get(operation_name, [])
        
        if not metrics:
            return None
        
        # Filtrar por ventana de tiempo
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        recent_metrics = [
            m for m in metrics
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return None
        
        # Calcular estadísticas
        durations = [m.duration_seconds for m in recent_metrics]
        durations_sorted = sorted(durations)
        
        successful = sum(1 for m in recent_metrics if m.success)
        failed = len(recent_metrics) - successful
        
        total = len(recent_metrics)
        success_rate = successful / total if total > 0 else 0.0
        
        avg_duration = sum(durations) / total if total > 0 else 0.0
        min_duration = min(durations) if durations else 0.0
        max_duration = max(durations) if durations else 0.0
        
        # Percentiles
        p50_index = int(len(durations_sorted) * 0.50)
        p95_index = int(len(durations_sorted) * 0.95)
        p99_index = int(len(durations_sorted) * 0.99)
        
        p50_duration = durations_sorted[p50_index] if p50_index < len(durations_sorted) else 0.0
        p95_duration = durations_sorted[p95_index] if p95_index < len(durations_sorted) else 0.0
        p99_duration = durations_sorted[p99_index] if p99_index < len(durations_sorted) else 0.0
        
        return PerformanceStats(
            operation_name=operation_name,
            total_operations=total,
            successful=successful,
            failed=failed,
            avg_duration=avg_duration,
            min_duration=min_duration,
            max_duration=max_duration,
            p50_duration=p50_duration,
            p95_duration=p95_duration,
            p99_duration=p99_duration,
            success_rate=success_rate
        )
    
    def get_all_stats(self, window_minutes: int = 60) -> Dict[str, PerformanceStats]:
        """Obtiene estadísticas para todas las operaciones."""
        all_stats = {}
        for operation_name in self.metrics.keys():
            stats = self.get_stats(operation_name, window_minutes)
            if stats:
                all_stats[operation_name] = stats
        return all_stats
    
    def monitor(self, operation_name: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Decorador para monitorear una función.
        
        Usage:
            @monitor.monitor("categorize_ticket")
            def categorize(ticket):
                ...
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                with self.track(operation_name, metadata):
                    return func(*args, **kwargs)
            return wrapper
        return decorator


# Instancia global para uso común
default_performance_monitor = SupportPerformanceMonitor()

