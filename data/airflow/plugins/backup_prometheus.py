"""
Módulo de Métricas de Prometheus para Backups.

Exporta métricas de backups a Prometheus para monitoreo.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Intentar importar Prometheus client
try:
    from prometheus_client import (
        Counter, Histogram, Gauge, Summary,
        generate_latest, REGISTRY
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    Counter = None
    Histogram = None
    Gauge = None
    Summary = None
    generate_latest = None
    REGISTRY = None


class BackupPrometheusMetrics:
    """Métricas de Prometheus para backups."""
    
    def __init__(self):
        """Inicializa métricas de Prometheus."""
        if not PROMETHEUS_AVAILABLE:
            logger.warning("Prometheus client not available, metrics disabled")
            self.enabled = False
            return
        
        self.enabled = True
        
        # Contadores
        self.backups_total = Counter(
            'backup_total',
            'Total number of backups',
            ['type', 'status']
        )
        
        self.backup_errors_total = Counter(
            'backup_errors_total',
            'Total number of backup errors',
            ['error_type']
        )
        
        # Histogramas
        self.backup_duration_seconds = Histogram(
            'backup_duration_seconds',
            'Backup duration in seconds',
            ['type', 'status'],
            buckets=[10, 30, 60, 120, 300, 600, 1800, 3600]
        )
        
        self.backup_size_bytes = Histogram(
            'backup_size_bytes',
            'Backup size in bytes',
            ['type'],
            buckets=[1024*1024, 10*1024*1024, 100*1024*1024, 1024*1024*1024, 10*1024*1024*1024]
        )
        
        # Gauges
        self.backup_success_rate = Gauge(
            'backup_success_rate',
            'Backup success rate (0-1)',
            ['type']
        )
        
        self.backup_total_size_bytes = Gauge(
            'backup_total_size_bytes',
            'Total size of all backups in bytes',
            ['type']
        )
        
        self.backup_encryption_time_seconds = Histogram(
            'backup_encryption_time_seconds',
            'Time taken to encrypt backup',
            buckets=[0.1, 0.5, 1, 2, 5, 10, 30]
        )
        
        self.backup_upload_time_seconds = Histogram(
            'backup_upload_time_seconds',
            'Time taken to upload backup to cloud',
            ['cloud_provider'],
            buckets=[5, 10, 30, 60, 120, 300, 600]
        )
        
        self.backup_verification_total = Counter(
            'backup_verification_total',
            'Total number of backup verifications',
            ['status']
        )
        
        self.backup_restore_total = Counter(
            'backup_restore_total',
            'Total number of restores',
            ['status']
        )
        
        # Health metrics
        self.backup_health_status = Gauge(
            'backup_health_status',
            'Backup system health status (1=healthy, 0=unhealthy)',
            ['check_type']
        )
        
        self.backup_disk_usage_percent = Gauge(
            'backup_disk_usage_percent',
            'Disk usage percentage for backup directory'
        )
        
        self.backup_disk_free_bytes = Gauge(
            'backup_disk_free_bytes',
            'Free disk space in bytes for backup directory'
        )
    
    def record_backup(
        self,
        backup_type: str,
        status: str,
        duration_seconds: float,
        size_bytes: int,
        encryption_time: Optional[float] = None,
        upload_time: Optional[float] = None,
        cloud_provider: Optional[str] = None
    ) -> None:
        """
        Registra métricas de un backup.
        
        Args:
            backup_type: Tipo de backup ('database', 'files', etc.)
            status: Estado ('completed', 'failed')
            duration_seconds: Duración en segundos
            size_bytes: Tamaño en bytes
            encryption_time: Tiempo de encriptación (opcional)
            upload_time: Tiempo de subida (opcional)
            cloud_provider: Proveedor de nube (opcional)
        """
        if not self.enabled:
            return
        
        # Incrementar contador
        self.backups_total.labels(type=backup_type, status=status).inc()
        
        # Registrar duración
        self.backup_duration_seconds.labels(
            type=backup_type,
            status=status
        ).observe(duration_seconds)
        
        # Registrar tamaño
        self.backup_size_bytes.labels(type=backup_type).observe(size_bytes)
        
        # Registrar errores si falló
        if status == 'failed':
            self.backup_errors_total.labels(error_type='backup_failed').inc()
        
        # Registrar tiempos de encriptación y subida
        if encryption_time:
            self.backup_encryption_time_seconds.observe(encryption_time)
        
        if upload_time and cloud_provider:
            self.backup_upload_time_seconds.labels(
                cloud_provider=cloud_provider
            ).observe(upload_time)
    
    def update_success_rate(self, backup_type: str, rate: float) -> None:
        """Actualiza tasa de éxito."""
        if not self.enabled:
            return
        self.backup_success_rate.labels(type=backup_type).set(rate)
    
    def update_total_size(self, backup_type: str, size_bytes: int) -> None:
        """Actualiza tamaño total."""
        if not self.enabled:
            return
        self.backup_total_size_bytes.labels(type=backup_type).set(size_bytes)
    
    def record_verification(self, status: str) -> None:
        """Registra verificación de backup."""
        if not self.enabled:
            return
        self.backup_verification_total.labels(status=status).inc()
    
    def record_restore(self, status: str) -> None:
        """Registra restauración de backup."""
        if not self.enabled:
            return
        self.backup_restore_total.labels(status=status).inc()
    
    def update_health_status(self, check_type: str, is_healthy: bool) -> None:
        """Actualiza estado de salud."""
        if not self.enabled:
            return
        self.backup_health_status.labels(check_type=check_type).set(
            1.0 if is_healthy else 0.0
        )
    
    def update_disk_metrics(self, usage_percent: float, free_bytes: int) -> None:
        """Actualiza métricas de disco."""
        if not self.enabled:
            return
        self.backup_disk_usage_percent.set(usage_percent)
        self.backup_disk_free_bytes.set(free_bytes)
    
    def get_metrics(self) -> str:
        """
        Obtiene métricas en formato Prometheus.
        
        Returns:
            String con métricas en formato Prometheus
        """
        if not self.enabled:
            return "# Prometheus client not available\n"
        
        return generate_latest(REGISTRY).decode('utf-8')


# Instancia global
_metrics_instance: Optional[BackupPrometheusMetrics] = None


def get_backup_metrics() -> BackupPrometheusMetrics:
    """Obtiene instancia global de métricas."""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = BackupPrometheusMetrics()
    return _metrics_instance

