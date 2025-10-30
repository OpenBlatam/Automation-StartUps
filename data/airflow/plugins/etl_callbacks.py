from __future__ import annotations

import logging
from typing import Dict, Any

from airflow.stats import Stats
from .etl_notifications import notify_slack, notify_email


def sla_miss_callback(dag, task_list, blocking_task_list, slas, session=None, **kwargs) -> None:  # type: ignore[no-untyped-def]
	logger = logging.getLogger("airflow.task")
	logger.warning("SLA miss detected", extra={
		"tasks": task_list,
		"blocking": blocking_task_list,
	})
	try:
		count = len(task_list) if task_list else 1
		Stats.incr("etl_example.sla_miss", count)
	except Exception:
		pass
	# best-effort notifications
	try:
		notify_slack(":warning: SLA miss in etl_example")
	except Exception:
		pass


def on_task_failure(context: Dict[str, Any]) -> None:
	logger = logging.getLogger("airflow.task")
	task_id = context.get("task_instance").task_id if context.get("task_instance") else "unknown"
	logger.error("task failed: %s", task_id)
	try:
		Stats.incr("etl_example.task_failure")
	except Exception:
		pass
	# best-effort notifications
	try:
		notify_slack(f":x: etl_example task failed: {task_id}")
		notify_email(
			subject=f"etl_example task failed: {task_id}",
			html_content=f"<b>Task failed</b>: {task_id}",
			to=None,  # derive from ALERT_EMAILS if enabled
		)
	except Exception:
		pass
