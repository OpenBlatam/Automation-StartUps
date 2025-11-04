"""
Sistema de Capacitación Automática para Agentes.

Identifica necesidades de capacitación, genera contenido,
y realiza seguimiento del progreso.
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class TrainingTopic(Enum):
    """Temas de capacitación."""
    TECHNICAL_SKILLS = "technical_skills"
    COMMUNICATION = "communication"
    PRODUCT_KNOWLEDGE = "product_knowledge"
    CUSTOMER_SERVICE = "customer_service"
    TICKET_RESOLUTION = "ticket_resolution"
    TIME_MANAGEMENT = "time_management"
    ESCALATION = "escalation"


class TrainingStatus(Enum):
    """Estado de capacitación."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


@dataclass
class TrainingNeed:
    """Necesidad de capacitación identificada."""
    agent_id: str
    topic: TrainingTopic
    priority: str
    reason: str
    evidence: List[Dict[str, Any]]
    recommended_modules: List[str]
    estimated_duration: int  # minutos


@dataclass
class TrainingModule:
    """Módulo de capacitación."""
    module_id: str
    title: str
    description: str
    topic: TrainingTopic
    content: str
    duration_minutes: int
    prerequisites: List[str]
    assessment_questions: List[Dict[str, Any]]
    created_at: datetime


@dataclass
class AgentTrainingProgress:
    """Progreso de capacitación de un agente."""
    agent_id: str
    agent_name: str
    completed_modules: int
    total_modules: int
    completion_rate: float
    current_training: Optional[str]
    next_recommended: List[str]
    skill_gaps: List[str]
    last_training_date: Optional[datetime]


