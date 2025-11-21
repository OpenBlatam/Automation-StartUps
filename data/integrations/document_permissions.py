"""
Sistema de Permisos y Acceso
============================

Gestiona permisos de acceso a documentos.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PermissionLevel(Enum):
    """Niveles de permiso"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


@dataclass
class DocumentPermission:
    """Permiso de documento"""
    permission_id: str
    document_id: str
    user_id: str
    user_email: str
    permission_level: PermissionLevel
    granted_by: str
    granted_at: str
    expires_at: Optional[str] = None
    revoked: bool = False
    revoked_at: Optional[str] = None


class PermissionManager:
    """Gestor de permisos"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.logger = logging.getLogger(__name__)
    
    def grant_permission(
        self,
        document_id: str,
        user_id: str,
        user_email: str,
        permission_level: PermissionLevel,
        granted_by: str,
        expires_hours: Optional[int] = None
    ) -> DocumentPermission:
        """Otorga permiso a un usuario"""
        permission_id = f"PERM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        expires_at = None
        if expires_hours:
            expires_at = (datetime.now() + timedelta(hours=expires_hours)).isoformat()
        
        permission = DocumentPermission(
            permission_id=permission_id,
            document_id=document_id,
            user_id=user_id,
            user_email=user_email,
            permission_level=permission_level,
            granted_by=granted_by,
            granted_at=datetime.now().isoformat(),
            expires_at=expires_at
        )
        
        if self.db:
            self._save_permission_to_db(permission)
        
        return permission
    
    def check_permission(
        self,
        document_id: str,
        user_id: str,
        required_level: PermissionLevel
    ) -> bool:
        """Verifica si un usuario tiene permiso"""
        if not self.db:
            return True  # Sin BD, permitir todo
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT permission_level, expires_at, revoked
                FROM document_permissions
                WHERE document_id = %s
                  AND user_id = %s
                  AND revoked = false
                  AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                ORDER BY 
                    CASE permission_level
                        WHEN 'admin' THEN 4
                        WHEN 'delete' THEN 3
                        WHEN 'write' THEN 2
                        WHEN 'read' THEN 1
                    END DESC
                LIMIT 1
            """, (document_id, user_id))
            
            row = cursor.fetchone()
            if not row:
                return False
            
            user_level = PermissionLevel(row[0])
            
            # Verificar nivel requerido
            level_hierarchy = {
                PermissionLevel.READ: 1,
                PermissionLevel.WRITE: 2,
                PermissionLevel.DELETE: 3,
                PermissionLevel.ADMIN: 4
            }
            
            return level_hierarchy.get(user_level, 0) >= level_hierarchy.get(required_level, 0)
            
        except Exception as e:
            self.logger.error(f"Error verificando permiso: {e}")
            return False
    
    def revoke_permission(self, permission_id: str, revoked_by: str) -> bool:
        """Revoca un permiso"""
        if not self.db:
            return False
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                UPDATE document_permissions
                SET revoked = true,
                    revoked_at = CURRENT_TIMESTAMP
                WHERE permission_id = %s
            """, (permission_id,))
            self.db.commit()
            return True
        except Exception as e:
            self.logger.error(f"Error revocando permiso: {e}")
            self.db.rollback()
            return False
    
    def get_user_permissions(self, user_id: str) -> List[DocumentPermission]:
        """Obtiene todos los permisos de un usuario"""
        if not self.db:
            return []
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT permission_id, document_id, user_id, user_email,
                       permission_level, granted_by, granted_at, expires_at,
                       revoked, revoked_at
                FROM document_permissions
                WHERE user_id = %s
                  AND revoked = false
                  AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
            """, (user_id,))
            
            permissions = []
            for row in cursor.fetchall():
                permissions.append(DocumentPermission(
                    permission_id=row[0],
                    document_id=row[1],
                    user_id=row[2],
                    user_email=row[3],
                    permission_level=PermissionLevel(row[4]),
                    granted_by=row[5],
                    granted_at=row[6],
                    expires_at=row[7],
                    revoked=row[8],
                    revoked_at=row[9]
                ))
            
            return permissions
        except Exception as e:
            self.logger.error(f"Error obteniendo permisos: {e}")
            return []
    
    def _save_permission_to_db(self, permission: DocumentPermission):
        """Guarda permiso en BD"""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO document_permissions
                (permission_id, document_id, user_id, user_email,
                 permission_level, granted_by, granted_at, expires_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                permission.permission_id,
                permission.document_id,
                permission.user_id,
                permission.user_email,
                permission.permission_level.value,
                permission.granted_by,
                permission.granted_at,
                permission.expires_at
            ))
            self.db.commit()
        except Exception as e:
            self.logger.error(f"Error guardando permiso: {e}")
            self.db.rollback()

