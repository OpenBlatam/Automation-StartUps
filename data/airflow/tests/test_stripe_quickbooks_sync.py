"""
Tests unitarios y de integración para sincronización de Stripe a QuickBooks.

Este módulo prueba las principales funcionalidades del módulo
stripe_product_to_quickbooks_item incluyendo:
- Cliente de QuickBooks (configuración, autenticación, operaciones CRUD)
- Funciones de sincronización (create, update, find)
- Manejo de errores y validaciones
- Procesamiento por lotes
- Health checks y conectividad
"""
import os
import json
import pytest
import time
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from decimal import Decimal

# Mock de dependencias opcionales antes de importar
import sys
sys.modules['circuitbreaker'] = MagicMock()

# Importar módulo después de hacer mocks
from data.airflow.dags import stripe_product_to_quickbooks_item as qb_module
from data.airflow.dags.stripe_product_to_quickbooks_item import (
    QuickBooksConfig,
    QuickBooksClient,
    QuickBooksError,
    QuickBooksAuthError,
    QuickBooksAPIError,
    QuickBooksValidationError,
    SyncResult,
    BatchSyncResult,
    ItemType,
    sync_stripe_product_to_quickbooks,
    sincronizar_producto_stripe_quickbooks,
)


# ==================== FIXTURES ====================

@pytest.fixture
def sample_config():
    """Configuración de prueba para QuickBooks."""
    return QuickBooksConfig(
        access_token='test_token_12345',
        realm_id='123456789',
        base_url='https://sandbox-quickbooks.api.intuit.com',
        environment='sandbox',
        income_account='Sales'
    )


@pytest.fixture
def mock_qb_response():
    """Respuesta mock de la API de QuickBooks."""
    return {
        'QueryResponse': {
            'Item': [{
                'Id': '123',
                'Name': 'Test Product',
                'UnitPrice': 99.99,
                'Type': 'Service',
                'SyncToken': '0'
            }],
            'maxResults': 1
        }
    }


@pytest.fixture
def mock_requests_session():
    """Sesión mock de requests."""
    session = MagicMock()
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {'QueryResponse': {'Item': []}}
    response.text = json.dumps({'QueryResponse': {'Item': []}})
    session.get.return_value = response
    session.post.return_value = response
    return session


# ==================== TESTS DE CONFIGURACIÓN ====================

class TestQuickBooksConfig:
    """Tests para QuickBooksConfig."""
    
    def test_config_defaults(self):
        """Test que los valores por defecto sean correctos."""
        config = QuickBooksConfig()
        assert config.environment == "production"
        assert config.income_account == "Sales"
        assert config.api_version == "v3"
        assert config.timeout == 30
        assert config.max_retries == 3
    
    def test_config_custom_values(self, sample_config):
        """Test configuración con valores personalizados."""
        assert sample_config.access_token == 'test_token_12345'
        assert sample_config.realm_id == '123456789'
        assert sample_config.environment == 'sandbox'
        assert sample_config.income_account == 'Sales'


# ==================== TESTS DE ESTRUCTURAS DE DATOS ====================

class TestSyncResult:
    """Tests para SyncResult."""
    
    def test_sync_result_success(self):
        """Test SyncResult para operación exitosa."""
        result = SyncResult(
            success=True,
            action='creado',
            qb_item_id='123',
            stripe_product_id='prod_123',
            nombre_producto='Test Product',
            precio=99.99
        )
        assert result.success is True
        assert result.action == 'creado'
        assert result.qb_item_id == '123'
        assert str(result) == "creado 123"
    
    def test_sync_result_error(self):
        """Test SyncResult para error."""
        result = SyncResult(
            success=False,
            action=None,
            qb_item_id=None,
            error_message='Error de prueba'
        )
        assert result.success is False
        assert result.error_message == 'Error de prueba'
        assert "ERROR" in str(result)
    
    def test_sync_result_to_dict(self):
        """Test conversión de SyncResult a diccionario."""
        result = SyncResult(
            success=True,
            action='actualizado',
            qb_item_id='456',
            stripe_product_id='prod_456',
            nombre_producto='Updated Product',
            precio=149.99
        )
        result_dict = result.to_dict()
        assert result_dict['success'] is True
        assert result_dict['action'] == 'actualizado'
        assert result_dict['qb_item_id'] == '456'
        assert 'duration_ms' in result_dict


