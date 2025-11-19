
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Dict, Any
from time import perf_counter
import os
import json
import hashlib

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.exceptions import AirflowFailException
from airflow.datasets import Dataset
from airflow.utils.task_group import TaskGroup
from airflow.models.param import Param
from data.airflow.plugins.etl_types import ExtractPayload, DEFAULT_ROWS, DEFAULT_RUN_NAME
from data.airflow.plugins.etl_ops import extract_rows, apply_transform, log_with_mlflow
from data.airflow.plugins.etl_callbacks import sla_miss_callback, on_task_failure
from data.airflow.plugins.etl_config import validate_params
from data.airflow.plugins.etl_metrics import (
	record_extract_start,
	record_extract_success,
	record_transform_start,
	record_transform_success,
	record_load_duration_ms,
	record_load_success,
)
from data.airflow.plugins.etl_notifications import notify_slack
from data.airflow.plugins.etl_tracing import start_span
from data.airflow.plugins.etl_validation import validate_and_raise, validate_rows_range
from data.airflow.plugins.etl_logging import get_task_logger, log_with_context, log_task_duration
from data.airflow.plugins.etl_performance import track_performance
from data.airflow.plugins.etl_debug import debug_context
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

try:
	from airflow.stats import Stats  # type: ignore
except Exception:
	Stats = None  # type: ignore


# optional mlflow import
try:
	import mlflow  # type: ignore
	_MLFLOW_AVAILABLE = True
except Exception:
	_MLFLOW_AVAILABLE = False


SOURCE_DATASET = Dataset("dataset://source_ready")
RAW_DATASET = Dataset("dataset://etl_example/raw")
TRANSFORMED_DATASET = Dataset("dataset://etl_example/transformed")
VALIDATED_DATASET = Dataset("dataset://etl_example/validated")
DQ_OK_DATASET = Dataset("dataset://etl_example/dq_ok")
COMPLETE_DATASET = Dataset("dataset://etl_example/complete")

# Environment-driven operational toggles
ETL_POOL = os.getenv("ETL_POOL", "etl_pool")
DQ_POOL = os.getenv("DQ_POOL", "dq_pool")
MAX_ACTIVE_TASKS = int(os.getenv("MAX_ACTIVE_TASKS", "32"))
CHUNK_PARALLELISM = int(os.getenv("CHUNK_PARALLELISM", "16"))
MAX_CHUNKS = int(os.getenv("MAX_CHUNKS", "100"))


def _resolve_mlflow_uri_from_env() -> str | None:
	"""
	Attempt to resolve MLflow URI from environments/<env>.yaml (domains.mlflow).
	
	Returns:
		Full MLflow tracking URI (e.g., "https://mlflow.example.com") or None if not found.
	"""
	logger = logging.getLogger(__name__)
	try:
		env = os.getenv("ENV", os.getenv("AIRFLOW_ENV", "dev")).lower()
		root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
		env_file = os.path.join(root, "environments", f"{env}.yaml")
		
		if not os.path.exists(env_file):
			logger.debug("Environment file not found: %s", env_file)
			return None
		
		domain = None
		with open(env_file, "r", encoding="utf-8") as fh:
			for line in fh:
				line_strip = line.strip()
				if line_strip.startswith("mlflow:"):
					parts = line_strip.split(":", 1)
					if len(parts) == 2:
						domain = parts[1].strip()
						break
		
		if not domain:
			logger.debug("MLflow domain not found in environment file: %s", env_file)
			return None
		
		# Ensure protocol prefix
		uri = f"https://{domain}" if not domain.startswith("http") else domain
		logger.debug("Resolved MLflow URI from environment: %s", uri)
		return uri
	except Exception as e:
		logger.warning("Failed to resolve MLflow URI from env: %s", e)
		return None


def _cb_key(dag_id: str) -> str:
	"""Circuit breaker state key in Variables."""
	return f"cb:failures:{dag_id}"


def _cb_is_open(dag_id: str, threshold: int, reset_minutes: int) -> bool:
	"""Check if circuit breaker is open (too many recent failures).
	
	Returns True if threshold is exceeded and reset window hasn't passed.
	"""
	if threshold <= 0:
		return False
	try:
		data_str = Variable.get(_cb_key(dag_id), default_var=None)
		if not data_str:
			return False
		data = json.loads(data_str)
		count = int(data.get("count", 0))
		last_failure_ts = int(data.get("last_failure_ts", 0))
		if count >= threshold:
			now_ts = pendulum.now("UTC").int_timestamp
			reset_sec = reset_minutes * 60
			age = now_ts - last_failure_ts
			if age < reset_sec:
				return True
			# Reset expired counter
			Variable.delete(_cb_key(dag_id))
			return False
		return False
	except Exception:
		return False


