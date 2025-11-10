"""
Análisis de Correlaciones entre Tendencias de Mercado

Identifica correlaciones entre diferentes tendencias para:
- Entender relaciones causales
- Predecir tendencias basadas en otras
- Identificar indicadores líderes
- Detectar patrones complejos
"""

from __future__ import annotations

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np

try:
    from scipy.stats import pearsonr, spearmanr
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class TrendCorrelation:
    """Correlación entre dos tendencias."""
    trend1: str
    trend2: str
    correlation_coefficient: float  # -1 a 1
    correlation_type: str  # 'pearson', 'spearman'
    significance: float  # p-value
    relationship_strength: str  # 'strong', 'moderate', 'weak'
    relationship_direction: str  # 'positive', 'negative'


class MarketCorrelationAnalyzer:
    """Analizador de correlaciones entre tendencias."""
    
    def __init__(self):
        """Inicializa el analizador."""
        self.logger = logging.getLogger(__name__)
    
    def analyze_correlations(
        self,
        trends: List[Dict[str, Any]],
        min_correlation: float = 0.5
    ) -> Dict[str, Any]:
        """
        Analiza correlaciones entre tendencias.
        
        Args:
            trends: Lista de tendencias
            min_correlation: Correlación mínima para reportar
            
        Returns:
            Análisis de correlaciones
        """
        logger.info(f"Analyzing correlations between {len(trends)} trends")
        
        if len(trends) < 2:
            return {"correlations_available": False, "reason": "Insufficient trends"}
        
        # Preparar datos para correlación
        trend_data = self._prepare_trend_data(trends)
        
        # Calcular correlaciones
        correlations = []
        for i, trend1 in enumerate(trend_data):
            for trend2 in trend_data[i+1:]:
                correlation = self._calculate_correlation(trend1, trend2)
                if correlation and abs(correlation.correlation_coefficient) >= min_correlation:
                    correlations.append(correlation)
        
        # Identificar indicadores líderes
        leading_indicators = self._identify_leading_indicators(correlations)
        
        # Agrupar por fuerza de correlación
        strong_correlations = [c for c in correlations if c.relationship_strength == "strong"]
        moderate_correlations = [c for c in correlations if c.relationship_strength == "moderate"]
        
        return {
            "correlations_available": True,
            "total_correlations": len(correlations),
            "strong_correlations": len(strong_correlations),
            "moderate_correlations": len(moderate_correlations),
            "correlations": [
                {
                    "trend1": c.trend1,
                    "trend2": c.trend2,
                    "coefficient": c.correlation_coefficient,
                    "type": c.correlation_type,
                    "significance": c.significance,
                    "strength": c.relationship_strength,
                    "direction": c.relationship_direction
                }
                for c in correlations
            ],
            "leading_indicators": leading_indicators
        }
    
    def _prepare_trend_data(
        self,
        trends: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Prepara datos de tendencias para análisis."""
        trend_data = []
        
        for trend in trends:
            # Extraer valores históricos si están disponibles
            # Por ahora usamos valores actuales y cambios
            trend_data.append({
                "name": trend.get("trend_name", "unknown"),
                "current_value": trend.get("current_value", 0),
                "previous_value": trend.get("previous_value", 0),
                "change_percentage": trend.get("change_percentage", 0),
                "category": trend.get("category", "unknown")
            })
        
        return trend_data
    
    def _calculate_correlation(
        self,
        trend1: Dict[str, Any],
        trend2: Dict[str, Any]
    ) -> Optional[TrendCorrelation]:
        """Calcula correlación entre dos tendencias."""
        if not SCIPY_AVAILABLE:
            # Fallback simple
            return self._simple_correlation(trend1, trend2)
        
        try:
            # Para análisis real, necesitarías series temporales
            # Por ahora usamos valores actuales como proxy
            values1 = [
                trend1.get("current_value", 0),
                trend1.get("previous_value", 0),
                trend1.get("change_percentage", 0)
            ]
            values2 = [
                trend2.get("current_value", 0),
                trend2.get("previous_value", 0),
                trend2.get("change_percentage", 0)
            ]
            
            # Calcular correlación de Pearson
            corr, p_value = pearsonr(values1, values2)
            
            # Determinar fuerza
            abs_corr = abs(corr)
            if abs_corr > 0.7:
                strength = "strong"
            elif abs_corr > 0.4:
                strength = "moderate"
            else:
                strength = "weak"
            
            return TrendCorrelation(
                trend1=trend1.get("name", "unknown"),
                trend2=trend2.get("name", "unknown"),
                correlation_coefficient=float(corr),
                correlation_type="pearson",
                significance=float(p_value),
                relationship_strength=strength,
                relationship_direction="positive" if corr > 0 else "negative"
            )
            
        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return None
    
    def _simple_correlation(
        self,
        trend1: Dict[str, Any],
        trend2: Dict[str, Any]
    ) -> Optional[TrendCorrelation]:
        """Correlación simple sin scipy."""
        # Correlación básica basada en dirección de cambio
        change1 = trend1.get("change_percentage", 0)
        change2 = trend2.get("change_percentage", 0)
        
        # Misma dirección = correlación positiva
        if (change1 > 0 and change2 > 0) or (change1 < 0 and change2 < 0):
            corr = 0.6  # Correlación moderada
            direction = "positive"
        elif (change1 > 0 and change2 < 0) or (change1 < 0 and change2 > 0):
            corr = -0.6  # Correlación negativa
            direction = "negative"
        else:
            corr = 0.0
            direction = "neutral"
        
        return TrendCorrelation(
            trend1=trend1.get("name", "unknown"),
            trend2=trend2.get("name", "unknown"),
            correlation_coefficient=corr,
            correlation_type="simple",
            significance=0.05,
            relationship_strength="moderate" if abs(corr) > 0.5 else "weak",
            relationship_direction=direction
        )
    
    def _identify_leading_indicators(
        self,
        correlations: List[TrendCorrelation]
    ) -> List[Dict[str, Any]]:
        """Identifica indicadores líderes."""
        # Un indicador líder es uno que correlaciona fuertemente
        # y típicamente precede a otros en el tiempo
        leading_indicators = []
        
        # Agrupar por trend1 (potencial líder)
        trend_counts = {}
        for corr in correlations:
            if corr.relationship_strength == "strong":
                trend1 = corr.trend1
                if trend1 not in trend_counts:
                    trend_counts[trend1] = 0
                trend_counts[trend1] += 1
        
        # Identificar trends con múltiples correlaciones fuertes
        for trend, count in trend_counts.items():
            if count >= 2:
                leading_indicators.append({
                    "indicator": trend,
                    "correlated_trends_count": count,
                    "type": "leading_indicator",
                    "description": f"{trend} shows strong correlation with {count} other trends"
                })
        
        return leading_indicators
    
    def predict_trend_from_correlation(
        self,
        source_trend: str,
        target_trend: str,
        source_value: float,
        correlations: List[TrendCorrelation]
    ) -> Optional[float]:
        """
        Predice valor de una tendencia basado en correlación con otra.
        
        Args:
            source_trend: Tendencia fuente
            target_trend: Tendencia objetivo
            source_value: Valor actual de tendencia fuente
            correlations: Lista de correlaciones
            
        Returns:
            Valor predicho o None
        """
        # Buscar correlación relevante
        relevant_corr = None
        for corr in correlations:
            if ((corr.trend1 == source_trend and corr.trend2 == target_trend) or
                (corr.trend1 == target_trend and corr.trend2 == source_trend)):
                relevant_corr = corr
                break
        
        if not relevant_corr or relevant_corr.relationship_strength == "weak":
            return None
        
        # Predicción simple basada en correlación
        # En producción usarías modelos más sofisticados
        predicted_change = source_value * relevant_corr.correlation_coefficient
        
        return predicted_change






