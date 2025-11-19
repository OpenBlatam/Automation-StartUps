"""
Validadores modulares para datos de ads.

Incluye:
- Validación de esquemas
- Validación de valores
- Validación de rangos
- Validación de consistencia
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Resultado de una validación."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    metrics: Optional[Dict[str, Any]] = None
    
    def __str__(self) -> str:
        if self.valid:
            return "Validation passed"
        return f"Validation failed: {', '.join(self.errors)}"


class BaseValidator(ABC):
    """Validador base."""
    
    @abstractmethod
    def validate(self, data: Any) -> ValidationResult:
        """Valida datos."""
        pass


class SchemaValidator(BaseValidator):
    """Valida que los datos cumplan con un schema esperado."""
    
    def __init__(self, required_fields: List[str], optional_fields: Optional[List[str]] = None):
        """
        Inicializa el validador de schema.
        
        Args:
            required_fields: Campos requeridos
            optional_fields: Campos opcionales
        """
        self.required_fields = required_fields
        self.optional_fields = optional_fields or []
    
    def validate(self, data: List[Dict[str, Any]]) -> ValidationResult:
        """Valida que todos los registros tengan los campos requeridos."""
        errors = []
        warnings = []
        valid_count = 0
        invalid_count = 0
        
        for i, record in enumerate(data):
            record_errors = []
            
            # Verificar campos requeridos
            for field in self.required_fields:
                if field not in record or record[field] is None:
                    record_errors.append(f"Campo requerido '{field}' faltante")
            
            if record_errors:
                errors.extend([f"Registro #{i+1}: {e}" for e in record_errors])
                invalid_count += 1
            else:
                valid_count += 1
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metrics={
                "total_records": len(data),
                "valid_records": valid_count,
                "invalid_records": invalid_count
            }
        )


class ValueValidator(BaseValidator):
    """Valida valores de campos."""
    
    def __init__(self, rules: Dict[str, Dict[str, Any]]):
        """
        Inicializa el validador de valores.
        
        Args:
            rules: Diccionario con reglas por campo
                   Ejemplo: {"spend": {"min": 0}, "ctr": {"min": 0, "max": 100}}
        """
        self.rules = rules
    
    def validate(self, data: List[Dict[str, Any]]) -> ValidationResult:
        """Valida valores según las reglas."""
        errors = []
        warnings = []
        invalid_records = 0
        
        for i, record in enumerate(data):
            record_errors = []
            
            for field, rule in self.rules.items():
                value = record.get(field)
                if value is None:
                    continue  # Ya validado por SchemaValidator
                
                # Validar mínimo
                if "min" in rule:
                    try:
                        if float(value) < rule["min"]:
                            record_errors.append(
                                f"Campo '{field}' ({value}) es menor que mínimo ({rule['min']})"
                            )
                    except (ValueError, TypeError):
                        record_errors.append(f"Campo '{field}' no es numérico")
                
                # Validar máximo
                if "max" in rule:
                    try:
                        if float(value) > rule["max"]:
                            record_errors.append(
                                f"Campo '{field}' ({value}) es mayor que máximo ({rule['max']})"
                            )
                    except (ValueError, TypeError):
                        record_errors.append(f"Campo '{field}' no es numérico")
                
                # Validar valores permitidos
                if "allowed_values" in rule:
                    if value not in rule["allowed_values"]:
                        record_errors.append(
                            f"Campo '{field}' ({value}) no está en valores permitidos"
                        )
            
            if record_errors:
                errors.extend([f"Registro #{i+1}: {e}" for e in record_errors])
                invalid_records += 1
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metrics={"invalid_records": invalid_records}
        )


class ConsistencyValidator(BaseValidator):
    """Valida consistencia entre campos relacionados."""
    
    def validate(self, data: List[Dict[str, Any]]) -> ValidationResult:
        """Valida consistencia de datos."""
        errors = []
        warnings = []
        
        for i, record in enumerate(data):
            # CTR debe ser consistente con clicks/impressions
            impressions = record.get("impressions", 0) or 0
            clicks = record.get("clicks", 0) or 0
            ctr = record.get("ctr", 0) or 0
            
            if impressions > 0 and clicks > 0:
                calculated_ctr = (clicks / impressions * 100)
                if abs(ctr - calculated_ctr) > 1.0:  # Tolerancia de 1%
                    warnings.append(
                        f"Registro #{i+1}: CTR reportado ({ctr}%) "
                        f"difiere del calculado ({calculated_ctr:.2f}%)"
                    )
            
            # CPC debe ser consistente con spend/clicks
            spend = record.get("spend", 0) or 0
            cpc = record.get("cpc", 0) or 0
            
            if clicks > 0 and spend > 0:
                calculated_cpc = spend / clicks
                if abs(cpc - calculated_cpc) > 0.01:  # Tolerancia de $0.01
                    warnings.append(
                        f"Registro #{i+1}: CPC reportado ({cpc}) "
                        f"difiere del calculado ({calculated_cpc:.4f})"
                    )
            
            # Conversiones no pueden ser negativas
            conversions = record.get("conversions", 0) or 0
            if conversions < 0:
                errors.append(f"Registro #{i+1}: Conversiones no pueden ser negativas")
            
            # Impresiones >= clicks
            if impressions < clicks:
                errors.append(
                    f"Registro #{i+1}: Impresiones ({impressions}) "
                    f"no pueden ser menores que clics ({clicks})"
                )
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


class CompletenessValidator(BaseValidator):
    """Valida completitud de datos."""
    
    def __init__(self, min_records: int = 1, min_impressions: int = 0):
        """
        Inicializa el validador de completitud.
        
        Args:
            min_records: Mínimo de registros esperados
            min_impressions: Mínimo de impresiones totales esperadas
        """
        self.min_records = min_records
        self.min_impressions = min_impressions
    
    def validate(self, data: List[Dict[str, Any]]) -> ValidationResult:
        """Valida completitud de datos."""
        errors = []
        warnings = []
        
        if len(data) < self.min_records:
            errors.append(
                f"Se encontraron solo {len(data)} registros, "
                f"se esperaban al menos {self.min_records}"
            )
        
        total_impressions = sum(r.get("impressions", 0) or 0 for r in data)
        if total_impressions < self.min_impressions:
            warnings.append(
                f"Total de impresiones ({total_impressions}) es menor que "
                f"el mínimo esperado ({self.min_impressions})"
            )
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metrics={
                "total_records": len(data),
                "total_impressions": total_impressions
            }
        )


def validate_campaign_data(
    data: List[Dict[str, Any]],
    strict: bool = False
) -> ValidationResult:
    """
    Valida datos de campañas con múltiples validadores.
    
    Args:
        data: Lista de datos de campañas
        strict: Si usar validación estricta (default: False)
        
    Returns:
        ValidationResult agregado
    """
    all_errors = []
    all_warnings = []
    all_metrics = {}
    
    # Schema validation
    schema_validator = SchemaValidator(
        required_fields=[
            "campaign_id", "impressions", "clicks", "spend", "conversions"
        ]
    )
    schema_result = schema_validator.validate(data)
    all_errors.extend(schema_result.errors)
    all_warnings.extend(schema_result.warnings)
    if schema_result.metrics:
        all_metrics.update(schema_result.metrics)
    
    if not schema_result.valid and strict:
        return ValidationResult(
            valid=False,
            errors=all_errors,
            warnings=all_warnings,
            metrics=all_metrics
        )
    
    # Value validation
    value_validator = ValueValidator({
        "impressions": {"min": 0},
        "clicks": {"min": 0},
        "spend": {"min": 0},
        "conversions": {"min": 0},
        "ctr": {"min": 0, "max": 100},
        "cpc": {"min": 0},
        "cpa": {"min": 0},
    })
    value_result = value_validator.validate(data)
    all_errors.extend(value_result.errors)
    all_warnings.extend(value_result.warnings)
    
    # Consistency validation
    consistency_validator = ConsistencyValidator()
    consistency_result = consistency_validator.validate(data)
    all_errors.extend(consistency_result.errors)
    all_warnings.extend(consistency_result.warnings)
    
    # Completeness validation
    completeness_validator = CompletenessValidator(
        min_records=1,
        min_impressions=0
    )
    completeness_result = completeness_validator.validate(data)
    all_errors.extend(completeness_result.errors)
    all_warnings.extend(completeness_result.warnings)
    if completeness_result.metrics:
        all_metrics.update(completeness_result.metrics)
    
    return ValidationResult(
        valid=len(all_errors) == 0,
        errors=all_errors,
        warnings=all_warnings,
        metrics=all_metrics
    )

