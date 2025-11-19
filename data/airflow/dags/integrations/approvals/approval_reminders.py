"""
Airflow DAG para enviar recordatorios de aprobaciones pendientes.
"""
from __future__ import annotations

from datetime import timedelta
import logging
import os
from typing import Dict, Any, List

import pendulum
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

from data.airflow.plugins.etl_callbacks import on_task_failure
from data.airflow.plugins.etl_notifications import notify_slack

try:
    from airflow.stats import Stats
except Exception:
    Stats = None

logger = logging.getLogger(__name__)

APPROVALS_DB_CONN = os.getenv("APPROVALS_DB_CONN_ID", "approvals_db")


@dag(
    'approval_reminders',
    default_args={
        'owner': 'approvals-team',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=2),
    },
    description='Envío de recordatorios de aprobaciones pendientes',
    schedule='0 9,14,17 * * 1-5',  # 9 AM, 2 PM, 5 PM de lunes a viernes
    start_date=pendulum.datetime(2025, 1, 1, tz='UTC'),
    catchup=False,
    tags=['approvals', 'reminders', 'notifications'],
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=15),
)
def approval_reminders() -> None:
    """Pipeline de recordatorios."""
    
    @task(task_id='send_reminders', on_failure_callback=on_task_failure)
    def send_reminders() -> Dict[str, Any]:
        """Enviar recordatorios de aprobaciones pendientes."""
        try:
            pg_hook = PostgresHook(postgres_conn_id=APPROVALS_DB_CONN)
            
            # Aprobaciones pendientes que no han sido notificadas en las últimas 24 horas
            sql = """
                SELECT 
                    ac.id,
                    ac.request_id,
                    ar.title,
                    ar.request_type,
                    ar.description,
                    ar.priority,
                    ac.approver_email,
                    au.user_name as approver_name,
                    ar.requester_email,
                    au2.user_name as requester_name,
                    ac.timeout_date,
                    EXTRACT(EPOCH FROM (ac.timeout_date - NOW())) / 3600 as hours_until_timeout,
                    ac.notified_at,
                    EXTRACT(EPOCH FROM (NOW() - COALESCE(ac.notified_at, ar.submitted_at)) / 3600) as hours_since_last_notification
                FROM approval_chains ac
                JOIN approval_requests ar ON ac.request_id = ar.id
                LEFT JOIN approval_users au ON ac.approver_email = au.user_email
                LEFT JOIN approval_users au2 ON ar.requester_email = au2.user_email
                WHERE ac.status = 'pending'
                  AND (ac.notified_at IS NULL OR ac.notified_at < NOW() - INTERVAL '24 hours')
                  AND ar.submitted_at IS NOT NULL
                ORDER BY ar.priority DESC, ac.timeout_date ASC NULLS LAST
                LIMIT 100;
            """
            
            results = pg_hook.get_records(sql)
            
            reminders_sent = 0
            reminders_failed = 0
            reminders_by_approver = {}
            
            for row in results:
                try:
                    chain_id = str(row[0])
                    request_id = str(row[1])
                    title = row[2]
                    request_type = row[3]
                    description = row[4] or ""
                    priority = row[5] or "normal"
                    approver_email = row[6]
                    approver_name = row[7] or approver_email
                    requester_email = row[8]
                    requester_name = row[9] or requester_email
                    timeout_date = row[10]
                    hours_until_timeout = row[11]
                    notified_at = row[12]
                    hours_since_notification = row[13] or 0
                    
                    # Preparar mensaje
                    priority_emoji = {
                        'urgent': '🚨',
                        'high': '⚠️',
                        'normal': '📋',
                        'low': '📌'
                    }.get(priority, '📋')
                    
                    timeout_message = ""
                    if timeout_date:
                        if hours_until_timeout and hours_until_timeout < 0:
                            timeout_message = f" ⏰ *EXPIRED {abs(hours_until_timeout):.1f}h ago*"
                        elif hours_until_timeout and hours_until_timeout < 24:
                            timeout_message = f" ⏰ Expires in {hours_until_timeout:.1f}h"
                    
                    message = f"""
{priority_emoji} *Approval Reminder*

*Request:* {title}
*Type:* {request_type}
*Requester:* {requester_name} ({requester_email})
*Priority:* {priority.upper()}{timeout_message}

{description[:200] if description else 'No description'}

[View Request](https://approvals.example.com/requests/{request_id})
"""
                    
                    # Enviar notificación (simulado - en producción usaría email/Slack API)
                    # Por ahora solo logueamos
                    logger.info(f"Sending reminder to {approver_email} for request {request_id}")
                    
                    # Actualizar notified_at
                    update_sql = """
                        UPDATE approval_chains
                        SET notified_at = NOW(),
                            updated_at = NOW()
                        WHERE id = %s
                    """
                    pg_hook.run(update_sql, parameters=(chain_id,))
                    
                    reminders_sent += 1
                    
                    # Agrupar por aprobador para estadísticas
                    if approver_email not in reminders_by_approver:
                        reminders_by_approver[approver_email] = 0
                    reminders_by_approver[approver_email] += 1
                    
                    # En producción, aquí se enviaría el email/Slack:
                    # send_notification(approver_email, message)
                    
                except Exception as e:
                    logger.error(f"Failed to send reminder for chain {chain_id}", exc_info=True)
                    reminders_failed += 1
            
            logger.info(f"Sent {reminders_sent} reminders, {reminders_failed} failed")
            
            # Enviar resumen a Slack
            if reminders_sent > 0:
                summary = f"""
📧 *Approval Reminders Sent*

• Total reminders sent: {reminders_sent}
• Failed: {reminders_failed}

*Top approvers:*
{chr(10).join([f"• {email}: {count} reminders" for email, count in list(reminders_by_approver.items())[:5]])}
"""
                try:
                    notify_slack(summary)
                except Exception as e:
                    logger.warning(f"Failed to send Slack summary: {e}")
            
            if Stats:
                try:
                    Stats.incr('approval_reminders.sent', reminders_sent)
                    Stats.incr('approval_reminders.failed', reminders_failed)
                except Exception:
                    pass
            
            return {
                'reminders_sent': reminders_sent,
                'reminders_failed': reminders_failed,
                'by_approver': reminders_by_approver
            }
            
        except Exception as e:
            logger.error("Failed to send reminders", exc_info=True)
            raise
    
    send_reminders()


approval_reminders_dag = approval_reminders()

