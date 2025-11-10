"""
Generador de Reportes Ejecutivos Avanzados

Genera reportes ejecutivos profesionales con:
- Resúmenes ejecutivos
- Visualizaciones ejecutivas
- Análisis de alto nivel
- Recomendaciones estratégicas
- Métricas clave destacadas
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

logger = logging.getLogger(__name__)


class ExecutiveReportGenerator:
    """Generador de reportes ejecutivos."""
    
    def __init__(self):
        """Inicializa el generador."""
        self.logger = logging.getLogger(__name__)
    
    def generate_executive_report(
        self,
        market_analysis: Dict[str, Any],
        insights: List[Dict[str, Any]],
        all_analyses: Dict[str, Any],
        industry: str
    ) -> Dict[str, Any]:
        """
        Genera reporte ejecutivo completo.
        
        Args:
            market_analysis: Análisis de mercado
            insights: Insights generados
            all_analyses: Todos los análisis realizados
            industry: Industria
            
        Returns:
            Reporte ejecutivo completo
        """
        logger.info(f"Generating executive report for {industry}")
        
        # Resumen ejecutivo
        executive_summary = self._generate_executive_summary(
            market_analysis,
            insights,
            all_analyses,
            industry
        )
        
        # Métricas clave
        key_metrics = self._extract_key_metrics(all_analyses)
        
        # Recomendaciones estratégicas
        strategic_recommendations = self._generate_strategic_recommendations(
            insights,
            all_analyses
        )
        
        # Análisis de riesgo
        risk_analysis = self._generate_risk_analysis(
            market_analysis,
            insights,
            all_analyses
        )
        
        # Oportunidades prioritarias
        priority_opportunities = self._identify_priority_opportunities(
            insights,
            all_analyses
        )
        
        return {
            "report_type": "executive",
            "industry": industry,
            "report_date": datetime.utcnow().isoformat(),
            "executive_summary": executive_summary,
            "key_metrics": key_metrics,
            "strategic_recommendations": strategic_recommendations,
            "risk_analysis": risk_analysis,
            "priority_opportunities": priority_opportunities,
            "next_steps": self._generate_next_steps(insights, all_analyses)
        }
    
    def _generate_executive_summary(
        self,
        market_analysis: Dict[str, Any],
        insights: List[Dict[str, Any]],
        all_analyses: Dict[str, Any],
        industry: str
    ) -> Dict[str, Any]:
        """Genera resumen ejecutivo."""
        trends = market_analysis.get("trends", [])
        opportunities = market_analysis.get("opportunities", [])
        risks = market_analysis.get("risk_factors", [])
        
        # Calcular momentum
        upward_trends = len([t for t in trends if t.get("trend_direction") == "up"])
        momentum = "positive" if upward_trends > len(trends) / 2 else "negative" if upward_trends < len(trends) / 3 else "neutral"
        
        # Obtener top insights
        high_priority_insights = [i for i in insights if i.get("priority") == "high"][:3]
        
        return {
            "industry": industry,
            "analysis_period": f"Last {market_analysis.get('timeframe_months', 6)} months",
            "overall_momentum": momentum,
            "key_findings": [
                f"{len(trends)} market trends analyzed",
                f"{len(opportunities)} opportunities identified",
                f"{len(risks)} risk factors detected",
                f"{len(high_priority_insights)} high-priority insights requiring attention"
            ],
            "top_insights": [
                {
                    "title": i.get("title", "N/A"),
                    "impact": i.get("expected_impact", "N/A")
                }
                for i in high_priority_insights
            ],
            "market_outlook": self._generate_market_outlook(market_analysis, all_analyses)
        }
    
    def _extract_key_metrics(self, all_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae métricas clave."""
        metrics = {}
        
        # KPI score
        if "kpi_tracking" in all_analyses and all_analyses["kpi_tracking"].get("kpi_tracking_available"):
            kpis = all_analyses["kpi_tracking"].get("kpis", {})
            metrics["kpi_score"] = kpis.get("overall_score", {}).get("score", 0)
            metrics["kpi_level"] = kpis.get("overall_score", {}).get("level", "unknown")
        
        # ROI
        if "roi_analysis" in all_analyses and all_analyses["roi_analysis"].get("roi_available"):
            roi_report = all_analyses["roi_analysis"].get("roi_report", {})
            metrics["overall_roi"] = roi_report.get("overall_roi_percentage", 0)
            metrics["total_investment_required"] = roi_report.get("total_investment_required", 0)
        
        # Benchmarking
        if "benchmark_result" in all_analyses and all_analyses["benchmark_result"].get("benchmarking_available"):
            benchmark = all_analyses["benchmark_result"].get("benchmark_result", {})
            metrics["benchmark_performance"] = benchmark.get("overall_performance", {}).get("level", "unknown")
        
        # Sentiment
        if "sentiment_nlp" in all_analyses and all_analyses["sentiment_nlp"].get("sentiment_analysis_available"):
            sentiment = all_analyses["sentiment_nlp"].get("sentiment_result", {})
            metrics["overall_sentiment"] = sentiment.get("overall_sentiment", "neutral")
            metrics["sentiment_score"] = sentiment.get("average_sentiment_score", 0)
        
        return metrics
    
    def _generate_strategic_recommendations(
        self,
        insights: List[Dict[str, Any]],
        all_analyses: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Genera recomendaciones estratégicas."""
        recommendations = []
        
        # Recomendación basada en ROI
        if "roi_analysis" in all_analyses:
            roi_report = all_analyses["roi_analysis"].get("roi_report", {})
            top_opp = roi_report.get("top_opportunities", [])
            if top_opp:
                recommendations.append({
                    "type": "investment",
                    "title": "High-ROI Investment Opportunity",
                    "description": f"Top opportunity: {top_opp[0].get('title', 'N/A')} with {top_opp[0].get('roi_analysis', {}).get('roi_percentage', 0):.1f}% ROI",
                    "priority": "high",
                    "action": "Allocate resources to top ROI opportunities"
                })
        
        # Recomendación basada en benchmarking
        if "benchmark_result" in all_analyses:
            benchmark = all_analyses["benchmark_result"].get("benchmark_result", {})
            performance = benchmark.get("overall_performance", {}).get("level", "unknown")
            if performance in ["fair", "poor"]:
                recommendations.append({
                    "type": "performance",
                    "title": "Improve Market Performance",
                    "description": f"Current performance is {performance}. Focus on closing gaps with industry leaders.",
                    "priority": "high",
                    "action": "Develop improvement plan based on benchmark gaps"
                })
        
        # Recomendación basada en segmentación
        if "market_segmentation" in all_analyses:
            segmentation = all_analyses["market_segmentation"].get("segmentation", {})
            segment_analysis = segmentation.get("segment_analysis", {})
            most_attractive = segment_analysis.get("most_attractive_segment", {})
            if most_attractive:
                recommendations.append({
                    "type": "targeting",
                    "title": f"Focus on {most_attractive.get('name', 'Most Attractive Segment')}",
                    "description": f"Most attractive segment identified with score {most_attractive.get('score', 0):.1f}",
                    "priority": "medium",
                    "action": f"Develop targeted strategy for {most_attractive.get('name')} segment"
                })
        
        return recommendations
    
    def _generate_risk_analysis(
        self,
        market_analysis: Dict[str, Any],
        insights: List[Dict[str, Any]],
        all_analyses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera análisis de riesgo."""
        risks = market_analysis.get("risk_factors", [])
        risk_insights = [i for i in insights if i.get("category") == "threat"]
        
        return {
            "total_risks": len(risks),
            "high_priority_risks": len([r for r in risks if r.get("confidence", 0) > 0.8]),
            "risk_categories": self._categorize_risks(risks),
            "mitigation_priorities": self._prioritize_risk_mitigation(risks, risk_insights),
            "overall_risk_level": "high" if len(risks) > 3 else "medium" if len(risks) > 1 else "low"
        }
    
    def _categorize_risks(self, risks: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categoriza riesgos."""
        categories = {}
        for risk in risks:
            category = risk.get("category", "unknown")
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _prioritize_risk_mitigation(
        self,
        risks: List[Dict[str, Any]],
        risk_insights: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Prioriza mitigación de riesgos."""
        priorities = []
        
        for risk in risks[:5]:  # Top 5
            priorities.append({
                "risk": risk.get("title", "Unknown Risk"),
                "priority": "high" if risk.get("confidence", 0) > 0.8 else "medium",
                "mitigation_action": f"Develop mitigation strategy for {risk.get('category', 'risk')}"
            })
        
        return priorities
    
    def _identify_priority_opportunities(
        self,
        insights: List[Dict[str, Any]],
        all_analyses: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identifica oportunidades prioritarias."""
        opportunities = [i for i in insights if i.get("category") == "opportunity"]
        
        # Ordenar por ROI si está disponible
        if "roi_analysis" in all_analyses:
            roi_report = all_analyses["roi_analysis"].get("roi_report", {})
            roi_opportunities = {opp.get("insight_id"): opp for opp in roi_report.get("opportunities", [])}
            
            for opp in opportunities:
                opp_id = opp.get("insight_id")
                if opp_id in roi_opportunities:
                    opp["roi"] = roi_opportunities[opp_id].get("roi_analysis", {})
        
        # Ordenar por prioridad y ROI
        opportunities.sort(
            key=lambda x: (
                {"high": 3, "medium": 2, "low": 1}.get(x.get("priority", "low"), 0),
                x.get("roi", {}).get("roi_percentage", 0) if x.get("roi") else 0
            ),
            reverse=True
        )
        
        return [
            {
                "title": opp.get("title", "N/A"),
                "priority": opp.get("priority", "medium"),
                "roi": opp.get("roi", {}).get("roi_percentage", 0) if opp.get("roi") else None,
                "expected_impact": opp.get("expected_impact", "N/A")
            }
            for opp in opportunities[:5]
        ]
    
    def _generate_market_outlook(
        self,
        market_analysis: Dict[str, Any],
        all_analyses: Dict[str, Any]
    ) -> str:
        """Genera outlook del mercado."""
        trends = market_analysis.get("trends", [])
        upward = len([t for t in trends if t.get("trend_direction") == "up"])
        
        if upward > len(trends) * 0.6:
            return "Positive - Strong upward trends indicate growth opportunities"
        elif upward < len(trends) * 0.4:
            return "Cautious - Mixed trends require careful monitoring"
        else:
            return "Stable - Market showing steady performance"
    
    def _generate_next_steps(
        self,
        insights: List[Dict[str, Any]],
        all_analyses: Dict[str, Any]
    ) -> List[str]:
        """Genera próximos pasos."""
        steps = []
        
        high_priority = [i for i in insights if i.get("priority") == "high"]
        if high_priority:
            steps.append(f"Review and act on {len(high_priority)} high-priority insights")
        
        if "roi_analysis" in all_analyses:
            steps.append("Evaluate top ROI opportunities for investment")
        
        if "benchmark_result" in all_analyses:
            steps.append("Address benchmark gaps to improve market position")
        
        steps.append("Schedule follow-up analysis in 1 month")
        steps.append("Monitor key metrics and trends continuously")
        
        return steps






