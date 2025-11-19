from __future__ import annotations

from datetime import timedelta
import os

import pendulum
from airflow.decorators import dag, task
from data.airflow.plugins.db import get_conn
from data.airflow.plugins.etl_notifications import notify_slack


@dag(
    dag_id="kpi_refresh_materialized",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=os.environ.get("KPI_REFRESH_SCHEDULE", "0 */4 * * *"),  # Every 4 hours, or custom via env
    catchup=False,
    default_args={
        "owner": "data-eng",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=20),
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    tags=["kpi", "maintenance"],
    description="Refresh CONCURRENTLY KPI materialized views and optionally ANALYZE",
)
def kpi_refresh_materialized() -> None:
    views = [
        "mv_revenue_24h_hourly",
        "mv_revenue_7d_daily",
        "mv_kpi_daily",
        "mv_kpi_timeseries_90d",
    ]

    @task(task_id="refresh_views")
    def refresh_views() -> None:
        analyze = os.environ.get("KPI_ANALYZE_AFTER_REFRESH", "0").lower() in {"1", "true", "yes", "on"}
        with get_conn() as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                for v in views:
                    cur.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {v};")
                    if analyze:
                        cur.execute(f"ANALYZE {v};")
        notify_slack(":arrows_counterclockwise: Refresco de vistas KPI completado")

    refresh_views()
    return None


dag = kpi_refresh_materialized()



