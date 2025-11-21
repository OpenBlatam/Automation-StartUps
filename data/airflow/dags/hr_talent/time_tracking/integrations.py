"""
Integraciones con Sistemas Externos
HRIS, Sistemas de Pago, Calendarios, etc.
"""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional
from decimal import Decimal
import json

from .storage import TimeTrackingStorage

logger = logging.getLogger(__name__)


class HRISIntegration:
    """Integración con sistemas HRIS (Human Resources Information System)"""
    
    def __init__(self, storage: TimeTrackingStorage, api_key: Optional[str] = None, api_url: Optional[str] = None):
        self.storage = storage
        self.api_key = api_key
        self.api_url = api_url or "https://api.hris.example.com"
    
    def sync_employees(self) -> Dict[str, Any]:
        """Sincroniza empleados desde HRIS"""
        # Simulación de llamada API
        # En producción, usaría requests o un SDK específico
        
        logger.info("Syncing employees from HRIS...")
        
        # Obtener empleados del HRIS
        # employees = self._fetch_from_hris()
        
        # Por ahora, retornamos estructura simulada
        return {
            "synced_count": 0,
            "updated_count": 0,
            "new_count": 0,
            "errors": []
        }
    
    def sync_employee_details(self, employee_id: str) -> Dict[str, Any]:
        """Sincroniza detalles de un empleado específico"""
        # Obtener datos del HRIS
        # employee_data = self._fetch_employee_from_hris(employee_id)
        
        # Actualizar en payroll_employees
        # self._update_employee(employee_id, employee_data)
        
        return {
            "employee_id": employee_id,
            "synced": True,
            "updated_fields": []
        }
    
    def sync_vacation_balances(self) -> Dict[str, Any]:
        """Sincroniza saldos de vacaciones desde HRIS"""
        sql = """
            SELECT employee_id FROM payroll_employees
            WHERE active = true
        """
        
        employees = self.storage.hook.get_records(sql)
        synced = 0
        
        for row in employees:
            employee_id = row[0]
            # Obtener saldo del HRIS
            # balance = self._fetch_vacation_balance_from_hris(employee_id)
            
            # Actualizar en time_tracking_vacation_balances
            # self._update_vacation_balance(employee_id, balance)
            synced += 1
        
        return {
            "synced_count": synced,
            "timestamp": datetime.now().isoformat()
        }


