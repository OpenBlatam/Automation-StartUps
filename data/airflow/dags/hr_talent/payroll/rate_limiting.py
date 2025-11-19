"""
Sistema de Rate Limiting para Nómina
Control de tasa de requests y throttling
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from collections import defaultdict
from threading import Lock

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter con ventana deslizante"""
    
    def __init__(
        self,
        max_requests: int = 100,
        window_seconds: int = 60
    ):
        """
        Args:
            max_requests: Máximo de requests permitidos
            window_seconds: Ventana de tiempo en segundos
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = Lock()
    
    def is_allowed(self, key: str = "default") -> bool:
        """Verifica si un request está permitido"""
        with self.lock:
            now = time.time()
            
            # Limpiar requests antiguos
            self.requests[key] = [
                ts for ts in self.requests[key]
                if now - ts < self.window_seconds
            ]
            
            # Verificar límite
            if len(self.requests[key]) >= self.max_requests:
                return False
            
            # Registrar request
            self.requests[key].append(now)
            return True
    
    def get_remaining(self, key: str = "default") -> int:
        """Obtiene requests restantes"""
        with self.lock:
            now = time.time()
            self.requests[key] = [
                ts for ts in self.requests[key]
                if now - ts < self.window_seconds
            ]
            return max(0, self.max_requests - len(self.requests[key]))
    
    def reset(self, key: str = "default") -> None:
        """Resetea el contador para una clave"""
        with self.lock:
            self.requests[key] = []


class Throttler:
    """Throttler para controlar velocidad de ejecución"""
    
    def __init__(self, min_interval_seconds: float = 1.0):
        """
        Args:
            min_interval_seconds: Intervalo mínimo entre ejecuciones
        """
        self.min_interval = min_interval_seconds
        self.last_execution: Dict[str, float] = {}
        self.lock = Lock()
    
    def wait_if_needed(self, key: str = "default") -> None:
        """Espera si es necesario para respetar el throttle"""
        with self.lock:
            now = time.time()
            last = self.last_execution.get(key, 0)
            
            elapsed = now - last
            if elapsed < self.min_interval:
                sleep_time = self.min_interval - elapsed
                time.sleep(sleep_time)
            
            self.last_execution[key] = time.time()


class PayrollRateLimiter:
    """Rate limiter específico para operaciones de nómina"""
    
    def __init__(self):
        """Inicializa rate limiters para diferentes operaciones"""
        # Limite de cálculos de nómina por minuto
        self.payroll_calculations = RateLimiter(
            max_requests=50,
            window_seconds=60
        )
        
        # Limite de consultas OCR por minuto
        self.ocr_requests = RateLimiter(
            max_requests=20,
            window_seconds=60
        )
        
        # Limite de consultas a base de datos por segundo
        self.database_queries = RateLimiter(
            max_requests=100,
            window_seconds=1
        )
        
        # Throttler para notificaciones
        self.notifications = Throttler(min_interval_seconds=0.5)
    
    def check_payroll_calculation(self) -> bool:
        """Verifica si se puede calcular nómina"""
        return self.payroll_calculations.is_allowed("payroll")
    
    def check_ocr_request(self) -> bool:
        """Verifica si se puede hacer request OCR"""
        return self.ocr_requests.is_allowed("ocr")
    
    def check_database_query(self) -> bool:
        """Verifica si se puede hacer query a base de datos"""
        return self.database_queries.is_allowed("database")
    
    def throttle_notification(self) -> None:
        """Throttle para notificaciones"""
        self.notifications.wait_if_needed("notifications")

