"""
DAG de Monitoreo de Seguridad.

Monitorea y alerta sobre:
- Intentos de acceso no autorizados
- Cambios en configuración de seguridad
- Violaciones de políticas
- Anomalías en el sistema
"""
from __future__ import annotations

from datetime import timedelta
import logging
import os
from typing import Dict, Any, List

import pendulum
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

from data.airflow.plugins.backup_notifications import SecurityAlertManager, AlertLevel
from data.airflow.plugins.backup_health import BackupHealthChecker
from data.airflow.plugins.etl_callbacks import on_task_failure

logger = logging.getLogger(__name__)


@dag(
    'security_monitoring',
    default_args={
        'owner': 'security-team',
        'depends_on_past': False,
        'email_on_failure': True,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
        'on_failure_callback': on_task_failure,
    },
    description='Monitoreo continuo de seguridad y alertas',
    schedule='*/15 * * * *',  # Cada 15 minutos
    start_date=pendulum.datetime(2025, 1, 1, tz='UTC'),
    catchup=False,
    tags=['security', 'monitoring', 'alerts'],
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=10),
)
def security_monitoring():
    """Pipeline de monitoreo de seguridad."""
    
    security_manager = SecurityAlertManager()
    
    @task(task_id='check_failed_logins')
    def check_failed_logins() -> Dict[str, Any]:
        """Verifica intentos de login fallidos."""
        # Verificar logs de autenticación
        # Esto es un ejemplo - adaptar según tu sistema de autenticación
        failed_attempts = []
        
        # Aquí puedes consultar tu base de datos de logs o sistema de autenticación
        # Por ejemplo:
        # db_hook = PostgresHook(postgres_conn_id='auth_db')
        # failed_attempts = db_hook.get_records("""
        #     SELECT user, ip, COUNT(*) as attempts, MAX(timestamp) as last_attempt
        #     FROM auth_logs
        #     WHERE status = 'failed'
        #       AND timestamp > NOW() - INTERVAL '15 minutes'
        #     GROUP BY user, ip
        #     HAVING COUNT(*) > 5
        # """)
        
        if len(failed_attempts) > 0:
            for attempt in failed_attempts:
                security_manager.alert_unauthorized_access(
                    resource="authentication",
                    user=attempt.get('user'),
                    ip=attempt.get('ip')
                )
        
        return {
            'failed_attempts': len(failed_attempts),
            'details': failed_attempts
        }
    
    @task(task_id='check_backup_status')
    def check_backup_status() -> Dict[str, Any]:
        """Verifica que los backups estén funcionando correctamente."""
        from data.airflow.plugins.backup_manager import BackupManager
        
        manager = BackupManager(backup_dir=os.getenv("BACKUP_DIR", "/tmp/backups"))
        
        # Verificar último backup
        # Esto es un ejemplo simplificado
        backup_dir = manager.backup_dir
        recent_backups = sorted(
            [f for f in backup_dir.glob("*.sql*") if f.is_file()],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if not recent_backups:
            security_manager.send_security_alert(
                title="No Recent Backups",
                message="No backups found in the last 24 hours",
                level=AlertLevel.WARNING,
                details={'backup_dir': str(backup_dir)}
            )
            return {'status': 'warning', 'message': 'No recent backups'}
        
        # Verificar que el último backup no sea muy antiguo
        from datetime import datetime, timedelta
        last_backup_time = datetime.fromtimestamp(recent_backups[0].stat().st_mtime)
        hours_since_backup = (datetime.now() - last_backup_time).total_seconds() / 3600
        
        if hours_since_backup > 48:
            security_manager.send_security_alert(
                title="Stale Backups",
                message=f"Last backup is {hours_since_backup:.1f} hours old",
                level=AlertLevel.WARNING,
                details={
                    'hours_since_backup': hours_since_backup,
                    'last_backup': recent_backups[0].name
                }
            )
        
        return {
            'status': 'ok',
            'last_backup': recent_backups[0].name if recent_backups else None,
            'hours_since_backup': hours_since_backup if recent_backups else None
        }
    
    @task(task_id='check_encryption_status')
    def check_encryption_status() -> Dict[str, Any]:
        """Verifica que la encriptación esté configurada correctamente."""
        encryption_key = os.getenv("BACKUP_ENCRYPTION_KEY")
        
        if not encryption_key:
            security_manager.send_security_alert(
                title="Encryption Key Missing",
                message="BACKUP_ENCRYPTION_KEY environment variable is not set",
                level=AlertLevel.ERROR,
                details={'issue': 'encryption_disabled'}
            )
            return {'status': 'error', 'encryption_enabled': False}
        
        return {'status': 'ok', 'encryption_enabled': True}
    
    @task(task_id='check_cloud_sync')
    def check_cloud_sync() -> Dict[str, Any]:
        """Verifica que la sincronización con la nube esté funcionando."""
        from data.airflow.plugins.backup_manager import CloudSync
        
        cloud_provider = os.getenv("CLOUD_PROVIDER", "aws")
        cloud_config = None
        
        if cloud_provider == "aws":
            cloud_config = {
                "provider": "aws",
                "config": {
                    "bucket": os.getenv("AWS_BACKUP_BUCKET"),
                    "access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
                    "secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
                    "region": os.getenv("AWS_REGION", "us-east-1")
                }
            }
        
        if not cloud_config or not cloud_config.get("config", {}).get("bucket"):
            security_manager.send_security_alert(
                title="Cloud Sync Not Configured",
                message="Cloud backup synchronization is not configured",
                level=AlertLevel.WARNING,
                details={'provider': cloud_provider}
            )
            return {'status': 'warning', 'cloud_sync_enabled': False}
        
        # Verificar conectividad
        try:
            cloud_sync = CloudSync(cloud_provider, cloud_config["config"])
            backups = cloud_sync.list_backups("backups/")
            
            if not backups:
                security_manager.send_security_alert(
                    title="No Cloud Backups Found",
                    message="No backups found in cloud storage",
                    level=AlertLevel.WARNING,
                    details={'provider': cloud_provider}
                )
            
            return {
                'status': 'ok',
                'cloud_sync_enabled': True,
                'backup_count': len(backups)
            }
        except Exception as e:
            security_manager.alert_cloud_sync_failure(cloud_provider, str(e))
            return {
                'status': 'error',
                'cloud_sync_enabled': True,
                'error': str(e)
            }
    
    @task(task_id='backup_health_check')
    def backup_health_check() -> Dict[str, Any]:
        """Ejecuta health check completo del sistema de backups."""
        checker = BackupHealthChecker(backup_dir=os.getenv("BACKUP_DIR", "/tmp/backups"))
        health = checker.check_all()
        
        # Alertar sobre problemas críticos
        if health['overall_status'] == 'critical':
            critical_issues = checker.get_critical_issues()
            for issue in critical_issues:
                security_manager.send_security_alert(
                    title=f"Critical Backup Issue: {issue.name}",
                    message=issue.message,
                    level=AlertLevel.CRITICAL,
                    details=issue.details
                )
        
        # Alertar sobre warnings
        warnings = checker.get_warnings()
        if warnings:
            for warning in warnings:
                security_manager.send_security_alert(
                    title=f"Backup Warning: {warning.name}",
                    message=warning.message,
                    level=AlertLevel.WARNING,
                    details=warning.details
                )
        
        return health
    
    @task(task_id='generate_security_report')
    def generate_security_report(
        login_status: Dict[str, Any],
        backup_status: Dict[str, Any],
        encryption_status: Dict[str, Any],
        cloud_sync_status: Dict[str, Any],
        health_status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera reporte de seguridad completo."""
        issues = []
        
        if login_status.get('failed_attempts', 0) > 0:
            issues.append(f"Failed login attempts: {login_status['failed_attempts']}")
        
        if backup_status.get('status') != 'ok':
            issues.append(f"Backup issue: {backup_status.get('message', 'Unknown')}")
        
        if encryption_status.get('encryption_enabled') is False:
            issues.append("Encryption not enabled")
        
        if cloud_sync_status.get('status') != 'ok':
            issues.append(f"Cloud sync issue: {cloud_sync_status.get('error', 'Unknown')}")
        
        if health_status.get('overall_status') in ['warning', 'critical']:
            issues.append(f"Backup health check: {health_status.get('overall_status')}")
        
        report = {
            'timestamp': pendulum.now().isoformat(),
            'issues': issues,
            'status': 'ok' if not issues else ('critical' if health_status.get('overall_status') == 'critical' else 'warning'),
            'checks': {
                'logins': login_status,
                'backups': backup_status,
                'encryption': encryption_status,
                'cloud_sync': cloud_sync_status,
                'health': health_status
            }
        }
        
        if issues:
            logger.warning(f"Security issues detected: {issues}")
        
        return report
    
    # Pipeline
    login_check = check_failed_logins()
    backup_check = check_backup_status()
    encryption_check = check_encryption_status()
    cloud_check = check_cloud_sync()
    health_check = backup_health_check()
    
    report = generate_security_report(
        login_check,
        backup_check,
        encryption_check,
        cloud_check,
        health_check
    )


security_monitoring_dag = security_monitoring()

