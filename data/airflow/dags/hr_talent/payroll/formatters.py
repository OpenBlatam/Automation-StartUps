"""
Formateadores Avanzados para Nómina
Funciones para formatear y presentar datos de nómina de manera legible
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional, Union, Callable
import json

logger = logging.getLogger(__name__)


class PayrollFormatter:
    """Formateador de datos de nómina"""
    
    @staticmethod
    def format_currency(
        amount: Decimal,
        currency: str = "USD",
        show_cents: bool = True,
        use_thousands_separator: bool = True
    ) -> str:
        """
        Formatea un monto como moneda
        
        Args:
            amount: Monto a formatear
            currency: Código de moneda
            show_cents: Si mostrar centavos
            use_thousands_separator: Si usar separador de miles
        
        Returns:
            String formateado
        """
        if amount is None:
            return "N/A"
        
        if not show_cents:
            amount = amount.quantize(Decimal("1"))
        
        if currency == "USD":
            symbol = "$"
        elif currency == "EUR":
            symbol = "€"
        elif currency == "GBP":
            symbol = "£"
        else:
            symbol = currency + " "
        
        if use_thousands_separator:
            formatted = f"{amount:,.2f}" if show_cents else f"{amount:,.0f}"
        else:
            formatted = f"{amount:.2f}" if show_cents else f"{amount:.0f}"
        
        return f"{symbol}{formatted}"
    
    @staticmethod
    def format_hours(
        hours: Decimal,
        format_type: str = "decimal"
    ) -> str:
        """
        Formatea horas trabajadas
        
        Args:
            hours: Horas a formatear
            format_type: Tipo de formato (decimal, hours_minutes, verbose)
        
        Returns:
            String formateado
        """
        if hours is None:
            return "0h"
        
        if format_type == "decimal":
            return f"{hours:.2f}h"
        
        elif format_type == "hours_minutes":
            hours_int = int(hours)
            minutes = int((hours - hours_int) * 60)
            return f"{hours_int}h {minutes}m"
        
        elif format_type == "verbose":
            hours_int = int(hours)
            minutes = int((hours - hours_int) * 60)
            if hours_int == 0:
                return f"{minutes} minutos"
            elif minutes == 0:
                return f"{hours_int} horas"
            else:
                return f"{hours_int} horas y {minutes} minutos"
        
        return str(hours)
    
    @staticmethod
    def format_percentage(
        value: Decimal,
        decimals: int = 2
    ) -> str:
        """Formatea un porcentaje"""
        if value is None:
            return "0.00%"
        
        return f"{value:.{decimals}f}%"
    
    @staticmethod
    def format_period_range(
        start_date: date,
        end_date: date,
        format_type: str = "short"
    ) -> str:
        """
        Formatea rango de período
        
        Args:
            start_date: Fecha inicio
            end_date: Fecha fin
            format_type: short, long, full, iso
        """
        if format_type == "short":
            return f"{start_date.strftime('%m/%d')} - {end_date.strftime('%m/%d/%Y')}"
        
        elif format_type == "long":
            return f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
        
        elif format_type == "full":
            return f"{start_date.strftime('%A, %B %d, %Y')} to {end_date.strftime('%A, %B %d, %Y')}"
        
        elif format_type == "iso":
            return f"{start_date.isoformat()} to {end_date.isoformat()}"
        
        return f"{start_date} to {end_date}"
    
    @staticmethod
    def format_employee_summary(
        employee_id: str,
        name: str,
        gross_pay: Decimal,
        net_pay: Decimal,
        hours: Decimal
    ) -> str:
        """Formatea resumen de empleado"""
        return (
            f"{employee_id} - {name}\n"
            f"  Hours: {PayrollFormatter.format_hours(hours)}\n"
            f"  Gross: {PayrollFormatter.format_currency(gross_pay)}\n"
            f"  Net: {PayrollFormatter.format_currency(net_pay)}"
        )
    
    @staticmethod
    def format_calculation_breakdown(
        calculation: Any,
        include_details: bool = True
    ) -> str:
        """
        Formatea desglose de cálculo
        
        Args:
            calculation: Objeto de cálculo
            include_details: Si incluir detalles de deducciones
        """
        period_start = getattr(calculation, 'period_start', date.today())
        period_end = getattr(calculation, 'period_end', date.today())
        lines = [
            f"Employee: {getattr(calculation, 'employee_id', 'N/A')}",
            f"Period: {PayrollFormatter.format_period_range(period_start, period_end)}",
            "",
            "Hours:",
            f"  Regular: {PayrollFormatter.format_hours(getattr(calculation, 'regular_hours', Decimal('0.00')))}",
            f"  Overtime: {PayrollFormatter.format_hours(getattr(calculation, 'overtime_hours', Decimal('0.00')))}",
            f"  Total: {PayrollFormatter.format_hours(getattr(calculation, 'total_hours', Decimal('0.00')))}",
            "",
            "Pay:",
            f"  Gross: {PayrollFormatter.format_currency(getattr(calculation, 'gross_pay', Decimal('0.00')))}",
            f"  Deductions: {PayrollFormatter.format_currency(getattr(calculation, 'total_deductions', Decimal('0.00')))}",
            f"  Expenses: {PayrollFormatter.format_currency(getattr(calculation, 'total_expenses', Decimal('0.00')))}",
            f"  Net: {PayrollFormatter.format_currency(getattr(calculation, 'net_pay', Decimal('0.00')))}",
        ]
        
        if include_details and hasattr(calculation, 'deductions'):
            lines.append("")
            lines.append("Deductions Breakdown:")
            for deduction in getattr(calculation, 'deductions', []):
                lines.append(
                    f"  {getattr(deduction, 'name', 'Unknown')}: "
                    f"{PayrollFormatter.format_currency(getattr(deduction, 'amount', Decimal('0.00')))}"
                )
        
        return "\n".join(lines)
    
    @staticmethod
    def format_table(
        headers: List[str],
        rows: List[List[Any]],
        align: Optional[List[str]] = None,
        max_width: int = 80
    ) -> str:
        """
        Formatea datos como tabla
        
        Args:
            headers: Encabezados de columna
            rows: Filas de datos
            align: Alineación por columna (left, right, center)
            max_width: Ancho máximo de la tabla
        """
        if not headers or not rows:
            return ""
        
        if align is None:
            align = ["left"] * len(headers)
        
        # Calcular anchos de columna
        col_widths = [len(str(h)) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Ajustar anchos si excede max_width
        total_width = sum(col_widths) + (len(headers) - 1) * 3 + 4
        if total_width > max_width:
            # Reducir proporcionalmente
            ratio = max_width / total_width
            col_widths = [int(w * ratio) for w in col_widths]
        
        # Formatear headers
        header_row = " | ".join(
            str(h).ljust(col_widths[i]) if i < len(col_widths) else str(h)
            for i, h in enumerate(headers)
        )
        
        separator = "-" * len(header_row)
        
        # Formatear filas
        formatted_rows = [header_row, separator]
        for row in rows:
            formatted_cells = []
            for i, cell in enumerate(row):
                if i >= len(col_widths):
                    break
                cell_str = str(cell)
                if len(cell_str) > col_widths[i]:
                    cell_str = cell_str[:col_widths[i]-3] + "..."
                
                if i < len(align):
                    if align[i] == "right":
                        formatted_cells.append(cell_str.rjust(col_widths[i]))
                    elif align[i] == "center":
                        formatted_cells.append(cell_str.center(col_widths[i]))
                    else:
                        formatted_cells.append(cell_str.ljust(col_widths[i]))
                else:
                    formatted_cells.append(cell_str.ljust(col_widths[i]))
            
            formatted_rows.append(" | ".join(formatted_cells))
        
        return "\n".join(formatted_rows)
    
    @staticmethod
    def format_json(
        data: Any,
        indent: int = 2,
        default_converter: Optional[Callable] = None
    ) -> str:
        """
        Formatea datos como JSON legible
        
        Args:
            data: Datos a formatear
            indent: Indentación
            default_converter: Función para convertir tipos no serializables
        """
        def default_convert(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, date):
                return obj.isoformat()
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif default_converter:
                return default_converter(obj)
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        return json.dumps(data, indent=indent, default=default_convert, ensure_ascii=False)
    
    @staticmethod
    def format_summary_card(
        title: str,
        data: Dict[str, Any],
        style: str = "simple"
    ) -> str:
        """
        Formatea una tarjeta de resumen
        
        Args:
            title: Título de la tarjeta
            data: Datos a mostrar (key: value)
            style: Estilo (simple, bordered, fancy)
        """
        lines = []
        
        if style == "bordered":
            lines.append("=" * 50)
            lines.append(f" {title}")
            lines.append("=" * 50)
            for key, value in data.items():
                lines.append(f"  {key}: {value}")
            lines.append("=" * 50)
        
        elif style == "fancy":
            lines.append("┌" + "─" * 48 + "┐")
            lines.append(f"│ {title:47s} │")
            lines.append("├" + "─" * 48 + "┤")
            for key, value in data.items():
                lines.append(f"│ {key:20s}: {str(value):25s} │")
            lines.append("└" + "─" * 48 + "┘")
        
        else:  # simple
            lines.append(title)
            lines.append("-" * len(title))
            for key, value in data.items():
                lines.append(f"{key}: {value}")
        
        return "\n".join(lines)


class PayrollComparisonFormatter:
    """Formateador para comparaciones de períodos"""
    
    @staticmethod
    def format_period_comparison(
        current: Dict[str, Any],
        previous: Dict[str, Any],
        show_variance: bool = True
    ) -> str:
        """
        Formatea comparación entre dos períodos
        
        Args:
            current: Datos del período actual
            previous: Datos del período anterior
            show_variance: Si mostrar varianza
        """
        lines = [
            "Period Comparison",
            "=" * 50,
            ""
        ]
        
        fields = [
            ("Total Employees", "employee_count"),
            ("Total Hours", "total_hours"),
            ("Gross Pay", "total_gross_pay"),
            ("Deductions", "total_deductions"),
            ("Net Pay", "total_net_pay"),
        ]
        
        for label, field in fields:
            current_val = current.get(field, 0)
            previous_val = previous.get(field, 0)
            
            if isinstance(current_val, Decimal):
                current_str = PayrollFormatter.format_currency(current_val)
            else:
                current_str = str(current_val)
            
            if isinstance(previous_val, Decimal):
                previous_str = PayrollFormatter.format_currency(previous_val)
            else:
                previous_str = str(previous_val)
            
            lines.append(f"{label}:")
            lines.append(f"  Current:  {current_str}")
            lines.append(f"  Previous: {previous_str}")
            
            if show_variance and isinstance(current_val, (int, Decimal)) and isinstance(previous_val, (int, Decimal)):
                if isinstance(current_val, Decimal) and isinstance(previous_val, Decimal):
                    diff = current_val - previous_val
                    if previous_val != Decimal("0.00"):
                        pct = (diff / previous_val * 100).quantize(Decimal("0.01"))
                        lines.append(f"  Change:   {PayrollFormatter.format_currency(diff)} ({pct}%)")
                else:
                    diff = current_val - previous_val
                    if previous_val != 0:
                        pct = (diff / previous_val * 100)
                        lines.append(f"  Change:   {diff} ({pct:.2f}%)")
            
            lines.append("")
        
        return "\n".join(lines)

