"""
Tests para approval_cleanup_queries.py
"""
from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, MagicMock
from airflow.providers.postgres.hooks.postgres import PostgresHook

from data.airflow.plugins.approval_cleanup_queries import (
    check_table_exists,
    create_archive_table,
    get_old_requests_to_archive,
    archive_requests_batch,
    get_expired_notifications,
    delete_notifications_batch,
    get_stale_pending_requests,
    create_history_table,
    insert_cleanup_history,
    get_database_size,
    get_table_sizes,
    get_request_counts,
    get_cleanup_history,
)


class TestCheckTableExists:
    """Tests para check_table_exists"""
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_check_table_exists_true(self, mock_get_hook):
        """Test cuando la tabla existe"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_first.return_value = (True,)
        
        result = check_table_exists('approval_requests')
        
        assert result is True
        mock_hook.get_first.assert_called_once()
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_check_table_exists_false(self, mock_get_hook):
        """Test cuando la tabla no existe"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_first.return_value = (False,)
        
        result = check_table_exists('nonexistent_table')
        
        assert result is False
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_check_table_exists_with_custom_schema(self, mock_get_hook):
        """Test con schema personalizado"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_first.return_value = (True,)
        
        result = check_table_exists('test_table', schema='custom_schema')
        
        assert result is True
        # Verificar que se pasó el schema correcto
        call_args = mock_hook.get_first.call_args
        assert 'custom_schema' in str(call_args)


class TestCreateArchiveTable:
    """Tests para create_archive_table"""
    
    @patch('data.airflow.plugins.approval_cleanup_queries.check_table_exists')
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_create_archive_table_success(self, mock_get_hook, mock_check_table):
        """Test creación exitosa de tabla de archivo"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_check_table.return_value = True  # Tabla principal existe
        
        create_archive_table()
        
        # Verificar que se ejecutó el SQL
        assert mock_hook.run.called
    
    @patch('data.airflow.plugins.approval_cleanup_queries.check_table_exists')
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_create_archive_table_main_table_missing(self, mock_get_hook, mock_check_table):
        """Test cuando la tabla principal no existe"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_check_table.return_value = False  # Tabla principal no existe
        
        with pytest.raises(Exception, match="Main table 'approval_requests' does not exist"):
            create_archive_table()


class TestGetOldRequestsToArchive:
    """Tests para get_old_requests_to_archive"""
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_get_old_requests_to_archive(self, mock_get_hook):
        """Test obtener requests antiguos para archivar"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_records.return_value = [
            (1, 'completed', '2020-01-01', '2019-01-01'),
            (2, 'completed', '2020-02-01', '2019-02-01'),
        ]
        
        result = get_old_requests_to_archive(retention_years=2, batch_size=100)
        
        assert len(result) == 2
        assert result[0][0] == 1
        mock_hook.get_records.assert_called_once()
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_get_old_requests_to_archive_empty(self, mock_get_hook):
        """Test cuando no hay requests antiguos"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_records.return_value = []
        
        result = get_old_requests_to_archive(retention_years=2)
        
        assert len(result) == 0


class TestArchiveRequestsBatch:
    """Tests para archive_requests_batch"""
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_archive_requests_batch_dry_run(self, mock_get_hook):
        """Test archivo en modo dry_run"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        
        result = archive_requests_batch([1, 2, 3], dry_run=True)
        
        assert result['archived'] == 3
        assert result['dry_run'] is True
        mock_hook.get_conn.assert_not_called()
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_archive_requests_batch_empty_list(self, mock_get_hook):
        """Test con lista vacía"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        
        result = archive_requests_batch([], dry_run=False)
        
        assert result['archived'] == 0
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_archive_requests_batch_success(self, mock_get_hook):
        """Test archivo exitoso de requests"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_hook.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 2
        
        result = archive_requests_batch([1, 2], dry_run=False)
        
        assert result['archived'] == 2
        assert result['request_ids'] == [1, 2]
        assert mock_cursor.execute.call_count == 2  # INSERT + DELETE
        mock_conn.commit.assert_called_once()
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_archive_requests_batch_rollback_on_error(self, mock_get_hook):
        """Test rollback en caso de error"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_hook.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")
        
        with pytest.raises(Exception, match="Database error"):
            archive_requests_batch([1, 2], dry_run=False)
        
        mock_conn.rollback.assert_called_once()


class TestGetExpiredNotifications:
    """Tests para get_expired_notifications"""
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_get_expired_notifications(self, mock_get_hook):
        """Test obtener notificaciones expiradas"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_records.return_value = [
            (1, 'email', '2020-01-01'),
            (2, 'slack', '2020-02-01'),
        ]
        
        result = get_expired_notifications(retention_months=6)
        
        assert len(result) == 2
        assert result[0][0] == 1
        mock_hook.get_records.assert_called_once()


class TestDeleteNotificationsBatch:
    """Tests para delete_notifications_batch"""
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_delete_notifications_batch_dry_run(self, mock_get_hook):
        """Test eliminación en modo dry_run"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        
        result = delete_notifications_batch([1, 2, 3], dry_run=True)
        
        assert result['deleted'] == 3
        assert result['dry_run'] is True
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_delete_notifications_batch_success(self, mock_get_hook):
        """Test eliminación exitosa"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_hook.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 3
        
        result = delete_notifications_batch([1, 2, 3], dry_run=False)
        
        assert result['deleted'] == 3
        assert result['notification_ids'] == [1, 2, 3]
        mock_conn.commit.assert_called_once()


