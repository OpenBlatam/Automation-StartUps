"""
Utilidades para el módulo de nómina
"""

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any, List, Callable
from functools import wraps
import time

logger = logging.getLogger(__name__)


def get_pay_period_dates(
    reference_date: Optional[date] = None,
    period_type: str = "biweekly"
) -> tuple[date, date]:
    """
    Calcula las fechas de un período de pago
    
    Args:
        reference_date: Fecha de referencia (default: hoy)
        period_type: Tipo de período (biweekly, monthly, weekly)
    
    Returns:
        Tupla (period_start, period_end)
    """
    if reference_date is None:
        reference_date = date.today()
    
    if period_type == "biweekly":
        # Período de 2 semanas (14 días)
        # Buscar el lunes de hace 2 semanas
        days_since_monday = (reference_date.weekday() + 14) % 7
        period_end = reference_date - timedelta(days=days_since_monday)
        period_start = period_end - timedelta(days=13)
        period_end = period_end - timedelta(days=7)
    
    elif period_type == "monthly":
        # Período del mes anterior
        first_day_current = reference_date.replace(day=1)
        period_end = first_day_current - timedelta(days=1)
        period_start = period_end.replace(day=1)
    
    elif period_type == "weekly":
        # Semana anterior
        days_since_monday = reference_date.weekday()
        period_end = reference_date - timedelta(days=days_since_monday + 7)
        period_start = period_end - timedelta(days=6)
    
    else:
        raise ValueError(f"Unsupported period_type: {period_type}")
    
    return period_start, period_end


def format_currency(amount: Decimal, currency: str = "USD") -> str:
    """Formatea un monto como moneda"""
    if currency == "USD":
        return f"${amount:,.2f}"
    return f"{amount:,.2f} {currency}"


def format_hours(hours: Decimal) -> str:
    """Formatea horas trabajadas"""
    hours_int = int(hours)
    minutes = int((hours - hours_int) * 60)
    return f"{hours_int}h {minutes}m"


def validate_date_range(start_date: date, end_date: date) -> tuple[bool, Optional[str]]:
    """Valida un rango de fechas"""
    if start_date > end_date:
        return False, "start_date cannot be after end_date"
    
    if (end_date - start_date).days > 90:
        return False, "Date range cannot exceed 90 days"
    
    return True, None


def retry_on_failure(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorador para reintentar operaciones fallidas
    
    Args:
        max_attempts: Número máximo de intentos
        delay: Delay inicial en segundos
        backoff: Factor de backoff exponencial
        exceptions: Tupla de excepciones a capturar
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"Attempt {attempt} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator


def safe_decimal(value: Any, default: Decimal = Decimal("0.00")) -> Decimal:
    """Convierte un valor a Decimal de forma segura"""
    if value is None:
        return default
    
    if isinstance(value, Decimal):
        return value
    
    try:
        return Decimal(str(value))
    except (ValueError, TypeError):
        logger.warning(f"Could not convert {value} to Decimal, using default {default}")
        return default


def calculate_percentage(part: Decimal, total: Decimal) -> Decimal:
    """Calcula porcentaje de forma segura"""
    if total == Decimal("0.00"):
        return Decimal("0.00")
    return (part / total * 100).quantize(Decimal("0.01"))


def group_by_date_range(
    dates: List[date],
    start_date: date,
    end_date: date
) -> Dict[str, List[date]]:
    """Agrupa fechas por rango"""
    result = {}
    current = start_date
    
    while current <= end_date:
        week_start = current
        week_end = min(current + timedelta(days=6), end_date)
        key = f"{week_start} to {week_end}"
        result[key] = [
            d for d in dates
            if week_start <= d <= week_end
        ]
        current = week_end + timedelta(days=1)
    
    return result


def log_calculation_summary(
    employee_id: str,
    calculation: Any,
    level: int = logging.INFO
) -> None:
    """Log un resumen de cálculo de nómina"""
    summary = (
        f"Payroll calculation for {employee_id}:\n"
        f"  Hours: {calculation.total_hours} "
        f"(regular: {calculation.regular_hours}, "
        f"overtime: {calculation.overtime_hours})\n"
        f"  Gross Pay: ${calculation.gross_pay}\n"
        f"  Deductions: ${calculation.total_deductions}\n"
        f"  Expenses: ${calculation.total_expenses}\n"
        f"  Net Pay: ${calculation.net_pay}"
    )
    logger.log(level, summary)


def calculate_yearly_total(
    period_amount: Decimal,
    periods_per_year: int = 26  # Biweekly
) -> Decimal:
    """Calcula total anual proyectado desde un período"""
    return (period_amount * Decimal(str(periods_per_year))).quantize(Decimal("0.01"))


def calculate_pay_period_number(
    start_date: date,
    reference_date: Optional[date] = None
) -> int:
    """Calcula el número de período desde una fecha de referencia"""
    if reference_date is None:
        reference_date = date(2025, 1, 1)  # Fecha de inicio del sistema
    
    days_diff = (start_date - reference_date).days
    period_number = (days_diff // 14) + 1  # Biweekly periods
    
    return max(1, period_number)


def format_period_range(
    start_date: date,
    end_date: date,
    format_type: str = "short"
) -> str:
    """Formatea rango de fechas de período"""
    if format_type == "short":
        return f"{start_date.strftime('%m/%d')}-{end_date.strftime('%m/%d/%Y')}"
    elif format_type == "long":
        return f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
    else:
        return f"{start_date} to {end_date}"


def calculate_deduction_rate(
    gross_pay: Decimal,
    deductions: Decimal
) -> Decimal:
    """Calcula tasa de deducción como porcentaje"""
    if gross_pay == Decimal("0.00"):
        return Decimal("0.00")
    return (deductions / gross_pay * 100).quantize(Decimal("0.01"))


def is_business_day(check_date: date) -> bool:
    """Verifica si una fecha es día hábil (lunes a viernes)"""
    return check_date.weekday() < 5  # 0-4 = Monday-Friday


def get_business_days_between(start_date: date, end_date: date) -> int:
    """Calcula días hábiles entre dos fechas"""
    business_days = 0
    current = start_date
    
    while current <= end_date:
        if is_business_day(current):
            business_days += 1
        current += timedelta(days=1)
    
    return business_days


def calculate_effective_hourly_rate(
    gross_pay: Decimal,
    total_hours: Decimal
) -> Decimal:
    """Calcula tarifa efectiva por hora"""
    if total_hours == Decimal("0.00"):
        return Decimal("0.00")
    return (gross_pay / total_hours).quantize(Decimal("0.01"))


def round_to_nearest_cent(amount: Decimal) -> Decimal:
    """Redondea a centavo más cercano"""
    return amount.quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")


def calculate_overtime_premium(
    overtime_hours: Decimal,
    hourly_rate: Decimal,
    overtime_multiplier: Decimal = Decimal("1.5")
) -> Decimal:
    """Calcula el premium de overtime (diferencia entre overtime y regular)"""
    regular_pay = overtime_hours * hourly_rate
    overtime_pay = overtime_hours * hourly_rate * overtime_multiplier
    premium = overtime_pay - regular_pay
    return premium.quantize(Decimal("0.01"))

