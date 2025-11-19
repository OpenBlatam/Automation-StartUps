"""
Dashboard y Visualizaciones para Nómina
Genera datos para dashboards y visualizaciones
"""

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


@dataclass
class DashboardData:
    """Datos para dashboard"""
    period_start: date
    period_end: date
    total_employees: int
    total_gross_pay: Decimal
    total_net_pay: Decimal
    total_hours: Decimal
    pending_approvals: int
    failed_ocr: int
    department_breakdown: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]


class PayrollDashboard:
    """Generador de datos para dashboard"""
    
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
    
    def get_dashboard_data(
        self,
        period_start: Optional[date] = None,
        period_end: Optional[date] = None
    ) -> DashboardData:
        """Obtiene todos los datos para el dashboard"""
        if period_start is None or period_end is None:
            period_start, period_end = self._get_current_period()
        
        # Obtener datos principales
        main_sql = """
            SELECT 
                COUNT(DISTINCT pp.employee_id) as employee_count,
                SUM(pp.gross_pay) as total_gross,
                SUM(pp.net_pay) as total_net,
                SUM(pp.total_hours) as total_hours
            FROM payroll_pay_periods pp
            WHERE pp.period_start = %s AND pp.period_end = %s
                AND pp.status IN ('calculated', 'reviewed', 'approved', 'paid')
        """
        
        main_result = self.hook.get_first(
            main_sql,
            parameters=(period_start, period_end)
        )
        
        # Obtener aprobaciones pendientes
        approvals_sql = """
            SELECT COUNT(*)
            FROM payroll_approvals
            WHERE status = 'pending'
        """
        
        approvals_result = self.hook.get_first(approvals_sql)
        pending_approvals = approvals_result[0] if approvals_result else 0
        
        # Obtener OCR fallidos recientes
        ocr_sql = """
            SELECT COUNT(*)
            FROM payroll_expense_receipts
            WHERE ocr_status = 'failed'
                AND created_at >= NOW() - INTERVAL '7 days'
        """
        
        ocr_result = self.hook.get_first(ocr_sql)
        failed_ocr = ocr_result[0] if ocr_result else 0
        
        # Obtener breakdown por departamento
        dept_sql = """
            SELECT 
                e.department,
                COUNT(DISTINCT pp.employee_id) as employees,
                SUM(pp.net_pay) as total_net
            FROM payroll_pay_periods pp
            JOIN payroll_employees e ON pp.employee_id = e.employee_id
            WHERE pp.period_start = %s AND pp.period_end = %s
                AND pp.status IN ('calculated', 'reviewed', 'approved', 'paid')
                AND e.department IS NOT NULL
            GROUP BY e.department
            ORDER BY total_net DESC
        """
        
        dept_results = self.hook.get_records(
            dept_sql,
            parameters=(period_start, period_end)
        )
        
        department_breakdown = []
        for row in dept_results:
            department_breakdown.append({
                "department": row[0],
                "employee_count": row[1],
                "total_net_pay": float(Decimal(str(row[2] or 0)))
            })
        
        # Obtener actividad reciente
        activity_sql = """
            SELECT 
                'pay_period' as type,
                employee_id,
                period_start::text as period_start,
                net_pay,
                status,
                created_at
            FROM payroll_pay_periods
            WHERE created_at >= NOW() - INTERVAL '7 days'
            ORDER BY created_at DESC
            LIMIT 10
        """
        
        activity_results = self.hook.get_records(activity_sql)
        
        recent_activity = []
        for row in activity_results:
            recent_activity.append({
                "type": row[0],
                "employee_id": row[1],
                "period": row[2],
                "amount": float(Decimal(str(row[3] or 0))),
                "status": row[4],
                "created_at": row[5].isoformat() if row[5] else None
            })
        
        return DashboardData(
            period_start=period_start,
            period_end=period_end,
            total_employees=main_result[0] if main_result else 0,
            total_gross_pay=Decimal(str(main_result[1] or 0)) if main_result else Decimal("0.00"),
            total_net_pay=Decimal(str(main_result[2] or 0)) if main_result else Decimal("0.00"),
            total_hours=Decimal(str(main_result[3] or 0)) if main_result else Decimal("0.00"),
            pending_approvals=pending_approvals,
            failed_ocr=failed_ocr,
            department_breakdown=department_breakdown,
            recent_activity=recent_activity
        )
    
    def get_time_series_data(
        self,
        periods: int = 12,
        period_type: str = "biweekly"
    ) -> Dict[str, Any]:
        """Obtiene datos de series temporales"""
        end_date = date.today()
        
        if period_type == "biweekly":
            start_date = end_date - timedelta(days=periods * 14)
        else:
            start_date = end_date - timedelta(days=periods * 30)
        
        sql = """
            SELECT 
                period_start,
                period_end,
                COUNT(DISTINCT employee_id) as employees,
                SUM(gross_pay) as gross,
                SUM(net_pay) as net,
                SUM(total_hours) as hours
            FROM payroll_pay_periods
            WHERE period_start >= %s
                AND status IN ('calculated', 'reviewed', 'approved', 'paid')
            GROUP BY period_start, period_end
            ORDER BY period_start ASC
        """
        
        results = self.hook.get_records(sql, parameters=(start_date,))
        
        time_series = []
        for row in results:
            time_series.append({
                "period_start": str(row[0]),
                "period_end": str(row[1]),
                "employees": row[2],
                "gross_pay": float(Decimal(str(row[3] or 0))),
                "net_pay": float(Decimal(str(row[4] or 0))),
                "hours": float(Decimal(str(row[5] or 0)))
            })
        
        return {
            "periods": time_series,
            "summary": {
                "total_periods": len(time_series),
                "avg_gross": sum(t["gross_pay"] for t in time_series) / len(time_series) if time_series else 0.0,
                "avg_net": sum(t["net_pay"] for t in time_series) / len(time_series) if time_series else 0.0
            }
        }
    
    def get_kpi_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de KPIs"""
        # KPIs del período actual
        current_period = self._get_current_period()
        dashboard_data = self.get_dashboard_data(*current_period)
        
        # KPIs de gastos
        expenses_sql = """
            SELECT 
                COUNT(*) as total_receipts,
                SUM(amount) as total_amount,
                SUM(CASE WHEN approved = true THEN amount ELSE 0 END) as approved_amount,
                SUM(CASE WHEN reimbursed = true THEN amount ELSE 0 END) as reimbursed_amount
            FROM payroll_expense_receipts
            WHERE expense_date >= %s
        """
        
        expenses_result = self.hook.get_first(
            expenses_sql,
            parameters=(current_period[0],)
        )
        
        # KPIs de aprobaciones
        approvals_sql = """
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved,
                COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected
            FROM payroll_approvals
            WHERE requested_at >= NOW() - INTERVAL '30 days'
        """
        
        approvals_result = self.hook.get_first(approvals_sql)
        
        return {
            "current_period": {
                "period_start": str(current_period[0]),
                "period_end": str(current_period[1]),
                "total_employees": dashboard_data.total_employees,
                "total_gross_pay": float(dashboard_data.total_gross_pay),
                "total_net_pay": float(dashboard_data.total_net_pay),
                "total_hours": float(dashboard_data.total_hours)
            },
            "expenses": {
                "total_receipts": expenses_result[0] if expenses_result else 0,
                "total_amount": float(Decimal(str(expenses_result[1] or 0))) if expenses_result else 0.0,
                "approved_amount": float(Decimal(str(expenses_result[2] or 0))) if expenses_result else 0.0,
                "reimbursed_amount": float(Decimal(str(expenses_result[3] or 0))) if expenses_result else 0.0
            },
            "approvals": {
                "total": approvals_result[0] if approvals_result else 0,
                "pending": approvals_result[1] if approvals_result else 0,
                "approved": approvals_result[2] if approvals_result else 0,
                "rejected": approvals_result[3] if approvals_result else 0
            },
            "alerts": {
                "pending_approvals": dashboard_data.pending_approvals,
                "failed_ocr": dashboard_data.failed_ocr
            }
        }
    
    def _get_current_period(self) -> tuple[date, date]:
        """Obtiene el período actual"""
        from .utils import get_pay_period_dates
        return get_pay_period_dates(period_type="biweekly")
    
    def export_for_dashboard(self, data: DashboardData) -> Dict[str, Any]:
        """Exporta datos para dashboard web"""
        return {
            "period": {
                "start": str(data.period_start),
                "end": str(data.period_end)
            },
            "metrics": {
                "total_employees": data.total_employees,
                "total_gross_pay": float(data.total_gross_pay),
                "total_net_pay": float(data.total_net_pay),
                "total_hours": float(data.total_hours)
            },
            "alerts": {
                "pending_approvals": data.pending_approvals,
                "failed_ocr": data.failed_ocr
            },
            "department_breakdown": data.department_breakdown,
            "recent_activity": data.recent_activity
        }

