"""
Módulo de Verificación Automática de Backups.

Verifica integridad de backups automáticamente:
- Verificación de checksums
- Pruebas de restauración
- Verificación de encriptación
- Tests de compresión
"""
import logging
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from data.airflow.plugins.backup_encryption import BackupEncryption
from data.airflow.plugins.backup_manager import BackupStatus

logger = logging.getLogger(__name__)


class VerificationStatus(Enum):
    """Estados de verificación."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class VerificationResult:
    """Resultado de verificación."""
    backup_path: str
    status: VerificationStatus
    checksum_valid: bool = False
    encryption_valid: bool = False
    compression_valid: bool = False
    restore_test_passed: bool = False
    verified_at: datetime = None
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.verified_at is None:
            self.verified_at = datetime.now()


class BackupVerifier:
    """Verificador de backups."""
    
    def __init__(
        self,
        backup_dir: str = "/tmp/backups",
        encryption_key: Optional[bytes] = None
    ):
        """
        Inicializa verificador.
        
        Args:
            backup_dir: Directorio de backups
            encryption_key: Clave de encriptación
        """
        self.backup_dir = Path(backup_dir)
        self.encryption = BackupEncryption(encryption_key) if encryption_key else None
    
    def verify_backup(
        self,
        backup_path: str,
        verify_checksum: bool = True,
        verify_encryption: bool = True,
        verify_compression: bool = True,
        test_restore: bool = False,
        restore_test_db: Optional[str] = None
    ) -> VerificationResult:
        """
        Verifica integridad completa de un backup.
        
        Args:
            backup_path: Ruta del backup
            verify_checksum: Si verificar checksum
            verify_encryption: Si verificar encriptación
            verify_compression: Si verificar compresión
            test_restore: Si hacer test de restauración
            restore_test_db: Connection string para test de restauración
        """
        result = VerificationResult(
            backup_path=backup_path,
            status=VerificationStatus.PASSED
        )
        
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            result.status = VerificationStatus.FAILED
            result.errors.append(f"Backup file not found: {backup_path}")
            return result
        
        # Verificar checksum
        if verify_checksum:
            if not self._verify_checksum(backup_path, result):
                result.status = VerificationStatus.FAILED
        
        # Verificar encriptación
        if verify_encryption and backup_path.endswith('.encrypted'):
            if not self._verify_encryption(backup_path, result):
                result.status = VerificationStatus.FAILED
        
        # Verificar compresión
        if verify_compression and backup_path.endswith('.gz'):
            if not self._verify_compression(backup_path, result):
                result.status = VerificationStatus.FAILED
        
        # Test de restauración
        if test_restore and restore_test_db:
            if not self._test_restore(backup_path, restore_test_db, result):
                result.status = VerificationStatus.WARNING
                result.warnings.append("Restore test failed")
        
        return result
    
    def verify_all_recent_backups(
        self,
        days: int = 7,
        verify_checksum: bool = True,
        verify_encryption: bool = True,
        verify_compression: bool = True
    ) -> List[VerificationResult]:
        """
        Verifica todos los backups recientes.
        
        Args:
            days: Días hacia atrás
            verify_checksum: Si verificar checksum
            verify_encryption: Si verificar encriptación
            verify_compression: Si verificar compresión
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        results = []
        
        for backup_file in self.backup_dir.glob("*"):
            if backup_file.is_file():
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_time >= cutoff_date:
                    result = self.verify_backup(
                        str(backup_file),
                        verify_checksum=verify_checksum,
                        verify_encryption=verify_encryption,
                        verify_compression=verify_compression
                    )
                    results.append(result)
        
        return results
    
    def _verify_checksum(self, backup_path: str, result: VerificationResult) -> bool:
        """Verifica checksum si existe archivo .checksum."""
        checksum_file = Path(backup_path + ".checksum")
        
        if not checksum_file.exists():
            result.warnings.append("No checksum file found")
            return True  # No es error, solo warning
        
        try:
            # Calcular checksum actual
            import hashlib
            sha256_hash = hashlib.sha256()
            with open(backup_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            current_checksum = sha256_hash.hexdigest()
            
            # Leer checksum esperado
            with open(checksum_file, 'r') as f:
                expected_checksum = f.read().strip()
            
            if current_checksum == expected_checksum:
                result.checksum_valid = True
                return True
            else:
                result.errors.append(f"Checksum mismatch: expected {expected_checksum[:16]}..., got {current_checksum[:16]}...")
                return False
        except Exception as e:
            result.errors.append(f"Checksum verification error: {e}")
            return False
    
    def _verify_encryption(self, backup_path: str, result: VerificationResult) -> bool:
        """Verifica que el backup encriptado se puede desencriptar."""
        if not self.encryption:
            result.errors.append("Backup is encrypted but no encryption key provided")
            return False
        
        try:
            # Intentar desencriptar a archivo temporal
            temp_path = backup_path + ".temp_verify"
            if self.encryption.decrypt_file(backup_path, temp_path):
                result.encryption_valid = True
                os.remove(temp_path)
                return True
            else:
                result.errors.append("Failed to decrypt backup")
                return False
        except Exception as e:
            result.errors.append(f"Encryption verification error: {e}")
            return False
    
    def _verify_compression(self, backup_path: str, result: VerificationResult) -> bool:
        """Verifica que el backup comprimido se puede descomprimir."""
        try:
            import gzip
            with gzip.open(backup_path, 'rb') as f:
                f.read(1024)  # Leer primeros bytes
            result.compression_valid = True
            return True
        except Exception as e:
            result.errors.append(f"Compression verification error: {e}")
            return False
    
    def _test_restore(
        self,
        backup_path: str,
        test_db_connection: str,
        result: VerificationResult
    ) -> bool:
        """Hace test de restauración en base de datos de prueba."""
        try:
            from data.airflow.plugins.backup_restore import BackupRestorer
            
            restorer = BackupRestorer(
                backup_dir=str(self.backup_dir.parent),
                encryption_key=self.encryption.key if self.encryption else None
            )
            
            # Detectar tipo de BD
            db_type = "postgresql" if "postgresql" in test_db_connection.lower() else "mysql"
            
            # Intentar restaurar (sin hacer drop_existing para seguridad)
            restore_result = restorer.restore_database(
                backup_path=backup_path,
                connection_string=test_db_connection,
                db_type=db_type,
                drop_existing=False,
                verify_backup=False  # Ya verificamos antes
            )
            
            if restore_result.status.value == 'completed':
                result.restore_test_passed = True
                return True
            else:
                result.errors.append(f"Restore test failed: {restore_result.error}")
                return False
        except Exception as e:
            result.errors.append(f"Restore test error: {e}")
            return False
    
    def generate_verification_report(
        self,
        results: List[VerificationResult]
    ) -> Dict[str, Any]:
        """Genera reporte de verificación."""
        total = len(results)
        passed = sum(1 for r in results if r.status == VerificationStatus.PASSED)
        failed = sum(1 for r in results if r.status == VerificationStatus.FAILED)
        warnings_count = sum(1 for r in results if r.status == VerificationStatus.WARNING)
        
        return {
            'total_backups': total,
            'passed': passed,
            'failed': failed,
            'warnings': warnings_count,
            'pass_rate': passed / total if total > 0 else 0.0,
            'results': [
                {
                    'backup_path': r.backup_path,
                    'status': r.status.value,
                    'checksum_valid': r.checksum_valid,
                    'encryption_valid': r.encryption_valid,
                    'compression_valid': r.compression_valid,
                    'errors': r.errors,
                    'warnings': r.warnings
                }
                for r in results
            ]
        }

