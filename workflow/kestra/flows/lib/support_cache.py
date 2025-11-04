"""
Sistema de Cache Avanzado para Soporte.

Características:
- Cache de FAQs con TTL
- Cache de respuestas del chatbot
- Cache de cálculos de prioridad
- Cache de enrutamiento
- Invalidation inteligente
"""
import logging
import hashlib
import json
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
from functools import wraps

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from cachetools import TTLCache
    CACHETOOLS_AVAILABLE = True
except ImportError:
    CACHETOOLS_AVAILABLE = False

logger = logging.getLogger(__name__)


class SupportCache:
    """Sistema de cache para componentes de soporte."""
    
    def __init__(
        self,
        cache_type: str = "memory",  # memory, redis
        redis_host: Optional[str] = None,
        redis_port: int = 6379,
        redis_db: int = 0,
        default_ttl: int = 3600  # 1 hora
    ):
        """
        Inicializa el sistema de cache.
        
        Args:
            cache_type: Tipo de cache (memory, redis)
            redis_host: Host de Redis (si cache_type = redis)
            redis_port: Puerto de Redis
            redis_db: Base de datos de Redis
            default_ttl: TTL por defecto en segundos
        """
        self.cache_type = cache_type
        self.default_ttl = default_ttl
        self.redis_client = None
        self.memory_cache = None
        
        if cache_type == "redis" and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=redis_host or "localhost",
                    port=redis_port,
                    db=redis_db,
                    decode_responses=True
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis cache: {e}, falling back to memory")
                cache_type = "memory"
        
        if cache_type == "memory" and CACHETOOLS_AVAILABLE:
            # Cache en memoria con TTL
            self.memory_cache = TTLCache(maxsize=1000, ttl=default_ttl)
            logger.info("Memory cache initialized")
        elif cache_type == "memory":
            # Fallback a dict simple (sin TTL automático)
            self.memory_cache = {}
            logger.warning("Using simple dict cache (no TTL)")
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Genera una clave de cache única."""
        key_data = f"{prefix}:{json.dumps(args, sort_keys=True)}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del cache."""
        try:
            if self.cache_type == "redis" and self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            elif self.memory_cache is not None:
                if isinstance(self.memory_cache, dict):
                    # Simple dict cache
                    cached = self.memory_cache.get(key)
                    if cached:
                        value, expires = cached
                        if datetime.now() < expires:
                            return value
                        else:
                            del self.memory_cache[key]
                else:
                    # TTLCache
                    return self.memory_cache.get(key)
        except Exception as e:
            logger.warning(f"Error getting from cache: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Guarda un valor en el cache."""
        try:
            ttl = ttl or self.default_ttl
            
            if self.cache_type == "redis" and self.redis_client:
                self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value)
                )
                return True
            elif self.memory_cache is not None:
                if isinstance(self.memory_cache, dict):
                    # Simple dict cache
                    expires = datetime.now() + timedelta(seconds=ttl)
                    self.memory_cache[key] = (value, expires)
                else:
                    # TTLCache (ttl se maneja automáticamente)
                    self.memory_cache[key] = value
                return True
        except Exception as e:
            logger.warning(f"Error setting cache: {e}")
        
        return False
    
    def delete(self, key: str) -> bool:
        """Elimina un valor del cache."""
        try:
            if self.cache_type == "redis" and self.redis_client:
                return bool(self.redis_client.delete(key))
            elif self.memory_cache is not None:
                if key in self.memory_cache:
                    del self.memory_cache[key]
                    return True
        except Exception as e:
            logger.warning(f"Error deleting from cache: {e}")
        
        return False
    
    def clear(self, pattern: Optional[str] = None) -> int:
        """Limpia el cache (opcionalmente con patrón)."""
        count = 0
        try:
            if self.cache_type == "redis" and self.redis_client:
                if pattern:
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        count = self.redis_client.delete(*keys)
                else:
                    self.redis_client.flushdb()
                    count = -1  # Indica que se limpió todo
            elif self.memory_cache is not None:
                if pattern:
                    keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
                    for k in keys_to_delete:
                        del self.memory_cache[k]
                        count += 1
                else:
                    self.memory_cache.clear()
                    count = -1
        except Exception as e:
            logger.warning(f"Error clearing cache: {e}")
        
        return count


def cached_result(prefix: str, ttl: int = 3600):
    """
    Decorador para cachear resultados de funciones.
    
    Args:
        prefix: Prefijo para las claves de cache
        ttl: TTL en segundos
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Usar cache global si está disponible
            cache = getattr(wrapper, '_cache', None)
            if not cache:
                # Intentar crear cache
                try:
                    cache = SupportCache()
                except Exception:
                    # Si no se puede crear cache, ejecutar función directamente
                    return func(*args, **kwargs)
            
            # Generar clave de cache
            cache_key = cache._generate_key(prefix, *args, **kwargs)
            
            # Intentar obtener del cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {prefix}")
                return cached_value
            
            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {prefix}")
            
            return result
        
        return wrapper
    return decorator

