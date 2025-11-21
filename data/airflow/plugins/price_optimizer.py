"""
Optimizador de Precios con Análisis Predictivo

Utiliza análisis estadístico y ML básico para optimizar precios
"""

import logging
import statistics
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import math

logger = logging.getLogger(__name__)


class PriceOptimizer:
    """Optimiza precios usando análisis predictivo"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.optimization_strategy = config.get('optimization_strategy', 'balanced')
        self.price_elasticity = config.get('price_elasticity', -1.5)  # Elasticidad por defecto
        self.min_margin = config.get('min_margin', 0.20)
        self.max_margin = config.get('max_margin', 0.50)
    
    def optimize_price(
        self,
        current_price: float,
        competitor_prices: List[float],
        historical_data: Optional[List[Dict]] = None,
        cost: Optional[float] = None,
        demand_forecast: Optional[float] = None
    ) -> Dict:
        """
        Optimiza precio usando múltiples factores
        
        Args:
            current_price: Precio actual
            competitor_prices: Lista de precios de competencia
            historical_data: Datos históricos de ventas/precios
            cost: Costo del producto
            demand_forecast: Pronóstico de demanda
        
        Returns:
            Diccionario con precio optimizado y análisis
        """
        # Calcular precio de mercado
        market_price = statistics.mean(competitor_prices) if competitor_prices else current_price
        min_competitor = min(competitor_prices) if competitor_prices else current_price
        max_competitor = max(competitor_prices) if competitor_prices else current_price
        
        # Análisis de posición
        position_analysis = self._analyze_market_position(
            current_price,
            market_price,
            min_competitor,
            max_competitor
        )
        
        # Calcular precio optimizado según estrategia
        if self.optimization_strategy == 'revenue_maximization':
            optimized_price = self._optimize_for_revenue(
                current_price,
                market_price,
                cost,
                demand_forecast
            )
        elif self.optimization_strategy == 'profit_maximization':
            optimized_price = self._optimize_for_profit(
                current_price,
                market_price,
                cost,
                demand_forecast
            )
        elif self.optimization_strategy == 'market_share':
            optimized_price = self._optimize_for_market_share(
                market_price,
                min_competitor
            )
        elif self.optimization_strategy == 'balanced':
            optimized_price = self._optimize_balanced(
                current_price,
                market_price,
                cost,
                competitor_prices
            )
        else:
            optimized_price = market_price
        
        # Aplicar límites
        optimized_price = self._apply_limits(
            optimized_price,
            current_price,
            cost,
            min_competitor,
            max_competitor
        )
        
        # Calcular métricas
        price_change = optimized_price - current_price
        price_change_percent = (price_change / current_price * 100) if current_price > 0 else 0
        
        # Estimar impacto
        impact_estimate = self._estimate_impact(
            current_price,
            optimized_price,
            demand_forecast
        )
        
        return {
            'current_price': current_price,
            'optimized_price': optimized_price,
            'price_change': price_change,
            'price_change_percent': price_change_percent,
            'market_price': market_price,
            'position_analysis': position_analysis,
            'optimization_strategy': self.optimization_strategy,
            'impact_estimate': impact_estimate,
            'confidence': self._calculate_confidence(
                competitor_prices,
                historical_data
            ),
        }
    
    def _analyze_market_position(
        self,
        current_price: float,
        market_price: float,
        min_competitor: float,
        max_competitor: float
    ) -> Dict:
        """Analiza posición en el mercado"""
        if current_price < min_competitor:
            position = 'below_market'
            percentile = 0
        elif current_price > max_competitor:
            position = 'above_market'
            percentile = 100
        else:
            position = 'in_market'
            # Calcular percentil aproximado
            range_size = max_competitor - min_competitor
            if range_size > 0:
                percentile = ((current_price - min_competitor) / range_size) * 100
            else:
                percentile = 50
        
        return {
            'position': position,
            'percentile': round(percentile, 2),
            'vs_market': round(((current_price - market_price) / market_price * 100), 2),
        }
    
    def _optimize_for_revenue(
        self,
        current_price: float,
        market_price: float,
        cost: Optional[float],
        demand_forecast: Optional[float]
    ) -> float:
        """Optimiza para maximizar ingresos"""
        # Usar elasticidad de precio
        if demand_forecast and self.price_elasticity:
            # Revenue = Price * Demand
            # Con elasticidad: Demand = base_demand * (Price/BasePrice)^elasticity
            # Optimizar derivando
            if cost:
                # Considerar margen mínimo
                min_price = cost * (1 + self.min_margin)
                optimal_price = max(min_price, market_price * 0.95)
            else:
                optimal_price = market_price * 0.98
        else:
            optimal_price = market_price * 0.97
        
        return optimal_price
    
    def _optimize_for_profit(
        self,
        current_price: float,
        market_price: float,
        cost: Optional[float],
        demand_forecast: Optional[float]
    ) -> float:
        """Optimiza para maximizar ganancias"""
        if not cost:
            return market_price * 1.05  # Aumentar precio si no hay costo
        
        # Profit = (Price - Cost) * Demand
        # Con elasticidad, optimizar
        optimal_margin = (self.min_margin + self.max_margin) / 2
        optimal_price = cost * (1 + optimal_margin)
        
        # Ajustar según mercado
        if optimal_price < market_price * 0.9:
            optimal_price = market_price * 0.95
        elif optimal_price > market_price * 1.1:
            optimal_price = market_price * 1.05
        
        return optimal_price
    
    def _optimize_for_market_share(
        self,
        market_price: float,
        min_competitor: float
    ) -> float:
        """Optimiza para ganar participación de mercado"""
        # Precio ligeramente por debajo del mínimo de competencia
        return min_competitor * 0.98
    
    def _optimize_balanced(
        self,
        current_price: float,
        market_price: float,
        cost: Optional[float],
        competitor_prices: List[float]
    ) -> float:
        """Optimización balanceada considerando múltiples factores"""
        # Ponderar: 40% mercado, 30% posición actual, 30% costo
        market_weight = 0.4
        current_weight = 0.3
        cost_weight = 0.3
        
        market_component = market_price * market_weight
        current_component = current_price * current_weight
        
        if cost:
            cost_component = cost * (1 + self.min_margin) * cost_weight
        else:
            cost_component = market_price * cost_weight
        
        optimized = market_component + current_component + cost_component
        
        # Ajustar según rango de competencia
        if competitor_prices:
            min_comp = min(competitor_prices)
            max_comp = max(competitor_prices)
            optimized = max(min_comp * 0.95, min(max_comp * 1.05, optimized))
        
        return optimized
    
    def _apply_limits(
        self,
        price: float,
        current_price: float,
        cost: Optional[float],
        min_competitor: float,
        max_competitor: float
    ) -> float:
        """Aplica límites al precio optimizado"""
        # Límite de cambio máximo
        max_change = self.config.get('max_price_change_percent', 20)
        max_price = current_price * (1 + max_change / 100)
        min_price = current_price * (1 - max_change / 100)
        
        # Límite de margen mínimo
        if cost:
            min_price = max(min_price, cost * (1 + self.min_margin))
        
        # Límite según competencia
        min_price = max(min_price, min_competitor * 0.9)
        max_price = min(max_price, max_competitor * 1.1)
        
        return max(min_price, min(max_price, price))
    
    def _estimate_impact(
        self,
        current_price: float,
        optimized_price: float,
        demand_forecast: Optional[float]
    ) -> Dict:
        """Estima impacto del cambio de precio"""
        price_change_percent = (
            (optimized_price - current_price) / current_price * 100
            if current_price > 0 else 0
        )
        
        # Estimar cambio en demanda usando elasticidad
        if demand_forecast and self.price_elasticity:
            demand_change_percent = price_change_percent * self.price_elasticity
            new_demand = demand_forecast * (1 + demand_change_percent / 100)
            
            # Estimar ingresos
            current_revenue = current_price * demand_forecast
            new_revenue = optimized_price * new_demand
            revenue_change = new_revenue - current_revenue
            revenue_change_percent = (revenue_change / current_revenue * 100) if current_revenue > 0 else 0
        else:
            demand_change_percent = 0
            new_demand = demand_forecast or 0
            revenue_change = 0
            revenue_change_percent = 0
        
        return {
            'price_change_percent': round(price_change_percent, 2),
            'estimated_demand_change_percent': round(demand_change_percent, 2),
            'estimated_new_demand': round(new_demand, 2),
            'estimated_revenue_change': round(revenue_change, 2),
            'estimated_revenue_change_percent': round(revenue_change_percent, 2),
        }
    
    def _calculate_confidence(
        self,
        competitor_prices: List[float],
        historical_data: Optional[List[Dict]]
    ) -> float:
        """Calcula nivel de confianza en la optimización"""
        confidence = 0.5  # Base
        
        # Más competidores = más confianza
        if competitor_prices:
            competitor_factor = min(len(competitor_prices) / 10, 0.3)
            confidence += competitor_factor
        
        # Datos históricos = más confianza
        if historical_data:
            historical_factor = min(len(historical_data) / 30, 0.2)
            confidence += historical_factor
        
        return min(confidence, 1.0)








