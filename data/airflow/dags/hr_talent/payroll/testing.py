"""
Utilidades de Testing para Nómina
Helpers para crear datos de prueba y validaciones
"""

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional
import random

from .hour_calculator import TimeEntry, HoursType
from .payment_calculator import PayPeriodCalculation

logger = logging.getLogger(__name__)


class PayrollTestData:
    """Generador de datos de prueba para nómina"""
    
    @staticmethod
    def create_test_employee(
        employee_id: str,
        name: str = "Test Employee",
        hourly_rate: Decimal = Decimal("25.00"),
        employee_type: str = "hourly"
    ) -> Dict[str, Any]:
        """Crea un empleado de prueba"""
        return {
            "employee_id": employee_id,
            "name": name,
            "email": f"{employee_id.lower()}@example.com",
            "position": "Software Engineer",
            "hourly_rate": hourly_rate,
            "salary_monthly": None,
            "employee_type": employee_type,
            "tax_rate": Decimal("0.25"),
            "benefits_rate": Decimal("0.10"),
            "department": "Engineering",
            "start_date": date.today() - timedelta(days=365),
            "end_date": None,
            "active": True,
            "metadata": {}
        }
    
    @staticmethod
    def create_test_time_entries(
        employee_id: str,
        period_start: date,
        period_end: date,
        hours_per_day: Decimal = Decimal("8.0"),
        include_overtime: bool = False
    ) -> List[TimeEntry]:
        """Crea entradas de tiempo de prueba"""
        entries = []
        current_date = period_start
        
        while current_date <= period_end:
            # Saltar fines de semana
            if current_date.weekday() < 5:  # Lunes a Viernes
                hours = hours_per_day
                
                # Agregar overtime ocasional
                if include_overtime and random.random() > 0.7:
                    hours += Decimal("2.0")
                    entries.append(TimeEntry(
                        employee_id=employee_id,
                        work_date=current_date,
                        hours_worked=Decimal("2.0"),
                        hours_type=HoursType.OVERTIME,
                        hourly_rate=Decimal("25.00"),
                        description="Overtime work"
                    ))
                
                entries.append(TimeEntry(
                    employee_id=employee_id,
                    work_date=current_date,
                    hours_worked=hours,
                    hours_type=HoursType.REGULAR,
                    hourly_rate=Decimal("25.00"),
                    description="Regular work"
                ))
            
            current_date += timedelta(days=1)
        
        return entries
    
    @staticmethod
    def create_test_calculation(
        employee_id: str,
        period_start: date,
        period_end: date
    ) -> PayPeriodCalculation:
        """Crea un cálculo de prueba"""
        return PayPeriodCalculation(
            employee_id=employee_id,
            period_start=period_start,
            period_end=period_end,
            pay_date=period_end + timedelta(days=7),
            total_hours=Decimal("80.0"),
            regular_hours=Decimal("70.0"),
            overtime_hours=Decimal("10.0"),
            double_time_hours=Decimal("0.00"),
            gross_pay=Decimal("2000.00"),
            total_deductions=Decimal("500.00"),
            total_expenses=Decimal("100.00"),
            net_pay=Decimal("1600.00"),
            deductions_breakdown=[],
            time_entries=[]
        )
    
    @staticmethod
    def create_test_expense(
        employee_id: str,
        amount: Decimal = Decimal("50.00"),
        category: str = "meals"
    ) -> Dict[str, Any]:
        """Crea un gasto de prueba"""
        return {
            "employee_id": employee_id,
            "expense_date": date.today(),
            "amount": amount,
            "currency": "USD",
            "category": category,
            "vendor": "Test Vendor",
            "description": "Test expense",
            "approved": False,
            "reimbursed": False
        }


class PayrollTestHelpers:
    """Helpers para testing"""
    
    @staticmethod
    def assert_calculation_valid(calculation: PayPeriodCalculation) -> None:
        """Valida que un cálculo sea válido"""
        assert calculation.net_pay >= Decimal("0.00"), "Net pay cannot be negative"
        assert calculation.total_hours >= Decimal("0.00"), "Total hours cannot be negative"
        assert calculation.gross_pay >= Decimal("0.00"), "Gross pay cannot be negative"
        
        # Verificar que las horas sumen
        expected_total = (
            calculation.regular_hours +
            calculation.overtime_hours +
            calculation.double_time_hours
        )
        assert abs(calculation.total_hours - expected_total) <= Decimal("1.00"), \
            "Total hours mismatch"
        
        # Verificar que el neto sea consistente
        expected_net = (
            calculation.gross_pay -
            calculation.total_deductions +
            calculation.total_expenses
        )
        assert abs(calculation.net_pay - expected_net) <= Decimal("0.01"), \
            "Net pay calculation mismatch"
    
    @staticmethod
    def create_test_dataset(
        num_employees: int = 5,
        num_periods: int = 2
    ) -> Dict[str, Any]:
        """Crea un dataset completo de prueba"""
        employees = []
        periods = []
        
        for i in range(num_employees):
            emp_id = f"TEST_EMP_{i+1:03d}"
            employee = PayrollTestData.create_test_employee(emp_id)
            employees.append(employee)
            
            # Crear períodos
            for j in range(num_periods):
                period_start = date.today() - timedelta(days=(j+1)*14)
                period_end = period_start + timedelta(days=13)
                
                calculation = PayrollTestData.create_test_calculation(
                    emp_id, period_start, period_end
                )
                periods.append(calculation)
        
        return {
            "employees": employees,
            "periods": periods,
            "time_entries": [],
            "expenses": []
        }

