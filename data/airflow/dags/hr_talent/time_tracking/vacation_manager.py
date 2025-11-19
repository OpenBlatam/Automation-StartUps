"""
Gestor de Vacaciones y Permisos
"""

import logging
from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal

from .storage import TimeTrackingStorage, VacationRequest, VacationType

logger = logging.getLogger(__name__)


class VacationManager:
    """Gestiona vacaciones y permisos"""
    
    def __init__(self, storage: TimeTrackingStorage):
        self.storage = storage
    
    def request_vacation(
        self,
        employee_id: str,
        vacation_type: VacationType,
        start_date: date,
        end_date: date,
        notes: Optional[str] = None
    ) -> int:
        """
        Solicita vacaciones
        
        Returns:
            ID de la solicitud creada
        """
        # Calcular días solicitados
        days_requested = Decimal(str((end_date - start_date).days + 1))
        
        # Verificar saldo disponible
        balance = self.storage.get_vacation_balance(employee_id)
        
        if vacation_type == VacationType.VACATION:
            available = balance["vacation_days"]
        elif vacation_type == VacationType.SICK:
            available = balance["sick_days"]
        elif vacation_type == VacationType.PERSONAL:
            available = balance["personal_days"]
        else:
            available = Decimal("999")  # Otros tipos pueden no tener límite
        
        if days_requested > available:
            logger.warning(
                f"Requested {days_requested} days but only {available} available "
                f"for employee {employee_id}"
            )
        
        request = VacationRequest(
            employee_id=employee_id,
            vacation_type=vacation_type,
            start_date=start_date,
            end_date=end_date,
            days_requested=days_requested,
            notes=notes
        )
        
        request_id = self.storage.save_vacation_request(request)
        logger.info(
            f"Vacation request created for employee {employee_id}, "
            f"{days_requested} days from {start_date} to {end_date}"
        )
        
        return request_id
    
    def approve_vacation(
        self,
        request_id: int,
        approved_by: str,
        days_approved: Optional[Decimal] = None
    ) -> bool:
        """Aprueba una solicitud de vacaciones"""
        # Primero obtener la solicitud
        sql = """
            SELECT employee_id, vacation_type, days_requested
            FROM time_tracking_vacations
            WHERE id = %s AND status = 'pending'
        """
        
        result = self.storage.hook.get_first(sql, parameters=(request_id,))
        if not result:
            logger.error(f"Vacation request {request_id} not found or not pending")
            return False
        
        employee_id = result[0]
        vacation_type = result[1]
        days_requested = Decimal(str(result[2]))
        
        if days_approved is None:
            days_approved = days_requested
        
        # Actualizar solicitud
        update_sql = """
            UPDATE time_tracking_vacations
            SET status = 'approved',
                approved_by = %s,
                approved_at = NOW(),
                days_approved = %s
            WHERE id = %s
        """
        
        self.storage.hook.run(
            update_sql,
            parameters=(approved_by, float(days_approved), request_id)
        )
        
        # Actualizar saldo de vacaciones
        self._update_vacation_balance(employee_id, vacation_type, -days_approved)
        
        logger.info(f"Vacation request {request_id} approved by {approved_by}")
        return True
    
    def reject_vacation(
        self,
        request_id: int,
        rejected_by: str,
        reason: Optional[str] = None
    ) -> bool:
        """Rechaza una solicitud de vacaciones"""
        update_sql = """
            UPDATE time_tracking_vacations
            SET status = 'rejected',
                rejected_by = %s,
                rejected_at = NOW(),
                rejection_reason = %s
            WHERE id = %s
        """
        
        self.storage.hook.run(
            update_sql,
            parameters=(rejected_by, reason, request_id)
        )
        
        logger.info(f"Vacation request {request_id} rejected by {rejected_by}")
        return True
    
    def _update_vacation_balance(
        self,
        employee_id: str,
        vacation_type: VacationType,
        days_change: Decimal
    ) -> None:
        """Actualiza el saldo de vacaciones"""
        year = date.today().year
        
        # Determinar qué columna actualizar
        if vacation_type == VacationType.VACATION:
            balance_column = "vacation_days_available"
            used_column = "vacation_days_used"
        elif vacation_type == VacationType.SICK:
            balance_column = "sick_days_available"
            used_column = "sick_days_used"
        elif vacation_type == VacationType.PERSONAL:
            balance_column = "personal_days_available"
            used_column = "personal_days_used"
        else:
            return
        
        # Insertar o actualizar saldo
        sql = f"""
            INSERT INTO time_tracking_vacation_balances (
                employee_id, year, {balance_column}, {used_column}
            ) VALUES (
                %s, %s, GREATEST(0, %s), GREATEST(0, %s)
            )
            ON CONFLICT (employee_id) DO UPDATE SET
                {balance_column} = GREATEST(0, time_tracking_vacation_balances.{balance_column} + %s),
                {used_column} = time_tracking_vacation_balances.{used_column} + GREATEST(0, %s),
                updated_at = NOW()
        """
        
        # Si days_change es negativo (usando días), actualizar used y reducir available
        if days_change < 0:
            used_change = abs(days_change)
            available_change = days_change
        else:
            used_change = Decimal("0")
            available_change = days_change
        
        self.storage.hook.run(
            sql,
            parameters=(
                employee_id,
                year,
                float(available_change),
                float(used_change),
                float(available_change),
                float(used_change)
            )
        )
    
    def get_pending_requests(self, employee_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtiene solicitudes pendientes"""
        if employee_id:
            sql = """
                SELECT id, employee_id, vacation_type, start_date, end_date,
                       days_requested, status, requested_at
                FROM time_tracking_vacations
                WHERE employee_id = %s AND status = 'pending'
                ORDER BY requested_at DESC
            """
            results = self.storage.hook.get_records(sql, parameters=(employee_id,))
        else:
            sql = """
                SELECT id, employee_id, vacation_type, start_date, end_date,
                       days_requested, status, requested_at
                FROM time_tracking_vacations
                WHERE status = 'pending'
                ORDER BY requested_at DESC
            """
            results = self.storage.hook.get_records(sql)
        
        requests = []
        for row in results:
            requests.append({
                "id": row[0],
                "employee_id": row[1],
                "vacation_type": row[2],
                "start_date": row[3],
                "end_date": row[4],
                "days_requested": float(row[5]),
                "status": row[6],
                "requested_at": row[7]
            })
        
        return requests

