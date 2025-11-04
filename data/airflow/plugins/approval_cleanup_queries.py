"""
SQL queries for approval cleanup operations.
Centralizes all database queries for maintainability and reusability.
"""
from __future__ import annotations

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from airflow.providers.postgres.hooks.postgres import PostgresHook

from .approval_cleanup_ops import get_pg_hook, execute_query_with_timeout


def check_table_exists(table_name: str, schema: str = 'public', pg_hook: Optional[PostgresHook] = None) -> bool:
    """Check if a table exists."""
    if not pg_hook:
        pg_hook = get_pg_hook()
    
    check_sql = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = %s
            AND table_name = %s
        );
    """
    
    result = pg_hook.get_first(check_sql, parameters=(schema, table_name))
    return result[0] if result else False


def create_archive_table(pg_hook: Optional[PostgresHook] = None) -> None:
    """Create archive table if it doesn't exist."""
    if not pg_hook:
        pg_hook = get_pg_hook()
    
    # Check if main table exists first
    if not check_table_exists('approval_requests', pg_hook=pg_hook):
        raise Exception("Main table 'approval_requests' does not exist")
    
    create_sql = """
        CREATE TABLE IF NOT EXISTS approval_requests_archive (
            LIKE approval_requests INCLUDING ALL
        );
        
        CREATE INDEX IF NOT EXISTS idx_archive_request_id 
            ON approval_requests_archive(id);
        CREATE INDEX IF NOT EXISTS idx_archive_completed_at 
            ON approval_requests_archive(completed_at);
        CREATE INDEX IF NOT EXISTS idx_archive_status 
            ON approval_requests_archive(status);
        CREATE INDEX IF NOT EXISTS idx_archive_created_at 
            ON approval_requests_archive(created_at);
    """
    
    pg_hook.run(create_sql)


def get_old_requests_to_archive(
    retention_years: int,
    batch_size: int = 1000,
    pg_hook: Optional[PostgresHook] = None
) -> List[Tuple[int, ...]]:
    """Get old completed requests to archive."""
    if not pg_hook:
        pg_hook = get_pg_hook()
    
    sql = """
        SELECT id, status, completed_at, created_at
        FROM approval_requests
        WHERE status = 'completed'
          AND completed_at < NOW() - INTERVAL '%s years'
        ORDER BY completed_at ASC
        LIMIT %s
    """
    
    return pg_hook.get_records(sql, parameters=(retention_years, batch_size))


