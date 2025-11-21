"""
Sistema de Satisfacción del Cliente Avanzado.

Análisis profundo de satisfacción, seguimiento de tendencias,
y acciones proactivas basadas en feedback.
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SatisfactionTrend(Enum):
    """Tendencias de satisfacción."""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    CRITICAL = "critical"


@dataclass
class SatisfactionScore:
    """Score de satisfacción."""
    overall_score: float
    response_time_score: float
    resolution_quality_score: float
    agent_helpfulness_score: float
    chatbot_helpfulness_score: float
    trend: SatisfactionTrend
    confidence: float
    sample_size: int
    period_start: datetime
    period_end: datetime


@dataclass
class SatisfactionInsight:
    """Insight de satisfacción."""
    insight_type: str
    title: str
    description: str
    severity: str
    recommendation: str
    metrics: Dict[str, Any]


@dataclass
class CustomerSatisfactionProfile:
    """Perfil de satisfacción de un cliente."""
    customer_email: str
    average_score: float
    total_tickets: int
    satisfaction_history: List[Dict[str, Any]]
    sentiment_trend: SatisfactionTrend
    risk_level: str
    recommendations: List[str]


class CustomerSatisfactionAnalyzer:
    """Analizador de satisfacción del cliente."""
    
    def __init__(self, db_connection):
        """Inicializar analizador."""
        self.db = db_connection
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def calculate_satisfaction_score(
        self,
        days: int = 30,
        customer_email: Optional[str] = None
    ) -> SatisfactionScore:
        """Calcular score de satisfacción."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        query = """
            SELECT 
                satisfaction_score,
                response_time_rating,
                resolution_quality_rating,
                agent_was_helpful,
                chatbot_was_helpful
            FROM support_ticket_feedback
            WHERE submitted_at >= %s AND submitted_at <= %s
        """
        params = [start_date, end_date]
        
        if customer_email:
            query += " AND customer_email = %s"
            params.append(customer_email)
        
        with self.db.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
        
        if not rows:
            return SatisfactionScore(
                overall_score=0.0,
                response_time_score=0.0,
                resolution_quality_score=0.0,
                agent_helpfulness_score=0.0,
                chatbot_helpfulness_score=0.0,
                trend=SatisfactionTrend.STABLE,
                confidence=0.0,
                sample_size=0,
                period_start=start_date,
                period_end=end_date
            )
        
        # Calcular scores promedio
        overall_scores = [r[0] for r in rows if r[0]]
        response_scores = [r[1] for r in rows if r[1] else []]
        quality_scores = [r[2] for r in rows if r[2] else []]
        agent_helpful = [1 if r[3] else 0 for r in rows if r[3] is not None]
        chatbot_helpful = [1 if r[4] else 0 for r in rows if r[4] is not None]
        
        overall = statistics.mean(overall_scores) if overall_scores else 0.0
        response = statistics.mean(response_scores) if response_scores else 0.0
        quality = statistics.mean(quality_scores) if quality_scores else 0.0
        agent = statistics.mean(agent_helpful) * 5.0 if agent_helpful else 0.0
        chatbot = statistics.mean(chatbot_helpful) * 5.0 if chatbot_helpful else 0.0
        
        # Comparar con período anterior
        prev_start = start_date - timedelta(days=days)
        prev_score = self._get_previous_score(prev_start, start_date, customer_email)
        
        if prev_score > 0:
            if overall > prev_score * 1.05:
                trend = SatisfactionTrend.IMPROVING
            elif overall < prev_score * 0.95:
                trend = SatisfactionTrend.DECLINING if overall >= 3.0 else SatisfactionTrend.CRITICAL
            else:
                trend = SatisfactionTrend.STABLE
        else:
            trend = SatisfactionTrend.STABLE
        
        confidence = min(1.0, len(rows) / 50.0)  # Máxima confianza con 50+ muestras
        
        return SatisfactionScore(
            overall_score=overall,
            response_time_score=response,
            resolution_quality_score=quality,
            agent_helpfulness_score=agent,
            chatbot_helpfulness_score=chatbot,
            trend=trend,
            confidence=confidence,
            sample_size=len(rows),
            period_start=start_date,
            period_end=end_date
        )
    
    def _get_previous_score(
        self,
        start: datetime,
        end: datetime,
        customer_email: Optional[str]
    ) -> float:
        """Obtener score del período anterior."""
        query = """
            SELECT AVG(satisfaction_score)
            FROM support_ticket_feedback
            WHERE submitted_at >= %s AND submitted_at < %s
        """
        params = [start, end]
        
        if customer_email:
            query += " AND customer_email = %s"
            params.append(customer_email)
        
        with self.db.cursor() as cur:
            cur.execute(query, params)
            result = cur.fetchone()
            return result[0] if result and result[0] else 0.0
    
    def analyze_satisfaction_insights(
        self,
        days: int = 30
    ) -> List[SatisfactionInsight]:
        """Analizar insights de satisfacción."""
        score = self.calculate_satisfaction_score(days=days)
        insights = []
        
        # Insight: Score general bajo
        if score.overall_score < 3.0:
            insights.append(SatisfactionInsight(
                insight_type="low_overall_score",
                title="Satisfacción General Baja",
                description=f"El score promedio es {score.overall_score:.2f}/5.0, por debajo del umbral de 3.0",
                severity="critical",
                recommendation="Revisar procesos de resolución y capacitación de agentes",
                metrics={"score": score.overall_score, "sample_size": score.sample_size}
            ))
        
        # Insight: Tiempo de respuesta
        if score.response_time_score < 3.0:
            insights.append(SatisfactionInsight(
                insight_type="slow_response",
                title="Tiempo de Respuesta Insatisfactorio",
                description=f"Calificación de tiempo de respuesta: {score.response_time_score:.2f}/5.0",
                severity="high",
                recommendation="Implementar alertas proactivas y reducir tiempos de respuesta",
                metrics={"response_score": score.response_time_score}
            ))
        
        # Insight: Calidad de resolución
        if score.resolution_quality_score < 3.0:
            insights.append(SatisfactionInsight(
                insight_type="poor_resolution_quality",
                title="Calidad de Resolución Baja",
                description=f"Calificación de calidad: {score.resolution_quality_score:.2f}/5.0",
                severity="high",
                recommendation="Mejorar documentación y capacitación técnica",
                metrics={"quality_score": score.resolution_quality_score}
            ))
        
        # Insight: Tendencia negativa
        if score.trend == SatisfactionTrend.DECLINING:
            insights.append(SatisfactionInsight(
                insight_type="declining_trend",
                title="Tendencia de Satisfacción Declinando",
                description="La satisfacción ha disminuido en comparación con el período anterior",
                severity="medium",
                recommendation="Investigar causas raíz y tomar acciones correctivas",
                metrics={"trend": score.trend.value}
            ))
        
        # Insight: Chatbot inefectivo
        if score.chatbot_helpfulness_score < 2.5:
            insights.append(SatisfactionInsight(
                insight_type="chatbot_ineffective",
                title="Chatbot No Efectivo",
                description=f"Calificación del chatbot: {score.chatbot_helpfulness_score:.2f}/5.0",
                severity="medium",
                recommendation="Mejorar conocimiento del chatbot y respuestas",
                metrics={"chatbot_score": score.chatbot_helpfulness_score}
            ))
        
        return insights
    
    def get_customer_satisfaction_profile(
        self,
        customer_email: str,
        days: int = 90
    ) -> CustomerSatisfactionProfile:
        """Obtener perfil de satisfacción de un cliente."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        query = """
            SELECT 
                ticket_id,
                satisfaction_score,
                response_time_rating,
                resolution_quality_rating,
                submitted_at
            FROM support_ticket_feedback
            WHERE customer_email = %s
                AND submitted_at >= %s
            ORDER BY submitted_at DESC
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [customer_email, start_date])
            rows = cur.fetchall()
        
        if not rows:
            return CustomerSatisfactionProfile(
                customer_email=customer_email,
                average_score=0.0,
                total_tickets=0,
                satisfaction_history=[],
                sentiment_trend=SatisfactionTrend.STABLE,
                risk_level="unknown",
                recommendations=[]
            )
        
        scores = [r[1] for r in rows if r[1]]
        avg_score = statistics.mean(scores) if scores else 0.0
        
        history = [
            {
                "ticket_id": r[0],
                "satisfaction": r[1],
                "response_time": r[2],
                "quality": r[3],
                "date": r[4]
            }
            for r in rows
        ]
        
        # Calcular tendencia
        if len(scores) >= 2:
            recent = statistics.mean(scores[:len(scores)//2])
            older = statistics.mean(scores[len(scores)//2:])
            if recent > older * 1.1:
                trend = SatisfactionTrend.IMPROVING
            elif recent < older * 0.9:
                trend = SatisfactionTrend.DECLINING
            else:
                trend = SatisfactionTrend.STABLE
        else:
            trend = SatisfactionTrend.STABLE
        
        # Determinar nivel de riesgo
        if avg_score < 2.0:
            risk = "critical"
        elif avg_score < 3.0:
            risk = "high"
        elif avg_score < 4.0:
            risk = "medium"
        else:
            risk = "low"
        
        # Generar recomendaciones
        recommendations = []
        if avg_score < 3.0:
            recommendations.append("Cliente insatisfecho - Contactar proactivamente")
        if trend == SatisfactionTrend.DECLINING:
            recommendations.append("Tendencia negativa - Revisar interacciones recientes")
        if risk == "critical":
            recommendations.append("Alto riesgo de churn - Acción inmediata requerida")
        
        return CustomerSatisfactionProfile(
            customer_email=customer_email,
            average_score=avg_score,
            total_tickets=len(rows),
            satisfaction_history=history,
            sentiment_trend=trend,
            risk_level=risk,
            recommendations=recommendations
        )
    
    def get_at_risk_customers(
        self,
        threshold: float = 3.0,
        limit: int = 50
    ) -> List[CustomerSatisfactionProfile]:
        """Obtener clientes en riesgo por satisfacción."""
        query = """
            SELECT 
                customer_email,
                AVG(satisfaction_score) as avg_score,
                COUNT(*) as ticket_count
            FROM support_ticket_feedback
            WHERE submitted_at >= NOW() - INTERVAL '90 days'
            GROUP BY customer_email
            HAVING AVG(satisfaction_score) < %s
            ORDER BY avg_score ASC, ticket_count DESC
            LIMIT %s
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [threshold, limit])
            rows = cur.fetchall()
        
        profiles = []
        for row in rows:
            profile = self.get_customer_satisfaction_profile(row[0])
            profiles.append(profile)
        
        return sorted(profiles, key=lambda p: p.average_score)
    
    def generate_satisfaction_report(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """Generar reporte completo de satisfacción."""
        score = self.calculate_satisfaction_score(days=days)
        insights = self.analyze_satisfaction_insights(days=days)
        at_risk = self.get_at_risk_customers(threshold=3.0, limit=10)
        
        # Distribución de scores
        query = """
            SELECT satisfaction_score, COUNT(*)
            FROM support_ticket_feedback
            WHERE submitted_at >= NOW() - INTERVAL '%s days'
            GROUP BY satisfaction_score
            ORDER BY satisfaction_score
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [f"{days} days"])
            distribution = {str(r[0]): r[1] for r in cur.fetchall()}
        
        return {
            "period_days": days,
            "overall_score": score.overall_score,
            "component_scores": {
                "response_time": score.response_time_score,
                "resolution_quality": score.resolution_quality_score,
                "agent_helpfulness": score.agent_helpfulness_score,
                "chatbot_helpfulness": score.chatbot_helpfulness_score
            },
            "trend": score.trend.value,
            "confidence": score.confidence,
            "sample_size": score.sample_size,
            "distribution": distribution,
            "insights": [
                {
                    "type": i.insight_type,
                    "title": i.title,
                    "description": i.description,
                    "severity": i.severity,
                    "recommendation": i.recommendation
                }
                for i in insights
            ],
            "at_risk_customers": len(at_risk),
            "top_at_risk": [
                {
                    "email": p.customer_email,
                    "score": p.average_score,
                    "risk": p.risk_level
                }
                for p in at_risk[:5]
            ]
        }

