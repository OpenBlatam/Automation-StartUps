"""
Exportadores de Datos de Nómina
Exporta datos a diferentes formatos (CSV, JSON, Excel)
"""

import logging
import csv
import json
from io import StringIO, BytesIO
from datetime import date
from decimal import Decimal
from typing import Dict, Any, List, Optional
from dataclasses import asdict

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from airflow.providers.postgres.hooks.postgres import PostgresHook

from .reports import PayrollReport

logger = logging.getLogger(__name__)


class PayrollExporter:
    """Exportador de datos de nómina"""
    
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
    
    def export_payroll_to_csv(
        self,
        period_start: date,
        period_end: date,
        include_details: bool = True
    ) -> str:
        """Exporta nómina a CSV"""
        sql = """
            SELECT 
                pp.employee_id,
                e.name as employee_name,
                pp.period_start,
                pp.period_end,
                pp.pay_date,
                pp.gross_pay,
                pp.total_deductions,
                pp.total_expenses,
                pp.net_pay,
                pp.total_hours,
                pp.regular_hours,
                pp.overtime_hours,
                pp.status
            FROM payroll_pay_periods pp
            JOIN payroll_employees e ON pp.employee_id = e.employee_id
            WHERE pp.period_start = %s AND pp.period_end = %s
            ORDER BY pp.employee_id
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(period_start, period_end)
        )
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Headers
        headers = [
            "Employee ID", "Employee Name", "Period Start", "Period End",
            "Pay Date", "Gross Pay", "Deductions", "Expenses", "Net Pay",
            "Total Hours", "Regular Hours", "Overtime Hours", "Status"
        ]
        writer.writerow(headers)
        
        # Data
        for row in results:
            writer.writerow([
                row[0], row[1], row[2], row[3], row[4],
                float(row[5]) if row[5] else 0.0,
                float(row[6]) if row[6] else 0.0,
                float(row[7]) if row[7] else 0.0,
                float(row[8]) if row[8] else 0.0,
                float(row[9]) if row[9] else 0.0,
                float(row[10]) if row[10] else 0.0,
                float(row[11]) if row[11] else 0.0,
                row[12]
            ])
        
        return output.getvalue()
    
    def export_payroll_to_json(
        self,
        period_start: date,
        period_end: date
    ) -> str:
        """Exporta nómina a JSON"""
        sql = """
            SELECT 
                pp.employee_id,
                e.name as employee_name,
                e.email,
                pp.period_start,
                pp.period_end,
                pp.pay_date,
                pp.gross_pay,
                pp.total_deductions,
                pp.total_expenses,
                pp.net_pay,
                pp.total_hours,
                pp.regular_hours,
                pp.overtime_hours,
                pp.status
            FROM payroll_pay_periods pp
            JOIN payroll_employees e ON pp.employee_id = e.employee_id
            WHERE pp.period_start = %s AND pp.period_end = %s
            ORDER BY pp.employee_id
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(period_start, period_end)
        )
        
        data = {
            "period_start": str(period_start),
            "period_end": str(period_end),
            "exported_at": str(date.today()),
            "records": []
        }
        
        for row in results:
            data["records"].append({
                "employee_id": row[0],
                "employee_name": row[1],
                "email": row[2],
                "period_start": str(row[3]),
                "period_end": str(row[4]),
                "pay_date": str(row[5]),
                "gross_pay": float(row[6]) if row[6] else 0.0,
                "deductions": float(row[7]) if row[7] else 0.0,
                "expenses": float(row[8]) if row[8] else 0.0,
                "net_pay": float(row[9]) if row[9] else 0.0,
                "total_hours": float(row[10]) if row[10] else 0.0,
                "regular_hours": float(row[11]) if row[11] else 0.0,
                "overtime_hours": float(row[12]) if row[12] else 0.0,
                "status": row[13]
            })
        
        return json.dumps(data, indent=2)
    
    def export_payroll_to_excel(
        self,
        period_start: date,
        period_end: date,
        output_path: Optional[str] = None
    ) -> Optional[BytesIO]:
        """Exporta nómina a Excel"""
        if not PANDAS_AVAILABLE:
            logger.error("pandas is required for Excel export. Install with: pip install pandas openpyxl")
            return None
        
        sql = """
            SELECT 
                pp.employee_id,
                e.name as employee_name,
                e.email,
                pp.period_start,
                pp.period_end,
                pp.pay_date,
                pp.gross_pay,
                pp.total_deductions,
                pp.total_expenses,
                pp.net_pay,
                pp.total_hours,
                pp.regular_hours,
                pp.overtime_hours,
                pp.status
            FROM payroll_pay_periods pp
            JOIN payroll_employees e ON pp.employee_id = e.employee_id
            WHERE pp.period_start = %s AND pp.period_end = %s
            ORDER BY pp.employee_id
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(period_start, period_end)
        )
        
        df = pd.DataFrame(results, columns=[
            "Employee ID", "Employee Name", "Email",
            "Period Start", "Period End", "Pay Date",
            "Gross Pay", "Deductions", "Expenses", "Net Pay",
            "Total Hours", "Regular Hours", "Overtime Hours", "Status"
        ])
        
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Payroll', index=False)
            
            # Agregar hoja de resumen
            summary_data = {
                "Metric": [
                    "Total Employees",
                    "Total Gross Pay",
                    "Total Deductions",
                    "Total Expenses",
                    "Total Net Pay",
                    "Total Hours",
                    "Regular Hours",
                    "Overtime Hours"
                ],
                "Value": [
                    len(df),
                    df["Gross Pay"].sum(),
                    df["Deductions"].sum(),
                    df["Expenses"].sum(),
                    df["Net Pay"].sum(),
                    df["Total Hours"].sum(),
                    df["Regular Hours"].sum(),
                    df["Overtime Hours"].sum()
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        output.seek(0)
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(output.getvalue())
            return None
        
        return output
    
    def export_expenses_to_csv(
        self,
        period_start: date,
        period_end: date
    ) -> str:
        """Exporta gastos a CSV"""
        sql = """
            SELECT 
                er.employee_id,
                e.name as employee_name,
                er.receipt_number,
                er.expense_date,
                er.amount,
                er.currency,
                er.category,
                er.vendor,
                er.description,
                er.approved,
                er.reimbursed,
                er.ocr_status
            FROM payroll_expense_receipts er
            JOIN payroll_employees e ON er.employee_id = e.employee_id
            WHERE er.expense_date >= %s AND er.expense_date <= %s
            ORDER BY er.employee_id, er.expense_date
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(period_start, period_end)
        )
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Headers
        headers = [
            "Employee ID", "Employee Name", "Receipt Number",
            "Expense Date", "Amount", "Currency", "Category",
            "Vendor", "Description", "Approved", "Reimbursed", "OCR Status"
        ]
        writer.writerow(headers)
        
        # Data
        for row in results:
            writer.writerow([
                row[0], row[1], row[2], row[3],
                float(row[4]) if row[4] else 0.0,
                row[5], row[6], row[7], row[8],
                "Yes" if row[9] else "No",
                "Yes" if row[10] else "No",
                row[11]
            ])
        
        return output.getvalue()

