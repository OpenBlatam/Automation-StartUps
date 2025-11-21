"""
Calculadora de Pagos
Combina horas, deducciones y gastos para calcular el pago neto
"""

import logging
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List, Optional, Dict, Any

from .hour_calculator import HourCalculator, TimeEntry
from .deduction_calculator import DeductionCalculator, Deduction
from .exceptions import CalculationError, ValidationError
from .utils import log_calculation_summary

logger = logging.getLogger(__name__)


@dataclass
class PayPeriodCalculation:
    """Resultado del cálculo de período de pago"""
    employee_id: str
    period_start: date
    period_end: date
    pay_date: date
    
    # Horas
    total_hours: Decimal = Decimal("0.00")
    regular_hours: Decimal = Decimal("0.00")
    overtime_hours: Decimal = Decimal("0.00")
    double_time_hours: Decimal = Decimal("0.00")
    
    # Pagos
    gross_pay: Decimal = Decimal("0.00")
    total_deductions: Decimal = Decimal("0.00")
    total_expenses: Decimal = Decimal("0.00")
    net_pay: Decimal = Decimal("0.00")
    
    # Detalles
    deductions_breakdown: List[Deduction] = None
    time_entries: List[TimeEntry] = None
    
    def __post_init__(self):
        if self.deductions_breakdown is None:
            self.deductions_breakdown = []
        if self.time_entries is None:
            self.time_entries = []


class PaymentCalculator:
    """Calculadora de pagos completo"""
    
    def __init__(
        self,
        hour_calculator: HourCalculator,
        deduction_calculator: DeductionCalculator,
    ):
        """
        Args:
            hour_calculator: Calculadora de horas
            deduction_calculator: Calculadora de deducciones
        """
        self.hour_calculator = hour_calculator
        self.deduction_calculator = deduction_calculator
    
    def calculate_pay_period(
        self,
        employee_id: str,
        hourly_rate: Decimal,
        employee_type: str,
        period_start: date,
        period_end: date,
        pay_date: date,
        time_entries: List[TimeEntry],
        expenses_total: Decimal = Decimal("0.00"),
        employee_context: Optional[Dict[str, Any]] = None
    ) -> PayPeriodCalculation:
        """
        Calcula el pago completo para un período
        
        Args:
            employee_id: ID del empleado
            hourly_rate: Tarifa por hora
            employee_type: Tipo de empleado (hourly, salaried, contractor)
            period_start: Inicio del período
            period_end: Fin del período
            pay_date: Fecha de pago
            time_entries: Entradas de tiempo trabajadas
            expenses_total: Total de gastos reembolsables
            employee_context: Contexto adicional del empleado
        """
        # Validar entradas de tiempo
        for entry in time_entries:
            is_valid, error = self.hour_calculator.validate_time_entry(entry)
            if not is_valid:
                raise ValidationError(
                    f"Invalid time entry for {employee_id} on {entry.work_date}: {error}",
                    employee_id=employee_id,
                    context={"entry": str(entry), "error": error}
                )
        
        # Calcular horas
        hours_breakdown = self.hour_calculator.calculate_overtime(
            time_entries, period_start, period_end
        )
        total_hours = self.hour_calculator.calculate_total_hours(time_entries)
        
        # Calcular pago bruto
        gross_pay = self.hour_calculator.calculate_gross_pay(
            time_entries, hourly_rate, period_start, period_end
        )
        
        # Si es salario fijo, usar el salario mensual en lugar de horas
        if employee_type == "salaried" and employee_context:
            monthly_salary = employee_context.get("monthly_salary")
            if monthly_salary:
                # Calcular proporcional según días del período
                days_in_period = (period_end - period_start).days + 1
                days_in_month = 30  # Simplificado
                gross_pay = Decimal(str(monthly_salary)) * Decimal(str(days_in_period)) / Decimal(str(days_in_month))
        
        # Calcular deducciones
        deductions = self.deduction_calculator.calculate_deductions(
            gross_pay,
            employee_type,
            employee_id,
            employee_context
        )
        total_deductions = sum(d.amount for d in deductions)
        
        # Calcular pago neto
        # Neto = Bruto - Deducciones + Gastos reembolsables
        net_pay = gross_pay - total_deductions + expenses_total
        
        calculation = PayPeriodCalculation(
            employee_id=employee_id,
            period_start=period_start,
            period_end=period_end,
            pay_date=pay_date,
            total_hours=total_hours,
            regular_hours=hours_breakdown["regular_hours"],
            overtime_hours=hours_breakdown["overtime_hours"],
            double_time_hours=hours_breakdown["double_time_hours"],
            gross_pay=gross_pay,
            total_deductions=total_deductions,
            total_expenses=expenses_total,
            net_pay=net_pay.quantize(Decimal("0.01")),
            deductions_breakdown=deductions,
            time_entries=time_entries
        )
        
        # Log resumen
        log_calculation_summary(employee_id, calculation)
        
        return calculation
    
    def validate_calculation(self, calculation: PayPeriodCalculation) -> tuple[bool, Optional[str]]:
        """Valida un cálculo de pago"""
        errors = []
        
        if calculation.net_pay < Decimal("0.00"):
            errors.append("net_pay cannot be negative")
        
        if calculation.total_hours < Decimal("0.00"):
            errors.append("total_hours cannot be negative")
        
        if calculation.gross_pay < Decimal("0.00"):
            errors.append("gross_pay cannot be negative")
        
        # Verificar que las horas sumen correctamente
        expected_total = (
            calculation.regular_hours +
            calculation.overtime_hours +
            calculation.double_time_hours
        )
        if abs(calculation.total_hours - expected_total) > Decimal("1.00"):
            errors.append(
                f"total_hours ({calculation.total_hours}) doesn't match breakdown ({expected_total})"
            )
        
        # Verificar que el neto sea consistente
        expected_net = (
            calculation.gross_pay -
            calculation.total_deductions +
            calculation.total_expenses
        )
        if abs(calculation.net_pay - expected_net) > Decimal("0.01"):
            errors.append(
                f"net_pay ({calculation.net_pay}) doesn't match calculation ({expected_net})"
            )
        
        if errors:
            return False, "; ".join(errors)
        
        return True, None

