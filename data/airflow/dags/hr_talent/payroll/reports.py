"""
Generador de Reportes de Nómina
Genera reportes detallados y métricas
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


@dataclass
class PayrollReport:
    """Reporte de nómina"""
    period_start: date
    period_end: date
    employee_count: int
    total_gross_pay: Decimal
    total_deductions: Decimal
    total_expenses: Decimal
    total_net_pay: Decimal
    total_hours: Decimal
    regular_hours: Decimal
    overtime_hours: Decimal
    details: List[Dict[str, Any]]


class PayrollReporter:
    """Generador de reportes de nómina"""
    
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
    
    def generate_period_report(
        self,
        period_start: date,
        period_end: date
    ) -> PayrollReport:
        """Genera reporte para un período"""
        sql = """
            SELECT 
                COUNT(DISTINCT employee_id) as employee_count,
                SUM(gross_pay) as total_gross,
                SUM(total_deductions) as total_deductions,
                SUM(total_expenses) as total_expenses,
                SUM(net_pay) as total_net,
                SUM(total_hours) as total_hours,
                SUM(regular_hours) as regular_hours,
                SUM(overtime_hours) as overtime_hours
            FROM payroll_pay_periods
            WHERE period_start = %s AND period_end = %s
                AND status IN ('calculated', 'reviewed', 'approved', 'paid')
        """
        
        result = self.hook.get_first(
            sql,
            parameters=(period_start, period_end)
        )
        
        if not result or not result[0]:
            return PayrollReport(
                period_start=period_start,
                period_end=period_end,
                employee_count=0,
                total_gross_pay=Decimal("0.00"),
                total_deductions=Decimal("0.00"),
                total_expenses=Decimal("0.00"),
                total_net_pay=Decimal("0.00"),
                total_hours=Decimal("0.00"),
                regular_hours=Decimal("0.00"),
                overtime_hours=Decimal("0.00"),
                details=[]
            )
        
        # Obtener detalles por empleado
        details_sql = """
            SELECT 
                employee_id,
                gross_pay,
                total_deductions,
                total_expenses,
                net_pay,
                total_hours,
                regular_hours,
                overtime_hours
            FROM payroll_pay_periods
            WHERE period_start = %s AND period_end = %s
                AND status IN ('calculated', 'reviewed', 'approved', 'paid')
            ORDER BY employee_id
        """
        
        details_results = self.hook.get_records(
            details_sql,
            parameters=(period_start, period_end)
        )
        
        details = []
        for row in details_results:
            details.append({
                "employee_id": row[0],
                "gross_pay": Decimal(str(row[1])),
                "deductions": Decimal(str(row[2])),
                "expenses": Decimal(str(row[3])),
                "net_pay": Decimal(str(row[4])),
                "total_hours": Decimal(str(row[5])),
                "regular_hours": Decimal(str(row[6])),
                "overtime_hours": Decimal(str(row[7]))
            })
        
        return PayrollReport(
            period_start=period_start,
            period_end=period_end,
            employee_count=result[0] or 0,
            total_gross_pay=Decimal(str(result[1] or 0)),
            total_deductions=Decimal(str(result[2] or 0)),
            total_expenses=Decimal(str(result[3] or 0)),
            total_net_pay=Decimal(str(result[4] or 0)),
            total_hours=Decimal(str(result[5] or 0)),
            regular_hours=Decimal(str(result[6] or 0)),
            overtime_hours=Decimal(str(result[7] or 0)),
            details=details
        )
    
    def generate_employee_report(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Genera reporte para un empleado específico"""
        sql = """
            SELECT 
                period_start,
                period_end,
                pay_date,
                gross_pay,
                total_deductions,
                total_expenses,
                net_pay,
                total_hours,
                regular_hours,
                overtime_hours,
                status
            FROM payroll_pay_periods
            WHERE employee_id = %s
                AND period_start >= %s
                AND period_end <= %s
            ORDER BY period_start DESC
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(employee_id, start_date, end_date)
        )
        
        periods = []
        total_gross = Decimal("0.00")
        total_net = Decimal("0.00")
        
        for row in results:
            period_data = {
                "period_start": row[0],
                "period_end": row[1],
                "pay_date": row[2],
                "gross_pay": Decimal(str(row[3])),
                "deductions": Decimal(str(row[4])),
                "expenses": Decimal(str(row[5])),
                "net_pay": Decimal(str(row[6])),
                "total_hours": Decimal(str(row[7])),
                "regular_hours": Decimal(str(row[8])),
                "overtime_hours": Decimal(str(row[9])),
                "status": row[10]
            }
            periods.append(period_data)
            total_gross += period_data["gross_pay"]
            total_net += period_data["net_pay"]
        
        return {
            "employee_id": employee_id,
            "start_date": start_date,
            "end_date": end_date,
            "periods": periods,
            "summary": {
                "period_count": len(periods),
                "total_gross_pay": total_gross,
                "total_net_pay": total_net,
                "average_gross_pay": total_gross / len(periods) if periods else Decimal("0.00"),
                "average_net_pay": total_net / len(periods) if periods else Decimal("0.00")
            }
        }
    
    def generate_expense_report(
        self,
        period_start: date,
        period_end: date
    ) -> Dict[str, Any]:
        """Genera reporte de gastos"""
        sql = """
            SELECT 
                employee_id,
                COUNT(*) as receipt_count,
                SUM(amount) as total_amount,
                SUM(CASE WHEN approved = true THEN amount ELSE 0 END) as approved_amount,
                SUM(CASE WHEN reimbursed = true THEN amount ELSE 0 END) as reimbursed_amount
            FROM payroll_expense_receipts
            WHERE expense_date >= %s AND expense_date <= %s
            GROUP BY employee_id
            ORDER BY total_amount DESC
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(period_start, period_end)
        )
        
        employee_expenses = []
        total_amount = Decimal("0.00")
        total_approved = Decimal("0.00")
        total_reimbursed = Decimal("0.00")
        
        for row in results:
            data = {
                "employee_id": row[0],
                "receipt_count": row[1],
                "total_amount": Decimal(str(row[2] or 0)),
                "approved_amount": Decimal(str(row[3] or 0)),
                "reimbursed_amount": Decimal(str(row[4] or 0))
            }
            employee_expenses.append(data)
            total_amount += data["total_amount"]
            total_approved += data["approved_amount"]
            total_reimbursed += data["reimbursed_amount"]
        
        return {
            "period_start": period_start,
            "period_end": period_end,
            "employee_expenses": employee_expenses,
            "summary": {
                "total_receipts": sum(e["receipt_count"] for e in employee_expenses),
                "total_amount": total_amount,
                "total_approved": total_approved,
                "total_reimbursed": total_reimbursed,
                "pending_approval": total_amount - total_approved,
                "pending_reimbursement": total_approved - total_reimbursed
            }
        }
    
    def export_to_dict(self, report: PayrollReport) -> Dict[str, Any]:
        """Exporta reporte a diccionario"""
        return {
            "period_start": str(report.period_start),
            "period_end": str(report.period_end),
            "employee_count": report.employee_count,
            "total_gross_pay": str(report.total_gross_pay),
            "total_deductions": str(report.total_deductions),
            "total_expenses": str(report.total_expenses),
            "total_net_pay": str(report.total_net_pay),
            "total_hours": str(report.total_hours),
            "regular_hours": str(report.regular_hours),
            "overtime_hours": str(report.overtime_hours),
            "details": [
                {
                    "employee_id": d["employee_id"],
                    "gross_pay": str(d["gross_pay"]),
                    "deductions": str(d["deductions"]),
                    "expenses": str(d["expenses"]),
                    "net_pay": str(d["net_pay"]),
                    "total_hours": str(d["total_hours"]),
                    "regular_hours": str(d["regular_hours"]),
                    "overtime_hours": str(d["overtime_hours"])
                }
                for d in report.details
            ]
        }

