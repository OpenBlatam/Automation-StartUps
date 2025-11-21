"""
Sistema de Forecasting y Análisis de Tendencias.

Características:
- Predicción de volumen de tickets
- Análisis de tendencias estacionales
- Forecasting de carga de trabajo
- Detección de patrones
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class ForecastResult:
    """Resultado de forecasting."""
    metric: str
    current_value: float
    forecast_value: float
    confidence: float
    trend: str  # increasing, decreasing, stable
    factors: Dict[str, Any]


class SupportForecaster:
    """Sistema de forecasting para tickets de soporte."""
    
    def __init__(self, db_connection: Any = None):
        """
        Inicializa el forecaster.
        
        Args:
            db_connection: Conexión a BD para datos históricos
        """
        self.db_connection = db_connection
    
    def forecast_volume(
        self,
        days_ahead: int = 7,
        period: str = "daily"
    ) -> ForecastResult:
        """
        Predice volumen de tickets.
        
        Args:
            days_ahead: Días a predecir
            period: daily, weekly, monthly
            
        Returns:
            ForecastResult con predicción
        """
        if not self.db_connection:
            return ForecastResult(
                metric="volume",
                current_value=0.0,
                forecast_value=0.0,
                confidence=0.0,
                trend="stable",
                factors={}
            )
        
        try:
            cursor = self.db_connection.cursor()
            
            # Obtener datos históricos (últimos 30 días)
            cursor.execute("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as ticket_count
                FROM support_tickets
                WHERE created_at >= NOW() - INTERVAL '30 days'
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """)
            
            historical_data = [(row[0], row[1]) for row in cursor.fetchall()]
            
            if not historical_data:
                return ForecastResult(
                    metric="volume",
                    current_value=0.0,
                    forecast_value=0.0,
                    confidence=0.0,
                    trend="stable",
                    factors={"error": "insufficient_data"}
                )
            
            # Calcular promedio diario
            daily_averages = [count for _, count in historical_data]
            avg_daily = sum(daily_averages) / len(daily_averages) if daily_averages else 0.0
            
            # Calcular tendencia (simple linear regression)
            n = len(daily_averages)
            if n > 1:
                x_values = list(range(n))
                y_values = daily_averages
                
                sum_x = sum(x_values)
                sum_y = sum(y_values)
                sum_xy = sum(x * y for x, y in zip(x_values, y_values))
                sum_x2 = sum(x * x for x in x_values)
                
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x) if (n * sum_x2 - sum_x * sum_x) != 0 else 0
                
                # Predicción
                forecast = avg_daily + (slope * days_ahead)
                forecast = max(0, forecast)  # No puede ser negativo
                
                # Determinar tendencia
                if slope > 0.1:
                    trend = "increasing"
                elif slope < -0.1:
                    trend = "decreasing"
                else:
                    trend = "stable"
                
                # Confianza basada en cantidad de datos y variabilidad
                variance = sum((y - avg_daily) ** 2 for y in y_values) / n if n > 0 else 0
                std_dev = variance ** 0.5
                confidence = min(0.9, max(0.3, 1.0 - (std_dev / avg_daily) if avg_daily > 0 else 0.3))
                
            else:
                forecast = avg_daily
                trend = "stable"
                confidence = 0.5
            
            cursor.close()
            
            return ForecastResult(
                metric="volume",
                current_value=avg_daily,
                forecast_value=forecast,
                confidence=confidence,
                trend=trend,
                factors={
                    "historical_days": n,
                    "slope": slope if n > 1 else 0,
                    "avg_daily": avg_daily
                }
            )
            
        except Exception as e:
            logger.error(f"Error forecasting volume: {e}", exc_info=True)
            return ForecastResult(
                metric="volume",
                current_value=0.0,
                forecast_value=0.0,
                confidence=0.0,
                trend="stable",
                factors={"error": str(e)}
            )
    
    def forecast_agent_workload(
        self,
        agent_id: str,
        days_ahead: int = 7
    ) -> ForecastResult:
        """Predice carga de trabajo de un agente."""
        if not self.db_connection:
            return ForecastResult(
                metric="agent_workload",
                current_value=0.0,
                forecast_value=0.0,
                confidence=0.0,
                trend="stable",
                factors={}
            )
        
        try:
            cursor = self.db_connection.cursor()
            
            # Tickets asignados históricamente
            cursor.execute("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as ticket_count
                FROM support_tickets
                WHERE assigned_agent_id = %s
                AND created_at >= NOW() - INTERVAL '30 days'
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """, (agent_id,))
            
            historical = [(row[0], row[1]) for row in cursor.fetchall()]
            
            if not historical:
                return ForecastResult(
                    metric="agent_workload",
                    current_value=0.0,
                    forecast_value=0.0,
                    confidence=0.0,
                    trend="stable",
                    factors={"error": "insufficient_data"}
                )
            
            daily_counts = [count for _, count in historical]
            avg_daily = sum(daily_counts) / len(daily_counts) if daily_counts else 0.0
            
            # Predicción simple (promedio)
            forecast = avg_daily * days_ahead
            
            cursor.close()
            
            return ForecastResult(
                metric="agent_workload",
                current_value=avg_daily,
                forecast_value=forecast,
                confidence=0.7,
                trend="stable",
                factors={
                    "agent_id": agent_id,
                    "historical_days": len(historical)
                }
            )
            
        except Exception as e:
            logger.error(f"Error forecasting agent workload: {e}")
            return ForecastResult(
                metric="agent_workload",
                current_value=0.0,
                forecast_value=0.0,
                confidence=0.0,
                trend="stable",
                factors={"error": str(e)}
            )
    
    def detect_seasonal_patterns(self) -> Dict[str, Any]:
        """Detecta patrones estacionales en los datos."""
        if not self.db_connection:
            return {}
        
        try:
            cursor = self.db_connection.cursor()
            
            # Tickets por día de la semana
            cursor.execute("""
                SELECT 
                    EXTRACT(DOW FROM created_at) as day_of_week,
                    COUNT(*) as ticket_count,
                    AVG(priority_score) as avg_priority
                FROM support_tickets
                WHERE created_at >= NOW() - INTERVAL '90 days'
                GROUP BY EXTRACT(DOW FROM created_at)
                ORDER BY day_of_week
            """)
            
            day_patterns = {}
            for row in cursor.fetchall():
                day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                day_name = day_names[int(row[0])]
                day_patterns[day_name] = {
                    "count": row[1],
                    "avg_priority": float(row[2]) if row[2] else 0.0
                }
            
            # Tickets por hora del día
            cursor.execute("""
                SELECT 
                    EXTRACT(HOUR FROM created_at) as hour,
                    COUNT(*) as ticket_count
                FROM support_tickets
                WHERE created_at >= NOW() - INTERVAL '30 days'
                GROUP BY EXTRACT(HOUR FROM created_at)
                ORDER BY hour
            """)
            
            hour_patterns = {}
            for row in cursor.fetchall():
                hour_patterns[int(row[0])] = row[1]
            
            cursor.close()
            
            return {
                "day_of_week": day_patterns,
                "hour_of_day": hour_patterns,
                "analysis_period_days": 90
            }
            
        except Exception as e:
            logger.error(f"Error detecting seasonal patterns: {e}")
            return {}

