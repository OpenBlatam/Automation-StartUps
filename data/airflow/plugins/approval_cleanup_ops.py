"""
Operational functions for approval cleanup DAG.
Contains database operations, query execution, and batch processing utilities.
"""
from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional, Tuple, Callable
from time import perf_counter
from functools import lru_cache

from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.exceptions import AirflowFailException

from .approval_cleanup_config import (
    APPROVALS_DB_CONN,
    QUERY_TIMEOUT_SECONDS,
    BATCH_SIZE,
    BATCH_SIZE_MIN,
    BATCH_SIZE_MAX,
    BATCH_SIZE_ADAPTIVE,
    PERFORMANCE_HISTORY_DAYS,
)

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_pg_hook() -> PostgresHook:
    """Get PostgreSQL hook with caching."""
    return PostgresHook(postgres_conn_id=APPROVALS_DB_CONN)


def execute_query_with_timeout(
    pg_hook: PostgresHook,
    sql: str,
    parameters: Optional[Tuple] = None,
    timeout_seconds: int = QUERY_TIMEOUT_SECONDS,
    operation_name: str = "query"
) -> Any:
    """Execute query with configurable timeout."""
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    try:
        # Set timeout (PostgreSQL uses milliseconds)
        cursor.execute(f"SET statement_timeout = {timeout_seconds * 1000};")
        
        # Execute query
        start_time = perf_counter()
        if parameters:
            cursor.execute(sql, parameters)
        else:
            cursor.execute(sql)
        
        result = cursor.fetchall() if cursor.description else None
        duration_ms = (perf_counter() - start_time) * 1000
        
        logger.debug(
            f"{operation_name} completed in {duration_ms:.2f}ms",
            extra={"duration_ms": round(duration_ms, 2), "timeout_seconds": timeout_seconds}
        )
        
        # Reset timeout
        cursor.execute("RESET statement_timeout;")
        conn.commit()
        
        return result
        
    except Exception as e:
        conn.rollback()
        error_msg = str(e)
        if 'timeout' in error_msg.lower() or 'statement_timeout' in error_msg:
            logger.error(
                f"{operation_name} timed out after {timeout_seconds}s",
                extra={"timeout_seconds": timeout_seconds, "error": error_msg}
            )
            raise AirflowFailException(f"Query timeout after {timeout_seconds}s: {error_msg}")
        raise
    finally:
        cursor.close()
        conn.close()


