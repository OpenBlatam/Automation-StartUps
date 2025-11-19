"""
Sistema de caché inteligente para evitar requests duplicados.

Incluye:
- Caché en memoria con TTL
- Caché persistente (opcional)
- Invalidación automática
- Prevención de duplicados
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    from cachetools import TTLCache
    CACHETOOLS_AVAILABLE = True
except ImportError:
    CACHETOOLS_AVAILABLE = False
    logger.warning("cachetools no disponible, usando caché simple")


@dataclass
class CacheEntry:
    """Entrada de caché."""
    key: str
    value: Any
    created_at: float
    expires_at: float
    hits: int = 0
    
    def is_expired(self) -> bool:
        """Verifica si la entrada ha expirado."""
        return time.time() > self.expires_at
    
    def hit(self):
        """Registra un hit en el caché."""
        self.hits += 1


class SimpleCache:
    """Caché simple en memoria (fallback si cachetools no está disponible)."""
    
    def __init__(self, maxsize: int = 100, ttl: int = 300):
        """
        Inicializa el caché simple.
        
        Args:
            maxsize: Tamaño máximo de entradas
            ttl: Tiempo de vida en segundos
        """
        self.maxsize = maxsize
        self.ttl = ttl
        self._cache: Dict[str, CacheEntry] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del caché."""
        entry = self._cache.get(key)
        
        if entry is None:
            return None
        
        if entry.is_expired():
            del self._cache[key]
            return None
        
        entry.hit()
        return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Almacena un valor en el caché."""
        ttl = ttl or self.ttl
        expires_at = time.time() + ttl
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=time.time(),
            expires_at=expires_at
        )
        
        # Limpiar entradas expiradas si el caché está lleno
        if len(self._cache) >= self.maxsize:
            self._cleanup_expired()
            
            # Si aún está lleno, eliminar la entrada más antigua
            if len(self._cache) >= self.maxsize:
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].created_at)
                del self._cache[oldest_key]
        
        self._cache[key] = entry
    
    def _cleanup_expired(self):
        """Limpia entradas expiradas."""
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self._cache[key]
    
    def clear(self):
        """Limpia todo el caché."""
        self._cache.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del caché."""
        self._cleanup_expired()
        
        total_hits = sum(entry.hits for entry in self._cache.values())
        
        return {
            "size": len(self._cache),
            "maxsize": self.maxsize,
            "total_hits": total_hits,
            "entries": [
                {
                    "key": entry.key,
                    "hits": entry.hits,
                    "age_seconds": time.time() - entry.created_at
                }
                for entry in self._cache.values()
            ]
        }


class AdsCache:
    """Sistema de caché para datos de ads."""
    
    def __init__(self, maxsize: int = 100, ttl: int = 300):
        """
        Inicializa el caché de ads.
        
        Args:
            maxsize: Tamaño máximo de entradas
            ttl: Tiempo de vida en segundos (default: 5 minutos)
        """
        if CACHETOOLS_AVAILABLE:
            self._cache = TTLCache(maxsize=maxsize, ttl=ttl)
        else:
            self._cache = SimpleCache(maxsize=maxsize, ttl=ttl)
        self.ttl = ttl
    
    def _generate_key(
        self,
        platform: str,
        operation: str,
        params: Dict[str, Any]
    ) -> str:
        """
        Genera una clave de caché única.
        
        Args:
            platform: Plataforma (facebook, tiktok, google)
            operation: Operación (campaign_performance, audience_performance, etc.)
            params: Parámetros de la operación
            
        Returns:
            Clave de caché
        """
        # Normalizar params para crear clave consistente
        normalized_params = json.dumps(params, sort_keys=True)
        
        key_string = f"{platform}:{operation}:{normalized_params}"
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def get(
        self,
        platform: str,
        operation: str,
        params: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Obtiene datos del caché.
        
        Args:
            platform: Plataforma
            operation: Operación
            params: Parámetros de la operación
            
        Returns:
            Datos cacheados o None si no existe
        """
        key = self._generate_key(platform, operation, params)
        
        if CACHETOOLS_AVAILABLE:
            return self._cache.get(key)
        else:
            return self._cache.get(key)
    
    def set(
        self,
        platform: str,
        operation: str,
        params: Dict[str, Any],
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        Almacena datos en el caché.
        
        Args:
            platform: Plataforma
            operation: Operación
            params: Parámetros de la operación
            value: Valor a almacenar
            ttl: Tiempo de vida específico (opcional)
        """
        key = self._generate_key(platform, operation, params)
        
        if CACHETOOLS_AVAILABLE:
            self._cache[key] = value
        else:
            self._cache.set(key, value, ttl=ttl or self.ttl)
    
    def invalidate(
        self,
        platform: Optional[str] = None,
        operation: Optional[str] = None
    ) -> int:
        """
        Invalida entradas del caché.
        
        Args:
            platform: Plataforma específica (None para todas)
            operation: Operación específica (None para todas)
            
        Returns:
            Número de entradas invalidadas
        """
        if not CACHETOOLS_AVAILABLE:
            # Para SimpleCache, necesitamos implementar invalidación manual
            if platform is None and operation is None:
                self._cache.clear()
                return 0
            else:
                # Invalidación selectiva más compleja - simplificamos
                logger.warning("Invalidación selectiva no disponible con SimpleCache")
                return 0
        
        # Para TTLCache, la invalidación es automática por TTL
        # Podríamos implementar invalidación manual si es necesario
        return 0
    
    def clear(self):
        """Limpia todo el caché."""
        if CACHETOOLS_AVAILABLE:
            self._cache.clear()
        else:
            self._cache.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del caché."""
        if CACHETOOLS_AVAILABLE:
            return {
                "size": len(self._cache),
                "maxsize": self._cache.maxsize,
                "ttl": self._cache.ttl
            }
        else:
            return self._cache.stats()


# Instancia global del caché (puede ser reemplazada)
_global_cache: Optional[AdsCache] = None


def get_cache(maxsize: int = 100, ttl: int = 300) -> AdsCache:
    """
    Obtiene o crea la instancia global del caché.
    
    Args:
        maxsize: Tamaño máximo (solo se aplica en primera llamada)
        ttl: Tiempo de vida (solo se aplica en primera llamada)
        
    Returns:
        Instancia del caché
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = AdsCache(maxsize=maxsize, ttl=ttl)
    return _global_cache


def set_cache(cache: AdsCache) -> None:
    """Establece la instancia global del caché."""
    global _global_cache
    _global_cache = cache

