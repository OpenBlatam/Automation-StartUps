"""
Sistema de Health Score de Clientes.

Calcula un score de salud del cliente basado en múltiples factores:
tickets, satisfacción, engagement, churn risk, etc.
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import statistics

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Estados de salud del cliente."""
    EXCELLENT = "excellent"  # 80-100
    GOOD = "good"  # 60-79
    FAIR = "fair"  # 40-59
    AT_RISK = "at_risk"  # 20-39
    CRITICAL = "critical"  # 0-19


@dataclass
class CustomerHealthScore:
    """Score de salud del cliente."""
    customer_email: str
    customer_id: Optional[str]
    health_score: float  # 0-100
    health_status: HealthStatus
    period_start: datetime
    period_end: datetime
    
    # Componentes del score
    ticket_volume_score: float
    satisfaction_score: float
    engagement_score: float
    churn_risk_score: float
    response_time_score: float
    
    # Métricas
    total_tickets: int
    avg_satisfaction: float
    days_since_last_ticket: int
    days_since_last_response: int
    churn_probability: float
    
    # Recomendaciones
    recommendations: List[str]
    risk_factors: List[str]


class CustomerHealthAnalyzer:
    """Analizador de salud de clientes."""
    
    def __init__(self, db_connection):
        """Inicializar analizador."""
        self.db = db_connection
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def calculate_health_score(
        self,
        customer_email: str,
        days: int = 90
    ) -> CustomerHealthScore:
        """Calcular health score de un cliente."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Obtener métricas de tickets
        ticket_metrics = self._get_ticket_metrics(customer_email, start_date)
        
        # Obtener métricas de satisfacción
        satisfaction_metrics = self._get_satisfaction_metrics(customer_email, start_date)
        
        # Obtener métricas de engagement
        engagement_metrics = self._get_engagement_metrics(customer_email, start_date)
        
        # Calcular churn risk
        churn_risk = self._calculate_churn_risk(customer_email, ticket_metrics, satisfaction_metrics)
        
        # Calcular scores por componente
        ticket_volume_score = self._score_ticket_volume(ticket_metrics)
        satisfaction_score = self._score_satisfaction(satisfaction_metrics)
        engagement_score = self._score_engagement(engagement_metrics)
        churn_risk_score = (1.0 - churn_risk) * 100  # Invertir para score
        response_time_score = self._score_response_time(ticket_metrics)
        
        # Calcular health score total (ponderado)
        health_score = (
            ticket_volume_score * 0.15 +
            satisfaction_score * 0.30 +
            engagement_score * 0.20 +
            churn_risk_score * 0.25 +
            response_time_score * 0.10
        )
        
        # Determinar estado
        if health_score >= 80:
            status = HealthStatus.EXCELLENT
        elif health_score >= 60:
            status = HealthStatus.GOOD
        elif health_score >= 40:
            status = HealthStatus.FAIR
        elif health_score >= 20:
            status = HealthStatus.AT_RISK
        else:
            status = HealthStatus.CRITICAL
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations(
            health_score, ticket_metrics, satisfaction_metrics, engagement_metrics
        )
        
        # Identificar factores de riesgo
        risk_factors = self._identify_risk_factors(
            ticket_metrics, satisfaction_metrics, engagement_metrics, churn_risk
        )
        
        return CustomerHealthScore(
            customer_email=customer_email,
            customer_id=ticket_metrics.get("customer_id"),
            health_score=health_score,
            health_status=status,
            period_start=start_date,
            period_end=end_date,
            ticket_volume_score=ticket_volume_score,
            satisfaction_score=satisfaction_score,
            engagement_score=engagement_score,
            churn_risk_score=churn_risk_score,
            response_time_score=response_time_score,
            total_tickets=ticket_metrics.get("total_tickets", 0),
            avg_satisfaction=satisfaction_metrics.get("avg_satisfaction", 0.0),
            days_since_last_ticket=ticket_metrics.get("days_since_last", 0),
            days_since_last_response=engagement_metrics.get("days_since_response", 0),
            churn_probability=churn_risk,
            recommendations=recommendations,
            risk_factors=risk_factors
        )
    
    def _get_ticket_metrics(
        self,
        customer_email: str,
        start_date: datetime
    ) -> Dict[str, Any]:
        """Obtener métricas de tickets."""
        query = """
            SELECT 
                COUNT(*) as total_tickets,
                COUNT(*) FILTER (WHERE status = 'resolved') as resolved,
                COUNT(*) FILTER (WHERE priority IN ('urgent', 'critical')) as urgent,
                AVG(time_to_resolution_minutes) as avg_resolution_time,
                MAX(created_at) as last_ticket_date,
                customer_id
            FROM support_tickets
            WHERE customer_email = %s
                AND created_at >= %s
            GROUP BY customer_id
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [customer_email, start_date])
            row = cur.fetchone()
        
        if not row:
            return {
                "total_tickets": 0,
                "resolved": 0,
                "urgent": 0,
                "avg_resolution_time": 0,
                "days_since_last": 999,
                "customer_id": None
            }
        
        last_ticket = row[4]
        days_since = (datetime.now() - last_ticket).days if last_ticket else 999
        
        return {
            "total_tickets": row[0] or 0,
            "resolved": row[1] or 0,
            "urgent": row[2] or 0,
            "avg_resolution_time": float(row[3]) if row[3] else 0,
            "days_since_last": days_since,
            "customer_id": row[5]
        }
    
    def _get_satisfaction_metrics(
        self,
        customer_email: str,
        start_date: datetime
    ) -> Dict[str, Any]:
        """Obtener métricas de satisfacción."""
        query = """
            SELECT 
                AVG(satisfaction_score) as avg_satisfaction,
                COUNT(*) as feedback_count,
                COUNT(*) FILTER (WHERE satisfaction_score >= 4) as positive_feedback
            FROM support_ticket_feedback
            WHERE customer_email = %s
                AND submitted_at >= %s
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [customer_email, start_date])
            row = cur.fetchone()
        
        if not row or not row[1]:
            return {
                "avg_satisfaction": 0.0,
                "feedback_count": 0,
                "positive_ratio": 0.0
            }
        
        return {
            "avg_satisfaction": float(row[0]) if row[0] else 0.0,
            "feedback_count": row[1] or 0,
            "positive_ratio": (row[2] or 0) / row[1] if row[1] > 0 else 0.0
        }
    
    def _get_engagement_metrics(
        self,
        customer_email: str,
        start_date: datetime
    ) -> Dict[str, Any]:
        """Obtener métricas de engagement."""
        query = """
            SELECT 
                MAX(updated_at) as last_response_date,
                COUNT(DISTINCT DATE(created_at)) as active_days
            FROM support_tickets
            WHERE customer_email = %s
                AND created_at >= %s
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [customer_email, start_date])
            row = cur.fetchone()
        
        last_response = row[0]
        days_since_response = (datetime.now() - last_response).days if last_response else 999
        
        return {
            "days_since_response": days_since_response,
            "active_days": row[1] or 0
        }
    
    def _calculate_churn_risk(
        self,
        customer_email: str,
        ticket_metrics: Dict[str, Any],
        satisfaction_metrics: Dict[str, Any]
    ) -> float:
        """Calcular riesgo de churn."""
        risk = 0.0
        
        # Factor: Sin tickets recientes
        if ticket_metrics["days_since_last"] > 90:
            risk += 0.3
        elif ticket_metrics["days_since_last"] > 60:
            risk += 0.2
        
        # Factor: Satisfacción baja
        if satisfaction_metrics["avg_satisfaction"] < 3.0:
            risk += 0.3
        elif satisfaction_metrics["avg_satisfaction"] < 3.5:
            risk += 0.15
        
        # Factor: Muchos tickets urgentes
        if ticket_metrics["total_tickets"] > 0:
            urgent_ratio = ticket_metrics["urgent"] / ticket_metrics["total_tickets"]
            if urgent_ratio > 0.3:
                risk += 0.2
        
        # Factor: Tiempo de resolución alto
        if ticket_metrics["avg_resolution_time"] > 480:  # >8 horas
            risk += 0.1
        
        return min(1.0, risk)
    
    def _score_ticket_volume(self, metrics: Dict[str, Any]) -> float:
        """Score por volumen de tickets (menos es mejor, pero no cero)."""
        total = metrics["total_tickets"]
        
        if total == 0:
            return 50.0  # Sin tickets puede ser bueno o malo
        elif total <= 2:
            return 90.0  # Pocos tickets, bueno
        elif total <= 5:
            return 70.0
        elif total <= 10:
            return 50.0
        elif total <= 20:
            return 30.0
        else:
            return 10.0  # Demasiados tickets
    
    def _score_satisfaction(self, metrics: Dict[str, Any]) -> float:
        """Score por satisfacción."""
        avg = metrics["avg_satisfaction"]
        
        if avg >= 4.5:
            return 100.0
        elif avg >= 4.0:
            return 80.0
        elif avg >= 3.5:
            return 60.0
        elif avg >= 3.0:
            return 40.0
        elif avg > 0:
            return 20.0
        else:
            return 50.0  # Sin feedback
    
    def _score_engagement(self, metrics: Dict[str, Any]) -> float:
        """Score por engagement."""
        days_since = metrics["days_since_response"]
        active_days = metrics["active_days"]
        
        # Componente 1: Días desde última respuesta
        if days_since <= 7:
            time_score = 100.0
        elif days_since <= 30:
            time_score = 70.0
        elif days_since <= 60:
            time_score = 40.0
        else:
            time_score = 10.0
        
        # Componente 2: Días activos
        if active_days >= 10:
            activity_score = 100.0
        elif active_days >= 5:
            activity_score = 70.0
        elif active_days >= 2:
            activity_score = 50.0
        else:
            activity_score = 20.0
        
        return (time_score * 0.6 + activity_score * 0.4)
    
    def _score_response_time(self, metrics: Dict[str, Any]) -> float:
        """Score por tiempo de respuesta."""
        avg_time = metrics["avg_resolution_time"]
        
        if avg_time == 0:
            return 50.0
        
        if avg_time <= 60:  # <1 hora
            return 100.0
        elif avg_time <= 120:  # <2 horas
            return 80.0
        elif avg_time <= 240:  # <4 horas
            return 60.0
        elif avg_time <= 480:  # <8 horas
            return 40.0
        else:
            return 20.0
    
    def _generate_recommendations(
        self,
        health_score: float,
        ticket_metrics: Dict[str, Any],
        satisfaction_metrics: Dict[str, Any],
        engagement_metrics: Dict[str, Any]
    ) -> List[str]:
        """Generar recomendaciones."""
        recommendations = []
        
        if health_score < 40:
            recommendations.append("Cliente en riesgo - Contacto proactivo requerido")
        
        if satisfaction_metrics["avg_satisfaction"] < 3.5:
            recommendations.append("Mejorar satisfacción del cliente - Revisar casos recientes")
        
        if ticket_metrics["days_since_last"] > 60:
            recommendations.append("Cliente inactivo - Campaña de re-engagement")
        
        if ticket_metrics["urgent"] > ticket_metrics["total_tickets"] * 0.3:
            recommendations.append("Muchos tickets urgentes - Revisar proceso de escalación")
        
        if engagement_metrics["days_since_response"] > 30:
            recommendations.append("Sin respuesta reciente - Verificar engagement")
        
        if not recommendations:
            recommendations.append("Cliente saludable - Mantener nivel actual")
        
        return recommendations
    
    def _identify_risk_factors(
        self,
        ticket_metrics: Dict[str, Any],
        satisfaction_metrics: Dict[str, Any],
        engagement_metrics: Dict[str, Any],
        churn_risk: float
    ) -> List[str]:
        """Identificar factores de riesgo."""
        factors = []
        
        if churn_risk > 0.5:
            factors.append("Alto riesgo de churn")
        
        if satisfaction_metrics["avg_satisfaction"] < 3.0:
            factors.append("Satisfacción baja")
        
        if ticket_metrics["days_since_last"] > 90:
            factors.append("Inactividad prolongada")
        
        if ticket_metrics["urgent"] > ticket_metrics["total_tickets"] * 0.3:
            factors.append("Alta proporción de tickets urgentes")
        
        if engagement_metrics["days_since_response"] > 60:
            factors.append("Bajo engagement")
        
        return factors
    
    def get_at_risk_customers(
        self,
        health_threshold: float = 40.0,
        limit: int = 50
    ) -> List[CustomerHealthScore]:
        """Obtener clientes en riesgo."""
        # Obtener clientes con tickets recientes
        query = """
            SELECT DISTINCT customer_email
            FROM support_tickets
            WHERE created_at >= NOW() - INTERVAL '90 days'
            ORDER BY customer_email
            LIMIT %s
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [limit * 2])
            customers = [row[0] for row in cur.fetchall()]
        
        health_scores = []
        for customer in customers:
            try:
                health = self.calculate_health_score(customer, days=90)
                if health.health_score < health_threshold:
                    health_scores.append(health)
            except Exception as e:
                self.logger.error(f"Error calculando health para {customer}: {e}")
        
        return sorted(health_scores, key=lambda h: h.health_score)[:limit]
    
    def generate_health_report(
        self,
        days: int = 90
    ) -> Dict[str, Any]:
        """Generar reporte de salud de clientes."""
        # Obtener todos los clientes
        query = """
            SELECT DISTINCT customer_email
            FROM support_tickets
            WHERE created_at >= NOW() - INTERVAL '%s days'
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [f"{days} days"])
            customers = [row[0] for row in cur.fetchall()]
        
        health_scores = []
        for customer in customers[:100]:  # Limitar para performance
            try:
                health = self.calculate_health_score(customer, days=days)
                health_scores.append(health)
            except Exception as e:
                self.logger.error(f"Error: {e}")
        
        # Estadísticas
        scores = [h.health_score for h in health_scores]
        
        status_counts = {}
        for status in HealthStatus:
            status_counts[status.value] = len([
                h for h in health_scores if h.health_status == status
            ])
        
        return {
            "period_days": days,
            "total_customers_analyzed": len(health_scores),
            "average_health_score": statistics.mean(scores) if scores else 0.0,
            "median_health_score": statistics.median(scores) if scores else 0.0,
            "status_distribution": status_counts,
            "at_risk_count": len([h for h in health_scores if h.health_status in [
                HealthStatus.AT_RISK, HealthStatus.CRITICAL
            ]]),
            "top_at_risk": [
                {
                    "email": h.customer_email,
                    "score": h.health_score,
                    "status": h.health_status.value,
                    "risk_factors": h.risk_factors
                }
                for h in sorted(health_scores, key=lambda x: x.health_score)[:10]
            ]
        }


