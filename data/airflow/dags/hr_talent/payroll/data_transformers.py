"""
Transformadores de Datos para Nómina
Funciones para transformar, normalizar y limpiar datos de nómina
"""

import logging
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, Any, Optional, List, Callable, Union
import re

logger = logging.getLogger(__name__)


class PayrollDataTransformer:
    """Transformador de datos para nómina"""
    
    @staticmethod
    def normalize_employee_id(employee_id: str) -> str:
        """
        Normaliza un employee ID a formato estándar
        
        Args:
            employee_id: ID de empleado en cualquier formato
        
        Returns:
            ID normalizado (ej: EMP001)
        """
        if not employee_id:
            return ""
        
        # Remover espacios y convertir a mayúsculas
        normalized = employee_id.strip().upper()
        
        # Remover caracteres especiales excepto guiones
        normalized = re.sub(r'[^A-Z0-9\-]', '', normalized)
        
        # Si tiene formato numérico, agregar prefijo
        if normalized.isdigit():
            normalized = f"EMP{normalized.zfill(3)}"
        
        # Si tiene formato con prefijo, asegurar formato consistente
        match = re.match(r'([A-Z]+)[-]?(\d+)', normalized)
        if match:
            prefix = match.group(1)
            number = match.group(2).zfill(3)
            normalized = f"{prefix}{number}"
        
        return normalized
    
    @staticmethod
    def normalize_currency(
        value: Any,
        default: Decimal = Decimal("0.00")
    ) -> Decimal:
        """
        Normaliza un valor a Decimal de moneda
        
        Args:
            value: Valor a normalizar (str, int, float, Decimal)
            default: Valor por defecto si falla
        
        Returns:
            Decimal normalizado
        """
        if value is None:
            return default
        
        if isinstance(value, Decimal):
            return value.quantize(Decimal("0.01"))
        
        if isinstance(value, (int, float)):
            try:
                return Decimal(str(value)).quantize(Decimal("0.01"))
            except (InvalidOperation, ValueError):
                return default
        
        if isinstance(value, str):
            # Remover símbolos de moneda y comas
            cleaned = value.replace("$", "").replace(",", "").strip()
            try:
                return Decimal(cleaned).quantize(Decimal("0.01"))
            except (InvalidOperation, ValueError):
                return default
        
        return default
    
    @staticmethod
    def normalize_hours(
        value: Any,
        default: Decimal = Decimal("0.00")
    ) -> Decimal:
        """
        Normaliza un valor a horas (Decimal)
        
        Args:
            value: Valor a normalizar
            default: Valor por defecto
        
        Returns:
            Decimal de horas
        """
        if value is None:
            return default
        
        if isinstance(value, Decimal):
            return value.quantize(Decimal("0.01"))
        
        if isinstance(value, (int, float)):
            try:
                return Decimal(str(value)).quantize(Decimal("0.01"))
            except (InvalidOperation, ValueError):
                return default
        
        if isinstance(value, str):
            # Intentar parsear formato "8h 30m" o "8.5"
            cleaned = value.strip().lower()
            
            # Formato "8h 30m"
            hour_match = re.match(r'(\d+)h\s*(\d+)m', cleaned)
            if hour_match:
                hours = Decimal(hour_match.group(1))
                minutes = Decimal(hour_match.group(2))
                total = hours + (minutes / Decimal("60"))
                return total.quantize(Decimal("0.01"))
            
            # Formato decimal simple
            try:
                return Decimal(cleaned).quantize(Decimal("0.01"))
            except (InvalidOperation, ValueError):
                return default
        
        return default
    
    @staticmethod
    def normalize_date(
        value: Any,
        default: Optional[date] = None
    ) -> Optional[date]:
        """
        Normaliza un valor a fecha
        
        Args:
            value: Valor a normalizar (str, date, datetime)
            default: Valor por defecto
        
        Returns:
            date o None
        """
        if value is None:
            return default
        
        if isinstance(value, date):
            return value
        
        if isinstance(value, datetime):
            return value.date()
        
        if isinstance(value, str):
            # Intentar varios formatos
            formats = [
                "%Y-%m-%d",
                "%m/%d/%Y",
                "%d/%m/%Y",
                "%Y/%m/%d",
                "%m-%d-%Y",
                "%d-%m-%Y"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(value.strip(), fmt).date()
                except ValueError:
                    continue
        
        return default
    
    @staticmethod
    def clean_string(value: Any, default: str = "") -> str:
        """
        Limpia y normaliza un string
        
        Args:
            value: Valor a limpiar
            default: Valor por defecto
        
        Returns:
            String limpio
        """
        if value is None:
            return default
        
        if not isinstance(value, str):
            value = str(value)
        
        # Remover espacios al inicio y final
        cleaned = value.strip()
        
        # Normalizar espacios múltiples
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned
    
    @staticmethod
    def transform_time_entry(
        entry: Dict[str, Any],
        employee_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transforma una entrada de tiempo a formato estándar
        
        Args:
            entry: Diccionario con datos de entrada
            employee_id: ID de empleado (se normaliza si está en entry)
        
        Returns:
            Diccionario normalizado
        """
        transformer = PayrollDataTransformer()
        
        result = {}
        
        # Normalizar employee_id
        if employee_id:
            result["employee_id"] = transformer.normalize_employee_id(employee_id)
        elif "employee_id" in entry:
            result["employee_id"] = transformer.normalize_employee_id(entry["employee_id"])
        
        # Normalizar fecha
        if "work_date" in entry:
            result["work_date"] = transformer.normalize_date(entry["work_date"])
        
        # Normalizar horas
        if "hours_worked" in entry:
            result["hours_worked"] = transformer.normalize_hours(entry["hours_worked"])
        
        # Normalizar tarifa
        if "hourly_rate" in entry:
            result["hourly_rate"] = transformer.normalize_currency(entry["hourly_rate"])
        
        # Limpiar strings
        for field in ["description", "project_code", "hours_type"]:
            if field in entry:
                result[field] = transformer.clean_string(entry[field])
        
        # Copiar otros campos
        for field in ["clock_in", "clock_out"]:
            if field in entry:
                result[field] = entry[field]
        
        return result
    
    @staticmethod
    def transform_employee(
        employee: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transforma datos de empleado a formato estándar
        
        Args:
            employee: Diccionario con datos de empleado
        
        Returns:
            Diccionario normalizado
        """
        transformer = PayrollDataTransformer()
        
        result = {}
        
        # Normalizar employee_id
        if "employee_id" in employee:
            result["employee_id"] = transformer.normalize_employee_id(employee["employee_id"])
        
        # Limpiar strings
        for field in ["name", "email", "position", "department", "employee_type"]:
            if field in employee:
                result[field] = transformer.clean_string(employee[field])
        
        # Normalizar valores numéricos
        if "hourly_rate" in employee:
            result["hourly_rate"] = transformer.normalize_currency(employee["hourly_rate"])
        
        if "salary_monthly" in employee:
            result["salary_monthly"] = transformer.normalize_currency(employee["salary_monthly"])
        
        if "tax_rate" in employee:
            result["tax_rate"] = transformer.normalize_currency(employee["tax_rate"])
        
        if "benefits_rate" in employee:
            result["benefits_rate"] = transformer.normalize_currency(employee["benefits_rate"])
        
        # Normalizar fechas
        for field in ["start_date", "end_date"]:
            if field in employee:
                result[field] = transformer.normalize_date(employee[field])
        
        # Copiar campos booleanos y otros
        for field in ["active", "metadata"]:
            if field in employee:
                result[field] = employee[field]
        
        return result
    
    @staticmethod
    def validate_and_transform(
        data: Dict[str, Any],
        schema: Dict[str, Callable],
        strict: bool = False
    ) -> Dict[str, Any]:
        """
        Valida y transforma datos según un schema
        
        Args:
            data: Datos a validar/transformar
            schema: Dict con campo -> función transformadora
            strict: Si True, falla si falta un campo requerido
        
        Returns:
            Dict transformado
        """
        result = {}
        errors = []
        
        for field, transformer in schema.items():
            if field not in data:
                if strict:
                    errors.append(f"Missing required field: {field}")
                continue
            
            try:
                result[field] = transformer(data[field])
            except Exception as e:
                errors.append(f"Error transforming {field}: {e}")
                if strict:
                    raise ValueError(f"Failed to transform {field}: {e}")
        
        if errors and not strict:
            logger.warning(f"Transformation warnings: {errors}")
        
        return result


def normalize_payroll_data(
    data: Dict[str, Any],
    data_type: str = "time_entry"
) -> Dict[str, Any]:
    """
    Función de conveniencia para normalizar datos de nómina
    
    Args:
        data: Datos a normalizar
        data_type: Tipo de datos (time_entry, employee, expense)
    
    Returns:
        Dict normalizado
    """
    transformer = PayrollDataTransformer()
    
    if data_type == "time_entry":
        return transformer.transform_time_entry(data)
    elif data_type == "employee":
        return transformer.transform_employee(data)
    else:
        # Normalización genérica
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = transformer.clean_string(value)
            elif isinstance(value, (int, float)):
                result[key] = transformer.normalize_currency(value)
            else:
                result[key] = value
        return result


