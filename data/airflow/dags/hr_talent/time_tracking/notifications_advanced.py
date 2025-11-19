"""
Sistema Avanzado de Notificaciones
Soporte para múltiples canales: Email, SMS, Push, Slack, etc.
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import json

from .storage import TimeTrackingStorage

logger = logging.getLogger(__name__)


class AdvancedNotifier:
    """Sistema avanzado de notificaciones multi-canal"""
    
    def __init__(self, storage: TimeTrackingStorage):
        self.storage = storage
    
    def send_notification(
        self,
        employee_id: str,
        notification_type: str,
        message: str,
        channels: List[str] = None,
        priority: str = "normal",
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Envía notificación por múltiples canales
        
        Args:
            channels: Lista de canales ['email', 'sms', 'push', 'slack']
            priority: 'low', 'normal', 'high', 'urgent'
        """
        if channels is None:
            channels = ['email']
        
        # Obtener preferencias del empleado
        preferences = self._get_notification_preferences(employee_id)
        
        # Filtrar canales según preferencias
        enabled_channels = [ch for ch in channels if ch in preferences.get('enabled_channels', channels)]
        
        if not enabled_channels:
            logger.warning(f"No enabled notification channels for employee {employee_id}")
            return False
        
        success_count = 0
        
        # Enviar por cada canal
        for channel in enabled_channels:
            try:
                if channel == 'email':
                    success = self._send_email(employee_id, notification_type, message, priority, metadata)
                elif channel == 'sms':
                    success = self._send_sms(employee_id, notification_type, message, priority, metadata)
                elif channel == 'push':
                    success = self._send_push(employee_id, notification_type, message, priority, metadata)
                elif channel == 'slack':
                    success = self._send_slack(employee_id, notification_type, message, priority, metadata)
                else:
                    logger.warning(f"Unknown notification channel: {channel}")
                    continue
                
                if success:
                    success_count += 1
                    
            except Exception as e:
                logger.error(f"Error sending {channel} notification: {e}")
        
        # Registrar en base de datos
        self._log_notification(employee_id, notification_type, message, enabled_channels, success_count)
        
        return success_count > 0
    
    def _get_notification_preferences(self, employee_id: str) -> Dict[str, Any]:
        """Obtiene preferencias de notificación del empleado"""
        sql = """
            SELECT notification_preferences
            FROM payroll_employees
            WHERE employee_id = %s
        """
        
        result = self.storage.hook.get_first(sql, parameters=(employee_id,))
        
        if result and result[0]:
            try:
                return json.loads(result[0]) if isinstance(result[0], str) else result[0]
            except:
                pass
        
        # Defaults
        return {
            "enabled_channels": ["email"],
            "email_enabled": True,
            "sms_enabled": False,
            "push_enabled": False,
            "slack_enabled": False
        }
    
    def _send_email(
        self,
        employee_id: str,
        notification_type: str,
        message: str,
        priority: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Envía notificación por email"""
        # Obtener email del empleado
        sql = """
            SELECT email FROM payroll_employees
            WHERE employee_id = %s
        """
        
        result = self.storage.hook.get_first(sql, parameters=(employee_id,))
        if not result or not result[0]:
            logger.error(f"No email found for employee {employee_id}")
            return False
        
        email = result[0]
        
        # Aquí iría la lógica real de envío de email
        # Por ahora, solo logueamos
        logger.info(f"Sending email to {email}: {message}")
        
        # En producción, usaría un servicio como SendGrid, AWS SES, etc.
        # send_email(to=email, subject=f"Time Tracking: {notification_type}", body=message)
        
        return True
    
    def _send_sms(
        self,
        employee_id: str,
        notification_type: str,
        message: str,
        priority: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Envía notificación por SMS"""
        # Obtener teléfono del empleado
        sql = """
            SELECT phone FROM payroll_employees
            WHERE employee_id = %s
        """
        
        result = self.storage.hook.get_first(sql, parameters=(employee_id,))
        if not result or not result[0]:
            logger.error(f"No phone found for employee {employee_id}")
            return False
        
        phone = result[0]
        
        logger.info(f"Sending SMS to {phone}: {message}")
        
        # En producción, usaría un servicio como Twilio, AWS SNS, etc.
        # send_sms(to=phone, message=message)
        
        return True
    
    def _send_push(
        self,
        employee_id: str,
        notification_type: str,
        message: str,
        priority: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Envía notificación push"""
        logger.info(f"Sending push notification to {employee_id}: {message}")
        
        # En producción, usaría Firebase Cloud Messaging, AWS SNS, etc.
        # send_push_notification(user_id=employee_id, message=message, priority=priority)
        
        return True
    
    def _send_slack(
        self,
        employee_id: str,
        notification_type: str,
        message: str,
        priority: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Envía notificación a Slack"""
        logger.info(f"Sending Slack notification for {employee_id}: {message}")
        
        # En producción, usaría Slack Webhook API
        # send_slack_message(channel="#time-tracking", text=message)
        
        return True
    
    def _log_notification(
        self,
        employee_id: str,
        notification_type: str,
        message: str,
        channels: List[str],
        success_count: int
    ) -> None:
        """Registra notificación en base de datos"""
        sql = """
            INSERT INTO time_tracking_alerts (
                employee_id, alert_type, alert_severity, message,
                metadata, status
            ) VALUES (
                %s, %s, %s, %s, %s, 'active'
            )
        """
        
        metadata = {
            "channels": channels,
            "channels_sent": success_count,
            "sent_at": datetime.now().isoformat()
        }
        
        try:
            self.storage.hook.run(
                sql,
                parameters=(
                    employee_id,
                    notification_type,
                    "info",
                    message,
                    json.dumps(metadata)
                )
            )
        except Exception as e:
            logger.error(f"Error logging notification: {e}")
    
    def notify_missing_clock_out_advanced(
        self,
        employee_id: str,
        work_date: date,
        hours_open: float
    ) -> bool:
        """Notifica sobre clock out faltante con múltiples canales"""
        message = f"Missing clock out for {work_date}. You've been clocked in for {hours_open:.1f} hours."
        
        # Determinar prioridad basada en horas abiertas
        if hours_open > 12:
            priority = "urgent"
            channels = ['email', 'sms', 'push']
        elif hours_open > 8:
            priority = "high"
            channels = ['email', 'push']
        else:
            priority = "normal"
            channels = ['email']
        
        return self.send_notification(
            employee_id=employee_id,
            notification_type="missing_clock_out",
            message=message,
            channels=channels,
            priority=priority
        )
    
    def notify_dispute_resolved(
        self,
        employee_id: str,
        dispute_id: int,
        resolution: str
    ) -> bool:
        """Notifica sobre resolución de disputa"""
        message = f"Your time dispute #{dispute_id} has been resolved: {resolution}"
        
        return self.send_notification(
            employee_id=employee_id,
            notification_type="dispute_resolved",
            message=message,
            channels=['email', 'push'],
            priority="normal"
        )
    
    def send_daily_summary(
        self,
        employee_id: str,
        summary_date: date
    ) -> bool:
        """Envía resumen diario al empleado"""
        from .reports import TimeTrackingReporter
        
        reporter = TimeTrackingReporter(self.storage)
        daily_report = reporter.generate_daily_report(employee_id, summary_date)
        
        total_hours = daily_report["summary"]["total_hours"]
        sessions = daily_report["summary"]["total_sessions"]
        
        message = f"Daily Summary for {summary_date}: {sessions} session(s), {total_hours:.2f} total hours"
        
        return self.send_notification(
            employee_id=employee_id,
            notification_type="daily_summary",
            message=message,
            channels=['email'],
            priority="low",
            metadata={"report": daily_report}
        )

