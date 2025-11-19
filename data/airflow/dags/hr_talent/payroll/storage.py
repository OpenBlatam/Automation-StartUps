"""
Módulo de Almacenamiento para Nómina
Maneja la persistencia de datos en PostgreSQL
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
import json

from airflow.providers.postgres.hooks.postgres import PostgresHook

from .hour_calculator import TimeEntry, HoursType
from .payment_calculator import PayPeriodCalculation
from .deduction_calculator import Deduction
from .ocr_processor import OCRResult
from .exceptions import StorageError, EmployeeNotFoundError
from .utils import retry_on_failure
from .cache import cached, PayrollCache

logger = logging.getLogger(__name__)


class PayrollStorage:
    """Almacenador de datos de nómina"""
    
    def __init__(
        self,
        postgres_conn_id: str = "postgres_default",
        cache: Optional[PayrollCache] = None
    ):
        """
        Args:
            postgres_conn_id: ID de conexión de Airflow para PostgreSQL
            cache: Instancia de caché (opcional)
        """
        self.postgres_conn_id = postgres_conn_id
        self._hook: Optional[PostgresHook] = None
        self.cache = cache or PayrollCache(enabled=True, ttl_seconds=1800)
    
    @property
    def hook(self) -> PostgresHook:
        """Obtiene el hook de PostgreSQL (lazy initialization)"""
        if self._hook is None:
            self._hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        return self._hook
    
    def ensure_schema(self) -> bool:
        """Verifica/crea el schema de nómina"""
        try:
            # Verificar si la tabla existe
            check_sql = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'payroll_employees'
                );
            """
            result = self.hook.get_first(check_sql)
            if result and result[0]:
                logger.info("Payroll schema already exists")
                return True
            
            # Si no existe, intentar crear
            logger.warning("Payroll schema not found. Please run payroll_schema.sql manually")
            return False
        except Exception as e:
            logger.error(f"Error checking schema: {e}")
            return False
    
    # ==================== Employees ====================
    
    @retry_on_failure(max_attempts=3, delay=1.0)
    @cached(key_prefix="employee", ttl_seconds=3600)
    def get_employee(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un empleado por ID"""
        sql = """
            SELECT 
                id, employee_id, name, email, position,
                hourly_rate, salary_monthly, employee_type,
                tax_rate, benefits_rate, department,
                start_date, end_date, active, metadata
            FROM payroll_employees
            WHERE employee_id = %s AND active = true
        """
        
        try:
            result = self.hook.get_first(sql, parameters=(employee_id,))
            if not result:
                return None
        except Exception as e:
            raise StorageError(
                f"Error fetching employee {employee_id}: {e}",
                employee_id=employee_id,
                context={"operation": "get_employee"}
            ) from e
        
        return {
            "id": result[0],
            "employee_id": result[1],
            "name": result[2],
            "email": result[3],
            "position": result[4],
            "hourly_rate": Decimal(str(result[5])) if result[5] else None,
            "salary_monthly": Decimal(str(result[6])) if result[6] else None,
            "employee_type": result[7],
            "tax_rate": Decimal(str(result[8])) if result[8] else Decimal("0.00"),
            "benefits_rate": Decimal(str(result[9])) if result[9] else Decimal("0.00"),
            "department": result[10],
            "start_date": result[11],
            "end_date": result[12],
            "active": result[13],
            "metadata": result[14] if isinstance(result[14], dict) else json.loads(result[14]) if result[14] else {}
        }
    
    def list_active_employees(self) -> List[Dict[str, Any]]:
        """Lista todos los empleados activos"""
        sql = """
            SELECT employee_id
            FROM payroll_employees
            WHERE active = true
            ORDER BY employee_id
        """
        
        results = self.hook.get_records(sql)
        employees = []
        for row in results:
            employee = self.get_employee(row[0])
            if employee:
                employees.append(employee)
        return employees
    
    # ==================== Time Entries ====================
    
    def save_time_entry(self, entry: TimeEntry) -> int:
        """Guarda una entrada de tiempo"""
        sql = """
            INSERT INTO payroll_time_entries (
                employee_id, work_date, clock_in, clock_out,
                hours_worked, hours_type, hourly_rate,
                description, project_code
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (employee_id, work_date, hours_type)
            DO UPDATE SET
                clock_in = EXCLUDED.clock_in,
                clock_out = EXCLUDED.clock_out,
                hours_worked = EXCLUDED.hours_worked,
                hourly_rate = EXCLUDED.hourly_rate,
                description = EXCLUDED.description,
                project_code = EXCLUDED.project_code,
                updated_at = NOW()
            RETURNING id
        """
        
        result = self.hook.get_first(
            sql,
            parameters=(
                entry.employee_id,
                entry.work_date,
                entry.clock_in,
                entry.clock_out,
                float(entry.hours_worked),
                entry.hours_type.value,
                float(entry.hourly_rate),
                entry.description,
                entry.project_code
            )
        )
        
        return result[0] if result else 0
    
    def get_time_entries(
        self,
        employee_id: str,
        period_start: date,
        period_end: date
    ) -> List[TimeEntry]:
        """Obtiene entradas de tiempo para un período"""
        sql = """
            SELECT 
                employee_id, work_date, clock_in, clock_out,
                hours_worked, hours_type, hourly_rate,
                description, project_code
            FROM payroll_time_entries
            WHERE employee_id = %s
                AND work_date >= %s
                AND work_date <= %s
            ORDER BY work_date, hours_type
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(employee_id, period_start, period_end)
        )
        
        entries = []
        for row in results:
            entries.append(TimeEntry(
                employee_id=row[0],
                work_date=row[1],
                clock_in=row[2],
                clock_out=row[3],
                hours_worked=Decimal(str(row[4])),
                hours_type=HoursType(row[5]),
                hourly_rate=Decimal(str(row[6])),
                description=row[7],
                project_code=row[8]
            ))
        
        return entries
    
    def approve_time_entry(self, entry_id: int, approved_by: str) -> bool:
        """Aprueba una entrada de tiempo"""
        sql = """
            UPDATE payroll_time_entries
            SET approved = true,
                approved_by = %s,
                approved_at = NOW()
            WHERE id = %s
        """
        
        try:
            self.hook.run(sql, parameters=(approved_by, entry_id))
            return True
        except Exception as e:
            logger.error(f"Error approving time entry {entry_id}: {e}")
            return False
    
    # ==================== Expense Receipts ====================
    
    def save_expense_receipt(
        self,
        employee_id: str,
        expense_date: date,
        amount: Decimal,
        ocr_result: Optional[OCRResult] = None,
        receipt_image_base64: Optional[str] = None,
        **kwargs
    ) -> int:
        """Guarda un recibo de gasto"""
        sql = """
            INSERT INTO payroll_expense_receipts (
                employee_id, expense_date, amount, currency,
                category, vendor, description,
                receipt_image_base64,
                ocr_status, ocr_confidence, ocr_extracted_data, ocr_processed_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id
        """
        
        ocr_status = "completed" if ocr_result and ocr_result.success else "pending"
        ocr_confidence = float(ocr_result.confidence) if ocr_result and ocr_result.success else None
        ocr_extracted_data = ocr_result.extracted_data if ocr_result and ocr_result.success else None
        ocr_processed_at = datetime.now() if ocr_result and ocr_result.success else None
        
        # Extraer datos de OCR si está disponible
        vendor = kwargs.get("vendor") or (ocr_extracted_data.get("vendor") if ocr_extracted_data else None)
        description = kwargs.get("description") or (ocr_extracted_data.get("total") if ocr_extracted_data else None)
        category = kwargs.get("category")
        
        result = self.hook.get_first(
            sql,
            parameters=(
                employee_id,
                expense_date,
                float(amount),
                kwargs.get("currency", "USD"),
                category,
                vendor,
                description,
                receipt_image_base64,
                ocr_status,
                ocr_confidence,
                json.dumps(ocr_extracted_data) if ocr_extracted_data else None,
                ocr_processed_at
            )
        )
        
        return result[0] if result else 0
    
    def get_expenses_total(
        self,
        employee_id: str,
        period_start: date,
        period_end: date
    ) -> Decimal:
        """Calcula el total de gastos aprobados para un período"""
        sql = """
            SELECT COALESCE(SUM(amount), 0)
            FROM payroll_expense_receipts
            WHERE employee_id = %s
                AND expense_date >= %s
                AND expense_date <= %s
                AND approved = true
        """
        
        result = self.hook.get_first(
            sql,
            parameters=(employee_id, period_start, period_end)
        )
        
        return Decimal(str(result[0])) if result and result[0] else Decimal("0.00")
    
    def approve_expense_receipt(self, receipt_id: int, approved_by: str) -> bool:
        """Aprueba un recibo de gasto"""
        sql = """
            UPDATE payroll_expense_receipts
            SET approved = true,
                approved_by = %s,
                approved_at = NOW()
            WHERE id = %s
        """
        
        try:
            self.hook.run(sql, parameters=(approved_by, receipt_id))
            return True
        except Exception as e:
            logger.error(f"Error approving expense receipt {receipt_id}: {e}")
            return False
    
    # ==================== Pay Periods ====================
    
    def save_pay_period(self, calculation: PayPeriodCalculation) -> int:
        """Guarda un período de pago"""
        sql = """
            INSERT INTO payroll_pay_periods (
                employee_id, period_start, period_end, pay_date,
                gross_pay, total_hours, regular_hours, overtime_hours,
                total_deductions, total_expenses, net_pay,
                status
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (employee_id, period_start, period_end)
            DO UPDATE SET
                gross_pay = EXCLUDED.gross_pay,
                total_hours = EXCLUDED.total_hours,
                regular_hours = EXCLUDED.regular_hours,
                overtime_hours = EXCLUDED.overtime_hours,
                total_deductions = EXCLUDED.total_deductions,
                total_expenses = EXCLUDED.total_expenses,
                net_pay = EXCLUDED.net_pay,
                status = EXCLUDED.status,
                calculated_at = NOW(),
                updated_at = NOW()
            RETURNING id
        """
        
        result = self.hook.get_first(
            sql,
            parameters=(
                calculation.employee_id,
                calculation.period_start,
                calculation.period_end,
                calculation.pay_date,
                float(calculation.gross_pay),
                float(calculation.total_hours),
                float(calculation.regular_hours),
                float(calculation.overtime_hours),
                float(calculation.total_deductions),
                float(calculation.total_expenses),
                float(calculation.net_pay),
                "calculated"
            )
        )
        
        pay_period_id = result[0] if result else 0
        
        # Guardar detalles de deducciones
        if pay_period_id > 0:
            self._save_deduction_details(pay_period_id, calculation)
        
        return pay_period_id
    
    def _save_deduction_details(
        self,
        pay_period_id: int,
        calculation: PayPeriodCalculation
    ) -> None:
        """Guarda detalles de deducciones"""
        sql = """
            INSERT INTO payroll_pay_calculations (
                pay_period_id, employee_id, calculation_type,
                description, amount
            ) VALUES (%s, %s, %s, %s, %s)
        """
        
        # Guardar cada deducción
        for deduction in calculation.deductions_breakdown:
            self.hook.run(
                sql,
                parameters=(
                    pay_period_id,
                    calculation.employee_id,
                    "deduction",
                    deduction.description,
                    float(deduction.amount)
                )
            )

