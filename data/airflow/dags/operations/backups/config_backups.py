"""
DAG de Backups de Configuraciones.

Realiza backups automáticos de:
- Variables de entorno
- Archivos de configuración
- Configuraciones de aplicaciones
"""
from __future__ import annotations

from datetime import timedelta
import logging
import os

import pendulum
from airflow.decorators import dag, task

from data.airflow.plugins.backup_config_backup import ConfigurationBackup
from data.airflow.plugins.backup_encryption import BackupEncryption
from data.airflow.plugins.backup_manager import BackupManager, BackupConfig
from data.airflow.plugins.etl_callbacks import on_task_failure
from data.airflow.plugins.etl_notifications import notify_slack

logger = logging.getLogger(__name__)


@dag(
    'config_backups',
    default_args={
        'owner': 'platform-team',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
        'on_failure_callback': on_task_failure,
    },
    description='Backups automáticos de configuraciones',
    schedule='0 1 * * *',  # Diario a la 1 AM
    start_date=pendulum.datetime(2025, 1, 1, tz='UTC'),
    catchup=False,
    tags=['backup', 'config', 'security'],
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=30),
)
def config_backups():
    """Pipeline de backups de configuraciones."""
    
    # Cargar clave de encriptación
    encryption_key = None
    encryption_key_env = os.getenv("BACKUP_ENCRYPTION_KEY")
    if encryption_key_env:
        encryption_key = BackupEncryption.load_key_from_base64(encryption_key_env)
    
    config_backup = ConfigurationBackup(
        backup_dir=os.getenv("CONFIG_BACKUP_DIR", "/tmp/config-backups"),
        encryption_key=encryption_key
    )
    
    @task(task_id='backup_environment_variables')
    def backup_environment_variables() -> dict:
        """Backup de variables de entorno críticas."""
        sensitive_keys = [
            'PASSWORD', 'SECRET', 'KEY', 'TOKEN', 'API_KEY',
            'DATABASE', 'DB_', 'REDIS_', 'MONGO_'
        ]
        
        result = config_backup.backup_environment_variables(
            env_prefix=os.getenv("CONFIG_ENV_PREFIX"),
            sensitive_keys=sensitive_keys
        )
        
        logger.info(f"Backed up environment variables: {result.config_id}")
        
        return {
            'config_id': result.config_id,
            'type': result.config_type,
            'encrypted': result.encrypted,
            'variables_count': len(result.content)
        }
    
    @task(task_id='backup_config_files')
    def backup_config_files() -> dict:
        """Backup de archivos de configuración críticos."""
        config_files = os.getenv("CONFIG_FILES_TO_BACKUP", "").split(",")
        config_files = [f.strip() for f in config_files if f.strip()]
        
        results = []
        for config_file in config_files:
            if not os.path.exists(config_file):
                logger.warning(f"Config file not found: {config_file}")
                continue
            
            try:
                result = config_backup.backup_config_file(config_file)
                results.append({
                    'config_id': result.config_id,
                    'source': result.source,
                    'type': result.config_type
                })
            except Exception as e:
                logger.error(f"Failed to backup {config_file}: {e}")
        
        return {
            'backed_up': len(results),
            'results': results
        }
    
    @task(task_id='compress_and_encrypt_configs')
    def compress_and_encrypt_configs(
        env_backup: dict,
        files_backup: dict
    ) -> dict:
        """Comprime y encripta backups de configuraciones."""
        manager = BackupManager(
            backup_dir=os.getenv("BACKUP_DIR", "/tmp/backups"),
            encryption_key=encryption_key
        )
        
        config_backup_dir = os.getenv("CONFIG_BACKUP_DIR", "/tmp/config-backups")
        
        result = manager.backup_files(
            source_paths=[config_backup_dir],
            config=BackupConfig(
                encrypt=True,
                compress=True,
                cloud_sync=True
            )
        )
        
        message = f"""
✅ *Configuration Backup Completed*

*Environment Variables:*
• Config ID: {env_backup['config_id']}
• Encrypted: {env_backup['encrypted']}
• Variables: {env_backup['variables_count']}

*Config Files:*
• Backed up: {files_backup['backed_up']}

*Final Backup:*
• ID: {result.backup_id}
• Size: {result.size_bytes / (1024**2):.2f} MB
• Status: {result.status.value}
"""
        
        notify_slack(message)
        
        return {
            'backup_id': result.backup_id,
            'status': result.status.value,
            'size_mb': result.size_bytes / (1024**2)
        }
    
    # Pipeline
    env_vars = backup_environment_variables()
    config_files = backup_config_files()
    final_backup = compress_and_encrypt_configs(env_vars, config_files)


config_backups_dag = config_backups()

