"""
Predicción de Demanda Avanzada

Predice demanda futura basada en múltiples factores
"""

import logging
import statistics
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import math

logger = logging.getLogger(__name__)


class DemandForecaster:
    """Predice demanda futura para optimización de precios"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get('enable_demand_forecast', False)
        self.price_elasticity = config.get('price_elasticity', -1.5)
    
    def forecast_demand(
        self,
        product_id: str,
        historical_sales: List[Dict],
        proposed_price: float,
        current_price: Optional[float] = None,
        seasonality_factor: Optional[float] = None
    ) -> Dict:
        """
        Predice demanda futura
        
        Args:
            product_id: ID del producto
            historical_sales: Ventas históricas
            proposed_price: Precio propuesto
            current_price: Precio actual (opcional)
            seasonality_factor: Factor de estacionalidad (opcional)
        
        Returns:
            Predicción de demanda
        """
        if not self.enabled or not historical_sales:
            return {'enabled': False}
        
        # Calcular demanda base
        base_demand = self._calculate_base_demand(historical_sales)
        
        # Ajustar por precio si se proporciona
        if current_price and proposed_price != current_price:
            price_impact = self._calculate_price_impact(
                current_price,
                proposed_price,
                base_demand
            )
            forecasted_demand = price_impact['forecasted_demand']
        else:
            forecasted_demand = base_demand
        
        # Ajustar por estacionalidad
        if seasonality_factor:
            forecasted_demand *= seasonality_factor
        
        # Calcular confianza
        confidence = self._calculate_confidence(historical_sales)
        
        return {
            'product_id': product_id,
            'base_demand': round(base_demand, 2),
            'forecasted_demand': round(forecasted_demand, 2),
            'proposed_price': proposed_price,
            'current_price': current_price,
            'demand_change_percent': round(
                ((forecasted_demand - base_demand) / base_demand * 100) if base_demand > 0 else 0,
                2
            ),
            'confidence': confidence,
            'forecast_method': 'historical_trend',
        }
    
    def _calculate_base_demand(self, historical_sales: List[Dict]) -> float:
        """Calcula demanda base desde histórico"""
        if not historical_sales:
            return 0.0
        
        # Extraer cantidades vendidas
        quantities = [
            s.get('quantity', 0) or s.get('sales', 0) or s.get('demand', 0)
            for s in historical_sales
        ]
        
        if not quantities:
            return 0.0
        
        # Usar promedio de últimos N períodos
        recent_periods = min(7, len(quantities))
        recent_quantities = quantities[-recent_periods:]
        
        # Calcular tendencia
        if len(recent_quantities) > 1:
            # Media móvil con tendencia
            avg = statistics.mean(recent_quantities)
            
            # Calcular tendencia simple
            first_half = statistics.mean(recent_quantities[:len(recent_quantities)//2])
            second_half = statistics.mean(recent_quantities[len(recent_quantities)//2:])
            trend = (second_half - first_half) / first_half if first_half > 0 else 0
            
            # Proyectar demanda futura
            forecasted = avg * (1 + trend)
        else:
            forecasted = statistics.mean(recent_quantities)
        
        return max(0, forecasted)
    
    def _calculate_price_impact(
        self,
        current_price: float,
        proposed_price: float,
        base_demand: float
    ) -> Dict:
        """Calcula impacto de cambio de precio en demanda"""
        price_change_pct = (
            (proposed_price - current_price) / current_price * 100
            if current_price > 0 else 0
        )
        
        # Aplicar elasticidad
        demand_change_pct = price_change_pct * self.price_elasticity
        forecasted_demand = base_demand * (1 + demand_change_pct / 100)
        
        # Calcular ingresos
        current_revenue = current_price * base_demand
        forecasted_revenue = proposed_price * forecasted_demand
        revenue_change = forecasted_revenue - current_revenue
        revenue_change_pct = (
            (revenue_change / current_revenue * 100)
            if current_revenue > 0 else 0
        )
        
        return {
            'price_change_percent': round(price_change_pct, 2),
            'demand_change_percent': round(demand_change_pct, 2),
            'forecasted_demand': round(max(0, forecasted_demand), 2),
            'current_revenue': round(current_revenue, 2),
            'forecasted_revenue': round(forecasted_revenue, 2),
            'revenue_change': round(revenue_change, 2),
            'revenue_change_percent': round(revenue_change_pct, 2),
        }
    
    def _calculate_confidence(self, historical_sales: List[Dict]) -> float:
        """Calcula confianza en la predicción"""
        if len(historical_sales) < 3:
            return 0.3
        
        # Más datos = más confianza
        data_factor = min(len(historical_sales) / 30, 0.4)
        
        # Consistencia = más confianza
        quantities = [
            s.get('quantity', 0) or s.get('sales', 0) or s.get('demand', 0)
            for s in historical_sales
        ]
        
        if len(quantities) > 1:
            cv = statistics.stdev(quantities) / statistics.mean(quantities) if statistics.mean(quantities) > 0 else 1
            consistency_factor = max(0, 0.3 - cv * 0.2)
        else:
            consistency_factor = 0.2
        
        confidence = 0.3 + data_factor + consistency_factor
        return min(confidence, 1.0)
    
    def forecast_revenue_optimization(
        self,
        product_id: str,
        historical_sales: List[Dict],
        price_range: tuple,
        current_price: float
    ) -> Dict:
        """
        Encuentra precio óptimo para maximizar ingresos
        
        Args:
            product_id: ID del producto
            historical_sales: Ventas históricas
            price_range: Tupla (min_price, max_price)
            current_price: Precio actual
        
        Returns:
            Precio óptimo y análisis
        """
        min_price, max_price = price_range
        base_demand = self._calculate_base_demand(historical_sales)
        
        # Probar diferentes precios
        test_prices = []
        step = (max_price - min_price) / 20
        
        for price in [min_price + step * i for i in range(21)]:
            price_impact = self._calculate_price_impact(
                current_price,
                price,
                base_demand
            )
            
            test_prices.append({
                'price': round(price, 2),
                'forecasted_demand': price_impact['forecasted_demand'],
                'forecasted_revenue': price_impact['forecasted_revenue'],
            })
        
        # Encontrar precio óptimo (máximo ingreso)
        optimal = max(test_prices, key=lambda x: x['forecasted_revenue'])
        
        return {
            'product_id': product_id,
            'current_price': current_price,
            'optimal_price': optimal['price'],
            'optimal_revenue': optimal['forecasted_revenue'],
            'current_revenue': current_price * base_demand,
            'revenue_improvement': optimal['forecasted_revenue'] - (current_price * base_demand),
            'price_tests': test_prices,
        }








