"""
Sistema de Eventos para Nómina
Event bus para comunicación entre componentes
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Tipos de eventos"""
    PAYROLL_CALCULATED = "payroll.calculated"
    PAYROLL_APPROVED = "payroll.approved"
    PAYROLL_PAID = "payroll.paid"
    EXPENSE_SUBMITTED = "expense.submitted"
    EXPENSE_APPROVED = "expense.approved"
    EXPENSE_REJECTED = "expense.rejected"
    APPROVAL_REQUESTED = "approval.requested"
    APPROVAL_APPROVED = "approval.approved"
    APPROVAL_REJECTED = "approval.rejected"
    ANOMALY_DETECTED = "anomaly.detected"
    ALERT_TRIGGERED = "alert.triggered"
    COMPLIANCE_VIOLATION = "compliance.violation"
    OCR_COMPLETED = "ocr.completed"
    OCR_FAILED = "ocr.failed"
    MAINTENANCE_STARTED = "maintenance.started"
    MAINTENANCE_COMPLETED = "maintenance.completed"
    BACKUP_CREATED = "backup.created"
    MIGRATION_APPLIED = "migration.applied"


@dataclass
class PayrollEvent:
    """Evento del sistema de nómina"""
    event_type: EventType
    payload: Dict[str, Any]
    timestamp: datetime = None
    event_id: str = None
    source: str = "payroll_system"
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.event_id is None:
            import uuid
            self.event_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte evento a diccionario"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "payload": self.payload,
            "metadata": self.metadata or {}
        }


class PayrollEventBus:
    """Event bus para sistema de nómina"""
    
    def __init__(self):
        """Inicializa event bus"""
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[PayrollEvent] = []
        self.max_history: int = 1000
    
    def subscribe(
        self,
        event_type: EventType,
        handler: Callable[[PayrollEvent], None]
    ) -> None:
        """Suscribe un handler a un tipo de evento"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(handler)
        logger.info(f"Subscribed handler to {event_type.value}")
    
    def unsubscribe(
        self,
        event_type: EventType,
        handler: Callable[[PayrollEvent], None]
    ) -> None:
        """Desuscribe un handler"""
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(handler)
                logger.info(f"Unsubscribed handler from {event_type.value}")
            except ValueError:
                logger.warning(f"Handler not found for {event_type.value}")
    
    def publish(self, event: PayrollEvent) -> None:
        """Publica un evento"""
        # Guardar en historial
        self.event_history.append(event)
        
        # Mantener solo últimos N eventos
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
        
        # Notificar subscribers
        handlers = self.subscribers.get(event.event_type, [])
        
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(
                    f"Error in event handler for {event.event_type.value}: {e}",
                    exc_info=True
                )
        
        logger.debug(f"Published event: {event.event_type.value}")
    
    def get_event_history(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Obtiene historial de eventos"""
        events = self.event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        return [e.to_dict() for e in events[-limit:]]
    
    def clear_history(self) -> None:
        """Limpia historial de eventos"""
        self.event_history = []
        logger.info("Event history cleared")


# Instancia global
event_bus = PayrollEventBus()