def process_batch(
    items: List[Any],
    batch_size: int,
    processor: Callable[[List[Any]], Dict[str, Any]],
    operation_name: str = "batch_operation"
) -> Dict[str, Any]:
    """
    Process items in batches with error handling.
    
    Args:
        items: List of items to process
        batch_size: Size of each batch
        processor: Function to process each batch
        operation_name: Name for logging
        
    Returns:
        Dict with results and statistics
    """
    total_items = len(items)
    total_batches = (total_items + batch_size - 1) // batch_size
    processed = 0
    failed = 0
    results = []
    
    logger.info(
        f"Processing {total_items} items in {total_batches} batches",
        extra={"operation": operation_name, "batch_size": batch_size}
    )
    
    for i in range(0, total_items, batch_size):
        batch = items[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        try:
            start_time = perf_counter()
            batch_result = processor(batch)
            duration_ms = (perf_counter() - start_time) * 1000
            
            processed += len(batch)
            results.append(batch_result)
            
            logger.debug(
                f"Batch {batch_num}/{total_batches} completed",
                extra={
                    "batch_num": batch_num,
                    "total_batches": total_batches,
                    "duration_ms": round(duration_ms, 2),
                    "items_in_batch": len(batch)
                }
            )
            
        except Exception as e:
            failed += len(batch)
            logger.error(
                f"Batch {batch_num}/{total_batches} failed",
                extra={"batch_num": batch_num, "error": str(e)},
                exc_info=True
            )
            # Continue processing other batches
    
    return {
        "total_items": total_items,
        "processed": processed,
        "failed": failed,
        "batches": total_batches,
        "results": results,
        "success_rate": (processed / total_items * 100) if total_items > 0 else 0
    }


def calculate_optimal_batch_size(
    estimated_count: int,
    operation_name: str,
    pg_hook: Optional[PostgresHook] = None
) -> int:
    """
    Calculate optimal batch size based on historical performance.
    
    Returns batch size between BATCH_SIZE_MIN and BATCH_SIZE_MAX.
    """
    if not BATCH_SIZE_ADAPTIVE or estimated_count < BATCH_SIZE:
        return BATCH_SIZE
    
    try:
        if not pg_hook:
            pg_hook = get_pg_hook()
        
        # Get historical performance
        perf_sql = """
            SELECT batch_size, duration_ms, records_processed
            FROM approval_cleanup_performance
            WHERE operation_name = %s
              AND cleanup_date >= NOW() - INTERVAL '30 days'
            ORDER BY cleanup_date DESC
            LIMIT 10
        """
        
        try:
            perf_history = pg_hook.get_records(perf_sql, parameters=(operation_name,))
        except Exception:
            return BATCH_SIZE
        
        if not perf_history:
            return BATCH_SIZE
        
        # Calculate throughput by batch size
        throughput_by_batch = {}
        for row in perf_history:
            batch_size, duration_ms, records = row[0] or BATCH_SIZE, row[1] or 0, row[2] or 0
            if duration_ms > 0 and records > 0:
                throughput = records / (duration_ms / 1000)  # records per second
                if batch_size not in throughput_by_batch:
                    throughput_by_batch[batch_size] = []
                throughput_by_batch[batch_size].append(throughput)
        
        if not throughput_by_batch:
            return BATCH_SIZE
        
        # Find best batch size
        best_batch_size = BATCH_SIZE
        best_avg_throughput = 0
        
        for batch_size, throughputs in throughput_by_batch.items():
            avg_throughput = sum(throughputs) / len(throughputs)
            if avg_throughput > best_avg_throughput:
                best_avg_throughput = avg_throughput
                best_batch_size = batch_size
        
        # Ensure in valid range
        optimal_size = max(BATCH_SIZE_MIN, min(BATCH_SIZE_MAX, best_batch_size))
        
        logger.debug(
            f"Optimal batch size calculated: {optimal_size}",
            extra={
                "operation": operation_name,
                "estimated_count": estimated_count,
                "best_throughput": round(best_avg_throughput, 2)
            }
        )
        
        return int(optimal_size)
        
    except Exception as e:
        logger.warning(f"Failed to calculate optimal batch size: {e}", exc_info=True)
        return BATCH_SIZE


def track_performance(
    operation_name: str,
    duration_ms: float,
    records_processed: int,
    batch_size: int,
    pg_hook: Optional[PostgresHook] = None
) -> None:
    """Track performance metrics for future analysis."""
    try:
        if not pg_hook:
            pg_hook = get_pg_hook()
        
        # Create performance table if not exists
        create_sql = """
            CREATE TABLE IF NOT EXISTS approval_cleanup_performance (
                id BIGSERIAL PRIMARY KEY,
                operation_name VARCHAR(255) NOT NULL,
                duration_ms FLOAT NOT NULL,
                records_processed INTEGER NOT NULL,
                batch_size INTEGER NOT NULL,
                throughput_per_sec FLOAT,
                cleanup_date TIMESTAMPTZ DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_perf_operation_date 
                ON approval_cleanup_performance(operation_name, cleanup_date DESC);
        """
        
        pg_hook.run(create_sql)
        
        throughput = records_processed / (duration_ms / 1000) if duration_ms > 0 else 0
        
        insert_sql = """
            INSERT INTO approval_cleanup_performance 
                (operation_name, duration_ms, records_processed, batch_size, throughput_per_sec)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        pg_hook.run(
            insert_sql,
            parameters=(operation_name, duration_ms, records_processed, batch_size, throughput)
        )
        
        # Cleanup old data (keep only last 60 days)
        cleanup_sql = """
            DELETE FROM approval_cleanup_performance
            WHERE cleanup_date < NOW() - INTERVAL '60 days'
        """
        pg_hook.run(cleanup_sql)
        
    except Exception as e:
        logger.debug(f"Failed to track performance: {e}", exc_info=True)

