"""
Scheduler Inteligente de Backups.

Proporciona:
- Programación adaptativa basada en carga
- Optimización de horarios de backup
- Detección de ventanas de bajo uso
- Balanceo de carga de backups
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import psutil

logger = logging.getLogger(__name__)


class BackupPriority(Enum):
    """Prioridades de backup."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class BackupSchedule:
    """Configuración de programación de backup."""
    backup_id: str
    priority: BackupPriority
    preferred_window_start: int  # Hora preferida (0-23)
    preferred_window_end: int  # Hora preferida (0-23)
    max_delay_hours: int = 6  # Máximo delay permitido
    estimated_duration_minutes: int = 30
    resources_required: Dict[str, float] = None  # CPU, memoria, etc.


class IntelligentBackupScheduler:
    """Scheduler inteligente de backups."""
    
    def __init__(self):
        """Inicializa scheduler."""
        self.schedules: List[BackupSchedule] = []
        self.current_load = {'cpu': 0.0, 'memory': 0.0, 'disk_io': 0.0}
    
    def add_schedule(self, schedule: BackupSchedule) -> None:
        """Agrega un schedule a la cola."""
        self.schedules.append(schedule)
        # Ordenar por prioridad
        priority_order = {
            BackupPriority.CRITICAL: 0,
            BackupPriority.HIGH: 1,
            BackupPriority.MEDIUM: 2,
            BackupPriority.LOW: 3
        }
        self.schedules.sort(key=lambda s: priority_order.get(s.priority, 99))
    
    def get_optimal_time(
        self,
        schedule: BackupSchedule,
        current_time: Optional[datetime] = None
    ) -> datetime:
        """
        Calcula el tiempo óptimo para ejecutar un backup.
        
        Args:
            schedule: Schedule del backup
            current_time: Tiempo actual (None = ahora)
        
        Returns:
            Tiempo óptimo para ejecutar
        """
        if current_time is None:
            current_time = datetime.now()
        
        # Verificar ventana preferida
        current_hour = current_time.hour
        
        if schedule.preferred_window_start <= current_hour < schedule.preferred_window_end:
            # Estamos en la ventana preferida
            if self._is_low_load():
                return current_time
            else:
                # Esperar a que baje la carga
                return self._find_next_low_load_window(current_time)
        else:
            # Estamos fuera de la ventana preferida
            next_window = self._get_next_preferred_window(current_time, schedule)
            return next_window
    
    def _is_low_load(self, threshold: float = 0.5) -> bool:
        """Verifica si la carga del sistema es baja."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent / 100
            
            self.current_load = {
                'cpu': cpu_percent / 100,
                'memory': memory_percent
            }
            
            return (cpu_percent / 100 < threshold and memory_percent < threshold)
        except Exception:
            return True  # Asumir baja carga si no se puede verificar
    
    def _find_next_low_load_window(self, start_time: datetime) -> datetime:
        """Encuentra la próxima ventana de baja carga."""
        check_time = start_time
        max_checks = 24  # Máximo 24 horas
        
        for _ in range(max_checks):
            check_time += timedelta(hours=1)
            
            # Simular carga (en producción usar datos históricos)
            if self._is_low_load():
                return check_time
        
        # Si no encuentra, retornar tiempo con delay mínimo
        return start_time + timedelta(hours=1)
    
    def _get_next_preferred_window(
        self,
        current_time: datetime,
        schedule: BackupSchedule
    ) -> datetime:
        """Obtiene la próxima ventana preferida."""
        next_time = current_time.replace(
            hour=schedule.preferred_window_start,
            minute=0,
            second=0,
            microsecond=0
        )
        
        # Si la ventana ya pasó hoy, programar para mañana
        if next_time <= current_time:
            next_time += timedelta(days=1)
        
        return next_time
    
    def schedule_backups(
        self,
        schedules: List[BackupSchedule]
    ) -> List[Dict[str, Any]]:
        """
        Programa múltiples backups de forma óptima.
        
        Args:
            schedules: Lista de schedules
        
        Returns:
            Lista de backups programados con tiempos óptimos
        """
        scheduled = []
        current_time = datetime.now()
        
        for schedule in schedules:
            optimal_time = self.get_optimal_time(schedule, current_time)
            
            scheduled.append({
                'backup_id': schedule.backup_id,
                'priority': schedule.priority.value,
                'scheduled_time': optimal_time.isoformat(),
                'delay_minutes': (optimal_time - current_time).total_seconds() / 60,
                'estimated_duration': schedule.estimated_duration_minutes
            })
            
            # Actualizar tiempo actual para próximos backups
            current_time = optimal_time + timedelta(minutes=schedule.estimated_duration_minutes)
        
        return scheduled
    
    def get_load_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de carga del sistema."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024 ** 3),
                'disk_usage_percent': (disk.used / disk.total) * 100,
                'disk_free_gb': disk.free / (1024 ** 3),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting load statistics: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

