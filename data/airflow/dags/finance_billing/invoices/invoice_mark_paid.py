from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Dict

import pendulum
from airflow.decorators import dag, task
from data.airflow.plugins.db import get_conn


@dag(
	dag_id="invoice_mark_paid",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule="0 */2 * * *",  # every 2 hours
	catchup=False,
	default_args={
		"owner": "finance",
		"retries": 1,
		"retry_delay": timedelta(minutes=2),
		"email_on_failure": False,
		"email_on_retry": False,
	},
	description="Mark invoices as paid when matching payments arrive",
	tags=["finance", "invoicing"],
)
def invoice_mark_paid() -> None:
	logger = logging.getLogger("airflow.task")

	@task(task_id="match_payments_to_invoices")
	def match_payments_to_invoices() -> Dict[str, Any]:
		tolerance = 0.01  # 1 cent tolerance
		matched_count = 0
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					# Ensure payments table exists
					cur.execute(
						"""
						CREATE TABLE IF NOT EXISTS payments (
							payment_id VARCHAR(128) PRIMARY KEY,
							amount NUMERIC(12,2) NOT NULL,
							currency VARCHAR(8) NOT NULL,
							customer VARCHAR(256),
							status VARCHAR(64),
							method VARCHAR(64),
							metadata JSONB,
							created_at TIMESTAMP NOT NULL,
							updated_at TIMESTAMP
						)
						"""
					)
					# Find unpaid invoices
					cur.execute(
						"""
						SELECT id, serie, total, created_at
						FROM invoices
						WHERE status = 'issued'
						ORDER BY id
						"""
					)
					invoices = cur.fetchall()
					# Find recent successful payments
					cur.execute(
						"""
						SELECT payment_id, amount, currency, customer, status, created_at, metadata
						FROM payments
						WHERE status IN ('succeeded', 'paid', 'payment_intent.succeeded', 'charge.succeeded')
						AND created_at >= NOW() - INTERVAL '7 days'
						ORDER BY created_at DESC
						"""
					)
					payments = cur.fetchall()
					# Match by amount and date proximity (within 30 days)
					for inv_row in invoices:
						inv_id, inv_serie, inv_total, inv_created = inv_row
						inv_total_float = float(inv_total) if inv_total else 0.0
						for pay_row in payments:
							pay_id, pay_amount, pay_currency, pay_customer, pay_status, pay_created, pay_meta = pay_row
							pay_amount_float = float(pay_amount) if pay_amount else 0.0
							# Amount match with tolerance
							if abs(inv_total_float - pay_amount_float) <= tolerance:
								# Check if already linked
								cur.execute(
									"""
									SELECT invoice_id FROM invoice_payments 
									WHERE invoice_id = %s AND payment_id = %s
									""",
									(inv_id, pay_id),
								)
								if cur.fetchone():
									continue
								# Create invoice_payments junction table if needed
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
								# Link payment to invoice
								cur.execute(
									"""
									INSERT INTO invoice_payments (invoice_id, payment_id)
									VALUES (%s, %s)
									ON CONFLICT DO NOTHING
									""",
									(inv_id, pay_id),
								)
								# Check if invoice is fully paid
								cur.execute(
									"""
									SELECT COALESCE(SUM(p.amount), 0)
									FROM invoice_payments ip
									JOIN payments p ON ip.payment_id = p.payment_id
									WHERE ip.invoice_id = %s
									""",
									(inv_id,),
								)
								paid_amount = float(cur.fetchone()[0] or 0.0)
								if paid_amount >= inv_total_float - tolerance:
									# Mark invoice as paid
									cur.execute(
										"UPDATE invoices SET status = 'paid', updated_at = NOW() WHERE id = %s AND status = 'issued'",
										(inv_id,),
									)
									matched_count += 1
									logger.info(
										"invoice marked as paid",
										extra={"invoice_id": inv_id, "serie": inv_serie, "payment_id": pay_id},
									)
					conn.commit()
		except Exception:
			logger.warning("payment matching failed", exc_info=True)
		logger.info("matched payments to invoices", extra={"count": matched_count})
		return {"matched_count": matched_count}

	matched = match_payments_to_invoices()
	return None


dag = invoice_mark_paid()


