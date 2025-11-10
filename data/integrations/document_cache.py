"""
Sistema de Cache Inteligente para Documentos
============================================

Cachea resultados de OCR y procesamiento para evitar reprocesamiento.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import hashlib
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
import pickle

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Entrada de cache"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    hits: int = 0
    
    def is_expired(self) -> bool:
        """Verifica si la entrada está expirada"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


class DocumentCache:
    """Cache para resultados de procesamiento"""
    
    def __init__(
        self,
        cache_dir: str = "./.cache",
        default_ttl: int = 86400,  # 24 horas
        max_size: int = 1000
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.logger = logging.getLogger(__name__)
        self._memory_cache: Dict[str, CacheEntry] = {}
    
    def _generate_key(self, file_path: str, config: Dict[str, Any]) -> str:
        """Genera clave de cache basada en archivo y configuración"""
        # Calcular hash del archivo
        file_hash = self._calculate_file_hash(file_path)
        
        # Hash de configuración
        config_str = json.dumps(config, sort_keys=True)
        config_hash = hashlib.md5(config_str.encode()).hexdigest()[:8]
        
        return f"{file_hash}_{config_hash}"
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcula hash SHA256 de un archivo"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculando hash: {e}")
            return ""
    
    def get(
        self,
        file_path: str,
        config: Dict[str, Any]
    ) -> Optional[Any]:
        """Obtiene valor del cache"""
        key = self._generate_key(file_path, config)
        
        # Intentar desde memoria
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            if not entry.is_expired():
                entry.hits += 1
                self.logger.debug(f"Cache hit (memoria): {key[:16]}...")
                return entry.value
            else:
                del self._memory_cache[key]
        
        # Intentar desde disco
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    entry: CacheEntry = pickle.load(f)
                
                if not entry.is_expired():
                    entry.hits += 1
                    # Cargar a memoria
                    self._memory_cache[key] = entry
                    self.logger.debug(f"Cache hit (disco): {key[:16]}...")
                    return entry.value
                else:
                    # Eliminar expirado
                    cache_file.unlink()
            except Exception as e:
                self.logger.warning(f"Error cargando cache: {e}")
        
        self.logger.debug(f"Cache miss: {key[:16]}...")
        return None
    
    def set(
        self,
        file_path: str,
        config: Dict[str, Any],
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Guarda valor en cache"""
        key = self._generate_key(file_path, config)
        ttl = ttl or self.default_ttl
        
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            expires_at=expires_at,
            hits=0
        )
        
        # Guardar en memoria
        self._memory_cache[key] = entry
        
        # Limpiar cache si excede tamaño
        if len(self._memory_cache) > self.max_size:
            self._cleanup_memory_cache()
        
        # Guardar en disco
        try:
            cache_file = self.cache_dir / f"{key}.pkl"
            with open(cache_file, 'wb') as f:
                pickle.dump(entry, f)
            
            self.logger.debug(f"Cache guardado: {key[:16]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando cache: {e}")
            return False
    
    def _cleanup_memory_cache(self):
        """Limpia cache de memoria (elimina menos usados)"""
        if not self._memory_cache:
            return
        
        # Ordenar por hits y eliminar los menos usados
        sorted_entries = sorted(
            self._memory_cache.items(),
            key=lambda x: (x[1].hits, x[1].created_at)
        )
        
        # Eliminar el 20% menos usado
        to_remove = int(len(sorted_entries) * 0.2)
        for key, _ in sorted_entries[:to_remove]:
            del self._memory_cache[key]
    
    def clear(self, expired_only: bool = True):
        """Limpia cache"""
        if expired_only:
            # Solo eliminar expirados
            for key, entry in list(self._memory_cache.items()):
                if entry.is_expired():
                    del self._memory_cache[key]
            
            # Limpiar disco
            for cache_file in self.cache_dir.glob("*.pkl"):
                try:
                    with open(cache_file, 'rb') as f:
                        entry: CacheEntry = pickle.load(f)
                    if entry.is_expired():
                        cache_file.unlink()
                except:
                    cache_file.unlink()
        else:
            # Limpiar todo
            self._memory_cache.clear()
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache"""
        total_entries = len(self._memory_cache)
        expired = sum(1 for e in self._memory_cache.values() if e.is_expired())
        
        # Estadísticas de disco
        disk_files = list(self.cache_dir.glob("*.pkl"))
        disk_size = sum(f.stat().st_size for f in disk_files)
        
        total_hits = sum(e.hits for e in self._memory_cache.values())
        
        return {
            "memory_entries": total_entries,
            "memory_expired": expired,
            "disk_entries": len(disk_files),
            "disk_size_mb": disk_size / (1024 * 1024),
            "total_hits": total_hits,
            "avg_hits_per_entry": total_hits / total_entries if total_entries > 0 else 0
        }

