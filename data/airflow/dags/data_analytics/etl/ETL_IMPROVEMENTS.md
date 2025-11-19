# ETL Example DAG - Improvements Documentation

## Overview

The `etl_example.py` DAG is a production-ready ETL pipeline with comprehensive features for robustness, observability, and scalability.

## Key Features

### 1. Idempotency & Deduplication

- **Checksum-based**: Uses SHA256 checksum of payload key fields (rows, since, until, transformed)
- **TTL-based locks**: Default 24h expiration (configurable via `IDEMP_TTL_SECONDS`)
- **Bypass option**: Set `allow_overwrite=true` parameter to force reload

### 2. Data Quality & Validation

- **Schema validation**: Strict type checking (dict with rows:int, transformed:bool)
- **Range validation**: Configurable min/max rows via parameters
- **Non-retryable**: Validation failures don't retry (fail fast for data issues)

### 3. Retry Strategy

- **Exponential backoff**: Automatic with jitter for distributed retries
- **Jitter**: Random delays to prevent thundering herd
- **Smart retries**: I/O tasks retryable, validation/DQ tasks non-retryable
- **Configurable**: Retry counts per task type

### 4. Circuit Breaker

- **Failure threshold**: Default 5 failures (configurable via `CB_FAILURE_THRESHOLD`)
- **Auto-reset**: Default 15 minutes (configurable via `CB_RESET_MINUTES`)
- **Automatic pause**: DAG pauses when threshold exceeded

### 5. Observability

- **Tracing**: OpenTelemetry-compatible spans for all tasks
- **Metrics**: Throughput (rows/sec), duration (ms), chunk counts
- **Lineage**: Dataset declarations (raw → transformed → validated → dq_ok → complete)
- **Structured logging**: Rich context in all log entries

### 6. Scalability

- **Adaptive chunking**: Auto-adjusts chunk size based on volume and MAX_CHUNKS limit
- **Parallelism control**: Configurable per-task concurrency limits
- **Pool management**: Separate pools for ETL vs DQ workloads

### 7. Configuration

- **Environment-based**: Reads MLflow URI from `environments/*.yaml`
- **Env vars**: All operational toggles configurable via environment variables
- **Type-safe params**: All parameters validated with Airflow Param types

## Configuration Files

### `etl_config_constants.py`
Centralized configuration constants for:
- Pool names
- Concurrency limits
- Timeouts
- Retry settings
- DQ thresholds

### `etl_utils.py`
Utility functions for:
- Throughput calculation
- Duration formatting
- Window validation
- Task metrics logging

## Environment Variables

### Core Configuration
- `ETL_POOL`: Pool name for extract/transform/load (default: "etl_pool")
- `DQ_POOL`: Pool name for validation/DQ (default: "dq_pool")
- `MAX_ACTIVE_TASKS`: Maximum concurrent tasks (default: 32)
- `CHUNK_PARALLELISM`: Max parallel chunks (default: 16)
- `MAX_CHUNKS`: Maximum chunks per run (default: 100)

### Idempotency
- `IDEMP_TTL_SECONDS`: Lock TTL in seconds (default: 86400 = 24h)

### Circuit Breaker
- `CB_FAILURE_THRESHOLD`: Failure threshold (default: 5)
- `CB_RESET_MINUTES`: Reset window in minutes (default: 15)

### Timeouts
- `EXTRACT_TIMEOUT_MINUTES`: Extract task timeout (default: 5)
- `TRANSFORM_TIMEOUT_MINUTES`: Transform task timeout (default: 5)
- `VALIDATE_TIMEOUT_MINUTES`: Validate task timeout (default: 2)
- `DQ_CHECK_TIMEOUT_MINUTES`: DQ check timeout (default: 2)
- `LOAD_TIMEOUT_MINUTES`: Load task timeout (default: 10)
- `LOAD_SLA_MINUTES`: Load SLA in minutes (default: 10)

### Retries
- `EXTRACT_RETRIES`: Extract retry count (default: 3)
- `TRANSFORM_RETRIES`: Transform retry count (default: 3)
- `LOAD_RETRIES`: Load retry count (default: 2)
- `RETRY_DELAY_MINUTES`: Base retry delay (default: 2)
- `MAX_RETRY_DELAY_MINUTES`: Maximum retry delay (default: 10)

## DAG Parameters

- `rows` (int, 1-10M): Number of rows to process
- `run_name` (str): MLflow experiment run name
- `chunk_rows` (int, default 100k): Max rows per chunk
- `dry_run` (bool): Skip load side-effects
- `enable_load` (bool): Enable load step
- `since` (str): ISO8601 start timestamp (optional)
- `until` (str): ISO8601 end timestamp (optional)
- `allow_overwrite` (bool): Bypass idempotency lock
- `min_rows` (int): Minimum rows for DQ check
- `max_rows` (int): Maximum rows for DQ check
- `trigger_post_report` (bool): Trigger downstream DAG
- `downstream_dag_id` (str): Downstream DAG to trigger
- `backfill_days` (int, 1-180): Max backfill window in days

## Dataset Lineage

The DAG declares the following datasets for lineage tracking:

- `dataset://source_ready` - Source data ready (triggers DAG)
- `dataset://etl_example/raw` - Raw extracted data
- `dataset://etl_example/transformed` - Transformed data
- `dataset://etl_example/validated` - Schema-validated data
- `dataset://etl_example/dq_ok` - Data quality validated
- `dataset://etl_example/complete` - Load complete

## Testing

### Unit Tests
- `test_etl_example.py`: Basic ETL operation tests
- `test_dq_helper.py`: Data quality helper tests
- `test_etl_utils.py`: Utility function tests

### Running Tests
```bash
pytest data/airflow/dags/test_*.py -v
```

## Monitoring

### Metrics Available
- `etl_example.extract.start` / `.success`
- `etl_example.transform.duration_ms` / `.success`
- `etl_example.load.duration_ms` / `.success`
- `etl_example.load.ms_per_1k_rows`
- `etl_example.rows_processed`
- `etl_example.total_duration_ms`
- `etl_example.chunks`
- `etl_example.dq_violation` (if soft-fail enabled)
- `etl_example.sla_miss`
- `etl_example.task_failure`

### Alerts
- Slack notifications on DAG success/failure
- SLA miss callbacks
- Circuit breaker state changes

## Best Practices

1. **Use idempotency**: Don't set `allow_overwrite=true` unless necessary
2. **Monitor throughput**: Watch `rows/sec` metrics for performance issues
3. **Set appropriate timeouts**: Adjust timeouts based on data volume
4. **Configure pools**: Separate pools for different workload types
5. **Use dry_run**: Test DAG logic without side effects
6. **Monitor circuit breaker**: Check CB state in health checks
7. **Validate windows**: Use `since`/`until` for incremental loads

## Troubleshooting

### DAG Paused
- Check circuit breaker: may be open due to recent failures
- Review failure logs to identify root cause
- Wait for reset window or manually reset

### Slow Performance
- Check pool utilization
- Review chunk size (too small = overhead, too large = memory)
- Monitor throughput metrics
- Check for resource contention

### Idempotency Issues
- Verify TTL hasn't expired
- Check lock key format
- Review `allow_overwrite` parameter

### Data Quality Failures
- Review DQ thresholds (min_rows/max_rows)
- Check data source for anomalies
- Validate transformation logic


