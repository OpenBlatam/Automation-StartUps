"""
DAG de Backups de Logs y Auditoría.

Realiza backups automáticos de:
- Logs de aplicaciones
- Logs del sistema
- Logs de auditoría
"""
from __future__ import annotations

from datetime import timedelta
import logging
import os

import pendulum
from airflow.decorators import dag, task

from data.airflow.plugins.backup_logs import LogBackupManager
from data.airflow.plugins.backup_manager import BackupManager, BackupConfig
from data.airflow.plugins.backup_encryption import BackupEncryption
from data.airflow.plugins.etl_callbacks import on_task_failure
from data.airflow.plugins.etl_notifications import notify_slack

logger = logging.getLogger(__name__)


@dag(
    'log_backups',
    default_args={
        'owner': 'platform-team',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
        'on_failure_callback': on_task_failure,
    },
    description='Backups automáticos de logs y auditoría',
    schedule='0 4 * * *',  # Diario a las 4 AM
    start_date=pendulum.datetime(2025, 1, 1, tz='UTC'),
    catchup=False,
    tags=['backup', 'logs', 'audit'],
    max_active_runs=1,
    dagrun_timeout=timedelta(hours=1),
)
def log_backups():
    """Pipeline de backups de logs."""
    
    log_backup_dir = os.getenv("LOG_BACKUP_DIR", "/tmp/log-backups")
    backup_dir = os.getenv("BACKUP_DIR", "/tmp/backups")
    
    # Cargar clave de encriptación
    encryption_key = None
    encryption_key_env = os.getenv("BACKUP_ENCRYPTION_KEY")
    if encryption_key_env:
        encryption_key = BackupEncryption.load_key_from_base64(encryption_key_env)
    
    log_manager = LogBackupManager(backup_dir=log_backup_dir)
    
    @task(task_id='backup_application_logs')
    def backup_application_logs() -> dict:
        """Backup de logs de aplicaciones."""
        log_paths = os.getenv("APP_LOG_PATHS", "").split(",")
        log_paths = [p.strip() for p in log_paths if p.strip()]
        
        if not log_paths:
            logger.warning("No application log paths configured")
            return {'status': 'skipped', 'message': 'No log paths configured'}
        
        result = log_manager.backup_application_logs(
            log_paths=log_paths,
            retention_days=7
        )
        
        logger.info(f"Backed up application logs: {result.backup_id}")
        
        return {
            'backup_id': result.backup_id,
            'size_mb': result.size_bytes / (1024**2),
            'status': 'completed'
        }
    
    @task(task_id='backup_system_logs')
    def backup_system_logs() -> dict:
        """Backup de logs del sistema."""
        try:
            result = log_manager.backup_system_logs()
            logger.info(f"Backed up system logs: {result.backup_id}")
            
            return {
                'backup_id': result.backup_id,
                'size_mb': result.size_bytes / (1024**2),
                'status': 'completed'
            }
        except Exception as e:
            logger.error(f"System logs backup failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    @task(task_id='backup_audit_logs')
    def backup_audit_logs() -> dict:
        """Backup de logs de auditoría."""
        audit_log_path = os.getenv("AUDIT_LOG_PATH", "/var/log/audit")
        
        try:
            result = log_manager.backup_audit_logs(audit_log_path=audit_log_path)
            logger.info(f"Backed up audit logs: {result.backup_id}")
            
            return {
                'backup_id': result.backup_id,
                'size_mb': result.size_bytes / (1024**2),
                'status': 'completed'
            }
        except Exception as e:
            logger.error(f"Audit logs backup failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    @task(task_id='compress_and_encrypt_logs')
    def compress_and_encrypt_logs(
        app_logs: dict,
        system_logs: dict,
        audit_logs: dict
    ) -> dict:
        """Comprime y encripta backups de logs."""
        manager = BackupManager(
            backup_dir=backup_dir,
            encryption_key=encryption_key
        )
        
        result = manager.backup_files(
            source_paths=[log_backup_dir],
            config=BackupConfig(
                encrypt=True,
                compress=True,
                cloud_sync=True
            )
        )
        
        message = f"""
✅ *Log Backup Completed*

*Application Logs:*
• Status: {app_logs.get('status', 'unknown')}
• Size: {app_logs.get('size_mb', 0):.2f} MB

*System Logs:*
• Status: {system_logs.get('status', 'unknown')}
• Size: {system_logs.get('size_mb', 0):.2f} MB

*Audit Logs:*
• Status: {audit_logs.get('status', 'unknown')}
• Size: {audit_logs.get('size_mb', 0):.2f} MB

*Final Backup:*
• ID: {result.backup_id}
• Size: {result.size_bytes / (1024**2):.2f} MB
"""
        
        notify_slack(message)
        
        return {
            'backup_id': result.backup_id,
            'status': result.status.value
        }
    
    # Pipeline
    app_logs = backup_application_logs()
    system_logs = backup_system_logs()
    audit_logs = backup_audit_logs()
    
    final_backup = compress_and_encrypt_logs(app_logs, system_logs, audit_logs)


log_backups_dag = log_backups()

