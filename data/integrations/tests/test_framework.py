"""
Tests para el framework de sincronización
==========================================
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from data.integrations.sync_framework import (
    SyncFramework,
    SyncConfig,
    SyncDirection,
    SyncStatus,
    CircuitBreaker
)


class TestCircuitBreaker(unittest.TestCase):
    """Tests para CircuitBreaker"""
    
    def setUp(self):
        self.cb = CircuitBreaker(threshold=3, timeout_seconds=60)
    
    def test_initial_state(self):
        """Test estado inicial"""
        self.assertEqual(self.cb.state, "closed")
        self.assertEqual(self.cb.failure_count, 0)
        self.assertTrue(self.cb.can_execute())
    
    def test_record_failure(self):
        """Test registro de fallos"""
        self.cb.record_failure()
        self.assertEqual(self.cb.failure_count, 1)
        self.assertTrue(self.cb.can_execute())
        
        self.cb.record_failure()
        self.cb.record_failure()
        
        self.assertEqual(self.cb.state, "open")
        self.assertFalse(self.cb.can_execute())
    
    def test_record_success(self):
        """Test registro de éxito"""
        self.cb.record_failure()
        self.cb.record_failure()
        self.cb.record_success()
        
        self.assertEqual(self.cb.failure_count, 0)
        self.assertEqual(self.cb.state, "closed")
        self.assertTrue(self.cb.can_execute())


class TestSyncConfig(unittest.TestCase):
    """Tests para SyncConfig"""
    
    def test_default_values(self):
        """Test valores por defecto"""
        config = SyncConfig(
            sync_id="test",
            source_connector_type="hubspot",
            source_config={},
            target_connector_type="quickbooks",
            target_config={}
        )
        
        self.assertEqual(config.direction, SyncDirection.BIDIRECTIONAL)
        self.assertEqual(config.batch_size, 50)
        self.assertTrue(config.enable_circuit_breaker)
        self.assertTrue(config.enable_validation)


class TestSyncFramework(unittest.TestCase):
    """Tests para SyncFramework"""
    
    def setUp(self):
        self.framework = SyncFramework(db_connection_string=None)
    
    def test_get_circuit_breaker(self):
        """Test obtención de circuit breaker"""
        cb1 = self.framework._get_circuit_breaker("hubspot")
        cb2 = self.framework._get_circuit_breaker("hubspot")
        
        self.assertIs(cb1, cb2)  # Mismo objeto
    
    def test_cache_operations(self):
        """Test operaciones de caché"""
        self.framework._set_cache("test_key", "test_value")
        
        value = self.framework._get_from_cache("test_key", ttl_seconds=300)
        self.assertEqual(value, "test_value")
        
        # Test expiración
        value = self.framework._get_from_cache("test_key", ttl_seconds=0)
        self.assertIsNone(value)
    
    def test_validate_record(self):
        """Test validación de registro"""
        from data.integrations.connectors import SyncRecord
        
        # Registro válido
        record = SyncRecord(
            source_id="123",
            source_type="test",
            data={"key": "value"}
        )
        is_valid, error = self.framework._validate_record(record)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Registro inválido (sin source_id)
        record_invalid = SyncRecord(
            source_id="",
            source_type="test",
            data={"key": "value"}
        )
        is_valid, error = self.framework._validate_record(record_invalid)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)


if __name__ == '__main__':
    unittest.main()


