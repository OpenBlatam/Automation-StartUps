#!/usr/bin/env python3
"""
Tests para Analytics, Workflows y Reportes

Este test suite valida:
- AnalyticsAnalyzer: análisis de métricas y health scores
- WorkflowTester: testing de webhooks y workflows
- ReportGenerator: generación de reportes ejecutivos
- CustomerAutomationHelper: integración y automatización de clientes

Usage:
    pytest tests/test_analytics_and_workflows.py -v
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Importar módulos a testear
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "n8n" / "scripts"))

from analytics_analyzer import AnalyticsAnalyzer
from workflow_tester import WorkflowTester
from report_generator import ReportGenerator
from integration_helper import CustomerAutomationHelper


class TestAnalyticsAnalyzer:
    """Tests para AnalyticsAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Crea instancia del analizador"""
        return AnalyticsAnalyzer(
            api_base_url="https://test-api.com",
            api_key="test_key"
        )
    
    def test_analyzer_initialization(self, analyzer):
        """Verifica inicialización correcta"""
        assert analyzer.api_base_url == "https://test-api.com"
        assert analyzer.api_key == "test_key"
        assert "X-API-Key" in analyzer.headers
    
    @patch('analytics_analyzer.requests.get')
    def test_get_performance_data(self, mock_get, analyzer):
        """Verifica obtención de datos de performance"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "totalEvents": 1000,
            "successRate": 95.5
        }
        mock_get.return_value = mock_response
        
        result = analyzer.get_performance_data("7d")
        
        assert mock_get.called
        assert result["totalEvents"] == 1000
        assert result["successRate"] == 95.5
    
    def test_calculate_health_score_excellent(self, analyzer):
        """Verifica cálculo de health score excelente"""
        metrics = {
            "cartAbandonmentRate": 50,
            "emailOpenRate": 30,
            "emailClickRate": 10,
            "conversionRate": 20,
            "recoveryRate": 40
        }
        
        result = analyzer.calculate_health_score(metrics)
        
        assert result["score"] >= 80
        assert result["status"] == "excellent"
        assert isinstance(result["issues"], list)
    
    def test_calculate_health_score_poor(self, analyzer):
        """Verifica cálculo de health score pobre"""
        metrics = {
            "cartAbandonmentRate": 90,
            "emailOpenRate": 10,
            "emailClickRate": 2,
            "conversionRate": 5,
            "recoveryRate": 10
        }
        
        result = analyzer.calculate_health_score(metrics)
        
        assert result["score"] < 40
        assert result["status"] == "poor"
        assert len(result["issues"]) > 0
    
    def test_calculate_health_score_boundaries(self, analyzer):
        """Verifica que el score esté en rango 0-100"""
        metrics = {
            "cartAbandonmentRate": 0,
            "emailOpenRate": 100,
            "emailClickRate": 100,
            "conversionRate": 100,
            "recoveryRate": 100
        }
        
        result = analyzer.calculate_health_score(metrics)
        assert 0 <= result["score"] <= 100
    
    def test_analyze_trends_improving(self, analyzer):
        """Verifica análisis de tendencias mejorando"""
        current = {
            "cartAbandonmentRate": 60,
            "emailOpenRate": 30,
            "conversionRate": 20
        }
        previous = {
            "cartAbandonmentRate": 70,
            "emailOpenRate": 25,
            "conversionRate": 15
        }
        
        trends = analyzer.analyze_trends(current, previous)
        
        assert "cartAbandonmentRate" in trends
        # cartAbandonmentRate disminuyendo es "down" (mejor)
        assert trends["cartAbandonmentRate"]["direction"] == "down"
        # emailOpenRate y conversionRate aumentando es "up" (mejor)
        assert trends["emailOpenRate"]["direction"] == "up"
        assert trends["conversionRate"]["direction"] == "up"
    
    def test_analyze_trends_declining(self, analyzer):
        """Verifica análisis de tendencias empeorando"""
        current = {
            "cartAbandonmentRate": 80,
            "emailOpenRate": 20,
            "conversionRate": 10
        }
        previous = {
            "cartAbandonmentRate": 70,
            "emailOpenRate": 25,
            "conversionRate": 15
        }
        
        trends = analyzer.analyze_trends(current, previous)
        
        # cartAbandonmentRate aumentando es "up" (peor)
        assert trends["cartAbandonmentRate"]["direction"] == "up"
        # emailOpenRate y conversionRate disminuyendo es "down" (peor)
        assert trends["emailOpenRate"]["direction"] == "down"
        assert trends["conversionRate"]["direction"] == "down"
    
    def test_analyze_trends_stable(self, analyzer):
        """Verifica análisis de tendencias estables"""
        current = {
            "cartAbandonmentRate": 70,
            "emailOpenRate": 25,
            "conversionRate": 15
        }
        previous = {
            "cartAbandonmentRate": 70,
            "emailOpenRate": 25,
            "conversionRate": 15
        }
        
        trends = analyzer.analyze_trends(current, previous)
        
        assert trends["cartAbandonmentRate"]["direction"] == "stable"
    
    def test_health_score_status_levels(self, analyzer):
        """Verifica todos los niveles de status"""
        # Test excellent (score >= 80)
        excellent_metrics = {
            "cartAbandonmentRate": 50,
            "emailOpenRate": 30,
            "emailClickRate": 10,
            "conversionRate": 20,
            "recoveryRate": 40
        }
        result = analyzer.calculate_health_score(excellent_metrics)
        assert result["status"] == "excellent"
        assert result["score"] >= 80
        
        # Test good (score >= 60, < 80)
        # Necesitamos restar entre 20-40 puntos del score inicial de 100
        # cartAbandonmentRate > 70: -10, emailOpenRate < 25: -8, emailClickRate < 8: -8, conversionRate < 15: -10, recoveryRate < 35: -8
        # Total: -44 puntos = 56 (fair). Necesitamos menos penalizaciones
        # cartAbandonmentRate <= 70: 0, emailOpenRate >= 25: 0, emailClickRate >= 8: 0, conversionRate >= 15: 0, recoveryRate >= 35: 0
        # Para good, necesitamos algunas penalizaciones moderadas
        good_metrics = {
            "cartAbandonmentRate": 68,  # <= 70, no penalty
            "emailOpenRate": 24,  # < 25, -8 puntos
            "emailClickRate": 7,  # < 8, -8 puntos
            "conversionRate": 14,  # < 15, -10 puntos
            "recoveryRate": 34  # < 35, -8 puntos
        }
        result = analyzer.calculate_health_score(good_metrics)
        # Total: -34 puntos = 66 (good)
        assert result["status"] == "good"
        assert 60 <= result["score"] < 80
        
        # Test fair (score >= 40)
        fair_metrics = {
            "cartAbandonmentRate": 75,
            "emailOpenRate": 20,
            "emailClickRate": 5,
            "conversionRate": 12,
            "recoveryRate": 30
        }
        result = analyzer.calculate_health_score(fair_metrics)
        assert result["status"] == "fair"
        assert 40 <= result["score"] < 60
        
        # Test poor (score < 40)
        poor_metrics = {
            "cartAbandonmentRate": 90,
            "emailOpenRate": 10,
            "emailClickRate": 2,
            "conversionRate": 5,
            "recoveryRate": 10
        }
        result = analyzer.calculate_health_score(poor_metrics)
        assert result["status"] == "poor"
        assert result["score"] < 40


