from __future__ import annotations

from datetime import timedelta
import os
import json
import logging
from typing import Tuple, Any, List, Dict
from time import perf_counter

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.exceptions import AirflowFailException
from airflow.models import Variable
from data.airflow.plugins.db import get_conn
from data.airflow.plugins.etl_notifications import notify_slack

try:
    import boto3
    _BOTO3_AVAILABLE = True
except Exception:
    _BOTO3_AVAILABLE = False

try:
    from azure.storage.fileshare import ShareFileClient
    _AZURE_STORAGE_AVAILABLE = True
except Exception:
    _AZURE_STORAGE_AVAILABLE = False

try:
    from airflow.stats import Stats  # type: ignore
except Exception:
    Stats = None  # type: ignore

logger = logging.getLogger(__name__)


def _one(sql: str, params: Tuple[Any, ...] | None = None) -> Any:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            r = cur.fetchone()
            return r[0] if r else None


def _rows(sql: str, params: Tuple[Any, ...] | None = None) -> List[Tuple[Any, ...]]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return list(cur.fetchall())


def _get_month_range(offset: int) -> tuple[pendulum.DateTime, pendulum.DateTime]:
	"""Get month range for a given offset (0 = current month, -1 = last month, etc.)."""
	now = pendulum.now("UTC")
	if offset == 0:
		month_start = now.start_of("month")
		month_end = now.end_of("month")
	else:
		# For negative offsets, go back that many months
		target_date = now.subtract(months=abs(offset))
		month_start = target_date.start_of("month")
		month_end = target_date.end_of("month")
	return month_start, month_end


def _idempotency_key(month_key: str, dag_id: str) -> str:
	"""Generate idempotency key for monthly report."""
	return f"kpi_report_idemp:{dag_id}:{month_key}"


def _check_idempotency(month_key: str, dag_id: str) -> bool:
	"""Check if report for month_key has already been generated."""
	try:
		key = _idempotency_key(month_key, dag_id)
		return Variable.get(key, default_var=None) is not None
	except Exception:
		return False


def _set_idempotency(month_key: str, dag_id: str) -> None:
	"""Mark report as generated for idempotency."""
	try:
		key = _idempotency_key(month_key, dag_id)
		Variable.set(key, str(pendulum.now("UTC").isoformat()))
	except Exception:
		pass


def _check_kpi_anomaly(metric_name: str, current_value: float, threshold_factor: float = 1.5) -> tuple[bool, float]:
	"""Check if KPI metric deviates significantly from historical average."""
	try:
		key = f"kpi_history:{metric_name}"
		data_str = Variable.get(key, default_var=None)
		if not data_str:
			return False, 0.0
		data = json.loads(data_str)
		history = data.get("values", [])
		if len(history) < 3:
			return False, 0.0
		# Keep last 12 months
		history = history[-12:]
		avg = sum(history) / len(history)
		max_val = max(history)
		min_val = min(history)
		# Anomaly if current > threshold * max or < (1/threshold) * min
		if current_value > threshold_factor * max_val or current_value < (1.0 / threshold_factor) * min_val:
			return True, avg
		return False, avg
	except Exception:
		return False, 0.0


def _record_kpi_value(metric_name: str, value: float) -> None:
	"""Record KPI value for anomaly detection."""
	try:
		key = f"kpi_history:{metric_name}"
		data_str = Variable.get(key, default_var=None)
		if data_str:
			data = json.loads(data_str)
			history = data.get("values", [])
		else:
			history = []
		history.append(value)
		# Keep last 12 months
		history = history[-12:]
		Variable.set(key, json.dumps({"values": history}))
	except Exception:
		pass


def _calculate_percentage_change(current: float, previous: float) -> float:
	"""Calculate percentage change between current and previous values."""
	if previous == 0:
		return 0.0
	return ((current / previous) - 1.0) * 100.0


