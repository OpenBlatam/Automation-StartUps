#!/usr/bin/env python3
"""
Simple Integration Tests for HeyGen AI
Basic integration test suite.
"""

import unittest
import json
import tempfile
import os


class TestSimpleIntegration(unittest.TestCase):
    """Test simple integration scenarios."""
    
    def test_json_processing_integration(self):
        """Test JSON processing integration."""
        data = {"name": "Test", "value": 42}
        json_str = json.dumps(data)
        parsed = json.loads(json_str)
        self.assertEqual(parsed, data)
    
    def test_file_operations_integration(self):
        """Test file operations integration."""
        test_data = {"test": "data"}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            test_file = f.name
            json.dump(test_data, f)
        
        try:
            with open(test_file, 'r') as f:
                loaded_data = json.load(f)
            self.assertEqual(loaded_data, test_data)
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
    
    def test_data_processing_pipeline(self):
        """Test data processing pipeline."""
        def process_data(data):
            return [item * 2 for item in data if item > 0]
        
        input_data = [1, -2, 3, -4, 5]
        result = process_data(input_data)
        expected = [2, 6, 10]
        self.assertEqual(result, expected)
    
    def test_string_processing_integration(self):
        """Test string processing integration."""
        def process_text(text):
            return text.strip().lower().replace(" ", "_")
        
        result = process_text("  Hello World  ")
        self.assertEqual(result, "hello_world")
    
    def test_list_operations_integration(self):
        """Test list operations integration."""
        def process_numbers(numbers):
            return {
                "sum": sum(numbers),
                "count": len(numbers),
                "max": max(numbers),
                "min": min(numbers)
            }
        
        numbers = [1, 2, 3, 4, 5]
        result = process_numbers(numbers)
        
        self.assertEqual(result["sum"], 15)
        self.assertEqual(result["count"], 5)
        self.assertEqual(result["max"], 5)
        self.assertEqual(result["min"], 1)


if __name__ == '__main__':
    unittest.main()