def _cb_record_failure(dag_id: str) -> None:
	"""Increment failure counter for circuit breaker."""
	try:
		data_str = Variable.get(_cb_key(dag_id), default_var=None)
		if data_str:
			data = json.loads(data_str)
			count = int(data.get("count", 0)) + 1
		else:
			count = 1
		now_ts = pendulum.now("UTC").int_timestamp
		Variable.set(_cb_key(dag_id), json.dumps({"count": count, "last_failure_ts": now_ts}))
	except Exception:
		pass


def _cb_reset(dag_id: str) -> None:
	"""Reset circuit breaker counter on success."""
	try:
		Variable.delete(_cb_key(dag_id))
	except Exception:
		pass


def _on_dag_success(context: Dict[str, Any]) -> None:
	"""Callback for DAG success: reset circuit breaker and notify."""
	try:
		dag_id = context.get("dag").dag_id if context.get("dag") else "etl_example"
		_cb_reset(dag_id)
	except Exception:
		pass
	try:
		notify_slack(":white_check_mark: etl_example DAG succeeded")
	except Exception:
		pass


def _volume_history_key(dag_id: str) -> str:
	"""Key for storing volume history in Variables."""
	return f"vol_history:{dag_id}"


def _check_volume_anomaly(dag_id: str, current_rows: int, threshold_factor: float = 2.0) -> tuple[bool, float]:
	"""Check if current volume deviates significantly from historical average.
	
	Returns (is_anomaly, avg_historical_rows).
	"""
	if threshold_factor <= 0:
		return False, 0.0
	try:
		data_str = Variable.get(_volume_history_key(dag_id), default_var=None)
		if not data_str:
			return False, 0.0
		data = json.loads(data_str)
		history = data.get("rows", [])
		if len(history) < 3:
			return False, 0.0
		# Keep last 20 runs
		history = history[-20:]
		avg = sum(history) / len(history)
		max_val = max(history)
		min_val = min(history)
		# Anomaly if current is > threshold_factor * max or < (1/threshold_factor) * min
		if current_rows > threshold_factor * max_val or current_rows < (1.0 / threshold_factor) * min_val:
			return True, avg
		return False, avg
	except Exception:
		return False, 0.0


def _record_volume(dag_id: str, rows: int) -> None:
	"""Record volume for anomaly detection."""
	try:
		key = _volume_history_key(dag_id)
		data_str = Variable.get(key, default_var=None)
		if data_str:
			data = json.loads(data_str)
			history = data.get("rows", [])
		else:
			history = []
		history.append(rows)
		# Keep last 20 runs
		history = history[-20:]
		Variable.set(key, json.dumps({"rows": history}))
	except Exception:
		pass


