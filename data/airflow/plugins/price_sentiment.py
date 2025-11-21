"""
Análisis de Sentimiento para Precios

Analiza reviews y feedback para optimizar precios
"""

import logging
import statistics
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


class PriceSentimentAnalyzer:
    """Analiza sentimiento de reviews relacionado con precios"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get('enable_sentiment_analysis', False)
        
        # Palabras clave relacionadas con precio
        self.price_keywords = {
            'expensive': -2,
            'overpriced': -2,
            'costly': -1,
            'cheap': 1,
            'affordable': 1,
            'value': 1,
            'worth': 1,
            'bargain': 2,
            'rip-off': -2,
            'expensive': -2,
        }
    
    def analyze_reviews(
        self,
        product_id: str,
        reviews: List[Dict]
    ) -> Dict:
        """
        Analiza reviews para extraer sentimiento sobre precios
        
        Args:
            product_id: ID del producto
            reviews: Lista de reviews con texto
        
        Returns:
            Análisis de sentimiento
        """
        if not self.enabled or not reviews:
            return {'enabled': False}
        
        price_related_reviews = []
        sentiment_scores = []
        
        for review in reviews:
            text = review.get('text', '').lower()
            rating = review.get('rating', 0)
            
            # Buscar menciones de precio
            if self._mentions_price(text):
                price_related_reviews.append(review)
                score = self._calculate_sentiment_score(text, rating)
                sentiment_scores.append(score)
        
        if not sentiment_scores:
            return {
                'product_id': product_id,
                'price_related_reviews': 0,
                'total_reviews': len(reviews),
                'sentiment': 'neutral',
                'score': 0.0,
            }
        
        avg_score = statistics.mean(sentiment_scores)
        
        # Determinar sentimiento
        if avg_score > 0.5:
            sentiment = 'positive'
        elif avg_score < -0.5:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'product_id': product_id,
            'price_related_reviews': len(price_related_reviews),
            'total_reviews': len(reviews),
            'coverage': len(price_related_reviews) / len(reviews) * 100 if reviews else 0,
            'sentiment': sentiment,
            'score': round(avg_score, 2),
            'recommendation': self._generate_recommendation(sentiment, avg_score),
        }
    
    def _mentions_price(self, text: str) -> bool:
        """Verifica si el texto menciona precio"""
        price_patterns = [
            r'\$[\d,]+',
            r'price',
            r'cost',
            r'expensive',
            r'cheap',
            r'affordable',
            r'value',
            r'worth',
        ]
        
        for pattern in price_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _calculate_sentiment_score(self, text: str, rating: int) -> float:
        """Calcula score de sentimiento"""
        score = 0.0
        
        # Score basado en rating (normalizado a -1 a 1)
        rating_score = (rating - 3) / 2.0  # 1->-1, 5->1
        score += rating_score * 0.5
        
        # Score basado en palabras clave
        for keyword, weight in self.price_keywords.items():
            count = text.count(keyword)
            if count > 0:
                score += weight * min(count, 3) / 10.0
        
        return max(-1.0, min(1.0, score))
    
    def _generate_recommendation(
        self,
        sentiment: str,
        score: float
    ) -> Dict:
        """Genera recomendación basada en sentimiento"""
        if sentiment == 'negative' and score < -0.7:
            return {
                'action': 'decrease',
                'priority': 'high',
                'reason': 'Sentimiento muy negativo sobre precio',
                'suggested_change': -10,  # Porcentaje
            }
        elif sentiment == 'negative':
            return {
                'action': 'decrease',
                'priority': 'medium',
                'reason': 'Sentimiento negativo sobre precio',
                'suggested_change': -5,
            }
        elif sentiment == 'positive' and score > 0.7:
            return {
                'action': 'increase',
                'priority': 'low',
                'reason': 'Sentimiento muy positivo, posible margen para aumento',
                'suggested_change': 5,
            }
        else:
            return {
                'action': 'maintain',
                'priority': 'low',
                'reason': 'Sentimiento neutral sobre precio',
                'suggested_change': 0,
            }
    
    def analyze_competitor_sentiment(
        self,
        competitor_reviews: Dict[str, List[Dict]]
    ) -> Dict:
        """
        Analiza sentimiento de competidores
        
        Args:
            competitor_reviews: Dict con reviews por competidor
        
        Returns:
            Análisis comparativo
        """
        competitor_sentiments = {}
        
        for competitor, reviews in competitor_reviews.items():
            analysis = self.analyze_reviews(competitor, reviews)
            competitor_sentiments[competitor] = analysis
        
        # Comparar sentimientos
        scores = [s.get('score', 0) for s in competitor_sentiments.values()]
        
        return {
            'competitor_sentiments': competitor_sentiments,
            'avg_competitor_score': statistics.mean(scores) if scores else 0,
            'best_sentiment': max(competitor_sentiments.items(), key=lambda x: x[1].get('score', 0))[0] if competitor_sentiments else None,
            'worst_sentiment': min(competitor_sentiments.items(), key=lambda x: x[1].get('score', 0))[0] if competitor_sentiments else None,
        }








