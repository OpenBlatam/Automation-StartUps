"""
Sistema de Auditoría Completo
Registra todos los cambios y acciones para cumplimiento y seguridad
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import json

from .storage import TimeTrackingStorage

logger = logging.getLogger(__name__)


class AuditLogger:
    """Sistema de auditoría para time tracking"""
    
    def __init__(self, storage: TimeTrackingStorage):
        self.storage = storage
        self._ensure_audit_table()
    
    def _ensure_audit_table(self) -> None:
        """Asegura que la tabla de auditoría exista"""
        sql = """
            CREATE TABLE IF NOT EXISTS time_tracking_audit_log (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(64) NOT NULL,
                entity_type VARCHAR(64) NOT NULL,
                entity_id VARCHAR(128),
                employee_id VARCHAR(128),
                action VARCHAR(64) NOT NULL,
                old_value JSONB,
                new_value JSONB,
                changed_by VARCHAR(128),
                changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                ip_address VARCHAR(45),
                user_agent TEXT,
                metadata JSONB
            );
            
            CREATE INDEX IF NOT EXISTS idx_time_tracking_audit_log_employee_id 
                ON time_tracking_audit_log(employee_id);
            CREATE INDEX IF NOT EXISTS idx_time_tracking_audit_log_event_type 
                ON time_tracking_audit_log(event_type);
            CREATE INDEX IF NOT EXISTS idx_time_tracking_audit_log_changed_at 
                ON time_tracking_audit_log(changed_at);
        """
        
        try:
            self.storage.hook.run(sql)
        except Exception as e:
            logger.warning(f"Audit table may already exist: {e}")
    
    def log_event(
        self,
        event_type: str,
        entity_type: str,
        action: str,
        entity_id: Optional[str] = None,
        employee_id: Optional[str] = None,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        changed_by: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Registra un evento de auditoría"""
        sql = """
            INSERT INTO time_tracking_audit_log (
                event_type, entity_type, entity_id, employee_id,
                action, old_value, new_value, changed_by,
                ip_address, user_agent, metadata
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id
        """
        
        result = self.storage.hook.get_first(
            sql,
            parameters=(
                event_type,
                entity_type,
                entity_id,
                employee_id,
                action,
                json.dumps(old_value) if old_value else None,
                json.dumps(new_value) if new_value else None,
                changed_by,
                ip_address,
                user_agent,
                json.dumps(metadata) if metadata else None
            )
        )
        
        return result[0] if result else 0
    
    def log_clock_event(
        self,
        employee_id: str,
        event_type: str,
        clock_event_id: int,
        changed_by: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> int:
        """Registra evento de clock in/out"""
        return self.log_event(
            event_type="clock_event",
            entity_type="clock_event",
            action=event_type,
            entity_id=str(clock_event_id),
            employee_id=employee_id,
            changed_by=changed_by or employee_id,
            ip_address=ip_address
        )
    
    def log_session_change(
        self,
        session_id: int,
        employee_id: str,
        action: str,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        changed_by: Optional[str] = None
    ) -> int:
        """Registra cambio en sesión de trabajo"""
        return self.log_event(
            event_type="session_change",
            entity_type="work_session",
            action=action,
            entity_id=str(session_id),
            employee_id=employee_id,
            old_value=old_value,
            new_value=new_value,
            changed_by=changed_by
        )
    
    def log_vacation_change(
        self,
        vacation_id: int,
        employee_id: str,
        action: str,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        changed_by: Optional[str] = None
    ) -> int:
        """Registra cambio en solicitud de vacaciones"""
        return self.log_event(
            event_type="vacation_change",
            entity_type="vacation",
            action=action,
            entity_id=str(vacation_id),
            employee_id=employee_id,
            old_value=old_value,
            new_value=new_value,
            changed_by=changed_by
        )
    
    def log_dispute_change(
        self,
        dispute_id: int,
        employee_id: str,
        action: str,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        changed_by: Optional[str] = None
    ) -> int:
        """Registra cambio en disputa"""
        return self.log_event(
            event_type="dispute_change",
            entity_type="dispute",
            action=action,
            entity_id=str(dispute_id),
            employee_id=employee_id,
            old_value=old_value,
            new_value=new_value,
            changed_by=changed_by
        )
    
    def get_audit_trail(
        self,
        employee_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Obtiene trail de auditoría"""
        conditions = []
        params = []
        
        if employee_id:
            conditions.append("employee_id = %s")
            params.append(employee_id)
        
        if entity_type:
            conditions.append("entity_type = %s")
            params.append(entity_type)
        
        if start_date:
            conditions.append("changed_at >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("changed_at <= %s")
            params.append(end_date)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.append(limit)
        
        sql = f"""
            SELECT 
                id, event_type, entity_type, entity_id, employee_id,
                action, old_value, new_value, changed_by,
                changed_at, ip_address
            FROM time_tracking_audit_log
            WHERE {where_clause}
            ORDER BY changed_at DESC
            LIMIT %s
        """
        
        results = self.storage.hook.get_records(sql, parameters=tuple(params))
        
        audit_entries = []
        for row in results:
            audit_entries.append({
                "id": row[0],
                "event_type": row[1],
                "entity_type": row[2],
                "entity_id": row[3],
                "employee_id": row[4],
                "action": row[5],
                "old_value": json.loads(row[6]) if row[6] else None,
                "new_value": json.loads(row[7]) if row[7] else None,
                "changed_by": row[8],
                "changed_at": row[9].isoformat() if row[9] else None,
                "ip_address": row[10]
            })
        
        return audit_entries
    
    def generate_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Genera reporte de cumplimiento"""
        sql = """
            SELECT 
                event_type,
                COUNT(*) as event_count,
                COUNT(DISTINCT employee_id) as employees_affected,
                COUNT(DISTINCT changed_by) as users_who_changed
            FROM time_tracking_audit_log
            WHERE changed_at BETWEEN %s AND %s
            GROUP BY event_type
            ORDER BY event_count DESC
        """
        
        results = self.storage.hook.get_records(
            sql,
            parameters=(start_date, end_date)
        )
        
        report = {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "events_by_type": []
        }
        
        for row in results:
            event_type, count, employees, users = row
            report["events_by_type"].append({
                "event_type": event_type,
                "event_count": count,
                "employees_affected": employees,
                "users_who_changed": users
            })
        
        return report

