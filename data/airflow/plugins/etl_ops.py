from __future__ import annotations

import os
from typing import Any, Optional, Dict

from .etl_types import ExtractPayload
from .etl_rate_limit import rate_limit


def extract_rows(rows: int) -> ExtractPayload:
	return {"rows": int(rows), "transformed": False}


def apply_transform(payload: ExtractPayload) -> ExtractPayload:
    rows = int(payload.get("rows", 0))
    # simple deterministic checksum surrogate for demo purposes
    checksum = (rows * 31 + 17) % 1_000_000_007
    # simulate null rate bounded [0, 0.1] based on rows
    null_rate = min(0.1, (rows % 100) / 10_000.0)
    return {**payload, "transformed": True, "checksum": int(checksum), "null_rate": float(null_rate)}


@rate_limit(max_calls=20, window_seconds=60, variable_key="mlflow_api")
def _mlflow_log_internal(payload: ExtractPayload, run_name: str, tags: Optional[Dict[str, str]] = None) -> None:
	"""Internal MLflow logging function with rate limiting."""
	try:
		import mlflow  # type: ignore
		tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow.example.com")
		mlflow.set_tracking_uri(tracking_uri)
		with mlflow.start_run(run_name=run_name):
			mlflow.log_param("task", "load")
			mlflow.log_metric("rows", float(payload.get("rows", 0)))
			mlflow.log_param("transformed", str(payload.get("transformed", False)))
			mlflow.set_tag("dag_id", "etl_example")
			mlflow.set_tag("environment", os.getenv("ENV", "dev"))
			if tags:
				mlflow.set_tags(tags)
	except Exception:
		# swallow any mlflow problem silently; caller may log
		return


def log_with_mlflow(payload: ExtractPayload, run_name: str, tags: Optional[Dict[str, str]] = None) -> None:
	"""
	Log payload to MLflow with rate limiting.
	
	Rate limited to 20 calls per 60 seconds to protect MLflow API.
	"""
	_mlflow_log_internal(payload, run_name, tags)
