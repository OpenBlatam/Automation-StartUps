"""
Análisis Comparativo Multi-Industria

Compara el mercado entre múltiples industrias:
- Comparación de tendencias entre industrias
- Análisis de performance relativa
- Identificación de mejores prácticas
- Oportunidades cross-industry
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class IndustryComparison:
    """Comparación entre industrias."""
    industry_1: str
    industry_2: str
    comparison_metric: str
    industry_1_value: float
    industry_2_value: float
    difference_percentage: float
    better_performer: str
    insights: List[str]


class MarketComparativeAnalyzer:
    """Analizador comparativo multi-industria."""
    
    def __init__(self):
        """Inicializa el analizador."""
        self.logger = logging.getLogger(__name__)
    
    def compare_industries(
        self,
        industries_data: Dict[str, Dict[str, Any]],
        primary_industry: str
    ) -> Dict[str, Any]:
        """
        Compara múltiples industrias.
        
        Args:
            industries_data: Datos de múltiples industrias {industry: analysis_data}
            primary_industry: Industria principal a comparar
            
        Returns:
            Análisis comparativo
        """
        logger.info(f"Comparing {primary_industry} with {len(industries_data) - 1} other industries")
        
        if primary_industry not in industries_data:
            return {"error": "Primary industry not found in data"}
        
        primary_data = industries_data[primary_industry]
        comparisons = []
        
        for industry, data in industries_data.items():
            if industry == primary_industry:
                continue
            
            comparison = self._compare_two_industries(
                primary_industry,
                industry,
                primary_data,
                data
            )
            comparisons.append(comparison)
        
        # Análisis agregado
        aggregated_analysis = self._aggregate_comparisons(comparisons, primary_industry)
        
        return {
            "primary_industry": primary_industry,
            "compared_industries": list(industries_data.keys()),
            "analysis_date": datetime.utcnow().isoformat(),
            "comparisons": [
                {
                    "industry_1": c.industry_1,
                    "industry_2": c.industry_2,
                    "comparison_metric": c.comparison_metric,
                    "industry_1_value": c.industry_1_value,
                    "industry_2_value": c.industry_2_value,
                    "difference_percentage": c.difference_percentage,
                    "better_performer": c.better_performer,
                    "insights": c.insights
                }
                for c in comparisons
            ],
            "aggregated_analysis": aggregated_analysis
        }
    
    def _compare_two_industries(
        self,
        industry_1: str,
        industry_2: str,
        data_1: Dict[str, Any],
        data_2: Dict[str, Any]
    ) -> IndustryComparison:
        """Compara dos industrias."""
        # Comparar número de tendencias alcistas
        trends_1 = data_1.get("trends", [])
        trends_2 = data_2.get("trends", [])
        
        upward_1 = len([t for t in trends_1 if t.get("trend_direction") == "up"]) / len(trends_1) if trends_1 else 0
        upward_2 = len([t for t in trends_2 if t.get("trend_direction") == "up"]) / len(trends_2) if trends_2 else 0
        
        diff_pct = ((upward_1 - upward_2) / upward_2 * 100) if upward_2 > 0 else 0
        better = industry_1 if upward_1 > upward_2 else industry_2
        
        insights = [
            f"{better} has {abs(diff_pct):.1f}% {'more' if diff_pct > 0 else 'fewer'} upward trends",
            f"Market momentum: {'Stronger' if upward_1 > upward_2 else 'Weaker'} in {industry_1}"
        ]
        
        return IndustryComparison(
            industry_1=industry_1,
            industry_2=industry_2,
            comparison_metric="upward_trends_ratio",
            industry_1_value=upward_1 * 100,
            industry_2_value=upward_2 * 100,
            difference_percentage=diff_pct,
            better_performer=better,
            insights=insights
        )
    
    def _aggregate_comparisons(
        self,
        comparisons: List[IndustryComparison],
        primary_industry: str
    ) -> Dict[str, Any]:
        """Agrega comparaciones."""
        primary_wins = len([c for c in comparisons if c.better_performer == primary_industry])
        total_comparisons = len(comparisons)
        
        avg_difference = sum(abs(c.difference_percentage) for c in comparisons) / total_comparisons if comparisons else 0
        
        return {
            "primary_industry_performance": f"{primary_wins}/{total_comparisons} comparisons won",
            "average_difference": avg_difference,
            "relative_position": "above_average" if primary_wins > total_comparisons / 2 else "below_average",
            "recommendation": self._generate_recommendation(primary_wins, total_comparisons)
        }
    
    def _generate_recommendation(
        self,
        primary_wins: int,
        total: int
    ) -> str:
        """Genera recomendación basada en comparación."""
        win_rate = primary_wins / total if total > 0 else 0
        
        if win_rate > 0.7:
            return "Strong performance relative to other industries - maintain current strategy"
        elif win_rate > 0.5:
            return "Average performance - identify improvement opportunities from top performers"
        else:
            return "Below average performance - urgent need to learn from better-performing industries"






