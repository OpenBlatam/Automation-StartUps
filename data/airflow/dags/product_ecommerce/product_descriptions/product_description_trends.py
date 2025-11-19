"""
Análisis de tendencias de mercado para optimizar descripciones.

Incluye:
- Análisis de keywords trending
- Tendencias de productos
- Análisis estacional
- Insights de mercado
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import Counter
import requests

logger = logging.getLogger(__name__)


class MarketTrendsAnalyzer:
    """Analizador de tendencias de mercado."""
    
    def __init__(self, google_trends_api_key: Optional[str] = None):
        """
        Inicializa el analizador.
        
        Args:
            google_trends_api_key: API key de Google Trends (opcional)
        """
        self.google_trends_api_key = google_trends_api_key
    
    def analyze_keyword_trends(self, keywords: List[str], days: int = 90) -> Dict:
        """
        Analiza tendencias de keywords.
        
        Args:
            keywords: Lista de keywords a analizar
            days: Días hacia atrás para análisis
        
        Returns:
            Dict con análisis de tendencias
        """
        # Simulación de análisis de tendencias
        # En producción, integrar con Google Trends API o similar
        
        trends = {}
        for keyword in keywords:
            # Simular datos de tendencia
            trend_score = self._calculate_trend_score(keyword)
            trends[keyword] = {
                'trend_score': trend_score,
                'trend_direction': 'up' if trend_score > 50 else 'down',
                'recommendation': self._get_trend_recommendation(trend_score),
                'seasonality': self._detect_seasonality(keyword)
            }
        
        return {
            'keywords_analyzed': len(keywords),
            'period_days': days,
            'trends': trends,
            'top_trending': sorted(trends.items(), key=lambda x: x[1]['trend_score'], reverse=True)[:5],
            'insights': self._generate_trend_insights(trends)
        }
    
    def analyze_product_trends(self, product_type: str, category: str = None) -> Dict:
        """
        Analiza tendencias de un tipo de producto.
        
        Args:
            product_type: Tipo de producto
            category: Categoría opcional
        
        Returns:
            Dict con análisis de tendencias del producto
        """
        # Análisis de tendencias del producto
        trending_keywords = self._get_trending_keywords_for_product(product_type)
        seasonal_patterns = self._analyze_seasonal_patterns(product_type)
        
        return {
            'product_type': product_type,
            'category': category,
            'trending_keywords': trending_keywords,
            'seasonal_patterns': seasonal_patterns,
            'recommendations': self._generate_product_recommendations(product_type, trending_keywords)
        }
    
    def get_optimal_keywords(self, base_keywords: List[str], product_type: str) -> List[str]:
        """
        Sugiere keywords óptimas basadas en tendencias.
        
        Args:
            base_keywords: Keywords base
            product_type: Tipo de producto
        
        Returns:
            Lista de keywords optimizadas con tendencias
        """
        # Analizar tendencias de keywords base
        trends = self.analyze_keyword_trends(base_keywords)
        
        # Obtener keywords trending del tipo de producto
        product_trends = self.analyze_product_trends(product_type)
        
        # Combinar y optimizar
        optimal = []
        
        # Agregar keywords base con buena tendencia
        for keyword, trend_data in trends['trends'].items():
            if trend_data['trend_score'] > 50:
                optimal.append(keyword)
        
        # Agregar keywords trending del producto
        for keyword in product_trends['trending_keywords'][:5]:
            if keyword not in optimal:
                optimal.append(keyword)
        
        return optimal[:15]  # Máximo 15 keywords
    
    def _calculate_trend_score(self, keyword: str) -> float:
        """Calcula score de tendencia (0-100)."""
        # Simulación: en producción usar API real
        import random
        return random.uniform(30, 90)  # Placeholder
    
    def _get_trend_recommendation(self, score: float) -> str:
        """Obtiene recomendación basada en score."""
        if score > 70:
            return 'Alta tendencia - Usar como keyword principal'
        elif score > 50:
            return 'Tendencia moderada - Incluir en descripción'
        else:
            return 'Baja tendencia - Considerar alternativas'
    
    def _detect_seasonality(self, keyword: str) -> Optional[str]:
        """Detecta patrones estacionales."""
        seasonal_keywords = {
            'navidad': 'winter',
            'verano': 'summer',
            'invierno': 'winter',
            'primavera': 'spring',
            'otoño': 'fall',
            'christmas': 'winter',
            'summer': 'summer',
            'winter': 'winter'
        }
        
        keyword_lower = keyword.lower()
        for seasonal, season in seasonal_keywords.items():
            if seasonal in keyword_lower:
                return season
        
        return None
    
    def _get_trending_keywords_for_product(self, product_type: str) -> List[str]:
        """Obtiene keywords trending para un tipo de producto."""
        # Simulación: en producción usar API real
        return [
            f'{product_type} 2024',
            f'nuevo {product_type}',
            f'mejor {product_type}',
            f'{product_type} premium',
            f'{product_type} ecológico'
        ]
    
    def _analyze_seasonal_patterns(self, product_type: str) -> Dict:
        """Analiza patrones estacionales."""
        return {
            'peak_seasons': ['winter', 'summer'],
            'low_seasons': ['spring', 'fall'],
            'recommendations': [
                'Aumentar keywords estacionales en temporadas pico',
                'Ajustar descripciones según estación'
            ]
        }
    
    def _generate_trend_insights(self, trends: Dict) -> List[str]:
        """Genera insights de tendencias."""
        insights = []
        
        trending_count = sum(1 for t in trends.values() if t['trend_score'] > 70)
        if trending_count > 0:
            insights.append(f"{trending_count} keywords están en alta tendencia - aprovecha ahora")
        
        declining_count = sum(1 for t in trends.values() if t['trend_score'] < 40)
        if declining_count > 0:
            insights.append(f"{declining_count} keywords están en declive - considera alternativas")
        
        seasonal_keywords = [k for k, t in trends.items() if t.get('seasonality')]
        if seasonal_keywords:
            insights.append(f"Keywords estacionales detectadas: ajusta según temporada")
        
        return insights
    
    def _generate_product_recommendations(self, product_type: str, trending_keywords: List[str]) -> List[str]:
        """Genera recomendaciones para el producto."""
        recommendations = [
            f"Incluye keywords trending: {', '.join(trending_keywords[:3])}",
            "Actualiza descripciones regularmente con keywords en tendencia",
            "Monitorea cambios estacionales en búsquedas"
        ]
        return recommendations


class SmartAlerts:
    """Sistema de alertas inteligentes para descripciones."""
    
    ALERT_TYPES = {
        'low_conversion': 'Conversión por debajo del umbral',
        'seo_degradation': 'Score SEO disminuyó significativamente',
        'trending_opportunity': 'Keyword trending detectada',
        'competitor_update': 'Competidor actualizó descripción',
        'quality_threshold': 'Calidad alcanzó umbral objetivo'
    }
    
    def __init__(self):
        self.alert_history = []
        self.thresholds = {
            'conversion_rate': 0.02,  # 2%
            'seo_score': 60,
            'quality_score': 70
        }
    
    def check_alerts(self, description_data: Dict, metrics: Dict = None) -> List[Dict]:
        """
        Verifica y genera alertas para una descripción.
        
        Args:
            description_data: Datos de la descripción
            metrics: Métricas de rendimiento (opcional)
        
        Returns:
            Lista de alertas generadas
        """
        alerts = []
        
        # Alerta de calidad
        quality_score = description_data.get('full_analysis', {}).get('quality_score', {}).get('total_score', 0)
        if quality_score < self.thresholds['quality_score']:
            alerts.append({
                'type': 'quality_threshold',
                'severity': 'medium',
                'message': f'Score de calidad ({quality_score}) por debajo del umbral ({self.thresholds["quality_score"]})',
                'recommendation': 'Revisa las recomendaciones de calidad y optimiza la descripción'
            })
        
        # Alerta de SEO
        seo_score = description_data.get('seo_analysis', {}).get('score', 0)
        if seo_score < self.thresholds['seo_score']:
            alerts.append({
                'type': 'seo_degradation',
                'severity': 'high',
                'message': f'Score SEO ({seo_score}) por debajo del umbral ({self.thresholds["seo_score"]})',
                'recommendation': 'Optimiza keywords y mejora la densidad SEO'
            })
        
        # Alerta de conversión (si hay métricas)
        if metrics:
            conversion_rate = metrics.get('conversion_rate', 0)
            if conversion_rate < self.thresholds['conversion_rate']:
                alerts.append({
                    'type': 'low_conversion',
                    'severity': 'high',
                    'message': f'Tasa de conversión ({conversion_rate:.2%}) por debajo del umbral ({self.thresholds["conversion_rate"]:.2%})',
                    'recommendation': 'Revisa CTA, bullets y optimización de conversión'
                })
        
        # Registrar alertas
        for alert in alerts:
            self.alert_history.append({
                **alert,
                'description_id': description_data.get('product_description_id'),
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts
    
    def get_alert_summary(self, days: int = 7) -> Dict:
        """
        Obtiene resumen de alertas recientes.
        
        Args:
            days: Días a analizar
        
        Returns:
            Dict con resumen de alertas
        """
        cutoff = datetime.now() - timedelta(days=days)
        recent_alerts = [
            a for a in self.alert_history
            if datetime.fromisoformat(a['timestamp']) >= cutoff
        ]
        
        by_type = Counter(a['type'] for a in recent_alerts)
        by_severity = Counter(a['severity'] for a in recent_alerts)
        
        return {
            'total_alerts': len(recent_alerts),
            'period_days': days,
            'by_type': dict(by_type),
            'by_severity': dict(by_severity),
            'recent_alerts': recent_alerts[-10:]  # Últimas 10
        }






