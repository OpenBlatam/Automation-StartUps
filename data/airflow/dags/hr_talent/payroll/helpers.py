"""
Helpers Adicionales para Nómina
Funciones de utilidad y helpers avanzados
"""

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional, List, Tuple
import re

logger = logging.getLogger(__name__)


class PayrollHelpers:
    """Helpers adicionales para nómina"""
    
    @staticmethod
    def parse_employee_id(employee_id: str) -> Dict[str, Any]:
        """Parsea un employee ID y extrae información"""
        # Ejemplos: EMP001, EMP-001, 001
        match = re.match(r'([A-Z]+)[-]?(\d+)', employee_id.upper())
        
        if match:
            prefix = match.group(1)
            number = int(match.group(2))
            return {
                "prefix": prefix,
                "number": number,
                "formatted": f"{prefix}{number:03d}"
            }
        
        return {
            "prefix": None,
            "number": None,
            "formatted": employee_id
        }
    
    @staticmethod
    def calculate_pay_period_number(
        start_date: date,
        reference_date: Optional[date] = None
    ) -> int:
        """Calcula el número de período de pago desde una fecha de referencia"""
        if reference_date is None:
            reference_date = date(2025, 1, 1)  # Fecha de inicio del sistema
        
        # Calcular días transcurridos
        days_diff = (start_date - reference_date).days
        
        # Calcular número de período (biweekly = cada 14 días)
        period_number = (days_diff // 14) + 1
        
        return period_number
    
    @staticmethod
    def format_employee_name(
        first_name: str,
        last_name: str,
        format: str = "full"
    ) -> str:
        """Formatea nombre de empleado"""
        if format == "full":
            return f"{first_name} {last_name}"
        elif format == "last_first":
            return f"{last_name}, {first_name}"
        elif format == "initial":
            return f"{first_name[0]}. {last_name}" if first_name else last_name
        else:
            return f"{first_name} {last_name}"
    
    @staticmethod
    def calculate_yearly_projection(
        current_period_amount: Decimal,
        periods_per_year: int = 26  # Biweekly
    ) -> Decimal:
        """Proyecta monto anual basado en período actual"""
        return current_period_amount * Decimal(str(periods_per_year))
    
    @staticmethod
    def calculate_tax_bracket(
        gross_pay: Decimal,
        brackets: List[Tuple[Decimal, Decimal]] = None
    ) -> Tuple[Decimal, Decimal]:
        """
        Calcula bracket de impuestos
        
        Returns:
            (taxable_amount, tax_rate)
        """
        if brackets is None:
            # Brackets por defecto (federal US)
            brackets = [
                (Decimal("0"), Decimal("0.10")),
                (Decimal("11000"), Decimal("0.12")),
                (Decimal("44725"), Decimal("0.22")),
                (Decimal("95375"), Decimal("0.24")),
                (Decimal("201050"), Decimal("0.32")),
                (Decimal("578125"), Decimal("0.35")),
                (Decimal("578125"), Decimal("0.37"))
            ]
        
        # Encontrar bracket apropiado
        for threshold, rate in reversed(brackets):
            if gross_pay >= threshold:
                return (gross_pay - threshold, rate)
        
        return (gross_pay, brackets[0][1])
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Valida formato de teléfono"""
        # Remover caracteres especiales
        digits = re.sub(r'[^\d]', '', phone)
        # Validar que tenga 10 dígitos (US)
        return len(digits) == 10
    
    @staticmethod
    def calculate_benefits_cost(
        base_salary: Decimal,
        benefits_rate: Decimal
    ) -> Decimal:
        """Calcula costo de beneficios"""
        return base_salary * benefits_rate
    
    @staticmethod
    def estimate_monthly_from_hourly(
        hourly_rate: Decimal,
        hours_per_week: Decimal = Decimal("40.0")
    ) -> Decimal:
        """Estima salario mensual desde tarifa por hora"""
        weekly = hourly_rate * hours_per_week
        monthly = weekly * Decimal("52.0") / Decimal("12.0")
        return monthly.quantize(Decimal("0.01"))
    
    @staticmethod
    def estimate_hourly_from_monthly(
        monthly_salary: Decimal,
        hours_per_week: Decimal = Decimal("40.0")
    ) -> Decimal:
        """Estima tarifa por hora desde salario mensual"""
        weekly = monthly_salary * Decimal("12.0") / Decimal("52.0")
        hourly = weekly / hours_per_week
        return hourly.quantize(Decimal("0.01"))
    
    @staticmethod
    def calculate_pay_increase_percentage(
        old_pay: Decimal,
        new_pay: Decimal
    ) -> Decimal:
        """Calcula porcentaje de aumento de pago"""
        if old_pay == Decimal("0"):
            return Decimal("0.00")
        
        increase = ((new_pay - old_pay) / old_pay) * Decimal("100")
        return increase.quantize(Decimal("0.01"))
    
    @staticmethod
    def format_pay_period_range(
        start_date: date,
        end_date: date,
        format: str = "short"
    ) -> str:
        """Formatea rango de período de pago"""
        if format == "short":
            return f"{start_date.strftime('%m/%d')}-{end_date.strftime('%m/%d/%Y')}"
        elif format == "long":
            return f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
        else:
            return f"{start_date} to {end_date}"
    
    @staticmethod
    def group_by_department(
        employees: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Agrupa empleados por departamento"""
        grouped = {}
        
        for employee in employees:
            dept = employee.get("department", "Unknown")
            if dept not in grouped:
                grouped[dept] = []
            grouped[dept].append(employee)
        
        return grouped
    
    @staticmethod
    def calculate_employee_tenure(
        start_date: date,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Calcula antigüedad de empleado"""
        if end_date is None:
            end_date = date.today()
        
        delta = end_date - start_date
        years = delta.days / 365.25
        months = (delta.days % 365.25) / 30.44
        days = delta.days
        
        return {
            "total_days": days,
            "years": int(years),
            "months": int(months),
            "formatted": f"{int(years)} years, {int(months)} months"
        }

