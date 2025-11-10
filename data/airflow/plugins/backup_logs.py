"""
Módulo de Backup de Logs y Auditoría.

Proporciona:
- Backup de logs de aplicaciones
- Backup de logs de sistema
- Backup de logs de auditoría
- Archivo y compresión de logs
"""
import logging
import os
import gzip
import shutil
import tarfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LogBackup:
    """Backup de logs."""
    backup_id: str
    log_type: str  # 'application', 'system', 'audit'
    source_paths: List[str]
    output_path: str
    size_bytes: int
    compressed: bool
    backed_up_at: datetime


class LogBackupManager:
    """Gestor de backups de logs."""
    
    def __init__(
        self,
        backup_dir: str = "/tmp/log-backups",
        compress: bool = True
    ):
        """
        Inicializa gestor de backups de logs.
        
        Args:
            backup_dir: Directorio de backups
            compress: Si comprimir logs
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.compress = compress
    
    def backup_application_logs(
        self,
        log_paths: List[str],
        app_name: Optional[str] = None,
        retention_days: int = 7
    ) -> LogBackup:
        """
        Hace backup de logs de aplicaciones.
        
        Args:
            log_paths: Rutas de logs a respaldar
            app_name: Nombre de la aplicación
            retention_days: Días de retención
        """
        backup_id = f"app-logs-{app_name or 'unknown'}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        output_path = self.backup_dir / f"{backup_id}.tar.gz"
        
        # Filtrar logs antiguos (últimos N días)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        try:
            with tarfile.open(str(output_path), "w:gz") as tar:
                total_size = 0
                
                for log_path in log_paths:
                    log_file = Path(log_path)
                    if not log_file.exists():
                        continue
                    
                    # Si es directorio, agregar archivos recientes
                    if log_file.is_dir():
                        for sub_file in log_file.rglob("*"):
                            if sub_file.is_file():
                                file_time = datetime.fromtimestamp(sub_file.stat().st_mtime)
                                if file_time >= cutoff_date:
                                    tar.add(sub_file, arcname=sub_file.name)
                                    total_size += sub_file.stat().st_size
                    else:
                        # Archivo individual
                        file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                        if file_time >= cutoff_date:
                            tar.add(log_file, arcname=log_file.name)
                            total_size += log_file.stat().st_size
            
            return LogBackup(
                backup_id=backup_id,
                log_type='application',
                source_paths=log_paths,
                output_path=str(output_path),
                size_bytes=output_path.stat().st_size,
                compressed=True,
                backed_up_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Application logs backup failed: {e}", exc_info=True)
            raise
    
    def backup_system_logs(
        self,
        system_log_paths: Optional[List[str]] = None
    ) -> LogBackup:
        """
        Hace backup de logs del sistema.
        
        Args:
            system_log_paths: Rutas de logs del sistema (None = defaults)
        """
        if system_log_paths is None:
            # Paths por defecto según sistema operativo
            if os.name == 'posix':  # Linux/Mac
                system_log_paths = [
                    '/var/log/syslog',
                    '/var/log/messages',
                    '/var/log/auth.log',
                    '/var/log/kern.log'
                ]
            else:
                system_log_paths = []
        
        backup_id = f"system-logs-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        output_path = self.backup_dir / f"{backup_id}.tar.gz"
        
        try:
            with tarfile.open(str(output_path), "w:gz") as tar:
                for log_path in system_log_paths:
                    log_file = Path(log_path)
                    if log_file.exists() and log_file.is_file():
                        tar.add(log_file, arcname=log_file.name)
            
            return LogBackup(
                backup_id=backup_id,
                log_type='system',
                source_paths=system_log_paths,
                output_path=str(output_path),
                size_bytes=output_path.stat().st_size,
                compressed=True,
                backed_up_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"System logs backup failed: {e}", exc_info=True)
            raise
    
    def backup_audit_logs(
        self,
        audit_log_path: str = "/var/log/audit"
    ) -> LogBackup:
        """
        Hace backup de logs de auditoría.
        
        Args:
            audit_log_path: Ruta de logs de auditoría
        """
        backup_id = f"audit-logs-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        output_path = self.backup_dir / f"{backup_id}.tar.gz"
        
        audit_path = Path(audit_log_path)
        
        try:
            if not audit_path.exists():
                logger.warning(f"Audit log path not found: {audit_log_path}")
                # Crear backup vacío
                output_path.touch()
                return LogBackup(
                    backup_id=backup_id,
                    log_type='audit',
                    source_paths=[audit_log_path],
                    output_path=str(output_path),
                    size_bytes=0,
                    compressed=True,
                    backed_up_at=datetime.now()
                )
            
            with tarfile.open(str(output_path), "w:gz") as tar:
                if audit_path.is_dir():
                    for log_file in audit_path.glob("*.log"):
                        tar.add(log_file, arcname=log_file.name)
                else:
                    tar.add(audit_path, arcname=audit_path.name)
            
            return LogBackup(
                backup_id=backup_id,
                log_type='audit',
                source_paths=[audit_log_path],
                output_path=str(output_path),
                size_bytes=output_path.stat().st_size,
                compressed=True,
                backed_up_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Audit logs backup failed: {e}", exc_info=True)
            raise
    
    def list_log_backups(
        self,
        log_type: Optional[str] = None,
        days: int = 30
    ) -> List[LogBackup]:
        """
        Lista backups de logs.
        
        Args:
            log_type: Tipo de log (None = todos)
            days: Días hacia atrás
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        backups = []
        
        for backup_file in self.backup_dir.glob("*.tar.gz"):
            file_time = datetime.now() - timedelta(days=days)
            if file_time < cutoff_date:
                continue
            
            # Determinar tipo desde nombre
            backup_type = 'unknown'
            if 'app-logs' in backup_file.name:
                backup_type = 'application'
            elif 'system-logs' in backup_file.name:
                backup_type = 'system'
            elif 'audit-logs' in backup_file.name:
                backup_type = 'audit'
            
            if log_type is None or backup_type == log_type:
                backups.append(LogBackup(
                    backup_id=backup_file.stem,
                    log_type=backup_type,
                    source_paths=[],
                    output_path=str(backup_file),
                    size_bytes=backup_file.stat().st_size,
                    compressed=True,
                    backed_up_at=datetime.fromtimestamp(backup_file.stat().st_mtime)
                ))
        
        return sorted(backups, key=lambda b: b.backed_up_at, reverse=True)