@dag(
	dag_id="kpi_reports_monthly",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule="0 9 1 * *",  # Day 1 of month, 09:00 UTC
	catchup=False,
	default_args={
		"owner": "data-eng",
		"retries": 2,
		"retry_delay": timedelta(minutes=10),
		"retry_exponential_backoff": True,
		"max_retry_delay": timedelta(minutes=30),
		"depends_on_past": False,
		"email_on_failure": False,
		"email_on_retry": False,
	},
	tags=["kpi", "reports", "monthly"],
	description="Monthly KPI report with trends, comparisons, and top sources/countries",
	doc_md="""
	### Monthly KPI Reports
	
	Generates comprehensive monthly KPI reports including:
	- Revenue and leads comparisons (MoM)
	- Top 5 sources by revenue
	- Top 5 countries by revenue
	- HTML report saved to filesystem and optionally S3
	
	**Idempotency**: Reports are cached per month to avoid regeneration.
	**Output**: HTML file + Slack notification + optional S3 upload.
	""",
)
def kpi_reports_monthly() -> None:
	logger = logging.getLogger("airflow.task")

	@task(task_id="build_monthly_report", execution_timeout=timedelta(minutes=15), retries=2)
	def build_monthly_report() -> str:
		"""Build monthly KPI report with idempotency check and validation."""
		ctx = get_current_context()
		dag_id = ctx.get("dag").dag_id if ctx.get("dag") else "kpi_reports_monthly"
		start = perf_counter()
		
		# Use helper for month ranges
		last_month_start, last_month_end = _get_month_range(-1)
		prev_month_start, prev_month_end = _get_month_range(-2)
		
		month_key = last_month_start.strftime("%Y-%m")
		logger.info("building monthly report", extra={
			"month": month_key,
			"month_start": last_month_start.isoformat(),
			"month_end": last_month_end.isoformat(),
		})
		
		# Idempotency check
		if _check_idempotency(month_key, dag_id):
			logger.warning("report already generated for month, returning existing", extra={"month": month_key})
			out_dir = os.environ.get("KPI_REPORTS_DIR", "/tmp")
			out_path = os.path.join(out_dir, f"kpi_monthly_{month_key.replace('-', '_')}.html")
			if os.path.exists(out_path):
				logger.info("using existing report", extra={"path": out_path})
				return out_path

		rev_last = float(_one(
			"SELECT COALESCE(SUM(revenue),0) FROM mv_kpi_daily WHERE day >= %s AND day <= %s",
			(last_month_start.date(), last_month_end.date())
		) or 0)
		rev_prev = float(_one(
			"SELECT COALESCE(SUM(revenue),0) FROM mv_kpi_daily WHERE day >= %s AND day <= %s",
			(prev_month_start.date(), prev_month_end.date())
		) or 0)
		leads_last = int(_one(
			"SELECT COALESCE(SUM(leads),0) FROM mv_kpi_daily WHERE day >= %s AND day <= %s",
			(last_month_start.date(), last_month_end.date())
		) or 0)
		leads_prev = int(_one(
			"SELECT COALESCE(SUM(leads),0) FROM mv_kpi_daily WHERE day >= %s AND day <= %s",
			(prev_month_start.date(), prev_month_end.date())
		) or 0)

		def pct(a: float, b: float) -> float:
			return ((a / (b or 1)) - 1.0) * 100.0 if b else 0.0

		rev_var = pct(rev_last, rev_prev)
		leads_var = pct(leads_last, leads_prev)
		
		# Anomaly detection
		try:
			rev_anomaly, rev_avg = _check_kpi_anomaly("revenue_monthly", rev_last, threshold_factor=1.5)
			leads_anomaly, leads_avg = _check_kpi_anomaly("leads_monthly", leads_last, threshold_factor=2.0)
			if rev_anomaly:
				logger.warning("Revenue anomaly detected", extra={
					"current": rev_last,
					"avg": rev_avg,
					"factor": rev_last / max(rev_avg, 1),
					"month": last_month_start.strftime("%Y-%m")
				})
				try:
					notify_slack(f":warning: Revenue anomaly: {rev_last:.2f} (avg: {rev_avg:.2f}) for {last_month_start.strftime('%B %Y')}")
					if Stats:
						Stats.incr("kpi_reports.revenue_anomaly", 1)
				except Exception:
					pass
			if leads_anomaly:
				logger.warning("Leads anomaly detected", extra={
					"current": leads_last,
					"avg": leads_avg,
					"factor": leads_last / max(leads_avg, 1),
					"month": last_month_start.strftime("%Y-%m")
				})
				try:
					notify_slack(f":warning: Leads anomaly: {leads_last} (avg: {leads_avg:.0f}) for {last_month_start.strftime('%B %Y')}")
					if Stats:
						Stats.incr("kpi_reports.leads_anomaly", 1)
				except Exception:
					pass
			# Record values
			_record_kpi_value("revenue_monthly", rev_last)
			_record_kpi_value("leads_monthly", leads_last)
		except Exception:
			pass
		
		# Metrics
		try:
			if Stats:
				Stats.incr("kpi_reports.monthly_report_built", 1)
				Stats.timing("kpi_reports.revenue_monthly", int(rev_last))
				Stats.timing("kpi_reports.leads_monthly", leads_last)
		except Exception:
			pass
		
		logger.info("built monthly report", extra={
			"component": "build_monthly_report",
			"month": last_month_start.strftime("%Y-%m"),
			"revenue": rev_last,
			"leads": leads_last,
			"revenue_var_pct": rev_var,
			"leads_var_pct": leads_var,
			"dag_run_id": str(ctx.get("run_id", "")),
		})

		# Top sources and countries (last month)
		top_sources = _rows(
			"SELECT source, SUM(revenue)::numeric(18,2) as rev, SUM(leads)::bigint as leads "
			"FROM mv_kpi_daily_segment WHERE day >= %s AND day <= %s AND source != 'unknown' "
			"GROUP BY source ORDER BY rev DESC LIMIT 5",
			(last_month_start.date(), last_month_end.date())
		)
		top_countries = _rows(
			"SELECT country, SUM(revenue)::numeric(18,2) as rev, SUM(leads)::bigint as leads "
			"FROM mv_kpi_daily_segment WHERE day >= %s AND day <= %s AND country != 'unknown' "
			"GROUP BY country ORDER BY rev DESC LIMIT 5",
			(last_month_start.date(), last_month_end.date())
		)

		html = f"""
		<html><head><meta charset="utf-8"><title>Reporte Mensual KPIs - {last_month_start.strftime('%Y-%m')}</title></head><body>
		<h1>Reporte Mensual de KPIs - {last_month_start.strftime('%B %Y')}</h1>
		<h2>Resumen Ejecutivo</h2>
		<table border="1" cellpadding="8">
		<tr><th>Métrica</th><th>{last_month_start.strftime('%B')}</th><th>{prev_month_start.strftime('%B')}</th><th>Variación</th></tr>
		<tr><td><b>Ingresos</b></td><td>{rev_last:.2f}</td><td>{rev_prev:.2f}</td><td>{rev_var:+.1f}%</td></tr>
		<tr><td><b>Leads</b></td><td>{leads_last}</td><td>{leads_prev}</td><td>{leads_var:+.1f}%</td></tr>
		</table>

		<h2>Top 5 Fuentes por Revenue</h2>
		<table border="1" cellpadding="8">
		<tr><th>Fuente</th><th>Revenue</th><th>Leads</th></tr>
		{"".join([f"<tr><td>{r[0]}</td><td>{float(r[1]):.2f}</td><td>{int(r[2])}</td></tr>" for r in top_sources])}
		</table>

		<h2>Top 5 Países por Revenue</h2>
		<table border="1" cellpadding="8">
		<tr><th>País</th><th>Revenue</th><th>Leads</th></tr>
		{"".join([f"<tr><td>{r[0]}</td><td>{float(r[1]):.2f}</td><td>{int(r[2])}</td></tr>" for r in top_countries])}
		</table>
		</body></html>
		""".strip()

		out_dir = os.environ.get("KPI_REPORTS_DIR", "/tmp")
		os.makedirs(out_dir, exist_ok=True)
		out_path = os.path.join(out_dir, f"kpi_monthly_{month_key.replace('-', '_')}.html")
		with open(out_path, "w", encoding="utf-8") as fh:
			fh.write(html)
		
		# Mark as completed for idempotency
		_set_idempotency(month_key, dag_id)
		
		# Record duration
		duration_ms = int((perf_counter() - start) * 1000)
		logger.info("report generated successfully", extra={
			"path": out_path,
			"duration_ms": duration_ms,
			"month": month_key,
		})
		try:
			if Stats:
				Stats.timing("kpi_reports.build_duration_ms", duration_ms)
		except Exception:
			pass
		
		return out_path

	@task(task_id="notify_slack_monthly", execution_timeout=timedelta(minutes=5), retries=1)
	def notify_slack_monthly(html_path: str) -> None:
		"""Send Slack notification with monthly KPI summary."""
		ctx = get_current_context()
		# Use helpers for month ranges
		last_month_start, last_month_end = _get_month_range(-1)
		prev_month_start, prev_month_end = _get_month_range(-2)

		rev_last = float(_one(
			"SELECT COALESCE(SUM(revenue),0) FROM mv_kpi_daily WHERE day >= %s AND day <= %s",
			(last_month_start.date(), last_month_end.date())
		) or 0)
		leads_last = int(_one(
			"SELECT COALESCE(SUM(leads),0) FROM mv_kpi_daily WHERE day >= %s AND day <= %s",
			(last_month_start.date(), last_month_end.date())
		) or 0)
		rev_prev = float(_one(
			"SELECT COALESCE(SUM(revenue),0) FROM mv_kpi_daily WHERE day >= %s AND day <= %s",
			(prev_month_start.date(), prev_month_end.date())
		) or 0)
		rev_var = _calculate_percentage_change(rev_last, rev_prev)

		text = (
			f":calendar_spiral: Reporte mensual KPIs - {last_month_start.strftime('%B %Y')}\n"
			f"Ingresos: {rev_last:.2f} ({rev_var:+.1f}% vs mes anterior)\n"
			f"Leads: {leads_last}\n"
			f"HTML: {html_path}"
		)
		logger.info("sending Slack notification", extra={
			"month": last_month_start.strftime("%Y-%m"),
			"revenue": rev_last,
			"leads": leads_last,
		})
		notify_slack(text)
		try:
			if Stats:
				Stats.incr("kpi_reports.slack_notification_sent", 1)
		except Exception:
			pass
		logger.info("notified Slack", extra={
			"component": "notify_slack_monthly",
			"month": last_month_start.strftime("%Y-%m"),
			"revenue": rev_last,
			"leads": leads_last,
			"dag_run_id": str(ctx.get("run_id", "")),
		})
		try:
			if Stats:
				Stats.incr("kpi_reports.slack_notified", 1)
		except Exception:
			pass

	@task(task_id="upload_to_storage")
	def upload_to_storage(html_path: str) -> str | None:
		ctx = get_current_context()
		# Try S3 first
		bucket = os.environ.get("KPI_REPORTS_S3_BUCKET")
		s3_prefix = os.environ.get("KPI_REPORTS_S3_PREFIX", "reports/monthly")
		if bucket and _BOTO3_AVAILABLE:
			try:
				s3 = boto3.client("s3")
				last_month_start = (pendulum.now("UTC").start_of("month") - timedelta(days=1)).start_of("month")
				key = f"{s3_prefix}/{last_month_start.strftime('%Y_%m')}/kpi_monthly_{last_month_start.strftime('%Y_%m')}.html"
				s3.upload_file(html_path, bucket, key)
				logger.info("uploaded to S3", extra={
					"bucket": bucket,
					"key": key,
					"dag_run_id": str(ctx.get("run_id", "")),
				})
				try:
					if Stats:
						Stats.incr("kpi_reports.s3_upload_success", 1)
				except Exception:
					pass
				return f"s3://{bucket}/{key}"
			except Exception as e:
				logger.error("S3 upload failed", extra={"error": str(e), "dag_run_id": str(ctx.get("run_id", ""))})
		
		# Try ADLS (Azure Data Lake Storage)
		adls_share = os.environ.get("KPI_REPORTS_ADLS_SHARE")
		adls_path = os.environ.get("KPI_REPORTS_ADLS_PATH", "reports/monthly")
		if adls_share and _AZURE_STORAGE_AVAILABLE:
			try:
				conn_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
				if conn_str:
					last_month_start = (pendulum.now("UTC").start_of("month") - timedelta(days=1)).start_of("month")
					file_path = f"{adls_path}/{last_month_start.strftime('%Y_%m')}/kpi_monthly_{last_month_start.strftime('%Y_%m')}.html"
					client = ShareFileClient.from_connection_string(conn_str, share_name=adls_share, file_path=file_path)
					with open(html_path, "rb") as fh:
						client.upload_file(fh)
					logger.info("uploaded to ADLS", extra={
						"share": adls_share,
						"file_path": file_path,
						"dag_run_id": str(ctx.get("run_id", "")),
					})
					try:
						if Stats:
							Stats.incr("kpi_reports.adls_upload_success", 1)
					except Exception:
						pass
					return f"adls://{adls_share}/{file_path}"
			except Exception as e:
				logger.error("ADLS upload failed", extra={"error": str(e), "dag_run_id": str(ctx.get("run_id", ""))})
		
		return None

	p = build_monthly_report()
	storage_url = upload_to_storage(p)
	notify_slack_monthly(f"{p} (Storage: {storage_url})" if storage_url else p)
	return None


dag = kpi_reports_monthly()

