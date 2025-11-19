from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Dict

import pendulum
from airflow.decorators import dag, task
from data.airflow.plugins.db import get_conn


@dag(
	dag_id="financial_reports",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule="0 1 * * *",  # daily at 01:00 UTC
	catchup=False,
	default_args={
		"owner": "finance",
		"retries": 1,
		"retry_delay": timedelta(minutes=2),
		"email_on_failure": False,
		"email_on_retry": False,
	},
	description="Refresh materialized views for financial KPIs",
	tags=["finance", "kpi", "reports"],
)
def financial_reports() -> None:
	logger = logging.getLogger("airflow.task")

	@task(task_id="refresh_materialized_views")
	def refresh_materialized_views() -> None:
		with get_conn() as conn:
			with conn.cursor() as cur:
				# Create materialized view for revenue daily if not exists
				cur.execute(
					"""
					CREATE MATERIALIZED VIEW IF NOT EXISTS mv_revenue_daily AS
					SELECT 
						created_at::date AS period,
						COUNT(*)::int AS invoice_count,
						COALESCE(SUM(total), 0)::numeric AS revenue,
						COALESCE(SUM(taxes), 0)::numeric AS taxes,
						COALESCE(SUM(subtotal), 0)::numeric AS subtotal
					FROM invoices
					WHERE created_at >= CURRENT_DATE - INTERVAL '90 days'
					GROUP BY period
					ORDER BY period DESC
					"""
				)
				# Create materialized view for AR aging if not exists
				cur.execute(
					"""
					CREATE MATERIALIZED VIEW IF NOT EXISTS mv_ar_aging AS
					SELECT 
						CASE 
							WHEN due_date >= CURRENT_DATE THEN 'current'
							WHEN due_date >= CURRENT_DATE - INTERVAL '30 days' THEN '1-30'
							WHEN due_date >= CURRENT_DATE - INTERVAL '60 days' THEN '31-60'
							WHEN due_date >= CURRENT_DATE - INTERVAL '90 days' THEN '61-90'
							ELSE '90+'
						END AS bucket,
						COUNT(*)::int AS invoice_count,
						COALESCE(SUM(total), 0)::numeric AS total_amount
					FROM invoices
					WHERE status = 'issued'
					AND due_date IS NOT NULL
					GROUP BY bucket
					"""
				)
				# Create materialized view for monthly revenue if not exists
				cur.execute(
					"""
					CREATE MATERIALIZED VIEW IF NOT EXISTS mv_revenue_monthly AS
					SELECT 
						DATE_TRUNC('month', created_at)::date AS period,
						COUNT(*)::int AS invoice_count,
						COALESCE(SUM(total), 0)::numeric AS revenue,
						COALESCE(SUM(taxes), 0)::numeric AS taxes,
						COALESCE(SUM(subtotal), 0)::numeric AS subtotal
					FROM invoices
					WHERE created_at >= CURRENT_DATE - INTERVAL '12 months'
					GROUP BY period
					ORDER BY period DESC
					"""
				)
				# Refresh materialized views
				cur.execute("REFRESH MATERIALIZED VIEW mv_revenue_daily")
				cur.execute("REFRESH MATERIALIZED VIEW mv_ar_aging")
				cur.execute("REFRESH MATERIALIZED VIEW mv_revenue_monthly")
				conn.commit()
		logger.info("materialized views refreshed")

	refresh_materialized_views()
	return None


dag = financial_reports()


