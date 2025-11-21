from __future__ import annotations

import logging
import traceback
from typing import Dict, Any, Optional
from contextlib import contextmanager
import time

_logger = logging.getLogger(__name__)


@contextmanager
def debug_context(
	task_name: str,
	dag_run_id: Optional[str] = None,
	chunk: Optional[str] = None,
	**extra_context: Any,
):
	"""
	Context manager for enhanced debugging with automatic error capture.
	
	Captures exceptions, logs stack traces, and records metrics.
	
	Example:
		with debug_context("transform", dag_run_id="run_123", chunk="0"):
			# do work
	"""
	start_time = time.perf_counter()
	context = {
		"task": task_name,
		"dag_run_id": dag_run_id,
		"chunk": chunk,
		**extra_context,
	}
	
	try:
		_logger.debug(f"Starting {task_name}", extra=context)
		yield
		duration_ms = int((time.perf_counter() - start_time) * 1000)
		_logger.debug(f"Completed {task_name} in {duration_ms}ms", extra={**context, "duration_ms": duration_ms})
	except Exception as e:
		duration_ms = int((time.perf_counter() - start_time) * 1000)
		tb_str = traceback.format_exc()
		_logger.error(
			f"Error in {task_name} after {duration_ms}ms: {e}",
			extra={
				**context,
				"duration_ms": duration_ms,
				"error_type": type(e).__name__,
				"error_msg": str(e),
				"traceback": tb_str,
			},
			exc_info=True,
		)
		# Record error metrics
		try:
			from airflow.stats import Stats
			Stats.incr(f"etl_example.debug.errors.{task_name}", 1)
			Stats.timing(f"etl_example.debug.duration.{task_name}.error", duration_ms)
		except Exception:
			pass
		raise


def log_payload_summary(
	logger: logging.Logger,
	payload: Dict[str, Any],
	task_name: str,
	**extra: Any,
) -> None:
	"""
	Log a structured summary of payload for debugging.
	
	Args:
		logger: Logger instance
		payload: Payload to summarize
		task_name: Task identifier
		**extra: Additional context fields
	"""
	summary = {
		"task": task_name,
		"payload_keys": list(payload.keys()),
		"rows": payload.get("rows"),
		"transformed": payload.get("transformed"),
		"has_since": "since" in payload,
		"has_until": "until" in payload,
		**extra,
	}
	logger.info(f"Payload summary for {task_name}", extra=summary)


def diagnose_task_environment(
	logger: Optional[logging.Logger] = None,
) -> Dict[str, Any]:
	"""
	Collect diagnostic information about the task execution environment.
	
	Returns dictionary with environment details for troubleshooting.
	"""
	import os
	from airflow.models import Variable
	
	diag: Dict[str, Any] = {
		"environment": {},
		"variables": {},
		"configuration": {},
	}
	
	# Environment variables
	env_vars = [
		"ENV", "AIRFLOW_ENV", "MLFLOW_TRACKING_URI",
		"ETL_POOL", "DQ_POOL", "MAX_ACTIVE_TASKS", "CHUNK_PARALLELISM",
	]
	for var in env_vars:
		diag["environment"][var] = os.getenv(var, "not_set")
	
	# Critical Airflow Variables
	critical_vars = ["DQ_MIN_ROWS", "DQ_MAX_ROWS"]
	for var in critical_vars:
		try:
			val = Variable.get(var, default_var=None)
			diag["variables"][var] = "set" if val else "unset"
		except Exception:
			diag["variables"][var] = "error"
	
	# Configuration summary
	try:
		diag["configuration"]["etl_pool"] = os.getenv("ETL_POOL", "etl_pool")
		diag["configuration"]["max_chunks"] = int(os.getenv("MAX_CHUNKS", "100"))
	except Exception as e:
		diag["configuration"]["error"] = str(e)
	
	if logger:
		logger.debug("Task environment diagnostics", extra=diag)
	
	return diag


