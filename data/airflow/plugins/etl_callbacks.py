from __future__ import annotations

import logging
from typing import Dict, Any
from airflow.exceptions import AirflowFailException

try:
	from airflow.stats import Stats
except Exception:
	Stats = None

_logger = logging.getLogger(__name__)


def sla_miss_callback(context: Dict[str, Any]) -> None:
	"""
	Callback for SLA misses with metrics and optional notifications.
	
	Records SLA miss metrics and sends notifications via Slack/Sentry.
	"""
	dag_id = context.get("dag").dag_id if context.get("dag") else "unknown"
	task_id = context.get("task_instance").task_id if context.get("task_instance") else "unknown"
	
	_logger.warning(
		"SLA miss detected",
		extra={
			"dag_id": dag_id,
			"task_id": task_id,
			"execution_date": str(context.get("execution_date")),
		}
	)
	
	# Record metrics
	if Stats:
		try:
			Stats.incr(f"{dag_id}.sla_miss", 1, tags={"task_id": task_id})
		except Exception:
			pass
	
	# Send notification
	try:
		from .etl_notifications import notify_slack
		notify_slack(
			f":warning: SLA miss: {dag_id}.{task_id}",
			extra_context={"execution_date": str(context.get("execution_date"))}
		)
	except Exception:
		pass
	
	# Send to Sentry if available
	try:
		import sentry_sdk
		sentry_sdk.capture_message(
			f"SLA miss: {dag_id}.{task_id}",
			level="warning",
			extra=context
		)
	except Exception:
		pass


def on_task_failure(context: Dict[str, Any]) -> None:
	"""
	Callback for task failures with detailed error logging and metrics.
	
	Records failure metrics, logs error details, and sends notifications.
	"""
	dag_id = context.get("dag").dag_id if context.get("dag") else "unknown"
	task_id = context.get("task_instance").task_id if context.get("task_instance") else "unknown"
	exception = context.get("exception")
	
	_logger.error(
		"Task failure",
		extra={
			"dag_id": dag_id,
			"task_id": task_id,
			"execution_date": str(context.get("execution_date")),
			"exception": str(exception) if exception else None,
		},
		exc_info=exception,
	)
	
	# Record metrics
	if Stats:
		try:
			Stats.incr(f"{dag_id}.task_failure", 1, tags={"task_id": task_id})
		except Exception:
			pass
	
	# Send notification
	try:
		from .etl_notifications import notify_slack
		error_msg = str(exception) if exception else "Unknown error"
		notify_slack(
			f":x: Task failed: {dag_id}.{task_id} - {error_msg[:200]}",
			extra_context={
				"execution_date": str(context.get("execution_date")),
				"exception_type": type(exception).__name__ if exception else None,
			}
		)
	except Exception:
		pass
	
	# Send to Sentry if available
	try:
		import sentry_sdk
		sentry_sdk.capture_exception(
			exception or Exception("Task failed"),
			extra=context
		)
	except Exception:
		pass


def on_task_retry(context: Dict[str, Any]) -> None:
	"""
	Callback for task retries with metrics and optional alerts.
	
	Records retry metrics and sends alerts if retry count exceeds threshold.
	"""
	dag_id = context.get("dag").dag_id if context.get("dag") else "unknown"
	task_id = context.get("task_instance").task_id if context.get("task_instance") else "unknown"
	try_count = context.get("task_instance").try_number if context.get("task_instance") else 0
	
	_logger.warning(
		"Task retry",
		extra={
			"dag_id": dag_id,
			"task_id": task_id,
			"try_number": try_count,
			"execution_date": str(context.get("execution_date")),
		}
	)
	
	# Record metrics
	if Stats:
		try:
			Stats.incr(f"{dag_id}.task_retry", 1, tags={"task_id": task_id, "try_number": str(try_count)})
		except Exception:
			pass
	
	# Alert if too many retries
	if try_count >= 3:
		try:
			from .etl_notifications import notify_slack
			notify_slack(
				f":warning: High retry count: {dag_id}.{task_id} (try {try_count})",
				extra_context={"execution_date": str(context.get("execution_date"))}
			)
		except Exception:
			pass
