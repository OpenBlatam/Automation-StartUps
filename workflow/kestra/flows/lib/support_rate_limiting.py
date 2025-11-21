"""
Sistema de Rate Limiting Inteligente.

Limita y controla la tasa de requests para proteger el sistema.
"""
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)


class RateLimitStrategy(Enum):
    """Estrategias de rate limiting."""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


@dataclass
class RateLimit:
    """Límite de tasa."""
    identifier: str  # IP, user_id, etc.
    strategy: RateLimitStrategy
    max_requests: int
    window_seconds: int
    current_requests: int = 0
    window_start: datetime = None
    blocked_until: Optional[datetime] = None
    
    def __post_init__(self):
        if self.window_start is None:
            self.window_start = datetime.now()


@dataclass
class RateLimitResult:
    """Resultado de verificación de rate limit."""
    allowed: bool
    remaining_requests: int
    reset_after_seconds: int
    retry_after_seconds: Optional[int] = None
    limit_exceeded: bool = False


class RateLimiter:
    """Rate limiter inteligente."""
    
    def __init__(self):
        """Inicializa rate limiter."""
        self.limits: Dict[str, RateLimit] = {}
        self.request_history: Dict[str, deque] = {}  # Para sliding window
        self.token_buckets: Dict[str, Dict[str, Any]] = {}  # Para token bucket
    
    def check_rate_limit(
        self,
        identifier: str,
        max_requests: int = 100,
        window_seconds: int = 60,
        strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    ) -> RateLimitResult:
        """
        Verifica si un request está permitido.
        
        Args:
            identifier: Identificador (IP, user_id, etc.)
            max_requests: Máximo de requests
            window_seconds: Ventana de tiempo en segundos
            strategy: Estrategia de rate limiting
            
        Returns:
            Resultado de verificación
        """
        # Verificar si está bloqueado
        limit = self.limits.get(identifier)
        if limit and limit.blocked_until:
            if datetime.now() < limit.blocked_until:
                retry_after = (limit.blocked_until - datetime.now()).total_seconds()
                return RateLimitResult(
                    allowed=False,
                    remaining_requests=0,
                    reset_after_seconds=window_seconds,
                    retry_after_seconds=retry_after,
                    limit_exceeded=True
                )
            else:
                # Desbloquear
                limit.blocked_until = None
        
        # Aplicar estrategia
        if strategy == RateLimitStrategy.FIXED_WINDOW:
            return self._check_fixed_window(identifier, max_requests, window_seconds)
        elif strategy == RateLimitStrategy.SLIDING_WINDOW:
            return self._check_sliding_window(identifier, max_requests, window_seconds)
        elif strategy == RateLimitStrategy.TOKEN_BUCKET:
            return self._check_token_bucket(identifier, max_requests, window_seconds)
        else:
            return self._check_fixed_window(identifier, max_requests, window_seconds)
    
    def _check_fixed_window(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> RateLimitResult:
        """Verifica con fixed window."""
        if identifier not in self.limits:
            self.limits[identifier] = RateLimit(
                identifier=identifier,
                strategy=RateLimitStrategy.FIXED_WINDOW,
                max_requests=max_requests,
                window_seconds=window_seconds
            )
        
        limit = self.limits[identifier]
        now = datetime.now()
        
        # Verificar si la ventana expiró
        if (now - limit.window_start).total_seconds() >= window_seconds:
            limit.current_requests = 0
            limit.window_start = now
        
        # Verificar límite
        if limit.current_requests >= max_requests:
            reset_after = window_seconds - (now - limit.window_start).total_seconds()
            return RateLimitResult(
                allowed=False,
                remaining_requests=0,
                reset_after_seconds=int(reset_after),
                limit_exceeded=True
            )
        
        # Permitir request
        limit.current_requests += 1
        remaining = max_requests - limit.current_requests
        reset_after = window_seconds - (now - limit.window_start).total_seconds()
        
        return RateLimitResult(
            allowed=True,
            remaining_requests=remaining,
            reset_after_seconds=int(reset_after)
        )
    
    def _check_sliding_window(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> RateLimitResult:
        """Verifica con sliding window."""
        if identifier not in self.request_history:
            self.request_history[identifier] = deque()
        
        history = self.request_history[identifier]
        now = datetime.now()
        cutoff = now - timedelta(seconds=window_seconds)
        
        # Limpiar requests antiguos
        while history and history[0] < cutoff:
            history.popleft()
        
        # Verificar límite
        if len(history) >= max_requests:
            oldest_request = history[0]
            reset_after = window_seconds - (now - oldest_request).total_seconds()
            return RateLimitResult(
                allowed=False,
                remaining_requests=0,
                reset_after_seconds=int(reset_after),
                limit_exceeded=True
            )
        
        # Permitir request
        history.append(now)
        remaining = max_requests - len(history)
        
        # Calcular reset (tiempo hasta que expire el request más antiguo)
        if history:
            oldest_request = history[0]
            reset_after = window_seconds - (now - oldest_request).total_seconds()
        else:
            reset_after = window_seconds
        
        return RateLimitResult(
            allowed=True,
            remaining_requests=remaining,
            reset_after_seconds=int(reset_after)
        )
    
    def _check_token_bucket(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> RateLimitResult:
        """Verifica con token bucket."""
        if identifier not in self.token_buckets:
            # Inicializar bucket
            tokens_per_second = max_requests / window_seconds
            self.token_buckets[identifier] = {
                "tokens": float(max_requests),
                "capacity": max_requests,
                "tokens_per_second": tokens_per_second,
                "last_refill": datetime.now()
            }
        
        bucket = self.token_buckets[identifier]
        now = datetime.now()
        
        # Refill tokens
        time_passed = (now - bucket["last_refill"]).total_seconds()
        tokens_to_add = time_passed * bucket["tokens_per_second"]
        bucket["tokens"] = min(bucket["capacity"], bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = now
        
        # Verificar si hay tokens disponibles
        if bucket["tokens"] < 1.0:
            # Calcular cuándo habrá tokens disponibles
            tokens_needed = 1.0 - bucket["tokens"]
            seconds_needed = tokens_needed / bucket["tokens_per_second"]
            return RateLimitResult(
                allowed=False,
                remaining_requests=int(bucket["tokens"]),
                reset_after_seconds=window_seconds,
                retry_after_seconds=int(seconds_needed),
                limit_exceeded=True
            )
        
        # Consumir token
        bucket["tokens"] -= 1.0
        remaining = int(bucket["tokens"])
        
        return RateLimitResult(
            allowed=True,
            remaining_requests=remaining,
            reset_after_seconds=window_seconds
        )
    
    def block_identifier(
        self,
        identifier: str,
        duration_seconds: int
    ):
        """
        Bloquea un identificador temporalmente.
        
        Args:
            identifier: Identificador a bloquear
            duration_seconds: Duración del bloqueo
        """
        if identifier not in self.limits:
            self.limits[identifier] = RateLimit(
                identifier=identifier,
                strategy=RateLimitStrategy.FIXED_WINDOW,
                max_requests=0,
                window_seconds=0
            )
        
        self.limits[identifier].blocked_until = datetime.now() + timedelta(seconds=duration_seconds)
        logger.warning(f"Blocked {identifier} for {duration_seconds} seconds")
    
    def get_rate_limit_status(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene estado de rate limit para un identificador.
        
        Args:
            identifier: Identificador
            
        Returns:
            Estado del rate limit
        """
        limit = self.limits.get(identifier)
        if not limit:
            return None
        
        bucket = self.token_buckets.get(identifier)
        history = self.request_history.get(identifier)
        
        status = {
            "identifier": identifier,
            "strategy": limit.strategy.value,
            "max_requests": limit.max_requests,
            "window_seconds": limit.window_seconds,
            "blocked_until": limit.blocked_until.isoformat() if limit.blocked_until else None,
            "is_blocked": limit.blocked_until is not None and datetime.now() < limit.blocked_until
        }
        
        if bucket:
            status["token_bucket"] = {
                "tokens": bucket["tokens"],
                "capacity": bucket["capacity"]
            }
        
        if history:
            status["sliding_window"] = {
                "requests_in_window": len(history),
                "oldest_request": history[0].isoformat() if history else None
            }
        
        return status
    
    def reset_limit(self, identifier: str):
        """Resetea límite para un identificador."""
        if identifier in self.limits:
            limit = self.limits[identifier]
            limit.current_requests = 0
            limit.window_start = datetime.now()
            limit.blocked_until = None
        
        if identifier in self.request_history:
            self.request_history[identifier].clear()
        
        if identifier in self.token_buckets:
            bucket = self.token_buckets[identifier]
            bucket["tokens"] = bucket["capacity"]
            bucket["last_refill"] = datetime.now()