class PayrollSystemIntegration:
    """Integración con sistemas de pago externos"""
    
    def __init__(self, storage: TimeTrackingStorage, system_type: str = "quickbooks"):
        self.storage = storage
        self.system_type = system_type
    
    def export_time_entries(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Exporta entradas de tiempo al sistema de pago"""
        sql = """
            SELECT 
                ws.work_date,
                ws.total_hours,
                ws.regular_hours,
                ws.overtime_hours,
                pe.hourly_rate
            FROM time_tracking_work_sessions ws
            JOIN payroll_employees pe ON ws.employee_id = pe.employee_id
            WHERE ws.employee_id = %s
                AND ws.work_date BETWEEN %s AND %s
                AND ws.status = 'closed'
                AND ws.approved = true
        """
        
        results = self.storage.hook.get_records(
            sql,
            parameters=(employee_id, start_date, end_date)
        )
        
        entries = []
        for row in results:
            work_date, total, regular, overtime, rate = row
            entries.append({
                "date": work_date.isoformat(),
                "hours": float(total) if total else 0.0,
                "regular_hours": float(regular) if regular else 0.0,
                "overtime_hours": float(overtime) if overtime else 0.0,
                "rate": float(rate) if rate else 0.0,
                "amount": float(total * rate) if total and rate else 0.0
            })
        
        # Exportar al sistema de pago
        # self._export_to_payroll_system(employee_id, entries)
        
        return {
            "employee_id": employee_id,
            "entries_exported": len(entries),
            "total_hours": sum(e["hours"] for e in entries),
            "total_amount": sum(e["amount"] for e in entries)
        }
    
    def sync_pay_periods(self) -> Dict[str, Any]:
        """Sincroniza períodos de pago"""
        # Obtener períodos desde el sistema de pago
        # periods = self._fetch_pay_periods()
        
        # Sincronizar con payroll_pay_periods
        # self._sync_periods(periods)
        
        return {
            "synced_periods": 0,
            "timestamp": datetime.now().isoformat()
        }


class CalendarIntegration:
    """Integración con sistemas de calendario (Google Calendar, Outlook, etc.)"""
    
    def __init__(self, storage: TimeTrackingStorage, calendar_type: str = "google"):
        self.storage = storage
        self.calendar_type = calendar_type
    
    def sync_holidays(self, year: int) -> Dict[str, Any]:
        """Sincroniza días festivos desde calendario"""
        # Obtener días festivos del calendario
        # holidays = self._fetch_holidays_from_calendar(year)
        
        # Insertar en time_tracking_holidays
        # self._insert_holidays(holidays)
        
        return {
            "year": year,
            "holidays_synced": 0,
            "timestamp": datetime.now().isoformat()
        }
    
    def create_vacation_event(
        self,
        employee_id: str,
        start_date: date,
        end_date: date,
        vacation_type: str
    ) -> Dict[str, Any]:
        """Crea evento de vacaciones en calendario"""
        # Crear evento en calendario compartido
        # event = self._create_calendar_event(
        #     title=f"Vacation: {employee_id}",
        #     start=start_date,
        #     end=end_date
        # )
        
        return {
            "employee_id": employee_id,
            "event_created": True,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }


class SlackIntegration:
    """Integración con Slack para notificaciones y comandos"""
    
    def __init__(self, storage: TimeTrackingStorage, webhook_url: Optional[str] = None):
        self.storage = storage
        self.webhook_url = webhook_url
    
    def send_slack_message(
        self,
        channel: str,
        message: str,
        blocks: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Envía mensaje a Slack"""
        # En producción, usaría requests para enviar a webhook
        # import requests
        # payload = {"text": message, "blocks": blocks}
        # response = requests.post(self.webhook_url, json=payload)
        
        logger.info(f"Sending Slack message to {channel}: {message}")
        return True
    
    def notify_team_attendance_summary(self, department: str) -> bool:
        """Envía resumen de asistencia del equipo a Slack"""
        from .analytics import TimeTrackingAnalytics
        
        analytics = TimeTrackingAnalytics(self.storage)
        team_comparison = analytics.generate_team_comparison(department=department)
        
        message = f"📊 *Attendance Summary - {department}*\n"
        message += f"Team Size: {team_comparison['team_size']}\n"
        message += f"Avg Hours: {team_comparison['team_averages']['average_hours']:.2f}\n"
        message += f"Avg Efficiency: {team_comparison['team_averages']['average_efficiency_score']:.2f}%"
        
        return self.send_slack_message(f"#{department.lower()}-attendance", message)
    
    def handle_slash_command(self, command: str, user_id: str, text: str) -> Dict[str, Any]:
        """Maneja comandos slash de Slack (/time-status, /clock-in, etc.)"""
        # Mapear user_id de Slack a employee_id
        employee_id = self._get_employee_from_slack_user(user_id)
        
        if not employee_id:
            return {"error": "Employee not found"}
        
        if command == "/time-status":
            return self._handle_time_status(employee_id)
        elif command == "/clock-in":
            return self._handle_clock_in(employee_id)
        elif command == "/clock-out":
            return self._handle_clock_out(employee_id)
        elif command == "/vacation-balance":
            return self._handle_vacation_balance(employee_id)
        else:
            return {"error": "Unknown command"}
    
    def _get_employee_from_slack_user(self, slack_user_id: str) -> Optional[str]:
        """Obtiene employee_id desde slack_user_id"""
        sql = """
            SELECT employee_id FROM payroll_employees
            WHERE metadata->>'slack_user_id' = %s
        """
        
        result = self.storage.hook.get_first(sql, parameters=(slack_user_id,))
        return result[0] if result else None
    
    def _handle_time_status(self, employee_id: str) -> Dict[str, Any]:
        """Maneja comando /time-status"""
        today = date.today()
        open_session = self.storage.get_open_session(employee_id, today)
        
        if open_session:
            hours_open = (datetime.now() - open_session['clock_in_time']).total_seconds() / 3600.0
            return {
                "text": f"⏰ You're clocked in since {open_session['clock_in_time'].strftime('%H:%M')} ({hours_open:.1f} hours)"
            }
        else:
            return {
                "text": "⏰ You're not currently clocked in"
            }
    
    def _handle_clock_in(self, employee_id: str) -> Dict[str, Any]:
        """Maneja comando /clock-in"""
        from .clock_manager import ClockManager
        from .session_manager import SessionManager
        from .hour_calculator import TimeTrackingHourCalculator
        
        clock_manager = ClockManager(self.storage)
        hour_calculator = TimeTrackingHourCalculator(self.storage)
        session_manager = SessionManager(self.storage, clock_manager, hour_calculator)
        
        session_id = session_manager.start_session(employee_id)
        
        return {
            "text": f"✅ Clocked in successfully! Session ID: {session_id}"
        }
    
    def _handle_clock_out(self, employee_id: str) -> Dict[str, Any]:
        """Maneja comando /clock-out"""
        from .session_manager import SessionManager
        from .clock_manager import ClockManager
        from .hour_calculator import TimeTrackingHourCalculator
        
        clock_manager = ClockManager(self.storage)
        hour_calculator = TimeTrackingHourCalculator(self.storage)
        session_manager = SessionManager(self.storage, clock_manager, hour_calculator)
        
        session_id = session_manager.end_session(employee_id)
        
        if session_id:
            return {
                "text": f"✅ Clocked out successfully! Session ID: {session_id}"
            }
        else:
            return {
                "text": "❌ No active session found"
            }
    
    def _handle_vacation_balance(self, employee_id: str) -> Dict[str, Any]:
        """Maneja comando /vacation-balance"""
        balance = self.storage.get_vacation_balance(employee_id)
        
        return {
            "text": f"🏖️ Vacation Balance:\n"
                   f"• Vacation Days: {float(balance['vacation_days']):.1f}\n"
                   f"• Sick Days: {float(balance['sick_days']):.1f}\n"
                   f"• Personal Days: {float(balance['personal_days']):.1f}"
        }


class IntegrationManager:
    """Gestor centralizado de todas las integraciones"""
    
    def __init__(self, storage: TimeTrackingStorage):
        self.storage = storage
        self.hris = HRISIntegration(storage)
        self.payroll = PayrollSystemIntegration(storage)
        self.calendar = CalendarIntegration(storage)
        self.slack = SlackIntegration(storage)
    
    def sync_all(self) -> Dict[str, Any]:
        """Sincroniza todas las integraciones"""
        results = {
            "hris": self.hris.sync_employees(),
            "payroll": self.payroll.sync_pay_periods(),
            "calendar": self.calendar.sync_holidays(datetime.now().year),
            "timestamp": datetime.now().isoformat()
        }
        
        return results

