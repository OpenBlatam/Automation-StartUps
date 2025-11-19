"""
Calculadora de Deducciones
Maneja el cálculo de impuestos, beneficios, y otras deducciones
"""

import logging
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List, Optional, Dict, Any
import json


logger = logging.getLogger(__name__)


@dataclass
class DeductionRule:
    """Regla de deducción"""
    rule_name: str
    deduction_type: str
    employee_type: Optional[str] = None  # None = aplica a todos
    amount_type: str = "percentage"  # fixed, percentage, formula
    amount_value: Optional[Decimal] = None  # Para fixed
    percentage_value: Optional[Decimal] = None  # Para percentage
    formula: Optional[str] = None  # Para formula
    conditions: Optional[Dict[str, Any]] = None
    priority: int = 0


@dataclass
class Deduction:
    """Deducción calculada"""
    deduction_type: str
    amount: Decimal
    description: str
    rule_applied: Optional[str] = None


class DeductionCalculator:
    """Calculadora de deducciones"""
    
    def __init__(
        self,
        default_tax_rate: Decimal = Decimal("0.25"),
        default_benefits_rate: Decimal = Decimal("0.10"),
    ):
        """
        Args:
            default_tax_rate: Tasa de impuestos por defecto (default: 25%)
            default_benefits_rate: Tasa de beneficios por defecto (default: 10%)
        """
        self.default_tax_rate = default_tax_rate
        self.default_benefits_rate = default_benefits_rate
        self.rules: List[DeductionRule] = []
    
    def add_rule(self, rule: DeductionRule) -> None:
        """Agrega una regla de deducción"""
        self.rules.append(rule)
        # Ordenar por prioridad (mayor prioridad primero)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def calculate_deductions(
        self,
        gross_pay: Decimal,
        employee_type: str,
        employee_id: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> List[Deduction]:
        """
        Calcula todas las deducciones aplicables
        
        Args:
            gross_pay: Pago bruto
            employee_type: Tipo de empleado (hourly, salaried, contractor)
            employee_id: ID del empleado (opcional)
            additional_context: Contexto adicional para fórmulas (opcional)
        
        Returns:
            Lista de deducciones calculadas
        """
        deductions: List[Deduction] = []
        
        # Aplicar reglas personalizadas
        for rule in self.rules:
            if not self._rule_applies(rule, employee_type):
                continue
            
            if not self._check_conditions(rule, gross_pay, additional_context):
                continue
            
            amount = self._calculate_deduction_amount(
                rule, gross_pay, additional_context
            )
            
            if amount > Decimal("0.00"):
                deductions.append(Deduction(
                    deduction_type=rule.deduction_type,
                    amount=amount,
                    description=f"{rule.rule_name} ({rule.deduction_type})",
                    rule_applied=rule.rule_name
                ))
        
        # Si no hay reglas específicas, aplicar defaults
        if not deductions:
            # Impuestos
            tax_amount = gross_pay * self.default_tax_rate
            deductions.append(Deduction(
                deduction_type="impuestos",
                amount=tax_amount,
                description=f"Impuestos ({self.default_tax_rate * 100}%)"
            ))
            
            # Beneficios
            benefits_amount = gross_pay * self.default_benefits_rate
            deductions.append(Deduction(
                deduction_type="beneficios",
                amount=benefits_amount,
                description=f"Beneficios ({self.default_benefits_rate * 100}%)"
            ))
        
        return deductions
    
    def calculate_total_deductions(
        self,
        gross_pay: Decimal,
        employee_type: str,
        employee_id: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Decimal:
        """Calcula el total de deducciones"""
        deductions = self.calculate_deductions(
            gross_pay, employee_type, employee_id, additional_context
        )
        total = sum(d.amount for d in deductions)
        return total.quantize(Decimal("0.01"))
    
    def _rule_applies(self, rule: DeductionRule, employee_type: str) -> bool:
        """Verifica si una regla aplica a un tipo de empleado"""
        if rule.employee_type is None:
            return True
        return rule.employee_type == employee_type
    
    def _check_conditions(
        self,
        rule: DeductionRule,
        gross_pay: Decimal,
        additional_context: Optional[Dict[str, Any]]
    ) -> bool:
        """Verifica condiciones de una regla"""
        if not rule.conditions:
            return True
        
        # Verificar mínimo de pago bruto
        if "min_gross_pay" in rule.conditions:
            min_gross = Decimal(str(rule.conditions["min_gross_pay"]))
            if gross_pay < min_gross:
                return False
        
        # Verificar máximo de pago bruto
        if "max_gross_pay" in rule.conditions:
            max_gross = Decimal(str(rule.conditions["max_gross_pay"]))
            if gross_pay > max_gross:
                return False
        
        # Verificar máximo de deducción
        if "max_deduction_amount" in rule.conditions:
            max_deduction = Decimal(str(rule.conditions["max_deduction_amount"]))
            # Calcular deducción primero
            amount = self._calculate_deduction_amount(rule, gross_pay, additional_context)
            if amount > max_deduction:
                return False
        
        # Verificar condiciones personalizadas desde contexto
        if additional_context and "custom_conditions" in rule.conditions:
            custom_conditions = rule.conditions["custom_conditions"]
            # Evaluar condiciones personalizadas (simplificado)
            for key, expected_value in custom_conditions.items():
                if additional_context.get(key) != expected_value:
                    return False
        
        return True
    
    def _calculate_deduction_amount(
        self,
        rule: DeductionRule,
        gross_pay: Decimal,
        additional_context: Optional[Dict[str, Any]]
    ) -> Decimal:
        """Calcula el monto de una deducción basado en la regla"""
        if rule.amount_type == "fixed":
            if rule.amount_value is None:
                return Decimal("0.00")
            return rule.amount_value
        
        elif rule.amount_type == "percentage":
            if rule.percentage_value is None:
                return Decimal("0.00")
            return gross_pay * rule.percentage_value
        
        elif rule.amount_type == "formula":
            if not rule.formula:
                return Decimal("0.00")
            # Evaluar fórmula simple (ej: "gross_pay * 0.25")
            try:
                # Reemplazar variables en la fórmula
                formula = rule.formula
                formula = formula.replace("gross_pay", str(gross_pay))
                
                # Si hay contexto adicional, reemplazar también
                if additional_context:
                    for key, value in additional_context.items():
                        formula = formula.replace(key, str(value))
                
                # Evaluar fórmula (SIMPLE - solo operaciones aritméticas básicas)
                # En producción, usar una librería más segura como `asteval`
                result = eval(formula, {"__builtins__": {}}, {})
                return Decimal(str(result)).quantize(Decimal("0.01"))
            except Exception as e:
                logger.error(f"Error evaluating formula '{rule.formula}': {e}")
                return Decimal("0.00")
        
        return Decimal("0.00")





