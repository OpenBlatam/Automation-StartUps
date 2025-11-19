"""
Health Checks para el Sistema de Nómina
Verifica el estado del sistema y sus componentes
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Estados de salud del sistema"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class PayrollHealthChecker:
    """Verificador de salud del sistema de nómina"""
    
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
    
    def check_database_connection(self) -> Dict[str, Any]:
        """Verifica conexión a la base de datos"""
        try:
            result = self.hook.get_first("SELECT 1")
            if result and result[0] == 1:
                return {
                    "status": HealthStatus.HEALTHY,
                    "message": "Database connection successful"
                }
            else:
                return {
                    "status": HealthStatus.WARNING,
                    "message": "Database connection returned unexpected result"
                }
        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL,
                "message": f"Database connection failed: {e}"
            }
    
    def check_schema_tables(self) -> Dict[str, Any]:
        """Verifica que todas las tablas necesarias existan"""
        required_tables = [
            "payroll_employees",
            "payroll_time_entries",
            "payroll_expense_receipts",
            "payroll_deductions",
            "payroll_pay_periods",
            "payroll_pay_calculations"
        ]
        
        missing_tables = []
        
        for table in required_tables:
            try:
                sql = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    )
                """
                result = self.hook.get_first(sql, parameters=(table,))
                if not result or not result[0]:
                    missing_tables.append(table)
            except Exception as e:
                logger.error(f"Error checking table {table}: {e}")
                missing_tables.append(table)
        
        if missing_tables:
            return {
                "status": HealthStatus.CRITICAL,
                "message": f"Missing tables: {', '.join(missing_tables)}",
                "missing_tables": missing_tables
            }
        
        return {
            "status": HealthStatus.HEALTHY,
            "message": "All required tables exist"
        }
    
    def check_pending_approvals(self, max_age_hours: int = 168) -> Dict[str, Any]:
        """Verifica aprobaciones pendientes antiguas"""
        try:
            sql = """
                SELECT COUNT(*)
                FROM payroll_approvals
                WHERE status = 'pending'
                    AND requested_at < NOW() - INTERVAL '%s hours'
            """
            
            result = self.hook.get_first(sql, parameters=(max_age_hours,))
            stale_count = result[0] if result else 0
            
            if stale_count > 10:
                return {
                    "status": HealthStatus.WARNING,
                    "message": f"{stale_count} stale pending approvals",
                    "stale_count": stale_count
                }
            elif stale_count > 0:
                return {
                    "status": HealthStatus.HEALTHY,
                    "message": f"{stale_count} stale pending approvals",
                    "stale_count": stale_count
                }
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "No stale pending approvals"
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNKNOWN,
                "message": f"Error checking approvals: {e}"
            }
    
    def check_failed_ocr(self, days: int = 7) -> Dict[str, Any]:
        """Verifica recibos con OCR fallido"""
        try:
            sql = """
                SELECT COUNT(*)
                FROM payroll_expense_receipts
                WHERE ocr_status = 'failed'
                    AND created_at >= NOW() - INTERVAL '%s days'
            """
            
            result = self.hook.get_first(sql, parameters=(days,))
            failed_count = result[0] if result else 0
            
            if failed_count > 50:
                return {
                    "status": HealthStatus.WARNING,
                    "message": f"{failed_count} failed OCR receipts in last {days} days",
                    "failed_count": failed_count
                }
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": f"{failed_count} failed OCR receipts",
                "failed_count": failed_count
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNKNOWN,
                "message": f"Error checking OCR: {e}"
            }
    
    def check_unprocessed_payroll(self) -> Dict[str, Any]:
        """Verifica períodos de pago sin procesar"""
        try:
            sql = """
                SELECT COUNT(*)
                FROM payroll_pay_periods
                WHERE status = 'draft'
                    AND pay_date < CURRENT_DATE
            """
            
            result = self.hook.get_first(sql)
            unprocessed = result[0] if result else 0
            
            if unprocessed > 0:
                return {
                    "status": HealthStatus.WARNING,
                    "message": f"{unprocessed} unprocessed payroll periods",
                    "unprocessed_count": unprocessed
                }
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "All payroll periods processed"
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNKNOWN,
                "message": f"Error checking payroll: {e}"
            }
    
    def comprehensive_health_check(self) -> Dict[str, Any]:
        """Realiza verificación completa de salud"""
        checks = {
            "database": self.check_database_connection(),
            "schema": self.check_schema_tables(),
            "pending_approvals": self.check_pending_approvals(),
            "failed_ocr": self.check_failed_ocr(),
            "unprocessed_payroll": self.check_unprocessed_payroll()
        }
        
        # Determinar estado general
        statuses = [check["status"] for check in checks.values()]
        
        if HealthStatus.CRITICAL in statuses:
            overall_status = HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            overall_status = HealthStatus.WARNING
        elif all(s == HealthStatus.HEALTHY for s in statuses):
            overall_status = HealthStatus.HEALTHY
        else:
            overall_status = HealthStatus.UNKNOWN
        
        return {
            "overall_status": overall_status.value,
            "timestamp": datetime.now().isoformat(),
            "checks": checks,
            "summary": {
                "healthy": sum(1 for s in statuses if s == HealthStatus.HEALTHY),
                "warnings": sum(1 for s in statuses if s == HealthStatus.WARNING),
                "critical": sum(1 for s in statuses if s == HealthStatus.CRITICAL),
                "unknown": sum(1 for s in statuses if s == HealthStatus.UNKNOWN)
            }
        }

