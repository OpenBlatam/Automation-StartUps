"""
Detector de Anomalías en Time Tracking
Detecta patrones sospechosos y posibles fraudes
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from decimal import Decimal
from collections import defaultdict

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Detecta anomalías y patrones sospechosos"""
    
    def __init__(self, storage):
        self.storage = storage
    
    def detect_anomalies(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Detecta múltiples tipos de anomalías
        
        Returns:
            Lista de anomalías detectadas
        """
        anomalies = []
        
        # 1. Detectar clock in/out muy tempranos o muy tardíos
        anomalies.extend(self._detect_unusual_times(employee_id, start_date, end_date))
        
        # 2. Detectar sesiones muy cortas o muy largas
        anomalies.extend(self._detect_unusual_durations(employee_id, start_date, end_date))
        
        # 3. Detectar múltiples clock in/out en el mismo día
        anomalies.extend(self._detect_multiple_sessions(employee_id, start_date, end_date))
        
        # 4. Detectar patrones de ausencia
        anomalies.extend(self._detect_absence_patterns(employee_id, start_date, end_date))
        
        # 5. Detectar horas excesivas
        anomalies.extend(self._detect_excessive_hours(employee_id, start_date, end_date))
        
        # 6. Detectar ubicaciones inconsistentes
        anomalies.extend(self._detect_location_inconsistencies(employee_id, start_date, end_date))
        
        return anomalies
    
    def _detect_unusual_times(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Detecta clock in/out en horarios inusuales"""
        anomalies = []
        
        sql = """
            SELECT 
                ws.id,
                ws.work_date,
                ws.clock_in_time,
                ws.clock_out_time,
                ts.start_time,
                ts.end_time
            FROM time_tracking_work_sessions ws
            LEFT JOIN time_tracking_schedules ts ON ws.employee_id = ts.employee_id
                AND ts.is_active = true
                AND (ts.day_of_week = EXTRACT(DOW FROM ws.work_date) OR ts.day_of_week IS NULL)
            WHERE ws.employee_id = %s
                AND ws.work_date BETWEEN %s AND %s
                AND ws.status = 'closed'
        """
        
        results = self.storage.hook.get_records(
            sql,
            parameters=(employee_id, start_date, end_date)
        )
        
        for row in results:
            session_id, work_date, clock_in, clock_out, expected_start, expected_end = row
            
            if clock_in and expected_start:
                clock_in_time = clock_in.time() if isinstance(clock_in, datetime) else clock_in
                expected_start_time = expected_start if isinstance(expected_start, time) else expected_start
                
                # Verificar si clock in es muy temprano o muy tardío
                if clock_in_time < expected_start_time:
                    diff_minutes = (
                        (expected_start_time.hour * 60 + expected_start_time.minute) -
                        (clock_in_time.hour * 60 + clock_in_time.minute)
                    )
                    if diff_minutes > 60:  # Más de 1 hora antes
                        anomalies.append({
                            "type": "early_clock_in",
                            "severity": "medium",
                            "work_session_id": session_id,
                            "work_date": work_date,
                            "message": f"Clock in {diff_minutes} minutes before scheduled time",
                            "clock_in_time": clock_in_time,
                            "expected_time": expected_start_time
                        })
            
            if clock_out and expected_end:
                clock_out_time = clock_out.time() if isinstance(clock_out, datetime) else clock_out
                expected_end_time = expected_end if isinstance(expected_end, time) else expected_end
                
                # Verificar si clock out es muy temprano o muy tardío
                if clock_out_time > expected_end_time:
                    diff_minutes = (
                        (clock_out_time.hour * 60 + clock_out_time.minute) -
                        (expected_end_time.hour * 60 + expected_end_time.minute)
                    )
                    if diff_minutes > 120:  # Más de 2 horas después
                        anomalies.append({
                            "type": "late_clock_out",
                            "severity": "low",
                            "work_session_id": session_id,
                            "work_date": work_date,
                            "message": f"Clock out {diff_minutes} minutes after scheduled time",
                            "clock_out_time": clock_out_time,
                            "expected_time": expected_end_time
                        })
        
        return anomalies
    
    def _detect_unusual_durations(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Detecta sesiones con duraciones inusuales"""
        anomalies = []
        
        sql = """
            SELECT id, work_date, total_hours
            FROM time_tracking_work_sessions
            WHERE employee_id = %s
                AND work_date BETWEEN %s AND %s
                AND status = 'closed'
        """
        
        results = self.storage.hook.get_records(
            sql,
            parameters=(employee_id, start_date, end_date)
        )
        
        for row in results:
            session_id, work_date, total_hours = row
            hours = float(total_hours) if total_hours else 0
            
            # Sesiones muy cortas (< 2 horas) pueden ser errores
            if 0 < hours < 2:
                anomalies.append({
                    "type": "short_session",
                    "severity": "medium",
                    "work_session_id": session_id,
                    "work_date": work_date,
                    "message": f"Very short session: {hours} hours",
                    "total_hours": hours
                })
            
            # Sesiones muy largas (> 14 horas) pueden ser errores o trabajo excesivo
            if hours > 14:
                anomalies.append({
                    "type": "very_long_session",
                    "severity": "high",
                    "work_session_id": session_id,
                    "work_date": work_date,
                    "message": f"Very long session: {hours} hours",
                    "total_hours": hours
                })
        
        return anomalies
    
    def _detect_multiple_sessions(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Detecta múltiples sesiones en el mismo día"""
        anomalies = []
        
        sql = """
            SELECT work_date, COUNT(*) as session_count
            FROM time_tracking_work_sessions
            WHERE employee_id = %s
                AND work_date BETWEEN %s AND %s
            GROUP BY work_date
            HAVING COUNT(*) > 1
        """
        
        results = self.storage.hook.get_records(
            sql,
            parameters=(employee_id, start_date, end_date)
        )
        
        for row in results:
            work_date, count = row
            if count > 2:  # Más de 2 sesiones en un día es inusual
                anomalies.append({
                    "type": "multiple_sessions",
                    "severity": "medium",
                    "work_date": work_date,
                    "message": f"{count} sessions in the same day",
                    "session_count": count
                })
        
        return anomalies
    
    def _detect_absence_patterns(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Detecta patrones de ausencia inusuales"""
        anomalies = []
        
        # Obtener días trabajados
        sql = """
            SELECT DISTINCT work_date
            FROM time_tracking_work_sessions
            WHERE employee_id = %s
                AND work_date BETWEEN %s AND %s
                AND status = 'closed'
            ORDER BY work_date
        """
        
        results = self.storage.hook.get_records(
            sql,
            parameters=(employee_id, start_date, end_date)
        )
        
        worked_days = {row[0] for row in results}
        
        # Encontrar períodos largos sin trabajo
        current_date = start_date
        consecutive_days_off = 0
        max_consecutive = 0
        
        while current_date <= end_date:
            if current_date not in worked_days:
                # Verificar si no es fin de semana
                if current_date.weekday() < 5:  # Lunes a Viernes
                    consecutive_days_off += 1
                    max_consecutive = max(max_consecutive, consecutive_days_off)
            else:
                consecutive_days_off = 0
            
            current_date += timedelta(days=1)
        
        # Si hay más de 5 días hábiles consecutivos sin trabajo, puede ser anomalía
        if max_consecutive > 5:
            anomalies.append({
                "type": "extended_absence",
                "severity": "low",
                "message": f"{max_consecutive} consecutive business days without work",
                "consecutive_days": max_consecutive
            })
        
        return anomalies
    
    def _detect_excessive_hours(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Detecta horas excesivas en períodos"""
        anomalies = []
        
        # Verificar horas diarias
        sql = """
            SELECT work_date, SUM(total_hours) as daily_hours
            FROM time_tracking_work_sessions
            WHERE employee_id = %s
                AND work_date BETWEEN %s AND %s
                AND status = 'closed'
            GROUP BY work_date
            HAVING SUM(total_hours) > 16
        """
        
        results = self.storage.hook.get_records(
            sql,
            parameters=(employee_id, start_date, end_date)
        )
        
        for row in results:
            work_date, daily_hours = row
            anomalies.append({
                "type": "excessive_daily_hours",
                "severity": "high",
                "work_date": work_date,
                "message": f"Excessive hours in one day: {float(daily_hours)} hours",
                "daily_hours": float(daily_hours)
            })
        
        # Verificar horas semanales
        sql = """
            SELECT 
                DATE_TRUNC('week', work_date) as week_start,
                SUM(total_hours) as weekly_hours
            FROM time_tracking_work_sessions
            WHERE employee_id = %s
                AND work_date BETWEEN %s AND %s
                AND status = 'closed'
            GROUP BY DATE_TRUNC('week', work_date)
            HAVING SUM(total_hours) > 60
        """
        
        results = self.storage.hook.get_records(
            sql,
            parameters=(employee_id, start_date, end_date)
        )
        
        for row in results:
            week_start, weekly_hours = row
            anomalies.append({
                "type": "excessive_weekly_hours",
                "severity": "high",
                "week_start": week_start,
                "message": f"Excessive hours in week: {float(weekly_hours)} hours",
                "weekly_hours": float(weekly_hours)
            })
        
        return anomalies
    
    def _detect_location_inconsistencies(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Detecta inconsistencias en ubicaciones"""
        anomalies = []
        
        sql = """
            SELECT 
                ws.id,
                ws.work_date,
                ce_in.location as clock_in_location,
                ce_out.location as clock_out_location
            FROM time_tracking_work_sessions ws
            JOIN time_tracking_clock_events ce_in ON ws.clock_in_event_id = ce_in.id
            LEFT JOIN time_tracking_clock_events ce_out ON ws.clock_out_event_id = ce_out.id
            WHERE ws.employee_id = %s
                AND ws.work_date BETWEEN %s AND %s
                AND ws.status = 'closed'
        """
        
        results = self.storage.hook.get_records(
            sql,
            parameters=(employee_id, start_date, end_date)
        )
        
        for row in results:
            session_id, work_date, clock_in_loc, clock_out_loc = row
            
            if clock_in_loc and clock_out_loc and clock_in_loc != clock_out_loc:
                # Verificar si las ubicaciones están muy lejos
                # Esto requeriría cálculo de distancia, por ahora solo notificar
                anomalies.append({
                    "type": "location_mismatch",
                    "severity": "medium",
                    "work_session_id": session_id,
                    "work_date": work_date,
                    "message": f"Different locations: in={clock_in_loc}, out={clock_out_loc}",
                    "clock_in_location": clock_in_loc,
                    "clock_out_location": clock_out_loc
                })
        
        return anomalies

