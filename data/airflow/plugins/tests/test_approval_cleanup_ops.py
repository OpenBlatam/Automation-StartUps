"""
Tests para approval_cleanup_ops.py
Mejorado con parametrización, mejores mocks y casos edge adicionales.
"""
from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.exceptions import AirflowFailException

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
    
    @pytest.fixture
    def mock_db_setup(self):
        """Fixture para setup de mocks de base de datos"""
        mock_hook = Mock()
        mock_conn = Mock()
        mock_cursor = Mock()
        
        mock_hook.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        return {
            'hook': mock_hook,
            'conn': mock_conn,
            'cursor': mock_cursor
        }
    
    @patch('data.airflow.plugins.approval_cleanup_ops.time.perf_counter')
    def test_execute_query_success(self, mock_perf_counter, mock_db_setup):
        """Test ejecución exitosa de query"""
        mock_db_setup['cursor'].description = [('col1',)]
        mock_db_setup['cursor'].fetchall.return_value = [('result',)]
        mock_perf_counter.side_effect = [0, 0.1]  # start, end
        
        result = execute_query_with_timeout(
            mock_db_setup['hook'],
            "SELECT 1",
            timeout_seconds=30
        )
        
        assert result == [('result',)]
        assert mock_db_setup['cursor'].execute.call_count >= 2  # SET timeout + query
        mock_db_setup['conn'].commit.assert_called_once()
        mock_db_setup['cursor'].close.assert_called_once()
        mock_db_setup['conn'].close.assert_called_once()
    
    @pytest.mark.parametrize("sql,parameters,expected_calls", [
        ("SELECT * FROM table WHERE id = %s", (1,), 2),
        ("INSERT INTO table VALUES (%s, %s)", (1, 'test'), 2),
        ("UPDATE table SET col = %s", ('value',), 2),
        ("DELETE FROM table WHERE id = %s", (1,), 2),
    ])
    def test_execute_query_with_parameters(self, mock_db_setup, sql, parameters, expected_calls):
        """Test ejecución de query con diferentes parámetros"""
        mock_db_setup['cursor'].description = None
        
        execute_query_with_timeout(
            mock_db_setup['hook'],
            sql,
            parameters=parameters,
            timeout_seconds=30
        )
        
        assert mock_db_setup['cursor'].execute.call_count >= expected_calls
        mock_db_setup['conn'].commit.assert_called_once()
    
    @patch('data.airflow.plugins.approval_cleanup_ops.time.perf_counter')
    def test_execute_query_timeout_error(self, mock_perf_counter, mock_db_setup):
        """Test cuando se excede el timeout"""
        mock_perf_counter.side_effect = [0, 35]  # Simula que pasó el timeout
        mock_db_setup['cursor'].execute.side_effect = Exception("statement_timeout exceeded")
        
        with pytest.raises(AirflowFailException, match="timeout"):
            execute_query_with_timeout(
                mock_db_setup['hook'],
                "SELECT * FROM large_table",
                timeout_seconds=30
            )
        
        mock_db_setup['conn'].rollback.assert_called_once()
    
    def test_execute_query_no_results(self, mock_db_setup):
        """Test query que no retorna resultados (INSERT/UPDATE/DELETE)"""
        mock_db_setup['cursor'].description = None
        
        result = execute_query_with_timeout(
            mock_db_setup['hook'],
            "INSERT INTO table VALUES (1)",
            timeout_seconds=30
        )
        
        assert result is None
        mock_db_setup['conn'].commit.assert_called_once()
    
    def test_execute_query_connection_error(self, mock_db_setup):
        """Test manejo de error de conexión"""
        mock_db_setup['hook'].get_conn.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception, match="Connection"):
            execute_query_with_timeout(
                mock_db_setup['hook'],
                "SELECT 1",
                timeout_seconds=30
            )


class TestProcessBatch:
    """Tests para process_batch"""
    
    @pytest.mark.parametrize("items,batch_size,expected_batches", [
        ([1, 2, 3, 4, 5], 2, 3),
        ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3, 4),
        ([1, 2, 3], 5, 1),
        ([], 10, 0),
        (list(range(1, 101)), 25, 4),
    ])
    def test_process_batch_success(self, items, batch_size, expected_batches):
        """Test procesamiento exitoso de batch con diferentes tamaños"""
        def processor(batch):
            return {'processed': len(batch), 'items': batch}
        
        result = process_batch(items, batch_size, processor, "test_operation")
        
        assert result['total_items'] == len(items)
        assert result['processed'] == len(items)
        assert result['failed'] == 0
        assert result['batches'] == expected_batches
        assert result['success_rate'] == 100.0
    
    @pytest.mark.parametrize("failure_batch,expected_failed", [
        (1, 2),  # Falla en primer batch
        (2, 3),  # Falla en segundo batch
        (3, 5),  # Falla en último batch
    ])
    def test_process_batch_with_failures(self, failure_batch, expected_failed):
        """Test procesamiento de batch con fallos en diferentes posiciones"""
        items = [1, 2, 3, 4, 5]
        batch_size = 2
        
        call_count = [0]
        def processor(batch):
            call_count[0] += 1
            if call_count[0] == failure_batch:
                raise Exception(f"Batch {failure_batch} failed")
            return {'processed': len(batch), 'items': batch}
        
        result = process_batch(items, batch_size, processor, "test_operation")
        
        assert result['total_items'] == 5
        assert result['failed'] == expected_failed
        assert result['success_rate'] < 100.0
        assert result['processed'] == (5 - expected_failed)
    
    def test_process_batch_all_failures(self):
        """Test cuando todos los batches fallan"""
        items = [1, 2, 3, 4, 5]
        
        def processor(batch):
            raise Exception("Always fails")
        
        result = process_batch(items, 2, processor, "test_operation")
        
        assert result['total_items'] == 5
        assert result['processed'] == 0
        assert result['failed'] == 5
        assert result['success_rate'] == 0.0
    
    def test_process_batch_single_item(self):
        """Test procesamiento con un solo item"""
        items = [1]
        
        def processor(batch):
            return {'processed': len(batch)}
        
        result = process_batch(items, 10, processor, "test_operation")
        
        assert result['total_items'] == 1
        assert result['processed'] == 1
        assert result['batches'] == 1
        assert result['success_rate'] == 100.0
    
    def test_process_batch_empty_list(self):
        """Test procesamiento con lista vacía"""
        items = []
        
        def processor(batch):
            return {'processed': len(batch)}
        
        result = process_batch(items, 10, processor, "test_operation")
        
        assert result['total_items'] == 0
        assert result['processed'] == 0
        assert result['batches'] == 0
        assert result['success_rate'] == 100.0
    
    def test_process_batch_partial_success(self):
        """Test cuando algunos items fallan pero otros tienen éxito"""
        items = [1, 2, 3, 4, 5]
        
        def processor(batch):
            # Falla si el batch contiene el número 3
            if 3 in batch:
                raise Exception("Item 3 failed")
            return {'processed': len(batch)}
        
        result = process_batch(items, 2, processor, "test_operation")
        
        assert result['total_items'] == 5
        assert result['failed'] > 0
        assert result['processed'] < 5
        assert 0 < result['success_rate'] < 100.0


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


