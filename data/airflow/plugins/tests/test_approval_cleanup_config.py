"""
Tests para approval_cleanup_config.py
"""
from __future__ import annotations

import pytest
import os
from unittest.mock import patch

from data.airflow.plugins.approval_cleanup_config import (
    APPROVALS_DB_CONN,
    MAX_RETENTION_YEARS,
    MIN_RETENTION_YEARS,
    MAX_NOTIFICATION_RETENTION_MONTHS,
    MIN_NOTIFICATION_RETENTION_MONTHS,
    STALE_THRESHOLD_DAYS,
    BATCH_SIZE,
    BATCH_SIZE_MIN,
    BATCH_SIZE_MAX,
    BATCH_SIZE_ADAPTIVE,
    MAX_QUERY_TIMEOUT_SECONDS,
    QUERY_TIMEOUT_SECONDS,
    REPORT_EXPORT_DIR,
    REPORT_RETENTION_DAYS,
    PERFORMANCE_HISTORY_DAYS,
    SLOW_TASK_THRESHOLD_MS,
    ANOMALY_Z_SCORE_THRESHOLD,
    PERFORMANCE_HISTORY_WINDOW,
    PREDICTION_WINDOW_DAYS,
    CIRCUIT_BREAKER_FAILURE_THRESHOLD,
    CIRCUIT_BREAKER_CHECK_WINDOW_HOURS,
    MAX_PARALLEL_WORKERS,
    CACHE_ENABLED,
    CACHE_TTL_SECONDS,
    get_config,
)


class TestConstants:
    """Tests para constantes básicas"""
    
    def test_retention_constants(self):
        """Test que las constantes de retención tienen valores válidos"""
        assert MAX_RETENTION_YEARS >= MIN_RETENTION_YEARS
        assert MAX_RETENTION_YEARS > 0
        assert MIN_RETENTION_YEARS > 0
        assert MAX_NOTIFICATION_RETENTION_MONTHS >= MIN_NOTIFICATION_RETENTION_MONTHS
        assert MAX_NOTIFICATION_RETENTION_MONTHS > 0
        assert MIN_NOTIFICATION_RETENTION_MONTHS > 0
    
    def test_batch_size_constants(self):
        """Test que las constantes de batch size tienen valores válidos"""
        assert BATCH_SIZE_MIN < BATCH_SIZE_MAX
        assert BATCH_SIZE >= BATCH_SIZE_MIN
        assert BATCH_SIZE <= BATCH_SIZE_MAX
        assert BATCH_SIZE_MIN > 0
        assert BATCH_SIZE_MAX > 0
    
    def test_timeout_constants(self):
        """Test que las constantes de timeout tienen valores válidos"""
        assert MAX_QUERY_TIMEOUT_SECONDS > 0
        assert QUERY_TIMEOUT_SECONDS > 0
        assert QUERY_TIMEOUT_SECONDS <= MAX_QUERY_TIMEOUT_SECONDS
    
    def test_stale_threshold(self):
        """Test que el threshold de stale tiene un valor válido"""
        assert STALE_THRESHOLD_DAYS > 0
    
    def test_performance_constants(self):
        """Test que las constantes de performance tienen valores válidos"""
        assert PERFORMANCE_HISTORY_DAYS > 0
        assert SLOW_TASK_THRESHOLD_MS > 0
        assert ANOMALY_Z_SCORE_THRESHOLD > 0
        assert PERFORMANCE_HISTORY_WINDOW > 0
        assert PREDICTION_WINDOW_DAYS > 0
    
    def test_circuit_breaker_constants(self):
        """Test que las constantes de circuit breaker tienen valores válidos"""
        assert CIRCUIT_BREAKER_FAILURE_THRESHOLD > 0
        assert CIRCUIT_BREAKER_CHECK_WINDOW_HOURS > 0
    
    def test_parallelism_constants(self):
        """Test que las constantes de paralelismo tienen valores válidos"""
        assert MAX_PARALLEL_WORKERS > 0
    
    def test_cache_constants(self):
        """Test que las constantes de cache tienen valores válidos"""
        assert isinstance(CACHE_ENABLED, bool)
        assert CACHE_TTL_SECONDS > 0


