"""
Motor de Reglas de Negocio para Sistema de Soporte.

Permite definir reglas complejas y dinámicas para el procesamiento de tickets.
"""
import logging
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Tipos de reglas."""
    PRIORITY = "priority"
    ROUTING = "routing"
    ESCALATION = "escalation"
    NOTIFICATION = "notification"
    TAG = "tag"
    AUTO_RESPONSE = "auto_response"
    SLA = "sla"
    CUSTOM = "custom"


class Operator(Enum):
    """Operadores para condiciones."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    IN = "in"
    NOT_IN = "not_in"
    REGEX = "regex"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


@dataclass
class RuleCondition:
    """Condición de regla."""
    field: str
    operator: Operator
    value: Any
    case_sensitive: bool = False


@dataclass
class RuleAction:
    """Acción de regla."""
    type: str
    params: Dict[str, Any]


@dataclass
class BusinessRule:
    """Regla de negocio."""
    rule_id: str
    name: str
    description: str
    rule_type: RuleType
    priority: int  # Mayor = más importante
    enabled: bool = True
    
    conditions: List[RuleCondition]
    actions: List[RuleAction]
    
    # Metadata
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Límites
    max_executions: Optional[int] = None  # None = ilimitado
    execution_count: int = 0
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Evalúa si la regla se cumple dado un contexto.
        
        Args:
            context: Contexto del ticket (ticket data, customer data, etc.)
            
        Returns:
            True si todas las condiciones se cumplen
        """
        for condition in self.conditions:
            if not self._evaluate_condition(condition, context):
                return False
        return True
    
    def _evaluate_condition(
        self,
        condition: RuleCondition,
        context: Dict[str, Any]
    ) -> bool:
        """Evalúa una condición individual."""
        field_value = self._get_field_value(condition.field, context)
        
        if condition.operator == Operator.IS_NULL:
            return field_value is None
        if condition.operator == Operator.IS_NOT_NULL:
            return field_value is not None
        
        if field_value is None:
            return False
        
        # Convertir a string si no es numérico y el operador lo requiere
        if condition.operator in [Operator.CONTAINS, Operator.NOT_CONTAINS,
                                   Operator.STARTS_WITH, Operator.ENDS_WITH,
                                   Operator.REGEX]:
            field_value = str(field_value)
            compare_value = str(condition.value)
            if not condition.case_sensitive:
                field_value = field_value.lower()
                compare_value = compare_value.lower()
        
        operator = condition.operator
        
        if operator == Operator.EQUALS:
            return field_value == condition.value
        elif operator == Operator.NOT_EQUALS:
            return field_value != condition.value
        elif operator == Operator.CONTAINS:
            return compare_value in field_value
        elif operator == Operator.NOT_CONTAINS:
            return compare_value not in field_value
        elif operator == Operator.STARTS_WITH:
            return field_value.startswith(compare_value)
        elif operator == Operator.ENDS_WITH:
            return field_value.endswith(compare_value)
        elif operator == Operator.GREATER_THAN:
            return float(field_value) > float(condition.value)
        elif operator == Operator.LESS_THAN:
            return float(field_value) < float(condition.value)
        elif operator == Operator.GREATER_EQUAL:
            return float(field_value) >= float(condition.value)
        elif operator == Operator.LESS_EQUAL:
            return float(field_value) <= float(condition.value)
        elif operator == Operator.IN:
            return field_value in condition.value
        elif operator == Operator.NOT_IN:
            return field_value not in condition.value
        elif operator == Operator.REGEX:
            flags = 0 if condition.case_sensitive else re.IGNORECASE
            return bool(re.search(condition.value, field_value, flags))
        
        return False
    
    def _get_field_value(self, field: str, context: Dict[str, Any]) -> Any:
        """
        Obtiene valor de campo usando notación de punto.
        
        Ejemplo: "ticket.priority" -> context["ticket"]["priority"]
        """
        parts = field.split(".")
        value = context
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
        
        return value
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta las acciones de la regla.
        
        Returns:
            Resultado de ejecución
        """
        if not self.enabled:
            return {"executed": False, "reason": "rule_disabled"}
        
        if not self.evaluate(context):
            return {"executed": False, "reason": "conditions_not_met"}
        
        if self.max_executions and self.execution_count >= self.max_executions:
            return {"executed": False, "reason": "max_executions_reached"}
        
        results = []
        for action in self.actions:
            try:
                result = self._execute_action(action, context)
                results.append(result)
            except Exception as e:
                logger.error(f"Error executing action {action.type}: {e}")
                results.append({"action": action.type, "error": str(e)})
        
        self.execution_count += 1
        return {"executed": True, "results": results}
    
    def _execute_action(
        self,
        action: RuleAction,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta una acción individual."""
        action_type = action.type
        
        if action_type == "set_priority":
            return {"action": action_type, "priority": action.params.get("priority")}
        
        elif action_type == "set_status":
            return {"action": action_type, "status": action.params.get("status")}
        
        elif action_type == "assign_to":
            return {
                "action": action_type,
                "agent_id": action.params.get("agent_id"),
                "department": action.params.get("department")
            }
        
        elif action_type == "add_tag":
            return {"action": action_type, "tag": action.params.get("tag")}
        
        elif action_type == "send_notification":
            return {
                "action": action_type,
                "channel": action.params.get("channel"),
                "template": action.params.get("template")
            }
        
        elif action_type == "set_sla":
            return {
                "action": action_type,
                "sla_hours": action.params.get("sla_hours")
            }
        
        elif action_type == "auto_escalate":
            return {
                "action": action_type,
                "priority": action.params.get("priority", "urgent")
            }
        
        elif action_type == "custom":
            # Ejecutar función personalizada
            func = action.params.get("function")
            if callable(func):
                return func(context)
            return {"action": action_type, "error": "function_not_callable"}
        
        else:
            return {"action": action_type, "error": "unknown_action_type"}


class BusinessRulesEngine:
    """Motor de ejecución de reglas de negocio."""
    
    def __init__(self, rules: List[BusinessRule] = None):
        """
        Inicializa el motor.
        
        Args:
            rules: Lista de reglas (opcional, se pueden cargar después)
        """
        self.rules: Dict[str, BusinessRule] = {}
        if rules:
            for rule in rules:
                self.add_rule(rule)
    
    def add_rule(self, rule: BusinessRule):
        """Agrega una regla al motor."""
        self.rules[rule.rule_id] = rule
    
    def remove_rule(self, rule_id: str):
        """Elimina una regla."""
        if rule_id in self.rules:
            del self.rules[rule_id]
    
    def get_rule(self, rule_id: str) -> Optional[BusinessRule]:
        """Obtiene una regla por ID."""
        return self.rules.get(rule_id)
    
    def get_rules_by_type(self, rule_type: RuleType) -> List[BusinessRule]:
        """Obtiene reglas por tipo."""
        return [
            rule for rule in self.rules.values()
            if rule.rule_type == rule_type and rule.enabled
        ]
    
    def execute_rules(
        self,
        context: Dict[str, Any],
        rule_types: Optional[List[RuleType]] = None,
        stop_on_first_match: bool = False
    ) -> Dict[str, Any]:
        """
        Ejecuta reglas aplicables.
        
        Args:
            context: Contexto del ticket
            rule_types: Tipos de reglas a ejecutar (None = todas)
            stop_on_first_match: Detener en primera coincidencia
            
        Returns:
            Resultados de ejecución
        """
        # Filtrar y ordenar reglas
        applicable_rules = []
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            if rule_types and rule.rule_type not in rule_types:
                continue
            applicable_rules.append(rule)
        
        # Ordenar por prioridad (mayor primero)
        applicable_rules.sort(key=lambda r: r.priority, reverse=True)
        
        results = {}
        for rule in applicable_rules:
            try:
                result = rule.execute(context)
                results[rule.rule_id] = result
                
                if stop_on_first_match and result.get("executed"):
                    break
            except Exception as e:
                logger.error(f"Error executing rule {rule.rule_id}: {e}")
                results[rule.rule_id] = {"executed": False, "error": str(e)}
        
        return results
    
    def load_rules_from_dict(self, rules_data: List[Dict[str, Any]]):
        """Carga reglas desde diccionarios."""
        for rule_data in rules_data:
            try:
                rule = self._dict_to_rule(rule_data)
                self.add_rule(rule)
            except Exception as e:
                logger.error(f"Error loading rule: {e}")
    
    def _dict_to_rule(self, data: Dict[str, Any]) -> BusinessRule:
        """Convierte diccionario a BusinessRule."""
        conditions = [
            RuleCondition(
                field=c["field"],
                operator=Operator(c["operator"]),
                value=c["value"],
                case_sensitive=c.get("case_sensitive", False)
            )
            for c in data.get("conditions", [])
        ]
        
        actions = [
            RuleAction(
                type=a["type"],
                params=a.get("params", {})
            )
            for a in data.get("actions", [])
        ]
        
        return BusinessRule(
            rule_id=data["rule_id"],
            name=data["name"],
            description=data.get("description", ""),
            rule_type=RuleType(data["rule_type"]),
            priority=data.get("priority", 5),
            enabled=data.get("enabled", True),
            conditions=conditions,
            actions=actions,
            created_by=data.get("created_by"),
            max_executions=data.get("max_executions")
        )


# Ejemplo de uso
if __name__ == "__main__":
    # Crear regla de ejemplo
    rule = BusinessRule(
        rule_id="vip_priority_boost",
        name="VIP Priority Boost",
        description="Aumenta prioridad para clientes VIP",
        rule_type=RuleType.PRIORITY,
        priority=10,
        conditions=[
            RuleCondition(
                field="customer.tier",
                operator=Operator.EQUALS,
                value="vip"
            )
        ],
        actions=[
            RuleAction(
                type="set_priority",
                params={"priority": "urgent"}
            ),
            RuleAction(
                type="add_tag",
                params={"tag": "vip"}
            )
        ]
    )
    
    engine = BusinessRulesEngine([rule])
    
    context = {
        "ticket": {
            "priority": "normal",
            "subject": "Test"
        },
        "customer": {
            "tier": "vip",
            "email": "vip@example.com"
        }
    }
    
    results = engine.execute_rules(context)
    print(json.dumps(results, indent=2, default=str))

