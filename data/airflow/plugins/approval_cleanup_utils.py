"""
Utility functions for approval cleanup DAG.
Contains logging, validation, circuit breaker, and other helper functions.
"""
from __future__ import annotations

import logging
import json
import time
from typing import Dict, Any, Optional, Callable
from functools import wraps

from airflow.operators.python import get_current_context
from airflow.exceptions import AirflowFailException

from .approval_cleanup_config import (
    CIRCUIT_BREAKER_FAILURE_THRESHOLD,
    CIRCUIT_BREAKER_CHECK_WINDOW_HOURS,
)
from .approval_cleanup_ops import get_pg_hook

logger = logging.getLogger(__name__)


def log_with_context(level: str, message: str, **kwargs) -> None:
    """
    Structured logging with DAG run context.
    
    Args:
        level: Log level ('info', 'warning', 'error', 'debug')
        message: Log message
        **kwargs: Additional context fields
    """
    try:
        context = get_current_context()
        dag_run = context.get('dag_run')
        task_instance = context.get('task_instance')
        
        log_data = {
            'dag_id': context.get('dag').dag_id if context.get('dag') else None,
            'dag_run_id': dag_run.run_id if dag_run else None,
            'task_id': task_instance.task_id if task_instance else None,
            'execution_date': str(dag_run.execution_date) if dag_run else None,
            **kwargs
        }
        
        log_message = f"{message} | Context: {json.dumps(log_data)}"
        
        if level == 'info':
            logger.info(log_message)
        elif level == 'warning':
            logger.warning(log_message)
        elif level == 'error':
            logger.error(log_message)
        elif level == 'debug':
            logger.debug(log_message)
        else:
            logger.info(log_message)
    except Exception:
        # Fallback to simple logging if context unavailable
        if level == 'info':
            logger.info(message)
        elif level == 'warning':
            logger.warning(message)
        elif level == 'error':
            logger.error(message)
        else:
            logger.debug(message)


def check_circuit_breaker(pg_hook=None) -> Dict[str, Any]:
    """
    Check if circuit breaker is active (too many recent failures).
    
    Returns:
        Dict with 'active' boolean and reason
    """
    try:
        if not pg_hook:
            pg_hook = get_pg_hook()
        
        # Check recent failures in history
        check_sql = """
            SELECT COUNT(*) 
            FROM approval_cleanup_history
            WHERE cleanup_date >= NOW() - INTERVAL '%s hours'
              AND archived_count = 0
              AND deleted_count = 0
              AND notifications_deleted = 0
              AND database_size_bytes = 0
        """
        
        try:
            recent_failures = pg_hook.get_first(
                check_sql,
                parameters=(CIRCUIT_BREAKER_CHECK_WINDOW_HOURS,)
            )
            failure_count = recent_failures[0] if recent_failures else 0
        except Exception:
            # Table doesn't exist or error, allow execution
            return {'active': False, 'reason': 'history_table_unavailable'}
        
        if failure_count >= CIRCUIT_BREAKER_FAILURE_THRESHOLD:
            log_with_context(
                'warning',
                f'Circuit breaker ACTIVE: {failure_count} failures in last {CIRCUIT_BREAKER_CHECK_WINDOW_HOURS}h',
                failure_count=failure_count,
                threshold=CIRCUIT_BREAKER_FAILURE_THRESHOLD
            )
            return {
                'active': True,
                'failure_count': failure_count,
                'threshold': CIRCUIT_BREAKER_FAILURE_THRESHOLD,
                'reason': 'too_many_failures'
            }
        
        return {'active': False, 'failure_count': failure_count}
        
    except Exception as e:
        log_with_context('warning', f'Circuit breaker check failed: {e}', error=str(e))
        # If check fails, allow execution (fail open)
        return {'active': False, 'reason': 'check_failed'}


