from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Dict

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.stats import Stats

try:
	from airflow.datasets import Dataset  # Airflow 2.5+
except Exception:
	Dataset = None  # type: ignore

try:
	from plugins.db import get_conn  # type: ignore
except Exception:
	get_conn = None  # type: ignore


# This DAG is triggered by the Dataset produced by etl_improved
ETL_DATASET_URI = "postgres://etl_improved/etl_improved_events"


@dag(
	dag_id="etl_downstream_example",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule=[Dataset(ETL_DATASET_URI)] if Dataset else None,  # Triggered by ETL dataset
	catchup=False,
	default_args={
		"owner": "data-eng",
		"retries": 1,
		"retry_delay": timedelta(minutes=2),
		"depends_on_past": False,
	},
	dagrun_timeout=timedelta(minutes=20),
	description="Example downstream DAG that processes ETL data (analytics, reports, etc.)",
	params={
		"analysis_type": "daily_summary",
		"top_n": 10,
	},
	tags=["etl", "downstream", "example"],
)
def etl_downstream_example() -> None:
	"""
	Example downstream DAG that consumes ETL data.
	
	This demonstrates how to:
	1. Trigger on ETL Dataset completion
	2. Read from ETL tables
	3. Perform analytics/aggregations
	4. Generate reports or trigger other processes
	"""
	logger = logging.getLogger("airflow.task")

	@task(task_id="read_latest_metrics", execution_timeout=timedelta(minutes=5))
	def read_latest_metrics() -> Dict[str, Any]:
		"""Read latest ETL metrics to understand what was processed."""
		if get_conn is None:
			raise RuntimeError("plugins.db.get_conn not available")
		
		with get_conn() as conn:
			with conn.cursor() as cur:
				cur.execute(
					"""
					SELECT run_label, total_rows, expected_rows, ratio, at
					FROM public.etl_improved_metrics
					ORDER BY at DESC
					LIMIT 1;
					"""
				)
				row = cur.fetchone()
				if not row:
					logger.warning("no metrics found")
					return {}
				run_label, total_rows, expected_rows, ratio, at = row
				metrics = {
					"run_label": run_label,
					"total_rows": total_rows,
					"expected_rows": expected_rows,
					"ratio": float(ratio),
					"at": str(at),
				}
				logger.info("latest metrics: %s", metrics)
				Stats.incr("etl_downstream.metrics_read")
				return metrics

	@task(task_id="analyze_events", execution_timeout=timedelta(minutes=10))
	def analyze_events(metrics: Dict[str, Any]) -> Dict[str, Any]:
		"""
		Perform analysis on ETL events.
		
		This is a placeholder for:
		- Aggregations
		- Statistical analysis
		- Pattern detection
		- Data quality checks
		"""
		ctx = get_current_context()
		analysis_type = str(ctx["params"].get("analysis_type", "daily_summary"))
		top_n = int(ctx["params"].get("top_n", 10))
		
		if get_conn is None:
			raise RuntimeError("plugins.db.get_conn not available")
		
		logger.info("running analysis: %s (top_n=%s)", analysis_type, top_n)
		
		# Example: Count events by date
		with get_conn() as conn:
			with conn.cursor() as cur:
				# Check if table exists
				cur.execute(
					"""
					SELECT EXISTS (
						SELECT FROM information_schema.tables 
						WHERE table_schema = 'public' AND table_name = 'etl_improved_events'
					);
					"""
				)
				if not cur.fetchone()[0]:
					logger.warning("etl_improved_events table not found, skipping analysis")
					return {"analysis": "skipped", "reason": "table_not_found"}
				
				# Example analysis: events by day
				cur.execute(
					"""
					SELECT DATE(event_time) AS day, COUNT(*) AS count
					FROM public.etl_improved_events
					WHERE event_time >= NOW() - INTERVAL '7 days'
					GROUP BY DATE(event_time)
					ORDER BY day DESC
					LIMIT %s;
					""",
					(top_n,),
				)
				rows = cur.fetchall()
				analysis = {
					"type": analysis_type,
					"events_by_day": [{"day": str(r[0]), "count": r[1]} for r in rows],
					"total_days": len(rows),
				}
				
				logger.info("analysis complete: %s days analyzed", len(rows))
				Stats.incr("etl_downstream.analysis_complete", 1, tags={"type": analysis_type})
				return analysis

	@task(task_id="generate_report", execution_timeout=timedelta(minutes=5))
	def generate_report(metrics: Dict[str, Any], analysis: Dict[str, Any]) -> None:
		"""
		Generate a report based on metrics and analysis.
		
		This could:
		- Write to a reporting table
		- Send via email/Slack
		- Trigger another process
		- Update a dashboard
		"""
		logger.info("generating report from metrics: %s", metrics.get("run_label"))
		logger.info("analysis summary: %s days", analysis.get("total_days", 0))
		
		# Example: Log summary (in production, this could write to a report table)
		report = {
			"run_label": metrics.get("run_label"),
			"processed_rows": metrics.get("total_rows", 0),
			"ratio": metrics.get("ratio", 0),
			"analysis_days": analysis.get("total_days", 0),
			"generated_at": str(pendulum.now()),
		}
		
		logger.info("report: %s", report)
		Stats.incr("etl_downstream.report_generated")
		
		# In a real scenario, you might:
		# - Write to a reports table
		# - Send via Slack/Email
		# - Trigger a notification workflow
		# - Update a BI tool

	@task(task_id="cleanup_temp_data", execution_timeout=timedelta(minutes=3))
	def cleanup_temp_data() -> None:
		"""Optional cleanup of temporary data created during analysis."""
		logger.info("cleanup completed (placeholder)")
		Stats.incr("etl_downstream.cleanup_complete")

	# Pipeline: read metrics → analyze → generate report → cleanup
	metrics = read_latest_metrics()
	analysis = analyze_events(metrics)
	generate_report(metrics, analysis) >> cleanup_temp_data()
	
	return None


dag = etl_downstream_example()


