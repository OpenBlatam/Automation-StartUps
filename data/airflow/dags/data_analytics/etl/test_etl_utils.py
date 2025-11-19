"""
Unit tests for ETL utility functions.
"""
import pytest
from data.airflow.dags.etl_utils import (
	calculate_throughput,
	format_duration,
	format_window_info,
	validate_time_window,
)


def test_calculate_throughput_valid():
	assert calculate_throughput(1000, 10.0) == 100.0
	assert calculate_throughput(5000, 2.5) == 2000.0


def test_calculate_throughput_invalid():
	assert calculate_throughput(0, 10.0) is None
	assert calculate_throughput(1000, 0) is None
	assert calculate_throughput(-1, 10.0) is None


def test_format_duration():
	assert format_duration(500) == "500ms"
	assert format_duration(1500) == "1.5s"
	assert format_duration(65000) == "1m 5.0s"
	assert format_duration(3900000) == "1h 5m 0.0s"


def test_format_window_info():
	assert format_window_info(None, None) == ""
	assert format_window_info("2024-01-01T00:00:00Z", None) == "2024-01-01..now"
	assert format_window_info(None, "2024-01-02T00:00:00Z") == "start..2024-01-02"
	assert format_window_info("2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z") == "2024-01-01..2024-01-02"


def test_validate_time_window_valid():
	valid, err = validate_time_window("2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z", max_days=30)
	assert valid is True
	assert err is None


def test_validate_time_window_invalid_reversed():
	valid, err = validate_time_window("2024-01-02T00:00:00Z", "2024-01-01T00:00:00Z", max_days=30)
	assert valid is False
	assert "until must be >=" in err


def test_validate_time_window_too_large():
	valid, err = validate_time_window("2024-01-01T00:00:00Z", "2024-02-15T00:00:00Z", max_days=30)
	assert valid is False
	assert "too large" in err


def test_validate_time_window_invalid_format():
	valid, err = validate_time_window("invalid-date", None, max_days=30)
	assert valid is False
	assert "Invalid timestamp format" in err


