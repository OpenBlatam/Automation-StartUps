from __future__ import annotations

from datetime import timedelta
import logging
import json
from typing import Dict, Any

import pendulum
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

from data.airflow.plugins.etl_callbacks import on_task_failure
from data.airflow.plugins.etl_notifications import notify_slack

logger = logging.getLogger(__name__)


@dag(
    dag_id="customer_onboarding_reports",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="0 9 * * 1",  # Cada lunes a las 9 AM
    catchup=False,
    default_args={
        "owner": "sales-operations",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    doc_md="""
    ### Customer Onboarding Reports
    
    Genera reportes semanales de métricas de onboarding de clientes.
    Incluye:
    - Tasa de completación
    - Métodos de verificación más usados
    - Servicios más activados
    - Tiempo promedio de onboarding
    - Análisis de fuentes
    """,
    tags=["onboarding", "reports", "customer"],
)
def customer_onboarding_reports() -> None:
    @task(task_id="generate_weekly_report")
    def generate_weekly_report() -> Dict[str, Any]:
        """Generar reporte semanal."""
        try:
            pg_hook = PostgresHook(postgres_conn_id="postgres_default")
            
            # Métricas de la semana
            week_start = pendulum.now().subtract(days=7).start_of("week")
            week_end = pendulum.now().start_of("week")
            
            # Total de onboardings iniciados
            total_sql = """
                SELECT COUNT(*) as total
                FROM customer_onboarding
                WHERE created_at >= %s AND created_at < %s
            """
            total = pg_hook.get_first(total_sql, parameters=(week_start, week_end))[0]
            
            # Onboardings completados
            completed_sql = """
                SELECT COUNT(*) as completed
                FROM customer_onboarding
                WHERE status = 'completed'
                  AND onboarding_completed_at >= %s
                  AND onboarding_completed_at < %s
            """
            completed = pg_hook.get_first(completed_sql, parameters=(week_start, week_end))[0]
            
            # Tasa de completación
            completion_rate = (completed / total * 100) if total > 0 else 0
            
            # Métodos de verificación
            verification_sql = """
                SELECT 
                    identity_verification_method,
                    COUNT(*) as total,
                    COUNT(CASE WHEN identity_verified = TRUE THEN 1 END) as verified
                FROM customer_onboarding
                WHERE created_at >= %s AND created_at < %s
                GROUP BY identity_verification_method
            """
            verification_methods = pg_hook.get_records(verification_sql, parameters=(week_start, week_end))
            
            # Servicios activados
            services_sql = """
                SELECT 
                    service_name,
                    COUNT(*) as total,
                    COUNT(CASE WHEN account_status = 'active' THEN 1 END) as active
                FROM customer_accounts
                WHERE activation_requested_at >= %s
                  AND activation_requested_at < %s
                GROUP BY service_name
                ORDER BY total DESC
            """
            services = pg_hook.get_records(services_sql, parameters=(week_start, week_end))
            
            # Tiempo promedio de completación
            avg_time_sql = """
                SELECT 
                    AVG(EXTRACT(EPOCH FROM (onboarding_completed_at - onboarding_started_at)) / 3600) as avg_hours
                FROM customer_onboarding
                WHERE status = 'completed'
                  AND onboarding_completed_at >= %s
                  AND onboarding_completed_at < %s
                  AND onboarding_completed_at IS NOT NULL
            """
            avg_time = pg_hook.get_first(avg_time_sql, parameters=(week_start, week_end))
            avg_hours = avg_time[0] if avg_time and avg_time[0] else 0
            
            # Fuentes de clientes
            sources_sql = """
                SELECT 
                    source,
                    COUNT(*) as count
                FROM customer_onboarding
                WHERE created_at >= %s AND created_at < %s
                GROUP BY source
                ORDER BY count DESC
            """
            sources = pg_hook.get_records(sources_sql, parameters=(week_start, week_end))
            
            # Reporte
            report = {
                "period": {
                    "start": week_start.isoformat(),
                    "end": week_end.isoformat(),
                    "generated_at": pendulum.now().isoformat()
                },
                "metrics": {
                    "total_onboardings": total,
                    "completed": completed,
                    "completion_rate": round(completion_rate, 2),
                    "avg_completion_hours": round(avg_hours, 2)
                },
                "verification_methods": [
                    {
                        "method": row[0],
                        "total": row[1],
                        "verified": row[2],
                        "verification_rate": round((row[2] / row[1] * 100) if row[1] > 0 else 0, 2)
                    }
                    for row in verification_methods
                ],
                "services": [
                    {
                        "service": row[0],
                        "total_requests": row[1],
                        "active": row[2],
                        "activation_rate": round((row[2] / row[1] * 100) if row[1] > 0 else 0, 2)
                    }
                    for row in services
                ],
                "sources": [
                    {"source": row[0], "count": row[1]}
                    for row in sources
                ]
            }
            
            # Guardar reporte
            report_json = json.dumps(report, indent=2)
            logger.info("Weekly report generated", extra={"report": report})
            
            # Enviar a Slack si está configurado
            try:
                slack_message = f"""
📊 *Customer Onboarding Report - Week of {week_start.format('MMM DD')}*

*Summary:*
• Total Onboardings: {total}
• Completed: {completed}
• Completion Rate: {completion_rate:.1f}%
• Avg Completion Time: {avg_hours:.1f} hours

*Top Services:*
{chr(10).join([f"• {s['service']}: {s['activation_rate']:.1f}% ({s['active']}/{s['total_requests']})" for s in report['services'][:5]])}

*Sources:*
{chr(10).join([f"• {s['source']}: {s['count']}" for s in report['sources']])}
"""
                notify_slack(slack_message)
            except Exception as e:
                logger.warning(f"Failed to send Slack notification: {e}")
            
            return report
            
        except Exception as e:
            logger.error("Failed to generate report", exc_info=True)
            raise
    
    generate_weekly_report()


customer_onboarding_reports_dag = customer_onboarding_reports()





