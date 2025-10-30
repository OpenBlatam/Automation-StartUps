from __future__ import annotations

import logging
from datetime import timedelta
import os
import json
from urllib import request
from typing import Any, Dict

import pendulum
from airflow.decorators import dag, task
from airflow.stats import Stats

try:
	from airflow.datasets import Dataset  # Airflow 2.5+
except Exception:
	Dataset = None  # type: ignore

try:
	from plugins.db import get_conn  # type: ignore
except Exception:
	get_conn = None  # type: ignore


DATASET_URI = "postgres://etl_improved/etl_improved_events"


@dag(
	dag_id="etl_consumer",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule=[Dataset(DATASET_URI)] if Dataset else None,
	catchup=False,
	default_args={
		"owner": "data-eng",
		"retries": 1,
		"retry_delay": timedelta(minutes=2),
	},
	description="Consumer DAG triggered by dataset from etl_improved; summarizes latest metrics",
	params={
		"trend_window": 7,
		"drop_threshold_pct": 20.0,
	},
	tags=["etl", "consumer"],
)
def etl_consumer() -> None:
	logger = logging.getLogger("airflow.task")

	@task(task_id="summarize_metrics", execution_timeout=timedelta(minutes=5))
	def summarize_metrics() -> None:
		if get_conn is None:
			raise RuntimeError("plugins.db.get_conn not available")
		with get_conn() as conn:
			with conn.cursor() as cur:
				cur.execute(
					"""
					CREATE SCHEMA IF NOT EXISTS public;
					CREATE TABLE IF NOT EXISTS public.etl_improved_metrics (
						id BIGSERIAL PRIMARY KEY,
						run_label TEXT NOT NULL,
						total_rows INT NOT NULL,
						expected_rows INT NOT NULL,
						ratio DOUBLE PRECISION NOT NULL,
						num_chunks INT NOT NULL,
						at TIMESTAMPTZ NOT NULL DEFAULT NOW()
					);
					"""
				)
				cur.execute(
					"""
					SELECT run_label, total_rows, expected_rows, ratio, num_chunks, at
					FROM public.etl_improved_metrics
					ORDER BY at DESC
					LIMIT 1;
					"""
				)
				row = cur.fetchone()
				if not row:
					logger.info("no metrics yet")
					return
				run_label, total_rows, expected_rows, ratio, num_chunks, at = row
				logger.info(
					"latest metrics: run=%s total=%s expected=%s ratio=%.3f chunks=%s at=%s",
					run_label,
					total_rows,
					expected_rows,
					ratio,
					num_chunks,
					str(at),
				)
				if float(ratio) < 1.0:
					webhook = os.environ.get("SLACK_WEBHOOK")
					if webhook:
						try:
							payload = json.dumps({"text": f":warning: etl_consumer low ratio {ratio:.3f} for run {run_label}"}).encode()
							req = request.Request(webhook, data=payload, headers={"Content-Type": "application/json"})
							request.urlopen(req, timeout=5)
						except Exception:
							pass
					# persist alert event
					try:
						cur.execute(
							"""
							CREATE TABLE IF NOT EXISTS public.etl_improved_alerts (
								id BIGSERIAL PRIMARY KEY,
								kind TEXT NOT NULL,
								message TEXT NOT NULL,
								run_label TEXT,
								ratio DOUBLE PRECISION,
								avg_ratio DOUBLE PRECISION,
								threshold_pct DOUBLE PRECISION,
								at TIMESTAMPTZ NOT NULL DEFAULT NOW()
							);
							"""
						)
						cur.execute(
							"""
							INSERT INTO public.etl_improved_alerts (kind, message, run_label, ratio)
							VALUES (%s, %s, %s, %s);
							""",
							("low_ratio", f"low ratio {ratio:.3f} for run {run_label}", run_label, float(ratio)),
						)
					except Exception:
						pass
				# Trend detection over recent window (excluding latest)
				window = 7
				try:
					from airflow.operators.python import get_current_context  # lazy import for context
					ctx = get_current_context()
					window = int(ctx["params"].get("trend_window", 7))
				except Exception:
					pass
				if window > 0:
					cur.execute(
						"""
						SELECT ratio
						FROM public.etl_improved_metrics
						WHERE at < %s
						ORDER BY at DESC
						LIMIT %s;
						""",
						(at, window),
					)
					rows = cur.fetchall()
					if rows:
						avg_ratio = sum(r[0] for r in rows) / float(len(rows))
						threshold = 20.0
						try:
							from airflow.operators.python import get_current_context  # reuse
							ctx = get_current_context()
							threshold = float(ctx["params"].get("drop_threshold_pct", 20.0))
						except Exception:
							pass
						if avg_ratio > 0 and float(ratio) < avg_ratio * (1 - threshold / 100.0):
							webhook = os.environ.get("SLACK_WEBHOOK")
							if webhook:
								try:
									payload = json.dumps({
										"text": f":small_red_triangle_down: ratio drop {ratio:.3f} vs {avg_ratio:.3f} ({threshold}% window {window} runs)"
									}).encode()
									req = request.Request(webhook, data=payload, headers={"Content-Type": "application/json"})
									request.urlopen(req, timeout=5)
								except Exception:
									pass
							# persist trend alert
							try:
								cur.execute(
									"""
									INSERT INTO public.etl_improved_alerts (kind, message, run_label, ratio, avg_ratio, threshold_pct)
									VALUES (%s, %s, %s, %s, %s, %s);
									""",
									(
										"trend_drop",
										f"ratio {ratio:.3f} < avg {avg_ratio:.3f} by >{threshold}%",
										run_label,
										float(ratio),
										float(avg_ratio),
										float(threshold),
									),
								)
							except Exception:
								pass
				Stats.incr("etl_consumer.summarize.success")

	summarize_metrics()
	return None


dag = etl_consumer()


