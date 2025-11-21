from __future__ import annotations

from airflow.stats import Stats


def record_extract_start() -> None:
	try:
		Stats.incr("etl_example.extract.start")
	except Exception:
		pass


def record_extract_success() -> None:
	try:
		Stats.incr("etl_example.extract.success")
	except Exception:
		pass


def record_transform_start() -> None:
	try:
		Stats.incr("etl_example.transform.start")
	except Exception:
		pass


def record_transform_success() -> None:
	try:
		Stats.incr("etl_example.transform.success")
	except Exception:
		pass


def record_load_duration_ms(duration_ms: int) -> None:
	try:
		Stats.timing("etl_example.load.duration_ms", duration_ms)
	except Exception:
		pass


def record_load_success() -> None:
	try:
		Stats.incr("etl_example.load.success")
	except Exception:
		pass


def record_throughput_metric(rows: int, duration_ms: int) -> None:
	"""Record throughput metrics including percentile calculations."""
	try:
		if rows > 0:
			# Rows per second
			rows_per_sec = (rows * 1000) / max(duration_ms, 1)
			Stats.timing("etl_example.throughput.rows_per_sec", int(rows_per_sec))
			# Milliseconds per 1k rows (for percentiles)
			ms_per_1k = int(duration_ms / max(rows / 1000.0, 0.001))
			Stats.timing("etl_example.throughput.ms_per_1k_rows", ms_per_1k)
	except Exception:
		pass
