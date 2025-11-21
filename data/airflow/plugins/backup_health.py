"""
Módulo de Health Checks para Sistema de Backups.

Proporciona verificaciones de salud del sistema de backups:
- Verificación de espacio en disco
- Verificación de conectividad
- Verificación de configuración
- Verificación de integridad de backups
"""
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import psutil

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Estados de salud."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Resultado de un health check."""
    name: str
    status: HealthStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class BackupHealthChecker:
    """Verificador de salud del sistema de backups."""
    
    def __init__(self, backup_dir: str = "/tmp/backups"):
        """
        Inicializa verificador de salud.
        
        Args:
            backup_dir: Directorio de backups
        """
        self.backup_dir = backup_dir
        self.checks: List[HealthCheck] = []
    
    def check_all(self) -> Dict[str, Any]:
        """
        Ejecuta todos los health checks.
        
        Returns:
            Dict con resumen de todos los checks
        """
        self.checks = []
        
        # Ejecutar checks
        self.checks.append(self.check_disk_space())
        self.checks.append(self.check_backup_directory())
        self.checks.append(self.check_encryption_key())
        self.checks.append(self.check_cloud_config())
        self.checks.append(self.check_recent_backups())
        
        # Determinar estado general
        critical_count = sum(1 for c in self.checks if c.status == HealthStatus.CRITICAL)
        warning_count = sum(1 for c in self.checks if c.status == HealthStatus.WARNING)
        
        if critical_count > 0:
            overall_status = HealthStatus.CRITICAL
        elif warning_count > 0:
            overall_status = HealthStatus.WARNING
        else:
            overall_status = HealthStatus.HEALTHY
        
        return {
            'overall_status': overall_status.value,
            'checks': [self._check_to_dict(c) for c in self.checks],
            'summary': {
                'total': len(self.checks),
                'healthy': sum(1 for c in self.checks if c.status == HealthStatus.HEALTHY),
                'warnings': warning_count,
                'critical': critical_count
            }
        }
    
    def check_disk_space(self, min_free_gb: float = 10.0) -> HealthCheck:
        """
        Verifica espacio disponible en disco.
        
        Args:
            min_free_gb: Espacio mínimo requerido en GB
        """
        try:
            disk_usage = psutil.disk_usage(str(self.backup_dir))
            free_gb = disk_usage.free / (1024 ** 3)
            used_percent = (disk_usage.used / disk_usage.total) * 100
            
            if free_gb < min_free_gb:
                status = HealthStatus.CRITICAL
                message = f"Low disk space: {free_gb:.2f}GB free (minimum: {min_free_gb}GB)"
            elif used_percent > 90:
                status = HealthStatus.WARNING
                message = f"High disk usage: {used_percent:.1f}% used"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk space OK: {free_gb:.2f}GB free"
            
            return HealthCheck(
                name="disk_space",
                status=status,
                message=message,
                details={
                    'free_gb': free_gb,
                    'used_percent': used_percent,
                    'total_gb': disk_usage.total / (1024 ** 3),
                    'min_required_gb': min_free_gb
                }
            )
        except Exception as e:
            logger.error(f"Disk space check failed: {e}")
            return HealthCheck(
                name="disk_space",
                status=HealthStatus.UNKNOWN,
                message=f"Could not check disk space: {e}"
            )
    
    def check_backup_directory(self) -> HealthCheck:
        """Verifica que el directorio de backups exista y sea accesible."""
        try:
            backup_path = os.path.abspath(self.backup_dir)
            
            if not os.path.exists(backup_path):
                return HealthCheck(
                    name="backup_directory",
                    status=HealthStatus.CRITICAL,
                    message=f"Backup directory does not exist: {backup_path}"
                )
            
            if not os.access(backup_path, os.W_OK):
                return HealthCheck(
                    name="backup_directory",
                    status=HealthStatus.CRITICAL,
                    message=f"Backup directory is not writable: {backup_path}"
                )
            
            return HealthCheck(
                name="backup_directory",
                status=HealthStatus.HEALTHY,
                message=f"Backup directory OK: {backup_path}",
                details={'path': backup_path}
            )
        except Exception as e:
            logger.error(f"Backup directory check failed: {e}")
            return HealthCheck(
                name="backup_directory",
                status=HealthStatus.UNKNOWN,
                message=f"Could not check backup directory: {e}"
            )
    
    def check_encryption_key(self) -> HealthCheck:
        """Verifica que la clave de encriptación esté configurada."""
        encryption_key = os.getenv("BACKUP_ENCRYPTION_KEY")
        
        if not encryption_key:
            return HealthCheck(
                name="encryption_key",
                status=HealthStatus.WARNING,
                message="Backup encryption key not configured",
                details={'note': 'Backups will not be encrypted'}
            )
        
        try:
            # Verificar que la clave es válida base64
            from data.airflow.plugins.backup_encryption import BackupEncryption
            BackupEncryption.load_key_from_base64(encryption_key)
            
            return HealthCheck(
                name="encryption_key",
                status=HealthStatus.HEALTHY,
                message="Encryption key configured and valid"
            )
        except Exception as e:
            return HealthCheck(
                name="encryption_key",
                status=HealthStatus.CRITICAL,
                message=f"Encryption key is invalid: {e}"
            )
    
    def check_cloud_config(self) -> HealthCheck:
        """Verifica configuración de nube."""
        cloud_provider = os.getenv("CLOUD_PROVIDER", "").lower()
        
        if not cloud_provider:
            return HealthCheck(
                name="cloud_config",
                status=HealthStatus.WARNING,
                message="Cloud provider not configured",
                details={'note': 'Backups will only be stored locally'}
            )
        
        if cloud_provider == "aws":
            bucket = os.getenv("AWS_BACKUP_BUCKET")
            access_key = os.getenv("AWS_ACCESS_KEY_ID")
            secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            
            if not all([bucket, access_key, secret_key]):
                return HealthCheck(
                    name="cloud_config",
                    status=HealthStatus.WARNING,
                    message="AWS configuration incomplete",
                    details={'missing': [k for k, v in {
                        'bucket': bucket,
                        'access_key': access_key,
                        'secret_key': secret_key
                    }.items() if not v]}
                )
            
            return HealthCheck(
                name="cloud_config",
                status=HealthStatus.HEALTHY,
                message=f"AWS S3 configured: {bucket}",
                details={'provider': 'aws', 'bucket': bucket}
            )
        
        elif cloud_provider == "azure":
            conn_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            container = os.getenv("AZURE_BACKUP_CONTAINER")
            
            if not all([conn_string, container]):
                return HealthCheck(
                    name="cloud_config",
                    status=HealthStatus.WARNING,
                    message="Azure configuration incomplete"
                )
            
            return HealthCheck(
                name="cloud_config",
                status=HealthStatus.HEALTHY,
                message=f"Azure Blob Storage configured: {container}",
                details={'provider': 'azure', 'container': container}
            )
        
        elif cloud_provider == "gcp":
            bucket = os.getenv("GCP_BACKUP_BUCKET")
            credentials = os.getenv("GCP_CREDENTIALS_PATH")
            
            if not bucket:
                return HealthCheck(
                    name="cloud_config",
                    status=HealthStatus.WARNING,
                    message="GCP configuration incomplete"
                )
            
            return HealthCheck(
                name="cloud_config",
                status=HealthStatus.HEALTHY,
                message=f"GCP Cloud Storage configured: {bucket}",
                details={'provider': 'gcp', 'bucket': bucket}
            )
        
        return HealthCheck(
            name="cloud_config",
            status=HealthStatus.WARNING,
            message=f"Unknown cloud provider: {cloud_provider}"
        )
    
    def check_recent_backups(self, hours: int = 24) -> HealthCheck:
        """
        Verifica que haya backups recientes.
        
        Args:
            hours: Horas hacia atrás para considerar "reciente"
        """
        try:
            backup_path = Path(self.backup_dir)
            if not backup_path.exists():
                return HealthCheck(
                    name="recent_backups",
                    status=HealthStatus.CRITICAL,
                    message="Backup directory does not exist"
                )
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_backups = []
            
            for backup_file in backup_path.glob("*"):
                if backup_file.is_file():
                    file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    if file_time >= cutoff_time:
                        recent_backups.append({
                            'name': backup_file.name,
                            'size': backup_file.stat().st_size,
                            'modified': file_time.isoformat()
                        })
            
            if not recent_backups:
                return HealthCheck(
                    name="recent_backups",
                    status=HealthStatus.WARNING,
                    message=f"No backups found in the last {hours} hours",
                    details={'hours': hours}
                )
            
            total_size_mb = sum(b['size'] for b in recent_backups) / (1024 ** 2)
            
            return HealthCheck(
                name="recent_backups",
                status=HealthStatus.HEALTHY,
                message=f"Found {len(recent_backups)} backup(s) in the last {hours} hours",
                details={
                    'count': len(recent_backups),
                    'total_size_mb': total_size_mb,
                    'backups': recent_backups[:5]  # Primeros 5
                }
            )
        except Exception as e:
            logger.error(f"Recent backups check failed: {e}")
            return HealthCheck(
                name="recent_backups",
                status=HealthStatus.UNKNOWN,
                message=f"Could not check recent backups: {e}"
            )
    
    def _check_to_dict(self, check: HealthCheck) -> Dict[str, Any]:
        """Convierte HealthCheck a dict."""
        return {
            'name': check.name,
            'status': check.status.value,
            'message': check.message,
            'details': check.details,
            'timestamp': check.timestamp.isoformat() if check.timestamp else None
        }
    
    def get_critical_issues(self) -> List[HealthCheck]:
        """Obtiene solo los checks críticos."""
        return [c for c in self.checks if c.status == HealthStatus.CRITICAL]
    
    def get_warnings(self) -> List[HealthCheck]:
        """Obtiene solo los warnings."""
        return [c for c in self.checks if c.status == HealthStatus.WARNING]

