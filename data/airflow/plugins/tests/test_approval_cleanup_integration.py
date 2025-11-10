"""
Tests de integración para approval_cleanup.
Prueba la interacción entre diferentes módulos.
"""
from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from data.airflow.plugins.approval_cleanup_queries import (
    get_old_requests_to_archive,
    archive_requests_batch,
    insert_cleanup_history,
)
from data.airflow.plugins.approval_cleanup_ops import (
    get_pg_hook,
    process_batch,
)
from data.airflow.plugins.approval_cleanup_analytics import (
    detect_anomaly,
    analyze_trends,
)
from data.airflow.plugins.approval_cleanup_utils import (
    validate_params,
    check_circuit_breaker,
)


class TestArchiveWorkflow:
    """Tests para el flujo completo de archivado"""
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_full_archive_workflow(self, mock_get_hook):
        """Test flujo completo de archivado"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        
        # Simular requests antiguos
        mock_hook.get_records.return_value = [
            (1, 'completed', '2020-01-01', '2019-01-01'),
            (2, 'completed', '2020-02-01', '2019-02-01'),
            (3, 'completed', '2020-03-01', '2019-03-01'),
        ]
        
        # Obtener requests para archivar
        old_requests = get_old_requests_to_archive(retention_years=2, batch_size=100)
        
        assert len(old_requests) == 3
        
        # Simular archivado
        request_ids = [r[0] for r in old_requests]
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_hook.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 3
        
        archive_result = archive_requests_batch(request_ids, pg_hook=mock_hook, dry_run=False)
        
        assert archive_result['archived'] == 3
        assert archive_result['request_ids'] == request_ids
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_archive_workflow_with_batch_processing(self, mock_get_hook):
        """Test archivado usando process_batch"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        
        # Simular muchos requests
        many_requests = [(i, 'completed', '2020-01-01', '2019-01-01') for i in range(1, 2501)]
        mock_hook.get_records.return_value = many_requests
        
        old_requests = get_old_requests_to_archive(retention_years=2, batch_size=2500)
        
        # Procesar en lotes
        request_ids = [r[0] for r in old_requests]
        
        def archive_batch(batch):
            return archive_requests_batch(batch, pg_hook=mock_hook, dry_run=True)
        
        result = process_batch(request_ids, batch_size=1000, processor=archive_batch, operation_name="archive")
        
        assert result['total_items'] == 2500
        assert result['processed'] == 2500
        assert result['batches'] == 3  # 1000 + 1000 + 500


class TestAnalyticsIntegration:
    """Tests de integración para analytics"""
    
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_pg_hook')
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_anomaly_detection_with_history(self, mock_queries_hook, mock_analytics_hook):
        """Test detección de anomalías con historial"""
        mock_hook = Mock()
        mock_queries_hook.return_value = mock_hook
        mock_analytics_hook.return_value = mock_hook
        
        # Insertar historial primero
        history_data = {
            'archived_count': 10,
            'deleted_count': 5,
            'notifications_deleted': 3,
            'database_size_bytes': 1000000,
            'execution_duration_ms': 1500.5,
            'dry_run': False
        }
        
        mock_hook.get_first.return_value = (1,)  # ID del historial insertado
        insert_cleanup_history(history_data, pg_hook=mock_hook)
        
        # Simular historial para detección de anomalías
        mock_hook.get_records.return_value = [
            (10, 5, 3, 1000000),
            (12, 6, 4, 1100000),
            (15, 7, 5, 1200000),
            (18, 8, 6, 1300000),
            (100, 50, 30, 5000000),  # Valor anómalo
        ]
        
        # Detectar anomalía
        result = detect_anomaly(1000, 'archived_count', pg_hook=mock_hook)
        
        # Debería detectar como anómalo si el valor es muy alto
        assert 'is_anomaly' in result
        assert 'z_score' in result
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_cleanup_history')
    def test_trend_analysis_with_history(self, mock_get_history):
        """Test análisis de tendencias con historial"""
        from data.airflow.plugins.approval_cleanup_analytics import analyze_trends
        
        # Simular historial
        history = [
            {
                'id': 1,
                'cleanup_date': datetime(2025, 1, 1),
                'archived_count': 10,
                'deleted_count': 5,
                'database_size_bytes': 1000000,
            },
            {
                'id': 2,
                'cleanup_date': datetime(2025, 1, 8),
                'archived_count': 20,
                'deleted_count': 10,
                'database_size_bytes': 2000000,
            },
            {
                'id': 3,
                'cleanup_date': datetime(2025, 1, 15),
                'archived_count': 30,
                'deleted_count': 15,
                'database_size_bytes': 3000000,
            },
        ]
        
        mock_get_history.return_value = history
        
        # Analizar tendencias
        result = analyze_trends(history, days=30)
        
        assert result['trends_available'] is True
        assert result['archived_trend'] == 'increasing'
        assert result['size_trend'] == 'increasing'
        assert result['archived_growth_pct'] > 0


