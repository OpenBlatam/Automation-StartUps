"""
Configuration module for approval cleanup DAG.
Centralizes all configuration constants and environment variables.
"""
from __future__ import annotations

import os
from typing import Dict, Any


# Database connection
APPROVALS_DB_CONN = os.getenv("APPROVALS_DB_CONN_ID", "approvals_db")

# Retention settings
MAX_RETENTION_YEARS = 10
MIN_RETENTION_YEARS = 1
MAX_NOTIFICATION_RETENTION_MONTHS = 24
MIN_NOTIFICATION_RETENTION_MONTHS = 1
STALE_THRESHOLD_DAYS = 90

# Batch processing
BATCH_SIZE = 1000
BATCH_SIZE_MIN = 100
BATCH_SIZE_MAX = 10000
BATCH_SIZE_ADAPTIVE = os.getenv('APPROVAL_CLEANUP_BATCH_ADAPTIVE', 'true').lower() == 'true'

# Timeouts
MAX_QUERY_TIMEOUT_SECONDS = 300
QUERY_TIMEOUT_SECONDS = int(os.getenv("APPROVAL_CLEANUP_QUERY_TIMEOUT", "300"))

# Reporting
REPORT_EXPORT_DIR = os.getenv("APPROVAL_CLEANUP_REPORT_DIR", "/tmp/approval_cleanup_reports")
REPORT_RETENTION_DAYS = 90
PERFORMANCE_HISTORY_DAYS = 30
SLOW_TASK_THRESHOLD_MS = 60000

# Analysis thresholds
ANOMALY_Z_SCORE_THRESHOLD = float(os.getenv('APPROVAL_CLEANUP_ANOMALY_Z_SCORE', '2.5'))
PERFORMANCE_HISTORY_WINDOW = int(os.getenv('APPROVAL_CLEANUP_PERF_HISTORY_WINDOW', '20'))
PREDICTION_WINDOW_DAYS = 30

# Feature toggles - Performance & Analytics
ENABLE_QUERY_OPTIMIZATION = os.getenv("APPROVAL_CLEANUP_QUERY_OPTIMIZATION", "true").lower() == "true"
ENABLE_MISSING_INDEX_ANALYSIS = os.getenv("APPROVAL_CLEANUP_MISSING_INDEXES", "true").lower() == "true"
ENABLE_PERFORMANCE_PROFILING = os.getenv("APPROVAL_CLEANUP_PERF_PROFILING", "true").lower() == "true"
ENABLE_BOTTLENECK_ANALYSIS = os.getenv("APPROVAL_CLEANUP_BOTTLENECK_ANALYSIS", "true").lower() == "true"
ENABLE_SCALABILITY_ANALYSIS = os.getenv("APPROVAL_CLEANUP_SCALABILITY", "true").lower() == "true"

# Feature toggles - Security & Compliance
ENABLE_SECURITY_ANALYSIS = os.getenv("APPROVAL_CLEANUP_SECURITY_ANALYSIS", "true").lower() == "true"
ENABLE_COMPLIANCE_ANALYSIS = os.getenv("APPROVAL_CLEANUP_COMPLIANCE", "true").lower() == "true"

# Feature toggles - Intelligence & Recommendations
ENABLE_INTELLIGENT_RECOMMENDATIONS = os.getenv("APPROVAL_CLEANUP_INTELLIGENT_RECS", "true").lower() == "true"
ENABLE_QUERY_RECOMMENDATIONS = os.getenv("APPROVAL_CLEANUP_QUERY_RECS", "true").lower() == "true"
ENABLE_ADAPTIVE_THRESHOLDS = os.getenv("APPROVAL_CLEANUP_ADAPTIVE_THRESHOLDS", "true").lower() == "true"
ENABLE_SEASONAL_ANALYSIS = os.getenv("APPROVAL_CLEANUP_SEASONAL", "true").lower() == "true"
ENABLE_ROOT_CAUSE_ANALYSIS = os.getenv("APPROVAL_CLEANUP_ROOT_CAUSE", "true").lower() == "true"
ENABLE_PREDICTIVE_ANALYTICS = os.getenv("APPROVAL_CLEANUP_PREDICTIVE_ANALYTICS", "true").lower() == "true"

# Feature toggles - Observability
PROMETHEUS_ENABLED = os.getenv("APPROVAL_CLEANUP_PROMETHEUS_ENABLED", "false").lower() == "true"
PROMETHEUS_PUSHGATEWAY_URL = os.getenv("APPROVAL_CLEANUP_PROMETHEUS_GATEWAY", "")
PROMETHEUS_METRICS_ENABLED = os.getenv("APPROVAL_CLEANUP_PROMETHEUS", "false").lower() == "true"
PROMETHEUS_PUSHGATEWAY = os.getenv("APPROVAL_CLEANUP_PROMETHEUS_GATEWAY", "")

# Feature toggles - Notifications & Alerts
ENABLE_SMART_ALERTS = os.getenv("APPROVAL_CLEANUP_SMART_ALERTS", "true").lower() == "true"
ENABLE_ADAPTIVE_ALERTING = os.getenv("APPROVAL_CLEANUP_ADAPTIVE_ALERTS", "true").lower() == "true"
ENABLE_INTELLIGENT_ALERTING = os.getenv("APPROVAL_CLEANUP_INTELLIGENT_ALERTS", "true").lower() == "true"

