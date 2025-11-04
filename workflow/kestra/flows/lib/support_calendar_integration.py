"""
Sistema de Integración con Calendario y Programación.

Integra con calendarios para programación de agentes y seguimiento.
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

try:
    from icalendar import Calendar, Event
    ICALENDAR_AVAILABLE = True
except ImportError:
    ICALENDAR_AVAILABLE = False

logger = logging.getLogger(__name__)


class CalendarProvider(Enum):
    """Proveedores de calendario."""
    GOOGLE = "google"
    OUTLOOK = "outlook"
    ICAL = "ical"
    CUSTOM = "custom"


@dataclass
class CalendarEvent:
    """Evento de calendario."""
    event_id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendees: List[str] = None
    related_ticket_id: Optional[str] = None
    event_type: str = "meeting"  # "meeting", "follow_up", "reminder"
    
    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []


@dataclass
class AgentSchedule:
    """Horario de agente."""
    agent_id: str
    agent_name: str
    date: datetime.date
    shifts: List[Dict[str, Any]]  # Lista de turnos
    availability_hours: float
    scheduled_events: List[CalendarEvent]


class CalendarIntegration:
    """Integración con calendarios."""
    
    def __init__(self, provider: CalendarProvider = CalendarProvider.GOOGLE):
        """
        Inicializa integración.
        
        Args:
            provider: Proveedor de calendario
        """
        self.provider = provider
        self.events: List[CalendarEvent] = []
        self.schedules: Dict[str, AgentSchedule] = {}
    
    def create_follow_up_event(
        self,
        ticket_id: str,
        customer_email: str,
        follow_up_date: datetime,
        description: str = ""
    ) -> CalendarEvent:
        """
        Crea evento de seguimiento.
        
        Args:
            ticket_id: ID del ticket
            customer_email: Email del cliente
            follow_up_date: Fecha de seguimiento
            description: Descripción
            
        Returns:
            Evento creado
        """
        event = CalendarEvent(
            event_id=f"event-{ticket_id}-{follow_up_date.timestamp()}",
            title=f"Follow-up: Ticket {ticket_id}",
            description=description or f"Seguimiento de ticket {ticket_id} con {customer_email}",
            start_time=follow_up_date,
            end_time=follow_up_date + timedelta(minutes=30),
            related_ticket_id=ticket_id,
            event_type="follow_up",
            attendees=[customer_email]
        )
        
        self.events.append(event)
        
        logger.info(f"Created follow-up event for ticket {ticket_id}")
        return event
    
    def create_reminder(
        self,
        ticket_id: str,
        reminder_time: datetime,
        message: str
    ) -> CalendarEvent:
        """
        Crea recordatorio.
        
        Args:
            ticket_id: ID del ticket
            reminder_time: Hora del recordatorio
            message: Mensaje
            
        Returns:
            Evento creado
        """
        event = CalendarEvent(
            event_id=f"reminder-{ticket_id}-{reminder_time.timestamp()}",
            title=f"Reminder: {message}",
            description=f"Recordatorio para ticket {ticket_id}: {message}",
            start_time=reminder_time,
            end_time=reminder_time + timedelta(minutes=15),
            related_ticket_id=ticket_id,
            event_type="reminder"
        )
        
        self.events.append(event)
        return event
    
    def schedule_agent_meeting(
        self,
        agent_ids: List[str],
        meeting_time: datetime,
        duration_minutes: int = 60,
        topic: str = ""
    ) -> CalendarEvent:
        """
        Programa reunión de agentes.
        
        Args:
            agent_ids: IDs de agentes
            meeting_time: Hora de la reunión
            duration_minutes: Duración en minutos
            topic: Tema de la reunión
            
        Returns:
            Evento creado
        """
        event = CalendarEvent(
            event_id=f"meeting-{meeting_time.timestamp()}",
            title=f"Team Meeting: {topic}" if topic else "Team Meeting",
            description=topic,
            start_time=meeting_time,
            end_time=meeting_time + timedelta(minutes=duration_minutes),
            event_type="meeting",
            attendees=agent_ids
        )
        
        self.events.append(event)
        return event
    
    def get_agent_schedule(
        self,
        agent_id: str,
        date: datetime.date
    ) -> Optional[AgentSchedule]:
        """
        Obtiene horario de agente.
        
        Args:
            agent_id: ID del agente
            date: Fecha
            
        Returns:
            Horario del agente
        """
        key = f"{agent_id}-{date}"
        return self.schedules.get(key)
    
    def set_agent_availability(
        self,
        agent_id: str,
        agent_name: str,
        date: datetime.date,
        shifts: List[Dict[str, Any]],
        availability_hours: float
    ):
        """
        Establece disponibilidad de agente.
        
        Args:
            agent_id: ID del agente
            agent_name: Nombre del agente
            date: Fecha
            shifts: Lista de turnos
            availability_hours: Horas disponibles
        """
        key = f"{agent_id}-{date}"
        
        schedule = AgentSchedule(
            agent_id=agent_id,
            agent_name=agent_name,
            date=date,
            shifts=shifts,
            availability_hours=availability_hours,
            scheduled_events=[
                e for e in self.events
                if agent_id in e.attendees
                and e.start_time.date() == date
            ]
        )
        
        self.schedules[key] = schedule
    
    def export_to_ical(self, events: List[CalendarEvent]) -> str:
        """
        Exporta eventos a formato iCal.
        
        Args:
            events: Lista de eventos
            
        Returns:
            String en formato iCal
        """
        if not ICALENDAR_AVAILABLE:
            logger.warning("icalendar not available, returning empty calendar")
            return ""
        
        cal = Calendar()
        cal.add('prodid', '-//Support System//')
        cal.add('version', '2.0')
        
        for event_data in events:
            event = Event()
            event.add('summary', event_data.title)
            event.add('description', event_data.description)
            event.add('dtstart', event_data.start_time)
            event.add('dtend', event_data.end_time)
            if event_data.location:
                event.add('location', event_data.location)
            if event_data.attendees:
                for attendee in event_data.attendees:
                    event.add('attendee', f"MAILTO:{attendee}")
            
            cal.add_component(event)
        
        return cal.to_ical().decode('utf-8')
    
    def get_upcoming_events(
        self,
        hours: int = 24,
        event_type: Optional[str] = None
    ) -> List[CalendarEvent]:
        """
        Obtiene eventos próximos.
        
        Args:
            hours: Horas hacia adelante
            event_type: Tipo de evento (opcional)
            
        Returns:
            Lista de eventos
        """
        cutoff = datetime.now() + timedelta(hours=hours)
        
        upcoming = [
            e for e in self.events
            if e.start_time >= datetime.now()
            and e.start_time <= cutoff
        ]
        
        if event_type:
            upcoming = [e for e in upcoming if e.event_type == event_type]
        
        return sorted(upcoming, key=lambda x: x.start_time)
    
    def get_events_for_ticket(self, ticket_id: str) -> List[CalendarEvent]:
        """
        Obtiene eventos relacionados con un ticket.
        
        Args:
            ticket_id: ID del ticket
            
        Returns:
            Lista de eventos
        """
        return [
            e for e in self.events
            if e.related_ticket_id == ticket_id
        ]

