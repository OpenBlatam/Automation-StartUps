"""
Sistema de Recomendaciones Inteligentes

Genera recomendaciones de precios basadas en múltiples factores
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class PriceRecommendationEngine:
    """Motor de recomendaciones inteligentes de precios"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get('enable_recommendations', False)
        self.recommendation_factors = config.get('recommendation_factors', {
            'market_position': 0.3,
            'profit_margin': 0.25,
            'demand_forecast': 0.2,
            'sentiment': 0.15,
            'competition': 0.1,
        })
    
    def generate_recommendation(
        self,
        product_data: Dict,
        market_data: Dict,
        demand_forecast: Optional[Dict] = None,
        sentiment_analysis: Optional[Dict] = None,
        competitor_analysis: Optional[Dict] = None
    ) -> Dict:
        """
        Genera recomendación completa de precio
        
        Args:
            product_data: Datos del producto
            market_data: Datos de mercado
            demand_forecast: Predicción de demanda (opcional)
            sentiment_analysis: Análisis de sentimiento (opcional)
            competitor_analysis: Análisis de competencia (opcional)
        
        Returns:
            Recomendación completa
        """
        if not self.enabled:
            return {'enabled': False}
        
        current_price = product_data.get('current_price', 0)
        cost = product_data.get('cost', 0)
        
        # Calcular scores por factor
        scores = {}
        recommendations = []
        
        # Factor 1: Posición en mercado
        if competitor_analysis:
            market_score, market_rec = self._analyze_market_position(
                current_price,
                competitor_analysis
            )
            scores['market'] = market_score
            recommendations.append(market_rec)
        
        # Factor 2: Margen de ganancia
        if cost:
            margin_score, margin_rec = self._analyze_profit_margin(
                current_price,
                cost
            )
            scores['margin'] = margin_score
            recommendations.append(margin_rec)
        
        # Factor 3: Predicción de demanda
        if demand_forecast:
            demand_score, demand_rec = self._analyze_demand(
                current_price,
                demand_forecast
            )
            scores['demand'] = demand_score
            recommendations.append(demand_rec)
        
        # Factor 4: Sentimiento
        if sentiment_analysis:
            sentiment_score, sentiment_rec = self._analyze_sentiment(
                sentiment_analysis
            )
            scores['sentiment'] = sentiment_score
            recommendations.append(sentiment_rec)
        
        # Factor 5: Competencia
        if competitor_analysis:
            competition_score, competition_rec = self._analyze_competition(
                competitor_analysis
            )
            scores['competition'] = competition_score
            recommendations.append(competition_rec)
        
        # Calcular recomendación final ponderada
        final_recommendation = self._calculate_final_recommendation(
            current_price,
            scores,
            recommendations
        )
        
        return {
            'product_id': product_data.get('product_id'),
            'product_name': product_data.get('product_name'),
            'current_price': current_price,
            'recommended_price': final_recommendation['price'],
            'price_change': final_recommendation['price'] - current_price,
            'price_change_percent': (
                ((final_recommendation['price'] - current_price) / current_price * 100)
                if current_price > 0 else 0
            ),
            'confidence': final_recommendation['confidence'],
            'action': final_recommendation['action'],
            'reason': final_recommendation['reason'],
            'factor_scores': scores,
            'detailed_recommendations': recommendations,
            'generated_at': datetime.now().isoformat(),
        }
    
    def _analyze_market_position(
        self,
        current_price: float,
        competitor_analysis: Dict
    ) -> tuple:
        """Analiza posición en mercado"""
        position = competitor_analysis.get('position', 'unknown')
        diff_from_avg = competitor_analysis.get('diff_from_avg_percent', 0)
        
        if position == 'highest' or diff_from_avg > 15:
            score = -0.8
            rec = {
                'factor': 'market_position',
                'action': 'decrease',
                'target_price': competitor_analysis.get('avg_competitor_price', current_price) * 0.98,
                'reason': 'Precio muy por encima del mercado',
            }
        elif position == 'lowest' or diff_from_avg < -15:
            score = 0.3
            rec = {
                'factor': 'market_position',
                'action': 'increase',
                'target_price': competitor_analysis.get('avg_competitor_price', current_price) * 1.02,
                'reason': 'Precio muy por debajo del mercado',
            }
        else:
            score = 0.0
            rec = {
                'factor': 'market_position',
                'action': 'maintain',
                'target_price': current_price,
                'reason': 'Posición competitiva',
            }
        
        return score, rec
    
    def _analyze_profit_margin(
        self,
        current_price: float,
        cost: float
    ) -> tuple:
        """Analiza margen de ganancia"""
        if cost <= 0:
            return 0.0, {'factor': 'margin', 'action': 'maintain', 'reason': 'Sin datos de costo'}
        
        margin = (current_price - cost) / cost
        min_margin = self.config.get('min_margin', 0.20)
        optimal_margin = self.config.get('optimal_margin', 0.30)
        
        if margin < min_margin:
            score = -0.9
            rec = {
                'factor': 'margin',
                'action': 'increase',
                'target_price': cost * (1 + min_margin),
                'reason': f'Margen por debajo del mínimo ({margin:.1%} < {min_margin:.1%})',
            }
        elif margin < optimal_margin:
            score = -0.3
            rec = {
                'factor': 'margin',
                'action': 'increase',
                'target_price': cost * (1 + optimal_margin),
                'reason': f'Margen por debajo del óptimo',
            }
        else:
            score = 0.5
            rec = {
                'factor': 'margin',
                'action': 'maintain',
                'target_price': current_price,
                'reason': 'Margen saludable',
            }
        
        return score, rec
    
    def _analyze_demand(
        self,
        current_price: float,
        demand_forecast: Dict
    ) -> tuple:
        """Analiza predicción de demanda"""
        revenue_change = demand_forecast.get('revenue_change_percent', 0)
        
        if revenue_change > 5:
            score = 0.7
            rec = {
                'factor': 'demand',
                'action': 'increase',
                'target_price': demand_forecast.get('proposed_price', current_price),
                'reason': f'Incremento de ingresos proyectado: {revenue_change:.1f}%',
            }
        elif revenue_change < -5:
            score = -0.7
            rec = {
                'factor': 'demand',
                'action': 'decrease',
                'target_price': demand_forecast.get('proposed_price', current_price),
                'reason': f'Reducción de ingresos proyectada: {revenue_change:.1f}%',
            }
        else:
            score = 0.0
            rec = {
                'factor': 'demand',
                'action': 'maintain',
                'target_price': current_price,
                'reason': 'Impacto en ingresos mínimo',
            }
        
        return score, rec
    
    def _analyze_sentiment(
        self,
        sentiment_analysis: Dict
    ) -> tuple:
        """Analiza sentimiento"""
        sentiment = sentiment_analysis.get('sentiment', 'neutral')
        score_value = sentiment_analysis.get('score', 0)
        
        if sentiment == 'negative' and score_value < -0.5:
            rec_data = sentiment_analysis.get('recommendation', {})
            return -0.6, {
                'factor': 'sentiment',
                'action': rec_data.get('action', 'decrease'),
                'target_price': current_price * (1 + rec_data.get('suggested_change', 0) / 100),
                'reason': 'Sentimiento negativo sobre precio',
            }
        elif sentiment == 'positive' and score_value > 0.5:
            rec_data = sentiment_analysis.get('recommendation', {})
            return 0.3, {
                'factor': 'sentiment',
                'action': rec_data.get('action', 'maintain'),
                'target_price': current_price * (1 + rec_data.get('suggested_change', 0) / 100),
                'reason': 'Sentimiento positivo sobre precio',
            }
        else:
            return 0.0, {
                'factor': 'sentiment',
                'action': 'maintain',
                'target_price': current_price,
                'reason': 'Sentimiento neutral',
            }
    
    def _analyze_competition(
        self,
        competitor_analysis: Dict
    ) -> tuple:
        """Analiza competencia"""
        recommendation = competitor_analysis.get('recommendation', {})
        priority = recommendation.get('priority', 'low')
        
        if priority == 'high':
            score = -0.8 if recommendation.get('action') == 'decrease' else 0.5
        elif priority == 'medium':
            score = -0.4 if recommendation.get('action') == 'decrease' else 0.2
        else:
            score = 0.0
        
        return score, {
            'factor': 'competition',
            'action': recommendation.get('action', 'maintain'),
            'target_price': recommendation.get('target_price', current_price),
            'reason': recommendation.get('reason', 'Análisis de competencia'),
        }
    
    def _calculate_final_recommendation(
        self,
        current_price: float,
        scores: Dict,
        recommendations: List[Dict]
    ) -> Dict:
        """Calcula recomendación final ponderada"""
        if not scores:
            return {
                'price': current_price,
                'action': 'maintain',
                'reason': 'Sin datos suficientes',
                'confidence': 0.0,
            }
        
        # Calcular precio objetivo ponderado
        weighted_price = 0.0
        total_weight = 0.0
        
        for rec in recommendations:
            factor = rec.get('factor', '')
            weight = self.recommendation_factors.get(factor, 0.1)
            target_price = rec.get('target_price', current_price)
            
            weighted_price += target_price * weight
            total_weight += weight
        
        if total_weight > 0:
            recommended_price = weighted_price / total_weight
        else:
            recommended_price = current_price
        
        # Determinar acción
        price_change_pct = (
            (recommended_price - current_price) / current_price * 100
            if current_price > 0 else 0
        )
        
        if abs(price_change_pct) < 1:
            action = 'maintain'
            reason = 'Cambio mínimo, mantener precio actual'
        elif price_change_pct > 0:
            action = 'increase'
            reason = 'Múltiples factores sugieren aumento'
        else:
            action = 'decrease'
            reason = 'Múltiples factores sugieren reducción'
        
        # Calcular confianza
        confidence = min(1.0, abs(sum(scores.values())) / len(scores) if scores else 0.0)
        
        return {
            'price': round(recommended_price, 2),
            'action': action,
            'reason': reason,
            'confidence': round(confidence, 2),
        }








