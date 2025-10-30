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
