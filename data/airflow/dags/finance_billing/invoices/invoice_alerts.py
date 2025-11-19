from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Dict

import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable
from data.airflow.plugins.db import get_conn
from data.airflow.plugins.etl_notifications import notify_slack, notify_email


def _get_env_var(name: str, default: str | None = None) -> str:
	return str(Variable.get(name, default_var=default))


@dag(
	dag_id="invoice_alerts",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule="0 10 * * *",  # daily at 10:00 UTC
	catchup=False,
	default_args={
		"owner": "finance",
		"retries": 1,
		"retry_delay": timedelta(minutes=2),
		"email_on_failure": False,
		"email_on_retry": False,
	},
	description="Send alerts for critical overdue invoices",
	tags=["finance", "alerts"],
)
def invoice_alerts() -> None:
	logger = logging.getLogger("airflow.task")

	@task(task_id="check_critical_invoices")
	def check_critical_invoices() -> Dict[str, Any]:
		critical_days = int(_get_env_var("CRITICAL_OVERDUE_DAYS", default="90"))
		min_amount = float(_get_env_var("CRITICAL_MIN_AMOUNT", default="1000.0"))
		critical: list[Dict[str, Any]] = []
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					cur.execute(
						"""
						SELECT 
							id, serie, total, due_date,
							CURRENT_DATE - due_date AS days_overdue,
							payment_reminder_count
						FROM invoices
						WHERE status = 'issued'
						AND due_date IS NOT NULL
						AND due_date < CURRENT_DATE - INTERVAL '%s days'
						AND total >= %s
						ORDER BY total DESC
						LIMIT 50
						""",
						(critical_days, min_amount),
					)
					for row in cur.fetchall():
						inv_id, serie, total, due_date, days_overdue, reminders = row
						critical.append({
							"id": inv_id,
							"serie": serie,
							"total": float(total) if total else 0.0,
							"due_date": due_date.isoformat() if due_date else "",
							"days_overdue": days_overdue or 0,
							"reminders": reminders or 0,
						})
		except Exception:
			logger.warning("critical invoice check failed", exc_info=True)
		logger.info("found critical invoices", extra={"count": len(critical)})
		return {"critical": critical}

	@task(task_id="send_alerts")
	def send_alerts(payload: Dict[str, Any]) -> None:
		critical = payload.get("critical", []) or []
		if not critical:
			logger.info("no critical invoices to alert")
			return
		total_overdue = sum(c.get("total", 0.0) for c in critical)
		count = len(critical)
		# Slack alert
		slack_msg = f"⚠️ *ALERTA: {count} factura(s) vencida(s) crítica(s)*\n"
		slack_msg += f"Total vencido: {total_overdue:,.2f}\n"
		slack_msg += f"Facturas con más de {_get_env_var('CRITICAL_OVERDUE_DAYS', default='90')} días de vencimiento.\n"
		slack_msg += "\nTop 5 facturas:\n"
		for c in critical[:5]:
			slack_msg += f"• {c.get('serie')}: {c.get('total', 0):,.2f} ({c.get('days_overdue', 0)} días)\n"
		try:
			notify_slack(slack_msg)
			logger.info("slack alert sent", extra={"count": count})
		except Exception:
			logger.warning("slack alert failed", exc_info=True)
		# Email alert
		email_body = f"<h2>Alerta de Facturas Críticas</h2>"
		email_body += f"<p>Se encontraron <strong>{count}</strong> facturas vencidas críticas.</p>"
		email_body += f"<p>Total vencido: <strong>{total_overdue:,.2f}</strong></p>"
		email_body += "<table border='1' cellpadding='5'><tr><th>Serie</th><th>Total</th><th>Días Vencida</th><th>Recordatorios</th></tr>"
		for c in critical[:10]:
			email_body += f"<tr><td>{c.get('serie')}</td><td>{c.get('total', 0):,.2f}</td><td>{c.get('days_overdue', 0)}</td><td>{c.get('reminders', 0)}</td></tr>"
		email_body += "</table>"
		try:
			notify_email(
				subject=f"ALERTA: {count} Facturas Críticas Vencidas",
				html_content=email_body,
				to=None,
			)
			logger.info("email alert sent", extra={"count": count})
		except Exception:
			logger.warning("email alert failed", exc_info=True)

	send_alerts(check_critical_invoices())
	return None


dag = invoice_alerts()


