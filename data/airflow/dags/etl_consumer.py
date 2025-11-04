from __future__ import annotations

import logging
from datetime import timedelta
import os
import json
from urllib import request
from typing import Any, Dict
from time import perf_counter

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.exceptions import AirflowFailException

try:
    from airflow.stats import Stats  # type: ignore
except Exception:
    Stats = None  # type: ignore

try:
	from airflow.datasets import Dataset  # Airflow 2.5+
except Exception:
	Dataset = None  # type: ignore

try:
	from plugins.db import get_conn  # type: ignore
except Exception:
	get_conn = None  # type: ignore

try:
	from airflow.providers.slack.hooks.slack_webhook import SlackWebhookHook  # type: ignore
	_SLACK_PROVIDER = True
except Exception:
	_SLACK_PROVIDER = False


DATASET_URI = "postgres://etl_improved/etl_improved_events"


@dag(
	dag_id="etl_consumer",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule=[Dataset(DATASET_URI)] if Dataset else None,
	catchup=False,
	default_args={
		"owner": "data-eng",
		"retries": 1,
		"retry_delay": timedelta(minutes=2),
		"email_on_failure": False,
		"email_on_retry": False,
	},
	description="Consumer DAG triggered by dataset from etl_improved; summarizes latest metrics",
	doc_md="""
	### ETL Consumer
	
	Consumes dataset updates from upstream ETL DAGs and generates summary reports with anomaly detection.
	
	**Params:**
	- `trend_window` (int, default 7): Number of historical runs to analyze for trend detection
	- `drop_threshold_pct` (float, default 20.0): Percentage drop threshold for alerting
	
	**Features:**
	- Detects low ratio anomalies (ratio < 1.0)
	- Trend detection over configurable window
	- Slack notifications for anomalies
	- Materialized view refresh
	""",
	params={
		"trend_window": 7,
		"drop_threshold_pct": 20.0,
	},
	tags=["etl", "consumer"],
	dagrun_timeout=timedelta(minutes=10),
)
def etl_consumer() -> None:
	logger = logging.getLogger("airflow.task")

	def ensure_metrics_table_exists(cur: Any) -> None:
		"""
		Ensure metrics table exists. Uses guard clauses for early validation.
		
		Args:
			cur: Database cursor
		"""
		if not cur:
			raise AirflowFailException("Database cursor is required")
		
		cur.execute(
			"""
			CREATE SCHEMA IF NOT EXISTS public;
			CREATE TABLE IF NOT EXISTS public.etl_improved_metrics (
				id BIGSERIAL PRIMARY KEY,
				run_label TEXT NOT NULL,
				total_rows INT NOT NULL,
				expected_rows INT NOT NULL,
				ratio DOUBLE PRECISION NOT NULL,
				num_chunks INT NOT NULL,
				at TIMESTAMPTZ NOT NULL DEFAULT NOW()
			);
			"""
		)
	
	def ensure_alerts_table_exists(cur: Any) -> None:
		"""
		Ensure alerts table exists. Uses guard clauses for early validation.
		
		Args:
			cur: Database cursor
		"""
		if not cur:
			raise AirflowFailException("Database cursor is required")
		
		cur.execute(
			"""
			CREATE TABLE IF NOT EXISTS public.etl_improved_alerts (
				id BIGSERIAL PRIMARY KEY,
				kind TEXT NOT NULL,
				message TEXT NOT NULL,
				run_label TEXT,
				ratio DOUBLE PRECISION,
				avg_ratio DOUBLE PRECISION,
				threshold_pct DOUBLE PRECISION,
				at TIMESTAMPTZ NOT NULL DEFAULT NOW()
			);
			"""
		)
	
	def get_latest_metrics(cur: Any) -> Any:
		"""
		Get latest metrics from database.
		
		Args:
			cur: Database cursor
			
		Returns:
			Row with latest metrics or None if not found
		"""
		if not cur:
			raise AirflowFailException("Database cursor is required")
		
		cur.execute(
			"""
			SELECT run_label, total_rows, expected_rows, ratio, num_chunks, at
			FROM public.etl_improved_metrics
			ORDER BY at DESC
			LIMIT 1;
			"""
		)
		return cur.fetchone()
	
	def get_config_from_context() -> Dict[str, Any]:
		"""
		Load configuration from Airflow context. Implements RORO pattern.
		
		Returns:
			Dictionary with configuration parameters
		"""
		ctx = get_current_context()
		params = ctx.get("params", {})
		
		return {
			"trend_window": int(params.get("trend_window", 7)),
			"drop_threshold_pct": float(params.get("drop_threshold_pct", 20.0)),
		}
	
	def persist_low_ratio_alert(cur: Any, run_label: str, ratio: float) -> None:
		"""
		Persist low ratio alert to database.
		
		Args:
			cur: Database cursor
			run_label: Run label
			ratio: Current ratio value
		"""
		if not cur or not run_label:
			return
		
		try:
			ensure_alerts_table_exists(cur)
			cur.execute(
				"""
				INSERT INTO public.etl_improved_alerts (kind, message, run_label, ratio)
				VALUES (%s, %s, %s, %s);
				""",
				("low_ratio", f"low ratio {ratio:.3f} for run {run_label}", run_label, float(ratio)),
			)
		except Exception:
			pass  # Non-critical operation
	
	def detect_trend_drop(
		cur: Any,
		current_ratio: float,
		current_at: Any,
		window: int,
		threshold_pct: float,
		run_label: str
	) -> None:
		"""
		Detect trend drops and send alerts. Implements guard clauses.
		
		Args:
			cur: Database cursor
			current_ratio: Current ratio value
			current_at: Current timestamp
			window: Number of historical runs to analyze
			threshold_pct: Drop threshold percentage
			run_label: Run label
		"""
		if not cur or window <= 0:
			return
		
		if not current_at:
			return
		
		cur.execute(
			"""
			SELECT ratio
			FROM public.etl_improved_metrics
			WHERE at < %s
			ORDER BY at DESC
			LIMIT %s;
			""",
			(current_at, window),
		)
		rows = cur.fetchall()
		
		if not rows:
			return
		
		avg_ratio = sum(r[0] for r in rows) / float(len(rows))
		
		if avg_ratio <= 0:
			return
		
		threshold_value = avg_ratio * (1 - threshold_pct / 100.0)
		if float(current_ratio) < threshold_value:
			_send_slack(
				f":small_red_triangle_down: ratio drop {current_ratio:.3f} vs {avg_ratio:.3f} "
				f"({threshold_pct}% window {window} runs)"
			)
			
			# Persist trend alert
			try:
				ensure_alerts_table_exists(cur)
				cur.execute(
					"""
					INSERT INTO public.etl_improved_alerts (kind, message, run_label, ratio, avg_ratio, threshold_pct)
					VALUES (%s, %s, %s, %s, %s, %s);
					""",
					(
						"trend_drop",
						f"ratio {current_ratio:.3f} < avg {avg_ratio:.3f} by >{threshold_pct}%",
						run_label,
						float(current_ratio),
						float(avg_ratio),
						float(threshold_pct),
					),
				)
			except Exception:
				pass
	
	def record_metrics(component: str, duration_ms: int, success: bool = True) -> None:
		"""
		Record metrics using Stats. Implements guard clauses.
		
		Args:
			component: Component name
			duration_ms: Duration in milliseconds
			success: Whether operation succeeded
		"""
		if not Stats:
			return
		
		try:
			if success:
				Stats.incr(f"etl_consumer.{component}.success", 1)
				Stats.timing(f"etl_consumer.{component}.duration_ms", duration_ms)
			else:
				Stats.incr(f"etl_consumer.{component}.failure", 1)
		except Exception:
			pass

	@task(task_id="summarize_metrics", execution_timeout=timedelta(minutes=5))
	def summarize_metrics() -> None:
		"""Summarize latest ETL metrics and detect anomalies. Implements RPA principles."""
		start_time = perf_counter()
		
		# Guard clause: validate database connection
		if get_conn is None:
			raise AirflowFailException("plugins.db.get_conn not available - check database connection")
		
		logger.info("Starting metrics summary", extra={"component": "summarize_metrics"})
		
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					# Ensure tables exist
					ensure_metrics_table_exists(cur)
					
					# Get latest metrics
					row = get_latest_metrics(cur)
					if not row:
						logger.info("no metrics yet")
						return
					
					run_label, total_rows, expected_rows, ratio, num_chunks, at = row
					logger.info(
						"latest metrics: run=%s total=%s expected=%s ratio=%.3f chunks=%s at=%s",
						run_label,
						total_rows,
						expected_rows,
						ratio,
						num_chunks,
						str(at),
					)
					
					# Check for low ratio anomaly
					if float(ratio) < 1.0:
						_send_slack(f":warning: etl_consumer low ratio {ratio:.3f} for run {run_label}")
						persist_low_ratio_alert(cur, run_label, float(ratio))
					
					# Trend detection
					config = get_config_from_context()
					detect_trend_drop(
						cur=cur,
						current_ratio=float(ratio),
						current_at=at,
						window=config["trend_window"],
						threshold_pct=config["drop_threshold_pct"],
						run_label=run_label
					)
			
			# Record success metrics
			duration_ms = int((perf_counter() - start_time) * 1000)
			logger.info("Metrics summary completed", extra={
				"component": "summarize_metrics",
				"duration_ms": duration_ms,
			})
			
			record_metrics("summarize", duration_ms, success=True)
				
		except Exception as e:
			duration_ms = int((perf_counter() - start_time) * 1000)
			logger.error("Metrics summary failed", extra={"error": str(e), "component": "summarize_metrics"})
			record_metrics("summarize", duration_ms, success=False)
			raise AirflowFailException(f"Failed to summarize metrics: {e}") from e

	@task(task_id="refresh_mvs", execution_timeout=timedelta(minutes=2))
	def refresh_mvs() -> None:
		"""
		Refresh materialized views for ETL metrics.
		Implements guard clauses and early returns.
		"""
		# Guard clause: validate database connection
		if get_conn is None:
			raise AirflowFailException("plugins.db.get_conn not available - check database connection")
		
		logger.info("Refreshing materialized views", extra={"component": "refresh_mvs"})
		
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					if not cur:
						logger.warning("Could not get database cursor")
						return
					
					try:
						cur.execute("SELECT refresh_etl_mvs();")
						logger.info("Materialized views refreshed successfully")
						record_metrics("mv_refresh", 0, success=True)
					except Exception as e:
						logger.warning(
							"refresh_etl_mvs() function may not exist (non-critical)",
							extra={"error": str(e)}
						)
						# Don't fail if function doesn't exist - might be optional
		except Exception as e:
			logger.error("Failed to refresh materialized views", extra={"error": str(e)})
			record_metrics("mv_refresh", 0, success=False)
			# Refresh failure is not critical - log but don't fail DAG

	def _send_slack(text: str) -> None:
		"""
		Send message to Slack. Implements guard clauses and early returns.
		
		Args:
			text: Message text to send
		"""
		if not text or not text.strip():
			return
		
		try:
			if _SLACK_PROVIDER:
				conn_id = os.environ.get("SLACK_CONN_ID", "slack_default")
				if not conn_id:
					return
				SlackWebhookHook(slack_webhook_conn_id=conn_id, message=text).execute()
				return
			
			webhook = os.environ.get("SLACK_WEBHOOK")
			if not webhook:
				return
			
			payload = json.dumps({"text": text}).encode()
			req = request.Request(webhook, data=payload, headers={"Content-Type": "application/json"})
			request.urlopen(req, timeout=5)
		except Exception:
			pass  # Non-critical operation, fail silently

	summarize_metrics() >> refresh_mvs()
	return None


dag = etl_consumer()


