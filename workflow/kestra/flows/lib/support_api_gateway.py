"""
Sistema de API Gateway y Gestión de APIs.

Maneja versionado, routing, autenticación y rate limiting de APIs.
"""
import logging
import hashlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class APIVersion(Enum):
    """Versiones de API."""
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"
    BETA = "beta"
    ALPHA = "alpha"


class RequestMethod(Enum):
    """Métodos HTTP."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


@dataclass
class APIEndpoint:
    """Endpoint de API."""
    endpoint_id: str
    path: str
    method: RequestMethod
    version: APIVersion
    handler: callable
    rate_limit: Optional[int] = None  # Requests por minuto
    requires_auth: bool = True
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class APIRequest:
    """Request de API."""
    request_id: str
    endpoint: str
    method: str
    headers: Dict[str, str]
    params: Dict[str, Any]
    body: Optional[Dict[str, Any]] = None
    client_ip: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class APIGateway:
    """Gateway de API."""
    
    def __init__(self):
        """Inicializa gateway."""
        self.endpoints: Dict[str, APIEndpoint] = {}
        self.request_history: List[APIRequest] = []
        self.rate_limiter = None  # Se puede inyectar
    
    def register_endpoint(self, endpoint: APIEndpoint):
        """Registra un endpoint."""
        key = f"{endpoint.method.value}:{endpoint.path}:{endpoint.version.value}"
        self.endpoints[key] = endpoint
        logger.info(f"Registered endpoint: {endpoint.method.value} {endpoint.path} ({endpoint.version.value})")
    
    def handle_request(
        self,
        path: str,
        method: str,
        version: APIVersion = APIVersion.V1,
        headers: Dict[str, str] = None,
        params: Dict[str, Any] = None,
        body: Dict[str, Any] = None,
        client_ip: str = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Maneja un request de API.
        
        Args:
            path: Ruta del endpoint
            method: Método HTTP
            version: Versión de API
            headers: Headers HTTP
            params: Parámetros de query
            body: Body del request
            client_ip: IP del cliente
            user_id: ID del usuario
            
        Returns:
            Respuesta del endpoint
        """
        request_id = f"req-{hashlib.md5(f'{path}{method}{datetime.now()}'.encode()).hexdigest()[:12]}"
        
        # Crear request
        api_request = APIRequest(
            request_id=request_id,
            endpoint=path,
            method=method,
            headers=headers or {},
            params=params or {},
            body=body,
            client_ip=client_ip,
            user_id=user_id
        )
        
        self.request_history.append(api_request)
        
        # Mantener solo últimos 1000 requests
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]
        
        # Buscar endpoint
        method_enum = RequestMethod(method.upper())
        key = f"{method_enum.value}:{path}:{version.value}"
        
        endpoint = self.endpoints.get(key)
        
        if not endpoint:
            # Intentar sin versión específica
            for v in [APIVersion.V1, APIVersion.V2, APIVersion.V3]:
                key_alt = f"{method_enum.value}:{path}:{v.value}"
                endpoint = self.endpoints.get(key_alt)
                if endpoint:
                    break
        
        if not endpoint:
            return {
                "error": "Endpoint not found",
                "status_code": 404,
                "request_id": request_id
            }
        
        # Verificar autenticación
        if endpoint.requires_auth:
            if not user_id and not headers.get("Authorization"):
                return {
                    "error": "Authentication required",
                    "status_code": 401,
                    "request_id": request_id
                }
        
        # Verificar rate limit
        if endpoint.rate_limit and self.rate_limiter:
            rate_limit_key = f"{endpoint.endpoint_id}:{client_ip or user_id or 'anonymous'}"
            result = self.rate_limiter.check_rate_limit(
                rate_limit_key,
                max_requests=endpoint.rate_limit,
                window_seconds=60
            )
            
            if not result.allowed:
                return {
                    "error": "Rate limit exceeded",
                    "status_code": 429,
                    "retry_after": result.retry_after_seconds,
                    "request_id": request_id
                }
        
        # Ejecutar handler
        try:
            response = endpoint.handler(
                params=api_request.params,
                body=api_request.body,
                headers=api_request.headers,
                user_id=user_id
            )
            
            return {
                "data": response,
                "status_code": 200,
                "request_id": request_id,
                "version": endpoint.version.value
            }
            
        except Exception as e:
            logger.error(f"Error handling request {request_id}: {e}")
            return {
                "error": str(e),
                "status_code": 500,
                "request_id": request_id
            }
    
    def get_endpoints(self, version: Optional[APIVersion] = None) -> List[Dict[str, Any]]:
        """
        Obtiene lista de endpoints.
        
        Args:
            version: Filtrar por versión (opcional)
            
        Returns:
            Lista de endpoints
        """
        endpoints = []
        
        for endpoint in self.endpoints.values():
            if version and endpoint.version != version:
                continue
            
            endpoints.append({
                "id": endpoint.endpoint_id,
                "path": endpoint.path,
                "method": endpoint.method.value,
                "version": endpoint.version.value,
                "rate_limit": endpoint.rate_limit,
                "requires_auth": endpoint.requires_auth
            })
        
        return endpoints
    
    def get_api_stats(self, hours: int = 24) -> Dict[str, Any]:
        """
        Obtiene estadísticas de API.
        
        Args:
            hours: Horas hacia atrás
            
        Returns:
            Estadísticas
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_requests = [r for r in self.request_history if r.timestamp >= cutoff]
        
        total_requests = len(recent_requests)
        successful = sum(1 for r in recent_requests if True)  # Simplificado
        
        by_method = {}
        by_endpoint = {}
        by_version = {}
        
        for req in recent_requests:
            method = req.method
            by_method[method] = by_method.get(method, 0) + 1
            
            endpoint = req.endpoint
            by_endpoint[endpoint] = by_endpoint.get(endpoint, 0) + 1
            
            # Extraer versión de path si es posible
            if "/v" in endpoint:
                version = endpoint.split("/v")[1].split("/")[0] if "/v" in endpoint else "v1"
                by_version[version] = by_version.get(version, 0) + 1
        
        return {
            "period_hours": hours,
            "total_requests": total_requests,
            "successful_requests": successful,
            "by_method": by_method,
            "by_endpoint": dict(sorted(by_endpoint.items(), key=lambda x: x[1], reverse=True)[:10]),
            "by_version": by_version
        }

