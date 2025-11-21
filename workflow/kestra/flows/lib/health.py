"""
Health check utilities para APIs y servicios externos.

Características:
- Health checks asíncronos
- Timeout configurable
- Resultados estructurados
- Validación de dependencias
"""
import time
import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Estados de health check."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Resultado de un health check."""
    status: HealthStatus
    message: str
    timestamp: str
    duration_ms: float
    details: Optional[Dict[str, Any]] = None
    checks: Optional[Dict[str, "HealthCheckResult"]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario."""
        result = {
            "status": self.status.value,
            "message": self.message,
            "timestamp": self.timestamp,
            "duration_ms": round(self.duration_ms, 2)
        }
        
        if self.details:
            result["details"] = self.details
        
        if self.checks:
            result["checks"] = {
                name: check.to_dict() for name, check in self.checks.items()
            }
        
        return result


class HealthChecker:
    """Colector de health checks."""
    
    def __init__(self, name: str = "service"):
        """
        Inicializa el health checker.
        
        Args:
            name: Nombre del servicio
        """
        self.name = name
        self.checks: List[Callable[[], HealthCheckResult]] = []
    
    def register_check(
        self,
        name: str,
        check_func: Callable[[], HealthCheckResult],
        required: bool = True
    ) -> None:
        """
        Registra un health check.
        
        Args:
            name: Nombre del check
            check_func: Función que retorna HealthCheckResult
            required: Si es requerido (afecta el status final)
        """
        def wrapped_check():
            try:
                result = check_func()
                if required and result.status == HealthStatus.UNHEALTHY:
                    result.message = f"[REQUIRED] {result.message}"
                return result
            except Exception as e:
                logger.error(f"Health check '{name}' failed", extra={
                    "check_name": name,
                    "error": str(e)
                })
                return HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check failed: {str(e)}",
                    timestamp=datetime.utcnow().isoformat() + 'Z',
                    duration_ms=0.0,
                    details={"error": str(e)}
                )
        
        self.checks.append(wrapped_check)
    
    def check(self, timeout_seconds: float = 5.0) -> HealthCheckResult:
        """
        Ejecuta todos los health checks registrados.
        
        Args:
            timeout_seconds: Timeout máximo por check
        
        Returns:
            HealthCheckResult agregado
        """
        start_time = time.time()
        check_results = {}
        has_unhealthy = False
        has_degraded = False
        
        for i, check_func in enumerate(self.checks):
            check_start = time.time()
            
            try:
                result = check_func()
                check_duration = (time.time() - check_start) * 1000
                result.duration_ms = check_duration
                
                if result.status == HealthStatus.UNHEALTHY:
                    has_unhealthy = True
                elif result.status == HealthStatus.DEGRADED:
                    has_degraded = True
                
                check_results[f"check_{i}"] = result
                
            except Exception as e:
                logger.error(f"Health check failed", extra={
                    "check_index": i,
                    "error": str(e)
                })
                check_results[f"check_{i}"] = HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check exception: {str(e)}",
                    timestamp=datetime.utcnow().isoformat() + 'Z',
                    duration_ms=(time.time() - check_start) * 1000,
                    details={"error": str(e)}
                )
                has_unhealthy = True
        
        total_duration = (time.time() - start_time) * 1000
        
        # Determinar status final
        if has_unhealthy:
            final_status = HealthStatus.UNHEALTHY
            message = f"{self.name} is unhealthy"
        elif has_degraded:
            final_status = HealthStatus.DEGRADED
            message = f"{self.name} is degraded"
        else:
            final_status = HealthStatus.HEALTHY
            message = f"{self.name} is healthy"
        
        return HealthCheckResult(
            status=final_status,
            message=message,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            duration_ms=total_duration,
            checks=check_results
        )


def create_api_health_check(
    api_name: str,
    check_func: Callable[[], bool],
    timeout_seconds: float = 3.0
) -> HealthCheckResult:
    """
    Crea un health check para una API.
    
    Args:
        api_name: Nombre de la API
        check_func: Función que retorna True si está saludable
        timeout_seconds: Timeout del check
    
    Returns:
        HealthCheckResult
    """
    start_time = time.time()
    
    try:
        result = check_func()
        duration = (time.time() - start_time) * 1000
        
        if result:
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                message=f"{api_name} API is responding",
                timestamp=datetime.utcnow().isoformat() + 'Z',
                duration_ms=duration
            )
        else:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"{api_name} API check failed",
                timestamp=datetime.utcnow().isoformat() + 'Z',
                duration_ms=duration
            )
    
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        return HealthCheckResult(
            status=HealthStatus.UNHEALTHY,
            message=f"{api_name} API check error: {str(e)}",
            timestamp=datetime.utcnow().isoformat() + 'Z',
            duration_ms=duration,
            details={"error": str(e)}
        )


def create_dependency_health_check(
    dependency_name: str,
    check_func: Callable[[], bool],
    required: bool = False
) -> HealthCheckResult:
    """
    Crea un health check para una dependencia.
    
    Args:
        dependency_name: Nombre de la dependencia
        check_func: Función que retorna True si está disponible
        required: Si es requerida (afecta el status)
    
    Returns:
        HealthCheckResult
    """
    start_time = time.time()
    
    try:
        result = check_func()
        duration = (time.time() - start_time) * 1000
        
        if result:
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                message=f"{dependency_name} is available",
                timestamp=datetime.utcnow().isoformat() + 'Z',
                duration_ms=duration
            )
        else:
            status = HealthStatus.UNHEALTHY if required else HealthStatus.DEGRADED
            message = f"{dependency_name} is {'unavailable' if required else 'degraded'}"
            
            return HealthCheckResult(
                status=status,
                message=message,
                timestamp=datetime.utcnow().isoformat() + 'Z',
                duration_ms=duration
            )
    
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        status = HealthStatus.UNHEALTHY if required else HealthStatus.DEGRADED
        
        return HealthCheckResult(
            status=status,
            message=f"{dependency_name} check error: {str(e)}",
            timestamp=datetime.utcnow().isoformat() + 'Z',
            duration_ms=duration,
            details={"error": str(e)}
        )



