"""
Tests para approval_cleanup_ops.py
"""
from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, MagicMock
from airflow.providers.postgres.hooks.postgres import PostgresHook

from data.airflow.plugins.approval_cleanup_ops import (
    get_pg_hook,
    execute_query_with_timeout,
    process_batch,
    calculate_optimal_batch_size,
    track_performance,
)


class TestGetPgHook:
    """Tests para get_pg_hook"""
    
    @patch('data.airflow.plugins.approval_cleanup_ops.PostgresHook')
    def test_get_pg_hook_creates_connection(self, mock_postgres_hook):
        """Test que get_pg_hook crea un hook de PostgreSQL"""
        mock_hook = Mock()
        mock_postgres_hook.return_value = mock_hook
        
        hook = get_pg_hook()
        
        mock_postgres_hook.assert_called_once()
        assert hook == mock_hook
    
    @patch('data.airflow.plugins.approval_cleanup_ops.PostgresHook')
    def test_get_pg_hook_caches_result(self, mock_postgres_hook):
        """Test que get_pg_hook cachea el resultado"""
        mock_hook = Mock()
        mock_postgres_hook.return_value = mock_hook
        
        hook1 = get_pg_hook()
        hook2 = get_pg_hook()
        
        # Debería llamarse solo una vez debido al cache
        assert mock_postgres_hook.call_count == 1
        assert hook1 == hook2


class TestExecuteQueryWithTimeout:
    """Tests para execute_query_with_timeout"""
    
    @patch('data.airflow.plugins.approval_cleanup_ops.time.perf_counter')
    def test_execute_query_success(self, mock_perf_counter):
        """Test ejecución exitosa de query"""
        mock_hook = Mock()
        mock_conn = Mock()
        mock_cursor = Mock()
        
        mock_hook.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.description = [('col1',)]
        mock_cursor.fetchall.return_value = [('result',)]
        
        mock_perf_counter.side_effect = [0, 0.1]  # start, end
        
        result = execute_query_with_timeout(
            mock_hook,
            "SELECT 1",
            timeout_seconds=30
        )
        
        assert result == [('result',)]
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()
    
    def test_execute_query_with_parameters(self):
        """Test ejecución de query con parámetros"""
        mock_hook = Mock()
        mock_conn = Mock()
        mock_cursor = Mock()
        
        mock_hook.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.description = None
        
        execute_query_with_timeout(
            mock_hook,
            "SELECT * FROM table WHERE id = %s",
            parameters=(1,),
            timeout_seconds=30
        )
        
        # Verificar que se ejecutó con parámetros
        assert mock_cursor.execute.call_count >= 2  # SET timeout + query
        mock_conn.commit.assert_called()


class TestProcessBatch:
    """Tests para process_batch"""
    
    def test_process_batch_success(self):
        """Test procesamiento exitoso de batch"""
        items = [1, 2, 3, 4, 5]
        batch_size = 2
        
        def processor(batch):
            return {'processed': len(batch), 'items': batch}
        
        result = process_batch(items, batch_size, processor, "test_operation")
        
        assert result['total_items'] == 5
        assert result['processed'] == 5
        assert result['failed'] == 0
        assert result['batches'] == 3
        assert result['success_rate'] == 100.0
    
    def test_process_batch_with_failures(self):
        """Test procesamiento de batch con fallos"""
        items = [1, 2, 3, 4, 5]
        batch_size = 2
        
        call_count = [0]
        def processor(batch):
            call_count[0] += 1
            if call_count[0] == 2:  # Falla en el segundo batch
                raise Exception("Batch failed")
            return {'processed': len(batch), 'items': batch}
        
        result = process_batch(items, batch_size, processor, "test_operation")
        
        assert result['total_items'] == 5
        assert result['processed'] == 2  # Solo el primer batch
        assert result['failed'] == 3  # El segundo y tercer batch fallaron
        assert result['success_rate'] < 100.0


class TestCalculateOptimalBatchSize:
    """Tests para calculate_optimal_batch_size"""
    
    @patch('data.airflow.plugins.approval_cleanup_ops.get_pg_hook')
    def test_calculate_optimal_batch_size_no_history(self, mock_get_hook):
        """Test cuando no hay historial de performance"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_records.side_effect = Exception("No table")
        
        from data.airflow.plugins.approval_cleanup_config import BATCH_SIZE
        
        result = calculate_optimal_batch_size(1000, "test_op")
        
        assert result == BATCH_SIZE
    
    @patch('data.airflow.plugins.approval_cleanup_ops.get_pg_hook')
    def test_calculate_optimal_batch_size_with_history(self, mock_get_hook):
        """Test cálculo con historial disponible"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        
        # Simular historial: batch_size=2000 tiene mejor throughput
        mock_hook.get_records.return_value = [
            (1000, 5000, 1000),  # batch_size, duration_ms, records
            (2000, 6000, 2000),  # Mejor throughput
            (500, 3000, 500),
        ]
        
        result = calculate_optimal_batch_size(5000, "test_op")
        
        # Debería elegir 2000 (mejor throughput)
        assert result == 2000


class TestTrackPerformance:
    """Tests para track_performance"""
    
    @patch('data.airflow.plugins.approval_cleanup_ops.get_pg_hook')
    def test_track_performance_success(self, mock_get_hook):
        """Test tracking exitoso de performance"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        
        track_performance(
            "test_operation",
            1000.0,  # duration_ms
            500,     # records_processed
            100,     # batch_size
            mock_hook
        )
        
        # Verificar que se creó la tabla
        assert mock_hook.run.call_count >= 1
        # Verificar que se insertó el registro
        insert_calls = [call for call in mock_hook.run.call_args_list 
                       if 'INSERT' in str(call)]
        assert len(insert_calls) > 0


