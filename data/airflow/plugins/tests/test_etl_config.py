from __future__ import annotations

from data.airflow.plugins.etl_config import validate_params


def test_validate_params_coerces_and_bounds_rows():
	assert validate_params({"rows": "5"})["rows"] == 5
	assert validate_params({"rows": 0})["rows"] == 1
	assert validate_params({"rows": -10})["rows"] == 1
	assert validate_params({"rows": 20_000_000})["rows"] == 10_000_000


def test_validate_params_defaults_run_name():
	params = validate_params({})
	assert "run_name" in params and isinstance(params["run_name"], str)
