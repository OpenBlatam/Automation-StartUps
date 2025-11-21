from __future__ import annotations

import importlib
import os


def test_dq_config_import_with_env_vars(monkeypatch):
    monkeypatch.setenv("DQ_MIN_ROWS", "10")
    monkeypatch.setenv("DQ_MAX_ROWS", "100000")
    mod = importlib.import_module("data.airflow.dags.etl_example")
    assert hasattr(mod, "dag")