# Feature toggles - Export & Storage
S3_EXPORT_ENABLED = os.getenv("APPROVAL_CLEANUP_S3_EXPORT_ENABLED", "false").lower() == "true"
S3_BUCKET = os.getenv("APPROVAL_CLEANUP_S3_BUCKET", "")

# Feature toggles - Advanced features
ENABLE_HEALTH_SCORING = os.getenv("APPROVAL_CLEANUP_HEALTH_SCORING", "true").lower() == "true"
ENABLE_METRIC_CORRELATION = os.getenv("APPROVAL_CLEANUP_METRIC_CORRELATION", "true").lower() == "true"
ENABLE_AUTO_TUNING = os.getenv("APPROVAL_CLEANUP_AUTO_TUNING", "true").lower() == "true"
ENABLE_AUTO_INDEX_OPTIMIZATION = os.getenv("APPROVAL_CLEANUP_AUTO_INDEX_OPT", "true").lower() == "true"
ENABLE_COST_ANALYSIS = os.getenv("APPROVAL_CLEANUP_COST_ANALYSIS", "true").lower() == "true"
ENABLE_ADVANCED_REMEDIATION = os.getenv("APPROVAL_CLEANUP_ADV_REMEDIATION", "true").lower() == "true"
ENABLE_USAGE_PATTERN_ANALYSIS = os.getenv("APPROVAL_CLEANUP_USAGE_PATTERNS", "true").lower() == "true"
ENABLE_IMPACT_ANALYSIS = os.getenv("APPROVAL_CLEANUP_IMPACT_ANALYSIS", "true").lower() == "true"
ENABLE_ADVANCED_DASHBOARD = os.getenv("APPROVAL_CLEANUP_ADV_DASHBOARD", "true").lower() == "true"
ENABLE_RESILIENCE_ANALYSIS = os.getenv("APPROVAL_CLEANUP_RESILIENCE", "true").lower() == "true"
ENABLE_CONTINUOUS_LEARNING = os.getenv("APPROVAL_CLEANUP_LEARNING", "true").lower() == "true"
ENABLE_ADVANCED_BUSINESS_METRICS = os.getenv("APPROVAL_CLEANUP_BUSINESS_METRICS", "true").lower() == "true"
ENABLE_ADVANCED_DEPENDENCY_ANALYSIS = os.getenv("APPROVAL_CLEANUP_ADV_DEPS", "true").lower() == "true"
ENABLE_SCORING_SYSTEM = os.getenv("APPROVAL_CLEANUP_SCORING", "true").lower() == "true"
ENABLE_TREND_FORECASTING = os.getenv("APPROVAL_CLEANUP_TREND_FORECAST", "true").lower() == "true"

# Circuit breaker
CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.getenv("APPROVAL_CLEANUP_CB_FAILURE_THRESHOLD", "5"))
CIRCUIT_BREAKER_CHECK_WINDOW_HOURS = int(os.getenv("APPROVAL_CLEANUP_CB_WINDOW_HOURS", "24"))

# Parallelism
MAX_PARALLEL_WORKERS = int(os.getenv("APPROVAL_CLEANUP_MAX_WORKERS", "4"))

# Caching
CACHE_ENABLED = os.getenv("APPROVAL_CLEANUP_CACHE_ENABLED", "true").lower() == "true"
CACHE_TTL_SECONDS = int(os.getenv("APPROVAL_CLEANUP_CACHE_TTL", "300"))


def get_config() -> Dict[str, Any]:
    """Get all configuration as a dictionary."""
    return {
        "db_conn": APPROVALS_DB_CONN,
        "retention": {
            "max_years": MAX_RETENTION_YEARS,
            "min_years": MIN_RETENTION_YEARS,
            "max_notification_months": MAX_NOTIFICATION_RETENTION_MONTHS,
            "min_notification_months": MIN_NOTIFICATION_RETENTION_MONTHS,
            "stale_threshold_days": STALE_THRESHOLD_DAYS,
        },
        "batch": {
            "size": BATCH_SIZE,
            "min": BATCH_SIZE_MIN,
            "max": BATCH_SIZE_MAX,
            "adaptive": BATCH_SIZE_ADAPTIVE,
        },
        "timeouts": {
            "query_seconds": QUERY_TIMEOUT_SECONDS,
            "max_query_seconds": MAX_QUERY_TIMEOUT_SECONDS,
        },
        "features": {
            "query_optimization": ENABLE_QUERY_OPTIMIZATION,
            "missing_index_analysis": ENABLE_MISSING_INDEX_ANALYSIS,
            "security_analysis": ENABLE_SECURITY_ANALYSIS,
            "compliance_analysis": ENABLE_COMPLIANCE_ANALYSIS,
            "predictive_analytics": ENABLE_PREDICTIVE_ANALYTICS,
            "performance_profiling": ENABLE_PERFORMANCE_PROFILING,
        },
        "observability": {
            "prometheus_enabled": PROMETHEUS_ENABLED,
            "prometheus_gateway": PROMETHEUS_PUSHGATEWAY_URL,
        },
        "export": {
            "s3_enabled": S3_EXPORT_ENABLED,
            "s3_bucket": S3_BUCKET,
            "report_dir": REPORT_EXPORT_DIR,
        },
    }



