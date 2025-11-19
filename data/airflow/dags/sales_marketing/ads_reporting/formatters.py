"""
Utilidades de formateo y presentación de datos.

Incluye:
- Formateo de números y monedas
- Formateo de porcentajes
- Tablas formateadas
- Formateo de fechas
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def format_number(
    value: float,
    decimals: int = 2,
    thousands_separator: bool = True
) -> str:
    """
    Formatea un número con separadores de miles.
    
    Args:
        value: Número a formatear
        decimals: Decimales a mostrar
        thousands_separator: Si usar separador de miles
        
    Returns:
        String formateado
    """
    if value is None:
        return "0"
    
    if thousands_separator:
        return f"{value:,.{decimals}f}"
    else:
        return f"{value:.{decimals}f}"


def format_currency(
    value: float,
    currency: str = "USD",
    show_symbol: bool = True
) -> str:
    """
    Formatea un valor como moneda.
    
    Args:
        value: Valor a formatear
        currency: Código de moneda (USD, EUR, etc.)
        show_symbol: Si mostrar símbolo de moneda
        
    Returns:
        String formateado
    """
    if value is None:
        value = 0.0
    
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "MXN": "$",
    }
    
    symbol = symbols.get(currency.upper(), currency.upper())
    
    if show_symbol:
        return f"{symbol}{value:,.2f}"
    else:
        return f"{value:,.2f} {currency.upper()}"


def format_percentage(
    value: float,
    decimals: int = 2,
    show_symbol: bool = True
) -> str:
    """
    Formatea un valor como porcentaje.
    
    Args:
        value: Valor a formatear (ya en porcentaje, ej: 2.5 para 2.5%)
        decimals: Decimales a mostrar
        show_symbol: Si mostrar símbolo %
        
    Returns:
        String formateado
    """
    if value is None:
        value = 0.0
    
    if show_symbol:
        return f"{value:.{decimals}f}%"
    else:
        return f"{value:.{decimals}f}"


def format_duration(
    seconds: float,
    precision: str = "seconds"
) -> str:
    """
    Formatea duración en formato legible.
    
    Args:
        seconds: Segundos a formatear
        precision: Precisión (seconds, minutes, hours)
        
    Returns:
        String formateado
    """
    if seconds is None:
        return "0s"
    
    if precision == "hours" or seconds >= 3600:
        hours = seconds / 3600
        return f"{hours:.2f}h"
    elif precision == "minutes" or seconds >= 60:
        minutes = seconds / 60
        return f"{minutes:.2f}m"
    else:
        return f"{seconds:.2f}s"


def format_table(
    data: List[Dict[str, Any]],
    columns: Optional[List[str]] = None,
    max_rows: int = 20
) -> str:
    """
    Formatea datos como tabla de texto.
    
    Args:
        data: Lista de diccionarios
        columns: Columnas a mostrar (None para todas)
        max_rows: Máximo de filas a mostrar
        
    Returns:
        String con tabla formateada
    """
    if not data:
        return "No data"
    
    if columns is None:
        columns = list(data[0].keys())
    
    # Calcular ancho de columnas
    widths = {}
    for col in columns:
        widths[col] = max(
            len(str(col)),
            max(len(str(row.get(col, ""))) for row in data[:max_rows]) if data else 0
        )
    
    # Crear header
    header = " | ".join(col.ljust(widths[col]) for col in columns)
    separator = "-+-".join("-" * widths[col] for col in columns)
    
    lines = [header, separator]
    
    # Agregar filas
    for row in data[:max_rows]:
        row_str = " | ".join(
            str(row.get(col, "")).ljust(widths[col])
            for col in columns
        )
        lines.append(row_str)
    
    if len(data) > max_rows:
        lines.append(f"... ({len(data) - max_rows} more rows)")
    
    return "\n".join(lines)


def format_metric_change(
    current: float,
    previous: float,
    format_type: str = "percentage"
) -> str:
    """
    Formatea cambio entre dos valores.
    
    Args:
        current: Valor actual
        previous: Valor anterior
        format_type: Tipo de formato (percentage, absolute)
        
    Returns:
        String formateado con cambio
    """
    if previous == 0:
        change = 0.0
        change_pct = 0.0
    else:
        change = current - previous
        change_pct = (change / previous) * 100
    
    if format_type == "percentage":
        if change_pct >= 0:
            return f"+{change_pct:.2f}%"
        else:
            return f"{change_pct:.2f}%"
    else:
        if change >= 0:
            return f"+{format_number(change)}"
        else:
            return format_number(change)


def format_summary_stats(
    data: List[Dict[str, Any]],
    metric_fields: List[str]
) -> str:
    """
    Formatea estadísticas resumidas.
    
    Args:
        data: Lista de datos
        metric_fields: Campos con métricas a resumir
        
    Returns:
        String con estadísticas formateadas
    """
    if not data:
        return "No data available"
    
    lines = ["SUMMARY STATISTICS", "=" * 60]
    
    for field in metric_fields:
        values = [float(r.get(field, 0) or 0) for r in data if field in r]
        
        if not values:
            continue
        
        import statistics
        try:
            mean = statistics.mean(values)
            median = statistics.median(values)
            min_val = min(values)
            max_val = max(values)
            
            if len(values) > 1:
                stdev = statistics.stdev(values)
            else:
                stdev = 0
            
            lines.append(f"\n{field.upper()}:")
            lines.append(f"  Mean:   {format_number(mean)}")
            lines.append(f"  Median: {format_number(median)}")
            lines.append(f"  Min:    {format_number(min_val)}")
            lines.append(f"  Max:    {format_number(max_val)}")
            lines.append(f"  StdDev: {format_number(stdev)}")
        except Exception as e:
            logger.warning(f"Error calculando stats para {field}: {str(e)}")
    
    return "\n".join(lines)


def format_list_summary(
    items: List[str],
    max_items: int = 5,
    separator: str = ", "
) -> str:
    """
    Formatea lista con resumen si es muy larga.
    
    Args:
        items: Lista de items
        max_items: Máximo de items a mostrar
        separator: Separador entre items
        
    Returns:
        String formateado
    """
    if not items:
        return "None"
    
    if len(items) <= max_items:
        return separator.join(items)
    else:
        shown = separator.join(items[:max_items])
        remaining = len(items) - max_items
        return f"{shown}{separator}... and {remaining} more"


def format_boolean(
    value: Any,
    true_text: str = "Yes",
    false_text: str = "No"
) -> str:
    """
    Formatea valor booleano como texto.
    
    Args:
        value: Valor a formatear
        true_text: Texto para True
        false_text: Texto para False
        
    Returns:
        String formateado
    """
    if value:
        return true_text
    else:
        return false_text


def format_date_range(
    date_start: str,
    date_stop: str,
    format_type: str = "short"
) -> str:
    """
    Formatea rango de fechas.
    
    Args:
        date_start: Fecha inicio
        date_stop: Fecha fin
        format_type: Tipo de formato (short, long, duration)
        
    Returns:
        String formateado
    """
    from datetime import datetime
    
    try:
        start = datetime.strptime(date_start, "%Y-%m-%d")
        stop = datetime.strptime(date_stop, "%Y-%m-%d")
        
        if format_type == "short":
            return f"{start.strftime('%m/%d')} - {stop.strftime('%m/%d/%Y')}"
        elif format_type == "long":
            return f"{start.strftime('%B %d, %Y')} to {stop.strftime('%B %d, %Y')}"
        elif format_type == "duration":
            days = (stop - start).days + 1
            return f"{days} days"
        else:
            return f"{date_start} to {date_stop}"
    except Exception:
        return f"{date_start} to {date_stop}"

