"""
Sistema de Mantenimiento para Nómina
Limpieza, archivado, optimización y mantenimiento del sistema
"""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, Any, Optional, List
from decimal import Decimal

from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


class PayrollMaintenance:
    """Sistema de mantenimiento para nómina"""
    
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
    
    def archive_old_pay_periods(
        self,
        retention_days: int = 365,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Archiva períodos de pago antiguos"""
        cutoff_date = date.today() - timedelta(days=retention_days)
        
        # Verificar si existe tabla de archivo
        check_sql = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'payroll_pay_periods_archive'
            )
        """
        
        exists = self.hook.get_first(check_sql)[0]
        
        if not exists and not dry_run:
            # Crear tabla de archivo
            create_sql = """
                CREATE TABLE IF NOT EXISTS payroll_pay_periods_archive (
                    LIKE payroll_pay_periods INCLUDING ALL
                );
                
                CREATE INDEX IF NOT EXISTS idx_archive_employee_id 
                    ON payroll_pay_periods_archive(employee_id);
                CREATE INDEX IF NOT EXISTS idx_archive_period 
                    ON payroll_pay_periods_archive(period_start, period_end);
            """
            self.hook.run(create_sql)
        
        # Contar registros a archivar
        count_sql = """
            SELECT COUNT(*)
            FROM payroll_pay_periods
            WHERE period_end < %s
                AND status IN ('paid', 'cancelled')
        """
        
        count_result = self.hook.get_first(count_sql, parameters=(cutoff_date,))
        count = count_result[0] if count_result else 0
        
        if count == 0:
            return {
                "archived": 0,
                "deleted": 0,
                "skipped": True,
                "message": "No records to archive"
            }
        
        if dry_run:
            return {
                "archived": count,
                "deleted": 0,
                "skipped": True,
                "message": f"[DRY RUN] Would archive {count} records"
            }
        
        # Archivar
        archive_sql = """
            INSERT INTO payroll_pay_periods_archive
            SELECT * FROM payroll_pay_periods
            WHERE period_end < %s
                AND status IN ('paid', 'cancelled')
        """
        
        self.hook.run(archive_sql, parameters=(cutoff_date,))
        
        # Eliminar de tabla principal
        delete_sql = """
            DELETE FROM payroll_pay_periods
            WHERE period_end < %s
                AND status IN ('paid', 'cancelled')
        """
        
        self.hook.run(delete_sql, parameters=(cutoff_date,))
        
        return {
            "archived": count,
            "deleted": count,
            "skipped": False,
            "cutoff_date": str(cutoff_date)
        }
    
    def cleanup_old_expense_receipts(
        self,
        retention_days: int = 730,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Limpia recibos de gastos antiguos"""
        cutoff_date = date.today() - timedelta(days=retention_days)
        
        # Contar registros a eliminar
        count_sql = """
            SELECT COUNT(*)
            FROM payroll_expense_receipts
            WHERE expense_date < %s
                AND reimbursed = true
                AND approved = true
        """
        
        count_result = self.hook.get_first(count_sql, parameters=(cutoff_date,))
        count = count_result[0] if count_result else 0
        
        if count == 0:
            return {
                "deleted": 0,
                "skipped": True,
                "message": "No records to delete"
            }
        
        if dry_run:
            return {
                "deleted": count,
                "skipped": True,
                "message": f"[DRY RUN] Would delete {count} records"
            }
        
        # Eliminar
        delete_sql = """
            DELETE FROM payroll_expense_receipts
            WHERE expense_date < %s
                AND reimbursed = true
                AND approved = true
        """
        
        self.hook.run(delete_sql, parameters=(cutoff_date,))
        
        return {
            "deleted": count,
            "skipped": False,
            "cutoff_date": str(cutoff_date)
        }
    
    def cleanup_failed_ocr_receipts(
        self,
        days: int = 90,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Limpia recibos con OCR fallido antiguos"""
        cutoff_date = date.today() - timedelta(days=days)
        
        count_sql = """
            SELECT COUNT(*)
            FROM payroll_expense_receipts
            WHERE ocr_status = 'failed'
                AND created_at < %s
        """
        
        count_result = self.hook.get_first(count_sql, parameters=(cutoff_date,))
        count = count_result[0] if count_result else 0
        
        if dry_run:
            return {
                "deleted": count,
                "skipped": True,
                "message": f"[DRY RUN] Would delete {count} failed OCR receipts"
            }
        
        if count > 0:
            delete_sql = """
                DELETE FROM payroll_expense_receipts
                WHERE ocr_status = 'failed'
                    AND created_at < %s
            """
            self.hook.run(delete_sql, parameters=(cutoff_date,))
        
        return {
            "deleted": count,
            "skipped": False,
            "cutoff_date": str(cutoff_date)
        }
    
    def optimize_tables(self) -> Dict[str, Any]:
        """Optimiza tablas de nómina"""
        tables = [
            "payroll_employees",
            "payroll_time_entries",
            "payroll_expense_receipts",
            "payroll_deductions",
            "payroll_pay_periods",
            "payroll_pay_calculations"
        ]
        
        optimized = []
        
        for table in tables:
            try:
                # ANALYZE table
                analyze_sql = f"ANALYZE {table}"
                self.hook.run(analyze_sql)
                
                # VACUUM (sin bloquear)
                vacuum_sql = f"VACUUM ANALYZE {table}"
                self.hook.run(vacuum_sql)
                
                optimized.append(table)
            except Exception as e:
                logger.error(f"Error optimizing table {table}: {e}")
        
        return {
            "optimized": len(optimized),
            "tables": optimized
        }
    
    def refresh_all_materialized_views(self) -> Dict[str, Any]:
        """Refresca todas las vistas materializadas"""
        views = [
            "mv_payroll_hours_summary",
            "mv_payroll_expenses_summary",
            "mv_payroll_payments_summary"
        ]
        
        refreshed = []
        
        for view in views:
            try:
                sql = f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view}"
                self.hook.run(sql)
                refreshed.append(view)
            except Exception as e:
                logger.error(f"Error refreshing view {view}: {e}")
        
        return {
            "refreshed": len(refreshed),
            "views": refreshed
        }
    
    def cleanup_stale_approvals(
        self,
        days: int = 90,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Limpia aprobaciones pendientes antiguas"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        count_sql = """
            SELECT COUNT(*)
            FROM payroll_approvals
            WHERE status = 'pending'
                AND requested_at < %s
        """
        
        count_result = self.hook.get_first(count_sql, parameters=(cutoff_date,))
        count = count_result[0] if count_result else 0
        
        if dry_run:
            return {
                "found": count,
                "skipped": True,
                "message": f"[DRY RUN] Found {count} stale approvals"
            }
        
        # Marcar como requeriendo revisión manual
        update_sql = """
            UPDATE payroll_approvals
            SET status = 'requires_review',
                metadata = COALESCE(metadata, '{}'::jsonb) || 
                    jsonb_build_object('stale_cleanup', NOW()::text)
            WHERE status = 'pending'
                AND requested_at < %s
        """
        
        self.hook.run(update_sql, parameters=(cutoff_date,))
        
        return {
            "found": count,
            "updated": count,
            "skipped": False
        }
    
    def get_maintenance_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas para mantenimiento"""
        stats = {}
        
        # Estadísticas de períodos
        periods_sql = """
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'paid' THEN 1 END) as paid,
                COUNT(CASE WHEN status = 'draft' THEN 1 END) as draft,
                COUNT(CASE WHEN period_end < CURRENT_DATE - INTERVAL '90 days' THEN 1 END) as old
            FROM payroll_pay_periods
        """
        
        periods_result = self.hook.get_first(periods_sql)
        if periods_result:
            stats["pay_periods"] = {
                "total": periods_result[0] or 0,
                "paid": periods_result[1] or 0,
                "draft": periods_result[2] or 0,
                "old": periods_result[3] or 0
            }
        
        # Estadísticas de aprobaciones
        approvals_sql = """
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                COUNT(CASE WHEN status = 'pending' AND requested_at < NOW() - INTERVAL '30 days' THEN 1 END) as stale
            FROM payroll_approvals
        """
        
        approvals_result = self.hook.get_first(approvals_sql)
        if approvals_result:
            stats["approvals"] = {
                "total": approvals_result[0] or 0,
                "pending": approvals_result[1] or 0,
                "stale": approvals_result[2] or 0
            }
        
        # Estadísticas de OCR
        ocr_sql = """
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN ocr_status = 'failed' THEN 1 END) as failed,
                COUNT(CASE WHEN ocr_status = 'pending' THEN 1 END) as pending
            FROM payroll_expense_receipts
        """
        
        ocr_result = self.hook.get_first(ocr_sql)
        if ocr_result:
            stats["ocr"] = {
                "total": ocr_result[0] or 0,
                "failed": ocr_result[1] or 0,
                "pending": ocr_result[2] or 0
            }
        
        return stats

