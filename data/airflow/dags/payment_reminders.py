from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Dict, List

import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable


def _get_env_var(name: str, default: str | None = None) -> str:
	return str(Variable.get(name, default_var=default))


def _parse_days(spec: str) -> List[int]:
	vals: List[int] = []
	for p in (spec or "").split(","):
		p = p.strip()
		if not p:
			continue
		try:
			vals.append(int(p))
		except Exception:
			continue
	return vals


@dag(
	dag_id="payment_reminders",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule="0 9 * * *",  # daily at 09:00 UTC
	catchup=False,
	default_args={
		"owner": "finance",
		"retries": 1,
		"retry_delay": timedelta(minutes=2),
		"email_on_failure": False,
		"email_on_retry": False,
	},
	description="Send dunning reminders for overdue and upcoming invoices",
	tags=["finance", "dunning"],
)
def payment_reminders() -> None:
	logger = logging.getLogger("airflow.task")

	@task(task_id="find_due_invoices")
	def find_due_invoices() -> Dict[str, Any]:
		reminder_days = _get_env_var("REMINDER_DAYS", default="-3,1,7,14")
		days = _parse_days(reminder_days)
		logger.info("scanning invoices for reminders", extra={"days": days})
		return {"candidates": [], "days": days}

	@task(task_id="send_notifications")
	def send_notifications(payload: Dict[str, Any]) -> Dict[str, Any]:
		smtp_url = _get_env_var("SMTP_URL", default="")
		wh_token = _get_env_var("WHATSAPP_PROVIDER_TOKEN", default="")
		logger.info(
			"sending notifications",
			extra={"smtp_url": bool(smtp_url), "whatsapp": bool(wh_token)},
		)
		payload["sent"] = True
		return payload

	@task(task_id="log_metrics")
	def log_metrics(payload: Dict[str, Any]) -> None:
		logger.info("reminders sent", extra={"count": len(payload.get("candidates", []))})
		return None

	log_metrics(send_notifications(find_due_invoices()))
	return None


dag = payment_reminders()


