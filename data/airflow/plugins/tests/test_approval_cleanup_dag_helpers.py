"""
Tests para funciones auxiliares del DAG approval_cleanup.py
"""
from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, MagicMock
from time import perf_counter

# Importar funciones del DAG (necesitaremos mockearlas o extraerlas)
# Por ahora, testaremos las funciones que están en los plugins pero que se usan en el DAG


class TestOptimizeBatchSize:
    """Tests para _optimize_batch_size del DAG"""
    
    def test_optimize_batch_size_adaptive_disabled(self):
        """Test cuando adaptive está deshabilitado"""
        import os
        with patch.dict(os.environ, {'APPROVAL_CLEANUP_BATCH_ADAPTIVE': 'false'}):
            import importlib
            import data.airflow.dags.approval_cleanup as dag_module
            importlib.reload(dag_module)
            
            # Si BATCH_SIZE_ADAPTIVE está deshabilitado, debería retornar el tamaño actual
            from data.airflow.dags.approval_cleanup import BATCH_SIZE_ADAPTIVE, _optimize_batch_size
            
            if not BATCH_SIZE_ADAPTIVE:
                result = _optimize_batch_size(1000, True, 10.0)
                assert result == 1000
    
    def test_optimize_batch_size_failure_reduces(self):
        """Test que reduce tamaño cuando falla"""
        import data.airflow.dags.approval_cleanup as dag_module
        from data.airflow.dags.approval_cleanup import _optimize_batch_size, BATCH_SIZE_MIN
        
        result = _optimize_batch_size(1000, False, 10.0)  # last_success=False
        
        # Debería reducir a 70% del tamaño actual
        assert result < 1000
        assert result >= BATCH_SIZE_MIN
    
    def test_optimize_batch_size_slow_reduces(self):
        """Test que reduce tamaño cuando es muy lento"""
        from data.airflow.dags.approval_cleanup import _optimize_batch_size, BATCH_SIZE_MIN
        
        # target_duration=30, last_duration=60 (> 1.5 * 30)
        result = _optimize_batch_size(1000, True, 60.0, target_duration=30.0)
        
        assert result < 1000
        assert result >= BATCH_SIZE_MIN
    
    def test_optimize_batch_size_fast_increases(self):
        """Test que aumenta tamaño cuando es muy rápido"""
        from data.airflow.dags.approval_cleanup import _optimize_batch_size, BATCH_SIZE_MAX
        
        # target_duration=30, last_duration=10 (< 0.5 * 30)
        result = _optimize_batch_size(1000, True, 10.0, target_duration=30.0)
        
        assert result > 1000
        assert result <= BATCH_SIZE_MAX
    
    def test_optimize_batch_size_stable_unchanged(self):
        """Test que mantiene tamaño cuando está en rango normal"""
        from data.airflow.dags.approval_cleanup import _optimize_batch_size
        
        # target_duration=30, last_duration=25 (entre 0.5 y 1.5 * 30)
        result = _optimize_batch_size(1000, True, 25.0, target_duration=30.0)
        
        assert result == 1000


class TestQueryStats:
    """Tests para _get_query_stats y _update_query_stats"""
    
    def test_get_query_stats_empty(self):
        """Test obtener stats de query sin historial"""
        from data.airflow.dags.approval_cleanup import _get_query_stats
        
        stats = _get_query_stats("new_query")
        
        assert stats['count'] == 0
        assert stats['total_time'] == 0.0
        assert stats['avg_time'] == 0.0
        assert stats['errors'] == 0
    
    def test_update_query_stats_success(self):
        """Test actualizar stats con ejecución exitosa"""
        from data.airflow.dags.approval_cleanup import _update_query_stats, _get_query_stats
        
        query_key = "test_query"
        
        # Actualizar con éxito
        _update_query_stats(query_key, 1.5, success=True)
        _update_query_stats(query_key, 2.0, success=True)
        
        stats = _get_query_stats(query_key)
        
        assert stats['count'] == 2
        assert stats['total_time'] == 3.5
        assert stats['avg_time'] == 1.75
        assert stats['min_time'] == 1.5
        assert stats['max_time'] == 2.0
        assert stats['errors'] == 0
    
    def test_update_query_stats_with_errors(self):
        """Test actualizar stats con errores"""
        from data.airflow.dags.approval_cleanup import _update_query_stats, _get_query_stats
        
        query_key = "error_query"
        
        _update_query_stats(query_key, 1.0, success=True)
        _update_query_stats(query_key, 0.5, success=False)
        _update_query_stats(query_key, 2.0, success=True)
        
        stats = _get_query_stats(query_key)
        
        assert stats['count'] == 3
        assert stats['errors'] == 1
        assert stats['total_time'] == 3.0  # Solo suma los exitosos
        assert stats['avg_time'] == 1.5  # Promedio de exitosos


