"""
Analytics and analysis functions for approval cleanup.
Contains functions for performance analysis, anomaly detection, and predictions.
"""
from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional
from statistics import mean, stdev

from airflow.providers.postgres.hooks.postgres import PostgresHook

from .approval_cleanup_ops import get_pg_hook
from .approval_cleanup_config import (
    ANOMALY_Z_SCORE_THRESHOLD,
    PERFORMANCE_HISTORY_DAYS,
    PERFORMANCE_HISTORY_WINDOW,
)

logger = logging.getLogger(__name__)


def calculate_percentiles(values: List[float]) -> Dict[str, float]:
    """Calculate percentiles (p50, p95, p99) from a list of values."""
    if not values:
        return {'p50': 0, 'p95': 0, 'p99': 0, 'min': 0, 'max': 0, 'avg': 0}
    
    sorted_values = sorted(values)
    n = len(sorted_values)
    
    def percentile(p: float) -> float:
        index = int((p / 100) * n)
        if index >= n:
            index = n - 1
        return sorted_values[index]
    
    return {
        'p50': percentile(50),
        'p95': percentile(95),
        'p99': percentile(99),
        'min': min(sorted_values),
        'max': max(sorted_values),
        'avg': sum(sorted_values) / n
    }


def detect_anomaly(
    value: float,
    metric_name: str,
    pg_hook: Optional[PostgresHook] = None
) -> Dict[str, Any]:
    """
    Detect anomalies using Z-score based on historical data.
    
    Returns:
        Dict with 'is_anomaly', 'z_score', 'mean', 'std', 'threshold'
    """
    try:
        if not pg_hook:
            pg_hook = get_pg_hook()
        
        # Get historical metrics
        history_sql = """
            SELECT archived_count, deleted_count, notifications_deleted,
                   database_size_bytes
            FROM approval_cleanup_history
            WHERE cleanup_date >= NOW() - INTERVAL '%s days'
            ORDER BY cleanup_date DESC
            LIMIT %s
        """
        
        try:
            history = pg_hook.get_records(
                history_sql,
                parameters=(PERFORMANCE_HISTORY_DAYS, PERFORMANCE_HISTORY_WINDOW)
            )
        except Exception:
            return {
                'is_anomaly': False,
                'z_score': 0,
                'mean': 0,
                'std': 0,
                'threshold': ANOMALY_Z_SCORE_THRESHOLD,
                'reason': 'insufficient_history'
            }
        
        if len(history) < 3:
            return {
                'is_anomaly': False,
                'z_score': 0,
                'mean': 0,
                'std': 0,
                'threshold': ANOMALY_Z_SCORE_THRESHOLD,
                'reason': 'insufficient_data'
            }
        
        # Map metric names to column indices
        metric_map = {
            'archived_count': 0,
            'deleted_count': 1,
            'notifications_deleted': 2,
            'database_size_bytes': 3
        }
        
        if metric_name not in metric_map:
            return {
                'is_anomaly': False,
                'z_score': 0,
                'mean': 0,
                'std': 0,
                'threshold': ANOMALY_Z_SCORE_THRESHOLD,
                'reason': 'unknown_metric'
            }
        
        col_idx = metric_map[metric_name]
        historical_values = [float(row[col_idx] or 0) for row in history]
        
        # Calculate mean and standard deviation
        if len(historical_values) < 2:
            std = 0
            mean_val = historical_values[0] if historical_values else 0
        else:
            mean_val = mean(historical_values)
            std = stdev(historical_values) if len(historical_values) > 1 else 0
        
        # Calculate Z-score
        if std == 0:
            z_score = 0
        else:
            z_score = abs((value - mean_val) / std)
        
        is_anomaly = z_score > ANOMALY_Z_SCORE_THRESHOLD
        
        return {
            'is_anomaly': is_anomaly,
            'z_score': round(z_score, 3),
            'mean': round(mean_val, 2),
            'std': round(std, 2),
            'threshold': ANOMALY_Z_SCORE_THRESHOLD,
            'historical_values_count': len(historical_values),
            'reason': 'calculated'
        }
        
    except Exception as e:
        logger.warning(f"Anomaly detection failed: {e}", exc_info=True)
        return {
            'is_anomaly': False,
            'z_score': 0,
            'mean': 0,
            'std': 0,
            'threshold': ANOMALY_Z_SCORE_THRESHOLD,
            'reason': 'error',
            'error': str(e)
        }


