"""
Rate Limiting para API de Contratos
Previene abuso y controla el uso de recursos
"""

from __future__ import annotations

import time
import logging
from typing import Dict, Any, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta
from threading import Lock

logger = logging.getLogger("airflow.task")


class RateLimiter:
    """Rate limiter basado en sliding window"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Inicializa rate limiter.
        
        Args:
            max_requests: Máximo de requests permitidos
            window_seconds: Ventana de tiempo en segundos
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.lock = Lock()
    
    def is_allowed(self, key: str = "default") -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        Verifica si un request está permitido.
        
        Args:
            key: Clave única para el rate limiter (IP, user_id, etc.)
            
        Returns:
            Tuple (is_allowed, rate_limit_info)
        """
        with self.lock:
            now = time.time()
            window_start = now - self.window_seconds
            
            # Limpiar requests antiguos
            request_times = self.requests[key]
            while request_times and request_times[0] < window_start:
                request_times.popleft()
            
            # Verificar límite
            current_count = len(request_times)
            
            if current_count >= self.max_requests:
                reset_time = request_times[0] + self.window_seconds if request_times else now
                return False, {
                    "limit": self.max_requests,
                    "remaining": 0,
                    "reset_at": datetime.fromtimestamp(reset_time).isoformat(),
                    "retry_after": int(reset_time - now)
                }
            
            # Agregar request actual
            request_times.append(now)
            
            return True, {
                "limit": self.max_requests,
                "remaining": self.max_requests - len(request_times),
                "reset_at": datetime.fromtimestamp(
                    request_times[0] + self.window_seconds if request_times else now
                ).isoformat()
            }
    
    def reset(self, key: str = "default"):
        """Resetea el contador para una clave"""
        with self.lock:
            if key in self.requests:
                del self.requests[key]


# Rate limiters globales por tipo de operación
_api_rate_limiter = RateLimiter(max_requests=1000, window_seconds=3600)  # 1000 req/hora
_create_rate_limiter = RateLimiter(max_requests=100, window_seconds=3600)  # 100 create/hora
_send_rate_limiter = RateLimiter(max_requests=50, window_seconds=3600)  # 50 send/hora


def check_rate_limit(operation: str, key: str = "default") -> tuple[bool, Optional[Dict[str, Any]]]:
    """
    Verifica rate limit para una operación.
    
    Args:
        operation: 'api', 'create', 'send'
        key: Clave única (IP, user_id, etc.)
        
    Returns:
        Tuple (is_allowed, rate_limit_info)
    """
    if operation == "api":
        return _api_rate_limiter.is_allowed(key)
    elif operation == "create":
        return _create_rate_limiter.is_allowed(key)
    elif operation == "send":
        return _send_rate_limiter.is_allowed(key)
    else:
        return True, None

