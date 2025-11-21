from __future__ import annotations

from datetime import timedelta
import os
from typing import Tuple, Any

import pendulum
from airflow.decorators import dag, task
from data.airflow.plugins.db import get_conn
from data.airflow.plugins.etl_notifications import notify_slack

try:
    import boto3
    _BOTO3_AVAILABLE = True
except Exception:
    _BOTO3_AVAILABLE = False

try:
    from azure.storage.fileshare import ShareFileClient
    _AZURE_STORAGE_AVAILABLE = True
except Exception:
    _AZURE_STORAGE_AVAILABLE = False


def _one(sql: str, params: Tuple[Any, ...] | None = None) -> Any:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            r = cur.fetchone()
            return r[0] if r else None


@dag(
    dag_id="kpi_reports_weekly",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="0 9 * * 1",  # Mondays 09:00 UTC
    catchup=False,
    default_args={
        "owner": "data-eng",
        "retries": 1,
        "retry_delay": timedelta(minutes=10),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=30),
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    tags=["kpi", "reports", "weekly"],
    description="Weekly KPI summary with 7/28d comparisons and Slack notification",
)
def kpi_reports_weekly() -> None:
    @task(task_id="build_weekly_summary")
    def build_weekly_summary() -> str:
        # Metrics
        rev_7 = float(_one("SELECT COALESCE(SUM(revenue),0) FROM mv_kpi_daily WHERE day >= CURRENT_DATE - interval '7 days' AND day < CURRENT_DATE") or 0)
        rev_28 = float(_one("SELECT COALESCE(SUM(revenue),0) FROM mv_kpi_daily WHERE day >= CURRENT_DATE - interval '28 days' AND day < CURRENT_DATE") or 0)
        leads_7 = int(_one("SELECT COALESCE(SUM(leads),0) FROM mv_kpi_daily WHERE day >= CURRENT_DATE - interval '7 days' AND day < CURRENT_DATE") or 0)
        leads_28 = int(_one("SELECT COALESCE(SUM(leads),0) FROM mv_kpi_daily WHERE day >= CURRENT_DATE - interval '28 days' AND day < CURRENT_DATE") or 0)
        pay_succ_7 = float(_one("SELECT COALESCE(AVG(payments_success_rate),0) FROM mv_kpi_daily WHERE day >= CURRENT_DATE - interval '7 days' AND day < CURRENT_DATE") or 0)
        pay_succ_28 = float(_one("SELECT COALESCE(AVG(payments_success_rate),0) FROM mv_kpi_daily WHERE day >= CURRENT_DATE - interval '28 days' AND day < CURRENT_DATE") or 0)

        def pct(a: float, b: float) -> float:
            if b == 0:
                return 0.0
            return (a / b - 1.0) * 100.0

        rev_var = pct(rev_7, rev_28 / 4.0)  # approx week vs 4-week average week
        leads_var = pct(leads_7, leads_28 / 4.0)
        pay_var = pct(pay_succ_7, pay_succ_28)

        html = f"""
        <h2>Reporte semanal de KPIs</h2>
        <h3>Ingresos</h3>
        <p>Semana: <b>{rev_7:.2f}</b> | 4 semanas: <b>{rev_28:.2f}</b> | Var: <b>{rev_var:.1f}%</b></p>
        <h3>Leads</h3>
        <p>Semana: <b>{leads_7}</b> | 4 semanas: <b>{leads_28}</b> | Var: <b>{leads_var:.1f}%</b></p>
        <h3>Éxito de pagos (promedio)</h3>
        <p>Semana: <b>{pay_succ_7:.2f}%</b> | 4 semanas: <b>{pay_succ_28:.2f}%</b> | Var: <b>{pay_var:.1f}%</b></p>
        """.strip()

        out_dir = os.environ.get("KPI_REPORTS_DIR", "/tmp")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"kpi_weekly_{pendulum.now('UTC').to_date_string()}.html")
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(html)
        return out_path

    @task(task_id="notify_slack_weekly")
    def notify_slack_weekly(html_path: str) -> None:
        rev_7 = float(_one("SELECT COALESCE(SUM(revenue),0) FROM mv_kpi_daily WHERE day >= CURRENT_DATE - interval '7 days' AND day < CURRENT_DATE") or 0)
        leads_7 = int(_one("SELECT COALESCE(SUM(leads),0) FROM mv_kpi_daily WHERE day >= CURRENT_DATE - interval '7 days' AND day < CURRENT_DATE") or 0)
        pay_succ_7 = float(_one("SELECT COALESCE(AVG(payments_success_rate),0) FROM mv_kpi_daily WHERE day >= CURRENT_DATE - interval '7 days' AND day < CURRENT_DATE") or 0)
        text = (
            ":spiral_calendar_pad: Reporte semanal KPIs\n"
            f"Ingresos 7d: {rev_7:.2f}\n"
            f"Leads 7d: {leads_7}\n"
            f"Éxito pagos 7d: {pay_succ_7:.2f}%\n"
            f"HTML: {html_path}"
        )
        notify_slack(text)

    @task(task_id="upload_to_storage")
    def upload_to_storage(html_path: str) -> str | None:
        bucket = os.environ.get("KPI_REPORTS_S3_BUCKET")
        s3_prefix = os.environ.get("KPI_REPORTS_S3_PREFIX", "reports/weekly")
        if bucket and _BOTO3_AVAILABLE:
            try:
                s3 = boto3.client("s3")
                date_str = pendulum.now("UTC").to_date_string()
                key = f"{s3_prefix}/{date_str}/kpi_weekly_{date_str}.html"
                s3.upload_file(html_path, bucket, key)
                return f"s3://{bucket}/{key}"
            except Exception:
                pass
        
        adls_share = os.environ.get("KPI_REPORTS_ADLS_SHARE")
        adls_path = os.environ.get("KPI_REPORTS_ADLS_PATH", "reports/weekly")
        if adls_share and _AZURE_STORAGE_AVAILABLE:
            try:
                conn_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
                if conn_str:
                    date_str = pendulum.now("UTC").to_date_string()
                    file_path = f"{adls_path}/{date_str}/kpi_weekly_{date_str}.html"
                    client = ShareFileClient.from_connection_string(conn_str, share_name=adls_share, file_path=file_path)
                    with open(html_path, "rb") as fh:
                        client.upload_file(fh)
                    return f"adls://{adls_share}/{file_path}"
            except Exception:
                pass
        
        return None

    p = build_weekly_summary()
    storage_url = upload_to_storage(p)
    notify_slack_weekly(f"{p} (Storage: {storage_url})" if storage_url else p)
    return None


dag = kpi_reports_weekly()



