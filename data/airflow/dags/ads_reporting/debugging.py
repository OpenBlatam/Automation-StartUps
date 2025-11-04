"""
Utilidades de debugging y diagnóstico.

Incluye:
- Logging mejorado
- Diagnóstico de problemas
- Profiling de operaciones
- Inspectores de datos
"""

from __future__ import annotations

import logging
import time
import traceback
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

try:
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False


@contextmanager
def timing_context(operation_name: str, log_level: int = logging.INFO):
    """
    Context manager para medir tiempo de ejecución.
    
    Args:
        operation_name: Nombre de la operación
        log_level: Nivel de logging
        
    Example:
        with timing_context("data_extraction"):
            data = extract_data()
    """
    start_time = time.time()
    logger.log(log_level, f"Starting {operation_name}")
    
    try:
        yield
    finally:
        duration = time.time() - start_time
        logger.log(
            log_level,
            f"Completed {operation_name} in {duration:.2f}s"
        )
        
        if STATS_AVAILABLE:
            try:
                stats = Stats()
                stats.timing(f"ads_reporting.{operation_name}.duration", int(duration * 1000))
            except Exception:
                pass


def debug_function(func: Callable) -> Callable:
    """
    Decorador para debugging de funciones.
    
    Logs:
    - Argumentos de entrada
    - Tiempo de ejecución
    - Resultado (si es pequeño)
    - Errores completos
    
    Example:
        @debug_function
        def my_function(arg1, arg2):
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        
        logger.debug(
            f"Calling {func_name}",
            extra={
                "args_count": len(args),
                "kwargs": list(kwargs.keys()),
                "args_preview": str(args)[:200] if args else None
            }
        )
        
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Log resultado si es pequeño
            result_preview = None
            if isinstance(result, (str, int, float, bool, type(None))):
                result_preview = str(result)
            elif isinstance(result, (list, dict)) and len(str(result)) < 200:
                result_preview = str(result)
            elif hasattr(result, "__len__") and len(result) <= 10:
                result_preview = f"{type(result).__name__} with {len(result)} items"
            
            logger.debug(
                f"{func_name} completed in {duration:.3f}s",
                extra={
                    "duration": duration,
                    "result_preview": result_preview
                }
            )
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"{func_name} failed after {duration:.3f}s: {str(e)}",
                exc_info=True,
                extra={
                    "duration": duration,
                    "error_type": type(e).__name__,
                    "traceback": traceback.format_exc()
                }
            )
            raise
    
    return wrapper


def inspect_data(
    data: Any,
    name: str = "data",
    max_depth: int = 3,
    max_items: int = 10
) -> Dict[str, Any]:
    """
    Inspecciona datos y retorna información de diagnóstico.
    
    Args:
        data: Datos a inspeccionar
        name: Nombre de los datos
        max_depth: Profundidad máxima para estructuras anidadas
        max_items: Máximo de items a mostrar
        
    Returns:
        Diccionario con información de diagnóstico
    """
    info = {
        "name": name,
        "type": type(data).__name__,
        "size": None,
        "shape": None,
        "sample": None,
        "keys": None,
        "nulls": None
    }
    
    try:
        if isinstance(data, list):
            info["size"] = len(data)
            info["sample"] = data[:max_items] if len(data) > max_items else data
            
            # Contar nulls en lista de dicts
            if data and isinstance(data[0], dict):
                all_keys = set()
                for item in data:
                    if isinstance(item, dict):
                        all_keys.update(item.keys())
                
                info["keys"] = list(all_keys)
                
                nulls = {}
                for key in all_keys:
                    null_count = sum(1 for item in data if not item.get(key) or item.get(key) == "")
                    nulls[key] = null_count
                info["nulls"] = nulls
        
        elif isinstance(data, dict):
            info["size"] = len(data)
            info["keys"] = list(data.keys())[:max_items]
            info["sample"] = {k: str(v)[:100] for k, v in list(data.items())[:max_items]}
        
        elif hasattr(data, "shape"):
            # Pandas DataFrame o numpy array
            info["shape"] = data.shape
            info["size"] = data.size if hasattr(data, "size") else None
        
        else:
            info["size"] = len(str(data)) if hasattr(data, "__len__") else None
            info["sample"] = str(data)[:200]
    
    except Exception as e:
        info["inspection_error"] = str(e)
    
    return info


def diagnose_extraction_issues(
    records_extracted: int,
    expected_min: int = 1,
    duration_ms: float = 0,
    errors: int = 0
) -> Dict[str, Any]:
    """
    Diagnostica problemas comunes en extracciones.
    
    Args:
        records_extracted: Registros extraídos
        expected_min: Mínimo esperado
        duration_ms: Duración en milisegundos
        errors: Número de errores
        
    Returns:
        Diccionario con diagnóstico
    """
    issues = []
    suggestions = []
    
    # Verificar número de registros
    if records_extracted < expected_min:
        issues.append({
            "type": "low_records",
            "severity": "warning",
            "message": f"Se extrajeron {records_extracted} registros, se esperaban al menos {expected_min}"
        })
        suggestions.append("Verificar filtros de fecha y parámetros de búsqueda")
        suggestions.append("Verificar que haya datos en el período seleccionado")
    
    # Verificar errores
    if errors > 0:
        issues.append({
            "type": "errors_present",
            "severity": "error",
            "message": f"Se encontraron {errors} errores durante la extracción"
        })
        suggestions.append("Revisar logs para detalles de errores")
        suggestions.append("Verificar credenciales y permisos de API")
    
    # Verificar tiempo de ejecución
    if duration_ms > 60000:  # Más de 1 minuto
        issues.append({
            "type": "slow_execution",
            "severity": "warning",
            "message": f"La extracción tomó {duration_ms/1000:.2f}s, puede ser lenta"
        })
        suggestions.append("Considerar usar batch processing para grandes volúmenes")
        suggestions.append("Verificar caché está habilitado")
    
    return {
        "issues": issues,
        "suggestions": suggestions,
        "healthy": len(issues) == 0
    }


def log_data_sample(
    data: Any,
    name: str = "data",
    sample_size: int = 5
) -> None:
    """
    Loguea una muestra de datos para debugging.
    
    Args:
        data: Datos a muestrear
        name: Nombre de los datos
        sample_size: Tamaño de la muestra
    """
    if isinstance(data, list):
        sample = data[:sample_size] if len(data) > sample_size else data
        logger.debug(
            f"Sample of {name} ({len(data)} total items):",
            extra={
                "total_items": len(data),
                "sample": sample,
                "sample_size": min(sample_size, len(data))
            }
        )
    elif isinstance(data, dict):
        logger.debug(
            f"Sample of {name}:",
            extra={"sample": dict(list(data.items())[:sample_size])}
        )
    else:
        logger.debug(f"{name}: {str(data)[:500]}")


@contextmanager
def error_handler_context(
    operation_name: str,
    reraise: bool = True,
    log_error: bool = True
):
    """
    Context manager para manejo de errores con logging.
    
    Args:
        operation_name: Nombre de la operación
        reraise: Si re-raise la excepción
        log_error: Si loguear el error
        
    Example:
        with error_handler_context("api_call"):
            result = make_api_call()
    """
    try:
        yield
    except Exception as e:
        if log_error:
            logger.error(
                f"Error in {operation_name}: {str(e)}",
                exc_info=True,
                extra={
                    "operation": operation_name,
                    "error_type": type(e).__name__
                }
            )
        
        if reraise:
            raise


def profile_function(func: Callable) -> Callable:
    """
    Decorador para profiling de funciones.
    
    Registra:
    - Tiempo de ejecución
    - Número de llamadas
    - Tasa de éxito/error
    
    Example:
        @profile_function
        def expensive_operation():
            ...
    """
    func.stats = {
        "calls": 0,
        "total_time": 0.0,
        "successes": 0,
        "errors": 0
    }
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        func.stats["calls"] += 1
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            func.stats["successes"] += 1
            return result
        except Exception:
            func.stats["errors"] += 1
            raise
        finally:
            duration = time.time() - start_time
            func.stats["total_time"] += duration
            
            # Log estadísticas cada 10 llamadas
            if func.stats["calls"] % 10 == 0:
                avg_time = func.stats["total_time"] / func.stats["calls"]
                success_rate = (func.stats["successes"] / func.stats["calls"]) * 100
                
                logger.debug(
                    f"{func.__name__} stats: "
                    f"{func.stats['calls']} calls, "
                    f"avg {avg_time:.3f}s, "
                    f"{success_rate:.1f}% success rate"
                )
    
    return wrapper