class AgentTrainingManager:
    """Gestor de capacitación de agentes."""
    
    def __init__(self, db_connection):
        """Inicializar gestor."""
        self.db = db_connection
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def identify_training_needs(
        self,
        agent_id: Optional[str] = None,
        days: int = 30
    ) -> List[TrainingNeed]:
        """Identificar necesidades de capacitación."""
        needs = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Query para obtener métricas de agentes
        query = """
            SELECT 
                t.assigned_agent_id,
                t.assigned_agent_name,
                COUNT(*) as total_tickets,
                AVG(t.time_to_resolution_minutes) as avg_resolution_time,
                AVG(f.satisfaction_score) as avg_satisfaction,
                COUNT(*) FILTER (WHERE t.status = 'escalated') as escalated_count,
                COUNT(*) FILTER (WHERE t.category = 'technical') as technical_count
            FROM support_tickets t
            LEFT JOIN support_ticket_feedback f ON t.ticket_id = f.ticket_id
            WHERE t.assigned_agent_id IS NOT NULL
                AND t.created_at >= %s
        """
        params = [start_date]
        
        if agent_id:
            query += " AND t.assigned_agent_id = %s"
            params.append(agent_id)
        
        query += " GROUP BY t.assigned_agent_id, t.assigned_agent_name"
        
        with self.db.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
        
        for row in rows:
            agent_id_val, agent_name, total, avg_res, avg_sat, escalated, technical = row
            
            # Necesidad: Tiempo de resolución alto
            if avg_res and avg_res > 120:  # Más de 2 horas promedio
                needs.append(TrainingNeed(
                    agent_id=agent_id_val,
                    topic=TrainingTopic.TIME_MANAGEMENT,
                    priority="high",
                    reason=f"Tiempo promedio de resolución: {avg_res:.0f} minutos (meta: <120)",
                    evidence=[
                        {"metric": "avg_resolution_time", "value": avg_res, "threshold": 120}
                    ],
                    recommended_modules=["time_management_basics", "ticket_prioritization"],
                    estimated_duration=60
                ))
            
            # Necesidad: Satisfacción baja
            if avg_sat and avg_sat < 3.5:
                needs.append(TrainingNeed(
                    agent_id=agent_id_val,
                    topic=TrainingTopic.CUSTOMER_SERVICE,
                    priority="high",
                    reason=f"Satisfacción promedio: {avg_sat:.2f}/5.0 (meta: >3.5)",
                    evidence=[
                        {"metric": "avg_satisfaction", "value": avg_sat, "threshold": 3.5}
                    ],
                    recommended_modules=["customer_service_excellence", "communication_skills"],
                    estimated_duration=90
                ))
            
            # Necesidad: Muchas escalaciones
            if escalated and total and (escalated / total) > 0.2:  # Más del 20%
                needs.append(TrainingNeed(
                    agent_id=agent_id_val,
                    topic=TrainingTopic.ESCALATION,
                    priority="medium",
                    reason=f"Tasa de escalación: {(escalated/total)*100:.1f}% (meta: <20%)",
                    evidence=[
                        {"metric": "escalation_rate", "value": escalated/total, "threshold": 0.2}
                    ],
                    recommended_modules=["escalation_guidelines", "problem_solving"],
                    estimated_duration=45
                ))
            
            # Necesidad: Pocos tickets técnicos resueltos
            if technical and total and (technical / total) < 0.1:  # Menos del 10%
                needs.append(TrainingNeed(
                    agent_id=agent_id_val,
                    topic=TrainingTopic.TECHNICAL_SKILLS,
                    priority="medium",
                    reason="Bajo conocimiento técnico demostrado",
                    evidence=[
                        {"metric": "technical_tickets", "value": technical, "total": total}
                    ],
                    recommended_modules=["technical_fundamentals", "product_architecture"],
                    estimated_duration=120
                ))
        
        return needs
    
    def create_training_module(
        self,
        module_id: str,
        title: str,
        description: str,
        topic: TrainingTopic,
        content: str,
        duration_minutes: int,
        prerequisites: Optional[List[str]] = None,
        assessment_questions: Optional[List[Dict[str, Any]]] = None
    ) -> TrainingModule:
        """Crear módulo de capacitación."""
        module = TrainingModule(
            module_id=module_id,
            title=title,
            description=description,
            topic=topic,
            content=content,
            duration_minutes=duration_minutes,
            prerequisites=prerequisites or [],
            assessment_questions=assessment_questions or [],
            created_at=datetime.now()
        )
        
        # Guardar en base de datos (asumiendo tabla support_training_modules)
        query = """
            INSERT INTO support_training_modules (
                module_id, title, description, topic, content,
                duration_minutes, prerequisites, assessment_questions, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (module_id) DO UPDATE SET
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                content = EXCLUDED.content,
                duration_minutes = EXCLUDED.duration_minutes,
                prerequisites = EXCLUDED.prerequisites,
                assessment_questions = EXCLUDED.assessment_questions
        """
        
        import json
        with self.db.cursor() as cur:
            cur.execute(query, [
                module_id, title, description, topic.value, content,
                duration_minutes, json.dumps(prerequisites), json.dumps(assessment_questions),
                module.created_at
            ])
            self.db.commit()
        
        return module
    
    def assign_training(
        self,
        agent_id: str,
        module_id: str,
        due_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Asignar capacitación a un agente."""
        if due_date is None:
            due_date = datetime.now() + timedelta(days=7)
        
        query = """
            INSERT INTO support_agent_training (
                agent_id, module_id, status, assigned_at, due_date
            ) VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (agent_id, module_id) DO UPDATE SET
                status = 'pending',
                due_date = EXCLUDED.due_date
            RETURNING id
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [
                agent_id, module_id, TrainingStatus.PENDING.value,
                datetime.now(), due_date
            ])
            result = cur.fetchone()
            self.db.commit()
        
        return {
            "assignment_id": result[0] if result else None,
            "agent_id": agent_id,
            "module_id": module_id,
            "status": TrainingStatus.PENDING.value,
            "due_date": due_date
        }
    
    def get_agent_progress(
        self,
        agent_id: str
    ) -> AgentTrainingProgress:
        """Obtener progreso de capacitación de un agente."""
        # Obtener información del agente
        query_agent = """
            SELECT agent_name FROM support_agents WHERE agent_id = %s
        """
        
        with self.db.cursor() as cur:
            cur.execute(query_agent, [agent_id])
            agent_row = cur.fetchone()
            agent_name = agent_row[0] if agent_row else "Unknown"
        
        # Obtener módulos completados
        query_completed = """
            SELECT COUNT(*) FROM support_agent_training
            WHERE agent_id = %s AND status = 'completed'
        """
        
        with self.db.cursor() as cur:
            cur.execute(query_completed, [agent_id])
            completed = cur.fetchone()[0] or 0
        
        # Obtener total de módulos
        query_total = """
            SELECT COUNT(*) FROM support_training_modules
        """
        
        with self.db.cursor() as cur:
            cur.execute(query_total)
            total = cur.fetchone()[0] or 0
        
        # Obtener entrenamiento actual
        query_current = """
            SELECT module_id FROM support_agent_training
            WHERE agent_id = %s AND status = 'in_progress'
            ORDER BY assigned_at DESC
            LIMIT 1
        """
        
        with self.db.cursor() as cur:
            cur.execute(query_current, [agent_id])
            current_row = cur.fetchone()
            current = current_row[0] if current_row else None
        
        # Obtener última fecha de entrenamiento
        query_last = """
            SELECT completed_at FROM support_agent_training
            WHERE agent_id = %s AND status = 'completed'
            ORDER BY completed_at DESC
            LIMIT 1
        """
        
        with self.db.cursor() as cur:
            cur.execute(query_last, [agent_id])
            last_row = cur.fetchone()
            last_training = last_row[0] if last_row else None
        
        # Identificar gaps de habilidades
        needs = self.identify_training_needs(agent_id=agent_id, days=90)
        skill_gaps = [n.topic.value for n in needs]
        
        # Recomendaciones basadas en gaps
        next_recommended = []
        for need in needs[:3]:  # Top 3
            next_recommended.extend(need.recommended_modules[:1])
        
        completion_rate = (completed / total * 100) if total > 0 else 0.0
        
        return AgentTrainingProgress(
            agent_id=agent_id,
            agent_name=agent_name,
            completed_modules=completed,
            total_modules=total,
            completion_rate=completion_rate,
            current_training=current,
            next_recommended=next_recommended,
            skill_gaps=skill_gaps,
            last_training_date=last_training
        )
    
    def complete_training(
        self,
        agent_id: str,
        module_id: str,
        score: Optional[float] = None
    ) -> Dict[str, Any]:
        """Marcar capacitación como completada."""
        query = """
            UPDATE support_agent_training
            SET status = %s, completed_at = %s, score = %s
            WHERE agent_id = %s AND module_id = %s
            RETURNING id
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [
                TrainingStatus.COMPLETED.value,
                datetime.now(),
                score,
                agent_id,
                module_id
            ])
            result = cur.fetchone()
            self.db.commit()
        
        return {
            "success": result is not None,
            "agent_id": agent_id,
            "module_id": module_id,
            "completed_at": datetime.now(),
            "score": score
        }
    
    def generate_training_report(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """Generar reporte de capacitación."""
        start_date = datetime.now() - timedelta(days=days)
        
        # Estadísticas generales
        query_stats = """
            SELECT 
                COUNT(*) FILTER (WHERE status = 'completed') as completed,
                COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress,
                COUNT(*) FILTER (WHERE status = 'pending') as pending,
                AVG(score) FILTER (WHERE status = 'completed') as avg_score
            FROM support_agent_training
            WHERE assigned_at >= %s
        """
        
        with self.db.cursor() as cur:
            cur.execute(query_stats, [start_date])
            row = cur.fetchone()
            completed, in_progress, pending, avg_score = row
        
        # Necesidades identificadas
        all_needs = self.identify_training_needs(days=days)
        needs_by_topic = defaultdict(list)
        for need in all_needs:
            needs_by_topic[need.topic.value].append(need)
        
        # Top agentes que necesitan capacitación
        agents_needing_training = {}
        for need in all_needs:
            if need.agent_id not in agents_needing_training:
                agents_needing_training[need.agent_id] = []
            agents_needing_training[need.agent_id].append(need)
        
        top_agents = sorted(
            agents_needing_training.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:10]
        
        return {
            "period_days": days,
            "statistics": {
                "completed": completed or 0,
                "in_progress": in_progress or 0,
                "pending": pending or 0,
                "avg_score": float(avg_score) if avg_score else 0.0
            },
            "training_needs": {
                "total": len(all_needs),
                "by_topic": {
                    topic: len(needs) for topic, needs in needs_by_topic.items()
                },
                "high_priority": len([n for n in all_needs if n.priority == "high"])
            },
            "top_agents_needing_training": [
                {
                    "agent_id": agent_id,
                    "needs_count": len(needs),
                    "topics": list(set(n.topic.value for n in needs))
                }
                for agent_id, needs in top_agents
            ]
        }


