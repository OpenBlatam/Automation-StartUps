"""
Sistema de Versionado de Precios

Gestiona versiones y cambios de precios con rollback
"""

import logging
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from copy import deepcopy

logger = logging.getLogger(__name__)


class PriceVersioning:
    """Gestiona versionado de precios con capacidad de rollback"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.versions_dir = Path(config.get('versions_dir', '/tmp/price_versions'))
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        self.max_versions = config.get('max_versions_per_product', 50)
    
    def create_version(
        self,
        product_id: str,
        price_data: Dict,
        version_metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Crea una nueva versión de precio
        
        Args:
            product_id: ID del producto
            price_data: Datos del precio
            version_metadata: Metadatos adicionales
        
        Returns:
            Información de la versión creada
        """
        version_id = f"{product_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        version = {
            'version_id': version_id,
            'product_id': product_id,
            'price_data': deepcopy(price_data),
            'created_at': datetime.now().isoformat(),
            'metadata': version_metadata or {},
        }
        
        # Guardar versión
        self._save_version(version)
        
        # Limpiar versiones antiguas
        self._cleanup_old_versions(product_id)
        
        logger.info(f"Versión creada: {version_id}")
        
        return version
    
    def get_version(self, version_id: str) -> Optional[Dict]:
        """Obtiene una versión específica"""
        version_file = self.versions_dir / f"{version_id}.json"
        
        if version_file.exists():
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error leyendo versión {version_id}: {e}")
        
        return None
    
    def get_product_versions(
        self,
        product_id: str,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Obtiene todas las versiones de un producto
        
        Args:
            product_id: ID del producto
            limit: Límite de versiones a retornar
        
        Returns:
            Lista de versiones ordenadas por fecha
        """
        versions = []
        
        for version_file in self.versions_dir.glob(f"{product_id}_*.json"):
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    version = json.load(f)
                    versions.append(version)
            except Exception as e:
                logger.warning(f"Error leyendo {version_file}: {e}")
        
        # Ordenar por fecha (más reciente primero)
        versions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        if limit:
            versions = versions[:limit]
        
        return versions
    
    def get_current_version(self, product_id: str) -> Optional[Dict]:
        """Obtiene la versión actual (más reciente) de un producto"""
        versions = self.get_product_versions(product_id, limit=1)
        return versions[0] if versions else None
    
    def rollback_to_version(
        self,
        product_id: str,
        version_id: str
    ) -> Dict:
        """
        Hace rollback a una versión específica
        
        Args:
            product_id: ID del producto
            version_id: ID de la versión a restaurar
        
        Returns:
            Nueva versión creada con datos del rollback
        """
        target_version = self.get_version(version_id)
        
        if not target_version:
            raise ValueError(f"Versión {version_id} no encontrada")
        
        if target_version['product_id'] != product_id:
            raise ValueError("Versión no corresponde al producto")
        
        # Crear nueva versión con datos del rollback
        rollback_version = self.create_version(
            product_id,
            target_version['price_data'],
            version_metadata={
                'rollback_from': version_id,
                'rollback_at': datetime.now().isoformat(),
                'original_created_at': target_version['created_at'],
            }
        )
        
        logger.info(f"Rollback realizado: {product_id} -> {version_id}")
        
        return rollback_version
    
    def compare_versions(
        self,
        version_id_1: str,
        version_id_2: str
    ) -> Dict:
        """
        Compara dos versiones
        
        Args:
            version_id_1: ID de la primera versión
            version_id_2: ID de la segunda versión
        
        Returns:
            Comparación detallada
        """
        v1 = self.get_version(version_id_1)
        v2 = self.get_version(version_id_2)
        
        if not v1 or not v2:
            raise ValueError("Una o ambas versiones no encontradas")
        
        price1 = v1['price_data'].get('price', 0)
        price2 = v2['price_data'].get('price', 0)
        
        price_diff = price2 - price1
        price_diff_pct = (price_diff / price1 * 100) if price1 > 0 else 0
        
        return {
            'version_1': {
                'version_id': version_id_1,
                'price': price1,
                'created_at': v1['created_at'],
            },
            'version_2': {
                'version_id': version_id_2,
                'price': price2,
                'created_at': v2['created_at'],
            },
            'differences': {
                'price_diff': round(price_diff, 2),
                'price_diff_percent': round(price_diff_pct, 2),
                'is_increase': price_diff > 0,
                'is_decrease': price_diff < 0,
            },
            'time_diff_seconds': (
                datetime.fromisoformat(v2['created_at']) -
                datetime.fromisoformat(v1['created_at'])
            ).total_seconds(),
        }
    
    def _save_version(self, version: Dict):
        """Guarda versión en archivo"""
        try:
            version_file = self.versions_dir / f"{version['version_id']}.json"
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(version, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando versión: {e}")
    
    def _cleanup_old_versions(self, product_id: str):
        """Elimina versiones antiguas excedentes"""
        versions = self.get_product_versions(product_id)
        
        if len(versions) > self.max_versions:
            # Eliminar las más antiguas
            to_remove = versions[self.max_versions:]
            for version in to_remove:
                version_file = self.versions_dir / f"{version['version_id']}.json"
                if version_file.exists():
                    version_file.unlink()
                    logger.debug(f"Versión antigua eliminada: {version['version_id']}")








