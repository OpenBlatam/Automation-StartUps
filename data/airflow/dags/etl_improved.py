from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass
import time
from datetime import timedelta
from typing import Any, Dict, List, Tuple
from urllib import request

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.stats import Stats
from psycopg import sql
from airflow.models import Variable
try:
    from airflow.datasets import Dataset  # Airflow 2.5+
except Exception:
    Dataset = None  # type: ignore
try:
	import psycopg.extras as pg_extras  # type: ignore
except Exception:
	pg_extras = None  # type: ignore
try:
	import psycopg.errors as pg_errors  # type: ignore
except Exception:
	pg_errors = None  # type: ignore
try:
	import mlflow  # type: ignore
	_MLFLOW = True
except Exception:
	_MLFLOW = False

try:
	from plugins.db import get_conn  # type: ignore
except Exception:  # pragma: no cover - airflow runtime will surface import errors
	get_conn = None  # type: ignore


@dataclass(frozen=True)
class Record:
    """Simple record type for clarity and typing."""
    pk: str
    timestamp: str
    attributes: Dict[str, Any]


# Optional Pydantic validation
try:
    from pydantic import BaseModel, Field  # type: ignore

    class RecordModel(BaseModel):  # type: ignore
        pk: str = Field(min_length=1)
        timestamp: str = Field(min_length=1)
        attributes: Dict[str, Any]

    def _validate_record(r: Record) -> None:
        RecordModel(pk=r.pk, timestamp=r.timestamp, attributes=r.attributes)

except Exception:  # pragma: no cover
    def _validate_record(r: Record) -> None:  # type: ignore
        return


def _stable_hash(*parts: str) -> str:
	joined = "|".join(parts)
	return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def _on_sla_miss(dag, task_list, blocking_task_list, slas, blocking_tis, *_, **__):  # type: ignore
	_webhook = os.environ.get("SLACK_WEBHOOK")
	if not _webhook:
		return
	try:
		text = f":warning: SLA missed in {dag.dag_id}: tasks={[t.task_id for t in task_list]}"
		payload = json.dumps({"text": text}).encode()
		req = request.Request(_webhook, data=payload, headers={"Content-Type": "application/json"})
		request.urlopen(req, timeout=5)
	except Exception:
		pass


