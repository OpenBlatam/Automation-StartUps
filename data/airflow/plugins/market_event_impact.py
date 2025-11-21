"""
Análisis de Impacto de Eventos en el Mercado

Analiza el impacto de eventos externos en el mercado:
- Eventos económicos
- Eventos políticos
- Eventos tecnológicos
- Eventos de la industria
- Análisis de impacto histórico
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MarketEvent:
    """Evento de mercado."""
    event_id: str
    event_name: str
    event_type: str  # 'economic', 'political', 'technological', 'industry'
    event_date: datetime
    impact_score: float  # 0-1
    impact_duration_days: int
    affected_segments: List[str]
    impact_description: str


class MarketEventImpactAnalyzer:
    """Analizador de impacto de eventos."""
    
    def __init__(self, postgres_conn_id: Optional[str] = None):
        """
        Inicializa el analizador.
        
        Args:
            postgres_conn_id: Connection ID para PostgreSQL
        """
        self.postgres_conn_id = postgres_conn_id
        self.logger = logging.getLogger(__name__)
    
    def analyze_event_impact(
        self,
        industry: str,
        timeframe_days: int = 90
    ) -> Dict[str, Any]:
        """
        Analiza impacto de eventos recientes.
        
        Args:
            industry: Industria
            timeframe_days: Días hacia atrás
            
        Returns:
            Análisis de impacto de eventos
        """
        logger.info(f"Analyzing event impact for {industry}")
        
        # Obtener eventos relevantes
        events = self._get_relevant_events(industry, timeframe_days)
        
        # Analizar impacto de cada evento
        event_impacts = []
        for event in events:
            impact = self._analyze_single_event_impact(event, industry)
            event_impacts.append(impact)
        
        # Análisis agregado
        total_impact = self._calculate_total_impact(event_impacts)
        
        # Eventos más impactantes
        top_events = sorted(
            event_impacts,
            key=lambda x: x.get("impact_score", 0),
            reverse=True
        )[:5]
        
        return {
            "industry": industry,
            "analysis_date": datetime.utcnow().isoformat(),
            "timeframe_days": timeframe_days,
            "total_events": len(events),
            "events_analyzed": event_impacts,
            "top_impactful_events": top_events,
            "total_impact_score": total_impact,
            "impact_summary": self._generate_impact_summary(event_impacts)
        }
    
    def _get_relevant_events(
        self,
        industry: str,
        timeframe_days: int
    ) -> List[MarketEvent]:
        """Obtiene eventos relevantes."""
        # En producción, esto vendría de APIs de noticias, calendarios económicos, etc.
        # Por ahora, simulamos eventos
        
        events = []
        
        # Eventos económicos
        events.append(MarketEvent(
            event_id="economic_1",
            event_name="Interest Rate Change",
            event_type="economic",
            event_date=datetime.utcnow() - timedelta(days=30),
            impact_score=0.7,
            impact_duration_days=60,
            affected_segments=["finance", "real_estate"],
            impact_description="Central bank interest rate adjustment affecting market liquidity"
        ))
        
        # Eventos tecnológicos
        events.append(MarketEvent(
            event_id="tech_1",
            event_name="Major Technology Launch",
            event_type="technological",
            event_date=datetime.utcnow() - timedelta(days=15),
            impact_score=0.8,
            impact_duration_days=90,
            affected_segments=["tech", "innovation"],
            impact_description="Breakthrough technology launch disrupting market"
        ))
        
        # Eventos de industria
        events.append(MarketEvent(
            event_id="industry_1",
            event_name=f"{industry} Industry Regulation",
            event_type="industry",
            event_date=datetime.utcnow() - timedelta(days=45),
            impact_score=0.6,
            impact_duration_days=180,
            affected_segments=[industry],
            impact_description=f"New regulations affecting {industry} industry"
        ))
        
        return events
    
    def _analyze_single_event_impact(
        self,
        event: MarketEvent,
        industry: str
    ) -> Dict[str, Any]:
        """Analiza impacto de un evento individual."""
        # Calcular impacto en métricas de mercado
        impact_on_trends = event.impact_score * 0.8  # Impacto en tendencias
        impact_on_sentiment = event.impact_score * 0.6  # Impacto en sentimiento
        
        # Determinar si el evento afecta a la industria
        industry_affected = industry in event.affected_segments or "all" in event.affected_segments
        
        return {
            "event_id": event.event_id,
            "event_name": event.event_name,
            "event_type": event.event_type,
            "event_date": event.event_date.isoformat(),
            "impact_score": event.impact_score,
            "impact_duration_days": event.impact_duration_days,
            "industry_affected": industry_affected,
            "impact_on_trends": impact_on_trends,
            "impact_on_sentiment": impact_on_sentiment,
            "affected_segments": event.affected_segments,
            "impact_description": event.impact_description,
            "recommendation": self._generate_event_recommendation(event, industry_affected)
        }
    
    def _generate_event_recommendation(
        self,
        event: MarketEvent,
        industry_affected: bool
    ) -> str:
        """Genera recomendación basada en evento."""
        if not industry_affected:
            return "Monitor event but low direct impact expected"
        
        if event.impact_score > 0.7:
            return "High impact event - develop contingency plan and adjust strategy"
        elif event.impact_score > 0.5:
            return "Moderate impact - review and adjust plans as needed"
        else:
            return "Low impact - continue monitoring"
    
    def _calculate_total_impact(
        self,
        event_impacts: List[Dict[str, Any]]
    ) -> float:
        """Calcula impacto total."""
        if not event_impacts:
            return 0.0
        
        # Promedio ponderado por duración
        total_weighted_impact = 0.0
        total_weight = 0.0
        
        for impact in event_impacts:
            weight = impact.get("impact_duration_days", 30)
            total_weighted_impact += impact.get("impact_score", 0) * weight
            total_weight += weight
        
        return total_weighted_impact / total_weight if total_weight > 0 else 0.0
    
    def _generate_impact_summary(
        self,
        event_impacts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Genera resumen de impacto."""
        high_impact = [e for e in event_impacts if e.get("impact_score", 0) > 0.7]
        industry_affected = [e for e in event_impacts if e.get("industry_affected", False)]
        
        return {
            "high_impact_events": len(high_impact),
            "industry_affected_events": len(industry_affected),
            "average_impact": sum(e.get("impact_score", 0) for e in event_impacts) / len(event_impacts) if event_impacts else 0,
            "overall_impact_level": "high" if len(high_impact) > 2 else "medium" if len(high_impact) > 0 else "low"
        }
    
    def predict_future_event_impact(
        self,
        upcoming_events: List[Dict[str, Any]],
        industry: str
    ) -> Dict[str, Any]:
        """
        Predice impacto de eventos futuros.
        
        Args:
            upcoming_events: Lista de eventos futuros
            industry: Industria
            
        Returns:
            Predicción de impacto
        """
        predictions = []
        
        for event in upcoming_events:
            # Estimar impacto basado en tipo de evento
            estimated_impact = self._estimate_event_impact(event, industry)
            predictions.append({
                "event_name": event.get("name", "Unknown"),
                "event_date": event.get("date", ""),
                "estimated_impact_score": estimated_impact,
                "preparation_recommendation": self._generate_preparation_recommendation(estimated_impact)
            })
        
        return {
            "upcoming_events_analyzed": len(upcoming_events),
            "predictions": predictions,
            "highest_impact_event": max(predictions, key=lambda x: x.get("estimated_impact_score", 0)) if predictions else None
        }
    
    def _estimate_event_impact(
        self,
        event: Dict[str, Any],
        industry: str
    ) -> float:
        """Estima impacto de un evento futuro."""
        event_type = event.get("type", "unknown")
        
        # Impacto base por tipo
        base_impact = {
            "economic": 0.6,
            "political": 0.5,
            "technological": 0.7,
            "industry": 0.8
        }.get(event_type, 0.5)
        
        # Ajustar si afecta a la industria
        if industry in event.get("affected_segments", []):
            base_impact *= 1.2
        
        return min(1.0, base_impact)
    
    def _generate_preparation_recommendation(self, impact_score: float) -> str:
        """Genera recomendación de preparación."""
        if impact_score > 0.7:
            return "High impact expected - prepare contingency plans and adjust strategy"
        elif impact_score > 0.5:
            return "Moderate impact expected - review plans and prepare adjustments"
        else:
            return "Low impact expected - monitor event development"






