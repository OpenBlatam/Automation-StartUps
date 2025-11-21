"""
Sistema de Sincronización para Nómina
Sincronización con sistemas externos y replicación
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass

from airflow.providers.postgres.hooks.postgres import PostgresHook

from .exceptions import PayrollError

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """Resultado de sincronización"""
    success: bool
    records_synced: int
    records_failed: int
    errors: List[str]
    sync_timestamp: datetime


class PayrollSync:
    """Sistema de sincronización para nómina"""
    
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
    
    def sync_pay_periods_to_external(
        self,
        period_start: date,
        period_end: date,
        sync_handler: Callable[[Dict[str, Any]], bool],
        batch_size: int = 10
    ) -> SyncResult:
        """
        Sincroniza períodos de pago a sistema externo
        
        Args:
            period_start: Inicio del período
            period_end: Fin del período
            sync_handler: Función que sincroniza un período
            batch_size: Tamaño de lote para sincronización
        """
        sql = """
            SELECT 
                id, employee_id, period_start, period_end,
                gross_pay, net_pay, status
            FROM payroll_pay_periods
            WHERE period_start = %s AND period_end = %s
                AND status IN ('calculated', 'reviewed', 'approved', 'paid')
            ORDER BY employee_id
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(period_start, period_end)
        )
        
        records_synced = 0
        records_failed = 0
        errors = []
        
        for row in results:
            period_data = {
                "id": row[0],
                "employee_id": row[1],
                "period_start": str(row[2]),
                "period_end": str(row[3]),
                "gross_pay": float(Decimal(str(row[4] or 0))),
                "net_pay": float(Decimal(str(row[5] or 0))),
                "status": row[6]
            }
            
            try:
                if sync_handler(period_data):
                    records_synced += 1
                else:
                    records_failed += 1
                    errors.append(f"Sync failed for period {row[0]}")
            except Exception as e:
                records_failed += 1
                errors.append(f"Error syncing period {row[0]}: {e}")
                logger.error(f"Error syncing period {row[0]}: {e}")
        
        return SyncResult(
            success=records_failed == 0,
            records_synced=records_synced,
            records_failed=records_failed,
            errors=errors,
            sync_timestamp=datetime.now()
        )
    
    def mark_synced(
        self,
        entity_type: str,
        entity_id: int,
        external_id: Optional[str] = None
    ) -> bool:
        """Marca una entidad como sincronizada"""
        # Crear tabla de sincronización si no existe
        create_sql = """
            CREATE TABLE IF NOT EXISTS payroll_sync_status (
                id SERIAL PRIMARY KEY,
                entity_type VARCHAR(64) NOT NULL,
                entity_id INT NOT NULL,
                external_id VARCHAR(256),
                synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                sync_status VARCHAR(32) NOT NULL DEFAULT 'synced',
                metadata JSONB,
                UNIQUE(entity_type, entity_id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_sync_entity 
                ON payroll_sync_status(entity_type, entity_id);
            CREATE INDEX IF NOT EXISTS idx_sync_status 
                ON payroll_sync_status(sync_status);
        """
        
        try:
            self.hook.run(create_sql)
        except Exception as e:
            logger.warning(f"Error creating sync table: {e}")
        
        # Insertar/actualizar estado
        sql = """
            INSERT INTO payroll_sync_status (
                entity_type, entity_id, external_id, sync_status
            ) VALUES (%s, %s, %s, %s)
            ON CONFLICT (entity_type, entity_id)
            DO UPDATE SET
                external_id = EXCLUDED.external_id,
                synced_at = NOW(),
                sync_status = EXCLUDED.sync_status
        """
        
        try:
            self.hook.run(
                sql,
                parameters=(entity_type, entity_id, external_id, "synced")
            )
            return True
        except Exception as e:
            logger.error(f"Error marking as synced: {e}")
            return False
    
    def get_unsynced_records(
        self,
        entity_type: str,
        period_start: Optional[date] = None,
        period_end: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Obtiene registros no sincronizados"""
        if entity_type == "pay_period":
            sql = """
                SELECT pp.id, pp.employee_id, pp.period_start, pp.period_end,
                       pp.net_pay, pp.status
                FROM payroll_pay_periods pp
                LEFT JOIN payroll_sync_status ss 
                    ON ss.entity_type = 'pay_period' AND ss.entity_id = pp.id
                WHERE ss.id IS NULL
                    AND pp.status IN ('calculated', 'reviewed', 'approved', 'paid')
            """
            
            params = []
            if period_start:
                sql += " AND pp.period_start >= %s"
                params.append(period_start)
            if period_end:
                sql += " AND pp.period_end <= %s"
                params.append(period_end)
            
            results = self.hook.get_records(sql, parameters=tuple(params))
            
            records = []
            for row in results:
                records.append({
                    "id": row[0],
                    "employee_id": row[1],
                    "period_start": row[2],
                    "period_end": row[3],
                    "net_pay": float(Decimal(str(row[4] or 0))),
                    "status": row[5]
                })
            
            return records
        
        return []

