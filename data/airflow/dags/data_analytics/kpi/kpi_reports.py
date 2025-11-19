from __future__ import annotations

from datetime import timedelta
import csv
import os
from typing import Dict, Any, List, Tuple
from urllib import request

import pendulum
from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator

from data.airflow.plugins.db import get_conn
from data.airflow.plugins.etl_notifications import notify_slack

try:
    import boto3
    _BOTO3_AVAILABLE = True
except Exception:
    _BOTO3_AVAILABLE = False

try:
    from azure.storage.fileshare import ShareFileClient
    from azure.core.exceptions import AzureError
    _AZURE_STORAGE_AVAILABLE = True
except Exception:
    _AZURE_STORAGE_AVAILABLE = False


def _query_one(sql: str, params: Tuple[Any, ...] | None = None) -> Any:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            row = cur.fetchone()
            return row[0] if row else None


def _query_rows(sql: str, params: Tuple[Any, ...] | None = None) -> List[Tuple[Any, ...]]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return list(cur.fetchall())


# Operational constants
KPI_REPORTS_POOL = os.getenv("KPI_REPORTS_POOL", "default_pool")
KPI_TASK_TIMEOUT_SECONDS = int(os.getenv("KPI_TASK_TIMEOUT_SECONDS", "600"))  # 10 minutes default


