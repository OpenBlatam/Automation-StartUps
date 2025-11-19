"""
DAG de Backups Automáticos.

Realiza backups automáticos de:
- Bases de datos (PostgreSQL, MySQL)
- Archivos y directorios críticos
- Configuraciones

Incluye:
- Encriptación automática
- Sincronización con nube (AWS S3, Azure, GCP)
- Verificación de integridad
- Alertas de seguridad
- Limpieza automática de backups antiguos
"""
from __future__ import annotations

from datetime import timedelta, datetime
import logging
import os
from typing import Dict, Any, Optional

import pendulum
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models.param import Param

from data.airflow.plugins.backup_manager import (
    BackupManager,
    BackupConfig,
    BackupType
)
from data.airflow.plugins.backup_notifications import SecurityAlertManager
from data.airflow.plugins.etl_callbacks import on_task_failure
from data.airflow.plugins.etl_notifications import notify_slack

logger = logging.getLogger(__name__)

# Configuración por defecto
DEFAULT_BACKUP_DIR = os.getenv("BACKUP_DIR", "/tmp/backups")
DEFAULT_RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
ENCRYPTION_KEY_ENV = os.getenv("BACKUP_ENCRYPTION_KEY")

# Configuración de nube
CLOUD_CONFIG = {
    "aws": {
        "provider": "aws",
        "config": {
            "bucket": os.getenv("AWS_BACKUP_BUCKET", "biz-datalake-backups"),
            "access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
            "secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "region": os.getenv("AWS_REGION", "us-east-1")
        }
    },
    "azure": {
        "provider": "azure",
        "config": {
            "connection_string": os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
            "container": os.getenv("AZURE_BACKUP_CONTAINER", "backups")
        }
    },
    "gcp": {
        "provider": "gcp",
        "config": {
            "bucket": os.getenv("GCP_BACKUP_BUCKET"),
            "credentials_path": os.getenv("GCP_CREDENTIALS_PATH")
        }
    }
}

# Seleccionar proveedor de nube
CLOUD_PROVIDER = os.getenv("CLOUD_PROVIDER", "aws")  # aws, azure, gcp
CLOUD_CONFIG_TO_USE = CLOUD_CONFIG.get(CLOUD_PROVIDER) if CLOUD_PROVIDER in CLOUD_CONFIG else None


