"""
Funciones de formateo para el sistema
"""
from datetime import datetime
from typing import Optional

def format_currency(amount: float, currency: str = 'MXN') -> str:
    """Formatea un monto como moneda"""
    if currency == 'MXN':
        return f"${amount:,.2f}"
    elif currency == 'USD':
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def format_date(date: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Formatea una fecha"""
    if date is None:
        return ''
    return date.strftime(format_str)

def format_duration(seconds: float) -> str:
    """Formatea una duración en segundos a formato legible"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def format_percentage(value: float, decimals: int = 2) -> str:
    """Formatea un valor como porcentaje"""
    return f"{value * 100:.{decimals}f}%"

def format_stock_status(current: int, min_level: int, max_level: int) -> str:
    """Formatea el estado de stock"""
    if current <= 0:
        return "Agotado"
    elif current < min_level:
        return "Bajo"
    elif current > max_level:
        return "Exceso"
    else:
        return "Normal"

def format_alert_severity(severity: str) -> str:
    """Formatea la severidad de alerta con emoji"""
    severity_map = {
        'critical': '🔴 Crítico',
        'high': '🟠 Alto',
        'medium': '🟡 Medio',
        'low': '🟢 Bajo'
    }
    return severity_map.get(severity.lower(), severity.capitalize())

def format_file_size(size_bytes: int) -> str:
    """Formatea el tamaño de archivo en formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def truncate_text(text: str, max_length: int = 50, suffix: str = '...') -> str:
    """Trunca texto a una longitud máxima"""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

