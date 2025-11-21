"""
Sistema de Alertas Inteligentes con ML

Sistema avanzado de alertas que usa ML para:
- Detectar patrones anómalos
- Predecir eventos críticos
- Priorizar alertas automáticamente
- Aprender de alertas previas
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

import numpy as np

logger = logging.getLogger(__name__)


class AlertPriority(Enum):
    """Prioridad de alerta."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class IntelligentAlert:
    """Alerta inteligente."""
    alert_id: str
    alert_type: str
    priority: AlertPriority
    title: str
    message: str
    ml_confidence: float  # 0-1
    predicted_impact: str
    recommended_action: str
    similar_past_alerts: int
    triggered_at: datetime
    features: Dict[str, Any]  # Features usados por ML


class IntelligentAlertSystem:
    """Sistema de alertas inteligentes con ML."""
    
    def __init__(self, postgres_conn_id: Optional[str] = None):
        """
        Inicializa el sistema.
        
        Args:
            postgres_conn_id: Connection ID para PostgreSQL
        """
        self.postgres_conn_id = postgres_conn_id
        self.alert_history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
    
    def generate_intelligent_alerts(
        self,
        market_analysis: Dict[str, Any],
        insights: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]],
        anomalies: List[Dict[str, Any]]
    ) -> List[IntelligentAlert]:
        """
        Genera alertas inteligentes usando ML.
        
        Args:
            market_analysis: Análisis de mercado
            insights: Insights generados
            predictions: Predicciones ML
            anomalies: Anomalías detectadas
            
        Returns:
            Lista de alertas inteligentes
        """
        logger.info("Generating intelligent alerts with ML")
        
        alerts = []
        
        # Analizar cada componente
        alerts.extend(self._analyze_trends_for_alerts(market_analysis))
        alerts.extend(self._analyze_insights_for_alerts(insights))
        alerts.extend(self._analyze_predictions_for_alerts(predictions))
        alerts.extend(self._analyze_anomalies_for_alerts(anomalies))
        
        # Aplicar ML para priorización
        prioritized_alerts = self._prioritize_alerts_with_ml(alerts)
        
        # Filtrar alertas redundantes
        filtered_alerts = self._filter_redundant_alerts(prioritized_alerts)
        
        return filtered_alerts
    
    def _analyze_trends_for_alerts(
        self,
        market_analysis: Dict[str, Any]
    ) -> List[IntelligentAlert]:
        """Analiza tendencias para generar alertas."""
        alerts = []
        trends = market_analysis.get("trends", [])
        
        for trend in trends:
            change_pct = abs(trend.get("change_percentage", 0))
            direction = trend.get("trend_direction", "stable")
            
            # Alerta: Cambio extremo
            if change_pct > 40:
                alert = IntelligentAlert(
                    alert_id=f"trend_extreme_{datetime.utcnow().timestamp()}",
                    alert_type="extreme_trend_change",
                    priority=AlertPriority.CRITICAL,
                    title=f"Extreme Trend Change: {trend.get('trend_name', 'Unknown')}",
                    message=f"Trend '{trend.get('trend_name')}' has changed by {change_pct:.1f}% - requires immediate attention",
                    ml_confidence=0.9,
                    predicted_impact="High impact on market strategy",
                    recommended_action="Review and adjust strategy immediately",
                    similar_past_alerts=self._count_similar_alerts("extreme_trend_change"),
                    triggered_at=datetime.utcnow(),
                    features={
                        "change_percentage": change_pct,
                        "direction": direction,
                        "category": trend.get("category")
                    }
                )
                alerts.append(alert)
        
        return alerts
    
    def _analyze_insights_for_alerts(
        self,
        insights: List[Dict[str, Any]]
    ) -> List[IntelligentAlert]:
        """Analiza insights para generar alertas."""
        alerts = []
        
        # Múltiples insights de alta prioridad
        high_priority = [i for i in insights if i.get("priority") == "high"]
        if len(high_priority) >= 5:
            alert = IntelligentAlert(
                alert_id=f"multiple_high_priority_{datetime.utcnow().timestamp()}",
                alert_type="multiple_high_priority_insights",
                priority=AlertPriority.HIGH,
                title="Multiple High-Priority Insights Detected",
                message=f"{len(high_priority)} high-priority insights require immediate attention",
                ml_confidence=0.85,
                predicted_impact="Significant strategic decisions needed",
                recommended_action="Prioritize and develop action plans for top insights",
                similar_past_alerts=self._count_similar_alerts("multiple_high_priority_insights"),
                triggered_at=datetime.utcnow(),
                features={
                    "high_priority_count": len(high_priority),
                    "total_insights": len(insights)
                }
            )
            alerts.append(alert)
        
        return alerts
    
    def _analyze_predictions_for_alerts(
        self,
        predictions: List[Dict[str, Any]]
    ) -> List[IntelligentAlert]:
        """Analiza predicciones para generar alertas."""
        alerts = []
        
        # Predicciones con alta confianza y cambio significativo
        strong_predictions = [
            p for p in predictions
            if p.get("confidence", 0) > 0.8 and abs(p.get("change_percentage", 0)) > 25
        ]
        
        if strong_predictions:
            top_prediction = max(strong_predictions, key=lambda x: abs(x.get("change_percentage", 0)))
            
            alert = IntelligentAlert(
                alert_id=f"strong_prediction_{datetime.utcnow().timestamp()}",
                alert_type="strong_ml_prediction",
                priority=AlertPriority.HIGH,
                title=f"Strong ML Prediction: {top_prediction.get('metric_name', 'Market')}",
                message=f"ML model predicts {top_prediction.get('change_percentage', 0):.1f}% change with {top_prediction.get('confidence', 0):.1%} confidence",
                ml_confidence=top_prediction.get("confidence", 0.8),
                predicted_impact="Prepare for significant market change",
                recommended_action="Develop contingency plans and adjust strategy",
                similar_past_alerts=self._count_similar_alerts("strong_ml_prediction"),
                triggered_at=datetime.utcnow(),
                features={
                    "predicted_change": top_prediction.get("change_percentage", 0),
                    "confidence": top_prediction.get("confidence", 0),
                    "metric": top_prediction.get("metric_name", "unknown")
                }
            )
            alerts.append(alert)
        
        return alerts
    
    def _analyze_anomalies_for_alerts(
        self,
        anomalies: List[Dict[str, Any]]
    ) -> List[IntelligentAlert]:
        """Analiza anomalías para generar alertas."""
        alerts = []
        
        critical_anomalies = [a for a in anomalies if a.get("severity") == "high"]
        
        if critical_anomalies:
            alert = IntelligentAlert(
                alert_id=f"critical_anomalies_{datetime.utcnow().timestamp()}",
                alert_type="critical_anomalies",
                priority=AlertPriority.CRITICAL,
                title="Critical Market Anomalies Detected",
                message=f"{len(critical_anomalies)} critical anomalies detected requiring investigation",
                ml_confidence=0.9,
                predicted_impact="Potential data quality issues or market disruptions",
                recommended_action="Investigate anomalies and verify data sources",
                similar_past_alerts=self._count_similar_alerts("critical_anomalies"),
                triggered_at=datetime.utcnow(),
                features={
                    "anomaly_count": len(critical_anomalies),
                    "severity": "high"
                }
            )
            alerts.append(alert)
        
        return alerts
    
    def _prioritize_alerts_with_ml(
        self,
        alerts: List[IntelligentAlert]
    ) -> List[IntelligentAlert]:
        """Prioriza alertas usando ML."""
        # Calcular score ML para cada alerta
        for alert in alerts:
            ml_score = self._calculate_ml_priority_score(alert)
            
            # Ajustar prioridad basado en score ML
            if ml_score > 0.8:
                alert.priority = AlertPriority.CRITICAL
            elif ml_score > 0.6:
                alert.priority = AlertPriority.HIGH
            elif ml_score > 0.4:
                alert.priority = AlertPriority.MEDIUM
            else:
                alert.priority = AlertPriority.LOW
        
        # Ordenar por prioridad y score ML
        alerts.sort(
            key=lambda a: (
                {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(a.priority.value, 0),
                a.ml_confidence
            ),
            reverse=True
        )
        
        return alerts
    
    def _calculate_ml_priority_score(self, alert: IntelligentAlert) -> float:
        """Calcula score de prioridad usando ML."""
        score = alert.ml_confidence
        
        # Ajustar por tipo de alerta
        type_weights = {
            "extreme_trend_change": 1.2,
            "critical_anomalies": 1.3,
            "strong_ml_prediction": 1.1,
            "multiple_high_priority_insights": 1.0
        }
        
        weight = type_weights.get(alert.alert_type, 1.0)
        score *= weight
        
        # Ajustar por alertas similares pasadas
        if alert.similar_past_alerts > 0:
            score *= 1.1  # Aumentar si hay precedentes
        
        return min(1.0, score)
    
    def _filter_redundant_alerts(
        self,
        alerts: List[IntelligentAlert]
    ) -> List[IntelligentAlert]:
        """Filtra alertas redundantes."""
        # Agrupar por tipo
        alerts_by_type = {}
        for alert in alerts:
            if alert.alert_type not in alerts_by_type:
                alerts_by_type[alert.alert_type] = []
            alerts_by_type[alert.alert_type].append(alert)
        
        # Mantener solo la alerta de mayor prioridad por tipo
        filtered = []
        for alert_type, type_alerts in alerts_by_type.items():
            # Ordenar por prioridad y confianza
            type_alerts.sort(
                key=lambda a: (
                    {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(a.priority.value, 0),
                    a.ml_confidence
                ),
                reverse=True
            )
            filtered.append(type_alerts[0])  # Solo la mejor
        
        return filtered
    
    def _count_similar_alerts(self, alert_type: str) -> int:
        """Cuenta alertas similares del pasado."""
        # En producción, consultarías la base de datos
        # Por ahora, simulado
        return len([a for a in self.alert_history if a.get("type") == alert_type])