def detect_deadlock_retry(
    func: Callable,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> Any:
    """
    Wrapper to detect deadlocks and retry automatically.
    
    Args:
        func: Function to execute
        max_retries: Maximum number of retries
        retry_delay: Initial retry delay in seconds
        
    Returns:
        Result of function execution
    """
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            error_str = str(e).lower()
            is_deadlock = (
                'deadlock' in error_str or
                'could not obtain lock' in error_str or
                'lock_not_available' in error_str or
                'serialization failure' in error_str
            )
            
            if is_deadlock and attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                log_with_context(
                    'warning',
                    f'Deadlock detected, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})',
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    error=error_str
                )
                time.sleep(wait_time)
                continue
            
            # Not a deadlock or retries exhausted
            raise


def validate_params(params: Dict[str, Any]) -> None:
    """
    Validate DAG parameters.
    
    Raises:
        AirflowFailException if validation fails
    """
    # Validate retention years
    archive_retention = params.get('archive_retention_years', 1)
    if not isinstance(archive_retention, int) or archive_retention < 1 or archive_retention > 10:
        raise AirflowFailException(
            f"Invalid archive_retention_years: {archive_retention}. Must be between 1 and 10."
        )
    
    # Validate notification retention
    notification_retention = params.get('notification_retention_months', 6)
    if not isinstance(notification_retention, int) or notification_retention < 1 or notification_retention > 24:
        raise AirflowFailException(
            f"Invalid notification_retention_months: {notification_retention}. Must be between 1 and 24."
        )
    
    # Validate dry_run is boolean
    dry_run = params.get('dry_run', False)
    if not isinstance(dry_run, bool):
        raise AirflowFailException(
            f"Invalid dry_run: {dry_run}. Must be boolean."
        )


def export_to_multiple_formats(
    data: Dict[str, Any],
    base_filename: str,
    export_dir: str,
    formats: list[str] = ['json', 'csv']
) -> Dict[str, str]:
    """
    Export data to multiple formats (JSON, CSV, etc.).
    
    Args:
        data: Data to export
        base_filename: Base filename (without extension)
        export_dir: Export directory
        formats: List of formats to export
        
    Returns:
        Dict with paths of exported files
    """
    import csv
    from pathlib import Path
    from datetime import datetime
    
    exported_files = {}
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    export_path = Path(export_dir)
    export_path.mkdir(parents=True, exist_ok=True)
    
    # Export to JSON
    if 'json' in formats:
        json_file = export_path / f"{base_filename}_{timestamp}.json"
        try:
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            exported_files['json'] = str(json_file)
            log_with_context('info', f'Exported to JSON: {json_file}')
        except Exception as e:
            log_with_context('warning', f'Failed to export JSON: {e}', error=str(e))
    
    # Export to CSV (if data is a list of dicts)
    if 'csv' in formats and isinstance(data, dict):
        csv_file = export_path / f"{base_filename}_{timestamp}.csv"
        try:
            # Try to find list values that can be tabular
            for key, value in data.items():
                if isinstance(value, list) and value and isinstance(value[0], dict):
                    with open(csv_file, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=value[0].keys())
                        writer.writeheader()
                        writer.writerows(value)
                    exported_files['csv'] = str(csv_file)
                    log_with_context('info', f'Exported to CSV: {csv_file}')
                    break
        except Exception as e:
            log_with_context('debug', f'CSV export not applicable or failed: {e}')
    
    return exported_files


def format_duration_ms(duration_ms: float) -> str:
    """Format duration in milliseconds to human-readable string."""
    if duration_ms < 1000:
        return f"{duration_ms:.0f}ms"
    elif duration_ms < 60000:
        return f"{duration_ms / 1000:.2f}s"
    else:
        minutes = int(duration_ms / 60000)
        seconds = (duration_ms % 60000) / 1000
        return f"{minutes}m {seconds:.1f}s"


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values."""
    if old_value == 0:
        return 0.0 if new_value == 0 else float('inf') if new_value > 0 else float('-inf')
    return ((new_value - old_value) / old_value) * 100


