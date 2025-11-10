"""
Tests para approval_cleanup_utils.py
"""
from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, MagicMock
from airflow.exceptions import AirflowFailException

from data.airflow.plugins.approval_cleanup_utils import (
    log_with_context,
    check_circuit_breaker,
    validate_params,
    format_duration_ms,
    format_bytes,
    safe_divide,
    calculate_percentage_change,
)


class TestLogWithContext:
    """Tests para log_with_context"""
    
    @patch('data.airflow.plugins.approval_cleanup_utils.get_current_context')
    @patch('data.airflow.plugins.approval_cleanup_utils.logger')
    def test_log_with_context_info(self, mock_logger, mock_context):
        """Test logging con contexto"""
        mock_context.return_value = {
            'dag': Mock(dag_id='test_dag'),
            'dag_run': Mock(run_id='test_run', execution_date='2025-01-01'),
            'task_instance': Mock(task_id='test_task')
        }
        
        log_with_context('info', 'Test message', extra_field='value')
        
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert 'Test message' in call_args
        assert 'test_dag' in call_args
    
    @patch('data.airflow.plugins.approval_cleanup_utils.get_current_context')
    @patch('data.airflow.plugins.approval_cleanup_utils.logger')
    def test_log_with_context_fallback(self, mock_logger, mock_context):
        """Test fallback cuando no hay contexto"""
        mock_context.side_effect = Exception("No context")
        
        log_with_context('info', 'Test message')
        
        # Debería usar fallback simple
        mock_logger.info.assert_called_once_with('Test message')


