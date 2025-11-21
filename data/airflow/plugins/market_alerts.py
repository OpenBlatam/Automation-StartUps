"""
Sistema de Alertas Proactivas para Investigación de Mercado

Sistema de alertas basado en umbrales y reglas para notificar sobre:
- Cambios significativos en tendencias
- Oportunidades de alto valor
- Riesgos emergentes
- Anomalías detectadas
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Severidad de alerta."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class MarketAlert:
    """Alerta de mercado."""
    alert_id: str
    alert_type: str
    severity: AlertSeverity
    title: str
    message: str
    triggered_by: str
    threshold_value: float
    current_value: float
    industry: str
    actionable_recommendation: str
    triggered_at: datetime


class MarketAlertSystem:
    """Sistema de alertas proactivas."""
    
    def __init__(
        self,
        slack_webhook: Optional[str] = None,
        email_config: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa sistema de alertas.
        
        Args:
            slack_webhook: Webhook de Slack
            email_config: Configuración de email
        """
        self.slack_webhook = slack_webhook
        self.email_config = email_config
        self.alert_rules: List[Dict[str, Any]] = []
        self.triggered_alerts: List[MarketAlert] = []
        self.logger = logging.getLogger(__name__)
    
    def add_alert_rule(
        self,
        rule_name: str,
        condition: Callable[[Dict[str, Any]], bool],
        severity: AlertSeverity,
        message_template: str,
        threshold: Optional[float] = None
    ):
        """Agrega regla de alerta."""
        self.alert_rules.append({
            "name": rule_name,
            "condition": condition,
            "severity": severity,
            "message_template": message_template,
            "threshold": threshold
        })
    
    def check_alerts(
        self,
        market_analysis: Dict[str, Any],
        insights: List[Dict[str, Any]],
        predictions: Optional[List[Dict[str, Any]]] = None,
        anomalies: Optional[List[Dict[str, Any]]] = None
    ) -> List[MarketAlert]:
        """
        Verifica y genera alertas.
        
        Args:
            market_analysis: Análisis de mercado
            insights: Insights generados
            predictions: Predicciones ML
            anomalies: Anomalías detectadas
            
        Returns:
            Lista de alertas generadas
        """
        alerts = []
        industry = market_analysis.get("industry", "unknown")
        
        # Alertas predefinidas
        alerts.extend(self._check_trend_alerts(market_analysis, industry))
        alerts.extend(self._check_opportunity_alerts(insights, industry))
        alerts.extend(self._check_risk_alerts(insights, industry))
        alerts.extend(self._check_anomaly_alerts(anomalies or [], industry))
        alerts.extend(self._check_prediction_alerts(predictions or [], industry))
        
        # Alertas personalizadas
        for rule in self.alert_rules:
            try:
                if rule["condition"](market_analysis):
                    alert = MarketAlert(
                        alert_id=f"{rule['name']}_{datetime.utcnow().timestamp()}",
                        alert_type=rule["name"],
                        severity=rule["severity"],
                        title=rule["name"].replace("_", " ").title(),
                        message=rule["message_template"].format(**market_analysis),
                        triggered_by=rule["name"],
                        threshold_value=rule.get("threshold", 0),
                        current_value=0,  # Calcular según regla
                        industry=industry,
                        actionable_recommendation="Review analysis and take appropriate action",
                        triggered_at=datetime.utcnow()
                    )
                    alerts.append(alert)
            except Exception as e:
                self.logger.error(f"Error checking rule {rule['name']}: {e}")
        
        # Guardar alertas
        self.triggered_alerts.extend(alerts)
        
        # Enviar notificaciones
        if alerts:
            self._send_alert_notifications(alerts)
        
        return alerts
    
    def _check_trend_alerts(
        self,
        market_analysis: Dict[str, Any],
        industry: str
    ) -> List[MarketAlert]:
        """Verifica alertas de tendencias."""
        alerts = []
        trends = market_analysis.get("trends", [])
        
        for trend in trends:
            change_pct = abs(trend.get("change_percentage", 0))
            direction = trend.get("trend_direction", "stable")
            
            # Alerta: Cambio muy significativo
            if change_pct > 30:
                alerts.append(MarketAlert(
                    alert_id=f"trend_spike_{datetime.utcnow().timestamp()}",
                    alert_type="trend_spike",
                    severity=AlertSeverity.HIGH,
                    title=f"Significant Trend Change: {trend.get('trend_name', 'Unknown')}",
                    message=f"Trend '{trend.get('trend_name')}' has changed by {change_pct:.1f}%",
                    triggered_by="trend_analysis",
                    threshold_value=30.0,
                    current_value=change_pct,
                    industry=industry,
                    actionable_recommendation=f"Review {trend.get('category', 'trend')} strategy immediately",
                    triggered_at=datetime.utcnow()
                ))
            
            # Alerta: Tendencia alcista fuerte
            if direction == "up" and change_pct > 20:
                alerts.append(MarketAlert(
                    alert_id=f"trend_opportunity_{datetime.utcnow().timestamp()}",
                    alert_type="trend_opportunity",
                    severity=AlertSeverity.MEDIUM,
                    title=f"Strong Upward Trend: {trend.get('trend_name', 'Unknown')}",
                    message=f"Opportunity detected: {trend.get('trend_name')} trending up {change_pct:.1f}%",
                    triggered_by="trend_analysis",
                    threshold_value=20.0,
                    current_value=change_pct,
                    industry=industry,
                    actionable_recommendation="Consider increasing investment in this area",
                    triggered_at=datetime.utcnow()
                ))
        
        return alerts
    
    def _check_opportunity_alerts(
        self,
        insights: List[Dict[str, Any]],
        industry: str
    ) -> List[MarketAlert]:
        """Verifica alertas de oportunidades."""
        alerts = []
        opportunities = [i for i in insights if i.get("category") == "opportunity"]
        
        high_value_opportunities = [
            o for o in opportunities
            if o.get("confidence_score", 0) > 0.8 or o.get("priority") == "high"
        ]
        
        if len(high_value_opportunities) >= 3:
            alerts.append(MarketAlert(
                alert_id=f"multiple_opportunities_{datetime.utcnow().timestamp()}",
                alert_type="multiple_opportunities",
                severity=AlertSeverity.HIGH,
                title="Multiple High-Value Opportunities Detected",
                message=f"{len(high_value_opportunities)} high-value opportunities identified",
                triggered_by="insight_analysis",
                threshold_value=3.0,
                current_value=len(high_value_opportunities),
                industry=industry,
                actionable_recommendation="Prioritize and develop action plans for top opportunities",
                triggered_at=datetime.utcnow()
            ))
        
        return alerts
    
    def _check_risk_alerts(
        self,
        insights: List[Dict[str, Any]],
        industry: str
    ) -> List[MarketAlert]:
        """Verifica alertas de riesgos."""
        alerts = []
        risks = [i for i in insights if i.get("category") == "threat"]
        
        high_risk = [r for r in risks if r.get("priority") == "high"]
        
        if len(high_risk) >= 2:
            alerts.append(MarketAlert(
                alert_id=f"high_risk_{datetime.utcnow().timestamp()}",
                alert_type="high_risk",
                severity=AlertSeverity.CRITICAL,
                title="Multiple High-Risk Factors Detected",
                message=f"{len(high_risk)} high-priority risks identified requiring immediate attention",
                triggered_by="risk_analysis",
                threshold_value=2.0,
                current_value=len(high_risk),
                industry=industry,
                actionable_recommendation="Develop risk mitigation strategies immediately",
                triggered_at=datetime.utcnow()
            ))
        
        return alerts
    
    def _check_anomaly_alerts(
        self,
        anomalies: List[Dict[str, Any]],
        industry: str
    ) -> List[MarketAlert]:
        """Verifica alertas de anomalías."""
        alerts = []
        
        critical_anomalies = [a for a in anomalies if a.get("severity") == "high"]
        
        if critical_anomalies:
            alerts.append(MarketAlert(
                alert_id=f"anomalies_detected_{datetime.utcnow().timestamp()}",
                alert_type="anomalies",
                severity=AlertSeverity.HIGH,
                title="Market Anomalies Detected",
                message=f"{len(critical_anomalies)} critical anomalies detected in market data",
                triggered_by="ml_anomaly_detection",
                threshold_value=1.0,
                current_value=len(critical_anomalies),
                industry=industry,
                actionable_recommendation="Investigate anomalies and verify data quality",
                triggered_at=datetime.utcnow()
            ))
        
        return alerts
    
    def _check_prediction_alerts(
        self,
        predictions: List[Dict[str, Any]],
        industry: str
    ) -> List[MarketAlert]:
        """Verifica alertas de predicciones."""
        alerts = []
        
        strong_predictions = [
            p for p in predictions
            if abs(p.get("change_percentage", 0)) > 20 and p.get("confidence", 0) > 0.8
        ]
        
        if strong_predictions:
            top_prediction = max(strong_predictions, key=lambda x: abs(x.get("change_percentage", 0)))
            alerts.append(MarketAlert(
                alert_id=f"strong_prediction_{datetime.utcnow().timestamp()}",
                alert_type="strong_prediction",
                severity=AlertSeverity.MEDIUM,
                title="Strong Market Prediction",
                message=f"ML model predicts {top_prediction.get('change_percentage', 0):.1f}% change in {top_prediction.get('metric_name', 'market')}",
                triggered_by="ml_prediction",
                threshold_value=20.0,
                current_value=abs(top_prediction.get("change_percentage", 0)),
                industry=industry,
                actionable_recommendation="Prepare strategy for predicted market change",
                triggered_at=datetime.utcnow()
            ))
        
        return alerts
    
    def _send_alert_notifications(self, alerts: List[MarketAlert]):
        """Envía notificaciones de alertas."""
        # Filtrar solo alertas críticas y de alta prioridad
        critical_alerts = [a for a in alerts if a.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]]
        
        if not critical_alerts:
            return
        
        # Enviar a Slack
        if self.slack_webhook:
            try:
                import httpx
                message = "🚨 *Market Research Alerts*\n\n"
                for alert in critical_alerts[:5]:  # Top 5
                    severity_emoji = {
                        AlertSeverity.CRITICAL: "🔴",
                        AlertSeverity.HIGH: "🟠",
                        AlertSeverity.MEDIUM: "🟡",
                        AlertSeverity.LOW: "🟢"
                    }.get(alert.severity, "⚪")
                    
                    message += f"{severity_emoji} *{alert.title}*\n"
                    message += f"{alert.message}\n"
                    message += f"Recommendation: {alert.actionable_recommendation}\n\n"
                
                httpx.post(self.slack_webhook, json={"text": message}, timeout=10)
            except Exception as e:
                self.logger.error(f"Error sending Slack notification: {e}")






