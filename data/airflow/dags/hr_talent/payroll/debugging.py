"""
Utilidades de Debugging y Desarrollo
Herramientas para debugging, profiling y desarrollo
"""

import logging
import time
import traceback
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, Optional, List, Callable, TypeVar
from functools import wraps
from contextlib import contextmanager
import json

logger = logging.getLogger(__name__)

T = TypeVar('T')


class PayrollDebugger:
    """Utilidades de debugging para nómina"""
    
    @staticmethod
    def log_calculation_details(
        employee_id: str,
        calculation: Any,
        include_breakdown: bool = True
    ) -> None:
        """Log detallado de un cálculo"""
        logger.debug(f"=== Calculation Details for {employee_id} ===")
        logger.debug(f"Total Hours: {calculation.total_hours}")
        logger.debug(f"  - Regular: {calculation.regular_hours}")
        logger.debug(f"  - Overtime: {calculation.overtime_hours}")
        logger.debug(f"  - Double Time: {calculation.double_time_hours}")
        
        logger.debug(f"Gross Pay: {calculation.gross_pay}")
        logger.debug(f"Total Deductions: {calculation.total_deductions}")
        
        if include_breakdown and hasattr(calculation, 'deductions'):
            logger.debug(f"Deductions Breakdown:")
            for deduction in calculation.deductions:
                logger.debug(f"  - {deduction.name}: {deduction.amount}")
        
        logger.debug(f"Total Expenses: {calculation.total_expenses}")
        logger.debug(f"Net Pay: {calculation.net_pay}")
        logger.debug("=" * 50)
    
    @staticmethod
    def log_time_entry_details(
        employee_id: str,
        time_entries: List[Any],
        period_start: date,
        period_end: date
    ) -> None:
        """Log detallado de entradas de tiempo"""
        logger.debug(f"=== Time Entries for {employee_id} ({period_start} to {period_end}) ===")
        total_hours = Decimal("0.00")
        
        for entry in time_entries:
            hours = entry.hours_worked if hasattr(entry, 'hours_worked') else Decimal("0.00")
            total_hours += hours
            logger.debug(
                f"  {entry.work_date}: {hours}h "
                f"({entry.hours_type if hasattr(entry, 'hours_type') else 'N/A'})"
            )
        
        logger.debug(f"Total Hours: {total_hours}")
        logger.debug("=" * 50)
    
    @staticmethod
    def log_database_query(
        query: str,
        parameters: Optional[tuple] = None,
        execution_time: Optional[float] = None
    ) -> None:
        """Log de query de base de datos"""
        logger.debug(f"=== Database Query ===")
        logger.debug(f"Query: {query[:200]}...")
        if parameters:
            logger.debug(f"Parameters: {parameters}")
        if execution_time:
            logger.debug(f"Execution Time: {execution_time:.3f}s")
        logger.debug("=" * 30)
    
    @staticmethod
    def format_error_context(
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Formatea contexto de error para debugging"""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {}
        }
        return json.dumps(error_info, indent=2, default=str)
    
    @staticmethod
    def compare_calculations(
        calc1: Any,
        calc2: Any,
        label1: str = "Calculation 1",
        label2: str = "Calculation 2"
    ) -> Dict[str, Any]:
        """Compara dos cálculos y muestra diferencias"""
        differences = {}
        
        fields = [
            "total_hours", "regular_hours", "overtime_hours",
            "gross_pay", "total_deductions", "net_pay"
        ]
        
        for field in fields:
            val1 = getattr(calc1, field, None)
            val2 = getattr(calc2, field, None)
            
            if val1 is not None and val2 is not None:
                diff = abs(val1 - val2)
                if diff > Decimal("0.01"):
                    differences[field] = {
                        label1: val1,
                        label2: val2,
                        "difference": diff
                    }
        
        return differences


def debug_timing(func: Callable[..., T]) -> Callable[..., T]:
    """Decorador para medir tiempo de ejecución"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(
                f"{func.__name__} executed in {execution_time:.3f}s"
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {execution_time:.3f}s: {e}"
            )
            raise
    
    return wrapper


@contextmanager
def debug_context(name: str, log_input: bool = False, log_output: bool = False):
    """Context manager para debugging con timing"""
    start_time = time.time()
    logger.debug(f"Starting {name}")
    
    try:
        yield
        execution_time = time.time() - start_time
        logger.debug(f"Completed {name} in {execution_time:.3f}s")
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Failed {name} after {execution_time:.3f}s: {e}")
        raise


