"""
Sistema de Detección de Anomalías.

Detecta patrones anómalos en tickets, métricas y comportamiento.
"""
import logging
import statistics
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Tipos de anomalías."""
    VOLUME_SPIKE = "volume_spike"
    VOLUME_DROP = "volume_drop"
    RESPONSE_TIME_ANOMALY = "response_time_anomaly"
    SATISFACTION_DROP = "satisfaction_drop"
    CATEGORY_SHIFT = "category_shift"
    PATTERN_DEVIATION = "pattern_deviation"


class AnomalySeverity(Enum):
    """Severidad de anomalía."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Anomaly:
    """Anomalía detectada."""
    anomaly_id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    description: str
    detected_at: datetime
    metric_name: str
    current_value: float
    expected_value: Optional[float] = None
    deviation_percentage: Optional[float] = None
    context: Dict[str, Any] = None
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.recommendations is None:
            self.recommendations = []


class AnomalyDetector:
    """Detector de anomalías."""
    
    def __init__(self, db_connection=None):
        """
        Inicializa detector.
        
        Args:
            db_connection: Conexión a BD (opcional)
        """
        self.db = db_connection
        self.detected_anomalies: List[Anomaly] = []
        self.baseline_metrics: Dict[str, Dict[str, float]] = {}  # metric -> stats
    
    def detect_anomalies(self) -> List[Anomaly]:
        """
        Detecta anomalías en el sistema.
        
        Returns:
            Lista de anomalías detectadas
        """
        anomalies = []
        
        # Detectar anomalías de volumen
        volume_anomalies = self._detect_volume_anomalies()
        anomalies.extend(volume_anomalies)
        
        # Detectar anomalías de tiempo de respuesta
        response_anomalies = self._detect_response_time_anomalies()
        anomalies.extend(response_anomalies)
        
        # Detectar anomalías de satisfacción
        satisfaction_anomalies = self._detect_satisfaction_anomalies()
        anomalies.extend(satisfaction_anomalies)
        
        # Detectar cambios en categorías
        category_anomalies = self._detect_category_shifts()
        anomalies.extend(category_anomalies)
        
        self.detected_anomalies.extend(anomalies)
        
        # Mantener solo últimos 1000
        if len(self.detected_anomalies) > 1000:
            self.detected_anomalies = self.detected_anomalies[-1000:]
        
        return anomalies
    
    def _detect_volume_anomalies(self) -> List[Anomaly]:
        """Detecta anomalías en volumen de tickets."""
        if not self.db:
            return []
        
        anomalies = []
        
        try:
            with self.db.cursor() as cur:
                # Volumen última hora vs promedio
                cur.execute("""
                    SELECT COUNT(*) FROM support_tickets
                    WHERE created_at >= NOW() - INTERVAL '1 hour'
                """)
                current_hour = cur.fetchone()[0]
                
                cur.execute("""
                    SELECT AVG(hour_count) FROM (
                        SELECT 
                            DATE_TRUNC('hour', created_at) as hour,
                            COUNT(*) as hour_count
                        FROM support_tickets
                        WHERE created_at >= NOW() - INTERVAL '7 days'
                        GROUP BY DATE_TRUNC('hour', created_at)
                    ) hourly_stats
                """)
                row = cur.fetchone()
                avg_hourly = float(row[0]) if row[0] else 0.0
                
                if avg_hourly > 0:
                    deviation = ((current_hour - avg_hourly) / avg_hourly) * 100
                    
                    if deviation > 50:  # Spike > 50%
                        anomalies.append(Anomaly(
                            anomaly_id=f"anomaly-volume-spike-{datetime.now().timestamp()}",
                            anomaly_type=AnomalyType.VOLUME_SPIKE,
                            severity=AnomalySeverity.HIGH if deviation > 100 else AnomalySeverity.MEDIUM,
                            description=f"Pico de volumen: {current_hour} tickets en última hora vs promedio {avg_hourly:.1f}",
                            detected_at=datetime.now(),
                            metric_name="tickets_per_hour",
                            current_value=float(current_hour),
                            expected_value=avg_hourly,
                            deviation_percentage=deviation,
                            recommendations=[
                                "Aumentar agentes disponibles",
                                "Verificar si hay incidente masivo",
                                "Considerar activar protocolo de emergencia"
                            ]
                        ))
                    
                    elif deviation < -50:  # Drop > 50%
                        anomalies.append(Anomaly(
                            anomaly_id=f"anomaly-volume-drop-{datetime.now().timestamp()}",
                            anomaly_type=AnomalyType.VOLUME_DROP,
                            severity=AnomalySeverity.LOW,
                            description=f"Caída de volumen: {current_hour} tickets en última hora vs promedio {avg_hourly:.1f}",
                            detected_at=datetime.now(),
                            metric_name="tickets_per_hour",
                            current_value=float(current_hour),
                            expected_value=avg_hourly,
                            deviation_percentage=deviation,
                            recommendations=[
                                "Verificar sistemas de entrada de tickets",
                                "Posible oportunidad para capacitación"
                            ]
                        ))
        except Exception as e:
            logger.error(f"Error detecting volume anomalies: {e}")
        
        return anomalies
    
    def _detect_response_time_anomalies(self) -> List[Anomaly]:
        """Detecta anomalías en tiempo de respuesta."""
        if not self.db:
            return []
        
        anomalies = []
        
        try:
            with self.db.cursor() as cur:
                # Tiempo promedio de respuesta últimas 24h
                cur.execute("""
                    SELECT AVG(EXTRACT(EPOCH FROM (first_response_at - created_at))/60)
                    FROM support_tickets
                    WHERE first_response_at IS NOT NULL
                    AND created_at >= NOW() - INTERVAL '24 hours'
                """)
                row = cur.fetchone()
                current_avg = float(row[0]) if row[0] else None
                
                if current_avg:
                    # Promedio histórico (últimos 7 días)
                    cur.execute("""
                        SELECT AVG(EXTRACT(EPOCH FROM (first_response_at - created_at))/60)
                        FROM support_tickets
                        WHERE first_response_at IS NOT NULL
                        AND created_at >= NOW() - INTERVAL '7 days'
                        AND created_at < NOW() - INTERVAL '24 hours'
                    """)
                    row = cur.fetchone()
                    historical_avg = float(row[0]) if row[0] else None
                    
                    if historical_avg and historical_avg > 0:
                        deviation = ((current_avg - historical_avg) / historical_avg) * 100
                        
                        if deviation > 30:  # Aumento significativo
                            anomalies.append(Anomaly(
                                anomaly_id=f"anomaly-response-time-{datetime.now().timestamp()}",
                                anomaly_type=AnomalyType.RESPONSE_TIME_ANOMALY,
                                severity=AnomalySeverity.HIGH if deviation > 50 else AnomalySeverity.MEDIUM,
                                description=f"Tiempo de respuesta aumentó: {current_avg:.1f} min vs promedio {historical_avg:.1f} min",
                                detected_at=datetime.now(),
                                metric_name="avg_response_time_minutes",
                                current_value=current_avg,
                                expected_value=historical_avg,
                                deviation_percentage=deviation,
                                recommendations=[
                                    "Revisar carga de agentes",
                                    "Verificar si hay bloqueos en el sistema",
                                    "Considerar escalar recursos"
                                ]
                            ))
        except Exception as e:
            logger.error(f"Error detecting response time anomalies: {e}")
        
        return anomalies
    
    def _detect_satisfaction_anomalies(self) -> List[Anomaly]:
        """Detecta anomalías en satisfacción."""
        if not self.db:
            return []
        
        anomalies = []
        
        try:
            with self.db.cursor() as cur:
                # Satisfacción últimas 24h
                cur.execute("""
                    SELECT AVG(satisfaction_score)
                    FROM support_ticket_feedback
                    WHERE submitted_at >= NOW() - INTERVAL '24 hours'
                """)
                row = cur.fetchone()
                current_avg = float(row[0]) if row[0] else None
                
                if current_avg:
                    # Promedio histórico
                    cur.execute("""
                        SELECT AVG(satisfaction_score)
                        FROM support_ticket_feedback
                        WHERE submitted_at >= NOW() - INTERVAL '7 days'
                        AND submitted_at < NOW() - INTERVAL '24 hours'
                    """)
                    row = cur.fetchone()
                    historical_avg = float(row[0]) if row[0] else None
                    
                    if historical_avg and historical_avg > 0:
                        deviation = ((current_avg - historical_avg) / historical_avg) * 100
                        
                        if deviation < -20:  # Caída significativa
                            anomalies.append(Anomaly(
                                anomaly_id=f"anomaly-satisfaction-{datetime.now().timestamp()}",
                                anomaly_type=AnomalyType.SATISFACTION_DROP,
                                severity=AnomalySeverity.CRITICAL if deviation < -30 else AnomalySeverity.HIGH,
                                description=f"Satisfacción cayó: {current_avg:.2f} vs promedio {historical_avg:.2f}",
                                detected_at=datetime.now(),
                                metric_name="customer_satisfaction",
                                current_value=current_avg,
                                expected_value=historical_avg,
                                deviation_percentage=deviation,
                                recommendations=[
                                    "Revisar tickets recientes con baja satisfacción",
                                    "Analizar causas de insatisfacción",
                                    "Implementar acciones correctivas inmediatas"
                                ]
                            ))
        except Exception as e:
            logger.error(f"Error detecting satisfaction anomalies: {e}")
        
        return anomalies
    
    def _detect_category_shifts(self) -> List[Anomaly]:
        """Detecta cambios en distribución de categorías."""
        if not self.db:
            return []
        
        anomalies = []
        
        try:
            with self.db.cursor() as cur:
                # Distribución actual (últimas 24h)
                cur.execute("""
                    SELECT category, COUNT(*) as count
                    FROM support_tickets
                    WHERE created_at >= NOW() - INTERVAL '24 hours'
                    AND category IS NOT NULL
                    GROUP BY category
                    ORDER BY count DESC
                """)
                current_dist = {row[0]: row[1] for row in cur.fetchall()}
                
                # Distribución histórica (últimos 7 días)
                cur.execute("""
                    SELECT category, COUNT(*) as count
                    FROM support_tickets
                    WHERE created_at >= NOW() - INTERVAL '7 days'
                    AND created_at < NOW() - INTERVAL '24 hours'
                    AND category IS NOT NULL
                    GROUP BY category
                """)
                historical_dist = {row[0]: row[1] for row in cur.fetchall()}
                
                # Calcular totales
                current_total = sum(current_dist.values())
                historical_total = sum(historical_dist.values())
                
                if current_total > 0 and historical_total > 0:
                    # Comparar proporciones
                    for category, current_count in current_dist.items():
                        current_pct = (current_count / current_total) * 100
                        historical_count = historical_dist.get(category, 0)
                        historical_pct = (historical_count / historical_total) * 100 if historical_total > 0 else 0
                        
                        if historical_pct > 0:
                            change = current_pct - historical_pct
                            
                            if abs(change) > 10:  # Cambio > 10 puntos porcentuales
                                anomalies.append(Anomaly(
                                    anomaly_id=f"anomaly-category-{category}-{datetime.now().timestamp()}",
                                    anomaly_type=AnomalyType.CATEGORY_SHIFT,
                                    severity=AnomalySeverity.MEDIUM if abs(change) > 15 else AnomalySeverity.LOW,
                                    description=f"Cambio en categoría {category}: {current_pct:.1f}% vs {historical_pct:.1f}% histórico",
                                    detected_at=datetime.now(),
                                    metric_name="category_distribution",
                                    current_value=current_pct,
                                    expected_value=historical_pct,
                                    deviation_percentage=change,
                                    context={"category": category},
                                    recommendations=[
                                        f"Verificar si hay problema específico en categoría {category}",
                                        "Revisar si hay cambio en producto o servicio"
                                    ]
                                ))
        except Exception as e:
            logger.error(f"Error detecting category shifts: {e}")
        
        return anomalies
    
    def get_anomaly_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Obtiene resumen de anomalías.
        
        Args:
            hours: Horas hacia atrás
            
        Returns:
            Resumen de anomalías
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [a for a in self.detected_anomalies if a.detected_at >= cutoff]
        
        by_type = {}
        by_severity = {}
        
        for anomaly in recent:
            # Por tipo
            atype = anomaly.anomaly_type.value
            by_type[atype] = by_type.get(atype, 0) + 1
            
            # Por severidad
            severity = anomaly.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            "period_hours": hours,
            "total_anomalies": len(recent),
            "by_type": by_type,
            "by_severity": by_severity,
            "recent_anomalies": [
                {
                    "id": a.anomaly_id,
                    "type": a.anomaly_type.value,
                    "severity": a.severity.value,
                    "description": a.description,
                    "detected_at": a.detected_at.isoformat()
                }
                for a in sorted(recent, key=lambda x: x.detected_at, reverse=True)[:10]
            ]
        }

