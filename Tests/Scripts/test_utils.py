"""
Tests para funciones utilitarias
"""
import unittest
from datetime import datetime
from utils.formatters import (
    format_currency,
    format_date,
    format_percentage,
    format_stock_status,
    truncate_text
)
from utils.helpers import (
    safe_divide,
    calculate_percentage_change,
    sanitize_filename,
    generate_sku
)

class TestFormatters(unittest.TestCase):
    """Tests para funciones de formateo"""
    
    def test_format_currency(self):
        """Test de formateo de moneda"""
        self.assertEqual(format_currency(1000.50), "$1,000.50")
        self.assertEqual(format_currency(1000.50, 'USD'), "$1,000.50")
    
    def test_format_date(self):
        """Test de formateo de fecha"""
        date = datetime(2024, 1, 15, 10, 30, 0)
        formatted = format_date(date)
        self.assertIn("2024-01-15", formatted)
        
        self.assertEqual(format_date(None), "")
    
    def test_format_percentage(self):
        """Test de formateo de porcentaje"""
        self.assertEqual(format_percentage(0.25), "25.00%")
        self.assertEqual(format_percentage(0.123, decimals=1), "12.3%")
    
    def test_format_stock_status(self):
        """Test de formateo de estado de stock"""
        self.assertEqual(format_stock_status(0, 10, 100), "Agotado")
        self.assertEqual(format_stock_status(5, 10, 100), "Bajo")
        self.assertEqual(format_stock_status(50, 10, 100), "Normal")
        self.assertEqual(format_stock_status(150, 10, 100), "Exceso")
    
    def test_truncate_text(self):
        """Test de truncado de texto"""
        text = "Este es un texto muy largo que necesita ser truncado"
        truncated = truncate_text(text, max_length=20)
        self.assertLessEqual(len(truncated), 20)
        self.assertTrue(truncated.endswith("..."))

class TestHelpers(unittest.TestCase):
    """Tests para funciones auxiliares"""
    
    def test_safe_divide(self):
        """Test de división segura"""
        self.assertEqual(safe_divide(10, 2), 5.0)
        self.assertEqual(safe_divide(10, 0), 0.0)
        self.assertEqual(safe_divide(10, 0, default=999), 999)
    
    def test_calculate_percentage_change(self):
        """Test de cálculo de cambio porcentual"""
        self.assertEqual(calculate_percentage_change(100, 150), 50.0)
        self.assertEqual(calculate_percentage_change(100, 50), -50.0)
        self.assertEqual(calculate_percentage_change(0, 100), 100.0)
    
    def test_sanitize_filename(self):
        """Test de sanitización de nombres de archivo"""
        self.assertEqual(sanitize_filename("file<name>.txt"), "file_name_.txt")
        self.assertEqual(sanitize_filename("test/file.txt"), "test_file.txt")
    
    def test_generate_sku(self):
        """Test de generación de SKU"""
        sku = generate_sku("Electronics", 1)
        self.assertTrue(sku.startswith("ELE"))
        self.assertIn("00001", sku)

if __name__ == '__main__':
    unittest.main()

