"""
DAG de Verificación de Compliance de Backups.

Verifica que los backups cumplan con políticas de compliance:
- Encriptación requerida
- Política de retención
- Frecuencia de backups
- Backups offsite
- Controles de acceso
- Verificación regular
"""
from __future__ import annotations

from datetime import timedelta
import logging
import os

import pendulum
from airflow.decorators import dag, task

from data.airflow.plugins.backup_compliance import BackupComplianceValidator
from data.airflow.plugins.backup_notifications import SecurityAlertManager, AlertLevel
from data.airflow.plugins.etl_callbacks import on_task_failure
from data.airflow.plugins.etl_notifications import notify_slack

logger = logging.getLogger(__name__)


@dag(
    'backup_compliance_check',
    default_args={
        'owner': 'compliance-team',
        'depends_on_past': False,
        'email_on_failure': True,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
        'on_failure_callback': on_task_failure,
    },
    description='Verificación de compliance de backups',
    schedule='0 9 * * *',  # Diario a las 9 AM
    start_date=pendulum.datetime(2025, 1, 1, tz='UTC'),
    catchup=False,
    tags=['backup', 'compliance', 'security'],
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=15),
)
def backup_compliance_check():
    """Pipeline de verificación de compliance."""
    
    validator = BackupComplianceValidator(
        backup_dir=os.getenv("BACKUP_DIR", "/tmp/backups")
    )
    security_manager = SecurityAlertManager()
    
    @task(task_id='run_compliance_checks')
    def run_compliance_checks() -> dict:
        """Ejecuta todas las verificaciones de compliance."""
        results = validator.validate_all()
        
        # Alertar sobre problemas críticos
        if results['overall_status'] == 'non_compliant':
            critical_issues = [
                c for c in results['checks']
                if c['status'] == 'non_compliant'
                and any(
                    r.severity == 'critical'
                    for r in validator.rules
                    if r.rule_id == c['rule_id']
                )
            ]
            
            for issue in critical_issues:
                security_manager.send_security_alert(
                    title=f"Compliance Violation: {issue['rule_name']}",
                    message=issue['message'],
                    level=AlertLevel.CRITICAL,
                    details=issue.get('details', {})
                )
        
        # Enviar resumen
        summary = results['summary']
        message = f"""
📋 *Backup Compliance Report*

*Estado General:* {results['overall_status'].upper()}

*Resumen:*
• Total checks: {summary['total_checks']}
• ✅ Compliant: {summary['compliant']}
• ❌ Non-compliant: {summary['non_compliant']}
• ⚠️ Warnings: {summary['warnings']}
"""
        
        if summary['non_compliant'] > 0:
            non_compliant_checks = [
                c for c in results['checks']
                if c['status'] == 'non_compliant'
            ]
            message += "\n*Issues:*\n"
            for check in non_compliant_checks[:5]:
                message += f"• {check['rule_name']}: {check['message']}\n"
        
        notify_slack(message)
        
        return results
    
    # Pipeline
    compliance_results = run_compliance_checks()


backup_compliance_check_dag = backup_compliance_check()