class TestCachedQuery:
    """Tests para _cached_query (función del DAG)"""
    
    @patch('data.airflow.dags.approval_cleanup.CACHE_ENABLED', True)
    @patch('data.airflow.dags.approval_cleanup.perf_counter')
    def test_cached_query_cache_hit(self, mock_perf_counter):
        """Test que retorna resultado desde cache"""
        from data.airflow.dags.approval_cleanup import _cached_query
        
        # Simular tiempo
        mock_perf_counter.side_effect = [0, 1, 1.5]  # start, cache check, second check
        
        call_count = [0]
        def expensive_query():
            call_count[0] += 1
            return {"result": "data"}
        
        # Primera llamada - cache miss
        result1 = _cached_query("test_key", expensive_query, ttl_seconds=10)
        
        # Segunda llamada - cache hit
        result2 = _cached_query("test_key", expensive_query, ttl_seconds=10)
        
        assert result1 == result2
        assert call_count[0] == 1  # Solo se ejecutó una vez
    
    @patch('data.airflow.dags.approval_cleanup.CACHE_ENABLED', True)
    @patch('data.airflow.dags.approval_cleanup.perf_counter')
    def test_cached_query_cache_expired(self, mock_perf_counter):
        """Test que ejecuta query cuando cache expiró"""
        from data.airflow.dags.approval_cleanup import _cached_query
        
        # Simular tiempo: cache expira
        mock_perf_counter.side_effect = [0, 0, 15]  # start, cache check (expired), second check
        
        call_count = [0]
        def expensive_query():
            call_count[0] += 1
            return {"result": f"data_{call_count[0]}"}
        
        # Primera llamada
        result1 = _cached_query("test_key", expensive_query, ttl_seconds=10)
        
        # Segunda llamada después de expirar
        result2 = _cached_query("test_key", expensive_query, ttl_seconds=10)
        
        assert call_count[0] == 2  # Se ejecutó dos veces
        assert result1["result"] != result2["result"]
    
    @patch('data.airflow.dags.approval_cleanup.CACHE_ENABLED', False)
    def test_cached_query_cache_disabled(self):
        """Test que ejecuta query cuando cache está deshabilitado"""
        from data.airflow.dags.approval_cleanup import _cached_query
        
        call_count = [0]
        def expensive_query():
            call_count[0] += 1
            return {"result": "data"}
        
        # Ambas llamadas deberían ejecutar la query
        _cached_query("test_key", expensive_query)
        _cached_query("test_key", expensive_query)
        
        assert call_count[0] == 2


class TestDetectDeadlockRetry:
    """Tests para _detect_deadlock_retry del DAG"""
    
    @patch('time.sleep')
    def test_detect_deadlock_retry_success(self, mock_sleep):
        """Test retry exitoso después de deadlock"""
        from data.airflow.dags.approval_cleanup import _detect_deadlock_retry
        
        call_count = [0]
        def operation():
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("deadlock detected")
            return "success"
        
        result = _detect_deadlock_retry(operation, max_retries=3)
        
        assert result == "success"
        assert call_count[0] == 2
        assert mock_sleep.called
    
    @patch('time.sleep')
    def test_detect_deadlock_retry_exhausted(self, mock_sleep):
        """Test que falla después de agotar reintentos"""
        from data.airflow.dags.approval_cleanup import _detect_deadlock_retry
        
        def operation():
            raise Exception("deadlock detected")
        
        with pytest.raises(Exception, match="deadlock"):
            _detect_deadlock_retry(operation, max_retries=3)
        
        assert mock_sleep.call_count == 2  # 2 reintentos antes de fallar
    
    @patch('time.sleep')
    def test_detect_deadlock_retry_non_deadlock_error(self, mock_sleep):
        """Test que no reintenta errores que no son deadlocks"""
        from data.airflow.dags.approval_cleanup import _detect_deadlock_retry
        
        def operation():
            raise Exception("connection error")
        
        with pytest.raises(Exception, match="connection error"):
            _detect_deadlock_retry(operation, max_retries=3)
        
        assert not mock_sleep.called  # No debería reintentar


class TestCalculatePercentiles:
    """Tests para _calculate_percentiles del DAG"""
    
    def test_calculate_percentiles_empty(self):
        """Test con lista vacía"""
        from data.airflow.dags.approval_cleanup import _calculate_percentiles
        
        result = _calculate_percentiles([])
        
        assert result['p50'] == 0
        assert result['p95'] == 0
        assert result['p99'] == 0
    
    def test_calculate_percentiles_multiple_values(self):
        """Test con múltiples valores"""
        from data.airflow.dags.approval_cleanup import _calculate_percentiles
        
        values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        result = _calculate_percentiles(values)
        
        assert result['min'] == 10
        assert result['max'] == 100
        assert result['avg'] == 55.0
        assert result['p50'] > 0
        assert result['p95'] > result['p50']
        assert result['p99'] >= result['p95']


class TestExportToMultipleFormats:
    """Tests para _export_to_multiple_formats del DAG"""
    
    @patch('data.airflow.dags.approval_cleanup.Path')
    @patch('builtins.open', create=True)
    def test_export_to_json(self, mock_open, mock_path):
        """Test exportación a JSON"""
        from data.airflow.dags.approval_cleanup import _export_to_multiple_formats
        from pathlib import Path
        import json
        
        mock_path_instance = Mock()
        mock_path_instance.__truediv__ = lambda self, other: mock_path_instance
        mock_path.return_value = mock_path_instance
        mock_path_instance.mkdir.return_value = None
        
        data = {"key": "value", "number": 123}
        result = _export_to_multiple_formats(
            data,
            "test_report",
            Path("/tmp/reports"),
            formats=['json']
        )
        
        assert 'json' in result
        assert mock_path_instance.mkdir.called
    
    @patch('data.airflow.dags.approval_cleanup.Path')
    @patch('builtins.open', create=True)
    def test_export_to_csv(self, mock_open, mock_path):
        """Test exportación a CSV"""
        from data.airflow.dags.approval_cleanup import _export_to_multiple_formats
        from pathlib import Path
        import csv
        
        mock_path_instance = Mock()
        mock_path_instance.__truediv__ = lambda self, other: mock_path_instance
        mock_path.return_value = mock_path_instance
        mock_path_instance.mkdir.return_value = None
        
        # Data con lista de dicts para CSV
        data = {
            "records": [
                {"id": 1, "name": "Test"},
                {"id": 2, "name": "Test2"},
            ]
        }
        
        result = _export_to_multiple_formats(
            data,
            "test_report",
            Path("/tmp/reports"),
            formats=['csv']
        )
        
        # CSV debería estar en el resultado si hay datos tabulares
        assert isinstance(result, dict)

