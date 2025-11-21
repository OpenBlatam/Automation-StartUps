"""
Excepciones personalizadas para el módulo de nómina
"""

from typing import Optional, Dict, Any


class PayrollError(Exception):
    """Excepción base para errores de nómina"""
    
    def __init__(
        self,
        message: str,
        employee_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.employee_id = employee_id
        self.context = context or {}
    
    def __str__(self) -> str:
        base = self.message
        if self.employee_id:
            base = f"[Employee: {self.employee_id}] {base}"
        if self.context:
            base += f" | Context: {self.context}"
        return base
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte excepción a diccionario para logging"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "employee_id": self.employee_id,
            "context": self.context
        }


class ConfigurationError(PayrollError):
    """Error de configuración"""
    pass


class ValidationError(PayrollError):
    """Error de validación de datos"""
    pass


class CalculationError(PayrollError):
    """Error en cálculo de nómina"""
    pass


class OCRError(PayrollError):
    """Error en procesamiento OCR"""
    pass


class StorageError(PayrollError):
    """Error en almacenamiento de datos"""
    pass


class EmployeeNotFoundError(PayrollError):
    """Empleado no encontrado"""
    pass