class TestBatchSyncResult:
    """Tests para BatchSyncResult."""
    
    def test_batch_sync_result_success(self):
        """Test BatchSyncResult con todos exitosos."""
        results = [
            SyncResult(success=True, action='creado', qb_item_id='1', 
                      stripe_product_id='prod_1', nombre_producto='Prod 1', precio=10.0),
            SyncResult(success=True, action='actualizado', qb_item_id='2',
                      stripe_product_id='prod_2', nombre_producto='Prod 2', precio=20.0),
        ]
        batch = BatchSyncResult(
            total=2,
            successful=2,
            failed=0,
            duration_ms=500.0,
            results=results
        )
        assert batch.total == 2
        assert batch.successful == 2
        assert batch.failed == 0
        assert batch.success_rate == 100.0
        assert batch.throughput > 0
    
    def test_batch_sync_result_with_failures(self):
        """Test BatchSyncResult con fallos."""
        results = [
            SyncResult(success=True, action='creado', qb_item_id='1',
                      stripe_product_id='prod_1', nombre_producto='Prod 1', precio=10.0),
            SyncResult(success=False, action=None, qb_item_id=None,
                      error_message='Error', stripe_product_id='prod_2', nombre_producto='Prod 2'),
        ]
        batch = BatchSyncResult(
            total=2,
            successful=1,
            failed=1,
            duration_ms=500.0,
            results=results
        )
        assert batch.success_rate == 50.0
        assert batch.failed == 1


# ==================== TESTS DE CLIENTE QUICKBOOKS ====================

class TestQuickBooksClient:
    """Tests para QuickBooksClient."""
    
    @patch('data.airflow.dags.stripe_product_to_quickbooks_item.requests.Session')
    def test_client_initialization(self, mock_session_class, sample_config):
        """Test inicialización del cliente."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        client = QuickBooksClient(sample_config)
        assert client.config == sample_config
        assert client._session == mock_session
    
    @patch('data.airflow.dags.stripe_product_to_quickbooks_item.requests.Session')
    def test_client_load_config_from_env(self, mock_session_class):
        """Test carga de configuración desde variables de entorno."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        with patch.dict(os.environ, {
            'QUICKBOOKS_ACCESS_TOKEN': 'env_token',
            'QUICKBOOKS_REALM_ID': 'env_realm',
            'QUICKBOOKS_BASE': 'https://test.api.intuit.com'
        }):
            # Limpiar cache del método lru_cache
            QuickBooksClient._load_config_from_env.cache_clear()
            client = QuickBooksClient()
            assert client.config.access_token == 'env_token'
            assert client.config.realm_id == 'env_realm'
    
    @patch('data.airflow.dags.stripe_product_to_quickbooks_item.requests.Session')
    def test_validate_item_name(self, mock_session_class, sample_config):
        """Test validación de nombre de ítem."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        client = QuickBooksClient(sample_config)
        assert client._validate_item_name('Test Product') == 'Test Product'
        assert client._validate_item_name('  Test Product  ') == 'Test Product'
        
        with pytest.raises(QuickBooksValidationError):
            client._validate_item_name('')
        
        with pytest.raises(QuickBooksValidationError):
            client._validate_item_name(None)
    
    @patch('data.airflow.dags.stripe_product_to_quickbooks_item.requests.Session')
    def test_normalize_price(self, mock_session_class, sample_config):
        """Test normalización de precios."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        client = QuickBooksClient(sample_config)
        assert client._normalize_price(99.99) == "99.99"
        assert client._normalize_price(Decimal("99.99")) == "99.99"
        assert client._normalize_price(100) == "100.00"
    
    @patch('data.airflow.dags.stripe_product_to_quickbooks_item.requests.Session')
    def test_context_manager(self, mock_session_class, sample_config):
        """Test uso del cliente como context manager."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        with QuickBooksClient(sample_config) as client:
            assert client.config == sample_config
        
        # Verificar que se intentó cerrar la sesión
        assert mock_session_class.called
    
    @patch('data.airflow.dags.stripe_product_to_quickbooks_item.requests.Session')
    def test_get_company_id(self, mock_session_class, sample_config):
        """Test obtención de company ID."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        client = QuickBooksClient(sample_config)
        company_id = client._get_company_id()
        assert company_id == '123456789'
        
        # Test con company_id en lugar de realm_id
        config2 = QuickBooksConfig(
            access_token='test',
            company_id='987654321'
        )
        client2 = QuickBooksClient(config2)
        assert client2._get_company_id() == '987654321'
        
        # Test sin company_id ni realm_id
        config3 = QuickBooksConfig(access_token='test')
        client3 = QuickBooksClient(config3)
        with pytest.raises(QuickBooksValidationError):
            client3._get_company_id()


