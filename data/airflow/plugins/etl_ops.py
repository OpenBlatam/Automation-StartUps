from __future__ import annotations

import os
from typing import Any, Optional, Dict

from .etl_types import ExtractPayload


def extract_rows(rows: int) -> ExtractPayload:
	return {"rows": int(rows), "transformed": False}


def apply_transform(payload: ExtractPayload) -> ExtractPayload:
	return {**payload, "transformed": True}


def log_with_mlflow(payload: ExtractPayload, run_name: str, tags: Optional[Dict[str, str]] = None) -> None:
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
