from __future__ import annotations

from datetime import timedelta
import os
from typing import Tuple, Any, List

import pendulum
from airflow.decorators import dag, task
from data.airflow.plugins.db import get_conn
from data.airflow.plugins.etl_notifications import notify_slack


def _one(sql: str, params: Tuple[Any, ...] | None = None) -> Any:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            r = cur.fetchone()
            return r[0] if r else None


def _rows(sql: str, params: Tuple[Any, ...] | None = None) -> List[Tuple[Any, ...]]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return list(cur.fetchall())


@dag(
    dag_id="kpi_dq_health_checks",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="0 */6 * * *",  # Every 6 hours
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
    tags=["kpi", "data-quality", "health"],
    description="Data quality health checks for KPI materialized views",
)
def kpi_dq_health_checks() -> None:
    @task(task_id="check_view_freshness")
    def check_view_freshness() -> List[str]:
        issues: List[str] = []
        # Check if today's data exists in mv_kpi_daily
        today_count = _one("SELECT COUNT(*) FROM mv_kpi_daily WHERE day = CURRENT_DATE")
        if today_count == 0:
            issues.append("No data for today in mv_kpi_daily")
        
        # Check max day (should be today or yesterday)
        max_day = _one("SELECT MAX(day) FROM mv_kpi_daily")
        if max_day:
            days_behind = (pendulum.today() - pendulum.instance(max_day)).days
            if days_behind > 1:
                issues.append(f"mv_kpi_daily is {days_behind} days behind (max day: {max_day})")
        
        return issues

    @task(task_id="check_null_rates")
    def check_null_rates() -> List[str]:
        issues: List[str] = []
        # Check for high null rates in recent data
        null_revenue = _one(
            "SELECT COUNT(*) FROM mv_kpi_daily WHERE revenue IS NULL AND day >= CURRENT_DATE - interval '7 days'"
        ) or 0
        total_recent = _one(
            "SELECT COUNT(*) FROM mv_kpi_daily WHERE day >= CURRENT_DATE - interval '7 days'"
        ) or 1
        if null_revenue > total_recent * 0.1:  # >10% nulls
            issues.append(f"High null revenue rate: {null_revenue}/{total_recent} in last 7 days")
        
        return issues

    @task(task_id="check_data_consistency")
    def check_data_consistency() -> List[str]:
        issues: List[str] = []
        # Check if conversion_pct is reasonable (0-100)
        invalid_conversion = _one(
            "SELECT COUNT(*) FROM mv_kpi_daily WHERE conversion_pct < 0 OR conversion_pct > 100"
        ) or 0
        if invalid_conversion > 0:
            issues.append(f"Invalid conversion_pct values found: {invalid_conversion}")
        
        # Check if payments_success_rate is reasonable
        invalid_success = _one(
            "SELECT COUNT(*) FROM mv_kpi_daily WHERE payments_success_rate < 0 OR payments_success_rate > 100"
        ) or 0
        if invalid_success > 0:
            issues.append(f"Invalid payments_success_rate values found: {invalid_success}")
        
        return issues

    @task(task_id="check_view_sizes")
    def check_view_sizes() -> List[str]:
        issues: List[str] = []
        # Check row counts (should be reasonable)
        daily_count = _one("SELECT COUNT(*) FROM mv_kpi_daily")
        if daily_count == 0:
            issues.append("mv_kpi_daily is empty")
        elif daily_count < 30:
            issues.append(f"mv_kpi_daily has only {daily_count} rows (expected >= 30)")
        
        segment_count = _one("SELECT COUNT(*) FROM mv_kpi_daily_segment")
        if segment_count == 0:
            issues.append("mv_kpi_daily_segment is empty")
        
        return issues

    @task(task_id="aggregate_and_notify")
    def aggregate_and_notify(
        freshness_issues: List[str],
        null_issues: List[str],
        consistency_issues: List[str],
        size_issues: List[str],
    ) -> None:
        all_issues = freshness_issues + null_issues + consistency_issues + size_issues
        if all_issues:
            text = ":warning: Data Quality Issues Detected\n- " + "\n- ".join(all_issues)
            notify_slack(text)
        else:
            notify_slack(":white_check_mark: All KPI data quality checks passed")

    freshness = check_view_freshness()
    nulls = check_null_rates()
    consistency = check_data_consistency()
    sizes = check_view_sizes()
    aggregate_and_notify(freshness, nulls, consistency, sizes)
    return None


dag = kpi_dq_health_checks()


