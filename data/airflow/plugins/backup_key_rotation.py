"""
Módulo de Rotación de Claves de Encriptación.

Proporciona:
- Rotación automática de claves
- Re-encriptación de backups antiguos
- Gestión de múltiples claves
- Migración de backups a nueva clave
"""
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass

from data.airflow.plugins.backup_encryption import BackupEncryption

logger = logging.getLogger(__name__)


@dataclass
class KeyRotationResult:
    """Resultado de rotación de clave."""
    rotation_id: str
    old_key_id: str
    new_key_id: str
    backups_reencrypted: int
    backups_failed: int
    rotation_started_at: datetime
    rotation_completed_at: Optional[datetime] = None
    error: Optional[str] = None


class BackupKeyRotator:
    """Rotador de claves de encriptación."""
    
    def __init__(
        self,
        backup_dir: str = "/tmp/backups",
        key_storage_dir: str = "/tmp/backup-keys"
    ):
        """
        Inicializa rotador de claves.
        
        Args:
            backup_dir: Directorio de backups
            key_storage_dir: Directorio para almacenar claves
        """
        self.backup_dir = Path(backup_dir)
        self.key_storage_dir = Path(key_storage_dir)
        self.key_storage_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_new_key(self) -> bytes:
        """Genera nueva clave de encriptación."""
        encryption = BackupEncryption()
        return encryption.key
    
    def save_key(
        self,
        key: bytes,
        key_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Guarda clave de forma segura.
        
        Args:
            key: Clave a guardar
            key_id: Identificador único de la clave
            metadata: Metadatos adicionales
        
        Returns:
            Ruta del archivo de clave guardado
        """
        key_file = self.key_storage_dir / f"key-{key_id}.key"
        
        # Guardar clave encriptada con clave maestra (si existe)
        key_b64 = BackupEncryption.load_key_from_base64(
            BackupEncryption(None).get_key_base64()
        )
        
        # Por seguridad, en producción usar un key management system
        with open(key_file, 'wb') as f:
            f.write(key)
        
        # Guardar metadata
        if metadata:
            metadata_file = self.key_storage_dir / f"key-{key_id}.metadata.json"
            import json
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f)
        
        logger.info(f"Saved key {key_id} to {key_file}")
        return str(key_file)
    
    def rotate_keys(
        self,
        old_key: bytes,
        new_key: Optional[bytes] = None,
        reencrypt_backups: bool = True,
        days_back: int = 90
    ) -> KeyRotationResult:
        """
        Rota claves de encriptación.
        
        Args:
            old_key: Clave antigua
            new_key: Nueva clave (None = generar nueva)
            reencrypt_backups: Si re-encriptar backups antiguos
            days_back: Días hacia atrás para re-encriptar
        
        Returns:
            Resultado de la rotación
        """
        rotation_id = f"rotation-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        old_key_id = self._get_key_id(old_key)
        
        if new_key is None:
            new_key = self.generate_new_key()
        
        new_key_id = self._get_key_id(new_key)
        start_time = datetime.now()
        
        result = KeyRotationResult(
            rotation_id=rotation_id,
            old_key_id=old_key_id,
            new_key_id=new_key_id,
            backups_reencrypted=0,
            backups_failed=0,
            rotation_started_at=start_time
        )
        
        try:
            # Guardar nueva clave
            self.save_key(
                new_key,
                new_key_id,
                metadata={
                    'created_at': start_time.isoformat(),
                    'rotated_from': old_key_id
                }
            )
            
            # Re-encriptar backups si se solicita
            if reencrypt_backups:
                reencrypt_result = self._reencrypt_backups(
                    old_key=old_key,
                    new_key=new_key,
                    days_back=days_back
                )
                result.backups_reencrypted = reencrypt_result['reencrypted']
                result.backups_failed = reencrypt_result['failed']
            
            result.rotation_completed_at = datetime.now()
            logger.info(f"Key rotation completed: {rotation_id}")
            
        except Exception as e:
            logger.error(f"Key rotation failed: {e}", exc_info=True)
            result.error = str(e)
        
        return result
    
    def _reencrypt_backups(
        self,
        old_key: bytes,
        new_key: bytes,
        days_back: int
    ) -> Dict[str, Any]:
        """Re-encripta backups con nueva clave."""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        reencrypted = 0
        failed = 0
        
        old_encryption = BackupEncryption(old_key)
        new_encryption = BackupEncryption(new_key)
        
        for backup_file in self.backup_dir.glob("*.encrypted"):
            if backup_file.stat().st_mtime < cutoff_date.timestamp():
                continue
            
            try:
                # Desencriptar con clave antigua
                temp_decrypted = str(backup_file) + ".temp"
                if not old_encryption.decrypt_file(str(backup_file), temp_decrypted):
                    failed += 1
                    continue
                
                # Encriptar con nueva clave
                new_encrypted = str(backup_file) + ".new"
                if new_encryption.encrypt_file(temp_decrypted, new_encrypted):
                    # Reemplazar archivo antiguo
                    backup_file.unlink()
                    Path(new_encrypted).rename(backup_file)
                    os.remove(temp_decrypted)
                    reencrypted += 1
                else:
                    failed += 1
                    if os.path.exists(temp_decrypted):
                        os.remove(temp_decrypted)
                    
            except Exception as e:
                logger.error(f"Re-encryption failed for {backup_file}: {e}")
                failed += 1
        
        return {
            'reencrypted': reencrypted,
            'failed': failed
        }
    
    def _get_key_id(self, key: bytes) -> str:
        """Genera ID único para una clave."""
        import hashlib
        return hashlib.sha256(key).hexdigest()[:16]
    
    def list_keys(self) -> List[Dict[str, Any]]:
        """Lista todas las claves almacenadas."""
        keys = []
        
        for key_file in self.key_storage_dir.glob("key-*.key"):
            key_id = key_file.stem.replace("key-", "")
            metadata_file = self.key_storage_dir / f"key-{key_id}.metadata.json"
            
            metadata = {}
            if metadata_file.exists():
                import json
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            
            keys.append({
                'key_id': key_id,
                'key_file': str(key_file),
                'metadata': metadata
            })
        
        return keys

