"""
Sistema de Auditoría para Nómina
Registra todos los cambios y operaciones para trazabilidad
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
import json

from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Tipos de eventos de auditoría"""
    PAYROLL_CALCULATED = "payroll_calculated"
    PAYROLL_APPROVED = "payroll_approved"
    PAYROLL_PAID = "payroll_paid"
    EXPENSE_APPROVED = "expense_approved"
    EXPENSE_REJECTED = "expense_rejected"
    TIME_ENTRY_CREATED = "time_entry_created"
    TIME_ENTRY_MODIFIED = "time_entry_modified"
    EMPLOYEE_UPDATED = "employee_updated"
    DEDUCTION_RULE_CHANGED = "deduction_rule_changed"
    CONFIGURATION_CHANGED = "configuration_changed"


class PayrollAuditor:
    """Sistema de auditoría para nómina"""
    
    def __init__(self, postgres_conn_id: str = "postgres_default"):
        """
        Args:
            postgres_conn_id: ID de conexión de PostgreSQL
        """
        self.postgres_conn_id = postgres_conn_id
        self._hook: Optional[PostgresHook] = None
    
    @property
    def hook(self) -> PostgresHook:
        """Obtiene el hook de PostgreSQL"""
        if self._hook is None:
            self._hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        return self._hook
    
    def ensure_audit_table(self) -> bool:
        """Crea la tabla de auditoría si no existe"""
        sql = """
            CREATE TABLE IF NOT EXISTS payroll_audit_log (
                id BIGSERIAL PRIMARY KEY,
                event_type VARCHAR(64) NOT NULL,
                entity_type VARCHAR(64) NOT NULL,
                entity_id VARCHAR(128),
                employee_id VARCHAR(128),
                user_id VARCHAR(128),
                action VARCHAR(64) NOT NULL,
                old_values JSONB,
                new_values JSONB,
                metadata JSONB,
                ip_address VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_payroll_audit_event_type 
                ON payroll_audit_log(event_type);
            CREATE INDEX IF NOT EXISTS idx_payroll_audit_entity 
                ON payroll_audit_log(entity_type, entity_id);
            CREATE INDEX IF NOT EXISTS idx_payroll_audit_employee 
                ON payroll_audit_log(employee_id);
            CREATE INDEX IF NOT EXISTS idx_payroll_audit_created_at 
                ON payroll_audit_log(created_at);
        """
        
        try:
            self.hook.run(sql)
            return True
        except Exception as e:
            logger.error(f"Error creating audit table: {e}")
            return False
    
    def log_event(
        self,
        event_type: AuditEventType,
        entity_type: str,
        entity_id: Optional[str] = None,
        employee_id: Optional[str] = None,
        user_id: Optional[str] = None,
        action: str = "unknown",
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[int]:
        """Registra un evento de auditoría"""
        sql = """
            INSERT INTO payroll_audit_log (
                event_type, entity_type, entity_id, employee_id,
                user_id, action, old_values, new_values, metadata,
                ip_address, user_agent
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id
        """
        
        try:
            result = self.hook.get_first(
                sql,
                parameters=(
                    event_type.value,
                    entity_type,
                    entity_id,
                    employee_id,
                    user_id,
                    action,
                    json.dumps(old_values) if old_values else None,
                    json.dumps(new_values) if new_values else None,
                    json.dumps(metadata) if metadata else None,
                    ip_address,
                    user_agent
                )
            )
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            return None
    
    def get_audit_trail(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        employee_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Obtiene el historial de auditoría"""
        conditions = []
        params = []
        
        if entity_type:
            conditions.append("entity_type = %s")
            params.append(entity_type)
        
        if entity_id:
            conditions.append("entity_id = %s")
            params.append(entity_id)
        
        if employee_id:
            conditions.append("employee_id = %s")
            params.append(employee_id)
        
        if event_type:
            conditions.append("event_type = %s")
            params.append(event_type.value)
        
        if start_date:
            conditions.append("created_at >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("created_at <= %s")
            params.append(end_date)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        sql = f"""
            SELECT 
                id, event_type, entity_type, entity_id, employee_id,
                user_id, action, old_values, new_values, metadata,
                ip_address, user_agent, created_at
            FROM payroll_audit_log
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT %s
        """
        
        params.append(limit)
        
        results = self.hook.get_records(sql, parameters=tuple(params))
        
        events = []
        for row in results:
            events.append({
                "id": row[0],
                "event_type": row[1],
                "entity_type": row[2],
                "entity_id": row[3],
                "employee_id": row[4],
                "user_id": row[5],
                "action": row[6],
                "old_values": row[7] if isinstance(row[7], dict) else json.loads(row[7]) if row[7] else None,
                "new_values": row[8] if isinstance(row[8], dict) else json.loads(row[8]) if row[8] else None,
                "metadata": row[9] if isinstance(row[9], dict) else json.loads(row[9]) if row[9] else None,
                "ip_address": row[10],
                "user_agent": row[11],
                "created_at": row[12]
            })
        
        return events

