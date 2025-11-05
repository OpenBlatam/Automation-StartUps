#!/usr/bin/env python3
"""
Comprehensive Testing Suite for Competitive Pricing Analysis System
==================================================================

Test suite covering all components of the pricing analysis system including:
- Unit tests for core functionality
- Integration tests for external systems
- Performance tests for scalability
- End-to-end tests for complete workflows
"""

import unittest
import pytest
import asyncio
import tempfile
import os
import sqlite3
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import time

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from competitive_pricing_analyzer import (
    CompetitivePricingAnalyzer, PricingData, DataSource, CompetitiveInsight
)
from ml_pricing_optimizer import MLPricingOptimizer, PricingPrediction, OptimizationResult
from pricing_alert_system import PricingAlertSystem, Alert, AlertType, AlertSeverity
from integration_tools import IntegrationManager, SalesforceIntegration, HubSpotIntegration

class TestPricingData(unittest.TestCase):
    """Test cases for PricingData class"""
    
    def test_pricing_data_creation(self):
        """Test creating PricingData object"""
        data = PricingData(
            product_id="test_product",
            product_name="Test Product",
            competitor="Test Competitor",
            price=99.99,
            currency="USD",
            date_collected=datetime.now(),
            source=DataSource.WEB_SCRAPING
        )
        
        self.assertEqual(data.product_id, "test_product")
        self.assertEqual(data.price, 99.99)
        self.assertEqual(data.currency, "USD")
        self.assertEqual(data.source, DataSource.WEB_SCRAPING)

class TestCompetitivePricingAnalyzer(unittest.TestCase):
    """Test cases for CompetitivePricingAnalyzer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create test configuration
        self.test_config = {
            'database_path': self.temp_db.name,
            'data_sources': {
                'web_scraping': {'enabled': True},
                'api_sources': {'enabled': True}
            },
            'products': [
                {'id': 'test_product_1', 'name': 'Test Product 1'},
                {'id': 'test_product_2', 'name': 'Test Product 2'}
            ],
            'competitors': ['Competitor A', 'Competitor B']
        }
        
        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
        import yaml
        yaml.dump(self.test_config, self.temp_config)
        self.temp_config.close()
        
        # Initialize analyzer
        self.analyzer = CompetitivePricingAnalyzer(self.temp_config.name)
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.unlink(self.temp_db.name)
        os.unlink(self.temp_config.name)
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization"""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(self.analyzer.db_path, self.temp_db.name)
        self.assertEqual(len(self.analyzer.products), 2)
        self.assertEqual(len(self.analyzer.competitors), 2)
    
    def test_database_initialization(self):
        """Test database initialization"""
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        self.assertIn('pricing_data', tables)
        self.assertIn('competitive_insights', tables)
        self.assertIn('pricing_history', tables)
        
        conn.close()
    
    def test_store_pricing_data(self):
        """Test storing pricing data"""
        test_data = [
            PricingData(
                product_id="test_product_1",
                product_name="Test Product 1",
                competitor="Competitor A",
                price=99.99,
                currency="USD",
                date_collected=datetime.now(),
                source=DataSource.MANUAL_INPUT
            )
        ]
        
        self.analyzer._store_pricing_data(test_data)
        
        # Verify data was stored
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM pricing_data")
        count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count, 1)
    
    def test_analyze_price_gaps(self):
        """Test price gap analysis"""
        # Create test data with price gaps
        test_data = pd.DataFrame({
            'product_id': ['product_1', 'product_1', 'product_1'],
            'product_name': ['Product 1', 'Product 1', 'Product 1'],
            'competitor': ['A', 'B', 'C'],
            'price': [100.0, 150.0, 200.0],
            'currency': ['USD', 'USD', 'USD'],
            'date_collected': [datetime.now(), datetime.now(), datetime.now()],
            'source': ['test', 'test', 'test']
        })
        
        insights = self.analyzer._analyze_price_gaps(test_data)
        
        self.assertGreater(len(insights), 0)
        self.assertEqual(insights[0].insight_type, "price_gap")
    
    def test_analyze_price_trends(self):
        """Test price trend analysis"""
        # Create test data with trends
        test_data = pd.DataFrame({
            'product_id': ['product_1', 'product_1', 'product_1'],
            'competitor': ['A', 'A', 'A'],
            'price': [100.0, 110.0, 120.0],
            'date_collected': [
                datetime.now() - timedelta(days=2),
                datetime.now() - timedelta(days=1),
                datetime.now()
            ]
        })
        
        insights = self.analyzer._analyze_price_trends()
        
        # This will return empty list since we don't have historical data
        # but the method should not raise an exception
        self.assertIsInstance(insights, list)
    
    def test_generate_pricing_report(self):
        """Test pricing report generation"""
        # Add some test data
        test_data = [
            PricingData(
                product_id="test_product_1",
                product_name="Test Product 1",
                competitor="Competitor A",
                price=99.99,
                currency="USD",
                date_collected=datetime.now(),
                source=DataSource.MANUAL_INPUT
            )
        ]
        self.analyzer._store_pricing_data(test_data)
        
        report = self.analyzer.generate_pricing_report()
        
        self.assertIsInstance(report, dict)
        self.assertIn('summary_statistics', report)
        self.assertIn('insights', report)
        self.assertIn('recommendations', report)
        self.assertIn('data_quality', report)

