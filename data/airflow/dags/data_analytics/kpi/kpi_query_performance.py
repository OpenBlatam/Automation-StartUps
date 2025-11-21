from __future__ import annotations

from datetime import timedelta
import os
import logging
from time import perf_counter
from typing import Tuple, Any

import pendulum
from airflow.decorators import dag, task
from data.airflow.plugins.db import get_conn

logger = logging.getLogger("airflow.task")


def _query_with_timing(sql: str, params: Tuple[Any, ...] | None = None) -> tuple[Any, float]:
    """Execute query and return result + execution time in ms."""
    start = perf_counter()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            result = cur.fetchone()
            duration_ms = (perf_counter() - start) * 1000
            return result[0] if result else None, duration_ms


@dag(
    dag_id="kpi_query_performance",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="*/30 * * * *",  # Every 30 minutes
    catchup=False,
    default_args={
        "owner": "data-eng",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=15),
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    tags=["kpi", "performance", "monitoring"],
    description="Track query performance/latency for KPI materialized views",
)
def kpi_query_performance() -> None:
    @task(task_id="measure_query_latencies")
    def measure_query_latencies() -> dict[str, float]:
        """Measure latency for common KPI queries."""
        latencies = {}
        
        # Daily view query
        _, latency = _query_with_timing(
            "SELECT COUNT(*) FROM mv_kpi_daily WHERE day >= CURRENT_DATE - interval '7 days'"
        )
        latencies["daily_view_7d"] = latency
        
        # Segment view query
        _, latency = _query_with_timing(
            "SELECT COUNT(*) FROM mv_kpi_daily_segment WHERE day = CURRENT_DATE"
        )
        latencies["segment_view_today"] = latency
        
        # Timeseries query
        _, latency = _query_with_timing(
            "SELECT SUM(revenue) FROM mv_kpi_timeseries_90d"
        )
        latencies["timeseries_90d"] = latency
        
        # Complex aggregation
        _, latency = _query_with_timing(
            "SELECT country, SUM(revenue) FROM mv_kpi_daily_segment WHERE day >= CURRENT_DATE - interval '30 days' GROUP BY country LIMIT 10"
        )
        latencies["segment_aggregate_30d"] = latency
        
        logger.info("measured query latencies", extra=latencies)
        
        # Log slow queries (>500ms)
        slow_queries = {k: v for k, v in latencies.items() if v > 500}
        if slow_queries:
            logger.warning("slow queries detected", extra=slow_queries)
        
        return latencies

    measure_query_latencies()
    return None


dag = kpi_query_performance()


