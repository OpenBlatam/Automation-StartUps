from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Dict

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.stats import Stats
from airflow.exceptions import AirflowFailException

try:
	from plugins.db import get_conn  # type: ignore
except Exception:
	get_conn = None  # type: ignore

try:
	from psycopg2.sql import SQL, Identifier
except Exception:
	# Fallback: use string formatting (less safe but works)
	SQL = None
	Identifier = None

try:
	from data.airflow.plugins.etl_logging import get_task_logger, log_with_context
	from data.airflow.plugins.etl_callbacks import on_task_failure, sla_miss_callback
	from data.airflow.plugins.etl_notifications import notify_slack
except Exception:
	get_task_logger = logging.getLogger
	log_with_context = None
	on_task_failure = None
	sla_miss_callback = None
	notify_slack = lambda msg: None

# Default retention periods (in days)
DEFAULT_RETENTION_METRICS = 90
DEFAULT_RETENTION_AUDIT = 90
DEFAULT_RETENTION_ALERTS = 180
DEFAULT_RETENTION_EVENTS = 365

# Validation limits
MIN_RETENTION_DAYS = 7  # Minimum retention (safety limit)
MAX_RETENTION_DAYS = 1095  # Maximum retention (~3 years)

# Task timeouts (in minutes)
CLEAN_TIMEOUT_MIN = 10
EVENTS_CLEAN_TIMEOUT_MIN = 15
MV_REFRESH_TIMEOUT_MIN = 5
VACUUM_TIMEOUT_MIN = 10

# Allowed table names for VACUUM (whitelist for security)
ALLOWED_TABLES = {
	"etl_improved_metrics",
	"etl_improved_audit",
	"etl_improved_alerts",
	"etl_improved_events",
}


def _validate_retention_days(days: int, param_name: str) -> int:
	"""Validate retention days parameter is within reasonable bounds."""
	if not isinstance(days, (int, float)) or days < MIN_RETENTION_DAYS:
		raise AirflowFailException(
			f"Invalid {param_name}: {days} (minimum: {MIN_RETENTION_DAYS} days)"
		)
	if days > MAX_RETENTION_DAYS:
		raise AirflowFailException(
			f"Invalid {param_name}: {days} (maximum: {MAX_RETENTION_DAYS} days)"
		)
	return int(days)