class TestWorkflowTester:
    """Tests para WorkflowTester"""
    
    @pytest.fixture
    def tester(self):
        """Crea instancia del tester"""
        return WorkflowTester(
            api_base_url="https://test-api.com",
            api_key="test_key"
        )
    
    def test_tester_initialization(self, tester):
        """Verifica inicialización correcta"""
        assert tester.api_base_url == "https://test-api.com"
        assert tester.api_key == "test_key"
        assert tester.test_results == []
    
    @patch('workflow_tester.requests.post')
    def test_test_cart_abandonment_webhook_success(self, mock_post, tester):
        """Verifica test de webhook de carrito abandonado exitoso"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.headers = {"content-type": "application/json"}
        mock_post.return_value = mock_response
        
        result = tester.test_cart_abandonment_webhook()
        
        assert result["status"] == "success"
        assert result["status_code"] == 200
        assert result["test"] == "cart_abandonment_webhook"
        assert "timestamp" in result
        assert len(tester.test_results) == 1
    
    @patch('workflow_tester.requests.post')
    def test_test_cart_abandonment_webhook_failure(self, mock_post, tester):
        """Verifica test de webhook con error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal error"}
        mock_response.headers = {"content-type": "application/json"}
        mock_post.return_value = mock_response
        
        result = tester.test_cart_abandonment_webhook()
        
        assert result["status"] == "failed"
        assert result["status_code"] == 500
    
    @patch('workflow_tester.requests.post')
    def test_test_cart_abandonment_webhook_exception(self, mock_post, tester):
        """Verifica manejo de excepciones en test"""
        mock_post.side_effect = Exception("Connection error")
        
        result = tester.test_cart_abandonment_webhook()
        
        assert result["status"] == "error"
        assert "error" in result
        assert "Connection error" in result["error"]
    
    @patch('workflow_tester.requests.post')
    def test_test_page_visit_webhook(self, mock_post, tester):
        """Verifica test de webhook de visita a página"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.headers = {"content-type": "application/json"}
        mock_post.return_value = mock_response
        
        result = tester.test_page_visit_webhook()
        
        assert result["status"] == "success"
        assert result["test"] == "page_visit_webhook"
    
    @patch('workflow_tester.requests.post')
    def test_test_cart_abandonment_custom_data(self, mock_post, tester):
        """Verifica test con datos personalizados"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.headers = {"content-type": "application/json"}
        mock_post.return_value = mock_response
        
        custom_data = {
            "eventType": "cart_abandonment",
            "customerId": "custom_customer",
            "email": "custom@test.com",
            "cartValue": 200.00
        }
        
        result = tester.test_cart_abandonment_webhook(custom_data)
        
        assert mock_post.called
        call_payload = mock_post.call_args[1]["json"]
        assert call_payload["customerId"] == "custom_customer"
        assert call_payload["cartValue"] == 200.00
    
    def test_test_results_accumulation(self, tester):
        """Verifica que los resultados se acumulen"""
        with patch('workflow_tester.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "success"}
            mock_response.headers = {"content-type": "application/json"}
            mock_post.return_value = mock_response
            
            tester.test_cart_abandonment_webhook()
            tester.test_page_visit_webhook()
            
            assert len(tester.test_results) == 2


class TestReportGenerator:
    """Tests para ReportGenerator"""
    
    @pytest.fixture
    def generator(self):
        """Crea instancia del generador"""
        return ReportGenerator(
            api_base_url="https://test-api.com",
            api_key="test_key"
        )
    
    def test_generator_initialization(self, generator):
        """Verifica inicialización correcta"""
        assert generator.api_base_url == "https://test-api.com"
        assert generator.api_key == "test_key"
    
    @patch('report_generator.requests.get')
    def test_fetch_all_metrics(self, mock_get, generator):
        """Verifica obtención de todas las métricas"""
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response
        
        metrics = generator.fetch_all_metrics("30d")
        
        assert "cartAbandonment" in metrics
        assert "email" in metrics
        assert "conversion" in metrics
        assert "abTesting" in metrics
    
    @patch('report_generator.requests.get')
    def test_fetch_all_metrics_with_errors(self, mock_get, generator):
        """Verifica manejo de errores al obtener métricas"""
        mock_get.side_effect = [Exception("Error"), Mock(json=lambda: {"data": "test"})]
        
        metrics = generator.fetch_all_metrics()
        
        # Debe manejar errores gracefully
        assert isinstance(metrics, dict)
    
    def test_generate_executive_summary_structure(self, generator):
        """Verifica estructura del resumen ejecutivo"""
        metrics = {
            "cartAbandonment": {
                "cartAbandonmentRate": 70,
                "recoveryRate": 35,
                "recoveredValue": 5000
            },
            "email": {
                "openRate": 25,
                "clickRate": 8
            },
            "conversion": {
                "conversionRate": 15,
                "revenue": 10000,
                "averageOrderValue": 100
            },
            "abTesting": {}
        }
        
        summary = generator.generate_executive_summary(metrics)
        
        assert "period" in summary
        assert "generatedAt" in summary
        assert "keyMetrics" in summary
        assert "insights" in summary
        assert "recommendations" in summary
        
        assert summary["keyMetrics"]["cartAbandonmentRate"] == 70
        assert summary["keyMetrics"]["recoveryRate"] == 35
        assert summary["keyMetrics"]["emailOpenRate"] == 25
    
    def test_generate_executive_summary_insights(self, generator):
        """Verifica generación de insights"""
        metrics = {
            "cartAbandonment": {
                "cartAbandonmentRate": 70,
                "recoveryRate": 45,  # Alta tasa de recuperación
                "recoveredValue": 5000
            },
            "email": {
                "openRate": 30,  # Buena tasa de apertura
                "clickRate": 10
            },
            "conversion": {
                "conversionRate": 20,  # Buena conversión
                "revenue": 10000,
                "averageOrderValue": 100
            },
            "abTesting": {}
        }
        
        summary = generator.generate_executive_summary(metrics)
        
        assert len(summary["insights"]) > 0
        assert isinstance(summary["insights"], list)
    
    def test_generate_executive_summary_recommendations(self, generator):
        """Verifica generación de recomendaciones"""
        metrics = {
            "cartAbandonment": {
                "cartAbandonmentRate": 85,  # Muy alta
                "recoveryRate": 20,  # Baja
                "recoveredValue": 2000
            },
            "email": {
                "openRate": 15,  # Baja
                "clickRate": 3  # Muy baja
            },
            "conversion": {
                "conversionRate": 8,  # Baja
                "revenue": 5000,
                "averageOrderValue": 80
            },
            "abTesting": {}
        }
        
        summary = generator.generate_executive_summary(metrics)
        
        assert len(summary["recommendations"]) > 0
        assert isinstance(summary["recommendations"], list)


class TestCustomerAutomationHelper:
    """Tests para CustomerAutomationHelper"""
    
    @pytest.fixture
    def helper(self):
        """Crea instancia del helper"""
        return CustomerAutomationHelper(
            api_base_url="https://test-api.com",
            api_key="test_key"
        )
    
    @pytest.fixture
    def customer_data(self):
        """Datos de ejemplo del cliente"""
        return {
            "customer_id": "customer_123",
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "cart_id": "cart_123",
            "cart_value": 150.00,
            "cart_items": [
                {
                    "name": "Product 1",
                    "price": 75.00,
                    "quantity": 2,
                    "category": "electronics"
                }
            ],
            "session_id": "session_123",
            "device": "desktop",
            "browser": "chrome",
            "referrer": "google",
            "utm_source": "google",
            "utm_campaign": "summer_sale"
        }
    
    def test_helper_initialization(self, helper):
        """Verifica inicialización correcta"""
        assert helper.api_base_url == "https://test-api.com"
        assert helper.api_key == "test_key"
        assert "X-API-Key" in helper.headers
    
    @patch('integration_helper.requests.post')
    def test_trigger_cart_abandonment(self, mock_post, helper, customer_data):
        """Verifica activación de workflow de carrito abandonado"""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "triggered", "workflow_id": "wf_123"}
        mock_post.return_value = mock_response
        
        result = helper.trigger_cart_abandonment(customer_data)
        
        assert mock_post.called
        call_url = mock_post.call_args[0][0]
        assert "cart-abandonment" in call_url
        
        payload = mock_post.call_args[1]["json"]
        assert payload["eventType"] == "cart_abandonment"
        assert payload["customerId"] == customer_data["customer_id"]
        assert payload["email"] == customer_data["email"]
        assert payload["cartValue"] == 150.00
        assert len(payload["cartItems"]) == 1
        
        assert result["status"] == "triggered"
    
    @patch('integration_helper.requests.post')
    def test_trigger_page_visit(self, mock_post, helper, customer_data):
        """Verifica activación de workflow de visita a página"""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "triggered"}
        mock_post.return_value = mock_response
        
        page_data = {
            "url": "https://example.com/product/test",
            "category": "product",
            "product_name": "Test Product",
            "session_id": "session_123",
            "time_on_page": 120,
            "pages_viewed": 3
        }
        
        result = helper.trigger_page_visit(customer_data, page_data)
        
        assert mock_post.called
        payload = mock_post.call_args[1]["json"]
        assert payload["eventType"] == "page_visit"
        assert payload["pageUrl"] == page_data["url"]
        assert payload["pageCategory"] == page_data["category"]
        assert payload["productName"] == page_data["product_name"]
    
    @patch('integration_helper.requests.get')
    def test_get_customer_history(self, mock_get, helper):
        """Verifica obtención de historial del cliente"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "customer_id": "customer_123",
            "orders": 5,
            "total_spent": 500.00
        }
        mock_get.return_value = mock_response
        
        result = helper.get_customer_history("customer_123")
        
        assert mock_get.called
        call_url = mock_get.call_args[0][0]
        assert "customer_123" in call_url
        assert result["orders"] == 5
    
    @patch('integration_helper.requests.get')
    def test_get_customer_preferences(self, mock_get, helper):
        """Verifica obtención de preferencias del cliente"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "preferred_categories": ["electronics", "books"],
            "communication_preference": "email"
        }
        mock_get.return_value = mock_response
        
        result = helper.get_customer_preferences("customer_123")
        
        assert "preferred_categories" in result
        assert "electronics" in result["preferred_categories"]
    
    @patch('integration_helper.requests.post')
    def test_track_event(self, mock_post, helper):
        """Verifica registro de eventos"""
        mock_response = Mock()
        mock_response.json.return_value = {"tracked": True, "event_id": "evt_123"}
        mock_post.return_value = mock_response
        
        event_data = {
            "event_type": "purchase",
            "customer_id": "customer_123",
            "value": 99.99
        }
        
        result = helper.track_event(event_data)
        
        assert mock_post.called
        assert result["tracked"] is True
    
    @patch('integration_helper.requests.get')
    def test_get_inactive_customers(self, mock_get, helper):
        """Verifica obtención de clientes inactivos"""
        mock_response = Mock()
        # El método espera un dict con "customers" key
        mock_response.json.return_value = {
            "customers": [
                {"customer_id": "customer_1", "last_activity": "2024-01-01"},
                {"customer_id": "customer_2", "last_activity": "2024-01-02"}
            ]
        }
        mock_get.return_value = mock_response
        
        result = helper.get_inactive_customers(days_inactive=90, limit=100)
        
        assert mock_get.called
        call_params = mock_get.call_args[1]["params"]
        assert call_params["daysInactive"] == 90
        assert call_params["limit"] == 100
        assert len(result) == 2
    
    def test_cart_abandonment_data_transformation(self, helper, customer_data):
        """Verifica transformación correcta de datos"""
        with patch('integration_helper.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"status": "success"}
            mock_post.return_value = mock_response
            
            helper.trigger_cart_abandonment(customer_data)
            
            payload = mock_post.call_args[1]["json"]
            # Verificar tipos de datos
            assert isinstance(payload["cartValue"], float)
            assert isinstance(payload["cartItems"], list)
            assert isinstance(payload["cartItems"][0]["price"], float)
            assert isinstance(payload["cartItems"][0]["quantity"], int)
    
    def test_cart_abandonment_defaults(self, helper):
        """Verifica valores por defecto en carrito abandonado"""
        minimal_data = {
            "customer_id": "customer_123",
            "email": "test@example.com"
        }
        
        with patch('integration_helper.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"status": "success"}
            mock_post.return_value = mock_response
            
            helper.trigger_cart_abandonment(minimal_data)
            
            payload = mock_post.call_args[1]["json"]
            assert payload["cartValue"] == 0.0
            assert payload["cartItems"] == []
            assert payload["device"] == "unknown"
            assert payload["browser"] == "unknown"
            assert payload["referrer"] == "direct"


class TestIntegrationScenarios:
    """Tests de integración entre componentes"""
    
    @pytest.fixture
    def analyzer(self):
        return AnalyticsAnalyzer("https://test-api.com", "test_key")
    
    @pytest.fixture
    def generator(self):
        return ReportGenerator("https://test-api.com", "test_key")
    
    @pytest.fixture
    def helper(self):
        return CustomerAutomationHelper("https://test-api.com", "test_key")
    
    def test_analytics_to_report_flow(self, analyzer, generator):
        """Verifica flujo de analytics a reporte"""
        # Simular obtención de métricas
        with patch('analytics_analyzer.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "cartAbandonmentRate": 70,
                "recoveryRate": 35
            }
            mock_get.return_value = mock_response
            
            metrics = analyzer.get_performance_data("30d")
            
            # Generar reporte con esas métricas
            report_metrics = {
                "cartAbandonment": metrics,
                "email": {"openRate": 25},
                "conversion": {"conversionRate": 15},
                "abTesting": {}
            }
            
            summary = generator.generate_executive_summary(report_metrics)
            
            assert "keyMetrics" in summary
            assert summary["keyMetrics"]["cartAbandonmentRate"] == 70
    
    def test_workflow_to_analytics_flow(self, helper, analyzer):
        """Verifica flujo de workflow a analytics"""
        customer_data = {
            "customer_id": "customer_123",
            "email": "test@example.com",
            "cart_value": 150.00,
            "cart_items": []
        }
        
        with patch('integration_helper.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"status": "triggered"}
            mock_post.return_value = mock_response
            
            # Disparar workflow
            result = helper.trigger_cart_abandonment(customer_data)
            assert result["status"] == "triggered"
            
            # Analizar métricas (simulado)
            metrics = {
                "cartAbandonmentRate": 70,
                "recoveryRate": 35
            }
            health = analyzer.calculate_health_score(metrics)
            
            assert health["score"] >= 0
            assert "status" in health


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

