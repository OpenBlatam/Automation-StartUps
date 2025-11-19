"""
Airflow DAG para verificación de salud del sistema de aprobaciones.
Verifica integridad de datos, consistencia y problemas.
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
    'approval_health_check',
    default_args={
        'owner': 'approvals-team',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=2),
    },
    description='Verificación de salud e integridad del sistema de aprobaciones',
    schedule='0 */6 * * *',  # Cada 6 horas
    start_date=pendulum.datetime(2025, 1, 1, tz='UTC'),
    catchup=False,
    tags=['approvals', 'health', 'validation'],
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=15),
)
def approval_health_check() -> None:
    """Pipeline de verificación de salud."""
    
    @task(task_id='check_data_integrity', on_failure_callback=on_task_failure)
    def check_data_integrity() -> Dict[str, Any]:
        """Verificar integridad de datos."""
        issues = []
        
        try:
            pg_hook = PostgresHook(postgres_conn_id=APPROVALS_DB_CONN)
            
            # Verificar referencias huérfanas
            orphan_chains_sql = """
                SELECT COUNT(*) 
                FROM approval_chains ac
                LEFT JOIN approval_requests ar ON ac.request_id = ar.id
                WHERE ar.id IS NULL;
            """
            
            orphan_chains = pg_hook.get_first(orphan_chains_sql)[0]
            if orphan_chains > 0:
                issues.append({
                    'type': 'orphan_chains',
                    'severity': 'high',
                    'count': orphan_chains,
                    'description': f'{orphan_chains} approval chains without request'
                })
            
            # Verificar cadenas sin aprobador
            chains_without_approver_sql = """
                SELECT COUNT(*) 
                FROM approval_chains
                WHERE approver_email IS NULL AND approver_role IS NULL;
            """
            
            chains_without_approver = pg_hook.get_first(chains_without_approver_sql)[0]
            if chains_without_approver > 0:
                issues.append({
                    'type': 'chains_without_approver',
                    'severity': 'medium',
                    'count': chains_without_approver,
                    'description': f'{chains_without_approver} chains without approver'
                })
            
            # Verificar solicitudes con estado inconsistente
            inconsistent_status_sql = """
                SELECT COUNT(*) 
                FROM approval_requests ar
                WHERE ar.status = 'pending'
                  AND NOT EXISTS (
                      SELECT 1 FROM approval_chains ac 
                      WHERE ac.request_id = ar.id AND ac.status = 'pending'
                  )
                  AND ar.submitted_at IS NOT NULL;
            """
            
            inconsistent_status = pg_hook.get_first(inconsistent_status_sql)[0]
            if inconsistent_status > 0:
                issues.append({
                    'type': 'inconsistent_status',
                    'severity': 'high',
                    'count': inconsistent_status,
                    'description': f'{inconsistent_status} pending requests without pending chains'
                })
            
            # Verificar duplicados
            duplicate_requests_sql = """
                SELECT 
                    requester_email,
                    request_type,
                    title,
                    submitted_at::date,
                    COUNT(*) as count
                FROM approval_requests
                WHERE submitted_at >= NOW() - INTERVAL '7 days'
                GROUP BY requester_email, request_type, title, submitted_at::date
                HAVING COUNT(*) > 1
                LIMIT 10;
            """
            
            duplicates = pg_hook.get_records(duplicate_requests_sql)
            if duplicates:
                issues.append({
                    'type': 'duplicate_requests',
                    'severity': 'low',
                    'count': len(duplicates),
                    'description': f'{len(duplicates)} potential duplicate requests found'
                })
            
            result = {
                'issues': issues,
                'total_issues': len(issues),
                'high_severity': len([i for i in issues if i['severity'] == 'high']),
                'medium_severity': len([i for i in issues if i['severity'] == 'medium']),
                'low_severity': len([i for i in issues if i['severity'] == 'low']),
                'status': 'healthy' if len(issues) == 0 else 'issues_found'
            }
            
            logger.info(f"Data integrity check: {result['status']}, {result['total_issues']} issues found")
            
            if Stats:
                try:
                    Stats.incr('approval_health_check.integrity_checks', 1)
                    Stats.incr(f"approval_health_check.issues.{result['status']}", 1)
                except Exception:
                    pass
            
            return result
            
        except Exception as e:
            logger.error("Failed to check data integrity", exc_info=True)
            raise
    
    @task(task_id='check_system_health', on_failure_callback=on_task_failure)
    def check_system_health() -> Dict[str, Any]:
        """Verificar salud general del sistema."""
        health_status = {
            'status': 'healthy',
            'checks': {},
            'warnings': []
        }
        
        try:
            pg_hook = PostgresHook(postgres_conn_id=APPROVALS_DB_CONN)
            
            # Verificar crecimiento de tablas
            table_size_sql = """
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                    pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
                FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename LIKE 'approval%'
                ORDER BY size_bytes DESC;
            """
            
            table_sizes = pg_hook.get_records(table_size_sql)
            health_status['checks']['table_sizes'] = [
                {'table': row[1], 'size': row[2], 'size_bytes': row[3]}
                for row in table_sizes
            ]
            
            # Verificar índices
            index_sql = """
                SELECT 
                    tablename,
                    indexname,
                    idx_scan as index_scans,
                    idx_tup_read as tuples_read,
                    idx_tup_fetch as tuples_fetched
                FROM pg_stat_user_indexes
                WHERE schemaname = 'public'
                  AND tablename LIKE 'approval%'
                ORDER BY idx_scan ASC
                LIMIT 10;
            """
            
            unused_indexes = pg_hook.get_records(index_sql)
            unused_count = len([i for i in unused_indexes if i[2] == 0])
            if unused_count > 0:
                health_status['warnings'].append(f'{unused_count} potentially unused indexes')
            
            # Verificar conexiones activas
            connections_sql = """
                SELECT COUNT(*) 
                FROM pg_stat_activity 
                WHERE datname = current_database();
            """
            
            active_connections = pg_hook.get_first(connections_sql)[0]
            health_status['checks']['active_connections'] = active_connections
            
            if active_connections > 100:
                health_status['warnings'].append(f'High number of active connections: {active_connections}')
            
            # Verificar locks
            locks_sql = """
                SELECT COUNT(*) 
                FROM pg_locks 
                WHERE NOT granted;
            """
            
            waiting_locks = pg_hook.get_first(locks_sql)[0]
            health_status['checks']['waiting_locks'] = waiting_locks
            
            if waiting_locks > 10:
                health_status['status'] = 'degraded'
                health_status['warnings'].append(f'High number of waiting locks: {waiting_locks}')
            
            # Verificar bloat
            bloat_sql = """
                SELECT 
                    schemaname,
                    tablename,
                    n_dead_tup,
                    n_live_tup,
                    CASE 
                        WHEN n_live_tup > 0 
                        THEN ROUND((n_dead_tup::numeric / n_live_tup::numeric) * 100, 2)
                        ELSE 0
                    END as dead_tuple_percent
                FROM pg_stat_user_tables
                WHERE schemaname = 'public'
                  AND tablename LIKE 'approval%'
                  AND n_dead_tup > 1000
                ORDER BY dead_tuple_percent DESC
                LIMIT 5;
            """
            
            bloat_results = pg_hook.get_records(bloat_sql)
            high_bloat = [b for b in bloat_results if b[4] > 20]
            if high_bloat:
                health_status['warnings'].append(f'{len(high_bloat)} tables with high bloat (>20% dead tuples)')
            
            logger.info(f"System health check: {health_status['status']}")
            
            if Stats:
                try:
                    Stats.incr(f"approval_health_check.system_health.{health_status['status']}", 1)
                except Exception:
                    pass
            
            return health_status
            
        except Exception as e:
            logger.error("Failed to check system health", exc_info=True)
            raise
    
    @task(task_id='send_health_report', on_failure_callback=on_task_failure)
    def send_health_report(
        integrity: Dict[str, Any],
        health: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enviar reporte de salud."""
        # Solo alertar si hay problemas
        if integrity['status'] != 'healthy' or health['status'] != 'healthy' or health['warnings']:
            message = f"""
🏥 *Approval System Health Check*

*Status:* {'⚠️ Issues Found' if integrity['status'] != 'healthy' or health['status'] != 'healthy' else '✅ Healthy'}

*Data Integrity:*
• Total Issues: {integrity['total_issues']}
• High Severity: {integrity['high_severity']}
• Medium Severity: {integrity['medium_severity']}
• Low Severity: {integrity['low_severity']}

*System Health:*
• Status: {health['status'].upper()}
• Active Connections: {health['checks'].get('active_connections', 'N/A')}
• Waiting Locks: {health['checks'].get('waiting_locks', 'N/A')}

*Warnings:*
{chr(10).join([f'• {w}' for w in health['warnings']]) if health['warnings'] else 'None'}
"""
            
            if integrity['issues']:
                message += "\n*Issues:*\n"
                for issue in integrity['issues'][:5]:
                    message += f"• {issue['type']}: {issue['description']}\n"
            
            try:
                notify_slack(message)
            except Exception as e:
                logger.warning(f"Failed to send health report: {e}")
        
        return {
            'integrity_status': integrity['status'],
            'system_status': health['status'],
            'report_sent': True
        }
    
    # Pipeline
    integrity = check_data_integrity()
    health = check_system_health()
    send_health_report(integrity, health)


approval_health_check_dag = approval_health_check()

