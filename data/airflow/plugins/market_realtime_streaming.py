"""
Sistema de Análisis de Mercado en Tiempo Real con Streaming

Análisis continuo de mercado usando streaming de datos:
- Procesamiento de streams en tiempo real
- Análisis de eventos de mercado
- Alertas en tiempo real
- Actualización continua de métricas
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from collections import deque
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class RealtimeMarketEvent:
    """Evento de mercado en tiempo real."""
    event_id: str
    event_type: str  # 'price_change', 'volume_spike', 'news_event', 'social_trend'
    metric_name: str
    value: float
    change_percentage: float
    timestamp: datetime
    significance: str  # 'high', 'medium', 'low'
    source: str


class RealtimeMarketStreamer:
    """Streamer de mercado en tiempo real."""
    
    def __init__(
        self,
        postgres_conn_id: Optional[str] = None,
        update_interval_seconds: int = 60
    ):
        """
        Inicializa el streamer.
        
        Args:
            postgres_conn_id: Connection ID para PostgreSQL
            update_interval_seconds: Intervalo de actualización
        """
        self.postgres_conn_id = postgres_conn_id
        self.update_interval = update_interval_seconds
        self.event_buffer: deque = deque(maxlen=1000)
        self.subscribers: List[Callable] = []
        self.logger = logging.getLogger(__name__)
    
    def process_realtime_event(
        self,
        event_data: Dict[str, Any],
        industry: str
    ) -> RealtimeMarketEvent:
        """
        Procesa un evento en tiempo real.
        
        Args:
            event_data: Datos del evento
            industry: Industria
            
        Returns:
            Evento procesado
        """
        logger.info(f"Processing realtime event for {industry}")
        
        event_type = event_data.get("type", "unknown")
        metric_name = event_data.get("metric", "unknown")
        value = event_data.get("value", 0)
        previous_value = event_data.get("previous_value", value)
        
        change_pct = ((value - previous_value) / previous_value * 100) if previous_value != 0 else 0
        
        # Determinar significancia
        if abs(change_pct) > 20:
            significance = "high"
        elif abs(change_pct) > 10:
            significance = "medium"
        else:
            significance = "low"
        
        event = RealtimeMarketEvent(
            event_id=f"realtime_{datetime.utcnow().timestamp()}",
            event_type=event_type,
            metric_name=metric_name,
            value=value,
            change_percentage=change_pct,
            timestamp=datetime.utcnow(),
            significance=significance,
            source=event_data.get("source", "unknown")
        )
        
        # Agregar al buffer
        self.event_buffer.append(event)
        
        # Notificar suscriptores
        for subscriber in self.subscribers:
            try:
                subscriber(event)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")
        
        return event
    
    def get_realtime_summary(
        self,
        lookback_minutes: int = 60
    ) -> Dict[str, Any]:
        """Obtiene resumen de eventos en tiempo real."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=lookback_minutes)
        
        recent_events = [
            e for e in self.event_buffer
            if e.timestamp >= cutoff_time
        ]
        
        high_significance = [e for e in recent_events if e.significance == "high"]
        
        # Agrupar por tipo
        events_by_type = {}
        for event in recent_events:
            if event.event_type not in events_by_type:
                events_by_type[event.event_type] = []
            events_by_type[event.event_type].append(event)
        
        return {
            "total_events": len(recent_events),
            "high_significance_events": len(high_significance),
            "events_by_type": {
                event_type: len(events)
                for event_type, events in events_by_type.items()
            },
            "recent_events": [
                {
                    "type": e.event_type,
                    "metric": e.metric_name,
                    "value": e.value,
                    "change_percentage": e.change_percentage,
                    "significance": e.significance,
                    "timestamp": e.timestamp.isoformat()
                }
                for e in recent_events[-10:]  # Últimos 10
            ]
        }
    
    def subscribe(self, callback: Callable[[RealtimeMarketEvent], None]):
        """Suscribe un callback para recibir eventos."""
        self.subscribers.append(callback)
    
    def get_trending_metrics(
        self,
        lookback_minutes: int = 30
    ) -> List[Dict[str, Any]]:
        """Obtiene métricas trending."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=lookback_minutes)
        
        recent_events = [
            e for e in self.event_buffer
            if e.timestamp >= cutoff_time
        ]
        
        # Agrupar por métrica
        metrics = {}
        for event in recent_events:
            if event.metric_name not in metrics:
                metrics[event.metric_name] = {
                    "events": [],
                    "total_change": 0,
                    "count": 0
                }
            metrics[event.metric_name]["events"].append(event)
            metrics[event.metric_name]["total_change"] += abs(event.change_percentage)
            metrics[event.metric_name]["count"] += 1
        
        # Calcular trending score
        trending = []
        for metric_name, data in metrics.items():
            avg_change = data["total_change"] / data["count"] if data["count"] > 0 else 0
            trending_score = avg_change * data["count"]  # Score = cambio promedio * frecuencia
            
            trending.append({
                "metric_name": metric_name,
                "trending_score": trending_score,
                "average_change": avg_change,
                "event_count": data["count"]
            })
        
        # Ordenar por trending score
        trending.sort(key=lambda x: x["trending_score"], reverse=True)
        
        return trending[:10]  # Top 10






