"""
Manejador Avanzado de Errores
==============================

Manejo robusto de errores con retry, circuit breaker y logging detallado.
"""

from typing import Dict, Any, Optional, Callable, TypeVar
from functools import wraps
import logging
from datetime import datetime, timedelta
from enum import Enum
import time

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ErrorSeverity(Enum):
    """Severidad de errores"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CircuitState(Enum):
    """Estado del circuit breaker"""
    CLOSED = "closed"  # Normal
    OPEN = "open"      # Fallando
    HALF_OPEN = "half_open"  # Probando


class CircuitBreaker:
    """Circuit Breaker para proteger servicios"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs):
        """Ejecuta función con circuit breaker"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Verifica si se debe intentar reset"""
        if self.last_failure_time is None:
            return True
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout
    
    def _on_success(self):
        """Maneja éxito"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Maneja fallo"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(
                f"Circuit breaker OPEN after {self.failure_count} failures"
            )


def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Decorador para retry con backoff exponencial"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        logger.error(
                            f"Failed after {max_attempts} attempts: {e}"
                        )
                        raise
                    
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                    delay *= backoff_factor
            
            return None
        return wrapper
    return decorator


class ErrorHandler:
    """Manejador centralizado de errores"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_log: list = []
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    def get_circuit_breaker(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60
    ) -> CircuitBreaker:
        """Obtiene o crea circuit breaker"""
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout
            )
        return self.circuit_breakers[name]
    
    def handle_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        severity: ErrorSeverity = ErrorSeverity.MEDIUM
    ) -> Dict[str, Any]:
        """Maneja error y retorna información estructurada"""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "severity": severity.value,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "traceback": None
        }
        
        # Agregar traceback si está disponible
        import traceback
        error_info["traceback"] = traceback.format_exc()
        
        # Log según severidad
        if severity == ErrorSeverity.CRITICAL:
            self.logger.critical(
                f"CRITICAL ERROR: {error_info['error_message']}",
                extra=error_info
            )
        elif severity == ErrorSeverity.HIGH:
            self.logger.error(
                f"HIGH ERROR: {error_info['error_message']}",
                extra=error_info
            )
        elif severity == ErrorSeverity.MEDIUM:
            self.logger.warning(
                f"MEDIUM ERROR: {error_info['error_message']}",
                extra=error_info
            )
        else:
            self.logger.info(
                f"LOW ERROR: {error_info['error_message']}",
                extra=error_info
            )
        
        # Guardar en log
        self.error_log.append(error_info)
        
        # Mantener solo últimos 100 errores
        if len(self.error_log) > 100:
            self.error_log = self.error_log[-100:]
        
        return error_info
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Obtiene resumen de errores"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent_errors = [
            e for e in self.error_log
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ]
        
        by_type = {}
        by_severity = {}
        
        for error in recent_errors:
            error_type = error["error_type"]
            severity = error["severity"]
            
            by_type[error_type] = by_type.get(error_type, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            "total_errors": len(recent_errors),
            "by_type": by_type,
            "by_severity": by_severity,
            "recent_errors": recent_errors[-10:]  # Últimos 10
        }

