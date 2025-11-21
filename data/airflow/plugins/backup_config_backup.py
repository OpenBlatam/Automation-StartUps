"""
Módulo de Backup de Configuraciones.

Proporciona backup de:
- Configuraciones de aplicaciones
- Variables de entorno
- Archivos de configuración
- Secrets (encriptados)
"""
import logging
import os
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from data.airflow.plugins.backup_encryption import BackupEncryption

logger = logging.getLogger(__name__)


@dataclass
class ConfigBackup:
    """Backup de configuración."""
    config_id: str
    config_type: str  # 'env', 'file', 'app_config'
    source: str
    content: Dict[str, Any]
    encrypted: bool
    backed_up_at: datetime


class ConfigurationBackup:
    """Gestor de backups de configuraciones."""
    
    def __init__(
        self,
        backup_dir: str = "/tmp/config-backups",
        encryption_key: Optional[bytes] = None
    ):
        """
        Inicializa gestor de backups de configuraciones.
        
        Args:
            backup_dir: Directorio de backups
            encryption_key: Clave de encriptación
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.encryption = BackupEncryption(encryption_key) if encryption_key else None
    
    def backup_environment_variables(
        self,
        env_prefix: Optional[str] = None,
        sensitive_keys: Optional[List[str]] = None
    ) -> ConfigBackup:
        """
        Hace backup de variables de entorno.
        
        Args:
            env_prefix: Prefijo de variables a respaldar (None = todas)
            sensitive_keys: Claves sensibles a encriptar
        """
        config_id = f"env-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Recopilar variables de entorno
        env_vars = {}
        for key, value in os.environ.items():
            if env_prefix and not key.startswith(env_prefix):
                continue
            
            # Encriptar valores sensibles
            if sensitive_keys and key in sensitive_keys:
                if self.encryption:
                    encrypted_value = self.encryption.encrypt_string(value)
                    env_vars[key] = {
                        'encrypted': True,
                        'value': encrypted_value
                    }
                else:
                    env_vars[key] = {
                        'encrypted': False,
                        'value': '***REDACTED***'
                    }
            else:
                env_vars[key] = {
                    'encrypted': False,
                    'value': value
                }
        
        # Guardar backup
        backup_file = self.backup_dir / f"{config_id}.json"
        with open(backup_file, 'w') as f:
            json.dump(env_vars, f, indent=2)
        
        return ConfigBackup(
            config_id=config_id,
            config_type='env',
            source='environment',
            content=env_vars,
            encrypted=self.encryption is not None,
            backed_up_at=datetime.now()
        )
    
    def backup_config_file(
        self,
        config_path: str,
        config_format: str = "auto"  # 'auto', 'json', 'yaml', 'ini'
    ) -> ConfigBackup:
        """
        Hace backup de archivo de configuración.
        
        Args:
            config_path: Ruta del archivo
            config_format: Formato del archivo
        """
        config_id = f"config-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        # Detectar formato automáticamente
        if config_format == "auto":
            if config_file.suffix == '.json':
                config_format = 'json'
            elif config_file.suffix in ['.yaml', '.yml']:
                config_format = 'yaml'
            elif config_file.suffix == '.ini':
                config_format = 'ini'
            else:
                config_format = 'text'
        
        # Leer contenido
        content = {}
        if config_format == 'json':
            with open(config_file, 'r') as f:
                content = json.load(f)
        elif config_format == 'yaml':
            with open(config_file, 'r') as f:
                content = yaml.safe_load(f)
        elif config_format == 'ini':
            import configparser
            parser = configparser.ConfigParser()
            parser.read(config_file)
            content = {section: dict(parser.items(section)) for section in parser.sections()}
        else:
            with open(config_file, 'r') as f:
                content = {'raw_content': f.read()}
        
        # Guardar backup
        backup_file = self.backup_dir / f"{config_id}.json"
        backup_data = {
            'source_file': str(config_file),
            'format': config_format,
            'content': content,
            'backed_up_at': datetime.now().isoformat()
        }
        
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        return ConfigBackup(
            config_id=config_id,
            config_type='file',
            source=str(config_file),
            content=backup_data,
            encrypted=False,
            backed_up_at=datetime.now()
        )
    
    def backup_application_config(
        self,
        app_name: str,
        config_data: Dict[str, Any],
        encrypt_sensitive: bool = True
    ) -> ConfigBackup:
        """
        Hace backup de configuración de aplicación.
        
        Args:
            app_name: Nombre de la aplicación
            config_data: Datos de configuración
            encrypt_sensitive: Si encriptar valores sensibles
        """
        config_id = f"app-{app_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Encriptar valores sensibles si se solicita
        if encrypt_sensitive and self.encryption:
            sensitive_keys = ['password', 'secret', 'key', 'token', 'api_key']
            for key, value in config_data.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    if isinstance(value, str):
                        config_data[key] = {
                            'encrypted': True,
                            'value': self.encryption.encrypt_string(value)
                        }
        
        # Guardar backup
        backup_file = self.backup_dir / f"{config_id}.json"
        backup_data = {
            'app_name': app_name,
            'config': config_data,
            'backed_up_at': datetime.now().isoformat()
        }
        
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        return ConfigBackup(
            config_id=config_id,
            config_type='app_config',
            source=app_name,
            content=backup_data,
            encrypted=encrypt_sensitive,
            backed_up_at=datetime.now()
        )
    
    def list_config_backups(
        self,
        config_type: Optional[str] = None,
        days: int = 30
    ) -> List[ConfigBackup]:
        """
        Lista backups de configuraciones.
        
        Args:
            config_type: Tipo de configuración (None = todos)
            days: Días hacia atrás
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        backups = []
        
        for backup_file in self.backup_dir.glob("*.json"):
            file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
            if file_time < cutoff_date:
                continue
            
            try:
                with open(backup_file, 'r') as f:
                    data = json.load(f)
                
                backup = ConfigBackup(
                    config_id=backup_file.stem,
                    config_type=data.get('format', 'unknown'),
                    source=data.get('source_file', data.get('app_name', 'unknown')),
                    content=data,
                    encrypted=data.get('encrypted', False),
                    backed_up_at=file_time
                )
                
                if config_type is None or backup.config_type == config_type:
                    backups.append(backup)
                    
            except Exception as e:
                logger.warning(f"Failed to load backup {backup_file}: {e}")
        
        return sorted(backups, key=lambda b: b.backed_up_at, reverse=True)

