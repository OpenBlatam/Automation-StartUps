"""
Módulo de Restauración de Backups.

Proporciona funcionalidades para restaurar backups:
- Restauración de bases de datos
- Restauración de archivos
- Verificación de backups antes de restaurar
- Restauración selectiva
"""
import logging
import os
import subprocess
import gzip
import tarfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from data.airflow.plugins.backup_encryption import BackupEncryption
from data.airflow.plugins.backup_manager import BackupResult, BackupStatus

logger = logging.getLogger(__name__)


class RestoreStatus(Enum):
    """Estados de restauración."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"


@dataclass
class RestoreResult:
    """Resultado de una restauración."""
    restore_id: str
    status: RestoreStatus
    backup_id: Optional[str] = None
    restored_at: datetime = None
    duration_seconds: float = 0.0
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class BackupRestorer:
    """Restaurador de backups."""
    
    def __init__(
        self,
        backup_dir: str = "/tmp/backups",
        encryption_key: Optional[bytes] = None
    ):
        """
        Inicializa restaurador.
        
        Args:
            backup_dir: Directorio de backups
            encryption_key: Clave de encriptación (opcional)
        """
        self.backup_dir = Path(backup_dir)
        self.encryption = BackupEncryption(encryption_key) if encryption_key else None
    
    def verify_backup(self, backup_path: str) -> tuple[bool, Optional[str]]:
        """
        Verifica integridad de un backup antes de restaurar.
        
        Args:
            backup_path: Ruta del backup
        
        Returns:
            Tuple de (es_válido, mensaje_error)
        """
        try:
            backup_file = Path(backup_path)
            
            if not backup_file.exists():
                return False, f"Backup file not found: {backup_path}"
            
            # Verificar que el archivo no esté corrupto
            file_size = backup_file.stat().st_size
            if file_size == 0:
                return False, "Backup file is empty"
            
            # Si está encriptado, intentar desencriptar temporalmente
            if backup_path.endswith('.encrypted'):
                if not self.encryption:
                    return False, "Backup is encrypted but no encryption key provided"
                
                # Verificar que se puede desencriptar
                try:
                    temp_path = str(backup_file) + ".temp"
                    if not self.encryption.decrypt_file(backup_path, temp_path):
                        return False, "Failed to decrypt backup"
                    os.remove(temp_path)
                except Exception as e:
                    return False, f"Decryption test failed: {e}"
            
            # Si está comprimido, verificar que se puede descomprimir
            if backup_path.endswith('.gz'):
                try:
                    with gzip.open(backup_path, 'rb') as f:
                        f.read(1024)  # Leer primeros bytes
                except Exception as e:
                    return False, f"Compression verification failed: {e}"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Backup verification failed: {e}", exc_info=True)
            return False, str(e)
    
    def restore_database(
        self,
        backup_path: str,
        connection_string: str,
        db_type: str = "postgresql",
        drop_existing: bool = False,
        verify_backup: bool = True
    ) -> RestoreResult:
        """
        Restaura backup de base de datos.
        
        Args:
            backup_path: Ruta del backup
            connection_string: Connection string de destino
            db_type: Tipo de BD
            drop_existing: Si eliminar base de datos existente
            verify_backup: Si verificar backup antes de restaurar
        """
        restore_id = f"restore-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        start_time = datetime.now()
        
        try:
            # Verificar backup
            if verify_backup:
                is_valid, error_msg = self.verify_backup(backup_path)
                if not is_valid:
                    return RestoreResult(
                        restore_id=restore_id,
                        status=RestoreStatus.FAILED,
                        error=f"Backup verification failed: {error_msg}",
                        restored_at=start_time
                    )
            
            # Preparar archivo para restaurar
            restore_file = self._prepare_backup_file(backup_path)
            if not restore_file:
                return RestoreResult(
                    restore_id=restore_id,
                    status=RestoreStatus.FAILED,
                    error="Failed to prepare backup file",
                    restored_at=start_time
                )
            
            # Restaurar según tipo de BD
            if db_type == "postgresql":
                result = self._restore_postgresql(
                    restore_file, connection_string, drop_existing, restore_id, start_time
                )
            elif db_type == "mysql":
                result = self._restore_mysql(
                    restore_file, connection_string, drop_existing, restore_id, start_time
                )
            else:
                return RestoreResult(
                    restore_id=restore_id,
                    status=RestoreStatus.FAILED,
                    error=f"Unsupported database type: {db_type}",
                    restored_at=start_time
                )
            
            # Limpiar archivo temporal si se creó
            if restore_file != backup_path and os.path.exists(restore_file):
                os.remove(restore_file)
            
            return result
            
        except Exception as e:
            logger.error(f"Restore failed: {e}", exc_info=True)
            return RestoreResult(
                restore_id=restore_id,
                status=RestoreStatus.FAILED,
                error=str(e),
                restored_at=start_time
            )
    
    def _prepare_backup_file(self, backup_path: str) -> Optional[str]:
        """
        Prepara archivo de backup para restaurar (desencripta/descomprime si es necesario).
        
        Args:
            backup_path: Ruta del backup
        
        Returns:
            Ruta del archivo listo para restaurar, o None si falla
        """
        backup_file = Path(backup_path)
        
        # Si está encriptado, desencriptar
        if backup_path.endswith('.encrypted'):
            if not self.encryption:
                logger.error("Backup is encrypted but no key provided")
                return None
            
            decrypted_path = str(backup_file).replace('.encrypted', '')
            if not self.encryption.decrypt_file(backup_path, decrypted_path):
                return None
            backup_path = decrypted_path
            backup_file = Path(backup_path)
        
        # Si está comprimido, descomprimir
        if backup_path.endswith('.gz'):
            decompressed_path = str(backup_file).replace('.gz', '')
            with gzip.open(backup_path, 'rb') as f_in:
                with open(decompressed_path, 'wb') as f_out:
                    f_out.write(f_in.read())
            backup_path = decompressed_path
        
        return backup_path
    
    def _restore_postgresql(
        self,
        backup_file: str,
        connection_string: str,
        drop_existing: bool,
        restore_id: str,
        start_time: datetime
    ) -> RestoreResult:
        """Restaura backup de PostgreSQL."""
        cmd = ["psql", connection_string]
        
        if drop_existing:
            logger.warning("drop_existing=True not fully supported for PostgreSQL")
        
        try:
            with open(backup_file, 'r') as f:
                result = subprocess.run(
                    cmd,
                    stdin=f,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    text=True,
                    check=True
                )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return RestoreResult(
                restore_id=restore_id,
                status=RestoreStatus.COMPLETED,
                restored_at=start_time,
                duration_seconds=duration,
                details={'output': result.stdout[:500]}  # Primeros 500 chars
            )
        except subprocess.CalledProcessError as e:
            return RestoreResult(
                restore_id=restore_id,
                status=RestoreStatus.FAILED,
                error=f"psql error: {e.stderr.decode() if e.stderr else str(e)}",
                restored_at=start_time
            )
    
    def _restore_mysql(
        self,
        backup_file: str,
        connection_string: str,
        drop_existing: bool,
        restore_id: str,
        start_time: datetime
    ) -> RestoreResult:
        """Restaura backup de MySQL."""
        cmd = ["mysql", connection_string]
        
        if drop_existing:
            cmd.append("--force")
        
        try:
            with open(backup_file, 'r') as f:
                result = subprocess.run(
                    cmd,
                    stdin=f,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    text=True,
                    check=True
                )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return RestoreResult(
                restore_id=restore_id,
                status=RestoreStatus.COMPLETED,
                restored_at=start_time,
                duration_seconds=duration
            )
        except subprocess.CalledProcessError as e:
            return RestoreResult(
                restore_id=restore_id,
                status=RestoreStatus.FAILED,
                error=f"mysql error: {e.stderr.decode() if e.stderr else str(e)}",
                restored_at=start_time
            )
    
    def restore_files(
        self,
        backup_path: str,
        target_dir: str,
        verify_backup: bool = True
    ) -> RestoreResult:
        """
        Restaura backup de archivos.
        
        Args:
            backup_path: Ruta del backup
            target_dir: Directorio de destino
            verify_backup: Si verificar backup antes de restaurar
        """
        restore_id = f"restore-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        start_time = datetime.now()
        
        try:
            # Verificar backup
            if verify_backup:
                is_valid, error_msg = self.verify_backup(backup_path)
                if not is_valid:
                    return RestoreResult(
                        restore_id=restore_id,
                        status=RestoreStatus.FAILED,
                        error=f"Backup verification failed: {error_msg}",
                        restored_at=start_time
                    )
            
            # Preparar archivo
            restore_file = self._prepare_backup_file(backup_path)
            if not restore_file:
                return RestoreResult(
                    restore_id=restore_id,
                    status=RestoreStatus.FAILED,
                    error="Failed to prepare backup file",
                    restored_at=start_time
                )
            
            # Crear directorio de destino
            target_path = Path(target_dir)
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Extraer archivos
            with tarfile.open(restore_file, "r:*") as tar:
                tar.extractall(target_dir)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Limpiar archivo temporal
            if restore_file != backup_path and os.path.exists(restore_file):
                os.remove(restore_file)
            
            return RestoreResult(
                restore_id=restore_id,
                status=RestoreStatus.COMPLETED,
                restored_at=start_time,
                duration_seconds=duration,
                details={'target_dir': target_dir}
            )
            
        except Exception as e:
            logger.error(f"File restore failed: {e}", exc_info=True)
            return RestoreResult(
                restore_id=restore_id,
                status=RestoreStatus.FAILED,
                error=str(e),
                restored_at=start_time
            )
    
    def list_available_backups(
        self,
        backup_type: Optional[str] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Lista backups disponibles.
        
        Args:
            backup_type: Tipo de backup ('db', 'files', None = todos)
            days: Días hacia atrás para buscar
        """
        backups = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        patterns = {
            'db': ['*.sql', '*.sql.gz', '*.sql.encrypted', '*.sql.gz.encrypted'],
            'files': ['*.tar.gz', '*.tar.gz.encrypted']
        }
        
        if backup_type:
            patterns_to_use = patterns.get(backup_type, [])
        else:
            patterns_to_use = sum(patterns.values(), [])
        
        for pattern in patterns_to_use:
            for backup_file in self.backup_dir.glob(pattern):
                if backup_file.is_file():
                    file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    if file_time >= cutoff_date:
                        backups.append({
                            'path': str(backup_file),
                            'name': backup_file.name,
                            'size': backup_file.stat().st_size,
                            'modified': file_time.isoformat(),
                            'type': 'db' if 'sql' in pattern else 'files'
                        })
        
        # Ordenar por fecha (más reciente primero)
        backups.sort(key=lambda x: x['modified'], reverse=True)
        
        return backups