@dag(
	dag_id="etl_improved",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule="@daily",
	catchup=False,
	default_args={
		"owner": "data-eng",
		"retries": 2,
		"retry_delay": timedelta(minutes=3),
		"retry_exponential_backoff": True,
		"max_retry_delay": timedelta(minutes=15),
		"depends_on_past": False,
		"email_on_failure": False,
		"email_on_retry": False,
	},
	dagrun_timeout=timedelta(minutes=45),
	max_active_runs=1,
	description="Improved ETL with idempotent load and observability",
	params={
		"batch_size": 500,
		"run_label": "etl_improved",
		"chunk_size": 500,
		"schema_name": "public",
		"table_name": "etl_improved_events",
		"audit_table_name": "etl_improved_audit",
		"min_acceptance_ratio": 1.0,
		"enforce_ge": False,
        "mlflow_enable": False,
        "mlflow_experiment": "etl_improved",
        "dry_run": False,
	},
	tags=["etl", "improved"],
 	sla_miss_callback=_on_sla_miss,
)
def etl_improved() -> None:
	logger = logging.getLogger("airflow.task")

	def _on_failure(context: Dict[str, Any]) -> None:
		ti = context.get("task_instance")
		task_id = ti.task_id if ti else "unknown"
		Stats.incr("etl_improved.task_failure", 1, tags={"task": task_id})
		logger.error("task failed: %s", task_id)
		_webhook = os.environ.get("SLACK_WEBHOOK")
		if _webhook:
			try:
				payload = json.dumps({"text": f":rotating_light: etl_improved task failed: {task_id}"}).encode()
				req = request.Request(_webhook, data=payload, headers={"Content-Type": "application/json"})
				request.urlopen(req, timeout=5)
			except Exception as _:
				# best-effort notification
				pass

	@task(task_id="extract", execution_timeout=timedelta(minutes=5), on_failure_callback=_on_failure, doc_md="Extract batched records deterministically for idempotency", pool=os.environ.get("ETL_POOL"))
	def extract() -> List[Record]:
		start = time.monotonic()
		ctx = get_current_context()
		exec_date = str(ctx["data_interval_start"])  # stable across retries
		batch_size = int(ctx["params"].get("batch_size") or Variable.get("etl_improved__batch_size", 500))
		Stats.incr("etl_improved.extract.start")
		records: List[Record] = []
		for i in range(batch_size):
			pk = _stable_hash(exec_date, str(i))[:16]
			rec = Record(
				Record(
					pk=pk,
					timestamp=exec_date,
					attributes={"index": i, "source": "synthetic", "version": 1},
				)
			)
			_validate_record(rec)
			records.append(rec)
		Stats.incr("etl_improved.extract.success")
		Stats.timing("etl_improved.extract.ms", int((time.monotonic() - start) * 1000))
		return records

	@task(task_id="transform", execution_timeout=timedelta(minutes=5), on_failure_callback=_on_failure, doc_md="Enrich records and compute deterministic fingerprints (uses Polars if available)", pool=os.environ.get("ETL_POOL"))
	def transform(records: List[Record]) -> List[Tuple[str, str, str]]:
		start = time.monotonic()
		Stats.incr("etl_improved.transform.start")
		# Try Polars for vectorized transform
		try:
			import polars as pl  # type: ignore
			df = pl.DataFrame(
				{
					"pk": [r.pk for r in records],
					"timestamp": [r.timestamp for r in records],
					"attributes": [r.attributes for r in records],
				}
			)
			# compute fingerprint deterministically
			def _fp(attrs: Dict[str, Any], pk: str, ts: str) -> str:
				return _stable_hash(pk, ts, json.dumps(attrs, sort_keys=True))[:16]
			df = df.with_columns(
				pl.struct(["attributes", "pk", "timestamp"]).map_elements(
					lambda s: _fp(s["attributes"], s["pk"], s["timestamp"])
				).alias("fingerprint")
			)
			# merge fingerprint into attributes and serialize
			def _merge_and_dump(attrs: Dict[str, Any], fp: str) -> str:
				a = dict(attrs)
				a["fingerprint"] = fp
				return json.dumps(a, sort_keys=True)
			df = df.with_columns(
				pl.struct(["attributes", "fingerprint"]).map_elements(
					lambda s: _merge_and_dump(s["attributes"], s["fingerprint"])
				).alias("attributes_json")
			)
			output = list(zip(df["pk"].to_list(), df["timestamp"].to_list(), df["attributes_json"].to_list()))
		except Exception:
			# fallback to Python
			output: List[Tuple[str, str, str]] = []
			for r in records:
				fingerprint = _stable_hash(r.pk, r.timestamp, json.dumps(r.attributes, sort_keys=True))[:16]
				attrs = dict(r.attributes)
				attrs["fingerprint"] = fingerprint
				output.append((r.pk, r.timestamp, json.dumps(attrs, sort_keys=True)))
		Stats.incr("etl_improved.transform.success")
		Stats.timing("etl_improved.transform.ms", int((time.monotonic() - start) * 1000))
		return output

	@task(task_id="validate", execution_timeout=timedelta(minutes=3), on_failure_callback=_on_failure, doc_md="Basic data quality checks: non-empty, unique pk, fingerprint present", pool=os.environ.get("ETL_POOL"))
	def validate(rows: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]:
		start = time.monotonic()
		Stats.incr("etl_improved.validate.start")
		if not rows:
			raise ValueError("no rows produced by transform")
		pks = [r[0] for r in rows]
		if len(set(pks)) != len(pks):
			raise ValueError("duplicate primary keys detected in batch")
		for _, __, attrs_json in rows:
			attrs = json.loads(attrs_json)
			if "fingerprint" not in attrs or not attrs["fingerprint"]:
				raise ValueError("missing fingerprint in attributes")
		Stats.incr("etl_improved.validate.success")
		Stats.timing("etl_improved.validate.ms", int((time.monotonic() - start) * 1000))
		return rows

	@task(task_id="ge_validate", execution_timeout=timedelta(minutes=5), on_failure_callback=_on_failure, doc_md="Optional Great Expectations validation if library is available", pool=os.environ.get("ETL_POOL"))
	def ge_validate(rows: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]:
		start = time.monotonic()
		ctx = get_current_context()
		enforce_ge = bool(ctx["params"].get("enforce_ge") or Variable.get("etl_improved__enforce_ge", default_var=False))
		try:
			import pandas as pd  # type: ignore
			import great_expectations as ge  # type: ignore
			from great_expectations.core.batch import RuntimeBatchRequest  # type: ignore
			from great_expectations.core.expectation_suite import ExpectationSuite  # type: ignore
			df = pd.DataFrame(rows, columns=["pk", "event_time", "attributes_json"])  # type: ignore
			gdf = ge.from_pandas(df)  # type: ignore
			gdf.expect_column_values_to_not_be_null("pk")
			gdf.expect_column_values_to_be_unique("pk")
			# basic presence check for fingerprint in JSON string
			gdf.expect_column_values_to_match_regex("attributes_json", r"\"fingerprint\":\s*\"[a-f0-9]{1,}\"")
			result = gdf.validate()  # type: ignore
			passed = bool(result.get("success", False))
			Stats.incr("etl_improved.ge_validate.success" if passed else "etl_improved.ge_validate.fail")
			if not passed:
				raise ValueError("Great Expectations validation failed")
		except Exception:
			# If GE unavailable or error
			if enforce_ge:
				raise
			Stats.incr("etl_improved.ge_validate.skipped")
		finally:
			Stats.timing("etl_improved.ge_validate.ms", int((time.monotonic() - start) * 1000))
		return rows

	@task(task_id="chunk", execution_timeout=timedelta(minutes=3), on_failure_callback=_on_failure, doc_md="Split transformed rows into chunks for parallel loading", pool=os.environ.get("ETL_POOL"))
	def chunk(rows: List[Tuple[str, str, str]]) -> List[List[Tuple[str, str, str]]]:
		ctx = get_current_context()
		size = int(ctx["params"].get("chunk_size") or Variable.get("etl_improved__chunk_size", 500))
		if size <= 0:
			size = len(rows) if rows else 1
		chunks: List[List[Tuple[str, str, str]]] = []
		for i in range(0, len(rows), size):
			chunks.append(rows[i : i + size])
		Stats.incr("etl_improved.chunk.success", 1, tags={"num_chunks": str(len(chunks))})
		return chunks

	@task(task_id="load", sla=timedelta(minutes=15), execution_timeout=timedelta(minutes=10), on_failure_callback=_on_failure, doc_md="Idempotent upsert into Postgres using primary key", outlets=[Dataset("postgres://etl_improved/etl_improved_events")] if Dataset else None, pool=os.environ.get("ETL_POOL"))
	def load(rows: List[Tuple[str, str, str]]) -> int:
		start = time.monotonic()
		ctx = get_current_context()
		run_label = str(ctx["params"].get("run_label") or Variable.get("etl_improved__run_label", "etl_improved"))
		schema_name = str(ctx["params"].get("schema_name") or Variable.get("etl_improved__schema_name", "public"))
		table_name = str(ctx["params"].get("table_name") or Variable.get("etl_improved__table_name", "etl_improved_events"))
		audit_table_name = str(ctx["params"].get("audit_table_name") or Variable.get("etl_improved__audit_table_name", "etl_improved_audit"))
		dry_run = bool(ctx["params"].get("dry_run") or Variable.get("etl_improved__dry_run", False))
		Stats.incr("etl_improved.load.start")
		# If dry_run, skip DB operations but return row count
		if dry_run:
			Stats.incr("etl_improved.load.dry_run", 1, tags={"rows": str(len(rows))})
			Stats.timing("etl_improved.load.ms", int((time.monotonic() - start) * 1000))
			return len(rows)
		if get_conn is None:
			raise RuntimeError("plugins.db.get_conn not available")
		# Use single transaction for atomicity; apply session settings
		with get_conn() as conn:
			with conn.cursor() as cur:
				# Apply statement_timeout if configured
				timeout_ms = int(ctx["params"].get("db_statement_timeout_ms") or Variable.get("etl_improved__db_statement_timeout_ms", 0))
				if timeout_ms and timeout_ms > 0:
					cur.execute(sql.SQL("SET LOCAL statement_timeout = %s;"), (timeout_ms,))
				# ensure schema exists
				cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {};").format(sql.Identifier(schema_name)))
				# create target table if needed
				cur.execute(
					sql.SQL(
						"""
						CREATE TABLE IF NOT EXISTS {}.{} (
							pk TEXT PRIMARY KEY,
							event_time TIMESTAMPTZ NOT NULL,
							attributes JSONB NOT NULL,
							inserted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
							updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
						);
						"""
					).format(sql.Identifier(schema_name), sql.Identifier(table_name))
				)
                # supporting index for common time filters
                cur.execute(
                    sql.SQL(
                        """
                        DO $$
                        BEGIN
                            IF NOT EXISTS (
                                SELECT 1 FROM pg_class c
                                JOIN pg_namespace n ON n.oid = c.relnamespace
                                WHERE c.relname = %s AND n.nspname = %s
                            ) THEN
                                EXECUTE format('CREATE INDEX %I ON %I.%I (event_time);',
                                               %s, %s, %s);
                            END IF;
                        END$$;
                        """
                    ),
                    (
                        f"{table_name}_event_time_idx",
                        schema_name,
                        f"{table_name}_event_time_idx",
                        schema_name,
                        table_name,
                    ),
                )
				# Upsert in batches with transient error retry
				if rows:
					max_tries = int(ctx["params"].get("db_max_retries") or Variable.get("etl_improved__db_max_retries", 3))
					base_sleep_ms = int(ctx["params"].get("db_retry_initial_ms") or Variable.get("etl_improved__db_retry_initial_ms", 200))
					page_size = int(ctx["params"].get("db_page_size") or Variable.get("etl_improved__db_page_size", 1000))
					attempt = 0
					while True:
						try:
							if pg_extras and hasattr(pg_extras, "execute_values"):
								template = sql.SQL(
									"""
									INSERT INTO {}.{} (pk, event_time, attributes)
									VALUES %s
									ON CONFLICT (pk) DO UPDATE SET
										event_time = EXCLUDED.event_time,
										attributes = EXCLUDED.attributes,
										updated_at = NOW();
									"""
								).format(sql.Identifier(schema_name), sql.Identifier(table_name))
								pg_extras.execute_values(cur, template.as_string(cur), rows, page_size=page_size)
							else:
								args_str = ",".join(["(%s,%s,%s)"] * len(rows))
								flat: List[Any] = []
								for pk, ts, attrs in rows:
									flat.extend([pk, ts, attrs])
								cur.execute(
									sql.SQL(
										"""
										INSERT INTO {}.{} (pk, event_time, attributes)
										VALUES {values}
										ON CONFLICT (pk) DO UPDATE SET
											event_time = EXCLUDED.event_time,
											attributes = EXCLUDED.attributes,
											updated_at = NOW();
										"""
									).format(
										sql.Identifier(schema_name),
										sql.Identifier(table_name),
										values=sql.SQL(args_str),
									),
									flat,
								)
							break
						except Exception as db_err:
							# Retry only on transient errors if classification available
							if pg_errors and not isinstance(db_err, (pg_errors.SerializationFailure, pg_errors.DeadlockDetected)):
								raise
							attempt += 1
							if attempt > max_tries:
								raise
							sleep_s = (base_sleep_ms / 1000.0) * (2 ** (attempt - 1))
							Stats.incr("etl_improved.load.retry", 1, tags={"attempt": str(attempt)})
							time.sleep(sleep_s)
					# audit table
					cur.execute(
						sql.SQL(
							"""
							CREATE TABLE IF NOT EXISTS {}.{} (
								id BIGSERIAL PRIMARY KEY,
								run_label TEXT NOT NULL,
								num_rows INT NOT NULL,
								at TIMESTAMPTZ NOT NULL DEFAULT NOW()
							);
							INSERT INTO {}.{} (run_label, num_rows) VALUES (%s, %s);
							"""
						).format(
							sql.Identifier(schema_name),
							sql.Identifier(audit_table_name),
							sql.Identifier(schema_name),
							sql.Identifier(audit_table_name),
						),
						(run_label, len(rows)),
					)
		Stats.incr("etl_improved.load.success", 1, tags={"rows": str(len(rows))})
		Stats.timing("etl_improved.load.ms", int((time.monotonic() - start) * 1000))
		return len(rows)

	# Dynamic task mapping over chunks -> validate -> load
	_chunks = chunk(transform(extract()))
	_validated = validate.expand(rows=_chunks)
	_ge_validated = ge_validate.expand(rows=_validated)
	_counts = load.expand(rows=_ge_validated)

	@task(task_id="finalize", execution_timeout=timedelta(minutes=3), on_failure_callback=_on_failure, doc_md="Verify that loaded rows meet acceptance ratio and persist metrics")
	def finalize(counts: List[int]) -> None:
		start = time.monotonic()
		ctx = get_current_context()
		expected = int(ctx["params"].get("batch_size") or Variable.get("etl_improved__batch_size", 500))
		min_ratio = float(ctx["params"].get("min_acceptance_ratio") or Variable.get("etl_improved__min_acceptance_ratio", 1.0))
		total = int(sum(counts)) if counts else 0
		ratio = (total / expected) if expected else 0.0
		run_label = str(ctx["params"].get("run_label") or Variable.get("etl_improved__run_label", "etl_improved"))
		schema_name = str(ctx["params"].get("schema_name") or Variable.get("etl_improved__schema_name", "public"))
		dry_run = bool(ctx["params"].get("dry_run") or Variable.get("etl_improved__dry_run", False))
		metrics_table = "etl_improved_metrics"
		Stats.incr("etl_improved.finalize.start")
		Stats.incr("etl_improved.finalize.success", 1, tags={"total": str(total), "expected": str(expected)})
		Stats.timing("etl_improved.finalize.ms", int((time.monotonic() - start) * 1000))
		# persist metrics (best-effort)
		try:
			if get_conn is None:
				raise RuntimeError("plugins.db.get_conn not available")
			with get_conn() as conn:
				with conn.cursor() as cur:
					cur.execute(
						sql.SQL(
							"""
							CREATE TABLE IF NOT EXISTS {}.{} (
								id BIGSERIAL PRIMARY KEY,
								run_label TEXT NOT NULL,
								total_rows INT NOT NULL,
								expected_rows INT NOT NULL,
								ratio DOUBLE PRECISION NOT NULL,
								num_chunks INT NOT NULL,
								dry_run BOOLEAN NOT NULL DEFAULT FALSE,
								at TIMESTAMPTZ NOT NULL DEFAULT NOW()
							);
							"""
						).format(sql.Identifier(schema_name), sql.Identifier(metrics_table))
					)
					# ensure column exists if table was created previously without it
					cur.execute(
						sql.SQL("ALTER TABLE {}.{} ADD COLUMN IF NOT EXISTS dry_run BOOLEAN NOT NULL DEFAULT FALSE;").format(
							sql.Identifier(schema_name), sql.Identifier(metrics_table)
						)
					)
					cur.execute(
						sql.SQL(
							"""
							INSERT INTO {}.{} (run_label, total_rows, expected_rows, ratio, num_chunks, dry_run)
							VALUES (%s, %s, %s, %s, %s, %s);
							"""
						).format(sql.Identifier(schema_name), sql.Identifier(metrics_table)),
						(run_label, total, expected, ratio, len(counts) if counts else 0, dry_run),
					)
		except Exception:
			# do not fail finalize due to metrics persistence
			pass
		if ratio < min_ratio:
			raise ValueError(f"acceptance ratio too low: {ratio:.3f} < {min_ratio:.3f}")

		# optional MLflow logging
		try:
			mlflow_enable = bool(ctx["params"].get("mlflow_enable") or Variable.get("etl_improved__mlflow_enable", False))
			mlflow_experiment = str(ctx["params"].get("mlflow_experiment") or Variable.get("etl_improved__mlflow_experiment", "etl_improved"))
			if mlflow_enable and _MLFLOW:
				tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
				if tracking_uri:
					mlflow.set_tracking_uri(tracking_uri)
				mlflow.set_experiment(mlflow_experiment)
				with mlflow.start_run(run_name=run_label):
					mlflow.log_param("dag", "etl_improved")
					mlflow.log_param("task", "finalize")
					mlflow.log_param("dry_run", str(dry_run))
					mlflow.log_metric("total_rows", float(total))
					mlflow.log_metric("expected_rows", float(expected))
					mlflow.log_metric("ratio", float(ratio))
					mlflow.log_param("num_chunks", str(len(counts) if counts else 0))
		except Exception:
			pass

	finalize(_counts)
	return None


dag = etl_improved()


