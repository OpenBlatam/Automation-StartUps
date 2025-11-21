"""
Sistema de Caché para Precios

Optimiza extracciones almacenando precios recientes
"""

import logging
import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class PriceCache:
    """Sistema de caché para precios de competencia"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.cache_dir = Path(config.get('cache_dir', '/tmp/price_cache'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = config.get('cache_ttl_seconds', 3600)  # 1 hora por defecto
        self.enabled = config.get('cache_enabled', True)
    
    def _get_cache_key(self, source: str, product_name: Optional[str] = None) -> str:
        """Genera clave de caché"""
        key_data = f"{source}:{product_name or 'all'}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Obtiene ruta del archivo de caché"""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, source: str, product_name: Optional[str] = None) -> Optional[List[Dict]]:
        """
        Obtiene precios desde caché
        
        Args:
            source: Nombre de la fuente
            product_name: Nombre del producto (opcional)
        
        Returns:
            Lista de precios o None si no está en caché/expirado
        """
        if not self.enabled:
            return None
        
        try:
            cache_key = self._get_cache_key(source, product_name)
            cache_path = self._get_cache_path(cache_key)
            
            if not cache_path.exists():
                return None
            
            # Verificar expiración
            cache_age = datetime.now().timestamp() - cache_path.stat().st_mtime
            if cache_age > self.ttl_seconds:
                logger.debug(f"Caché expirado para {source} (edad: {cache_age:.0f}s)")
                cache_path.unlink()  # Eliminar caché expirado
                return None
            
            # Leer caché
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            logger.debug(f"Cache hit para {source}")
            return cached_data.get('prices', [])
            
        except Exception as e:
            logger.warning(f"Error leyendo caché para {source}: {e}")
            return None
    
    def set(self, source: str, prices: List[Dict], product_name: Optional[str] = None):
        """
        Almacena precios en caché
        
        Args:
            source: Nombre de la fuente
            prices: Lista de precios a cachear
            product_name: Nombre del producto (opcional)
        """
        if not self.enabled:
            return
        
        try:
            cache_key = self._get_cache_key(source, product_name)
            cache_path = self._get_cache_path(cache_key)
            
            cache_data = {
                'source': source,
                'product_name': product_name,
                'prices': prices,
                'cached_at': datetime.now().isoformat(),
                'ttl_seconds': self.ttl_seconds,
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Precios cacheados para {source}: {len(prices)} productos")
            
        except Exception as e:
            logger.warning(f"Error escribiendo caché para {source}: {e}")
    
    def invalidate(self, source: Optional[str] = None):
        """
        Invalida caché
        
        Args:
            source: Fuente específica a invalidar (None = todas)
        """
        try:
            if source:
                cache_key = self._get_cache_key(source)
                cache_path = self._get_cache_path(cache_key)
                if cache_path.exists():
                    cache_path.unlink()
                    logger.info(f"Caché invalidado para {source}")
            else:
                # Invalidar todo
                for cache_file in self.cache_dir.glob("*.json"):
                    cache_file.unlink()
                logger.info("Todo el caché invalidado")
                
        except Exception as e:
            logger.warning(f"Error invalidando caché: {e}")
    
    def get_cache_stats(self) -> Dict:
        """Obtiene estadísticas del caché"""
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            return {
                'enabled': self.enabled,
                'cache_files': len(cache_files),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / 1024 / 1024, 2),
                'ttl_seconds': self.ttl_seconds,
            }
        except Exception as e:
            logger.warning(f"Error obteniendo stats de caché: {e}")
            return {'enabled': self.enabled, 'error': str(e)}








