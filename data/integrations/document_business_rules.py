"""
Sistema de Reglas de Negocio
=============================

Define y ejecuta reglas de negocio personalizadas para documentos.
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class RuleAction(Enum):
    """Acciones de reglas"""
    APPROVE = "approve"
    REJECT = "reject"
    FLAG = "flag"
    NOTIFY = "notify"
    ROUTE = "route"
    TRANSFORM = "transform"


@dataclass
class BusinessRule:
    """Regla de negocio"""
    rule_id: str
    name: str
    description: str
    conditions: Dict[str, Any]  # Condiciones a evaluar
    action: RuleAction
    action_params: Dict[str, Any] = None
    priority: int = 5  # 1-10
    enabled: bool = True
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class BusinessRulesEngine:
    """Motor de reglas de negocio"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.logger = logging.getLogger(__name__)
        self.rules: List[BusinessRule] = []
        self._load_rules()
    
    def add_rule(self, rule: BusinessRule) -> bool:
        """Agrega una regla"""
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        
        if self.db:
            self._save_rule_to_db(rule)
        
        return True
    
    def evaluate_document(
        self,
        document: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Evalúa un documento contra todas las reglas"""
        results = []
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            if self._evaluate_conditions(rule.conditions, document):
                result = {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "action": rule.action.value,
                    "action_params": rule.action_params or {},
                    "matched": True,
                    "evaluated_at": datetime.now().isoformat()
                }
                results.append(result)
        
        return results
    
    def _evaluate_conditions(
        self,
        conditions: Dict[str, Any],
        document: Dict[str, Any]
    ) -> bool:
        """Evalúa condiciones de una regla"""
        for condition_type, condition_value in conditions.items():
            if condition_type == "document_type":
                if document.get("document_type") != condition_value:
                    return False
            
            elif condition_type == "field_equals":
                for field, value in condition_value.items():
                    doc_value = document.get("extracted_fields", {}).get(field)
                    if doc_value != value:
                        return False
            
            elif condition_type == "field_contains":
                for field, value in condition_value.items():
                    doc_value = str(document.get("extracted_fields", {}).get(field, ""))
                    if value not in doc_value:
                        return False
            
            elif condition_type == "field_greater_than":
                for field, value in condition_value.items():
                    doc_value = document.get("extracted_fields", {}).get(field)
                    try:
                        if float(doc_value) <= float(value):
                            return False
                    except:
                        return False
            
            elif condition_type == "confidence_above":
                if document.get("classification_confidence", 0) < condition_value:
                    return False
            
            elif condition_type == "has_field":
                for field in condition_value:
                    if field not in document.get("extracted_fields", {}):
                        return False
        
        return True
    
    def execute_actions(
        self,
        document: Dict[str, Any],
        rule_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Ejecuta acciones de reglas aplicadas"""
        executed_actions = []
        
        for result in rule_results:
            action = result["action"]
            params = result.get("action_params", {})
            
            if action == "approve":
                executed_actions.append({
                    "action": "approve",
                    "message": params.get("message", "Documento aprobado por regla")
                })
            
            elif action == "reject":
                executed_actions.append({
                    "action": "reject",
                    "reason": params.get("reason", "Documento rechazado por regla")
                })
            
            elif action == "flag":
                executed_actions.append({
                    "action": "flag",
                    "flag_type": params.get("flag_type", "warning"),
                    "message": params.get("message", "Documento marcado")
                })
            
            elif action == "notify":
                executed_actions.append({
                    "action": "notify",
                    "recipients": params.get("recipients", []),
                    "message": params.get("message", "Notificación de regla")
                })
            
            elif action == "route":
                executed_actions.append({
                    "action": "route",
                    "route_to": params.get("route_to"),
                    "workflow": params.get("workflow")
                })
        
        return {
            "document_id": document.get("document_id"),
            "actions_executed": executed_actions,
            "total_rules_matched": len(rule_results)
        }
    
    def _load_rules(self):
        """Carga reglas desde BD"""
        if not self.db:
            return
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT rule_id, name, description, conditions, action,
                       action_params, priority, enabled, created_at
                FROM business_rules
                WHERE enabled = true
                ORDER BY priority DESC
            """)
            
            for row in cursor.fetchall():
                rule = BusinessRule(
                    rule_id=row[0],
                    name=row[1],
                    description=row[2],
                    conditions=json.loads(row[3]) if row[3] else {},
                    action=RuleAction(row[4]),
                    action_params=json.loads(row[5]) if row[5] else {},
                    priority=row[6],
                    enabled=row[7],
                    created_at=row[8]
                )
                self.rules.append(rule)
        except Exception as e:
            self.logger.error(f"Error cargando reglas: {e}")
    
    def _save_rule_to_db(self, rule: BusinessRule):
        """Guarda regla en BD"""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO business_rules
                (rule_id, name, description, conditions, action, action_params,
                 priority, enabled, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (rule_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    conditions = EXCLUDED.conditions,
                    action = EXCLUDED.action,
                    action_params = EXCLUDED.action_params,
                    priority = EXCLUDED.priority,
                    enabled = EXCLUDED.enabled
            """, (
                rule.rule_id,
                rule.name,
                rule.description,
                json.dumps(rule.conditions),
                rule.action.value,
                json.dumps(rule.action_params) if rule.action_params else None,
                rule.priority,
                rule.enabled,
                rule.created_at
            ))
            self.db.commit()
        except Exception as e:
            self.logger.error(f"Error guardando regla: {e}")
            self.db.rollback()

