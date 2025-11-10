"""
Sistema de Validación Avanzada de Precios

Validaciones robustas y detección de anomalías
"""

import logging
import statistics
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import math

logger = logging.getLogger(__name__)


class PriceValidator:
    """Valida precios con múltiples reglas y detección de anomalías"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.validation_rules = self._initialize_rules()
        self.anomaly_threshold = config.get('anomaly_threshold', 3.0)  # Desviaciones estándar
    
    def _initialize_rules(self) -> List[Dict]:
        """Inicializa reglas de validación"""
        return [
            {
                'name': 'price_positive',
                'check': lambda p: p > 0,
                'message': 'El precio debe ser positivo'
            },
            {
                'name': 'price_within_range',
                'check': lambda p, min_p, max_p: min_p <= p <= max_p if min_p and max_p else True,
                'message': 'El precio está fuera del rango permitido'
            },
            {
                'name': 'price_change_reasonable',
                'check': lambda change_pct, max_change: abs(change_pct) <= max_change if max_change else True,
                'message': 'El cambio de precio excede el límite permitido'
            },
            {
                'name': 'price_vs_cost',
                'check': lambda price, cost, min_margin: price >= cost * (1 + min_margin) if cost else True,
                'message': 'El precio está por debajo del margen mínimo'
            },
        ]
    
    def validate_price(
        self,
        price: float,
        context: Optional[Dict] = None
    ) -> Tuple[bool, List[str]]:
        """
        Valida un precio individual
        
        Args:
            price: Precio a validar
            context: Contexto adicional (cost, min_price, max_price, etc.)
        
        Returns:
            Tuple (es_válido, lista_de_errores)
        """
        errors = []
        context = context or {}
        
        # Aplicar reglas básicas
        for rule in self.validation_rules:
            try:
                if rule['name'] == 'price_positive':
                    if not rule['check'](price):
                        errors.append(rule['message'])
                
                elif rule['name'] == 'price_within_range':
                    min_price = context.get('min_price')
                    max_price = context.get('max_price')
                    if not rule['check'](price, min_price, max_price):
                        errors.append(rule['message'])
                
                elif rule['name'] == 'price_change_reasonable':
                    change_pct = context.get('price_change_percent', 0)
                    max_change = context.get('max_price_change_percent', 20)
                    if not rule['check'](change_pct, max_change):
                        errors.append(rule['message'])
                
                elif rule['name'] == 'price_vs_cost':
                    cost = context.get('cost')
                    min_margin = context.get('min_margin', 0.20)
                    if not rule['check'](price, cost, min_margin):
                        errors.append(rule['message'])
                
            except Exception as e:
                logger.warning(f"Error aplicando regla {rule['name']}: {e}")
        
        return len(errors) == 0, errors
    
    def validate_price_adjustment(
        self,
        current_price: float,
        new_price: float,
        context: Optional[Dict] = None
    ) -> Tuple[bool, List[str], Dict]:
        """
        Valida un ajuste de precio
        
        Args:
            current_price: Precio actual
            new_price: Nuevo precio propuesto
            context: Contexto adicional
        
        Returns:
            Tuple (es_válido, errores, análisis)
        """
        context = context or {}
        errors = []
        warnings = []
        
        # Calcular cambio
        price_change = new_price - current_price
        price_change_percent = (price_change / current_price * 100) if current_price > 0 else 0
        
        # Validar nuevo precio
        validation_context = {
            **context,
            'price_change_percent': price_change_percent
        }
        is_valid, validation_errors = self.validate_price(new_price, validation_context)
        errors.extend(validation_errors)
        
        # Análisis adicional
        analysis = {
            'price_change': price_change,
            'price_change_percent': price_change_percent,
            'is_increase': price_change > 0,
            'is_decrease': price_change < 0,
            'change_magnitude': abs(price_change_percent),
        }
        
        # Detectar cambios extremos
        max_change = context.get('max_price_change_percent', 20)
        if abs(price_change_percent) > max_change:
            warnings.append(f"Cambio de precio extremo: {price_change_percent:.2f}%")
            analysis['is_extreme'] = True
        else:
            analysis['is_extreme'] = False
        
        # Detectar anomalías estadísticas
        if context.get('historical_prices'):
            is_anomaly, anomaly_score = self._detect_anomaly(
                new_price,
                context['historical_prices']
            )
            analysis['is_anomaly'] = is_anomaly
            analysis['anomaly_score'] = anomaly_score
            
            if is_anomaly:
                warnings.append(f"Precio anómalo detectado (score: {anomaly_score:.2f})")
        
        return is_valid, errors, {**analysis, 'warnings': warnings}
    
    def _detect_anomaly(
        self,
        price: float,
        historical_prices: List[float]
    ) -> Tuple[bool, float]:
        """
        Detecta si un precio es anómalo comparado con histórico
        
        Args:
            price: Precio a evaluar
            historical_prices: Precios históricos
        
        Returns:
            Tuple (es_anómalo, score_de_anomalía)
        """
        if not historical_prices or len(historical_prices) < 3:
            return False, 0.0
        
        mean = statistics.mean(historical_prices)
        stdev = statistics.stdev(historical_prices) if len(historical_prices) > 1 else 0
        
        if stdev == 0:
            return False, 0.0
        
        # Calcular z-score
        z_score = abs((price - mean) / stdev)
        
        # Es anómalo si está más de N desviaciones estándar
        is_anomaly = z_score > self.anomaly_threshold
        
        return is_anomaly, z_score
    
    def validate_batch(
        self,
        prices: List[Dict],
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Valida un lote de precios
        
        Args:
            prices: Lista de precios a validar
            context: Contexto compartido
        
        Returns:
            Diccionario con resultados de validación
        """
        results = {
            'total': len(prices),
            'valid': 0,
            'invalid': 0,
            'errors': [],
            'warnings': [],
            'anomalies': [],
        }
        
        for price_data in prices:
            price = price_data.get('price', 0)
            price_context = {**(context or {}), **price_data}
            
            is_valid, errors = self.validate_price(price, price_context)
            
            if is_valid:
                results['valid'] += 1
            else:
                results['invalid'] += 1
                results['errors'].extend([
                    {
                        'product': price_data.get('product_name', 'Unknown'),
                        'error': error
                    }
                    for error in errors
                ])
        
        return results
    
    def get_validation_summary(self, validation_results: Dict) -> str:
        """Genera resumen legible de validación"""
        total = validation_results.get('total', 0)
        valid = validation_results.get('valid', 0)
        invalid = validation_results.get('invalid', 0)
        errors = validation_results.get('errors', [])
        
        summary = f"Validación completada: {valid}/{total} válidos"
        
        if invalid > 0:
            summary += f", {invalid} inválidos"
        
        if errors:
            summary += f"\nErrores encontrados: {len(errors)}"
            for error in errors[:5]:  # Mostrar primeros 5
                summary += f"\n  - {error.get('product')}: {error.get('error')}"
        
        return summary








