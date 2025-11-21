"""
Sistema de Colaboración entre Agentes.

Permite que múltiples agentes colaboren en tickets complejos.
"""
import logging
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class CollaborationType(Enum):
    """Tipos de colaboración."""
    HANDOFF = "handoff"  # Transferencia de ticket
    ASSISTANCE = "assistance"  # Asistencia temporal
    CONSULTATION = "consultation"  # Consulta/opinión
    PAIR = "pair"  # Trabajo en pareja


class CollaborationStatus(Enum):
    """Estado de colaboración."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class CollaborationRequest:
    """Solicitud de colaboración."""
    request_id: str
    ticket_id: str
    from_agent_id: str
    from_agent_name: str
    to_agent_id: Optional[str] = None
    to_department: Optional[str] = None
    collaboration_type: CollaborationType = CollaborationType.ASSISTANCE
    reason: str = ""
    priority: str = "normal"
    status: CollaborationStatus = CollaborationStatus.PENDING
    created_at: datetime = None
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: List[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.notes is None:
            self.notes = []


@dataclass
class AgentNote:
    """Nota de agente."""
    note_id: str
    ticket_id: str
    agent_id: str
    agent_name: str
    content: str
    is_internal: bool = True  # Nota interna vs. visible al cliente
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class AgentActivity:
    """Actividad de agente en ticket."""
    activity_id: str
    ticket_id: str
    agent_id: str
    agent_name: str
    activity_type: str  # 'view', 'edit', 'comment', 'resolve', 'assign'
    description: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class CollaborationManager:
    """Gestor de colaboración."""
    
    def __init__(self, db_connection):
        """
        Inicializa gestor.
        
        Args:
            db_connection: Conexión a base de datos
        """
        self.db = db_connection
        self.active_collaborations: Dict[str, CollaborationRequest] = {}
        self.agent_notes: Dict[str, List[AgentNote]] = {}
        self.agent_activities: Dict[str, List[AgentActivity]] = {}
    
    def create_collaboration_request(
        self,
        ticket_id: str,
        from_agent_id: str,
        from_agent_name: str,
        to_agent_id: Optional[str] = None,
        to_department: Optional[str] = None,
        collaboration_type: CollaborationType = CollaborationType.ASSISTANCE,
        reason: str = ""
    ) -> CollaborationRequest:
        """
        Crea solicitud de colaboración.
        
        Args:
            ticket_id: ID del ticket
            from_agent_id: ID del agente que solicita
            from_agent_name: Nombre del agente
            to_agent_id: ID del agente destino (opcional)
            to_department: Departamento destino (opcional)
            collaboration_type: Tipo de colaboración
            reason: Razón de la colaboración
            
        Returns:
            Solicitud creada
        """
        request = CollaborationRequest(
            request_id=f"collab-{uuid.uuid4().hex[:12]}",
            ticket_id=ticket_id,
            from_agent_id=from_agent_id,
            from_agent_name=from_agent_name,
            to_agent_id=to_agent_id,
            to_department=to_department,
            collaboration_type=collaboration_type,
            reason=reason
        )
        
        self.active_collaborations[request.request_id] = request
        
        # Persistir en BD
        self._save_collaboration_request(request)
        
        logger.info(f"Collaboration request created: {request.request_id}")
        return request
    
    def accept_collaboration(
        self,
        request_id: str,
        agent_id: str,
        agent_name: str
    ) -> bool:
        """
        Acepta solicitud de colaboración.
        
        Args:
            request_id: ID de la solicitud
            agent_id: ID del agente que acepta
            agent_name: Nombre del agente
            
        Returns:
            True si se aceptó correctamente
        """
        if request_id not in self.active_collaborations:
            return False
        
        request = self.active_collaborations[request_id]
        
        if request.status != CollaborationStatus.PENDING:
            return False
        
        request.status = CollaborationStatus.ACTIVE
        request.accepted_at = datetime.now()
        
        # Si había to_agent_id, verificar que coincida
        if request.to_agent_id and request.to_agent_id != agent_id:
            return False
        
        # Actualizar BD
        self._update_collaboration_request(request)
        
        logger.info(f"Collaboration accepted: {request_id} by {agent_name}")
        return True
    
    def complete_collaboration(
        self,
        request_id: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Completa colaboración.
        
        Args:
            request_id: ID de la solicitud
            notes: Notas finales
            
        Returns:
            True si se completó correctamente
        """
        if request_id not in self.active_collaborations:
            return False
        
        request = self.active_collaborations[request_id]
        request.status = CollaborationStatus.COMPLETED
        request.completed_at = datetime.now()
        
        if notes:
            request.notes.append(notes)
        
        # Actualizar BD
        self._update_collaboration_request(request)
        
        logger.info(f"Collaboration completed: {request_id}")
        return True
    
    def add_note(
        self,
        ticket_id: str,
        agent_id: str,
        agent_name: str,
        content: str,
        is_internal: bool = True
    ) -> AgentNote:
        """
        Agrega nota de agente.
        
        Args:
            ticket_id: ID del ticket
            agent_id: ID del agente
            agent_name: Nombre del agente
            content: Contenido de la nota
            is_internal: Si es nota interna
            
        Returns:
            Nota creada
        """
        note = AgentNote(
            note_id=f"note-{uuid.uuid4().hex[:12]}",
            ticket_id=ticket_id,
            agent_id=agent_id,
            agent_name=agent_name,
            content=content,
            is_internal=is_internal
        )
        
        if ticket_id not in self.agent_notes:
            self.agent_notes[ticket_id] = []
        self.agent_notes[ticket_id].append(note)
        
        # Persistir en BD
        self._save_note(note)
        
        logger.info(f"Note added to ticket {ticket_id} by {agent_name}")
        return note
    
    def get_collaboration_history(
        self,
        ticket_id: str
    ) -> List[CollaborationRequest]:
        """
        Obtiene historial de colaboración.
        
        Args:
            ticket_id: ID del ticket
            
        Returns:
            Lista de colaboraciones
        """
        # Cargar desde BD
        return self._load_collaborations_for_ticket(ticket_id)
    
    def get_notes(
        self,
        ticket_id: str,
        include_internal: bool = True
    ) -> List[AgentNote]:
        """
        Obtiene notas de un ticket.
        
        Args:
            ticket_id: ID del ticket
            include_internal: Incluir notas internas
            
        Returns:
            Lista de notas
        """
        # Cargar desde BD
        notes = self._load_notes_for_ticket(ticket_id)
        
        if not include_internal:
            notes = [n for n in notes if not n.is_internal]
        
        return notes
    
    def log_activity(
        self,
        ticket_id: str,
        agent_id: str,
        agent_name: str,
        activity_type: str,
        description: str
    ) -> AgentActivity:
        """
        Registra actividad de agente.
        
        Args:
            ticket_id: ID del ticket
            agent_id: ID del agente
            agent_name: Nombre del agente
            activity_type: Tipo de actividad
            description: Descripción
            
        Returns:
            Actividad registrada
        """
        activity = AgentActivity(
            activity_id=f"activity-{uuid.uuid4().hex[:12]}",
            ticket_id=ticket_id,
            agent_id=agent_id,
            agent_name=agent_name,
            activity_type=activity_type,
            description=description
        )
        
        if ticket_id not in self.agent_activities:
            self.agent_activities[ticket_id] = []
        self.agent_activities[ticket_id].append(activity)
        
        # Persistir en BD
        self._save_activity(activity)
        
        return activity
    
    def _save_collaboration_request(self, request: CollaborationRequest):
        """Persiste solicitud en BD."""
        # Implementar según esquema de BD
        pass
    
    def _update_collaboration_request(self, request: CollaborationRequest):
        """Actualiza solicitud en BD."""
        # Implementar según esquema de BD
        pass
    
    def _load_collaborations_for_ticket(self, ticket_id: str) -> List[CollaborationRequest]:
        """Carga colaboraciones desde BD."""
        # Implementar según esquema de BD
        return []
    
    def _save_note(self, note: AgentNote):
        """Persiste nota en BD."""
        # Implementar según esquema de BD
        pass
    
    def _load_notes_for_ticket(self, ticket_id: str) -> List[AgentNote]:
        """Carga notas desde BD."""
        # Implementar según esquema de BD
        return []
    
    def _save_activity(self, activity: AgentActivity):
        """Persiste actividad en BD."""
        # Implementar según esquema de BD
        pass

