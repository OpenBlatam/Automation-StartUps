"""
Sistema de Aprobaciones para Nómina
Maneja workflows de aprobación para períodos de pago y gastos
"""

import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, Optional, List
from enum import Enum
import json

from airflow.providers.postgres.hooks.postgres import PostgresHook

from .exceptions import PayrollError, ValidationError

logger = logging.getLogger(__name__)


class ApprovalStatus(str, Enum):
    """Estados de aprobación"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"
    CANCELLED = "cancelled"


class ApprovalLevel(str, Enum):
    """Niveles de aprobación"""
    AUTO = "auto"
    MANAGER = "manager"
    HR = "hr"
    FINANCE = "finance"
    EXECUTIVE = "executive"


class PayrollApprovalSystem:
    """Sistema de aprobaciones para nómina"""
    
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
    
    def ensure_approval_tables(self) -> bool:
        """Crea las tablas de aprobación si no existen"""
        sql = """
            CREATE TABLE IF NOT EXISTS payroll_approvals (
                id SERIAL PRIMARY KEY,
                entity_type VARCHAR(64) NOT NULL, -- 'pay_period', 'expense', 'time_entry'
                entity_id INT NOT NULL,
                employee_id VARCHAR(128) NOT NULL,
                approval_level VARCHAR(32) NOT NULL,
                status VARCHAR(32) NOT NULL DEFAULT 'pending',
                requested_by VARCHAR(128),
                requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                approved_by VARCHAR(128),
                approved_at TIMESTAMPTZ,
                rejected_by VARCHAR(128),
                rejected_at TIMESTAMPTZ,
                rejection_reason TEXT,
                metadata JSONB,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ
            );
            
            CREATE INDEX IF NOT EXISTS idx_payroll_approvals_entity 
                ON payroll_approvals(entity_type, entity_id);
            CREATE INDEX IF NOT EXISTS idx_payroll_approvals_employee 
                ON payroll_approvals(employee_id);
            CREATE INDEX IF NOT EXISTS idx_payroll_approvals_status 
                ON payroll_approvals(status) WHERE status = 'pending';
            CREATE INDEX IF NOT EXISTS idx_payroll_approvals_level 
                ON payroll_approvals(approval_level);
        """
        
        try:
            self.hook.run(sql)
            return True
        except Exception as e:
            logger.error(f"Error creating approval tables: {e}")
            return False
    
    def request_approval(
        self,
        entity_type: str,
        entity_id: int,
        employee_id: str,
        approval_level: ApprovalLevel,
        requested_by: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Solicita una aprobación"""
        sql = """
            INSERT INTO payroll_approvals (
                entity_type, entity_id, employee_id,
                approval_level, status, requested_by, metadata
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id
        """
        
        result = self.hook.get_first(
            sql,
            parameters=(
                entity_type,
                entity_id,
                employee_id,
                approval_level.value,
                ApprovalStatus.PENDING.value,
                requested_by,
                json.dumps(metadata) if metadata else None
            )
        )
        
        return result[0] if result else 0
    
    def approve(
        self,
        approval_id: int,
        approved_by: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Aprueba una solicitud"""
        sql = """
            UPDATE payroll_approvals
            SET 
                status = 'approved',
                approved_by = %s,
                approved_at = NOW(),
                updated_at = NOW(),
                metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
            WHERE id = %s AND status = 'pending'
            RETURNING id
        """
        
        try:
            result = self.hook.get_first(
                sql,
                parameters=(
                    approved_by,
                    json.dumps(metadata or {}),
                    approval_id
                )
            )
            return result is not None
        except Exception as e:
            logger.error(f"Error approving {approval_id}: {e}")
            return False
    
    def reject(
        self,
        approval_id: int,
        rejected_by: str,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Rechaza una solicitud"""
        sql = """
            UPDATE payroll_approvals
            SET 
                status = 'rejected',
                rejected_by = %s,
                rejected_at = NOW(),
                rejection_reason = %s,
                updated_at = NOW(),
                metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
            WHERE id = %s AND status = 'pending'
            RETURNING id
        """
        
        try:
            result = self.hook.get_first(
                sql,
                parameters=(
                    rejected_by,
                    reason,
                    json.dumps(metadata or {}),
                    approval_id
                )
            )
            return result is not None
        except Exception as e:
            logger.error(f"Error rejecting {approval_id}: {e}")
            return False
    
    def get_pending_approvals(
        self,
        approval_level: Optional[ApprovalLevel] = None,
        employee_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Obtiene aprobaciones pendientes"""
        conditions = ["status = 'pending'"]
        params = []
        
        if approval_level:
            conditions.append("approval_level = %s")
            params.append(approval_level.value)
        
        if employee_id:
            conditions.append("employee_id = %s")
            params.append(employee_id)
        
        where_clause = " AND ".join(conditions)
        
        sql = f"""
            SELECT 
                id, entity_type, entity_id, employee_id,
                approval_level, requested_by, requested_at, metadata
            FROM payroll_approvals
            WHERE {where_clause}
            ORDER BY requested_at ASC
            LIMIT %s
        """
        
        params.append(limit)
        results = self.hook.get_records(sql, parameters=tuple(params))
        
        approvals = []
        for row in results:
            approvals.append({
                "id": row[0],
                "entity_type": row[1],
                "entity_id": row[2],
                "employee_id": row[3],
                "approval_level": row[4],
                "requested_by": row[5],
                "requested_at": row[6],
                "metadata": row[7] if isinstance(row[7], dict) else json.loads(row[7]) if row[7] else {}
            })
        
        return approvals
    
    def auto_approve_if_eligible(
        self,
        entity_type: str,
        entity_id: int,
        employee_id: str,
        amount: Decimal,
        auto_approve_threshold: Decimal = Decimal("100.00")
    ) -> bool:
        """Auto-aprueba si cumple con los criterios"""
        if amount <= auto_approve_threshold:
            # Auto-aprobar directamente
            sql = """
                UPDATE payroll_approvals
                SET 
                    status = 'approved',
                    approved_by = 'system_auto',
                    approved_at = NOW(),
                    updated_at = NOW()
                WHERE entity_type = %s AND entity_id = %s
                    AND employee_id = %s AND status = 'pending'
                RETURNING id
            """
            
            result = self.hook.get_first(
                sql,
                parameters=(entity_type, entity_id, employee_id)
            )
            
            return result is not None
        
        return False
    
    def get_approval_history(
        self,
        entity_type: str,
        entity_id: int
    ) -> List[Dict[str, Any]]:
        """Obtiene el historial de aprobaciones para una entidad"""
        sql = """
            SELECT 
                id, employee_id, approval_level, status,
                requested_by, requested_at,
                approved_by, approved_at,
                rejected_by, rejected_at, rejection_reason,
                metadata
            FROM payroll_approvals
            WHERE entity_type = %s AND entity_id = %s
            ORDER BY requested_at DESC
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(entity_type, entity_id)
        )
        
        history = []
        for row in results:
            history.append({
                "id": row[0],
                "employee_id": row[1],
                "approval_level": row[2],
                "status": row[3],
                "requested_by": row[4],
                "requested_at": row[5],
                "approved_by": row[6],
                "approved_at": row[7],
                "rejected_by": row[8],
                "rejected_at": row[9],
                "rejection_reason": row[10],
                "metadata": row[11] if isinstance(row[11], dict) else json.loads(row[11]) if row[11] else {}
            })
        
        return history

