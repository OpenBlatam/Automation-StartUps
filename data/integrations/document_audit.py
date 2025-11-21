"""
Sistema de Auditoría Completo
==============================

Registra todas las acciones y cambios en documentos para auditoría.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class AuditAction(Enum):
    """Tipos de acciones auditadas"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    PROCESS = "process"
    CLASSIFY = "classify"
    VALIDATE = "validate"
    ARCHIVE = "archive"
    EXPORT = "export"
    DOWNLOAD = "download"
    UPLOAD = "upload"


@dataclass
class AuditLog:
    """Entrada de auditoría"""
    id: Optional[int]
    document_id: str
    action: AuditAction
    user_id: Optional[str]
    user_email: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: str
    details: Dict[str, Any]
    result: str  # success, failure, error
    error_message: Optional[str] = None


class AuditLogger:
    """Logger de auditoría"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.logger = logging.getLogger(__name__)
    
    def log_action(
        self,
        document_id: str,
        action: AuditAction,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        result: str = "success",
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Registra una acción de auditoría"""
        audit_log = AuditLog(
            id=None,
            document_id=document_id,
            action=action,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.now().isoformat(),
            details=details or {},
            result=result,
            error_message=error_message
        )
        
        # Guardar en BD
        if self.db:
            self._save_audit_log(audit_log)
        
        # Log local
        self.logger.info(
            f"Audit: {action.value} on {document_id} by {user_email or user_id or 'system'}"
        )
        
        return audit_log
    
    def get_audit_trail(
        self,
        document_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AuditLog]:
        """Obtiene trail de auditoría de un documento"""
        if not self.db:
            return []
        
        try:
            cursor = self.db.cursor()
            query = """
                SELECT id, document_id, action, user_id, user_email, ip_address,
                       user_agent, timestamp, details, result, error_message
                FROM audit_logs
                WHERE document_id = %s
            """
            params = [document_id]
            
            if start_date:
                query += " AND timestamp >= %s"
                params.append(start_date)
            
            if end_date:
                query += " AND timestamp <= %s"
                params.append(end_date)
            
            query += " ORDER BY timestamp DESC"
            
            cursor.execute(query, params)
            
            logs = []
            for row in cursor.fetchall():
                logs.append(AuditLog(
                    id=row[0],
                    document_id=row[1],
                    action=AuditAction(row[2]),
                    user_id=row[3],
                    user_email=row[4],
                    ip_address=row[5],
                    user_agent=row[6],
                    timestamp=row[7],
                    details=json.loads(row[8]) if row[8] else {},
                    result=row[9],
                    error_message=row[10]
                ))
            
            return logs
        except Exception as e:
            self.logger.error(f"Error obteniendo audit trail: {e}")
            return []
    
    def get_user_activity(
        self,
        user_id: str,
        days: int = 30
    ) -> List[AuditLog]:
        """Obtiene actividad de un usuario"""
        if not self.db:
            return []
        
        try:
            cursor = self.db.cursor()
            cutoff = datetime.now() - timedelta(days=days)
            
            cursor.execute("""
                SELECT id, document_id, action, user_id, user_email, ip_address,
                       user_agent, timestamp, details, result, error_message
                FROM audit_logs
                WHERE (user_id = %s OR user_email = %s)
                  AND timestamp >= %s
                ORDER BY timestamp DESC
            """, (user_id, user_id, cutoff))
            
            logs = []
            for row in cursor.fetchall():
                logs.append(AuditLog(
                    id=row[0],
                    document_id=row[1],
                    action=AuditAction(row[2]),
                    user_id=row[3],
                    user_email=row[4],
                    ip_address=row[5],
                    user_agent=row[6],
                    timestamp=row[7],
                    details=json.loads(row[8]) if row[8] else {},
                    result=row[9],
                    error_message=row[10]
                ))
            
            return logs
        except Exception as e:
            self.logger.error(f"Error obteniendo actividad de usuario: {e}")
            return []
    
    def _save_audit_log(self, audit_log: AuditLog):
        """Guarda log en BD"""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO audit_logs
                (document_id, action, user_id, user_email, ip_address, user_agent,
                 timestamp, details, result, error_message)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                audit_log.document_id,
                audit_log.action.value,
                audit_log.user_id,
                audit_log.user_email,
                audit_log.ip_address,
                audit_log.user_agent,
                audit_log.timestamp,
                json.dumps(audit_log.details),
                audit_log.result,
                audit_log.error_message
            ))
            self.db.commit()
        except Exception as e:
            self.logger.error(f"Error guardando audit log: {e}")
            self.db.rollback()
    
    def generate_audit_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Genera reporte de auditoría"""
        if not self.db:
            return {}
        
        try:
            cursor = self.db.cursor()
            
            # Estadísticas por acción
            cursor.execute("""
                SELECT action, COUNT(*) as count, 
                       COUNT(*) FILTER (WHERE result = 'success') as success_count
                FROM audit_logs
                WHERE timestamp BETWEEN %s AND %s
                GROUP BY action
            """, (start_date, end_date))
            
            by_action = {
                row[0]: {"total": row[1], "success": row[2]}
                for row in cursor.fetchall()
            }
            
            # Estadísticas por usuario
            cursor.execute("""
                SELECT COALESCE(user_email, user_id, 'system') as user,
                       COUNT(*) as count
                FROM audit_logs
                WHERE timestamp BETWEEN %s AND %s
                GROUP BY COALESCE(user_email, user_id, 'system')
                ORDER BY count DESC
                LIMIT 10
            """, (start_date, end_date))
            
            by_user = {
                row[0]: row[1]
                for row in cursor.fetchall()
            }
            
            # Total de acciones
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM audit_logs
                WHERE timestamp BETWEEN %s AND %s
            """, (start_date, end_date))
            
            total = cursor.fetchone()[0]
            
            return {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "total_actions": total,
                "by_action": by_action,
                "top_users": by_user
            }
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return {}

