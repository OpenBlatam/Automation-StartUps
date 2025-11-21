"""
Tests para approval_cleanup_analytics.py
"""
from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, MagicMock
from airflow.providers.postgres.hooks.postgres import PostgresHook

from data.airflow.plugins.approval_cleanup_analytics import (
    calculate_percentiles,
    detect_anomaly,
    analyze_query_performance,
    predict_capacity_need,
    analyze_table_sizes,
    analyze_trends,
)


class TestCalculatePercentiles:
    """Tests para calculate_percentiles"""
    
    def test_calculate_percentiles_empty_list(self):
        """Test con lista vacía"""
        result = calculate_percentiles([])
        
        assert result['p50'] == 0
        assert result['p95'] == 0
        assert result['p99'] == 0
        assert result['min'] == 0
        assert result['max'] == 0
        assert result['avg'] == 0
    
    def test_calculate_percentiles_single_value(self):
        """Test con un solo valor"""
        result = calculate_percentiles([100])
        
        assert result['p50'] == 100
        assert result['p95'] == 100
        assert result['p99'] == 100
        assert result['min'] == 100
        assert result['max'] == 100
        assert result['avg'] == 100
    
    def test_calculate_percentiles_multiple_values(self):
        """Test con múltiples valores"""
        values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        result = calculate_percentiles(values)
        
        assert result['min'] == 10
        assert result['max'] == 100
        assert result['avg'] == 55.0
        assert result['p50'] == 50 or result['p50'] == 60  # Mediana
        assert result['p95'] >= 90
        assert result['p99'] >= 90
    
    def test_calculate_percentiles_unsorted(self):
        """Test que funciona con valores no ordenados"""
        values = [100, 10, 50, 30, 90, 20, 80, 40, 70, 60]
        result = calculate_percentiles(values)
        
        assert result['min'] == 10
        assert result['max'] == 100
        assert result['avg'] == 55.0


