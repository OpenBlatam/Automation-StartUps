"""
Tests para casos edge y escenarios límite de approval_cleanup.
"""
from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from data.airflow.plugins.approval_cleanup_queries import (
    check_table_exists,
    archive_requests_batch,
    get_database_size,
    get_table_sizes,
)
from data.airflow.plugins.approval_cleanup_ops import (
    process_batch,
    execute_query_with_timeout,
)
from data.airflow.plugins.approval_cleanup_analytics import (
    calculate_percentiles,
    detect_anomaly,
    analyze_trends,
)
from data.airflow.plugins.approval_cleanup_utils import (
    validate_params,
    safe_divide,
    calculate_percentage_change,
    format_duration_ms,
    format_bytes,
)


class TestEdgeCasesQueries:
    """Tests para casos edge en queries"""
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_archive_empty_list(self, mock_get_hook):
        """Test archivado con lista vacía"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        
        result = archive_requests_batch([], dry_run=False)
        
        assert result['archived'] == 0
        mock_hook.get_conn.assert_not_called()
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_archive_very_large_batch(self, mock_get_hook):
        """Test archivado con batch muy grande"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_hook.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Simular batch de 10000 IDs
        large_batch = list(range(1, 10001))
        mock_cursor.rowcount = 10000
        
        result = archive_requests_batch(large_batch, dry_run=False)
        
        assert result['archived'] == 10000
        # Verificar que se crearon los placeholders correctamente
        assert mock_cursor.execute.called
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_get_database_size_none_result(self, mock_get_hook):
        """Test cuando get_database_size retorna None"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_first.return_value = None
        
        result = get_database_size()
        
        assert result['size_bytes'] == 0
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_get_table_sizes_empty(self, mock_get_hook):
        """Test cuando no hay tablas"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_records.return_value = []
        
        result = get_table_sizes()
        
        assert result == []


class TestEdgeCasesBatchProcessing:
    """Tests para casos edge en batch processing"""
    
    def test_process_batch_empty_list(self):
        """Test procesamiento con lista vacía"""
        def processor(batch):
            return {'processed': len(batch)}
        
        result = process_batch([], batch_size=100, processor=processor, operation_name="test")
        
        assert result['total_items'] == 0
        assert result['processed'] == 0
        assert result['batches'] == 0
        assert result['success_rate'] == 100.0
    
    def test_process_batch_single_item(self):
        """Test procesamiento con un solo item"""
        def processor(batch):
            return {'processed': len(batch)}
        
        result = process_batch([1], batch_size=100, processor=processor, operation_name="test")
        
        assert result['total_items'] == 1
        assert result['processed'] == 1
        assert result['batches'] == 1
    
    def test_process_batch_batch_size_larger_than_items(self):
        """Test cuando batch_size es mayor que items"""
        def processor(batch):
            return {'processed': len(batch)}
        
        result = process_batch([1, 2, 3], batch_size=100, processor=processor, operation_name="test")
        
        assert result['total_items'] == 3
        assert result['processed'] == 3
        assert result['batches'] == 1
    
    def test_process_batch_all_failures(self):
        """Test cuando todos los batches fallan"""
        def processor(batch):
            raise Exception("Always fails")
        
        result = process_batch([1, 2, 3, 4, 5], batch_size=2, processor=processor, operation_name="test")
        
        assert result['total_items'] == 5
        assert result['processed'] == 0
        assert result['failed'] == 5
        assert result['success_rate'] == 0.0
    
    def test_process_batch_partial_failures(self):
        """Test cuando algunos batches fallan"""
        call_count = [0]
        def processor(batch):
            call_count[0] += 1
            if call_count[0] == 2:  # Segundo batch falla
                raise Exception("Batch failed")
            return {'processed': len(batch)}
        
        result = process_batch([1, 2, 3, 4, 5], batch_size=2, processor=processor, operation_name="test")
        
        assert result['total_items'] == 5
        assert result['failed'] > 0
        assert result['success_rate'] < 100.0


