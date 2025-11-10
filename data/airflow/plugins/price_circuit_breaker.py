"""
Circuit Breaker para Protección de APIs de Precios

Previene fallos en cascada y mejora la resiliencia
"""

import logging
import time
from typing import Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Estados del circuit breaker"""
    CLOSED = "closed"  # Normal, permite requests
    OPEN = "open"  # Falló, bloquea requests
    HALF_OPEN = "half_open"  # Probando si el servicio se recuperó


@dataclass
class CircuitBreakerConfig:
    """Configuración del circuit breaker"""
    failure_threshold: int = 5  # Fallos antes de abrir
    success_threshold: int = 2  # Éxitos para cerrar desde half_open
    timeout_seconds: int = 60  # Tiempo antes de intentar half_open
    expected_exception: type = Exception  # Excepciones que cuentan como fallos


class PriceCircuitBreaker:
    """Circuit Breaker para proteger integraciones de precios"""
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Ejecuta una función con protección de circuit breaker.
        
        Args:
            func: Función a ejecutar
            *args, **kwargs: Argumentos de la función
            
        Returns:
            Resultado de la función
            
        Raises:
            Exception: Si el circuit breaker está abierto o la función falla
        """
        # Verificar estado
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logger.info(f"Circuit breaker {self.name} movido a HALF_OPEN")
            else:
                raise Exception(
                    f"Circuit breaker {self.name} is OPEN. "
                    f"Last failure: {self.last_failure_time}"
                )
        
        # Intentar ejecutar
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Verifica si se debe intentar resetear"""
        if self.last_failure_time is None:
            return False
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.config.timeout_seconds
    
    def _on_success(self):
        """Maneja éxito"""
        self.last_success_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logger.info(f"Circuit breaker {self.name} cerrado (recuperado)")
        else:
            # Resetear contador de fallos en estado CLOSED
            self.failure_count = 0
    
    def _on_failure(self):
        """Maneja fallo"""
        self.last_failure_time = datetime.now()
        self.failure_count += 1
        
        if self.state == CircuitState.HALF_OPEN:
            # Falló en half_open, volver a abrir
            self.state = CircuitState.OPEN
            self.success_count = 0
            logger.warning(f"Circuit breaker {self.name} reabierto (falló en half_open)")
        elif self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(
                f"Circuit breaker {self.name} abierto "
                f"({self.failure_count} fallos)"
            )
    
    def get_state(self) -> dict:
        """Obtiene estado actual del circuit breaker"""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure_time': (
                self.last_failure_time.isoformat()
                if self.last_failure_time else None
            ),
            'last_success_time': (
                self.last_success_time.isoformat()
                if self.last_success_time else None
            ),
        }
    
    def reset(self):
        """Resetea el circuit breaker manualmente"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        logger.info(f"Circuit breaker {self.name} reseteado manualmente")


# Circuit breakers globales por fuente
_circuit_breakers: dict = {}


def get_circuit_breaker(
    name: str,
    config: Optional[CircuitBreakerConfig] = None
) -> PriceCircuitBreaker:
    """Obtiene o crea un circuit breaker"""
    if name not in _circuit_breakers:
        _circuit_breakers[name] = PriceCircuitBreaker(name, config)
    return _circuit_breakers[name]








