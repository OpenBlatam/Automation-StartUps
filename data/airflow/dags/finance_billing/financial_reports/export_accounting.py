from __future__ import annotations

from datetime import timedelta, date
import logging
import os
import json
from typing import Any, Dict, List, Tuple
from pathlib import Path

import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable, Param
from airflow.exceptions import AirflowFailException
from airflow.operators.empty import EmptyOperator
from data.airflow.plugins.db import get_conn

logger = logging.getLogger(__name__)

# Operational constants
ACCOUNTING_POOL = os.getenv("ACCOUNTING_POOL", "default_pool")
MAX_RETRIES = int(os.getenv("ACCOUNTING_MAX_RETRIES", "2"))
RETRY_DELAY_MINUTES = int(os.getenv("ACCOUNTING_RETRY_DELAY_MINUTES", "5"))
TASK_TIMEOUT_SECONDS = int(os.getenv("ACCOUNTING_TASK_TIMEOUT_SECONDS", "1800"))  # 30 minutes default
DEFAULT_EXPORT_DIR = os.getenv("ACCOUNTING_EXPORT_DIR", "/tmp/accounting")


def _get_env_var(name: str, default: str | None = None) -> str:
	"""Get environment variable from Airflow Variables with fallback."""
	try:
		return str(Variable.get(name, default_var=default))
	except Exception:
		return default or ""


def _idemp_should_skip(month_key: str) -> bool:
	"""Check if export for this month has already been completed."""
	try:
		lock_key = f"accounting:export:{month_key}"
		lock_data = Variable.get(lock_key, default_var=None)
		if lock_data:
			data = json.loads(lock_data)
			expires_at = data.get("expires_at", 0)
			now = pendulum.now("UTC").int_timestamp
			if expires_at > now:
				logger.info(f"Export already completed for month: {month_key}")
				return True
		return False
	except Exception as e:
		logger.warning(f"Failed to check idempotency lock: {e}")
		return False


def _idemp_set(month_key: str, ttl_days: int = 90) -> None:
	"""Set idempotency lock for this month's export."""
	try:
		lock_key = f"accounting:export:{month_key}"
		expires_at = pendulum.now("UTC").int_timestamp + (ttl_days * 24 * 3600)
		data = json.dumps({
			"expires_at": expires_at,
			"created_at": pendulum.now("UTC").int_timestamp,
			"month_key": month_key,
		})
		Variable.set(lock_key, data)
		logger.info(f"Idempotency lock set for month: {month_key}, expires in {ttl_days} days")
	except Exception as e:
		logger.warning(f"Failed to set idempotency lock: {e}")


def _escape_xml(text: str) -> str:
	"""Escape XML special characters."""
	if not text:
		return ""
	return (
		text.replace("&", "&amp;")
		.replace("<", "&lt;")
		.replace(">", "&gt;")
		.replace('"', "&quot;")
		.replace("'", "&apos;")
	)


def _generate_ofx_file(rows: List[Tuple], output_path: Path, month_start: date, month_end: date) -> None:
	"""Generate OFX file from transaction rows."""
	logger.info(f"Generating OFX file with {len(rows)} transactions")
	
	with open(output_path, "w", encoding="utf-8") as f:
		f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
		f.write('<OFX>\n')
		f.write('<SIGNONMSGSRSV1>\n')
		f.write('<SONRS>\n')
		f.write('<STATUS><CODE>0</CODE><SEVERITY>INFO</SEVERITY></STATUS>\n')
		f.write(f'<DTSERVER>{pendulum.now("UTC").format("YYYYMMDDHHmmss")}</DTSERVER>\n')
		f.write('<LANGUAGE>ENG</LANGUAGE>\n')
		f.write('</SONRS>\n')
		f.write('</SIGNONMSGSRSV1>\n')
		f.write('<BANKMSGSRSV1>\n')
		f.write('<STMTTRNRS>\n')
		f.write('<STMTRS>\n')
		f.write('<CURDEF>USD</CURDEF>\n')
		f.write('<BANKACCTFROM>\n')
		f.write('<ACCTID>MAIN</ACCTID>\n')
		f.write('<ACCTTYPE>CHECKING</ACCTTYPE>\n')
		f.write('</BANKACCTFROM>\n')
		f.write('<BANKTRANLIST>\n')
		f.write(f'<DTSTART>{month_start.strftime("%Y%m%d")}</DTSTART>\n')
		f.write(f'<DTEND>{month_end.strftime("%Y%m%d")}</DTEND>\n')
		
		total_debits = 0.0
		total_credits = 0.0
		
		for row in rows:
			trans_date, amount, currency, memo, trans_type = row
			if not trans_date:
				continue
			
			dt = trans_date.strftime("%Y%m%d") if hasattr(trans_date, "strftime") else str(trans_date)[:8]
			amount_float = float(amount) if amount else 0.0
			
			if trans_type == "CREDIT":
				total_credits += amount_float
			else:
				total_debits += abs(amount_float)
			
			f.write('<STMTTRN>\n')
			f.write(f'<TRNTYPE>{"CREDIT" if trans_type == "CREDIT" else "DEBIT"}</TRNTYPE>\n')
			f.write(f'<DTPOSTED>{dt}</DTPOSTED>\n')
			f.write(f'<TRNAMT>{amount_float:.2f}</TRNAMT>\n')
			f.write(f'<MEMO>{_escape_xml(memo or "")}</MEMO>\n')
			f.write('</STMTTRN>\n')
		
		f.write('</BANKTRANLIST>\n')
		f.write('</STMTRS>\n')
		f.write('</STMTTRNRS>\n')
		f.write('</BANKMSGSRSV1>\n')
		f.write('</OFX>\n')
	
	logger.info(
		"OFX file generated",
		extra={
			"path": str(output_path),
			"transactions": len(rows),
			"total_debits": total_debits,
			"total_credits": total_credits,
		},
	)


