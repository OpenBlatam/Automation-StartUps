#!/usr/bin/env python3
"""
API Documentation Generator for Competitive Pricing Analysis System
================================================================

Generador de documentación de API que proporciona:
- Documentación automática con Swagger/OpenAPI
- Documentación interactiva
- Ejemplos de uso
- Esquemas de datos
- Códigos de respuesta
- Autenticación
- Rate limiting
- Endpoints de prueba
- Exportación a múltiples formatos
"""

import json
import yaml
import logging
import inspect
import ast
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import re
import importlib.util
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIEndpoint:
    """Endpoint de API"""
    path: str
    method: str
    summary: str
    description: str
    parameters: List[Dict[str, Any]]
    request_body: Optional[Dict[str, Any]]
    responses: Dict[str, Dict[str, Any]]
    tags: List[str]
    security: Optional[Dict[str, Any]]
    deprecated: bool = False

@dataclass
class APISchema:
    """Esquema de datos de API"""
    name: str
    type: str
    properties: Dict[str, Any]
    required: List[str]
    description: str
    example: Optional[Any]

@dataclass
class APIDocumentation:
    """Documentación completa de API"""
    title: str
    version: str
    description: str
    base_url: str
    servers: List[Dict[str, str]]
    endpoints: List[APIEndpoint]
    schemas: List[APISchema]
    security_schemes: Dict[str, Any]
    info: Dict[str, Any]

