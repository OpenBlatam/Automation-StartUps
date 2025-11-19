"""
DAG de Verificación Automática de Backups.

Verifica integridad de backups automáticamente:
- Verificación de checksums
- Verificación de encriptación
- Verificación de compresión
- Tests de restauración (opcional)
"""
from __future__ import annotations

from datetime import timedelta
import logging
import os

import pendulum
from airflow.decorators import dag, task

from data.airflow.plugins.backup_verification import BackupVerifier
from data.airflow.plugins.backup_encryption import BackupEncryption
from data.airflow.plugins.etl_callbacks import on_task_failure
from data.airflow.plugins.etl_notifications import notify_slack

logger = logging.getLogger(__name__)


@dag(
    'backup_verification',
    default_args={
        'owner': 'platform-team',
        'depends_on_past': False,
        'email_on_failure': True,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
        'on_failure_callback': on_task_failure,
    },
    description='Verificación automática de integridad de backups',
    schedule='0 6 * * *',  # Diario a las 6 AM
    start_date=pendulum.datetime(2025, 1, 1, tz='UTC'),
    catchup=False,
    tags=['backup', 'verification', 'integrity'],
    max_active_runs=1,
    dagrun_timeout=timedelta(hours=1),
)
def backup_verification():
    """Pipeline de verificación de backups."""
    
    # Cargar clave de encriptación
    encryption_key = None
    encryption_key_env = os.getenv("BACKUP_ENCRYPTION_KEY")
    if encryption_key_env:
        encryption_key = BackupEncryption.load_key_from_base64(encryption_key_env)
    
    verifier = BackupVerifier(
        backup_dir=os.getenv("BACKUP_DIR", "/tmp/backups"),
        encryption_key=encryption_key
    )
    
    @task(task_id='verify_recent_backups')
    def verify_recent_backups() -> dict:
        """Verifica backups de últimos 7 días."""
        results = verifier.verify_all_recent_backups(
            days=7,
            verify_checksum=True,
            verify_encryption=True,
            verify_compression=True
        )
        
        report = verifier.generate_verification_report(results)
        
        # Alertar si hay fallos
        if report['failed'] > 0:
            message = f"""
⚠️ *Backup Verification Report*

*Resumen:*
• Total verificados: {report['total_backups']}
• ✅ Pasaron: {report['passed']}
• ❌ Fallaron: {report['failed']}
• ⚠️ Advertencias: {report['warnings']}
• Tasa de éxito: {report['pass_rate']:.1%}

*Backups con fallos:*
"""
            failed_backups = [r for r in report['results'] if r['status'] == 'failed']
            for backup in failed_backups[:5]:  # Primeros 5
                message += f"• {backup['backup_path']}\n"
                if backup['errors']:
                    message += f"  Errores: {', '.join(backup['errors'][:2])}\n"
            
            notify_slack(message)
        
        return report
    
    @task(task_id='verify_critical_backups')
    def verify_critical_backups() -> dict:
        """Verifica backups críticos (últimas 24 horas)."""
        results = verifier.verify_all_recent_backups(
            days=1,
            verify_checksum=True,
            verify_encryption=True,
            verify_compression=True
        )
        
        report = verifier.generate_verification_report(results)
        
        # Si hay fallos en backups críticos, alerta crítica
        if report['failed'] > 0:
            critical_message = f"""
🚨 *CRITICAL: Backup Verification Failures*

Backups críticos (últimas 24h) fallaron verificación:
• Fallos: {report['failed']} de {report['total_backups']}

*Acción requerida inmediata*
"""
            notify_slack(critical_message)
        
        return report
    
    # Pipeline
    recent_verification = verify_recent_backups()
    critical_verification = verify_critical_backups()


backup_verification_dag = backup_verification()

