from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Dict

import pendulum
from airflow.decorators import dag, task
from data.airflow.plugins.db import get_conn


@dag(
	dag_id="invoice_audit",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule="0 3 * * *",  # daily at 03:00 UTC
	catchup=False,
	default_args={
		"owner": "finance",
		"retries": 1,
		"retry_delay": timedelta(minutes=2),
		"email_on_failure": False,
		"email_on_retry": False,
	},
	description="Create audit trail for invoice changes",
	tags=["finance", "audit"],
)
def invoice_audit() -> None:
	logger = logging.getLogger("airflow.task")

	@task(task_id="setup_audit_trail")
	def setup_audit_trail() -> None:
		with get_conn() as conn:
			with conn.cursor() as cur:
				# Create audit log table
				cur.execute(
					"""
					CREATE TABLE IF NOT EXISTS invoice_audit_log (
						id SERIAL PRIMARY KEY,
						invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
						field_name TEXT NOT NULL,
						old_value TEXT,
						new_value TEXT,
						changed_by TEXT,
						changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
					)
					"""
				)
				# Create function to log invoice changes
				cur.execute(
					"""
					CREATE OR REPLACE FUNCTION log_invoice_changes()
					RETURNS TRIGGER AS $$
					BEGIN
						IF TG_OP = 'UPDATE' THEN
							IF OLD.status IS DISTINCT FROM NEW.status THEN
								INSERT INTO invoice_audit_log (invoice_id, field_name, old_value, new_value)
								VALUES (NEW.id, 'status', OLD.status, NEW.status);
							END IF;
							IF OLD.total IS DISTINCT FROM NEW.total THEN
								INSERT INTO invoice_audit_log (invoice_id, field_name, old_value, new_value)
								VALUES (NEW.id, 'total', OLD.total::text, NEW.total::text);
							END IF;
							IF OLD.due_date IS DISTINCT FROM NEW.due_date THEN
								INSERT INTO invoice_audit_log (invoice_id, field_name, old_value, new_value)
								VALUES (NEW.id, 'due_date', OLD.due_date::text, NEW.due_date::text);
							END IF;
						END IF;
						RETURN NEW;
					END;
					$$ LANGUAGE plpgsql;
					"""
				)
				# Create trigger if it doesn't exist
				cur.execute(
					"""
					DROP TRIGGER IF EXISTS invoice_audit_trigger ON invoices;
					CREATE TRIGGER invoice_audit_trigger
					AFTER UPDATE ON invoices
					FOR EACH ROW
					EXECUTE FUNCTION log_invoice_changes();
					"""
				)
				conn.commit()
		logger.info("audit trail setup completed")

	@task(task_id="generate_audit_report")
	def generate_audit_report() -> Dict[str, Any]:
		recent_changes: list[Dict[str, Any]] = []
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					cur.execute(
						"""
						SELECT 
							ial.invoice_id,
							i.serie,
							ial.field_name,
							ial.old_value,
							ial.new_value,
							ial.changed_at
						FROM invoice_audit_log ial
						JOIN invoices i ON ial.invoice_id = i.id
						WHERE ial.changed_at >= CURRENT_DATE - INTERVAL '7 days'
						ORDER BY ial.changed_at DESC
						LIMIT 100
						"""
					)
					for row in cur.fetchall():
						recent_changes.append({
							"invoice_id": row[0],
							"serie": row[1],
							"field": row[2],
							"old_value": row[3],
							"new_value": row[4],
							"changed_at": row[5].isoformat() if row[5] else "",
						})
		except Exception:
			logger.warning("audit report generation failed", exc_info=True)
		logger.info("audit report generated", extra={"changes_count": len(recent_changes)})
		return {"recent_changes": recent_changes, "count": len(recent_changes)}

	setup_audit_trail()
	generate_audit_report()
	return None


dag = invoice_audit()