class TestEnvironmentVariables:
    """Tests para variables de entorno"""
    
    @patch.dict(os.environ, {'APPROVALS_DB_CONN_ID': 'test_db_conn'}, clear=False)
    def test_db_conn_from_env(self):
        """Test que APPROVALS_DB_CONN lee de variable de entorno"""
        # Reimportar para obtener el valor actualizado
        import importlib
        import data.airflow.plugins.approval_cleanup_config as config_module
        importlib.reload(config_module)
        
        assert config_module.APPROVALS_DB_CONN == 'test_db_conn'
    
    def test_db_conn_default(self):
        """Test que APPROVALS_DB_CONN tiene un valor por defecto"""
        # El valor por defecto debería ser 'approvals_db'
        assert APPROVALS_DB_CONN is not None
        assert isinstance(APPROVALS_DB_CONN, str)
    
    @patch.dict(os.environ, {'APPROVAL_CLEANUP_QUERY_TIMEOUT': '600'}, clear=False)
    def test_query_timeout_from_env(self):
        """Test que QUERY_TIMEOUT_SECONDS lee de variable de entorno"""
        import importlib
        import data.airflow.plugins.approval_cleanup_config as config_module
        importlib.reload(config_module)
        
        assert config_module.QUERY_TIMEOUT_SECONDS == 600
    
    @patch.dict(os.environ, {'APPROVAL_CLEANUP_BATCH_ADAPTIVE': 'false'}, clear=False)
    def test_batch_adaptive_from_env(self):
        """Test que BATCH_SIZE_ADAPTIVE lee de variable de entorno"""
        import importlib
        import data.airflow.plugins.approval_cleanup_config as config_module
        importlib.reload(config_module)
        
        assert config_module.BATCH_SIZE_ADAPTIVE is False
    
    @patch.dict(os.environ, {'APPROVAL_CLEANUP_ANOMALY_Z_SCORE': '3.0'}, clear=False)
    def test_anomaly_threshold_from_env(self):
        """Test que ANOMALY_Z_SCORE_THRESHOLD lee de variable de entorno"""
        import importlib
        import data.airflow.plugins.approval_cleanup_config as config_module
        importlib.reload(config_module)
        
        assert config_module.ANOMALY_Z_SCORE_THRESHOLD == 3.0


class TestGetConfig:
    """Tests para get_config"""
    
    def test_get_config_structure(self):
        """Test que get_config retorna un diccionario con estructura correcta"""
        config = get_config()
        
        assert isinstance(config, dict)
        assert 'db_conn' in config
        assert 'retention' in config
        assert 'batch' in config
        assert 'timeouts' in config
        assert 'features' in config
        assert 'observability' in config
        assert 'export' in config
    
    def test_get_config_db_conn(self):
        """Test que get_config incluye db_conn"""
        config = get_config()
        
        assert 'db_conn' in config
        assert config['db_conn'] == APPROVALS_DB_CONN
    
    def test_get_config_retention(self):
        """Test que get_config incluye configuración de retención"""
        config = get_config()
        
        assert 'retention' in config
        retention = config['retention']
        assert 'max_years' in retention
        assert 'min_years' in retention
        assert 'max_notification_months' in retention
        assert 'min_notification_months' in retention
        assert 'stale_threshold_days' in retention
        
        assert retention['max_years'] == MAX_RETENTION_YEARS
        assert retention['min_years'] == MIN_RETENTION_YEARS
        assert retention['max_notification_months'] == MAX_NOTIFICATION_RETENTION_MONTHS
        assert retention['min_notification_months'] == MIN_NOTIFICATION_RETENTION_MONTHS
        assert retention['stale_threshold_days'] == STALE_THRESHOLD_DAYS
    
    def test_get_config_batch(self):
        """Test que get_config incluye configuración de batch"""
        config = get_config()
        
        assert 'batch' in config
        batch = config['batch']
        assert 'size' in batch
        assert 'min' in batch
        assert 'max' in batch
        assert 'adaptive' in batch
        
        assert batch['size'] == BATCH_SIZE
        assert batch['min'] == BATCH_SIZE_MIN
        assert batch['max'] == BATCH_SIZE_MAX
        assert batch['adaptive'] == BATCH_SIZE_ADAPTIVE
    
    def test_get_config_timeouts(self):
        """Test que get_config incluye configuración de timeouts"""
        config = get_config()
        
        assert 'timeouts' in config
        timeouts = config['timeouts']
        assert 'query_seconds' in timeouts
        assert 'max_query_seconds' in timeouts
        
        assert timeouts['query_seconds'] == QUERY_TIMEOUT_SECONDS
        assert timeouts['max_query_seconds'] == MAX_QUERY_TIMEOUT_SECONDS
    
    def test_get_config_features(self):
        """Test que get_config incluye feature toggles"""
        config = get_config()
        
        assert 'features' in config
        features = config['features']
        
        # Verificar que tiene algunas features clave
        assert 'query_optimization' in features
        assert 'missing_index_analysis' in features
        assert 'security_analysis' in features
        assert 'compliance_analysis' in features
        assert 'predictive_analytics' in features
        assert 'performance_profiling' in features
        
        # Verificar que son booleanos
        for feature_value in features.values():
            assert isinstance(feature_value, bool)
    
    def test_get_config_observability(self):
        """Test que get_config incluye configuración de observabilidad"""
        config = get_config()
        
        assert 'observability' in config
        observability = config['observability']
        assert 'prometheus_enabled' in observability
        assert 'prometheus_gateway' in observability
    
    def test_get_config_export(self):
        """Test que get_config incluye configuración de export"""
        config = get_config()
        
        assert 'export' in config
        export = config['export']
        assert 's3_enabled' in export
        assert 's3_bucket' in export
        assert 'report_dir' in export
        
        assert export['report_dir'] == REPORT_EXPORT_DIR
    
    def test_get_config_consistency(self):
        """Test que get_config retorna valores consistentes en múltiples llamadas"""
        config1 = get_config()
        config2 = get_config()
        
        assert config1 == config2
        assert config1['db_conn'] == config2['db_conn']
        assert config1['retention'] == config2['retention']


