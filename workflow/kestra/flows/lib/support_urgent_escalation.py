"""
Módulo de Escalación Automática para Casos Urgentes.

Características:
- Detección automática de casos urgentes
- Escalación inmediata a supervisores
- Notificaciones prioritarias
- Reasignación a agentes senior
"""
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class EscalationAction:
    """Acción de escalación."""
    action_type: str  # priority_increase, reassign, supervisor_notify, etc.
    executed: bool
    details: str
    timestamp: datetime


@dataclass
class EscalationResult:
    """Resultado de escalación."""
    escalated: bool
    actions: List[EscalationAction]
    new_priority: Optional[str] = None
    new_agent_id: Optional[str] = None
    supervisor_notified: bool = False
    reason: str = ""


class SupportUrgentEscalation:
    """Manejador de escalación automática para casos urgentes."""
    
    # Umbrales de tiempo para escalación
    TIME_THRESHOLDS = {
        "critical": timedelta(minutes=15),  # 15 minutos sin respuesta
        "urgent": timedelta(minutes=30),    # 30 minutos sin respuesta
        "high": timedelta(hours=2),          # 2 horas sin respuesta
        "medium": timedelta(hours=4),       # 4 horas sin respuesta
    }
    
    # Prioridades de escalación
    PRIORITY_ESCALATION = {
        "low": "medium",
        "medium": "high",
        "high": "urgent",
        "urgent": "critical",
        "critical": "critical"  # No puede subir más
    }
    
    def __init__(self, db_connection: Any = None):
        """
        Inicializa el manejador de escalación.
        
        Args:
            db_connection: Conexión a BD
        """
        self.db_connection = db_connection
    
    def check_urgent_conditions(self, ticket_data: Dict[str, Any]) -> bool:
        """
        Verifica si un ticket cumple condiciones para escalación urgente.
        
        Args:
            ticket_data: Datos del ticket
            
        Returns:
            True si requiere escalación urgente
        """
        priority = ticket_data.get("priority", "medium")
        
        # Prioridades críticas y urgentes siempre requieren atención
        if priority in ["critical", "urgent"]:
            return True
        
        # Verificar tiempo sin respuesta
        created_at = ticket_data.get("created_at")
        first_response_at = ticket_data.get("first_response_at")
        
        if created_at and not first_response_at:
            # Calcular tiempo transcurrido
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            elif not isinstance(created_at, datetime):
                return False
            
            time_elapsed = datetime.now(created_at.tzinfo) - created_at if hasattr(created_at, 'tzinfo') else datetime.now() - created_at
            
            threshold = self.TIME_THRESHOLDS.get(priority, timedelta(hours=24))
            if time_elapsed > threshold:
                return True
        
        # Verificar si está marcado como escalado
        metadata = ticket_data.get("metadata", {})
        if isinstance(metadata, str):
            import json
            metadata = json.loads(metadata) if metadata else {}
        
        if metadata.get("requires_escalation"):
            return True
        
        return False
    
    def find_supervisor(self, department: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Encuentra un supervisor disponible.
        
        Args:
            department: Departamento específico (opcional)
            
        Returns:
            Dict con información del supervisor o None
        """
        if not self.db_connection:
            return None
        
        try:
            cursor = self.db_connection.cursor()
            
            # Buscar agentes con rol supervisor o manager
            query = """
                SELECT 
                    agent_id,
                    agent_name,
                    email,
                    department
                FROM support_agents
                WHERE is_available = true
                AND (metadata->>'role' IN ('supervisor', 'manager', 'lead') 
                     OR metadata->>'is_supervisor' = 'true')
            """
            params = []
            
            if department:
                query += " AND (department = %s OR metadata->>'departments' LIKE %s)"
                params.extend([department, f'%{department}%'])
            
            query += " LIMIT 1"
            
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            if row:
                supervisor = {
                    "agent_id": row[0],
                    "agent_name": row[1],
                    "email": row[2],
                    "department": row[3]
                }
                cursor.close()
                return supervisor
            
            cursor.close()
            return None
            
        except Exception as e:
            logger.error(f"Error buscando supervisor: {e}")
            return None
    
    def find_senior_agent(
        self,
        department: str,
        exclude_agent_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Encuentra un agente senior disponible.
        
        Args:
            department: Departamento requerido
            exclude_agent_id: ID de agente a excluir
            
        Returns:
            Dict con información del agente o None
        """
        if not self.db_connection:
            return None
        
        try:
            cursor = self.db_connection.cursor()
            
            # Buscar agente con más experiencia en el departamento
            query = """
                SELECT 
                    a.agent_id,
                    a.agent_name,
                    a.email,
                    a.department,
                    a.current_active_tickets,
                    a.max_concurrent_tickets,
                    COUNT(t.ticket_id) FILTER (WHERE t.status = 'resolved') as resolved_count,
                    AVG(t.customer_satisfaction_score) FILTER (WHERE t.status = 'resolved') as avg_satisfaction
                FROM support_agents a
                LEFT JOIN support_tickets t ON a.agent_id = t.assigned_agent_id
                WHERE a.is_available = true
                AND a.department = %s
            """
            params = [department]
            
            if exclude_agent_id:
                query += " AND a.agent_id != %s"
                params.append(exclude_agent_id)
            
            query += """
                GROUP BY a.agent_id, a.agent_name, a.email, a.department,
                         a.current_active_tickets, a.max_concurrent_tickets
                HAVING a.current_active_tickets < a.max_concurrent_tickets
                ORDER BY resolved_count DESC, avg_satisfaction DESC NULLS LAST
                LIMIT 1
            """
            
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            if row:
                agent = {
                    "agent_id": row[0],
                    "agent_name": row[1],
                    "email": row[2],
                    "department": row[3],
                    "current_load": row[4],
                    "max_load": row[5]
                }
                cursor.close()
                return agent
            
            cursor.close()
            return None
            
        except Exception as e:
            logger.error(f"Error buscando agente senior: {e}")
            return None
    
    def escalate_ticket(
        self,
        ticket_id: str,
        reason: str = "auto_urgent"
    ) -> EscalationResult:
        """
        Escala un ticket automáticamente.
        
        Args:
            ticket_id: ID del ticket
            reason: Razón de escalación
            
        Returns:
            EscalationResult con acciones aplicadas
        """
        if not self.db_connection:
            return EscalationResult(
                escalated=False,
                actions=[],
                reason="Sin conexión a BD"
            )
        
        actions = []
        
        try:
            cursor = self.db_connection.cursor()
            
            # Obtener información del ticket
            cursor.execute("""
                SELECT 
                    priority,
                    assigned_department,
                    assigned_agent_id,
                    status,
                    created_at,
                    first_response_at,
                    metadata
                FROM support_tickets
                WHERE ticket_id = %s
            """, (ticket_id,))
            
            row = cursor.fetchone()
            if not row:
                cursor.close()
                return EscalationResult(
                    escalated=False,
                    actions=[],
                    reason="Ticket no encontrado"
                )
            
            priority, department, agent_id, status, created_at, first_response_at, metadata = row
            
            ticket_data = {
                "priority": priority,
                "assigned_department": department,
                "assigned_agent_id": agent_id,
                "status": status,
                "created_at": created_at,
                "first_response_at": first_response_at,
                "metadata": metadata
            }
            
            new_priority = None
            new_agent_id = None
            supervisor_notified = False
            
            # Acción 1: Aumentar prioridad si es posible
            if priority in self.PRIORITY_ESCALATION:
                new_priority = self.PRIORITY_ESCALATION[priority]
                if new_priority != priority:
                    cursor.execute("""
                        UPDATE support_tickets
                        SET priority = %s,
                            priority_score = LEAST(100, priority_score + 15),
                            updated_at = NOW()
                        WHERE ticket_id = %s
                    """, (new_priority, ticket_id))
                    
                    actions.append(EscalationAction(
                        action_type="priority_increase",
                        executed=True,
                        details=f"Prioridad aumentada de {priority} a {new_priority}",
                        timestamp=datetime.now()
                    ))
            
            # Acción 2: Reasignar a agente senior si hay departamento
            if department and (not agent_id or reason.startswith("no_response")):
                senior_agent = self.find_senior_agent(department, agent_id)
                if senior_agent:
                    cursor.execute("""
                        UPDATE support_tickets
                        SET assigned_agent_id = %s,
                            assigned_agent_name = %s,
                            status = CASE WHEN status = 'open' THEN 'assigned' ELSE status END,
                            updated_at = NOW()
                        WHERE ticket_id = %s
                    """, (
                        senior_agent["agent_id"],
                        senior_agent["agent_name"],
                        ticket_id
                    ))
                    
                    new_agent_id = senior_agent["agent_id"]
                    actions.append(EscalationAction(
                        action_type="reassign_senior",
                        executed=True,
                        details=f"Reasignado a agente senior: {senior_agent['agent_name']}",
                        timestamp=datetime.now()
                    ))
            
            # Acción 3: Notificar supervisor
            supervisor = self.find_supervisor(department)
            if supervisor:
                # Marcar en metadata que supervisor fue notificado
                # (la notificación real se enviará por el sistema de notificaciones)
                cursor.execute("""
                    UPDATE support_tickets
                    SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                        jsonb_build_object(
                            'supervisor_notified', true,
                            'supervisor_id', %s,
                            'supervisor_notified_at', NOW()
                        ),
                        updated_at = NOW()
                    WHERE ticket_id = %s
                """, (supervisor["agent_id"], ticket_id))
                
                supervisor_notified = True
                actions.append(EscalationAction(
                    action_type="supervisor_notify",
                    executed=True,
                    details=f"Supervisor notificado: {supervisor['agent_name']}",
                    timestamp=datetime.now()
                ))
            
            # Acción 4: Marcar como escalado
            cursor.execute("""
                UPDATE support_tickets
                SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                    jsonb_build_object(
                        'escalated', true,
                        'escalation_reason', %s,
                        'escalated_at', NOW(),
                        'escalation_count', COALESCE((metadata->>'escalation_count')::int, 0) + 1
                    ),
                    status = CASE 
                        WHEN status = 'open' THEN 'escalated'
                        WHEN status = 'assigned' THEN 'escalated'
                        ELSE status
                    END,
                    updated_at = NOW()
                WHERE ticket_id = %s
            """, (reason, ticket_id))
            
            # Registrar en historial
            cursor.execute("""
                INSERT INTO support_ticket_history (
                    ticket_id,
                    field_changed,
                    old_value,
                    new_value,
                    changed_by,
                    change_reason
                ) VALUES (
                    %s,
                    'escalation',
                    %s,
                    'escalated',
                    'system',
                    %s
                )
            """, (ticket_id, priority, f"Escalación automática: {reason}"))
            
            self.db_connection.commit()
            cursor.close()
            
            return EscalationResult(
                escalated=True,
                actions=actions,
                new_priority=new_priority or priority,
                new_agent_id=new_agent_id,
                supervisor_notified=supervisor_notified,
                reason=reason
            )
            
        except Exception as e:
            logger.error(f"Error escalando ticket {ticket_id}: {e}", exc_info=True)
            if self.db_connection:
                self.db_connection.rollback()
            return EscalationResult(
                escalated=False,
                actions=[EscalationAction(
                    action_type="error",
                    executed=False,
                    details=f"Error: {str(e)}",
                    timestamp=datetime.now()
                )],
                reason=f"Error: {str(e)}"
            )
    
    def auto_escalate_urgent_tickets(self) -> List[EscalationResult]:
        """
        Escala automáticamente todos los tickets urgentes que lo requieran.
        
        Returns:
            Lista de resultados de escalación
        """
        if not self.db_connection:
            return []
        
        results = []
        
        try:
            cursor = self.db_connection.cursor()
            
            # Buscar tickets que requieren escalación
            cursor.execute("""
                SELECT 
                    ticket_id,
                    priority,
                    assigned_department,
                    assigned_agent_id,
                    status,
                    created_at,
                    first_response_at,
                    metadata
                FROM support_tickets
                WHERE status IN ('open', 'assigned', 'in_progress')
                AND priority IN ('urgent', 'critical')
                AND (
                    (metadata->>'escalated')::boolean IS NOT TRUE
                    OR (metadata->>'escalated')::boolean = false
                )
            """)
            
            for row in cursor.fetchall():
                ticket_id, priority, dept, agent_id, status, created_at, first_response_at, metadata = row
                
                ticket_data = {
                    "priority": priority,
                    "assigned_department": dept,
                    "assigned_agent_id": agent_id,
                    "status": status,
                    "created_at": created_at,
                    "first_response_at": first_response_at,
                    "metadata": metadata
                }
                
                # Verificar si requiere escalación
                if self.check_urgent_conditions(ticket_data):
                    result = self.escalate_ticket(ticket_id, "auto_urgent")
                    results.append(result)
            
            cursor.close()
            return results
            
        except Exception as e:
            logger.error(f"Error en auto-escalación: {e}")
            return results

