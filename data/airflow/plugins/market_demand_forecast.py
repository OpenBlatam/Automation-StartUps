"""
Análisis Predictivo de Demanda de Mercado

Predice demanda futura del mercado usando técnicas de forecasting:
- Predicción de demanda a corto/medio/largo plazo
- Análisis de estacionalidad
- Detección de patrones de demanda
- Escenarios de demanda (optimista, realista, pesimista)
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class DemandForecast:
    """Predicción de demanda."""
    metric_name: str
    current_value: float
    forecast_periods: List[Dict[str, Any]]  # [{period: "1 month", value: 100, confidence: 0.8}, ...]
    trend: str  # 'increasing', 'decreasing', 'stable'
    seasonality_detected: bool
    confidence: float  # 0-1
    scenarios: Dict[str, float]  # {'optimistic': 120, 'realistic': 100, 'pessimistic': 80}


class MarketDemandForecaster:
    """Predictor de demanda de mercado."""
    
    def __init__(self):
        """Inicializa el predictor."""
        self.logger = logging.getLogger(__name__)
    
    def forecast_demand(
        self,
        historical_data: List[Dict[str, Any]],
        forecast_months: int = 6,
        metric_name: str = "market_demand"
    ) -> DemandForecast:
        """
        Predice demanda futura.
        
        Args:
            historical_data: Datos históricos
            forecast_months: Meses a predecir
            metric_name: Nombre de la métrica
            
        Returns:
            Predicción de demanda
        """
        logger.info(f"Forecasting demand for {metric_name} - {forecast_months} months ahead")
        
        if len(historical_data) < 3:
            # Datos insuficientes, usar predicción simple
            return self._simple_forecast(historical_data, forecast_months, metric_name)
        
        # Extraer valores históricos
        values = [d.get("value", 0) for d in historical_data]
        current_value = values[-1] if values else 0
        
        # Calcular tendencia
        trend = self._calculate_trend(values)
        
        # Detectar estacionalidad
        seasonality = self._detect_seasonality(values)
        
        # Generar predicciones por período
        forecast_periods = []
        for month in range(1, forecast_months + 1):
            forecast_value = self._predict_value(values, month, trend)
            confidence = max(0.5, 1.0 - (month * 0.1))  # Menor confianza para períodos más lejanos
            
            forecast_periods.append({
                "period": f"{month} month{'s' if month > 1 else ''}",
                "value": forecast_value,
                "confidence": confidence
            })
        
        # Generar escenarios
        scenarios = self._generate_scenarios(values, forecast_periods[-1]["value"])
        
        return DemandForecast(
            metric_name=metric_name,
            current_value=current_value,
            forecast_periods=forecast_periods,
            trend=trend,
            seasonality_detected=seasonality,
            confidence=0.75,  # Confianza promedio
            scenarios=scenarios
        )
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calcula tendencia de los valores."""
        if len(values) < 2:
            return "stable"
        
        # Calcular pendiente
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _detect_seasonality(self, values: List[float]) -> bool:
        """Detecta estacionalidad en los datos."""
        if len(values) < 12:
            return False
        
        # Análisis simple de variación
        mean = np.mean(values)
        std = np.std(values)
        cv = std / mean if mean > 0 else 0  # Coefficient of variation
        
        # Si hay alta variación, podría haber estacionalidad
        return cv > 0.2
    
    def _predict_value(
        self,
        historical_values: List[float],
        months_ahead: int,
        trend: str
    ) -> float:
        """Predice valor futuro."""
        if not historical_values:
            return 0.0
        
        current = historical_values[-1]
        avg_change = 0.0
        
        if len(historical_values) > 1:
            changes = [
                historical_values[i] - historical_values[i-1]
                for i in range(1, len(historical_values))
            ]
            avg_change = np.mean(changes) if changes else 0.0
        
        # Ajustar por tendencia
        if trend == "increasing":
            multiplier = 1.0 + (months_ahead * 0.05)
        elif trend == "decreasing":
            multiplier = 1.0 - (months_ahead * 0.03)
        else:
            multiplier = 1.0
        
        predicted = current + (avg_change * months_ahead * multiplier)
        
        return max(0.0, predicted)  # No valores negativos
    
    def _generate_scenarios(
        self,
        historical_values: List[float],
        base_forecast: float
    ) -> Dict[str, float]:
        """Genera escenarios de demanda."""
        if historical_values:
            volatility = np.std(historical_values) / np.mean(historical_values) if np.mean(historical_values) > 0 else 0.1
        else:
            volatility = 0.1
        
        return {
            "optimistic": base_forecast * (1 + volatility * 1.5),
            "realistic": base_forecast,
            "pessimistic": base_forecast * (1 - volatility * 1.5)
        }
    
    def _simple_forecast(
        self,
        historical_data: List[Dict[str, Any]],
        forecast_months: int,
        metric_name: str
    ) -> DemandForecast:
        """Predicción simple cuando hay pocos datos."""
        current_value = historical_data[-1].get("value", 0) if historical_data else 0
        
        forecast_periods = []
        for month in range(1, forecast_months + 1):
            # Predicción conservadora: mantener valor actual
            forecast_periods.append({
                "period": f"{month} month{'s' if month > 1 else ''}",
                "value": current_value,
                "confidence": 0.5
            })
        
        return DemandForecast(
            metric_name=metric_name,
            current_value=current_value,
            forecast_periods=forecast_periods,
            trend="stable",
            seasonality_detected=False,
            confidence=0.5,
            scenarios={
                "optimistic": current_value * 1.2,
                "realistic": current_value,
                "pessimistic": current_value * 0.8
            }
        )
    
    def forecast_multiple_metrics(
        self,
        metrics_data: Dict[str, List[Dict[str, Any]]],
        forecast_months: int = 6
    ) -> Dict[str, DemandForecast]:
        """
        Predice demanda para múltiples métricas.
        
        Args:
            metrics_data: Diccionario de {metric_name: historical_data}
            forecast_months: Meses a predecir
            
        Returns:
            Predicciones por métrica
        """
        forecasts = {}
        
        for metric_name, historical_data in metrics_data.items():
            forecast = self.forecast_demand(
                historical_data=historical_data,
                forecast_months=forecast_months,
                metric_name=metric_name
            )
            forecasts[metric_name] = forecast
        
        return forecasts






