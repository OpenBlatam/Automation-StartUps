"""
DAG de Reportes Semanales y Mensuales de Soporte

Genera reportes automatizados de:
- Métricas de rendimiento
- Tasa de resolución por chatbot
- Satisfacción del cliente
- Tiempo de respuesta
- Distribución por categoría/prioridad
"""
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    from airflow import DAG
    from airflow.decorators import task, dag
    from airflow.utils.dates import days_ago
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    "owner": "support",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

REPORT_RECIPIENTS = os.getenv("SUPPORT_REPORT_RECIPIENTS", "").split(",")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
EMAIL_API_URL = os.getenv("EMAIL_API_URL", "")


@dag(
    dag_id="support_tickets_reports",
    start_date=days_ago(1),
    schedule="0 9 * * MON",  # Lunes a las 9 AM
    catchup=False,
    default_args=DEFAULT_ARGS,
    description="Reportes semanales y mensuales de soporte",
    tags=["support", "reports", "weekly"],
)
def support_tickets_reports():
    """DAG para generar reportes de soporte."""
    
    @task(task_id="generate_weekly_report")
    def generate_weekly_report() -> Dict[str, Any]:
        """Genera reporte semanal de métricas."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Período: última semana
                start_date = datetime.now() - timedelta(days=7)
                
                # Tickets totales
                cur.execute("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE chatbot_resolved = true) as chatbot_resolved,
                        COUNT(*) FILTER (WHERE status = 'resolved') as manually_resolved,
                        COUNT(*) FILTER (WHERE status IN ('open', 'assigned', 'in_progress')) as pending,
                        AVG(priority_score) as avg_priority_score
                    FROM support_tickets
                    WHERE created_at >= %s
                """, (start_date,))
                row = cur.fetchone()
                ticket_stats = {
                    "total": row[0] or 0,
                    "chatbot_resolved": row[1] or 0,
                    "manually_resolved": row[2] or 0,
                    "pending": row[3] or 0,
                    "avg_priority_score": float(row[4]) if row[4] else 0.0
                }
                
                # Tasa de resolución por chatbot
                chatbot_rate = (ticket_stats["chatbot_resolved"] / ticket_stats["total"] * 100) if ticket_stats["total"] > 0 else 0.0
                
                # Distribución por prioridad
                cur.execute("""
                    SELECT 
                        priority,
                        COUNT(*) as count,
                        AVG(time_to_resolution_minutes) as avg_resolution_time
                    FROM support_tickets
                    WHERE created_at >= %s
                    GROUP BY priority
                    ORDER BY 
                        CASE priority
                            WHEN 'critical' THEN 1
                            WHEN 'urgent' THEN 2
                            WHEN 'high' THEN 3
                            WHEN 'medium' THEN 4
                            WHEN 'low' THEN 5
                        END
                """, (start_date,))
                priority_distribution = {
                    row[0]: {
                        "count": row[1],
                        "avg_resolution_minutes": float(row[2]) if row[2] else None
                    }
                    for row in cur.fetchall()
                }
                
                # Distribución por categoría
                cur.execute("""
                    SELECT 
                        category,
                        COUNT(*) as count
                    FROM support_tickets
                    WHERE created_at >= %s
                    AND category IS NOT NULL
                    GROUP BY category
                    ORDER BY count DESC
                """, (start_date,))
                category_distribution = {
                    row[0]: row[1] for row in cur.fetchall()
                }
                
                # Tiempo promedio de primera respuesta
                cur.execute("""
                    SELECT 
                        AVG(time_to_first_response_minutes) as avg_first_response,
                        AVG(time_to_resolution_minutes) as avg_resolution,
                        COUNT(*) FILTER (WHERE first_response_at IS NOT NULL) as responded_count
                    FROM support_tickets
                    WHERE created_at >= %s
                    AND chatbot_resolved = false
                """, (start_date,))
                row = cur.fetchone()
                response_times = {
                    "avg_first_response_minutes": float(row[0]) if row[0] else None,
                    "avg_resolution_minutes": float(row[1]) if row[1] else None,
                    "responded_count": row[2] or 0
                }
                
                # Top agentes
                cur.execute("""
                    SELECT 
                        assigned_agent_name,
                        COUNT(*) as tickets_resolved,
                        AVG(time_to_resolution_minutes) as avg_resolution_time
                    FROM support_tickets
                    WHERE created_at >= %s
                    AND assigned_agent_name IS NOT NULL
                    AND status = 'resolved'
                    GROUP BY assigned_agent_name
                    ORDER BY tickets_resolved DESC
                    LIMIT 5
                """, (start_date,))
                top_agents = [
                    {
                        "name": row[0],
                        "resolved": row[1],
                        "avg_time_minutes": float(row[2]) if row[2] else None
                    }
                    for row in cur.fetchall()
                ]
                
                # SLA compliance
                cur.execute("""
                    SELECT 
                        COUNT(*) FILTER (WHERE priority IN ('critical', 'urgent') 
                            AND time_to_first_response_minutes <= 60) as critical_sla_met,
                        COUNT(*) FILTER (WHERE priority IN ('critical', 'urgent')) as critical_total,
                        COUNT(*) FILTER (WHERE time_to_first_response_minutes <= 240) as all_sla_met,
                        COUNT(*) FILTER (WHERE first_response_at IS NOT NULL) as all_total
                    FROM support_tickets
                    WHERE created_at >= %s
                    AND chatbot_resolved = false
                """, (start_date,))
                row = cur.fetchone()
                sla_metrics = {
                    "critical_sla_rate": (row[0] / row[1] * 100) if row[1] and row[1] > 0 else 0.0,
                    "all_sla_rate": (row[2] / row[3] * 100) if row[3] and row[3] > 0 else 0.0
                }
        
        report = {
            "period": {
                "start": start_date.isoformat(),
                "end": datetime.now().isoformat(),
                "type": "weekly"
            },
            "ticket_stats": ticket_stats,
            "chatbot_rate": chatbot_rate,
            "priority_distribution": priority_distribution,
            "category_distribution": category_distribution,
            "response_times": response_times,
            "top_agents": top_agents,
            "sla_metrics": sla_metrics,
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info(f"Generated weekly report: {report}")
        return report
    
    @task(task_id="format_report")
    def format_report(report_data: Dict[str, Any]) -> Dict[str, str]:
        """Formatea el reporte en texto y HTML."""
        period = report_data["period"]
        stats = report_data["ticket_stats"]
        
        # Texto plano
        text_report = f"""
REPORTE SEMANAL DE SOPORTE
==========================

Período: {period['start'][:10]} a {period['end'][:10]}

RESUMEN DE TICKETS
------------------
Total de tickets: {stats['total']}
Resueltos por chatbot: {stats['chatbot_resolved']} ({report_data['chatbot_rate']:.1f}%)
Resueltos manualmente: {stats['manually_resolved']}
Pendientes: {stats['pending']}

TIEMPOS DE RESPUESTA
--------------------
Tiempo promedio primera respuesta: {report_data['response_times']['avg_first_response_minutes']:.1f} minutos
Tiempo promedio de resolución: {report_data['response_times']['avg_resolution_minutes']:.1f} minutos

SLA COMPLIANCE
--------------
Tickets críticos cumpliendo SLA: {report_data['sla_metrics']['critical_sla_rate']:.1f}%
Todos los tickets cumpliendo SLA: {report_data['sla_metrics']['all_sla_rate']:.1f}%

DISTRIBUCIÓN POR PRIORIDAD
---------------------------
"""
        for priority, data in report_data["priority_distribution"].items():
            text_report += f"{priority.upper()}: {data['count']} tickets\n"
        
        text_report += "\nTOP AGENTES\n-----------\n"
        for i, agent in enumerate(report_data["top_agents"], 1):
            text_report += f"{i}. {agent['name']}: {agent['resolved']} tickets resueltos\n"
        
        # HTML
        html_report = f"""
        <html>
        <body>
            <h1>Reporte Semanal de Soporte</h1>
            <p><strong>Período:</strong> {period['start'][:10]} a {period['end'][:10]}</p>
            
            <h2>Resumen</h2>
            <ul>
                <li>Total de tickets: <strong>{stats['total']}</strong></li>
                <li>Resueltos por chatbot: <strong>{stats['chatbot_resolved']}</strong> ({report_data['chatbot_rate']:.1f}%)</li>
                <li>Resueltos manualmente: <strong>{stats['manually_resolved']}</strong></li>
                <li>Pendientes: <strong>{stats['pending']}</strong></li>
            </ul>
            
            <h2>Tiempos de Respuesta</h2>
            <ul>
                <li>Primera respuesta promedio: <strong>{report_data['response_times']['avg_first_response_minutes']:.1f}</strong> minutos</li>
                <li>Resolución promedio: <strong>{report_data['response_times']['avg_resolution_minutes']:.1f}</strong> minutos</li>
            </ul>
            
            <h2>SLA Compliance</h2>
            <ul>
                <li>Tickets críticos: <strong>{report_data['sla_metrics']['critical_sla_rate']:.1f}%</strong></li>
                <li>Todos los tickets: <strong>{report_data['sla_metrics']['all_sla_rate']:.1f}%</strong></li>
            </ul>
            
            <h2>Top Agentes</h2>
            <ol>
        """
        for agent in report_data["top_agents"]:
            html_report += f"<li>{agent['name']}: {agent['resolved']} tickets resueltos</li>"
        
        html_report += """
            </ol>
        </body>
        </html>
        """
        
        return {
            "text": text_report,
            "html": html_report,
            "subject": f"Reporte Semanal de Soporte - {period['end'][:10]}"
        }
    
    @task(task_id="send_report")
    def send_report(formatted_report: Dict[str, str]) -> None:
        """Envía el reporte por email y/o Slack."""
        # Enviar por email
        if EMAIL_API_URL and REPORT_RECIPIENTS:
            try:
                for recipient in REPORT_RECIPIENTS:
                    if recipient.strip():
                        payload = {
                            "to": recipient.strip(),
                            "subject": formatted_report["subject"],
                            "body": formatted_report["text"],
                            "html": formatted_report["html"]
                        }
                        response = requests.post(
                            EMAIL_API_URL,
                            json=payload,
                            timeout=30
                        )
                        response.raise_for_status()
                        logger.info(f"Report sent to {recipient}")
            except Exception as e:
                logger.error(f"Failed to send email report: {e}", exc_info=True)
        
        # Enviar a Slack
        if SLACK_WEBHOOK_URL:
            try:
                payload = {
                    "text": formatted_report["subject"],
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": formatted_report["text"].replace("\n", "\n")
                            }
                        }
                    ]
                }
                response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
                response.raise_for_status()
                logger.info("Report sent to Slack")
            except Exception as e:
                logger.error(f"Failed to send Slack report: {e}", exc_info=True)
    
    # Pipeline
    report_data = generate_weekly_report()
    formatted = format_report(report_data)
    send_report(formatted)


dag = support_tickets_reports()