def archive_requests_batch(
    request_ids: List[int],
    pg_hook: Optional[PostgresHook] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """Archive a batch of requests."""
    if not pg_hook:
        pg_hook = get_pg_hook()
    
    if dry_run:
        return {
            'archived': len(request_ids),
            'dry_run': True
        }
    
    if not request_ids:
        return {'archived': 0}
    
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    try:
        # Create placeholders for IN clause
        placeholders = ','.join(['%s'] * len(request_ids))
        
        # Insert into archive
        insert_sql = f"""
            INSERT INTO approval_requests_archive
            SELECT * FROM approval_requests
            WHERE id IN ({placeholders})
        """
        
        cursor.execute(insert_sql, request_ids)
        
        # Delete from main table
        delete_sql = f"""
            DELETE FROM approval_requests
            WHERE id IN ({placeholders})
        """
        
        cursor.execute(delete_sql, request_ids)
        
        conn.commit()
        
        return {
            'archived': cursor.rowcount,
            'request_ids': request_ids
        }
        
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def get_expired_notifications(
    retention_months: int,
    pg_hook: Optional[PostgresHook] = None
) -> List[Tuple[int, ...]]:
    """Get expired notifications to delete."""
    if not pg_hook:
        pg_hook = get_pg_hook()
    
    sql = """
        SELECT id, notification_type, created_at
        FROM approval_notifications
        WHERE created_at < NOW() - INTERVAL '%s months'
        ORDER BY created_at ASC
    """
    
    return pg_hook.get_records(sql, parameters=(retention_months,))


def delete_notifications_batch(
    notification_ids: List[int],
    pg_hook: Optional[PostgresHook] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """Delete a batch of notifications."""
    if not pg_hook:
        pg_hook = get_pg_hook()
    
    if dry_run:
        return {
            'deleted': len(notification_ids),
            'dry_run': True
        }
    
    if not notification_ids:
        return {'deleted': 0}
    
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    try:
        placeholders = ','.join(['%s'] * len(notification_ids))
        delete_sql = f"""
            DELETE FROM approval_notifications
            WHERE id IN ({placeholders})
        """
        
        cursor.execute(delete_sql, notification_ids)
        conn.commit()
        
        return {
            'deleted': cursor.rowcount,
            'notification_ids': notification_ids
        }
        
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def get_stale_pending_requests(
    stale_threshold_days: int = 90,
    pg_hook: Optional[PostgresHook] = None
) -> List[Tuple[int, ...]]:
    """Get stale pending requests."""
    if not pg_hook:
        pg_hook = get_pg_hook()
    
    sql = """
        SELECT id, status, created_at, updated_at
        FROM approval_requests
        WHERE status = 'pending'
          AND updated_at < NOW() - INTERVAL '%s days'
        ORDER BY updated_at ASC
    """
    
    return pg_hook.get_records(sql, parameters=(stale_threshold_days,))


def create_history_table(pg_hook: Optional[PostgresHook] = None) -> None:
    """Create history table for tracking cleanup operations."""
    if not pg_hook:
        pg_hook = get_pg_hook()
    
    create_sql = """
        CREATE TABLE IF NOT EXISTS approval_cleanup_history (
            id BIGSERIAL PRIMARY KEY,
            cleanup_date TIMESTAMPTZ DEFAULT NOW(),
            archived_count INTEGER DEFAULT 0,
            deleted_count INTEGER DEFAULT 0,
            notifications_deleted INTEGER DEFAULT 0,
            stale_count INTEGER DEFAULT 0,
            database_size_bytes BIGINT DEFAULT 0,
            total_pending INTEGER DEFAULT 0,
            total_completed INTEGER DEFAULT 0,
            indexes_optimized INTEGER DEFAULT 0,
            views_refreshed INTEGER DEFAULT 0,
            execution_duration_ms FLOAT,
            dry_run BOOLEAN DEFAULT FALSE,
            notes TEXT
        );
        
        CREATE INDEX IF NOT EXISTS idx_cleanup_history_date 
            ON approval_cleanup_history(cleanup_date DESC);
    """
    
    pg_hook.run(create_sql)


def insert_cleanup_history(
    data: Dict[str, Any],
    pg_hook: Optional[PostgresHook] = None
) -> int:
    """Insert cleanup history record."""
    if not pg_hook:
        pg_hook = get_pg_hook()
    
    create_history_table(pg_hook=pg_hook)
    
    insert_sql = """
        INSERT INTO approval_cleanup_history (
            archived_count, deleted_count, notifications_deleted,
            stale_count, database_size_bytes, total_pending, total_completed,
            indexes_optimized, views_refreshed, execution_duration_ms,
            dry_run, notes
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        RETURNING id
    """
    
    result = pg_hook.get_first(
        insert_sql,
        parameters=(
            data.get('archived_count', 0),
            data.get('deleted_count', 0),
            data.get('notifications_deleted', 0),
            data.get('stale_count', 0),
            data.get('database_size_bytes', 0),
            data.get('total_pending', 0),
            data.get('total_completed', 0),
            data.get('indexes_optimized', 0),
            data.get('views_refreshed', 0),
            data.get('execution_duration_ms'),
            data.get('dry_run', False),
            data.get('notes')
        )
    )
    
    return result[0] if result else 0


def get_database_size(pg_hook: Optional[PostgresHook] = None) -> Dict[str, Any]:
    """Get database size information."""
    if not pg_hook:
        pg_hook = get_pg_hook()
    
    sql = """
        SELECT 
            pg_database.datname,
            pg_size_pretty(pg_database_size(pg_database.datname)) AS size,
            pg_database_size(pg_database.datname) AS size_bytes
        FROM pg_database
        WHERE datname = current_database()
    """
    
    result = pg_hook.get_first(sql)
    if result:
        return {
            'database_name': result[0],
            'size_pretty': result[1],
            'size_bytes': result[2]
        }
    return {'size_bytes': 0}


def get_table_sizes(pg_hook: Optional[PostgresHook] = None) -> List[Dict[str, Any]]:
    """Get sizes of all approval-related tables."""
    if not pg_hook:
        pg_hook = get_pg_hook()
    
    sql = """
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
            pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes,
            pg_relation_size(schemaname||'.'||tablename) AS table_size_bytes,
            pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename) AS indexes_size_bytes
        FROM pg_tables
        WHERE schemaname = 'public'
          AND tablename LIKE 'approval_%'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
    """
    
    records = pg_hook.get_records(sql)
    return [
        {
            'schema': row[0],
            'table': row[1],
            'size_pretty': row[2],
            'total_bytes': row[3],
            'table_bytes': row[4],
            'indexes_bytes': row[5]
        }
        for row in records
    ]


def get_request_counts(pg_hook: Optional[PostgresHook] = None) -> Dict[str, int]:
    """Get counts of requests by status."""
    if not pg_hook:
        pg_hook = get_pg_hook()
    
    sql = """
        SELECT 
            status,
            COUNT(*) as count
        FROM approval_requests
        GROUP BY status
    """
    
    records = pg_hook.get_records(sql)
    return {row[0]: row[1] for row in records}


def get_cleanup_history(
    days: int = 30,
    pg_hook: Optional[PostgresHook] = None
) -> List[Dict[str, Any]]:
    """Get cleanup history for analysis."""
    if not pg_hook:
        pg_hook = get_pg_hook()
    
    sql = """
        SELECT 
            id, cleanup_date, archived_count, deleted_count,
            notifications_deleted, database_size_bytes, total_pending,
            total_completed, execution_duration_ms, dry_run
        FROM approval_cleanup_history
        WHERE cleanup_date >= NOW() - INTERVAL '%s days'
        ORDER BY cleanup_date DESC
    """
    
    records = pg_hook.get_records(sql, parameters=(days,))
    return [
        {
            'id': row[0],
            'cleanup_date': row[1],
            'archived_count': row[2],
            'deleted_count': row[3],
            'notifications_deleted': row[4],
            'database_size_bytes': row[5],
            'total_pending': row[6],
            'total_completed': row[7],
            'execution_duration_ms': row[8],
            'dry_run': row[9]
        }
        for row in records
    ]