def analyze_query_performance(
    pg_hook: PostgresHook,
    sql: str,
    parameters: Optional[tuple] = None
) -> Dict[str, Any]:
    """Analyze query performance using EXPLAIN ANALYZE."""
    import json
    
    try:
        explain_sql = f"EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON) {sql}"
        
        conn = pg_hook.get_conn()
        cursor = conn.cursor()
        
        try:
            if parameters:
                cursor.execute(explain_sql, parameters)
            else:
                cursor.execute(explain_sql)
            
            result = cursor.fetchone()
            if result and result[0]:
                plan = json.loads(result[0][0]) if isinstance(result[0], (list, tuple)) else result[0]
                
                # Extract key metrics
                execution_time = plan[0].get('Execution Time', 0) if isinstance(plan, list) else plan.get('Execution Time', 0)
                planning_time = plan[0].get('Planning Time', 0) if isinstance(plan, list) else plan.get('Planning Time', 0)
                
                return {
                    'execution_time_ms': execution_time,
                    'planning_time_ms': planning_time,
                    'total_time_ms': execution_time + planning_time,
                    'plan': plan
                }
            
            return {'execution_time_ms': 0, 'planning_time_ms': 0, 'total_time_ms': 0}
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.warning(f"Query analysis failed: {e}", exc_info=True)
        return {'error': str(e)}


def predict_capacity_need(
    days_ahead: int = 30,
    pg_hook: Optional[PostgresHook] = None
) -> Dict[str, Any]:
    """
    Predict future capacity needs based on historical trends.
    
    Returns:
        Dict with predictions of growth, capacity needed, etc.
    """
    try:
        if not pg_hook:
            pg_hook = get_pg_hook()
        
        # Get growth history
        growth_sql = """
            SELECT 
                cleanup_date,
                database_size_bytes,
                archived_count,
                deleted_count,
                total_pending,
                total_completed
            FROM approval_cleanup_history
            WHERE cleanup_date >= NOW() - INTERVAL '60 days'
            ORDER BY cleanup_date ASC
        """
        
        try:
            history = pg_hook.get_records(growth_sql)
        except Exception:
            return {
                'prediction_available': False,
                'reason': 'insufficient_history'
            }
        
        if len(history) < 5:
            return {
                'prediction_available': False,
                'reason': 'insufficient_data_points'
            }
        
        # Calculate average growth rate
        sizes = [float(row[1] or 0) for row in history]
        if len(sizes) < 2:
            return {'prediction_available': False, 'reason': 'no_size_data'}
        
        # Calculate average daily growth rate
        growth_rates = []
        for i in range(1, len(sizes)):
            if sizes[i-1] > 0:
                growth_rate = (sizes[i] - sizes[i-1]) / sizes[i-1]
                growth_rates.append(growth_rate)
        
        if not growth_rates:
            return {'prediction_available': False, 'reason': 'no_growth_data'}
        
        avg_growth_rate = mean(growth_rates)
        
        # Simple linear prediction
        current_size = sizes[-1]
        predicted_size = current_size * (1 + avg_growth_rate) ** days_ahead
        
        # Calculate when limit will be reached (assuming 100GB limit)
        size_limit_gb = 100
        size_limit_bytes = size_limit_gb * (1024 ** 3)
        
        days_to_limit = None
        if avg_growth_rate > 0 and current_size < size_limit_bytes:
            days_to_limit = int((size_limit_bytes / current_size - 1) / avg_growth_rate) if avg_growth_rate > 0 else None
        
        return {
            'prediction_available': True,
            'current_size_bytes': current_size,
            'current_size_gb': round(current_size / (1024 ** 3), 2),
            'predicted_size_bytes': predicted_size,
            'predicted_size_gb': round(predicted_size / (1024 ** 3), 2),
            'avg_growth_rate': round(avg_growth_rate, 6),
            'days_ahead': days_ahead,
            'days_to_limit': days_to_limit,
            'growth_rate_per_day': round(avg_growth_rate, 6)
        }
        
    except Exception as e:
        logger.warning(f"Capacity prediction failed: {e}", exc_info=True)
        return {
            'prediction_available': False,
            'reason': 'error',
            'error': str(e)
        }


