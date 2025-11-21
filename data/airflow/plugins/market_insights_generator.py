"""
Generador de Insights Accionables de Mercado

Genera insights accionables basados en análisis de tendencias de mercado.
Incluye:
- Análisis predictivo
- Recomendaciones estratégicas
- Alertas de oportunidades y riesgos
- Planes de acción personalizados
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)


@dataclass
class ActionableInsight:
    """Insight accionable sobre el mercado."""
    insight_id: str
    title: str
    description: str
    category: str  # 'opportunity', 'threat', 'trend', 'recommendation'
    priority: str  # 'high', 'medium', 'low'
    actionable_steps: List[str]
    expected_impact: str
    timeframe: str
    confidence_score: float  # 0-1
    supporting_data: Dict[str, Any]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        return data


class MarketInsightsGenerator:
    """Generador de insights accionables de mercado."""
    
    def __init__(self):
        """Inicializa el generador de insights."""
        self.insights_history: List[ActionableInsight] = []
    
    def generate_insights(
        self,
        market_analysis: Dict[str, Any],
        industry: str,
        business_context: Optional[Dict[str, Any]] = None
    ) -> List[ActionableInsight]:
        """
        Genera insights accionables basados en análisis de mercado.
        
        Args:
            market_analysis: Análisis completo de mercado
            industry: Industria objetivo
            business_context: Contexto del negocio (opcional)
            
        Returns:
            Lista de insights accionables
        """
        logger.info(f"Generating actionable insights for {industry}")
        
        insights = []
        
        # 1. Analizar tendencias principales
        trends = market_analysis.get("trends", [])
        trend_insights = self._analyze_trends_for_insights(trends, industry)
        insights.extend(trend_insights)
        
        # 2. Analizar oportunidades
        opportunities = market_analysis.get("opportunities", [])
        opportunity_insights = self._analyze_opportunities(opportunities, industry)
        insights.extend(opportunity_insights)
        
        # 3. Analizar riesgos
        risks = market_analysis.get("risk_factors", [])
        risk_insights = self._analyze_risks(risks, industry)
        insights.extend(risk_insights)
        
        # 4. Generar recomendaciones estratégicas
        recommendations = self._generate_strategic_recommendations(
            market_analysis,
            industry,
            business_context
        )
        insights.extend(recommendations)
        
        # 5. Generar insights predictivos
        predictive_insights = self._generate_predictive_insights(
            market_analysis,
            industry
        )
        insights.extend(predictive_insights)
        
        # Guardar en historial
        self.insights_history.extend(insights)
        
        return insights
    
    def _analyze_trends_for_insights(
        self,
        trends: List[Dict[str, Any]],
        industry: str
    ) -> List[ActionableInsight]:
        """Analiza tendencias para generar insights."""
        insights = []
        
        # Agrupar por categoría
        trends_by_category = {}
        for trend in trends:
            category = trend.get("category", "unknown")
            if category not in trends_by_category:
                trends_by_category[category] = []
            trends_by_category[category].append(trend)
        
        # Generar insights por categoría
        for category, category_trends in trends_by_category.items():
            if len(category_trends) == 0:
                continue
            
            # Calcular métricas agregadas
            avg_change = sum(
                t.get("change_percentage", 0) for t in category_trends
            ) / len(category_trends)
            
            avg_confidence = sum(
                t.get("confidence", 0) for t in category_trends
            ) / len(category_trends)
            
            # Generar insight si hay cambio significativo
            if abs(avg_change) > 10 and avg_confidence > 0.7:
                direction = "up" if avg_change > 0 else "down"
                priority = "high" if abs(avg_change) > 20 else "medium"
                
                insight = ActionableInsight(
                    insight_id=f"trend_{category}_{datetime.utcnow().timestamp()}",
                    title=f"Tendencia {'Alcista' if direction == 'up' else 'Bajista'} en {category}",
                    description=self._generate_trend_description(category, avg_change, direction),
                    category="trend",
                    priority=priority,
                    actionable_steps=self._generate_trend_actionable_steps(
                        category,
                        direction,
                        avg_change
                    ),
                    expected_impact=self._estimate_impact(abs(avg_change)),
                    timeframe="3-6 meses",
                    confidence_score=avg_confidence,
                    supporting_data={
                        "category": category,
                        "change_percentage": avg_change,
                        "trend_count": len(category_trends)
                    },
                    created_at=datetime.utcnow()
                )
                insights.append(insight)
        
        return insights
    
    def _analyze_opportunities(
        self,
        opportunities: List[Dict[str, Any]],
        industry: str
    ) -> List[ActionableInsight]:
        """Analiza oportunidades para generar insights."""
        insights = []
        
        for opp in opportunities:
            confidence = opp.get("confidence", 0.7)
            if confidence > 0.6:
                insight = ActionableInsight(
                    insight_id=f"opportunity_{datetime.utcnow().timestamp()}",
                    title=opp.get("title", "Oportunidad de Mercado"),
                    description=opp.get("description", ""),
                    category="opportunity",
                    priority="high" if confidence > 0.8 else "medium",
                    actionable_steps=[
                        f"Evaluar viabilidad de {opp.get('category', 'oportunidad')}",
                        "Desarrollar plan de acción específico",
                        "Asignar recursos y timeline",
                        "Establecer métricas de éxito"
                    ],
                    expected_impact="Alto potencial de crecimiento",
                    timeframe="1-3 meses",
                    confidence_score=confidence,
                    supporting_data=opp,
                    created_at=datetime.utcnow()
                )
                insights.append(insight)
        
        return insights
    
    def _analyze_risks(
        self,
        risks: List[Dict[str, Any]],
        industry: str
    ) -> List[ActionableInsight]:
        """Analiza riesgos para generar insights."""
        insights = []
        
        for risk in risks:
            confidence = risk.get("confidence", 0.7)
            if confidence > 0.6:
                insight = ActionableInsight(
                    insight_id=f"risk_{datetime.utcnow().timestamp()}",
                    title=risk.get("title", "Riesgo de Mercado"),
                    description=risk.get("description", ""),
                    category="threat",
                    priority="high" if confidence > 0.8 else "medium",
                    actionable_steps=[
                        f"Desarrollar plan de mitigación para {risk.get('category', 'riesgo')}",
                        "Monitorear indicadores clave",
                        "Preparar respuesta rápida",
                        "Diversificar estrategia"
                    ],
                    expected_impact="Potencial impacto negativo si no se mitiga",
                    timeframe="Inmediato - 1 mes",
                    confidence_score=confidence,
                    supporting_data=risk,
                    created_at=datetime.utcnow()
                )
                insights.append(insight)
        
        return insights
    
    def _generate_strategic_recommendations(
        self,
        market_analysis: Dict[str, Any],
        industry: str,
        business_context: Optional[Dict[str, Any]]
    ) -> List[ActionableInsight]:
        """Genera recomendaciones estratégicas."""
        insights = []
        
        # Analizar patrones generales
        trends = market_analysis.get("trends", [])
        upward_count = sum(1 for t in trends if t.get("trend_direction") == "up")
        downward_count = sum(1 for t in trends if t.get("trend_direction") == "down")
        
        # Recomendación basada en momentum
        if upward_count > downward_count * 1.5:
            insight = ActionableInsight(
                insight_id=f"recommendation_momentum_{datetime.utcnow().timestamp()}",
                title="Momentum Positivo Detectado - Oportunidad de Crecimiento",
                description="Múltiples indicadores muestran tendencia positiva en el mercado",
                category="recommendation",
                priority="high",
                actionable_steps=[
                    "Aumentar inversión en áreas de crecimiento",
                    "Escalar operaciones para capitalizar momentum",
                    "Acelerar lanzamiento de productos/servicios",
                    "Amplificar mensajes de marketing positivos"
                ],
                expected_impact="Alto potencial de crecimiento y market share",
                timeframe="3-6 meses",
                confidence_score=0.75,
                supporting_data={
                    "upward_trends": upward_count,
                    "downward_trends": downward_count
                },
                created_at=datetime.utcnow()
            )
            insights.append(insight)
        
        # Recomendación de diversificación si hay riesgos
        risks = market_analysis.get("risk_factors", [])
        if len(risks) > 2:
            insight = ActionableInsight(
                insight_id=f"recommendation_diversification_{datetime.utcnow().timestamp()}",
                title="Diversificación Estratégica Recomendada",
                description="Múltiples riesgos detectados requieren estrategia diversificada",
                category="recommendation",
                priority="high",
                actionable_steps=[
                    "Diversificar fuentes de ingresos",
                    "Explorar nuevos segmentos de mercado",
                    "Fortalecer fundamentos del negocio",
                    "Desarrollar productos/servicios complementarios"
                ],
                expected_impact="Reducción de riesgo y mayor estabilidad",
                timeframe="6-12 meses",
                confidence_score=0.70,
                supporting_data={"risk_count": len(risks)},
                created_at=datetime.utcnow()
            )
            insights.append(insight)
        
        return insights
    
    def _generate_predictive_insights(
        self,
        market_analysis: Dict[str, Any],
        industry: str
    ) -> List[ActionableInsight]:
        """Genera insights predictivos."""
        insights = []
        
        trends = market_analysis.get("trends", [])
        
        # Predecir tendencias futuras basadas en patrones actuales
        for trend in trends:
            change = trend.get("change_percentage", 0)
            confidence = trend.get("confidence", 0.5)
            
            # Si hay tendencia fuerte y consistente, predecir continuación
            if abs(change) > 15 and confidence > 0.75:
                direction = "up" if change > 0 else "down"
                
                insight = ActionableInsight(
                    insight_id=f"predictive_{datetime.utcnow().timestamp()}",
                    title=f"Predicción: Tendencia {'Alcista' if direction == 'up' else 'Bajista'} Continuará",
                    description=f"Basado en análisis de {trend.get('category', 'tendencia')}, se espera que la tendencia continúe en los próximos 3-6 meses",
                    category="trend",
                    priority="medium",
                    actionable_steps=[
                        f"Prepararse para {'crecimiento' if direction == 'up' else 'ajustes'} en {trend.get('category', 'área')}",
                        "Ajustar estrategia según predicción",
                        "Monitorear indicadores clave semanalmente",
                        "Tener plan de contingencia listo"
                    ],
                    expected_impact=f"Ventaja competitiva al anticipar {'crecimiento' if direction == 'up' else 'ajustes'}",
                    timeframe="3-6 meses",
                    confidence_score=confidence * 0.8,  # Predicciones tienen menor confianza
                    supporting_data=trend,
                    created_at=datetime.utcnow()
                )
                insights.append(insight)
        
        return insights
    
    def _generate_trend_description(
        self,
        category: str,
        change: float,
        direction: str
    ) -> str:
        """Genera descripción de tendencia."""
        descriptions = {
            "search_volume": f"El volumen de búsqueda ha {'aumentado' if direction == 'up' else 'disminuido'} un {abs(change):.1f}%, indicando {'mayor interés' if direction == 'up' else 'menor interés'} del mercado",
            "news_volume": f"La cobertura de noticias ha {'aumentado' if direction == 'up' else 'disminuido'} un {abs(change):.1f}%, reflejando {'mayor visibilidad' if direction == 'up' else 'menor visibilidad'} en medios",
            "sentiment": f"El sentimiento del mercado ha {'mejorado' if direction == 'up' else 'empeorado'} un {abs(change):.1f}%, mostrando {'mayor optimismo' if direction == 'up' else 'mayor pesimismo'}",
            "competition": f"La actividad de competidores ha {'aumentado' if direction == 'up' else 'disminuido'} un {abs(change):.1f}%, indicando {'mayor competencia' if direction == 'up' else 'menor competencia'}"
        }
        
        return descriptions.get(
            category,
            f"Tendencia {'alcista' if direction == 'up' else 'bajista'} del {abs(change):.1f}% en {category}"
        )
    
    def _generate_trend_actionable_steps(
        self,
        category: str,
        direction: str,
        change: float
    ) -> List[str]:
        """Genera pasos accionables para una tendencia."""
        if direction == "up":
            steps_map = {
                "search_volume": [
                    "Aumentar inversión en SEO y contenido relacionado",
                    "Crear campañas de marketing dirigidas a estas búsquedas",
                    "Optimizar landing pages para keywords de tendencia",
                    "Amplificar presencia en canales de búsqueda"
                ],
                "news_volume": [
                    "Aprovechar el momentum mediático con PR estratégico",
                    "Participar activamente en conversaciones de la industria",
                    "Crear contenido que responda a las noticias actuales",
                    "Establecer relaciones con medios relevantes"
                ],
                "sentiment": [
                    "Reforzar mensajes positivos en marketing",
                    "Amplificar testimonios y casos de éxito",
                    "Aumentar presencia en canales con sentimiento positivo",
                    "Capitalizar momentum positivo con lanzamientos"
                ],
                "competition": [
                    "Acelerar diferenciación de producto",
                    "Fortalecer propuesta de valor única",
                    "Aumentar inversión en innovación",
                    "Mejorar velocidad de ejecución"
                ]
            }
        else:
            steps_map = {
                "search_volume": [
                    "Diversificar estrategia de marketing",
                    "Explorar nuevos canales y keywords",
                    "Revisar y optimizar estrategia de contenido",
                    "Identificar nuevas oportunidades de búsqueda"
                ],
                "news_volume": [
                    "Generar contenido propio para mantener visibilidad",
                    "Buscar oportunidades de thought leadership",
                    "Explorar nichos menos saturados",
                    "Crear narrativa propia independiente de noticias"
                ],
                "sentiment": [
                    "Identificar y abordar causas del sentimiento negativo",
                    "Mejorar comunicación y transparencia",
                    "Reforzar relaciones con clientes existentes",
                    "Desarrollar estrategia de recuperación de reputación"
                ],
                "competition": [
                    "Aprovechar menor competencia para ganar market share",
                    "Fortalecer posición en mercado",
                    "Invertir en retención de clientes",
                    "Acelerar mientras competencia se retrae"
                ]
            }
        
        return steps_map.get(category, [
            f"Ajustar estrategia para tendencia {'alcista' if direction == 'up' else 'bajista'}",
            "Monitorear evolución de la tendencia",
            "Preparar respuesta según desarrollo"
        ])
    
    def _estimate_impact(self, change_magnitude: float) -> str:
        """Estima el impacto esperado basado en magnitud del cambio."""
        if change_magnitude > 30:
            return "Impacto muy alto - Cambio significativo en mercado"
        elif change_magnitude > 20:
            return "Impacto alto - Oportunidad/riesgo importante"
        elif change_magnitude > 10:
            return "Impacto medio - Cambio notable que requiere atención"
        else:
            return "Impacto bajo - Cambio menor, monitorear evolución"
    
    def format_insights_report(
        self,
        insights: List[ActionableInsight],
        format: str = "json"
    ) -> str:
        """
        Formatea insights en un reporte.
        
        Args:
            insights: Lista de insights
            format: Formato del reporte ("json", "markdown", "html")
            
        Returns:
            Reporte formateado
        """
        if format == "json":
            return json.dumps(
                [insight.to_dict() for insight in insights],
                indent=2,
                ensure_ascii=False
            )
        
        elif format == "markdown":
            report = "# Insights Accionables de Mercado\n\n"
            report += f"**Fecha de análisis:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            report += f"**Total de insights:** {len(insights)}\n\n"
            
            # Agrupar por prioridad
            by_priority = {"high": [], "medium": [], "low": []}
            for insight in insights:
                by_priority[insight.priority].append(insight)
            
            for priority in ["high", "medium", "low"]:
                if by_priority[priority]:
                    report += f"## Prioridad {priority.upper()}\n\n"
                    for insight in by_priority[priority]:
                        report += f"### {insight.title}\n\n"
                        report += f"**Categoría:** {insight.category}\n\n"
                        report += f"**Descripción:** {insight.description}\n\n"
                        report += f"**Impacto esperado:** {insight.expected_impact}\n\n"
                        report += f"**Timeframe:** {insight.timeframe}\n\n"
                        report += f"**Confianza:** {insight.confidence_score:.1%}\n\n"
                        report += "**Pasos accionables:**\n"
                        for i, step in enumerate(insight.actionable_steps, 1):
                            report += f"{i}. {step}\n"
                        report += "\n---\n\n"
            
            return report
        
        else:
            return str(insights)