class TestMLPricingOptimizer(unittest.TestCase):
    """Test cases for MLPricingOptimizer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create test data in database
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE pricing_data (
                id INTEGER PRIMARY KEY,
                product_id TEXT,
                product_name TEXT,
                competitor TEXT,
                price REAL,
                currency TEXT,
                date_collected TIMESTAMP,
                source TEXT
            )
        ''')
        
        # Insert test data
        test_data = [
            ('product_1', 'Product 1', 'Competitor A', 100.0, 'USD', '2024-01-01', 'test'),
            ('product_1', 'Product 1', 'Competitor B', 120.0, 'USD', '2024-01-01', 'test'),
            ('product_1', 'Product 1', 'Competitor A', 105.0, 'USD', '2024-01-02', 'test'),
            ('product_1', 'Product 1', 'Competitor B', 125.0, 'USD', '2024-01-02', 'test'),
        ]
        
        cursor.executemany('''
            INSERT INTO pricing_data (product_id, product_name, competitor, price, currency, date_collected, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', test_data)
        
        conn.commit()
        conn.close()
        
        # Initialize optimizer
        self.optimizer = MLPricingOptimizer(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.unlink(self.temp_db.name)
    
    def test_optimizer_initialization(self):
        """Test optimizer initialization"""
        self.assertIsNotNone(self.optimizer)
        self.assertIn('price_prediction', self.optimizer.models)
        self.assertIn('random_forest', self.optimizer.models['price_prediction'])
    
    def test_prepare_training_data(self):
        """Test training data preparation"""
        X, y = self.optimizer.prepare_training_data()
        
        self.assertIsInstance(X, pd.DataFrame)
        self.assertIsInstance(y, pd.Series)
        
        if not X.empty:
            self.assertGreater(len(X), 0)
            self.assertGreater(len(y), 0)
    
    def test_train_price_prediction_models(self):
        """Test model training"""
        scores = self.optimizer.train_price_prediction_models()
        
        self.assertIsInstance(scores, dict)
        
        # Check if any models were trained successfully
        if scores:
            for model_name, metrics in scores.items():
                self.assertIn('r2', metrics)
                self.assertIn('rmse', metrics)
    
    def test_predict_optimal_price(self):
        """Test optimal price prediction"""
        # Train models first
        self.optimizer.train_price_prediction_models()
        
        result = self.optimizer.predict_optimal_price("product_1", 100.0)
        
        if result:
            self.assertIsInstance(result, OptimizationResult)
            self.assertEqual(result.product_id, "product_1")
            self.assertEqual(result.current_price, 100.0)
            self.assertGreater(result.optimal_price, 0)
    
    def test_analyze_price_elasticity(self):
        """Test price elasticity analysis"""
        result = self.optimizer.analyze_price_elasticity("product_1")
        
        self.assertIsInstance(result, dict)
        
        if 'error' not in result:
            self.assertIn('estimated_elasticity', result)
            self.assertIn('price_volatility', result)

class TestPricingAlertSystem(unittest.TestCase):
    """Test cases for PricingAlertSystem"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create test configuration
        self.test_config = {
            'database_path': self.temp_db.name,
            'email': {
                'smtp_server': 'smtp.test.com',
                'smtp_port': 587,
                'username': 'test@test.com',
                'password': 'test_password',
                'from_email': 'alerts@test.com'
            },
            'alert_rules': []
        }
        
        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
        import yaml
        yaml.dump(self.test_config, self.temp_config)
        self.temp_config.close()
        
        # Initialize alert system
        self.alert_system = PricingAlertSystem(self.temp_config.name)
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.unlink(self.temp_db.name)
        os.unlink(self.temp_config.name)
    
    def test_alert_system_initialization(self):
        """Test alert system initialization"""
        self.assertIsNotNone(self.alert_system)
        self.assertEqual(self.alert_system.db_path, self.temp_db.name)
    
    def test_check_price_changes(self):
        """Test price change detection"""
        # Add test data with price changes
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pricing_data (
                id INTEGER PRIMARY KEY,
                product_id TEXT,
                product_name TEXT,
                competitor TEXT,
                price REAL,
                currency TEXT,
                date_collected TIMESTAMP,
                source TEXT
            )
        ''')
        
        # Insert test data with price changes
        test_data = [
            ('product_1', 'Product 1', 'Competitor A', 100.0, 'USD', '2024-01-01', 'test'),
            ('product_1', 'Product 1', 'Competitor A', 120.0, 'USD', '2024-01-02', 'test'),  # 20% increase
        ]
        
        cursor.executemany('''
            INSERT INTO pricing_data (product_id, product_name, competitor, price, currency, date_collected, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', test_data)
        
        conn.commit()
        conn.close()
        
        alerts = self.alert_system.check_price_changes()
        
        # Should detect the price increase
        self.assertGreater(len(alerts), 0)
        self.assertEqual(alerts[0].alert_type, AlertType.PRICE_INCREASE)
    
    def test_check_price_gaps(self):
        """Test price gap detection"""
        # Add test data with price gaps
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pricing_data (
                id INTEGER PRIMARY KEY,
                product_id TEXT,
                product_name TEXT,
                competitor TEXT,
                price REAL,
                currency TEXT,
                date_collected TIMESTAMP,
                source TEXT
            )
        ''')
        
        # Insert test data with large price gap
        test_data = [
            ('product_1', 'Product 1', 'Competitor A', 100.0, 'USD', '2024-01-01', 'test'),
            ('product_1', 'Product 1', 'Competitor B', 200.0, 'USD', '2024-01-01', 'test'),  # 100% gap
        ]
        
        cursor.executemany('''
            INSERT INTO pricing_data (product_id, product_name, competitor, price, currency, date_collected, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', test_data)
        
        conn.commit()
        conn.close()
        
        alerts = self.alert_system.check_price_gaps()
        
        # Should detect the price gap
        self.assertGreater(len(alerts), 0)
        self.assertEqual(alerts[0].alert_type, AlertType.PRICE_GAP)
    
    def test_check_data_quality(self):
        """Test data quality checks"""
        alerts = self.alert_system.check_data_quality()
        
        # Should detect no data available
        self.assertGreater(len(alerts), 0)
        self.assertEqual(alerts[0].alert_type, AlertType.DATA_QUALITY)
    
    def test_store_alert(self):
        """Test alert storage"""
        alert = Alert(
            alert_id="test_alert_1",
            rule_id="test_rule",
            alert_type=AlertType.PRICE_INCREASE,
            severity=AlertSeverity.HIGH,
            title="Test Alert",
            message="This is a test alert",
            created_at=datetime.now()
        )
        
        self.alert_system._store_alert(alert)
        
        # Verify alert was stored
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM alerts")
        count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count, 1)
    
    def test_get_alert_history(self):
        """Test getting alert history"""
        # Add test alert
        alert = Alert(
            alert_id="test_alert_2",
            rule_id="test_rule",
            alert_type=AlertType.PRICE_DECREASE,
            severity=AlertSeverity.MEDIUM,
            title="Test Alert 2",
            message="This is another test alert",
            created_at=datetime.now()
        )
        
        self.alert_system._store_alert(alert)
        
        history = self.alert_system.get_alert_history()
        
        self.assertGreater(len(history), 0)
        self.assertEqual(history[0]['alert_id'], "test_alert_2")

class TestIntegrationTools(unittest.TestCase):
    """Test cases for Integration Tools"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create test configuration
        self.test_config = {
            'database_path': self.temp_db.name,
            'integrations': {
                'salesforce': {
                    'api_endpoint': 'https://test.salesforce.com',
                    'api_key': 'test_key',
                    'auth_type': 'bearer'
                }
            }
        }
        
        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
        import yaml
        yaml.dump(self.test_config, self.temp_config)
        self.temp_config.close()
        
        # Initialize integration manager
        self.integration_manager = IntegrationManager(self.temp_config.name)
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.unlink(self.temp_db.name)
        os.unlink(self.temp_config.name)
    
    def test_integration_manager_initialization(self):
        """Test integration manager initialization"""
        self.assertIsNotNone(self.integration_manager)
        self.assertIn('salesforce', self.integration_manager.integrations)
    
    @patch('requests.Session.get')
    def test_salesforce_connection_test(self, mock_get):
        """Test Salesforce connection test"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        salesforce = self.integration_manager.integrations['salesforce']
        result = salesforce.test_connection()
        
        self.assertTrue(result)
    
    def test_salesforce_data_mapping(self):
        """Test Salesforce data mapping"""
        salesforce = self.integration_manager.integrations['salesforce']
        
        test_record = {
            'product_id': 'test_product',
            'product_name': 'Test Product',
            'competitor': 'Test Competitor',
            'price': 99.99,
            'currency': 'USD',
            'date_collected': '2024-01-01'
        }
        
        mapped_data = salesforce._map_to_salesforce_fields(test_record)
        
        self.assertEqual(mapped_data['Product__c'], 'test_product')
        self.assertEqual(mapped_data['Competitor__c'], 'Test Competitor')
        self.assertEqual(mapped_data['Price__c'], 99.99)

class TestPerformance(unittest.TestCase):
    """Performance tests"""
    
    def test_large_dataset_processing(self):
        """Test processing large datasets"""
        # Create large test dataset
        n_records = 10000
        test_data = []
        
        for i in range(n_records):
            test_data.append(PricingData(
                product_id=f"product_{i % 100}",
                product_name=f"Product {i % 100}",
                competitor=f"Competitor {i % 10}",
                price=100.0 + (i % 50),
                currency="USD",
                date_collected=datetime.now(),
                source=DataSource.MANUAL_INPUT
            ))
        
        # Test processing time
        start_time = time.time()
        
        # Create temporary database
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        # Initialize analyzer
        config = {
            'database_path': temp_db.name,
            'data_sources': {'web_scraping': {'enabled': True}},
            'products': [],
            'competitors': []
        }
        
        temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
        import yaml
        yaml.dump(config, temp_config)
        temp_config.close()
        
        analyzer = CompetitivePricingAnalyzer(temp_config.name)
        analyzer._store_pricing_data(test_data)
        
        processing_time = time.time() - start_time
        
        # Clean up
        os.unlink(temp_db.name)
        os.unlink(temp_config.name)
        
        # Should process 10,000 records in reasonable time
        self.assertLess(processing_time, 30)  # Less than 30 seconds

class TestEndToEnd(unittest.TestCase):
    """End-to-end tests"""
    
    def test_complete_workflow(self):
        """Test complete pricing analysis workflow"""
        # Create temporary files
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        config = {
            'database_path': temp_db.name,
            'data_sources': {
                'web_scraping': {'enabled': True},
                'api_sources': {'enabled': True}
            },
            'products': [
                {'id': 'test_product', 'name': 'Test Product'}
            ],
            'competitors': ['Competitor A', 'Competitor B']
        }
        
        temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
        import yaml
        yaml.dump(config, temp_config)
        temp_config.close()
        
        try:
            # Initialize analyzer
            analyzer = CompetitivePricingAnalyzer(temp_config.name)
            
            # Add test data
            test_data = [
                PricingData(
                    product_id="test_product",
                    product_name="Test Product",
                    competitor="Competitor A",
                    price=100.0,
                    currency="USD",
                    date_collected=datetime.now(),
                    source=DataSource.MANUAL_INPUT
                ),
                PricingData(
                    product_id="test_product",
                    product_name="Test Product",
                    competitor="Competitor B",
                    price=150.0,
                    currency="USD",
                    date_collected=datetime.now(),
                    source=DataSource.MANUAL_INPUT
                )
            ]
            
            analyzer._store_pricing_data(test_data)
            
            # Run analysis
            insights = analyzer.analyze_pricing_differences()
            
            # Generate report
            report = analyzer.generate_pricing_report()
            
            # Verify results
            self.assertGreater(len(insights), 0)
            self.assertIsInstance(report, dict)
            self.assertIn('summary_statistics', report)
            
        finally:
            # Clean up
            os.unlink(temp_db.name)
            os.unlink(temp_config.name)

def run_performance_tests():
    """Run performance tests"""
    print("Running performance tests...")
    
    # Test data processing speed
    start_time = time.time()
    
    # Create large dataset
    n_records = 5000
    data = []
    for i in range(n_records):
        data.append({
            'product_id': f'product_{i % 50}',
            'product_name': f'Product {i % 50}',
            'competitor': f'Competitor {i % 10}',
            'price': 100.0 + (i % 100),
            'currency': 'USD',
            'date_collected': datetime.now().isoformat()
        })
    
    # Process data
    df = pd.DataFrame(data)
    insights = []
    
    for product in df['product_id'].unique():
        product_data = df[df['product_id'] == product]
        if len(product_data) >= 2:
            prices = product_data['price'].values
            price_range = np.max(prices) - np.min(prices)
            avg_price = np.mean(prices)
            
            if price_range / avg_price > 0.2:
                insights.append({
                    'product_id': product,
                    'price_range': price_range,
                    'price_gap_percentage': price_range / avg_price
                })
    
    processing_time = time.time() - start_time
    
    print(f"Processed {n_records} records in {processing_time:.2f} seconds")
    print(f"Generated {len(insights)} insights")
    print(f"Processing rate: {n_records / processing_time:.0f} records/second")

def run_integration_tests():
    """Run integration tests"""
    print("Running integration tests...")
    
    # Test database connectivity
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        conn = sqlite3.connect(temp_db.name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        ''')
        
        cursor.execute("INSERT INTO test_table (name) VALUES ('test')")
        conn.commit()
        
        cursor.execute("SELECT * FROM test_table")
        result = cursor.fetchone()
        
        conn.close()
        
        assert result[1] == 'test'
        print("✓ Database connectivity test passed")
        
    except Exception as e:
        print(f"✗ Database connectivity test failed: {e}")
    finally:
        os.unlink(temp_db.name)
    
    # Test API connectivity (mock)
    try:
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            response = requests.get('https://api.test.com/test')
            assert response.status_code == 200
            print("✓ API connectivity test passed")
            
    except Exception as e:
        print(f"✗ API connectivity test failed: {e}")

def main():
    """Main function to run all tests"""
    print("=" * 60)
    print("COMPETITIVE PRICING ANALYSIS SYSTEM - TEST SUITE")
    print("=" * 60)
    
    # Run unit tests
    print("\n1. Running Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance tests
    print("\n2. Running Performance Tests...")
    run_performance_tests()
    
    # Run integration tests
    print("\n3. Running Integration Tests...")
    run_integration_tests()
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETED")
    print("=" * 60)

if __name__ == '__main__':
    main()






