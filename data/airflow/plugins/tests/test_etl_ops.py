from __future__ import annotations

from data.airflow.plugins.etl_ops import extract_rows, apply_transform


def test_extract_rows_builds_payload():
	payload = extract_rows(123)
	assert payload["rows"] == 123
	assert payload["transformed"] is False


def test_apply_transform_sets_flag_true():
	payload = {"rows": 10, "transformed": False}
	result = apply_transform(payload)
	assert result is not payload  # should not mutate
	assert result["rows"] == 10
	assert result["transformed"] is True