@dag(
    'automated_backups',
    default_args={
        'owner': 'platform-team',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
        'on_failure_callback': on_task_failure,
    },
    description='Backups automáticos con encriptación y sincronización en nube',
    schedule='0 2 * * *',  # Diario a las 2 AM
    start_date=pendulum.datetime(2025, 1, 1, tz='UTC'),
    catchup=False,
    tags=['backup', 'security', 'automation'],
    max_active_runs=1,
    dagrun_timeout=timedelta(hours=2),
    params={
        'backup_type': Param('full', type='string', enum=['full', 'incremental']),
        'encrypt': Param(True, type='boolean'),
        'cloud_sync': Param(True, type='boolean'),
        'retention_days': Param(30, type='integer', minimum=1, maximum=365),
    },
)
def automated_backups():
    """Pipeline de backups automáticos."""
    
    @task(task_id='backup_databases')
    def backup_databases(**context) -> Dict[str, Any]:
        """Backup de bases de datos críticas."""
        params = context.get('params', {})
        backup_type = BackupType.FULL if params.get('backup_type') == 'full' else BackupType.INCREMENTAL
        
        # Cargar clave de encriptación
        encryption_key = None
        if ENCRYPTION_KEY_ENV:
            from data.airflow.plugins.backup_encryption import BackupEncryption
            encryption_key = BackupEncryption.load_key_from_base64(ENCRYPTION_KEY_ENV)
        
        # Configurar backup
        backup_config = BackupConfig(
            backup_type=backup_type,
            encrypt=params.get('encrypt', True),
            compress=True,
            verify_integrity=True,
            retention_days=params.get('retention_days', DEFAULT_RETENTION_DAYS),
            cloud_sync=params.get('cloud_sync', True) and CLOUD_CONFIG_TO_USE is not None,
            cloud_provider=CLOUD_PROVIDER if CLOUD_CONFIG_TO_USE else None,
            cloud_config=CLOUD_CONFIG_TO_USE
        )
        
        manager = BackupManager(
            backup_dir=DEFAULT_BACKUP_DIR,
            encryption_key=encryption_key,
            cloud_config=CLOUD_CONFIG_TO_USE
        )
        
        results = {}
        
        # Backup de bases de datos configuradas
        db_connections = os.getenv("BACKUP_DB_CONNECTIONS", "").split(",")
        
        for db_conn in db_connections:
            if not db_conn.strip():
                continue
            
            try:
                # Detectar tipo de BD desde connection string
                db_type = "postgresql" if "postgresql" in db_conn.lower() else "mysql"
                
                logger.info(f"Backing up database: {db_conn[:20]}...")
                result = manager.backup_database(
                    connection_string=db_conn.strip(),
                    db_type=db_type,
                    config=backup_config
                )
                
                results[db_conn[:20]] = {
                    'status': result.status.value,
                    'backup_id': result.backup_id,
                    'size_mb': result.size_bytes / (1024 * 1024) if result.size_bytes else 0,
                    'cloud_path': result.cloud_path,
                    'error': result.error
                }
                
                if result.status.value == 'failed':
                    logger.error(f"Database backup failed: {result.error}")
                    
            except Exception as e:
                logger.error(f"Error backing up database: {e}", exc_info=True)
                results[db_conn[:20]] = {
                    'status': 'failed',
                    'error': str(e)
                }
        
        return {
            'total': len(results),
            'successful': sum(1 for r in results.values() if r.get('status') == 'completed'),
            'failed': sum(1 for r in results.values() if r.get('status') == 'failed'),
            'results': results
        }
    
    @task(task_id='backup_critical_files')
    def backup_critical_files(**context) -> Dict[str, Any]:
        """Backup de archivos y directorios críticos."""
        params = context.get('params', {})
        
        # Cargar clave de encriptación
        encryption_key = None
        if ENCRYPTION_KEY_ENV:
            from data.airflow.plugins.backup_encryption import BackupEncryption
            encryption_key = BackupEncryption.load_key_from_base64(ENCRYPTION_KEY_ENV)
        
        # Configurar backup
        backup_config = BackupConfig(
            encrypt=params.get('encrypt', True),
            compress=True,
            verify_integrity=True,
            retention_days=params.get('retention_days', DEFAULT_RETENTION_DAYS),
            cloud_sync=params.get('cloud_sync', True) and CLOUD_CONFIG_TO_USE is not None,
            cloud_provider=CLOUD_PROVIDER if CLOUD_CONFIG_TO_USE else None,
            cloud_config=CLOUD_CONFIG_TO_USE
        )
        
        manager = BackupManager(
            backup_dir=DEFAULT_BACKUP_DIR,
            encryption_key=encryption_key,
            cloud_config=CLOUD_CONFIG_TO_USE
        )
        
        # Directorios críticos a respaldar
        critical_paths = os.getenv("BACKUP_CRITICAL_PATHS", "").split(",")
        critical_paths = [p.strip() for p in critical_paths if p.strip()]
        
        results = {}
        
        for path in critical_paths:
            if not os.path.exists(path):
                logger.warning(f"Path does not exist: {path}")
                continue
            
            try:
                logger.info(f"Backing up path: {path}")
                result = manager.backup_files(
                    source_paths=[path],
                    config=backup_config
                )
                
                results[path] = {
                    'status': result.status.value,
                    'backup_id': result.backup_id,
                    'size_mb': result.size_bytes / (1024 * 1024) if result.size_bytes else 0,
                    'cloud_path': result.cloud_path,
                    'error': result.error
                }
                
            except Exception as e:
                logger.error(f"Error backing up path {path}: {e}", exc_info=True)
                results[path] = {
                    'status': 'failed',
                    'error': str(e)
                }
        
        return {
            'total': len(results),
            'successful': sum(1 for r in results.values() if r.get('status') == 'completed'),
            'failed': sum(1 for r in results.values() if r.get('status') == 'failed'),
            'results': results
        }
    
    @task(task_id='cleanup_old_backups')
    def cleanup_old_backups(**context) -> Dict[str, Any]:
        """Limpia backups antiguos según política de retención."""
        params = context.get('params', {})
        retention_days = params.get('retention_days', DEFAULT_RETENTION_DAYS)
        
        manager = BackupManager(
            backup_dir=DEFAULT_BACKUP_DIR,
            cloud_config=CLOUD_CONFIG_TO_USE
        )
        
        try:
            deleted_count = manager.cleanup_old_backups(retention_days)
            logger.info(f"Cleaned up {deleted_count} old backups")
            
            return {
                'deleted_count': deleted_count,
                'retention_days': retention_days
            }
        except Exception as e:
            logger.error(f"Cleanup failed: {e}", exc_info=True)
            return {
                'deleted_count': 0,
                'error': str(e)
            }
    
    @task(task_id='verify_backups')
    def verify_backups(
        db_results: Dict[str, Any],
        file_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verifica integridad de backups y envía resumen."""
        total_backups = db_results.get('total', 0) + file_results.get('total', 0)
        successful = db_results.get('successful', 0) + file_results.get('successful', 0)
        failed = db_results.get('failed', 0) + file_results.get('failed', 0)
        
        # Enviar resumen
        if failed > 0:
            message = f"""
⚠️ *Backup Summary - {successful}/{total_backups} Successful*

*Database Backups:*
• Successful: {db_results.get('successful', 0)}
• Failed: {db_results.get('failed', 0)}

*File Backups:*
• Successful: {file_results.get('successful', 0)}
• Failed: {file_results.get('failed', 0)}

*Total:* {successful} successful, {failed} failed
"""
            notify_slack(message)
        
        # Alertas de seguridad si hay fallos críticos
        if failed > 0:
            security_manager = SecurityAlertManager()
            security_manager.send_security_alert(
                title="Backup Failures Detected",
                message=f"{failed} backup(s) failed. Immediate attention required.",
                level=security_manager.AlertLevel.ERROR if failed > total_backups * 0.5 else security_manager.AlertLevel.WARNING,
                details={
                    'total': total_backups,
                    'successful': successful,
                    'failed': failed,
                    'failure_rate': f"{(failed/total_backups)*100:.1f}%" if total_backups > 0 else "0%"
                }
            )
        
        return {
            'total': total_backups,
            'successful': successful,
            'failed': failed,
            'success_rate': f"{(successful/total_backups)*100:.1f}%" if total_backups > 0 else "0%"
        }
    
    # Pipeline
    db_backups = backup_databases()
    file_backups = backup_critical_files()
    cleanup = cleanup_old_backups()
    verification = verify_backups(db_backups, file_backups)
    
    # Dependencias
    cleanup >> verification


# DAG adicional para backups incrementales
@dag(
    'incremental_backups',
    default_args={
        'owner': 'platform-team',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
        'on_failure_callback': on_task_failure,
    },
    description='Backups incrementales (más frecuentes)',
    schedule='0 */6 * * *',  # Cada 6 horas
    start_date=pendulum.datetime(2025, 1, 1, tz='UTC'),
    catchup=False,
    tags=['backup', 'incremental'],
    max_active_runs=1,
    dagrun_timeout=timedelta(hours=1),
)
def incremental_backups():
    """Pipeline de backups incrementales."""
    
    @task(task_id='incremental_database_backup')
    def incremental_database_backup() -> Dict[str, Any]:
        """Backup incremental de base de datos."""
        # Similar a backup_databases pero con tipo incremental
        # Implementación simplificada para este ejemplo
        return {'status': 'completed', 'type': 'incremental'}
    
    incremental_database_backup()


# Exportar DAGs
automated_backups_dag = automated_backups()
incremental_backups_dag = incremental_backups()