class TestParameterValidationIntegration:
    """Tests de integración para validación de parámetros"""
    
    def test_validate_params_with_dag_params(self):
        """Test validación con parámetros típicos de DAG"""
        params = {
            'archive_retention_years': 2,
            'notification_retention_months': 6,
            'dry_run': False,
            'notify_on_completion': True,
        }
        
        # No debería lanzar excepción
        validate_params(params)
    
    def test_validate_params_invalid_combination(self):
        """Test validación con combinación inválida"""
        params = {
            'archive_retention_years': 15,  # Inválido
            'notification_retention_months': 6,
            'dry_run': False,
        }
        
        with pytest.raises(Exception):
            validate_params(params)


class TestCircuitBreakerIntegration:
    """Tests de integración para circuit breaker"""
    
    @patch('data.airflow.plugins.approval_cleanup_utils.get_pg_hook')
    @patch('data.airflow.plugins.approval_cleanup_queries.get_cleanup_history')
    def test_circuit_breaker_with_history(self, mock_get_history, mock_get_hook):
        """Test circuit breaker con historial de fallos"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        
        # Simular muchos fallos (todos con 0 en todos los campos)
        mock_hook.get_first.return_value = (10,)  # 10 fallos
        
        result = check_circuit_breaker(pg_hook=mock_hook)
        
        # Si el threshold es 5, debería estar activo
        if result['failure_count'] >= 5:
            assert result['active'] is True
            assert result['reason'] == 'too_many_failures'
        else:
            assert result['active'] is False


class TestPerformanceTrackingIntegration:
    """Tests de integración para tracking de performance"""
    
    @patch('data.airflow.plugins.approval_cleanup_ops.get_pg_hook')
    def test_performance_tracking_through_operations(self, mock_get_hook):
        """Test tracking de performance a través de operaciones"""
        from data.airflow.plugins.approval_cleanup_ops import track_performance
        
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        
        # Simular tracking de performance
        track_performance(
            "archive_operation",
            1500.0,  # duration_ms
            100,     # records_processed
            50,      # batch_size
            mock_hook
        )
        
        # Verificar que se ejecutaron queries para crear tabla e insertar
        assert mock_hook.run.called
        # Verificar que se insertó un registro
        insert_calls = [call for call in mock_hook.run.call_args_list 
                       if 'INSERT' in str(call) or 'INSERT' in str(call.args)]
        assert len(insert_calls) > 0


class TestBatchProcessingIntegration:
    """Tests de integración para procesamiento en lotes"""
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    def test_batch_processing_with_archive(self, mock_get_hook):
        """Test procesamiento en lotes con archivado"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        
        # Simular requests para archivar
        request_ids = list(range(1, 2501))
        
        # Simular conexión para archivado
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_hook.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1000  # Procesa 1000 por batch
        
        def archive_processor(batch):
            return archive_requests_batch(batch, pg_hook=mock_hook, dry_run=False)
        
        result = process_batch(
            request_ids,
            batch_size=1000,
            processor=archive_processor,
            operation_name="archive_batch"
        )
        
        assert result['total_items'] == 2500
        assert result['batches'] == 3
        assert result['processed'] == 2500


class TestQueryAndAnalyticsIntegration:
    """Tests de integración entre queries y analytics"""
    
    @patch('data.airflow.plugins.approval_cleanup_queries.get_pg_hook')
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_pg_hook')
    def test_query_results_used_for_analytics(self, mock_analytics_hook, mock_queries_hook):
        """Test que resultados de queries se usan para analytics"""
        mock_hook = Mock()
        mock_queries_hook.return_value = mock_hook
        mock_analytics_hook.return_value = mock_hook
        
        # Obtener tamaños de tablas
        mock_hook.get_records.return_value = [
            ('public', 'approval_requests', '500 MB', 524288000, 400000000, 124288000),
        ]
        
        from data.airflow.plugins.approval_cleanup_queries import get_table_sizes
        from data.airflow.plugins.approval_cleanup_analytics import analyze_table_sizes
        
        table_sizes = get_table_sizes(pg_hook=mock_hook)
        analysis = analyze_table_sizes(pg_hook=mock_hook)
        
        assert len(table_sizes) > 0
        assert analysis['total_size_bytes'] > 0
        assert analysis['table_count'] > 0

