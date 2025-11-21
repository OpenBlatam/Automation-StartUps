"""
Versionado de Documentos
========================

Maneja versiones de documentos procesados y cambios.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import hashlib
import json

logger = logging.getLogger(__name__)


@dataclass
class DocumentVersion:
    """Versión de un documento"""
    version: int
    document_id: str
    file_hash: str
    extracted_text: str
    extracted_fields: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: str
    created_by: Optional[str] = None
    changes: Optional[List[str]] = None


class DocumentVersionManager:
    """Gestor de versiones de documentos"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.logger = logging.getLogger(__name__)
    
    def create_version(
        self,
        document_id: str,
        document_data: Dict[str, Any],
        created_by: Optional[str] = None
    ) -> DocumentVersion:
        """Crea una nueva versión del documento"""
        # Obtener versión actual
        current_version = self.get_latest_version(document_id)
        new_version = (current_version.version + 1) if current_version else 1
        
        # Calcular hash
        file_hash = document_data.get("file_hash", "")
        if not file_hash:
            content = json.dumps(document_data, sort_keys=True)
            file_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Detectar cambios si hay versión anterior
        changes = []
        if current_version:
            changes = self._detect_changes(current_version, document_data)
        
        version = DocumentVersion(
            version=new_version,
            document_id=document_id,
            file_hash=file_hash,
            extracted_text=document_data.get("extracted_text", ""),
            extracted_fields=document_data.get("extracted_fields", {}),
            metadata=document_data.get("metadata", {}),
            created_at=datetime.now().isoformat(),
            created_by=created_by,
            changes=changes
        )
        
        # Guardar en BD si está disponible
        if self.db:
            self._save_version_to_db(version)
        
        return version
    
    def get_latest_version(self, document_id: str) -> Optional[DocumentVersion]:
        """Obtiene la última versión"""
        if self.db:
            return self._get_version_from_db(document_id, None)
        return None
    
    def get_version(self, document_id: str, version: int) -> Optional[DocumentVersion]:
        """Obtiene una versión específica"""
        if self.db:
            return self._get_version_from_db(document_id, version)
        return None
    
    def get_all_versions(self, document_id: str) -> List[DocumentVersion]:
        """Obtiene todas las versiones"""
        if self.db:
            return self._get_all_versions_from_db(document_id)
        return []
    
    def compare_versions(
        self,
        document_id: str,
        version1: int,
        version2: int
    ) -> Dict[str, Any]:
        """Compara dos versiones"""
        v1 = self.get_version(document_id, version1)
        v2 = self.get_version(document_id, version2)
        
        if not v1 or not v2:
            return {"error": "Versiones no encontradas"}
        
        changes = self._detect_changes(v1, {
            "extracted_text": v2.extracted_text,
            "extracted_fields": v2.extracted_fields
        })
        
        return {
            "version1": version1,
            "version2": version2,
            "changes": changes,
            "fields_changed": len([c for c in changes if c.startswith("Campo")]),
            "text_changed": any("texto" in c.lower() for c in changes)
        }
    
    def _detect_changes(
        self,
        old_version: DocumentVersion,
        new_data: Dict[str, Any]
    ) -> List[str]:
        """Detecta cambios entre versiones"""
        changes = []
        
        # Cambios en texto
        old_text = old_version.extracted_text
        new_text = new_data.get("extracted_text", "")
        if old_text != new_text:
            text_diff = len(new_text) - len(old_text)
            changes.append(f"Texto cambiado: {text_diff:+d} caracteres")
        
        # Cambios en campos
        old_fields = old_version.extracted_fields
        new_fields = new_data.get("extracted_fields", {})
        
        all_keys = set(old_fields.keys()) | set(new_fields.keys())
        for key in all_keys:
            old_val = old_fields.get(key)
            new_val = new_fields.get(key)
            
            if old_val != new_val:
                changes.append(f"Campo '{key}': '{old_val}' -> '{new_val}'")
        
        return changes
    
    def _save_version_to_db(self, version: DocumentVersion):
        """Guarda versión en BD"""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO document_versions
                (document_id, version, file_hash, extracted_text, extracted_fields,
                 metadata, created_at, created_by, changes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                version.document_id,
                version.version,
                version.file_hash,
                version.extracted_text,
                json.dumps(version.extracted_fields),
                json.dumps(version.metadata),
                version.created_at,
                version.created_by,
                json.dumps(version.changes) if version.changes else None
            ))
            self.db.commit()
        except Exception as e:
            self.logger.error(f"Error guardando versión: {e}")
            self.db.rollback()
    
    def _get_version_from_db(
        self,
        document_id: str,
        version: Optional[int]
    ) -> Optional[DocumentVersion]:
        """Obtiene versión de BD"""
        try:
            cursor = self.db.cursor()
            if version:
                cursor.execute("""
                    SELECT version, file_hash, extracted_text, extracted_fields,
                           metadata, created_at, created_by, changes
                    FROM document_versions
                    WHERE document_id = %s AND version = %s
                    ORDER BY version DESC
                    LIMIT 1
                """, (document_id, version))
            else:
                cursor.execute("""
                    SELECT version, file_hash, extracted_text, extracted_fields,
                           metadata, created_at, created_by, changes
                    FROM document_versions
                    WHERE document_id = %s
                    ORDER BY version DESC
                    LIMIT 1
                """, (document_id,))
            
            row = cursor.fetchone()
            if row:
                return DocumentVersion(
                    version=row[0],
                    document_id=document_id,
                    file_hash=row[1],
                    extracted_text=row[2],
                    extracted_fields=json.loads(row[3]) if row[3] else {},
                    metadata=json.loads(row[4]) if row[4] else {},
                    created_at=row[5],
                    created_by=row[6],
                    changes=json.loads(row[7]) if row[7] else []
                )
        except Exception as e:
            self.logger.error(f"Error obteniendo versión: {e}")
        
        return None
    
    def _get_all_versions_from_db(self, document_id: str) -> List[DocumentVersion]:
        """Obtiene todas las versiones de BD"""
        versions = []
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT version, file_hash, extracted_text, extracted_fields,
                       metadata, created_at, created_by, changes
                FROM document_versions
                WHERE document_id = %s
                ORDER BY version ASC
            """, (document_id,))
            
            for row in cursor.fetchall():
                versions.append(DocumentVersion(
                    version=row[0],
                    document_id=document_id,
                    file_hash=row[1],
                    extracted_text=row[2],
                    extracted_fields=json.loads(row[3]) if row[3] else {},
                    metadata=json.loads(row[4]) if row[4] else {},
                    created_at=row[5],
                    created_by=row[6],
                    changes=json.loads(row[7]) if row[7] else []
                ))
        except Exception as e:
            self.logger.error(f"Error obteniendo versiones: {e}")
        
        return versions

