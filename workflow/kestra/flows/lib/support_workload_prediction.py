"""
Sistema de Predicción de Carga de Trabajo.

Predice volumen de tickets y carga de trabajo futura.
"""
import logging
import math
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class WorkloadPrediction:
    """Predicción de carga de trabajo."""
    prediction_id: str
    period: str  # "hour", "day", "week", "month"
    start_time: datetime
    end_time: datetime
    predicted_ticket_count: float
    confidence: float  # 0.0 a 1.0
    predicted_agent_load: Dict[str, float]  # agent_id -> predicted_load
    factors: Dict[str, Any]  # Factores que influyen
    recommendations: List[str]


class WorkloadPredictor:
    """Predictor de carga de trabajo."""
    
    def __init__(self, db_connection=None):
        """
        Inicializa predictor.
        
        Args:
            db_connection: Conexión a BD (opcional)
        """
        self.db = db_connection
        self.historical_data: List[Dict[str, Any]] = []
    
    def predict_hourly(
        self,
        target_hour: datetime,
        lookback_days: int = 30
    ) -> WorkloadPrediction:
        """
        Predice carga horaria.
        
        Args:
            target_hour: Hora objetivo
            lookback_days: Días de historial a usar
            
        Returns:
            Predicción horaria
        """
        if not self.db:
            return self._default_prediction(target_hour, "hour")
        
        try:
            with self.db.cursor() as cur:
                # Obtener datos históricos para la misma hora del día
                hour_of_day = target_hour.hour
                day_of_week = target_hour.weekday()
                
                cur.execute("""
                    SELECT 
                        DATE_TRUNC('hour', created_at) as hour,
                        COUNT(*) as ticket_count
                    FROM support_tickets
                    WHERE created_at >= NOW() - INTERVAL %s days
                    AND EXTRACT(HOUR FROM created_at) = %s
                    AND EXTRACT(DOW FROM created_at) = %s
                    GROUP BY DATE_TRUNC('hour', created_at)
                    ORDER BY hour
                """, (lookback_days, hour_of_day, day_of_week))
                
                historical = cur.fetchall()
                
                if historical:
                    # Calcular promedio
                    counts = [row[1] for row in historical]
                    avg_count = sum(counts) / len(counts)
                    
                    # Calcular tendencia
                    trend = self._calculate_trend(counts)
                    
                    # Predicción ajustada por tendencia
                    predicted = avg_count * (1 + trend)
                    
                    # Calcular confianza (más datos = más confianza)
                    confidence = min(0.9, 0.5 + (len(counts) / 100))
                    
                    return WorkloadPrediction(
                        prediction_id=f"pred-hour-{target_hour.timestamp()}",
                        period="hour",
                        start_time=target_hour,
                        end_time=target_hour + timedelta(hours=1),
                        predicted_ticket_count=predicted,
                        confidence=confidence,
                        predicted_agent_load={},
                        factors={
                            "hour_of_day": hour_of_day,
                            "day_of_week": day_of_week,
                            "historical_average": avg_count,
                            "trend": trend,
                            "data_points": len(counts)
                        },
                        recommendations=self._generate_recommendations(predicted, "hour")
                    )
        except Exception as e:
            logger.error(f"Error predicting hourly workload: {e}")
        
        return self._default_prediction(target_hour, "hour")
    
    def predict_daily(
        self,
        target_date: datetime,
        lookback_days: int = 90
    ) -> WorkloadPrediction:
        """
        Predice carga diaria.
        
        Args:
            target_date: Fecha objetivo
            lookback_days: Días de historial
            
        Returns:
            Predicción diaria
        """
        if not self.db:
            return self._default_prediction(target_date, "day")
        
        try:
            with self.db.cursor() as cur:
                day_of_week = target_date.weekday()
                
                cur.execute("""
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as ticket_count
                    FROM support_tickets
                    WHERE created_at >= NOW() - INTERVAL %s days
                    AND EXTRACT(DOW FROM created_at) = %s
                    GROUP BY DATE(created_at)
                    ORDER BY date
                """, (lookback_days, day_of_week))
                
                historical = cur.fetchall()
                
                if historical:
                    counts = [row[1] for row in historical]
                    avg_count = sum(counts) / len(counts)
                    trend = self._calculate_trend(counts)
                    predicted = avg_count * (1 + trend)
                    
                    # Estimar carga por agente
                    agent_load = self._estimate_agent_load(predicted)
                    
                    return WorkloadPrediction(
                        prediction_id=f"pred-day-{target_date.date()}",
                        period="day",
                        start_time=target_date.replace(hour=0, minute=0, second=0),
                        end_time=target_date.replace(hour=23, minute=59, second=59),
                        predicted_ticket_count=predicted,
                        confidence=min(0.85, 0.6 + (len(counts) / 200)),
                        predicted_agent_load=agent_load,
                        factors={
                            "day_of_week": day_of_week,
                            "historical_average": avg_count,
                            "trend": trend,
                            "data_points": len(counts)
                        },
                        recommendations=self._generate_recommendations(predicted, "day")
                    )
        except Exception as e:
            logger.error(f"Error predicting daily workload: {e}")
        
        return self._default_prediction(target_date, "day")
    
    def predict_weekly(
        self,
        target_week_start: datetime,
        lookback_weeks: int = 12
    ) -> WorkloadPrediction:
        """
        Predice carga semanal.
        
        Args:
            target_week_start: Inicio de semana objetivo
            lookback_weeks: Semanas de historial
            
        Returns:
            Predicción semanal
        """
        if not self.db:
            return self._default_prediction(target_week_start, "week")
        
        try:
            with self.db.cursor() as cur:
                cur.execute("""
                    SELECT 
                        DATE_TRUNC('week', created_at) as week,
                        COUNT(*) as ticket_count
                    FROM support_tickets
                    WHERE created_at >= NOW() - INTERVAL %s weeks
                    GROUP BY DATE_TRUNC('week', created_at)
                    ORDER BY week
                """, (lookback_weeks,))
                
                historical = cur.fetchall()
                
                if historical:
                    counts = [row[1] for row in historical]
                    avg_count = sum(counts) / len(counts)
                    trend = self._calculate_trend(counts)
                    predicted = avg_count * (1 + trend)
                    
                    agent_load = self._estimate_agent_load(predicted / 7)  # Por día
                    
                    return WorkloadPrediction(
                        prediction_id=f"pred-week-{target_week_start.date()}",
                        period="week",
                        start_time=target_week_start,
                        end_time=target_week_start + timedelta(days=7),
                        predicted_ticket_count=predicted,
                        confidence=min(0.8, 0.5 + (len(counts) / 50)),
                        predicted_agent_load=agent_load,
                        factors={
                            "historical_average": avg_count,
                            "trend": trend,
                            "data_points": len(counts)
                        },
                        recommendations=self._generate_recommendations(predicted, "week")
                    )
        except Exception as e:
            logger.error(f"Error predicting weekly workload: {e}")
        
        return self._default_prediction(target_week_start, "week")
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calcula tendencia (regresión lineal simple)."""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x = list(range(n))
        y = values
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] * x[i] for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x) if (n * sum_x2 - sum_x * sum_x) != 0 else 0
        
        # Normalizar a porcentaje de cambio
        avg = sum_y / n
        trend = (slope / avg) if avg != 0 else 0
        
        return trend
    
    def _estimate_agent_load(self, predicted_tickets: float) -> Dict[str, float]:
        """Estima carga por agente."""
        if not self.db:
            return {}
        
        try:
            with self.db.cursor() as cur:
                cur.execute("""
                    SELECT agent_id, is_available
                    FROM support_agents
                    WHERE is_available = true
                """)
                
                agents = cur.fetchall()
                agent_count = len(agents)
                
                if agent_count == 0:
                    return {}
                
                # Distribución promedio
                avg_load_per_agent = predicted_tickets / agent_count
                
                return {agent[0]: avg_load_per_agent for agent in agents}
        except Exception as e:
            logger.error(f"Error estimating agent load: {e}")
        
        return {}
    
    def _generate_recommendations(
        self,
        predicted_count: float,
        period: str
    ) -> List[str]:
        """Genera recomendaciones basadas en predicción."""
        recommendations = []
        
        if predicted_count > 100 and period == "day":
            recommendations.append("Alta carga prevista. Considerar aumentar agentes disponibles.")
        
        if predicted_count > 20 and period == "hour":
            recommendations.append("Pico horario previsto. Preparar recursos adicionales.")
        
        if predicted_count < 10 and period == "day":
            recommendations.append("Baja carga prevista. Buen momento para capacitación o mantenimiento.")
        
        return recommendations
    
    def _default_prediction(
        self,
        target_time: datetime,
        period: str
    ) -> WorkloadPrediction:
        """Predicción por defecto cuando no hay datos."""
        end_time = target_time + timedelta(hours=1 if period == "hour" else days=1 if period == "day" else days=7)
        
        return WorkloadPrediction(
            prediction_id=f"pred-{period}-{target_time.timestamp()}",
            period=period,
            start_time=target_time,
            end_time=end_time,
            predicted_ticket_count=50.0,  # Valor por defecto
            confidence=0.3,
            predicted_agent_load={},
            factors={"note": "Insufficient historical data"},
            recommendations=["Recopilar más datos históricos para mejorar predicciones"]
        )
    
    def get_prediction_accuracy(
        self,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """
        Evalúa precisión de predicciones.
        
        Args:
            days_back: Días hacia atrás para evaluar
            
        Returns:
            Métricas de precisión
        """
        # Implementación básica - en producción comparar predicciones vs real
        return {
            "evaluation_period_days": days_back,
            "mean_absolute_error": 0.0,
            "accuracy_percentage": 0.0,
            "note": "Accuracy evaluation not yet implemented"
        }