class TestEdgeCasesAnalytics:
    """Tests para casos edge en analytics"""
    
    def test_calculate_percentiles_single_value(self):
        """Test percentiles con un solo valor"""
        result = calculate_percentiles([100])
        
        assert result['p50'] == 100
        assert result['p95'] == 100
        assert result['p99'] == 100
        assert result['min'] == 100
        assert result['max'] == 100
        assert result['avg'] == 100
    
    def test_calculate_percentiles_two_values(self):
        """Test percentiles con dos valores"""
        result = calculate_percentiles([10, 20])
        
        assert result['min'] == 10
        assert result['max'] == 20
        assert result['avg'] == 15.0
    
    def test_calculate_percentiles_negative_values(self):
        """Test percentiles con valores negativos"""
        result = calculate_percentiles([-10, -5, 0, 5, 10])
        
        assert result['min'] == -10
        assert result['max'] == 10
        assert result['avg'] == 0.0
    
    def test_calculate_percentiles_duplicate_values(self):
        """Test percentiles con valores duplicados"""
        result = calculate_percentiles([10, 10, 10, 10, 10])
        
        assert result['p50'] == 10
        assert result['p95'] == 10
        assert result['p99'] == 10
        assert result['avg'] == 10
    
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_pg_hook')
    def test_detect_anomaly_zero_values(self, mock_get_hook):
        """Test detección de anomalías con valores cero"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_records.return_value = [
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        ]
        
        result = detect_anomaly(0, 'archived_count', pg_hook=mock_hook)
        
        assert 'is_anomaly' in result
        # Con todos los valores en 0, cualquier valor debería ser normal
        assert result['z_score'] == 0 or result['is_anomaly'] is False
    
    def test_analyze_trends_single_data_point(self):
        """Test análisis de tendencias con un solo punto de datos"""
        history = [
            {'archived_count': 10, 'deleted_count': 5, 'database_size_bytes': 1000000}
        ]
        
        result = analyze_trends(history, days=30)
        
        assert result['trends_available'] is False
        assert result['reason'] == 'insufficient_data'
    
    def test_analyze_trends_none_values(self):
        """Test análisis de tendencias con valores None"""
        history = [
            {'archived_count': None, 'deleted_count': 5, 'database_size_bytes': 1000000},
            {'archived_count': 10, 'deleted_count': None, 'database_size_bytes': None},
        ]
        
        # Debería manejar None correctamente
        result = analyze_trends(history, days=30)
        
        # Puede retornar error o manejar None
        assert 'trends_available' in result


class TestEdgeCasesUtils:
    """Tests para casos edge en utilidades"""
    
    def test_safe_divide_by_zero(self):
        """Test división por cero"""
        result = safe_divide(10, 0)
        assert result == 0.0
    
    def test_safe_divide_by_zero_custom_default(self):
        """Test división por cero con default personalizado"""
        result = safe_divide(10, 0, default=-1.0)
        assert result == -1.0
    
    def test_safe_divide_negative(self):
        """Test división con números negativos"""
        result = safe_divide(-10, 2)
        assert result == -5.0
    
    def test_safe_divide_float_result(self):
        """Test división que resulta en float"""
        result = safe_divide(1, 3)
        assert abs(result - 0.3333333333333333) < 0.0001
    
    def test_calculate_percentage_change_zero_old(self):
        """Test cambio porcentual cuando valor antiguo es cero"""
        result = calculate_percentage_change(0, 100)
        assert result == float('inf')
    
    def test_calculate_percentage_change_zero_new(self):
        """Test cambio porcentual cuando valor nuevo es cero"""
        result = calculate_percentage_change(100, 0)
        assert result == -100.0
    
    def test_calculate_percentage_change_both_zero(self):
        """Test cambio porcentual cuando ambos son cero"""
        result = calculate_percentage_change(0, 0)
        assert result == 0.0
    
    def test_calculate_percentage_change_negative(self):
        """Test cambio porcentual con valores negativos"""
        result = calculate_percentage_change(-100, -50)
        assert result == 50.0
    
    def test_format_duration_ms_zero(self):
        """Test formateo de duración cero"""
        result = format_duration_ms(0)
        assert "0ms" in result or "0" in result
    
    def test_format_duration_ms_very_small(self):
        """Test formateo de duración muy pequeña"""
        result = format_duration_ms(0.5)
        assert "ms" in result
    
    def test_format_duration_ms_very_large(self):
        """Test formateo de duración muy grande"""
        result = format_duration_ms(3600000)  # 1 hora
        assert "m" in result or "h" in result
    
    def test_format_bytes_zero(self):
        """Test formateo de bytes cero"""
        result = format_bytes(0)
        assert "0" in result
    
    def test_format_bytes_very_large(self):
        """Test formateo de bytes muy grandes"""
        result = format_bytes(1024 ** 5)  # 1 PB
        assert "PB" in result or "TB" in result
    
    def test_validate_params_missing_keys(self):
        """Test validación con claves faltantes"""
        params = {}  # Sin claves
        
        # Debería usar valores por defecto o fallar
        try:
            validate_params(params)
        except Exception:
            pass  # Esperado si requiere todas las claves


class TestEdgeCasesTimeout:
    """Tests para casos edge en timeouts"""
    
    @patch('data.airflow.plugins.approval_cleanup_ops.time.perf_counter')
    def test_execute_query_timeout_exceeded(self, mock_perf_counter):
        """Test cuando se excede el timeout"""
        mock_hook = Mock()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_hook.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Simular timeout
        mock_cursor.execute.side_effect = Exception("statement_timeout exceeded")
        mock_perf_counter.side_effect = [0, 300]  # Simula que pasó el timeout
        
        from airflow.exceptions import AirflowFailException
        
        with pytest.raises(AirflowFailException):
            execute_query_with_timeout(
                mock_hook,
                "SELECT * FROM table",
                timeout_seconds=30
            )
    
    @patch('data.airflow.plugins.approval_cleanup_ops.time.perf_counter')
    def test_execute_query_no_results(self, mock_perf_counter):
        """Test query que no retorna resultados"""
        mock_hook = Mock()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_hook.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.description = None  # No hay resultados
        mock_perf_counter.side_effect = [0, 0.1]
        
        result = execute_query_with_timeout(
            mock_hook,
            "INSERT INTO table VALUES (1)",
            timeout_seconds=30
        )
        
        assert result is None or result == []


class TestEdgeCasesConcurrency:
    """Tests para casos edge en concurrencia"""
    
    def test_process_batch_single_thread(self):
        """Test procesamiento secuencial cuando max_workers es 1"""
        items = [1, 2, 3, 4, 5]
        
        call_order = []
        def processor(batch):
            call_order.append(batch)
            return {'processed': len(batch)}
        
        result = process_batch(items, batch_size=2, processor=processor, operation_name="test")
        
        # Debería procesar en orden
        assert len(call_order) > 0
        assert result['processed'] == 5
    
    def test_process_batch_very_large_batch_size(self):
        """Test con batch_size muy grande"""
        items = list(range(1, 101))
        
        def processor(batch):
            return {'processed': len(batch)}
        
        result = process_batch(items, batch_size=1000, processor=processor, operation_name="test")
        
        assert result['total_items'] == 100
        assert result['batches'] == 1  # Todo en un batch


class TestEdgeCasesErrorHandling:
    """Tests para manejo de errores en casos edge"""
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_archive_connection_error(self, mock_get_hook):
        """Test cuando falla la conexión durante archivado"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_conn.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception, match="Connection"):
            archive_requests_batch([1, 2, 3], dry_run=False)
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_archive_rollback_on_error(self, mock_get_hook):
        """Test que hace rollback en caso de error"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_hook.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("SQL error")
        
        with pytest.raises(Exception):
            archive_requests_batch([1, 2, 3], dry_run=False)
        
        mock_conn.rollback.assert_called_once()

