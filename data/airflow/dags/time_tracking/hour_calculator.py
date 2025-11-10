"""
Calculador de Horas Trabajadas Mejorado
Soporte para horarios nocturnos, días festivos, y cálculos más precisos
"""

import logging
from datetime import datetime, timedelta, date
from typing import Tuple, Optional, Dict, Any
from decimal import Decimal, ROUND_HALF_UP

from .storage import TimeTrackingStorage

logger = logging.getLogger(__name__)


class TimeTrackingHourCalculator:
    """Calcula horas trabajadas, incluyendo overtime"""
    
    # Configuración por defecto (puede ser personalizada por empleado)
    REGULAR_HOURS_PER_DAY = Decimal("8.0")
    OVERTIME_THRESHOLD = Decimal("8.0")  # Horas después de las cuales se considera overtime
    OVERTIME_MULTIPLIER = Decimal("1.5")  # 1.5x para overtime
    DOUBLE_TIME_THRESHOLD = Decimal("12.0")  # Horas después de las cuales se considera double time
    DOUBLE_TIME_MULTIPLIER = Decimal("2.0")  # 2x para double time
    
    def __init__(self, storage: TimeTrackingStorage):
        self.storage = storage
    
    def is_holiday(self, check_date: date, employee_id: Optional[str] = None) -> bool:
        """Verifica si una fecha es día festivo"""
        # Verificar en tabla de días festivos
        sql = """
            SELECT COUNT(*) FROM time_tracking_holidays
            WHERE holiday_date = %s
                AND (employee_id = %s OR employee_id IS NULL)
                AND is_active = true
        """
        
        result = self.storage.hook.get_first(
            sql,
            parameters=(check_date, employee_id)
        )
        
        return (result[0] or 0) > 0
    
    def calculate_hours(
        self,
        clock_in_time: datetime,
        clock_out_time: datetime,
        break_minutes: int = 0,
        employee_id: Optional[str] = None,
        consider_holidays: bool = True
    ) -> Tuple[Decimal, Decimal, Decimal, Decimal]:
        """
        Calcula horas trabajadas con mejoras
        
        Returns:
            Tuple de (total_hours, regular_hours, overtime_hours, double_time_hours)
        """
        if clock_out_time <= clock_in_time:
            logger.warning(f"Invalid time range: {clock_in_time} to {clock_out_time}")
            return Decimal("0.00"), Decimal("0.00"), Decimal("0.00"), Decimal("0.00")
        
        # Manejar casos donde clock_out es al día siguiente
        work_date = clock_in_time.date() if isinstance(clock_in_time, datetime) else clock_in_time
        clock_out_date = clock_out_time.date() if isinstance(clock_out_time, datetime) else clock_out_time
        
        # Calcular horas brutas
        time_diff = clock_out_time - clock_in_time
        total_minutes = time_diff.total_seconds() / 60.0
        total_minutes -= break_minutes  # Restar breaks
        
        if total_minutes < 0:
            total_minutes = 0
        
        total_hours = Decimal(str(total_minutes / 60.0)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        
        # Verificar si es día festivo
        is_holiday = False
        if consider_holidays and employee_id:
            is_holiday = self.is_holiday(work_date, employee_id)
        
        # Calcular horas regulares, overtime y double time
        if total_hours <= self.OVERTIME_THRESHOLD:
            regular_hours = total_hours
            overtime_hours = Decimal("0.00")
            double_time_hours = Decimal("0.00")
        elif total_hours <= self.DOUBLE_TIME_THRESHOLD:
            regular_hours = self.OVERTIME_THRESHOLD
            overtime_hours = total_hours - self.OVERTIME_THRESHOLD
            double_time_hours = Decimal("0.00")
        else:
            # Más de 12 horas
            regular_hours = self.OVERTIME_THRESHOLD
            overtime_up_to_double = self.DOUBLE_TIME_THRESHOLD - self.OVERTIME_THRESHOLD
            double_time_hours = total_hours - self.DOUBLE_TIME_THRESHOLD
            overtime_hours = overtime_up_to_double
        
        # Si es día festivo, todas las horas pueden tener un multiplicador especial
        # (esto se maneja en el procesamiento de nómina)
        
        return total_hours, regular_hours, overtime_hours, double_time_hours
    
    def calculate_weekly_hours(
        self,
        employee_id: str,
        week_start: datetime
    ) -> Tuple[Decimal, Decimal, Decimal]:
        """
        Calcula horas trabajadas en una semana
        
        Returns:
            Tuple de (total_hours, regular_hours, overtime_hours)
        """
        week_end = week_start + timedelta(days=7)
        
        sql = """
            SELECT 
                SUM(total_hours) as total,
                SUM(regular_hours) as regular,
                SUM(overtime_hours) as overtime
            FROM time_tracking_work_sessions
            WHERE employee_id = %s
                AND clock_in_time >= %s
                AND clock_in_time < %s
                AND status = 'closed'
        """
        
        result = self.storage.hook.get_first(
            sql,
            parameters=(employee_id, week_start, week_end)
        )
        
        if not result:
            return Decimal("0.00"), Decimal("0.00"), Decimal("0.00")
        
        return (
            Decimal(str(result[0] or 0)),
            Decimal(str(result[1] or 0)),
            Decimal(str(result[2] or 0))
        )

