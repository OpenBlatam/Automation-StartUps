"""
Analytics Avanzado y Predicciones para Time Tracking
Análisis de tendencias, predicciones y métricas avanzadas
"""

import logging
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
from collections import defaultdict
import statistics

from .storage import TimeTrackingStorage

logger = logging.getLogger(__name__)


class TimeTrackingAnalytics:
    """Analytics avanzado para time tracking"""
    
    def __init__(self, storage: TimeTrackingStorage):
        self.storage = storage
    
    def calculate_punctuality_score(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Calcula puntuación de puntualidad
        
        Returns:
            Dict con score (0-100) y detalles
        """
        sql = """
            SELECT 
                ws.work_date,
                ws.clock_in_time,
                ts.start_time,
                EXTRACT(EPOCH FROM (ws.clock_in_time::time - ts.start_time)) / 60 as minutes_late
            FROM time_tracking_work_sessions ws
            LEFT JOIN time_tracking_schedules ts ON ws.employee_id = ts.employee_id
                AND ts.is_active = true
                AND (ts.day_of_week = EXTRACT(DOW FROM ws.work_date) OR ts.day_of_week IS NULL)
            WHERE ws.employee_id = %s
                AND ws.work_date BETWEEN %s AND %s
                AND ws.status = 'closed'
                AND ws.clock_in_time IS NOT NULL
                AND ts.start_time IS NOT NULL
            ORDER BY ws.work_date
        """
        
        results = self.storage.hook.get_records(
            sql,
            parameters=(employee_id, start_date, end_date)
        )
        
        if not results:
            return {
                "employee_id": employee_id,
                "score": 0,
                "total_days": 0,
                "on_time_days": 0,
                "late_days": 0,
                "average_minutes_late": 0.0
            }
        
        total_days = len(results)
        on_time_days = 0
        late_days = 0
        late_minutes = []
        
        for row in results:
            work_date, clock_in, expected_start, minutes_late = row
            
            if minutes_late is None:
                continue
            
            if minutes_late <= 5:  # Tolerancia de 5 minutos
                on_time_days += 1
            else:
                late_days += 1
                late_minutes.append(float(minutes_late))
        
        score = (on_time_days / total_days * 100) if total_days > 0 else 0
        avg_late = statistics.mean(late_minutes) if late_minutes else 0.0
        
        return {
            "employee_id": employee_id,
            "score": round(score, 2),
            "total_days": total_days,
            "on_time_days": on_time_days,
            "late_days": late_days,
            "average_minutes_late": round(avg_late, 2),
            "max_minutes_late": round(max(late_minutes), 2) if late_minutes else 0.0
        }
    
    def analyze_work_patterns(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Analiza patrones de trabajo"""
        sql = """
            SELECT 
                ws.work_date,
                EXTRACT(HOUR FROM ws.clock_in_time) as clock_in_hour,
                EXTRACT(HOUR FROM ws.clock_out_time) as clock_out_hour,
                ws.total_hours,
                ws.break_duration_minutes
            FROM time_tracking_work_sessions ws
            WHERE ws.employee_id = %s
                AND ws.work_date BETWEEN %s AND %s
                AND ws.status = 'closed'
            ORDER BY ws.work_date
        """
        
        results = self.storage.hook.get_records(
            sql,
            parameters=(employee_id, start_date, end_date)
        )
        
        clock_in_hours = []
        clock_out_hours = []
        total_hours_list = []
        break_durations = []
        
        for row in results:
            work_date, ci_hour, co_hour, total, breaks = row
            if ci_hour:
                clock_in_hours.append(float(ci_hour))
            if co_hour:
                clock_out_hours.append(float(co_hour))
            if total:
                total_hours_list.append(float(total))
            if breaks:
                break_durations.append(breaks)
        
        patterns = {
            "employee_id": employee_id,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "clock_in_patterns": {
                "average_hour": round(statistics.mean(clock_in_hours), 2) if clock_in_hours else None,
                "most_common_hour": self._most_common(clock_in_hours) if clock_in_hours else None,
                "earliest_hour": round(min(clock_in_hours), 2) if clock_in_hours else None,
                "latest_hour": round(max(clock_in_hours), 2) if clock_in_hours else None
            },
            "clock_out_patterns": {
                "average_hour": round(statistics.mean(clock_out_hours), 2) if clock_out_hours else None,
                "most_common_hour": self._most_common(clock_out_hours) if clock_out_hours else None,
                "earliest_hour": round(min(clock_out_hours), 2) if clock_out_hours else None,
                "latest_hour": round(max(clock_out_hours), 2) if clock_out_hours else None
            },
            "hours_patterns": {
                "average_hours": round(statistics.mean(total_hours_list), 2) if total_hours_list else None,
                "median_hours": round(statistics.median(total_hours_list), 2) if total_hours_list else None,
                "min_hours": round(min(total_hours_list), 2) if total_hours_list else None,
                "max_hours": round(max(total_hours_list), 2) if total_hours_list else None
            },
            "break_patterns": {
                "average_minutes": round(statistics.mean(break_durations), 2) if break_durations else None,
                "total_break_minutes": sum(break_durations) if break_durations else 0
            }
        }
        
        return patterns
    
    def _most_common(self, values: List[float]) -> Optional[float]:
        """Encuentra el valor más común"""
        if not values:
            return None
        
        from collections import Counter
        counter = Counter([round(v) for v in values])
        return float(counter.most_common(1)[0][0])
    
    def predict_absenteeism(
        self,
        employee_id: str,
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """
        Predice probabilidad de ausentismo basado en patrones históricos
        
        Returns:
            Dict con predicciones por día
        """
        # Obtener historial de los últimos 90 días
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        
        sql = """
            SELECT work_date
            FROM time_tracking_work_sessions
            WHERE employee_id = %s
                AND work_date BETWEEN %s AND %s
                AND status = 'closed'
            GROUP BY work_date
            ORDER BY work_date
        """
        
        results = self.storage.hook.get_records(
            sql,
            parameters=(employee_id, start_date, end_date)
        )
        
        worked_days = {row[0] for row in results}
        
        # Calcular tasa de asistencia
        total_days = (end_date - start_date).days
        attendance_rate = len(worked_days) / total_days if total_days > 0 else 0
        
        # Identificar patrones (días de la semana más propensos a ausencia)
        absence_patterns = defaultdict(int)
        current_date = start_date
        while current_date <= end_date:
            if current_date not in worked_days and current_date.weekday() < 5:  # Lunes a Viernes
                day_name = current_date.strftime('%A')
                absence_patterns[day_name] += 1
            current_date += timedelta(days=1)
        
        # Generar predicciones
        predictions = []
        prediction_date = date.today() + timedelta(days=1)
        
        for i in range(days_ahead):
            day_name = prediction_date.strftime('%A')
            is_weekend = prediction_date.weekday() >= 5
            
            # Probabilidad basada en tasa histórica y patrones
            base_probability = 1 - attendance_rate
            day_pattern_boost = absence_patterns.get(day_name, 0) / 13  # Aproximadamente 13 semanas en 90 días
            
            if is_weekend:
                absence_probability = 0.95  # Alta probabilidad de no trabajar en fin de semana
            else:
                absence_probability = min(0.8, base_probability + day_pattern_boost)
            
            predictions.append({
                "date": prediction_date.isoformat(),
                "day_of_week": day_name,
                "absence_probability": round(absence_probability * 100, 2),
                "is_weekend": is_weekend
            })
            
            prediction_date += timedelta(days=1)
        
        return {
            "employee_id": employee_id,
            "historical_attendance_rate": round(attendance_rate * 100, 2),
            "absence_patterns": dict(absence_patterns),
            "predictions": predictions
        }
    
    def calculate_productivity_metrics(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Calcula métricas de productividad"""
        # Obtener horas trabajadas
        sql = """
            SELECT 
                SUM(ws.total_hours) as total_hours,
                SUM(ws.regular_hours) as regular_hours,
                SUM(ws.overtime_hours) as overtime_hours,
                COUNT(DISTINCT ws.work_date) as days_worked,
                COUNT(*) as total_sessions
            FROM time_tracking_work_sessions ws
            WHERE ws.employee_id = %s
                AND ws.work_date BETWEEN %s AND %s
                AND ws.status = 'closed'
                AND ws.approved = true
        """
        
        result = self.storage.hook.get_first(
            sql,
            parameters=(employee_id, start_date, end_date)
        )
        
        if not result or not result[0]:
            return {
                "employee_id": employee_id,
                "total_hours": 0.0,
                "average_hours_per_day": 0.0,
                "efficiency_score": 0.0
            }
        
        total_hours, regular_hours, overtime_hours, days_worked, total_sessions = result
        
        total_hours = float(total_hours) if total_hours else 0.0
        days_worked = days_worked or 0
        
        # Calcular métricas
        avg_hours_per_day = total_hours / days_worked if days_worked > 0 else 0.0
        
        # Score de eficiencia (basado en consistencia y horas trabajadas)
        # Idealmente, debería trabajar 8 horas por día, 5 días a la semana
        expected_hours = days_worked * 8.0
        efficiency_score = min(100, (total_hours / expected_hours * 100)) if expected_hours > 0 else 0
        
        # Consistencia (variabilidad en horas diarias)
        sql_daily = """
            SELECT ws.total_hours
            FROM time_tracking_work_sessions ws
            WHERE ws.employee_id = %s
                AND ws.work_date BETWEEN %s AND %s
                AND ws.status = 'closed'
                AND ws.approved = true
        """
        
        daily_hours = self.storage.hook.get_records(
            sql_daily,
            parameters=(employee_id, start_date, end_date)
        )
        
        daily_hours_list = [float(row[0]) for row in daily_hours if row[0]]
        consistency_score = 0.0
        
        if daily_hours_list:
            # Menor variabilidad = mayor consistencia
            if len(daily_hours_list) > 1:
                std_dev = statistics.stdev(daily_hours_list)
                mean_hours = statistics.mean(daily_hours_list)
                coefficient_of_variation = std_dev / mean_hours if mean_hours > 0 else 1.0
                consistency_score = max(0, 100 - (coefficient_of_variation * 100))
            else:
                consistency_score = 100.0
        
        return {
            "employee_id": employee_id,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "metrics": {
                "total_hours": round(total_hours, 2),
                "regular_hours": float(regular_hours) if regular_hours else 0.0,
                "overtime_hours": float(overtime_hours) if overtime_hours else 0.0,
                "days_worked": days_worked,
                "total_sessions": total_sessions or 0,
                "average_hours_per_day": round(avg_hours_per_day, 2),
                "efficiency_score": round(efficiency_score, 2),
                "consistency_score": round(consistency_score, 2),
                "overall_score": round((efficiency_score + consistency_score) / 2, 2)
            }
        }
    
    def generate_team_comparison(
        self,
        department: Optional[str] = None,
        start_date: date = None,
        end_date: date = None
    ) -> Dict[str, Any]:
        """Compara métricas del equipo"""
        if start_date is None:
            start_date = date.today() - timedelta(days=30)
        if end_date is None:
            end_date = date.today()
        
        # Obtener empleados del departamento
        if department:
            sql_employees = """
                SELECT employee_id, name
                FROM payroll_employees
                WHERE department = %s AND active = true
            """
            employees = self.storage.hook.get_records(sql_employees, parameters=(department,))
        else:
            sql_employees = """
                SELECT employee_id, name
                FROM payroll_employees
                WHERE active = true
            """
            employees = self.storage.hook.get_records(sql_employees)
        
        team_metrics = []
        
        for employee_id, name in employees:
            metrics = self.calculate_productivity_metrics(
                employee_id,
                start_date,
                end_date
            )
            team_metrics.append({
                "employee_id": employee_id,
                "name": name,
                "metrics": metrics["metrics"]
            })
        
        # Calcular promedios del equipo
        if team_metrics:
            avg_hours = statistics.mean([m["metrics"]["total_hours"] for m in team_metrics])
            avg_efficiency = statistics.mean([m["metrics"]["efficiency_score"] for m in team_metrics])
            avg_consistency = statistics.mean([m["metrics"]["consistency_score"] for m in team_metrics])
        else:
            avg_hours = avg_efficiency = avg_consistency = 0.0
        
        return {
            "department": department or "All",
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "team_size": len(team_metrics),
            "team_averages": {
                "average_hours": round(avg_hours, 2),
                "average_efficiency_score": round(avg_efficiency, 2),
                "average_consistency_score": round(avg_consistency, 2)
            },
            "individual_metrics": team_metrics
        }

