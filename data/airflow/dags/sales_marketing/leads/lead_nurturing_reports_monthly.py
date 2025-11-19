from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List
import csv
import os
import logging

import pendulum
import requests
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.stats import Stats
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


@dag(
    dag_id="lead_nurturing_reports_monthly",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 9 1 * *",  # Día 1 de cada mes, 09:00 UTC
    catchup=False,
    default_args={
        "owner": "marketing",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
    },
    doc_md="""
    ### Reportes Mensuales de Lead Nurturing
    
    Genera reportes ejecutivos mensuales con análisis completo y tendencias.
    
    **Outputs:**
    - CSV con métricas mensuales y comparativas
    - HTML ejecutivo con análisis de tendencias
    - Top templates y pasos por performance
    - Exportación a S3 (opcional)
    - Resumen ejecutivo en Slack
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "reports_dir": Param("/tmp/lead_nurturing_reports", type="string"),
        "slack_webhook_url": Param("", type="string"),
        "export_to_s3": Param(False, type="boolean"),
        "s3_bucket": Param("", type="string"),
        "s3_path": Param("lead_nurturing/reports", type="string"),
    },
    tags=["marketing", "lead-nurturing", "reports", "monthly"],
)
def lead_nurturing_reports_monthly() -> None:
    """
    DAG para generar reportes mensuales ejecutivos de lead nurturing.
    """
    
    @task(task_id="generate_monthly_report")
    def generate_monthly_report() -> Dict[str, Any]:
        """
        Genera reporte mensual completo con análisis de tendencias.
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        now = pendulum.now("UTC")
        month_start = now.start_of("month")
        prev_month_start = month_start.subtract(months=1)
        prev_month_end = month_start.subtract(days=1)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Métricas del mes actual
                cur.execute("""
                    SELECT 
                        COUNT(DISTINCT s.id) as total_sequences,
                        COUNT(DISTINCT CASE WHEN s.qualified_at IS NOT NULL THEN s.id END) as qualified,
                        COUNT(DISTINCT e.id) as total_emails_sent,
                        COUNT(DISTINCT CASE WHEN e.opened_at IS NOT NULL THEN e.id END) as opened,
                        COUNT(DISTINCT CASE WHEN e.clicked_at IS NOT NULL THEN e.id END) as clicked,
                        COUNT(DISTINCT CASE WHEN e.replied_at IS NOT NULL THEN e.id END) as replied,
                        AVG(EXTRACT(EPOCH FROM (s.qualified_at - s.started_at)) / 86400) as avg_days_to_qualify
                    FROM lead_nurturing_sequences s
                    LEFT JOIN lead_nurturing_events e ON s.id = e.sequence_id
                    WHERE s.started_at >= %s
                        AND s.started_at < %s
                """, (month_start.to_datetime_string(), now.to_datetime_string()))
                
                month_result = cur.fetchone()
                m_total, m_qualified, m_sent, m_opened, m_clicked, m_replied, m_avg_days = month_result or (0, 0, 0, 0, 0, 0, 0)
                
                # Métricas del mes anterior
                cur.execute("""
                    SELECT 
                        COUNT(DISTINCT s.id) as total_sequences,
                        COUNT(DISTINCT CASE WHEN s.qualified_at IS NOT NULL THEN s.id END) as qualified,
                        COUNT(DISTINCT e.id) as total_emails_sent,
                        COUNT(DISTINCT CASE WHEN e.opened_at IS NOT NULL THEN e.id END) as opened,
                        COUNT(DISTINCT CASE WHEN e.clicked_at IS NOT NULL THEN e.id END) as clicked,
                        COUNT(DISTINCT CASE WHEN e.replied_at IS NOT NULL THEN e.id END) as replied,
                        AVG(EXTRACT(EPOCH FROM (s.qualified_at - s.started_at)) / 86400) as avg_days_to_qualify
                    FROM lead_nurturing_sequences s
                    LEFT JOIN lead_nurturing_events e ON s.id = e.sequence_id
                    WHERE s.started_at >= %s
                        AND s.started_at < %s
                """, (prev_month_start.to_datetime_string(), prev_month_end.to_datetime_string()))
                
                prev_result = cur.fetchone()
                p_total, p_qualified, p_sent, p_opened, p_clicked, p_replied, p_avg_days = prev_result or (0, 0, 0, 0, 0, 0, 0)
                
                # Top templates por performance
                cur.execute("""
                    SELECT 
                        s.sequence_name,
                        COUNT(DISTINCT s.id) as sequences,
                        COUNT(DISTINCT CASE WHEN s.qualified_at IS NOT NULL THEN s.id END) as qualified,
                        ROUND(COUNT(DISTINCT CASE WHEN s.qualified_at IS NOT NULL THEN s.id END)::NUMERIC / 
                              NULLIF(COUNT(DISTINCT s.id), 0) * 100, 2) as conversion_rate
                    FROM lead_nurturing_sequences s
                    WHERE s.started_at >= %s
                        AND s.started_at < %s
                    GROUP BY s.sequence_name
                    ORDER BY conversion_rate DESC
                    LIMIT 5
                """, (month_start.to_datetime_string(), now.to_datetime_string()))
                
                top_templates = [
                    {"name": row[0], "sequences": row[1], "qualified": row[2], "conversion_rate": float(row[3] or 0)}
                    for row in cur.fetchall()
                ]
                
                # Top pasos por engagement
                cur.execute("""
                    SELECT 
                        step_number,
                        COUNT(*) as sent,
                        COUNT(*) FILTER (WHERE opened_at IS NOT NULL) as opened,
                        COUNT(*) FILTER (WHERE replied_at IS NOT NULL) as replied,
                        ROUND(COUNT(*) FILTER (WHERE replied_at IS NOT NULL)::NUMERIC / 
                              NULLIF(COUNT(*), 0) * 100, 2) as reply_rate
                    FROM lead_nurturing_events
                    WHERE sent_at >= %s
                        AND sent_at < %s
                        AND status = 'sent'
                    GROUP BY step_number
                    ORDER BY reply_rate DESC
                    LIMIT 5
                """, (month_start.to_datetime_string(), now.to_datetime_string()))
                
                top_steps = [
                    {
                        "step_number": int(row[0]),
                        "sent": row[1],
                        "opened": row[2],
                        "replied": row[3],
                        "reply_rate": float(row[4] or 0)
                    }
                    for row in cur.fetchall()
                ]
        
        # Calcular tasas
        def calc_rate(current, total):
            return (current / total * 100) if total > 0 else 0
        
        def calc_change(current, previous):
            if previous == 0:
                return 100.0 if current > 0 else 0.0
            return ((current - previous) / previous) * 100
        
        m_conv_rate = calc_rate(m_qualified, m_total)
        p_conv_rate = calc_rate(p_qualified, p_total)
        conv_change = calc_change(m_conv_rate, p_conv_rate)
        
        m_open_rate = calc_rate(m_opened, m_sent)
        m_reply_rate = calc_rate(m_replied, m_sent)
        
        report = {
            "period": f"{month_start.format('YYYY-MM')}",
            "previous_period": f"{prev_month_start.format('YYYY-MM')}",
            "current_month": {
                "sequences": m_total,
                "qualified": m_qualified,
                "conversion_rate": round(m_conv_rate, 2),
                "emails_sent": m_sent,
                "emails_opened": m_opened,
                "emails_replied": m_replied,
                "open_rate": round(m_open_rate, 2),
                "reply_rate": round(m_reply_rate, 2),
                "avg_days_to_qualify": round(float(m_avg_days or 0), 2)
            },
            "previous_month": {
                "sequences": p_total,
                "qualified": p_qualified,
                "conversion_rate": round(p_conv_rate, 2),
                "emails_sent": p_sent,
                "emails_opened": p_opened,
                "emails_replied": p_replied,
                "open_rate": round(calc_rate(p_opened, p_sent), 2),
                "reply_rate": round(calc_rate(p_replied, p_sent), 2),
                "avg_days_to_qualify": round(float(p_avg_days or 0), 2)
            },
            "month_over_month_change": {
                "conversion_rate_change": round(conv_change, 2),
                "sequences_change": round(calc_change(m_total, p_total), 2),
                "qualified_change": round(calc_change(m_qualified, p_qualified), 2)
            },
            "top_templates": top_templates,
            "top_steps": top_steps,
            "generated_at": now.isoformat()
        }
        
        logger.info(f"Reporte mensual generado para {report['period']}")
        return report
    
    @task(task_id="export_monthly_csv")
    def export_monthly_csv(report: Dict[str, Any]) -> str:
        """
        Exporta reporte mensual a CSV.
        """
        ctx = get_current_context()
        params = ctx["params"]
        reports_dir = str(params["reports_dir"])
        
        os.makedirs(reports_dir, exist_ok=True)
        
        csv_path = os.path.join(
            reports_dir,
            f"lead_nurturing_monthly_{report['period']}.csv"
        )
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "metric", "current_month", "previous_month", "change_pct"
            ])
            
            writer.writerow([
                "sequences_started",
                report["current_month"]["sequences"],
                report["previous_month"]["sequences"],
                report["month_over_month_change"]["sequences_change"]
            ])
            
            writer.writerow([
                "leads_qualified",
                report["current_month"]["qualified"],
                report["previous_month"]["qualified"],
                report["month_over_month_change"]["qualified_change"]
            ])
            
            writer.writerow([
                "conversion_rate",
                report["current_month"]["conversion_rate"],
                report["previous_month"]["conversion_rate"],
                report["month_over_month_change"]["conversion_rate_change"]
            ])
            
            writer.writerow([
                "reply_rate",
                report["current_month"]["reply_rate"],
                report["previous_month"]["reply_rate"],
                round(calc_change(
                    report["current_month"]["reply_rate"],
                    report["previous_month"]["reply_rate"]
                ), 2)
            ])
        
        logger.info(f"CSV mensual generado: {csv_path}")
        return csv_path
    
    def calc_change(current: float, previous: float) -> float:
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100
    
    @task(task_id="slack_monthly_summary")
    def slack_monthly_summary(report: Dict[str, Any]) -> None:
        """
        Envía resumen mensual ejecutivo a Slack.
        """
        ctx = get_current_context()
        params = ctx["params"]
        slack_webhook = str(params.get("slack_webhook_url", "")).strip()
        
        if not slack_webhook:
            return
        
        current = report["current_month"]
        changes = report["month_over_month_change"]
        
        text = (
            f"📊 *Reporte Mensual Lead Nurturing - {report['period']}*\n\n"
            f"*Métricas Principales:*\n"
            f"• Leads calificados: {current['qualified']} ({current['conversion_rate']}%)\n"
            f"• Secuencias iniciadas: {current['sequences']}\n"
            f"• Reply rate: {current['reply_rate']}%\n"
            f"• Tiempo promedio a calificar: {current['avg_days_to_qualify']} días\n\n"
            f"*Cambio vs mes anterior:*\n"
            f"• Conversion rate: {changes['conversion_rate_change']:+.1f}%\n"
            f"• Leads calificados: {changes['qualified_change']:+.1f}%\n"
        )
        
        if report["top_templates"]:
            text += f"\n*Top Templates:*\n"
            for i, template in enumerate(report["top_templates"][:3], 1):
                text += f"{i}. {template['name']}: {template['conversion_rate']}%\n"
        
        try:
            requests.post(
                slack_webhook,
                json={"text": text},
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
        except Exception as e:
            logger.warning(f"Error enviando a Slack: {e}")
    
    # Pipeline
    monthly_report = generate_monthly_report()
    csv_file = export_monthly_csv(monthly_report)
    slack_monthly_summary(monthly_report)


dag = lead_nurturing_reports_monthly()

