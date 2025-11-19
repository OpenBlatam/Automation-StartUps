from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List, Optional
import json
import logging
import csv
import io

import pendulum
import requests
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.stats import Stats
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


@dag(
    dag_id="sales_analytics_reports",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 9 * * 1",  # Lunes 09:00 UTC (reporte semanal)
    catchup=False,
    default_args={
        "owner": "sales",
        "retries": 1,
        "retry_delay": timedelta(minutes=10),
        "depends_on_past": False,
    },
    doc_md="""
    ### Reportes y Analytics de Ventas
    
    Genera reportes automáticos semanales y mensuales del pipeline de ventas:
    - Métricas de conversión por etapa
    - Performance de vendedores
    - Análisis de fuentes de leads
    - Tendencias de scoring
    - Forecast de ventas
    - Exportación a CSV/JSON
    
    **Schedule:** Lunes 09:00 UTC (semanal)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "report_type": Param("weekly", type="string", enum=["weekly", "monthly"]),
        "export_to_s3": Param(False, type="boolean"),
        "s3_bucket": Param("", type="string"),
        "s3_path": Param("sales_reports", type="string"),
        "slack_webhook_url": Param("", type="string"),
        "email_recipients": Param("", type="string"),
    },
    tags=["sales", "analytics", "reports"],
)
def sales_analytics_reports() -> None:
    """
    DAG para generar reportes y analytics de ventas.
    """
    
    @task(task_id="refresh_metrics_view")
    def refresh_metrics_view() -> bool:
        """Refresca la vista materializada de métricas."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("REFRESH MATERIALIZED VIEW mv_sales_metrics")
                    conn.commit()
            
            logger.info("Vista de métricas refrescada")
            return True
        except Exception as e:
            logger.error(f"Error refrescando métricas: {e}", exc_info=True)
            return False
    
    @task(task_id="generate_pipeline_report")
    def generate_pipeline_report() -> Dict[str, Any]:
        """Genera reporte del pipeline de ventas."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        report_type = str(params["report_type"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Determinar rango de fechas
        if report_type == "weekly":
            start_date = datetime.utcnow() - timedelta(days=7)
            end_date = datetime.utcnow()
        else:  # monthly
            start_date = datetime.utcnow() - timedelta(days=30)
            end_date = datetime.utcnow()
        
        report = {
            "report_type": report_type,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Pipeline por etapa
                cur.execute("""
                    SELECT 
                        stage,
                        COUNT(*) AS count,
                        AVG(score) AS avg_score,
                        SUM(estimated_value) AS total_value,
                        AVG(probability_pct) AS avg_probability,
                        COUNT(*) FILTER (WHERE assigned_to IS NOT NULL) AS assigned_count
                    FROM sales_pipeline
                    WHERE qualified_at >= %s AND qualified_at <= %s
                    GROUP BY stage
                    ORDER BY 
                        CASE stage
                            WHEN 'qualified' THEN 1
                            WHEN 'contacted' THEN 2
                            WHEN 'meeting_scheduled' THEN 3
                            WHEN 'proposal_sent' THEN 4
                            WHEN 'negotiating' THEN 5
                            WHEN 'closed_won' THEN 6
                            WHEN 'closed_lost' THEN 7
                        END
                """, (start_date, end_date))
                
                columns = [desc[0] for desc in cur.description]
                report["pipeline_by_stage"] = [
                    dict(zip(columns, row)) for row in cur.fetchall()
                ]
                
                # Performance de vendedores
                cur.execute("""
                    SELECT 
                        assigned_to,
                        COUNT(*) AS total_leads,
                        COUNT(*) FILTER (WHERE stage = 'closed_won') AS won,
                        COUNT(*) FILTER (WHERE stage = 'closed_lost') AS lost,
                        ROUND(
                            COUNT(*) FILTER (WHERE stage = 'closed_won')::NUMERIC / 
                            NULLIF(COUNT(*) FILTER (WHERE stage IN ('closed_won', 'closed_lost')), 0) * 100,
                            2
                        ) AS win_rate_pct,
                        SUM(estimated_value) FILTER (WHERE stage = 'closed_won') AS total_revenue,
                        AVG(EXTRACT(EPOCH FROM (COALESCE(closed_at, NOW()) - qualified_at)) / 86400) 
                            FILTER (WHERE stage = 'closed_won') AS avg_days_to_close
                    FROM sales_pipeline
                    WHERE qualified_at >= %s AND qualified_at <= %s
                    AND assigned_to IS NOT NULL
                    GROUP BY assigned_to
                    ORDER BY total_revenue DESC NULLS LAST
                """, (start_date, end_date))
                
                columns = [desc[0] for desc in cur.description]
                report["sales_rep_performance"] = [
                    dict(zip(columns, row)) for row in cur.fetchall()
                ]
                
                # Análisis de fuentes
                cur.execute("""
                    SELECT 
                        source,
                        COUNT(*) AS total_leads,
                        AVG(score) AS avg_score,
                        COUNT(*) FILTER (WHERE stage = 'closed_won') AS won,
                        ROUND(
                            COUNT(*) FILTER (WHERE stage = 'closed_won')::NUMERIC / 
                            NULLIF(COUNT(*), 0) * 100,
                            2
                        ) AS conversion_rate_pct
                    FROM sales_pipeline
                    WHERE qualified_at >= %s AND qualified_at <= %s
                    GROUP BY source
                    ORDER BY total_leads DESC
                """, (start_date, end_date))
                
                columns = [desc[0] for desc in cur.description]
                report["source_analysis"] = [
                    dict(zip(columns, row)) for row in cur.fetchall()
                ]
                
                # Tendencias de scoring
                cur.execute("""
                    SELECT 
                        DATE_TRUNC('day', calculated_at) AS date,
                        COUNT(*) AS score_updates,
                        AVG(score) AS avg_score,
                        AVG(score_change) AS avg_score_change,
                        COUNT(*) FILTER (WHERE score_change > 0) AS increases,
                        COUNT(*) FILTER (WHERE score_change < 0) AS decreases
                    FROM lead_score_history
                    WHERE calculated_at >= %s AND calculated_at <= %s
                    GROUP BY DATE_TRUNC('day', calculated_at)
                    ORDER BY date DESC
                """, (start_date, end_date))
                
                columns = [desc[0] for desc in cur.description]
                report["scoring_trends"] = [
                    dict(zip(columns, row)) for row in cur.fetchall()
                ]
                
                # Forecast de ventas
                cur.execute("""
                    SELECT 
                        SUM(estimated_value * probability_pct / 100.0) AS weighted_forecast,
                        SUM(estimated_value) AS total_pipeline_value,
                        COUNT(*) AS total_deals,
                        AVG(probability_pct) AS avg_probability
                    FROM sales_pipeline
                    WHERE stage NOT IN ('closed_won', 'closed_lost')
                    AND estimated_value IS NOT NULL
                """)
                
                row = cur.fetchone()
                report["sales_forecast"] = {
                    "weighted_forecast": float(row[0] or 0),
                    "total_pipeline_value": float(row[1] or 0),
                    "total_deals": row[2] or 0,
                    "avg_probability": float(row[3] or 0) if row[3] else None
                }
                
                # Resumen de tareas
                cur.execute("""
                    SELECT 
                        COUNT(*) AS total_tasks,
                        COUNT(*) FILTER (WHERE status = 'completed') AS completed,
                        COUNT(*) FILTER (WHERE status = 'pending') AS pending,
                        COUNT(*) FILTER (WHERE status = 'pending' AND due_date <= NOW()) AS overdue,
                        AVG(EXTRACT(EPOCH FROM (completed_at - created_at)) / 3600) 
                            FILTER (WHERE status = 'completed') AS avg_completion_hours
                    FROM sales_followup_tasks
                    WHERE created_at >= %s AND created_at <= %s
                """, (start_date, end_date))
                
                row = cur.fetchone()
                report["tasks_summary"] = {
                    "total": row[0] or 0,
                    "completed": row[1] or 0,
                    "pending": row[2] or 0,
                    "overdue": row[3] or 0,
                    "avg_completion_hours": float(row[4] or 0) if row[4] else None
                }
        
        logger.info(f"Reporte de pipeline generado: {len(report['pipeline_by_stage'])} etapas")
        return report
    
    @task(task_id="generate_campaign_performance")
    def generate_campaign_performance() -> Dict[str, Any]:
        """Genera reporte de performance de campañas."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        c.id,
                        c.name,
                        c.campaign_type,
                        COUNT(DISTINCT ce.id) AS total_executions,
                        COUNT(DISTINCT ce.lead_ext_id) AS unique_leads,
                        COUNT(DISTINCT CASE WHEN ce.status = 'completed' THEN ce.id END) AS completed,
                        COUNT(DISTINCT e.id) FILTER (WHERE e.status = 'sent') AS events_sent,
                        COUNT(DISTINCT e.id) FILTER (WHERE e.event_type LIKE '%opened%') AS events_opened,
                        COUNT(DISTINCT e.id) FILTER (WHERE e.event_type LIKE '%clicked%') AS events_clicked,
                        ROUND(
                            COUNT(DISTINCT CASE WHEN ce.status = 'completed' THEN ce.id END)::NUMERIC /
                            NULLIF(COUNT(DISTINCT ce.id), 0) * 100,
                            2
                        ) AS completion_rate_pct
                    FROM sales_campaigns c
                    LEFT JOIN sales_campaign_executions ce ON c.id = ce.campaign_id
                    LEFT JOIN sales_campaign_events e ON ce.id = e.execution_id
                    WHERE c.enabled = true
                    GROUP BY c.id, c.name, c.campaign_type
                    ORDER BY total_executions DESC
                """)
                
                columns = [desc[0] for desc in cur.description]
                campaigns = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        return {"campaigns": campaigns}
    
    @task(task_id="export_to_csv")
    def export_to_csv(pipeline_report: Dict[str, Any], campaign_report: Dict[str, Any]) -> str:
        """Exporta reporte a CSV."""
        ctx = get_current_context()
        params = ctx["params"]
        export_s3 = bool(params["export_to_s3"])
        s3_bucket = str(params["s3_bucket"]).strip()
        s3_path = str(params["s3_path"]).strip()
        
        if not export_s3 or not s3_bucket:
            logger.info("Exportación a S3 deshabilitada")
            return ""
        
        # Crear CSV en memoria
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Pipeline por etapa
        writer.writerow(["Pipeline por Etapa"])
        writer.writerow(["Etapa", "Count", "Avg Score", "Total Value", "Avg Probability", "Assigned"])
        for stage_data in pipeline_report.get("pipeline_by_stage", []):
            writer.writerow([
                stage_data.get("stage"),
                stage_data.get("count"),
                f"{stage_data.get('avg_score', 0):.2f}",
                f"{stage_data.get('total_value', 0):.2f}",
                f"{stage_data.get('avg_probability', 0):.2f}",
                stage_data.get("assigned_count")
            ])
        
        writer.writerow([])
        
        # Performance de vendedores
        writer.writerow(["Performance de Vendedores"])
        writer.writerow(["Vendedor", "Total Leads", "Won", "Lost", "Win Rate %", "Revenue", "Avg Days to Close"])
        for rep in pipeline_report.get("sales_rep_performance", []):
            writer.writerow([
                rep.get("assigned_to"),
                rep.get("total_leads"),
                rep.get("won"),
                rep.get("lost"),
                f"{rep.get('win_rate_pct', 0):.2f}",
                f"{rep.get('total_revenue', 0):.2f}",
                f"{rep.get('avg_days_to_close', 0):.2f}"
            ])
        
        csv_content = output.getvalue()
        
        # Exportar a S3 (requiere boto3)
        try:
            import boto3
            from airflow.providers.amazon.aws.hooks.s3 import S3Hook
            
            s3_hook = S3Hook()
            key = f"{s3_path}/sales_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            
            s3_hook.load_string(
                string_data=csv_content,
                bucket_name=s3_bucket,
                key=key,
                replace=True
            )
            
            logger.info(f"Reporte exportado a s3://{s3_bucket}/{key}")
            return f"s3://{s3_bucket}/{key}"
        except Exception as e:
            logger.error(f"Error exportando a S3: {e}", exc_info=True)
            return ""
    
    @task(task_id="send_report")
    def send_report(pipeline_report: Dict[str, Any], campaign_report: Dict[str, Any],
                   csv_location: str) -> None:
        """Envía reporte a Slack y/o email."""
        ctx = get_current_context()
        params = ctx["params"]
        slack_url = str(params["slack_webhook_url"]).strip()
        email_recipients = str(params["email_recipients"]).strip()
        
        # Formatear resumen
        pipeline_data = pipeline_report.get("pipeline_by_stage", [])
        total_qualified = sum(s.get("count", 0) for s in pipeline_data if s.get("stage") != "closed_won" and s.get("stage") != "closed_lost")
        total_won = sum(s.get("count", 0) for s in pipeline_data if s.get("stage") == "closed_won")
        total_lost = sum(s.get("count", 0) for s in pipeline_data if s.get("stage") == "closed_lost")
        forecast = pipeline_report.get("sales_forecast", {})
        
        summary = f"""
📊 *Sales Analytics Report - {pipeline_report.get('report_type', 'weekly').title()}*

📈 *Pipeline Summary:*
• Total Qualified: {total_qualified}
• Closed Won: {total_won}
• Closed Lost: {total_lost}
• Win Rate: {total_won / (total_won + total_lost) * 100:.1f}% (si aplica)

💰 *Sales Forecast:*
• Weighted Forecast: ${forecast.get('weighted_forecast', 0):,.2f}
• Total Pipeline Value: ${forecast.get('total_pipeline_value', 0):,.2f}
• Avg Probability: {forecast.get('avg_probability', 0):.1f}%

🎯 *Pipeline by Stage:*
"""
        for stage_data in pipeline_data:
            if stage_data.get("stage") not in ["closed_won", "closed_lost"]:
                summary += f"• {stage_data.get('stage')}: {stage_data.get('count')} leads (${stage_data.get('total_value', 0):,.2f})\n"
        
        tasks_summary = pipeline_report.get("tasks_summary", {})
        summary += f"""
📋 *Tasks Summary:*
• Total: {tasks_summary.get('total', 0)}
• Completed: {tasks_summary.get('completed', 0)}
• Pending: {tasks_summary.get('pending', 0)}
• Overdue: {tasks_summary.get('overdue', 0)}
"""
        
        if csv_location:
            summary += f"\n📎 Full report: {csv_location}"
        
        # Enviar a Slack
        if slack_url:
            try:
                requests.post(
                    slack_url,
                    json={"text": summary},
                    timeout=10
                )
                logger.info("Reporte enviado a Slack")
            except Exception as e:
                logger.warning(f"Error enviando a Slack: {e}")
        
        # Enviar por email (requiere configuración de email)
        if email_recipients:
            # Aquí se podría implementar envío por email usando Airflow email backend
            logger.info(f"Reporte listo para enviar a: {email_recipients}")
    
    # Pipeline
    metrics_refreshed = refresh_metrics_view()
    pipeline_report = generate_pipeline_report()
    campaign_report = generate_campaign_performance()
    csv_location = export_to_csv(pipeline_report, campaign_report)
    send_report(pipeline_report, campaign_report, csv_location)


dag = sales_analytics_reports()

