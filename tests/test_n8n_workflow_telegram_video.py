#!/usr/bin/env python3
"""
Tests para el workflow de n8n: Telegram Video Auto Post - Multi Platform

Este test suite valida:
- Estructura del JSON del workflow
- Configuración de nodos
- Lógica de los nodos de código
- Conexiones entre nodos
- Configuración de credenciales
- Datos estáticos del workflow
- Validación de parámetros críticos

Usage:
    pytest tests/test_n8n_workflow_telegram_video.py -v
    pytest tests/test_n8n_workflow_telegram_video.py::TestWorkflowStructure -v
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any
import pytest


class TestWorkflowStructure:
    """Tests para validar la estructura básica del workflow"""
    
    @pytest.fixture
    def workflow(self):
        """Carga el workflow JSON"""
        workflow_path = Path(__file__).parent.parent / "n8n_workflow_telegram_video_auto_post.json"
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_workflow_has_name(self, workflow):
        """Verifica que el workflow tenga un nombre"""
        assert "name" in workflow
        assert workflow["name"] == "Telegram Video Auto Post - Multi Platform"
    
    def test_workflow_has_nodes(self, workflow):
        """Verifica que el workflow tenga nodos"""
        assert "nodes" in workflow
        assert isinstance(workflow["nodes"], list)
        assert len(workflow["nodes"]) > 0
    
    def test_workflow_has_connections(self, workflow):
        """Verifica que el workflow tenga conexiones"""
        assert "connections" in workflow
        assert isinstance(workflow["connections"], dict)
    
    def test_workflow_has_static_data(self, workflow):
        """Verifica que el workflow tenga staticData configurado"""
        assert "staticData" in workflow
        static_data = workflow["staticData"]
        
        # Verifica campos críticos en staticData
        assert "lastTikTokIndex" in static_data
        assert "lastInstagramIndex" in static_data
        assert "rateLimitHistory" in static_data
        assert "videoQueue" in static_data
        assert "circuitBreaker" in static_data
        assert "videoCache" in static_data
    
    def test_workflow_has_settings(self, workflow):
        """Verifica que el workflow tenga settings"""
        assert "settings" in workflow
        assert "executionOrder" in workflow["settings"]


class TestNodeConfiguration:
    """Tests para validar la configuración de nodos específicos"""
    
    @pytest.fixture
    def workflow(self):
        """Carga el workflow JSON"""
        workflow_path = Path(__file__).parent.parent / "n8n_workflow_telegram_video_auto_post.json"
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @pytest.fixture
    def nodes_by_id(self, workflow):
        """Crea un diccionario de nodos por ID"""
        return {node["id"]: node for node in workflow["nodes"]}
    
    def test_telegram_trigger_exists(self, nodes_by_id):
        """Verifica que exista el nodo de trigger de Telegram"""
        assert "telegram-trigger" in nodes_by_id
        node = nodes_by_id["telegram-trigger"]
        assert node["type"] == "n8n-nodes-base.telegramTrigger"
        assert "credentials" in node
        assert "telegramApi" in node["credentials"]
    
    def test_filter_video_node_exists(self, nodes_by_id):
        """Verifica que exista el nodo de filtro de video"""
        assert "filter-video" in nodes_by_id
        node = nodes_by_id["filter-video"]
        assert node["type"] == "n8n-nodes-base.if"
        assert "parameters" in node
        assert "conditions" in node["parameters"]
    
    def test_select_account_node_exists(self, nodes_by_id):
        """Verifica que exista el nodo de selección de cuenta"""
        assert "select-account" in nodes_by_id
        node = nodes_by_id["select-account"]
        assert node["type"] == "n8n-nodes-base.code"
        assert "parameters" in node
        assert "jsCode" in node["parameters"]
    
    def test_health_check_node_exists(self, nodes_by_id):
        """Verifica que exista el nodo de health check"""
        assert "health-check" in nodes_by_id
        node = nodes_by_id["health-check"]
        assert node["type"] == "n8n-nodes-base.code"
        assert "parameters" in node
        assert "jsCode" in node["parameters"]
    
    def test_rate_limit_node_exists(self, nodes_by_id):
        """Verifica que exista el nodo de rate limiting"""
        assert "check-rate-limits" in nodes_by_id
        node = nodes_by_id["check-rate-limits"]
        assert node["type"] == "n8n-nodes-base.code"
        assert "parameters" in node
        assert "jsCode" in node["parameters"]
    
    def test_content_moderation_node_exists(self, nodes_by_id):
        """Verifica que exista el nodo de moderación de contenido"""
        assert "content-moderation" in nodes_by_id
        node = nodes_by_id["content-moderation"]
        assert node["type"] == "n8n-nodes-base.code"
        assert "parameters" in node
        assert "jsCode" in node["parameters"]
    
    def test_platform_nodes_exist(self, nodes_by_id):
        """Verifica que existan los nodos de publicación a plataformas"""
        assert "post-tiktok" in nodes_by_id
        assert "post-youtube" in nodes_by_id
        assert "create-instagram-container" in nodes_by_id
        assert "publish-instagram" in nodes_by_id
    
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


class TestCodeNodeLogic:
    """Tests para validar la lógica de los nodos de código"""
    
    @pytest.fixture
    def workflow(self):
        """Carga el workflow JSON"""
        workflow_path = Path(__file__).parent.parent / "n8n_workflow_telegram_video_auto_post.json"
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @pytest.fixture
    def code_nodes(self, workflow):
        """Extrae todos los nodos de código"""
        return [
            node for node in workflow["nodes"]
            if node.get("type") == "n8n-nodes-base.code"
        ]
    
    def test_select_account_logic(self, workflow):
        """Valida la lógica de selección de cuenta"""
        node = next(
            (n for n in workflow["nodes"] if n["id"] == "select-account"),
            None
        )
        assert node is not None
        
        js_code = node["parameters"]["jsCode"]
        
        # Verifica que contenga lógica de round-robin
        assert "lastTikTokIndex" in js_code
        assert "lastInstagramIndex" in js_code
        assert "Round robin" in js_code or "round robin" in js_code or "round-robin" in js_code.lower()
        
        # Verifica que maneje múltiples cuentas
        assert "tiktok" in js_code.lower()
        assert "instagram" in js_code.lower()
    
    def test_health_check_logic(self, workflow):
        """Valida la lógica de health check"""
        node = next(
            (n for n in workflow["nodes"] if n["id"] == "health-check"),
            None
        )
        assert node is not None
        
        js_code = node["parameters"]["jsCode"]
        
        # Verifica que contenga checks de servicios
        assert "healthStatus" in js_code
        assert "services" in js_code
        assert "overall" in js_code
    
    def test_rate_limit_logic(self, workflow):
        """Valida la lógica de rate limiting"""
        node = next(
            (n for n in workflow["nodes"] if n["id"] == "check-rate-limits"),
            None
        )
        assert node is not None
        
        js_code = node["parameters"]["jsCode"]
        
        # Verifica que contenga lógica de rate limiting
        assert "RATE_LIMITS" in js_code
        assert "rateLimitHistory" in js_code
        assert "canProceed" in js_code
        assert "window" in js_code
    
    def test_content_moderation_logic(self, workflow):
        """Valida la lógica de moderación de contenido"""
        node = next(
            (n for n in workflow["nodes"] if n["id"] == "content-moderation"),
            None
        )
        assert node is not None
        
        js_code = node["parameters"]["jsCode"]
        
        # Verifica que contenga checks de moderación
        assert "moderation" in js_code.lower()
        assert "prohibitedWords" in js_code or "prohibited" in js_code.lower()
        assert "score" in js_code.lower()
    
    def test_queue_logic(self, workflow):
        """Valida la lógica de cola de videos"""
        node = next(
            (n for n in workflow["nodes"] if n["id"] == "queue-video"),
            None
        )
        assert node is not None
        
        js_code = node["parameters"]["jsCode"]
        
        # Verifica que contenga lógica de cola
        assert "queue" in js_code.lower()
        assert "priority" in js_code.lower()
        assert "scheduledFor" in js_code
    
    def test_all_code_nodes_have_valid_js(self, code_nodes):
        """Verifica que todos los nodos de código tengan JavaScript válido"""
        for node in code_nodes:
            assert "parameters" in node
            assert "jsCode" in node["parameters"]
            js_code = node["parameters"]["jsCode"]
            assert js_code, f"Nodo {node.get('name')} tiene código vacío"
            
            # Verifica sintaxis básica (paréntesis balanceados)
            assert js_code.count("(") == js_code.count(")"), \
                f"Nodo {node.get('name')} tiene paréntesis desbalanceados"
            assert js_code.count("{") == js_code.count("}"), \
                f"Nodo {node.get('name')} tiene llaves desbalanceadas"


class TestWorkflowConnections:
    """Tests para validar las conexiones del workflow"""
    
    @pytest.fixture
    def workflow(self):
        """Carga el workflow JSON"""
        workflow_path = Path(__file__).parent.parent / "n8n_workflow_telegram_video_auto_post.json"
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @pytest.fixture
    def node_ids(self, workflow):
        """Obtiene todos los IDs de nodos"""
        return {node["id"] for node in workflow["nodes"]}
    
    def test_telegram_trigger_connected(self, workflow, node_ids):
        """Verifica que el trigger de Telegram esté conectado"""
        connections = workflow.get("connections", {})
        trigger_connections = connections.get("Telegram Trigger", {})
        
        # El trigger debe tener conexiones de salida
        assert "main" in trigger_connections
        assert len(trigger_connections["main"]) > 0
    
    def test_filter_video_connected(self, workflow, node_ids):
        """Verifica que el filtro de video esté conectado"""
        connections = workflow.get("connections", {})
        filter_connections = connections.get("Filter Video Messages", {})
        
        # El filtro debe tener conexiones
        assert "main" in filter_connections
    
    def test_platform_router_connected(self, workflow, node_ids):
        """Verifica que el router de plataformas esté conectado"""
        connections = workflow.get("connections", {})
        router_connections = connections.get("Platform Router", {})
        
        # El router debe tener conexiones
        assert "main" in router_connections
    
    def test_all_connection_targets_exist(self, workflow, node_ids):
        """Verifica que todos los nodos referenciados en conexiones existan"""
        connections = workflow.get("connections", {})
        
        for source_node, connection_data in connections.items():
            if "main" in connection_data:
                for connection_group in connection_data["main"]:
                    for connection in connection_group:
                        if "node" in connection:
                            target_node_name = connection["node"]
                            # Busca el nodo por nombre
                            target_exists = any(
                                node["name"] == target_node_name
                                for node in workflow["nodes"]
                            )
                            assert target_exists, \
                                f"Nodo objetivo '{target_node_name}' no existe en conexión desde '{source_node}'"


class TestCredentialsConfiguration:
    """Tests para validar la configuración de credenciales"""
    
    @pytest.fixture
    def workflow(self):
        """Carga el workflow JSON"""
        workflow_path = Path(__file__).parent.parent / "n8n_workflow_telegram_video_auto_post.json"
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_telegram_credentials_configured(self, workflow):
        """Verifica que las credenciales de Telegram estén configuradas"""
        telegram_nodes = [
            node for node in workflow["nodes"]
            if "telegram" in node.get("type", "").lower() or
               "telegram" in node.get("name", "").lower()
        ]
        
        for node in telegram_nodes:
            if "credentials" in node:
                assert "telegramApi" in node["credentials"]
    
    def test_tiktok_credentials_configured(self, workflow):
        """Verifica que las credenciales de TikTok estén configuradas"""
        tiktok_node = next(
            (n for n in workflow["nodes"] if n["id"] == "post-tiktok"),
            None
        )
        
        if tiktok_node:
            assert "credentials" in tiktok_node
            assert "tiktokApi" in tiktok_node["credentials"]
    
    def test_instagram_credentials_configured(self, workflow):
        """Verifica que las credenciales de Instagram estén configuradas"""
        instagram_nodes = [
            node for node in workflow["nodes"]
            if "instagram" in node.get("name", "").lower()
        ]
        
        for node in instagram_nodes:
            if "credentials" in node:
                assert "instagramApi" in node["credentials"] or "instagram" in str(node["credentials"]).lower()
    
    def test_youtube_credentials_configured(self, workflow):
        """Verifica que las credenciales de YouTube estén configuradas"""
        youtube_node = next(
            (n for n in workflow["nodes"] if n["id"] == "post-youtube"),
            None
        )
        
        if youtube_node:
            assert "credentials" in youtube_node
            assert "youtube" in str(youtube_node["credentials"]).lower()


class TestStaticDataStructure:
    """Tests para validar la estructura de staticData"""
    
    @pytest.fixture
    def workflow(self):
        """Carga el workflow JSON"""
        workflow_path = Path(__file__).parent.parent / "n8n_workflow_telegram_video_auto_post.json"
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_circuit_breaker_structure(self, workflow):
        """Verifica la estructura del circuit breaker"""
        static_data = workflow.get("staticData", {})
        circuit_breaker = static_data.get("circuitBreaker", {})
        
        assert "state" in circuit_breaker
        assert "failureCount" in circuit_breaker
        assert "successCount" in circuit_breaker
        assert circuit_breaker["state"] in ["CLOSED", "OPEN", "HALF_OPEN"]
    
    def test_rate_limit_history_structure(self, workflow):
        """Verifica la estructura de rate limit history"""
        static_data = workflow.get("staticData", {})
        rate_limit_history = static_data.get("rateLimitHistory", {})
        
        assert isinstance(rate_limit_history, dict)
    
    def test_video_queue_structure(self, workflow):
        """Verifica la estructura de la cola de videos"""
        static_data = workflow.get("staticData", {})
        video_queue = static_data.get("videoQueue", [])
        
        assert isinstance(video_queue, list)
    
    def test_video_cache_structure(self, workflow):
        """Verifica la estructura del cache de videos"""
        static_data = workflow.get("staticData", {})
        video_cache = static_data.get("videoCache", {})
        
        assert isinstance(video_cache, dict)


class TestWorkflowParameters:
    """Tests para validar parámetros críticos del workflow"""
    
    @pytest.fixture
    def workflow(self):
        """Carga el workflow JSON"""
        workflow_path = Path(__file__).parent.parent / "n8n_workflow_telegram_video_auto_post.json"
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_telegram_trigger_has_webhook_id(self, workflow):
        """Verifica que el trigger de Telegram tenga webhook ID"""
        trigger_node = next(
            (n for n in workflow["nodes"] if n["id"] == "telegram-trigger"),
            None
        )
        
        assert trigger_node is not None
        assert "webhookId" in trigger_node
        assert trigger_node["webhookId"]
    
    def test_platform_router_has_conditions(self, workflow):
        """Verifica que el router de plataformas tenga condiciones"""
        router_node = next(
            (n for n in workflow["nodes"] if n["id"] == "platform-router"),
            None
        )
        
        if router_node:
            assert "parameters" in router_node
            params = router_node["parameters"]
            # Debe tener condiciones o rutas configuradas
            assert "conditions" in params or "routing" in params or "rules" in params
    
    def test_video_validation_parameters(self, workflow):
        """Verifica que el nodo de validación de video tenga parámetros"""
        validation_node = next(
            (n for n in workflow["nodes"] if n["id"] == "validate-video"),
            None
        )
        
        if validation_node:
            assert "parameters" in validation_node


class TestWorkflowIntegrity:
    """Tests de integridad general del workflow"""
    
    @pytest.fixture
    def workflow(self):
        """Carga el workflow JSON"""
        workflow_path = Path(__file__).parent.parent / "n8n_workflow_telegram_video_auto_post.json"
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_workflow_is_valid_json(self, workflow):
        """Verifica que el workflow sea JSON válido"""
        # Si llegamos aquí, el JSON es válido
        assert isinstance(workflow, dict)
    
    def test_no_duplicate_node_ids(self, workflow):
        """Verifica que no haya IDs de nodos duplicados"""
        node_ids = [node["id"] for node in workflow["nodes"]]
        assert len(node_ids) == len(set(node_ids)), "Hay IDs de nodos duplicados"
    
    def test_all_code_nodes_return_data(self, workflow):
        """Verifica que los nodos de código retornen datos"""
        code_nodes = [
            node for node in workflow["nodes"]
            if node.get("type") == "n8n-nodes-base.code"
        ]
        
        for node in code_nodes:
            js_code = node["parameters"].get("jsCode", "")
            # Debe tener un return statement
            assert "return" in js_code, \
                f"Nodo {node.get('name')} no tiene return statement"
    
    def test_workflow_version(self, workflow):
        """Verifica que el workflow tenga versión"""
        assert "versionId" in workflow or "version" in workflow


class TestN8nExpressions:
    """Tests para validar expresiones n8n ({{ }})"""
    
    @pytest.fixture
    def workflow(self):
        """Carga el workflow JSON"""
        workflow_path = Path(__file__).parent.parent / "n8n_workflow_telegram_video_auto_post.json"
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_expressions_are_valid(self, workflow):
        """Verifica que las expresiones n8n tengan sintaxis válida"""
        expression_pattern = re.compile(r'\{\{.*?\}\}')
        
        for node in workflow["nodes"]:
            node_str = json.dumps(node)
            expressions = expression_pattern.findall(node_str)
            
            for expr in expressions:
                # Verifica que tenga contenido entre llaves
                content = expr[2:-2].strip()
                assert content, f"Expresión vacía en nodo {node.get('name')}"
                
                # Verifica que no tenga llaves anidadas incorrectas
                assert expr.count("{{") == 1, f"Expresión con múltiples {{ en nodo {node.get('name')}"
                assert expr.count("}}") == 1, f"Expresión con múltiples }} en nodo {node.get('name')}"
    
    def test_telegram_expressions(self, workflow):
        """Verifica expresiones específicas de Telegram"""
        telegram_nodes = [
            node for node in workflow["nodes"]
            if "telegram" in node.get("type", "").lower()
        ]
        
        for node in telegram_nodes:
            node_str = json.dumps(node)
            # Debe tener expresiones para chatId o message
            if "chatId" in node_str or "message" in node_str:
                assert "{{" in node_str or "=" in node_str, \
                    f"Nodo Telegram {node.get('name')} debería usar expresiones"


class TestHTTPRequests:
    """Tests para validar nodos HTTP Request"""
    
    @pytest.fixture
    def workflow(self):
        """Carga el workflow JSON"""
        workflow_path = Path(__file__).parent.parent / "n8n_workflow_telegram_video_auto_post.json"
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_http_request_nodes_have_urls(self, workflow):
        """Verifica que los nodos HTTP Request tengan URLs"""
        http_nodes = [
            node for node in workflow["nodes"]
            if node.get("type") == "n8n-nodes-base.httpRequest"
        ]
        
        for node in http_nodes:
            assert "parameters" in node
            assert "url" in node["parameters"]
            url = node["parameters"]["url"]
            assert url, f"Nodo HTTP {node.get('name')} no tiene URL"
    
    def test_youtube_api_url(self, workflow):
        """Verifica la URL de la API de YouTube"""
        youtube_node = next(
            (n for n in workflow["nodes"] if n["id"] == "post-youtube"),
            None
        )
        
        if youtube_node:
            url = youtube_node["parameters"].get("url", "")
            assert "youtube" in url.lower() or "googleapis.com" in url.lower()
    
    def test_tiktok_api_url(self, workflow):
        """Verifica la URL de la API de TikTok"""
        tiktok_node = next(
            (n for n in workflow["nodes"] if n["id"] == "post-tiktok"),
            None
        )
        
        if tiktok_node:
            url = tiktok_node["parameters"].get("url", "")
            assert "tiktok" in url.lower() or "open.tiktokapis.com" in url.lower()
    
    def test_instagram_api_url(self, workflow):
        """Verifica la URL de la API de Instagram"""
        instagram_nodes = [
            node for node in workflow["nodes"]
            if "instagram" in node.get("name", "").lower() and
               node.get("type") == "n8n-nodes-base.httpRequest"
        ]
        
        for node in instagram_nodes:
            url = node["parameters"].get("url", "")
            assert "instagram" in url.lower() or "graph.instagram.com" in url.lower()


class TestErrorHandling:
    """Tests para validar manejo de errores"""
    
    @pytest.fixture
    def workflow(self):
        """Carga el workflow JSON"""
        workflow_path = Path(__file__).parent.parent / "n8n_workflow_telegram_video_auto_post.json"
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_error_notification_nodes_exist(self, workflow):
        """Verifica que existan nodos de notificación de errores"""
        error_nodes = [
            node for node in workflow["nodes"]
            if "error" in node.get("name", "").lower() or
               "notify" in node.get("name", "").lower() and "error" in node.get("name", "").lower()
        ]
        
        assert len(error_nodes) > 0, "No hay nodos de notificación de errores"
    
    def test_retry_logic_exists(self, workflow):
        """Verifica que exista lógica de reintentos"""
        retry_node = next(
            (n for n in workflow["nodes"] if "retry" in n.get("name", "").lower()),
            None
        )
        
        assert retry_node is not None, "No hay nodo de reintentos"
        if retry_node.get("type") == "n8n-nodes-base.code":
            js_code = retry_node["parameters"].get("jsCode", "")
            assert "retry" in js_code.lower() or "backoff" in js_code.lower()
    
    def test_circuit_breaker_logic(self, workflow):
        """Verifica la lógica del circuit breaker"""
        circuit_breaker_node = next(
            (n for n in workflow["nodes"] if "circuit" in n.get("name", "").lower()),
            None
        )
        
        if circuit_breaker_node:
            if circuit_breaker_node.get("type") == "n8n-nodes-base.code":
                js_code = circuit_breaker_node["parameters"].get("jsCode", "")
                assert "circuit" in js_code.lower() or "breaker" in js_code.lower()


class TestDataFlow:
    """Tests para validar el flujo de datos"""
    
    @pytest.fixture
    def workflow(self):
        """Carga el workflow JSON"""
        workflow_path = Path(__file__).parent.parent / "n8n_workflow_telegram_video_auto_post.json"
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_trigger_to_filter_connection(self, workflow):
        """Verifica conexión del trigger al filtro"""
        connections = workflow.get("connections", {})
        trigger_conn = connections.get("Telegram Trigger", {})
        
        if "main" in trigger_conn and len(trigger_conn["main"]) > 0:
            first_connection = trigger_conn["main"][0]
            if len(first_connection) > 0:
                target = first_connection[0].get("node", "")
                assert "filter" in target.lower() or "video" in target.lower()
    
    def test_platform_split_exists(self, workflow):
        """Verifica que exista un nodo que divida por plataformas"""
        split_nodes = [
            node for node in workflow["nodes"]
            if "split" in node.get("name", "").lower() and "platform" in node.get("name", "").lower()
        ]
        
        assert len(split_nodes) > 0, "No hay nodo que divida por plataformas"
    
    def test_merge_results_exists(self, workflow):
        """Verifica que exista un nodo que combine resultados"""
        merge_nodes = [
            node for node in workflow["nodes"]
            if "merge" in node.get("name", "").lower() and "result" in node.get("name", "").lower()
        ]
        
        assert len(merge_nodes) > 0, "No hay nodo que combine resultados"


class TestSecurity:
    """Tests de seguridad"""
    
    @pytest.fixture
    def workflow(self):
        """Carga el workflow JSON"""
        workflow_path = Path(__file__).parent.parent / "n8n_workflow_telegram_video_auto_post.json"
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_no_hardcoded_secrets(self, workflow):
        """Verifica que no haya secretos hardcodeados"""
        workflow_str = json.dumps(workflow).lower()
        
        # Patrones comunes de secretos
        secret_patterns = [
            r'password["\']?\s*[:=]\s*["\'][^"\']+["\']',
            r'api[_-]?key["\']?\s*[:=]\s*["\'][^"\']+["\']',
            r'secret["\']?\s*[:=]\s*["\'][^"\']+["\']',
            r'token["\']?\s*[:=]\s*["\'](?!\$env)[^"\']+["\']',
        ]
        
        for pattern in secret_patterns:
            matches = re.findall(pattern, workflow_str, re.IGNORECASE)
            # Filtrar falsos positivos (como "telegramApi" que es un nombre de credencial)
            real_secrets = [
                m for m in matches
                if not any(keyword in m.lower() for keyword in ['telegramapi', 'tiktokapi', 'instagramapi', 'youtubeapi'])
            ]
            assert len(real_secrets) == 0, f"Posibles secretos hardcodeados encontrados: {real_secrets[:3]}"
    
    def test_credentials_use_env_vars(self, workflow):
        """Verifica que las credenciales usen variables de entorno"""
        code_nodes = [
            node for node in workflow["nodes"]
            if node.get("type") == "n8n-nodes-base.code"
        ]
        
        for node in code_nodes:
            js_code = node["parameters"].get("jsCode", "")
            # Si hay referencias a tokens/keys, deberían usar $env
            if "token" in js_code.lower() or "key" in js_code.lower():
                # Debe usar $env para variables sensibles
                assert "$env" in js_code or "credentials" in str(node.get("credentials", "")), \
                    f"Nodo {node.get('name')} podría estar usando valores hardcodeados"


class TestPerformance:
    """Tests de performance y optimización"""
    
    @pytest.fixture
    def workflow(self):
        """Carga el workflow JSON"""
        workflow_path = Path(__file__).parent.parent / "n8n_workflow_telegram_video_auto_post.json"
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_cache_mechanism_exists(self, workflow):
        """Verifica que exista mecanismo de cache"""
        cache_nodes = [
            node for node in workflow["nodes"]
            if "cache" in node.get("name", "").lower()
        ]
        
        assert len(cache_nodes) > 0, "No hay nodos de cache"
    
    def test_rate_limiting_exists(self, workflow):
        """Verifica que exista rate limiting"""
        rate_limit_nodes = [
            node for node in workflow["nodes"]
            if "rate" in node.get("name", "").lower() and "limit" in node.get("name", "").lower()
        ]
        
        assert len(rate_limit_nodes) > 0, "No hay nodos de rate limiting"
    
    def test_queue_mechanism_exists(self, workflow):
        """Verifica que exista mecanismo de cola"""
        queue_nodes = [
            node for node in workflow["nodes"]
            if "queue" in node.get("name", "").lower()
        ]
        
        assert len(queue_nodes) > 0, "No hay nodos de cola"


class TestPlatformIntegration:
    """Tests para validar integración con plataformas"""
    
    @pytest.fixture
    def workflow(self):
        """Carga el workflow JSON"""
        workflow_path = Path(__file__).parent.parent / "n8n_workflow_telegram_video_auto_post.json"
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_tiktok_integration_complete(self, workflow):
        """Verifica que la integración de TikTok esté completa"""
        tiktok_nodes = [
            node for node in workflow["nodes"]
            if "tiktok" in node.get("name", "").lower()
        ]
        
        assert len(tiktok_nodes) > 0, "No hay nodos de TikTok"
        
        # Debe haber al menos un nodo de publicación
        post_nodes = [n for n in tiktok_nodes if "post" in n.get("name", "").lower()]
        assert len(post_nodes) > 0, "No hay nodo de publicación a TikTok"
    
    def test_instagram_integration_complete(self, workflow):
        """Verifica que la integración de Instagram esté completa"""
        instagram_nodes = [
            node for node in workflow["nodes"]
            if "instagram" in node.get("name", "").lower()
        ]
        
        assert len(instagram_nodes) > 0, "No hay nodos de Instagram"
        
        # Debe haber nodos de creación de container y publicación
        container_nodes = [n for n in instagram_nodes if "container" in n.get("name", "").lower()]
        publish_nodes = [n for n in instagram_nodes if "publish" in n.get("name", "").lower()]
        
        assert len(container_nodes) > 0 or len(publish_nodes) > 0, \
            "No hay nodos de creación/publicación de Instagram"
    
    def test_youtube_integration_complete(self, workflow):
        """Verifica que la integración de YouTube esté completa"""
        youtube_nodes = [
            node for node in workflow["nodes"]
            if "youtube" in node.get("name", "").lower()
        ]
        
        assert len(youtube_nodes) > 0, "No hay nodos de YouTube"
        
        # Debe haber al menos un nodo de publicación
        post_nodes = [n for n in youtube_nodes if "post" in n.get("name", "").lower() or "shorts" in n.get("name", "").lower()]
        assert len(post_nodes) > 0, "No hay nodo de publicación a YouTube"


class TestVideoProcessing:
    """Tests para validar procesamiento de video"""
    
    @pytest.fixture
    def workflow(self):
        """Carga el workflow JSON"""
        workflow_path = Path(__file__).parent.parent / "n8n_workflow_telegram_video_auto_post.json"
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_video_validation_exists(self, workflow):
        """Verifica que exista validación de video"""
        validation_nodes = [
            node for node in workflow["nodes"]
            if "validate" in node.get("name", "").lower() and "video" in node.get("name", "").lower()
        ]
        
        assert len(validation_nodes) > 0, "No hay nodos de validación de video"
    
    def test_video_download_exists(self, workflow):
        """Verifica que exista descarga de video"""
        download_nodes = [
            node for node in workflow["nodes"]
            if "download" in node.get("name", "").lower() and "video" in node.get("name", "").lower()
        ]
        
        assert len(download_nodes) > 0, "No hay nodos de descarga de video"
    
    def test_video_processing_service_call(self, workflow):
        """Verifica que exista llamada a servicio de procesamiento"""
        processing_nodes = [
            node for node in workflow["nodes"]
            if "process" in node.get("name", "").lower() and "video" in node.get("name", "").lower()
        ]
        
        assert len(processing_nodes) > 0, "No hay nodos de procesamiento de video"


class TestNotifications:
    """Tests para validar notificaciones"""
    
    @pytest.fixture
    def workflow(self):
        """Carga el workflow JSON"""
        workflow_path = Path(__file__).parent.parent / "n8n_workflow_telegram_video_auto_post.json"
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_telegram_notifications_exist(self, workflow):
        """Verifica que existan notificaciones de Telegram"""
        telegram_notify_nodes = [
            node for node in workflow["nodes"]
            if "telegram" in node.get("type", "").lower() and
               "notify" in node.get("name", "").lower() or
               "send" in node.get("name", "").lower()
        ]
        
        assert len(telegram_notify_nodes) > 0, "No hay nodos de notificación de Telegram"
    
    def test_confirmation_message_exists(self, workflow):
        """Verifica que exista mensaje de confirmación"""
        confirmation_nodes = [
            node for node in workflow["nodes"]
            if "confirm" in node.get("name", "").lower() or
               "success" in node.get("name", "").lower()
        ]
        
        assert len(confirmation_nodes) > 0, "No hay nodos de confirmación"


class TestAnalytics:
    """Tests para validar analytics y tracking"""
    
    @pytest.fixture
    def workflow(self):
        """Carga el workflow JSON"""
        workflow_path = Path(__file__).parent.parent / "n8n_workflow_telegram_video_auto_post.json"
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_analytics_tracking_exists(self, workflow):
        """Verifica que exista tracking de analytics"""
        analytics_nodes = [
            node for node in workflow["nodes"]
            if "analytics" in node.get("name", "").lower() or
               "track" in node.get("name", "").lower()
        ]
        
        assert len(analytics_nodes) > 0, "No hay nodos de analytics"
    
    def test_static_data_has_analytics(self, workflow):
        """Verifica que staticData tenga estructura de analytics"""
        static_data = workflow.get("staticData", {})
        assert "analyticsHistory" in static_data or "analytics" in str(static_data).lower()


class TestEdgeCases:
    """Tests para casos límite"""
    
    @pytest.fixture
    def workflow(self):
        """Carga el workflow JSON"""
        workflow_path = Path(__file__).parent.parent / "n8n_workflow_telegram_video_auto_post.json"
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_empty_message_handling(self, workflow):
        """Verifica manejo de mensajes vacíos"""
        filter_node = next(
            (n for n in workflow["nodes"] if n["id"] == "filter-video"),
            None
        )
        
        if filter_node:
            # El filtro debe tener condiciones para manejar casos vacíos
            assert "parameters" in filter_node
            assert "conditions" in filter_node["parameters"]
    
    def test_large_file_handling(self, workflow):
        """Verifica manejo de archivos grandes"""
        validation_node = next(
            (n for n in workflow["nodes"] if n["id"] == "validate-video"),
            None
        )
        
        if validation_node and validation_node.get("type") == "n8n-nodes-base.code":
            js_code = validation_node["parameters"].get("jsCode", "")
            assert "maxSize" in js_code or "file_size" in js_code.lower()
    
    def test_multiple_platform_failure(self, workflow):
        """Verifica manejo de fallos en múltiples plataformas"""
        merge_results_node = next(
            (n for n in workflow["nodes"] if "merge" in n.get("name", "").lower() and "result" in n.get("name", "").lower()),
            None
        )
        
        if merge_results_node and merge_results_node.get("type") == "n8n-nodes-base.code":
            js_code = merge_results_node["parameters"].get("jsCode", "")
            assert "failed" in js_code.lower() or "error" in js_code.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

