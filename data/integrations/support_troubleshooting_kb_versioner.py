"""
Sistema de Versionado para Base de Conocimiento
Permite versionar cambios en la KB y hacer rollback si es necesario
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import hashlib
import shutil

logger = logging.getLogger(__name__)


class KnowledgeBaseVersioner:
    """Gestiona versionado de la base de conocimiento"""
    
    def __init__(self, kb_path: str, versions_dir: str = None):
        self.kb_path = Path(kb_path)
        if versions_dir is None:
            versions_dir = self.kb_path.parent / "kb_versions"
        self.versions_dir = Path(versions_dir)
        self.versions_dir.mkdir(exist_ok=True)
        self.version_history_file = self.versions_dir / "version_history.json"
        self._load_version_history()
    
    def _load_version_history(self):
        """Carga historial de versiones"""
        if self.version_history_file.exists():
            with open(self.version_history_file, 'r') as f:
                self.version_history = json.load(f)
        else:
            self.version_history = []
    
    def _save_version_history(self):
        """Guarda historial de versiones"""
        with open(self.version_history_file, 'w') as f:
            json.dump(self.version_history, f, indent=2)
    
    def create_version(
        self,
        description: str,
        author: str = "system",
        tags: List[str] = None
    ) -> str:
        """
        Crea una nueva versión de la KB
        
        Returns:
            Version ID
        """
        if not self.kb_path.exists():
            raise FileNotFoundError(f"KB file not found: {self.kb_path}")
        
        # Leer KB actual
        with open(self.kb_path, 'r', encoding='utf-8') as f:
            kb_content = f.read()
        
        # Calcular hash
        kb_hash = hashlib.sha256(kb_content.encode()).hexdigest()
        
        # Verificar si es diferente a la última versión
        if self.version_history:
            last_version = self.version_history[-1]
            if last_version.get("hash") == kb_hash:
                logger.info("No hay cambios desde la última versión")
                return last_version["version_id"]
        
        # Crear versión
        version_id = f"v{len(self.version_history) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        version_file = self.versions_dir / f"{version_id}.json"
        
        # Copiar KB a versión
        shutil.copy(self.kb_path, version_file)
        
        # Registrar en historial
        version_info = {
            "version_id": version_id,
            "created_at": datetime.now().isoformat(),
            "description": description,
            "author": author,
            "tags": tags or [],
            "hash": kb_hash,
            "file": str(version_file),
            "problem_count": len(json.loads(kb_content))
        }
        
        self.version_history.append(version_info)
        self._save_version_history()
        
        logger.info(f"Versión creada: {version_id}")
        return version_id
    
    def list_versions(self) -> List[Dict]:
        """Lista todas las versiones"""
        return self.version_history.copy()
    
    def get_version(self, version_id: str) -> Optional[Dict]:
        """Obtiene información de una versión específica"""
        for version in self.version_history:
            if version["version_id"] == version_id:
                return version
        return None
    
    def restore_version(self, version_id: str) -> bool:
        """Restaura una versión específica"""
        version_info = self.get_version(version_id)
        if not version_info:
            logger.error(f"Versión no encontrada: {version_id}")
            return False
        
        version_file = Path(version_info["file"])
        if not version_file.exists():
            logger.error(f"Archivo de versión no encontrado: {version_file}")
            return False
        
        # Hacer backup de versión actual
        current_backup = f"{self.kb_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if self.kb_path.exists():
            shutil.copy(self.kb_path, current_backup)
        
        # Restaurar versión
        shutil.copy(version_file, self.kb_path)
        
        logger.info(f"Versión {version_id} restaurada. Backup guardado en {current_backup}")
        return True
    
    def compare_versions(self, version_id1: str, version_id2: str) -> Dict:
        """Compara dos versiones"""
        v1_info = self.get_version(version_id1)
        v2_info = self.get_version(version_id2)
        
        if not v1_info or not v2_info:
            return {"error": "Una o ambas versiones no encontradas"}
        
        v1_file = Path(v1_info["file"])
        v2_file = Path(v2_info["file"])
        
        with open(v1_file, 'r') as f:
            v1_data = json.load(f)
        with open(v2_file, 'r') as f:
            v2_data = json.load(f)
        
        v1_problems = set(v1_data.keys())
        v2_problems = set(v2_data.keys())
        
        return {
            "version1": version_id1,
            "version2": version_id2,
            "added": list(v2_problems - v1_problems),
            "removed": list(v1_problems - v2_problems),
            "modified": [
                pid for pid in v1_problems & v2_problems
                if v1_data[pid] != v2_data[pid]
            ],
            "unchanged": list(v1_problems & v2_problems - set([
                pid for pid in v1_problems & v2_problems
                if v1_data[pid] != v2_data[pid]
            ]))
        }
    
    def get_latest_version(self) -> Optional[Dict]:
        """Obtiene la última versión"""
        if self.version_history:
            return self.version_history[-1]
        return None