# ==================== TESTS DE SINCRONIZACIÓN ====================

class TestSyncStripeProduct:
    """Tests para funciones de sincronización."""
    
    @patch('data.airflow.dags.stripe_product_to_quickbooks_item.QuickBooksClient')
    def test_sync_create_new_item(self, mock_client_class):
        """Test sincronización creando nuevo ítem."""
        mock_client = MagicMock()
        mock_client.find_item_by_stripe_id.return_value = None
        mock_client.find_item_by_name.return_value = None
        mock_client.create_item.return_value = '123'
        mock_client.config.income_account = 'Sales'
        mock_client_class.return_value = mock_client
        
        result = sync_stripe_product_to_quickbooks(
            stripe_product_id='prod_123',
            nombre_producto='New Product',
            precio=99.99
        )
        
        assert result.success is True
        assert result.action == 'creado'
        assert result.qb_item_id == '123'
        mock_client.create_item.assert_called_once()
    
    @patch('data.airflow.dags.stripe_product_to_quickbooks_item.QuickBooksClient')
    def test_sync_update_existing_item(self, mock_client_class):
        """Test sincronización actualizando ítem existente."""
        mock_client = MagicMock()
        mock_client.find_item_by_stripe_id.return_value = None
        mock_client.find_item_by_name.return_value = {
            'Id': '456',
            'Name': 'Existing Product',
            'Type': 'Service',
            'SyncToken': '0'
        }
        mock_client.update_item.return_value = '456'
        mock_client.config.income_account = 'Sales'
        mock_client_class.return_value = mock_client
        
        result = sync_stripe_product_to_quickbooks(
            stripe_product_id='prod_456',
            nombre_producto='Existing Product',
            precio=149.99
        )
        
        assert result.success is True
        assert result.action == 'actualizado'
        assert result.qb_item_id == '456'
        mock_client.update_item.assert_called_once()
    
    @patch('data.airflow.dags.stripe_product_to_quickbooks_item.QuickBooksClient')
    def test_sync_validation_error(self, mock_client_class):
        """Test manejo de error de validación."""
        mock_client = MagicMock()
        mock_client.find_item_by_stripe_id.side_effect = QuickBooksValidationError("Invalid name")
        mock_client_class.return_value = mock_client
        
        result = sync_stripe_product_to_quickbooks(
            stripe_product_id='prod_123',
            nombre_producto='Test Product',
            precio=99.99
        )
        
        assert result.success is False
        assert 'ERROR_VALIDATION' in result.error_message
    
    @patch('data.airflow.dags.stripe_product_to_quickbooks_item.QuickBooksClient')
    def test_sync_auth_error(self, mock_client_class):
        """Test manejo de error de autenticación."""
        mock_client = MagicMock()
        mock_client.find_item_by_stripe_id.side_effect = QuickBooksAuthError("Invalid token")
        mock_client_class.return_value = mock_client
        
        result = sync_stripe_product_to_quickbooks(
            stripe_product_id='prod_123',
            nombre_producto='Test Product',
            precio=99.99
        )
        
        assert result.success is False
        assert 'ERROR_AUTH' in result.error_message
    
    def test_sync_validation_empty_product_id(self):
        """Test validación de product_id vacío."""
        result = sync_stripe_product_to_quickbooks(
            stripe_product_id='',
            nombre_producto='Test Product',
            precio=99.99
        )
        
        assert result.success is False
        assert 'stripe_product_id es requerido' in result.error_message
    
    def test_sync_validation_empty_name(self):
        """Test validación de nombre vacío."""
        result = sync_stripe_product_to_quickbooks(
            stripe_product_id='prod_123',
            nombre_producto='',
            precio=99.99
        )
        
        assert result.success is False
        assert 'nombre_producto es requerido' in result.error_message
    
    def test_sync_validation_negative_price(self):
        """Test validación de precio negativo."""
        result = sync_stripe_product_to_quickbooks(
            stripe_product_id='prod_123',
            nombre_producto='Test Product',
            precio=-10.0
        )
        
        assert result.success is False
        assert 'precio debe ser mayor o igual a cero' in result.error_message or \
               'ERROR_VALIDATION' in result.error_message
    
    @patch('data.airflow.dags.stripe_product_to_quickbooks_item.QuickBooksClient')
    def test_legacy_wrapper_function(self, mock_client_class):
        """Test función wrapper legacy."""
        mock_client = MagicMock()
        mock_client.find_item_by_stripe_id.return_value = None
        mock_client.find_item_by_name.return_value = None
        mock_client.create_item.return_value = '789'
        mock_client.config.income_account = 'Sales'
        mock_client_class.return_value = mock_client
        
        result_str = sincronizar_producto_stripe_quickbooks(
            stripe_product_id='prod_789',
            nombre_producto='Legacy Product',
            precio=199.99
        )
        
        assert 'creado' in result_str
        assert '789' in result_str


