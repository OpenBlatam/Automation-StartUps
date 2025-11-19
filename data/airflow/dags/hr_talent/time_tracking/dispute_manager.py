"""
Gestor de Disputas de Tiempo
"""

import logging
from datetime import date
from typing import List, Optional, Dict, Any
from decimal import Decimal

from .storage import TimeTrackingStorage, TimeDispute, DisputeType, SessionStatus

logger = logging.getLogger(__name__)


class DisputeManager:
    """Gestiona disputas de tiempo trabajado"""
    
    def __init__(self, storage: TimeTrackingStorage):
        self.storage = storage
    
    def submit_dispute(
        self,
        employee_id: str,
        dispute_type: DisputeType,
        dispute_date: date,
        description: str,
        work_session_id: Optional[int] = None,
        requested_hours: Optional[Decimal] = None,
        current_hours: Optional[Decimal] = None,
        evidence_urls: Optional[List[str]] = None
    ) -> int:
        """
        Envía una disputa de tiempo
        
        Returns:
            ID de la disputa creada
        """
        dispute = TimeDispute(
            employee_id=employee_id,
            dispute_type=dispute_type,
            dispute_date=dispute_date,
            description=description,
            requested_hours=requested_hours,
            current_hours=current_hours,
            evidence_urls=evidence_urls
        )
        
        dispute_id = self.storage.save_dispute(dispute, work_session_id)
        
        # Marcar sesión como disputada si aplica
        if work_session_id:
            self._mark_session_as_disputed(work_session_id)
        
        logger.info(
            f"Time dispute submitted by employee {employee_id} "
            f"for date {dispute_date}, dispute_id={dispute_id}"
        )
        
        return dispute_id
    
    def resolve_dispute(
        self,
        dispute_id: int,
        resolved_by: str,
        resolution_action: str,
        resolution_notes: Optional[str] = None,
        approved_hours: Optional[Decimal] = None
    ) -> bool:
        """
        Resuelve una disputa
        
        Args:
            resolution_action: 'approved', 'adjusted', 'rejected', 'forwarded'
        """
        # Obtener información de la disputa
        sql = """
            SELECT employee_id, work_session_id, requested_hours, current_hours
            FROM time_tracking_disputes
            WHERE id = %s AND status IN ('open', 'under_review')
        """
        
        result = self.storage.hook.get_first(sql, parameters=(dispute_id,))
        if not result:
            logger.error(f"Dispute {dispute_id} not found or already resolved")
            return False
        
        employee_id = result[0]
        work_session_id = result[1]
        requested_hours = Decimal(str(result[2])) if result[2] else None
        current_hours = Decimal(str(result[3])) if result[3] else None
        
        # Actualizar disputa
        update_sql = """
            UPDATE time_tracking_disputes
            SET status = 'resolved',
                resolved_by = %s,
                resolved_at = NOW(),
                resolution_notes = %s,
                resolution_action = %s
            WHERE id = %s
        """
        
        self.storage.hook.run(
            update_sql,
            parameters=(resolved_by, resolution_notes, resolution_action, dispute_id)
        )
        
        # Si se aprobó, actualizar sesión de trabajo
        if resolution_action == "approved" and work_session_id and approved_hours:
            self._update_session_hours(work_session_id, approved_hours)
        
        logger.info(
            f"Dispute {dispute_id} resolved by {resolved_by} with action {resolution_action}"
        )
        
        return True
    
    def _mark_session_as_disputed(self, work_session_id: int) -> None:
        """Marca una sesión como disputada"""
        sql = """
            UPDATE time_tracking_work_sessions
            SET status = 'disputed', disputed = true
            WHERE id = %s
        """
        
        self.storage.hook.run(sql, parameters=(work_session_id,))
    
    def _update_session_hours(self, work_session_id: int, approved_hours: Decimal) -> None:
        """Actualiza las horas de una sesión después de resolver disputa"""
        # Recalcular horas regulares y overtime
        from .hour_calculator import TimeTrackingHourCalculator
        
        calculator = TimeTrackingHourCalculator(self.storage)
        
        # Obtener información de la sesión
        sql = """
            SELECT clock_in_time, clock_out_time, break_duration_minutes, employee_id
            FROM time_tracking_work_sessions
            WHERE id = %s
        """
        
        result = self.storage.hook.get_first(sql, parameters=(work_session_id,))
        if not result:
            return
        
        clock_in_time = result[0]
        clock_out_time = result[1]
        break_minutes = result[2] if result[2] else 0
        employee_id = result[3]
        
        # Recalcular
        total_hours, regular_hours, overtime_hours = calculator.calculate_hours(
            clock_in_time=clock_in_time,
            clock_out_time=clock_out_time,
            break_minutes=break_minutes,
            employee_id=employee_id
        )
        
        # Actualizar con horas aprobadas
        self.storage.update_work_session(
            session_id=work_session_id,
            total_hours=approved_hours,
            regular_hours=regular_hours if approved_hours >= regular_hours else approved_hours,
            overtime_hours=overtime_hours if approved_hours > regular_hours else Decimal("0.00"),
            status=SessionStatus.APPROVED
        )
    
    def get_disputes(
        self,
        employee_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Obtiene disputas"""
        if employee_id:
            if status:
                sql = """
                    SELECT id, employee_id, dispute_type, dispute_date,
                           description, status, priority, submitted_at
                    FROM time_tracking_disputes
                    WHERE employee_id = %s AND status = %s
                    ORDER BY priority DESC, dispute_date DESC
                """
                results = self.storage.hook.get_records(sql, parameters=(employee_id, status))
            else:
                sql = """
                    SELECT id, employee_id, dispute_type, dispute_date,
                           description, status, priority, submitted_at
                    FROM time_tracking_disputes
                    WHERE employee_id = %s
                    ORDER BY priority DESC, dispute_date DESC
                """
                results = self.storage.hook.get_records(sql, parameters=(employee_id,))
        else:
            if status:
                sql = """
                    SELECT id, employee_id, dispute_type, dispute_date,
                           description, status, priority, submitted_at
                    FROM time_tracking_disputes
                    WHERE status = %s
                    ORDER BY priority DESC, dispute_date DESC
                """
                results = self.storage.hook.get_records(sql, parameters=(status,))
            else:
                sql = """
                    SELECT id, employee_id, dispute_type, dispute_date,
                           description, status, priority, submitted_at
                    FROM time_tracking_disputes
                    ORDER BY priority DESC, dispute_date DESC
                """
                results = self.storage.hook.get_records(sql)
        
        disputes = []
        for row in results:
            disputes.append({
                "id": row[0],
                "employee_id": row[1],
                "dispute_type": row[2],
                "dispute_date": row[3],
                "description": row[4],
                "status": row[5],
                "priority": row[6],
                "submitted_at": row[7]
            })
        
        return disputes

