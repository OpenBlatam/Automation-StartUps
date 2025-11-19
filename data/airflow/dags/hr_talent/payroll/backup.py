"""
Sistema de Backup y Recuperación para Nómina
Backups incrementales y recuperación de datos
"""

import logging
from datetime import datetime, date
from typing import Dict, Any, Optional, List
import json

from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


class PayrollBackup:
    """Sistema de backup para nómina"""
    
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
    
    def create_backup_metadata(
        self,
        backup_type: str = "full",
        description: Optional[str] = None
    ) -> int:
        """Crea registro de metadata de backup"""
        sql = """
            CREATE TABLE IF NOT EXISTS payroll_backup_metadata (
                id SERIAL PRIMARY KEY,
                backup_type VARCHAR(32) NOT NULL,
                description TEXT,
                status VARCHAR(32) NOT NULL DEFAULT 'in_progress',
                started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                completed_at TIMESTAMPTZ,
                record_count INT,
                size_bytes BIGINT,
                metadata JSONB,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_backup_status 
                ON payroll_backup_metadata(status);
            CREATE INDEX IF NOT EXISTS idx_backup_started_at 
                ON payroll_backup_metadata(started_at);
        """
        
        self.hook.run(sql)
        
        insert_sql = """
            INSERT INTO payroll_backup_metadata (
                backup_type, description, status
            ) VALUES (%s, %s, %s)
            RETURNING id
        """
        
        result = self.hook.get_first(
            insert_sql,
            parameters=(backup_type, description, "in_progress")
        )
        
        return result[0] if result else 0
    
    def backup_pay_periods(
        self,
        period_start: date,
        period_end: date,
        backup_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Backup de períodos de pago"""
        if backup_id is None:
            backup_id = self.create_backup_metadata(
                backup_type="incremental",
                description=f"Backup periods {period_start} to {period_end}"
            )
        
        # Exportar datos
        sql = """
            SELECT 
                id, employee_id, period_start, period_end, pay_date,
                gross_pay, total_hours, regular_hours, overtime_hours,
                total_deductions, total_expenses, net_pay, status
            FROM payroll_pay_periods
            WHERE period_start >= %s AND period_end <= %s
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(period_start, period_end)
        )
        
        records = []
        for row in results:
            records.append({
                "id": row[0],
                "employee_id": row[1],
                "period_start": str(row[2]),
                "period_end": str(row[3]),
                "pay_date": str(row[4]),
                "gross_pay": float(row[5]) if row[5] else 0.0,
                "total_hours": float(row[6]) if row[6] else 0.0,
                "regular_hours": float(row[7]) if row[7] else 0.0,
                "overtime_hours": float(row[8]) if row[8] else 0.0,
                "total_deductions": float(row[9]) if row[9] else 0.0,
                "total_expenses": float(row[10]) if row[10] else 0.0,
                "net_pay": float(row[11]) if row[11] else 0.0,
                "status": row[12]
            })
        
        # Actualizar metadata
        update_sql = """
            UPDATE payroll_backup_metadata
            SET 
                status = 'completed',
                completed_at = NOW(),
                record_count = %s,
                metadata = %s
            WHERE id = %s
        """
        
        metadata = {
            "period_start": str(period_start),
            "period_end": str(period_end),
            "record_count": len(records)
        }
        
        self.hook.run(
            update_sql,
            parameters=(len(records), json.dumps(metadata), backup_id)
        )
        
        return {
            "backup_id": backup_id,
            "records": records,
            "count": len(records),
            "period_start": str(period_start),
            "period_end": str(period_end)
        }
    
    def get_backup_history(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Obtiene historial de backups"""
        sql = """
            SELECT 
                id, backup_type, description, status,
                started_at, completed_at, record_count,
                size_bytes, metadata
            FROM payroll_backup_metadata
            ORDER BY started_at DESC
            LIMIT %s
        """
        
        results = self.hook.get_records(sql, parameters=(limit,))
        
        backups = []
        for row in results:
            backups.append({
                "id": row[0],
                "backup_type": row[1],
                "description": row[2],
                "status": row[3],
                "started_at": row[4],
                "completed_at": row[5],
                "record_count": row[6],
                "size_bytes": row[7],
                "metadata": row[8] if isinstance(row[8], dict) else json.loads(row[8]) if row[8] else {}
            })
        
        return backups

