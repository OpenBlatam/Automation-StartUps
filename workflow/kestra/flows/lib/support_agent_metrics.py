"""
Sistema de Métricas de Agentes Avanzado.

Análisis profundo de rendimiento, productividad,
y métricas de agentes individuales y equipos.
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class PerformanceLevel(Enum):
    """Niveles de rendimiento."""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    BELOW_AVERAGE = "below_average"
    NEEDS_IMPROVEMENT = "needs_improvement"


@dataclass
class AgentMetrics:
    """Métricas de un agente."""
    agent_id: str
    agent_name: str
    period_start: datetime
    period_end: datetime
    
    # Volumen
    tickets_assigned: int
    tickets_resolved: int
    tickets_escalated: int
    resolution_rate: float
    
    # Tiempos
    avg_response_time_minutes: float
    avg_resolution_time_minutes: float
    avg_first_response_minutes: float
    
    # Calidad
    avg_satisfaction_score: float
    positive_feedback_count: int
    negative_feedback_count: int
    
    # Eficiencia
    tickets_per_day: float
    avg_handling_time_minutes: float
    
    # Performance
    performance_level: PerformanceLevel
    performance_score: float  # 0-100


@dataclass
class TeamMetrics:
    """Métricas de equipo."""
    team_name: str
    period_start: datetime
    period_end: datetime
    total_agents: int
    active_agents: int
    total_tickets: int
    total_resolved: int
    avg_resolution_time: float
    avg_satisfaction: float
    team_performance_score: float
    top_performers: List[Dict[str, Any]]
    agents_needing_support: List[Dict[str, Any]]


class AgentMetricsAnalyzer:
    """Analizador de métricas de agentes."""
    
    def __init__(self, db_connection):
        """Inicializar analizador."""
        self.db = db_connection
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def calculate_agent_metrics(
        self,
        agent_id: str,
        days: int = 30
    ) -> AgentMetrics:
        """Calcular métricas de un agente."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Query principal de métricas
        query = """
            SELECT 
                t.assigned_agent_id,
                t.assigned_agent_name,
                COUNT(*) as total_assigned,
                COUNT(*) FILTER (WHERE t.status = 'resolved') as resolved,
                COUNT(*) FILTER (WHERE t.status = 'escalated') as escalated,
                AVG(t.time_to_first_response_minutes) as avg_first_response,
                AVG(t.time_to_resolution_minutes) as avg_resolution,
                AVG(f.satisfaction_score) as avg_satisfaction,
                COUNT(*) FILTER (WHERE f.satisfaction_score >= 4) as positive_feedback,
                COUNT(*) FILTER (WHERE f.satisfaction_score <= 2) as negative_feedback
            FROM support_tickets t
            LEFT JOIN support_ticket_feedback f ON t.ticket_id = f.ticket_id
            WHERE t.assigned_agent_id = %s
                AND t.created_at >= %s
            GROUP BY t.assigned_agent_id, t.assigned_agent_name
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [agent_id, start_date])
            row = cur.fetchone()
        
        if not row:
            return AgentMetrics(
                agent_id=agent_id,
                agent_name="Unknown",
                period_start=start_date,
                period_end=end_date,
                tickets_assigned=0,
                tickets_resolved=0,
                tickets_escalated=0,
                resolution_rate=0.0,
                avg_response_time_minutes=0.0,
                avg_resolution_time_minutes=0.0,
                avg_first_response_minutes=0.0,
                avg_satisfaction_score=0.0,
                positive_feedback_count=0,
                negative_feedback_count=0,
                tickets_per_day=0.0,
                avg_handling_time_minutes=0.0,
                performance_level=PerformanceLevel.NEEDS_IMPROVEMENT,
                performance_score=0.0
            )
        
        agent_id_val, agent_name, total, resolved, escalated, avg_first, avg_res, \
            avg_sat, positive, negative = row
        
        resolution_rate = (resolved / total * 100) if total > 0 else 0.0
        tickets_per_day = total / days if days > 0 else 0.0
        
        # Calcular tiempo de manejo promedio
        avg_handling = avg_res if avg_res else 0.0
        
        # Calcular performance score (0-100)
        performance_score = self._calculate_performance_score(
            resolution_rate=resolution_rate,
            avg_resolution=avg_res or 0,
            avg_satisfaction=avg_sat or 0,
            positive_feedback=positive or 0,
            negative_feedback=negative or 0,
            total=total
        )
        
        # Determinar nivel de performance
        if performance_score >= 90:
            level = PerformanceLevel.EXCELLENT
        elif performance_score >= 75:
            level = PerformanceLevel.GOOD
        elif performance_score >= 60:
            level = PerformanceLevel.AVERAGE
        elif performance_score >= 45:
            level = PerformanceLevel.BELOW_AVERAGE
        else:
            level = PerformanceLevel.NEEDS_IMPROVEMENT
        
        return AgentMetrics(
            agent_id=agent_id_val,
            agent_name=agent_name or "Unknown",
            period_start=start_date,
            period_end=end_date,
            tickets_assigned=total or 0,
            tickets_resolved=resolved or 0,
            tickets_escalated=escalated or 0,
            resolution_rate=resolution_rate,
            avg_response_time_minutes=0.0,  # Calcular separadamente si existe
            avg_resolution_time_minutes=avg_res or 0.0,
            avg_first_response_minutes=avg_first or 0.0,
            avg_satisfaction_score=avg_sat or 0.0,
            positive_feedback_count=positive or 0,
            negative_feedback_count=negative or 0,
            tickets_per_day=tickets_per_day,
            avg_handling_time_minutes=avg_handling,
            performance_level=level,
            performance_score=performance_score
        )
    
    def _calculate_performance_score(
        self,
        resolution_rate: float,
        avg_resolution: float,
        avg_satisfaction: float,
        positive_feedback: int,
        negative_feedback: int,
        total: int
    ) -> float:
        """Calcular score de performance (0-100)."""
        score = 0.0
        
        # Resolución (30 puntos)
        if resolution_rate >= 90:
            score += 30
        elif resolution_rate >= 75:
            score += 25
        elif resolution_rate >= 60:
            score += 20
        elif resolution_rate >= 50:
            score += 15
        else:
            score += 10
        
        # Tiempo de resolución (25 puntos)
        if avg_resolution <= 60:  # Menos de 1 hora
            score += 25
        elif avg_resolution <= 120:  # Menos de 2 horas
            score += 20
        elif avg_resolution <= 240:  # Menos de 4 horas
            score += 15
        elif avg_resolution <= 480:  # Menos de 8 horas
            score += 10
        else:
            score += 5
        
        # Satisfacción (25 puntos)
        if avg_satisfaction >= 4.5:
            score += 25
        elif avg_satisfaction >= 4.0:
            score += 20
        elif avg_satisfaction >= 3.5:
            score += 15
        elif avg_satisfaction >= 3.0:
            score += 10
        else:
            score += 5
        
        # Feedback positivo (10 puntos)
        if total > 0:
            positive_ratio = positive_feedback / total
            if positive_ratio >= 0.8:
                score += 10
            elif positive_ratio >= 0.6:
                score += 8
            elif positive_ratio >= 0.4:
                score += 5
            else:
                score += 2
        
        # Feedback negativo (10 puntos, inverso)
        if total > 0:
            negative_ratio = negative_feedback / total
            if negative_ratio <= 0.1:
                score += 10
            elif negative_ratio <= 0.2:
                score += 8
            elif negative_ratio <= 0.3:
                score += 5
            else:
                score += 2
        
        return min(100.0, score)
    
    def get_team_metrics(
        self,
        department: Optional[str] = None,
        days: int = 30
    ) -> TeamMetrics:
        """Obtener métricas de equipo."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        query = """
            SELECT 
                a.department,
                COUNT(DISTINCT a.agent_id) as total_agents,
                COUNT(DISTINCT a.agent_id) FILTER (WHERE a.is_available = true) as active_agents,
                COUNT(t.ticket_id) as total_tickets,
                COUNT(t.ticket_id) FILTER (WHERE t.status = 'resolved') as resolved,
                AVG(t.time_to_resolution_minutes) as avg_resolution,
                AVG(f.satisfaction_score) as avg_satisfaction
            FROM support_agents a
            LEFT JOIN support_tickets t ON a.agent_id = t.assigned_agent_id
                AND t.created_at >= %s
            LEFT JOIN support_ticket_feedback f ON t.ticket_id = f.ticket_id
        """
        params = [start_date]
        
        if department:
            query += " WHERE a.department = %s"
            params.append(department)
        
        query += " GROUP BY a.department"
        
        with self.db.cursor() as cur:
            cur.execute(query, params)
            row = cur.fetchone()
        
        if not row:
            return TeamMetrics(
                team_name=department or "All Teams",
                period_start=start_date,
                period_end=end_date,
                total_agents=0,
                active_agents=0,
                total_tickets=0,
                total_resolved=0,
                avg_resolution_time=0.0,
                avg_satisfaction=0.0,
                team_performance_score=0.0,
                top_performers=[],
                agents_needing_support=[]
            )
        
        dept, total_agents, active, total, resolved, avg_res, avg_sat = row
        
        # Obtener métricas individuales para top performers
        agents_query = """
            SELECT DISTINCT assigned_agent_id
            FROM support_tickets
            WHERE assigned_agent_id IS NOT NULL
                AND created_at >= %s
        """
        if department:
            agents_query += """
                AND assigned_agent_id IN (
                    SELECT agent_id FROM support_agents WHERE department = %s
                )
            """
        
        with self.db.cursor() as cur:
            cur.execute(agents_query, params[:1] if not department else params)
            agent_ids = [r[0] for r in cur.fetchall()]
        
        agent_metrics = []
        for agent_id in agent_ids:
            metrics = self.calculate_agent_metrics(agent_id, days=days)
            agent_metrics.append(metrics)
        
        # Top performers (top 5)
        top_performers = sorted(
            agent_metrics,
            key=lambda m: m.performance_score,
            reverse=True
        )[:5]
        
        # Agentes que necesitan apoyo (bottom 5)
        needing_support = sorted(
            agent_metrics,
            key=lambda m: m.performance_score
        )[:5]
        
        # Calcular score del equipo
        if agent_metrics:
            team_score = statistics.mean([m.performance_score for m in agent_metrics])
        else:
            team_score = 0.0
        
        return TeamMetrics(
            team_name=dept or "All Teams",
            period_start=start_date,
            period_end=end_date,
            total_agents=total_agents or 0,
            active_agents=active or 0,
            total_tickets=total or 0,
            total_resolved=resolved or 0,
            avg_resolution_time=avg_res or 0.0,
            avg_satisfaction=avg_sat or 0.0,
            team_performance_score=team_score,
            top_performers=[
                {
                    "agent_id": m.agent_id,
                    "agent_name": m.agent_name,
                    "score": m.performance_score,
                    "level": m.performance_level.value
                }
                for m in top_performers
            ],
            agents_needing_support=[
                {
                    "agent_id": m.agent_id,
                    "agent_name": m.agent_name,
                    "score": m.performance_score,
                    "level": m.performance_level.value,
                    "issues": [
                        "Resolución baja" if m.resolution_rate < 60 else None,
                        "Satisfacción baja" if m.avg_satisfaction_score < 3.5 else None,
                        "Tiempo alto" if m.avg_resolution_time_minutes > 240 else None
                    ]
                }
                for m in needing_support
            ]
        )
    
    def generate_agent_report(
        self,
        agent_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Generar reporte completo de un agente."""
        metrics = self.calculate_agent_metrics(agent_id, days=days)
        
        # Comparar con promedio del equipo
        team_metrics = self.get_team_metrics(days=days)
        
        # Tendencias (comparar con período anterior)
        prev_metrics = self.calculate_agent_metrics(agent_id, days=days*2)
        prev_metrics.period_start = prev_metrics.period_end - timedelta(days=days)
        prev_metrics.period_end = metrics.period_start
        
        trends = {
            "resolution_rate": "improving" if metrics.resolution_rate > prev_metrics.resolution_rate else "declining",
            "satisfaction": "improving" if metrics.avg_satisfaction_score > prev_metrics.avg_satisfaction_score else "declining",
            "resolution_time": "improving" if metrics.avg_resolution_time_minutes < prev_metrics.avg_resolution_time_minutes else "declining"
        }
        
        return {
            "agent_id": metrics.agent_id,
            "agent_name": metrics.agent_name,
            "period": {
                "start": metrics.period_start.isoformat(),
                "end": metrics.period_end.isoformat(),
                "days": days
            },
            "metrics": {
                "volume": {
                    "assigned": metrics.tickets_assigned,
                    "resolved": metrics.tickets_resolved,
                    "escalated": metrics.tickets_escalated,
                    "resolution_rate": metrics.resolution_rate
                },
                "timing": {
                    "avg_first_response_minutes": metrics.avg_first_response_minutes,
                    "avg_resolution_minutes": metrics.avg_resolution_time_minutes,
                    "avg_handling_minutes": metrics.avg_handling_time_minutes,
                    "tickets_per_day": metrics.tickets_per_day
                },
                "quality": {
                    "avg_satisfaction": metrics.avg_satisfaction_score,
                    "positive_feedback": metrics.positive_feedback_count,
                    "negative_feedback": metrics.negative_feedback_count
                }
            },
            "performance": {
                "score": metrics.performance_score,
                "level": metrics.performance_level.value,
                "vs_team_average": metrics.performance_score - team_metrics.team_performance_score
            },
            "trends": trends,
            "recommendations": self._generate_recommendations(metrics, team_metrics)
        }
    
    def _generate_recommendations(
        self,
        metrics: AgentMetrics,
        team_metrics: TeamMetrics
    ) -> List[str]:
        """Generar recomendaciones para el agente."""
        recommendations = []
        
        if metrics.resolution_rate < 60:
            recommendations.append(
                f"Mejorar tasa de resolución ({metrics.resolution_rate:.1f}% vs promedio {team_metrics.team_performance_score:.1f}%)"
            )
        
        if metrics.avg_satisfaction_score < 3.5:
            recommendations.append(
                f"Mejorar satisfacción del cliente ({metrics.avg_satisfaction_score:.2f}/5.0)"
            )
        
        if metrics.avg_resolution_time_minutes > 240:
            recommendations.append(
                f"Reducir tiempo de resolución ({metrics.avg_resolution_time_minutes:.0f} min vs objetivo <240 min)"
            )
        
        if metrics.performance_level == PerformanceLevel.NEEDS_IMPROVEMENT:
            recommendations.append("Capacitación adicional recomendada")
        
        if not recommendations:
            recommendations.append("¡Excelente rendimiento! Mantener el nivel actual")
        
        return recommendations
    
    def get_leaderboard(
        self,
        department: Optional[str] = None,
        days: int = 30,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Obtener leaderboard de agentes."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        query = """
            SELECT DISTINCT assigned_agent_id
            FROM support_tickets
            WHERE assigned_agent_id IS NOT NULL
                AND created_at >= %s
        """
        params = [start_date]
        
        if department:
            query += """
                AND assigned_agent_id IN (
                    SELECT agent_id FROM support_agents WHERE department = %s
                )
            """
            params.append(department)
        
        with self.db.cursor() as cur:
            cur.execute(query, params)
            agent_ids = [r[0] for r in cur.fetchall()]
        
        leaderboard = []
        for agent_id in agent_ids:
            metrics = self.calculate_agent_metrics(agent_id, days=days)
            leaderboard.append({
                "agent_id": metrics.agent_id,
                "agent_name": metrics.agent_name,
                "performance_score": metrics.performance_score,
                "performance_level": metrics.performance_level.value,
                "tickets_resolved": metrics.tickets_resolved,
                "resolution_rate": metrics.resolution_rate,
                "avg_satisfaction": metrics.avg_satisfaction_score
            })
        
        return sorted(
            leaderboard,
            key=lambda x: x["performance_score"],
            reverse=True
        )[:limit]


