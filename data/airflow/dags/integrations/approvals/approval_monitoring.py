"""
Airflow DAG para monitoreo y alertas del sistema de aprobaciones.
Identifica aprobaciones pendientes, timeouts próximos y problemas.
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
    'approval_monitoring',
    default_args={
        'owner': 'approvals-team',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=2),
    },
    description='Monitoreo y alertas del sistema de aprobaciones',
    schedule='*/30 * * * *',  # Cada 30 minutos
    start_date=pendulum.datetime(2025, 1, 1, tz='UTC'),
    catchup=False,
    tags=['approvals', 'monitoring', 'alerts'],
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=10),
)
def approval_monitoring() -> None:
    """Pipeline de monitoreo de aprobaciones."""
    
    @task(task_id='check_pending_timeouts', on_failure_callback=on_task_failure)
    def check_pending_timeouts() -> Dict[str, Any]:
        """Verificar aprobaciones pendientes próximas a timeout."""
        try:
            pg_hook = PostgresHook(postgres_conn_id=APPROVALS_DB_CONN)
            
            # Aprobaciones que expiran en las próximas 24 horas
            sql = """
                SELECT 
                    ac.id,
                    ac.request_id,
                    ar.title,
                    ar.request_type,
                    ac.approver_email,
                    ac.timeout_date,
                    EXTRACT(EPOCH FROM (ac.timeout_date - NOW())) / 3600 as hours_until_timeout,
                    ar.requester_email,
                    ar.priority
                FROM approval_chains ac
                JOIN approval_requests ar ON ac.request_id = ar.id
                WHERE ac.status = 'pending'
                  AND ac.timeout_date IS NOT NULL
                  AND ac.timeout_date > NOW()
                  AND ac.timeout_date <= NOW() + INTERVAL '24 hours'
                ORDER BY ac.timeout_date ASC
                LIMIT 50;
            """
            
            results = pg_hook.get_records(sql)
            
            timeouts_soon = []
            for row in results:
                timeouts_soon.append({
                    'chain_id': str(row[0]),
                    'request_id': str(row[1]),
                    'title': row[2],
                    'request_type': row[3],
                    'approver_email': row[4],
                    'timeout_date': row[5].isoformat() if row[5] else None,
                    'hours_until_timeout': round(row[6], 2) if row[6] else None,
                    'requester_email': row[7],
                    'priority': row[8]
                })
            
            logger.info(f"Found {len(timeouts_soon)} approvals expiring soon")
            
            if Stats:
                try:
                    Stats.incr('approval_monitoring.timeouts_soon', len(timeouts_soon))
                except Exception:
                    pass
            
            return {
                'timeouts_soon': timeouts_soon,
                'count': len(timeouts_soon)
            }
            
        except Exception as e:
            logger.error("Failed to check pending timeouts", exc_info=True)
            raise
    
    @task(task_id='check_expired_timeouts', on_failure_callback=on_task_failure)
    def check_expired_timeouts() -> Dict[str, Any]:
        """Verificar aprobaciones que ya expiraron."""
        try:
            pg_hook = PostgresHook(postgres_conn_id=APPROVALS_DB_CONN)
            
            # Aprobaciones expiradas (últimas 24 horas)
            sql = """
                SELECT 
                    ac.id,
                    ac.request_id,
                    ar.title,
                    ar.request_type,
                    ac.approver_email,
                    ac.timeout_date,
                    EXTRACT(EPOCH FROM (NOW() - ac.timeout_date)) / 3600 as hours_expired,
                    ar.requester_email,
                    ar.priority
                FROM approval_chains ac
                JOIN approval_requests ar ON ac.request_id = ar.id
                WHERE ac.status = 'pending'
                  AND ac.timeout_date IS NOT NULL
                  AND ac.timeout_date < NOW()
                  AND ac.timeout_date > NOW() - INTERVAL '24 hours'
                ORDER BY ac.timeout_date ASC
                LIMIT 50;
            """
            
            results = pg_hook.get_records(sql)
            
            expired = []
            for row in results:
                expired.append({
                    'chain_id': str(row[0]),
                    'request_id': str(row[1]),
                    'title': row[2],
                    'request_type': row[3],
                    'approver_email': row[4],
                    'timeout_date': row[5].isoformat() if row[5] else None,
                    'hours_expired': round(row[6], 2) if row[6] else None,
                    'requester_email': row[7],
                    'priority': row[8]
                })
            
            logger.warning(f"Found {len(expired)} expired approvals")
            
            if Stats:
                try:
                    Stats.incr('approval_monitoring.timeouts_expired', len(expired))
                except Exception:
                    pass
            
            return {
                'expired': expired,
                'count': len(expired)
            }
            
        except Exception as e:
            logger.error("Failed to check expired timeouts", exc_info=True)
            raise
    
    @task(task_id='check_stale_requests', on_failure_callback=on_task_failure)
    def check_stale_requests() -> Dict[str, Any]:
        """Verificar solicitudes pendientes antiguas."""
        try:
            pg_hook = PostgresHook(postgres_conn_id=APPROVALS_DB_CONN)
            
            # Solicitudes pendientes > 30 días
            sql = """
                SELECT 
                    ar.id,
                    ar.title,
                    ar.request_type,
                    ar.requester_email,
                    ar.submitted_at,
                    EXTRACT(EPOCH FROM (NOW() - ar.submitted_at)) / 86400 as days_pending,
                    ar.priority,
                    COUNT(ac.id) FILTER (WHERE ac.status = 'pending') as pending_approvals
                FROM approval_requests ar
                LEFT JOIN approval_chains ac ON ar.id = ac.request_id
                WHERE ar.status = 'pending'
                  AND ar.submitted_at IS NOT NULL
                  AND ar.submitted_at < NOW() - INTERVAL '30 days'
                GROUP BY ar.id, ar.title, ar.request_type, ar.requester_email, ar.submitted_at, ar.priority
                ORDER BY ar.submitted_at ASC
                LIMIT 50;
            """
            
            results = pg_hook.get_records(sql)
            
            stale = []
            for row in results:
                stale.append({
                    'request_id': str(row[0]),
                    'title': row[1],
                    'request_type': row[2],
                    'requester_email': row[3],
                    'submitted_at': row[4].isoformat() if row[4] else None,
                    'days_pending': round(row[5], 1) if row[5] else None,
                    'priority': row[6],
                    'pending_approvals': row[7]
                })
            
            logger.warning(f"Found {len(stale)} stale requests (>30 days)")
            
            if Stats:
                try:
                    Stats.incr('approval_monitoring.stale_requests', len(stale))
                except Exception:
                    pass
            
            return {
                'stale_requests': stale,
                'count': len(stale)
            }
            
        except Exception as e:
            logger.error("Failed to check stale requests", exc_info=True)
            raise
    
    @task(task_id='check_high_priority_pending', on_failure_callback=on_task_failure)
    def check_high_priority_pending() -> Dict[str, Any]:
        """Verificar aprobaciones de alta prioridad pendientes."""
        try:
            pg_hook = PostgresHook(postgres_conn_id=APPROVALS_DB_CONN)
            
            # Aprobaciones urgentes o de alta prioridad pendientes
            sql = """
                SELECT 
                    ac.id,
                    ac.request_id,
                    ar.title,
                    ar.request_type,
                    ar.priority,
                    ac.approver_email,
                    ar.submitted_at,
                    EXTRACT(EPOCH FROM (NOW() - ar.submitted_at)) / 3600 as hours_pending,
                    ar.requester_email
                FROM approval_chains ac
                JOIN approval_requests ar ON ac.request_id = ar.id
                WHERE ac.status = 'pending'
                  AND ar.priority IN ('high', 'urgent')
                  AND ar.submitted_at > NOW() - INTERVAL '7 days'
                ORDER BY ar.priority DESC, ar.submitted_at ASC
                LIMIT 50;
            """
            
            results = pg_hook.get_records(sql)
            
            high_priority = []
            for row in results:
                high_priority.append({
                    'chain_id': str(row[0]),
                    'request_id': str(row[1]),
                    'title': row[2],
                    'request_type': row[3],
                    'priority': row[4],
                    'approver_email': row[5],
                    'submitted_at': row[6].isoformat() if row[6] else None,
                    'hours_pending': round(row[7], 2) if row[7] else None,
                    'requester_email': row[8]
                })
            
            logger.info(f"Found {len(high_priority)} high priority pending approvals")
            
            if Stats:
                try:
                    Stats.incr('approval_monitoring.high_priority_pending', len(high_priority))
                except Exception:
                    pass
            
            return {
                'high_priority': high_priority,
                'count': len(high_priority)
            }
            
        except Exception as e:
            logger.error("Failed to check high priority pending", exc_info=True)
            raise
    
    @task(task_id='send_alerts', on_failure_callback=on_task_failure)
    def send_alerts(
        timeouts_soon: Dict[str, Any],
        expired: Dict[str, Any],
        stale: Dict[str, Any],
        high_priority: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enviar alertas según condiciones."""
        alerts_sent = []
        
        try:
            # Alertar sobre aprobaciones expiradas
            if expired['count'] > 0:
                expired_list = "\n".join([
                    f"• {item['title']} ({item['request_type']}) - {item['approver_email']} - Expired {item['hours_expired']:.1f}h ago"
                    for item in expired['expired'][:10]
                ])
                
                message = f"""
⚠️ *Approval Timeouts Expired*

{expired['count']} approval(s) have expired:
{expired_list}
"""
                notify_slack(message)
                alerts_sent.append('expired_timeouts')
            
            # Alertar sobre aprobaciones próximas a expirar (solo si < 2 horas)
            urgent_timeouts = [t for t in timeouts_soon['timeouts_soon'] if t.get('hours_until_timeout', 999) < 2]
            if urgent_timeouts:
                urgent_list = "\n".join([
                    f"• {item['title']} ({item['request_type']}) - {item['approver_email']} - Expires in {item['hours_until_timeout']:.1f}h"
                    for item in urgent_timeouts[:10]
                ])
                
                message = f"""
⏰ *Urgent Approvals Expiring Soon*

{len(urgent_timeouts)} approval(s) expiring in < 2 hours:
{urgent_list}
"""
                notify_slack(message)
                alerts_sent.append('urgent_timeouts')
            
            # Alertar sobre solicitudes stale (solo si > 60 días)
            very_stale = [s for s in stale['stale_requests'] if s.get('days_pending', 0) > 60]
            if very_stale:
                stale_list = "\n".join([
                    f"• {item['title']} ({item['request_type']}) - {item['requester_email']} - {item['days_pending']:.0f} days pending"
                    for item in very_stale[:10]
                ])
                
                message = f"""
🔴 *Very Stale Requests*

{len(very_stale)} request(s) pending > 60 days:
{stale_list}
"""
                notify_slack(message)
                alerts_sent.append('very_stale')
            
            # Alertar sobre alta prioridad pendiente (solo si > 24 horas)
            urgent_high_priority = [h for h in high_priority['high_priority'] if h.get('hours_pending', 0) > 24 and h.get('priority') == 'urgent']
            if urgent_high_priority:
                urgent_list = "\n".join([
                    f"• {item['title']} ({item['request_type']}) - {item['approver_email']} - {item['hours_pending']:.1f}h pending"
                    for item in urgent_high_priority[:10]
                ])
                
                message = f"""
🚨 *Urgent High Priority Pending*

{len(urgent_high_priority)} urgent approval(s) pending > 24 hours:
{urgent_list}
"""
                notify_slack(message)
                alerts_sent.append('urgent_high_priority')
            
            logger.info(f"Sent {len(alerts_sent)} alerts")
            
            if Stats:
                try:
                    Stats.incr('approval_monitoring.alerts_sent', len(alerts_sent))
                except Exception:
                    pass
            
            return {
                'alerts_sent': alerts_sent,
                'count': len(alerts_sent)
            }
            
        except Exception as e:
            logger.error("Failed to send alerts", exc_info=True)
            # No fallar el DAG si las notificaciones fallan
            return {'alerts_sent': [], 'count': 0, 'error': str(e)}
    
    # Pipeline
    timeouts_soon = check_pending_timeouts()
    expired = check_expired_timeouts()
    stale = check_stale_requests()
    high_priority = check_high_priority_pending()
    
    send_alerts(timeouts_soon, expired, stale, high_priority)


approval_monitoring_dag = approval_monitoring()