class TestCheckCircuitBreaker:
    """Tests para check_circuit_breaker"""
    
    @patch('data.airflow.plugins.approval_cleanup_utils.get_pg_hook')
    def test_circuit_breaker_inactive(self, mock_get_hook):
        """Test circuit breaker inactivo"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_first.return_value = (2,)  # Solo 2 fallos
        
        result = check_circuit_breaker()
        
        assert result['active'] is False
        assert result['failure_count'] == 2
    
    @patch('data.airflow.plugins.approval_cleanup_utils.get_pg_hook')
    def test_circuit_breaker_active(self, mock_get_hook):
        """Test circuit breaker activo"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        # 10 fallos (mayor que threshold de 5)
        mock_hook.get_first.return_value = (10,)
        
        result = check_circuit_breaker()
        
        assert result['active'] is True
        assert result['failure_count'] == 10
        assert result['reason'] == 'too_many_failures'
    
    @patch('data.airflow.plugins.approval_cleanup_utils.get_pg_hook')
    def test_circuit_breaker_no_table(self, mock_get_hook):
        """Test cuando no existe tabla de historial"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        mock_hook.get_first.side_effect = Exception("Table not found")
        
        result = check_circuit_breaker()
        
        assert result['active'] is False
        assert result['reason'] == 'history_table_unavailable'


class TestValidateParams:
    """Tests para validate_params"""
    
    @pytest.mark.parametrize("retention_years,retention_months,dry_run,should_pass", [
        (1, 1, False, True),
        (5, 12, True, True),
        (10, 24, False, True),
        (2, 6, False, True),
        (0, 6, False, False),  # Menor que mínimo
        (11, 6, False, False),  # Mayor que máximo
        (2, 0, False, False),  # Menor que mínimo
        (2, 25, False, False),  # Mayor que máximo
        (2, 6, 'yes', False),  # dry_run no es boolean
        (2, 6, 1, False),  # dry_run no es boolean
    ])
    def test_validate_params_various(self, retention_years, retention_months, dry_run, should_pass):
        """Test validación con varios parámetros"""
        params = {
            'archive_retention_years': retention_years,
            'notification_retention_months': retention_months,
            'dry_run': dry_run
        }
        
        if should_pass:
            validate_params(params)  # No debería lanzar excepción
        else:
            with pytest.raises(AirflowFailException):
                validate_params(params)
    
    def test_validate_params_valid(self):
        """Test validación con parámetros válidos"""
        params = {
            'archive_retention_years': 2,
            'notification_retention_months': 6,
            'dry_run': False
        }
        
        # No debería lanzar excepción
        validate_params(params)
    
    def test_validate_params_invalid_retention_years(self):
        """Test validación con años de retención inválidos"""
        params = {
            'archive_retention_years': 15,  # Mayor que 10
            'notification_retention_months': 6,
            'dry_run': False
        }
        
        with pytest.raises(AirflowFailException, match="archive_retention_years"):
            validate_params(params)
    
    def test_validate_params_invalid_notification_months(self):
        """Test validación con meses de retención inválidos"""
        params = {
            'archive_retention_years': 1,
            'notification_retention_months': 30,  # Mayor que 24
            'dry_run': False
        }
        
        with pytest.raises(AirflowFailException, match="notification_retention_months"):
            validate_params(params)
    
    def test_validate_params_invalid_dry_run(self):
        """Test validación con dry_run inválido"""
        params = {
            'archive_retention_years': 1,
            'notification_retention_months': 6,
            'dry_run': 'yes'  # No es boolean
        }
        
        with pytest.raises(AirflowFailException, match="dry_run"):
            validate_params(params)
    
    def test_validate_params_missing_keys(self):
        """Test validación con claves faltantes (usa defaults)"""
        params = {}  # Sin claves
        
        # Debería usar valores por defecto o fallar
        try:
            validate_params(params)
        except (AirflowFailException, KeyError):
            pass  # Esperado si requiere todas las claves


class TestFormatDurationMs:
    """Tests para format_duration_ms"""
    
    @pytest.mark.parametrize("duration_ms,expected_pattern", [
        (0, "ms"),
        (500, "500ms"),
        (999, "ms"),
        (1000, "1"),
        (1500, "1.5"),
        (2500, "2.5"),
        (60000, "m"),
        (125000, "m"),
        (3600000, "m"),
        (3600000 * 24, "m"),
    ])
    def test_format_duration_ms_various(self, duration_ms, expected_pattern):
        """Test formateo de duración en varios casos"""
        result = format_duration_ms(duration_ms)
        
        assert expected_pattern in result
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_format_duration_ms_milliseconds(self):
        """Test formateo de milisegundos"""
        result = format_duration_ms(500)
        assert result == "500ms"
    
    def test_format_duration_ms_seconds(self):
        """Test formateo de segundos"""
        result = format_duration_ms(2500)
        assert "2.50s" in result or "2.5s" in result
    
    def test_format_duration_ms_minutes(self):
        """Test formateo de minutos"""
        result = format_duration_ms(125000)  # 2 minutos 5 segundos
        assert "m" in result
        assert "s" in result
    
    def test_format_duration_ms_very_large(self):
        """Test formateo de duración muy grande"""
        result = format_duration_ms(3600000 * 24)  # 24 horas
        assert len(result) > 0
        assert "m" in result or "h" in result


class TestFormatBytes:
    """Tests para format_bytes"""
    
    @pytest.mark.parametrize("bytes_value,expected_unit", [
        (0, "B"),
        (1, "B"),
        (500, "B"),
        (1023, "B"),
        (1024, "KB"),
        (1024 * 1024 - 1, "KB"),
        (1024 * 1024, "MB"),
        (1024 * 1024 * 1024 - 1, "MB"),
        (1024 * 1024 * 1024, "GB"),
        (1024 * 1024 * 1024 * 1024, "TB"),
    ])
    def test_format_bytes_various(self, bytes_value, expected_unit):
        """Test formateo de bytes en varios casos"""
        result = format_bytes(bytes_value)
        
        assert expected_unit in result
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_format_bytes_bytes(self):
        """Test formateo de bytes"""
        result = format_bytes(500)
        assert "B" in result
    
    def test_format_bytes_kb(self):
        """Test formateo de kilobytes"""
        result = format_bytes(2048)
        assert "KB" in result
    
    def test_format_bytes_mb(self):
        """Test formateo de megabytes"""
        result = format_bytes(2 * 1024 * 1024)
        assert "MB" in result
    
    def test_format_bytes_gb(self):
        """Test formateo de gigabytes"""
        result = format_bytes(2 * 1024 * 1024 * 1024)
        assert "GB" in result
    
    def test_format_bytes_very_large(self):
        """Test formateo de bytes muy grandes"""
        result = format_bytes(1024 ** 5)  # 1 PB
        assert "PB" in result or "TB" in result


class TestSafeDivide:
    """Tests para safe_divide"""
    
    def test_safe_divide_normal(self):
        """Test división normal"""
        result = safe_divide(10, 2)
        assert result == 5.0
    
    def test_safe_divide_zero_denominator(self):
        """Test división por cero"""
        result = safe_divide(10, 0)
        assert result == 0.0
    
    def test_safe_divide_zero_denominator_custom_default(self):
        """Test división por cero con default personalizado"""
        result = safe_divide(10, 0, default=-1.0)
        assert result == -1.0


class TestCalculatePercentageChange:
    """Tests para calculate_percentage_change"""
    
    def test_calculate_percentage_change_increase(self):
        """Test cambio porcentual positivo"""
        result = calculate_percentage_change(100, 150)
        assert result == 50.0
    
    def test_calculate_percentage_change_decrease(self):
        """Test cambio porcentual negativo"""
        result = calculate_percentage_change(100, 75)
        assert result == -25.0
    
    def test_calculate_percentage_change_zero_old(self):
        """Test cuando el valor antiguo es cero"""
        result = calculate_percentage_change(0, 100)
        assert result == float('inf')
    
    def test_calculate_percentage_change_zero_new(self):
        """Test cuando el valor nuevo es cero"""
        result = calculate_percentage_change(100, 0)
        assert result == -100.0


