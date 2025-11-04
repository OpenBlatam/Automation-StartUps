"""
Sistema de Resolución Proactiva.

Identifica problemas potenciales antes de que se conviertan en tickets
y genera acciones preventivas.
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class ProactiveActionType(Enum):
    """Tipos de acciones proactivas."""
    PREVENTIVE_OUTREACH = "preventive_outreach"
    KNOWLEDGE_BASE_UPDATE = "knowledge_base_update"
    PRODUCT_IMPROVEMENT = "product_improvement"
    TRAINING_NEEDED = "training_needed"
    SYSTEM_ALERT = "system_alert"
    CUSTOMER_EDUCATION = "customer_education"


class ActionPriority(Enum):
    """Prioridad de acción."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ProactiveAction:
    """Acción proactiva identificada."""
    action_id: str
    action_type: ProactiveActionType
    priority: ActionPriority
    title: str
    description: str
    target_audience: List[str]  # Emails de clientes afectados
    predicted_impact: str
    estimated_effort: str
    recommended_action: str
    related_tickets: List[str]
    confidence: float
    created_at: datetime


class ProactiveResolutionEngine:
    """Motor de resolución proactiva."""
    
    def __init__(self, db_connection):
        """Inicializar motor."""
        self.db = db_connection
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def identify_proactive_actions(
        self,
        days_back: int = 30
    ) -> List[ProactiveAction]:
        """Identificar acciones proactivas."""
        actions = []
        
        # 1. Patrones de tickets recurrentes
        actions.extend(self._detect_recurring_patterns(days_back))
        
        # 2. Clientes con múltiples tickets similares
        actions.extend(self._detect_customer_patterns(days_back))
        
        # 3. Categorías con alto volumen
        actions.extend(self._detect_high_volume_categories(days_back))
        
        # 4. Problemas de satisfacción
        actions.extend(self._detect_satisfaction_issues(days_back))
        
        # 5. Gaps en conocimiento
        actions.extend(self._detect_knowledge_gaps(days_back))
        
        return sorted(actions, key=lambda a: (
            ["critical", "high", "medium", "low"].index(a.priority.value),
            -a.confidence
        ))
    
    def _detect_recurring_patterns(
        self,
        days_back: int
    ) -> List[ProactiveAction]:
        """Detectar patrones recurrentes."""
        start_date = datetime.now() - timedelta(days=days_back)
        
        query = """
            SELECT 
                category,
                subcategory,
                COUNT(*) as ticket_count,
                COUNT(DISTINCT customer_email) as affected_customers,
                ARRAY_AGG(DISTINCT customer_email) as customers
            FROM support_tickets
            WHERE created_at >= %s
                AND category IS NOT NULL
            GROUP BY category, subcategory
            HAVING COUNT(*) >= 5
            ORDER BY ticket_count DESC
            LIMIT 10
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [start_date])
            rows = cur.fetchall()
        
        actions = []
        for row in rows:
            category, subcategory, count, customers_count, customers = row
            
            if count >= 10:
                priority = ActionPriority.CRITICAL
            elif count >= 7:
                priority = ActionPriority.HIGH
            else:
                priority = ActionPriority.MEDIUM
            
            actions.append(ProactiveAction(
                action_id=f"recurring_{category}_{subcategory}",
                action_type=ProactiveActionType.KNOWLEDGE_BASE_UPDATE,
                priority=priority,
                title=f"Patrón Recurrente: {category}/{subcategory}",
                description=f"{count} tickets similares en los últimos {days_back} días",
                target_audience=list(customers)[:10],  # Limitar
                predicted_impact=f"Reducir {count} tickets potenciales",
                estimated_effort="2-4 horas",
                recommended_action=f"Crear FAQ/guía para {category}/{subcategory}",
                related_tickets=[],
                confidence=min(0.9, count / 10.0),
                created_at=datetime.now()
            ))
        
        return actions
    
    def _detect_customer_patterns(
        self,
        days_back: int
    ) -> List[ProactiveAction]:
        """Detectar patrones por cliente."""
        start_date = datetime.now() - timedelta(days=days_back)
        
        query = """
            SELECT 
                customer_email,
                COUNT(*) as ticket_count,
                COUNT(DISTINCT category) as category_count,
                ARRAY_AGG(ticket_id) as ticket_ids
            FROM support_tickets
            WHERE created_at >= %s
            GROUP BY customer_email
            HAVING COUNT(*) >= 3
            ORDER BY ticket_count DESC
            LIMIT 20
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [start_date])
            rows = cur.fetchall()
        
        actions = []
        for row in rows:
            email, count, category_count, ticket_ids = row
            
            if count >= 5:
                priority = ActionPriority.HIGH
            else:
                priority = ActionPriority.MEDIUM
            
            actions.append(ProactiveAction(
                action_id=f"customer_{email.replace('@', '_at_')}",
                action_type=ProactiveActionType.PREVENTIVE_OUTREACH,
                priority=priority,
                title=f"Cliente con Múltiples Tickets: {email}",
                description=f"{count} tickets en {category_count} categorías",
                target_audience=[email],
                predicted_impact=f"Reducir tickets futuros para {email}",
                estimated_effort="1 hora",
                recommended_action=f"Contactar a {email} para capacitación/onboarding",
                related_tickets=list(ticket_ids)[:5],
                confidence=min(0.8, count / 5.0),
                created_at=datetime.now()
            ))
        
        return actions
    
    def _detect_high_volume_categories(
        self,
        days_back: int
    ) -> List[ProactiveAction]:
        """Detectar categorías con alto volumen."""
        start_date = datetime.now() - timedelta(days=days_back)
        
        query = """
            SELECT 
                category,
                COUNT(*) as ticket_count,
                AVG(time_to_resolution_minutes) as avg_resolution,
                COUNT(DISTINCT customer_email) as affected_customers
            FROM support_tickets
            WHERE created_at >= %s
                AND category IS NOT NULL
            GROUP BY category
            HAVING COUNT(*) >= 10
            ORDER BY ticket_count DESC
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [start_date])
            rows = cur.fetchall()
        
        actions = []
        for row in rows:
            category, count, avg_res, customers = row
            
            if count >= 20:
                priority = ActionPriority.CRITICAL
            elif count >= 15:
                priority = ActionPriority.HIGH
            else:
                priority = ActionPriority.MEDIUM
            
            actions.append(ProactiveAction(
                action_id=f"volume_{category}",
                action_type=ProactiveActionType.PRODUCT_IMPROVEMENT,
                priority=priority,
                title=f"Alto Volumen en Categoría: {category}",
                description=f"{count} tickets, {customers} clientes afectados",
                target_audience=[],
                predicted_impact=f"Reducir volumen en {category}",
                estimated_effort="4-8 horas",
                recommended_action=f"Investigar causas raíz en {category} y proponer mejoras",
                related_tickets=[],
                confidence=min(0.85, count / 20.0),
                created_at=datetime.now()
            ))
        
        return actions
    
    def _detect_satisfaction_issues(
        self,
        days_back: int
    ) -> List[ProactiveAction]:
        """Detectar problemas de satisfacción."""
        start_date = datetime.now() - timedelta(days=days_back)
        
        query = """
            SELECT 
                t.category,
                AVG(f.satisfaction_score) as avg_satisfaction,
                COUNT(*) as feedback_count
            FROM support_tickets t
            JOIN support_ticket_feedback f ON t.ticket_id = f.ticket_id
            WHERE t.created_at >= %s
                AND t.category IS NOT NULL
            GROUP BY t.category
            HAVING AVG(f.satisfaction_score) < 3.5
            ORDER BY avg_satisfaction ASC
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [start_date])
            rows = cur.fetchall()
        
        actions = []
        for row in rows:
            category, avg_sat, feedback_count = row
            
            if avg_sat < 3.0:
                priority = ActionPriority.CRITICAL
            else:
                priority = ActionPriority.HIGH
            
            actions.append(ProactiveAction(
                action_id=f"satisfaction_{category}",
                action_type=ProactiveActionType.TRAINING_NEEDED,
                priority=priority,
                title=f"Satisfacción Baja en {category}",
                description=f"Satisfacción promedio: {avg_sat:.2f}/5.0 ({feedback_count} respuestas)",
                target_audience=[],
                predicted_impact=f"Mejorar satisfacción en {category}",
                estimated_effort="2-4 horas",
                recommended_action=f"Revisar procesos y capacitación para {category}",
                related_tickets=[],
                confidence=0.8 if feedback_count >= 5 else 0.5,
                created_at=datetime.now()
            ))
        
        return actions
    
    def _detect_knowledge_gaps(
        self,
        days_back: int
    ) -> List[ProactiveAction]:
        """Detectar gaps en conocimiento."""
        start_date = datetime.now() - timedelta(days=days_back)
        
        query = """
            SELECT 
                category,
                COUNT(*) FILTER (WHERE chatbot_resolved = false AND faq_matched = false) as unresolved_count,
                COUNT(*) as total_tickets
            FROM support_tickets
            WHERE created_at >= %s
                AND category IS NOT NULL
            GROUP BY category
            HAVING COUNT(*) >= 5
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [start_date])
            rows = cur.fetchall()
        
        actions = []
        for row in rows:
            category, unresolved, total = row
            
            unresolved_ratio = unresolved / total if total > 0 else 0
            
            if unresolved_ratio > 0.5:
                priority = ActionPriority.HIGH
            elif unresolved_ratio > 0.3:
                priority = ActionPriority.MEDIUM
            else:
                continue
            
            actions.append(ProactiveAction(
                action_id=f"knowledge_{category}",
                action_type=ProactiveActionType.KNOWLEDGE_BASE_UPDATE,
                priority=priority,
                title=f"Gap de Conocimiento en {category}",
                description=f"{unresolved}/{total} tickets no resueltos por chatbot/FAQ",
                target_audience=[],
                predicted_impact=f"Mejorar resolución automática en {category}",
                estimated_effort="3-6 horas",
                recommended_action=f"Agregar contenido a knowledge base para {category}",
                related_tickets=[],
                confidence=unresolved_ratio,
                created_at=datetime.now()
            ))
        
        return actions
    
    def execute_action(
        self,
        action_id: str,
        executed_by: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ejecutar acción proactiva."""
        # Registrar ejecución
        query = """
            INSERT INTO support_proactive_actions (
                action_id, executed_by, executed_at, notes, status
            ) VALUES (%s, %s, %s, %s, 'completed')
            ON CONFLICT (action_id) DO UPDATE SET
                executed_by = EXCLUDED.executed_by,
                executed_at = EXCLUDED.executed_at,
                notes = EXCLUDED.notes,
                status = 'completed'
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [
                action_id, executed_by, datetime.now(), notes
            ])
            self.db.commit()
        
        return {
            "success": True,
            "action_id": action_id,
            "executed_by": executed_by,
            "executed_at": datetime.now()
        }
    
    def generate_proactive_report(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """Generar reporte de acciones proactivas."""
        actions = self.identify_proactive_actions(days_back=days)
        
        by_type = {}
        by_priority = {}
        
        for action in actions:
            type_key = action.action_type.value
            if type_key not in by_type:
                by_type[type_key] = []
            by_type[type_key].append(action)
            
            priority_key = action.priority.value
            if priority_key not in by_priority:
                by_priority[priority_key] = 0
            by_priority[priority_key] += 1
        
        return {
            "period_days": days,
            "total_actions": len(actions),
            "by_type": {
                k: len(v) for k, v in by_type.items()
            },
            "by_priority": by_priority,
            "top_actions": [
                {
                    "action_id": a.action_id,
                    "title": a.title,
                    "type": a.action_type.value,
                    "priority": a.priority.value,
                    "confidence": a.confidence
                }
                for a in actions[:10]
            ]
        }


