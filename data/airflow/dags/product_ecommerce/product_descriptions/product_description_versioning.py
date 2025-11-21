"""
Sistema de versionado y control de cambios para descripciones.

Incluye:
- Historial de versiones
- Comparación de cambios
- Rollback a versiones anteriores
- Diferencias detalladas
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import json
import hashlib
from difflib import unified_diff

logger = logging.getLogger(__name__)


class DescriptionVersionControl:
    """Sistema de control de versiones para descripciones."""
    
    def __init__(self):
        self.versions = {}
    
    def create_version(self, description_id: str, description_data: Dict, metadata: Dict = None) -> str:
        """
        Crea una nueva versión de una descripción.
        
        Args:
            description_id: ID de la descripción
            description_data: Datos de la descripción
            metadata: Metadata adicional (autor, motivo, etc.)
        
        Returns:
            Versión ID creada
        """
        if description_id not in self.versions:
            self.versions[description_id] = []
        
        # Generar hash del contenido
        content_hash = self._generate_hash(description_data)
        
        # Verificar si es diferente a la última versión
        if self.versions[description_id]:
            last_version = self.versions[description_id][-1]
            if last_version['content_hash'] == content_hash:
                logger.info(f"Contenido idéntico a versión anterior, no se crea nueva versión")
                return last_version['version_id']
        
        version_id = f"{description_id}_v{len(self.versions[description_id]) + 1}"
        
        version = {
            'version_id': version_id,
            'description_id': description_id,
            'description_data': description_data,
            'content_hash': content_hash,
            'created_at': datetime.now().isoformat(),
            'metadata': metadata or {},
            'is_current': True
        }
        
        # Marcar versiones anteriores como no actuales
        for v in self.versions[description_id]:
            v['is_current'] = False
        
        self.versions[description_id].append(version)
        
        logger.info(f"Versión creada: {version_id}")
        return version_id
    
    def get_version(self, description_id: str, version_id: Optional[str] = None) -> Optional[Dict]:
        """
        Obtiene una versión específica o la actual.
        
        Args:
            description_id: ID de la descripción
            version_id: ID de versión específica (None para actual)
        
        Returns:
            Datos de la versión o None
        """
        if description_id not in self.versions:
            return None
        
        if version_id:
            for version in self.versions[description_id]:
                if version['version_id'] == version_id:
                    return version
            return None
        else:
            # Retornar versión actual
            for version in reversed(self.versions[description_id]):
                if version.get('is_current', True):
                    return version
            return self.versions[description_id][-1] if self.versions[description_id] else None
    
    def get_version_history(self, description_id: str) -> List[Dict]:
        """
        Obtiene historial completo de versiones.
        
        Args:
            description_id: ID de la descripción
        
        Returns:
            Lista de versiones ordenadas por fecha
        """
        if description_id not in self.versions:
            return []
        
        return sorted(
            self.versions[description_id],
            key=lambda x: x['created_at'],
            reverse=True
        )
    
    def compare_versions(self, description_id: str, version1_id: str, version2_id: str) -> Dict:
        """
        Compara dos versiones de una descripción.
        
        Args:
            description_id: ID de la descripción
            version1_id: ID de primera versión
            version2_id: ID de segunda versión
        
        Returns:
            Dict con comparación detallada
        """
        v1 = self.get_version(description_id, version1_id)
        v2 = self.get_version(description_id, version2_id)
        
        if not v1 or not v2:
            return {'error': 'Una o ambas versiones no encontradas'}
        
        desc1 = v1['description_data'].get('description', '')
        desc2 = v2['description_data'].get('description', '')
        
        # Calcular diferencias
        diff_lines = list(unified_diff(
            desc1.splitlines(keepends=True),
            desc2.splitlines(keepends=True),
            fromfile=version1_id,
            tofile=version2_id,
            lineterm=''
        ))
        
        # Estadísticas de cambios
        changes = {
            'added_words': len(desc2.split()) - len(desc1.split()),
            'added_chars': len(desc2) - len(desc1),
            'seo_score_change': (
                v2['description_data'].get('seo_analysis', {}).get('score', 0) -
                v1['description_data'].get('seo_analysis', {}).get('score', 0)
            ),
            'word_count_change': (
                v2['description_data'].get('word_count', 0) -
                v1['description_data'].get('word_count', 0)
            )
        }
        
        return {
            'version1': {
                'version_id': version1_id,
                'created_at': v1['created_at'],
                'word_count': v1['description_data'].get('word_count', 0),
                'seo_score': v1['description_data'].get('seo_analysis', {}).get('score', 0)
            },
            'version2': {
                'version_id': version2_id,
                'created_at': v2['created_at'],
                'word_count': v2['description_data'].get('word_count', 0),
                'seo_score': v2['description_data'].get('seo_analysis', {}).get('score', 0)
            },
            'changes': changes,
            'diff': ''.join(diff_lines),
            'summary': self._generate_change_summary(changes)
        }
    
    def rollback_to_version(self, description_id: str, version_id: str) -> Dict:
        """
        Hace rollback a una versión anterior.
        
        Args:
            description_id: ID de la descripción
            version_id: ID de versión a restaurar
        
        Returns:
            Dict con resultado del rollback
        """
        target_version = self.get_version(description_id, version_id)
        
        if not target_version:
            return {'error': 'Versión no encontrada'}
        
        # Crear nueva versión basada en la versión objetivo
        new_version_id = self.create_version(
            description_id,
            target_version['description_data'],
            metadata={
                'rollback_from': version_id,
                'rollback_at': datetime.now().isoformat(),
                'reason': 'Rollback to previous version'
            }
        )
        
        return {
            'success': True,
            'restored_version': version_id,
            'new_version_id': new_version_id,
            'description_data': target_version['description_data']
        }
    
    def _generate_hash(self, description_data: Dict) -> str:
        """Genera hash del contenido para detectar cambios."""
        content = json.dumps(description_data, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def _generate_change_summary(self, changes: Dict) -> str:
        """Genera resumen de cambios."""
        summary_parts = []
        
        if changes['added_words'] > 0:
            summary_parts.append(f"Agregadas {changes['added_words']} palabras")
        elif changes['added_words'] < 0:
            summary_parts.append(f"Removidas {abs(changes['added_words'])} palabras")
        
        if changes['seo_score_change'] > 0:
            summary_parts.append(f"SEO mejoró {changes['seo_score_change']:.1f} puntos")
        elif changes['seo_score_change'] < 0:
            summary_parts.append(f"SEO disminuyó {abs(changes['seo_score_change']):.1f} puntos")
        
        if not summary_parts:
            summary_parts.append("Cambios menores")
        
        return "; ".join(summary_parts)