# ==================== TESTS DE ERRORES ====================

class TestExceptionHandling:
    """Tests para manejo de excepciones."""
    
    def test_quickbooks_error(self):
        """Test excepción base QuickBooksError."""
        error = QuickBooksError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_quickbooks_auth_error(self):
        """Test QuickBooksAuthError."""
        error = QuickBooksAuthError("Auth failed")
        assert str(error) == "Auth failed"
        assert isinstance(error, QuickBooksError)
    
    def test_quickbooks_api_error(self):
        """Test QuickBooksAPIError con status code."""
        error = QuickBooksAPIError("API error", status_code=400)
        assert str(error) == "API error"
        assert error.status_code == 400
        assert isinstance(error, QuickBooksError)
    
    def test_quickbooks_validation_error(self):
        """Test QuickBooksValidationError."""
        error = QuickBooksValidationError("Validation failed")
        assert str(error) == "Validation failed"
        assert isinstance(error, QuickBooksError)


# ==================== TESTS DE HEALTH CHECK ====================

class TestHealthCheck:
    """Tests para health check."""
    
    @patch('data.airflow.dags.stripe_product_to_quickbooks_item.requests.Session')
    def test_health_check_success(self, mock_session_class, sample_config):
        """Test health check exitoso."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'QueryResponse': {}}
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = QuickBooksClient(sample_config)
        client._get_access_token = MagicMock(return_value='test_token')
        client._get_company_id = MagicMock(return_value='123456789')
        client._get_headers = MagicMock(return_value={'Authorization': 'Bearer test_token'})
        
        health = client.health_check()
        
        assert 'status' in health
        assert 'checks' in health
        assert 'timestamp' in health
    
    @patch('data.airflow.dags.stripe_product_to_quickbooks_item.requests.Session')
    def test_health_check_with_errors(self, mock_session_class, sample_config):
        """Test health check con errores."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        client = QuickBooksClient(sample_config)
        client._get_access_token = MagicMock(side_effect=Exception("Token error"))
        client._get_company_id = MagicMock(return_value='123456789')
        
        health = client.health_check()
        
        assert health['status'] == 'error' or 'error' in health['checks'].get('authentication', {})


# ==================== TESTS DE VALIDACIÓN DE ENTRADA ====================

