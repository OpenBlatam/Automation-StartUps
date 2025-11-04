"""
Validadores de Negocio para Nómina
Validaciones específicas de reglas de negocio
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any, Tuple

from .exceptions import ValidationError
from .hour_calculator import TimeEntry

logger = logging.getLogger(__name__)


class PayrollValidator:
    """Validador de reglas de negocio"""
    
    def __init__(
        self,
        max_hours_per_day: Decimal = Decimal("16.0"),
        max_hours_per_week: Decimal = Decimal("80.0"),
        min_hourly_rate: Decimal = Decimal("7.25"),
        max_expense_per_receipt: Decimal = Decimal("10000.0"),
        max_expense_per_month: Decimal = Decimal("50000.0"),
    ):
        """
        Args:
            max_hours_per_day: Máximo de horas por día
            max_hours_per_week: Máximo de horas por semana
            min_hourly_rate: Tarifa mínima por hora (legal)
            max_expense_per_receipt: Máximo de gasto por recibo
            max_expense_per_month: Máximo de gastos por mes
        """
        self.max_hours_per_day = max_hours_per_day
        self.max_hours_per_week = max_hours_per_week
        self.min_hourly_rate = min_hourly_rate
        self.max_expense_per_receipt = max_expense_per_receipt
        self.max_expense_per_month = max_expense_per_month
    
    def validate_time_entries(
        self,
        entries: List[TimeEntry],
        period_start: date,
        period_end: date
    ) -> Tuple[bool, Optional[str], List[str]]:
        """
        Valida múltiples entradas de tiempo
        
        Returns:
            (is_valid, error_message, warnings)
        """
        warnings = []
        
        # Agrupar por fecha
        entries_by_date: Dict[date, List[TimeEntry]] = {}
        for entry in entries:
            if entry.work_date not in entries_by_date:
                entries_by_date[entry.work_date] = []
            entries_by_date[entry.work_date].append(entry)
        
        # Validar horas por día
        for work_date, day_entries in entries_by_date.items():
            total_hours = sum(e.hours_worked for e in day_entries)
            if total_hours > self.max_hours_per_day:
                return False, (
                    f"Total hours on {work_date} ({total_hours}) "
                    f"exceeds maximum ({self.max_hours_per_day})"
                ), warnings
            
            if total_hours > Decimal("12.0"):
                warnings.append(
                    f"High hours on {work_date}: {total_hours} hours"
                )
        
        # Validar horas por semana
        from collections import defaultdict
        entries_by_week: Dict[int, List[TimeEntry]] = defaultdict(list)
        
        for entry in entries:
            week_num = entry.work_date.isocalendar()[1]
            year = entry.work_date.year
            week_key = f"{year}-{week_num}"
            entries_by_week[week_key].append(entry)
        
        for week_key, week_entries in entries_by_week.items():
            total_hours = sum(e.hours_worked for e in week_entries)
            if total_hours > self.max_hours_per_week:
                return False, (
                    f"Total hours in week {week_key} ({total_hours}) "
                    f"exceeds maximum ({self.max_hours_per_week})"
                ), warnings
        
        # Validar tarifas
        for entry in entries:
            if entry.hourly_rate < self.min_hourly_rate:
                return False, (
                    f"Hourly rate ${entry.hourly_rate} for {entry.work_date} "
                    f"is below minimum (${self.min_hourly_rate})"
                ), warnings
        
        return True, None, warnings
    
    def validate_expense_amount(
        self,
        amount: Decimal,
        employee_id: str,
        expense_date: date
    ) -> Tuple[bool, Optional[str]]:
        """Valida monto de gasto"""
        if amount <= Decimal("0.00"):
            return False, "Expense amount must be positive"
        
        if amount > self.max_expense_per_receipt:
            return False, (
                f"Expense amount ${amount} exceeds maximum "
                f"(${self.max_expense_per_receipt})"
            )
        
        return True, None
    
    def validate_pay_period_dates(
        self,
        period_start: date,
        period_end: date
    ) -> Tuple[bool, Optional[str]]:
        """Valida fechas de período de pago"""
        if period_start > period_end:
            return False, "period_start must be before period_end"
        
        days_diff = (period_end - period_start).days
        if days_diff > 35:
            return False, "Pay period cannot exceed 35 days"
        
        if days_diff < 1:
            return False, "Pay period must be at least 1 day"
        
        return True, None
    
    def validate_gross_pay(
        self,
        gross_pay: Decimal,
        hours: Decimal,
        hourly_rate: Decimal
    ) -> Tuple[bool, Optional[str]]:
        """Valida que el pago bruto sea razonable"""
        expected_min = hours * hourly_rate * Decimal("0.95")  # 5% de tolerancia
        expected_max = hours * hourly_rate * Decimal("2.0")  # Hasta 2x por overtime
        
        if gross_pay < expected_min:
            return False, (
                f"Gross pay ${gross_pay} is below expected minimum "
                f"${expected_min} (hours: {hours}, rate: ${hourly_rate})"
            )
        
        if gross_pay > expected_max:
            return False, (
                f"Gross pay ${gross_pay} exceeds expected maximum "
                f"${expected_max} (hours: {hours}, rate: ${hourly_rate})"
            )
        
        return True, None
    
    def validate_deductions(
        self,
        gross_pay: Decimal,
        total_deductions: Decimal
    ) -> Tuple[bool, Optional[str]]:
        """Valida que las deducciones sean razonables"""
        if total_deductions < Decimal("0.00"):
            return False, "Deductions cannot be negative"
        
        # Deducciones no deberían exceder el 50% del pago bruto
        max_deductions = gross_pay * Decimal("0.50")
        if total_deductions > max_deductions:
            return False, (
                f"Total deductions ${total_deductions} exceed "
                f"50% of gross pay ${gross_pay}"
            )
        
        return True, None

