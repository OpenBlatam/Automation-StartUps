#!/usr/bin/env python3
"""
Campaign Alert System
Sistema de alertas inteligentes para campañas
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum


class AlertSeverity(Enum):
    """Niveles de severidad de alertas"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class CampaignAlertSystem:
    """
    Sistema de alertas inteligentes para campañas
    Detecta problemas y envía alertas automáticas
    """
    
    def __init__(
        self,
        n8n_base_url: str,
        api_key: str,
        email_service_url: Optional[str] = None,
        slack_webhook: Optional[str] = None
    ):
        self.n8n_base_url = n8n_base_url.rstrip('/')
        self.api_key = api_key
        self.email_service_url = email_service_url
        self.slack_webhook = slack_webhook
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def check_campaign_health(
        self,
        campaign_id: str,
        current_metrics: Dict[str, Any],
        targets: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Verifica salud de la campaña y genera alertas
        
        Args:
            campaign_id: ID de la campaña
            current_metrics: Métricas actuales
            targets: Objetivos de la campaña
        
        Returns:
            Lista de alertas generadas
        """
        alerts = []
        
        # Verificar engagement
        engagement_alerts = self._check_engagement(current_metrics, targets)
        alerts.extend(engagement_alerts)
        
        # Verificar conversiones
        conversion_alerts = self._check_conversions(current_metrics, targets)
        alerts.extend(conversion_alerts)
        
        # Verificar alcance
        reach_alerts = self._check_reach(current_metrics, targets)
        alerts.extend(reach_alerts)
        
        # Verificar anomalías
        anomaly_alerts = self._check_anomalies(current_metrics)
        alerts.extend(anomaly_alerts)
        
        # Enviar alertas si hay alguna crítica o alta
        critical_alerts = [a for a in alerts if a["severity"] in [AlertSeverity.CRITICAL.value, AlertSeverity.HIGH.value]]
        if critical_alerts:
            self._send_alerts(campaign_id, critical_alerts)
        
        return alerts
    
    def _check_engagement(
        self,
        metrics: Dict[str, Any],
        targets: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Verifica métricas de engagement"""
        alerts = []
        
        current_rate = metrics.get("engagementRate", 0)
        target_rate = targets.get("engagementRate", 0.05)
        
        if current_rate < target_rate * 0.5:
            alerts.append({
                "type": "low_engagement",
                "severity": AlertSeverity.CRITICAL.value,
                "message": f"Engagement rate crítico: {current_rate:.2%} (objetivo: {target_rate:.2%})",
                "current": current_rate,
                "target": target_rate,
                "recommendation": "Revisar contenido, hashtags y timing inmediatamente"
            })
        elif current_rate < target_rate * 0.7:
            alerts.append({
                "type": "low_engagement",
                "severity": AlertSeverity.HIGH.value,
                "message": f"Engagement rate bajo: {current_rate:.2%} (objetivo: {target_rate:.2%})",
                "current": current_rate,
                "target": target_rate,
                "recommendation": "Considerar optimizar contenido o aumentar alcance"
            })
        
        return alerts
    
    def _check_conversions(
        self,
        metrics: Dict[str, Any],
        targets: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Verifica métricas de conversión"""
        alerts = []
        
        current_rate = metrics.get("conversionRate", 0)
        target_rate = targets.get("conversionRate", 0.10)
        
        if current_rate < target_rate * 0.5:
            alerts.append({
                "type": "low_conversion",
                "severity": AlertSeverity.CRITICAL.value,
                "message": f"Tasa de conversión crítica: {current_rate:.2%} (objetivo: {target_rate:.2%})",
                "current": current_rate,
                "target": target_rate,
                "recommendation": "Revisar oferta, CTA y landing page urgentemente"
            })
        elif current_rate < target_rate * 0.7:
            alerts.append({
                "type": "low_conversion",
                "severity": AlertSeverity.HIGH.value,
                "message": f"Tasa de conversión baja: {current_rate:.2%} (objetivo: {target_rate:.2%})",
                "current": current_rate,
                "target": target_rate,
                "recommendation": "Optimizar oferta o mejorar CTA"
            })
        
        return alerts
    
    def _check_reach(
        self,
        metrics: Dict[str, Any],
        targets: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Verifica métricas de alcance"""
        alerts = []
        
        current_reach = metrics.get("totalReach", 0)
        target_reach = targets.get("totalReach", 5000)
        
        if current_reach < target_reach * 0.5:
            alerts.append({
                "type": "low_reach",
                "severity": AlertSeverity.HIGH.value,
                "message": f"Alcance bajo: {current_reach:,} (objetivo: {target_reach:,})",
                "current": current_reach,
                "target": target_reach,
                "recommendation": "Amplificar en más plataformas o usar hashtags trending"
            })
        
        return alerts
    
    def _check_anomalies(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detecta anomalías en las métricas"""
        alerts = []
        
        # Anomalía: Caída súbita de engagement
        if "engagementHistory" in metrics:
            history = metrics["engagementHistory"]
            if len(history) >= 2:
                recent = history[-1]
                previous = history[-2]
                
                if recent < previous * 0.5:  # Caída del 50%
                    alerts.append({
                        "type": "engagement_drop",
                        "severity": AlertSeverity.HIGH.value,
                        "message": f"Caída súbita de engagement: {previous:.2%} → {recent:.2%}",
                        "recommendation": "Investigar causa inmediatamente"
                    })
        
        # Anomalía: Cero conversiones después de X tiempo
        if metrics.get("totalLeads", 0) == 0 and metrics.get("daysElapsed", 0) >= 1:
            alerts.append({
                "type": "no_conversions",
                "severity": AlertSeverity.CRITICAL.value,
                "message": "No hay conversiones después de 1 día",
                "recommendation": "Revisar todo el funnel de conversión urgentemente"
            })
        
        return alerts
    
    def _send_alerts(
        self,
        campaign_id: str,
        alerts: List[Dict[str, Any]]
    ) -> None:
        """Envía alertas por los canales configurados"""
        # Email
        if self.email_service_url:
            self._send_email_alerts(campaign_id, alerts)
        
        # Slack
        if self.slack_webhook:
            self._send_slack_alerts(campaign_id, alerts)
        
        # Webhook n8n
        self._send_n8n_webhook(campaign_id, alerts)
    
    def _send_email_alerts(
        self,
        campaign_id: str,
        alerts: List[Dict[str, Any]]
    ) -> None:
        """Envía alertas por email"""
        if not self.email_service_url:
            return
        
        subject = f"🚨 Alertas de Campaña {campaign_id}"
        
        body = f"""Se detectaron {len(alerts)} alerta(s) en la campaña {campaign_id}:\n\n"""
        
        for alert in alerts:
            body += f"""
Severidad: {alert['severity'].upper()}
Tipo: {alert['type']}
Mensaje: {alert['message']}
Recomendación: {alert.get('recommendation', 'N/A')}
---
"""
        
        try:
            requests.post(
                f"{self.email_service_url}/send",
                json={
                    "to": os.getenv("ALERT_EMAIL", "alerts@example.com"),
                    "subject": subject,
                    "body": body
                },
                headers=self.headers
            )
        except Exception as e:
            print(f"Error enviando email: {e}")
    
    def _send_slack_alerts(
        self,
        campaign_id: str,
        alerts: List[Dict[str, Any]]
    ) -> None:
        """Envía alertas a Slack"""
        if not self.slack_webhook:
            return
        
        # Determinar color según severidad
        severity_colors = {
            AlertSeverity.CRITICAL.value: "danger",
            AlertSeverity.HIGH.value: "warning",
            AlertSeverity.MEDIUM.value: "#FFA500",
            AlertSeverity.LOW.value: "good",
            AlertSeverity.INFO.value: "#36A2EB"
        }
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 Alertas de Campaña {campaign_id}"
                }
            }
        ]
        
        for alert in alerts:
            color = severity_colors.get(alert["severity"], "#36A2EB")
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{alert['type'].replace('_', ' ').title()}*\n{alert['message']}\n\n*Recomendación:* {alert.get('recommendation', 'N/A')}"
                }
            })
            
            blocks.append({"type": "divider"})
        
        payload = {
            "blocks": blocks
        }
        
        try:
            requests.post(self.slack_webhook, json=payload)
        except Exception as e:
            print(f"Error enviando a Slack: {e}")
    
    def _send_n8n_webhook(
        self,
        campaign_id: str,
        alerts: List[Dict[str, Any]]
    ) -> None:
        """Envía alertas a webhook de n8n"""
        webhook_url = f"{self.n8n_base_url}/webhook/campaign-alerts"
        
        payload = {
            "campaignId": campaign_id,
            "alerts": alerts,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            requests.post(webhook_url, json=payload, headers=self.headers)
        except Exception as e:
            print(f"Error enviando webhook: {e}")


def main():
    """Ejemplo de uso"""
    alert_system = CampaignAlertSystem(
        n8n_base_url="https://your-n8n.com",
        api_key="your_api_key",
        email_service_url="https://email-service.com",
        slack_webhook=os.getenv("SLACK_WEBHOOK")
    )
    
    # Métricas actuales
    current_metrics = {
        "engagementRate": 0.02,  # 2% (bajo)
        "conversionRate": 0.03,  # 3% (bajo)
        "totalReach": 2000,
        "totalLeads": 0,
        "daysElapsed": 1.5
    }
    
    # Objetivos
    targets = {
        "engagementRate": 0.05,  # 5%
        "conversionRate": 0.10,  # 10%
        "totalReach": 5000
    }
    
    # Verificar salud
    alerts = alert_system.check_campaign_health(
        campaign_id="campaign_123",
        current_metrics=current_metrics,
        targets=targets
    )
    
    print(f"Se generaron {len(alerts)} alerta(s):")
    for alert in alerts:
        print(f"\n[{alert['severity'].upper()}] {alert['type']}")
        print(f"  Mensaje: {alert['message']}")
        print(f"  Recomendación: {alert.get('recommendation', 'N/A')}")


if __name__ == "__main__":
    main()



