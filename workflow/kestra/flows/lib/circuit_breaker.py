"""
Circuit Breaker pattern para APIs externas.

Características:
- Protege contra cascading failures
- Estado: CLOSED, OPEN, HALF_OPEN
- Configuración de thresholds
- Auto-recovery
- Logging estructurado
"""
import time
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Estados del circuit breaker."""
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"  # Failing, reject requests
    HALF_OPEN = "HALF_OPEN"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuración del circuit breaker."""
    failure_threshold: int = 5  # Número de fallos antes de abrir
    success_threshold: int = 2  # Número de éxitos para cerrar desde HALF_OPEN
    timeout_seconds: int = 60  # Tiempo antes de intentar HALF_OPEN
    expected_exception: type = Exception  # Excepción que cuenta como fallo


@dataclass
class CircuitBreakerState:
    """Estado interno del circuit breaker."""
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    opened_at: Optional[float] = None


class CircuitBreaker:
    """Circuit Breaker para proteger llamadas a APIs externas."""
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ):
        """
        Inicializa el circuit breaker.
        
        Args:
            name: Nombre identificador del circuit breaker
            config: Configuración (opcional)
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitBreakerState()
        
        logger.info(f"CircuitBreaker '{name}' initialized", extra={
            "failure_threshold": self.config.failure_threshold,
            "timeout_seconds": self.config.timeout_seconds
        })
    
    def _should_attempt_request(self) -> bool:
        """
        Determina si se debe intentar la request basado en el estado.
        
        Returns:
            True si se puede intentar, False si debe rechazarse
        """
        current_time = time.time()
        
        if self._state.state == CircuitState.CLOSED:
            return True
        
        if self._state.state == CircuitState.OPEN:
            # Verificar si ha pasado suficiente tiempo para intentar HALF_OPEN
            if self._state.opened_at:
                elapsed = current_time - self._state.opened_at
                if elapsed >= self.config.timeout_seconds:
                    logger.info(f"Circuit breaker '{self.name}' transitioning to HALF_OPEN", extra={
                        "elapsed_seconds": elapsed
                    })
                    self._state.state = CircuitState.HALF_OPEN
                    self._state.success_count = 0
                    return True
            return False
        
        if self._state.state == CircuitState.HALF_OPEN:
            return True
        
        return False
    
    def _record_success(self) -> None:
        """Registra un éxito."""
        if self._state.state == CircuitState.HALF_OPEN:
            self._state.success_count += 1
            if self._state.success_count >= self.config.success_threshold:
                logger.info(f"Circuit breaker '{self.name}' closed after successful requests", extra={
                    "success_count": self._state.success_count
                })
                self._state.state = CircuitState.CLOSED
                self._state.failure_count = 0
                self._state.opened_at = None
        
        if self._state.state == CircuitState.CLOSED:
            # Reset failure count en estado cerrado
            self._state.failure_count = 0
    
    def _record_failure(self) -> None:
        """Registra un fallo."""
        self._state.failure_count += 1
        self._state.last_failure_time = time.time()
        
        if self._state.state == CircuitState.CLOSED:
            if self._state.failure_count >= self.config.failure_threshold:
                logger.warning(f"Circuit breaker '{self.name}' opened due to failures", extra={
                    "failure_count": self._state.failure_count,
                    "threshold": self.config.failure_threshold
                })
                self._state.state = CircuitState.OPEN
                self._state.opened_at = time.time()
        
        elif self._state.state == CircuitState.HALF_OPEN:
            # Cualquier fallo en HALF_OPEN vuelve a OPEN
            logger.warning(f"Circuit breaker '{self.name}' reopened after failure in HALF_OPEN", extra={
                "failure_count": self._state.failure_count
            })
            self._state.state = CircuitState.OPEN
            self._state.opened_at = time.time()
            self._state.success_count = 0
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Ejecuta una función protegida por el circuit breaker.
        
        Args:
            func: Función a ejecutar
            *args: Argumentos posicionales
            **kwargs: Argumentos de palabra clave
        
        Returns:
            Resultado de la función
        
        Raises:
            CircuitBreakerOpenError: Si el circuit breaker está abierto
            Exception: La excepción original si falla
        """
        if not self._should_attempt_request():
            error_msg = f"Circuit breaker '{self.name}' is OPEN, request rejected"
            logger.warning(error_msg, extra={
                "state": self._state.state.value,
                "failure_count": self._state.failure_count
            })
            raise CircuitBreakerOpenError(error_msg, self.name, self._state.state)
        
        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except self.config.expected_exception as e:
            self._record_failure()
            logger.error(f"Circuit breaker '{self.name}' recorded failure", extra={
                "error": str(e),
                "failure_count": self._state.failure_count,
                "state": self._state.state.value
            })
            raise
        except Exception as e:
            # Otras excepciones no cuentan como fallos
            logger.debug(f"Non-fatal exception in circuit breaker '{self.name}': {e}")
            raise
    
    def get_state(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del circuit breaker.
        
        Returns:
            Diccionario con el estado
        """
        return {
            "name": self.name,
            "state": self._state.state.value,
            "failure_count": self._state.failure_count,
            "success_count": self._state.success_count,
            "last_failure_time": self._state.last_failure_time,
            "opened_at": self._state.opened_at
        }
    
    def reset(self) -> None:
        """Resetea el circuit breaker a estado CLOSED."""
        logger.info(f"Circuit breaker '{self.name}' manually reset")
        self._state = CircuitBreakerState()


class CircuitBreakerOpenError(Exception):
    """Excepción lanzada cuando el circuit breaker está abierto."""
    
    def __init__(self, message: str, breaker_name: str, state: CircuitState):
        super().__init__(message)
        self.breaker_name = breaker_name
        self.state = state


# Instancias globales de circuit breakers
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
    """
    Obtiene o crea un circuit breaker por nombre.
    
    Args:
        name: Nombre del circuit breaker
        config: Configuración (opcional)
    
    Returns:
        Instancia de CircuitBreaker
    """
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(name, config)
    return _circuit_breakers[name]


def circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None):
    """
    Decorador para aplicar circuit breaker a una función.
    
    Args:
        name: Nombre del circuit breaker
        config: Configuración (opcional)
    
    Returns:
        Decorador
    """
    breaker = get_circuit_breaker(name, config)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        return wrapper
    
    return decorator



