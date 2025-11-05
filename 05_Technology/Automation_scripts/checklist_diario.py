#!/usr/bin/env python3
"""
Checklist Diario de Implementación
Genera checklist personalizado por día de implementación
"""

from datetime import datetime, timedelta
from typing import Dict, List
import json

class DailyChecklist:
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self):
        """Carga templates de tareas"""
        return {
            'foundation': {
                'daily': [
                    'Review métricas del día anterior',
                    'Priorización de tareas del día',
                    'Standup con equipo (15 min)',
                    'Al menos 3 acciones en pipeline de ventas',
                    'Revisión de métricas de producto',
                    'Comunicación con stakeholders clave',
                    'Documentación de aprendizajes',
                    'Preparación para próximo día'
                ],
                'weekly': [
                    'Weekly business review',
                    'Análisis de pipeline vs. target',
                    'Review de product metrics',
                    'Team 1-on-1s',
                    'Customer feedback session'
                ]
            },
            'validation': {
                'daily': [
                    'Review de pilotos activos',
                    'Análisis de feedback recibido',
                    'Optimización de productos',
                    'Seguimiento de demos programadas',
                    'Actualización de CRM',
                    'Communication con early adopters',
                    'Métricas de adopción',
                    'Iteración rápida'
                ],
                'weekly': [
                    'Análisis de feedback agregado',
                    'Optimización de pricing',
                    'Review de conversion funnels',
                    'Customer success metrics',
                    'Product iteration priorities'
                ]
            },
            'scaling': {
                'daily': [
                    'Análisis de performance de campañas',
                    'Tracking de nuevos leads',
                    'Pipeline management',
                    'Content creation y distribution',
                    'Social media engagement',
                    'Community building',
                    'Analytics review',
                    'Growth hacks testing'
                ],
                'weekly': [
                    'Marketing performance review',
                    'Sales performance analysis',
                    'Growth metrics tracking',
                    'Partnership development',
                    'Market expansion planning'
                ]
            }
        }
    
    def generate_day_checklist(self, day: int, phase: str) -> Dict:
        """
        Genera checklist para un día específico
        
        Args:
            day: Número de día (1-90)
            phase: Fase actual (foundation/validation/scaling)
            
        Returns:
            Diccionario con checklist
        """
        if day <= 30:
            current_phase = 'foundation'
        elif day <= 60:
            current_phase = 'validation'
        else:
            current_phase = 'scaling'
        
        checklist = {
            'day': day,
            'phase': current_phase,
            'date': (datetime.now() + timedelta(days=day)).strftime('%Y-%m-%d'),
            'priority_tasks': self._get_priority_tasks_for_day(day),
            'daily_tasks': self.templates[current_phase]['daily'],
            'weekly_tasks': self._get_weekly_tasks(day),
            'metrics_to_track': self._get_metrics_for_day(day),
            'notes_section': ''
        }
        
        return checklist
    
    def _get_priority_tasks_for_day(self, day: int) -> List[str]:
        """Obtiene tareas prioritarias para el día"""
        priority_tasks = []
        
        # Semana 1
        if day == 1:
            priority_tasks = [
                'Kick-off meeting ejecutivo (2 horas)',
                'Setup de herramientas y accesos',
                'Revisión de inventario de IP',
                'Identificación de stakeholders clave'
            ]
        elif day == 2:
            priority_tasks = [
                'Contratación de VP de Licensing (proceso inicial)',
                'Análisis de competencia detallado (50+ competidores)',
                'Setup de infraestructura de datos',
                'Definición de target personas'
            ]
        elif 3 <= day <= 7:
            priority_tasks = [
                'Desarrollo de propuesta de valor por segmento',
                'Setup de CRM y pipeline management',
                'Creación de materiales de venta',
                'Outreach inicial a prospectos'
            ]
        
        # Semana 2
        elif 8 <= day <= 14:
            priority_tasks = [
                'Desarrollo de APIs core (10 APIs prioritarias)',
                'Implementación de SDKs',
                'Testing y QA',
                'Documentación técnica completa'
            ]
        
        # Semana 3
        elif 15 <= day <= 21:
            priority_tasks = [
                'Lanzamiento de 10 pilotos con clientes target',
                'Demos con 15 prospectos prioritarios',
                'Feedback session con early adopters',
                'Análisis de feedback'
            ]
        
        # Semana 4+
        elif day > 21:
            priority_tasks = [
                'Optimización de productos basada en feedback',
                'Cierre de deals activos',
                'Implementación de mejoras',
                'Preparación para lanzamiento público'
            ]
        
        return priority_tasks
    
    def _get_weekly_tasks(self, day: int) -> List[str]:
        """Obtiene tareas semanales"""
        week = (day - 1) // 7 + 1
        
        if day % 7 == 0 or day == 1:
            current_phase = 'foundation' if day <= 30 else 'validation' if day <= 60 else 'scaling'
            return self.templates[current_phase].get('weekly', [])
        return []
    
    def _get_metrics_for_day(self, day: int) -> List[str]:
        """Obtiene métricas a trackear para el día"""
        return [
            'Revenue (MTD)',
            'Pipeline value',
            'Nuevos leads',
            'Deals cerrados',
            'Active users',
            'API calls',
            'Error rate',
            'Uptime',
            'NPS',
            'Churn'
        ]
    
    def print_checklist(self, day: int, phase: str):
        """Imprime checklist formateado"""
        checklist = self.generate_day_checklist(day, phase)
        
        print("\n" + "=" * 80)
        print(f"CHECKLIST DIARIO - DÍA {checklist['day']}")
        print(f"Fecha: {checklist['date']}")
        print(f"Fase: {checklist['phase'].upper()}")
        print("=" * 80)
        
        print("\n🎯 TAREAS PRIORITARIAS:")
        for i, task in enumerate(checklist['priority_tasks'], 1):
            print(f"  {i}. [ ] {task}")
        
        print("\n📋 TAREAS DIARIAS:")
        for i, task in enumerate(checklist['daily_tasks'], 1):
            print(f"  {i}. [ ] {task}")
        
        if checklist['weekly_tasks']:
            print("\n📅 TAREAS SEMANALES:")
            for i, task in enumerate(checklist['weekly_tasks'], 1):
                print(f"  {i}. [ ] {task}")
        
        print("\n📊 MÉTRICAS A TRACKEAR:")
        for metric in checklist['metrics_to_track']:
            print(f"  • {metric}")
        
        print("\n📝 NOTAS:")
        print("  " + "_" * 75)
        print()
    
    def export_to_markdown(self, day: int, phase: str, filename: str):
        """Exporta checklist a markdown"""
        checklist = self.generate_day_checklist(day, phase)
        
        md_content = f"""# 📋 Checklist Diario - Día {checklist['day']}

**Fecha**: {checklist['date']}  
**Fase**: {checklist['phase'].upper()}

---

## 🎯 Tareas Prioritarias

"""
        for i, task in enumerate(checklist['priority_tasks'], 1):
            md_content += f"{i}. [ ] {task}\n"
        
        md_content += "\n## 📋 Tareas Diarias\n\n"
        for i, task in enumerate(checklist['daily_tasks'], 1):
            md_content += f"{i}. [ ] {task}\n"
        
        if checklist['weekly_tasks']:
            md_content += "\n## 📅 Tareas Semanales\n\n"
            for i, task in enumerate(checklist['weekly_tasks'], 1):
                md_content += f"{i}. [ ] {task}\n"
        
        md_content += "\n## 📊 Métricas a Trackear\n\n"
        for metric in checklist['metrics_to_track']:
            md_content += f"- {metric}\n"
        
        md_content += "\n## 📝 Notas\n\n"
        md_content += "_\n\n"
        
        with open(filename, 'w') as f:
            f.write(md_content)
        
        print(f"✅ Checklist exportado a {filename}")


def main():
    """
    Función principal - Genera checklist para día específico
    """
    planner = DailyChecklist()
    
    # Generar checklist para hoy (Día 1)
    print("Generando checklist para Día 1...")
    planner.print_checklist(1, 'foundation')
    
    # Exportar a markdown
    planner.export_to_markdown(1, 'foundation', 'checklist_dia_1.md')
    
    # Generar checklist para Día 7 (end of week 1)
    print("\nGenerando checklist para Día 7...")
    planner.print_checklist(7, 'foundation')
    
    # Generar checklist para Día 30 (end of phase 1)
    print("\nGenerando checklist para Día 30...")
    planner.print_checklist(30, 'foundation')
    
    print("\n" + "=" * 80)
    print("✅ Checklists generados exitosamente")
    print("=" * 80)


if __name__ == "__main__":
    main()

