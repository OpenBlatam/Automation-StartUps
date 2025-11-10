"""
Sistema de Reglas de Negocio Personalizadas

Permite definir reglas de negocio complejas para precios
"""

import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class BusinessRule:
    """Representa una regla de negocio"""
    
    def __init__(
        self,
        name: str,
        condition: Callable,
        action: Callable,
        priority: int = 0,
        enabled: bool = True
    ):
        self.name = name
        self.condition = condition
        self.action = action
        self.priority = priority
        self.enabled = enabled


class PriceBusinessRules:
    """Gestiona reglas de negocio personalizadas para precios"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.rules: List[BusinessRule] = []
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Inicializa reglas por defecto"""
        
        # Regla: Precio mínimo basado en costo
        self.add_rule(BusinessRule(
            name='min_price_from_cost',
            condition=lambda data: data.get('cost') and data.get('new_price', 0) < data['cost'] * 1.2,
            action=lambda data: {
                **data,
                'new_price': data['cost'] * 1.2,
                'rule_applied': 'min_price_from_cost',
                'reason': 'Aplicado precio mínimo basado en costo'
            },
            priority=10
        ))
        
        # Regla: No bajar precio si está en top 3 más baratos
        self.add_rule(BusinessRule(
            name='maintain_competitive_position',
            condition=lambda data: (
                data.get('market_position') == 'lowest' and
                data.get('price_change_percent', 0) < 0
            ),
            action=lambda data: {
                **data,
                'new_price': data.get('current_price', 0),
                'rule_applied': 'maintain_competitive_position',
                'reason': 'Mantener posición competitiva'
            },
            priority=8
        ))
        
        # Regla: Aumentar precio si está muy por debajo del mercado
        self.add_rule(BusinessRule(
            name='increase_if_below_market',
            condition=lambda data: (
                data.get('market_position') == 'lowest' and
                data.get('diff_from_avg_percent', 0) < -15
            ),
            action=lambda data: {
                **data,
                'new_price': data.get('avg_competitor_price', data.get('current_price', 0)) * 0.95,
                'rule_applied': 'increase_if_below_market',
                'reason': 'Aumentar precio muy por debajo del mercado'
            },
            priority=7
        ))
    
    def add_rule(self, rule: BusinessRule):
        """Agrega una regla de negocio"""
        self.rules.append(rule)
        # Ordenar por prioridad (mayor primero)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        logger.info(f"Regla agregada: {rule.name} (prioridad: {rule.priority})")
    
    def remove_rule(self, rule_name: str):
        """Elimina una regla"""
        self.rules = [r for r in self.rules if r.name != rule_name]
        logger.info(f"Regla eliminada: {rule_name}")
    
    def enable_rule(self, rule_name: str):
        """Habilita una regla"""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = True
                logger.info(f"Regla habilitada: {rule_name}")
                return
        logger.warning(f"Regla no encontrada: {rule_name}")
    
    def disable_rule(self, rule_name: str):
        """Deshabilita una regla"""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = False
                logger.info(f"Regla deshabilitada: {rule_name}")
                return
        logger.warning(f"Regla no encontrada: {rule_name}")
    
    def apply_rules(
        self,
        price_data: Dict,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Aplica reglas de negocio a un ajuste de precio
        
        Args:
            price_data: Datos del precio a ajustar
            context: Contexto adicional
        
        Returns:
            Datos del precio después de aplicar reglas
        """
        result = {**price_data}
        context = context or {}
        
        applied_rules = []
        
        # Aplicar reglas en orden de prioridad
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            try:
                # Combinar datos y contexto
                rule_data = {**result, **context}
                
                # Verificar condición
                if rule.condition(rule_data):
                    # Aplicar acción
                    result = rule.action(rule_data)
                    applied_rules.append(rule.name)
                    logger.debug(f"Regla aplicada: {rule.name}")
                    
                    # Si la regla establece que no se debe continuar, parar
                    if result.get('stop_processing', False):
                        break
                        
            except Exception as e:
                logger.error(f"Error aplicando regla {rule.name}: {e}")
                continue
        
        result['applied_rules'] = applied_rules
        result['rules_applied_count'] = len(applied_rules)
        
        return result
    
    def apply_rules_batch(
        self,
        price_adjustments: List[Dict],
        context: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Aplica reglas a un lote de ajustes
        
        Args:
            price_adjustments: Lista de ajustes de precio
            context: Contexto compartido
        
        Returns:
            Lista de ajustes después de aplicar reglas
        """
        results = []
        
        for adjustment in price_adjustments:
            adjusted = self.apply_rules(adjustment, context)
            results.append(adjusted)
        
        return results
    
    def get_rules_summary(self) -> Dict:
        """Obtiene resumen de reglas"""
        return {
            'total_rules': len(self.rules),
            'enabled_rules': len([r for r in self.rules if r.enabled]),
            'disabled_rules': len([r for r in self.rules if not r.enabled]),
            'rules': [
                {
                    'name': r.name,
                    'priority': r.priority,
                    'enabled': r.enabled,
                }
                for r in self.rules
            ],
        }








