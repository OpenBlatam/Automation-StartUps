"""
Circuit Breaker para Servicios Externos
Protección contra fallos en cascada
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Estados del circuit breaker"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuración del circuit breaker"""
    failure_threshold: int = 5  # Abrir después de N fallos
    success_threshold: int = 2  # Cerrar después de N éxitos (half-open)
    timeout_seconds: int = 60  # Tiempo antes de intentar half-open
    expected_exception: type = Exception


class CircuitBreaker:
    """Circuit breaker para servicios externos"""
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ):
        """
        Args:
            name: Nombre del circuit breaker
            config: Configuración
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_state_change: datetime = datetime.now()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Ejecuta una función con protección del circuit breaker"""
        if self.state == CircuitState.OPEN:
            # Verificar si debemos intentar half-open
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logger.info(f"Circuit breaker {self.name} entering HALF_OPEN state")
            else:
                raise Exception(
                    f"Circuit breaker {self.name} is OPEN. "
                    f"Service unavailable. Last failure: {self.last_failure_time}"
                )
        
        try:
            result = func(*args, **kwargs)
            
            # Registro de éxito
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self._reset()
                    logger.info(f"Circuit breaker {self.name} reset to CLOSED")
            else:
                # Reset contador de fallos en estado cerrado
                self.failure_count = 0
            
            return result
            
        except self.config.expected_exception as e:
            self._record_failure()
            raise
        except Exception as e:
            # Solo registrar si es el tipo de excepción esperado
            if isinstance(e, self.config.expected_exception):
                self._record_failure()
            raise
    
    def _record_failure(self) -> None:
        """Registra un fallo"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            # Fallo en half-open, volver a open
            self.state = CircuitState.OPEN
            self.last_state_change = datetime.now()
            logger.warning(f"Circuit breaker {self.name} back to OPEN state")
        
        elif self.failure_count >= self.config.failure_threshold:
            # Abrir circuit breaker
            self.state = CircuitState.OPEN
            self.last_state_change = datetime.now()
            logger.error(
                f"Circuit breaker {self.name} opened after {self.failure_count} failures"
            )
    
    def _should_attempt_reset(self) -> bool:
        """Verifica si debemos intentar resetear"""
        if self.last_failure_time is None:
            return True
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.config.timeout_seconds
    
    def _reset(self) -> None:
        """Resetea el circuit breaker a estado cerrado"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_state_change = datetime.now()
    
    def get_state(self) -> Dict[str, Any]:
        """Obtiene el estado actual"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_state_change": self.last_state_change.isoformat()
        }


class PayrollCircuitBreakers:
    """Circuit breakers para servicios de nómina"""
    
    def __init__(self):
        """Inicializa circuit breakers para diferentes servicios"""
        # Circuit breaker para OCR
        self.ocr = CircuitBreaker(
            "ocr_service",
            CircuitBreakerConfig(
                failure_threshold=5,
                success_threshold=2,
                timeout_seconds=60,
                expected_exception=Exception
            )
        )
        
        # Circuit breaker para notificaciones
        self.notifications = CircuitBreaker(
            "notification_service",
            CircuitBreakerConfig(
                failure_threshold=10,
                success_threshold=3,
                timeout_seconds=30,
                expected_exception=Exception
            )
        )
        
        # Circuit breaker para integraciones externas
        self.external_integrations = CircuitBreaker(
            "external_integrations",
            CircuitBreakerConfig(
                failure_threshold=5,
                success_threshold=2,
                timeout_seconds=120,
                expected_exception=Exception
            )
        )
    
    def call_ocr(self, func: Callable, *args, **kwargs) -> Any:
        """Ejecuta función OCR con circuit breaker"""
        return self.ocr.call(func, *args, **kwargs)
    
    def call_notification(self, func: Callable, *args, **kwargs) -> Any:
        """Ejecuta función de notificación con circuit breaker"""
        return self.notifications.call(func, *args, **kwargs)
    
    def call_integration(self, func: Callable, *args, **kwargs) -> Any:
        """Ejecuta función de integración con circuit breaker"""
        return self.external_integrations.call(func, *args, **kwargs)
    
    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene estados de todos los circuit breakers"""
        return {
            "ocr": self.ocr.get_state(),
            "notifications": self.notifications.get_state(),
            "external_integrations": self.external_integrations.get_state()
        }

