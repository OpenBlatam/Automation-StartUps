from __future__ import annotations

from datetime import timedelta, date
import logging
from typing import Any, Dict, List

import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.operators.python import get_current_context
from data.airflow.plugins.db import get_conn
from data.airflow.plugins.etl_notifications import notify_email


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
		payment_terms_days = int(_get_env_var("PAYMENT_TERMS_DAYS", default="30"))
		today = date.today()
		candidates: List[Dict[str, Any]] = []
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					# Ensure due_date column exists
					cur.execute(
						"""
						ALTER TABLE invoices 
						ADD COLUMN IF NOT EXISTS due_date DATE,
						ADD COLUMN IF NOT EXISTS payment_reminder_count INTEGER DEFAULT 0
						"""
					)
					# Update due_date for invoices without it (created_at + terms)
					cur.execute(
						"""
						UPDATE invoices 
						SET due_date = created_at + INTERVAL '%s days'
						WHERE due_date IS NULL AND status = 'issued'
						""",
						(payment_terms_days,),
					)
					# Find invoices that need reminders
					cur.execute(
						"""
						SELECT id, serie, total, due_date, payment_reminder_count, created_at
						FROM invoices
						WHERE status = 'issued'
						AND due_date IS NOT NULL
						ORDER BY id
						"""
					)
					for row in cur.fetchall():
						inv_id, serie, total, due_date, reminder_count, created_at = row
						if due_date:
							days_until_due = (due_date - today).days
							if days_until_due in days:
								candidates.append({
									"id": inv_id,
									"serie": serie,
									"total": float(total) if total else 0.0,
									"due_date": due_date.isoformat() if due_date else None,
									"days_until_due": days_until_due,
									"reminder_count": reminder_count or 0,
								})
		except Exception:
			logger.warning("DB query failed; falling back to empty candidates", exc_info=True)
		logger.info("scanning invoices for reminders", extra={"days": days, "found": len(candidates)})
		return {"candidates": candidates, "days": days}

	@task(task_id="send_notifications")
	def send_notifications(payload: Dict[str, Any]) -> Dict[str, Any]:
		candidates = payload.get("candidates", []) or []
		sent_count = 0
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					for cand in candidates:
						inv_id = cand.get("id")
						serie = cand.get("serie", "")
						total = cand.get("total", 0.0)
						days_until_due = cand.get("days_until_due", 0)
						if days_until_due < 0:
							subject = f"Recordatorio de pago - Factura {serie} vencida"
							body = f"<p>La factura {serie} por {total:.2f} está vencida hace {abs(days_until_due)} días.</p>"
						elif days_until_due == 0:
							subject = f"Recordatorio de pago - Factura {serie} vence hoy"
							body = f"<p>La factura {serie} por {total:.2f} vence hoy.</p>"
						else:
							subject = f"Recordatorio de pago - Factura {serie} vence en {days_until_due} días"
							body = f"<p>La factura {serie} por {total:.2f} vence en {days_until_due} días.</p>"
						body += "<p>Por favor, realice el pago a la brevedad.</p>"
						try:
							notify_email(subject=subject, html_content=body, to=None)
							cur.execute(
								"UPDATE invoices SET payment_reminder_count = payment_reminder_count + 1 WHERE id = %s",
								(inv_id,),
							)
							sent_count += 1
						except Exception:
							logger.warning(f"notification failed for invoice {inv_id}", exc_info=True)
					conn.commit()
		except Exception:
			logger.warning("notification send failed", exc_info=True)
		payload["sent_count"] = sent_count
		return payload

	@task(task_id="log_metrics")
	def log_metrics(payload: Dict[str, Any]) -> None:
		sent_count = payload.get("sent_count", 0)
		total_candidates = len(payload.get("candidates", []))
		logger.info("reminders sent", extra={"sent": sent_count, "total": total_candidates})
		return None

	log_metrics(send_notifications(find_due_invoices()))
	return None


dag = payment_reminders()



