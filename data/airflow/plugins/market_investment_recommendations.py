"""
Sistema de Recomendaciones de Inversión

Genera recomendaciones de inversión basadas en análisis de mercado:
- Recomendaciones de inversión por oportunidad
- Análisis de riesgo/retorno
- Estrategias de inversión
- Portfolio de inversión recomendado
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class InvestmentRecommendation:
    """Recomendación de inversión."""
    recommendation_id: str
    opportunity_name: str
    investment_type: str  # 'aggressive', 'moderate', 'conservative'
    recommended_amount: float
    expected_return: float
    risk_level: str  # 'low', 'medium', 'high'
    time_horizon: str  # 'short', 'medium', 'long'
    roi_estimate: float
    confidence: float  # 0-1
    rationale: str
    action_items: List[str]


class InvestmentRecommendationEngine:
    """Motor de recomendaciones de inversión."""
    
    def __init__(self):
        """Inicializa el motor."""
        self.logger = logging.getLogger(__name__)
    
    def generate_investment_recommendations(
        self,
        opportunities: List[Dict[str, Any]],
        market_context: Dict[str, Any],
        total_budget: float = 1000000.0
    ) -> Dict[str, Any]:
        """
        Genera recomendaciones de inversión.
        
        Args:
            opportunities: Lista de oportunidades
            market_context: Contexto del mercado
            total_budget: Presupuesto total disponible
            
        Returns:
            Recomendaciones de inversión
        """
        logger.info(f"Generating investment recommendations for {len(opportunities)} opportunities")
        
        recommendations = []
        
        for opp in opportunities:
            # Obtener ROI si está disponible
            roi_data = opp.get("roi_analysis", {})
            roi_pct = roi_data.get("roi_percentage", 0) if roi_data else 0
            
            # Calcular recomendación de inversión
            rec = self._create_investment_recommendation(
                opp,
                roi_pct,
                market_context
            )
            if rec:
                recommendations.append(rec)
        
        # Ordenar por ROI estimado
        recommendations.sort(key=lambda r: r.roi_estimate, reverse=True)
        
        # Crear portfolio recomendado
        portfolio = self._create_recommended_portfolio(
            recommendations,
            total_budget
        )
        
        return {
            "total_opportunities": len(opportunities),
            "recommendations_generated": len(recommendations),
            "recommendations": [
                {
                    "recommendation_id": r.recommendation_id,
                    "opportunity_name": r.opportunity_name,
                    "investment_type": r.investment_type,
                    "recommended_amount": r.recommended_amount,
                    "expected_return": r.expected_return,
                    "risk_level": r.risk_level,
                    "time_horizon": r.time_horizon,
                    "roi_estimate": r.roi_estimate,
                    "confidence": r.confidence,
                    "rationale": r.rationale,
                    "action_items": r.action_items
                }
                for r in recommendations
            ],
            "recommended_portfolio": portfolio,
            "total_recommended_investment": sum(r.recommended_amount for r in recommendations),
            "expected_total_return": sum(r.expected_return for r in recommendations),
            "portfolio_roi": (sum(r.expected_return for r in recommendations) / sum(r.recommended_amount for r in recommendations) * 100) if recommendations else 0
        }
    
    def _create_investment_recommendation(
        self,
        opportunity: Dict[str, Any],
        roi_pct: float,
        market_context: Dict[str, Any]
    ) -> Optional[InvestmentRecommendation]:
        """Crea recomendación de inversión."""
        opp_name = opportunity.get("title", "Unknown Opportunity")
        priority = opportunity.get("priority", "medium")
        confidence = opportunity.get("confidence_score", 0.7)
        
        # Determinar tipo de inversión
        if roi_pct > 50 and confidence > 0.8:
            investment_type = "aggressive"
            risk_level = "medium"
        elif roi_pct > 30:
            investment_type = "moderate"
            risk_level = "medium"
        else:
            investment_type = "conservative"
            risk_level = "low"
        
        # Calcular monto recomendado
        base_amount = 100000.0  # Base
        if priority == "high":
            base_amount *= 1.5
        elif priority == "low":
            base_amount *= 0.7
        
        # Ajustar por ROI
        if roi_pct > 0:
            base_amount *= (1 + roi_pct / 200)  # Aumentar si ROI es alto
        
        recommended_amount = base_amount
        
        # Calcular retorno esperado
        expected_return = recommended_amount * (roi_pct / 100) if roi_pct > 0 else recommended_amount * 0.1
        
        # Determinar horizonte temporal
        timeframe = opportunity.get("timeframe", "3-6 months")
        if "1-3" in timeframe or "short" in timeframe.lower():
            time_horizon = "short"
        elif "6-12" in timeframe or "long" in timeframe.lower():
            time_horizon = "long"
        else:
            time_horizon = "medium"
        
        # Rationale
        rationale = f"Investment recommended based on {roi_pct:.1f}% ROI estimate, {priority} priority, and {confidence:.1%} confidence"
        
        # Action items
        action_items = [
            f"Allocate ${recommended_amount:,.0f} to {opp_name}",
            f"Monitor performance monthly",
            f"Review ROI targets quarterly",
            f"Adjust investment based on market conditions"
        ]
        
        return InvestmentRecommendation(
            recommendation_id=f"inv_{datetime.utcnow().timestamp()}",
            opportunity_name=opp_name,
            investment_type=investment_type,
            recommended_amount=recommended_amount,
            expected_return=expected_return,
            risk_level=risk_level,
            time_horizon=time_horizon,
            roi_estimate=roi_pct,
            confidence=confidence,
            rationale=rationale,
            action_items=action_items
        )
    
    def _create_recommended_portfolio(
        self,
        recommendations: List[InvestmentRecommendation],
        total_budget: float
    ) -> Dict[str, Any]:
        """Crea portfolio recomendado."""
        # Priorizar por ROI
        top_recommendations = recommendations[:5]  # Top 5
        
        # Calcular distribución
        total_recommended = sum(r.recommended_amount for r in top_recommendations)
        
        if total_recommended > total_budget:
            # Escalar proporcionalmente
            scale_factor = total_budget / total_recommended
            portfolio_items = []
            for rec in top_recommendations:
                portfolio_items.append({
                    "opportunity": rec.opportunity_name,
                    "allocated_amount": rec.recommended_amount * scale_factor,
                    "percentage": (rec.recommended_amount * scale_factor / total_budget * 100),
                    "expected_return": rec.expected_return * scale_factor,
                    "roi": rec.roi_estimate
                })
        else:
            portfolio_items = []
            for rec in top_recommendations:
                portfolio_items.append({
                    "opportunity": rec.opportunity_name,
                    "allocated_amount": rec.recommended_amount,
                    "percentage": (rec.recommended_amount / total_budget * 100),
                    "expected_return": rec.expected_return,
                    "roi": rec.roi_estimate
                })
        
        return {
            "total_budget": total_budget,
            "allocated_budget": sum(item["allocated_amount"] for item in portfolio_items),
            "remaining_budget": total_budget - sum(item["allocated_amount"] for item in portfolio_items),
            "portfolio_items": portfolio_items,
            "diversification_score": self._calculate_diversification_score(portfolio_items),
            "expected_portfolio_return": sum(item["expected_return"] for item in portfolio_items),
            "portfolio_roi": (sum(item["expected_return"] for item in portfolio_items) / sum(item["allocated_amount"] for item in portfolio_items) * 100) if portfolio_items else 0
        }
    
    def _calculate_diversification_score(self, portfolio_items: List[Dict[str, Any]]) -> float:
        """Calcula score de diversificación."""
        if len(portfolio_items) < 2:
            return 0.0
        
        # Score basado en número de items y distribución
        num_items_score = min(30, len(portfolio_items) * 6)
        
        # Score de distribución (más uniforme = mejor)
        percentages = [item["percentage"] for item in portfolio_items]
        if percentages:
            avg_pct = sum(percentages) / len(percentages)
            variance = sum((p - avg_pct) ** 2 for p in percentages) / len(percentages)
            distribution_score = max(0, 70 - variance)  # Menor varianza = mejor
        else:
            distribution_score = 0
        
        return min(100.0, num_items_score + distribution_score)






