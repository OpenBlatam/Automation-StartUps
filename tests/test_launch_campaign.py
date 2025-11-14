#!/usr/bin/env python3
"""
Tests para el sistema de Campaña de Lanzamiento de Producto

Este test suite valida:
- Estructura del workflow JSON de launch campaign
- Funcionalidad del LaunchCampaignHelper
- Integración con workflows n8n
- Validación de datos y parámetros
- Manejo de errores

Usage:
    pytest tests/test_launch_campaign.py -v
    pytest tests/test_launch_campaign.py::TestLaunchCampaignHelper -v
"""

import json
import os
import re
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Importar módulos a testear
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "n8n" / "scripts"))

from launch_campaign_helper import LaunchCampaignHelper
from advanced_testing_framework import (
    AdvancedTestingFramework,
    TestType,
    TestVariant,
    TestResult
)


class TestWorkflowStructure:
    """Tests para validar la estructura del workflow de launch campaign"""
    
    @pytest.fixture
    def workflow(self):
        """Carga el workflow JSON"""
        workflow_path = Path(__file__).parent.parent / "n8n" / "n8n_workflow_launch_campaign.json"
        if not workflow_path.exists():
            pytest.skip(f"Workflow file not found: {workflow_path}")
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_workflow_has_name(self, workflow):
        """Verifica que el workflow tenga un nombre"""
        assert "name" in workflow
        assert "Launch Campaign" in workflow["name"] or "launch" in workflow["name"].lower()
    
    def test_workflow_has_nodes(self, workflow):
        """Verifica que el workflow tenga nodos"""
        assert "nodes" in workflow
        assert isinstance(workflow["nodes"], list)
        assert len(workflow["nodes"]) > 0
    
    def test_workflow_has_connections(self, workflow):
        """Verifica que el workflow tenga conexiones"""
        assert "connections" in workflow
        assert isinstance(workflow["connections"], dict)
    
    def test_schedule_triggers_exist(self, workflow):
        """Verifica que existan los triggers programados para los 3 días"""
        schedule_nodes = [
            node for node in workflow["nodes"]
            if node.get("type") == "n8n-nodes-base.scheduleTrigger"
        ]
        
        assert len(schedule_nodes) >= 3, "Debe haber al menos 3 triggers programados"
        
        # Verificar que haya triggers para cada día
        node_names = [node.get("name", "").lower() for node in schedule_nodes]
        assert any("day 1" in name or "monday" in name for name in node_names)
        assert any("day 2" in name or "wednesday" in name for name in node_names)
        assert any("day 3" in name or "friday" in name for name in node_names)
    
    def test_content_preparation_node_exists(self, workflow):
        """Verifica que exista nodo de preparación de contenido"""
        content_nodes = [
            node for node in workflow["nodes"]
            if "content" in node.get("name", "").lower() or
               "prepare" in node.get("name", "").lower()
        ]
        
        assert len(content_nodes) > 0, "Debe haber nodo de preparación de contenido"
    
    def test_platform_nodes_exist(self, workflow):
        """Verifica que existan nodos para cada plataforma"""
        platform_keywords = ["instagram", "facebook", "linkedin", "twitter"]
        platform_nodes = []
        
        for node in workflow["nodes"]:
            node_name = node.get("name", "").lower()
            if any(keyword in node_name for keyword in platform_keywords):
                platform_nodes.append(node)
        
        assert len(platform_nodes) > 0, "Debe haber nodos de plataformas sociales"
    
    def test_all_nodes_have_id(self, workflow):
        """Verifica que todos los nodos tengan ID"""
        for node in workflow["nodes"]:
            assert "id" in node, f"Nodo sin ID: {node.get('name', 'Unknown')}"
            assert node["id"], f"Nodo con ID vacío: {node.get('name', 'Unknown')}"
    
    def test_all_nodes_have_name(self, workflow):
        """Verifica que todos los nodos tengan nombre"""
        for node in workflow["nodes"]:
            assert "name" in node, f"Nodo sin nombre: {node.get('id', 'Unknown')}"
            assert node["name"], f"Nodo con nombre vacío: {node.get('id', 'Unknown')}"
    
    def test_all_nodes_have_type(self, workflow):
        """Verifica que todos los nodos tengan tipo"""
        for node in workflow["nodes"]:
            assert "type" in node, f"Nodo sin tipo: {node.get('name', 'Unknown')}"
            assert node["type"], f"Nodo con tipo vacío: {node.get('name', 'Unknown')}"


