"""
Sistema de Recovery para Nómina
Recuperación de errores y rollback de operaciones
"""

import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


class RecoveryAction(str, Enum):
    """Acciones de recuperación"""
    ROLLBACK = "rollback"
    RETRY = "retry"
    SKIP = "skip"
    MANUAL_INTERVENTION = "manual_intervention"


@dataclass
class RecoveryPlan:
    """Plan de recuperación"""
    action: RecoveryAction
    description: str
    steps: List[str]
    estimated_time_minutes: int
    metadata: Optional[Dict[str, Any]] = None


class PayrollRecovery:
    """Sistema de recuperación para nómina"""
    
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
    
    def rollback_pay_period(
        self,
        pay_period_id: int
    ) -> bool:
        """Rollback de un período de pago"""
        try:
            # Verificar que el período existe
            check_sql = """
                SELECT id, employee_id, status
                FROM payroll_pay_periods
                WHERE id = %s
            """
            
            result = self.hook.get_first(check_sql, parameters=(pay_period_id,))
            
            if not result:
                logger.error(f"Pay period {pay_period_id} not found")
                return False
            
            status = result[2]
            
            # Solo rollback si no está pagado
            if status == "paid":
                logger.warning(
                    f"Cannot rollback pay period {pay_period_id} - already paid"
                )
                return False
            
            # Cambiar estado a cancelled
            update_sql = """
                UPDATE payroll_pay_periods
                SET status = 'cancelled',
                    updated_at = NOW()
                WHERE id = %s
            """
            
            self.hook.run(update_sql, parameters=(pay_period_id,))
            
            logger.info(f"Pay period {pay_period_id} rolled back successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error rolling back pay period {pay_period_id}: {e}")
            return False
    
    def recover_failed_calculation(
        self,
        employee_id: str,
        period_start: date,
        period_end: date
    ) -> RecoveryPlan:
        """Genera plan de recuperación para cálculo fallido"""
        # Verificar qué falló
        sql = """
            SELECT 
                COUNT(*) as time_entries,
                SUM(CASE WHEN clock_in >= clock_out THEN 1 ELSE 0 END) as invalid_entries
            FROM payroll_time_entries
            WHERE employee_id = %s
                AND work_date >= %s
                AND work_date <= %s
        """
        
        result = self.hook.get_first(
            sql,
            parameters=(employee_id, period_start, period_end)
        )
        
        time_entries_count = result[0] if result else 0
        invalid_entries = result[1] if result else 0
        
        if time_entries_count == 0:
            return RecoveryPlan(
                action=RecoveryAction.MANUAL_INTERVENTION,
                description="No time entries found for period",
                steps=[
                    "1. Verify employee was active during period",
                    "2. Check if time entries need to be imported",
                    "3. Manually create time entries if needed"
                ],
                estimated_time_minutes=30
            )
        
        if invalid_entries > 0:
            return RecoveryPlan(
                action=RecoveryAction.MANUAL_INTERVENTION,
                description=f"{invalid_entries} invalid time entries found",
                steps=[
                    "1. Review invalid time entries",
                    "2. Correct clock_in/clock_out times",
                    "3. Retry calculation"
                ],
                estimated_time_minutes=15
            )
        
        # Si hay entradas válidas, puede ser retry
        return RecoveryPlan(
            action=RecoveryAction.RETRY,
            description="Time entries appear valid, retry calculation",
            steps=[
                "1. Verify employee data is correct",
                "2. Check deduction rules",
                "3. Retry calculation"
            ],
            estimated_time_minutes=5
        )
    
    def recover_failed_ocr(
        self,
        receipt_id: int
    ) -> RecoveryPlan:
        """Genera plan de recuperación para OCR fallido"""
        # Intentar con otro proveedor
        return RecoveryPlan(
            action=RecoveryAction.RETRY,
            description="Retry OCR with different provider",
            steps=[
                "1. Try OCR with Tesseract (if not tried)",
                "2. Try OCR with AWS Textract (if not tried)",
                "3. Try OCR with Google Vision (if not tried)",
                "4. If all fail, mark for manual review"
            ],
            estimated_time_minutes=10
        )
    
    def get_failed_operations(
        self,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Obtiene operaciones fallidas recientes"""
        sql = """
            SELECT 
                'pay_period' as operation_type,
                id,
                employee_id,
                status,
                created_at,
                updated_at
            FROM payroll_pay_periods
            WHERE status = 'failed'
                AND created_at >= NOW() - INTERVAL '%s hours'
            
            UNION ALL
            
            SELECT 
                'expense' as operation_type,
                id,
                employee_id,
                ocr_status as status,
                created_at,
                updated_at
            FROM payroll_expense_receipts
            WHERE ocr_status = 'failed'
                AND created_at >= NOW() - INTERVAL '%s hours'
            
            ORDER BY created_at DESC
        """
        
        results = self.hook.get_records(sql, parameters=(hours, hours))
        
        failed_operations = []
        for row in results:
            failed_operations.append({
                "operation_type": row[0],
                "id": row[1],
                "employee_id": row[2],
                "status": row[3],
                "created_at": row[4],
                "updated_at": row[5]
            })
        
        return failed_operations
    
    def create_recovery_summary(self) -> Dict[str, Any]:
        """Crea resumen de operaciones que necesitan recuperación"""
        failed_operations = self.get_failed_operations(hours=24)
        
        by_type = {}
        for op in failed_operations:
            op_type = op["operation_type"]
            if op_type not in by_type:
                by_type[op_type] = 0
            by_type[op_type] += 1
        
        return {
            "total_failed": len(failed_operations),
            "by_type": by_type,
            "operations": failed_operations,
            "needs_attention": len(failed_operations) > 0
        }

