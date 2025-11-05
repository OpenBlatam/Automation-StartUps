"""
Funciones auxiliares generales
"""
import logging
from functools import wraps
from typing import Callable, Any
from datetime import datetime, timedelta

def setup_logging(level=logging.INFO):
    """Configura el sistema de logging"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def log_execution_time(func: Callable) -> Callable:
    """Decorador para medir tiempo de ejecución de funciones"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logging.info(f"{func.__name__} ejecutado en {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logging.error(f"{func.__name__} falló después de {execution_time:.2f}s: {e}")
            raise
    return wrapper

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """División segura que evita división por cero"""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calcula el cambio porcentual entre dos valores"""
    if old_value == 0:
        return 0.0 if new_value == 0 else 100.0
    return ((new_value - old_value) / old_value) * 100

def get_date_range(days: int = 30) -> tuple[datetime, datetime]:
    """Obtiene rango de fechas (hace N días hasta hoy)"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date

def chunk_list(items: list, chunk_size: int) -> list:
    """Divide una lista en chunks de tamaño especificado"""
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]

def safe_get(dictionary: dict, *keys, default=None) -> Any:
    """Obtiene valor de diccionario anidado de forma segura"""
    current = dictionary
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

def sanitize_filename(filename: str) -> str:
    """Sanitiza nombres de archivo eliminando caracteres inválidos"""
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()

def generate_sku(category: str, number: int) -> str:
    """Genera un SKU automático basado en categoría y número"""
    category_prefix = category[:3].upper() if category else 'PRD'
    return f"{category_prefix}-{number:05d}"

