"""
Gestor de Timezones
Maneja conversiones y validaciones de zonas horarias
"""

import logging
from datetime import datetime, time
from typing import Optional
import pytz

logger = logging.getLogger(__name__)


class TimezoneManager:
    """Gestiona timezones y conversiones"""
    
    def __init__(self, storage):
        self.storage = storage
    
    def get_employee_timezone(self, employee_id: str) -> pytz.timezone:
        """Obtiene el timezone del empleado"""
        # Primero intentar obtener de la configuración del empleado
        sql = """
            SELECT timezone FROM time_tracking_schedules
            WHERE employee_id = %s
                AND is_active = true
            ORDER BY valid_from DESC
            LIMIT 1
        """
        
        result = self.storage.hook.get_first(sql, parameters=(employee_id,))
        
        if result and result[0]:
            try:
                return pytz.timezone(result[0])
            except Exception:
                pass
        
        # Obtener de la oficina del empleado
        sql = """
            SELECT office_location FROM payroll_employees
            WHERE employee_id = %s
        """
        
        result = self.storage.hook.get_first(sql, parameters=(employee_id,))
        
        if result and result[0]:
            # Mapeo simple de ubicaciones a timezones
            location_timezones = {
                "Mexico City": "America/Mexico_City",
                "New York": "America/New_York",
                "Los Angeles": "America/Los_Angeles",
                "London": "Europe/London",
                "Madrid": "Europe/Madrid",
            }
            
            tz_name = location_timezones.get(result[0], "UTC")
            return pytz.timezone(tz_name)
        
        # Default a UTC
        return pytz.UTC
    
    def convert_to_employee_timezone(
        self,
        dt: datetime,
        employee_id: str
    ) -> datetime:
        """Convierte datetime a timezone del empleado"""
        if dt.tzinfo is None:
            # Asumir UTC si no tiene timezone
            dt = pytz.UTC.localize(dt)
        
        employee_tz = self.get_employee_timezone(employee_id)
        return dt.astimezone(employee_tz)
    
    def get_local_time(
        self,
        employee_id: str,
        dt: Optional[datetime] = None
    ) -> datetime:
        """Obtiene la hora local del empleado"""
        if dt is None:
            dt = datetime.now(pytz.UTC)
        
        return self.convert_to_employee_timezone(dt, employee_id)
    
    def is_business_hours(
        self,
        employee_id: str,
        dt: Optional[datetime] = None
    ) -> bool:
        """Verifica si es horario laboral para el empleado"""
        if dt is None:
            dt = datetime.now(pytz.UTC)
        
        local_time = self.convert_to_employee_timezone(dt, employee_id)
        
        # Obtener horario del empleado
        sql = """
            SELECT start_time, end_time, day_of_week
            FROM time_tracking_schedules
            WHERE employee_id = %s
                AND is_active = true
                AND (day_of_week = %s OR day_of_week IS NULL)
            ORDER BY valid_from DESC
            LIMIT 1
        """
        
        day_of_week = local_time.weekday()  # 0=Monday, 6=Sunday
        result = self.storage.hook.get_first(
            sql,
            parameters=(employee_id, day_of_week)
        )
        
        if not result:
            # Sin horario específico, permitir cualquier hora
            return True
        
        start_time = result[0]
        end_time = result[1]
        
        if not start_time or not end_time:
            return True
        
        current_time = local_time.time()
        
        # Manejar horarios que cruzan medianoche
        if start_time > end_time:
            # Horario nocturno (ej: 22:00 - 06:00)
            return current_time >= start_time or current_time <= end_time
        else:
            return start_time <= current_time <= end_time
    
    def is_weekend(self, employee_id: str, dt: Optional[datetime] = None) -> bool:
        """Verifica si es fin de semana"""
        if dt is None:
            dt = datetime.now(pytz.UTC)
        
        local_time = self.convert_to_employee_timezone(dt, employee_id)
        # 5 = Saturday, 6 = Sunday
        return local_time.weekday() >= 5

