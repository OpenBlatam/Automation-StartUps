"""
Sistema de Recomendaciones de Estrategia de Mercado

Genera recomendaciones estratégicas basadas en análisis completo:
- Estrategias de crecimiento
- Estrategias de diferenciación
- Estrategias de penetración
- Estrategias de diversificación
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MarketStrategy:
    """Estrategia de mercado."""
    strategy_id: str
    strategy_name: str
    strategy_type: str  # 'growth', 'differentiation', 'penetration', 'diversification'
    priority: str  # 'high', 'medium', 'low'
    expected_impact: str
    implementation_timeframe: str
    required_resources: Dict[str, Any]
    success_metrics: List[str]
    risk_level: str
    confidence: float  # 0-1


class MarketStrategyRecommender:
    """Recomendador de estrategias de mercado."""
    
    def __init__(self):
        """Inicializa el recomendador."""
        self.logger = logging.getLogger(__name__)
    
    def generate_strategy_recommendations(
        self,
        market_analysis: Dict[str, Any],
        all_analyses: Dict[str, Any],
        industry: str
    ) -> Dict[str, Any]:
        """
        Genera recomendaciones de estrategia.
        
        Args:
            market_analysis: Análisis de mercado
            all_analyses: Todos los análisis realizados
            industry: Industria
            
        Returns:
            Recomendaciones de estrategia
        """
        logger.info(f"Generating strategy recommendations for {industry}")
        
        strategies = []
        
        # Estrategia basada en oportunidades
        if "roi_analysis" in all_analyses:
            roi_report = all_analyses["roi_analysis"].get("roi_report", {})
            top_opportunities = roi_report.get("top_opportunities", [])
            
            if top_opportunities:
                growth_strategy = self._create_growth_strategy(
                    top_opportunities[0],
                    market_analysis,
                    industry
                )
                strategies.append(growth_strategy)
        
        # Estrategia basada en competencia
        if "competitor_analysis" in all_analyses:
            competitor_data = all_analyses.get("competitor_analysis", {})
            if competitor_data.get("analysis_available"):
                differentiation_strategy = self._create_differentiation_strategy(
                    market_analysis,
                    competitor_data,
                    industry
                )
                strategies.append(differentiation_strategy)
        
        # Estrategia basada en segmentación
        if "market_segmentation" in all_analyses:
            segmentation = all_analyses["market_segmentation"].get("segmentation", {})
            penetration_strategy = self._create_penetration_strategy(
                segmentation,
                industry
            )
            strategies.append(penetration_strategy)
        
        # Estrategia basada en tendencias emergentes
        if "emerging_trends" in all_analyses:
            emerging = all_analyses["emerging_trends"]
            if emerging.get("analysis_available"):
                diversification_strategy = self._create_diversification_strategy(
                    emerging,
                    industry
                )
                strategies.append(diversification_strategy)
        
        # Ordenar por prioridad
        strategies.sort(
            key=lambda s: {"high": 3, "medium": 2, "low": 1}.get(s.priority, 0),
            reverse=True
        )
        
        return {
            "industry": industry,
            "analysis_date": datetime.utcnow().isoformat(),
            "total_strategies": len(strategies),
            "strategies": [
                {
                    "strategy_id": s.strategy_id,
                    "strategy_name": s.strategy_name,
                    "strategy_type": s.strategy_type,
                    "priority": s.priority,
                    "expected_impact": s.expected_impact,
                    "implementation_timeframe": s.implementation_timeframe,
                    "required_resources": s.required_resources,
                    "success_metrics": s.success_metrics,
                    "risk_level": s.risk_level,
                    "confidence": s.confidence
                }
                for s in strategies
            ],
            "recommended_strategy": strategies[0] if strategies else None
        }
    
    def _create_growth_strategy(
        self,
        opportunity: Dict[str, Any],
        market_analysis: Dict[str, Any],
        industry: str
    ) -> MarketStrategy:
        """Crea estrategia de crecimiento."""
        return MarketStrategy(
            strategy_id=f"growth_{datetime.utcnow().timestamp()}",
            strategy_name=f"Growth Strategy: {opportunity.get('title', 'Opportunity')}",
            strategy_type="growth",
            priority="high",
            expected_impact=f"High ROI opportunity with {opportunity.get('roi_analysis', {}).get('roi_percentage', 0):.1f}% expected return",
            implementation_timeframe="3-6 months",
            required_resources={
                "budget": opportunity.get("roi_analysis", {}).get("investment_required", 100000),
                "team_size": 5,
                "technology": "standard"
            },
            success_metrics=[
                "Revenue growth > 20%",
                "Market share increase",
                "ROI > 30%"
            ],
            risk_level="medium",
            confidence=0.8
        )
    
    def _create_differentiation_strategy(
        self,
        market_analysis: Dict[str, Any],
        competitor_data: Dict[str, Any],
        industry: str
    ) -> MarketStrategy:
        """Crea estrategia de diferenciación."""
        return MarketStrategy(
            strategy_id=f"differentiation_{datetime.utcnow().timestamp()}",
            strategy_name="Differentiation Strategy",
            strategy_type="differentiation",
            priority="medium",
            expected_impact="Stand out from competitors through unique value proposition",
            implementation_timeframe="6-12 months",
            required_resources={
                "budget": 200000,
                "team_size": 8,
                "technology": "advanced"
            },
            success_metrics=[
                "Brand recognition increase",
                "Customer loyalty improvement",
                "Premium pricing capability"
            ],
            risk_level="low",
            confidence=0.7
        )
    
    def _create_penetration_strategy(
        self,
        segmentation: Dict[str, Any],
        industry: str
    ) -> MarketStrategy:
        """Crea estrategia de penetración."""
        segments = segmentation.get("segments", [])
        most_attractive = max(segments, key=lambda s: s.get("attractiveness_score", 0)) if segments else None
        
        return MarketStrategy(
            strategy_id=f"penetration_{datetime.utcnow().timestamp()}",
            strategy_name=f"Market Penetration: {most_attractive.get('segment_name', 'Target Segment') if most_attractive else 'Market'}",
            strategy_type="penetration",
            priority="high" if most_attractive and most_attractive.get("attractiveness_score", 0) > 70 else "medium",
            expected_impact=f"Increase market share in {most_attractive.get('segment_name', 'target segment') if most_attractive else 'target market'}",
            implementation_timeframe="3-9 months",
            required_resources={
                "budget": 150000,
                "team_size": 6,
                "technology": "standard"
            },
            success_metrics=[
                "Market share increase > 10%",
                "Customer acquisition growth",
                "Revenue from segment > 30%"
            ],
            risk_level="medium",
            confidence=0.75
        )
    
    def _create_diversification_strategy(
        self,
        emerging_trends: Dict[str, Any],
        industry: str
    ) -> MarketStrategy:
        """Crea estrategia de diversificación."""
        trends = emerging_trends.get("emerging_trends", [])
        top_trend = trends[0] if trends else None
        
        return MarketStrategy(
            strategy_id=f"diversification_{datetime.utcnow().timestamp()}",
            strategy_name=f"Diversification: {top_trend.get('trend_name', 'New Trend') if top_trend else 'New Markets'}",
            strategy_type="diversification",
            priority="medium",
            expected_impact="Expand into new markets/trends to reduce risk and capture growth",
            implementation_timeframe="6-18 months",
            required_resources={
                "budget": 300000,
                "team_size": 10,
                "technology": "advanced"
            },
            success_metrics=[
                "Revenue from new markets > 15%",
                "Risk diversification achieved",
                "Market presence in 2+ new areas"
            ],
            risk_level="high",
            confidence=0.65
        )

