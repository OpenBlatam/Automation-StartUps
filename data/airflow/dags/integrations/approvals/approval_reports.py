"""
Airflow DAG para generar reportes de métricas del sistema de aprobaciones.
Genera reportes diarios, semanales y mensuales.
"""
from __future__ import annotations

from datetime import timedelta
import logging
import os
import json
from typing import Dict, Any

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
    'approval_reports_daily',
    default_args={
        'owner': 'approvals-team',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='Reporte diario de métricas de aprobaciones',
    schedule='0 8 * * *',  # Cada día a las 8 AM
    start_date=pendulum.datetime(2025, 1, 1, tz='UTC'),
    catchup=False,
    tags=['approvals', 'reports', 'daily'],
    max_active_runs=1,
)
def approval_reports_daily() -> None:
    """Pipeline de reporte diario."""
    
    @task(task_id='generate_daily_report', on_failure_callback=on_task_failure)
    def generate_daily_report() -> Dict[str, Any]:
        """Generar reporte diario de métricas."""
        try:
            pg_hook = PostgresHook(postgres_conn_id=APPROVALS_DB_CONN)
            
            yesterday = pendulum.yesterday()
            today = pendulum.today()
            
            # Métricas del día anterior
            sql = """
                SELECT 
                    COUNT(*) FILTER (WHERE status = 'pending') as pending,
                    COUNT(*) FILTER (WHERE status = 'approved') as approved,
                    COUNT(*) FILTER (WHERE status = 'rejected') as rejected,
                    COUNT(*) FILTER (WHERE status = 'auto_approved') as auto_approved,
                    COUNT(*) FILTER (WHERE submitted_at::date = %s) as submitted,
                    COUNT(*) FILTER (WHERE completed_at::date = %s) as completed,
                    AVG(EXTRACT(EPOCH FROM (completed_at - submitted_at)) / 3600) 
                        FILTER (WHERE completed_at::date = %s) as avg_completion_hours
                FROM approval_requests
                WHERE created_at >= %s - INTERVAL '1 day';
            """
            
            result = pg_hook.get_first(sql, parameters=(
                yesterday.date(),
                yesterday.date(),
                yesterday.date(),
                yesterday
            ))
            
            # Por tipo de solicitud
            type_sql = """
                SELECT 
                    request_type,
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE status = 'approved') as approved,
                    COUNT(*) FILTER (WHERE status = 'pending') as pending
                FROM approval_requests
                WHERE created_at >= %s - INTERVAL '1 day'
                GROUP BY request_type;
            """
            
            type_results = pg_hook.get_records(type_sql, parameters=(yesterday,))
            
            # Top aprobadores
            approver_sql = """
                SELECT 
                    ac.approver_email,
                    COUNT(*) FILTER (WHERE ac.status = 'approved') as approved_count,
                    COUNT(*) FILTER (WHERE ac.status = 'pending') as pending_count
                FROM approval_chains ac
                JOIN approval_requests ar ON ac.request_id = ar.id
                WHERE ar.created_at >= %s - INTERVAL '1 day'
                GROUP BY ac.approver_email
                ORDER BY approved_count DESC
                LIMIT 10;
            """
            
            approver_results = pg_hook.get_records(approver_sql, parameters=(yesterday,))
            
            report = {
                'date': yesterday.isoformat(),
                'generated_at': pendulum.now().isoformat(),
                'metrics': {
                    'pending': result[0] if result else 0,
                    'approved': result[1] if result else 0,
                    'rejected': result[2] if result else 0,
                    'auto_approved': result[3] if result else 0,
                    'submitted': result[4] if result else 0,
                    'completed': result[5] if result else 0,
                    'avg_completion_hours': round(result[6], 2) if result and result[6] else 0
                },
                'by_type': [
                    {
                        'request_type': row[0],
                        'total': row[1],
                        'approved': row[2],
                        'pending': row[3]
                    }
                    for row in type_results
                ],
                'top_approvers': [
                    {
                        'approver_email': row[0],
                        'approved_count': row[1],
                        'pending_count': row[2]
                    }
                    for row in approver_results
                ]
            }
            
            # Enviar resumen a Slack
            message = f"""
📊 *Daily Approval Report - {yesterday.format('YYYY-MM-DD')}*

*Summary:*
• Submitted: {report['metrics']['submitted']}
• Completed: {report['metrics']['completed']}
• Approved: {report['metrics']['approved']}
• Rejected: {report['metrics']['rejected']}
• Auto-approved: {report['metrics']['auto_approved']}
• Pending: {report['metrics']['pending']}
• Avg Completion: {report['metrics']['avg_completion_hours']:.1f} hours

*By Type:*
{chr(10).join([f"• {t['request_type']}: {t['approved']} approved, {t['pending']} pending" for t in report['by_type']])}
"""
            
            try:
                notify_slack(message)
            except Exception as e:
                logger.warning(f"Failed to send Slack notification: {e}")
            
            logger.info(f"Daily report generated: {json.dumps(report, indent=2)}")
            
            if Stats:
                try:
                    Stats.incr('approval_reports.daily_generated', 1)
                except Exception:
                    pass
            
            return report
            
        except Exception as e:
            logger.error("Failed to generate daily report", exc_info=True)
            raise


approval_reports_daily_dag = approval_reports_daily()


