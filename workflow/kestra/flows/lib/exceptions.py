"""
Excepciones personalizadas para las librerías de workflows.

Características:
- Jerarquía de excepciones estructurada
- Contexto adicional en errores
- Tipos específicos por dominio
- Compatibilidad con logging estructurado
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class ErrorContext:
    """Contexto adicional para errores."""
    operation: Optional[str] = None
    resource_id: Optional[str] = None
    status_code: Optional[int] = None
    retry_count: Optional[int] = None
    api_response: Optional[Dict[str, Any]] = None
    request_params: Optional[Dict[str, Any]] = None
    extra: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el contexto a diccionario."""
        result = {}
        if self.operation:
            result["operation"] = self.operation
        if self.resource_id:
            result["resource_id"] = self.resource_id
        if self.status_code:
            result["status_code"] = self.status_code
        if self.retry_count is not None:
            result["retry_count"] = self.retry_count
        if self.api_response:
            result["api_response"] = self.api_response
        if self.request_params:
            result["request_params"] = self.request_params
        if self.extra:
            result.update(self.extra)
        return result


class APIError(Exception):
    """Excepción base para errores de API."""
    
    def __init__(
        self,
        message: str,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.context = context or ErrorContext()
        self.cause = cause
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la excepción a diccionario para logging."""
        result = {
            "error_type": self.__class__.__name__,
            "message": self.message
        }
        if self.context:
            result["context"] = self.context.to_dict()
        if self.cause:
            result["cause"] = str(self.cause)
        return result
    
    def __str__(self) -> str:
        context_str = ""
        if self.context:
            ctx_dict = self.context.to_dict()
            if ctx_dict:
                context_str = f" (context: {ctx_dict})"
        cause_str = f" (caused by: {self.cause})" if self.cause else ""
        return f"{self.message}{context_str}{cause_str}"


class HubSpotError(APIError):
    """Excepción base para errores de HubSpot."""
    pass


class HubSpotAPIError(HubSpotError):
    """Error al llamar a la API de HubSpot."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message, context=context, cause=cause)
        if status_code and not context:
            self.context = ErrorContext(status_code=status_code)
        elif status_code and context:
            context.status_code = status_code


class HubSpotRateLimitError(HubSpotAPIError):
    """Error de rate limiting en HubSpot."""
    
    def __init__(
        self,
        retry_after: Optional[int] = None,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None
    ):
        message = "HubSpot rate limit exceeded"
        if retry_after:
            message += f" (retry after {retry_after}s)"
        super().__init__(message, status_code=429, context=context, cause=cause)
        if retry_after:
            if not self.context:
                self.context = ErrorContext()
            self.context.extra = self.context.extra or {}
            self.context.extra["retry_after"] = retry_after


class HubSpotValidationError(HubSpotError):
    """Error de validación de datos de HubSpot."""
    pass


class HubSpotNotFoundError(HubSpotAPIError):
    """Recurso no encontrado en HubSpot."""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None
    ):
        message = f"{resource_type} '{resource_id}' not found in HubSpot"
        super().__init__(message, status_code=404, context=context, cause=cause)
        if not self.context:
            self.context = ErrorContext()
        self.context.resource_id = resource_id
        self.context.extra = self.context.extra or {}
        self.context.extra["resource_type"] = resource_type


class ManyChatError(APIError):
    """Excepción base para errores de ManyChat."""
    pass


class ManyChatAPIError(ManyChatError):
    """Error al llamar a la API de ManyChat."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message, context=context, cause=cause)
        if status_code and not context:
            self.context = ErrorContext(status_code=status_code)
        elif status_code and context:
            context.status_code = status_code


class ManyChatRateLimitError(ManyChatAPIError):
    """Error de rate limiting en ManyChat."""
    
    def __init__(
        self,
        retry_after: Optional[int] = None,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None
    ):
        message = "ManyChat rate limit exceeded"
        if retry_after:
            message += f" (retry after {retry_after}s)"
        super().__init__(message, status_code=429, context=context, cause=cause)
        if retry_after:
            if not self.context:
                self.context = ErrorContext()
            self.context.extra = self.context.extra or {}
            self.context.extra["retry_after"] = retry_after


class ManyChatValidationError(ManyChatError):
    """Error de validación de datos de ManyChat."""
    pass


class ConfigurationError(APIError):
    """Error de configuración."""
    pass


class CircuitBreakerOpenError(APIError):
    """Error cuando el circuit breaker está abierto."""
    
    def __init__(
        self,
        service_name: str,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None
    ):
        message = f"Circuit breaker is OPEN for {service_name}"
        super().__init__(message, context=context, cause=cause)
        if not self.context:
            self.context = ErrorContext()
        self.context.extra = self.context.extra or {}
        self.context.extra["service_name"] = service_name


class TimeoutError(APIError):
    """Error de timeout."""
    
    def __init__(
        self,
        operation: str,
        timeout_seconds: float,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None
    ):
        message = f"Operation '{operation}' timed out after {timeout_seconds}s"
        super().__init__(message, context=context, cause=cause)
        if not self.context:
            self.context = ErrorContext(operation=operation)
        self.context.extra = self.context.extra or {}
        self.context.extra["timeout_seconds"] = timeout_seconds


def enrich_error(
    error: Exception,
    operation: Optional[str] = None,
    resource_id: Optional[str] = None,
    **extra
) -> APIError:
    """
    Enriquece un error genérico con contexto adicional.
    
    Args:
        error: Excepción original
        operation: Nombre de la operación
        resource_id: ID del recurso
        **extra: Campos adicionales
    
    Returns:
        APIError enriquecido
    """
    if isinstance(error, APIError):
        # Ya es una APIError, solo enriquecer contexto
        if not error.context:
            error.context = ErrorContext()
        if operation:
            error.context.operation = operation
        if resource_id:
            error.context.resource_id = resource_id
        if extra:
            error.context.extra = error.context.extra or {}
            error.context.extra.update(extra)
        return error
    
    # Convertir a APIError genérico
    context = ErrorContext(
        operation=operation,
        resource_id=resource_id,
        extra=extra if extra else None
    )
    return APIError(str(error), context=context, cause=error)


