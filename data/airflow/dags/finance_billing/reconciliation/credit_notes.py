from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Dict

import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.exceptions import AirflowFailException
from data.airflow.plugins.db import get_conn
from data.airflow.plugins.etl_notifications import notify_email


def _get_env_var(name: str, default: str | None = None) -> str:
	return str(Variable.get(name, default_var=default))


@dag(
	dag_id="credit_notes",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule=None,  # Manual trigger only
	catchup=False,
	default_args={
		"owner": "finance",
		"retries": 1,
		"retry_delay": timedelta(minutes=2),
		"email_on_failure": False,
		"email_on_retry": False,
	},
	description="Generate credit notes for refunds or adjustments",
	tags=["finance", "credit-notes"],
)
def credit_notes() -> None:
	logger = logging.getLogger("airflow.task")

	@task(task_id="validate_invoice")
	def validate_invoice(invoice_id: int, reason: str) -> Dict[str, Any]:
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					cur.execute(
						"""
						SELECT id, serie, total, currency, status
						FROM invoices
						WHERE id = %s
						""",
						(invoice_id,),
					)
					row = cur.fetchone()
					if not row:
						raise AirflowFailException(f"Invoice {invoice_id} not found")
					inv_id, serie, total, currency, status = row
					if status not in ("issued", "paid"):
						raise AirflowFailException(f"Invoice {serie} has invalid status: {status}")
					if not reason or not reason.strip():
						raise AirflowFailException("Reason for credit note is required")
					return {
						"invoice_id": inv_id,
						"serie": serie,
						"total": float(total),
						"currency": currency,
						"status": status,
						"reason": reason.strip(),
					}
		except Exception as e:
			if isinstance(e, AirflowFailException):
				raise
			logger.error("validation failed", exc_info=True)
			raise AirflowFailException(f"Validation failed: {e}")

	@task(task_id="create_credit_note")
	def create_credit_note(payload: Dict[str, Any]) -> Dict[str, Any]:
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					# Create credit_notes table if needed
					cur.execute(
						"""
						CREATE TABLE IF NOT EXISTS credit_notes (
							id SERIAL PRIMARY KEY,
							invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE RESTRICT,
							credit_note_number TEXT NOT NULL UNIQUE,
							amount NUMERIC(12,2) NOT NULL,
							currency VARCHAR(8) NOT NULL,
							reason TEXT NOT NULL,
							status TEXT NOT NULL DEFAULT 'issued',
							created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
						)
						"""
					)
					# Generate credit note number
					serie_prefix = _get_env_var("CREDIT_NOTE_PREFIX", default="CN")
					cur.execute(
						"SELECT COUNT(*) FROM credit_notes WHERE credit_note_number LIKE %s",
						(f"{serie_prefix}%",),
					)
					count = cur.fetchone()[0] or 0
					credit_note_number = f"{serie_prefix}-{count + 1:06d}"
					# Create credit note
					cur.execute(
						"""
						INSERT INTO credit_notes 
						(invoice_id, credit_note_number, amount, currency, reason)
						VALUES (%s, %s, %s, %s, %s)
						RETURNING id
						""",
						(
							payload["invoice_id"],
							credit_note_number,
							payload["total"],
							payload["currency"],
							payload["reason"],
						),
					)
					cn_id = cur.fetchone()[0]
					# Update invoice status if it was paid
					if payload["status"] == "paid":
						cur.execute(
							"UPDATE invoices SET status = 'refunded', updated_at = NOW() WHERE id = %s",
							(payload["invoice_id"],),
						)
					conn.commit()
					payload.update({
						"credit_note_id": cn_id,
						"credit_note_number": credit_note_number,
					})
					logger.info(
						"credit note created",
						extra={
							"credit_note_id": cn_id,
							"credit_note_number": credit_note_number,
							"invoice_id": payload["invoice_id"],
						},
					)
		except Exception:
			logger.error("credit note creation failed", exc_info=True)
			raise
		return payload

	@task(task_id="notify_credit_note")
	def notify_credit_note(payload: Dict[str, Any]) -> None:
		subject = f"Nota de Crédito emitida: {payload.get('credit_note_number')}"
		body = f"""
		<h3>Nota de Crédito Generada</h3>
		<p><strong>Número:</strong> {payload.get('credit_note_number')}</p>
		<p><strong>Factura:</strong> {payload.get('serie')}</p>
		<p><strong>Monto:</strong> {payload.get('currency', 'USD')} {payload.get('total', 0):,.2f}</p>
		<p><strong>Razón:</strong> {payload.get('reason')}</p>
		"""
		try:
			notify_email(subject=subject, html_content=body, to=None)
		except Exception:
			logger.warning("credit note notification failed", exc_info=True)

	# This DAG should be triggered with params: {"invoice_id": 123, "reason": "Customer refund"}
	@task(task_id="entry")
	def entry(**context) -> Dict[str, Any]:
		from airflow.operators.python import get_current_context
		ctx = get_current_context()
		params = ctx.get("params", {}) or {}
		invoice_id = int(params.get("invoice_id", 0))
		reason = params.get("reason", "")
		if not invoice_id or not reason:
			raise AirflowFailException("Required params: invoice_id (int) and reason (str)")
		return {"invoice_id": invoice_id, "reason": reason}

	entry_data = entry()
	validated = validate_invoice(entry_data["invoice_id"], entry_data["reason"])
	notify_credit_note(create_credit_note(validated))
	return None


dag = credit_notes()

