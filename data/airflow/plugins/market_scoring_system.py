"""
Sistema de Scoring Completo de Mercado

Sistema integral de scoring que evalúa múltiples aspectos del mercado:
- Market Attractiveness Score
- Opportunity Score
- Risk Score
- Competitive Position Score
- Overall Market Score
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MarketScore:
    """Score de mercado."""
    score_type: str
    score_value: float  # 0-100
    score_level: str  # 'excellent', 'good', 'fair', 'poor'
    components: Dict[str, float]  # Componentes del score
    factors: List[str]  # Factores que influyen
    recommendation: str


class MarketScoringSystem:
    """Sistema de scoring de mercado."""
    
    def __init__(self):
        """Inicializa el sistema."""
        self.logger = logging.getLogger(__name__)
    
    def calculate_comprehensive_market_score(
        self,
        market_analysis: Dict[str, Any],
        insights: List[Dict[str, Any]],
        all_analyses: Dict[str, Any],
        industry: str
    ) -> Dict[str, Any]:
        """
        Calcula score completo de mercado.
        
        Args:
            market_analysis: Análisis de mercado
            insights: Insights generados
            all_analyses: Todos los análisis
            industry: Industria
            
        Returns:
            Scores completos
        """
        logger.info(f"Calculating comprehensive market scores for {industry}")
        
        scores = {}
        
        # Market Attractiveness Score
        attractiveness_score = self._calculate_attractiveness_score(
            market_analysis,
            all_analyses
        )
        scores["attractiveness"] = attractiveness_score
        
        # Opportunity Score
        opportunity_score = self._calculate_opportunity_score(
            market_analysis,
            insights,
            all_analyses
        )
        scores["opportunity"] = opportunity_score
        
        # Risk Score
        risk_score = self._calculate_risk_score(
            market_analysis,
            insights
        )
        scores["risk"] = risk_score
        
        # Competitive Position Score
        competitive_score = self._calculate_competitive_score(
            all_analyses
        )
        scores["competitive"] = competitive_score
        
        # Overall Market Score
        overall_score = self._calculate_overall_score(scores)
        scores["overall"] = overall_score
        
        return {
            "industry": industry,
            "scoring_date": datetime.utcnow().isoformat(),
            "scores": {
                "attractiveness": {
                    "value": attractiveness_score.score_value,
                    "level": attractiveness_score.score_level,
                    "components": attractiveness_score.components,
                    "recommendation": attractiveness_score.recommendation
                },
                "opportunity": {
                    "value": opportunity_score.score_value,
                    "level": opportunity_score.score_level,
                    "components": opportunity_score.components,
                    "recommendation": opportunity_score.recommendation
                },
                "risk": {
                    "value": risk_score.score_value,
                    "level": risk_score.score_level,
                    "components": risk_score.components,
                    "recommendation": risk_score.recommendation
                },
                "competitive": {
                    "value": competitive_score.score_value,
                    "level": competitive_score.score_level,
                    "components": competitive_score.components,
                    "recommendation": competitive_score.recommendation
                },
                "overall": {
                    "value": overall_score.score_value,
                    "level": overall_score.score_level,
                    "components": overall_score.components,
                    "recommendation": overall_score.recommendation
                }
            },
            "score_summary": self._generate_score_summary(scores)
        }
    
    def _calculate_attractiveness_score(
        self,
        market_analysis: Dict[str, Any],
        all_analyses: Dict[str, Any]
    ) -> MarketScore:
        """Calcula Market Attractiveness Score."""
        score = 50.0  # Base
        components = {}
        factors = []
        
        # Factor 1: Tendencias alcistas (0-25 puntos)
        trends = market_analysis.get("trends", [])
        upward_ratio = len([t for t in trends if t.get("trend_direction") == "up"]) / len(trends) if trends else 0
        trend_score = upward_ratio * 25
        score += trend_score
        components["trends"] = trend_score
        if upward_ratio > 0.6:
            factors.append("Strong upward trends")
        
        # Factor 2: Oportunidades (0-25 puntos)
        opportunities = market_analysis.get("opportunities", [])
        opp_score = min(25, len(opportunities) * 5)
        score += opp_score
        components["opportunities"] = opp_score
        if len(opportunities) > 3:
            factors.append("Multiple opportunities available")
        
        # Factor 3: Sentimiento (0-25 puntos)
        if "sentiment_nlp" in all_analyses:
            sentiment = all_analyses["sentiment_nlp"].get("sentiment_result", {})
            sentiment_val = sentiment.get("average_sentiment_score", 0)
            sentiment_score = (sentiment_val + 1) * 12.5  # Normalizar -1 a 1 -> 0 a 25
            score += sentiment_score
            components["sentiment"] = sentiment_score
            if sentiment_val > 0.3:
                factors.append("Positive market sentiment")
        
        # Factor 4: Crecimiento (0-25 puntos)
        if "demand_forecast" in all_analyses:
            forecast = all_analyses["demand_forecast"]
            if forecast.get("forecast_available"):
                # Usar tendencia de forecast
                growth_score = 20.0  # Simulado
                score += growth_score
                components["growth"] = growth_score
                factors.append("Positive growth forecast")
        
        score = min(100.0, max(0.0, score))
        
        # Determinar nivel
        if score >= 80:
            level = "excellent"
            recommendation = "Highly attractive market - consider aggressive investment"
        elif score >= 65:
            level = "good"
            recommendation = "Attractive market with good opportunities"
        elif score >= 50:
            level = "fair"
            recommendation = "Moderately attractive - selective investment recommended"
        else:
            level = "poor"
            recommendation = "Low attractiveness - cautious approach recommended"
        
        return MarketScore(
            score_type="attractiveness",
            score_value=score,
            score_level=level,
            components=components,
            factors=factors,
            recommendation=recommendation
        )
    
    def _calculate_opportunity_score(
        self,
        market_analysis: Dict[str, Any],
        insights: List[Dict[str, Any]],
        all_analyses: Dict[str, Any]
    ) -> MarketScore:
        """Calcula Opportunity Score."""
        score = 0.0
        components = {}
        factors = []
        
        # Factor 1: Número de oportunidades (0-30 puntos)
        opportunities = market_analysis.get("opportunities", [])
        opp_count_score = min(30, len(opportunities) * 6)
        score += opp_count_score
        components["opportunity_count"] = opp_count_score
        
        # Factor 2: ROI promedio (0-40 puntos)
        if "roi_analysis" in all_analyses:
            roi_report = all_analyses["roi_analysis"].get("roi_report", {})
            avg_roi = roi_report.get("overall_roi_percentage", 0)
            roi_score = min(40, avg_roi / 2.5)  # 100% ROI = 40 puntos
            score += roi_score
            components["roi"] = roi_score
            if avg_roi > 50:
                factors.append("High ROI opportunities")
        
        # Factor 3: Calidad de oportunidades (0-30 puntos)
        high_priority_opps = [o for o in opportunities if o.get("confidence", 0) > 0.8]
        quality_score = min(30, len(high_priority_opps) * 10)
        score += quality_score
        components["quality"] = quality_score
        if len(high_priority_opps) > 2:
            factors.append("High-quality opportunities identified")
        
        score = min(100.0, max(0.0, score))
        
        if score >= 70:
            level = "excellent"
            recommendation = "Excellent opportunities - prioritize and invest"
        elif score >= 50:
            level = "good"
            recommendation = "Good opportunities available"
        else:
            level = "fair"
            recommendation = "Limited opportunities - explore further"
        
        return MarketScore(
            score_type="opportunity",
            score_value=score,
            score_level=level,
            components=components,
            factors=factors,
            recommendation=recommendation
        )
    
    def _calculate_risk_score(
        self,
        market_analysis: Dict[str, Any],
        insights: List[Dict[str, Any]]
    ) -> MarketScore:
        """Calcula Risk Score (menor es mejor, pero normalizamos a 0-100 donde mayor = más riesgo)."""
        risk_value = 0.0
        components = {}
        factors = []
        
        # Factor 1: Número de riesgos (0-40 puntos)
        risks = market_analysis.get("risk_factors", [])
        risk_count_score = min(40, len(risks) * 8)
        risk_value += risk_count_score
        components["risk_count"] = risk_count_score
        
        # Factor 2: Severidad de riesgos (0-40 puntos)
        high_risk = [r for r in risks if r.get("confidence", 0) > 0.8]
        severity_score = min(40, len(high_risk) * 13)
        risk_value += severity_score
        components["severity"] = severity_score
        if len(high_risk) > 1:
            factors.append("Multiple high-severity risks")
        
        # Factor 3: Insights de riesgo (0-20 puntos)
        risk_insights = [i for i in insights if i.get("category") == "threat"]
        insight_score = min(20, len(risk_insights) * 4)
        risk_value += insight_score
        components["risk_insights"] = insight_score
        
        risk_value = min(100.0, max(0.0, risk_value))
        
        # Para risk score, mayor valor = más riesgo
        if risk_value >= 70:
            level = "high"
            recommendation = "High risk level - develop comprehensive mitigation strategy"
        elif risk_value >= 50:
            level = "medium"
            recommendation = "Moderate risk - monitor and mitigate key risks"
        else:
            level = "low"
            recommendation = "Low risk level - maintain current risk management"
        
        return MarketScore(
            score_type="risk",
            score_value=risk_value,
            score_level=level,
            components=components,
            factors=factors,
            recommendation=recommendation
        )
    
    def _calculate_competitive_score(
        self,
        all_analyses: Dict[str, Any]
    ) -> MarketScore:
        """Calcula Competitive Position Score."""
        score = 50.0  # Base
        components = {}
        factors = []
        
        # Factor 1: Benchmarking (0-35 puntos)
        if "benchmark_result" in all_analyses:
            benchmark = all_analyses["benchmark_result"].get("benchmark_result", {})
            performance = benchmark.get("overall_performance", {}).get("level", "unknown")
            benchmark_scores = {
                "excellent": 35,
                "good": 25,
                "fair": 15,
                "poor": 5
            }
            bench_score = benchmark_scores.get(performance, 15)
            score += bench_score
            components["benchmark"] = bench_score
            if performance in ["excellent", "good"]:
                factors.append(f"Strong benchmark performance ({performance})")
        
        # Factor 2: Competitor analysis (0-35 puntos)
        if "competitor_analysis" in all_analyses:
            comp_analysis = all_analyses["competitor_analysis"]
            if comp_analysis.get("analysis_available"):
                # Simular score basado en posición competitiva
                comp_score = 25.0
                score += comp_score
                components["competition"] = comp_score
                factors.append("Competitive position analyzed")
        
        # Factor 3: Market share indicators (0-30 puntos)
        # Simulado - en producción usarías datos reales
        market_share_score = 20.0
        score += market_share_score
        components["market_share"] = market_share_score
        
        score = min(100.0, max(0.0, score))
        
        if score >= 75:
            level = "excellent"
            recommendation = "Strong competitive position - leverage advantages"
        elif score >= 60:
            level = "good"
            recommendation = "Good competitive position - maintain and improve"
        elif score >= 45:
            level = "fair"
            recommendation = "Fair competitive position - focus on differentiation"
        else:
            level = "poor"
            recommendation = "Weak competitive position - urgent improvement needed"
        
        return MarketScore(
            score_type="competitive",
            score_value=score,
            score_level=level,
            components=components,
            factors=factors,
            recommendation=recommendation
        )
    
    def _calculate_overall_score(
        self,
        scores: Dict[str, MarketScore]
    ) -> MarketScore:
        """Calcula Overall Market Score."""
        # Ponderar scores
        weights = {
            "attractiveness": 0.30,
            "opportunity": 0.25,
            "risk": 0.20,  # Invertir porque mayor riesgo = peor
            "competitive": 0.25
        }
        
        overall = 0.0
        components = {}
        
        for score_type, weight in weights.items():
            if score_type in scores:
                score = scores[score_type]
                if score_type == "risk":
                    # Invertir risk score (100 - risk = opportunity)
                    adjusted_score = 100 - score.score_value
                else:
                    adjusted_score = score.score_value
                
                weighted = adjusted_score * weight
                overall += weighted
                components[score_type] = adjusted_score
        
        overall = min(100.0, max(0.0, overall))
        
        if overall >= 80:
            level = "excellent"
            recommendation = "Excellent market conditions - aggressive growth strategy recommended"
        elif overall >= 65:
            level = "good"
            recommendation = "Good market conditions - balanced growth strategy"
        elif overall >= 50:
            level = "fair"
            recommendation = "Fair market conditions - selective investment strategy"
        else:
            level = "poor"
            recommendation = "Challenging market conditions - conservative strategy recommended"
        
        return MarketScore(
            score_type="overall",
            score_value=overall,
            score_level=level,
            components=components,
            factors=["Comprehensive market analysis"],
            recommendation=recommendation
        )
    
    def _generate_score_summary(
        self,
        scores: Dict[str, MarketScore]
    ) -> Dict[str, Any]:
        """Genera resumen de scores."""
        return {
            "overall_score": scores["overall"].score_value,
            "overall_level": scores["overall"].score_level,
            "strongest_area": max(
                [(k, v.score_value) for k, v in scores.items() if k != "risk"],
                key=lambda x: x[1]
            )[0] if scores else "unknown",
            "weakest_area": min(
                [(k, v.score_value) for k, v in scores.items() if k != "risk"],
                key=lambda x: x[1]
            )[0] if scores else "unknown",
            "risk_level": scores.get("risk", MarketScore("risk", 0, "unknown", {}, [], "")).score_level
        }






