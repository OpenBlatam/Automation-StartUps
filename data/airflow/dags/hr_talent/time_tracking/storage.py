"""
Almacenamiento para Sistema de Gestión de Tiempo y Asistencia
"""

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Tipos de eventos de clock"""
    CLOCK_IN = "clock_in"
    CLOCK_OUT = "clock_out"
    BREAK_START = "break_start"
    BREAK_END = "break_end"


class SessionStatus(str, Enum):
    """Estados de sesión de trabajo"""
    OPEN = "open"
    CLOSED = "closed"
    DISPUTED = "disputed"
    APPROVED = "approved"
    REJECTED = "rejected"


class VacationType(str, Enum):
    """Tipos de vacaciones"""
    VACATION = "vacation"
    SICK = "sick"
    PERSONAL = "personal"
    BEREAVEMENT = "bereavement"
    JURY_DUTY = "jury_duty"
    MILITARY = "military"
    OTHER = "other"


class DisputeType(str, Enum):
    """Tipos de disputas"""
    MISSING_CLOCK = "missing_clock"
    INCORRECT_TIME = "incorrect_time"
    MISSING_BREAK = "missing_break"
    OVERTIME_CALCULATION = "overtime_calculation"
    OTHER = "other"


@dataclass
class ClockEvent:
    """Evento de clock in/out"""
    employee_id: str
    event_type: EventType
    event_time: datetime
    location: Optional[str] = None
    device_type: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class WorkSession:
    """Sesión de trabajo"""
    employee_id: str
    work_date: date
    clock_in_time: datetime
    clock_out_time: Optional[datetime] = None
    total_hours: Decimal = Decimal("0.00")
    regular_hours: Decimal = Decimal("0.00")
    overtime_hours: Decimal = Decimal("0.00")
    break_duration_minutes: int = 0
    status: SessionStatus = SessionStatus.OPEN
    notes: Optional[str] = None


@dataclass
class VacationRequest:
    """Solicitud de vacaciones"""
    employee_id: str
    vacation_type: VacationType
    start_date: date
    end_date: date
    days_requested: Decimal
    notes: Optional[str] = None


@dataclass
class TimeDispute:
    """Disputa de tiempo"""
    employee_id: str
    dispute_type: DisputeType
    dispute_date: date
    description: str
    requested_hours: Optional[Decimal] = None
    current_hours: Optional[Decimal] = None
    evidence_urls: Optional[List[str]] = None


class TimeTrackingStorage:
    """Almacenamiento para time tracking"""
    
    def __init__(self, postgres_conn_id: str = "postgres_default"):
        self.postgres_conn_id = postgres_conn_id
        self._hook: Optional[PostgresHook] = None
    
    @property
    def hook(self) -> PostgresHook:
        if self._hook is None:
            self._hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        return self._hook
    
    def save_clock_event(self, event: ClockEvent) -> int:
        """Guarda un evento de clock in/out"""
        sql = """
            INSERT INTO time_tracking_clock_events (
                employee_id, event_type, event_time, location,
                device_type, notes, metadata
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id
        """
        
        result = self.hook.get_first(
            sql,
            parameters=(
                event.employee_id,
                event.event_type.value,
                event.event_time,
                event.location,
                event.device_type,
                event.notes,
                event.metadata
            )
        )
        
        return result[0] if result else 0
    
    def get_open_session(self, employee_id: str, work_date: date) -> Optional[Dict[str, Any]]:
        """Obtiene la sesión abierta del empleado para una fecha"""
        sql = """
            SELECT id, employee_id, work_date, clock_in_time, clock_out_time,
                   total_hours, regular_hours, overtime_hours,
                   break_duration_minutes, status
            FROM time_tracking_work_sessions
            WHERE employee_id = %s
                AND work_date = %s
                AND status = 'open'
                AND clock_out_time IS NULL
            ORDER BY clock_in_time DESC
            LIMIT 1
        """
        
        result = self.hook.get_first(sql, parameters=(employee_id, work_date))
        if not result:
            return None
        
        return {
            "id": result[0],
            "employee_id": result[1],
            "work_date": result[2],
            "clock_in_time": result[3],
            "clock_out_time": result[4],
            "total_hours": float(result[5]) if result[5] else 0.0,
            "regular_hours": float(result[6]) if result[6] else 0.0,
            "overtime_hours": float(result[7]) if result[7] else 0.0,
            "break_duration_minutes": result[8] if result[8] else 0,
            "status": result[9]
        }
    
    def create_work_session(self, session: WorkSession, clock_in_event_id: int) -> int:
        """Crea una nueva sesión de trabajo"""
        sql = """
            INSERT INTO time_tracking_work_sessions (
                employee_id, work_date, clock_in_event_id,
                clock_in_time, clock_out_time, total_hours,
                regular_hours, overtime_hours, break_duration_minutes,
                status, notes
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id
        """
        
        result = self.hook.get_first(
            sql,
            parameters=(
                session.employee_id,
                session.work_date,
                clock_in_event_id,
                session.clock_in_time,
                session.clock_out_time,
                float(session.total_hours),
                float(session.regular_hours),
                float(session.overtime_hours),
                session.break_duration_minutes,
                session.status.value,
                session.notes
            )
        )
        
        return result[0] if result else 0
    
    def update_work_session(
        self,
        session_id: int,
        clock_out_event_id: Optional[int] = None,
        clock_out_time: Optional[datetime] = None,
        total_hours: Optional[Decimal] = None,
        regular_hours: Optional[Decimal] = None,
        overtime_hours: Optional[Decimal] = None,
        status: Optional[SessionStatus] = None
    ) -> bool:
        """Actualiza una sesión de trabajo"""
        updates = []
        params = []
        
        if clock_out_event_id is not None:
            updates.append("clock_out_event_id = %s")
            params.append(clock_out_event_id)
        
        if clock_out_time is not None:
            updates.append("clock_out_time = %s")
            params.append(clock_out_time)
        
        if total_hours is not None:
            updates.append("total_hours = %s")
            params.append(float(total_hours))
        
        if regular_hours is not None:
            updates.append("regular_hours = %s")
            params.append(float(regular_hours))
        
        if overtime_hours is not None:
            updates.append("overtime_hours = %s")
            params.append(float(overtime_hours))
        
        if status is not None:
            updates.append("status = %s")
            params.append(status.value)
        
        if not updates:
            return False
        
        updates.append("updated_at = NOW()")
        params.append(session_id)
        
        sql = f"""
            UPDATE time_tracking_work_sessions
            SET {', '.join(updates)}
            WHERE id = %s
        """
        
        self.hook.run(sql, parameters=params)
        return True
    
    def save_vacation_request(self, request: VacationRequest) -> int:
        """Guarda una solicitud de vacaciones"""
        sql = """
            INSERT INTO time_tracking_vacations (
                employee_id, vacation_type, start_date, end_date,
                days_requested, notes
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            )
            RETURNING id
        """
        
        result = self.hook.get_first(
            sql,
            parameters=(
                request.employee_id,
                request.vacation_type.value,
                request.start_date,
                request.end_date,
                float(request.days_requested),
                request.notes
            )
        )
        
        return result[0] if result else 0
    
    def save_dispute(self, dispute: TimeDispute, work_session_id: Optional[int] = None) -> int:
        """Guarda una disputa de tiempo"""
        sql = """
            INSERT INTO time_tracking_disputes (
                employee_id, work_session_id, dispute_type,
                dispute_date, description, requested_hours,
                current_hours, evidence_urls
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id
        """
        
        result = self.hook.get_first(
            sql,
            parameters=(
                dispute.employee_id,
                work_session_id,
                dispute.dispute_type.value,
                dispute.dispute_date,
                dispute.description,
                float(dispute.requested_hours) if dispute.requested_hours else None,
                float(dispute.current_hours) if dispute.current_hours else None,
                dispute.evidence_urls
            )
        )
        
        return result[0] if result else 0
    
    def get_vacation_balance(self, employee_id: str, year: int = None) -> Dict[str, Decimal]:
        """Obtiene el saldo de vacaciones del empleado"""
        if year is None:
            year = datetime.now().year
        
        sql = """
            SELECT vacation_days_available, sick_days_available, personal_days_available
            FROM time_tracking_vacation_balances
            WHERE employee_id = %s AND year = %s
        """
        
        result = self.hook.get_first(sql, parameters=(employee_id, year))
        if not result:
            return {
                "vacation_days": Decimal("0.00"),
                "sick_days": Decimal("0.00"),
                "personal_days": Decimal("0.00")
            }
        
        return {
            "vacation_days": Decimal(str(result[0])),
            "sick_days": Decimal(str(result[1])),
            "personal_days": Decimal(str(result[2]))
        }
    
    def get_open_disputes(self, employee_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtiene disputas abiertas"""
        if employee_id:
            sql = """
                SELECT id, employee_id, dispute_type, dispute_date,
                       description, status, priority
                FROM time_tracking_disputes
                WHERE employee_id = %s
                    AND status IN ('open', 'under_review')
                ORDER BY priority DESC, dispute_date DESC
            """
            results = self.hook.get_records(sql, parameters=(employee_id,))
        else:
            sql = """
                SELECT id, employee_id, dispute_type, dispute_date,
                       description, status, priority
                FROM time_tracking_disputes
                WHERE status IN ('open', 'under_review')
                ORDER BY priority DESC, dispute_date DESC
            """
            results = self.hook.get_records(sql)
        
        disputes = []
        for row in results:
            disputes.append({
                "id": row[0],
                "employee_id": row[1],
                "dispute_type": row[2],
                "dispute_date": row[3],
                "description": row[4],
                "status": row[5],
                "priority": row[6]
            })
        
        return disputes