class TestGetStalePendingRequests:
    """Tests para get_stale_pending_requests"""
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_get_stale_pending_requests(self, mock_get_hook):
        """Test obtener requests pending stale"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_records.return_value = [
            (1, 'pending', '2020-01-01', '2020-01-01'),
            (2, 'pending', '2020-02-01', '2020-02-01'),
        ]
        
        result = get_stale_pending_requests(stale_threshold_days=90)
        
        assert len(result) == 2
        mock_hook.get_records.assert_called_once()


class TestCreateHistoryTable:
    """Tests para create_history_table"""
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_create_history_table(self, mock_get_hook):
        """Test creación de tabla de historial"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        
        create_history_table()
        
        # Verificar que se ejecutó el SQL
        assert mock_hook.run.called
        # Verificar que el SQL contiene CREATE TABLE
        call_args = str(mock_hook.run.call_args)
        assert 'CREATE TABLE' in call_args or 'approval_cleanup_history' in call_args


class TestInsertCleanupHistory:
    """Tests para insert_cleanup_history"""
    
    @patch('data.airflow.plugins.approval_cleanup_queries.create_history_table')
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_insert_cleanup_history(self, mock_get_hook, mock_create_table):
        """Test insertar historial de limpieza"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_first.return_value = (42,)  # ID retornado
        
        data = {
            'archived_count': 10,
            'deleted_count': 5,
            'notifications_deleted': 3,
            'execution_duration_ms': 1500.5,
            'dry_run': False
        }
        
        result = insert_cleanup_history(data)
        
        assert result == 42
        mock_create_table.assert_called_once()
        mock_hook.get_first.assert_called_once()
    
    @patch('data.airflow.plugins.approval_cleanup_queries.create_history_table')
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_insert_cleanup_history_with_defaults(self, mock_get_hook, mock_create_table):
        """Test insertar historial con valores por defecto"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_first.return_value = (1,)
        
        result = insert_cleanup_history({})  # Datos vacíos
        
        assert result == 1
        # Verificar que se usaron valores por defecto
        call_args = mock_hook.get_first.call_args
        assert call_args is not None


class TestGetDatabaseSize:
    """Tests para get_database_size"""
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_get_database_size(self, mock_get_hook):
        """Test obtener tamaño de base de datos"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_first.return_value = (
            'test_db',
            '1.5 GB',
            1610612736  # bytes
        )
        
        result = get_database_size()
        
        assert result['database_name'] == 'test_db'
        assert result['size_pretty'] == '1.5 GB'
        assert result['size_bytes'] == 1610612736
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_get_database_size_no_result(self, mock_get_hook):
        """Test cuando no hay resultado"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_first.return_value = None
        
        result = get_database_size()
        
        assert result['size_bytes'] == 0


class TestGetTableSizes:
    """Tests para get_table_sizes"""
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_get_table_sizes(self, mock_get_hook):
        """Test obtener tamaños de tablas"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_records.return_value = [
            ('public', 'approval_requests', '500 MB', 524288000, 400000000, 124288000),
            ('public', 'approval_notifications', '100 MB', 104857600, 80000000, 24857600),
        ]
        
        result = get_table_sizes()
        
        assert len(result) == 2
        assert result[0]['table'] == 'approval_requests'
        assert result[0]['total_bytes'] == 524288000
        assert result[0]['table_bytes'] == 400000000
        assert result[0]['indexes_bytes'] == 124288000


class TestGetRequestCounts:
    """Tests para get_request_counts"""
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_get_request_counts(self, mock_get_hook):
        """Test obtener conteos de requests por status"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_records.return_value = [
            ('pending', 10),
            ('completed', 50),
            ('rejected', 5),
        ]
        
        result = get_request_counts()
        
        assert result['pending'] == 10
        assert result['completed'] == 50
        assert result['rejected'] == 5
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_get_request_counts_empty(self, mock_get_hook):
        """Test cuando no hay requests"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_records.return_value = []
        
        result = get_request_counts()
        
        assert result == {}


class TestGetCleanupHistory:
    """Tests para get_cleanup_history"""
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_get_cleanup_history(self, mock_get_hook):
        """Test obtener historial de limpieza"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        from datetime import datetime
        mock_hook.get_records.return_value = [
            (
                1,
                datetime(2025, 1, 1),
                10,
                5,
                3,
                1000000,
                20,
                50,
                1500.5,
                False
            ),
        ]
        
        result = get_cleanup_history(days=30)
        
        assert len(result) == 1
        assert result[0]['id'] == 1
        assert result[0]['archived_count'] == 10
        assert result[0]['deleted_count'] == 5
        assert result[0]['notifications_deleted'] == 3
        assert result[0]['execution_duration_ms'] == 1500.5
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_get_cleanup_history_empty(self, mock_get_hook):
        """Test cuando no hay historial"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_records.return_value = []
        
        result = get_cleanup_history(days=30)
        
        assert result == []