@dag(
    dag_id="kpi_reports",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="0 8 * * *",  # 08:00 UTC daily
    catchup=False,
    default_args={
        "owner": "data-eng",
        "pool": KPI_REPORTS_POOL,
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=20),
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    tags=["kpi", "reports"],
    description="Daily KPI CSV export and Slack summary",
    doc_md="""
    # KPI Reports DAG

    Daily export of KPI metrics to CSV and summary notifications.

    ## Features

    - Exports last 30 days of KPIs to CSV
    - Sends Slack summary with today's metrics
    - Pushes metrics to Prometheus Pushgateway
    - Detects anomalies in revenue vs 7-day average
    - Uploads CSV to S3/ADLS if configured

    ## Configuration

    Set these environment variables:
    - `KPI_REPORTS_DIR`: Directory for CSV exports (default: /tmp)
    - `KPI_REPORTS_POOL`: Task pool (default: default_pool)
    - `KPI_TASK_TIMEOUT_SECONDS`: Task timeout (default: 600)
    - `KPI_REPORTS_S3_BUCKET`: S3 bucket for uploads (optional)
    - `KPI_REPORTS_S3_PREFIX`: S3 key prefix (default: reports/daily)
    - `KPI_REPORTS_ADLS_SHARE`: Azure File Share (optional)
    - `PUSHGATEWAY_URL`: Prometheus Pushgateway URL (optional)
    """,
)
def kpi_reports() -> None:
    @task(
        task_id="export_csv_30d",
        timeout=timedelta(seconds=KPI_TASK_TIMEOUT_SECONDS),
        pool=KPI_REPORTS_POOL,
    )
    def export_csv_30d() -> str:
        sql = (
            "SELECT day, leads, conversion_pct, revenue, payments_count, payments_success_rate "
            "FROM mv_kpi_daily WHERE day >= CURRENT_DATE - interval '30 days' ORDER BY day"
        )
        rows = _query_rows(sql)
        out_dir = os.environ.get("KPI_REPORTS_DIR", "/tmp")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"kpi_daily_{pendulum.now('UTC').to_date_string()}.csv")
        with open(out_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["day", "leads", "conversion_pct", "revenue", "payments_count", "payments_success_rate"])
            for r in rows:
                writer.writerow(list(r))
        return out_path

    @task(
        task_id="slack_summary",
        timeout=timedelta(seconds=60),
    )
    def slack_summary(csv_path: str) -> None:
        today_leads = _query_one("SELECT leads FROM mv_kpi_daily WHERE day = CURRENT_DATE") or 0
        today_revenue = _query_one("SELECT revenue FROM mv_kpi_daily WHERE day = CURRENT_DATE") or 0
        today_pay_succ = _query_one("SELECT payments_success_rate FROM mv_kpi_daily WHERE day = CURRENT_DATE") or 0
        avg7d_revenue = _query_one(
            "SELECT COALESCE(AVG(revenue),0) FROM mv_kpi_daily WHERE day >= CURRENT_DATE - interval '7 days' AND day < CURRENT_DATE"
        ) or 0

        text = (
            ":bar_chart: Resumen KPIs diario\n"
            f"Leads hoy: {int(today_leads)}\n"
            f"Ingresos hoy: {float(today_revenue):.2f}\n"
            f"Éxito pagos hoy: {float(today_pay_succ):.2f}%\n"
            f"Ingresos vs avg7d: {((float(today_revenue) / (float(avg7d_revenue) or 1)) * 100):.1f}%\n"
            f"CSV: {csv_path}"
        )
        notify_slack(text)

    done = EmptyOperator(task_id="done")

    @task(
        task_id="push_prometheus_metrics",
        timeout=timedelta(seconds=120),
    )
    def push_prometheus_metrics() -> None:
        push_url = os.environ.get("PUSHGATEWAY_URL")
        if not push_url:
            return
        # Collect values
        leads_today = _query_one("SELECT leads FROM mv_kpi_daily WHERE day = CURRENT_DATE") or 0
        revenue_today = _query_one("SELECT revenue FROM mv_kpi_daily WHERE day = CURRENT_DATE") or 0
        avg7d = _query_one("SELECT COALESCE(AVG(revenue),0) FROM mv_kpi_daily WHERE day >= CURRENT_DATE - interval '7 days' AND day < CURRENT_DATE") or 0
        pay_succ = _query_one("SELECT payments_success_rate FROM mv_kpi_daily WHERE day = CURRENT_DATE") or 0

        body = []
        body.append(f"kpi_leads_today {int(leads_today)}")
        body.append(f"kpi_revenue_today {float(revenue_today):.6f}")
        body.append(f"kpi_revenue_avg7d {float(avg7d):.6f}")
        body.append(f"kpi_payments_success_rate {float(pay_succ):.6f}")
        
        # Segment metrics (top 10 by revenue today)
        segment_rows = _query_rows(
            "SELECT country, source, revenue FROM mv_kpi_daily_segment WHERE day = CURRENT_DATE AND revenue > 0 AND country != 'unknown' AND source != 'unknown' ORDER BY revenue DESC LIMIT 10"
        )
        for row in segment_rows:
            country, source, revenue = row
            # Metric with labels
            body.append(f'kpi_revenue_by_segment{{country="{country}",source="{source}"}} {float(revenue):.6f}')
            # Avg 7d for same segment
            avg7d_seg = _query_one(
                "SELECT COALESCE(AVG(revenue),0) FROM mv_kpi_daily_segment WHERE country = %s AND source = %s AND day >= CURRENT_DATE - interval '7 days' AND day < CURRENT_DATE",
                (country, source)
            ) or 0
            body.append(f'kpi_revenue_avg7d_by_segment{{country="{country}",source="{source}"}} {float(avg7d_seg):.6f}')
            # Leads
            leads_seg = _query_one(
                "SELECT leads FROM mv_kpi_daily_segment WHERE country = %s AND source = %s AND day = CURRENT_DATE",
                (country, source)
            ) or 0
            body.append(f'kpi_leads_by_segment{{country="{country}",source="{source}"}} {int(leads_seg)}')
        
        payload = ("\n".join(body) + "\n").encode("utf-8")

        # Post to pushgateway: /metrics/job/<job>
        url = push_url.rstrip("/") + "/metrics/job/kpi_reports"
        try:
            req = request.Request(url, data=payload, headers={"Content-Type": "text/plain; version=0.0.4"})
            request.urlopen(req, timeout=5).read()
        except Exception:
            # best-effort
            pass

    @task(task_id="track_mlflow_metrics")
    def track_mlflow_metrics() -> None:
        """Track KPI metrics to MLflow if enabled."""
        tracking_uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not tracking_uri:
            return
        
        try:
            import mlflow
            mlflow.set_tracking_uri(tracking_uri)
            experiment_name = os.environ.get("MLFLOW_KPI_EXPERIMENT_NAME", "kpi_tracking")
            mlflow.set_experiment(experiment_name)
            
            # Collect metrics
            leads_today = _query_one("SELECT leads FROM mv_kpi_daily WHERE day = CURRENT_DATE") or 0
            revenue_today = _query_one("SELECT revenue FROM mv_kpi_daily WHERE day = CURRENT_DATE") or 0
            avg7d = _query_one("SELECT COALESCE(AVG(revenue),0) FROM mv_kpi_daily WHERE day >= CURRENT_DATE - interval '7 days' AND day < CURRENT_DATE") or 0
            pay_succ = _query_one("SELECT payments_success_rate FROM mv_kpi_daily WHERE day = CURRENT_DATE") or 0
            conversion = _query_one("SELECT conversion_pct FROM mv_kpi_daily WHERE day = CURRENT_DATE") or 0
            
            run_name = f"kpi_daily_{pendulum.now('UTC').to_date_string()}"
            with mlflow.start_run(run_name=run_name):
                # Log metrics
                mlflow.log_metric("leads_today", float(leads_today))
                mlflow.log_metric("revenue_today", float(revenue_today))
                mlflow.log_metric("revenue_avg7d", float(avg7d))
                mlflow.log_metric("payments_success_rate", float(pay_succ))
                mlflow.log_metric("conversion_pct", float(conversion))
                
                # Log params
                mlflow.log_param("dag_id", "kpi_reports")
                mlflow.log_param("report_type", "daily")
                mlflow.log_param("date", pendulum.now("UTC").to_date_string())
                
                # Tags
                mlflow.set_tag("environment", os.environ.get("ENV", "dev"))
                mlflow.set_tag("kpi_type", "daily_summary")
        except Exception:
            # best-effort, don't fail the DAG
            pass

    @task(task_id="anomaly_check")
    def anomaly_check() -> None:
        # Revenue anomalies vs last 28 days (excluding today)
        sql = (
            "WITH hist AS (\n"
            "  SELECT revenue FROM mv_kpi_daily\n"
            "  WHERE day >= CURRENT_DATE - interval '28 days' AND day < CURRENT_DATE\n"
            ")\n"
            "SELECT\n"
            "  (SELECT COALESCE(revenue,0) FROM mv_kpi_daily WHERE day = CURRENT_DATE) AS today_rev,\n"
            "  COALESCE((SELECT AVG(revenue) FROM hist),0) AS avg28,\n"
            "  COALESCE((SELECT STDDEV_POP(revenue) FROM hist),0) AS std28,\n"
            "  (SELECT COALESCE(leads,0) FROM mv_kpi_daily WHERE day = CURRENT_DATE) AS today_leads,\n"
            "  COALESCE((SELECT AVG(leads) FROM (SELECT leads FROM mv_kpi_daily WHERE day >= CURRENT_DATE - interval '28 days' AND day < CURRENT_DATE) t),0) AS avg28_leads,\n"
            "  COALESCE((SELECT STDDEV_POP(leads) FROM (SELECT leads FROM mv_kpi_daily WHERE day >= CURRENT_DATE - interval '28 days' AND day < CURRENT_DATE) t),0) AS std28_leads\n"
        )
        row = _query_rows(sql)
        if not row:
            return
        today_rev, avg28, std28, today_leads, avg28_leads, std28_leads = row[0]
        alerts: List[str] = []
        # Z-score anomalies
        if std28 and (today_rev - avg28) / (std28 or 1) <= -2.0:
            alerts.append(f"Revenue z-score negativo: {(today_rev - avg28) / (std28 or 1):.2f}")
        if std28_leads and (today_leads - avg28_leads) / (std28_leads or 1) <= -2.0:
            alerts.append(f"Leads z-score negativo: {(today_leads - avg28_leads) / (std28_leads or 1):.2f}")
        # Ratio vs promedio 7d
        avg7 = _query_one("SELECT COALESCE(AVG(revenue),0) FROM mv_kpi_daily WHERE day >= CURRENT_DATE - interval '7 days' AND day < CURRENT_DATE") or 0
        if avg7 and (today_rev / (avg7 or 1)) < 0.7:
            alerts.append(f"Revenue hoy < 70% del promedio 7d ({(today_rev/(avg7 or 1))*100:.1f}%)")
        if alerts:
            notify_slack(":rotating_light: Anomalías KPI detectadas\n- " + "\n- ".join(alerts))

    @task(task_id="upload_to_storage")
    def upload_to_storage(csv_path: str) -> str | None:
        # Try S3 first
        bucket = os.environ.get("KPI_REPORTS_S3_BUCKET")
        s3_prefix = os.environ.get("KPI_REPORTS_S3_PREFIX", "reports/daily")
        if bucket and _BOTO3_AVAILABLE:
            try:
                s3 = boto3.client("s3")
                date_str = pendulum.now("UTC").to_date_string()
                key = f"{s3_prefix}/{date_str}/kpi_daily_{date_str}.csv"
                s3.upload_file(csv_path, bucket, key)
                return f"s3://{bucket}/{key}"
            except Exception:
                pass
        
        # Try ADLS (Azure Data Lake Storage)
        adls_share = os.environ.get("KPI_REPORTS_ADLS_SHARE")
        adls_path = os.environ.get("KPI_REPORTS_ADLS_PATH", "reports/daily")
        if adls_share and _AZURE_STORAGE_AVAILABLE:
            try:
                conn_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
                if not conn_str:
                    return None
                date_str = pendulum.now("UTC").to_date_string()
                file_path = f"{adls_path}/{date_str}/kpi_daily_{date_str}.csv"
                client = ShareFileClient.from_connection_string(conn_str, share_name=adls_share, file_path=file_path)
                with open(csv_path, "rb") as fh:
                    client.upload_file(fh)
                return f"adls://{adls_share}/{file_path}"
            except Exception:
                pass
        
        return None

    path = export_csv_30d()
    storage_url = upload_to_storage(path)
    slack_summary(path if not storage_url else f"{path} (Storage: {storage_url})")
    push_prometheus_metrics()
    track_mlflow_metrics()
    anomaly_check() >> done
    return None


dag = kpi_reports()


