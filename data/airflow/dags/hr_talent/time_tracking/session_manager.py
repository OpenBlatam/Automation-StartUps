"""
Gestor de Sesiones de Trabajo
"""

import logging
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any
from decimal import Decimal

from .storage import TimeTrackingStorage, WorkSession, SessionStatus, ClockEvent, EventType
from .clock_manager import ClockManager
from .hour_calculator import TimeTrackingHourCalculator

logger = logging.getLogger(__name__)


class SessionManager:
    """Gestiona sesiones de trabajo"""
    
    def __init__(
        self,
        storage: TimeTrackingStorage,
        clock_manager: ClockManager,
        hour_calculator: TimeTrackingHourCalculator
    ):
        self.storage = storage
        self.clock_manager = clock_manager
        self.hour_calculator = hour_calculator
    
    def start_session(
        self,
        employee_id: str,
        clock_in_time: Optional[datetime] = None,
        location: Optional[str] = None,
        notes: Optional[str] = None
    ) -> int:
        """
        Inicia una nueva sesión de trabajo
        
        Returns:
            ID de la sesión creada
        """
        if clock_in_time is None:
            clock_in_time = datetime.now()
        
        work_date = clock_in_time.date()
        
        # Verificar si ya hay una sesión abierta
        open_session = self.storage.get_open_session(employee_id, work_date)
        if open_session:
            logger.warning(
                f"Employee {employee_id} already has an open session starting at {open_session['clock_in_time']}"
            )
            return open_session["id"]
        
        # Registrar clock in
        clock_in_event_id = self.clock_manager.clock_in(
            employee_id=employee_id,
            event_time=clock_in_time,
            location=location,
            notes=notes
        )
        
        # Crear sesión
        session = WorkSession(
            employee_id=employee_id,
            work_date=work_date,
            clock_in_time=clock_in_time,
            status=SessionStatus.OPEN
        )
        
        session_id = self.storage.create_work_session(session, clock_in_event_id)
        logger.info(f"Work session started for employee {employee_id}, session_id={session_id}")
        
        return session_id
    
    def end_session(
        self,
        employee_id: str,
        clock_out_time: Optional[datetime] = None,
        notes: Optional[str] = None
    ) -> Optional[int]:
        """
        Cierra una sesión de trabajo abierta
        
        Returns:
            ID de la sesión cerrada, o None si no había sesión abierta
        """
        if clock_out_time is None:
            clock_out_time = datetime.now()
        
        work_date = clock_out_time.date()
        
        # Buscar sesión abierta
        open_session = self.storage.get_open_session(employee_id, work_date)
        if not open_session:
            logger.warning(f"No open session found for employee {employee_id} on {work_date}")
            return None
        
        session_id = open_session["id"]
        clock_in_time = open_session["clock_in_time"]
        
        # Registrar clock out
        clock_out_event_id = self.clock_manager.clock_out(
            employee_id=employee_id,
            event_time=clock_out_time,
            notes=notes
        )
        
        # Calcular horas (ahora retorna también double_time_hours)
        break_minutes = open_session.get("break_duration_minutes", 0)
        total_hours, regular_hours, overtime_hours, double_time_hours = self.hour_calculator.calculate_hours(
            clock_in_time=clock_in_time,
            clock_out_time=clock_out_time,
            break_minutes=break_minutes,
            employee_id=employee_id
        )
        
        # Actualizar sesión (combinar overtime y double_time para compatibilidad)
        # Nota: double_time_hours se almacena junto con overtime_hours
        # En el futuro, podríamos usar la columna double_time_hours si existe
        total_overtime = overtime_hours + double_time_hours
        
        self.storage.update_work_session(
            session_id=session_id,
            clock_out_event_id=clock_out_event_id,
            clock_out_time=clock_out_time,
            total_hours=total_hours,
            regular_hours=regular_hours,
            overtime_hours=total_overtime,
            status=SessionStatus.CLOSED
        )
        
        logger.info(
            f"Work session closed for employee {employee_id}, "
            f"total_hours={total_hours}, regular={regular_hours}, "
            f"overtime={overtime_hours}, double_time={double_time_hours}"
        )
        
        return session_id
    
    def auto_close_stale_sessions(self, max_hours_open: int = 24) -> int:
        """
        Cierra automáticamente sesiones abiertas que tienen más de X horas
        
        Returns:
            Número de sesiones cerradas
        """
        sql = f"""
            SELECT auto_close_stale_sessions(%s)
        """
        
        result = self.storage.hook.get_first(sql, parameters=(max_hours_open,))
        count = result[0] if result else 0
        
        logger.info(f"Auto-closed {count} stale sessions")
        return count
    
    def get_session_summary(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Obtiene resumen de sesiones en un rango de fechas"""
        sql = """
            SELECT 
                COUNT(*) as total_sessions,
                SUM(total_hours) as total_hours,
                SUM(regular_hours) as regular_hours,
                SUM(overtime_hours) as overtime_hours,
                COUNT(CASE WHEN status = 'disputed' THEN 1 END) as disputed_count,
                COUNT(CASE WHEN approved = false THEN 1 END) as unapproved_count
            FROM time_tracking_work_sessions
            WHERE employee_id = %s
                AND work_date BETWEEN %s AND %s
        """
        
        result = self.storage.hook.get_first(
            sql,
            parameters=(employee_id, start_date, end_date)
        )
        
        if not result:
            return {
                "total_sessions": 0,
                "total_hours": Decimal("0.00"),
                "regular_hours": Decimal("0.00"),
                "overtime_hours": Decimal("0.00"),
                "disputed_count": 0,
                "unapproved_count": 0
            }
        
        return {
            "total_sessions": result[0] or 0,
            "total_hours": Decimal(str(result[1] or 0)),
            "regular_hours": Decimal(str(result[2] or 0)),
            "overtime_hours": Decimal(str(result[3] or 0)),
            "disputed_count": result[4] or 0,
            "unapproved_count": result[5] or 0
        }