class APIDocumentationGenerator:
    """Generador de documentación de API"""
    
    def __init__(self, api_module_path: str = "pricing_api_server.py"):
        """Inicializar generador de documentación"""
        self.api_module_path = api_module_path
        self.endpoints = []
        self.schemas = []
        self.security_schemes = {}
        
        # Configuración por defecto
        self.api_info = {
            "title": "Competitive Pricing Analysis API",
            "version": "1.0.0",
            "description": "API for competitive pricing analysis and monitoring",
            "contact": {
                "name": "API Support",
                "email": "support@company.com"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        }
        
        # Esquemas por defecto
        self._load_default_schemas()
        
        logger.info("API Documentation Generator initialized")
    
    def _load_default_schemas(self):
        """Cargar esquemas por defecto"""
        try:
            # Esquema de Producto
            product_schema = APISchema(
                name="Product",
                type="object",
                properties={
                    "id": {"type": "string", "description": "Unique product identifier"},
                    "name": {"type": "string", "description": "Product name"},
                    "category": {"type": "string", "description": "Product category"},
                    "brand": {"type": "string", "description": "Product brand"},
                    "description": {"type": "string", "description": "Product description"},
                    "created_at": {"type": "string", "format": "date-time", "description": "Creation timestamp"},
                    "updated_at": {"type": "string", "format": "date-time", "description": "Last update timestamp"}
                },
                required=["id", "name", "category"],
                description="Product information",
                example={
                    "id": "P001",
                    "name": "Wireless Headphones",
                    "category": "Electronics",
                    "brand": "TechBrand",
                    "description": "High-quality wireless headphones",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                }
            )
            self.schemas.append(product_schema)
            
            # Esquema de Precio
            price_schema = APISchema(
                name="Price",
                type="object",
                properties={
                    "id": {"type": "string", "description": "Unique price identifier"},
                    "product_id": {"type": "string", "description": "Product identifier"},
                    "competitor": {"type": "string", "description": "Competitor name"},
                    "price": {"type": "number", "format": "float", "description": "Price value"},
                    "currency": {"type": "string", "description": "Currency code"},
                    "date_collected": {"type": "string", "format": "date-time", "description": "Price collection date"},
                    "source": {"type": "string", "description": "Price source URL"},
                    "availability": {"type": "string", "description": "Product availability status"}
                },
                required=["id", "product_id", "competitor", "price", "currency"],
                description="Price information",
                example={
                    "id": "PR001",
                    "product_id": "P001",
                    "competitor": "Amazon",
                    "price": 99.99,
                    "currency": "USD",
                    "date_collected": "2024-01-01T12:00:00Z",
                    "source": "https://amazon.com/product",
                    "availability": "in_stock"
                }
            )
            self.schemas.append(price_schema)
            
            # Esquema de Análisis
            analysis_schema = APISchema(
                name="Analysis",
                type="object",
                properties={
                    "id": {"type": "string", "description": "Analysis identifier"},
                    "product_id": {"type": "string", "description": "Product identifier"},
                    "analysis_type": {"type": "string", "description": "Type of analysis"},
                    "insights": {"type": "array", "items": {"type": "string"}, "description": "Analysis insights"},
                    "recommendations": {"type": "array", "items": {"type": "string"}, "description": "Recommendations"},
                    "confidence_score": {"type": "number", "format": "float", "description": "Confidence score"},
                    "created_at": {"type": "string", "format": "date-time", "description": "Analysis timestamp"}
                },
                required=["id", "product_id", "analysis_type"],
                description="Analysis results",
                example={
                    "id": "A001",
                    "product_id": "P001",
                    "analysis_type": "competitive_pricing",
                    "insights": ["Price is 15% below market average", "Strong competitive position"],
                    "recommendations": ["Consider price increase", "Monitor competitor pricing"],
                    "confidence_score": 0.85,
                    "created_at": "2024-01-01T12:00:00Z"
                }
            )
            self.schemas.append(analysis_schema)
            
            # Esquema de Error
            error_schema = APISchema(
                name="Error",
                type="object",
                properties={
                    "error": {"type": "string", "description": "Error message"},
                    "code": {"type": "integer", "description": "Error code"},
                    "details": {"type": "string", "description": "Error details"},
                    "timestamp": {"type": "string", "format": "date-time", "description": "Error timestamp"}
                },
                required=["error", "code"],
                description="Error response",
                example={
                    "error": "Product not found",
                    "code": 404,
                    "details": "The requested product does not exist",
                    "timestamp": "2024-01-01T12:00:00Z"
                }
            )
            self.schemas.append(error_schema)
            
            logger.info("Default schemas loaded")
            
        except Exception as e:
            logger.error(f"Error loading default schemas: {e}")
    
    def analyze_api_module(self):
        """Analizar módulo de API para extraer endpoints"""
        try:
            # Cargar módulo de API
            spec = importlib.util.spec_from_file_location("api_module", self.api_module_path)
            if not spec or not spec.loader:
                logger.error(f"Could not load API module: {self.api_module_path}")
                return
            
            api_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(api_module)
            
            # Buscar aplicación Flask
            app = None
            for name, obj in inspect.getmembers(api_module):
                if hasattr(obj, 'route') and hasattr(obj, 'run'):
                    app = obj
                    break
            
            if not app:
                logger.error("Flask app not found in module")
                return
            
            # Extraer rutas
            self._extract_routes(app)
            
            logger.info(f"Analyzed API module and found {len(self.endpoints)} endpoints")
            
        except Exception as e:
            logger.error(f"Error analyzing API module: {e}")
    
    def _extract_routes(self, app):
        """Extraer rutas de la aplicación Flask"""
        try:
            for rule in app.url_map.iter_rules():
                endpoint = self._parse_route(rule, app)
                if endpoint:
                    self.endpoints.append(endpoint)
            
        except Exception as e:
            logger.error(f"Error extracting routes: {e}")
    
    def _parse_route(self, rule, app) -> Optional[APIEndpoint]:
        """Parsear ruta individual"""
        try:
            # Obtener función del endpoint
            view_func = app.view_functions.get(rule.endpoint)
            if not view_func:
                return None
            
            # Extraer información del endpoint
            path = rule.rule
            methods = list(rule.methods - {'HEAD', 'OPTIONS'})
            
            # Obtener documentación de la función
            docstring = inspect.getdoc(view_func) or ""
            summary, description = self._parse_docstring(docstring)
            
            # Extraer parámetros
            parameters = self._extract_parameters(rule, view_func)
            
            # Extraer request body
            request_body = self._extract_request_body(view_func)
            
            # Extraer respuestas
            responses = self._extract_responses(view_func)
            
            # Determinar tags
            tags = self._determine_tags(path)
            
            # Determinar seguridad
            security = self._determine_security(view_func)
            
            return APIEndpoint(
                path=path,
                method=methods[0] if methods else "GET",
                summary=summary,
                description=description,
                parameters=parameters,
                request_body=request_body,
                responses=responses,
                tags=tags,
                security=security
            )
            
        except Exception as e:
            logger.error(f"Error parsing route {rule.rule}: {e}")
            return None
    
    def _parse_docstring(self, docstring: str) -> Tuple[str, str]:
        """Parsear docstring para extraer resumen y descripción"""
        if not docstring:
            return "API Endpoint", "No description available"
        
        lines = docstring.strip().split('\n')
        summary = lines[0].strip()
        description = '\n'.join(lines[1:]).strip() if len(lines) > 1 else summary
        
        return summary, description
    
    def _extract_parameters(self, rule, view_func) -> List[Dict[str, Any]]:
        """Extraer parámetros del endpoint"""
        parameters = []
        
        try:
            # Parámetros de ruta
            for arg in rule.arguments:
                parameters.append({
                    "name": arg,
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                    "description": f"Path parameter: {arg}"
                })
            
            # Parámetros de query
            sig = inspect.signature(view_func)
            for param_name, param in sig.parameters.items():
                if param_name not in ['self', 'request', 'json']:
                    parameters.append({
                        "name": param_name,
                        "in": "query",
                        "required": param.default == inspect.Parameter.empty,
                        "schema": {"type": "string"},
                        "description": f"Query parameter: {param_name}"
                    })
            
        except Exception as e:
            logger.error(f"Error extracting parameters: {e}")
        
        return parameters
    
    def _extract_request_body(self, view_func) -> Optional[Dict[str, Any]]:
        """Extraer request body del endpoint"""
        try:
            sig = inspect.signature(view_func)
            
            # Buscar parámetro que acepte JSON
            for param_name, param in sig.parameters.items():
                if param_name in ['json', 'data', 'body']:
                    return {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/RequestData"}
                            }
                        }
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting request body: {e}")
            return None
    
    def _extract_responses(self, view_func) -> Dict[str, Dict[str, Any]]:
        """Extraer respuestas del endpoint"""
        responses = {
            "200": {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "schema": {"type": "object"}
                    }
                }
            },
            "400": {
                "description": "Bad request",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    }
                }
            },
            "401": {
                "description": "Unauthorized",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    }
                }
            },
            "404": {
                "description": "Not found",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    }
                }
            },
            "500": {
                "description": "Internal server error",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    }
                }
            }
        }
        
        return responses
    
    def _determine_tags(self, path: str) -> List[str]:
        """Determinar tags basado en la ruta"""
        if path.startswith('/products'):
            return ['Products']
        elif path.startswith('/prices'):
            return ['Prices']
        elif path.startswith('/analysis'):
            return ['Analysis']
        elif path.startswith('/competitors'):
            return ['Competitors']
        elif path.startswith('/reports'):
            return ['Reports']
        elif path.startswith('/admin'):
            return ['Admin']
        else:
            return ['General']
    
    def _determine_security(self, view_func) -> Optional[Dict[str, Any]]:
        """Determinar esquema de seguridad"""
        # Verificar si la función tiene decoradores de autenticación
        if hasattr(view_func, '__wrapped__'):
            # Función decorada, verificar si requiere autenticación
            return {"bearerAuth": []}
        
        return None
    
    def add_custom_endpoint(self, endpoint: APIEndpoint):
        """Agregar endpoint personalizado"""
        try:
            self.endpoints.append(endpoint)
            logger.info(f"Custom endpoint added: {endpoint.method} {endpoint.path}")
            
        except Exception as e:
            logger.error(f"Error adding custom endpoint: {e}")
    
    def add_custom_schema(self, schema: APISchema):
        """Agregar esquema personalizado"""
        try:
            self.schemas.append(schema)
            logger.info(f"Custom schema added: {schema.name}")
            
        except Exception as e:
            logger.error(f"Error adding custom schema: {e}")
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generar especificación OpenAPI"""
        try:
            # Configurar esquemas de seguridad
            self.security_schemes = {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                },
                "apiKey": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key"
                }
            }
            
            # Crear especificación OpenAPI
            openapi_spec = {
                "openapi": "3.0.3",
                "info": self.api_info,
                "servers": [
                    {"url": "http://localhost:5000", "description": "Development server"},
                    {"url": "https://api.company.com", "description": "Production server"}
                ],
                "paths": {},
                "components": {
                    "schemas": {},
                    "securitySchemes": self.security_schemes
                },
                "security": [{"bearerAuth": []}]
            }
            
            # Agregar endpoints
            for endpoint in self.endpoints:
                if endpoint.path not in openapi_spec["paths"]:
                    openapi_spec["paths"][endpoint.path] = {}
                
                endpoint_spec = {
                    "summary": endpoint.summary,
                    "description": endpoint.description,
                    "tags": endpoint.tags,
                    "parameters": endpoint.parameters,
                    "responses": endpoint.responses
                }
                
                if endpoint.request_body:
                    endpoint_spec["requestBody"] = endpoint.request_body
                
                if endpoint.security:
                    endpoint_spec["security"] = [endpoint.security]
                
                if endpoint.deprecated:
                    endpoint_spec["deprecated"] = True
                
                openapi_spec["paths"][endpoint.path][endpoint.method.lower()] = endpoint_spec
            
            # Agregar esquemas
            for schema in self.schemas:
                openapi_spec["components"]["schemas"][schema.name] = {
                    "type": schema.type,
                    "properties": schema.properties,
                    "required": schema.required,
                    "description": schema.description,
                    "example": schema.example
                }
            
            return openapi_spec
            
        except Exception as e:
            logger.error(f"Error generating OpenAPI spec: {e}")
            return {}
    
    def generate_swagger_ui_html(self, openapi_spec: Dict[str, Any]) -> str:
        """Generar HTML de Swagger UI"""
        try:
            html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
    <style>
        html {
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }
        *, *:before, *:after {
            box-sizing: inherit;
        }
        body {
            margin:0;
            background: #fafafa;
        }
        .swagger-ui .topbar {
            background-color: #2c3e50;
        }
        .swagger-ui .topbar .download-url-wrapper {
            display: none;
        }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: 'data:application/json;base64,{{ spec_base64 }}',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                tryItOutEnabled: true,
                requestInterceptor: function(request) {
                    // Add authentication header if available
                    const token = localStorage.getItem('auth_token');
                    if (token) {
                        request.headers['Authorization'] = 'Bearer ' + token;
                    }
                    return request;
                }
            });
        };
    </script>
</body>
</html>
            """
            
            # Codificar especificación en base64
            import base64
            spec_json = json.dumps(openapi_spec, indent=2)
            spec_base64 = base64.b64encode(spec_json.encode()).decode()
            
            # Renderizar template
            from jinja2 import Template
            template = Template(html_template)
            html_content = template.render(
                title=self.api_info["title"],
                spec_base64=spec_base64
            )
            
            return html_content
            
        except Exception as e:
            logger.error(f"Error generating Swagger UI HTML: {e}")
            return ""
    
    def generate_postman_collection(self, openapi_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generar colección de Postman"""
        try:
            collection = {
                "info": {
                    "name": self.api_info["title"],
                    "description": self.api_info["description"],
                    "version": self.api_info["version"],
                    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
                },
                "auth": {
                    "type": "bearer",
                    "bearer": [
                        {
                            "key": "token",
                            "value": "{{auth_token}}",
                            "type": "string"
                        }
                    ]
                },
                "variable": [
                    {
                        "key": "base_url",
                        "value": "http://localhost:5000",
                        "type": "string"
                    }
                ],
                "item": []
            }
            
            # Agrupar endpoints por tags
            endpoints_by_tag = {}
            for endpoint in self.endpoints:
                for tag in endpoint.tags:
                    if tag not in endpoints_by_tag:
                        endpoints_by_tag[tag] = []
                    endpoints_by_tag[tag].append(endpoint)
            
            # Crear items de Postman
            for tag, tag_endpoints in endpoints_by_tag.items():
                tag_item = {
                    "name": tag,
                    "item": []
                }
                
                for endpoint in tag_endpoints:
                    item = {
                        "name": endpoint.summary,
                        "request": {
                            "method": endpoint.method.upper(),
                            "header": [
                                {
                                    "key": "Content-Type",
                                    "value": "application/json",
                                    "type": "text"
                                }
                            ],
                            "url": {
                                "raw": "{{base_url}}" + endpoint.path,
                                "host": ["{{base_url}}"],
                                "path": endpoint.path.strip('/').split('/')
                            },
                            "description": endpoint.description
                        }
                    }
                    
                    # Agregar parámetros de query
                    if endpoint.parameters:
                        query_params = []
                        for param in endpoint.parameters:
                            if param["in"] == "query":
                                query_params.append({
                                    "key": param["name"],
                                    "value": "",
                                    "description": param["description"]
                                })
                        if query_params:
                            item["request"]["url"]["query"] = query_params
                    
                    # Agregar request body
                    if endpoint.request_body:
                        item["request"]["body"] = {
                            "mode": "raw",
                            "raw": "{\n  \"example\": \"data\"\n}",
                            "options": {
                                "raw": {
                                    "language": "json"
                                }
                            }
                        }
                    
                    tag_item["item"].append(item)
                
                collection["item"].append(tag_item)
            
            return collection
            
        except Exception as e:
            logger.error(f"Error generating Postman collection: {e}")
            return {}
    
    def generate_curl_examples(self, openapi_spec: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generar ejemplos de cURL"""
        try:
            curl_examples = {}
            
            for endpoint in self.endpoints:
                examples = []
                
                # Construir comando cURL básico
                curl_cmd = f"curl -X {endpoint.method.upper()}"
                
                # Agregar headers
                curl_cmd += " -H 'Content-Type: application/json'"
                curl_cmd += " -H 'Authorization: Bearer YOUR_TOKEN'"
                
                # Agregar URL
                curl_cmd += f" 'http://localhost:5000{endpoint.path}'"
                
                # Agregar request body si existe
                if endpoint.request_body:
                    curl_cmd += " -d '{\"example\": \"data\"}'"
                
                examples.append(curl_cmd)
                
                # Agregar ejemplo con parámetros
                if endpoint.parameters:
                    param_example = curl_cmd
                    for param in endpoint.parameters:
                        if param["in"] == "query":
                            param_example += f"&{param['name']}=example_value"
                    examples.append(param_example)
                
                curl_examples[f"{endpoint.method.upper()} {endpoint.path}"] = examples
            
            return curl_examples
            
        except Exception as e:
            logger.error(f"Error generating cURL examples: {e}")
            return {}
    
    def export_documentation(self, output_dir: str = "api_docs"):
        """Exportar documentación completa"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Generar especificación OpenAPI
            openapi_spec = self.generate_openapi_spec()
            
            # Exportar OpenAPI JSON
            with open(output_path / "openapi.json", "w") as f:
                json.dump(openapi_spec, f, indent=2)
            
            # Exportar OpenAPI YAML
            with open(output_path / "openapi.yaml", "w") as f:
                yaml.dump(openapi_spec, f, default_flow_style=False)
            
            # Generar y exportar Swagger UI HTML
            swagger_html = self.generate_swagger_ui_html(openapi_spec)
            with open(output_path / "swagger-ui.html", "w") as f:
                f.write(swagger_html)
            
            # Generar y exportar colección de Postman
            postman_collection = self.generate_postman_collection(openapi_spec)
            with open(output_path / "postman_collection.json", "w") as f:
                json.dump(postman_collection, f, indent=2)
            
            # Generar y exportar ejemplos de cURL
            curl_examples = self.generate_curl_examples(openapi_spec)
            with open(output_path / "curl_examples.json", "w") as f:
                json.dump(curl_examples, f, indent=2)
            
            # Generar documentación en Markdown
            markdown_doc = self.generate_markdown_documentation(openapi_spec)
            with open(output_path / "README.md", "w") as f:
                f.write(markdown_doc)
            
            logger.info(f"API documentation exported to {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting documentation: {e}")
    
    def generate_markdown_documentation(self, openapi_spec: Dict[str, Any]) -> str:
        """Generar documentación en Markdown"""
        try:
            md_content = f"""# {self.api_info['title']}

{self.api_info['description']}

## API Information

- **Version**: {self.api_info['version']}
- **Base URL**: http://localhost:5000
- **Contact**: {self.api_info.get('contact', {}).get('email', 'N/A')}

## Authentication

This API uses Bearer token authentication. Include the token in the Authorization header:

```
Authorization: Bearer YOUR_TOKEN
```

## Endpoints

"""
            
            # Agrupar endpoints por tags
            endpoints_by_tag = {}
            for endpoint in self.endpoints:
                for tag in endpoint.tags:
                    if tag not in endpoints_by_tag:
                        endpoints_by_tag[tag] = []
                    endpoints_by_tag[tag].append(endpoint)
            
            # Generar documentación por tag
            for tag, tag_endpoints in endpoints_by_tag.items():
                md_content += f"### {tag}\n\n"
                
                for endpoint in tag_endpoints:
                    md_content += f"#### {endpoint.method.upper()} {endpoint.path}\n\n"
                    md_content += f"**Summary**: {endpoint.summary}\n\n"
                    md_content += f"**Description**: {endpoint.description}\n\n"
                    
                    if endpoint.parameters:
                        md_content += "**Parameters**:\n\n"
                        for param in endpoint.parameters:
                            md_content += f"- `{param['name']}` ({param['in']}): {param['description']}\n"
                        md_content += "\n"
                    
                    if endpoint.request_body:
                        md_content += "**Request Body**: JSON object\n\n"
                    
                    md_content += "**Responses**:\n\n"
                    for status_code, response in endpoint.responses.items():
                        md_content += f"- `{status_code}`: {response['description']}\n"
                    
                    md_content += "\n"
            
            # Agregar esquemas
            md_content += "## Data Schemas\n\n"
            for schema in self.schemas:
                md_content += f"### {schema.name}\n\n"
                md_content += f"{schema.description}\n\n"
                md_content += "**Properties**:\n\n"
                for prop_name, prop_info in schema.properties.items():
                    required = " (required)" if prop_name in schema.required else ""
                    md_content += f"- `{prop_name}` ({prop_info.get('type', 'unknown')}): {prop_info.get('description', 'No description')}{required}\n"
                md_content += "\n"
            
            return md_content
            
        except Exception as e:
            logger.error(f"Error generating Markdown documentation: {e}")
            return ""

def main():
    """Función principal para demostrar generador de documentación"""
    print("=" * 60)
    print("API DOCUMENTATION GENERATOR - DEMO")
    print("=" * 60)
    
    # Inicializar generador de documentación
    doc_generator = APIDocumentationGenerator()
    
    # Analizar módulo de API
    print("Analyzing API module...")
    doc_generator.analyze_api_module()
    
    # Agregar endpoints personalizados de ejemplo
    print("Adding custom endpoints...")
    
    # Endpoint de ejemplo
    custom_endpoint = APIEndpoint(
        path="/api/v1/products",
        method="GET",
        summary="Get all products",
        description="Retrieve a list of all products with optional filtering and pagination",
        parameters=[
            {
                "name": "page",
                "in": "query",
                "required": False,
                "schema": {"type": "integer", "default": 1},
                "description": "Page number for pagination"
            },
            {
                "name": "limit",
                "in": "query",
                "required": False,
                "schema": {"type": "integer", "default": 10},
                "description": "Number of items per page"
            },
            {
                "name": "category",
                "in": "query",
                "required": False,
                "schema": {"type": "string"},
                "description": "Filter by product category"
            }
        ],
        request_body=None,
        responses={
            "200": {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "products": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Product"}
                                },
                                "total": {"type": "integer"},
                                "page": {"type": "integer"},
                                "limit": {"type": "integer"}
                            }
                        }
                    }
                }
            }
        },
        tags=["Products"],
        security={"bearerAuth": []}
    )
    doc_generator.add_custom_endpoint(custom_endpoint)
    
    # Endpoint POST de ejemplo
    post_endpoint = APIEndpoint(
        path="/api/v1/products",
        method="POST",
        summary="Create new product",
        description="Create a new product in the system",
        parameters=[],
        request_body={
            "required": True,
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/Product"}
                }
            }
        },
        responses={
            "201": {
                "description": "Product created successfully",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Product"}
                    }
                }
            }
        },
        tags=["Products"],
        security={"bearerAuth": []}
    )
    doc_generator.add_custom_endpoint(post_endpoint)
    
    # Generar especificación OpenAPI
    print("Generating OpenAPI specification...")
    openapi_spec = doc_generator.generate_openapi_spec()
    
    print(f"✓ Generated OpenAPI spec with {len(openapi_spec.get('paths', {}))} endpoints")
    print(f"✓ Generated {len(openapi_spec.get('components', {}).get('schemas', {}))} schemas")
    
    # Exportar documentación
    print("\nExporting documentation...")
    doc_generator.export_documentation("api_docs")
    
    print("✓ Documentation exported to api_docs/")
    print("  • openapi.json - OpenAPI specification (JSON)")
    print("  • openapi.yaml - OpenAPI specification (YAML)")
    print("  • swagger-ui.html - Interactive Swagger UI")
    print("  • postman_collection.json - Postman collection")
    print("  • curl_examples.json - cURL examples")
    print("  • README.md - Markdown documentation")
    
    # Generar ejemplos de cURL
    print("\nGenerating cURL examples...")
    curl_examples = doc_generator.generate_curl_examples(openapi_spec)
    
    print("Sample cURL commands:")
    for endpoint_name, examples in list(curl_examples.items())[:3]:
        print(f"\n{endpoint_name}:")
        for example in examples[:1]:  # Mostrar solo el primer ejemplo
            print(f"  {example}")
    
    print("\n" + "=" * 60)
    print("API DOCUMENTATION GENERATOR DEMO COMPLETED")
    print("=" * 60)
    print("📚 API documentation features:")
    print("  • Automatic OpenAPI 3.0 specification generation")
    print("  • Interactive Swagger UI")
    print("  • Postman collection export")
    print("  • cURL examples generation")
    print("  • Markdown documentation")
    print("  • Custom endpoint and schema support")
    print("  • Authentication documentation")
    print("  • Multiple export formats")
    print("  • Parameter and response documentation")

if __name__ == "__main__":
    main()






