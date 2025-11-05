"""
Sistema de cache avanzado para la aplicación
"""
from functools import wraps
from datetime import datetime, timedelta
from typing import Any, Optional, Callable
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

class SimpleCache:
    """Cache simple en memoria"""
    
    def __init__(self, default_timeout: int = 300):
        self.cache: dict[str, tuple[datetime, Any]] = {}
        self.default_timeout = default_timeout
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del cache"""
        if key not in self.cache:
            self.misses += 1
            return None
        
        timestamp, value = self.cache[key]
        
        # Verificar si expiró
        if datetime.now() - timestamp > timedelta(seconds=self.default_timeout):
            del self.cache[key]
            self.misses += 1
            return None
        
        self.hits += 1
        return value
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None):
        """Establece un valor en el cache"""
        timeout = timeout or self.default_timeout
        self.cache[key] = (datetime.now(), value)
    
    def delete(self, key: str):
        """Elimina una clave del cache"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """Limpia todo el cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas del cache"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            'size': len(self.cache),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate, 2),
            'total_requests': total
        }

# Instancia global del cache
cache = SimpleCache(default_timeout=300)

def cached(timeout: int = 300, key_prefix: str = ''):
    """
    Decorador para cachear resultados de funciones
    
    Args:
        timeout: Tiempo de expiración en segundos
        key_prefix: Prefijo para la clave de cache
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generar clave de cache
            cache_key = _generate_cache_key(
                f.__name__,
                args,
                kwargs,
                key_prefix
            )
            
            # Intentar obtener del cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit para {f.__name__}")
                return cached_value
            
            # Ejecutar función y cachear resultado
            logger.debug(f"Cache miss para {f.__name__}")
            result = f(*args, **kwargs)
            
            # Solo cachear si el resultado no es un error
            if result and not (isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], int) and result[1] >= 400):
                cache.set(cache_key, result, timeout)
            
            return result
        
        return decorated_function
    return decorator

def _generate_cache_key(func_name: str, args: tuple, kwargs: dict, prefix: str = '') -> str:
    """Genera una clave única para el cache"""
    # Serializar argumentos
    args_str = json.dumps(args, sort_keys=True, default=str)
    kwargs_str = json.dumps(kwargs, sort_keys=True, default=str)
    
    # Crear hash
    key_string = f"{prefix}{func_name}{args_str}{kwargs_str}"
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    
    return f"cache:{key_hash}"

def invalidate_cache(pattern: str = None):
    """Invalida entradas del cache que coincidan con el patrón"""
    if pattern is None:
        cache.clear()
        return
    
    keys_to_delete = [
        key for key in cache.cache.keys()
        if pattern in key
    ]
    
    for key in keys_to_delete:
        cache.delete(key)
    
    logger.info(f"Invalidadas {len(keys_to_delete)} entradas del cache")

