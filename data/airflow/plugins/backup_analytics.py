"""
Módulo de Analytics y Reportes para Backups.

Proporciona:
- Análisis de tendencias de backups
- Reportes de uso de espacio
- Análisis de performance
- Predicción de necesidades de espacio
- Reportes de cumplimiento
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class BackupAnalytics:
    """Analytics de backups."""
    total_backups: int = 0
    successful_backups: int = 0
    failed_backups: int = 0
    total_size_gb: float = 0.0
    avg_duration_seconds: float = 0.0
    success_rate: float = 0.0
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class BackupAnalyticsEngine:
    """Motor de analytics para backups."""
    
    def __init__(self, backup_dir: str = "/tmp/backups"):
        """
        Inicializa motor de analytics.
        
        Args:
            backup_dir: Directorio de backups
        """
        self.backup_dir = Path(backup_dir)
    
    def generate_daily_report(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Genera reporte diario de backups.
        
        Args:
            date: Fecha del reporte (None = hoy)
        """
        if date is None:
            date = datetime.now()
        
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        backups = self._get_backups_in_range(start_date, end_date)
        
        analytics = self._calculate_analytics(backups, start_date, end_date)
        
        return {
            'date': date.date().isoformat(),
            'analytics': self._analytics_to_dict(analytics),
            'backups': backups[:10],  # Primeros 10
            'trends': self._calculate_trends(backups)
        }
    
    def generate_weekly_report(self, week_start: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Genera reporte semanal de backups.
        
        Args:
            week_start: Inicio de semana (None = esta semana)
        """
        if week_start is None:
            week_start = datetime.now()
            # Lunes de esta semana
            days_since_monday = week_start.weekday()
            week_start = week_start - timedelta(days=days_since_monday)
        
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=7)
        
        backups = self._get_backups_in_range(week_start, week_end)
        
        analytics = self._calculate_analytics(backups, week_start, week_end)
        
        # Análisis por día
        daily_breakdown = {}
        for i in range(7):
            day_start = week_start + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            day_backups = [b for b in backups if day_start <= datetime.fromisoformat(b['modified']) < day_end]
            daily_breakdown[day_start.date().isoformat()] = {
                'count': len(day_backups),
                'success_count': sum(1 for b in day_backups if b.get('status') == 'completed'),
                'total_size_mb': sum(b.get('size', 0) for b in day_backups) / (1024 ** 2)
            }
        
        return {
            'week_start': week_start.date().isoformat(),
            'week_end': (week_end - timedelta(days=1)).date().isoformat(),
            'analytics': self._analytics_to_dict(analytics),
            'daily_breakdown': daily_breakdown,
            'trends': self._calculate_trends(backups)
        }
    
    def generate_monthly_report(self, month: Optional[int] = None, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Genera reporte mensual de backups.
        
        Args:
            month: Mes (1-12, None = mes actual)
            year: Año (None = año actual)
        """
        if month is None:
            month = datetime.now().month
        if year is None:
            year = datetime.now().year
        
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1)
        else:
            month_end = datetime(year, month + 1, 1)
        
        backups = self._get_backups_in_range(month_start, month_end)
        analytics = self._calculate_analytics(backups, month_start, month_end)
        
        # Análisis por semana
        weekly_breakdown = {}
        current_week_start = month_start
        week_num = 1
        
        while current_week_start < month_end:
            week_end = min(current_week_start + timedelta(days=7), month_end)
            week_backups = [b for b in backups if current_week_start <= datetime.fromisoformat(b['modified']) < week_end]
            
            weekly_breakdown[f"week_{week_num}"] = {
                'start': current_week_start.date().isoformat(),
                'count': len(week_backups),
                'success_count': sum(1 for b in week_backups if b.get('status') == 'completed'),
                'total_size_gb': sum(b.get('size', 0) for b in week_backups) / (1024 ** 3)
            }
            
            current_week_start = week_end
            week_num += 1
        
        # Predicción de espacio
        space_prediction = self._predict_space_needs(backups)
        
        return {
            'month': month,
            'year': year,
            'analytics': self._analytics_to_dict(analytics),
            'weekly_breakdown': weekly_breakdown,
            'space_prediction': space_prediction,
            'trends': self._calculate_trends(backups)
        }
    
    def predict_space_needs(self, days: int = 30) -> Dict[str, Any]:
        """
        Predice necesidades de espacio para próximos días.
        
        Args:
            days: Días a predecir
        """
        # Obtener backups de últimos 30 días
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        backups = self._get_backups_in_range(start_date, end_date)
        
        if not backups:
            return {
                'predicted_size_gb': 0,
                'confidence': 'low',
                'message': 'No historical data available'
            }
        
        # Calcular crecimiento diario promedio
        daily_sizes = {}
        for backup in backups:
            backup_date = datetime.fromisoformat(backup['modified']).date()
            if backup_date not in daily_sizes:
                daily_sizes[backup_date] = 0
            daily_sizes[backup_date] += backup.get('size', 0)
        
        if len(daily_sizes) < 2:
            avg_daily_gb = sum(daily_sizes.values()) / (1024 ** 3) / max(len(daily_sizes), 1)
        else:
            sorted_dates = sorted(daily_sizes.keys())
            total_gb = sum(daily_sizes.values()) / (1024 ** 3)
            days_span = (sorted_dates[-1] - sorted_dates[0]).days or 1
            avg_daily_gb = total_gb / days_span
        
        predicted_size_gb = avg_daily_gb * days
        
        # Calcular confianza basada en cantidad de datos
        confidence = 'high' if len(daily_sizes) >= 14 else ('medium' if len(daily_sizes) >= 7 else 'low')
        
        return {
            'predicted_size_gb': predicted_size_gb,
            'avg_daily_gb': avg_daily_gb,
            'confidence': confidence,
            'days_predicted': days,
            'historical_days': len(daily_sizes)
        }
    
    def _get_backups_in_range(self, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        """Obtiene backups en un rango de fechas."""
        backups = []
        
        for backup_file in self.backup_dir.glob("*"):
            if backup_file.is_file():
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if start <= file_time < end:
                    backups.append({
                        'name': backup_file.name,
                        'path': str(backup_file),
                        'size': backup_file.stat().st_size,
                        'modified': file_time.isoformat(),
                        'status': 'completed'  # Asumir completado si existe
                    })
        
        return sorted(backups, key=lambda x: x['modified'], reverse=True)
    
    def _calculate_analytics(
        self,
        backups: List[Dict[str, Any]],
        start: datetime,
        end: datetime
    ) -> BackupAnalytics:
        """Calcula analytics de backups."""
        total = len(backups)
        successful = sum(1 for b in backups if b.get('status') == 'completed')
        failed = total - successful
        total_size = sum(b.get('size', 0) for b in backups)
        
        return BackupAnalytics(
            total_backups=total,
            successful_backups=successful,
            failed_backups=failed,
            total_size_gb=total_size / (1024 ** 3),
            success_rate=successful / total if total > 0 else 0.0,
            period_start=start,
            period_end=end
        )
    
    def _calculate_trends(self, backups: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula tendencias de backups."""
        if len(backups) < 2:
            return {'message': 'Insufficient data for trends'}
        
        # Ordenar por fecha
        sorted_backups = sorted(backups, key=lambda x: x['modified'])
        
        # Calcular crecimiento de tamaño
        first_size = sorted_backups[0].get('size', 0) / (1024 ** 3)
        last_size = sorted_backups[-1].get('size', 0) / (1024 ** 3)
        size_growth = ((last_size - first_size) / first_size * 100) if first_size > 0 else 0
        
        # Calcular frecuencia
        first_date = datetime.fromisoformat(sorted_backups[0]['modified'])
        last_date = datetime.fromisoformat(sorted_backups[-1]['modified'])
        days_span = (last_date - first_date).days or 1
        avg_frequency = len(sorted_backups) / days_span
        
        return {
            'size_growth_percent': size_growth,
            'avg_backups_per_day': avg_frequency,
            'trend': 'increasing' if size_growth > 5 else ('decreasing' if size_growth < -5 else 'stable')
        }
    
    def _predict_space_needs(self, backups: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predice necesidades de espacio."""
        return self.predict_space_needs(days=30)
    
    def _analytics_to_dict(self, analytics: BackupAnalytics) -> Dict[str, Any]:
        """Convierte BackupAnalytics a dict."""
        return {
            'total_backups': analytics.total_backups,
            'successful_backups': analytics.successful_backups,
            'failed_backups': analytics.failed_backups,
            'total_size_gb': analytics.total_size_gb,
            'success_rate': analytics.success_rate,
            'period_start': analytics.period_start.isoformat() if analytics.period_start else None,
            'period_end': analytics.period_end.isoformat() if analytics.period_end else None
        }

