"""
Sistema de Webhooks para Integración Externa

Permite enviar datos de análisis de mercado a sistemas externos
mediante webhooks configurables.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class MarketWebhookSender:
    """Enviador de webhooks para análisis de mercado."""
    
    def __init__(self):
        """Inicializa el enviador."""
        self.http_client = httpx.Client(timeout=30.0)
        self.logger = logging.getLogger(__name__)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def send_analysis_webhook(
        self,
        webhook_url: str,
        market_analysis: Dict[str, Any],
        insights: List[Dict[str, Any]],
        event_type: str = "market_analysis_complete"
    ) -> bool:
        """
        Envía análisis completo a webhook.
        
        Args:
            webhook_url: URL del webhook
            market_analysis: Análisis de mercado
            insights: Insights generados
            event_type: Tipo de evento
            
        Returns:
            True si se envió exitosamente
        """
        try:
            payload = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "market_analysis": market_analysis,
                    "insights": insights,
                    "summary": {
                        "industry": market_analysis.get("industry", "unknown"),
                        "trends_count": len(market_analysis.get("trends", [])),
                        "insights_count": len(insights),
                        "high_priority_insights": len([i for i in insights if i.get("priority") == "high"])
                    }
                }
            }
            
            response = self.http_client.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            response.raise_for_status()
            
            logger.info(f"Webhook sent successfully to {webhook_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending webhook to {webhook_url}: {e}")
            return False
    
    def send_alert_webhook(
        self,
        webhook_url: str,
        alert: Dict[str, Any]
    ) -> bool:
        """
        Envía alerta a webhook.
        
        Args:
            webhook_url: URL del webhook
            alert: Datos de la alerta
            
        Returns:
            True si se envió exitosamente
        """
        try:
            payload = {
                "event_type": "market_alert",
                "timestamp": datetime.utcnow().isoformat(),
                "alert": alert
            }
            
            response = self.http_client.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            response.raise_for_status()
            
            logger.info(f"Alert webhook sent successfully to {webhook_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending alert webhook: {e}")
            return False
    
    def send_insight_webhook(
        self,
        webhook_url: str,
        insight: Dict[str, Any],
        priority_filter: Optional[str] = None
    ) -> bool:
        """
        Envía insight a webhook.
        
        Args:
            webhook_url: URL del webhook
            insight: Datos del insight
            priority_filter: Filtrar por prioridad (opcional)
            
        Returns:
            True si se envió exitosamente
        """
        if priority_filter and insight.get("priority") != priority_filter:
            return False
        
        try:
            payload = {
                "event_type": "insight_generated",
                "timestamp": datetime.utcnow().isoformat(),
                "insight": insight
            }
            
            response = self.http_client.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            response.raise_for_status()
            
            logger.info(f"Insight webhook sent successfully to {webhook_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending insight webhook: {e}")
            return False






