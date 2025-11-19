"""
Gestor de Registros de Entrada/Salida (Clock In/Out)
"""

import logging
from datetime import datetime, date
from typing import Optional, Dict, Any
from decimal import Decimal

from .storage import TimeTrackingStorage, ClockEvent, EventType

logger = logging.getLogger(__name__)


class ClockManager:
    """Gestiona registros de entrada/salida automáticos"""
    
    def __init__(self, storage: TimeTrackingStorage):
        self.storage = storage
    
    def clock_in(
        self,
        employee_id: str,
        event_time: Optional[datetime] = None,
        location: Optional[str] = None,
        device_type: Optional[str] = None,
        notes: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Registra entrada (clock in)
        
        Returns:
            ID del evento creado
        """
        if event_time is None:
            event_time = datetime.now()
        
        event = ClockEvent(
            employee_id=employee_id,
            event_type=EventType.CLOCK_IN,
            event_time=event_time,
            location=location,
            device_type=device_type or "api",
            notes=notes,
            metadata=metadata
        )
        
        event_id = self.storage.save_clock_event(event)
        logger.info(f"Clock in registered for employee {employee_id} at {event_time}")
        
        return event_id
    
    def clock_out(
        self,
        employee_id: str,
        event_time: Optional[datetime] = None,
        location: Optional[str] = None,
        device_type: Optional[str] = None,
        notes: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Registra salida (clock out)
        
        Returns:
            ID del evento creado
        """
        if event_time is None:
            event_time = datetime.now()
        
        event = ClockEvent(
            employee_id=employee_id,
            event_type=EventType.CLOCK_OUT,
            event_time=event_time,
            location=location,
            device_type=device_type or "api",
            notes=notes,
            metadata=metadata
        )
        
        event_id = self.storage.save_clock_event(event)
        logger.info(f"Clock out registered for employee {employee_id} at {event_time}")
        
        return event_id
    
    def get_last_clock_event(
        self,
        employee_id: str,
        event_type: Optional[EventType] = None
    ) -> Optional[Dict[str, Any]]:
        """Obtiene el último evento de clock del empleado"""
        sql = """
            SELECT id, employee_id, event_type, event_time, location, device_type
            FROM time_tracking_clock_events
            WHERE employee_id = %s
        """
        
        params = [employee_id]
        if event_type:
            sql += " AND event_type = %s"
            params.append(event_type.value)
        
        sql += " ORDER BY event_time DESC LIMIT 1"
        
        result = self.storage.hook.get_first(sql, parameters=tuple(params))
        if not result:
            return None
        
        return {
            "id": result[0],
            "employee_id": result[1],
            "event_type": result[2],
            "event_time": result[3],
            "location": result[4],
            "device_type": result[5]
        }
    
    def is_clocked_in(self, employee_id: str, work_date: Optional[date] = None) -> bool:
        """Verifica si el empleado está actualmente clock in"""
        if work_date is None:
            work_date = date.today()
        
        open_session = self.storage.get_open_session(employee_id, work_date)
        return open_session is not None