@dag(
	dag_id="export_accounting",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule="0 6 1 * *",  # monthly on 1st at 06:00 UTC
	catchup=False,
	default_args={
		"owner": "finance",
		"pool": ACCOUNTING_POOL,
		"retries": MAX_RETRIES,
		"retry_delay": timedelta(minutes=RETRY_DELAY_MINUTES),
		"retry_exponential_backoff": True,
		"max_retry_delay": timedelta(minutes=30),
		"email_on_failure": False,
		"email_on_retry": False,
	},
	params={
		"export_dir": Param(
			DEFAULT_EXPORT_DIR,
			type="string",
			description="Directory to export OFX file",
		),
		"target_month": Param(
			"",
			type="string",
			description="Target month in YYYY-MM format (default: previous month)",
		),
		"skip_if_exists": Param(
			True,
			type="boolean",
			description="Skip export if file already exists",
		),
	},
	description="Export accounting data to OFX format for accounting software",
	tags=["finance", "export", "accounting"],
	doc_md="""
	# Accounting Export DAG

	Exports accounting transactions (payments and invoices) to OFX format for import into accounting software.

	## Features

	- Idempotent: Skips export if already completed for the month
	- Validates transaction data before export
	- Generates proper OFX XML with escaped characters
	- Tracks totals (debits/credits) for validation
	- Comprehensive error handling and logging

	## Parameters

	- `export_dir`: Directory to export OFX file (default: /tmp/accounting)
	- `target_month`: Target month in YYYY-MM format (default: previous month)
	- `skip_if_exists`: Skip export if file already exists (default: true)

	## Configuration

	Set these environment variables:
	- `ACCOUNTING_EXPORT_DIR`: Default export directory
	- `ACCOUNTING_POOL`: Task pool (default: default_pool)
	- `ACCOUNTING_MAX_RETRIES`: Maximum retries (default: 2)
	- `ACCOUNTING_TASK_TIMEOUT_SECONDS`: Task timeout (default: 1800)
	""",
)
def export_accounting() -> None:
	"""
	Export accounting data to OFX format with idempotency and validation.
	"""
	start = EmptyOperator(task_id="start")
	end = EmptyOperator(task_id="end")

	@task(
		task_id="validate_and_prepare",
		timeout=timedelta(seconds=60),
	)
	def validate_and_prepare(**context) -> Dict[str, Any]:
		"""Validate parameters and determine target month."""
		params = context["params"]
		export_dir = params.get("export_dir", DEFAULT_EXPORT_DIR)
		target_month_str = params.get("target_month", "")
		
		# Determine target month
		if target_month_str:
			try:
				target_month = pendulum.parse(f"{target_month_str}-01")
			except Exception as e:
				logger.warning(f"Invalid target_month format: {target_month_str}, using previous month")
				target_month = pendulum.now("UTC").subtract(months=1)
		else:
			# Default to previous month
			target_month = pendulum.now("UTC").subtract(months=1)
		
		month_key = target_month.format("YYYY-MM")
		month_start = target_month.start_of("month").date()
		month_end = target_month.end_of("month").date()
		
		# Validate export directory
		export_path = Path(export_dir)
		if not export_path.exists():
			export_path.mkdir(parents=True, exist_ok=True)
			logger.info(f"Created export directory: {export_dir}")
		
		if not export_path.is_dir():
			raise AirflowFailException(f"Export directory is not a directory: {export_dir}")
		
		ofx_filename = f"transactions_{month_key}.ofx"
		ofx_path = export_path / ofx_filename
		
		logger.info(
			"Validation and preparation completed",
			extra={
				"target_month": month_key,
				"month_start": str(month_start),
				"month_end": str(month_end),
				"export_path": str(ofx_path),
			},
		)
		
		return {
			"target_month": month_key,
			"month_start": str(month_start),
			"month_end": str(month_end),
			"export_path": str(ofx_path),
			"skip_if_exists": params.get("skip_if_exists", True),
		}

	@task(
		task_id="check_idempotency",
		timeout=timedelta(seconds=30),
	)
	def check_idempotency(prepared: Dict[str, Any]) -> Dict[str, Any]:
		"""Check if export has already been completed for this month."""
		month_key = prepared["target_month"]
		skip_if_exists = prepared.get("skip_if_exists", True)
		
		if skip_if_exists and _idemp_should_skip(month_key):
			raise AirflowFailException(f"Export already completed for month: {month_key}")
		
		# Check if file already exists
		export_path = Path(prepared["export_path"])
		if skip_if_exists and export_path.exists():
			logger.warning(f"Export file already exists: {export_path}")
			raise AirflowFailException(f"Export file already exists: {export_path}")
		
		logger.info("Idempotency check passed", extra={"month_key": month_key})
		return prepared

	@task(
		task_id="fetch_transactions",
		timeout=timedelta(seconds=TASK_TIMEOUT_SECONDS),
		pool=ACCOUNTING_POOL,
	)
	def fetch_transactions(prepared: Dict[str, Any]) -> Dict[str, Any]:
		"""Fetch transactions from database for the target month."""
		month_start = prepared["month_start"]
		month_end = prepared["month_end"]
		
		logger.info(f"Fetching transactions for period: {month_start} to {month_end}")
		
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					cur.execute(
						"""
						SELECT 
							COALESCE(p.created_at, i.created_at) AS trans_date,
							COALESCE(p.amount, i.total) AS amount,
							COALESCE(p.currency, i.currency) AS currency,
							CASE 
								WHEN p.payment_id IS NOT NULL THEN 'PAYMENT: ' || COALESCE(p.payment_id::text, '')
								WHEN i.serie IS NOT NULL THEN 'INVOICE: ' || i.serie
								ELSE 'TRANSACTION'
							END AS memo,
							CASE 
								WHEN p.payment_id IS NOT NULL THEN 'CREDIT'
								ELSE 'DEBIT'
							END AS trans_type
						FROM (
							SELECT payment_id, amount, currency, created_at, 'payment' AS source
							FROM payments
							WHERE status IN ('succeeded', 'paid', 'payment_intent.succeeded')
							AND created_at >= %s::date
							AND created_at < (%s::date + INTERVAL '1 day')
							UNION ALL
							SELECT NULL::uuid, total, currency, created_at, 'invoice' AS source
							FROM invoices
							WHERE created_at >= %s::date
							AND created_at < (%s::date + INTERVAL '1 day')
						) combined
						LEFT JOIN payments p ON combined.payment_id = p.payment_id
						LEFT JOIN invoices i ON combined.source = 'invoice' AND i.created_at = combined.created_at
						ORDER BY trans_date
						""",
						(month_start, month_end, month_start, month_end),
					)
					rows = cur.fetchall()
			
			logger.info(
				"Transactions fetched successfully",
				extra={
					"count": len(rows),
					"month_start": month_start,
					"month_end": month_end,
				},
			)
			
			return {**prepared, "transactions": rows}
		except Exception as e:
			logger.error(
				"Failed to fetch transactions",
				extra={"month_start": month_start, "month_end": month_end, "error": str(e)},
				exc_info=True,
			)
			raise AirflowFailException(f"Failed to fetch transactions: {e}") from e

	@task(
		task_id="generate_ofx",
		timeout=timedelta(seconds=TASK_TIMEOUT_SECONDS),
		pool=ACCOUNTING_POOL,
	)
	def generate_ofx(data: Dict[str, Any]) -> Dict[str, Any]:
		"""Generate OFX file from transactions."""
		transactions = data.get("transactions", [])
		export_path = Path(data["export_path"])
		month_start = date.fromisoformat(data["month_start"])
		month_end = date.fromisoformat(data["month_end"])
		
		if not transactions:
			logger.warning("No transactions found for export period")
			# Still create empty file for audit trail
			export_path.touch()
			logger.info("Created empty OFX file", extra={"path": str(export_path)})
			return {**data, "transactions_count": 0}
		
		try:
			_generate_ofx_file(transactions, export_path, month_start, month_end)
			
			# Verify file was created
			if not export_path.exists():
				raise AirflowFailException(f"OFX file was not created: {export_path}")
			
			file_size = export_path.stat().st_size
			logger.info(
				"OFX file generated successfully",
				extra={
					"path": str(export_path),
					"file_size_bytes": file_size,
					"transactions_count": len(transactions),
				},
			)
			
			return {
				**data,
				"transactions_count": len(transactions),
				"file_size_bytes": file_size,
			}
		except Exception as e:
			logger.error(
				"Failed to generate OFX file",
				extra={"export_path": str(export_path), "error": str(e)},
				exc_info=True,
			)
			raise AirflowFailException(f"Failed to generate OFX file: {e}") from e

	@task(
		task_id="set_idempotency_lock",
		timeout=timedelta(seconds=30),
	)
	def set_idempotency_lock(data: Dict[str, Any]) -> Dict[str, Any]:
		"""Set idempotency lock after successful export."""
		month_key = data["target_month"]
		_idemp_set(month_key, ttl_days=90)
		logger.info("Idempotency lock set", extra={"month_key": month_key})
		return data

	# Build DAG graph
	prepared = validate_and_prepare()
	checked = check_idempotency(prepared)
	fetched = fetch_transactions(checked)
	generated = generate_ofx(fetched)
	locked = set_idempotency_lock(generated)
	
	start >> prepared >> checked >> fetched >> generated >> locked >> end
	
	return None


dag = export_accounting()


