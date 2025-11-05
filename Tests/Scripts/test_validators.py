"""
Tests para los validadores
"""
import unittest
from utils.validators import (
    validate_email,
    validate_phone,
    validate_sku,
    validate_price,
    validate_stock_quantity,
    validate_date,
    validate_product_data
)

class TestValidators(unittest.TestCase):
    """Tests para funciones de validación"""
    
    def test_validate_email(self):
        """Test de validación de email"""
        self.assertTrue(validate_email("test@example.com"))
        self.assertTrue(validate_email("user.name@domain.co.uk"))
        self.assertFalse(validate_email("invalid-email"))
        self.assertFalse(validate_email("@example.com"))
        self.assertFalse(validate_email("test@"))
    
    def test_validate_phone(self):
        """Test de validación de teléfono"""
        self.assertTrue(validate_phone("+52 55 1234 5678"))
        self.assertTrue(validate_phone("(555) 123-4567"))
        self.assertTrue(validate_phone("555-123-4567"))
        self.assertFalse(validate_phone("abc"))
        self.assertFalse(validate_phone("123"))
    
    def test_validate_sku(self):
        """Test de validación de SKU"""
        self.assertTrue(validate_sku("PROD-001"))
        self.assertTrue(validate_sku("ABC123"))
        self.assertTrue(validate_sku("PROD-A-001"))
        self.assertFalse(validate_sku("AB"))  # Muy corto
        self.assertFalse(validate_sku("prod-001"))  # Debe ser mayúscula
        self.assertFalse(validate_sku("PROD 001"))  # No espacios
    
    def test_validate_price(self):
        """Test de validación de precio"""
        self.assertTrue(validate_price(10.50))
        self.assertTrue(validate_price(0))
        self.assertTrue(validate_price(1000))
        self.assertFalse(validate_price(-10))
        self.assertFalse(validate_price("abc"))
        self.assertFalse(validate_price(None))
    
    def test_validate_stock_quantity(self):
        """Test de validación de cantidad de stock"""
        self.assertTrue(validate_stock_quantity(10))
        self.assertTrue(validate_stock_quantity(0))
        self.assertFalse(validate_stock_quantity(-5))
        self.assertTrue(validate_stock_quantity(-5, allow_negative=True))
        self.assertFalse(validate_stock_quantity("abc"))
    
    def test_validate_date(self):
        """Test de validación de fecha"""
        valid_date = validate_date("2024-01-15")
        self.assertIsNotNone(valid_date)
        
        invalid_date = validate_date("invalid-date")
        self.assertIsNone(invalid_date)
    
    def test_validate_product_data(self):
        """Test de validación de datos de producto"""
        # Datos válidos
        valid_data = {
            'name': 'Producto Test',
            'sku': 'TEST-001',
            'unit_price': 100.0,
            'cost_price': 50.0,
            'min_stock_level': 10,
            'max_stock_level': 100
        }
        is_valid, errors = validate_product_data(valid_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Datos inválidos
        invalid_data = {
            'name': 'AB',  # Muy corto
            'sku': 'test',  # SKU inválido
            'unit_price': -10  # Precio negativo
        }
        is_valid, errors = validate_product_data(invalid_data)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

if __name__ == '__main__':
    unittest.main()

