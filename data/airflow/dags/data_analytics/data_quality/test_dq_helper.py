import pytest

from data.airflow.dags.etl_example import _dq_ok


def test_dq_ok_within_bounds():
	assert _dq_ok(10, 1, 100)
	assert _dq_ok(1, 1, 100)
	assert _dq_ok(100, 1, 100)


def test_dq_ok_out_of_bounds():
	assert _dq_ok(0, 1, 100) is False
	assert _dq_ok(101, 1, 100) is False


