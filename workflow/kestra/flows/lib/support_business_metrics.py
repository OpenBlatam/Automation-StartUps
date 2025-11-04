"""
Sistema de Métricas de Negocio Avanzadas.

Calcula y analiza métricas de negocio clave para soporte.
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Tipos de métricas."""
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    CUSTOMER = "customer"
    EFFICIENCY = "efficiency"
    QUALITY = "quality"


@dataclass
class BusinessMetric:
    """Métrica de negocio."""
    metric_id: str
    name: str
    description: str
    metric_type: MetricType
    value: float
    unit: str
    period_start: datetime
    period_end: datetime
    target_value: Optional[float] = None
    previous_value: Optional[float] = None
    trend: Optional[str] = None  # "up", "down", "stable"
    
    def __post_init__(self):
        if self.previous_value is not None:
            if self.value > self.previous_value:
                self.trend = "up"
            elif self.value < self.previous_value:
                self.trend = "down"
            else:
                self.trend = "stable"


@dataclass
class BusinessMetricsReport:
    """Reporte de métricas de negocio."""
    report_id: str
    period_start: datetime
    period_end: datetime
    metrics: List[BusinessMetric]
    insights: List[str]
    recommendations: List[str]
    generated_at: datetime = None
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now()


class BusinessMetricsAnalyzer:
    """Analizador de métricas de negocio."""
    
    def __init__(self, db_connection=None):
        """
        Inicializa analizador.
        
        Args:
            db_connection: Conexión a BD (opcional)
        """
        self.db = db_connection
        self.metrics: List[BusinessMetric] = []
    
    def calculate_customer_lifetime_value(
        self,
        customer_id: str,
        period_months: int = 12
    ) -> float:
        """
        Calcula Customer Lifetime Value (CLV).
        
        Args:
            customer_id: ID del cliente
            period_months: Meses hacia atrás
            
        Returns:
            CLV estimado
        """
        if not self.db:
            return 0.0
        
        try:
            with self.db.cursor() as cur:
                period_start = datetime.now() - timedelta(days=period_months * 30)
                
                # Tickets del cliente
                cur.execute("""
                    SELECT 
                        COUNT(*) as tickets,
                        AVG(customer_satisfaction_score) as avg_satisfaction,
                        AVG(time_to_resolution_minutes) / 60.0 as avg_hours
                    FROM support_tickets
                    WHERE customer_email = %s
                    AND created_at >= %s
                """, (customer_id, period_start))
                
                row = cur.fetchone()
                tickets = row[0] or 0
                avg_satisfaction = float(row[1]) if row[1] else 0.0
                avg_hours = float(row[2]) if row[2] else 0.0
                
                # Calcular CLV basado en satisfacción y volumen
                base_value = tickets * 50  # $50 por ticket
                satisfaction_multiplier = avg_satisfaction / 100.0
                clv = base_value * (1 + satisfaction_multiplier)
                
                return clv
                
        except Exception as e:
            logger.error(f"Error calculating CLV: {e}")
            return 0.0
    
    def calculate_cost_per_ticket(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> float:
        """
        Calcula costo por ticket.
        
        Args:
            period_start: Inicio del período
            period_end: Fin del período
            
        Returns:
            Costo por ticket
        """
        if not self.db:
            return 0.0
        
        try:
            with self.db.cursor() as cur:
                # Costos totales
                cur.execute("""
                    SELECT 
                        COUNT(*) as tickets,
                        SUM(time_to_resolution_minutes) / 60.0 as total_hours
                    FROM support_tickets
                    WHERE created_at >= %s AND created_at <= %s
                    AND chatbot_resolved = false
                """, (period_start, period_end))
                
                row = cur.fetchone()
                tickets = row[0] or 0
                total_hours = float(row[1]) if row[1] else 0.0
                
                if tickets == 0:
                    return 0.0
                
                # Costo por hora de agente
                hourly_rate = 25.0
                total_cost = total_hours * hourly_rate
                cost_per_ticket = total_cost / tickets
                
                return cost_per_ticket
                
        except Exception as e:
            logger.error(f"Error calculating cost per ticket: {e}")
            return 0.0
    
    def calculate_first_contact_resolution_rate(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> float:
        """
        Calcula tasa de resolución en primer contacto.
        
        Args:
            period_start: Inicio del período
            period_end: Fin del período
            
        Returns:
            Tasa de FCR (0-100)
        """
        if not self.db:
            return 0.0
        
        try:
            with self.db.cursor() as cur:
                cur.execute("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE interaction_count = 1) as fcr
                    FROM support_tickets
                    WHERE created_at >= %s AND created_at <= %s
                    AND status = 'resolved'
                """, (period_start, period_end))
                
                row = cur.fetchone()
                total = row[0] or 0
                fcr = row[1] or 0
                
                if total == 0:
                    return 0.0
                
                return (fcr / total) * 100
                
        except Exception as e:
            logger.error(f"Error calculating FCR: {e}")
            return 0.0
    
    def calculate_net_promoter_score(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> float:
        """
        Calcula Net Promoter Score (NPS).
        
        Args:
            period_start: Inicio del período
            period_end: Fin del período
            
        Returns:
            NPS (-100 a 100)
        """
        if not self.db:
            return 0.0
        
        try:
            with self.db.cursor() as cur:
                cur.execute("""
                    SELECT 
                        COUNT(*) FILTER (WHERE nps_score >= 9) as promoters,
                        COUNT(*) FILTER (WHERE nps_score <= 6) as detractors,
                        COUNT(*) as total
                    FROM support_feedback
                    WHERE created_at >= %s AND created_at <= %s
                    AND nps_score IS NOT NULL
                """, (period_start, period_end))
                
                row = cur.fetchone()
                promoters = row[0] or 0
                detractors = row[1] or 0
                total = row[2] or 0
                
                if total == 0:
                    return 0.0
                
                promoter_percentage = (promoters / total) * 100
                detractor_percentage = (detractors / total) * 100
                
                nps = promoter_percentage - detractor_percentage
                
                return nps
                
        except Exception as e:
            logger.error(f"Error calculating NPS: {e}")
            return 0.0
    
    def calculate_agent_productivity(
        self,
        agent_id: str,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """
        Calcula productividad de agente.
        
        Args:
            agent_id: ID del agente
            period_start: Inicio del período
            period_end: Fin del período
            
        Returns:
            Métricas de productividad
        """
        if not self.db:
            return {}
        
        try:
            with self.db.cursor() as cur:
                cur.execute("""
                    SELECT 
                        COUNT(*) as tickets,
                        AVG(time_to_resolution_minutes) / 60.0 as avg_resolution_hours,
                        AVG(customer_satisfaction_score) as avg_satisfaction,
                        COUNT(*) FILTER (WHERE status = 'resolved') as resolved
                    FROM support_tickets
                    WHERE assigned_agent_id = %s
                    AND created_at >= %s AND created_at <= %s
                """, (agent_id, period_start, period_end))
                
                row = cur.fetchone()
                tickets = row[0] or 0
                avg_hours = float(row[1]) if row[1] else 0.0
                avg_satisfaction = float(row[2]) if row[2] else 0.0
                resolved = row[3] or 0
                
                resolution_rate = (resolved / tickets * 100) if tickets > 0 else 0.0
                
                return {
                    "tickets_handled": tickets,
                    "avg_resolution_hours": avg_hours,
                    "avg_satisfaction": avg_satisfaction,
                    "resolution_rate": resolution_rate,
                    "productivity_score": (tickets * 0.4) + (resolution_rate * 0.3) + (avg_satisfaction * 0.3)
                }
                
        except Exception as e:
            logger.error(f"Error calculating agent productivity: {e}")
            return {}
    
    def generate_business_metrics_report(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> BusinessMetricsReport:
        """
        Genera reporte completo de métricas de negocio.
        
        Args:
            period_start: Inicio del período
            period_end: Fin del período
            
        Returns:
            Reporte de métricas
        """
        metrics = []
        insights = []
        recommendations = []
        
        # Costo por ticket
        cost_per_ticket = self.calculate_cost_per_ticket(period_start, period_end)
        metrics.append(BusinessMetric(
            metric_id="cost-per-ticket",
            name="Costo por Ticket",
            description="Costo promedio de procesar un ticket",
            metric_type=MetricType.FINANCIAL,
            value=cost_per_ticket,
            unit="USD",
            period_start=period_start,
            period_end=period_end,
            target_value=20.0
        ))
        
        # FCR
        fcr = self.calculate_first_contact_resolution_rate(period_start, period_end)
        metrics.append(BusinessMetric(
            metric_id="fcr-rate",
            name="First Contact Resolution",
            description="Tasa de resolución en primer contacto",
            metric_type=MetricType.EFFICIENCY,
            value=fcr,
            unit="%",
            period_start=period_start,
            period_end=period_end,
            target_value=75.0
        ))
        
        # NPS
        nps = self.calculate_net_promoter_score(period_start, period_end)
        metrics.append(BusinessMetric(
            metric_id="nps",
            name="Net Promoter Score",
            description="NPS del servicio de soporte",
            metric_type=MetricType.CUSTOMER,
            value=nps,
            unit="score",
            period_start=period_start,
            period_end=period_end,
            target_value=50.0
        ))
        
        # Generar insights
        if cost_per_ticket > 30:
            insights.append(f"Costo por ticket alto: ${cost_per_ticket:.2f}. Considerar optimización.")
        
        if fcr < 60:
            insights.append(f"FCR bajo: {fcr:.1f}%. Mejorar resolución en primer contacto.")
        
        if nps < 30:
            insights.append(f"NPS bajo: {nps:.1f}. Mejorar experiencia del cliente.")
        
        # Recomendaciones
        if cost_per_ticket > 30:
            recommendations.append("Implementar más automatización con chatbot")
        
        if fcr < 60:
            recommendations.append("Mejorar conocimiento de agentes y base de conocimiento")
        
        if nps < 30:
            recommendations.append("Analizar feedback de clientes y mejorar procesos")
        
        report = BusinessMetricsReport(
            report_id=f"business-metrics-{period_end.strftime('%Y%m%d')}",
            period_start=period_start,
            period_end=period_end,
            metrics=metrics,
            insights=insights,
            recommendations=recommendations
        )
        
        return report

