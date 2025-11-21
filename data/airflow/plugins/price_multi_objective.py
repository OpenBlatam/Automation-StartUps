"""
Optimización Multi-Objetivo de Precios

Optimiza precios considerando múltiples objetivos simultáneos
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import statistics

logger = logging.getLogger(__name__)


class MultiObjectiveOptimizer:
    """Optimiza precios considerando múltiples objetivos"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get('enable_multi_objective', False)
        self.objectives = config.get('optimization_objectives', {
            'revenue': 0.4,
            'profit': 0.3,
            'market_share': 0.2,
            'customer_satisfaction': 0.1,
        })
    
    def optimize_multi_objective(
        self,
        product_data: Dict,
        market_data: Dict,
        demand_forecast: Optional[Dict] = None,
        price_range: Optional[Tuple[float, float]] = None
    ) -> Dict:
        """
        Optimiza precio considerando múltiples objetivos
        
        Args:
            product_data: Datos del producto
            market_data: Datos de mercado
            demand_forecast: Predicción de demanda
            price_range: Rango de precios (min, max)
        
        Returns:
            Optimización multi-objetivo
        """
        if not self.enabled:
            return {'enabled': False}
        
        current_price = product_data.get('current_price', 0)
        cost = product_data.get('cost', 0)
        
        if not price_range:
            min_price = cost * 1.1 if cost else current_price * 0.8
            max_price = current_price * 1.2
        else:
            min_price, max_price = price_range
        
        # Evaluar diferentes precios
        price_candidates = self._generate_price_candidates(min_price, max_price)
        
        evaluations = []
        for price in price_candidates:
            evaluation = self._evaluate_price(
                price,
                product_data,
                market_data,
                demand_forecast
            )
            evaluations.append(evaluation)
        
        # Encontrar mejor solución (Pareto optimal)
        optimal = self._find_optimal_solution(evaluations)
        
        return {
            'product_id': product_data.get('product_id'),
            'current_price': current_price,
            'optimal_price': optimal['price'],
            'price_change': optimal['price'] - current_price,
            'price_change_percent': (
                ((optimal['price'] - current_price) / current_price * 100)
                if current_price > 0 else 0
            ),
            'objectives_score': optimal['objectives_score'],
            'individual_scores': optimal['individual_scores'],
            'trade_offs': optimal['trade_offs'],
            'recommendation': optimal['recommendation'],
            'evaluated_prices': len(evaluations),
        }
    
    def _generate_price_candidates(
        self,
        min_price: float,
        max_price: float,
        steps: int = 20
    ) -> List[float]:
        """Genera candidatos de precio"""
        step = (max_price - min_price) / steps
        return [round(min_price + step * i, 2) for i in range(steps + 1)]
    
    def _evaluate_price(
        self,
        price: float,
        product_data: Dict,
        market_data: Dict,
        demand_forecast: Optional[Dict]
    ) -> Dict:
        """Evalúa un precio según todos los objetivos"""
        current_price = product_data.get('current_price', 0)
        cost = product_data.get('cost', 0)
        base_demand = demand_forecast.get('base_demand', 100) if demand_forecast else 100
        
        # Calcular demanda estimada
        if demand_forecast and current_price > 0:
            price_change_pct = ((price - current_price) / current_price * 100)
            elasticity = self.config.get('price_elasticity', -1.5)
            demand_change_pct = price_change_pct * elasticity
            estimated_demand = base_demand * (1 + demand_change_pct / 100)
        else:
            estimated_demand = base_demand
        
        # Objetivo 1: Revenue
        revenue = price * estimated_demand
        revenue_score = self._normalize_score(revenue, 0, revenue * 2)
        
        # Objetivo 2: Profit
        if cost > 0:
            profit = (price - cost) * estimated_demand
            profit_score = self._normalize_score(profit, 0, profit * 2)
        else:
            profit = 0
            profit_score = 0.5
        
        # Objetivo 3: Market Share
        avg_market_price = market_data.get('avg_competitor_price', current_price)
        if price <= avg_market_price * 0.95:
            market_share_score = 1.0
        elif price <= avg_market_price:
            market_share_score = 0.7
        elif price <= avg_market_price * 1.05:
            market_share_score = 0.5
        else:
            market_share_score = 0.2
        
        # Objetivo 4: Customer Satisfaction
        # Basado en relación precio/valor percibido
        if cost > 0:
            margin = (price - cost) / cost
            if margin < 0.2:
                satisfaction_score = 0.9  # Buen valor
            elif margin < 0.4:
                satisfaction_score = 0.7
            else:
                satisfaction_score = 0.5  # Puede ser percibido como caro
        else:
            satisfaction_score = 0.5
        
        # Score combinado
        combined_score = (
            revenue_score * self.objectives.get('revenue', 0.4) +
            profit_score * self.objectives.get('profit', 0.3) +
            market_share_score * self.objectives.get('market_share', 0.2) +
            satisfaction_score * self.objectives.get('customer_satisfaction', 0.1)
        )
        
        return {
            'price': price,
            'estimated_demand': estimated_demand,
            'revenue': revenue,
            'profit': profit,
            'individual_scores': {
                'revenue': revenue_score,
                'profit': profit_score,
                'market_share': market_share_score,
                'customer_satisfaction': satisfaction_score,
            },
            'objectives_score': combined_score,
        }
    
    def _normalize_score(self, value: float, min_val: float, max_val: float) -> float:
        """Normaliza un valor a score 0-1"""
        if max_val == min_val:
            return 0.5
        normalized = (value - min_val) / (max_val - min_val)
        return max(0.0, min(1.0, normalized))
    
    def _find_optimal_solution(self, evaluations: List[Dict]) -> Dict:
        """Encuentra solución óptima (mayor score combinado)"""
        optimal = max(evaluations, key=lambda x: x['objectives_score'])
        
        # Calcular trade-offs
        trade_offs = self._calculate_trade_offs(optimal, evaluations)
        
        # Generar recomendación
        recommendation = self._generate_recommendation(optimal, trade_offs)
        
        return {
            **optimal,
            'trade_offs': trade_offs,
            'recommendation': recommendation,
        }
    
    def _calculate_trade_offs(
        self,
        optimal: Dict,
        all_evaluations: List[Dict]
    ) -> Dict:
        """Calcula trade-offs de la solución óptima"""
        avg_revenue = statistics.mean([e['revenue'] for e in all_evaluations])
        avg_profit = statistics.mean([e['profit'] for e in all_evaluations])
        
        return {
            'revenue_vs_avg': optimal['revenue'] - avg_revenue,
            'profit_vs_avg': optimal['profit'] - avg_profit,
            'revenue_improvement_pct': (
                ((optimal['revenue'] - avg_revenue) / avg_revenue * 100)
                if avg_revenue > 0 else 0
            ),
            'profit_improvement_pct': (
                ((optimal['profit'] - avg_profit) / avg_profit * 100)
                if avg_profit > 0 else 0
            ),
        }
    
    def _generate_recommendation(
        self,
        optimal: Dict,
        trade_offs: Dict
    ) -> Dict:
        """Genera recomendación basada en optimización"""
        scores = optimal['individual_scores']
        
        # Identificar objetivos mejor logrados
        best_objective = max(scores.items(), key=lambda x: x[1])
        worst_objective = min(scores.items(), key=lambda x: x[1])
        
        return {
            'action': 'optimize',
            'reason': f'Optimización multi-objetivo: mejor en {best_objective[0]}, mejora en {worst_objective[0]}',
            'strengths': [k for k, v in scores.items() if v > 0.7],
            'improvements': [k for k, v in scores.items() if v < 0.5],
            'expected_revenue_improvement': round(trade_offs.get('revenue_improvement_pct', 0), 2),
            'expected_profit_improvement': round(trade_offs.get('profit_improvement_pct', 0), 2),
        }








