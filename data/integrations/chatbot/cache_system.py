"""
Sistema de Cache para Respuestas Frecuentes
Versión: 2.0.0
Mejora el rendimiento cacheando respuestas comunes
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional
from pathlib import Path
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


class CacheSystem:
    """
    Sistema de cache inteligente para respuestas del chatbot
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Args:
            max_size: Tamaño máximo del cache (LRU)
            ttl_seconds: Tiempo de vida de las entradas en segundos
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict = OrderedDict()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
        self.cache_file = Path("cache_data.json")
        self._load_cache()
    
    def _generate_key(self, message: str, language: str, user_context: Dict = None) -> str:
        """Genera una clave única para el cache"""
        # Normalizar mensaje
        normalized = message.lower().strip()
        
        # Incluir contexto relevante si existe
        context_str = ""
        if user_context:
            # Solo incluir contexto que afecte la respuesta
            relevant_context = {
                "language": user_context.get("language"),
                "channel": user_context.get("channel")
            }
            context_str = json.dumps(relevant_context, sort_keys=True)
        
        # Crear hash
        key_string = f"{normalized}:{language}:{context_str}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, message: str, language: str, user_context: Dict = None) -> Optional[Dict]:
        """
        Obtiene una respuesta del cache si existe y no ha expirado
        
        Returns:
            Dict con la respuesta cacheada o None
        """
        key = self._generate_key(message, language, user_context)
        
        if key in self.cache:
            entry = self.cache[key]
            
            # Verificar si ha expirado
            if datetime.now() - entry["timestamp"] < timedelta(seconds=self.ttl_seconds):
                # Mover al final (LRU)
                self.cache.move_to_end(key)
                self.stats["hits"] += 1
                logger.debug(f"Cache HIT: {key[:8]}")
                return entry["response"]
            else:
                # Expiró, eliminar
                del self.cache[key]
                self.stats["misses"] += 1
                logger.debug(f"Cache MISS (expired): {key[:8]}")
        else:
            self.stats["misses"] += 1
            logger.debug(f"Cache MISS: {key[:8]}")
        
        return None
    
    def set(self, message: str, language: str, response: Dict, 
            user_context: Dict = None, priority: int = 0):
        """
        Almacena una respuesta en el cache
        
        Args:
            message: Mensaje original
            language: Idioma
            response: Respuesta a cachear
            user_context: Contexto del usuario
            priority: Prioridad (mayor = más importante, se cachea más tiempo)
        """
        key = self._generate_key(message, language, user_context)
        
        # Si el cache está lleno, eliminar el más antiguo
        if len(self.cache) >= self.max_size and key not in self.cache:
            # Eliminar el más antiguo (LRU)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            self.stats["evictions"] += 1
        
        # Calcular TTL basado en prioridad
        ttl = self.ttl_seconds
        if priority > 0:
            ttl = self.ttl_seconds * (1 + priority * 0.5)  # Hasta 50% más tiempo
        
        entry = {
            "response": response,
            "timestamp": datetime.now(),
            "ttl": ttl,
            "priority": priority,
            "hits": 0
        }
        
        self.cache[key] = entry
        self.cache.move_to_end(key)  # Mover al final (más reciente)
        
        logger.debug(f"Cache SET: {key[:8]}")
    
    def invalidate(self, pattern: str = None):
        """
        Invalida entradas del cache
        
        Args:
            pattern: Patrón para invalidar (si None, limpia todo)
        """
        if pattern is None:
            self.cache.clear()
            logger.info("Cache limpiado completamente")
        else:
            # Invalidar por patrón (implementación básica)
            keys_to_remove = [
                key for key in self.cache.keys()
                if pattern.lower() in str(self.cache[key].get("response", {})).lower()
            ]
            for key in keys_to_remove:
                del self.cache[key]
            logger.info(f"Invalidadas {len(keys_to_remove)} entradas del cache")
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del cache"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": round(hit_rate, 2),
            "evictions": self.stats["evictions"],
            "total_requests": total_requests
        }
    
    def get_top_cached(self, limit: int = 10) -> list:
        """Obtiene las entradas más accedidas del cache"""
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: x[1].get("hits", 0),
            reverse=True
        )
        return [
            {
                "key": key[:8],
                "hits": entry.get("hits", 0),
                "age": (datetime.now() - entry["timestamp"]).total_seconds()
            }
            for key, entry in sorted_entries[:limit]
        ]
    
    def _load_cache(self):
        """Carga el cache desde disco"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convertir timestamps de string a datetime
                    for key, entry in data.items():
                        entry["timestamp"] = datetime.fromisoformat(entry["timestamp"])
                    self.cache = OrderedDict(data)
                logger.info(f"Cache cargado: {len(self.cache)} entradas")
        except Exception as e:
            logger.warning(f"No se pudo cargar cache: {e}")
    
    def save_cache(self):
        """Guarda el cache en disco"""
        try:
            # Convertir datetime a string para JSON
            cache_data = {}
            for key, entry in self.cache.items():
                cache_data[key] = {
                    **entry,
                    "timestamp": entry["timestamp"].isoformat()
                }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Cache guardado: {len(self.cache)} entradas")
        except Exception as e:
            logger.error(f"Error guardando cache: {e}")
    
    def cleanup_expired(self):
        """Limpia entradas expiradas del cache"""
        now = datetime.now()
        expired_keys = [
            key for key, entry in self.cache.items()
            if now - entry["timestamp"] > timedelta(seconds=entry.get("ttl", self.ttl_seconds))
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Limpiadas {len(expired_keys)} entradas expiradas del cache")
        
        return len(expired_keys)






