"""
Sistema de Métricas y KPIs para Nómina
Tracking de métricas en tiempo real y análisis de tendencias
"""

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


@dataclass
class PayrollMetrics:
    """Métricas de nómina"""
    period_start: date
    period_end: date
    total_employees: int
    total_gross_pay: Decimal
    total_net_pay: Decimal
    total_hours: Decimal
    avg_hours_per_employee: Decimal
    avg_gross_pay: Decimal
    avg_net_pay: Decimal
    total_deductions: Decimal
    total_expenses: Decimal
    overtime_percentage: Decimal
    processing_time_seconds: Optional[float] = None


class PayrollMetricsCollector:
    """Recolector de métricas de nómina"""
    
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
    
    def collect_period_metrics(
        self,
        period_start: date,
        period_end: date
    ) -> PayrollMetrics:
        """Recolecta métricas para un período"""
        sql = """
            SELECT 
                COUNT(DISTINCT pp.employee_id) as total_employees,
                COUNT(*) as pay_period_count,
                SUM(pp.gross_pay) as total_gross,
                SUM(pp.net_pay) as total_net,
                SUM(pp.total_hours) as total_hours,
                SUM(pp.overtime_hours) as total_overtime,
                SUM(pp.total_deductions) as total_deductions,
                SUM(pp.total_expenses) as total_expenses,
                AVG(pp.total_hours) as avg_hours,
                AVG(pp.gross_pay) as avg_gross,
                AVG(pp.net_pay) as avg_net
            FROM payroll_pay_periods pp
            WHERE pp.period_start = %s AND pp.period_end = %s
                AND pp.status IN ('calculated', 'reviewed', 'approved', 'paid')
        """
        
        result = self.hook.get_first(
            sql,
            parameters=(period_start, period_end)
        )
        
        if not result:
            return PayrollMetrics(
                period_start=period_start,
                period_end=period_end,
                total_employees=0,
                total_gross_pay=Decimal("0.00"),
                total_net_pay=Decimal("0.00"),
                total_hours=Decimal("0.00"),
                avg_hours_per_employee=Decimal("0.00"),
                avg_gross_pay=Decimal("0.00"),
                avg_net_pay=Decimal("0.00"),
                total_deductions=Decimal("0.00"),
                total_expenses=Decimal("0.00"),
                overtime_percentage=Decimal("0.00")
            )
        
        total_hours = Decimal(str(result[4] or 0))
        total_overtime = Decimal(str(result[5] or 0))
        total_employees = result[0] or 0
        
        overtime_pct = (
            (total_overtime / total_hours * 100) if total_hours > 0
            else Decimal("0.00")
        )
        
        return PayrollMetrics(
            period_start=period_start,
            period_end=period_end,
            total_employees=total_employees,
            total_gross_pay=Decimal(str(result[2] or 0)),
            total_net_pay=Decimal(str(result[3] or 0)),
            total_hours=total_hours,
            avg_hours_per_employee=Decimal(str(result[8] or 0)),
            avg_gross_pay=Decimal(str(result[9] or 0)),
            avg_net_pay=Decimal(str(result[10] or 0)),
            total_deductions=Decimal(str(result[6] or 0)),
            total_expenses=Decimal(str(result[7] or 0)),
            overtime_percentage=overtime_pct.quantize(Decimal("0.01"))
        )
    
    def get_trend_analysis(
        self,
        periods: int = 12,
        period_type: str = "biweekly"
    ) -> Dict[str, Any]:
        """Analiza tendencias de múltiples períodos"""
        end_date = date.today()
        
        if period_type == "biweekly":
            start_date = end_date - timedelta(days=periods * 14)
        elif period_type == "monthly":
            start_date = end_date - timedelta(days=periods * 30)
        else:
            start_date = end_date - timedelta(days=periods * 7)
        
        sql = """
            SELECT 
                period_start,
                period_end,
                COUNT(DISTINCT employee_id) as employees,
                SUM(gross_pay) as gross,
                SUM(net_pay) as net,
                SUM(total_hours) as hours,
                SUM(overtime_hours) as overtime
            FROM payroll_pay_periods
            WHERE period_start >= %s
                AND status IN ('calculated', 'reviewed', 'approved', 'paid')
            GROUP BY period_start, period_end
            ORDER BY period_start DESC
            LIMIT %s
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(start_date, periods)
        )
        
        trends = []
        for row in results:
            trends.append({
                "period_start": row[0],
                "period_end": row[1],
                "employees": row[2],
                "gross_pay": Decimal(str(row[3] or 0)),
                "net_pay": Decimal(str(row[4] or 0)),
                "hours": Decimal(str(row[5] or 0)),
                "overtime": Decimal(str(row[6] or 0))
            })
        
        # Calcular cambios porcentuales
        if len(trends) >= 2:
            latest = trends[0]
            previous = trends[1]
            
            gross_change = (
                ((latest["gross_pay"] - previous["gross_pay"]) / previous["gross_pay"] * 100)
                if previous["gross_pay"] > 0 else Decimal("0.00")
            )
            
            net_change = (
                ((latest["net_pay"] - previous["net_pay"]) / previous["net_pay"] * 100)
                if previous["net_pay"] > 0 else Decimal("0.00")
            )
        else:
            gross_change = Decimal("0.00")
            net_change = Decimal("0.00")
        
        return {
            "periods": trends,
            "latest_period": trends[0] if trends else None,
            "changes": {
                "gross_pay_percentage": gross_change.quantize(Decimal("0.01")),
                "net_pay_percentage": net_change.quantize(Decimal("0.01"))
            },
            "summary": {
                "total_periods": len(trends),
                "avg_gross_pay": sum(t["gross_pay"] for t in trends) / len(trends) if trends else Decimal("0.00"),
                "avg_net_pay": sum(t["net_pay"] for t in trends) / len(trends) if trends else Decimal("0.00")
            }
        }
    
    def get_department_metrics(
        self,
        period_start: date,
        period_end: date
    ) -> Dict[str, Any]:
        """Métricas por departamento"""
        sql = """
            SELECT 
                e.department,
                COUNT(DISTINCT pp.employee_id) as employee_count,
                SUM(pp.gross_pay) as total_gross,
                SUM(pp.net_pay) as total_net,
                SUM(pp.total_hours) as total_hours,
                AVG(pp.net_pay) as avg_net_pay
            FROM payroll_pay_periods pp
            JOIN payroll_employees e ON pp.employee_id = e.employee_id
            WHERE pp.period_start = %s AND pp.period_end = %s
                AND pp.status IN ('calculated', 'reviewed', 'approved', 'paid')
                AND e.department IS NOT NULL
            GROUP BY e.department
            ORDER BY total_gross DESC
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(period_start, period_end)
        )
        
        departments = []
        for row in results:
            departments.append({
                "department": row[0],
                "employee_count": row[1],
                "total_gross_pay": Decimal(str(row[2] or 0)),
                "total_net_pay": Decimal(str(row[3] or 0)),
                "total_hours": Decimal(str(row[4] or 0)),
                "avg_net_pay": Decimal(str(row[5] or 0))
            })
        
        return {
            "period_start": period_start,
            "period_end": period_end,
            "departments": departments,
            "total_departments": len(departments)
        }
    
    def get_expense_metrics(
        self,
        period_start: date,
        period_end: date
    ) -> Dict[str, Any]:
        """Métricas de gastos"""
        sql = """
            SELECT 
                COUNT(*) as total_receipts,
                SUM(amount) as total_amount,
                SUM(CASE WHEN approved = true THEN amount ELSE 0 END) as approved_amount,
                SUM(CASE WHEN reimbursed = true THEN amount ELSE 0 END) as reimbursed_amount,
                COUNT(CASE WHEN ocr_status = 'failed' THEN 1 END) as ocr_failed,
                COUNT(CASE WHEN ocr_status = 'completed' THEN 1 END) as ocr_completed,
                AVG(amount) as avg_amount
            FROM payroll_expense_receipts
            WHERE expense_date >= %s AND expense_date <= %s
        """
        
        result = self.hook.get_first(
            sql,
            parameters=(period_start, period_end)
        )
        
        if not result:
            return {}
        
        return {
            "period_start": period_start,
            "period_end": period_end,
            "total_receipts": result[0] or 0,
            "total_amount": Decimal(str(result[1] or 0)),
            "approved_amount": Decimal(str(result[2] or 0)),
            "reimbursed_amount": Decimal(str(result[3] or 0)),
            "pending_approval": Decimal(str(result[1] or 0)) - Decimal(str(result[2] or 0)),
            "pending_reimbursement": Decimal(str(result[2] or 0)) - Decimal(str(result[3] or 0)),
            "ocr_failed": result[4] or 0,
            "ocr_completed": result[5] or 0,
            "ocr_success_rate": (
                (result[5] / result[0] * 100) if result[0] > 0 else 0.0
            ),
            "avg_amount": Decimal(str(result[6] or 0))
        }

