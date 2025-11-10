"""
Análisis de Riesgo con Escenarios

Análisis avanzado de riesgo usando escenarios:
- Escenarios optimista, base, pesimista
- Análisis de sensibilidad
- Stress testing
- Análisis de Monte Carlo (simplificado)
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import random

logger = logging.getLogger(__name__)


@dataclass
class RiskScenario:
    """Escenario de riesgo."""
    scenario_id: str
    scenario_name: str
    scenario_type: str  # 'optimistic', 'base', 'pessimistic', 'stress'
    probability: float  # 0-1
    impact_score: float  # 0-100
    affected_metrics: List[str]
    description: str
    mitigation_strategies: List[str]


class MarketRiskScenarioAnalyzer:
    """Analizador de riesgo con escenarios."""
    
    def __init__(self):
        """Inicializa el analizador."""
        self.logger = logging.getLogger(__name__)
    
    def analyze_risk_scenarios(
        self,
        market_analysis: Dict[str, Any],
        insights: List[Dict[str, Any]],
        industry: str
    ) -> Dict[str, Any]:
        """
        Analiza escenarios de riesgo.
        
        Args:
            market_analysis: Análisis de mercado
            insights: Insights generados
            industry: Industria
            
        Returns:
            Análisis de escenarios de riesgo
        """
        logger.info(f"Analyzing risk scenarios for {industry}")
        
        scenarios = []
        
        # Escenario base
        base_scenario = self._create_base_scenario(market_analysis, industry)
        scenarios.append(base_scenario)
        
        # Escenario optimista
        optimistic_scenario = self._create_optimistic_scenario(market_analysis, industry)
        scenarios.append(optimistic_scenario)
        
        # Escenario pesimista
        pessimistic_scenario = self._create_pessimistic_scenario(market_analysis, industry)
        scenarios.append(pessimistic_scenario)
        
        # Stress scenarios
        stress_scenarios = self._create_stress_scenarios(market_analysis, industry)
        scenarios.extend(stress_scenarios)
        
        # Análisis de sensibilidad
        sensitivity_analysis = self._perform_sensitivity_analysis(scenarios)
        
        return {
            "industry": industry,
            "analysis_date": datetime.utcnow().isoformat(),
            "total_scenarios": len(scenarios),
            "scenarios": [
                {
                    "scenario_id": s.scenario_id,
                    "scenario_name": s.scenario_name,
                    "scenario_type": s.scenario_type,
                    "probability": s.probability,
                    "impact_score": s.impact_score,
                    "affected_metrics": s.affected_metrics,
                    "description": s.description,
                    "mitigation_strategies": s.mitigation_strategies
                }
                for s in scenarios
            ],
            "sensitivity_analysis": sensitivity_analysis,
            "risk_summary": self._generate_risk_summary(scenarios)
        }
    
    def _create_base_scenario(
        self,
        market_analysis: Dict[str, Any],
        industry: str
    ) -> RiskScenario:
        """Crea escenario base."""
        trends = market_analysis.get("trends", [])
        avg_change = sum(abs(t.get("change_percentage", 0)) for t in trends) / len(trends) if trends else 0
        
        return RiskScenario(
            scenario_id="base_scenario",
            scenario_name="Base Case Scenario",
            scenario_type="base",
            probability=0.5,
            impact_score=50.0,
            affected_metrics=["all"],
            description=f"Base case with average market conditions. Average trend change: {avg_change:.1f}%",
            mitigation_strategies=[
                "Maintain current strategy",
                "Monitor key metrics",
                "Adjust as needed"
            ]
        )
    
    def _create_optimistic_scenario(
        self,
        market_analysis: Dict[str, Any],
        industry: str
    ) -> RiskScenario:
        """Crea escenario optimista."""
        return RiskScenario(
            scenario_id="optimistic_scenario",
            scenario_name="Optimistic Scenario",
            scenario_type="optimistic",
            probability=0.25,
            impact_score=30.0,  # Menor impacto negativo
            affected_metrics=["growth", "opportunities"],
            description="Best-case scenario with strong market growth and favorable conditions",
            mitigation_strategies=[
                "Scale operations to capitalize on growth",
                "Increase investment in high-ROI opportunities",
                "Expand market presence"
            ]
        )
    
    def _create_pessimistic_scenario(
        self,
        market_analysis: Dict[str, Any],
        industry: str
    ) -> RiskScenario:
        """Crea escenario pesimista."""
        risks = market_analysis.get("risk_factors", [])
        
        return RiskScenario(
            scenario_id="pessimistic_scenario",
            scenario_name="Pessimistic Scenario",
            scenario_type="pessimistic",
            probability=0.25,
            impact_score=80.0,  # Alto impacto negativo
            affected_metrics=["revenue", "growth", "market_share"],
            description=f"Worst-case scenario with {len(risks)} risk factors materializing",
            mitigation_strategies=[
                "Reduce exposure to high-risk areas",
                "Diversify revenue streams",
                "Strengthen cash position",
                "Focus on core competencies"
            ]
        )
    
    def _create_stress_scenarios(
        self,
        market_analysis: Dict[str, Any],
        industry: str
    ) -> List[RiskScenario]:
        """Crea escenarios de stress testing."""
        scenarios = []
        
        # Stress scenario 1: Recesión económica
        scenarios.append(RiskScenario(
            scenario_id="stress_recession",
            scenario_name="Economic Recession Stress Test",
            scenario_type="stress",
            probability=0.1,
            impact_score=90.0,
            affected_metrics=["demand", "pricing", "competition"],
            description="Stress test: Economic recession reducing market demand by 30%",
            mitigation_strategies=[
                "Reduce costs and optimize operations",
                "Focus on essential products/services",
                "Strengthen customer relationships",
                "Explore new revenue streams"
            ]
        ))
        
        # Stress scenario 2: Disrupción tecnológica
        scenarios.append(RiskScenario(
            scenario_id="stress_disruption",
            scenario_name="Technology Disruption Stress Test",
            scenario_type="stress",
            probability=0.15,
            impact_score=85.0,
            affected_metrics=["competitive_position", "market_share"],
            description="Stress test: Major technology disruption changing industry dynamics",
            mitigation_strategies=[
                "Accelerate innovation",
                "Invest in new technologies",
                "Adapt business model",
                "Form strategic partnerships"
            ]
        ))
        
        return scenarios
    
    def _perform_sensitivity_analysis(
        self,
        scenarios: List[RiskScenario]
    ) -> Dict[str, Any]:
        """Realiza análisis de sensibilidad."""
        # Calcular impacto esperado
        expected_impact = sum(
            s.impact_score * s.probability
            for s in scenarios
        )
        
        # Identificar métricas más sensibles
        all_metrics = []
        for scenario in scenarios:
            all_metrics.extend(scenario.affected_metrics)
        
        from collections import Counter
        metric_counts = Counter(all_metrics)
        most_sensitive = [metric for metric, count in metric_counts.most_common(5)]
        
        return {
            "expected_impact": expected_impact,
            "impact_range": {
                "min": min(s.impact_score for s in scenarios),
                "max": max(s.impact_score for s in scenarios),
                "average": sum(s.impact_score for s in scenarios) / len(scenarios) if scenarios else 0
            },
            "most_sensitive_metrics": most_sensitive,
            "scenario_probabilities": {
                s.scenario_type: s.probability
                for s in scenarios
            }
        }
    
    def _generate_risk_summary(
        self,
        scenarios: List[RiskScenario]
    ) -> Dict[str, Any]:
        """Genera resumen de riesgo."""
        high_impact = [s for s in scenarios if s.impact_score > 70]
        high_probability = [s for s in scenarios if s.probability > 0.3]
        
        return {
            "high_impact_scenarios": len(high_impact),
            "high_probability_scenarios": len(high_probability),
            "overall_risk_level": "high" if len(high_impact) > 2 else "medium" if len(high_impact) > 0 else "low",
            "recommended_action": "Develop comprehensive risk mitigation plan" if len(high_impact) > 1 else "Monitor risks and maintain current mitigation strategies"
        }