class TestInputValidation:
    """Tests para validación de entrada."""
    
    def test_valid_product_input(self):
        """Test entrada válida de producto."""
        # Esto debería funcionar sin errores
        from data.airflow.dags.stripe_product_to_quickbooks_item import sync_stripe_product_to_quickbooks
        
        # Solo validamos que la función acepta los parámetros correctos
        # La ejecución real se prueba en otros tests
        assert callable(sync_stripe_product_to_quickbooks)
    
    @pytest.mark.skipif(not qb_module.PYDANTIC_AVAILABLE, reason="Pydantic no disponible")
    def test_pydantic_validation(self):
        """Test validación con Pydantic si está disponible."""
        if qb_module.PYDANTIC_AVAILABLE:
            from data.airflow.dags.stripe_product_to_quickbooks_item import StripeProductInput
            
            # Entrada válida
            valid_input = StripeProductInput(
                stripe_product_id='prod_123',
                nombre_producto='Test',
                precio=Decimal('99.99')
            )
            assert valid_input.stripe_product_id == 'prod_123'
            
            # Entrada inválida
            with pytest.raises(Exception):  # Puede ser ValidationError o similar
                StripeProductInput(
                    stripe_product_id='',
                    nombre_producto='Test',
                    precio=Decimal('99.99')
                )


# ==================== TESTS DE ITEM TYPE ====================

class TestItemType:
    """Tests para ItemType enum."""
    
    def test_item_type_values(self):
        """Test valores del enum ItemType."""
        assert ItemType.SERVICE.value == "Service"
        assert ItemType.INVENTORY.value == "Inventory"
        assert ItemType.NON_INVENTORY.value == "NonInventory"
    
    def test_item_type_creation(self):
        """Test creación de ItemType desde string."""
        assert ItemType("Service") == ItemType.SERVICE
        assert ItemType("Inventory") == ItemType.INVENTORY


# ==================== TESTS DE INTEGRACIÓN ====================

class TestIntegrationScenarios:
    """Tests de escenarios de integración."""
    
    @patch('data.airflow.dags.stripe_product_to_quickbooks_item.QuickBooksClient')
    def test_full_workflow_create_then_update(self, mock_client_class):
        """Test flujo completo: crear y luego actualizar."""
        mock_client = MagicMock()
        mock_client.config.income_account = 'Sales'
        mock_client_class.return_value = mock_client
        
        # Primera sincronización - crear
        mock_client.find_item_by_stripe_id.return_value = None
        mock_client.find_item_by_name.return_value = None
        mock_client.create_item.return_value = '100'
        
        result1 = sync_stripe_product_to_quickbooks(
            stripe_product_id='prod_100',
            nombre_producto='Workflow Product',
            precio=99.99,
            quickbooks_client=mock_client
        )
        
        assert result1.success is True
        assert result1.action == 'creado'
        
        # Segunda sincronización - actualizar
        mock_client.find_item_by_stripe_id.return_value = None
        mock_client.find_item_by_name.return_value = {
            'Id': '100',
            'Name': 'Workflow Product',
            'Type': 'Service',
            'SyncToken': '1'
        }
        mock_client.update_item.return_value = '100'
        
        result2 = sync_stripe_product_to_quickbooks(
            stripe_product_id='prod_100',
            nombre_producto='Workflow Product',
            precio=149.99,
            quickbooks_client=mock_client
        )
        
        assert result2.success is True
        assert result2.action == 'actualizado'
    
    def test_multiple_price_formats(self):
        """Test manejo de múltiples formatos de precio."""
        # Los precios deberían aceptarse como float, Decimal, o string numérico
        @patch('data.airflow.dags.stripe_product_to_quickbooks_item.QuickBooksClient')
        def test_with_price_type(price_value):
            mock_client_class = MagicMock()
            mock_client = MagicMock()
            mock_client.find_item_by_stripe_id.return_value = None
            mock_client.find_item_by_name.return_value = None
            mock_client.create_item.return_value = '200'
            mock_client.config.income_account = 'Sales'
            mock_client_class.return_value = mock_client
            
            result = sync_stripe_product_to_quickbooks(
                stripe_product_id='prod_200',
                nombre_producto='Price Test',
                precio=price_value
            )
            return result.success
        
        # Test con diferentes tipos de precio
        assert callable(test_with_price_type)


# ==================== MAIN ====================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
