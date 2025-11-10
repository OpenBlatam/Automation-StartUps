"""
Sistema de Caché Avanzado para Contratos
Mejora rendimiento con caché de consultas frecuentes
"""

from __future__ import annotations

import logging
import hashlib
import json
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

# Intentar usar Redis para caché distribuido
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger = logging.getLogger("airflow.task")
    logger.debug("redis no disponible, usando caché en memoria")

logger = logging.getLogger("airflow.task")


class ContractCache:
    """Sistema de caché para contratos"""
    
    def __init__(self, use_redis: bool = False, redis_host: str = None, redis_port: int = 6379):
        """
        Inicializa sistema de caché.
        
        Args:
            use_redis: Usar Redis para caché distribuido
            redis_host: Host de Redis
            redis_port: Puerto de Redis
        """
        self.use_redis = use_redis and REDIS_AVAILABLE
        self.cache_ttl = 3600  # 1 hora por defecto
        
        if self.use_redis:
            try:
                self.redis_client = redis.Redis(
                    host=redis_host or "localhost",
                    port=redis_port,
                    decode_responses=True
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache conectado")
            except Exception as e:
                logger.warning(f"Error conectando a Redis, usando caché en memoria: {e}")
                self.use_redis = False
                self.memory_cache = {}
        else:
            self.memory_cache = {}
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Genera clave de caché"""
        key_data = {
            "prefix": prefix,
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"contract_cache:{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene valor del caché"""
        if self.use_redis:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.warning(f"Error obteniendo de Redis cache: {e}")
                return None
        else:
            cached_item = self.memory_cache.get(key)
            if cached_item:
                expires_at = cached_item.get("expires_at")
                if expires_at and datetime.now() > expires_at:
                    del self.memory_cache[key]
                    return None
                return cached_item.get("value")
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = None) -> bool:
        """Guarda valor en caché"""
        ttl = ttl_seconds or self.cache_ttl
        
        if self.use_redis:
            try:
                self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value, default=str)
                )
                return True
            except Exception as e:
                logger.warning(f"Error guardando en Redis cache: {e}")
                return False
        else:
            expires_at = datetime.now() + timedelta(seconds=ttl)
            self.memory_cache[key] = {
                "value": value,
                "expires_at": expires_at
            }
            return True
    
    def delete(self, key: str) -> bool:
        """Elimina clave del caché"""
        if self.use_redis:
            try:
                return bool(self.redis_client.delete(key))
            except Exception as e:
                logger.warning(f"Error eliminando de Redis cache: {e}")
                return False
        else:
            if key in self.memory_cache:
                del self.memory_cache[key]
                return True
            return False
    
    def clear(self, prefix: str = None) -> int:
        """Limpia caché, opcionalmente por prefijo"""
        if self.use_redis:
            try:
                if prefix:
                    pattern = f"contract_cache:{prefix}:*"
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        return self.redis_client.delete(*keys)
                else:
                    # Limpiar todo el caché de contratos
                    pattern = "contract_cache:*"
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        return self.redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Error limpiando Redis cache: {e}")
                return 0
        else:
            if prefix:
                keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(f"contract_cache:{prefix}:")]
                for key in keys_to_delete:
                    del self.memory_cache[key]
                return len(keys_to_delete)
            else:
                count = len(self.memory_cache)
                self.memory_cache.clear()
                return count


# Instancia global de caché
_contract_cache = None


def get_contract_cache() -> ContractCache:
    """Obtiene instancia global de caché"""
    global _contract_cache
    if _contract_cache is None:
        import os
        use_redis = os.getenv("CONTRACT_CACHE_USE_REDIS", "false").lower() == "true"
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        _contract_cache = ContractCache(use_redis=use_redis, redis_host=redis_host, redis_port=redis_port)
    return _contract_cache


def cached(ttl_seconds: int = 3600, key_prefix: str = None):
    """
    Decorador para cachear resultados de funciones.
    
    Args:
        ttl_seconds: Tiempo de vida del caché en segundos
        key_prefix: Prefijo para la clave de caché
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_contract_cache()
            prefix = key_prefix or func.__name__
            cache_key = cache._generate_key(prefix, *args, **kwargs)
            
            # Intentar obtener del caché
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit para {func.__name__}")
                return cached_value
            
            # Ejecutar función y cachear resultado
            logger.debug(f"Cache miss para {func.__name__}, ejecutando función")
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator


# Ejemplo de uso del decorador
@cached(ttl_seconds=1800, key_prefix="template")
def get_template_cached(template_id: str, postgres_conn_id: str = "postgres_default"):
    """Versión con caché de get_template"""
    from data.airflow.plugins.contract_integrations import get_template
    return get_template(template_id, postgres_conn_id)