def _adaptive_chunk_size(total_rows: int, max_chunks: int, base_chunk_size: int) -> int:
	"""Calculate optimal chunk size based on data volume and parallelism limits.
	
	Returns chunk size that balances parallelism with overhead.
	"""
	if total_rows <= 0:
		return base_chunk_size
	# Ideal chunks: balance between parallelism and overhead
	ideal_chunks = min(max_chunks, max(1, total_rows // base_chunk_size))
	if ideal_chunks == 0:
		ideal_chunks = 1
	# Chunk size to achieve ideal parallelism
	chunk_size = max(1, total_rows // ideal_chunks)
	# Round up to nearest 10k for efficiency
	chunk_size = ((chunk_size + 9999) // 10000) * 10000
	return max(1, min(chunk_size, total_rows))


def _now_ts() -> int:
	"""Get current UTC timestamp as integer.
	
	Returns:
		Current Unix timestamp (seconds since epoch).
	"""
	return pendulum.now("UTC").int_timestamp


def _payload_checksum(payload: Dict[str, Any]) -> str:
	"""
	Generate stable checksum for idempotency; ignores non-deterministic fields.
	
	Args:
		payload: Dictionary containing rows, since, until, and transformed fields.
		
	Returns:
		SHA256 hex digest of the payload's key fields.
	"""
	rows = int(payload.get("rows", 0))
	since = str(payload.get("since", ""))
	until = str(payload.get("until", ""))
	transformed = bool(payload.get("transformed", False))
	
	blob = json.dumps(
		{"rows": rows, "since": since, "until": until, "transformed": transformed},
		sort_keys=True,
		separators=(",", ":")
	)
	return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _idemp_should_skip(lock_key: str) -> bool:
	"""
	Check if a non-expired idempotency lock exists for the given key.
	
	Args:
		lock_key: Unique identifier for the idempotency check.
		
	Returns:
		True if lock exists and hasn't expired, False otherwise.
	"""
	val = Variable.get(lock_key, default_var=None)
	if not val:
		return False
	
	try:
		expires = int(val)
		return _now_ts() < expires
	except (ValueError, TypeError) as e:
		logging.getLogger(__name__).warning("Invalid lock value for key %s: %s", lock_key, e)
		return True


def _idemp_set(lock_key: str, ttl_seconds: int) -> None:
	"""
	Set an idempotency lock with TTL.
	
	Args:
		lock_key: Unique identifier for the idempotency check.
		ttl_seconds: Time-to-live in seconds for the lock.
	"""
	expires = _now_ts() + max(0, int(ttl_seconds))
	Variable.set(lock_key, str(expires))


def _dq_ok(rows: int, min_rows: int, max_rows: int) -> bool:
	"""
	Check if row count passes data quality constraints.
	
	Args:
		rows: Actual number of rows to validate.
		min_rows: Minimum acceptable row count.
		max_rows: Maximum acceptable row count.
		
	Returns:
		True if rows is within [min_rows, max_rows] range.
	"""
	return min_rows <= rows <= max_rows


@dag(
	dag_id="etl_example",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule=[SOURCE_DATASET],
	catchup=False,
	default_args={
		"owner": "data-eng",
		"retries": 1,
		"retry_delay": timedelta(minutes=2),
		"retry_exponential_backoff": True,
		"max_retry_delay": timedelta(minutes=10),
		"depends_on_past": False,
		"email_on_failure": False,
		"email_on_retry": False,
	},
	doc_md="""
	### ETL Example

	Simple example ETL using Airflow TaskFlow API. Supports overriding params at trigger time:

	**Params:**
	- `rows` (int, 1-10M): number of rows to simulate
	- `run_name` (str, 1-128): mlflow run name
	- `chunk_rows` (int, 1-10M, default 100k): max rows per chunk for parallelism
	- `dry_run` (bool): skip load side-effects (default false)
	- `enable_load` (bool): enable load step (default true)
	- `since` (str): ISO 8601 start timestamp (optional)
	- `until` (str): ISO 8601 end timestamp (optional)
	- `allow_overwrite` (bool): allow overwriting existing loads (default false)
	- `min_rows` (int): minimum rows for DQ check (default 1)
	- `max_rows` (int): maximum rows for DQ check (default 10M)
	- `trigger_post_report` (bool): trigger downstream DAG (default false)
	- `downstream_dag_id` (str): downstream DAG ID (default "post_etl_report")

	**Triggers:** when `dataset://source_ready` is updated.

	**Pools:** Uses `etl_pool` (transform/load) and `dq_pool` (validate/dq_check).
	**Metrics:** Records duration, success counters, and chunk counts via Stats.
	""",
	params={
		"rows": Param(DEFAULT_ROWS, type="integer", minimum=1, maximum=10_000_000),
		"run_name": Param(DEFAULT_RUN_NAME, type="string", minLength=1, maxLength=128),
		"chunk_rows": Param(100_000, type="integer", minimum=1, maximum=10_000_000),
		"enable_load": Param(True, type="boolean"),
		"dry_run": Param(False, type="boolean"),
		"since": Param("", type="string"),
		"until": Param("", type="string"),
		"allow_overwrite": Param(False, type="boolean"),
		"min_rows": Param(1, type="integer", minimum=0, maximum=10_000_000),
		"max_rows": Param(10_000_000, type="integer", minimum=1, maximum=10_000_000),
		"trigger_post_report": Param(False, type="boolean"),
		"downstream_dag_id": Param("", type="string"),
		"backfill_days": Param(30, type="integer", minimum=1, maximum=180),
	},
	description="Example ETL pipeline using Airflow TaskFlow API",
	tags=["example", "etl"],
	dagrun_timeout=timedelta(minutes=30),
	max_active_runs=1,
	max_active_tasks=MAX_ACTIVE_TASKS,
	concurrency=8,
	sla_miss_callback=sla_miss_callback,
	render_template_as_native_obj=True,
	on_success_callback=lambda context: (
		_cb_reset(context.get("dag").dag_id if context.get("dag") else "etl_example"),
		notify_slack(":white_check_mark: etl_example DAG succeeded")
	),
	on_failure_callback=lambda context: (
		_cb_record_failure(context.get("dag").dag_id if context.get("dag") else "etl_example"),
		notify_slack(":x: etl_example DAG failed")
	),
)
def etl_example() -> None:
	logger = get_task_logger("etl_example")

	@task(
		task_id="extract",
		execution_timeout=timedelta(minutes=5),
		on_failure_callback=on_task_failure,
		pool=ETL_POOL,
		priority_weight=3,
		doc_md="Extracts source data based on row count and optional time window parameters.",
		retries=3,
		task_concurrency=CHUNK_PARALLELISM,
	)
	def extract() -> ExtractPayload:
		"""Extract source data and prepare payload for transformation."""
		ctx = get_current_context()
		params = validate_params(ctx["params"])  # type: ignore[index]
		rows = params["rows"]
		
		with start_span("etl_example.extract", attributes={
			"rows": rows,
			"dag_run_id": str(ctx.get("run_id")),
			"since": str(params.get("since", "")),
			"until": str(params.get("until", "")),
		}):
			log_with_context(
				logger,
				logging.INFO,
				"Extracting data",
				task_id="extract",
				dag_run_id=str(ctx.get("run_id")),
				rows=rows,
				since=str(params.get("since", "")),
				until=str(params.get("until", "")),
			)
			record_extract_start()
			
			# Mark DAG run start time for total duration metric
			try:
				dag_id = ctx.get("dag").dag_id if ctx.get("dag") else "etl_example"
				run_id = ctx.get("run_id", "")
				start_ts_key = f"run_start_ts:{dag_id}:{run_id}"
				Variable.set(start_ts_key, str(pendulum.now("UTC").int_timestamp))
			except Exception as e:
				logger.warning("Failed to record run start timestamp: %s", e)
			
			payload: ExtractPayload = extract_rows(rows)
			payload["since"] = params.get("since")  # type: ignore[index]
			payload["until"] = params.get("until")  # type: ignore[index]
			
			# Volume anomaly detection
			try:
				dag_id = ctx.get("dag").dag_id if ctx.get("dag") else "etl_example"
				is_anomaly, avg_rows = _check_volume_anomaly(dag_id, rows, threshold_factor=2.0)
				if is_anomaly:
					logger.warning(
						"Volume anomaly detected",
						extra={
							"rows": rows,
							"avg_rows": avg_rows,
							"factor": rows / max(avg_rows, 1),
							"dag_id": dag_id,
						}
					)
					try:
						notify_slack(f":warning: Volume anomaly: {rows} rows (avg: {avg_rows:.0f})")
						if Stats:
							Stats.incr("etl_example.volume_anomaly", 1)
					except Exception:
						pass
				_record_volume(dag_id, rows)
			except Exception as e:
				logger.warning("Failed to check/record volume anomaly", extra={"error": str(e)})
			
			record_extract_success()
			log_with_context(
				logger,
				logging.INFO,
				"Extraction completed",
				task_id="extract",
				dag_run_id=str(ctx.get("run_id")),
				rows=rows,
			)
			return payload

	@task(task_id="validate_window", execution_timeout=timedelta(minutes=1), on_failure_callback=on_task_failure, pool=ETL_POOL, priority_weight=2)
	def validate_window() -> None:
		ctx = get_current_context()
		p = ctx["params"]  # type: ignore[index]
		since = str(p.get("since", "")).strip()
		until = str(p.get("until", "")).strip()
		max_days = int(p.get("backfill_days", 30))
		if not since and not until:
			return None
		try:
			ts_since = pendulum.parse(since) if since else None
			ts_until = pendulum.parse(until) if until else pendulum.now("UTC")
			if not ts_since:
				return None
		except Exception as e:
			raise AirflowFailException(f"Invalid since/until format; use ISO8601 e.g. 2024-10-01T00:00:00Z: {e}")
		if ts_until < ts_since:
			raise AirflowFailException("until must be >= since")
		delta_days = (ts_until - ts_since).days
		if delta_days > max_days:
			raise AirflowFailException(f"backfill window too large: {delta_days}d > {max_days}d")
		return None

	@task(task_id="transform", execution_timeout=timedelta(minutes=5), on_failure_callback=on_task_failure, pool=ETL_POOL, priority_weight=5, inlets=[RAW_DATASET], outlets=[TRANSFORMED_DATASET], retries=3, max_active_tis_per_dag=CHUNK_PARALLELISM, task_concurrency=CHUNK_PARALLELISM)
	def transform(payload: ExtractPayload) -> ExtractPayload:
		ctx = get_current_context()
		chunk_idx = str(ctx.get("map_index", ""))
		rows = int(payload.get("rows", 0))
		with start_span("etl_example.transform", attributes={
			"chunk": chunk_idx,
			"rows": rows,
		}):
			with debug_context("transform", chunk=chunk_idx):
				log_with_context(
					logger,
					logging.INFO,
					"transforming data",
					task_id="transform",
					dag_run_id=str(ctx.get("run_id", "")),
					chunk=chunk_idx,
					rows=rows,
				)
				record_transform_start()
				with track_performance("transform", report=True):
					result = apply_transform(payload)
				try:
					if Stats:
						Stats.incr("etl_example.transform.success", 1)
				except Exception:
					pass
				record_transform_success()
				return result

	@task(task_id="validate", execution_timeout=timedelta(minutes=2), on_failure_callback=on_task_failure, pool=ETL_POOL, priority_weight=7, retries=0, max_active_tis_per_dag=CHUNK_PARALLELISM, task_concurrency=CHUNK_PARALLELISM)
	def validate(payload: ExtractPayload) -> ExtractPayload:
		ctx = get_current_context()
		chunk_idx = str(ctx.get("map_index", ""))
		rows = int(payload.get("rows", 0))
		with start_span("etl_example.validate", attributes={
			"rows": rows,
			"transformed": bool(payload.get("transformed", False)),
		}):
			with debug_context("validate", chunk=chunk_idx):
				# Use plugin validation instead of manual checks
				validate_and_raise(payload, strict=False)
				# Additional business rule: rows must be > 0
				if rows <= 0:
					raise AirflowFailException("Validation failed: rows must be > 0")
				log_with_context(
					logger,
					logging.INFO,
					"validated payload",
					task_id="validate",
					dag_run_id=str(ctx.get("run_id", "")),
					chunk=chunk_idx,
					rows=rows,
					transformed=bool(payload.get("transformed", False)),
				)
				return payload

	@task(task_id="dq_check", execution_timeout=timedelta(minutes=2), on_failure_callback=on_task_failure, pool=ETL_POOL, priority_weight=8, retries=0, inlets=[VALIDATED_DATASET], outlets=[DQ_OK_DATASET], max_active_tis_per_dag=CHUNK_PARALLELISM, task_concurrency=CHUNK_PARALLELISM)
	def dq_check(payload: ExtractPayload) -> ExtractPayload:
		ctx = get_current_context()
		params = ctx["params"]  # type: ignore[index]
		rows = int(payload.get("rows", 0))
		min_rows = int(params.get("min_rows", 1))
		max_rows = int(params.get("max_rows", 10_000_000))
		chunk_idx = str(ctx.get("map_index", ""))
		with start_span("etl_example.dq_check", attributes={
			"rows": rows,
			"min_rows": min_rows,
			"max_rows": max_rows,
		}):
			with debug_context("dq_check", chunk=chunk_idx):
				# Use plugin validation with context
				validate_rows_range(rows, min_rows, max_rows, context={
					"task_id": "dq_check",
					"chunk": chunk_idx,
					"dag_run_id": str(ctx.get("run_id", "")),
				})
				log_with_context(
					logger,
					logging.INFO,
					"dq_check passed",
					task_id="dq_check",
					dag_run_id=str(ctx.get("run_id", "")),
					chunk=chunk_idx,
					rows=rows,
					min_rows=min_rows,
					max_rows=max_rows,
				)
				return payload

	@task(task_id="load", sla=timedelta(minutes=10), execution_timeout=timedelta(minutes=10), on_failure_callback=on_task_failure, inlets=[DQ_OK_DATASET], outlets=[COMPLETE_DATASET], pool=ETL_POOL, priority_weight=10, retries=2, max_active_tis_per_dag=CHUNK_PARALLELISM, task_concurrency=CHUNK_PARALLELISM)
	def load(payload: ExtractPayload) -> None:
		ctx = get_current_context()
		params_raw = ctx["params"]  # type: ignore[index]
		if bool(params_raw.get("dry_run", False)):
			log_with_context(
				logger,
				logging.INFO,
				"dry_run enabled; skipping load side-effects",
				task_id="load",
				dag_run_id=str(run_id),
				chunk=str(ctx.get("map_index", "")),
				rows=int(payload.get("rows", 0)),
			)
			return None
		run_name = str(params_raw.get("run_name", DEFAULT_RUN_NAME))
		allow_overwrite = bool(params_raw.get("allow_overwrite", False))
		dag_id = ctx.get("dag").dag_id if ctx.get("dag") else "etl_example"
		run_id = ctx.get("run_id")
		lock_key = f"idemp:{dag_id}:{params_raw.get('since','')}:{params_raw.get('until','')}:{run_id}"
		if not allow_overwrite and _idemp_should_skip(lock_key):
			log_with_context(
				logger,
				logging.WARNING,
				"idempotency lock hit; skipping load",
				task_id="load",
				dag_run_id=str(run_id),
				chunk=str(ctx.get("map_index", "")),
				lock_key=lock_key,
			)
			return None
		_idemp_set(lock_key, ttl_seconds=86400)  # 24h TTL
		start = perf_counter()
		try:
			with start_span("etl_example.load", attributes={
				"dag_id": dag_id,
				"run_id": str(run_id),
				"rows": int(payload.get("rows", 0)),
				"chunk": str(ctx.get("map_index")),
				"since": str(params_raw.get("since", "")),
				"until": str(params_raw.get("until", "")),
			}):
				log_with_context(
					logger,
					logging.INFO,
					"loading data",
					task_id="load",
					dag_run_id=str(run_id),
					chunk=str(ctx.get("map_index", "")),
					rows=int(payload.get("rows", 0)),
					run_name=run_name,
				)
				if _MLFLOW_AVAILABLE:
					try:
						if not os.getenv("MLFLOW_TRACKING_URI"):
							uri = _resolve_mlflow_uri_from_env()
							if uri:
								os.environ["MLFLOW_TRACKING_URI"] = uri
						tags = {
							"dag_id": dag_id,
							"run_id": str(run_id),
							"chunk": str(ctx.get("map_index")),
							"since": str(params_raw.get("since", "")),
							"until": str(params_raw.get("until", "")),
						}
						log_with_mlflow(payload, run_name, tags=tags)
					except Exception as ml_err:
						log_with_context(
							logger,
							logging.WARNING,
							f"mlflow logging skipped: {ml_err}",
							task_id="load",
							dag_run_id=str(run_id),
							chunk=str(ctx.get("map_index", "")),
							error=str(ml_err),
						)
			else:
				log_with_context(
					logger,
					logging.INFO,
					"mlflow not available; skipping experiment logging",
					task_id="load",
					dag_run_id=str(run_id),
					chunk=str(ctx.get("map_index", "")),
				)
		finally:
			duration_ms = int((perf_counter() - start) * 1000)
			record_load_duration_ms(duration_ms)
			record_load_success()
			try:
				if Stats:
					Stats.incr("etl_example.load.success", 1)
					# throughput metrics
					try:
						rows = int(payload.get("rows", 0))
					except Exception:
						rows = 0
					if rows > 0:
						Stats.incr("etl_example.rows_processed", rows)
						per_k_ms = int(duration_ms / max(rows / 1000.0, 0.001))
						Stats.timing("etl_example.load.ms_per_1k_rows", per_k_ms)
					# total DAG run duration metric
					try:
						dag_id = ctx.get("dag").dag_id if ctx.get("dag") else "etl_example"
						run_id = ctx.get("run_id", "")
						start_ts = int(Variable.get(f"run_start_ts:{dag_id}:{run_id}", default_var="0"))
						if start_ts > 0:
							total_ms = (pendulum.now("UTC").int_timestamp - start_ts) * 1000
							Stats.timing("etl_example.total_duration_ms", int(total_ms))
					except Exception:
						pass
			except Exception:
				pass

	@task.branch(task_id="branch")
	def branch(payload: ExtractPayload) -> str:
		ctx = get_current_context()
		params_raw = ctx["params"]  # type: ignore[index]
		enable = bool(params_raw.get("enable_load", True))
		is_dry = bool(params_raw.get("dry_run", False))
		rows = int(payload.get("rows", 0))
		return "etl_pipeline.make_chunks" if (enable and not is_dry and rows > 0) else "end"

	@task(task_id="make_chunks", execution_timeout=timedelta(minutes=2), on_failure_callback=on_task_failure, task_concurrency=CHUNK_PARALLELISM, doc_md="Splits payload into chunks for parallel processing")
	def make_chunks(payload: ExtractPayload) -> list[ExtractPayload]:
		"""Split rows into chunks for parallel processing.
		
		Respects MAX_CHUNKS limit by adjusting chunk size if needed.
		"""
		ctx = get_current_context()
		chunk_rows = int(ctx["params"].get("chunk_rows", 100_000))
		rows = int(payload.get("rows", 0))
		if rows <= 0:
			log_with_context(
				logger,
				logging.INFO,
				"make_chunks: empty payload, returning []",
				task_id="make_chunks",
				dag_run_id=str(ctx.get("run_id", "")),
				rows=rows,
			)
			return []
		if chunk_rows <= 0:
			chunk_rows = rows
			log_with_context(
				logger,
				logging.WARNING,
				"make_chunks: invalid chunk_rows, using full rows",
				task_id="make_chunks",
				dag_run_id=str(ctx.get("run_id", "")),
				chunk_rows=chunk_rows,
				rows=rows,
			)
		# Use adaptive chunk sizing to optimize parallelism
		chunk_rows = _adaptive_chunk_size(rows, MAX_CHUNKS, chunk_rows)
		chunks: list[ExtractPayload] = []
		remaining = rows
		while remaining > 0:
			part = min(chunk_rows, remaining)
			chunks.append({"rows": part, "transformed": False})
			remaining -= part
		try:
			if Stats:
				Stats.gauge("etl_example.chunks", len(chunks))
		except Exception:
			pass
		log_with_context(
			logger,
			logging.INFO,
			"make_chunks: created chunks",
			task_id="make_chunks",
			dag_run_id=str(ctx.get("run_id", "")),
			num_chunks=len(chunks),
			total_rows=rows,
			chunk_size=chunk_rows,
		)
		return chunks

	end = EmptyOperator(task_id="end", trigger_rule="none_failed_min_one_success")

	@task(
		task_id="health_check",
		execution_timeout=timedelta(minutes=1),
		on_failure_callback=on_task_failure,
		doc_md="Validates environment and dependencies before ETL starts",
	)
	def health_check() -> dict[str, Any]:
		"""Validate dependencies and environment before starting ETL.
		
		Performs comprehensive pre-flight checks including:
		- Circuit breaker status
		- MLflow availability and configuration
		- Pool utilization and capacity
		
		Returns:
			Dictionary with status ("ok", "degraded", "error") and detailed checks.
		"""
		ctx = get_current_context()
		dag_id = ctx.get("dag").dag_id if ctx.get("dag") else "etl_example"
		checks: dict[str, Any] = {"status": "ok", "checks": {}}
		
		# Check circuit breaker
		cb_open = _cb_is_open(dag_id, threshold=5, reset_minutes=15)
		checks["checks"]["circuit_breaker"] = {
			"status": "warning" if cb_open else "ok",
			"open": cb_open,
		}
		if cb_open:
			checks["status"] = "degraded"
			log_with_context(
				logger,
				logging.WARNING,
				"Circuit breaker is open - DAG may have recent failures",
				task_id="health_check",
				dag_run_id=str(ctx.get("run_id", "")),
				dag_id=dag_id,
			)
		# Check MLflow availability if needed
		if _MLFLOW_AVAILABLE:
			try:
				tracking_uri = os.getenv("MLFLOW_TRACKING_URI") or _resolve_mlflow_uri_from_env()
				checks["checks"]["mlflow"] = {
					"status": "ok" if tracking_uri else "warning",
					"uri": tracking_uri or "not_set",
				}
				if not tracking_uri:
					checks["status"] = "degraded"
					log_with_context(
						logger,
						logging.WARNING,
						"MLflow tracking URI not configured",
						task_id="health_check",
						dag_run_id=str(ctx.get("run_id", "")),
					)
			except Exception as e:
				checks["checks"]["mlflow"] = {"status": "warning", "error": str(e)}
				checks["status"] = "degraded"
				log_with_context(
					logger,
					logging.WARNING,
					"MLflow check failed",
					task_id="health_check",
					dag_run_id=str(ctx.get("run_id", "")),
					error=str(e),
				)
		else:
			checks["checks"]["mlflow"] = {"status": "ok", "available": False}
		# Check pools configuration and availability
		try:
			from airflow.models import Pool
			etl_pool = Pool.get_pool(pool_name=ETL_POOL)
			dq_pool = Pool.get_pool(pool_name=DQ_POOL)
			etl_open = etl_pool.open_slots()
			dq_open = dq_pool.open_slots()
			etl_slots = max(etl_pool.slots, 1)  # Avoid division by zero
			dq_slots = max(dq_pool.slots, 1)
			etl_utilization = (etl_pool.slots - etl_open) / etl_slots * 100
			dq_utilization = (dq_pool.slots - dq_open) / dq_slots * 100
			
			checks["checks"]["pools"] = {
				"etl_pool": {
					"slots": etl_pool.slots,
					"open": etl_open,
					"utilization": f"{etl_utilization:.1f}%",
				},
				"dq_pool": {
					"slots": dq_pool.slots,
					"open": dq_open,
					"utilization": f"{dq_utilization:.1f}%",
				},
			}
			if etl_open == 0 or dq_open == 0:
				checks["status"] = "degraded"
				log_with_context(
					logger,
					logging.WARNING,
					"Pool capacity exhausted",
					task_id="health_check",
					dag_run_id=str(ctx.get("run_id", "")),
					etl_open=etl_open,
					dq_open=dq_open,
					dag_id=dag_id,
				)
		except Exception as e:
			checks["checks"]["pools"] = {"status": "warning", "error": str(e)}
			checks["status"] = "degraded"
			log_with_context(
				logger,
				logging.WARNING,
				"Failed to check pool status",
				task_id="health_check",
				dag_run_id=str(ctx.get("run_id", "")),
				error=str(e),
			)
		
		# Log final status
		if checks["status"] != "ok":
			log_with_context(
				logger,
				logging.WARNING,
				"Health check found issues",
				task_id="health_check",
				dag_run_id=str(ctx.get("run_id", "")),
				**checks,
			)
		else:
			log_with_context(
				logger,
				logging.INFO,
				"Health check completed successfully",
				task_id="health_check",
				dag_run_id=str(ctx.get("run_id", "")),
				**checks,
			)
		
		return checks

	with TaskGroup(group_id="etl_pipeline") as etl_pipeline:
		extracted = extract()
		chunked = make_chunks(extracted)
		transformed = transform.expand(payload=chunked)
		validated = validate.expand(payload=transformed)
		checked = dq_check.expand(payload=validated)
		load.expand(payload=checked)

	guard = validate_window()
	health = health_check()
	br = branch(extracted)
	guard >> health
	health >> br
	br >> etl_pipeline

	trigger_post = TriggerDagRunOperator(
		task_id="trigger_post_etl_report",
		trigger_dag_id="post_etl_report",
		trigger_rule="none_failed_min_one_success",
		reset_dag_run=True,
		conf={
			"source": "etl_example",
			"since": "{{ params.since }}",
			"until": "{{ params.until }}",
			"run_id": "{{ run_id }}",
		},
	)

	@task.branch(task_id="branch_post")
	def branch_post() -> str:
		ctx = get_current_context()
		return "trigger_post_etl_report" if bool(ctx["params"].get("trigger_post_report", False)) else "end"

	post = branch_post()
	etl_pipeline >> post
	post >> trigger_post
	post >> end

	@task(task_id="notify_summary", trigger_rule="none_failed_min_one_success")
	def notify_summary(rows: int) -> None:
		try:
			dag_ctx = get_current_context()
			dag_id = dag_ctx.get("dag").dag_id if dag_ctx.get("dag") else "etl_example"
			run_id = dag_ctx.get("run_id", "")
			start_ts = int(Variable.get(f"run_start_ts:{dag_id}:{run_id}", default_var="0"))
			dur_ms = 0
			if start_ts > 0:
				dur_ms = (pendulum.now("UTC").int_timestamp - start_ts) * 1000
			msg = f":white_check_mark: etl_example done | rows={rows} | total_ms={dur_ms}"
			notify_slack(msg)
		except Exception:
			pass

	summary = notify_summary(extracted["rows"])  # type: ignore[index]
	trigger_post >> summary
	end >> summary
	return None


dag = etl_example()

