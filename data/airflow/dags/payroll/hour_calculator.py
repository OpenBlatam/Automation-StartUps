"""
Calculadora de Horas Trabajadas
Maneja el cálculo de horas regulares, horas extra, y diferentes tipos de horas
"""

import logging
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any
from enum import Enum

from .exceptions import ValidationError, CalculationError

logger = logging.getLogger(__name__)


class HoursType(str, Enum):
    """Tipos de horas trabajadas"""
    REGULAR = "regular"
    OVERTIME = "overtime"
    DOUBLE_TIME = "double_time"
    HOLIDAY = "holiday"
    SICK = "sick"
    VACATION = "vacation"
    OTHER = "other"


@dataclass
class TimeEntry:
    """Entrada de tiempo trabajado"""
    employee_id: str
    work_date: date
    clock_in: Optional[datetime] = None
    clock_out: Optional[datetime] = None
    hours_worked: Decimal = Decimal("0.00")
    hours_type: HoursType = HoursType.REGULAR
    hourly_rate: Decimal = Decimal("0.00")
    description: Optional[str] = None
    project_code: Optional[str] = None


class HourCalculator:
    """Calculadora de horas trabajadas"""
    
    def __init__(
        self,
        regular_hours_per_week: Decimal = Decimal("40.0"),
        overtime_multiplier: Decimal = Decimal("1.5"),
        double_time_multiplier: Decimal = Decimal("2.0"),
    ):
        """
        Args:
            regular_hours_per_week: Horas regulares por semana antes de overtime
            overtime_multiplier: Multiplicador para horas extra (default: 1.5x)
            double_time_multiplier: Multiplicador para double time (default: 2.0x)
        """
        self.regular_hours_per_week = regular_hours_per_week
        self.overtime_multiplier = overtime_multiplier
        self.double_time_multiplier = double_time_multiplier
    
    def calculate_hours_from_timestamps(
        self,
        clock_in: datetime,
        clock_out: datetime
    ) -> Decimal:
        """Calcula horas trabajadas desde timestamps"""
        if clock_in >= clock_out:
            raise ValidationError(
                f"clock_in ({clock_in}) must be before clock_out ({clock_out})",
                context={"clock_in": str(clock_in), "clock_out": str(clock_out)}
            )
        
        # Verificar que no exceda 24 horas
        delta = clock_out - clock_in
        hours = Decimal(str(delta.total_seconds() / 3600.0))
        
        if hours > Decimal("24.0"):
            raise ValidationError(
                f"Time entry exceeds 24 hours: {hours}",
                context={"hours": str(hours), "clock_in": str(clock_in), "clock_out": str(clock_out)}
            )
        
        return hours.quantize(Decimal("0.01"))
    
    def calculate_overtime(
        self,
        time_entries: List[TimeEntry],
        period_start: date,
        period_end: date
    ) -> Dict[str, Decimal]:
        """
        Calcula horas regulares y overtime para un período
        
        Returns:
            Dict con 'regular_hours', 'overtime_hours', 'double_time_hours'
        """
        # Calcular horas por semana
        weeks = self._get_weeks_in_period(period_start, period_end)
        
        # Agrupar horas por semana
        hours_by_week: Dict[int, Decimal] = {}
        
        current_date = period_start
        while current_date <= period_end:
            week_num = current_date.isocalendar()[1]
            year = current_date.year
            
            # Si cambiamos de año, usar año-semana como clave
            week_key = f"{year}-{week_num}"
            
            for entry in time_entries:
                if entry.work_date == current_date and entry.hours_type == HoursType.REGULAR:
                    if week_key not in hours_by_week:
                        hours_by_week[week_key] = Decimal("0.00")
                    hours_by_week[week_key] += entry.hours_worked
            
            current_date += timedelta(days=1)
        
        # Calcular overtime
        total_regular = Decimal("0.00")
        total_overtime = Decimal("0.00")
        total_double_time = Decimal("0.00")
        
        for week_key, week_hours in hours_by_week.items():
            if week_hours <= self.regular_hours_per_week:
                total_regular += week_hours
            else:
                # Horas regulares hasta el límite
                total_regular += self.regular_hours_per_week
                
                # Horas extra
                overtime_hours = week_hours - self.regular_hours_per_week
                
                # Si hay más de 8 horas extra en un día, algunas son double time
                # Por simplicidad, asumimos que después de 48 horas semanales es double time
                if week_hours > Decimal("48.0"):
                    double_time_hours = week_hours - Decimal("48.0")
                    regular_overtime = Decimal("48.0") - self.regular_hours_per_week
                    total_overtime += regular_overtime
                    total_double_time += double_time_hours
                else:
                    total_overtime += overtime_hours
        
        # Sumar horas de tipos específicos que ya están marcadas como overtime/double_time
        for entry in time_entries:
            if entry.hours_type == HoursType.OVERTIME:
                total_overtime += entry.hours_worked
            elif entry.hours_type == HoursType.DOUBLE_TIME:
                total_double_time += entry.hours_worked
            elif entry.hours_type in [HoursType.HOLIDAY, HoursType.SICK, HoursType.VACATION]:
                # Estas no cuentan para overtime
                pass
        
        return {
            "regular_hours": total_regular.quantize(Decimal("0.01")),
            "overtime_hours": total_overtime.quantize(Decimal("0.01")),
            "double_time_hours": total_double_time.quantize(Decimal("0.01")),
        }
    
    def calculate_total_hours(
        self,
        time_entries: List[TimeEntry]
    ) -> Decimal:
        """Calcula el total de horas trabajadas"""
        total = Decimal("0.00")
        for entry in time_entries:
            total += entry.hours_worked
        return total.quantize(Decimal("0.01"))
    
    def calculate_gross_pay(
        self,
        time_entries: List[TimeEntry],
        hourly_rate: Decimal,
        period_start: date,
        period_end: date
    ) -> Decimal:
        """
        Calcula pago bruto basado en horas trabajadas
        
        Args:
            time_entries: Lista de entradas de tiempo
            hourly_rate: Tarifa por hora
            period_start: Inicio del período
            period_end: Fin del período
        """
        hours_breakdown = self.calculate_overtime(time_entries, period_start, period_end)
        
        regular_pay = hours_breakdown["regular_hours"] * hourly_rate
        overtime_pay = hours_breakdown["overtime_hours"] * hourly_rate * self.overtime_multiplier
        double_time_pay = hours_breakdown["double_time_hours"] * hourly_rate * self.double_time_multiplier
        
        # Agregar horas especiales (holiday, etc.) que pueden tener diferentes tasas
        special_hours_pay = Decimal("0.00")
        for entry in time_entries:
            if entry.hours_type == HoursType.HOLIDAY:
                # Holiday generalmente se paga a tasa premium
                special_hours_pay += entry.hours_worked * hourly_rate * Decimal("2.0")
            elif entry.hours_type in [HoursType.SICK, HoursType.VACATION]:
                # Pueden tener tasa diferente o no pagarse
                special_hours_pay += entry.hours_worked * hourly_rate
        
        total = regular_pay + overtime_pay + double_time_pay + special_hours_pay
        return total.quantize(Decimal("0.01"))
    
    def validate_time_entry(self, entry: TimeEntry) -> tuple[bool, Optional[str]]:
        """Valida una entrada de tiempo"""
        if entry.hours_worked < Decimal("0.00"):
            return False, "hours_worked cannot be negative"
        
        if entry.hours_worked > Decimal("24.0"):
            return False, "hours_worked cannot exceed 24 hours per day"
        
        if entry.clock_in and entry.clock_out:
            calculated_hours = self.calculate_hours_from_timestamps(
                entry.clock_in, entry.clock_out
            )
            if abs(calculated_hours - entry.hours_worked) > Decimal("0.1"):
                return False, f"hours_worked ({entry.hours_worked}) doesn't match timestamps ({calculated_hours})"
        
        return True, None
    
    def _get_weeks_in_period(self, period_start: date, period_end: date) -> int:
        """Calcula número de semanas en un período"""
        delta = period_end - period_start
        weeks = (delta.days // 7) + 1
        return weeks

