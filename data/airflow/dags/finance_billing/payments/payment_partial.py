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
	dag_id="payment_partial",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule="0 */4 * * *",  # every 4 hours
	catchup=False,
	default_args={
		"owner": "finance",
		"retries": 1,
		"retry_delay": timedelta(minutes=2),
		"email_on_failure": False,
		"email_on_retry": False,
	},
	description="Handle partial payments and update invoice status accordingly",
	tags=["finance", "payments"],
)
def payment_partial() -> None:
	logger = logging.getLogger("airflow.task")

	@task(task_id="match_partial_payments")
	def match_partial_payments() -> Dict[str, Any]:
		tolerance = 0.01
		matched: list[Dict[str, Any]] = []
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					# Ensure invoice_payments table exists
					cur.execute(
						"""
						CREATE TABLE IF NOT EXISTS invoice_payments (
							invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
							payment_id VARCHAR(128) NOT NULL REFERENCES payments(payment_id) ON DELETE CASCADE,
							matched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
							PRIMARY KEY (invoice_id, payment_id)
						)
						"""
					)
					# Get unpaid or partially paid invoices
					cur.execute(
						"""
						SELECT 
							i.id, i.serie, i.total, i.currency,
							COALESCE(SUM(p.amount), 0) AS paid_amount
						FROM invoices i
						LEFT JOIN invoice_payments ip ON i.id = ip.invoice_id
						LEFT JOIN payments p ON ip.payment_id = p.payment_id 
							AND p.status IN ('succeeded', 'paid', 'payment_intent.succeeded')
						WHERE i.status IN ('issued', 'partial')
						GROUP BY i.id, i.serie, i.total, i.currency
						HAVING COALESCE(SUM(p.amount), 0) < i.total - %s
						ORDER BY i.id
						""",
						(tolerance,),
					)
					invoices = cur.fetchall()
					# Get unmatched successful payments
					cur.execute(
						"""
						SELECT p.payment_id, p.amount, p.currency, p.created_at, p.customer
						FROM payments p
						WHERE p.status IN ('succeeded', 'paid', 'payment_intent.succeeded')
						AND p.created_at >= NOW() - INTERVAL '7 days'
						AND NOT EXISTS (
							SELECT 1 FROM invoice_payments ip 
							WHERE ip.payment_id = p.payment_id
						)
						ORDER BY p.created_at DESC
						LIMIT 100
						"""
					)
					payments = cur.fetchall()
					# Try to match payments to invoices
					for inv_row in invoices:
						inv_id, inv_serie, inv_total, inv_currency = inv_row
						paid_amount = float(inv_row[4] or 0.0)
						remaining = float(inv_total) - paid_amount
						for pay_row in payments:
							pay_id, pay_amount, pay_currency, pay_created, pay_customer = pay_row
							pay_amount_float = float(pay_amount) if pay_amount else 0.0
							# Check currency match and amount compatibility
							if pay_currency.upper() == inv_currency.upper() and pay_amount_float <= remaining + tolerance:
								# Check if already linked
								cur.execute(
									"SELECT 1 FROM invoice_payments WHERE invoice_id = %s AND payment_id = %s",
									(inv_id, pay_id),
								)
								if cur.fetchone():
									continue
								# Link payment
								cur.execute(
									"INSERT INTO invoice_payments (invoice_id, payment_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
									(inv_id, pay_id),
								)
								# Recalculate paid amount
								cur.execute(
									"""
									SELECT COALESCE(SUM(p.amount), 0)
									FROM invoice_payments ip
									JOIN payments p ON ip.payment_id = p.payment_id
									WHERE ip.invoice_id = %s
									""",
									(inv_id,),
								)
								new_paid = float(cur.fetchone()[0] or 0.0)
								# Update invoice status
								if new_paid >= float(inv_total) - tolerance:
									cur.execute(
										"UPDATE invoices SET status = 'paid', updated_at = NOW() WHERE id = %s",
										(inv_id,),
									)
									matched.append({
										"invoice_id": inv_id,
										"serie": inv_serie,
										"payment_id": pay_id,
										"status": "fully_paid",
									})
								elif new_paid > tolerance:
									cur.execute(
										"UPDATE invoices SET status = 'partial', updated_at = NOW() WHERE id = %s AND status = 'issued'",
										(inv_id,),
									)
									matched.append({
										"invoice_id": inv_id,
										"serie": inv_serie,
										"payment_id": pay_id,
										"status": "partial",
										"paid_amount": new_paid,
										"remaining": float(inv_total) - new_paid,
									})
								break
					conn.commit()
		except Exception:
			logger.warning("partial payment matching failed", exc_info=True)
		logger.info("matched partial payments", extra={"count": len(matched)})
		return {"matched": matched}

	matched = match_partial_payments()
	return None


dag = payment_partial()


