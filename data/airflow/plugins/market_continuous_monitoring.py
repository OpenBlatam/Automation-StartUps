"""
Sistema de Monitoreo Continuo de Mercado

Monitoreo en tiempo real de cambios en el mercado:
- Monitoreo continuo de tendencias
- Detección de cambios significativos
- Alertas en tiempo real
- Tracking de métricas clave
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class MarketChange:
    """Cambio detectado en el mercado."""
    change_id: str
    metric_name: str
    change_type: str  # 'spike', 'drop', 'trend_change', 'anomaly'
    previous_value: float
    current_value: float
    change_percentage: float
    significance: str  # 'high', 'medium', 'low'
    detected_at: datetime
    description: str


class ContinuousMarketMonitor:
    """Monitor continuo de mercado."""
    
    def __init__(
        self,
        postgres_conn_id: Optional[str] = None,
        check_interval_minutes: int = 60
    ):
        """
        Inicializa el monitor.
        
        Args:
            postgres_conn_id: Connection ID para PostgreSQL
            check_interval_minutes: Intervalo de verificación en minutos
        """
        self.postgres_conn_id = postgres_conn_id
        self.check_interval = check_interval_minutes
        self.metric_history: Dict[str, deque] = {}
        self.change_thresholds: Dict[str, float] = {
            "spike": 20.0,  # 20% aumento
            "drop": -15.0,  # 15% disminución
            "trend_change": 10.0
        }
        self.logger = logging.getLogger(__name__)
    
    def monitor_market_changes(
        self,
        current_analysis: Dict[str, Any],
        industry: str
    ) -> List[MarketChange]:
        """
        Monitorea cambios en el mercado.
        
        Args:
            current_analysis: Análisis actual
            industry: Industria
            
        Returns:
            Lista de cambios detectados
        """
        logger.info(f"Monitoring market changes for {industry}")
        
        changes = []
        trends = current_analysis.get("trends", [])
        
        for trend in trends:
            # Obtener valor histórico
            trend_name = trend.get("trend_name", "unknown")
            current_value = trend.get("current_value", 0)
            previous_value = trend.get("previous_value", 0)
            
            # Detectar cambios significativos
            change_pct = ((current_value - previous_value) / previous_value * 100) if previous_value != 0 else 0
            
            if abs(change_pct) > abs(self.change_thresholds.get("spike", 20)):
                change_type = "spike" if change_pct > 0 else "drop"
                significance = "high" if abs(change_pct) > 30 else "medium"
                
                change = MarketChange(
                    change_id=f"change_{datetime.utcnow().timestamp()}",
                    metric_name=trend_name,
                    change_type=change_type,
                    previous_value=previous_value,
                    current_value=current_value,
                    change_percentage=change_pct,
                    significance=significance,
                    detected_at=datetime.utcnow(),
                    description=f"{change_type.capitalize()} detected: {abs(change_pct):.1f}% change in {trend_name}"
                )
                changes.append(change)
        
        return changes
    
    def track_metric(
        self,
        metric_name: str,
        value: float,
        max_history: int = 100
    ):
        """Trackea una métrica."""
        if metric_name not in self.metric_history:
            self.metric_history[metric_name] = deque(maxlen=max_history)
        
        self.metric_history[metric_name].append({
            "value": value,
            "timestamp": datetime.utcnow()
        })
    
    def detect_anomalies_in_metric(
        self,
        metric_name: str,
        threshold_std: float = 2.5
    ) -> Optional[MarketChange]:
        """Detecta anomalías en una métrica."""
        if metric_name not in self.metric_history:
            return None
        
        history = list(self.metric_history[metric_name])
        if len(history) < 10:
            return None
        
        values = [h["value"] for h in history]
        mean = sum(values) / len(values)
        std = (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5
        
        current_value = values[-1]
        z_score = abs((current_value - mean) / (std + 1e-6))
        
        if z_score > threshold_std:
            change_pct = ((current_value - mean) / mean * 100) if mean != 0 else 0
            
            return MarketChange(
                change_id=f"anomaly_{datetime.utcnow().timestamp()}",
                metric_name=metric_name,
                change_type="anomaly",
                previous_value=mean,
                current_value=current_value,
                change_percentage=change_pct,
                significance="high" if z_score > 3 else "medium",
                detected_at=datetime.utcnow(),
                description=f"Anomaly detected: {current_value:.2f} is {z_score:.2f} standard deviations from mean"
            )
        
        return None
    
    def get_metric_trend(
        self,
        metric_name: str,
        lookback_periods: int = 10
    ) -> Optional[Dict[str, Any]]:
        """Obtiene tendencia de una métrica."""
        if metric_name not in self.metric_history:
            return None
        
        history = list(self.metric_history[metric_name])[-lookback_periods:]
        if len(history) < 2:
            return None
        
        values = [h["value"] for h in history]
        
        # Calcular tendencia
        if values[-1] > values[0]:
            trend = "increasing"
            change_pct = ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
        elif values[-1] < values[0]:
            trend = "decreasing"
            change_pct = ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
        else:
            trend = "stable"
            change_pct = 0.0
        
        return {
            "metric_name": metric_name,
            "trend": trend,
            "change_percentage": change_pct,
            "current_value": values[-1],
            "average_value": sum(values) / len(values),
            "volatility": self._calculate_volatility(values)
        }
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calcula volatilidad."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return variance ** 0.5






