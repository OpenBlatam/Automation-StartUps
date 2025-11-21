#!/usr/bin/env python3
"""
Generador de Calendario de Contenido Optimizado para Testimonios
Genera calendarios semanales/mensuales con horarios óptimos
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class CalendarEvent:
    """Evento del calendario"""
    date: datetime
    platform: str
    content_type: str
    optimal_time: str
    testimonial_id: Optional[str] = None
    notes: Optional[str] = None


class ContentCalendarGenerator:
    """Generador de calendario de contenido optimizado"""
    
    def __init__(self, optimal_times: Optional[Dict[str, List[str]]] = None):
        """
        Inicializa el generador de calendario
        
        Args:
            optimal_times: Horarios óptimos por plataforma
        """
        self.optimal_times = optimal_times or {
            'linkedin': ['09:00-11:00', '13:00-15:00'],
            'instagram': ['11:00-13:00', '19:00-21:00'],
            'facebook': ['09:00-11:00', '13:00-15:00', '19:00-21:00'],
            'twitter': ['08:00-10:00', '12:00-14:00', '17:00-19:00'],
            'tiktok': ['18:00-22:00', '06:00-09:00']
        }
        
        self.optimal_days = {
            'linkedin': ['Tuesday', 'Wednesday', 'Thursday'],
            'instagram': ['Tuesday', 'Wednesday', 'Thursday'],
            'facebook': ['Thursday', 'Friday', 'Saturday', 'Sunday'],
            'twitter': ['Monday', 'Tuesday', 'Wednesday', 'Thursday'],
            'tiktok': ['Tuesday', 'Wednesday', 'Thursday', 'Friday']
        }
    
    def generate_weekly_calendar(
        self,
        platforms: List[str],
        start_date: Optional[datetime] = None,
        posts_per_platform: int = 3
    ) -> Dict[str, Any]:
        """
        Genera un calendario semanal optimizado
        
        Args:
            platforms: Lista de plataformas a incluir
            start_date: Fecha de inicio (default: próximo lunes)
            posts_per_platform: Posts por plataforma por semana
        
        Returns:
            Calendario semanal con eventos optimizados
        """
        if start_date is None:
            # Encontrar próximo lunes
            today = datetime.now()
            days_until_monday = (7 - today.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            start_date = today + timedelta(days=days_until_monday)
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        calendar = {
            'start_date': start_date.isoformat(),
            'end_date': (start_date + timedelta(days=6)).isoformat(),
            'events': [],
            'summary': {}
        }
        
        events = []
        platform_counts = defaultdict(int)
        
        # Generar eventos para cada día de la semana
        for day_offset in range(7):
            current_date = start_date + timedelta(days=day_offset)
            day_name = current_date.strftime('%A')
            
            for platform in platforms:
                # Verificar si este día es óptimo para la plataforma
                if day_name in self.optimal_days.get(platform, []):
                    # Generar eventos para esta plataforma en este día
                    if platform_counts[platform] < posts_per_platform:
                        optimal_times = self.optimal_times.get(platform, ['09:00-11:00'])
                        
                        for time_slot in optimal_times[:posts_per_platform]:
                            if platform_counts[platform] < posts_per_platform:
                                event = CalendarEvent(
                                    date=current_date,
                                    platform=platform,
                                    content_type='testimonial',
                                    optimal_time=time_slot,
                                    notes=f"Publicación optimizada para {platform}"
                                )
                                events.append(event)
                                platform_counts[platform] += 1
        
        calendar['events'] = [
            {
                'date': e.date.isoformat(),
                'platform': e.platform,
                'content_type': e.content_type,
                'optimal_time': e.optimal_time,
                'day_name': e.date.strftime('%A'),
                'notes': e.notes
            }
            for e in events
        ]
        
        calendar['summary'] = {
            'total_events': len(events),
            'events_by_platform': dict(platform_counts),
            'events_by_day': self._count_by_day(events)
        }
        
        return calendar
    
    def generate_monthly_calendar(
        self,
        platforms: List[str],
        start_date: Optional[datetime] = None,
        posts_per_week: int = 3
    ) -> Dict[str, Any]:
        """
        Genera un calendario mensual optimizado
        
        Args:
            platforms: Lista de plataformas
            start_date: Fecha de inicio (default: inicio del mes actual)
            posts_per_week: Posts por plataforma por semana
        
        Returns:
            Calendario mensual con eventos optimizados
        """
        if start_date is None:
            today = datetime.now()
            start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calcular fin del mes
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1)
        
        calendar = {
            'start_date': start_date.isoformat(),
            'end_date': (end_date - timedelta(days=1)).isoformat(),
            'events': [],
            'summary': {}
        }
        
        events = []
        current_date = start_date
        
        while current_date < end_date:
            day_name = current_date.strftime('%A')
            
            # Generar eventos solo en días óptimos
            for platform in platforms:
                if day_name in self.optimal_days.get(platform, []):
                    # Limitar posts por semana
                    week_start = current_date - timedelta(days=current_date.weekday())
                    week_events = [
                        e for e in events
                        if e.date >= week_start and e.platform == platform
                    ]
                    
                    if len(week_events) < posts_per_week:
                        optimal_times = self.optimal_times.get(platform, ['09:00-11:00'])
                        time_slot = optimal_times[0]  # Usar primer horario óptimo
                        
                        event = CalendarEvent(
                            date=current_date.replace(
                                hour=int(time_slot.split(':')[0]),
                                minute=0
                            ),
                            platform=platform,
                            content_type='testimonial',
                            optimal_time=time_slot,
                            notes=f"Publicación semanal optimizada para {platform}"
                        )
                        events.append(event)
            
            current_date += timedelta(days=1)
        
        calendar['events'] = [
            {
                'date': e.date.isoformat(),
                'platform': e.platform,
                'content_type': e.content_type,
                'optimal_time': e.optimal_time,
                'day_name': e.date.strftime('%A'),
                'week': e.date.isocalendar()[1],
                'notes': e.notes
            }
            for e in events
        ]
        
        calendar['summary'] = {
            'total_events': len(events),
            'events_by_platform': self._count_by_platform(events),
            'events_by_week': self._count_by_week(events),
            'events_by_day': self._count_by_day(events)
        }
        
        return calendar
    
    def _count_by_day(self, events: List[CalendarEvent]) -> Dict[str, int]:
        """Cuenta eventos por día de la semana"""
        counts = defaultdict(int)
        for event in events:
            day_name = event.date.strftime('%A')
            counts[day_name] += 1
        return dict(counts)
    
    def _count_by_platform(self, events: List[CalendarEvent]) -> Dict[str, int]:
        """Cuenta eventos por plataforma"""
        counts = defaultdict(int)
        for event in events:
            counts[event.platform] += 1
        return dict(counts)
    
    def _count_by_week(self, events: List[CalendarEvent]) -> Dict[int, int]:
        """Cuenta eventos por semana"""
        counts = defaultdict(int)
        for event in events:
            week = event.date.isocalendar()[1]
            counts[week] += 1
        return dict(counts)
    
    def export_to_json(self, calendar: Dict[str, Any], output_file: str) -> str:
        """Exporta calendario a JSON"""
        from pathlib import Path
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(calendar, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Calendario exportado a: {output_file}")
        return str(output_path)
    
    def export_to_ical(self, calendar: Dict[str, Any], output_file: str) -> str:
        """Exporta calendario a formato iCal"""
        from pathlib import Path
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        ical_content = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Testimonial Calendar//EN"]
        
        for event_data in calendar.get('events', []):
            event_date = datetime.fromisoformat(event_data['date'])
            end_date = event_date + timedelta(hours=1)
            
            ical_content.extend([
                "BEGIN:VEVENT",
                f"DTSTART:{event_date.strftime('%Y%m%dT%H%M%S')}",
                f"DTEND:{end_date.strftime('%Y%m%dT%H%M%S')}",
                f"SUMMARY:Publicación {event_data['platform'].upper()} - {event_data['content_type']}",
                f"DESCRIPTION:{event_data.get('notes', '')}",
                f"LOCATION:{event_data['platform']}",
                "END:VEVENT"
            ])
        
        ical_content.append("END:VCALENDAR")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(ical_content))
        
        logger.info(f"Calendario iCal exportado a: {output_file}")
        return str(output_path)



