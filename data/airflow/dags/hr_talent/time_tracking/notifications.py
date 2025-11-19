"""
Sistema de Notificaciones para Time Tracking
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TimeTrackingNotifier:
    """Envía notificaciones relacionadas con time tracking"""
    
    def __init__(self, storage):
        self.storage = storage
    
    def notify_missing_clock_out(self, employee_id: str, work_date: date) -> None:
        """Notifica sobre clock out faltante"""
        # Crear alerta en la base de datos
        sql = """
            INSERT INTO time_tracking_alerts (
                employee_id, alert_type, alert_severity, message,
                related_entity_type, status
            ) VALUES (
                %s, 'missing_clock_out', 'warning',
                %s, 'work_session', 'active'
            )
            ON CONFLICT DO NOTHING
        """
        
        message = f"Missing clock out for {work_date}. Please record your clock out time."
        
        try:
            self.storage.hook.run(
                sql,
                parameters=(employee_id, message)
            )
            logger.info(f"Alert created for missing clock out: employee={employee_id}, date={work_date}")
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
    
    def notify_dispute_submitted(self, employee_id: str, dispute_id: int) -> None:
        """Notifica sobre disputa enviada"""
        sql = """
            INSERT INTO time_tracking_alerts (
                employee_id, alert_type, alert_severity, message,
                related_entity_type, related_entity_id, status
            ) VALUES (
                %s, 'dispute_submitted', 'info',
                %s, 'dispute', %s, 'active'
            )
        """
        
        message = f"Time dispute submitted and awaiting review."
        
        try:
            self.storage.hook.run(
                sql,
                parameters=(employee_id, message, dispute_id)
            )
            logger.info(f"Alert created for dispute: employee={employee_id}, dispute_id={dispute_id}")
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
    
    def notify_vacation_balance_low(
        self,
        employee_id: str,
        vacation_type: str,
        remaining_days: float
    ) -> None:
        """Notifica cuando el saldo de vacaciones es bajo"""
        sql = """
            INSERT INTO time_tracking_alerts (
                employee_id, alert_type, alert_severity, message, status
            ) VALUES (
                %s, 'vacation_balance_low', 'warning',
                %s, 'active'
            )
            ON CONFLICT DO NOTHING
        """
        
        message = f"Low vacation balance: {remaining_days} {vacation_type} days remaining."
        
        try:
            self.storage.hook.run(
                sql,
                parameters=(employee_id, message)
            )
            logger.info(f"Alert created for low vacation balance: employee={employee_id}")
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
    
    def get_active_alerts(
        self,
        employee_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Obtiene alertas activas"""
        if employee_id:
            sql = """
                SELECT id, alert_type, alert_severity, message, created_at
                FROM time_tracking_alerts
                WHERE employee_id = %s AND status = 'active'
                ORDER BY created_at DESC
            """
            results = self.storage.hook.get_records(sql, parameters=(employee_id,))
        else:
            sql = """
                SELECT id, employee_id, alert_type, alert_severity, message, created_at
                FROM time_tracking_alerts
                WHERE status = 'active'
                ORDER BY created_at DESC
            """
            results = self.storage.hook.get_records(sql)
        
        alerts = []
        for row in results:
            if employee_id:
                alerts.append({
                    "id": row[0],
                    "alert_type": row[1],
                    "severity": row[2],
                    "message": row[3],
                    "created_at": row[4]
                })
            else:
                alerts.append({
                    "id": row[0],
                    "employee_id": row[1],
                    "alert_type": row[2],
                    "severity": row[3],
                    "message": row[4],
                    "created_at": row[5]
                })
        
        return alerts

