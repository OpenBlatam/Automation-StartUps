"""
Módulo de Escalación Automática de Tickets.

Características:
- Escalación basada en tiempo sin respuesta
- Reasignación a agentes senior
- Aumento de prioridad
- Notificaciones a supervisores
"""
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EscalationResult:
    """Resultado de una escalación."""
    escalated: bool
    actions: List[str]
    new_priority: Optional[str] = None
    new_agent_id: Optional[str] = None
    supervisor_notified: bool = False


class SupportEscalation:
    """Manejador de escalación de tickets."""
    
    # Mapeo de prioridades para escalación
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
            
            # Buscar agentes con menos carga y más experiencia (asumimos que agentes con más tickets resueltos son más senior)
            query = """
                SELECT 
                    a.agent_id,
                    a.agent_name,
                    a.email,
                    a.department,
                    a.current_active_tickets,
                    a.max_concurrent_tickets,
                    COUNT(t.ticket_id) FILTER (WHERE t.status = 'resolved') as resolved_tickets
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
                ORDER BY resolved_tickets DESC, a.current_active_tickets ASC
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
                    "current_active_tickets": row[4],
                    "max_concurrent_tickets": row[5]
                }
                cursor.close()
                return agent
            
            cursor.close()
            return None
            
        except Exception as e:
            logger.error(f"Error buscando agente senior: {e}", exc_info=True)
            return None
    
    def escalate_ticket(
        self,
        ticket_id: str,
        reason: str,
        priority: str,
        current_agent_id: Optional[str] = None
    ) -> EscalationResult:
        """
        Escala un ticket.
        
        Args:
            ticket_id: ID del ticket
            reason: Razón de escalación
            priority: Prioridad actual
            current_agent_id: ID del agente actual
            
        Returns:
            EscalationResult con acciones aplicadas
        """
        actions = []
        new_priority = None
        new_agent_id = None
        
        # Obtener información del ticket
        if not self.db_connection:
            return EscalationResult(
                escalated=False,
                actions=["No hay conexión a BD"]
            )
        
        try:
            cursor = self.db_connection.cursor()
            
            # Obtener información del ticket
            cursor.execute("""
                SELECT 
                    assigned_department,
                    priority,
                    status
                FROM support_tickets
                WHERE ticket_id = %s
            """, (ticket_id,))
            
            row = cursor.fetchone()
            if not row:
                cursor.close()
                return EscalationResult(
                    escalated=False,
                    actions=["Ticket no encontrado"]
                )
            
            department, current_priority, status = row
            
            # Acción 1: Aumentar prioridad si es posible
            if current_priority in self.PRIORITY_ESCALATION:
                new_priority = self.PRIORITY_ESCALATION[current_priority]
                if new_priority != current_priority:
                    cursor.execute("""
                        UPDATE support_tickets
                        SET priority = %s,
                            priority_score = priority_score + 10,
                            updated_at = NOW()
                        WHERE ticket_id = %s
                    """, (new_priority, ticket_id))
                    actions.append(f"Prioridad aumentada de {current_priority} a {new_priority}")
            
            # Acción 2: Reasignar a agente senior si hay departamento
            if department and (reason.startswith("no_response") or reason.startswith("stale")):
                senior_agent = self.find_senior_agent(department, current_agent_id)
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
                    actions.append(f"Reasignado a agente senior: {senior_agent['agent_name']}")
            
            # Acción 3: Marcar como escalado en metadata
            cursor.execute("""
                UPDATE support_tickets
                SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                    jsonb_build_object(
                        'escalated', true,
                        'escalation_reason', %s,
                        'escalated_at', NOW()
                    ),
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
            """, (ticket_id, current_priority, f"Escalación automática: {reason}"))
            
            self.db_connection.commit()
            cursor.close()
            
            if actions:
                return EscalationResult(
                    escalated=True,
                    actions=actions,
                    new_priority=new_priority or priority,
                    new_agent_id=new_agent_id
                )
            else:
                return EscalationResult(
                    escalated=False,
                    actions=["No se aplicaron acciones de escalación"]
                )
            
        except Exception as e:
            logger.error(f"Error escalando ticket {ticket_id}: {e}", exc_info=True)
            if self.db_connection:
                self.db_connection.rollback()
            return EscalationResult(
                escalated=False,
                actions=[f"Error: {str(e)}"]
            )