class TestFeatureToggles:
    """Tests para feature toggles"""
    
    def test_feature_toggles_are_booleans(self):
        """Test que los feature toggles son booleanos"""
        # Importar todos los feature toggles
        from data.airflow.plugins.approval_cleanup_config import (
            ENABLE_QUERY_OPTIMIZATION,
            ENABLE_MISSING_INDEX_ANALYSIS,
            ENABLE_SECURITY_ANALYSIS,
            ENABLE_COMPLIANCE_ANALYSIS,
            ENABLE_PREDICTIVE_ANALYTICS,
            ENABLE_PERFORMANCE_PROFILING,
            PROMETHEUS_ENABLED,
            S3_EXPORT_ENABLED,
        )
        
        toggles = [
            ENABLE_QUERY_OPTIMIZATION,
            ENABLE_MISSING_INDEX_ANALYSIS,
            ENABLE_SECURITY_ANALYSIS,
            ENABLE_COMPLIANCE_ANALYSIS,
            ENABLE_PREDICTIVE_ANALYTICS,
            ENABLE_PERFORMANCE_PROFILING,
            PROMETHEUS_ENABLED,
            S3_EXPORT_ENABLED,
        ]
        
        for toggle in toggles:
            assert isinstance(toggle, bool), f"{toggle} should be a boolean"
    
    @patch.dict(os.environ, {'APPROVAL_CLEANUP_QUERY_OPTIMIZATION': 'false'}, clear=False)
    def test_feature_toggle_from_env_false(self):
        """Test que los feature toggles leen 'false' de variables de entorno"""
        import importlib
        import data.airflow.plugins.approval_cleanup_config as config_module
        importlib.reload(config_module)
        
        assert config_module.ENABLE_QUERY_OPTIMIZATION is False
    
    @patch.dict(os.environ, {'APPROVAL_CLEANUP_QUERY_OPTIMIZATION': 'true'}, clear=False)
    def test_feature_toggle_from_env_true(self):
        """Test que los feature toggles leen 'true' de variables de entorno"""
        import importlib
        import data.airflow.plugins.approval_cleanup_config as config_module
        importlib.reload(config_module)
        
        assert config_module.ENABLE_QUERY_OPTIMIZATION is True


class TestReportPaths:
    """Tests para paths de reportes"""
    
    def test_report_export_dir(self):
        """Test que REPORT_EXPORT_DIR tiene un valor válido"""
        assert REPORT_EXPORT_DIR is not None
        assert isinstance(REPORT_EXPORT_DIR, str)
        assert len(REPORT_EXPORT_DIR) > 0
    
    @patch.dict(os.environ, {'APPROVAL_CLEANUP_REPORT_DIR': '/custom/reports'}, clear=False)
    def test_report_export_dir_from_env(self):
        """Test que REPORT_EXPORT_DIR lee de variable de entorno"""
        import importlib
        import data.airflow.plugins.approval_cleanup_config as config_module
        importlib.reload(config_module)
        
        assert config_module.REPORT_EXPORT_DIR == '/custom/reports'
    
    def test_report_retention_days(self):
        """Test que REPORT_RETENTION_DAYS tiene un valor válido"""
        assert REPORT_RETENTION_DAYS > 0
        assert isinstance(REPORT_RETENTION_DAYS, int)

