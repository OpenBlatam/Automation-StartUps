"""
Análisis Avanzado de Competencia

Análisis profundo de precios de competencia
"""

import logging
import statistics
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class CompetitorAnalyzer:
    """Analiza precios de competencia en profundidad"""
    
    def __init__(self, config: Dict):
        self.config = config
    
    def analyze_competitor_landscape(
        self,
        current_prices: List[Dict],
        competitor_prices: List[Dict]
    ) -> Dict:
        """
        Analiza el panorama completo de competencia
        
        Args:
            current_prices: Precios actuales
            competitor_prices: Precios de competencia
        
        Returns:
            Análisis completo del panorama
        """
        # Agrupar por producto
        product_analysis = {}
        
        for current in current_prices:
            product_name = current.get('product_name', '').lower()
            current_price = current.get('current_price', 0)
            product_id = current.get('product_id')
            
            if not product_name or current_price <= 0:
                continue
            
            # Buscar competidores para este producto
            competitors = [
                comp for comp in competitor_prices
                if comp.get('product_name', '').lower() == product_name
            ]
            
            if competitors:
                analysis = self._analyze_product_competition(
                    current_price,
                    competitors
                )
                product_analysis[product_id or product_name] = {
                    'product_name': current.get('product_name'),
                    'current_price': current_price,
                    'competitor_count': len(competitors),
                    **analysis
                }
        
        # Análisis agregado
        aggregate = self._calculate_aggregate_metrics(product_analysis)
        
        return {
            'products_analyzed': len(product_analysis),
            'product_analysis': product_analysis,
            'aggregate_metrics': aggregate,
            'generated_at': datetime.now().isoformat(),
        }
    
    def _analyze_product_competition(
        self,
        current_price: float,
        competitors: List[Dict]
    ) -> Dict:
        """Analiza competencia para un producto específico"""
        comp_prices = [
            c.get('avg_competitor_price', 0) or c.get('competitor_price', 0)
            for c in competitors
            if (c.get('avg_competitor_price', 0) or c.get('competitor_price', 0)) > 0
        ]
        
        if not comp_prices:
            return {'error': 'No valid competitor prices'}
        
        avg_competitor = statistics.mean(comp_prices)
        min_competitor = min(comp_prices)
        max_competitor = max(comp_prices)
        median_competitor = statistics.median(comp_prices)
        
        # Posición relativa
        if current_price < min_competitor:
            position = 'lowest'
            percentile = 0
        elif current_price > max_competitor:
            position = 'highest'
            percentile = 100
        else:
            # Calcular percentil aproximado
            below_count = sum(1 for p in comp_prices if p < current_price)
            percentile = (below_count / len(comp_prices)) * 100
            
            if percentile < 25:
                position = 'low'
            elif percentile < 50:
                position = 'below_median'
            elif percentile < 75:
                position = 'above_median'
            else:
                position = 'high'
        
        # Diferencias
        diff_from_avg = current_price - avg_competitor
        diff_from_avg_pct = (diff_from_avg / avg_competitor * 100) if avg_competitor > 0 else 0
        
        diff_from_min = current_price - min_competitor
        diff_from_max = current_price - max_competitor
        
        # Recomendación
        recommendation = self._generate_recommendation(
            current_price,
            avg_competitor,
            min_competitor,
            max_competitor,
            position
        )
        
        return {
            'avg_competitor_price': round(avg_competitor, 2),
            'min_competitor_price': round(min_competitor, 2),
            'max_competitor_price': round(max_competitor, 2),
            'median_competitor_price': round(median_competitor, 2),
            'price_range': round(max_competitor - min_competitor, 2),
            'position': position,
            'percentile': round(percentile, 2),
            'diff_from_avg': round(diff_from_avg, 2),
            'diff_from_avg_percent': round(diff_from_avg_pct, 2),
            'diff_from_min': round(diff_from_min, 2),
            'diff_from_max': round(diff_from_max, 2),
            'recommendation': recommendation,
            'competitor_count': len(comp_prices),
        }
    
    def _generate_recommendation(
        self,
        current_price: float,
        avg_competitor: float,
        min_competitor: float,
        max_competitor: float,
        position: str
    ) -> Dict:
        """Genera recomendación basada en análisis"""
        if position == 'highest':
            return {
                'action': 'decrease',
                'target_price': round(avg_competitor * 0.98, 2),
                'reason': 'Precio muy por encima del mercado',
                'priority': 'high'
            }
        elif position == 'lowest':
            return {
                'action': 'increase',
                'target_price': round(avg_competitor * 1.02, 2),
                'reason': 'Precio muy por debajo del mercado',
                'priority': 'medium'
            }
        elif current_price > avg_competitor * 1.1:
            return {
                'action': 'decrease',
                'target_price': round(avg_competitor, 2),
                'reason': 'Precio significativamente por encima del promedio',
                'priority': 'medium'
            }
        elif current_price < avg_competitor * 0.9:
            return {
                'action': 'increase',
                'target_price': round(avg_competitor, 2),
                'reason': 'Precio significativamente por debajo del promedio',
                'priority': 'low'
            }
        else:
            return {
                'action': 'maintain',
                'target_price': round(current_price, 2),
                'reason': 'Precio competitivo',
                'priority': 'low'
            }
    
    def _calculate_aggregate_metrics(self, product_analysis: Dict) -> Dict:
        """Calcula métricas agregadas"""
        if not product_analysis:
            return {}
        
        positions = [a.get('position') for a in product_analysis.values()]
        position_counts = defaultdict(int)
        for pos in positions:
            position_counts[pos] += 1
        
        recommendations = [a.get('recommendation', {}) for a in product_analysis.values()]
        action_counts = defaultdict(int)
        for rec in recommendations:
            action = rec.get('action', 'unknown')
            action_counts[action] += 1
        
        total_products = len(product_analysis)
        
        return {
            'total_products': total_products,
            'position_distribution': dict(position_counts),
            'recommendation_distribution': dict(action_counts),
            'products_above_market': position_counts.get('high', 0) + position_counts.get('highest', 0),
            'products_below_market': position_counts.get('low', 0) + position_counts.get('lowest', 0),
            'products_in_market': total_products - position_counts.get('high', 0) - position_counts.get('highest', 0) - position_counts.get('low', 0) - position_counts.get('lowest', 0),
        }
    
    def identify_opportunities(
        self,
        competitor_analysis: Dict
    ) -> List[Dict]:
        """
        Identifica oportunidades de optimización
        
        Args:
            competitor_analysis: Resultado de analyze_competitor_landscape
        
        Returns:
            Lista de oportunidades
        """
        opportunities = []
        product_analysis = competitor_analysis.get('product_analysis', {})
        
        for product_id, analysis in product_analysis.items():
            recommendation = analysis.get('recommendation', {})
            priority = recommendation.get('priority', 'low')
            
            if priority in ['high', 'medium']:
                opportunities.append({
                    'product_id': product_id,
                    'product_name': analysis.get('product_name'),
                    'current_price': analysis.get('current_price'),
                    'recommended_price': recommendation.get('target_price'),
                    'action': recommendation.get('action'),
                    'reason': recommendation.get('reason'),
                    'priority': priority,
                    'potential_impact': self._estimate_impact(analysis),
                })
        
        # Ordenar por prioridad e impacto
        opportunities.sort(
            key=lambda x: (
                {'high': 3, 'medium': 2, 'low': 1}.get(x['priority'], 0),
                x.get('potential_impact', 0)
            ),
            reverse=True
        )
        
        return opportunities
    
    def _estimate_impact(self, analysis: Dict) -> float:
        """Estima impacto potencial de ajuste"""
        current_price = analysis.get('current_price', 0)
        recommended = analysis.get('recommendation', {}).get('target_price', current_price)
        diff_pct = abs((recommended - current_price) / current_price * 100) if current_price > 0 else 0
        
        # Impacto basado en diferencia y posición
        position_factor = {
            'highest': 1.5,
            'high': 1.2,
            'lowest': 1.0,
            'low': 0.8,
        }.get(analysis.get('position', ''), 1.0)
        
        return round(diff_pct * position_factor, 2)