@dag(
    'approval_reports_weekly',
    default_args={
        'owner': 'approvals-team',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='Reporte semanal de métricas de aprobaciones',
    schedule='0 9 * * 1',  # Cada lunes a las 9 AM
    start_date=pendulum.datetime(2025, 1, 1, tz='UTC'),
    catchup=False,
    tags=['approvals', 'reports', 'weekly'],
    max_active_runs=1,
)
def approval_reports_weekly() -> None:
    """Pipeline de reporte semanal."""
    
    @task(task_id='generate_weekly_report', on_failure_callback=on_task_failure)
    def generate_weekly_report() -> Dict[str, Any]:
        """Generar reporte semanal de métricas."""
        try:
            pg_hook = PostgresHook(postgres_conn_id=APPROVALS_DB_CONN)
            
            week_start = pendulum.now().subtract(days=7).start_of('week')
            week_end = pendulum.now().start_of('week')
            
            # Métricas de la semana
            sql = """
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE status = 'approved') as approved,
                    COUNT(*) FILTER (WHERE status = 'rejected') as rejected,
                    COUNT(*) FILTER (WHERE status = 'auto_approved') as auto_approved,
                    COUNT(*) FILTER (WHERE status = 'pending') as pending,
                    AVG(EXTRACT(EPOCH FROM (completed_at - submitted_at)) / 3600) 
                        FILTER (WHERE completed_at IS NOT NULL) as avg_completion_hours,
                    COUNT(DISTINCT requester_email) as unique_requesters,
                    COUNT(DISTINCT ac.approver_email) FILTER (WHERE ac.status = 'approved') as unique_approvers
                FROM approval_requests ar
                LEFT JOIN approval_chains ac ON ar.id = ac.request_id
                WHERE ar.created_at >= %s AND ar.created_at < %s;
            """
            
            result = pg_hook.get_first(sql, parameters=(week_start, week_end))
            
            # Tasa de aprobación por día
            daily_sql = """
                SELECT 
                    DATE(ar.created_at) as date,
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE ar.status = 'approved') as approved,
                    COUNT(*) FILTER (WHERE ar.status = 'rejected') as rejected
                FROM approval_requests ar
                WHERE ar.created_at >= %s AND ar.created_at < %s
                GROUP BY DATE(ar.created_at)
                ORDER BY date;
            """
            
            daily_results = pg_hook.get_records(daily_sql, parameters=(week_start, week_end))
            
            # Tiempo promedio de aprobación por tipo
            type_sql = """
                SELECT 
                    ar.request_type,
                    COUNT(*) as total,
                    AVG(EXTRACT(EPOCH FROM (ar.completed_at - ar.submitted_at)) / 3600) as avg_hours
                FROM approval_requests ar
                WHERE ar.created_at >= %s AND ar.created_at < %s
                  AND ar.completed_at IS NOT NULL
                GROUP BY ar.request_type;
            """
            
            type_results = pg_hook.get_records(type_sql, parameters=(week_start, week_end))
            
            report = {
                'period': {
                    'start': week_start.isoformat(),
                    'end': week_end.isoformat()
                },
                'generated_at': pendulum.now().isoformat(),
                'metrics': {
                    'total': result[0] if result else 0,
                    'approved': result[1] if result else 0,
                    'rejected': result[2] if result else 0,
                    'auto_approved': result[3] if result else 0,
                    'pending': result[4] if result else 0,
                    'approval_rate': round((result[1] / result[0] * 100) if result and result[0] > 0 else 0, 2),
                    'avg_completion_hours': round(result[5], 2) if result and result[5] else 0,
                    'unique_requesters': result[6] if result else 0,
                    'unique_approvers': result[7] if result else 0
                },
                'daily_breakdown': [
                    {
                        'date': row[0].isoformat() if hasattr(row[0], 'isoformat') else str(row[0]),
                        'total': row[1],
                        'approved': row[2],
                        'rejected': row[3]
                    }
                    for row in daily_results
                ],
                'by_type': [
                    {
                        'request_type': row[0],
                        'total': row[1],
                        'avg_completion_hours': round(row[2], 2) if row[2] else 0
                    }
                    for row in type_results
                ]
            }
            
            # Enviar resumen a Slack
            message = f"""
📊 *Weekly Approval Report - Week of {week_start.format('MMM DD')}*

*Summary:*
• Total Requests: {report['metrics']['total']}
• Approved: {report['metrics']['approved']} ({report['metrics']['approval_rate']:.1f}%)
• Rejected: {report['metrics']['rejected']}
• Auto-approved: {report['metrics']['auto_approved']}
• Pending: {report['metrics']['pending']}
• Avg Completion: {report['metrics']['avg_completion_hours']:.1f} hours
• Unique Requesters: {report['metrics']['unique_requesters']}
• Unique Approvers: {report['metrics']['unique_approvers']}

*By Type:*
{chr(10).join([f"• {t['request_type']}: {t['avg_completion_hours']:.1f}h avg" for t in report['by_type']])}
"""
            
            try:
                notify_slack(message)
            except Exception as e:
                logger.warning(f"Failed to send Slack notification: {e}")
            
            logger.info(f"Weekly report generated: {json.dumps(report, indent=2)}")
            
            if Stats:
                try:
                    Stats.incr('approval_reports.weekly_generated', 1)
                except Exception:
                    pass
            
            return report
            
        except Exception as e:
            logger.error("Failed to generate weekly report", exc_info=True)
            raise
    
    generate_weekly_report()


approval_reports_weekly_dag = approval_reports_weekly()

