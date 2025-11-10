"""
Políticas de Retención de Documentos
======================================

Gestiona políticas de retención y eliminación automática de documentos.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RetentionAction(Enum):
    """Acciones de retención"""
    ARCHIVE = "archive"
    DELETE = "delete"
    MOVE_TO_COLD_STORAGE = "move_to_cold_storage"
    COMPRESS = "compress"
    NOTIFY = "notify"


@dataclass
class RetentionPolicy:
    """Política de retención"""
    policy_id: str
    name: str
    description: str
    document_type: Optional[str]  # None = todos los tipos
    retention_days: int
    action: RetentionAction
    action_config: Dict[str, Any] = None
    enabled: bool = True
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class RetentionManager:
    """Gestor de políticas de retención"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.logger = logging.getLogger(__name__)
        self.policies: List[RetentionPolicy] = []
        self._load_policies()
    
    def add_policy(self, policy: RetentionPolicy):
        """Agrega política de retención"""
        self.policies.append(policy)
        
        if self.db:
            self._save_policy_to_db(policy)
    
    def apply_retention_policies(self) -> Dict[str, Any]:
        """Aplica políticas de retención"""
        results = {
            "archived": 0,
            "deleted": 0,
            "moved": 0,
            "compressed": 0,
            "notified": 0,
            "errors": []
        }
        
        for policy in self.policies:
            if not policy.enabled:
                continue
            
            try:
                documents = self._get_documents_for_policy(policy)
                
                for doc in documents:
                    try:
                        if policy.action == RetentionAction.ARCHIVE:
                            self._archive_document(doc)
                            results["archived"] += 1
                        
                        elif policy.action == RetentionAction.DELETE:
                            self._delete_document(doc)
                            results["deleted"] += 1
                        
                        elif policy.action == RetentionAction.MOVE_TO_COLD_STORAGE:
                            self._move_to_cold_storage(doc)
                            results["moved"] += 1
                        
                        elif policy.action == RetentionAction.COMPRESS:
                            self._compress_document(doc)
                            results["compressed"] += 1
                        
                        elif policy.action == RetentionAction.NOTIFY:
                            self._notify_retention(doc, policy)
                            results["notified"] += 1
                    
                    except Exception as e:
                        results["errors"].append({
                            "document_id": doc.get("document_id"),
                            "error": str(e)
                        })
            
            except Exception as e:
                self.logger.error(f"Error aplicando política {policy.policy_id}: {e}")
                results["errors"].append({
                    "policy_id": policy.policy_id,
                    "error": str(e)
                })
        
        return results
    
    def _get_documents_for_policy(self, policy: RetentionPolicy) -> List[Dict[str, Any]]:
        """Obtiene documentos que aplican a la política"""
        if not self.db:
            return []
        
        try:
            cursor = self.db.cursor()
            cutoff_date = datetime.now() - timedelta(days=policy.retention_days)
            
            query = """
                SELECT document_id, original_filename, document_type,
                       processed_at, archive_path
                FROM processed_documents
                WHERE processed_at < %s
            """
            params = [cutoff_date]
            
            if policy.document_type:
                query += " AND document_type = %s"
                params.append(policy.document_type)
            
            query += " AND retention_applied = false"
            
            cursor.execute(query, params)
            
            documents = []
            for row in cursor.fetchall():
                documents.append({
                    "document_id": row[0],
                    "original_filename": row[1],
                    "document_type": row[2],
                    "processed_at": row[3],
                    "archive_path": row[4]
                })
            
            return documents
        except Exception as e:
            self.logger.error(f"Error obteniendo documentos: {e}")
            return []
    
    def _archive_document(self, document: Dict[str, Any]):
        """Archiva documento"""
        # Implementación simplificada
        self.logger.info(f"Archivando documento: {document['document_id']}")
    
    def _delete_document(self, document: Dict[str, Any]):
        """Elimina documento"""
        if not self.db:
            return
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                UPDATE processed_documents
                SET retention_applied = true,
                    deleted_at = CURRENT_TIMESTAMP
                WHERE document_id = %s
            """, (document["document_id"],))
            self.db.commit()
            
            # Eliminar archivo físico si existe
            if document.get("archive_path"):
                import os
                if os.path.exists(document["archive_path"]):
                    os.remove(document["archive_path"])
            
            self.logger.info(f"Documento eliminado: {document['document_id']}")
        except Exception as e:
            self.logger.error(f"Error eliminando documento: {e}")
            self.db.rollback()
    
    def _move_to_cold_storage(self, document: Dict[str, Any]):
        """Mueve a almacenamiento frío"""
        # Implementación simplificada
        self.logger.info(f"Moviendo a cold storage: {document['document_id']}")
    
    def _compress_document(self, document: Dict[str, Any]):
        """Comprime documento"""
        # Implementación simplificada
        self.logger.info(f"Comprimiendo documento: {document['document_id']}")
    
    def _notify_retention(self, document: Dict[str, Any], policy: RetentionPolicy):
        """Notifica sobre retención"""
        # Implementación simplificada
        self.logger.info(f"Notificando retención: {document['document_id']}")
    
    def _load_policies(self):
        """Carga políticas desde BD"""
        if not self.db:
            return
        
        # Implementación simplificada
        pass
    
    def _save_policy_to_db(self, policy: RetentionPolicy):
        """Guarda política en BD"""
        if not self.db:
            return
        
        # Implementación simplificada
        pass

