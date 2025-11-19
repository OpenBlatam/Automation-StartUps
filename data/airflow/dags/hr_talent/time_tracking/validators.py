"""
Validadores para Time Tracking
"""

import logging
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
from decimal import Decimal

from .storage import TimeTrackingStorage

logger = logging.getLogger(__name__)


class TimeTrackingValidator:
    """Valida datos y reglas de negocio para time tracking"""
    
    def __init__(self, storage: TimeTrackingStorage):
        self.storage = storage
    
    def validate_clock_in(
        self,
        employee_id: str,
        event_time: datetime
    ) -> tuple[bool, Optional[str]]:
        """
        Valida que se pueda hacer clock in
        
        Returns:
            (is_valid, error_message)
        """
        work_date = event_time.date()
        
        # Verificar si ya hay una sesión abierta
        open_session = self.storage.get_open_session(employee_id, work_date)
        if open_session:
            return False, f"Employee already has an open session starting at {open_session['clock_in_time']}"
        
        # Verificar si el empleado está activo
        sql = """
            SELECT active FROM payroll_employees
            WHERE employee_id = %s
        """
        result = self.storage.hook.get_first(sql, parameters=(employee_id,))
        if not result or not result[0]:
            return False, f"Employee {employee_id} is not active"
        
        return True, None
    
    def validate_clock_out(
        self,
        employee_id: str,
        event_time: datetime
    ) -> tuple[bool, Optional[str]]:
        """
        Valida que se pueda hacer clock out
        
        Returns:
            (is_valid, error_message)
        """
        work_date = event_time.date()
        
        # Verificar que haya una sesión abierta
        open_session = self.storage.get_open_session(employee_id, work_date)
        if not open_session:
            return False, f"No open session found for employee {employee_id}"
        
        # Verificar que clock_out sea después de clock_in
        clock_in_time = open_session["clock_in_time"]
        if event_time <= clock_in_time:
            return False, f"Clock out time must be after clock in time"
        
        # Verificar límite máximo de horas (por ejemplo, 24 horas)
        max_hours = 24
        hours_open = (event_time - clock_in_time).total_seconds() / 3600.0
        if hours_open > max_hours:
            return False, f"Session exceeds maximum allowed hours ({max_hours})"
        
        return True, None
    
    def validate_vacation_request(
        self,
        employee_id: str,
        start_date: date,
        end_date: date,
        vacation_type: str
    ) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Valida una solicitud de vacaciones
        
        Returns:
            (is_valid, error_message, balance_info)
        """
        # Validar fechas
        if end_date < start_date:
            return False, "End date must be after start date", None
        
        if start_date < date.today():
            return False, "Start date cannot be in the past", None
        
        # Verificar saldo disponible
        balance = self.storage.get_vacation_balance(employee_id)
        days_requested = Decimal(str((end_date - start_date).days + 1))
        
        if vacation_type == "vacation":
            available = balance["vacation_days"]
        elif vacation_type == "sick":
            available = balance["sick_days"]
        elif vacation_type == "personal":
            available = balance["personal_days"]
        else:
            available = Decimal("999")  # Sin límite para otros tipos
        
        if days_requested > available:
            return (
                False,
                f"Insufficient balance: requested {days_requested} days, available {available} days",
                balance
            )
        
        # Verificar solapamiento con otras solicitudes
        sql = """
            SELECT id FROM time_tracking_vacations
            WHERE employee_id = %s
                AND status IN ('pending', 'approved')
                AND (
                    (start_date <= %s AND end_date >= %s) OR
                    (start_date <= %s AND end_date >= %s) OR
                    (start_date >= %s AND end_date <= %s)
                )
        """
        
        result = self.storage.hook.get_first(
            sql,
            parameters=(employee_id, start_date, start_date, end_date, end_date, start_date, end_date)
        )
        
        if result:
            return False, "Overlapping vacation request already exists", balance
        
        return True, None, balance
    
    def detect_time_discrepancies(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Detecta discrepancias en registros de tiempo
        
        Returns:
            Lista de discrepancias detectadas
        """
        discrepancies = []
        
        # Buscar sesiones sin clock out después de 24 horas
        sql = """
            SELECT id, work_date, clock_in_time
            FROM time_tracking_work_sessions
            WHERE employee_id = %s
                AND work_date BETWEEN %s AND %s
                AND status = 'open'
                AND clock_out_time IS NULL
                AND clock_in_time < NOW() - INTERVAL '24 hours'
        """
        
        results = self.storage.hook.get_records(
            sql,
            parameters=(employee_id, start_date, end_date)
        )
        
        for row in results:
            discrepancies.append({
                "type": "missing_clock_out",
                "work_session_id": row[0],
                "work_date": row[1],
                "clock_in_time": row[2],
                "severity": "high"
            })
        
        # Buscar sesiones con horas muy altas (> 12 horas)
        sql = """
            SELECT id, work_date, total_hours
            FROM time_tracking_work_sessions
            WHERE employee_id = %s
                AND work_date BETWEEN %s AND %s
                AND total_hours > 12
        """
        
        results = self.storage.hook.get_records(
            sql,
            parameters=(employee_id, start_date, end_date)
        )
        
        for row in results:
            discrepancies.append({
                "type": "excessive_hours",
                "work_session_id": row[0],
                "work_date": row[1],
                "total_hours": float(row[2]),
                "severity": "medium"
            })
        
        return discrepancies

