"""
Calculadora de ROI para Oportunidades de Mercado

Calcula ROI potencial de oportunidades identificadas basado en:
- Inversión estimada
- Impacto esperado
- Probabilidad de éxito
- Timeframe
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OpportunityROI:
    """ROI de una oportunidad."""
    opportunity_id: str
    opportunity_title: str
    estimated_investment: float
    expected_return: float
    roi_percentage: float
    payback_period_months: float
    net_present_value: float
    probability_of_success: float
    risk_adjusted_roi: float
    confidence_score: float


class MarketROICalculator:
    """Calculadora de ROI para oportunidades."""
    
    def __init__(self, discount_rate: float = 0.1):
        """
        Inicializa calculadora.
        
        Args:
            discount_rate: Tasa de descuento para NPV (default: 10%)
        """
        self.discount_rate = discount_rate
        self.logger = logging.getLogger(__name__)
    
    def calculate_opportunity_roi(
        self,
        opportunity: Dict[str, Any],
        market_context: Dict[str, Any]
    ) -> OpportunityROI:
        """
        Calcula ROI de una oportunidad.
        
        Args:
            opportunity: Datos de la oportunidad
            market_context: Contexto del mercado
            
        Returns:
            ROI calculado
        """
        # Estimar inversión basado en tipo de oportunidad
        estimated_investment = self._estimate_investment(opportunity, market_context)
        
        # Estimar retorno esperado
        expected_return = self._estimate_return(opportunity, market_context)
        
        # Calcular ROI básico
        roi_percentage = ((expected_return - estimated_investment) / estimated_investment * 100) if estimated_investment > 0 else 0
        
        # Calcular período de recuperación
        monthly_return = expected_return / 12  # Simplificado
        payback_period = estimated_investment / monthly_return if monthly_return > 0 else 999
        
        # Calcular NPV
        npv = self._calculate_npv(estimated_investment, expected_return, 12)
        
        # Probabilidad de éxito
        probability = self._estimate_probability(opportunity, market_context)
        
        # ROI ajustado por riesgo
        risk_adjusted_roi = roi_percentage * probability
        
        # Confidence score
        confidence = opportunity.get("confidence_score", 0.7)
        
        return OpportunityROI(
            opportunity_id=opportunity.get("insight_id", "unknown"),
            opportunity_title=opportunity.get("title", "Unknown Opportunity"),
            estimated_investment=estimated_investment,
            expected_return=expected_return,
            roi_percentage=roi_percentage,
            payback_period_months=payback_period,
            net_present_value=npv,
            probability_of_success=probability,
            risk_adjusted_roi=risk_adjusted_roi,
            confidence_score=confidence
        )
    
    def _estimate_investment(
        self,
        opportunity: Dict[str, Any],
        market_context: Dict[str, Any]
    ) -> float:
        """Estima inversión requerida."""
        category = opportunity.get("category", "unknown")
        priority = opportunity.get("priority", "medium")
        
        # Inversión base por categoría
        base_investment = {
            "opportunity": 50000,
            "trend": 30000,
            "recommendation": 40000
        }.get(category, 35000)
        
        # Ajustar por prioridad
        priority_multiplier = {
            "high": 1.5,
            "medium": 1.0,
            "low": 0.7
        }.get(priority, 1.0)
        
        return base_investment * priority_multiplier
    
    def _estimate_return(
        self,
        opportunity: Dict[str, Any],
        market_context: Dict[str, Any]
    ) -> float:
        """Estima retorno esperado."""
        # Basado en impacto esperado y contexto de mercado
        impact = opportunity.get("expected_impact", "")
        
        # Extraer magnitud de cambio si está disponible
        change_pct = abs(opportunity.get("supporting_data", {}).get("change_percentage", 0))
        
        # Retorno base
        base_return = 100000
        
        # Ajustar por magnitud de cambio
        if change_pct > 20:
            multiplier = 2.0
        elif change_pct > 10:
            multiplier = 1.5
        else:
            multiplier = 1.0
        
        # Ajustar por momentum del mercado
        market_momentum = market_context.get("momentum", 0.5)
        momentum_multiplier = 0.8 + (market_momentum * 0.4)  # 0.8 a 1.2
        
        return base_return * multiplier * momentum_multiplier
    
    def _calculate_npv(
        self,
        investment: float,
        return_amount: float,
        periods: int
    ) -> float:
        """Calcula Net Present Value."""
        # Simplificado: asumir retorno distribuido uniformemente
        period_return = return_amount / periods
        
        npv = -investment
        for i in range(1, periods + 1):
            npv += period_return / ((1 + self.discount_rate) ** i)
        
        return npv
    
    def _estimate_probability(
        self,
        opportunity: Dict[str, Any],
        market_context: Dict[str, Any]
    ) -> float:
        """Estima probabilidad de éxito."""
        # Basado en confidence score y contexto
        base_probability = opportunity.get("confidence_score", 0.7)
        
        # Ajustar por prioridad
        priority = opportunity.get("priority", "medium")
        priority_adjustment = {
            "high": 0.1,
            "medium": 0.0,
            "low": -0.1
        }.get(priority, 0.0)
        
        # Ajustar por momentum
        market_momentum = market_context.get("momentum", 0.5)
        momentum_adjustment = (market_momentum - 0.5) * 0.2
        
        probability = base_probability + priority_adjustment + momentum_adjustment
        
        return max(0.0, min(1.0, probability))
    
    def rank_opportunities_by_roi(
        self,
        opportunities: List[Dict[str, Any]],
        market_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Rankea oportunidades por ROI.
        
        Args:
            opportunities: Lista de oportunidades
            market_context: Contexto del mercado
            
        Returns:
            Oportunidades rankeadas por ROI
        """
        roi_results = []
        
        for opp in opportunities:
            roi = self.calculate_opportunity_roi(opp, market_context)
            roi_results.append({
                **opp,
                "roi_analysis": {
                    "roi_percentage": roi.roi_percentage,
                    "risk_adjusted_roi": roi.risk_adjusted_roi,
                    "payback_period_months": roi.payback_period_months,
                    "npv": roi.net_present_value,
                    "probability_of_success": roi.probability_of_success,
                    "estimated_investment": roi.estimated_investment,
                    "expected_return": roi.expected_return
                }
            })
        
        # Ordenar por ROI ajustado por riesgo
        roi_results.sort(
            key=lambda x: x["roi_analysis"]["risk_adjusted_roi"],
            reverse=True
        )
        
        return roi_results
    
    def generate_roi_report(
        self,
        opportunities: List[Dict[str, Any]],
        market_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera reporte de ROI."""
        ranked = self.rank_opportunities_by_roi(opportunities, market_context)
        
        total_investment = sum(
            o["roi_analysis"]["estimated_investment"]
            for o in ranked
        )
        
        total_expected_return = sum(
            o["roi_analysis"]["expected_return"]
            for o in ranked
        )
        
        total_npv = sum(
            o["roi_analysis"]["npv"]
            for o in ranked
        )
        
        return {
            "total_opportunities": len(ranked),
            "total_investment_required": total_investment,
            "total_expected_return": total_expected_return,
            "total_npv": total_npv,
            "overall_roi_percentage": ((total_expected_return - total_investment) / total_investment * 100) if total_investment > 0 else 0,
            "top_opportunities": ranked[:5],
            "opportunities": ranked
        }






