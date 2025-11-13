#!/usr/bin/env python3
"""
Sistema de Versionado de Contenido para Testimonios
Mantiene historial de versiones y permite comparación y rollback
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class ContentVersion:
    """Versión de contenido"""
    version_id: str
    timestamp: datetime
    post_data: Dict[str, Any]
    changes_summary: str
    author: Optional[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class VersionControl:
    """Sistema de control de versiones para contenido"""
    
    def __init__(self, storage_file: Optional[str] = None):
        """
        Inicializa el sistema de versionado
        
        Args:
            storage_file: Archivo para almacenar versiones
        """
        self.storage_file = storage_file or "data/testimonial_versions.json"
        self.versions: Dict[str, List[ContentVersion]] = defaultdict(list)
        self._load_versions()
    
    def _load_versions(self):
        """Carga versiones desde archivo"""
        storage_path = Path(self.storage_file)
        if storage_path.exists():
            try:
                with open(storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for post_id, versions_data in data.items():
                        self.versions[post_id] = [
                            ContentVersion(
                                version_id=v['version_id'],
                                timestamp=datetime.fromisoformat(v['timestamp']),
                                post_data=v['post_data'],
                                changes_summary=v['changes_summary'],
                                author=v.get('author'),
                                tags=v.get('tags', [])
                            )
                            for v in versions_data
                        ]
                logger.info(f"Versiones cargadas: {len(self.versions)} posts")
            except Exception as e:
                logger.warning(f"Error al cargar versiones: {e}")
    
    def _save_versions(self):
        """Guarda versiones en archivo"""
        try:
            storage_path = Path(self.storage_file)
            storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {}
            for post_id, versions in self.versions.items():
                data[post_id] = [
                    {
                        'version_id': v.version_id,
                        'timestamp': v.timestamp.isoformat(),
                        'post_data': v.post_data,
                        'changes_summary': v.changes_summary,
                        'author': v.author,
                        'tags': v.tags
                    }
                    for v in versions
                ]
            
            with open(storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Error al guardar versiones: {e}")
    
    def _generate_version_id(self, post_data: Dict[str, Any]) -> str:
        """Genera un ID único para la versión"""
        content_hash = hashlib.md5(
            json.dumps(post_data, sort_keys=True).encode()
        ).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"v{timestamp}_{content_hash}"
    
    def create_version(
        self,
        post_id: str,
        post_data: Dict[str, Any],
        changes_summary: str = "",
        author: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> ContentVersion:
        """
        Crea una nueva versión del contenido
        
        Args:
            post_id: ID único del post
            post_data: Datos completos del post
            changes_summary: Resumen de cambios
            author: Autor de la versión
            tags: Tags para categorizar
        
        Returns:
            ContentVersion creada
        """
        # Comparar con versión anterior para generar resumen automático
        if not changes_summary and self.versions[post_id]:
            previous = self.versions[post_id][-1]
            changes_summary = self._compare_versions(previous.post_data, post_data)
        
        version = ContentVersion(
            version_id=self._generate_version_id(post_data),
            timestamp=datetime.now(),
            post_data=post_data.copy(),
            changes_summary=changes_summary or "Versión inicial",
            author=author,
            tags=tags or []
        )
        
        self.versions[post_id].append(version)
        self._save_versions()
        
        logger.info(f"Versión creada: {version.version_id} para post {post_id}")
        return version
    
    def _compare_versions(
        self,
        old_data: Dict[str, Any],
        new_data: Dict[str, Any]
    ) -> str:
        """Compara dos versiones y genera resumen de cambios"""
        changes = []
        
        # Comparar contenido
        old_content = old_data.get('post_content', '')
        new_content = new_data.get('post_content', '')
        if old_content != new_content:
            changes.append("Contenido modificado")
        
        # Comparar hashtags
        old_hashtags = set(old_data.get('hashtags', []))
        new_hashtags = set(new_data.get('hashtags', []))
        if old_hashtags != new_hashtags:
            added = new_hashtags - old_hashtags
            removed = old_hashtags - new_hashtags
            if added:
                changes.append(f"Hashtags agregados: {len(added)}")
            if removed:
                changes.append(f"Hashtags removidos: {len(removed)}")
        
        # Comparar CTA
        old_cta = old_data.get('call_to_action', '')
        new_cta = new_data.get('call_to_action', '')
        if old_cta != new_cta:
            changes.append("CTA modificado")
        
        # Comparar predicción de engagement
        old_score = old_data.get('engagement_prediction', {}).get('predicted_score', 0)
        new_score = new_data.get('engagement_prediction', {}).get('predicted_score', 0)
        if old_score != new_score:
            diff = new_score - old_score
            changes.append(f"Score de engagement: {old_score:.1f} → {new_score:.1f} ({diff:+.1f})")
        
        return "; ".join(changes) if changes else "Sin cambios detectados"
    
    def get_versions(self, post_id: str) -> List[ContentVersion]:
        """Obtiene todas las versiones de un post"""
        return self.versions.get(post_id, [])
    
    def get_latest_version(self, post_id: str) -> Optional[ContentVersion]:
        """Obtiene la última versión de un post"""
        versions = self.versions.get(post_id, [])
        return versions[-1] if versions else None
    
    def get_version(self, post_id: str, version_id: str) -> Optional[ContentVersion]:
        """Obtiene una versión específica"""
        versions = self.versions.get(post_id, [])
        for version in versions:
            if version.version_id == version_id:
                return version
        return None
    
    def compare_versions(
        self,
        post_id: str,
        version_id_1: str,
        version_id_2: str
    ) -> Dict[str, Any]:
        """
        Compara dos versiones específicas
        
        Args:
            post_id: ID del post
            version_id_1: ID de la primera versión
            version_id_2: ID de la segunda versión
        
        Returns:
            Dict con comparación detallada
        """
        v1 = self.get_version(post_id, version_id_1)
        v2 = self.get_version(post_id, version_id_2)
        
        if not v1 or not v2:
            return {"error": "Una o ambas versiones no encontradas"}
        
        comparison = {
            "version_1": {
                "version_id": v1.version_id,
                "timestamp": v1.timestamp.isoformat(),
                "score": v1.post_data.get('engagement_prediction', {}).get('predicted_score', 0)
            },
            "version_2": {
                "version_id": v2.version_id,
                "timestamp": v2.timestamp.isoformat(),
                "score": v2.post_data.get('engagement_prediction', {}).get('predicted_score', 0)
            },
            "changes": self._compare_versions(v1.post_data, v2.post_data),
            "improvement": v2.post_data.get('engagement_prediction', {}).get('predicted_score', 0) - 
                          v1.post_data.get('engagement_prediction', {}).get('predicted_score', 0)
        }
        
        return comparison
    
    def rollback_to_version(
        self,
        post_id: str,
        version_id: str
    ) -> Optional[ContentVersion]:
        """
        Restaura una versión anterior
        
        Args:
            post_id: ID del post
            version_id: ID de la versión a restaurar
        
        Returns:
            ContentVersion restaurada o None
        """
        target_version = self.get_version(post_id, version_id)
        if not target_version:
            return None
        
        # Crear nueva versión basada en la versión objetivo
        restored = self.create_version(
            post_id=post_id,
            post_data=target_version.post_data.copy(),
            changes_summary=f"Rollback a versión {version_id}",
            tags=["rollback"]
        )
        
        logger.info(f"Rollback realizado: {post_id} → {version_id}")
        return restored
    
    def get_version_history(self, post_id: str) -> Dict[str, Any]:
        """Obtiene historial completo de versiones"""
        versions = self.get_versions(post_id)
        
        if not versions:
            return {"error": "No hay versiones para este post"}
        
        return {
            "post_id": post_id,
            "total_versions": len(versions),
            "versions": [
                {
                    "version_id": v.version_id,
                    "timestamp": v.timestamp.isoformat(),
                    "changes": v.changes_summary,
                    "author": v.author,
                    "tags": v.tags,
                    "score": v.post_data.get('engagement_prediction', {}).get('predicted_score', 0)
                }
                for v in versions
            ],
            "latest_version": versions[-1].version_id,
            "first_version": versions[0].version_id
        }


