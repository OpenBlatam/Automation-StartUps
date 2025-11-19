import pytest

from data.airflow.plugins.etl_ops import extract_rows, apply_transform


def test_extract_rows_positive():
	out = extract_rows(5)
	assert out["rows"] == 5
	assert out.get("transformed") is False


def test_apply_transform_sets_flag():
	payload = {"rows": 3, "transformed": False}
	res = apply_transform(payload)
	assert res["rows"] == 3
	assert res["transformed"] is True