def analyze_table_sizes(pg_hook: Optional[PostgresHook] = None) -> Dict[str, Any]:
    """Analyze sizes of all tables."""
    from .approval_cleanup_queries import get_table_sizes
    
    try:
        if not pg_hook:
            pg_hook = get_pg_hook()
        
        table_sizes = get_table_sizes(pg_hook=pg_hook)
        
        total_bytes = sum(t['total_bytes'] for t in table_sizes)
        total_gb = total_bytes / (1024 ** 3)
        
        largest_table = max(table_sizes, key=lambda x: x['total_bytes']) if table_sizes else None
        
        return {
            'table_sizes': table_sizes,
            'total_size_bytes': total_bytes,
            'total_size_gb': round(total_gb, 2),
            'table_count': len(table_sizes),
            'largest_table': largest_table
        }
        
    except Exception as e:
        logger.warning(f"Table size analysis failed: {e}", exc_info=True)
        return {
            'table_sizes': [],
            'total_size_bytes': 0,
            'error': str(e)
        }


def analyze_trends(
    history_data: List[Dict[str, Any]],
    days: int = 30
) -> Dict[str, Any]:
    """
    Analyze trends from historical cleanup data.
    
    Args:
        history_data: List of historical cleanup records
        days: Number of days to analyze
        
    Returns:
        Dict with trend analysis
    """
    if not history_data or len(history_data) < 2:
        return {
            'trends_available': False,
            'reason': 'insufficient_data'
        }
    
    try:
        # Extract metrics
        archived_counts = [h.get('archived_count', 0) for h in history_data]
        deleted_counts = [h.get('deleted_count', 0) for h in history_data]
        sizes = [h.get('database_size_bytes', 0) for h in history_data]
        
        # Calculate trends
        archived_trend = 'increasing' if archived_counts[-1] > archived_counts[0] else 'decreasing' if archived_counts[-1] < archived_counts[0] else 'stable'
        deleted_trend = 'increasing' if deleted_counts[-1] > deleted_counts[0] else 'decreasing' if deleted_counts[-1] < deleted_counts[0] else 'stable'
        size_trend = 'increasing' if sizes[-1] > sizes[0] else 'decreasing' if sizes[-1] < sizes[0] else 'stable'
        
        # Calculate averages
        avg_archived = mean(archived_counts) if archived_counts else 0
        avg_deleted = mean(deleted_counts) if deleted_counts else 0
        avg_size = mean(sizes) if sizes else 0
        
        # Calculate growth rates
        archived_growth = ((archived_counts[-1] - archived_counts[0]) / archived_counts[0] * 100) if archived_counts[0] > 0 else 0
        size_growth = ((sizes[-1] - sizes[0]) / sizes[0] * 100) if sizes[0] > 0 else 0
        
        return {
            'trends_available': True,
            'days_analyzed': days,
            'data_points': len(history_data),
            'archived_trend': archived_trend,
            'deleted_trend': deleted_trend,
            'size_trend': size_trend,
            'avg_archived_per_run': round(avg_archived, 2),
            'avg_deleted_per_run': round(avg_deleted, 2),
            'avg_size_bytes': round(avg_size, 0),
            'archived_growth_pct': round(archived_growth, 2),
            'size_growth_pct': round(size_growth, 2),
            'most_recent_archived': archived_counts[-1] if archived_counts else 0,
            'most_recent_deleted': deleted_counts[-1] if deleted_counts else 0,
            'most_recent_size_bytes': sizes[-1] if sizes else 0
        }
        
    except Exception as e:
        logger.warning(f"Trend analysis failed: {e}", exc_info=True)
        return {
            'trends_available': False,
            'reason': 'error',
            'error': str(e)
        }



