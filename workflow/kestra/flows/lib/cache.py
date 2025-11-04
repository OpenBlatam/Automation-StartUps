"""
Caché simple para reducir llamadas repetidas a APIs.

Características:
- TTL-based caching
- Key-based invalidation
- Thread-safe (básico)
- Memory-efficient
"""
import time
import logging
import hashlib
import json
from typing import Any, Optional, Dict, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Entrada de caché con TTL."""
    value: Any
    expires_at: float
    created_at: float
    
    def is_expired(self) -> bool:
        """Verifica si la entrada ha expirado."""
        return time.time() > self.expires_at


class SimpleCache:
    """Caché simple con TTL."""
    
    def __init__(self, default_ttl: int = 300):
        """
        Inicializa el caché.
        
        Args:
            default_ttl: TTL por defecto en segundos (default: 5 minutos)
        """
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._hits = 0
        self._misses = 0
        
        logger.info("SimpleCache initialized", extra={"default_ttl": default_ttl})
    
    def _make_key(self, *args, **kwargs) -> str:
        """
        Genera una key única para los argumentos.
        
        Args:
            *args: Argumentos posicionales
            **kwargs: Argumentos de palabra clave
        
        Returns:
            Key única
        """
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items()) if kwargs else {}
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor del caché.
        
        Args:
            key: Key del caché
        
        Returns:
            Valor o None si no existe o expiró
        """
        entry = self._cache.get(key)
        
        if entry is None:
            self._misses += 1
            return None
        
        if entry.is_expired():
            del self._cache[key]
            self._misses += 1
            logger.debug(f"Cache key '{key}' expired")
            return None
        
        self._hits += 1
        return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Guarda un valor en el caché.
        
        Args:
            key: Key del caché
            value: Valor a guardar
            ttl: TTL en segundos (usa default si None)
        """
        ttl = ttl or self.default_ttl
        current_time = time.time()
        
        entry = CacheEntry(
            value=value,
            expires_at=current_time + ttl,
            created_at=current_time
        )
        
        self._cache[key] = entry
        logger.debug(f"Cached value for key '{key}' with TTL {ttl}s")
    
    def get_or_set(
        self,
        key: str,
        func: Callable[[], Any],
        ttl: Optional[int] = None
    ) -> Any:
        """
        Obtiene un valor del caché o lo calcula y guarda.
        
        Args:
            key: Key del caché
            func: Función para calcular el valor si no está en caché
            ttl: TTL en segundos (opcional)
        
        Returns:
            Valor del caché o calculado
        """
        value = self.get(key)
        if value is not None:
            return value
        
        # Calcular valor
        value = func()
        self.set(key, value, ttl)
        return value
    
    def clear(self, pattern: Optional[str] = None) -> int:
        """
        Limpia el caché.
        
        Args:
            pattern: Si se proporciona, limpia solo keys que contengan el patrón
        
        Returns:
            Número de entradas eliminadas
        """
        if pattern:
            keys_to_delete = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self._cache[key]
            count = len(keys_to_delete)
        else:
            count = len(self._cache)
            self._cache.clear()
        
        logger.info(f"Cache cleared", extra={"pattern": pattern, "entries_removed": count})
        return count
    
    def cleanup_expired(self) -> int:
        """
        Limpia entradas expiradas.
        
        Returns:
            Número de entradas eliminadas
        """
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del caché.
        
        Returns:
            Diccionario con estadísticas
        """
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "size": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 2),
            "total_requests": total_requests
        }


# Instancias globales de caché
_caches: Dict[str, SimpleCache] = {}


def get_cache(name: str = "default", default_ttl: int = 300) -> SimpleCache:
    """
    Obtiene o crea un caché por nombre.
    
    Args:
        name: Nombre del caché
        default_ttl: TTL por defecto en segundos
    
    Returns:
        Instancia de SimpleCache
    """
    if name not in _caches:
        _caches[name] = SimpleCache(default_ttl)
    return _caches[name]



