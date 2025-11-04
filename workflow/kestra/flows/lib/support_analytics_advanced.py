"""
Sistema de Analytics Avanzado para Soporte.

Proporciona análisis detallados, predicciones, y visualizaciones.
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


@dataclass
class TrendData:
    """Datos de tendencia."""
    period: str
    value: float
    change_percentage: Optional[float] = None
    trend: Optional[str] = None  # "up", "down", "stable"


@dataclass
class CorrelationData:
    """Datos de correlación."""
    metric1: str
    metric2: str
    correlation: float  # -1.0 a 1.0
    strength: str  # "strong", "moderate", "weak"


@dataclass
class SegmentData:
    """Datos de segmentación."""
    segment: str
    count: int
    percentage: float
    avg_value: Optional[float] = None


class SupportAnalyticsEngine:
    """Motor de analytics avanzado."""
    
    def __init__(self, db_connection):
        """
        Inicializa motor de analytics.
        
        Args:
            db_connection: Conexión a base de datos
        """
        self.db = db_connection
    
    def calculate_trends(
        self,
        metric: str,
        days: int = 30,
        period: str = "day"
    ) -> List[TrendData]:
        """
        Calcula tendencias de una métrica.
        
        Args:
            metric: Métrica a analizar
            days: Días a analizar
            period: "day", "week", "month"
            
        Returns:
            Lista de datos de tendencia
        """
        # Implementación básica - en producción usar queries SQL optimizadas
        trends = []
        
        # Query para obtener datos históricos
        query = self._get_metric_query(metric, days, period)
        
        try:
            with self.db.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
                
                previous_value = None
                for row in rows:
                    period_name = row[0]
                    value = float(row[1])
                    
                    change_pct = None
                    trend = None
                    if previous_value is not None:
                        change_pct = ((value - previous_value) / previous_value) * 100
                        if abs(change_pct) < 2:
                            trend = "stable"
                        elif change_pct > 0:
                            trend = "up"
                        else:
                            trend = "down"
                    
                    trends.append(TrendData(
                        period=period_name,
                        value=value,
                        change_percentage=change_pct,
                        trend=trend
                    ))
                    
                    previous_value = value
        except Exception as e:
            logger.error(f"Error calculating trends: {e}")
        
        return trends
    
    def _get_metric_query(self, metric: str, days: int, period: str) -> str:
        """Genera query SQL para métrica."""
        period_format = {
            "day": "DATE(created_at)",
            "week": "DATE_TRUNC('week', created_at)",
            "month": "DATE_TRUNC('month', created_at)"
        }
        
        period_str = period_format.get(period, "DATE(created_at)")
        
        metric_queries = {
            "ticket_volume": f"""
                SELECT 
                    {period_str}::text as period,
                    COUNT(*) as value
                FROM support_tickets
                WHERE created_at >= NOW() - INTERVAL '{days} days'
                GROUP BY {period_str}
                ORDER BY period
            """,
            "resolution_time": f"""
                SELECT 
                    {period_str}::text as period,
                    AVG(time_to_resolution_minutes) as value
                FROM support_tickets
                WHERE status = 'resolved'
                AND created_at >= NOW() - INTERVAL '{days} days'
                GROUP BY {period_str}
                ORDER BY period
            """,
            "chatbot_resolution_rate": f"""
                SELECT 
                    {period_str}::text as period,
                    (COUNT(*) FILTER (WHERE chatbot_resolved = true)::float / 
                     NULLIF(COUNT(*), 0)) * 100 as value
                FROM support_tickets
                WHERE created_at >= NOW() - INTERVAL '{days} days'
                GROUP BY {period_str}
                ORDER BY period
            """,
            "customer_satisfaction": f"""
                SELECT 
                    {period_str}::text as period,
                    AVG(satisfaction_score) as value
                FROM support_ticket_feedback
                WHERE submitted_at >= NOW() - INTERVAL '{days} days'
                GROUP BY {period_str}
                ORDER BY period
            """
        }
        
        return metric_queries.get(metric, metric_queries["ticket_volume"])
    
    def calculate_correlations(
        self,
        metrics: List[str],
        days: int = 30
    ) -> List[CorrelationData]:
        """
        Calcula correlaciones entre métricas.
        
        Args:
            metrics: Lista de métricas
            days: Días a analizar
            
        Returns:
            Lista de correlaciones
        """
        correlations = []
        
        # Obtener datos para todas las métricas
        metric_data = {}
        for metric in metrics:
            trends = self.calculate_trends(metric, days)
            metric_data[metric] = [t.value for t in trends]
        
        # Calcular correlaciones entre pares
        for i, metric1 in enumerate(metrics):
            for metric2 in metrics[i+1:]:
                if metric1 in metric_data and metric2 in metric_data:
                    corr = self._calculate_correlation(
                        metric_data[metric1],
                        metric_data[metric2]
                    )
                    
                    strength = "strong" if abs(corr) > 0.7 else \
                               "moderate" if abs(corr) > 0.4 else "weak"
                    
                    correlations.append(CorrelationData(
                        metric1=metric1,
                        metric2=metric2,
                        correlation=corr,
                        strength=strength
                    ))
        
        return correlations
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calcula correlación de Pearson."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        try:
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(xi * xi for xi in x)
            sum_y2 = sum(yi * yi for yi in y)
            
            numerator = n * sum_xy - sum_x * sum_y
            denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5
            
            if denominator == 0:
                return 0.0
            
            return numerator / denominator
        except Exception:
            return 0.0
    
    def segment_tickets(
        self,
        dimension: str,
        metric: str = "count",
        days: int = 30
    ) -> List[SegmentData]:
        """
        Segmenta tickets por dimensión.
        
        Args:
            dimension: "priority", "category", "status", "department"
            metric: "count", "avg_resolution_time", "satisfaction"
            days: Días a analizar
            
        Returns:
            Lista de segmentos
        """
        segments = []
        
        query = self._get_segmentation_query(dimension, metric, days)
        
        try:
            with self.db.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
                
                total = sum(float(row[1]) for row in rows)
                
                for row in rows:
                    segment = row[0]
                    value = float(row[1])
                    percentage = (value / total * 100) if total > 0 else 0.0
                    
                    avg_value = float(row[2]) if len(row) > 2 and row[2] else None
                    
                    segments.append(SegmentData(
                        segment=segment,
                        count=int(value) if metric == "count" else 0,
                        percentage=percentage,
                        avg_value=avg_value
                    ))
        except Exception as e:
            logger.error(f"Error segmenting tickets: {e}")
        
        return segments
    
    def _get_segmentation_query(
        self,
        dimension: str,
        metric: str,
        days: int
    ) -> str:
        """Genera query de segmentación."""
        dimension_field = {
            "priority": "priority",
            "category": "category",
            "status": "status",
            "department": "assigned_department"
        }.get(dimension, "priority")
        
        if metric == "count":
            return f"""
                SELECT 
                    {dimension_field} as segment,
                    COUNT(*) as value,
                    NULL as avg_value
                FROM support_tickets
                WHERE created_at >= NOW() - INTERVAL '{days} days'
                GROUP BY {dimension_field}
                ORDER BY value DESC
            """
        elif metric == "avg_resolution_time":
            return f"""
                SELECT 
                    {dimension_field} as segment,
                    COUNT(*) as value,
                    AVG(time_to_resolution_minutes) as avg_value
                FROM support_tickets
                WHERE created_at >= NOW() - INTERVAL '{days} days'
                AND status = 'resolved'
                GROUP BY {dimension_field}
                ORDER BY value DESC
            """
        elif metric == "satisfaction":
            return f"""
                SELECT 
                    t.{dimension_field} as segment,
                    COUNT(*) as value,
                    AVG(f.satisfaction_score) as avg_value
                FROM support_tickets t
                JOIN support_ticket_feedback f ON t.ticket_id = f.ticket_id
                WHERE t.created_at >= NOW() - INTERVAL '{days} days'
                GROUP BY t.{dimension_field}
                ORDER BY value DESC
            """
        else:
            return f"SELECT {dimension_field}, COUNT(*) FROM support_tickets GROUP BY {dimension_field}"
    
    def generate_insights(self, days: int = 30) -> Dict[str, Any]:
        """
        Genera insights automáticos.
        
        Args:
            days: Días a analizar
            
        Returns:
            Diccionario con insights
        """
        insights = {
            "timestamp": datetime.now().isoformat(),
            "period_days": days,
            "insights": [],
            "recommendations": []
        }
        
        # Análisis de volumen
        volume_trend = self.calculate_trends("ticket_volume", days)
        if volume_trend:
            latest = volume_trend[-1]
            if latest.trend == "up" and latest.change_percentage and latest.change_percentage > 20:
                insights["insights"].append({
                    "type": "volume_increase",
                    "message": f"Volumen de tickets aumentó {latest.change_percentage:.1f}%",
                    "severity": "warning"
                })
        
        # Análisis de tiempo de resolución
        resolution_trend = self.calculate_trends("resolution_time", days)
        if resolution_trend:
            latest = resolution_trend[-1]
            if latest.trend == "up" and latest.change_percentage and latest.change_percentage > 15:
                insights["recommendations"].append({
                    "type": "optimize_resolution",
                    "message": "Tiempo de resolución está aumentando. Considerar optimizar procesos.",
                    "priority": "high"
                })
        
        # Análisis de satisfacción
        satisfaction_trend = self.calculate_trends("customer_satisfaction", days)
        if satisfaction_trend:
            latest = satisfaction_trend[-1]
            if latest.value and latest.value < 3.0:
                insights["insights"].append({
                    "type": "low_satisfaction",
                    "message": f"Satisfacción del cliente baja: {latest.value:.2f}/5.0",
                    "severity": "critical"
                })
        
        # Correlaciones
        correlations = self.calculate_correlations(
            ["ticket_volume", "resolution_time", "customer_satisfaction"],
            days
        )
        for corr in correlations:
            if abs(corr.correlation) > 0.7:
                insights["insights"].append({
                    "type": "strong_correlation",
                    "message": f"Correlación fuerte entre {corr.metric1} y {corr.metric2} ({corr.correlation:.2f})",
                    "severity": "info"
                })
        
        return insights