class TestDetectAnomaly:
    """Tests para detect_anomaly"""
    
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_pg_hook')
    def test_detect_anomaly_insufficient_history(self, mock_get_hook):
        """Test cuando no hay suficiente historial"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_records.side_effect = Exception("No table")
        
        result = detect_anomaly(1000, 'archived_count')
        
        assert result['is_anomaly'] is False
        assert result['reason'] == 'insufficient_history'
    
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_pg_hook')
    def test_detect_anomaly_insufficient_data(self, mock_get_hook):
        """Test cuando hay pocos datos"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_records.return_value = [
            (10, 5, 3, 1000000),
            (15, 7, 4, 1100000),
        ]  # Solo 2 registros
        
        result = detect_anomaly(1000, 'archived_count')
        
        assert result['is_anomaly'] is False
        assert result['reason'] == 'insufficient_data'
    
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_pg_hook')
    def test_detect_anomaly_normal_value(self, mock_get_hook):
        """Test con valor normal (no anómalo)"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        # Historial con valores alrededor de 100
        mock_hook.get_records.return_value = [
            (90, 5, 3, 1000000),
            (100, 7, 4, 1100000),
            (110, 6, 5, 1200000),
            (95, 8, 3, 1050000),
            (105, 9, 4, 1150000),
        ]
        
        result = detect_anomaly(100, 'archived_count')
        
        # Valor 100 está dentro del rango normal
        assert result['is_anomaly'] is False
        assert 'z_score' in result
        assert 'mean' in result
    
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_pg_hook')
    def test_detect_anomaly_anomalous_value(self, mock_get_hook):
        """Test con valor anómalo (muy alto)"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        # Historial con valores alrededor de 100
        mock_hook.get_records.return_value = [
            (90, 5, 3, 1000000),
            (100, 7, 4, 1100000),
            (110, 6, 5, 1200000),
            (95, 8, 3, 1050000),
            (105, 9, 4, 1150000),
        ]
        
        # Valor muy alto (1000 cuando promedio es ~100)
        result = detect_anomaly(1000, 'archived_count')
        
        # Debería detectar como anómalo
        assert result['is_anomaly'] is True
        assert result['z_score'] > 2.5  # Threshold por defecto
    
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_pg_hook')
    def test_detect_anomaly_unknown_metric(self, mock_get_hook):
        """Test con métrica desconocida"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_records.return_value = [
            (90, 5, 3, 1000000),
        ]
        
        result = detect_anomaly(100, 'unknown_metric')
        
        assert result['is_anomaly'] is False
        assert result['reason'] == 'unknown_metric'
    
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_pg_hook')
    def test_detect_anomaly_error_handling(self, mock_get_hook):
        """Test manejo de errores"""
        mock_get_hook.side_effect = Exception("Connection error")
        
        result = detect_anomaly(100, 'archived_count')
        
        assert result['is_anomaly'] is False
        assert result['reason'] == 'error'
        assert 'error' in result


class TestAnalyzeQueryPerformance:
    """Tests para analyze_query_performance"""
    
    def test_analyze_query_performance_success(self):
        """Test análisis exitoso de query"""
        mock_hook = Mock()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_hook.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Simular resultado de EXPLAIN ANALYZE
        import json
        explain_result = [[{
            'Execution Time': 150.5,
            'Planning Time': 10.2,
            'Plan': {'Node Type': 'Seq Scan'}
        }]]
        mock_cursor.fetchone.return_value = (json.dumps(explain_result),)
        
        result = analyze_query_performance(mock_hook, "SELECT * FROM table")
        
        assert result['execution_time_ms'] == 150.5
        assert result['planning_time_ms'] == 10.2
        assert result['total_time_ms'] == 160.7
        assert 'plan' in result
    
    def test_analyze_query_performance_with_parameters(self):
        """Test análisis con parámetros"""
        mock_hook = Mock()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_hook.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        import json
        explain_result = [[{'Execution Time': 50.0, 'Planning Time': 5.0}]]
        mock_cursor.fetchone.return_value = (json.dumps(explain_result),)
        
        result = analyze_query_performance(
            mock_hook,
            "SELECT * FROM table WHERE id = %s",
            parameters=(1,)
        )
        
        assert result['execution_time_ms'] == 50.0
        # Verificar que se pasaron parámetros
        assert mock_cursor.execute.called
    
    def test_analyze_query_performance_error(self):
        """Test manejo de errores"""
        mock_hook = Mock()
        mock_hook.get_conn.side_effect = Exception("Connection failed")
        
        result = analyze_query_performance(mock_hook, "SELECT * FROM table")
        
        assert 'error' in result
        assert 'Connection failed' in result['error']


class TestPredictCapacityNeed:
    """Tests para predict_capacity_need"""
    
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_pg_hook')
    def test_predict_capacity_need_insufficient_history(self, mock_get_hook):
        """Test cuando no hay suficiente historial"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_records.side_effect = Exception("No table")
        
        result = predict_capacity_need(days_ahead=30)
        
        assert result['prediction_available'] is False
        assert result['reason'] == 'insufficient_history'
    
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_pg_hook')
    def test_predict_capacity_need_insufficient_data_points(self, mock_get_hook):
        """Test cuando hay pocos puntos de datos"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_records.return_value = [
            (None, 1000000, 10, 5, 20, 50),
            (None, 1100000, 12, 6, 25, 55),
        ]  # Solo 2 puntos
        
        result = predict_capacity_need(days_ahead=30)
        
        assert result['prediction_available'] is False
        assert result['reason'] == 'insufficient_data_points'
    
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_pg_hook')
    def test_predict_capacity_need_success(self, mock_get_hook):
        """Test predicción exitosa"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        from datetime import datetime, timedelta
        base_date = datetime(2025, 1, 1)
        
        # Simular crecimiento histórico
        history = []
        for i in range(10):
            date = base_date + timedelta(days=i)
            size_bytes = 1000000 * (1 + i * 0.1)  # Crecimiento del 10% por día
            history.append((
                date,
                size_bytes,
                10 + i,
                5 + i,
                20 + i,
                50 + i
            ))
        
        mock_hook.get_records.return_value = history
        
        result = predict_capacity_need(days_ahead=30)
        
        assert result['prediction_available'] is True
        assert 'current_size_bytes' in result
        assert 'predicted_size_bytes' in result
        assert 'avg_growth_rate' in result
        assert result['days_ahead'] == 30
    
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_pg_hook')
    def test_predict_capacity_need_no_growth(self, mock_get_hook):
        """Test cuando no hay crecimiento"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        from datetime import datetime
        base_date = datetime(2025, 1, 1)
        
        # Tamaño constante
        history = [
            (base_date, 1000000, 10, 5, 20, 50),
            (base_date, 1000000, 10, 5, 20, 50),
        ]
        
        mock_hook.get_records.return_value = history
        
        result = predict_capacity_need(days_ahead=30)
        
        # Debería funcionar pero con crecimiento 0
        if result['prediction_available']:
            assert result['avg_growth_rate'] <= 0


class TestAnalyzeTableSizes:
    """Tests para analyze_table_sizes"""
    
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_table_sizes')
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_pg_hook')
    def test_analyze_table_sizes_success(self, mock_get_hook, mock_get_table_sizes):
        """Test análisis exitoso de tamaños de tablas"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        
        mock_get_table_sizes.return_value = [
            {
                'table': 'approval_requests',
                'total_bytes': 524288000,
                'table_bytes': 400000000,
                'indexes_bytes': 124288000
            },
            {
                'table': 'approval_notifications',
                'total_bytes': 104857600,
                'table_bytes': 80000000,
                'indexes_bytes': 24857600
            },
        ]
        
        result = analyze_table_sizes(pg_hook=mock_hook)
        
        assert result['total_size_bytes'] == 629145600
        assert result['table_count'] == 2
        assert result['largest_table']['table'] == 'approval_requests'
        assert result['total_size_gb'] > 0
    
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_table_sizes')
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_pg_hook')
    def test_analyze_table_sizes_empty(self, mock_get_hook, mock_get_table_sizes):
        """Test cuando no hay tablas"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_get_table_sizes.return_value = []
        
        result = analyze_table_sizes(pg_hook=mock_hook)
        
        assert result['total_size_bytes'] == 0
        assert result['table_count'] == 0
        assert result['largest_table'] is None
    
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_table_sizes')
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_pg_hook')
    def test_analyze_table_sizes_error(self, mock_get_hook, mock_get_table_sizes):
        """Test manejo de errores"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_get_table_sizes.side_effect = Exception("Query failed")
        
        result = analyze_table_sizes(pg_hook=mock_hook)
        
        assert 'error' in result
        assert result['total_size_bytes'] == 0


