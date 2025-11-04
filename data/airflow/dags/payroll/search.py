"""
Sistema de Búsqueda y Filtrado Avanzado
Búsqueda eficiente de datos de nómina
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


@dataclass
class SearchFilters:
    """Filtros para búsqueda"""
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None
    department: Optional[str] = None
    period_start_min: Optional[date] = None
    period_start_max: Optional[date] = None
    period_end_min: Optional[date] = None
    period_end_max: Optional[date] = None
    min_gross_pay: Optional[Decimal] = None
    max_gross_pay: Optional[Decimal] = None
    min_net_pay: Optional[Decimal] = None
    max_net_pay: Optional[Decimal] = None
    status: Optional[str] = None
    employee_type: Optional[str] = None


class PayrollSearch:
    """Sistema de búsqueda para nómina"""
    
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
    
    def search_pay_periods(
        self,
        filters: SearchFilters,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "period_start",
        order_direction: str = "DESC"
    ) -> Dict[str, Any]:
        """Busca períodos de pago con filtros"""
        conditions = []
        params = []
        
        # Construir condiciones dinámicamente
        if filters.employee_id:
            conditions.append("pp.employee_id = %s")
            params.append(filters.employee_id)
        
        if filters.employee_name:
            conditions.append("e.name ILIKE %s")
            params.append(f"%{filters.employee_name}%")
        
        if filters.department:
            conditions.append("e.department = %s")
            params.append(filters.department)
        
        if filters.period_start_min:
            conditions.append("pp.period_start >= %s")
            params.append(filters.period_start_min)
        
        if filters.period_start_max:
            conditions.append("pp.period_start <= %s")
            params.append(filters.period_start_max)
        
        if filters.min_gross_pay:
            conditions.append("pp.gross_pay >= %s")
            params.append(float(filters.min_gross_pay))
        
        if filters.max_gross_pay:
            conditions.append("pp.gross_pay <= %s")
            params.append(float(filters.max_gross_pay))
        
        if filters.min_net_pay:
            conditions.append("pp.net_pay >= %s")
            params.append(float(filters.min_net_pay))
        
        if filters.max_net_pay:
            conditions.append("pp.net_pay <= %s")
            params.append(float(filters.max_net_pay))
        
        if filters.status:
            conditions.append("pp.status = %s")
            params.append(filters.status)
        
        if filters.employee_type:
            conditions.append("e.employee_type = %s")
            params.append(filters.employee_type)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # Query principal
        sql = f"""
            SELECT 
                pp.id,
                pp.employee_id,
                e.name as employee_name,
                e.department,
                pp.period_start,
                pp.period_end,
                pp.pay_date,
                pp.gross_pay,
                pp.total_deductions,
                pp.total_expenses,
                pp.net_pay,
                pp.total_hours,
                pp.status,
                pp.created_at
            FROM payroll_pay_periods pp
            JOIN payroll_employees e ON pp.employee_id = e.employee_id
            WHERE {where_clause}
            ORDER BY pp.{order_by} {order_direction}
            LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        
        results = self.hook.get_records(sql, parameters=tuple(params))
        
        # Contar total
        count_sql = f"""
            SELECT COUNT(*)
            FROM payroll_pay_periods pp
            JOIN payroll_employees e ON pp.employee_id = e.employee_id
            WHERE {where_clause}
        """
        
        count_params = tuple(params[:-2])  # Excluir limit y offset
        total_result = self.hook.get_first(count_sql, parameters=count_params)
        total = total_result[0] if total_result else 0
        
        records = []
        for row in results:
            records.append({
                "id": row[0],
                "employee_id": row[1],
                "employee_name": row[2],
                "department": row[3],
                "period_start": row[4],
                "period_end": row[5],
                "pay_date": row[6],
                "gross_pay": Decimal(str(row[7])) if row[7] else Decimal("0.00"),
                "deductions": Decimal(str(row[8])) if row[8] else Decimal("0.00"),
                "expenses": Decimal(str(row[9])) if row[9] else Decimal("0.00"),
                "net_pay": Decimal(str(row[10])) if row[10] else Decimal("0.00"),
                "total_hours": Decimal(str(row[11])) if row[11] else Decimal("0.00"),
                "status": row[12],
                "created_at": row[13]
            })
        
        return {
            "records": records,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total
        }
    
    def search_expenses(
        self,
        employee_id: Optional[str] = None,
        category: Optional[str] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        approved: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Busca gastos con filtros"""
        conditions = []
        params = []
        
        if employee_id:
            conditions.append("er.employee_id = %s")
            params.append(employee_id)
        
        if category:
            conditions.append("er.category = %s")
            params.append(category)
        
        if min_amount:
            conditions.append("er.amount >= %s")
            params.append(float(min_amount))
        
        if max_amount:
            conditions.append("er.amount <= %s")
            params.append(float(max_amount))
        
        if date_from:
            conditions.append("er.expense_date >= %s")
            params.append(date_from)
        
        if date_to:
            conditions.append("er.expense_date <= %s")
            params.append(date_to)
        
        if approved is not None:
            conditions.append("er.approved = %s")
            params.append(approved)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        sql = f"""
            SELECT 
                er.id,
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
                er.reimbursed
            FROM payroll_expense_receipts er
            JOIN payroll_employees e ON er.employee_id = e.employee_id
            WHERE {where_clause}
            ORDER BY er.expense_date DESC, er.amount DESC
            LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        results = self.hook.get_records(sql, parameters=tuple(params))
        
        records = []
        for row in results:
            records.append({
                "id": row[0],
                "employee_id": row[1],
                "employee_name": row[2],
                "receipt_number": row[3],
                "expense_date": row[4],
                "amount": Decimal(str(row[5])) if row[5] else Decimal("0.00"),
                "currency": row[6],
                "category": row[7],
                "vendor": row[8],
                "description": row[9],
                "approved": row[10],
                "reimbursed": row[11]
            })
        
        return {
            "records": records,
            "limit": limit,
            "offset": offset
        }
    
    def get_statistics(
        self,
        period_start: date,
        period_end: date
    ) -> Dict[str, Any]:
        """Obtiene estadísticas agregadas para un período"""
        sql = """
            SELECT 
                COUNT(DISTINCT pp.employee_id) as employee_count,
                COUNT(*) as pay_period_count,
                SUM(pp.gross_pay) as total_gross,
                SUM(pp.total_deductions) as total_deductions,
                SUM(pp.total_expenses) as total_expenses,
                SUM(pp.net_pay) as total_net,
                SUM(pp.total_hours) as total_hours,
                AVG(pp.net_pay) as avg_net_pay,
                MIN(pp.net_pay) as min_net_pay,
                MAX(pp.net_pay) as max_net_pay
            FROM payroll_pay_periods pp
            WHERE pp.period_start >= %s AND pp.period_end <= %s
                AND pp.status IN ('calculated', 'reviewed', 'approved', 'paid')
        """
        
        result = self.hook.get_first(
            sql,
            parameters=(period_start, period_end)
        )
        
        if not result:
            return {}
        
        return {
            "employee_count": result[0] or 0,
            "pay_period_count": result[1] or 0,
            "total_gross_pay": Decimal(str(result[2] or 0)),
            "total_deductions": Decimal(str(result[3] or 0)),
            "total_expenses": Decimal(str(result[4] or 0)),
            "total_net_pay": Decimal(str(result[5] or 0)),
            "total_hours": Decimal(str(result[6] or 0)),
            "average_net_pay": Decimal(str(result[7] or 0)),
            "min_net_pay": Decimal(str(result[8] or 0)),
            "max_net_pay": Decimal(str(result[9] or 0))
        }

