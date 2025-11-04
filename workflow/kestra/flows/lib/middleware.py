"""
Sistema de middleware/interceptors para clientes HTTP.

Características:
- Request/response interceptors
- Pipeline de procesamiento
- Extensibilidad fácil
- Logging automático
- Métricas automáticas
"""
import logging
import time
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class Request:
    """Modelo de request para interceptors."""
    method: str
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    params: Optional[Dict[str, Any]] = None
    json: Optional[Dict[str, Any]] = None
    data: Optional[Any] = None
    timeout: Optional[float] = None
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para logging."""
        return {
            "method": self.method,
            "url": self.url,
            "headers": {k: "***" if "auth" in k.lower() else v for k, v in self.headers.items()},
            "params": self.params,
            "has_json": bool(self.json),
            "has_data": bool(self.data),
            "timeout": self.timeout,
            "extra": self.extra
        }


@dataclass
class Response:
    """Modelo de response para interceptors."""
    status_code: int
    headers: Dict[str, str] = field(default_factory=dict)
    data: Optional[Any] = None
    elapsed_seconds: Optional[float] = None
    request: Optional[Request] = None
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para logging."""
        return {
            "status_code": self.status_code,
            "headers": dict(self.headers),
            "has_data": bool(self.data),
            "elapsed_seconds": self.elapsed_seconds,
            "request_method": self.request.method if self.request else None,
            "request_url": self.request.url if self.request else None,
            "extra": self.extra
        }


class Middleware(ABC):
    """Interfaz base para middleware."""
    
    @abstractmethod
    def before_request(self, request: Request) -> Request:
        """
        Intercepta el request antes de enviarlo.
        
        Args:
            request: Request a interceptar
        
        Returns:
            Request (posiblemente modificado)
        """
        pass
    
    @abstractmethod
    def after_response(self, response: Response) -> Response:
        """
        Intercepta el response después de recibirlo.
        
        Args:
            response: Response a interceptar
        
        Returns:
            Response (posiblemente modificado)
        """
        pass
    
    def on_error(self, error: Exception, request: Request) -> None:
        """
        Maneja errores durante el request.
        
        Args:
            error: Excepción ocurrida
            request: Request que causó el error
        """
        pass


class LoggingMiddleware(Middleware):
    """Middleware para logging estructurado."""
    
    def __init__(self, log_level: int = logging.INFO):
        self.log_level = log_level
    
    def before_request(self, request: Request) -> Request:
        """Log del request."""
        logger.log(
            self.log_level,
            "HTTP request",
            extra=request.to_dict()
        )
        return request
    
    def after_response(self, response: Response) -> Response:
        """Log del response."""
        logger.log(
            self.log_level,
            "HTTP response",
            extra=response.to_dict()
        )
        return response
    
    def on_error(self, error: Exception, request: Request) -> None:
        """Log del error."""
        logger.error(
            "HTTP request failed",
            extra={
                **request.to_dict(),
                "error": str(error),
                "error_type": type(error).__name__
            },
            exc_info=True
        )


class MetricsMiddleware(Middleware):
    """Middleware para registrar métricas."""
    
    def __init__(self, metrics_collector=None):
        self.metrics = metrics_collector
    
    def before_request(self, request: Request) -> Request:
        """Inicia timer para métricas."""
        if self.metrics:
            request.extra["_metrics_timer"] = f"http_{request.method.lower()}_{id(request)}"
            self.metrics.start_timer(request.extra["_metrics_timer"])
        return request
    
    def after_response(self, response: Response) -> Response:
        """Registra métricas del response."""
        if self.metrics and response.request:
            timer_key = response.request.extra.get("_metrics_timer")
            if timer_key:
                duration = self.metrics.record_duration(timer_key)
                self.metrics.add_histogram(
                    "http_request_duration_seconds",
                    duration,
                    labels={
                        "method": response.request.method,
                        "status_code": str(response.status_code)
                    }
                )
                self.metrics.add_counter(
                    "http_requests_total",
                    value=1,
                    labels={
                        "method": response.request.method,
                        "status_code": str(response.status_code)
                    }
                )
        return response
    
    def on_error(self, error: Exception, request: Request) -> None:
        """Registra métricas de error."""
        if self.metrics:
            timer_key = request.extra.get("_metrics_timer")
            if timer_key:
                self.metrics.record_duration(timer_key)
            self.metrics.add_counter(
                "http_requests_total",
                value=1,
                labels={
                    "method": request.method,
                    "status_code": "error"
                }
            )


class RetryMiddleware(Middleware):
    """Middleware para retry automático (usado con tenacity normalmente)."""
    
    def before_request(self, request: Request) -> Request:
        """Marca intento en request."""
        request.extra["_attempt"] = request.extra.get("_attempt", 0) + 1
        return request
    
    def after_response(self, response: Response) -> Response:
        """Verifica si necesita retry."""
        # La lógica de retry se maneja en el cliente, esto solo marca
        return response
    
    def on_error(self, error: Exception, request: Request) -> None:
        """Marca intento fallido."""
        request.extra["_failed_attempt"] = request.extra.get("_failed_attempt", 0) + 1


class HeaderMiddleware(Middleware):
    """Middleware para agregar headers automáticamente."""
    
    def __init__(self, headers: Dict[str, str]):
        self.headers = headers
    
    def before_request(self, request: Request) -> Request:
        """Agrega headers al request."""
        request.headers.update(self.headers)
        return request
    
    def after_response(self, response: Response) -> Response:
        """No modifica response."""
        return response
    
    def on_error(self, error: Exception, request: Request) -> None:
        """No hace nada en error."""
        pass


class MiddlewarePipeline:
    """Pipeline de middleware para procesar requests/responses."""
    
    def __init__(self, middlewares: Optional[List[Middleware]] = None):
        self.middlewares: List[Middleware] = middlewares or []
    
    def add(self, middleware: Middleware) -> "MiddlewarePipeline":
        """Agrega un middleware al pipeline."""
        self.middlewares.append(middleware)
        return self
    
    def before_request(self, request: Request) -> Request:
        """Aplica todos los middlewares antes del request."""
        for middleware in self.middlewares:
            request = middleware.before_request(request)
        return request
    
    def after_response(self, response: Response) -> Response:
        """Aplica todos los middlewares después del response."""
        for middleware in reversed(self.middlewares):
            response = middleware.after_response(response)
        return response
    
    def on_error(self, error: Exception, request: Request) -> None:
        """Propaga error a todos los middlewares."""
        for middleware in reversed(self.middlewares):
            try:
                middleware.on_error(error, request)
            except Exception as e:
                logger.warning(f"Middleware {type(middleware).__name__} failed in on_error: {e}")


def create_default_pipeline(
    metrics_collector=None,
    log_level: int = logging.INFO,
    extra_headers: Optional[Dict[str, str]] = None
) -> MiddlewarePipeline:
    """
    Crea un pipeline de middleware por defecto.
    
    Args:
        metrics_collector: Collector de métricas (opcional)
        log_level: Nivel de logging
        extra_headers: Headers adicionales (opcional)
    
    Returns:
        Pipeline configurado
    """
    pipeline = MiddlewarePipeline()
    
    # Logging primero (para capturar todo)
    pipeline.add(LoggingMiddleware(log_level=log_level))
    
    # Metrics
    if metrics_collector:
        pipeline.add(MetricsMiddleware(metrics_collector))
    
    # Retry tracking
    pipeline.add(RetryMiddleware())
    
    # Headers adicionales
    if extra_headers:
        pipeline.add(HeaderMiddleware(extra_headers))
    
    return pipeline


