from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List
import csv
import json
import os

import pendulum
import requests
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.stats import Stats
from airflow.providers.postgres.hooks.postgres import PostgresHook


@dag(
    dag_id="lead_nurturing_reports",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 9 * * 1",  # Lunes 09:00 UTC (semanal)
    catchup=False,
    default_args={
        "owner": "marketing",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
    },
    doc_md="""
    ### Reportes Semanales de Lead Nurturing
    
    Genera reportes ejecutivos semanales con análisis completo del sistema de nutrición.
    
    **Outputs:**
    - CSV con métricas semanales
    - HTML ejecutivo con comparativas
    - Exportación a S3 (opcional)
    - Resumen en Slack
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "reports_dir": Param("/tmp/lead_nurturing_reports", type="string"),
        "slack_webhook_url": Param("", type="string"),
        "export_to_s3": Param(False, type="boolean"),
        "s3_bucket": Param("", type="string"),
        "s3_path": Param("lead_nurturing/reports", type="string"),
    },
    tags=["marketing", "lead-nurturing", "reports"],
)
def lead_nurturing_reports() -> None:
    """
    DAG para generar reportes semanales de lead nurturing.
    """
    
    @task(task_id="generate_weekly_csv")
    def generate_weekly_csv() -> str:
        """
        Genera CSV con métricas semanales agregadas.
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        reports_dir = str(params["reports_dir"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        os.makedirs(reports_dir, exist_ok=True)
        
        # Query métricas de la última semana
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        DATE_TRUNC('day', s.started_at) as date,
                        COUNT(DISTINCT s.id) as sequences_started,
                        COUNT(DISTINCT CASE WHEN s.qualified_at IS NOT NULL THEN s.id END) as qualified,
                        COUNT(DISTINCT e.id) as emails_sent,
                        COUNT(DISTINCT CASE WHEN e.opened_at IS NOT NULL THEN e.id END) as emails_opened,
                        COUNT(DISTINCT CASE WHEN e.clicked_at IS NOT NULL THEN e.id END) as emails_clicked,
                        COUNT(DISTINCT CASE WHEN e.replied_at IS NOT NULL THEN e.id END) as emails_replied
                    FROM lead_nurturing_sequences s
                    LEFT JOIN lead_nurturing_events e ON s.id = e.sequence_id
                    WHERE s.started_at >= CURRENT_DATE - INTERVAL '7 days'
                    GROUP BY DATE_TRUNC('day', s.started_at)
                    ORDER BY date DESC
                """)
                
                rows = cur.fetchall()
        
        # Escribir CSV
        csv_path = os.path.join(reports_dir, f"lead_nurturing_weekly_{pendulum.now('UTC').to_date_string()}.csv")
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "date", "sequences_started", "qualified", "emails_sent",
                "emails_opened", "emails_clicked", "emails_replied",
                "conversion_rate", "open_rate", "click_rate", "reply_rate"
            ])
            
            for row in rows:
                date, started, qualified, sent, opened, clicked, replied = row
                conversion = (qualified / started * 100) if started > 0 else 0
                open_rate = (opened / sent * 100) if sent > 0 else 0
                click_rate = (clicked / sent * 100) if sent > 0 else 0
                reply_rate = (replied / sent * 100) if sent > 0 else 0
                
                writer.writerow([
                    date, started, qualified, sent, opened, clicked, replied,
                    round(conversion, 2), round(open_rate, 2),
                    round(click_rate, 2), round(reply_rate, 2)
                ])
        
        logger.info(f"CSV generado: {csv_path}")
        return csv_path
    
    @task(task_id="generate_weekly_html")
    def generate_weekly_html() -> str:
        """
        Genera reporte HTML ejecutivo con comparativas semanales.
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        reports_dir = str(params["reports_dir"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        now = pendulum.now("UTC")
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Métricas última semana
                cur.execute("""
                    SELECT 
                        COUNT(DISTINCT s.id) as total_sequences,
                        COUNT(DISTINCT CASE WHEN s.qualified_at IS NOT NULL THEN s.id END) as qualified,
                        COUNT(DISTINCT e.id) as total_emails_sent,
                        COUNT(DISTINCT CASE WHEN e.opened_at IS NOT NULL THEN e.id END) as opened,
                        COUNT(DISTINCT CASE WHEN e.clicked_at IS NOT NULL THEN e.id END) as clicked,
                        COUNT(DISTINCT CASE WHEN e.replied_at IS NOT NULL THEN e.id END) as replied,
                        AVG(EXTRACT(EPOCH FROM (s.qualified_at - s.started_at)) / 86400) as avg_days
                    FROM lead_nurturing_sequences s
                    LEFT JOIN lead_nurturing_events e ON s.id = e.sequence_id
                    WHERE s.started_at >= CURRENT_DATE - INTERVAL '7 days'
                """)
                
                week_result = cur.fetchone()
                week_total, week_qualified, week_sent, week_opened, week_clicked, week_replied, week_avg_days = week_result or (0, 0, 0, 0, 0, 0, 0)
                
                # Métricas semana anterior (para comparación)
                cur.execute("""
                    SELECT 
                        COUNT(DISTINCT s.id) as total_sequences,
                        COUNT(DISTINCT CASE WHEN s.qualified_at IS NOT NULL THEN s.id END) as qualified,
                        COUNT(DISTINCT e.id) as total_emails_sent,
                        COUNT(DISTINCT CASE WHEN e.opened_at IS NOT NULL THEN e.id END) as opened,
                        COUNT(DISTINCT CASE WHEN e.clicked_at IS NOT NULL THEN e.id END) as clicked,
                        COUNT(DISTINCT CASE WHEN e.replied_at IS NOT NULL THEN e.id END) as replied,
                        AVG(EXTRACT(EPOCH FROM (s.qualified_at - s.started_at)) / 86400) as avg_days
                    FROM lead_nurturing_sequences s
                    LEFT JOIN lead_nurturing_events e ON s.id = e.sequence_id
                    WHERE s.started_at >= CURRENT_DATE - INTERVAL '14 days'
                        AND s.started_at < CURRENT_DATE - INTERVAL '7 days'
                """)
                
                prev_result = cur.fetchone()
                prev_total, prev_qualified, prev_sent, prev_opened, prev_clicked, prev_replied, prev_avg_days = prev_result or (0, 0, 0, 0, 0, 0, 0)
        
        # Calcular tasas y cambios
        def calc_rate(current, total):
            return (current / total * 100) if total > 0 else 0
        
        def calc_change(current, previous):
            if previous == 0:
                return 100.0 if current > 0 else 0.0
            return ((current - previous) / previous) * 100
        
        week_conv_rate = calc_rate(week_qualified, week_total)
        prev_conv_rate = calc_rate(prev_qualified, prev_total)
        conv_change = calc_change(week_conv_rate, prev_conv_rate)
        
        week_open_rate = calc_rate(week_opened, week_sent)
        prev_open_rate = calc_rate(prev_opened, prev_sent)
        open_change = calc_change(week_open_rate, prev_open_rate)
        
        week_reply_rate = calc_rate(week_replied, week_sent)
        prev_reply_rate = calc_rate(prev_replied, prev_sent)
        reply_change = calc_change(week_reply_rate, prev_reply_rate)
        
        # Generar HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Lead Nurturing Report - Semana {now.to_date_string()}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .metric-card {{ background: #ecf0f1; padding: 20px; margin: 15px 0; border-radius: 6px; border-left: 4px solid #3498db; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #2c3e50; }}
        .metric-label {{ color: #7f8c8d; margin-top: 5px; }}
        .change {{ font-size: 0.9em; margin-top: 5px; }}
        .change.positive {{ color: #27ae60; }}
        .change.negative {{ color: #e74c3c; }}
        .change.neutral {{ color: #95a5a6; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #3498db; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 2px solid #ecf0f1; color: #95a5a6; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Reporte Semanal de Lead Nurturing</h1>
        <p><strong>Período:</strong> Última semana (7 días) | <strong>Generado:</strong> {now.format('YYYY-MM-DD HH:mm')} UTC</p>
        
        <h2>Métricas Principales</h2>
        <div class="metric-card">
            <div class="metric-value">{week_qualified:.0f}</div>
            <div class="metric-label">Leads Calificados</div>
            <div class="change {'positive' if conv_change > 0 else 'negative' if conv_change < 0 else 'neutral'}">
                {f'{conv_change:+.1f}%' if conv_change != 0 else 'Sin cambio'} vs semana anterior
            </div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value">{week_conv_rate:.2f}%</div>
            <div class="metric-label">Tasa de Conversión</div>
            <div class="change {'positive' if conv_change > 0 else 'negative' if conv_change < 0 else 'neutral'}">
                {f'{conv_change:+.1f}%' if conv_change != 0 else 'Sin cambio'} vs semana anterior ({prev_conv_rate:.2f}%)
            </div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value">{week_reply_rate:.2f}%</div>
            <div class="metric-label">Reply Rate</div>
            <div class="change {'positive' if reply_change > 0 else 'negative' if reply_change < 0 else 'neutral'}">
                {f'{reply_change:+.1f}%' if reply_change != 0 else 'Sin cambio'} vs semana anterior ({prev_reply_rate:.2f}%)
            </div>
        </div>
        
        <h2>Desglose Semanal</h2>
        <table>
            <thead>
                <tr>
                    <th>Métrica</th>
                    <th>Última Semana</th>
                    <th>Semana Anterior</th>
                    <th>Cambio</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Secuencias Iniciadas</td>
                    <td>{week_total}</td>
                    <td>{prev_total}</td>
                    <td class="{'positive' if week_total > prev_total else 'negative' if week_total < prev_total else 'neutral'}">
                        {calc_change(week_total, prev_total):+.1f}%
                    </td>
                </tr>
                <tr>
                    <td>Emails Enviados</td>
                    <td>{week_sent}</td>
                    <td>{prev_sent}</td>
                    <td class="{'positive' if week_sent > prev_sent else 'negative' if week_sent < prev_sent else 'neutral'}">
                        {calc_change(week_sent, prev_sent):+.1f}%
                    </td>
                </tr>
                <tr>
                    <td>Emails Abiertos</td>
                    <td>{week_opened}</td>
                    <td>{prev_opened}</td>
                    <td class="{'positive' if week_opened > prev_opened else 'negative' if week_opened < prev_opened else 'neutral'}">
                        {calc_change(week_opened, prev_opened):+.1f}%
                    </td>
                </tr>
                <tr>
                    <td>Emails con Reply</td>
                    <td>{week_replied}</td>
                    <td>{prev_replied}</td>
                    <td class="{'positive' if week_replied > prev_replied else 'negative' if week_replied < prev_replied else 'neutral'}">
                        {calc_change(week_replied, prev_replied):+.1f}%
                    </td>
                </tr>
                <tr>
                    <td>Tiempo Promedio a Calificar</td>
                    <td>{week_avg_days:.1f} días</td>
                    <td>{prev_avg_days:.1f} días</td>
                    <td class="{'negative' if week_avg_days > prev_avg_days else 'positive' if week_avg_days < prev_avg_days else 'neutral'}">
                        {calc_change(week_avg_days, prev_avg_days):+.1f}%
                    </td>
                </tr>
            </tbody>
        </table>
        
        <div class="footer">
            <p>Generado automáticamente por Lead Nurturing System</p>
            <p>Para más detalles, consulta el dashboard en Airflow</p>
        </div>
    </div>
</body>
</html>
        """
        
        html_path = os.path.join(reports_dir, f"lead_nurturing_weekly_{now.to_date_string()}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"HTML report generado: {html_path}")
        return html_path
    
    @task(task_id="upload_to_s3")
    def upload_to_s3(csv_path: str, html_path: str) -> Dict[str, Any]:
        """
        Sube reportes a S3 si está configurado.
        """
        ctx = get_current_context()
        params = ctx["params"]
        export_s3 = bool(params.get("export_to_s3", False))
        s3_bucket = str(params.get("s3_bucket", "")).strip()
        s3_path = str(params.get("s3_path", "lead_nurturing/reports")).strip()
        
        if not export_s3 or not s3_bucket:
            return {"uploaded": False}
        
        try:
            import boto3
            
            s3_client = boto3.client('s3')
            date_str = datetime.utcnow().strftime("%Y/%m/%d")
            
            uploaded_files = []
            
            # Subir CSV
            csv_filename = os.path.basename(csv_path)
            csv_key = f"{s3_path}/weekly/{date_str}/{csv_filename}"
            s3_client.upload_file(csv_path, s3_bucket, csv_key)
            uploaded_files.append(csv_key)
            
            # Subir HTML
            html_filename = os.path.basename(html_path)
            html_key = f"{s3_path}/weekly/{date_str}/{html_filename}"
            s3_client.upload_file(html_path, s3_bucket, html_key)
            uploaded_files.append(html_key)
            
            logger.info(f"Reportes subidos a S3: s3://{s3_bucket}/{s3_path}/weekly/{date_str}/")
            
            return {"uploaded": True, "bucket": s3_bucket, "files": uploaded_files}
            
        except ImportError:
            logger.warning("boto3 no disponible")
            return {"uploaded": False, "reason": "boto3_not_available"}
        except Exception as e:
            logger.error(f"Error subiendo a S3: {e}", exc_info=True)
            return {"uploaded": False, "reason": str(e)[:200]}
    
    @task(task_id="slack_summary")
    def slack_summary(csv_path: str) -> None:
        """
        Envía resumen semanal a Slack.
        """
        ctx = get_current_context()
        params = ctx["params"]
        slack_webhook = str(params.get("slack_webhook_url", "")).strip()
        
        if not slack_webhook:
            return
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        COUNT(DISTINCT s.id) as total,
                        COUNT(DISTINCT CASE WHEN s.qualified_at IS NOT NULL THEN s.id END) as qualified,
                        COUNT(DISTINCT e.id) as sent,
                        COUNT(DISTINCT CASE WHEN e.replied_at IS NOT NULL THEN e.id END) as replied
                    FROM lead_nurturing_sequences s
                    LEFT JOIN lead_nurturing_events e ON s.id = e.sequence_id
                    WHERE s.started_at >= CURRENT_DATE - INTERVAL '7 days'
                """)
                
                result = cur.fetchone()
                total, qualified, sent, replied = result or (0, 0, 0, 0)
                
                conv_rate = (qualified / total * 100) if total > 0 else 0
                reply_rate = (replied / sent * 100) if sent > 0 else 0
        
        text = (
            f"📊 *Reporte Semanal Lead Nurturing*\n\n"
            f"*Resumen (últimos 7 días):*\n"
            f"• Secuencias iniciadas: {total}\n"
            f"• Leads calificados: {qualified} ({conv_rate:.2f}%)\n"
            f"• Emails enviados: {sent}\n"
            f"• Reply rate: {reply_rate:.2f}%\n\n"
            f"Reporte completo disponible en: `{csv_path}`"
        )
        
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
    csv_file = generate_weekly_csv()
    html_file = generate_weekly_html()
    s3_result = upload_to_s3(csv_file, html_file)
    slack_summary(csv_file)


dag = lead_nurturing_reports()

