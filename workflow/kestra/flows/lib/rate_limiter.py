"""
Rate limiter avanzado con token bucket algorithm.

Características:
- Token bucket algorithm
- Rate limiting por endpoint/operación
- Thread-safe
- Configuración flexible
"""
import time
import threading
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class TokenBucket:
    """Bucket de tokens para rate limiting."""
    capacity: float
    refill_rate: float  # tokens per second
    tokens: float = field(init=False)
    last_refill: float = field(init=False)
    lock: threading.Lock = field(default_factory=threading.Lock, init=False)
    
    def __post_init__(self):
        """Inicializa el bucket."""
        self.tokens = self.capacity
        self.last_refill = time.time()
    
    def consume(self, tokens: float = 1.0) -> bool:
        """
        Intenta consumir tokens.
        
        Args:
            tokens: Número de tokens a consumir
        
        Returns:
            True si se consumieron los tokens, False si no hay suficientes
        """
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def wait_until_available(self, tokens: float = 1.0) -> float:
        """
        Espera hasta que haya tokens disponibles.
        
        Args:
            tokens: Número de tokens necesarios
        
        Returns:
            Tiempo de espera en segundos
        """
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                return 0.0
            
            # Calcular cuánto tiempo esperar
            tokens_needed = tokens - self.tokens
            wait_time = tokens_needed / self.refill_rate
            return wait_time
    
    def _refill(self) -> None:
        """Recarga tokens basado en el tiempo transcurrido."""
        now = time.time()
        elapsed = now - self.last_refill
        
        if elapsed > 0:
            tokens_to_add = elapsed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now


class RateLimiter:
    """Rate limiter con token bucket por operación."""
    
    def __init__(
        self,
        default_capacity: float = 100.0,
        default_refill_rate: float = 10.0,
        per_operation_buckets: Optional[Dict[str, Dict[str, float]]] = None
    ):
        """
        Inicializa el rate limiter.
        
        Args:
            default_capacity: Capacidad por defecto del bucket
            default_refill_rate: Tasa de recarga por defecto (tokens/segundo)
            per_operation_buckets: Configuración por operación
                Ejemplo: {"get_contact": {"capacity": 50, "refill_rate": 5}}
        """
        self.default_capacity = default_capacity
        self.default_refill_rate = default_refill_rate
        self.buckets: Dict[str, TokenBucket] = {}
        self.buckets_lock = threading.Lock()
        
        # Configurar buckets por operación si se proporcionan
        if per_operation_buckets:
            for operation, config in per_operation_buckets.items():
                capacity = config.get("capacity", default_capacity)
                refill_rate = config.get("refill_rate", default_refill_rate)
                self.buckets[operation] = TokenBucket(capacity, refill_rate)
    
    def get_bucket(self, operation: str = "default") -> TokenBucket:
        """
        Obtiene o crea un bucket para una operación.
        
        Args:
            operation: Nombre de la operación
        
        Returns:
            TokenBucket para la operación
        """
        if operation not in self.buckets:
            with self.buckets_lock:
                if operation not in self.buckets:
                    self.buckets[operation] = TokenBucket(
                        self.default_capacity,
                        self.default_refill_rate
                    )
        return self.buckets[operation]
    
    def acquire(self, operation: str = "default", tokens: float = 1.0, wait: bool = False) -> bool:
        """
        Intenta adquirir tokens para una operación.
        
        Args:
            operation: Nombre de la operación
            tokens: Número de tokens necesarios
            wait: Si esperar hasta que haya tokens disponibles
        
        Returns:
            True si se adquirieron los tokens, False si no
        """
        bucket = self.get_bucket(operation)
        
        if bucket.consume(tokens):
            return True
        
        if wait:
            wait_time = bucket.wait_until_available(tokens)
            if wait_time > 0:
                time.sleep(wait_time)
            return bucket.consume(tokens)
        
        return False
    
    def wait(self, operation: str = "default", tokens: float = 1.0) -> float:
        """
        Calcula el tiempo de espera necesario para adquirir tokens.
        
        Args:
            operation: Nombre de la operación
            tokens: Número de tokens necesarios
        
        Returns:
            Tiempo de espera en segundos
        """
        bucket = self.get_bucket(operation)
        return bucket.wait_until_available(tokens)
    
    def get_stats(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene estadísticas del rate limiter.
        
        Args:
            operation: Operación específica (None para todas)
        
        Returns:
            Diccionario con estadísticas
        """
        if operation:
            bucket = self.get_bucket(operation)
            with bucket.lock:
                bucket._refill()
                return {
                    "operation": operation,
                    "tokens": bucket.tokens,
                    "capacity": bucket.capacity,
                    "refill_rate": bucket.refill_rate
                }
        else:
            stats = {}
            for op, bucket in self.buckets.items():
                with bucket.lock:
                    bucket._refill()
                    stats[op] = {
                        "tokens": bucket.tokens,
                        "capacity": bucket.capacity,
                        "refill_rate": bucket.refill_rate
                    }
            return stats


# Rate limiter global por defecto
_default_rate_limiter: Optional[RateLimiter] = None


def get_default_rate_limiter() -> RateLimiter:
    """Obtiene el rate limiter global por defecto."""
    global _default_rate_limiter
    if _default_rate_limiter is None:
        _default_rate_limiter = RateLimiter()
    return _default_rate_limiter


def set_default_rate_limiter(limiter: RateLimiter) -> None:
    """Configura el rate limiter global por defecto."""
    global _default_rate_limiter
    _default_rate_limiter = limiter


