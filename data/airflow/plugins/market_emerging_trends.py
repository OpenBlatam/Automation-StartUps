"""
Análisis de Tendencias Emergentes

Identifica tendencias emergentes antes de que se vuelvan mainstream:
- Detección temprana de tendencias
- Análisis de señales débiles
- Predicción de tendencias futuras
- Scoring de potencial de tendencias
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EmergingTrend:
    """Tendencia emergente."""
    trend_id: str
    trend_name: str
    emergence_stage: str  # 'early', 'growing', 'accelerating'
    current_volume: float
    growth_rate: float
    potential_score: float  # 0-100
    early_indicators: List[str]
    predicted_mainstream_date: Optional[datetime]
    confidence: float  # 0-1


class EmergingTrendsAnalyzer:
    """Analizador de tendencias emergentes."""
    
    def __init__(self, postgres_conn_id: Optional[str] = None):
        """
        Inicializa el analizador.
        
        Args:
            postgres_conn_id: Connection ID para PostgreSQL
        """
        self.postgres_conn_id = postgres_conn_id
        self.logger = logging.getLogger(__name__)
    
    def identify_emerging_trends(
        self,
        market_data: Dict[str, Any],
        industry: str,
        min_growth_rate: float = 15.0
    ) -> Dict[str, Any]:
        """
        Identifica tendencias emergentes.
        
        Args:
            market_data: Datos de mercado
            industry: Industria
            min_growth_rate: Tasa de crecimiento mínima para considerar emergente
            
        Returns:
            Análisis de tendencias emergentes
        """
        logger.info(f"Identifying emerging trends for {industry}")
        
        # Obtener datos de búsquedas y noticias
        trends_data = market_data.get("market_data", {}).get("sources", {}).get("google_trends", {})
        news_data = market_data.get("market_data", {}).get("sources", {}).get("news", {})
        
        emerging_trends = []
        
        # Analizar keywords de tendencia
        if trends_data.get("data"):
            for trend_data in trends_data["data"][:10]:  # Top 10
                keyword = trend_data.get("keyword", "")
                interest_data = trend_data.get("interest_over_time", [])
                
                if len(interest_data) >= 2:
                    # Calcular tasa de crecimiento
                    recent_values = [d.get("value", 0) for d in interest_data[-6:]]  # Últimas 6 semanas
                    older_values = [d.get("value", 0) for d in interest_data[:6]]  # Primeras 6 semanas
                    
                    recent_avg = sum(recent_values) / len(recent_values) if recent_values else 0
                    older_avg = sum(older_values) / len(older_values) if older_values else 0
                    
                    if older_avg > 0:
                        growth_rate = ((recent_avg - older_avg) / older_avg * 100)
                        
                        if growth_rate >= min_growth_rate:
                            # Es una tendencia emergente
                            trend = self._create_emerging_trend(
                                keyword,
                                recent_avg,
                                growth_rate,
                                industry
                            )
                            emerging_trends.append(trend)
        
        # Analizar noticias para detectar temas emergentes
        news_trends = self._analyze_news_for_emerging_trends(news_data, industry)
        emerging_trends.extend(news_trends)
        
        # Ordenar por potential score
        emerging_trends.sort(key=lambda t: t.potential_score, reverse=True)
        
        return {
            "industry": industry,
            "analysis_date": datetime.utcnow().isoformat(),
            "total_emerging_trends": len(emerging_trends),
            "emerging_trends": [
                {
                    "trend_id": t.trend_id,
                    "trend_name": t.trend_name,
                    "emergence_stage": t.emergence_stage,
                    "current_volume": t.current_volume,
                    "growth_rate": t.growth_rate,
                    "potential_score": t.potential_score,
                    "early_indicators": t.early_indicators,
                    "predicted_mainstream_date": t.predicted_mainstream_date.isoformat() if t.predicted_mainstream_date else None,
                    "confidence": t.confidence
                }
                for t in emerging_trends
            ],
            "top_emerging_trends": [
                {
                    "name": t.trend_name,
                    "potential_score": t.potential_score,
                    "growth_rate": t.growth_rate
                }
                for t in emerging_trends[:5]
            ]
        }
    
    def _create_emerging_trend(
        self,
        keyword: str,
        current_volume: float,
        growth_rate: float,
        industry: str
    ) -> EmergingTrend:
        """Crea objeto de tendencia emergente."""
        # Determinar etapa
        if growth_rate > 50:
            stage = "accelerating"
        elif growth_rate > 25:
            stage = "growing"
        else:
            stage = "early"
        
        # Calcular potential score
        potential_score = self._calculate_potential_score(
            current_volume,
            growth_rate,
            stage
        )
        
        # Predecir fecha de mainstream
        if growth_rate > 20:
            months_to_mainstream = max(1, 12 - (growth_rate / 5))
            predicted_date = datetime.utcnow() + timedelta(days=months_to_mainstream * 30)
        else:
            predicted_date = None
        
        # Early indicators
        indicators = [
            f"Rapid growth rate: {growth_rate:.1f}%",
            f"Stage: {stage}",
            f"Increasing search volume"
        ]
        
        # Confidence basado en datos
        confidence = min(0.95, 0.5 + (growth_rate / 100))
        
        return EmergingTrend(
            trend_id=f"emerging_{keyword.replace(' ', '_')}_{datetime.utcnow().timestamp()}",
            trend_name=keyword,
            emergence_stage=stage,
            current_volume=current_volume,
            growth_rate=growth_rate,
            potential_score=potential_score,
            early_indicators=indicators,
            predicted_mainstream_date=predicted_date,
            confidence=confidence
        )
    
    def _calculate_potential_score(
        self,
        current_volume: float,
        growth_rate: float,
        stage: str
    ) -> float:
        """Calcula score de potencial."""
        score = 0.0
        
        # Factor 1: Volumen actual (0-30 puntos)
        if current_volume > 50:
            score += 30
        elif current_volume > 30:
            score += 20
        elif current_volume > 10:
            score += 10
        
        # Factor 2: Tasa de crecimiento (0-40 puntos)
        if growth_rate > 50:
            score += 40
        elif growth_rate > 30:
            score += 30
        elif growth_rate > 15:
            score += 20
        else:
            score += 10
        
        # Factor 3: Etapa (0-30 puntos)
        stage_scores = {
            "accelerating": 30,
            "growing": 20,
            "early": 10
        }
        score += stage_scores.get(stage, 10)
        
        return min(100.0, score)
    
    def _analyze_news_for_emerging_trends(
        self,
        news_data: Dict[str, Any],
        industry: str
    ) -> List[EmergingTrend]:
        """Analiza noticias para detectar tendencias emergentes."""
        trends = []
        
        articles = news_data.get("articles", [])
        
        # Agrupar por temas (simplificado)
        topics = {}
        for article in articles[:50]:  # Top 50
            title = article.get("title", "")
            # Extraer palabras clave del título
            keywords = title.lower().split()[:3]  # Primeras 3 palabras
            
            for keyword in keywords:
                if len(keyword) > 4:  # Filtrar palabras muy cortas
                    if keyword not in topics:
                        topics[keyword] = 0
                    topics[keyword] += 1
        
        # Identificar temas emergentes (mencionados frecuentemente)
        for topic, count in topics.items():
            if count >= 3:  # Mencionado al menos 3 veces
                trend = EmergingTrend(
                    trend_id=f"news_trend_{topic}_{datetime.utcnow().timestamp()}",
                    trend_name=topic.title(),
                    emergence_stage="early",
                    current_volume=count * 10,
                    growth_rate=count * 5,  # Simulado
                    potential_score=min(70, count * 15),
                    early_indicators=[f"Mentioned {count} times in recent news"],
                    predicted_mainstream_date=datetime.utcnow() + timedelta(days=90),
                    confidence=0.6
                )
                trends.append(trend)
        
        return trends






