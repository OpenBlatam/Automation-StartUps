"""
Tests unitarios para HubSpotClient.

Ejecutar con: pytest lib/tests/test_hubspot_client.py
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from lib.hubspot_client import HubSpotClient, HubSpotContact, HubSpotResult


class TestHubSpotContact:
    """Tests para HubSpotContact."""
    
    def test_nombre_property(self):
        """Test que la propiedad nombre combina firstname y lastname."""
        contact = HubSpotContact(
            id="123",
            firstname="Juan",
            lastname="Pérez"
        )
        assert contact.nombre == "Juan Pérez"
    
    def test_nombre_fallback(self):
        """Test que nombre usa fallback si no hay firstname/lastname."""
        contact = HubSpotContact(id="123")
        assert contact.nombre == "Cliente"
        
        contact2 = HubSpotContact(id="123", firstname="Juan")
        assert contact2.nombre == "Juan"


class TestHubSpotClient:
    """Tests para HubSpotClient."""
    
    @patch('lib.hubspot_client.requests.Session')
    def test_init(self, mock_session):
        """Test inicialización del cliente."""
        client = HubSpotClient(api_token="test_token")
        assert client.api_token == "test_token"
        assert client.base_url == "https://api.hubapi.com"
        assert client.max_retries == 3
    
    @patch('lib.hubspot_client.requests.Session')
    def test_parse_webhook_payload_standard_format(self, mock_session):
        """Test parsing de webhook formato estándar."""
        client = HubSpotClient(api_token="test")
        
        payload = {
            "subscriptionType": "contact.creation",
            "objectId": "12345",
            "properties": {
                "firstname": "Juan",
                "lastname": "Pérez",
                "interés_producto": "Producto X",
                "manychat_user_id": "67890"
            }
        }
        
        contact = client.parse_webhook_payload(payload)
        assert contact is not None
        assert contact.id == "12345"
        assert contact.firstname == "Juan"
        assert contact.interes_producto == "Producto X"
        assert contact.manychat_user_id == "67890"
    
    @patch('lib.hubspot_client.requests.Session')
    def test_parse_webhook_payload_invalid(self, mock_session):
        """Test parsing de webhook inválido."""
        client = HubSpotClient(api_token="test")
        
        payload = {"invalid": "data"}
        contact = client.parse_webhook_payload(payload)
        assert contact is None
    
    @patch('lib.hubspot_client.requests.Session')
    @patch('lib.hubspot_client.requests.Response')
    def test_get_contact_success(self, mock_response, mock_session):
        """Test obtención exitosa de contacto."""
        # Setup mocks
        mock_response.json.return_value = {
            "id": "123",
            "properties": {
                "firstname": "Juan",
                "lastname": "Pérez",
                "email": "juan@example.com"
            }
        }
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        
        mock_session_instance = MagicMock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = HubSpotClient(api_token="test", use_tenacity=False)
        client.session = mock_session_instance
        
        result = client.get_contact("123", use_cache=False)
        
        assert result.success is True
        assert result.status_code == 200
        assert result.data is not None
    
    @patch('lib.hubspot_client.requests.Session')
    def test_get_contact_cache(self, mock_session):
        """Test que el caché funciona."""
        from lib.cache import SimpleCache
        
        client = HubSpotClient(api_token="test", use_tenacity=False)
        client.cache = SimpleCache(default_ttl=300)
        
        # Mock successful response
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": "123", "properties": {}}
            mock_response.raise_for_status = Mock()
            mock_request.return_value = mock_response
            
            # First call - should fetch
            result1 = client.get_contact("123", use_cache=True)
            
            # Second call - should use cache
            result2 = client.get_contact("123", use_cache=True)
            
            # Should only call API once
            assert mock_request.call_count == 1
            assert result1 == result2


class TestHubSpotResult:
    """Tests para HubSpotResult."""
    
    def test_to_dict(self):
        """Test conversión a diccionario."""
        result = HubSpotResult(
            success=True,
            status_code=200,
            message="Success",
            contact_id="123",
            nuevo_estado="active"
        )
        
        data = result.to_dict()
        assert data["success"] is True
        assert data["status_code"] == 200
        assert data["contact_id"] == "123"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