class TestAnalyzeTrends:
    """Tests para analyze_trends"""
    
    def test_analyze_trends_insufficient_data(self):
        """Test cuando no hay suficiente data"""
        result = analyze_trends([])
        
        assert result['trends_available'] is False
        assert result['reason'] == 'insufficient_data'
    
    def test_analyze_trends_increasing(self):
        """Test tendencia creciente"""
        history_data = [
            {'archived_count': 10, 'deleted_count': 5, 'database_size_bytes': 1000000},
            {'archived_count': 20, 'deleted_count': 10, 'database_size_bytes': 2000000},
            {'archived_count': 30, 'deleted_count': 15, 'database_size_bytes': 3000000},
        ]
        
        result = analyze_trends(history_data, days=30)
        
        assert result['trends_available'] is True
        assert result['archived_trend'] == 'increasing'
        assert result['deleted_trend'] == 'increasing'
        assert result['size_trend'] == 'increasing'
        assert result['archived_growth_pct'] > 0
    
    def test_analyze_trends_decreasing(self):
        """Test tendencia decreciente"""
        history_data = [
            {'archived_count': 30, 'deleted_count': 15, 'database_size_bytes': 3000000},
            {'archived_count': 20, 'deleted_count': 10, 'database_size_bytes': 2000000},
            {'archived_count': 10, 'deleted_count': 5, 'database_size_bytes': 1000000},
        ]
        
        result = analyze_trends(history_data, days=30)
        
        assert result['trends_available'] is True
        assert result['archived_trend'] == 'decreasing'
        assert result['deleted_trend'] == 'decreasing'
        assert result['size_trend'] == 'decreasing'
        assert result['archived_growth_pct'] < 0
    
    def test_analyze_trends_stable(self):
        """Test tendencia estable"""
        history_data = [
            {'archived_count': 10, 'deleted_count': 5, 'database_size_bytes': 1000000},
            {'archived_count': 10, 'deleted_count': 5, 'database_size_bytes': 1000000},
            {'archived_count': 10, 'deleted_count': 5, 'database_size_bytes': 1000000},
        ]
        
        result = analyze_trends(history_data, days=30)
        
        assert result['trends_available'] is True
        assert result['archived_trend'] == 'stable'
        assert result['deleted_trend'] == 'stable'
        assert result['size_trend'] == 'stable'
        assert result['archived_growth_pct'] == 0
    
    def test_analyze_trends_mixed(self):
        """Test tendencias mixtas"""
        history_data = [
            {'archived_count': 10, 'deleted_count': 5, 'database_size_bytes': 1000000},
            {'archived_count': 20, 'deleted_count': 3, 'database_size_bytes': 2000000},
            {'archived_count': 15, 'deleted_count': 7, 'database_size_bytes': 1500000},
        ]
        
        result = analyze_trends(history_data, days=30)
        
        assert result['trends_available'] is True
        assert 'archived_trend' in result
        assert 'avg_archived_per_run' in result
        assert result['data_points'] == 3
    
    def test_analyze_trends_error_handling(self):
        """Test manejo de errores"""
        # Datos con valores None que pueden causar errores
        history_data = [
            {'archived_count': None, 'deleted_count': 5, 'database_size_bytes': 1000000},
        ]
        
        result = analyze_trends(history_data, days=30)
        
        # Debería manejar el error o retornar información útil
        assert 'trends_available' in result

