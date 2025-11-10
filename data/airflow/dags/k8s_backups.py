"""
DAG de Backups de Recursos de Kubernetes.

Realiza backups automáticos de:
- ConfigMaps
- Secrets
- Deployments
- Services
"""
from __future__ import annotations

from datetime import timedelta
import logging
import os

import pendulum
from airflow.decorators import dag, task

from data.airflow.plugins.backup_kubernetes import KubernetesBackup
from data.airflow.plugins.backup_manager import BackupManager, BackupConfig
from data.airflow.plugins.backup_encryption import BackupEncryption
from data.airflow.plugins.etl_callbacks import on_task_failure
from data.airflow.plugins.etl_notifications import notify_slack

logger = logging.getLogger(__name__)


@dag(
    'k8s_backups',
    default_args={
        'owner': 'platform-team',
        'depends_on_past': False,
        'email_on_failure': True,
        'email_on_retry': False,
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
        'on_failure_callback': on_task_failure,
    },
    description='Backups automáticos de recursos de Kubernetes',
    schedule='0 3 * * *',  # Diario a las 3 AM
    start_date=pendulum.datetime(2025, 1, 1, tz='UTC'),
    catchup=False,
    tags=['backup', 'kubernetes', 'k8s'],
    max_active_runs=1,
    dagrun_timeout=timedelta(hours=2),
)
def k8s_backups():
    """Pipeline de backups de Kubernetes."""
    
    k8s_backup_dir = os.getenv("K8S_BACKUP_DIR", "/tmp/k8s-backups")
    backup_dir = os.getenv("BACKUP_DIR", "/tmp/backups")
    
    # Cargar clave de encriptación
    encryption_key = None
    encryption_key_env = os.getenv("BACKUP_ENCRYPTION_KEY")
    if encryption_key_env:
        encryption_key = BackupEncryption.load_key_from_base64(encryption_key_env)
    
    @task(task_id='backup_configmaps')
    def backup_configmaps() -> dict:
        """Backup de ConfigMaps."""
        try:
            k8s_backup = KubernetesBackup()
            results = k8s_backup.backup_configmaps(
                namespace=None,  # Todos los namespaces
                output_dir=k8s_backup_dir
            )
            
            logger.info(f"Backed up {len(results)} ConfigMaps")
            return {
                'count': len(results),
                'results': results[:10]  # Primeros 10
            }
        except Exception as e:
            logger.error(f"ConfigMap backup failed: {e}", exc_info=True)
            raise
    
    @task(task_id='backup_secrets')
    def backup_secrets() -> dict:
        """Backup de Secrets (encriptados)."""
        try:
            k8s_backup = KubernetesBackup()
            results = k8s_backup.backup_secrets(
                namespace=None,
                output_dir=k8s_backup_dir,
                decrypt=False  # Mantener encriptados
            )
            
            logger.info(f"Backed up {len(results)} Secrets")
            return {
                'count': len(results),
                'results': results[:10]
            }
        except Exception as e:
            logger.error(f"Secret backup failed: {e}", exc_info=True)
            raise
    
    @task(task_id='backup_deployments')
    def backup_deployments() -> dict:
        """Backup de Deployments."""
        try:
            k8s_backup = KubernetesBackup()
            results = k8s_backup.backup_deployments(
                namespace=None,
                output_dir=k8s_backup_dir
            )
            
            logger.info(f"Backed up {len(results)} Deployments")
            return {
                'count': len(results),
                'results': results[:10]
            }
        except Exception as e:
            logger.error(f"Deployment backup failed: {e}", exc_info=True)
            raise
    
    @task(task_id='compress_and_encrypt')
    def compress_and_encrypt(
        configmaps: dict,
        secrets: dict,
        deployments: dict
    ) -> dict:
        """Comprime y encripta backups de Kubernetes."""
        try:
            manager = BackupManager(
                backup_dir=backup_dir,
                encryption_key=encryption_key
            )
            
            # Crear backup de todo el directorio de k8s
            result = manager.backup_files(
                source_paths=[k8s_backup_dir],
                config=BackupConfig(
                    encrypt=True,
                    compress=True,
                    cloud_sync=True
                )
            )
            
            total_resources = (
                configmaps.get('count', 0) +
                secrets.get('count', 0) +
                deployments.get('count', 0)
            )
            
            message = f"""
✅ *Kubernetes Backup Completed*

*Recursos respaldados:*
• ConfigMaps: {configmaps.get('count', 0)}
• Secrets: {secrets.get('count', 0)}
• Deployments: {deployments.get('count', 0)}
• Total: {total_resources}

*Backup:*
• ID: {result.backup_id}
• Tamaño: {result.size_bytes / (1024**2):.2f} MB
• Estado: {result.status.value}
"""
            
            notify_slack(message)
            
            return {
                'backup_id': result.backup_id,
                'total_resources': total_resources,
                'status': result.status.value
            }
            
        except Exception as e:
            logger.error(f"Compress and encrypt failed: {e}", exc_info=True)
            raise
    
    # Pipeline
    configmaps = backup_configmaps()
    secrets = backup_secrets()
    deployments = backup_deployments()
    
    final_backup = compress_and_encrypt(configmaps, secrets, deployments)


k8s_backups_dag = k8s_backups()

