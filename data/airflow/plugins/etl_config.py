from __future__ import annotations

from typing import Dict, Any

from .etl_types import DEFAULT_ROWS, DEFAULT_RUN_NAME


def validate_params(raw_params: Dict[str, Any]) -> Dict[str, Any]:
	rows = raw_params.get("rows", DEFAULT_ROWS)
	try:
		rows = int(rows)
	except Exception:
		rows = DEFAULT_ROWS
	if rows < 1:
		rows = 1
	if rows > 10_000_000:
		rows = 10_000_000
	return {"rows": rows, "run_name": str(raw_params.get("run_name", DEFAULT_RUN_NAME))}
