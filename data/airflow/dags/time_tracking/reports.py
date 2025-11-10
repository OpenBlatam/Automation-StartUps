"""
Sistema de Reportes Avanzados para Time Tracking
Genera reportes en múltiples formatos (PDF, Excel, CSV)
"""

import logging
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from decimal import Decimal
import io
import csv

from .storage import TimeTrackingStorage

logger = logging.getLogger(__name__)


class TimeTrackingReporter:
    """Genera reportes de time tracking"""
    
    def __init__(self, storage: TimeTrackingStorage):
        self.storage = storage
    
    def generate_daily_report(
        self,
        employee_id: str,
        report_date: date
    ) -> Dict[str, Any]:
        """Genera reporte diario detallado"""
        sql = """
            SELECT 
                ws.id,
                ws.work_date,
                ws.clock_in_time,
                ws.clock_out_time,
                ws.total_hours,
                ws.regular_hours,
                ws.overtime_hours,
                ws.break_duration_minutes,
                ws.status,
                ws.approved,
                ce_in.location as clock_in_location,
                ce_out.location as clock_out_location
            FROM time_tracking_work_sessions ws
            LEFT JOIN time_tracking_clock_events ce_in ON ws.clock_in_event_id = ce_in.id
            LEFT JOIN time_tracking_clock_events ce_out ON ws.clock_out_event_id = ce_out.id
            WHERE ws.employee_id = %s
                AND ws.work_date = %s
            ORDER BY ws.clock_in_time
        """
        
        results = self.storage.hook.get_records(
            sql,
            parameters=(employee_id, report_date)
        )
        
        sessions = []
        total_hours = Decimal("0.00")
        total_regular = Decimal("0.00")
        total_overtime = Decimal("0.00")
        
        for row in results:
            session_id, work_date, clock_in, clock_out, total, regular, overtime, breaks, status, approved, loc_in, loc_out = row
            
            sessions.append({
                "session_id": session_id,
                "clock_in_time": clock_in.isoformat() if clock_in else None,
                "clock_out_time": clock_out.isoformat() if clock_out else None,
                "total_hours": float(total) if total else 0.0,
                "regular_hours": float(regular) if regular else 0.0,
                "overtime_hours": float(overtime) if overtime else 0.0,
                "break_minutes": breaks if breaks else 0,
                "status": status,
                "approved": approved,
                "clock_in_location": loc_in,
                "clock_out_location": loc_out
            })
            
            if total:
                total_hours += Decimal(str(total))
            if regular:
                total_regular += Decimal(str(regular))
            if overtime:
                total_overtime += Decimal(str(overtime))
        
        return {
            "employee_id": employee_id,
            "report_date": report_date.isoformat(),
            "sessions": sessions,
            "summary": {
                "total_sessions": len(sessions),
                "total_hours": float(total_hours),
                "regular_hours": float(total_regular),
                "overtime_hours": float(total_overtime)
            }
        }
    
    def generate_weekly_report(
        self,
        employee_id: str,
        week_start: date
    ) -> Dict[str, Any]:
        """Genera reporte semanal"""
        week_end = week_start + timedelta(days=6)
        
        daily_reports = []
        total_hours = Decimal("0.00")
        total_regular = Decimal("0.00")
        total_overtime = Decimal("0.00")
        
        current_date = week_start
        while current_date <= week_end:
            daily_report = self.generate_daily_report(employee_id, current_date)
            daily_reports.append(daily_report)
            
            if daily_report["summary"]["total_hours"] > 0:
                total_hours += Decimal(str(daily_report["summary"]["total_hours"]))
                total_regular += Decimal(str(daily_report["summary"]["regular_hours"]))
                total_overtime += Decimal(str(daily_report["summary"]["overtime_hours"]))
            
            current_date += timedelta(days=1)
        
        return {
            "employee_id": employee_id,
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "daily_reports": daily_reports,
            "summary": {
                "total_hours": float(total_hours),
                "regular_hours": float(total_regular),
                "overtime_hours": float(total_overtime),
                "average_daily_hours": float(total_hours / 7) if total_hours > 0 else 0.0
            }
        }
    
    def generate_monthly_report(
        self,
        employee_id: str,
        year: int,
        month: int
    ) -> Dict[str, Any]:
        """Genera reporte mensual"""
        from calendar import monthrange
        
        start_date = date(year, month, 1)
        end_date = date(year, month, monthrange(year, month)[1])
        
        sql = """
            SELECT 
                ws.work_date,
                COUNT(*) as sessions_count,
                SUM(ws.total_hours) as total_hours,
                SUM(ws.regular_hours) as regular_hours,
                SUM(ws.overtime_hours) as overtime_hours
            FROM time_tracking_work_sessions ws
            WHERE ws.employee_id = %s
                AND ws.work_date BETWEEN %s AND %s
                AND ws.status = 'closed'
            GROUP BY ws.work_date
            ORDER BY ws.work_date
        """
        
        results = self.storage.hook.get_records(
            sql,
            parameters=(employee_id, start_date, end_date)
        )
        
        daily_summaries = []
        total_hours = Decimal("0.00")
        total_regular = Decimal("0.00")
        total_overtime = Decimal("0.00")
        days_worked = 0
        
        for row in results:
            work_date, sessions_count, total, regular, overtime = row
            
            daily_summaries.append({
                "date": work_date.isoformat(),
                "sessions_count": sessions_count,
                "total_hours": float(total) if total else 0.0,
                "regular_hours": float(regular) if regular else 0.0,
                "overtime_hours": float(overtime) if overtime else 0.0
            })
            
            if total:
                total_hours += Decimal(str(total))
                total_regular += Decimal(str(regular))
                total_overtime += Decimal(str(overtime))
                days_worked += 1
        
        return {
            "employee_id": employee_id,
            "year": year,
            "month": month,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily_summaries": daily_summaries,
            "summary": {
                "total_hours": float(total_hours),
                "regular_hours": float(total_regular),
                "overtime_hours": float(total_overtime),
                "days_worked": days_worked,
                "average_daily_hours": float(total_hours / days_worked) if days_worked > 0 else 0.0
            }
        }
    
    def export_to_csv(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> str:
        """Exporta datos a CSV"""
        sql = """
            SELECT 
                ws.work_date,
                ws.clock_in_time,
                ws.clock_out_time,
                ws.total_hours,
                ws.regular_hours,
                ws.overtime_hours,
                ws.break_duration_minutes,
                ws.status,
                ws.approved
            FROM time_tracking_work_sessions ws
            WHERE ws.employee_id = %s
                AND ws.work_date BETWEEN %s AND %s
            ORDER BY ws.work_date, ws.clock_in_time
        """
        
        results = self.storage.hook.get_records(
            sql,
            parameters=(employee_id, start_date, end_date)
        )
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow([
            'Date', 'Clock In', 'Clock Out', 'Total Hours',
            'Regular Hours', 'Overtime Hours', 'Break Minutes',
            'Status', 'Approved'
        ])
        
        # Data
        for row in results:
            work_date, clock_in, clock_out, total, regular, overtime, breaks, status, approved = row
            
            writer.writerow([
                work_date.isoformat() if work_date else '',
                clock_in.isoformat() if clock_in else '',
                clock_out.isoformat() if clock_out else '',
                float(total) if total else 0.0,
                float(regular) if regular else 0.0,
                float(overtime) if overtime else 0.0,
                breaks if breaks else 0,
                status,
                'Yes' if approved else 'No'
            ])
        
        return output.getvalue()
    
    def generate_attendance_stats(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Genera estadísticas de asistencia"""
        sql = """
            SELECT 
                COUNT(DISTINCT ws.work_date) as days_worked,
                COUNT(*) as total_sessions,
                SUM(ws.total_hours) as total_hours,
                AVG(ws.total_hours) as avg_hours_per_day,
                MIN(ws.clock_in_time) as earliest_clock_in,
                MAX(ws.clock_out_time) as latest_clock_out,
                COUNT(CASE WHEN ws.status = 'disputed' THEN 1 END) as disputed_sessions,
                COUNT(CASE WHEN ws.approved = false THEN 1 END) as unapproved_sessions
            FROM time_tracking_work_sessions ws
            WHERE ws.employee_id = %s
                AND ws.work_date BETWEEN %s AND %s
                AND ws.status = 'closed'
        """
        
        result = self.storage.hook.get_first(
            sql,
            parameters=(employee_id, start_date, end_date)
        )
        
        if not result:
            return {
                "employee_id": employee_id,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "stats": {
                    "days_worked": 0,
                    "total_sessions": 0,
                    "total_hours": 0.0,
                    "average_hours_per_day": 0.0,
                    "disputed_sessions": 0,
                    "unapproved_sessions": 0
                }
            }
        
        days_worked, total_sessions, total_hours, avg_hours, earliest, latest, disputed, unapproved = result
        
        return {
            "employee_id": employee_id,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "stats": {
                "days_worked": days_worked or 0,
                "total_sessions": total_sessions or 0,
                "total_hours": float(total_hours) if total_hours else 0.0,
                "average_hours_per_day": float(avg_hours) if avg_hours else 0.0,
                "earliest_clock_in": earliest.isoformat() if earliest else None,
                "latest_clock_out": latest.isoformat() if latest else None,
                "disputed_sessions": disputed or 0,
                "unapproved_sessions": unapproved or 0
            }
        }

