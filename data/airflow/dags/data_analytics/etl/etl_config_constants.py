"""
Configuration constants for etl_example DAG.

These values can be overridden via environment variables for flexibility.
"""
import os

# Pool names
ETL_POOL = os.getenv("ETL_POOL", "etl_pool")
DQ_POOL = os.getenv("DQ_POOL", "dq_pool")

# Concurrency and parallelism
MAX_ACTIVE_TASKS = int(os.getenv("MAX_ACTIVE_TASKS", "32"))
CHUNK_PARALLELISM = int(os.getenv("CHUNK_PARALLELISM", "16"))
MAX_CHUNKS = int(os.getenv("MAX_CHUNKS", "100"))

# Idempotency
DEFAULT_IDEMPOTENCY_TTL_SECONDS = int(os.getenv("IDEMP_TTL_SECONDS", "86400"))  # 24 hours

# Circuit breaker
CIRCUIT_BREAKER_THRESHOLD = int(os.getenv("CB_FAILURE_THRESHOLD", "5"))
CIRCUIT_BREAKER_RESET_MINUTES = int(os.getenv("CB_RESET_MINUTES", "15"))

# Data quality thresholds
DEFAULT_MIN_ROWS = int(os.getenv("DQ_MIN_ROWS", "1"))
DEFAULT_MAX_ROWS = int(os.getenv("DQ_MAX_ROWS", "10_000_000"))

# Timeouts (seconds)
HEALTH_CHECK_TIMEOUT_SECONDS = int(os.getenv("HEALTH_CHECK_TIMEOUT", "30"))
EXTRACT_TIMEOUT_MINUTES = int(os.getenv("EXTRACT_TIMEOUT_MINUTES", "5"))
TRANSFORM_TIMEOUT_MINUTES = int(os.getenv("TRANSFORM_TIMEOUT_MINUTES", "5"))
VALIDATE_TIMEOUT_MINUTES = int(os.getenv("VALIDATE_TIMEOUT_MINUTES", "2"))
DQ_CHECK_TIMEOUT_MINUTES = int(os.getenv("DQ_CHECK_TIMEOUT_MINUTES", "2"))
LOAD_TIMEOUT_MINUTES = int(os.getenv("LOAD_TIMEOUT_MINUTES", "10"))
LOAD_SLA_MINUTES = int(os.getenv("LOAD_SLA_MINUTES", "10"))

# Retry configuration
DEFAULT_RETRIES = int(os.getenv("DEFAULT_RETRIES", "1"))
EXTRACT_RETRIES = int(os.getenv("EXTRACT_RETRIES", "3"))
TRANSFORM_RETRIES = int(os.getenv("TRANSFORM_RETRIES", "3"))
LOAD_RETRIES = int(os.getenv("LOAD_RETRIES", "2"))
RETRY_DELAY_MINUTES = int(os.getenv("RETRY_DELAY_MINUTES", "2"))
MAX_RETRY_DELAY_MINUTES = int(os.getenv("MAX_RETRY_DELAY_MINUTES", "10"))

# Chunking
DEFAULT_CHUNK_ROWS = int(os.getenv("DEFAULT_CHUNK_ROWS", "100000"))

# Backfill limits
DEFAULT_BACKFILL_DAYS = int(os.getenv("DEFAULT_BACKFILL_DAYS", "30"))
MAX_BACKFILL_DAYS = int(os.getenv("MAX_BACKFILL_DAYS", "180"))


