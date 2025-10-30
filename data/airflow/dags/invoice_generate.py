from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Dict

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.models import Variable
from airflow.exceptions import AirflowFailException


def _get_env_var(name: str, default: str | None = None, required: bool = False) -> str:
	value = Variable.get(name, default_var=default)
	if required and (value is None or str(value).strip() == ""):
		raise AirflowFailException(f"Missing required Airflow Variable: {name}")
	return str(value)


@dag(
	dag_id="invoice_generate",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule="0 2 * * *",  # daily at 02:00 UTC
	catchup=False,
	default_args={
		"owner": "finance",
		"retries": 1,
		"retry_delay": timedelta(minutes=2),
		"email_on_failure": False,
		"email_on_retry": False,
	},
	description="Generate invoices daily from confirmed sales and notify customers",
	tags=["finance", "invoicing"],
)
def invoice_generate() -> None:
	logger = logging.getLogger("airflow.task")

	@task(task_id="load_sales")
	def load_sales() -> Dict[str, Any]:
		# In a real implementation, pull sales from DB or Stripe
		ctx = get_current_context()
		window = {
			"since": ctx["data_interval_start"].to_datetime_string(),
			"until": ctx["data_interval_end"].to_datetime_string(),
		}
		logger.info("loading sales window", extra=window)
		return {"sales": [], "window": window}

	@task(task_id="build_invoice_rows")
	def build_invoice_rows(payload: Dict[str, Any]) -> Dict[str, Any]:
		serie = _get_env_var("INVOICE_SERIE", default="A")
		tax_rate = float(_get_env_var("TAX_RATE", default="0.21"))
		company_tax_id = _get_env_var("COMPANY_TAX_ID", default="")
		logger.info(
			"building invoice rows",
			extra={"serie": serie, "tax_rate": tax_rate, "company_tax_id": company_tax_id},
		)
		payload["invoices"] = []  # placeholder
		return payload

	@task(task_id="render_pdf")
	def render_pdf(payload: Dict[str, Any]) -> Dict[str, Any]:
		# Render using Jinja2/WeasyPrint in a future step
		logger.info("rendering invoice PDFs", extra={"count": len(payload.get("invoices", []))})
		payload["pdf_paths"] = []
		return payload

	@task(task_id="store_artifacts")
	def store_artifacts(payload: Dict[str, Any]) -> Dict[str, Any]:
		s3_bucket = _get_env_var("S3_BUCKET", default="")
		logger.info("storing artifacts", extra={"bucket": s3_bucket})
		payload["artifact_urls"] = []
		return payload

	@task(task_id="email_customer")
	def email_customer(payload: Dict[str, Any]) -> Dict[str, Any]:
		smtp_url = _get_env_var("SMTP_URL", default="")
		logger.info("emailing customers", extra={"smtp_url": smtp_url})
		payload["emailed"] = True
		return payload

	@task(task_id="mark_issued")
	def mark_issued(payload: Dict[str, Any]) -> None:
		logger.info("marking invoices as issued")
		return None

	issued = mark_issued(email_customer(store_artifacts(render_pdf(build_invoice_rows(load_sales())))))
	return None


dag = invoice_generate()


