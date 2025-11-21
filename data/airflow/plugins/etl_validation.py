from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional
from airflow.exceptions import AirflowFailException

_logger = logging.getLogger(__name__)


def validate_payload_schema(payload: Dict[str, Any], strict: bool = False) -> tuple[bool, List[str]]:
	"""
	Validate ExtractPayload schema with detailed error reporting.
	
	Args:
		payload: Payload to validate
		strict: If True, fail on unexpected fields
		
	Returns:
		(is_valid, list_of_errors)
	"""
	errors: List[str] = []
	required_fields = ["rows", "transformed"]
	
	# Check required fields
	for field in required_fields:
		if field not in payload:
			errors.append(f"Missing required field: {field}")
		elif field == "rows":
			if not isinstance(payload[field], int):
				errors.append(f"Field 'rows' must be int, got {type(payload[field]).__name__}")
			elif payload[field] < 0:
				errors.append(f"Field 'rows' must be >= 0, got {payload[field]}")
		elif field == "transformed":
			if not isinstance(payload[field], bool):
				errors.append(f"Field 'transformed' must be bool, got {type(payload[field]).__name__}")
	
	# Check optional fields
	optional_fields = {"since": str, "until": str, "checksum": int, "null_rate": float}
	for field, expected_type in optional_fields.items():
		if field in payload:
			if not isinstance(payload[field], expected_type):
				errors.append(f"Field '{field}' must be {expected_type.__name__}, got {type(payload[field]).__name__}")
	
	# Strict mode: check for unexpected fields
	if strict:
		allowed = set(required_fields) | set(optional_fields.keys())
		for key in payload.keys():
			if key not in allowed:
				errors.append(f"Unexpected field: {key}")
	
	return len(errors) == 0, errors


def validate_and_raise(payload: Dict[str, Any], strict: bool = False) -> None:
	"""
	Validate payload schema and raise AirflowFailException if invalid.
	
	Args:
		payload: Payload to validate
		strict: If True, fail on unexpected fields
		
	Raises:
		AirflowFailException if validation fails
	"""
	is_valid, errors = validate_payload_schema(payload, strict=strict)
	if not is_valid:
		error_msg = "Schema validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
		_logger.error(error_msg, extra={"payload_keys": list(payload.keys()), "errors": errors})
		raise AirflowFailException(error_msg)


def validate_rows_range(rows: int, min_rows: int, max_rows: int, context: Optional[Dict[str, Any]] = None) -> None:
	"""
	Validate row count against min/max bounds with context.
	
	Args:
		rows: Actual row count
		min_rows: Minimum allowed
		max_rows: Maximum allowed
		context: Optional context for logging
		
	Raises:
		AirflowFailException if out of range
	"""
	if rows < min_rows:
		msg = f"Row count {rows} below minimum {min_rows}"
		if context:
			_logger.error(msg, extra=context)
		raise AirflowFailException(msg)
	if rows > max_rows:
		msg = f"Row count {rows} above maximum {max_rows}"
		if context:
			_logger.error(msg, extra=context)
		raise AirflowFailException(msg)


