"""
Utilidades Avanzadas para Nómina
Funciones avanzadas de utilidad para cálculos complejos y análisis
"""

import logging
import math
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional, List, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class PayrollAdvancedUtilities:
    """Utilidades avanzadas para nómina"""
    
    @staticmethod
    def calculate_projected_annual_cost(
        period_cost: Decimal,
        periods_per_year: int = 26,
        growth_rate: Decimal = Decimal("0.00")
    ) -> Dict[str, Decimal]:
        """
        Calcula costo anual proyectado con crecimiento
        
        Args:
            period_cost: Costo del período actual
            periods_per_year: Períodos por año (default: 26 para biweekly)
            growth_rate: Tasa de crecimiento anual (default: 0%)
        
        Returns:
            Dict con proyecciones actual, con crecimiento, y diferencia
        """
        current_annual = period_cost * Decimal(str(periods_per_year))
        
        if growth_rate > Decimal("0.00"):
            projected_annual = current_annual * (Decimal("1.00") + growth_rate)
            difference = projected_annual - current_annual
        else:
            projected_annual = current_annual
            difference = Decimal("0.00")
        
        return {
            "current_annual": current_annual.quantize(Decimal("0.01")),
            "projected_annual": projected_annual.quantize(Decimal("0.01")),
            "growth_amount": difference.quantize(Decimal("0.01")),
            "growth_rate": growth_rate
        }
    
    @staticmethod
    def calculate_cost_per_employee(
        total_cost: Decimal,
        employee_count: int
    ) -> Decimal:
        """Calcula costo promedio por empleado"""
        if employee_count == 0:
            return Decimal("0.00")
        return (total_cost / Decimal(str(employee_count))).quantize(Decimal("0.01"))
    
    @staticmethod
    def calculate_overtime_cost_impact(
        regular_hours: Decimal,
        overtime_hours: Decimal,
        hourly_rate: Decimal,
        overtime_multiplier: Decimal = Decimal("1.5")
    ) -> Dict[str, Decimal]:
        """
        Calcula el impacto de costo del overtime
        
        Returns:
            Dict con costo regular, overtime, premium, y total
        """
        regular_cost = regular_hours * hourly_rate
        overtime_cost = overtime_hours * hourly_rate * overtime_multiplier
        overtime_premium = overtime_hours * hourly_rate * (overtime_multiplier - Decimal("1.00"))
        total_cost = regular_cost + overtime_cost
        
        return {
            "regular_cost": regular_cost.quantize(Decimal("0.01")),
            "overtime_cost": overtime_cost.quantize(Decimal("0.01")),
            "overtime_premium": overtime_premium.quantize(Decimal("0.01")),
            "total_cost": total_cost.quantize(Decimal("0.01")),
            "overtime_percentage": (
                (overtime_hours / (regular_hours + overtime_hours) * 100)
                if (regular_hours + overtime_hours) > 0 else Decimal("0.00")
            ).quantize(Decimal("0.01"))
        }
    
    @staticmethod
    def calculate_break_even_hours(
        fixed_cost: Decimal,
        variable_cost_per_hour: Decimal,
        revenue_per_hour: Decimal
    ) -> Decimal:
        """
        Calcula horas de break-even
        
        Args:
            fixed_cost: Costo fijo
            variable_cost_per_hour: Costo variable por hora
            revenue_per_hour: Ingreso por hora
        
        Returns:
            Horas necesarias para break-even
        """
        if revenue_per_hour <= variable_cost_per_hour:
            return Decimal("0.00")  # No hay break-even posible
        
        contribution_margin = revenue_per_hour - variable_cost_per_hour
        break_even_hours = fixed_cost / contribution_margin
        
        return break_even_hours.quantize(Decimal("0.01"))
    
    @staticmethod
    def calculate_variance(
        actual: Decimal,
        expected: Decimal
    ) -> Dict[str, Decimal]:
        """
        Calcula varianza entre valores actuales y esperados
        
        Returns:
            Dict con diferencia absoluta, diferencia porcentual, y variación
        """
        difference = actual - expected
        absolute_difference = abs(difference)
        
        if expected != Decimal("0.00"):
            percentage_difference = (difference / expected * 100).quantize(Decimal("0.01"))
        else:
            percentage_difference = Decimal("0.00") if actual == Decimal("0.00") else Decimal("100.00")
        
        variance_type = "over" if difference > 0 else "under" if difference < 0 else "exact"
        
        return {
            "actual": actual,
            "expected": expected,
            "difference": difference.quantize(Decimal("0.01")),
            "absolute_difference": absolute_difference.quantize(Decimal("0.01")),
            "percentage_difference": percentage_difference,
            "variance_type": variance_type
        }
    
    @staticmethod
    def calculate_efficiency_ratio(
        output: Decimal,
        input_hours: Decimal
    ) -> Decimal:
        """
        Calcula ratio de eficiencia (output por hora)
        
        Args:
            output: Cantidad producida/completada
            input_hours: Horas trabajadas
        
        Returns:
            Ratio de eficiencia
        """
        if input_hours == Decimal("0.00"):
            return Decimal("0.00")
        
        return (output / input_hours).quantize(Decimal("0.01"))
    
    @staticmethod
    def calculate_utilization_rate(
        hours_worked: Decimal,
        hours_available: Decimal
    ) -> Decimal:
        """
        Calcula tasa de utilización
        
        Args:
            hours_worked: Horas trabajadas
            hours_available: Horas disponibles
        
        Returns:
            Tasa de utilización como porcentaje
        """
        if hours_available == Decimal("0.00"):
            return Decimal("0.00")
        
        utilization = (hours_worked / hours_available * 100).quantize(Decimal("0.01"))
        return min(utilization, Decimal("100.00"))  # Cap at 100%
    
    @staticmethod
    def group_by_department(
        calculations: List[Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Agrupa cálculos por departamento
        
        Args:
            calculations: Lista de cálculos de período
        
        Returns:
            Dict agrupado por departamento con totales
        """
        grouped = defaultdict(lambda: {
            "employees": [],
            "total_hours": Decimal("0.00"),
            "total_gross": Decimal("0.00"),
            "total_net": Decimal("0.00"),
            "total_deductions": Decimal("0.00"),
            "count": 0
        })
        
        for calc in calculations:
            dept = getattr(calc, "department", "Unknown")
            grouped[dept]["employees"].append(getattr(calc, "employee_id", "Unknown"))
            grouped[dept]["total_hours"] += getattr(calc, "total_hours", Decimal("0.00"))
            grouped[dept]["total_gross"] += getattr(calc, "gross_pay", Decimal("0.00"))
            grouped[dept]["total_net"] += getattr(calc, "net_pay", Decimal("0.00"))
            grouped[dept]["total_deductions"] += getattr(calc, "total_deductions", Decimal("0.00"))
            grouped[dept]["count"] += 1
        
        # Convertir a dict regular y cuantizar
        result = {}
        for dept, data in grouped.items():
            result[dept] = {
                "employees": data["employees"],
                "total_hours": data["total_hours"].quantize(Decimal("0.01")),
                "total_gross": data["total_gross"].quantize(Decimal("0.01")),
                "total_net": data["total_net"].quantize(Decimal("0.01")),
                "total_deductions": data["total_deductions"].quantize(Decimal("0.01")),
                "employee_count": data["count"],
                "average_gross": (
                    data["total_gross"] / Decimal(str(data["count"]))
                    if data["count"] > 0 else Decimal("0.00")
                ).quantize(Decimal("0.01"))
            }
        
        return result
    
    @staticmethod
    def calculate_percentile(
        values: List[Decimal],
        percentile: Decimal
    ) -> Decimal:
        """
        Calcula percentil de una lista de valores
        
        Args:
            values: Lista de valores
            percentile: Percentil deseado (0-100)
        
        Returns:
            Valor del percentil
        """
        if not values:
            return Decimal("0.00")
        
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            weight = Decimal(str(index - int(index)))
            return (lower * (Decimal("1.00") - weight) + upper * weight).quantize(Decimal("0.01"))
    
    @staticmethod
    def calculate_statistics(
        values: List[Decimal]
    ) -> Dict[str, Decimal]:
        """
        Calcula estadísticas descriptivas
        
        Returns:
            Dict con min, max, mean, median, std_dev
        """
        if not values:
            return {
                "count": 0,
                "min": Decimal("0.00"),
                "max": Decimal("0.00"),
                "mean": Decimal("0.00"),
                "median": Decimal("0.00"),
                "std_dev": Decimal("0.00")
            }
        
        sorted_values = sorted(values)
        count = len(values)
        total = sum(values)
        mean = (total / Decimal(str(count))).quantize(Decimal("0.01"))
        
        # Mediana
        if count % 2 == 0:
            median = (
                (sorted_values[count // 2 - 1] + sorted_values[count // 2]) / Decimal("2.00")
            ).quantize(Decimal("0.01"))
        else:
            median = sorted_values[count // 2]
        
        # Desviación estándar
        variance = sum((v - mean) ** 2 for v in values) / Decimal(str(count))
        std_dev = Decimal(str(math.sqrt(float(variance)))) if variance > 0 else Decimal("0.00")
        
        return {
            "count": count,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "mean": mean,
            "median": median,
            "std_dev": std_dev.quantize(Decimal("0.01"))
        }
    
    @staticmethod
    def calculate_trend(
        values: List[Decimal],
        periods: Optional[List[date]] = None
    ) -> Dict[str, Any]:
        """
        Calcula tendencia de valores a lo largo del tiempo
        
        Returns:
            Dict con tendencia, cambio promedio, y dirección
        """
        if len(values) < 2:
            return {
                "trend": "insufficient_data",
                "change_per_period": Decimal("0.00"),
                "direction": "stable",
                "slope": Decimal("0.00")
            }
        
        # Calcular cambios
        changes = [values[i] - values[i-1] for i in range(1, len(values))]
        avg_change = sum(changes) / Decimal(str(len(changes)))
        
        # Determinar dirección
        if avg_change > Decimal("0.01"):
            direction = "increasing"
        elif avg_change < Decimal("-0.01"):
            direction = "decreasing"
        else:
            direction = "stable"
        
        # Calcular pendiente (simple linear regression)
        if periods and len(periods) == len(values):
            # Usar días desde el primer período
            days = [(periods[i] - periods[0]).days for i in range(len(periods))]
            if all(d > 0 for d in days[1:]):
                # Pendiente = cambio promedio por día
                total_days = days[-1]
                slope = (values[-1] - values[0]) / Decimal(str(total_days)) if total_days > 0 else Decimal("0.00")
            else:
                slope = Decimal("0.00")
        else:
            slope = avg_change
        
        return {
            "trend": direction,
            "change_per_period": avg_change.quantize(Decimal("0.01")),
            "direction": direction,
            "slope": slope.quantize(Decimal("0.01")),
            "first_value": values[0],
            "last_value": values[-1],
            "total_change": (values[-1] - values[0]).quantize(Decimal("0.01"))
        }


def format_payroll_summary(
    calculations: List[Any],
    period_start: date,
    period_end: date
) -> str:
    """
    Formatea un resumen legible de cálculos de nómina
    
    Args:
        calculations: Lista de cálculos
        period_start: Inicio del período
        period_end: Fin del período
    
    Returns:
        String formateado con resumen
    """
    if not calculations:
        return f"No payroll calculations for period {period_start} to {period_end}"
    
    total_employees = len(calculations)
    total_hours = sum(getattr(c, "total_hours", Decimal("0.00")) for c in calculations)
    total_gross = sum(getattr(c, "gross_pay", Decimal("0.00")) for c in calculations)
    total_net = sum(getattr(c, "net_pay", Decimal("0.00")) for c in calculations)
    total_deductions = sum(getattr(c, "total_deductions", Decimal("0.00")) for c in calculations)
    
    summary = f"""
Payroll Summary - {period_start} to {period_end}
{'=' * 50}
Total Employees: {total_employees}
Total Hours: {total_hours}
Total Gross Pay: ${total_gross:,.2f}
Total Deductions: ${total_deductions:,.2f}
Total Net Pay: ${total_net:,.2f}
{'=' * 50}
"""
    
    return summary.strip()


def calculate_payroll_metrics_summary(
    calculations: List[Any]
) -> Dict[str, Any]:
    """
    Calcula resumen de métricas de nómina
    
    Returns:
        Dict con métricas agregadas
    """
    if not calculations:
        return {}
    
    utilities = PayrollAdvancedUtilities()
    
    # Extraer valores
    gross_pays = [getattr(c, "gross_pay", Decimal("0.00")) for c in calculations]
    net_pays = [getattr(c, "net_pay", Decimal("0.00")) for c in calculations]
    hours = [getattr(c, "total_hours", Decimal("0.00")) for c in calculations]
    
    # Calcular estadísticas
    gross_stats = utilities.calculate_statistics(gross_pays)
    net_stats = utilities.calculate_statistics(net_pays)
    hours_stats = utilities.calculate_statistics(hours)
    
    # Totales
    total_gross = sum(gross_pays)
    total_net = sum(net_pays)
    total_hours = sum(hours)
    
    return {
        "employee_count": len(calculations),
        "total_gross": total_gross.quantize(Decimal("0.01")),
        "total_net": total_net.quantize(Decimal("0.01")),
        "total_hours": total_hours.quantize(Decimal("0.01")),
        "gross_statistics": gross_stats,
        "net_statistics": net_stats,
        "hours_statistics": hours_stats,
        "average_gross_per_employee": (
            total_gross / Decimal(str(len(calculations)))
            if calculations else Decimal("0.00")
        ).quantize(Decimal("0.01")),
        "average_hours_per_employee": (
            total_hours / Decimal(str(len(calculations)))
            if calculations else Decimal("0.00")
        ).quantize(Decimal("0.01"))
    }

