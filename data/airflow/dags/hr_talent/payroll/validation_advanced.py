"""
Validaciones Avanzadas para Nómina
Validaciones adicionales y reglas de negocio complejas
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationRule:
    """Regla de validación"""
    name: str
    description: str
    severity: str  # error, warning, info
    check_function: callable
    error_message: str


class AdvancedPayrollValidator:
    """Validador avanzado con reglas personalizables"""
    
    def __init__(self):
        """Inicializa validador con reglas por defecto"""
        self.rules: List[ValidationRule] = []
        self._load_default_rules()
    
    def _load_default_rules(self) -> None:
        """Carga reglas de validación por defecto"""
        # Regla: Horas no pueden exceder 80 por semana
        self.rules.append(ValidationRule(
            name="max_weekly_hours",
            description="Maximum 80 hours per week",
            severity="error",
            check_function=self._check_max_weekly_hours,
            error_message="Total hours exceed 80 hours per week"
        ))
        
        # Regla: Pago neto no puede ser negativo
        self.rules.append(ValidationRule(
            name="non_negative_net_pay",
            description="Net pay cannot be negative",
            severity="error",
            check_function=self._check_non_negative_net_pay,
            error_message="Net pay cannot be negative"
        ))
        
        # Regla: Deducciones no pueden exceder 50% del bruto
        self.rules.append(ValidationRule(
            name="max_deductions",
            description="Deductions cannot exceed 50% of gross",
            severity="warning",
            check_function=self._check_max_deductions,
            error_message="Deductions exceed 50% of gross pay"
        ))
        
        # Regla: Overtime debe ser al menos 1.5x la tarifa regular
        self.rules.append(ValidationRule(
            name="overtime_rate",
            description="Overtime rate must be at least 1.5x regular rate",
            severity="error",
            check_function=self._check_overtime_rate,
            error_message="Overtime rate below minimum required"
        ))
    
    def _check_max_weekly_hours(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Verifica horas máximas por semana"""
        total_hours = data.get("total_hours", Decimal("0.00"))
        if total_hours > Decimal("80.0"):
            return False, f"Total hours {total_hours} exceed 80 hours per week"
        return True, None
    
    def _check_non_negative_net_pay(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Verifica que el pago neto no sea negativo"""
        net_pay = data.get("net_pay", Decimal("0.00"))
        if net_pay < Decimal("0.00"):
            return False, f"Net pay {net_pay} is negative"
        return True, None
    
    def _check_max_deductions(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Verifica que las deducciones no excedan 50% del bruto"""
        gross_pay = data.get("gross_pay", Decimal("0.00"))
        total_deductions = data.get("total_deductions", Decimal("0.00"))
        
        if gross_pay > Decimal("0.00"):
            deduction_rate = total_deductions / gross_pay
            if deduction_rate > Decimal("0.50"):
                return False, f"Deduction rate {deduction_rate:.2%} exceeds 50%"
        return True, None
    
    def _check_overtime_rate(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Verifica rate de overtime"""
        hourly_rate = data.get("hourly_rate", Decimal("0.00"))
        overtime_rate = data.get("overtime_rate", Decimal("0.00"))
        
        if hourly_rate > Decimal("0.00") and overtime_rate > Decimal("0.00"):
            expected_min = hourly_rate * Decimal("1.5")
            if overtime_rate < expected_min:
                return False, f"Overtime rate {overtime_rate} below minimum {expected_min}"
        return True, None
    
    def add_rule(
        self,
        name: str,
        description: str,
        severity: str,
        check_function: callable,
        error_message: str
    ) -> None:
        """Agrega una regla de validación personalizada"""
        rule = ValidationRule(
            name=name,
            description=description,
            severity=severity,
            check_function=check_function,
            error_message=error_message
        )
        self.rules.append(rule)
    
    def validate(
        self,
        data: Dict[str, Any],
        rule_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta validaciones
        
        Args:
            data: Datos a validar
            rule_names: Lista de nombres de reglas a ejecutar (None = todas)
        
        Returns:
            Dict con resultados de validación
        """
        errors = []
        warnings = []
        info = []
        
        rules_to_check = (
            [r for r in self.rules if r.name in rule_names]
            if rule_names
            else self.rules
        )
        
        for rule in rules_to_check:
            try:
                is_valid, message = rule.check_function(data)
                
                if not is_valid:
                    if rule.severity == "error":
                        errors.append({
                            "rule": rule.name,
                            "message": message or rule.error_message,
                            "severity": rule.severity
                        })
                    elif rule.severity == "warning":
                        warnings.append({
                            "rule": rule.name,
                            "message": message or rule.error_message,
                            "severity": rule.severity
                        })
                    else:
                        info.append({
                            "rule": rule.name,
                            "message": message or rule.error_message,
                            "severity": rule.severity
                        })
            except Exception as e:
                logger.error(f"Error executing validation rule {rule.name}: {e}")
                errors.append({
                    "rule": rule.name,
                    "message": f"Validation rule error: {e}",
                    "severity": "error"
                })
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "info": info,
            "total_checks": len(rules_to_check),
            "passed": len(rules_to_check) - len(errors) - len(warnings) - len(info)
        }
    
    def validate_pay_period_calculation(
        self,
        calculation: Any  # PayPeriodCalculation
    ) -> Dict[str, Any]:
        """Valida un cálculo de período de pago"""
        data = {
            "total_hours": calculation.total_hours,
            "gross_pay": calculation.gross_pay,
            "net_pay": calculation.net_pay,
            "total_deductions": calculation.total_deductions,
            "regular_hours": calculation.regular_hours,
            "overtime_hours": calculation.overtime_hours
        }
        
        return self.validate(data)
    
    def validate_employee_data(
        self,
        employee: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Valida datos de empleado"""
        data = {
            "hourly_rate": employee.get("hourly_rate", Decimal("0.00")),
            "employee_type": employee.get("employee_type", "hourly"),
            "active": employee.get("active", True)
        }
        
        # Agregar validaciones específicas de empleado
        errors = []
        warnings = []
        
        # Validar tarifa mínima
        if data["hourly_rate"] < Decimal("7.25"):
            errors.append({
                "rule": "minimum_wage",
                "message": f"Hourly rate {data['hourly_rate']} below minimum wage",
                "severity": "error"
            })
        
        # Validar tipo de empleado
        if data["employee_type"] not in ["hourly", "salaried"]:
            errors.append({
                "rule": "employee_type",
                "message": f"Invalid employee type: {data['employee_type']}",
                "severity": "error"
            })
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "info": [],
            "total_checks": len(errors) + len(warnings),
            "passed": len(warnings)
        }

