"""
Análisis de Keywords y SEO para Investigación de Mercado

Analiza keywords relevantes para la industria y proporciona insights SEO:
- Análisis de volumen de búsqueda
- Análisis de competencia de keywords
- Oportunidades de keywords
- Tendencias de keywords
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class KeywordAnalysis:
    """Análisis de keyword."""
    keyword: str
    search_volume: int
    competition_level: str  # 'low', 'medium', 'high'
    competition_score: float  # 0-1
    trend_direction: str  # 'up', 'down', 'stable'
    trend_percentage: float
    opportunity_score: float  # 0-100
    difficulty: int  # 0-100
    cpc_estimate: float  # Cost per click estimado
    related_keywords: List[str]


class MarketKeywordSEOAnalyzer:
    """Analizador de keywords y SEO."""
    
    def __init__(self):
        """Inicializa el analizador."""
        self.logger = logging.getLogger(__name__)
    
    def analyze_keywords(
        self,
        industry: str,
        base_keywords: List[str],
        timeframe_months: int = 6
    ) -> Dict[str, Any]:
        """
        Analiza keywords para una industria.
        
        Args:
            industry: Industria
            base_keywords: Keywords base
            timeframe_months: Período de análisis
            
        Returns:
            Análisis completo de keywords
        """
        logger.info(f"Analyzing keywords for {industry}")
        
        keyword_analyses = []
        
        for keyword in base_keywords:
            analysis = self._analyze_single_keyword(keyword, industry)
            keyword_analyses.append(analysis)
        
        # Generar keywords relacionados
        related_keywords = self._generate_related_keywords(base_keywords, industry)
        
        # Identificar oportunidades
        opportunities = self._identify_keyword_opportunities(keyword_analyses)
        
        # Análisis de tendencias
        trends = self._analyze_keyword_trends(keyword_analyses)
        
        return {
            "industry": industry,
            "analysis_date": datetime.utcnow().isoformat(),
            "timeframe_months": timeframe_months,
            "keywords_analyzed": len(keyword_analyses),
            "keyword_analyses": [
                {
                    "keyword": k.keyword,
                    "search_volume": k.search_volume,
                    "competition_level": k.competition_level,
                    "competition_score": k.competition_score,
                    "trend_direction": k.trend_direction,
                    "trend_percentage": k.trend_percentage,
                    "opportunity_score": k.opportunity_score,
                    "difficulty": k.difficulty,
                    "cpc_estimate": k.cpc_estimate,
                    "related_keywords": k.related_keywords
                }
                for k in keyword_analyses
            ],
            "related_keywords": related_keywords,
            "opportunities": opportunities,
            "trends": trends
        }
    
    def _analyze_single_keyword(
        self,
        keyword: str,
        industry: str
    ) -> KeywordAnalysis:
        """Analiza un keyword individual."""
        # Simulación de análisis (en producción usarías APIs reales como Google Keyword Planner)
        search_volume = len(keyword) * 1000  # Simulado
        competition_score = 0.5  # Simulado
        
        # Determinar nivel de competencia
        if competition_score < 0.3:
            competition_level = "low"
            difficulty = 30
        elif competition_score < 0.7:
            competition_level = "medium"
            difficulty = 60
        else:
            competition_level = "high"
            difficulty = 85
        
        # Simular tendencia
        trend_percentage = 10.0  # Simulado
        trend_direction = "up" if trend_percentage > 0 else "down" if trend_percentage < 0 else "stable"
        
        # Calcular opportunity score
        opportunity_score = self._calculate_opportunity_score(
            search_volume,
            competition_score,
            trend_percentage
        )
        
        # CPC estimado
        cpc_estimate = competition_score * 5.0  # Simulado
        
        # Keywords relacionados
        related_keywords = self._get_related_keywords(keyword, industry)
        
        return KeywordAnalysis(
            keyword=keyword,
            search_volume=search_volume,
            competition_level=competition_level,
            competition_score=competition_score,
            trend_direction=trend_direction,
            trend_percentage=trend_percentage,
            opportunity_score=opportunity_score,
            difficulty=difficulty,
            cpc_estimate=cpc_estimate,
            related_keywords=related_keywords
        )
    
    def _calculate_opportunity_score(
        self,
        search_volume: int,
        competition_score: float,
        trend_percentage: float
    ) -> float:
        """Calcula score de oportunidad para un keyword."""
        score = 0.0
        
        # Factor 1: Volumen de búsqueda (0-40 puntos)
        if search_volume > 10000:
            score += 40
        elif search_volume > 5000:
            score += 30
        elif search_volume > 1000:
            score += 20
        else:
            score += 10
        
        # Factor 2: Baja competencia (0-40 puntos)
        if competition_score < 0.3:
            score += 40
        elif competition_score < 0.5:
            score += 30
        elif competition_score < 0.7:
            score += 20
        else:
            score += 10
        
        # Factor 3: Tendencias positivas (0-20 puntos)
        if trend_percentage > 20:
            score += 20
        elif trend_percentage > 10:
            score += 15
        elif trend_percentage > 0:
            score += 10
        
        return min(100.0, score)
    
    def _get_related_keywords(
        self,
        keyword: str,
        industry: str
    ) -> List[str]:
        """Obtiene keywords relacionados."""
        # Simulado - en producción usarías APIs de keywords
        related = [
            f"{keyword} {industry}",
            f"{industry} {keyword}",
            f"best {keyword}",
            f"{keyword} trends"
        ]
        return related[:5]
    
    def _generate_related_keywords(
        self,
        base_keywords: List[str],
        industry: str
    ) -> List[str]:
        """Genera keywords relacionados adicionales."""
        related = []
        
        # Agregar variaciones
        for keyword in base_keywords:
            related.extend([
                f"{keyword} software",
                f"{keyword} solutions",
                f"{keyword} platform",
                f"{keyword} tools"
            ])
        
        return list(set(related))[:20]  # Top 20 únicos
    
    def _identify_keyword_opportunities(
        self,
        keyword_analyses: List[KeywordAnalysis]
    ) -> List[Dict[str, Any]]:
        """Identifica oportunidades de keywords."""
        opportunities = []
        
        for analysis in keyword_analyses:
            if analysis.opportunity_score > 70:
                opportunities.append({
                    "keyword": analysis.keyword,
                    "opportunity_score": analysis.opportunity_score,
                    "search_volume": analysis.search_volume,
                    "competition_level": analysis.competition_level,
                    "recommendation": f"High opportunity keyword with {analysis.search_volume} monthly searches and {analysis.competition_level} competition"
                })
        
        # Ordenar por opportunity score
        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        
        return opportunities[:10]  # Top 10
    
    def _analyze_keyword_trends(
        self,
        keyword_analyses: List[KeywordAnalysis]
    ) -> Dict[str, Any]:
        """Analiza tendencias de keywords."""
        upward_trends = len([k for k in keyword_analyses if k.trend_direction == "up"])
        downward_trends = len([k for k in keyword_analyses if k.trend_direction == "down"])
        stable_trends = len([k for k in keyword_analyses if k.trend_direction == "stable"])
        
        avg_trend = sum(k.trend_percentage for k in keyword_analyses) / len(keyword_analyses) if keyword_analyses else 0
        
        return {
            "upward_trends": upward_trends,
            "downward_trends": downward_trends,
            "stable_trends": stable_trends,
            "average_trend_percentage": avg_trend,
            "overall_trend": "up" if avg_trend > 5 else "down" if avg_trend < -5 else "stable"
        }
    
    def generate_seo_recommendations(
        self,
        keyword_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Genera recomendaciones SEO basadas en análisis de keywords."""
        recommendations = []
        
        opportunities = keyword_analysis.get("opportunities", [])
        
        for opp in opportunities[:5]:  # Top 5
            recommendations.append({
                "type": "keyword_optimization",
                "title": f"Optimize for '{opp['keyword']}'",
                "description": opp["recommendation"],
                "priority": "high" if opp["opportunity_score"] > 80 else "medium",
                "actionable_steps": [
                    f"Create content targeting '{opp['keyword']}'",
                    f"Optimize existing pages for '{opp['keyword']}'",
                    f"Build backlinks with '{opp['keyword']}' anchor text",
                    f"Monitor ranking for '{opp['keyword']}'"
                ],
                "expected_impact": f"Potential {opp['search_volume']} monthly organic visits"
            })
        
        return recommendations






