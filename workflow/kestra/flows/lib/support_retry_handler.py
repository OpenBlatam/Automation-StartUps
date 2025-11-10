"""
Manejador de Reintentos (Retry) para Operaciones de Soporte.

Características:
- Retry automático con exponential backoff
- Circuit breaker pattern
- Configuración flexible por tipo de operación
- Logging detallado
"""
import logging
import time
from typing import Callable, Any, Optional, TypeVar, List
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryStrategy(Enum):
    """Estrategias de retry."""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"
    CUSTOM = "custom"


@dataclass
class RetryConfig:
    """Configuración de retry."""
    max_attempts: int = 3
    initial_delay: float = 1.0  # segundos
    max_delay: float = 60.0  # segundos
    backoff_multiplier: float = 2.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    retryable_exceptions: tuple = (Exception,)
    non_retryable_exceptions: tuple = ()


@dataclass
class CircuitBreakerState:
    """Estado del circuit breaker."""
    failures: int = 0
    last_failure_time: Optional[datetime] = None
    is_open: bool = False
    half_open_attempts: int = 0


class SupportRetryHandler:
    """Manejador de retry para operaciones de soporte."""
    
    def __init__(
        self,
        default_config: Optional[RetryConfig] = None,
        enable_circuit_breaker: bool = True,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: timedelta = timedelta(minutes=5)
    ):
        """
        Inicializa el manejador de retry.
        
        Args:
            default_config: Configuración por defecto
            enable_circuit_breaker: Habilitar circuit breaker
            circuit_breaker_threshold: Número de fallos para abrir circuito
            circuit_breaker_timeout: Tiempo antes de intentar half-open
        """
        self.default_config = default_config or RetryConfig()
        self.enable_circuit_breaker = enable_circuit_breaker
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        self.circuit_breakers: dict = {}
    
    def _get_circuit_breaker(self, operation_name: str) -> CircuitBreakerState:
        """Obtiene o crea circuit breaker para una operación."""
        if operation_name not in self.circuit_breakers:
            self.circuit_breakers[operation_name] = CircuitBreakerState()
        return self.circuit_breakers[operation_name]
    
    def _check_circuit_breaker(self, operation_name: str) -> bool:
        """Verifica si el circuito está abierto."""
        if not self.enable_circuit_breaker:
            return True
        
        cb = self._get_circuit_breaker(operation_name)
        
        if cb.is_open:
            # Verificar si debemos intentar half-open
            if cb.last_failure_time:
                time_since_failure = datetime.now() - cb.last_failure_time
                if time_since_failure >= self.circuit_breaker_timeout:
                    cb.is_open = False
                    cb.half_open_attempts = 0
                    logger.info(f"Circuit breaker para {operation_name} en estado half-open")
                    return True
            return False
        
        return True
    
    def _record_success(self, operation_name: str):
        """Registra éxito y resetea circuit breaker."""
        if not self.enable_circuit_breaker:
            return
        
        cb = self._get_circuit_breaker(operation_name)
        if cb.is_open:
            # Éxito en half-open, cerrar circuito
            cb.is_open = False
            cb.failures = 0
            cb.half_open_attempts = 0
            logger.info(f"Circuit breaker para {operation_name} cerrado después de éxito")
        else:
            cb.failures = 0
    
    def _record_failure(self, operation_name: str):
        """Registra fallo y actualiza circuit breaker."""
        if not self.enable_circuit_breaker:
            return
        
        cb = self._get_circuit_breaker(operation_name)
        cb.failures += 1
        cb.last_failure_time = datetime.now()
        
        if cb.failures >= self.circuit_breaker_threshold:
            cb.is_open = True
            logger.warning(
                f"Circuit breaker para {operation_name} abierto después de {cb.failures} fallos"
            )
        elif cb.half_open_attempts > 0:
            # Fallo en half-open, volver a abrir
            cb.is_open = True
            cb.half_open_attempts = 0
            logger.warning(f"Circuit breaker para {operation_name} reabierto después de fallo")
    
    def _calculate_delay(
        self,
        attempt: int,
        config: RetryConfig
    ) -> float:
        """Calcula delay para el siguiente intento."""
        if config.strategy == RetryStrategy.EXPONENTIAL:
            delay = config.initial_delay * (config.backoff_multiplier ** (attempt - 1))
        elif config.strategy == RetryStrategy.LINEAR:
            delay = config.initial_delay * attempt
        elif config.strategy == RetryStrategy.FIXED:
            delay = config.initial_delay
        else:
            delay = config.initial_delay
        
        return min(delay, config.max_delay)
    
    def _should_retry(
        self,
        exception: Exception,
        attempt: int,
        config: RetryConfig
    ) -> bool:
        """Determina si se debe reintentar."""
        if attempt >= config.max_attempts:
            return False
        
        # No retryar excepciones no retryables
        if config.non_retryable_exceptions:
            if isinstance(exception, config.non_retryable_exceptions):
                return False
        
        # Retryar solo excepciones retryables
        if config.retryable_exceptions:
            return isinstance(exception, config.retryable_exceptions)
        
        return True
    
    def execute_with_retry(
        self,
        func: Callable[[], T],
        operation_name: str = "operation",
        config: Optional[RetryConfig] = None,
        on_retry: Optional[Callable[[int, Exception], None]] = None
    ) -> T:
        """
        Ejecuta una función con retry automático.
        
        Args:
            func: Función a ejecutar
            operation_name: Nombre de la operación (para circuit breaker)
            config: Configuración de retry (None = usar default)
            on_retry: Callback llamado en cada retry
            
        Returns:
            Resultado de la función
            
        Raises:
            Exception: Si todos los intentos fallan
        """
        retry_config = config or self.default_config
        last_exception = None
        
        # Verificar circuit breaker
        if not self._check_circuit_breaker(operation_name):
            raise Exception(f"Circuit breaker abierto para {operation_name}")
        
        for attempt in range(1, retry_config.max_attempts + 1):
            try:
                result = func()
                
                # Éxito
                self._record_success(operation_name)
                if attempt > 1:
                    logger.info(
                        f"Operación {operation_name} exitosa después de {attempt} intentos"
                    )
                return result
                
            except Exception as e:
                last_exception = e
                
                # Verificar si debemos retryar
                if not self._should_retry(e, attempt, retry_config):
                    logger.error(
                        f"Operación {operation_name} falló con excepción no retryable: {e}"
                    )
                    self._record_failure(operation_name)
                    raise
                
                # Si es el último intento, no esperar
                if attempt >= retry_config.max_attempts:
                    logger.error(
                        f"Operación {operation_name} falló después de {attempt} intentos: {e}"
                    )
                    self._record_failure(operation_name)
                    break
                
                # Calcular delay
                delay = self._calculate_delay(attempt, retry_config)
                
                logger.warning(
                    f"Operación {operation_name} falló (intento {attempt}/{retry_config.max_attempts}): {e}. "
                    f"Reintentando en {delay:.2f}s"
                )
                
                # Callback de retry
                if on_retry:
                    try:
                        on_retry(attempt, e)
                    except Exception as callback_error:
                        logger.warning(f"Error en callback de retry: {callback_error}")
                
                # Esperar antes de reintentar
                time.sleep(delay)
        
        # Todos los intentos fallaron
        self._record_failure(operation_name)
        raise last_exception
    
    def retry(
        self,
        operation_name: str = "operation",
        config: Optional[RetryConfig] = None
    ):
        """
        Decorador para funciones con retry automático.
        
        Usage:
            @retry_handler.retry(operation_name="categorize_ticket")
            def categorize(ticket):
                ...
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return self.execute_with_retry(
                    lambda: func(*args, **kwargs),
                    operation_name=operation_name,
                    config=config
                )
            return wrapper
        return decorator


# Instancia global para uso común
default_retry_handler = SupportRetryHandler(
    default_config=RetryConfig(
        max_attempts=3,
        initial_delay=1.0,
        max_delay=30.0,
        backoff_multiplier=2.0,
        strategy=RetryStrategy.EXPONENTIAL
    )
)

