"""
Rate Limiting y Throttling
==========================

Controla la tasa de procesamiento para evitar sobrecarga.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque
import time
import logging
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuración de rate limiting"""
    max_requests: int
    time_window: int  # segundos
    burst_size: Optional[int] = None


class TokenBucket:
    """Token bucket para rate limiting"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = float(capacity)
        self.refill_rate = refill_rate  # tokens por segundo
        self.last_refill = datetime.now()
        self.lock = Lock()
    
    def consume(self, tokens: int = 1) -> bool:
        """Consume tokens del bucket"""
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def _refill(self):
        """Recarga tokens según tasa"""
        now = datetime.now()
        elapsed = (now - self.last_refill).total_seconds()
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def wait_time(self, tokens: int = 1) -> float:
        """Calcula tiempo de espera necesario"""
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                return 0.0
            
            needed = tokens - self.tokens
            return needed / self.refill_rate


class RateLimiter:
    """Rate limiter para procesamiento de documentos"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Token bucket principal
        self.bucket = TokenBucket(
            capacity=config.max_requests,
            refill_rate=config.max_requests / config.time_window
        )
        
        # Burst bucket (opcional)
        if config.burst_size:
            self.burst_bucket = TokenBucket(
                capacity=config.burst_size,
                refill_rate=config.burst_size / config.time_window
            )
        else:
            self.burst_bucket = None
        
        # Historial de requests
        self.request_history = deque(maxlen=1000)
        self.lock = Lock()
    
    def acquire(self, tokens: int = 1) -> bool:
        """Intenta adquirir tokens"""
        # Intentar bucket principal
        if self.bucket.consume(tokens):
            self._record_request(True)
            return True
        
        # Intentar burst bucket si está disponible
        if self.burst_bucket and self.burst_bucket.consume(tokens):
            self._record_request(True)
            self.logger.warning("Usando burst bucket")
            return True
        
        self._record_request(False)
        return False
    
    def wait_and_acquire(self, tokens: int = 1) -> bool:
        """Espera y adquiere tokens"""
        while not self.acquire(tokens):
            wait_time = self.bucket.wait_time(tokens)
            if wait_time > 0:
                self.logger.debug(f"Rate limit alcanzado, esperando {wait_time:.2f}s")
                time.sleep(min(wait_time, 1.0))  # Sleep máximo 1 segundo por vez
        
        return True
    
    def _record_request(self, allowed: bool):
        """Registra request"""
        with self.lock:
            self.request_history.append({
                "timestamp": datetime.now(),
                "allowed": allowed
            })
    
    def get_stats(self, minutes: int = 5) -> Dict[str, Any]:
        """Obtiene estadísticas"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        
        with self.lock:
            recent = [
                r for r in self.request_history
                if r["timestamp"] > cutoff
            ]
        
        total = len(recent)
        allowed = sum(1 for r in recent if r["allowed"])
        denied = total - allowed
        
        return {
            "total_requests": total,
            "allowed": allowed,
            "denied": denied,
            "denial_rate": denied / total if total > 0 else 0.0,
            "current_tokens": self.bucket.tokens,
            "burst_tokens": self.burst_bucket.tokens if self.burst_bucket else None
        }


class AdaptiveRateLimiter(RateLimiter):
    """Rate limiter adaptativo que ajusta límites dinámicamente"""
    
    def __init__(self, initial_config: RateLimitConfig):
        super().__init__(initial_config)
        self.performance_history = deque(maxlen=100)
        self.adaptive = True
    
    def record_performance(self, processing_time: float, success: bool):
        """Registra performance para ajustar límites"""
        self.performance_history.append({
            "time": processing_time,
            "success": success,
            "timestamp": datetime.now()
        })
        
        if self.adaptive and len(self.performance_history) >= 20:
            self._adjust_limits()
    
    def _adjust_limits(self):
        """Ajusta límites basado en performance"""
        recent = list(self.performance_history)[-20:]
        
        avg_time = sum(p["time"] for p in recent) / len(recent)
        success_rate = sum(1 for p in recent if p["success"]) / len(recent)
        
        # Si el sistema está rápido y estable, aumentar límite
        if avg_time < 5.0 and success_rate > 0.95:
            new_capacity = int(self.bucket.capacity * 1.1)
            self.bucket.capacity = min(new_capacity, self.bucket.capacity * 2)
            self.logger.info(f"Aumentando capacidad a {self.bucket.capacity}")
        
        # Si el sistema está lento o fallando, reducir límite
        elif avg_time > 30.0 or success_rate < 0.90:
            new_capacity = int(self.bucket.capacity * 0.9)
            self.bucket.capacity = max(new_capacity, self.bucket.capacity // 2)
            self.logger.warning(f"Reduciendo capacidad a {self.bucket.capacity}")