class PayrollProfiler:
    """Profiler para operaciones de nómina"""
    
    def __init__(self):
        self.operations: Dict[str, List[float]] = {}
    
    def record_operation(self, operation_name: str, duration: float) -> None:
        """Registra duración de una operación"""
        if operation_name not in self.operations:
            self.operations[operation_name] = []
        self.operations[operation_name].append(duration)
    
    def get_statistics(self) -> Dict[str, Dict[str, float]]:
        """Obtiene estadísticas de operaciones"""
        stats = {}
        
        for operation, durations in self.operations.items():
            if durations:
                stats[operation] = {
                    "count": len(durations),
                    "total": sum(durations),
                    "average": sum(durations) / len(durations),
                    "min": min(durations),
                    "max": max(durations)
                }
        
        return stats
    
    def print_statistics(self) -> None:
        """Imprime estadísticas formateadas"""
        stats = self.get_statistics()
        
        logger.info("=== Payroll Performance Statistics ===")
        for operation, stat in stats.items():
            logger.info(
                f"{operation}: "
                f"count={stat['count']}, "
                f"avg={stat['average']:.3f}s, "
                f"min={stat['min']:.3f}s, "
                f"max={stat['max']:.3f}s"
            )
        logger.info("=" * 40)


def log_function_call(
    func_name: str,
    args: tuple = (),
    kwargs: Optional[Dict[str, Any]] = None,
    result: Optional[Any] = None,
    execution_time: Optional[float] = None
) -> None:
    """Log de llamada a función con detalles"""
    logger.debug(f"=== Function Call: {func_name} ===")
    
    if args:
        logger.debug(f"Args: {args}")
    
    if kwargs:
        logger.debug(f"Kwargs: {kwargs}")
    
    if result is not None:
        logger.debug(f"Result: {result}")
    
    if execution_time:
        logger.debug(f"Execution Time: {execution_time:.3f}s")
    
    logger.debug("=" * 30)


class PayrollDataInspector:
    """Inspector de datos para debugging"""
    
    @staticmethod
    def inspect_employee(employee: Dict[str, Any]) -> Dict[str, Any]:
        """Inspecciona datos de empleado"""
        return {
            "id": employee.get("employee_id"),
            "name": employee.get("name"),
            "type": employee.get("employee_type"),
            "rate": employee.get("hourly_rate"),
            "salary": employee.get("salary_monthly"),
            "active": employee.get("active"),
            "department": employee.get("department")
        }
    
    @staticmethod
    def inspect_time_entry(entry: Any) -> Dict[str, Any]:
        """Inspecciona entrada de tiempo"""
        return {
            "employee_id": getattr(entry, "employee_id", None),
            "work_date": str(getattr(entry, "work_date", None)),
            "clock_in": str(getattr(entry, "clock_in", None)),
            "clock_out": str(getattr(entry, "clock_out", None)),
            "hours_worked": str(getattr(entry, "hours_worked", None)),
            "hours_type": str(getattr(entry, "hours_type", None)),
            "hourly_rate": str(getattr(entry, "hourly_rate", None))
        }
    
    @staticmethod
    def inspect_calculation(calculation: Any) -> Dict[str, Any]:
        """Inspecciona cálculo de pago"""
        return {
            "employee_id": getattr(calculation, "employee_id", None),
            "period_start": str(getattr(calculation, "period_start", None)),
            "period_end": str(getattr(calculation, "period_end", None)),
            "total_hours": str(getattr(calculation, "total_hours", None)),
            "regular_hours": str(getattr(calculation, "regular_hours", None)),
            "overtime_hours": str(getattr(calculation, "overtime_hours", None)),
            "gross_pay": str(getattr(calculation, "gross_pay", None)),
            "total_deductions": str(getattr(calculation, "total_deductions", None)),
            "net_pay": str(getattr(calculation, "net_pay", None))
        }


def enable_debug_mode(enable: bool = True) -> None:
    """Habilita/deshabilita modo debug"""
    if enable:
        logging.getLogger("payroll").setLevel(logging.DEBUG)
        logger.info("Debug mode enabled")
    else:
        logging.getLogger("payroll").setLevel(logging.INFO)
        logger.info("Debug mode disabled")


def validate_data_integrity(
    employee_id: str,
    calculation: Any,
    time_entries: List[Any],
    expenses: List[Any]
) -> Dict[str, Any]:
    """Valida integridad de datos para debugging"""
    issues = []
    warnings = []
    
    # Validar que horas sumen correctamente
    total_hours = sum(
        getattr(entry, "hours_worked", Decimal("0.00"))
        for entry in time_entries
    )
    
    if abs(total_hours - calculation.total_hours) > Decimal("0.01"):
        issues.append(
            f"Hours mismatch: entries={total_hours}, calculation={calculation.total_hours}"
        )
    
    # Validar que expenses sumen correctamente
    total_expenses = sum(
        getattr(exp, "amount", Decimal("0.00"))
        for exp in expenses
    )
    
    if abs(total_expenses - calculation.total_expenses) > Decimal("0.01"):
        issues.append(
            f"Expenses mismatch: list={total_expenses}, calculation={calculation.total_expenses}"
        )
    
    # Validar cálculo neto
    expected_net = (
        calculation.gross_pay -
        calculation.total_deductions +
        calculation.total_expenses
    )
    
    if abs(expected_net - calculation.net_pay) > Decimal("0.01"):
        issues.append(
            f"Net pay mismatch: expected={expected_net}, actual={calculation.net_pay}"
        )
    
    return {
        "employee_id": employee_id,
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "timestamp": datetime.now().isoformat()
    }



