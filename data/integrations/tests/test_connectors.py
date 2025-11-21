"""
Tests unitarios para conectores
================================
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from data.integrations.connectors import (
    HubSpotConnector,
    QuickBooksConnector,
    GoogleSheetsConnector,
    DatabaseConnector,
    SyncRecord,
    create_connector
)


class TestHubSpotConnector(unittest.TestCase):
    """Tests para HubSpotConnector"""
    
    def setUp(self):
        self.config = {
            "name": "hubspot",
            "api_token": "test_token"
        }
        self.connector = HubSpotConnector(self.config)
    
    @patch('data.integrations.connectors.requests.get')
    def test_connect_success(self, mock_get):
        """Test conexión exitosa"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.connector.connect()
        self.assertTrue(result)
    
    @patch('data.integrations.connectors.requests.get')
    def test_connect_failure(self, mock_get):
        """Test fallo de conexión"""
        mock_get.side_effect = Exception("Connection error")
        
        result = self.connector.connect()
        self.assertFalse(result)
    
    @patch('data.integrations.connectors.requests.get')
    def test_read_records(self, mock_get):
        """Test lectura de registros"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "123",
                    "properties": {
                        "email": "test@example.com",
                        "firstname": "Test"
                    }
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        records = self.connector.read_records(filters={"object_type": "contacts"})
        
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].source_id, "123")
        self.assertEqual(records[0].data["email"], "test@example.com")


class TestQuickBooksConnector(unittest.TestCase):
    """Tests para QuickBooksConnector"""
    
    def setUp(self):
        self.config = {
            "name": "quickbooks",
            "access_token": "test_token",
            "realm_id": "test_realm",
            "base_url": "https://sandbox-quickbooks.api.intuit.com"
        }
        self.connector = QuickBooksConnector(self.config)
    
    @patch('data.integrations.connectors.requests.get')
    def test_connect_success(self, mock_get):
        """Test conexión exitosa"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.connector.connect()
        self.assertTrue(result)


class TestSyncRecord(unittest.TestCase):
    """Tests para SyncRecord"""
    
    def test_checksum_calculation(self):
        """Test cálculo de checksum"""
        record = SyncRecord(
            source_id="123",
            source_type="test",
            data={"key": "value"}
        )
        
        self.assertIsNotNone(record.checksum)
        self.assertEqual(len(record.checksum), 64)  # SHA256 hex length
    
    def test_checksum_consistency(self):
        """Test que checksum es consistente"""
        data = {"key": "value"}
        record1 = SyncRecord(
            source_id="123",
            source_type="test",
            data=data
        )
        record2 = SyncRecord(
            source_id="123",
            source_type="test",
            data=data
        )
        
        self.assertEqual(record1.checksum, record2.checksum)


class TestCreateConnector(unittest.TestCase):
    """Tests para factory function"""
    
    def test_create_hubspot_connector(self):
        """Test creación de conector HubSpot"""
        connector = create_connector("hubspot", {"api_token": "test"})
        self.assertIsInstance(connector, HubSpotConnector)
    
    def test_create_invalid_connector(self):
        """Test creación de conector inválido"""
        with self.assertRaises(ValueError):
            create_connector("invalid", {})


if __name__ == '__main__':
    unittest.main()


