from __future__ import annotations

from datetime import timedelta
import logging
from typing import Dict, Any
from time import perf_counter
import os

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
MAX_ACTIVE_TASKS = int(os.getenv("MAX_ACTIVE_TASKS", "32"))
CHUNK_PARALLELISM = int(os.getenv("CHUNK_PARALLELISM", "16"))


def _resolve_mlflow_uri_from_env() -> str | None:
	"""Attempt to resolve MLflow URI from environments/<env>.yaml (domains.mlflow)."""
	try:
		env = os.getenv("ENV", os.getenv("AIRFLOW_ENV", "dev")).lower()
		root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
		env_file = os.path.join(root, "environments", f"{env}.yaml")
		if not os.path.exists(env_file):
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
			return None
		return f"https://{domain}"
	except Exception:
		return None


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

	- `rows` (int): number of rows to simulate
	- `run_name` (str): mlflow run name
	- `chunk_rows` (int, optional): max rows per chunk for parallelism (default 100000)
	Triggers when `dataset://source_ready` is updated.
	""",
	params={
		"rows": Param(DEFAULT_ROWS, type="integer", minimum=1, maximum=10_000_000),
		"run_name": Param(DEFAULT_RUN_NAME, type="string", minLength=1, maxLength=128),
		"chunk_rows": Param(100_000, type="integer", minimum=1, maximum=10_000_000),
		"enable_load": Param(True, type="boolean"),
		"since": Param("", type="string"),
		"until": Param("", type="string"),
		"allow_overwrite": Param(False, type="boolean"),
		"min_rows": Param(1, type="integer", minimum=0, maximum=10_000_000),
		"max_rows": Param(10_000_000, type="integer", minimum=1, maximum=10_000_000),
		"trigger_post_report": Param(False, type="boolean"),
		"downstream_dag_id": Param("", type="string"),
	},
	description="Example ETL pipeline using Airflow TaskFlow API",
	tags=["example", "etl"],
	dagrun_timeout=timedelta(minutes=30),
	max_active_runs=1,
	max_active_tasks=MAX_ACTIVE_TASKS,
	concurrency=8,
	sla_miss_callback=sla_miss_callback,
	render_template_as_native_obj=True,
	on_success_callback=lambda context: notify_slack(":white_check_mark: etl_example DAG succeeded"),
	on_failure_callback=lambda context: notify_slack(":x: etl_example DAG failed"),
)
def etl_example() -> None:
	logger = logging.getLogger("airflow.task")

	@task(task_id="extract", execution_timeout=timedelta(minutes=5), on_failure_callback=on_task_failure, pool=ETL_POOL, priority_weight=3, doc_md="Extracts source data", retries=3)
	def extract() -> ExtractPayload:
		ctx = get_current_context()
		params = validate_params(ctx["params"])  # type: ignore[index]
		rows = params["rows"]
		logger.info("extracting data...", extra={"rows": rows, "since": params.get("since"), "until": params.get("until"), "dag_run_id": ctx.get("run_id")})
		record_extract_start()
		payload: ExtractPayload = extract_rows(rows)
		payload["since"] = params.get("since")  # type: ignore[index]
		payload["until"] = params.get("until")  # type: ignore[index]
		record_extract_success()
		return payload

	@task(task_id="transform", execution_timeout=timedelta(minutes=5), on_failure_callback=on_task_failure, pool=ETL_POOL, priority_weight=5, inlets=[RAW_DATASET], outlets=[TRANSFORMED_DATASET], retries=3, max_active_tis_per_dag=CHUNK_PARALLELISM)
	def transform(payload: ExtractPayload) -> ExtractPayload:
		ctx = get_current_context()
		logger.info("transforming data", extra={"component": "transform", "chunk": ctx.get("map_index")})
		record_transform_start()
		start = perf_counter()
		result = apply_transform(payload)
		duration_ms = int((perf_counter() - start) * 1000)
		logger.info("transform done", extra={"component": "transform", "chunk": ctx.get("map_index"), "duration_ms": duration_ms})
		try:
			if Stats:
				Stats.timing("etl_example.transform.duration_ms", duration_ms)
				Stats.incr("etl_example.transform.success", 1)
		except Exception:
			pass
		record_transform_success()
		return result

	@task(task_id="validate", execution_timeout=timedelta(minutes=2), on_failure_callback=on_task_failure, pool=ETL_POOL, priority_weight=7, retries=0, max_active_tis_per_dag=CHUNK_PARALLELISM)
	def validate(payload: ExtractPayload) -> ExtractPayload:
		if not isinstance(payload, dict):
			raise AirflowFailException("Validation failed: payload must be a dict")
		if "rows" not in payload or not isinstance(payload["rows"], int):
			raise AirflowFailException("Validation failed: 'rows' must be int")
		if "transformed" not in payload or not isinstance(payload["transformed"], bool):
			raise AirflowFailException("Validation failed: 'transformed' must be bool")
		rows = int(payload["rows"])
		if rows <= 0:
			raise AirflowFailException("Validation failed: rows must be > 0")
		logger.info("validated payload", extra={"component": "validate", "rows": rows, "transformed": payload["transformed"]})
		return payload

	@task(task_id="dq_check", execution_timeout=timedelta(minutes=2), on_failure_callback=on_task_failure, pool=ETL_POOL, priority_weight=8, retries=0, inlets=[VALIDATED_DATASET], outlets=[DQ_OK_DATASET], max_active_tis_per_dag=CHUNK_PARALLELISM)
	def dq_check(payload: ExtractPayload) -> ExtractPayload:
		ctx = get_current_context()
		params = ctx["params"]  # type: ignore[index]
		rows = int(payload.get("rows", 0))
		min_rows = int(params.get("min_rows", 1))
		max_rows = int(params.get("max_rows", 10_000_000))
		if rows < min_rows:
			raise AirflowFailException(f"DQ failed: rows {rows} < min_rows {min_rows}")
		if rows > max_rows:
			raise AirflowFailException(f"DQ failed: rows {rows} > max_rows {max_rows}")
		logger.info("dq_check passed", extra={"component": "dq", "rows": rows, "min": min_rows, "max": max_rows})
		return payload

	@task(task_id="load", sla=timedelta(minutes=10), execution_timeout=timedelta(minutes=10), on_failure_callback=on_task_failure, inlets=[DQ_OK_DATASET], outlets=[COMPLETE_DATASET], pool=ETL_POOL, priority_weight=10, retries=2, max_active_tis_per_dag=CHUNK_PARALLELISM)
	def load(payload: ExtractPayload) -> None:
		ctx = get_current_context()
		run_name = str(ctx["params"].get("run_name", DEFAULT_RUN_NAME))
		params_raw = ctx["params"]  # type: ignore[index]
		allow_overwrite = bool(params_raw.get("allow_overwrite", False))
		dag_id = ctx.get("dag").dag_id if ctx.get("dag") else "etl_example"
		run_id = ctx.get("run_id")
		lock_key = f"idemp:{dag_id}:{params_raw.get('since','')}:{params_raw.get('until','')}:{run_id}"
		if not allow_overwrite and Variable.get(lock_key, default_var=None):
			logging.getLogger("airflow.task").warning("idempotency lock hit; skipping load", extra={"key": lock_key})
			return None
		Variable.set(lock_key, "1")
		start = perf_counter()
		try:
			logger.info("loading data", extra={"component": "load", "rows": payload.get("rows"), "run": run_name, "chunk": ctx.get("map_index")})
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
					logger.warning("mlflow logging skipped: %s", ml_err)
			else:
				logger.info("mlflow not available; skipping experiment logging")
		finally:
			duration_ms = int((perf_counter() - start) * 1000)
			record_load_duration_ms(duration_ms)
			record_load_success()
			try:
				if Stats:
					Stats.incr("etl_example.load.success", 1)
			except Exception:
				pass

	@task.branch(task_id="branch")
	def branch(payload: ExtractPayload) -> str:
		ctx = get_current_context()
		enable = bool(ctx["params"].get("enable_load", True))
		rows = int(payload.get("rows", 0))
		return "etl_pipeline.make_chunks" if enable and rows > 0 else "end"

	@task(task_id="make_chunks", execution_timeout=timedelta(minutes=2), on_failure_callback=on_task_failure)
	def make_chunks(payload: ExtractPayload) -> list[ExtractPayload]:
		ctx = get_current_context()
		chunk_rows = int(ctx["params"].get("chunk_rows", 100_000))
		rows = int(payload.get("rows", 0))
		if rows <= 0:
			return []
		if chunk_rows <= 0:
			chunk_rows = rows
		chunks: list[ExtractPayload] = []
		remaining = rows
		while remaining > 0:
			part = min(chunk_rows, remaining)
			chunks.append({"rows": part, "transformed": False})
			remaining -= part
		return chunks

	end = EmptyOperator(task_id="end", trigger_rule="none_failed_min_one_success")

	with TaskGroup(group_id="etl_pipeline") as etl_pipeline:
		extracted = extract()
		chunked = make_chunks(extracted)
		transformed = transform.expand(payload=chunked)
		validated = validate.expand(payload=transformed)
		checked = dq_check.expand(payload=validated)
		load.expand(payload=checked)

	br = branch(extracted)
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
	return None


dag = etl_example()
