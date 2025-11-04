"""
Excepciones personalizadas mejoradas para ads reporting.

Incluye:
- Jerarquía de excepciones bien definida
- Contexto adicional en excepciones
- Helpers para manejo de errores
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class AdsReportingError(Exception):
    """Excepción base para todos los errores de ads reporting."""
    
    def __init__(
        self,
        message: str,
        platform: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.platform = platform
        self.context = context or {}
    
    def __str__(self) -> str:
        base = self.message
        if self.platform:
            base = f"[{self.platform}] {base}"
        if self.context:
            base += f" | Context: {self.context}"
        return base
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte excepción a diccionario."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "platform": self.platform,
            "context": self.context
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
        platform: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, platform, context)
        self.status_code = status_code
        if status_code:
            self.context["status_code"] = status_code


class RateLimitError(APIError):
    """Error de rate limiting."""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        platform: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=429, platform=platform, context=context)
        self.retry_after = retry_after
        if retry_after:
            self.context["retry_after"] = retry_after


class ValidationError(AdsReportingError):
    """Error de validación."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        platform: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, platform, context)
        self.field = field
        self.value = value
        if field:
            self.context["field"] = field
        if value is not None:
            self.context["value"] = str(value)[:100]  # Limitar tamaño


class DataQualityError(AdsReportingError):
    """Error de calidad de datos."""
    
    def __init__(
        self,
        message: str,
        quality_issues: Optional[list] = None,
        platform: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, platform, context)
        self.quality_issues = quality_issues or []
        if quality_issues:
            self.context["quality_issues_count"] = len(quality_issues)


class ExtractionError(AdsReportingError):
    """Error durante extracción de datos."""
    
    def __init__(
        self,
        message: str,
        records_extracted: int = 0,
        platform: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, platform, context)
        self.records_extracted = records_extracted
        self.context["records_extracted"] = records_extracted


class StorageError(AdsReportingError):
    """Error durante almacenamiento."""
    
    def __init__(
        self,
        message: str,
        table_name: Optional[str] = None,
        records_saved: int = 0,
        platform: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, platform, context)
        self.table_name = table_name
        self.records_saved = records_saved
        if table_name:
            self.context["table_name"] = table_name
        self.context["records_saved"] = records_saved


class ProcessingError(AdsReportingError):
    """Error durante procesamiento."""
    pass


def create_error_summary(errors: list) -> Dict[str, Any]:
    """
    Crea resumen de errores.
    
    Args:
        errors: Lista de excepciones o dicts de error
        
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
        if isinstance(error, AdsReportingError):
            error_dict = error.to_dict()
        elif isinstance(error, dict):
            error_dict = error
        else:
            error_dict = {
                "error_type": type(error).__name__,
                "message": str(error)
            }
        
        # Contar por tipo
        error_type = error_dict.get("error_type", "Unknown")
        summary["by_type"][error_type] = summary["by_type"].get(error_type, 0) + 1
        
        # Contar por plataforma
        platform = error_dict.get("platform", "unknown")
        summary["by_platform"][platform] = summary["by_platform"].get(platform, 0) + 1
        
        summary["errors"].append(error_dict)
    
    return summary

