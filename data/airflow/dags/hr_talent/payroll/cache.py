"""
Sistema de Caché para Nómina
Optimiza consultas frecuentes con caché
"""

import logging
from typing import Optional, Dict, Any, Callable
from functools import wraps
from datetime import datetime, timedelta
import hashlib
import json

try:
    from cachetools import TTLCache
    CACHETOOLS_AVAILABLE = True
except ImportError:
    CACHETOOLS_AVAILABLE = False
    TTLCache = None

logger = logging.getLogger(__name__)


class PayrollCache:
    """Sistema de caché para nómina"""
    
    def __init__(
        self,
        max_size: int = 1000,
        ttl_seconds: int = 3600,
        enabled: bool = True
    ):
        """
        Args:
            max_size: Tamaño máximo del caché
            ttl_seconds: Tiempo de vida en segundos
            enabled: Si el caché está habilitado
        """
        self.enabled = enabled and CACHETOOLS_AVAILABLE
        
        if self.enabled:
            self.cache = TTLCache(maxsize=max_size, ttl=ttl_seconds)
        else:
            self.cache = None
            if not CACHETOOLS_AVAILABLE:
                logger.warning("cachetools not available. Install with: pip install cachetools")
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del caché"""
        if not self.enabled or not self.cache:
            return None
        
        try:
            return self.cache.get(key)
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """Establece un valor en el caché"""
        if not self.enabled or not self.cache:
            return False
        
        try:
            self.cache[key] = value
            return True
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    def clear(self) -> None:
        """Limpia el caché"""
        if self.cache:
            self.cache.clear()
    
    def invalidate(self, pattern: str) -> int:
        """
        Invalida entradas del caché que coincidan con un patrón
        
        Returns:
            Número de entradas invalidadas
        """
        if not self.cache:
            return 0
        
        count = 0
        keys_to_remove = []
        
        for key in self.cache.keys():
            if pattern in str(key):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            try:
                del self.cache[key]
                count += 1
            except KeyError:
                pass
        
        return count


def cached(
    cache_instance: Optional[PayrollCache] = None,
    key_prefix: str = "",
    ttl_seconds: int = 3600
):
    """
    Decorador para cachear resultados de funciones
    
    Args:
        cache_instance: Instancia de PayrollCache (opcional)
        key_prefix: Prefijo para las claves de caché
        ttl_seconds: Tiempo de vida en segundos
    """
    def decorator(func: Callable) -> Callable:
        if cache_instance is None:
            cache = PayrollCache(ttl_seconds=ttl_seconds)
        else:
            cache = cache_instance
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave de caché
            cache_key_parts = [key_prefix, func.__name__]
            
            # Incluir argumentos posicionales
            for arg in args:
                if isinstance(arg, (str, int, float, bool)):
                    cache_key_parts.append(str(arg))
                elif isinstance(arg, (datetime,)):
                    cache_key_parts.append(arg.isoformat())
                else:
                    cache_key_parts.append(str(hash(str(arg))))
            
            # Incluir argumentos de palabra clave
            for k, v in sorted(kwargs.items()):
                if isinstance(v, (str, int, float, bool)):
                    cache_key_parts.append(f"{k}={v}")
                elif isinstance(v, (datetime,)):
                    cache_key_parts.append(f"{k}={v.isoformat()}")
                else:
                    cache_key_parts.append(f"{k}={hash(str(v))}")
            
            cache_key = "|".join(cache_key_parts)
            cache_key_hash = hashlib.md5(cache_key.encode()).hexdigest()
            
            # Intentar obtener del caché
            cached_result = cache.get(cache_key_hash)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Ejecutar función y cachear resultado
            logger.debug(f"Cache miss for {func.__name__}")
            result = func(*args, **kwargs)
            cache.set(cache_key_hash, result)
            
            return result
        
        return wrapper
    return decorator


def make_cache_key(*args, **kwargs) -> str:
    """Genera una clave de caché a partir de argumentos"""
    parts = []
    
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            parts.append(str(arg))
        elif isinstance(arg, (datetime,)):
            parts.append(arg.isoformat())
        else:
            parts.append(str(hash(str(arg))))
    
    for k, v in sorted(kwargs.items()):
        if isinstance(v, (str, int, float, bool)):
            parts.append(f"{k}={v}")
        elif isinstance(v, (datetime,)):
            parts.append(f"{k}={v.isoformat()}")
        else:
            parts.append(f"{k}={hash(str(v))}")
    
    key = "|".join(parts)
    return hashlib.md5(key.encode()).hexdigest()