class TestLaunchCampaignHelper:
    """Tests para el helper de launch campaign"""
    
    @pytest.fixture
    def helper(self):
        """Crea instancia del helper"""
        return LaunchCampaignHelper(
            n8n_base_url="https://test-n8n.com",
            api_key="test_api_key"
        )
    
    @pytest.fixture
    def product_config(self):
        """Configuración de ejemplo del producto"""
        return {
            "name": "Producto Test",
            "benefits": [
                "Beneficio 1",
                "Beneficio 2",
                "Beneficio 3"
            ],
            "problem": "Problema específico",
            "pain": "Dolor específico",
            "result": "Resultado deseado",
            "area": "Área de aplicación",
            "discount_percentage": 25,
            "normal_price": 199,
            "special_price": 149,
            "bonuses": ["Bonus 1", "Bonus 2"],
            "units_available": 50,
            "cta_link": "https://test.com/launch",
            "platforms": ["instagram", "facebook", "linkedin"],
            "hashtags": ["#Test", "#Producto"]
        }
    
    def test_helper_initialization(self, helper):
        """Verifica inicialización correcta del helper"""
        assert helper.n8n_base_url == "https://test-n8n.com"
        assert helper.api_key == "test_api_key"
        assert "X-API-Key" in helper.headers
        assert helper.headers["X-API-Key"] == "test_api_key"
        assert helper.headers["Content-Type"] == "application/json"
    
    def test_helper_url_normalization(self):
        """Verifica que las URLs se normalicen correctamente"""
        helper1 = LaunchCampaignHelper("https://test.com/", "key")
        helper2 = LaunchCampaignHelper("https://test.com", "key")
        
        assert helper1.n8n_base_url == helper2.n8n_base_url
    
    @patch('launch_campaign_helper.requests.post')
    def test_trigger_day_1_teaser(self, mock_post, helper, product_config):
        """Verifica disparo del Día 1 (Teaser)"""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success", "post_id": "post_123"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = helper.trigger_day_1_teaser(product_config)
        
        assert mock_post.called
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://test-n8n.com/webhook/launch-campaign"
        
        payload = call_args[1]["json"]
        assert payload["campaignDay"] == 1
        assert payload["campaignType"] == "teaser"
        assert payload["productName"] == product_config["name"]
        assert payload["productBenefits"] == product_config["benefits"]
        assert "timestamp" in payload
        
        assert result["status"] == "success"
    
    @patch('launch_campaign_helper.requests.post')
    def test_trigger_day_2_demo(self, mock_post, helper, product_config):
        """Verifica disparo del Día 2 (Demo)"""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success", "post_id": "post_456"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = helper.trigger_day_2_demo(product_config)
        
        assert mock_post.called
        payload = mock_post.call_args[1]["json"]
        assert payload["campaignDay"] == 2
        assert payload["campaignType"] == "demo"
        assert payload["ctaLink"] == product_config["cta_link"]
        assert result["status"] == "success"
    
    @patch('launch_campaign_helper.requests.post')
    def test_trigger_day_3_offer(self, mock_post, helper, product_config):
        """Verifica disparo del Día 3 (Oferta)"""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success", "post_id": "post_789"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = helper.trigger_day_3_offer(product_config)
        
        assert mock_post.called
        payload = mock_post.call_args[1]["json"]
        assert payload["campaignDay"] == 3
        assert payload["campaignType"] == "offer"
        assert payload["discountPercentage"] == product_config["discount_percentage"]
        assert payload["normalPrice"] == product_config["normal_price"]
        assert payload["specialPrice"] == product_config["special_price"]
        assert payload["unitsAvailable"] == product_config["units_available"]
        assert result["status"] == "success"
    
    @patch('launch_campaign_helper.requests.post')
    def test_trigger_day_1_defaults(self, mock_post, helper):
        """Verifica que se usen valores por defecto cuando faltan campos"""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = helper.trigger_day_1_teaser({})
        
        payload = mock_post.call_args[1]["json"]
        assert payload["productName"] == "[NOMBRE PRODUCTO]"
        assert payload["problem"] == "[PROBLEMA ESPECÍFICO]"
        assert payload["platforms"] == ["instagram", "facebook", "linkedin"]
    
    @patch('launch_campaign_helper.requests.post')
    def test_track_social_engagement(self, mock_post, helper):
        """Verifica tracking de engagement en redes sociales"""
        mock_response = Mock()
        mock_response.json.return_value = {"score": 85, "is_lead": True}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = helper.track_social_engagement(
            platform="instagram",
            post_id="post_123",
            engagement_type="comment",
            content="SÍ, quiero ser de los primeros",
            user_id="user_456"
        )
        
        assert mock_post.called
        payload = mock_post.call_args[1]["json"]
        assert payload["platform"] == "instagram"
        assert payload["postId"] == "post_123"
        assert payload["engagementType"] == "comment"
        assert payload["content"] == "SÍ, quiero ser de los primeros"
        assert payload["userId"] == "user_456"
        assert "timestamp" in payload
        
        assert result["score"] == 85
        assert result["is_lead"] is True
    
    @patch('launch_campaign_helper.requests.post')
    def test_track_journey_event(self, mock_post, helper):
        """Verifica tracking de eventos en customer journey"""
        mock_response = Mock()
        mock_response.json.return_value = {"journey_updated": True, "stage": "awareness"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = helper.track_journey_event(
            customer_id="customer_123",
            event_type="page_visit",
            page_category="landing_page",
            page_url="https://test.com/launch"
        )
        
        assert mock_post.called
        payload = mock_post.call_args[1]["json"]
        assert payload["customerId"] == "customer_123"
        assert payload["eventType"] == "page_visit"
        assert payload["pageCategory"] == "landing_page"
        assert payload["pageUrl"] == "https://test.com/launch"
        assert "timestamp" in payload
        
        assert result["journey_updated"] is True
    
    def test_get_campaign_metrics_structure(self, helper):
        """Verifica estructura de métricas de campaña"""
        metrics = helper.get_campaign_metrics()
        
        assert "totalReach" in metrics
        assert "totalEngagements" in metrics
        assert "totalLeads" in metrics
        assert "totalConversions" in metrics
        assert "conversionRate" in metrics
        assert "roi" in metrics
        assert "platforms" in metrics
        assert "byDay" in metrics
        
        assert "instagram" in metrics["platforms"]
        assert "facebook" in metrics["platforms"]
        assert "linkedin" in metrics["platforms"]
        
        assert "day1" in metrics["byDay"]
        assert "day2" in metrics["byDay"]
        assert "day3" in metrics["byDay"]
    
    @patch('launch_campaign_helper.requests.post')
    def test_error_handling_http_error(self, mock_post, helper, product_config):
        """Verifica manejo de errores HTTP"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 500 Error")
        mock_post.return_value = mock_response
        
        with pytest.raises(Exception):
            helper.trigger_day_1_teaser(product_config)
    
    def test_timestamp_in_payloads(self, helper, product_config):
        """Verifica que todos los payloads incluyan timestamp"""
        with patch('launch_campaign_helper.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"status": "success"}
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            
            helper.trigger_day_1_teaser(product_config)
            payload1 = mock_post.call_args[1]["json"]
            assert "timestamp" in payload1
            assert isinstance(payload1["timestamp"], str)
            
            helper.trigger_day_2_demo(product_config)
            payload2 = mock_post.call_args[1]["json"]
            assert "timestamp" in payload2
            
            helper.trigger_day_3_offer(product_config)
            payload3 = mock_post.call_args[1]["json"]
            assert "timestamp" in payload3


class TestAdvancedTestingFramework:
    """Tests para el framework avanzado de testing"""
    
    @pytest.fixture
    def framework(self):
        """Crea instancia del framework"""
        return AdvancedTestingFramework(
            api_base_url="https://test-api.com",
            api_key="test_key"
        )
    
    @pytest.fixture
    def test_variants(self):
        """Variantes de ejemplo para tests"""
        return [
            TestVariant(
                id="control",
                name="Control",
                config={"headline": "Original"},
                traffic_percentage=50.0
            ),
            TestVariant(
                id="variant_a",
                name="Variant A",
                config={"headline": "New Headline"},
                traffic_percentage=50.0
            )
        ]
    
    def test_framework_initialization(self, framework):
        """Verifica inicialización del framework"""
        assert framework.api_base_url == "https://test-api.com"
        assert framework.api_key == "test_key"
        assert "Authorization" in framework.headers
        assert framework.headers["Authorization"] == "Bearer test_key"
    
    def test_create_test_valid(self, framework, test_variants):
        """Verifica creación de test válido"""
        test = framework.create_test(
            test_name="Test Headline",
            test_type=TestType.AB,
            variants=test_variants,
            target_metric="conversion_rate"
        )
        
        assert "test_id" in test
        assert "config" in test
        assert test["config"]["name"] == "Test Headline"
        assert test["config"]["type"] == "ab"
        assert len(test["config"]["variants"]) == 2
        assert test["config"]["status"] == "active"
    
    def test_create_test_invalid_traffic(self, framework):
        """Verifica que se rechacen tests con tráfico inválido"""
        variants = [
            TestVariant(
                id="control",
                name="Control",
                config={},
                traffic_percentage=30.0
            ),
            TestVariant(
                id="variant_a",
                name="Variant A",
                config={},
                traffic_percentage=50.0
            )
        ]
        
        with pytest.raises(ValueError, match="Traffic percentages must sum to 100%"):
            framework.create_test(
                test_name="Invalid Test",
                test_type=TestType.AB,
                variants=variants
            )
    
    def test_assign_variant(self, framework):
        """Verifica asignación de variantes"""
        variant = framework.assign_variant("test_123", "visitor_456")
        
        assert variant in ["control", "variant_a"]
    
    def test_assign_variant_consistent(self, framework):
        """Verifica que la asignación sea consistente para el mismo visitante"""
        variant1 = framework.assign_variant("test_123", "visitor_456")
        variant2 = framework.assign_variant("test_123", "visitor_456")
        
        assert variant1 == variant2
    
    def test_track_conversion(self, framework):
        """Verifica tracking de conversiones"""
        result = framework.track_conversion(
            test_id="test_123",
            visitor_id="visitor_456",
            variant_id="control",
            value=99.99,
            metadata={"source": "email"}
        )
        
        assert result is True
    
    def test_get_test_results_structure(self, framework):
        """Verifica estructura de resultados de test"""
        results = framework.get_test_results("test_123")
        
        assert "test_id" in results
        assert "test_name" in results
        assert "status" in results
        assert "results" in results
        assert "winner" in results
        assert "recommendation" in results
        assert isinstance(results["results"], list)
    
    def test_test_result_calculation(self, framework):
        """Verifica cálculo de resultados de test"""
        results = framework.get_test_results("test_123")
        
        for result in results["results"]:
            assert hasattr(result, "variant_id")
            assert hasattr(result, "conversion_rate")
            assert hasattr(result, "revenue_per_visitor")
            assert hasattr(result, "statistical_significance")
            assert hasattr(result, "confidence_level")
            assert 0 <= result.conversion_rate <= 1
            assert 0 <= result.statistical_significance <= 1
    
    def test_determine_winner(self, framework):
        """Verifica determinación de ganador"""
        results = framework.get_test_results("test_123")
        
        if results["winner"]:
            assert results["winner"] in ["control", "variant_a"]
            # Verificar que el ganador esté en los resultados
            winner_ids = [r.variant_id for r in results["results"]]
            assert results["winner"] in winner_ids
    
    def test_recommendation_generation(self, framework):
        """Verifica generación de recomendaciones"""
        results = framework.get_test_results("test_123")
        
        assert isinstance(results["recommendation"], str)
        assert len(results["recommendation"]) > 0
    
    def test_multiple_test_types(self, framework, test_variants):
        """Verifica soporte para múltiples tipos de test"""
        test_ab = framework.create_test(
            test_name="AB Test",
            test_type=TestType.AB,
            variants=test_variants
        )
        assert test_ab["config"]["type"] == "ab"
        
        # Test ABC (necesitaría 3 variantes)
        variants_abc = test_variants + [
            TestVariant(
                id="variant_b",
                name="Variant B",
                config={"headline": "Another Headline"},
                traffic_percentage=33.33
            )
        ]
        # Ajustar porcentajes
        variants_abc[0].traffic_percentage = 33.33
        variants_abc[1].traffic_percentage = 33.34
        
        test_abc = framework.create_test(
            test_name="ABC Test",
            test_type=TestType.ABC,
            variants=variants_abc
        )
        assert test_abc["config"]["type"] == "abc"


class TestIntegration:
    """Tests de integración entre componentes"""
    
    @pytest.fixture
    def helper(self):
        """Helper para campaña"""
        return LaunchCampaignHelper(
            n8n_base_url="https://test-n8n.com",
            api_key="test_key"
        )
    
    @pytest.fixture
    def framework(self):
        """Framework de testing"""
        return AdvancedTestingFramework(
            api_base_url="https://test-api.com",
            api_key="test_key"
        )
    
    @pytest.fixture
    def product_config(self):
        """Configuración de ejemplo del producto"""
        return {
            "name": "Producto Test",
            "benefits": [
                "Beneficio 1",
                "Beneficio 2",
                "Beneficio 3"
            ],
            "problem": "Problema específico",
            "pain": "Dolor específico",
            "result": "Resultado deseado",
            "area": "Área de aplicación",
            "discount_percentage": 25,
            "normal_price": 199,
            "special_price": 149,
            "bonuses": ["Bonus 1", "Bonus 2"],
            "units_available": 50,
            "cta_link": "https://test.com/launch",
            "platforms": ["instagram", "facebook", "linkedin"],
            "hashtags": ["#Test", "#Producto"]
        }
    
    def test_campaign_with_ab_testing(self, helper, framework, product_config):
        """Verifica integración de campaña con A/B testing"""
        # Crear test A/B para la campaña
        variants = [
            TestVariant(
                id="control",
                name="Control",
                config={"headline": "Original Campaign"},
                traffic_percentage=50.0
            ),
            TestVariant(
                id="variant_a",
                name="Variant A",
                config={"headline": "New Campaign Headline"},
                traffic_percentage=50.0
            )
        ]
        
        test = framework.create_test(
            test_name="Campaign Headline Test",
            test_type=TestType.AB,
            variants=variants
        )
        
        assert test["config"]["name"] == "Campaign Headline Test"
        
        # Disparar campaña (simulado)
        with patch('launch_campaign_helper.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"status": "success"}
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            
            result = helper.trigger_day_1_teaser(product_config)
            assert result["status"] == "success"


class TestDataValidation:
    """Tests de validación de datos"""
    
    @pytest.fixture
    def helper(self):
        """Helper para campaña"""
        return LaunchCampaignHelper(
            n8n_base_url="https://test-n8n.com",
            api_key="test_key"
        )
    
    def test_product_config_validation(self, helper):
        """Verifica validación de configuración de producto"""
        # Configuración mínima válida
        minimal_config = {"name": "Test Product"}
        
        with patch('launch_campaign_helper.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"status": "success"}
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            
            # Debe funcionar con configuración mínima
            result = helper.trigger_day_1_teaser(minimal_config)
            assert result["status"] == "success"
    
    def test_platform_validation(self, helper):
        """Verifica validación de plataformas"""
        config = {
            "name": "Test",
            "platforms": ["instagram", "facebook", "linkedin", "invalid_platform"]
        }
        
        with patch('launch_campaign_helper.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"status": "success"}
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            
            # Debe aceptar cualquier lista de plataformas
            result = helper.trigger_day_1_teaser(config)
            payload = mock_post.call_args[1]["json"]
            assert "invalid_platform" in payload["platforms"]


class TestEdgeCases:
    """Tests para casos límite"""
    
    @pytest.fixture
    def helper(self):
        """Helper para campaña"""
        return LaunchCampaignHelper(
            n8n_base_url="https://test-n8n.com",
            api_key="test_key"
        )
    
    def test_empty_benefits_list(self, helper):
        """Verifica manejo de lista de beneficios vacía"""
        config = {"name": "Test", "benefits": []}
        
        with patch('launch_campaign_helper.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"status": "success"}
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            
            result = helper.trigger_day_1_teaser(config)
            payload = mock_post.call_args[1]["json"]
            assert payload["productBenefits"] == []
    
    def test_zero_discount(self, helper):
        """Verifica manejo de descuento cero"""
        config = {
            "name": "Test",
            "discount_percentage": 0,
            "normal_price": 100,
            "special_price": 100
        }
        
        with patch('launch_campaign_helper.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"status": "success"}
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            
            result = helper.trigger_day_3_offer(config)
            payload = mock_post.call_args[1]["json"]
            assert payload["discountPercentage"] == 0
    
    def test_large_hashtags_list(self, helper):
        """Verifica manejo de lista grande de hashtags"""
        config = {
            "name": "Test",
            "hashtags": [f"#tag{i}" for i in range(100)]
        }
        
        with patch('launch_campaign_helper.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"status": "success"}
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            
            result = helper.trigger_day_1_teaser(config)
            payload = mock_post.call_args[1]["json"]
            assert len(payload["hashtags"]) == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

