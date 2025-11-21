"""
Sistema de Machine Learning Básico para Predicción de Precios

Predicciones simples usando modelos estadísticos
"""

import logging
import statistics
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import math

logger = logging.getLogger(__name__)


class PriceMLPredictor:
    """Predicción de precios usando ML básico"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.model_type = config.get('ml_model_type', 'linear_regression')
        self.enabled = config.get('enable_ml_predictions', False)
    
    def predict_optimal_price(
        self,
        product_data: Dict,
        competitor_prices: List[float],
        historical_data: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Predice precio óptimo usando ML
        
        Args:
            product_data: Datos del producto
            competitor_prices: Precios de competencia
            historical_data: Datos históricos
        
        Returns:
            Diccionario con predicción y confianza
        """
        if not self.enabled:
            return {'enabled': False}
        
        try:
            if self.model_type == 'linear_regression':
                prediction = self._linear_regression_predict(
                    product_data,
                    competitor_prices,
                    historical_data
                )
            elif self.model_type == 'moving_average':
                prediction = self._moving_average_predict(
                    product_data,
                    competitor_prices,
                    historical_data
                )
            elif self.model_type == 'weighted_average':
                prediction = self._weighted_average_predict(
                    product_data,
                    competitor_prices,
                    historical_data
                )
            else:
                prediction = self._simple_average_predict(
                    competitor_prices
                )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error en predicción ML: {e}")
            return {'error': str(e), 'enabled': True}
    
    def _linear_regression_predict(
        self,
        product_data: Dict,
        competitor_prices: List[float],
        historical_data: Optional[List[Dict]]
    ) -> Dict:
        """Predicción usando regresión lineal simple"""
        if not competitor_prices:
            return {'error': 'No hay datos de competencia'}
        
        # Precio base: promedio de competencia
        base_price = statistics.mean(competitor_prices)
        
        # Ajustar según histórico si está disponible
        if historical_data and len(historical_data) > 2:
            # Calcular tendencia
            prices = [d.get('price', 0) for d in historical_data[-10:]]
            if len(prices) > 1:
                # Regresión lineal simple
                n = len(prices)
                x = list(range(n))
                y = prices
                
                x_mean = statistics.mean(x)
                y_mean = statistics.mean(y)
                
                numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
                denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
                
                if denominator != 0:
                    slope = numerator / denominator
                    intercept = y_mean - slope * x_mean
                    
                    # Predecir siguiente precio
                    next_x = n
                    predicted = slope * next_x + intercept
                    
                    # Combinar con precio de mercado
                    optimal = (base_price * 0.6 + predicted * 0.4)
                else:
                    optimal = base_price
            else:
                optimal = base_price
        else:
            optimal = base_price
        
        # Calcular confianza
        confidence = self._calculate_confidence(
            competitor_prices,
            historical_data
        )
        
        return {
            'predicted_price': round(optimal, 2),
            'base_price': round(base_price, 2),
            'confidence': confidence,
            'model': 'linear_regression',
        }
    
    def _moving_average_predict(
        self,
        product_data: Dict,
        competitor_prices: List[float],
        historical_data: Optional[List[Dict]]
    ) -> Dict:
        """Predicción usando media móvil"""
        if not historical_data or len(historical_data) < 3:
            # Fallback a promedio de competencia
            base_price = statistics.mean(competitor_prices) if competitor_prices else 0
            return {
                'predicted_price': round(base_price, 2),
                'confidence': 0.5,
                'model': 'moving_average',
            }
        
        # Media móvil de últimos N precios
        window = min(7, len(historical_data))
        recent_prices = [d.get('price', 0) for d in historical_data[-window:]]
        moving_avg = statistics.mean(recent_prices)
        
        # Combinar con precio de mercado
        market_price = statistics.mean(competitor_prices) if competitor_prices else moving_avg
        optimal = (moving_avg * 0.7 + market_price * 0.3)
        
        confidence = self._calculate_confidence(competitor_prices, historical_data)
        
        return {
            'predicted_price': round(optimal, 2),
            'moving_average': round(moving_avg, 2),
            'market_price': round(market_price, 2),
            'confidence': confidence,
            'model': 'moving_average',
        }
    
    def _weighted_average_predict(
        self,
        product_data: Dict,
        competitor_prices: List[float],
        historical_data: Optional[List[Dict]]
    ) -> Dict:
        """Predicción usando promedio ponderado"""
        factors = []
        weights = []
        
        # Factor 1: Precio de mercado (peso 0.4)
        if competitor_prices:
            market_price = statistics.mean(competitor_prices)
            factors.append(market_price)
            weights.append(0.4)
        
        # Factor 2: Precio histórico reciente (peso 0.3)
        if historical_data:
            recent_prices = [d.get('price', 0) for d in historical_data[-5:]]
            if recent_prices:
                historical_avg = statistics.mean(recent_prices)
                factors.append(historical_avg)
                weights.append(0.3)
        
        # Factor 3: Costo + margen (peso 0.2)
        cost = product_data.get('cost')
        if cost:
            min_margin = self.config.get('min_margin', 0.20)
            cost_based = cost * (1 + min_margin)
            factors.append(cost_based)
            weights.append(0.2)
        
        # Factor 4: Precio actual (peso 0.1)
        current_price = product_data.get('current_price')
        if current_price:
            factors.append(current_price)
            weights.append(0.1)
        
        if not factors:
            return {'error': 'No hay suficientes datos para predicción'}
        
        # Normalizar pesos
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        
        # Calcular promedio ponderado
        optimal = sum(f * w for f, w in zip(factors, weights))
        
        confidence = self._calculate_confidence(competitor_prices, historical_data)
        
        return {
            'predicted_price': round(optimal, 2),
            'factors': {
                'market': factors[0] if len(factors) > 0 else None,
                'historical': factors[1] if len(factors) > 1 else None,
                'cost_based': factors[2] if len(factors) > 2 else None,
            },
            'confidence': confidence,
            'model': 'weighted_average',
        }
    
    def _simple_average_predict(
        self,
        competitor_prices: List[float]
    ) -> Dict:
        """Predicción simple usando promedio"""
        if not competitor_prices:
            return {'error': 'No hay datos de competencia'}
        
        optimal = statistics.mean(competitor_prices)
        
        return {
            'predicted_price': round(optimal, 2),
            'confidence': 0.6,
            'model': 'simple_average',
        }
    
    def _calculate_confidence(
        self,
        competitor_prices: List[float],
        historical_data: Optional[List[Dict]]
    ) -> float:
        """Calcula nivel de confianza en la predicción"""
        confidence = 0.5  # Base
        
        # Más competidores = más confianza
        if competitor_prices:
            comp_factor = min(len(competitor_prices) / 10, 0.3)
            confidence += comp_factor
        
        # Más datos históricos = más confianza
        if historical_data:
            hist_factor = min(len(historical_data) / 30, 0.2)
            confidence += hist_factor
        
        return min(confidence, 1.0)
    
    def predict_demand(
        self,
        price: float,
        historical_demand: Optional[List[float]] = None,
        elasticity: float = -1.5
    ) -> Dict:
        """
        Predice demanda basada en precio
        
        Args:
            price: Precio propuesto
            historical_demand: Demanda histórica
            elasticity: Elasticidad de precio
        
        Returns:
            Predicción de demanda
        """
        if not historical_demand:
            return {'error': 'No hay datos históricos de demanda'}
        
        base_demand = statistics.mean(historical_demand)
        base_price = statistics.mean([d.get('price', price) for d in historical_demand] if isinstance(historical_demand[0], dict) else [price])
        
        # Calcular cambio porcentual en precio
        price_change_pct = ((price - base_price) / base_price * 100) if base_price > 0 else 0
        
        # Aplicar elasticidad
        demand_change_pct = price_change_pct * elasticity
        predicted_demand = base_demand * (1 + demand_change_pct / 100)
        
        return {
            'predicted_demand': round(predicted_demand, 2),
            'base_demand': round(base_demand, 2),
            'demand_change_percent': round(demand_change_pct, 2),
            'price_change_percent': round(price_change_pct, 2),
        }








