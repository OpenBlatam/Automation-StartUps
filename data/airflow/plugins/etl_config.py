from __future__ import annotations

import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime
import pendulum
from airflow.models import Variable
from airflow.exceptions import AirflowFailException

_logger = logging.getLogger(__name__)


def validate_params(params: Dict[str, Any]) -> Dict[str, Any]:
	"""
	Validate and normalize DAG parameters with safe parsing and type conversion.
	
	Validates:
	- rows: integer in range [1, 10_000_000]
	- run_name: non-empty string, max 128 chars
	- chunk_rows: integer in range [1, 10_000_000]
	- since/until: ISO 8601 timestamp strings, normalized to UTC
	- min_rows/max_rows: non-negative integers, min <= max
	
	Args:
		params: Raw parameters dictionary from DAG context
		
	Returns:
		Validated and normalized parameters dictionary
		
	Raises:
		AirflowFailException if validation fails
	"""
	validated: Dict[str, Any] = {}
	
	# Validate rows
	if "rows" in params:
		try:
			rows = int(params["rows"])
			if rows < 1 or rows > 10_000_000:
				raise AirflowFailException(f"rows must be in [1, 10_000_000], got {rows}")
			validated["rows"] = rows
		except (ValueError, TypeError) as e:
			raise AirflowFailException(f"Invalid rows parameter: {e}")
	else:
		validated["rows"] = 1000  # Default
	
	# Validate run_name
	if "run_name" in params:
		run_name = str(params["run_name"]).strip()
		if not run_name or len(run_name) > 128:
			raise AirflowFailException(f"run_name must be 1-128 chars, got length {len(run_name)}")
		validated["run_name"] = run_name
	else:
		validated["run_name"] = "etl_example"  # Default
	
	# Validate chunk_rows
	if "chunk_rows" in params:
		try:
			chunk_rows = int(params["chunk_rows"])
			if chunk_rows < 1 or chunk_rows > 10_000_000:
				raise AirflowFailException(f"chunk_rows must be in [1, 10_000_000], got {chunk_rows}")
			validated["chunk_rows"] = chunk_rows
		except (ValueError, TypeError) as e:
			raise AirflowFailException(f"Invalid chunk_rows parameter: {e}")
	else:
		validated["chunk_rows"] = 100_000  # Default
	
	# Validate and normalize since/until timestamps
	for field in ["since", "until"]:
		if field in params:
			val = str(params[field]).strip()
			if val:
				try:
					# Parse and normalize to UTC ISO format
					dt = pendulum.parse(val, strict=False)
					if dt:
						validated[field] = dt.in_timezone("UTC").isoformat()
					else:
						raise AirflowFailException(f"Invalid {field} format: {val}. Use ISO 8601 (e.g., 2024-01-01T00:00:00Z)")
				except Exception as e:
					raise AirflowFailException(f"Failed to parse {field}: {e}")
			else:
				validated[field] = ""
		else:
			validated[field] = ""
	
	# Validate min_rows/max_rows
	if "min_rows" in params:
		try:
			min_rows = int(params["min_rows"])
			if min_rows < 0:
				raise AirflowFailException(f"min_rows must be >= 0, got {min_rows}")
			validated["min_rows"] = min_rows
		except (ValueError, TypeError) as e:
			raise AirflowFailException(f"Invalid min_rows parameter: {e}")
	else:
		validated["min_rows"] = 1  # Default
	
	if "max_rows" in params:
		try:
			max_rows = int(params["max_rows"])
			if max_rows < 1:
				raise AirflowFailException(f"max_rows must be >= 1, got {max_rows}")
			validated["max_rows"] = max_rows
		except (ValueError, TypeError) as e:
			raise AirflowFailException(f"Invalid max_rows parameter: {e}")
	else:
		validated["max_rows"] = 10_000_000  # Default
	
	# Ensure min_rows <= max_rows
	if validated["min_rows"] > validated["max_rows"]:
		raise AirflowFailException(
			f"min_rows ({validated['min_rows']}) must be <= max_rows ({validated['max_rows']})"
		)
	
	# Validate boolean parameters
	for field in ["dry_run", "enable_load", "allow_overwrite", "trigger_post_report"]:
		if field in params:
			val = params[field]
			if isinstance(val, bool):
				validated[field] = val
			elif isinstance(val, str):
				validated[field] = val.lower() in ("true", "1", "yes", "on")
			else:
				validated[field] = bool(val)
		else:
			validated[field] = False  # Default
	
	# Validate string parameters
	for field in ["downstream_dag_id"]:
		if field in params:
			validated[field] = str(params[field]).strip()
		else:
			validated[field] = ""
	
	# Validate backfill_days
	if "backfill_days" in params:
		try:
			backfill_days = int(params["backfill_days"])
			if backfill_days < 1 or backfill_days > 180:
				raise AirflowFailException(f"backfill_days must be in [1, 180], got {backfill_days}")
			validated["backfill_days"] = backfill_days
		except (ValueError, TypeError) as e:
			raise AirflowFailException(f"Invalid backfill_days parameter: {e}")
	else:
		validated["backfill_days"] = 30  # Default
	
	return validated


def get_config_value(key: str, default: Any = None, env_prefix: str = "ETL_") -> Any:
	"""
	Get configuration value from Airflow Variables or environment variables.
	
	Priority:
	1. Airflow Variable (key)
	2. Environment variable (ETL_<KEY>)
	3. Default value
	
	Args:
		key: Configuration key name
		default: Default value if not found
		env_prefix: Prefix for environment variable lookup
		
	Returns:
		Configuration value or default
	"""
	try:
		# Try Airflow Variable first
		val = Variable.get(key, default_var=None)
		if val is not None:
			return val
	except Exception:
		pass
	
	# Try environment variable
	env_key = f"{env_prefix}{key}".upper()
	val = os.getenv(env_key)
	if val is not None:
		# Try to convert to appropriate type
		if isinstance(default, bool):
			return val.lower() in ("true", "1", "yes", "on")
		elif isinstance(default, int):
			try:
				return int(val)
			except ValueError:
				return default
		elif isinstance(default, float):
			try:
				return float(val)
			except ValueError:
				return default
		return val
	
	return default
