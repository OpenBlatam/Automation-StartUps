"""
Manejo mejorado de errores y excepciones personalizadas.

Incluye:
- Excepciones más descriptivas
- Helpers para manejo de errores
- Mensajes de error mejorados
"""

from __future__ import annotations

import logging
import traceback
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class AdsReportingError(Exception):
    """Excepción base para ads reporting."""
    
    def __init__(
        self,
        message: str,
        platform: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa excepción.
        
        Args:
            message: Mensaje de error
            platform: Plataforma relacionada (opcional)
            error_code: Código de error (opcional)
            details: Detalles adicionales (opcional)
        """
        super().__init__(message)
        self.message = message
        self.platform = platform
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self) -> str:
        parts = [self.message]
        if self.platform:
            parts.append(f"[Platform: {self.platform}]")
        if self.error_code:
            parts.append(f"[Code: {self.error_code}]")
        return " ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte excepción a diccionario."""
        return {
            "error_type": type(self).__name__,
            "message": self.message,
            "platform": self.platform,
            "error_code": self.error_code,
            "details": self.details
        }


class ConfigurationError(AdsReportingError):
    """Error de configuración."""
    pass


class AuthenticationError(AdsReportingError):
    """Error de autenticación."""
    pass


class APIError(AdsReportingError):
    """Error de API."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Inicializa error de API.
        
        Args:
            message: Mensaje de error
            status_code: Código de estado HTTP
            response_data: Datos de respuesta (opcional)
            **kwargs: Argumentos adicionales
        """
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.response_data = response_data or {}
        if status_code:
            self.details["status_code"] = status_code
        if response_data:
            self.details["response_data"] = response_data


class ValidationError(AdsReportingError):
    """Error de validación."""
    
    def __init__(
        self,
        message: str,
        validation_errors: Optional[list] = None,
        **kwargs
    ):
        """
        Inicializa error de validación.
        
        Args:
            message: Mensaje de error
            validation_errors: Lista de errores de validación
            **kwargs: Argumentos adicionales
        """
        super().__init__(message, **kwargs)
        self.validation_errors = validation_errors or []
        if validation_errors:
            self.details["validation_errors"] = validation_errors


class DataQualityError(AdsReportingError):
    """Error de calidad de datos."""
    pass


class RateLimitError(APIError):
    """Error de rate limiting."""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        """
        Inicializa error de rate limit.
        
        Args:
            message: Mensaje de error
            retry_after: Segundos hasta reintento
            **kwargs: Argumentos adicionales
        """
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after
        if retry_after:
            self.details["retry_after"] = retry_after


def format_error_message(
    error: Exception,
    include_traceback: bool = False
) -> str:
    """
    Formatea mensaje de error de forma legible.
    
    Args:
        error: Excepción a formatear
        include_traceback: Si incluir traceback completo
        
    Returns:
        String con mensaje formateado
    """
    if isinstance(error, AdsReportingError):
        lines = [
            f"Error: {error.message}",
        ]
        
        if error.platform:
            lines.append(f"Platform: {error.platform}")
        
        if error.error_code:
            lines.append(f"Error Code: {error.error_code}")
        
        if error.details:
            lines.append("Details:")
            for key, value in error.details.items():
                if not isinstance(value, (dict, list)) or len(str(value)) < 200:
                    lines.append(f"  {key}: {value}")
        
        if include_traceback:
            lines.append("\nTraceback:")
            lines.append(traceback.format_exc())
        
        return "\n".join(lines)
    else:
        lines = [
            f"Error: {str(error)}",
            f"Type: {type(error).__name__}"
        ]
        
        if include_traceback:
            lines.append("\nTraceback:")
            lines.append(traceback.format_exc())
        
        return "\n".join(lines)


def safe_execute(
    func: callable,
    *args,
    default_return: Any = None,
    error_message: Optional[str] = None,
    **kwargs
) -> Any:
    """
    Ejecuta función de forma segura con manejo de errores.
    
    Args:
        func: Función a ejecutar
        *args: Argumentos posicionales
        default_return: Valor a retornar en caso de error
        error_message: Mensaje personalizado de error
        **kwargs: Argumentos keyword
        
    Returns:
        Resultado de la función o default_return
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        msg = error_message or f"Error executing {func.__name__}"
        logger.error(f"{msg}: {str(e)}", exc_info=True)
        return default_return


def get_error_summary(
    errors: list[Exception]
) -> Dict[str, Any]:
    """
    Crea resumen de errores.
    
    Args:
        errors: Lista de excepciones
        
    Returns:
        Diccionario con resumen
    """
    summary = {
        "total_errors": len(errors),
        "by_type": {},
        "by_platform": {},
        "errors": []
    }
    
    for error in errors:
        error_type = type(error).__name__
        summary["by_type"][error_type] = summary["by_type"].get(error_type, 0) + 1
        
        if isinstance(error, AdsReportingError):
            platform = error.platform or "unknown"
            summary["by_platform"][platform] = summary["by_platform"].get(platform, 0) + 1
            
            summary["errors"].append(error.to_dict())
        else:
            summary["errors"].append({
                "error_type": error_type,
                "message": str(error)
            })
    
    return summary

