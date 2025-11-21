from __future__ import annotations

import importlib


def test_import_etl_example_dag():
	mod = importlib.import_module("data.airflow.dags.etl_example")
	assert hasattr(mod, "dag"), "etl_example should define 'dag'"