@dag(
	dag_id="etl_maintenance",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule="@weekly",  # Run weekly to clean old data
	catchup=False,
	default_args={
		"owner": "data-eng",
		"retries": 1,
		"retry_delay": timedelta(minutes=5),
		"depends_on_past": False,
		"email_on_failure": False,
		"email_on_retry": False,
	},
	dagrun_timeout=timedelta(minutes=30),
	max_active_runs=1,
	description="Maintenance DAG for cleaning old ETL data and refreshing views",
	params={
		"retention_days_metrics": DEFAULT_RETENTION_METRICS,
		"retention_days_audit": DEFAULT_RETENTION_AUDIT,
		"retention_days_alerts": DEFAULT_RETENTION_ALERTS,
		"retention_days_events": DEFAULT_RETENTION_EVENTS,
	},
	tags=["etl", "maintenance"],
	sla_miss_callback=sla_miss_callback,
	on_success_callback=lambda context: notify_slack(":white_check_mark: etl_maintenance DAG succeeded"),
	on_failure_callback=lambda context: notify_slack(":x: etl_maintenance DAG failed"),
)
def etl_maintenance() -> None:
	logger = get_task_logger("etl_maintenance")

	@task(
		task_id="clean_old_metrics",
		execution_timeout=timedelta(minutes=CLEAN_TIMEOUT_MIN),
		on_failure_callback=on_task_failure,
		doc_md="Clean old metrics records based on retention policy",
	)
	def clean_old_metrics() -> int:
		"""Clean old metrics records based on retention policy."""
		ctx = get_current_context()
		retention_days = _validate_retention_days(
			int(ctx["params"].get("retention_days_metrics", DEFAULT_RETENTION_METRICS)),
			"retention_days_metrics"
		)
		cutoff_date = pendulum.now("UTC").subtract(days=retention_days)
		
		if get_conn is None:
			logger.error("Database connection not available")
			raise RuntimeError("plugins.db.get_conn not available")
		
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					# Get count before deletion for logging
					cur.execute(
						"""
						SELECT COUNT(*) FROM public.etl_improved_metrics
						WHERE at < NOW() - INTERVAL '%s days';
						""",
						(retention_days,),
					)
					count_before = cur.fetchone()[0]
					
					cur.execute(
						"""
						DELETE FROM public.etl_improved_metrics
						WHERE at < NOW() - INTERVAL '%s days';
						""",
						(retention_days,),
					)
					deleted = cur.rowcount
					conn.commit()
					
					logger.info(
						"Cleaned old metrics records",
						extra={
							"deleted": deleted,
							"count_before": count_before,
							"retention_days": retention_days,
							"cutoff_date": cutoff_date.isoformat(),
						}
					)
					
					try:
						Stats.incr("etl_maintenance.metrics_deleted", deleted)
						Stats.gauge("etl_maintenance.metrics_retention_days", retention_days)
					except Exception as e:
						logger.debug("Stats recording failed: %s", e)
					
					return deleted
		except Exception as e:
			logger.error("Failed to clean old metrics", extra={"error": str(e), "retention_days": retention_days})
			raise

	@task(
		task_id="clean_old_audit",
		execution_timeout=timedelta(minutes=CLEAN_TIMEOUT_MIN),
		on_failure_callback=on_task_failure,
		doc_md="Clean old audit records based on retention policy",
	)
	def clean_old_audit() -> int:
		"""Clean old audit records based on retention policy."""
		ctx = get_current_context()
		retention_days = _validate_retention_days(
			int(ctx["params"].get("retention_days_audit", DEFAULT_RETENTION_AUDIT)),
			"retention_days_audit"
		)
		cutoff_date = pendulum.now("UTC").subtract(days=retention_days)
		
		if get_conn is None:
			logger.error("Database connection not available")
			raise RuntimeError("plugins.db.get_conn not available")
		
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					# Get count before deletion for logging
					cur.execute(
						"""
						SELECT COUNT(*) FROM public.etl_improved_audit
						WHERE at < NOW() - INTERVAL '%s days';
						""",
						(retention_days,),
					)
					count_before = cur.fetchone()[0]
					
					cur.execute(
						"""
						DELETE FROM public.etl_improved_audit
						WHERE at < NOW() - INTERVAL '%s days';
						""",
						(retention_days,),
					)
					deleted = cur.rowcount
					conn.commit()
					
					logger.info(
						"Cleaned old audit records",
						extra={
							"deleted": deleted,
							"count_before": count_before,
							"retention_days": retention_days,
							"cutoff_date": cutoff_date.isoformat(),
						}
					)
					
					try:
						Stats.incr("etl_maintenance.audit_deleted", deleted)
						Stats.gauge("etl_maintenance.audit_retention_days", retention_days)
					except Exception as e:
						logger.debug("Stats recording failed: %s", e)
					
					return deleted
		except Exception as e:
			logger.error("Failed to clean old audit records", extra={"error": str(e), "retention_days": retention_days})
			raise

	@task(
		task_id="clean_old_alerts",
		execution_timeout=timedelta(minutes=CLEAN_TIMEOUT_MIN),
		on_failure_callback=on_task_failure,
		doc_md="Clean old alert records based on retention policy",
	)
	def clean_old_alerts() -> int:
		"""Clean old alert records based on retention policy."""
		ctx = get_current_context()
		retention_days = _validate_retention_days(
			int(ctx["params"].get("retention_days_alerts", DEFAULT_RETENTION_ALERTS)),
			"retention_days_alerts"
		)
		cutoff_date = pendulum.now("UTC").subtract(days=retention_days)
		
		if get_conn is None:
			logger.error("Database connection not available")
			raise RuntimeError("plugins.db.get_conn not available")
		
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					# Get count before deletion for logging
					cur.execute(
						"""
						SELECT COUNT(*) FROM public.etl_improved_alerts
						WHERE at < NOW() - INTERVAL '%s days';
						""",
						(retention_days,),
					)
					count_before = cur.fetchone()[0]
					
					cur.execute(
						"""
						DELETE FROM public.etl_improved_alerts
						WHERE at < NOW() - INTERVAL '%s days';
						""",
						(retention_days,),
					)
					deleted = cur.rowcount
					conn.commit()
					
					logger.info(
						"Cleaned old alert records",
						extra={
							"deleted": deleted,
							"count_before": count_before,
							"retention_days": retention_days,
							"cutoff_date": cutoff_date.isoformat(),
						}
					)
					
					try:
						Stats.incr("etl_maintenance.alerts_deleted", deleted)
						Stats.gauge("etl_maintenance.alerts_retention_days", retention_days)
					except Exception as e:
						logger.debug("Stats recording failed: %s", e)
					
					return deleted
		except Exception as e:
			logger.error("Failed to clean old alert records", extra={"error": str(e), "retention_days": retention_days})
			raise

	@task(
		task_id="clean_old_events",
		execution_timeout=timedelta(minutes=EVENTS_CLEAN_TIMEOUT_MIN),
		on_failure_callback=on_task_failure,
		doc_md="Clean old event records based on retention policy",
	)
	def clean_old_events() -> int:
		"""Clean old event records based on retention policy."""
		ctx = get_current_context()
		retention_days = _validate_retention_days(
			int(ctx["params"].get("retention_days_events", DEFAULT_RETENTION_EVENTS)),
			"retention_days_events"
		)
		cutoff_date = pendulum.now("UTC").subtract(days=retention_days)
		
		if get_conn is None:
			logger.error("Database connection not available")
			raise RuntimeError("plugins.db.get_conn not available")
		
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					# Check if table exists first
					cur.execute(
						"""
						SELECT EXISTS (
							SELECT FROM information_schema.tables 
							WHERE table_schema = 'public' AND table_name = 'etl_improved_events'
						);
						"""
					)
					exists = cur.fetchone()[0]
					if not exists:
						logger.info(
							"Events table does not exist; skipping cleanup",
							extra={"table": "etl_improved_events"}
						)
						return 0
					
					# Get count before deletion for logging
					cur.execute(
						"""
						SELECT COUNT(*) FROM public.etl_improved_events
						WHERE event_time < NOW() - INTERVAL '%s days';
						""",
						(retention_days,),
					)
					count_before = cur.fetchone()[0]
					
					cur.execute(
						"""
						DELETE FROM public.etl_improved_events
						WHERE event_time < NOW() - INTERVAL '%s days';
						""",
						(retention_days,),
					)
					deleted = cur.rowcount
					conn.commit()
					
					logger.info(
						"Cleaned old event records",
						extra={
							"deleted": deleted,
							"count_before": count_before,
							"retention_days": retention_days,
							"cutoff_date": cutoff_date.isoformat(),
							"table": "etl_improved_events",
						}
					)
					
					try:
						Stats.incr("etl_maintenance.events_deleted", deleted)
						Stats.gauge("etl_maintenance.events_retention_days", retention_days)
					except Exception as e:
						logger.debug("Stats recording failed: %s", e)
					
					return deleted
		except Exception as e:
			logger.error("Failed to clean old event records", extra={"error": str(e), "retention_days": retention_days})
			raise

	@task(
		task_id="refresh_mvs",
		execution_timeout=timedelta(minutes=MV_REFRESH_TIMEOUT_MIN),
		on_failure_callback=on_task_failure,
		doc_md="Refresh materialized views after data cleanup",
	)
	def refresh_mvs() -> None:
		"""Refresh materialized views after data cleanup."""
		if get_conn is None:
			logger.error("Database connection not available")
			raise RuntimeError("plugins.db.get_conn not available")
		
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					try:
						start = pendulum.now("UTC")
						cur.execute("SELECT refresh_etl_mvs();")
						result = cur.fetchone()[0] if cur.rowcount > 0 else None
						duration = (pendulum.now("UTC") - start).total_seconds()
						conn.commit()
						
						logger.info(
							"Materialized views refreshed successfully",
							extra={
								"function": "refresh_etl_mvs",
								"duration_seconds": duration,
								"result": result,
							}
						)
						
						try:
							Stats.incr("etl_maintenance.mvs_refreshed")
							Stats.timing("etl_maintenance.mvs_refresh_duration_sec", int(duration))
						except Exception as e:
							logger.debug("Stats recording failed: %s", e)
					except Exception as e:
						logger.error(
							"Failed to refresh materialized views",
							extra={"function": "refresh_etl_mvs", "error": str(e)}
						)
						raise
		except Exception as e:
			logger.error("Database operation failed during MV refresh", extra={"error": str(e)})
			raise

	@task(
		task_id="vacuum_analyze",
		execution_timeout=timedelta(minutes=VACUUM_TIMEOUT_MIN),
		on_failure_callback=on_task_failure,
		doc_md="Run VACUUM ANALYZE on cleaned tables to reclaim space and update statistics",
	)
	def vacuum_analyze() -> None:
		"""Run VACUUM ANALYZE on cleaned tables to reclaim space and update statistics."""
		if get_conn is None:
			logger.error("Database connection not available")
			raise RuntimeError("plugins.db.get_conn not available")
		
		tables = list(ALLOWED_TABLES)  # Use whitelist for security
		
		vacuumed_count = 0
		skipped_count = 0
		failed_count = 0
		
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					for table in tables:
						try:
							# Check if table exists
							cur.execute(
								"""
								SELECT EXISTS (
									SELECT FROM information_schema.tables 
									WHERE table_schema = 'public' AND table_name = %s
								);
								""",
								(table,),
							)
							exists = cur.fetchone()[0]
							
							if not exists:
								logger.debug(
									"Table does not exist; skipping vacuum",
									extra={"table": table}
								)
								skipped_count += 1
								continue
							
							# Run VACUUM ANALYZE using SQL identifier quoting (safer than f-string)
							start = pendulum.now("UTC")
							if SQL and Identifier:
								# Safe: Use psycopg2 SQL builder
								cur.execute(SQL("VACUUM ANALYZE public.{}").format(Identifier(table)))
							else:
								# Fallback: Use format with validation (table already in whitelist)
								cur.execute("VACUUM ANALYZE public.{}".format(table.replace('"', '""')))
							duration = (pendulum.now("UTC") - start).total_seconds()
							conn.commit()
							
							logger.info(
								"Vacuumed and analyzed table",
								extra={
									"table": table,
									"duration_seconds": duration,
								}
							)
							vacuumed_count += 1
							
						except Exception as e:
							logger.warning(
								"Vacuum operation failed for table",
								extra={"table": table, "error": str(e)}
							)
							failed_count += 1
			
			logger.info(
				"Vacuum analyze operation completed",
				extra={
					"total_tables": len(tables),
					"vacuumed": vacuumed_count,
					"skipped": skipped_count,
					"failed": failed_count,
				}
			)
			
			try:
				Stats.incr("etl_maintenance.vacuum_completed")
				Stats.gauge("etl_maintenance.vacuum_tables_count", vacuumed_count)
				Stats.gauge("etl_maintenance.vacuum_failed_count", failed_count)
			except Exception as e:
				logger.debug("Stats recording failed: %s", e)
				
		except Exception as e:
			logger.error("Database operation failed during vacuum", extra={"error": str(e)})
			raise

	# Cleanup tasks run in parallel, then refresh and vacuum
	metrics_deleted = clean_old_metrics()
	audit_deleted = clean_old_audit()
	alerts_deleted = clean_old_alerts()
	events_deleted = clean_old_events()
	
	# Refresh views after cleanup, then vacuum
	refresh_mvs() << [metrics_deleted, audit_deleted, alerts_deleted]
	vacuum_analyze() << refresh_mvs()
	
	return None


dag = etl_maintenance()

