"""
Análisis de Ciclo de Vida de Tendencias

Identifica en qué etapa del ciclo de vida se encuentra cada tendencia:
- Emergence (Emergencia)
- Growth (Crecimiento)
- Maturity (Madurez)
- Decline (Declive)
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TrendLifecycleStage(Enum):
    """Etapas del ciclo de vida de una tendencia."""
    EMERGENCE = "emergence"
    GROWTH = "growth"
    MATURITY = "maturity"
    DECLINE = "decline"
    UNKNOWN = "unknown"


@dataclass
class TrendLifecycle:
    """Ciclo de vida de una tendencia."""
    trend_name: str
    current_stage: TrendLifecycleStage
    stage_confidence: float  # 0-1
    time_in_stage_days: int
    next_stage_prediction: TrendLifecycleStage
    transition_probability: float  # 0-1
    growth_rate: float
    maturity_indicators: List[str]


class MarketTrendLifecycleAnalyzer:
    """Analizador de ciclo de vida de tendencias."""
    
    def __init__(self, postgres_conn_id: Optional[str] = None):
        """
        Inicializa el analizador.
        
        Args:
            postgres_conn_id: Connection ID para PostgreSQL
        """
        self.postgres_conn_id = postgres_conn_id
        self.logger = logging.getLogger(__name__)
    
    def analyze_trend_lifecycle(
        self,
        trend: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> TrendLifecycle:
        """
        Analiza el ciclo de vida de una tendencia.
        
        Args:
            trend: Datos de la tendencia
            historical_data: Datos históricos (opcional)
            
        Returns:
            Análisis del ciclo de vida
        """
        trend_name = trend.get("trend_name", "unknown")
        change_pct = trend.get("change_percentage", 0)
        direction = trend.get("trend_direction", "stable")
        current_value = trend.get("current_value", 0)
        confidence = trend.get("confidence", 0.5)
        
        # Determinar etapa basado en características
        if abs(change_pct) < 5 and direction == "stable":
            # Tendencia estable = probablemente en madurez
            stage = TrendLifecycleStage.MATURITY
            stage_confidence = 0.7
        elif change_pct > 20 and direction == "up":
            # Crecimiento fuerte = etapa de crecimiento
            stage = TrendLifecycleStage.GROWTH
            stage_confidence = 0.8
        elif change_pct > 5 and change_pct < 20 and direction == "up":
            # Crecimiento moderado = podría ser emergencia o crecimiento temprano
            stage = TrendLifecycleStage.EMERGENCE if current_value < 50 else TrendLifecycleStage.GROWTH
            stage_confidence = 0.6
        elif change_pct < -10 and direction == "down":
            # Declive = etapa de declive
            stage = TrendLifecycleStage.DECLINE
            stage_confidence = 0.75
        else:
            stage = TrendLifecycleStage.UNKNOWN
            stage_confidence = 0.5
        
        # Predecir siguiente etapa
        next_stage = self._predict_next_stage(stage, change_pct, direction)
        
        # Calcular probabilidad de transición
        transition_probability = self._calculate_transition_probability(
            stage,
            next_stage,
            change_pct
        )
        
        # Calcular tasa de crecimiento
        growth_rate = change_pct if direction == "up" else abs(change_pct) if direction == "down" else 0
        
        # Identificar indicadores de madurez
        maturity_indicators = self._identify_maturity_indicators(trend, stage)
        
        return TrendLifecycle(
            trend_name=trend_name,
            current_stage=stage,
            stage_confidence=stage_confidence * confidence,
            time_in_stage_days=30,  # Simulado - en producción usarías datos históricos
            next_stage_prediction=next_stage,
            transition_probability=transition_probability,
            growth_rate=growth_rate,
            maturity_indicators=maturity_indicators
        )
    
    def _predict_next_stage(
        self,
        current_stage: TrendLifecycleStage,
        change_pct: float,
        direction: str
    ) -> TrendLifecycleStage:
        """Predice la siguiente etapa."""
        if current_stage == TrendLifecycleStage.EMERGENCE:
            if change_pct > 15:
                return TrendLifecycleStage.GROWTH
            else:
                return TrendLifecycleStage.EMERGENCE
        
        elif current_stage == TrendLifecycleStage.GROWTH:
            if change_pct < 5:
                return TrendLifecycleStage.MATURITY
            else:
                return TrendLifecycleStage.GROWTH
        
        elif current_stage == TrendLifecycleStage.MATURITY:
            if direction == "down" and change_pct < -5:
                return TrendLifecycleStage.DECLINE
            else:
                return TrendLifecycleStage.MATURITY
        
        elif current_stage == TrendLifecycleStage.DECLINE:
            return TrendLifecycleStage.DECLINE
        
        return TrendLifecycleStage.UNKNOWN
    
    def _calculate_transition_probability(
        self,
        current_stage: TrendLifecycleStage,
        next_stage: TrendLifecycleStage,
        change_pct: float
    ) -> float:
        """Calcula probabilidad de transición."""
        if current_stage == next_stage:
            return 0.3  # Baja probabilidad de cambio si ya está en esa etapa
        
        # Probabilidad basada en magnitud del cambio
        if abs(change_pct) > 20:
            return 0.8  # Alta probabilidad con cambios grandes
        elif abs(change_pct) > 10:
            return 0.6  # Media probabilidad
        else:
            return 0.4  # Baja probabilidad
    
    def _identify_maturity_indicators(
        self,
        trend: Dict[str, Any],
        stage: TrendLifecycleStage
    ) -> List[str]:
        """Identifica indicadores de madurez."""
        indicators = []
        
        if stage == TrendLifecycleStage.MATURITY:
            indicators.append("Stable growth rate")
            indicators.append("Consistent market presence")
            indicators.append("Established market position")
        elif stage == TrendLifecycleStage.GROWTH:
            indicators.append("Rapid growth rate")
            indicators.append("Increasing market adoption")
        elif stage == TrendLifecycleStage.EMERGENCE:
            indicators.append("Early stage development")
            indicators.append("Initial market interest")
        elif stage == TrendLifecycleStage.DECLINE:
            indicators.append("Declining interest")
            indicators.append("Market saturation")
        
        return indicators
    
    def analyze_all_trends_lifecycle(
        self,
        trends: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analiza ciclo de vida de todas las tendencias.
        
        Args:
            trends: Lista de tendencias
            
        Returns:
            Análisis completo
        """
        lifecycle_analyses = []
        
        for trend in trends:
            lifecycle = self.analyze_trend_lifecycle(trend)
            lifecycle_analyses.append({
                "trend_name": lifecycle.trend_name,
                "current_stage": lifecycle.current_stage.value,
                "stage_confidence": lifecycle.stage_confidence,
                "next_stage": lifecycle.next_stage_prediction.value,
                "transition_probability": lifecycle.transition_probability,
                "growth_rate": lifecycle.growth_rate,
                "maturity_indicators": lifecycle.maturity_indicators
            })
        
        # Agrupar por etapa
        stage_distribution = {}
        for analysis in lifecycle_analyses:
            stage = analysis["current_stage"]
            if stage not in stage_distribution:
                stage_distribution[stage] = 0
            stage_distribution[stage] += 1
        
        return {
            "total_trends": len(trends),
            "lifecycle_analyses": lifecycle_analyses,
            "stage_distribution": stage_distribution,
            "dominant_stage": max(stage_distribution.items(), key=lambda x: x[1])[0] if stage_distribution else "unknown"
        }






