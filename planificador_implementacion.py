#!/usr/bin/env python3
"""
Planificador de Implementación de Pivotes
Genera cronogramas detallados y checklist personalizados
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict
import os

class ImplementationPlanner:
    def __init__(self):
        self.tasks = []
        self.milestones = []
        self.resources = {}
        
    def create_90_day_plan(self, pivote_name: str, start_date: datetime) -> Dict:
        """
        Crea plan de 90 días para un pivote
        
        Args:
            pivote_name: Nombre del pivote
            start_date: Fecha de inicio
            
        Returns:
            Diccionario con plan completo
        """
        plan = {
            'pivote': pivote_name,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': (start_date + timedelta(days=90)).strftime('%Y-%m-%d'),
            'phases': [],
            'milestones': [],
            'resources': {}
        }
        
        # Fase 1: Días 1-30 (Fundación)
        phase1 = {
            'name': 'Fundación y Estructura',
            'start_day': 1,
            'end_day': 30,
            'tasks': self._generate_foundation_tasks()
        }
        plan['phases'].append(phase1)
        
        # Fase 2: Días 31-60 (Implementación)
        phase2 = {
            'name': 'Validación y Pilotos',
            'start_day': 31,
            'end_day': 60,
            'tasks': self._generate_validation_tasks()
        }
        plan['phases'].append(phase2)
        
        # Fase 3: Días 61-90 (Consolidación)
        phase3 = {
            'name': 'Escalamiento',
            'start_day': 61,
            'end_day': 90,
            'tasks': self._generate_scaling_tasks()
        }
        plan['phases'].append(phase3)
        
        # Milestones
        plan['milestones'] = self._generate_milestones(start_date)
        
        # Resources
        plan['resources'] = self._calculate_resources(pivote_name)
        
        return plan
    
    def _generate_foundation_tasks(self) -> List[Dict]:
        """Genera tareas de fundación"""
        return [
            {'id': 'F1', 'name': 'Setup de infraestructura', 'days': 3, 'priority': 'high'},
            {'id': 'F2', 'name': 'Contratación de VP de Licensing', 'days': 7, 'priority': 'high'},
            {'id': 'F3', 'name': 'Desarrollo de 4 algoritmos patentables', 'days': 15, 'priority': 'high'},
            {'id': 'F4', 'name': 'Arquitectura de microservicios', 'days': 5, 'priority': 'high'},
            {'id': 'F5', 'name': 'Creación de 20+ APIs', 'days': 12, 'priority': 'medium'},
            {'id': 'F6', 'name': 'Desarrollo de 5+ SDKs', 'days': 10, 'priority': 'medium'},
            {'id': 'F7', 'name': 'Setup de CRM y analytics', 'days': 2, 'priority': 'high'},
            {'id': 'F8', 'name': 'Outreach a 25 prospectos Fortune 500', 'days': 3, 'priority': 'high'},
            {'id': 'F9', 'name': 'Pricing strategy por tipo de licencia', 'days': 4, 'priority': 'medium'},
            {'id': 'F10', 'name': 'Documentación técnica completa', 'days': 5, 'priority': 'medium'},
        ]
    
    def _generate_validation_tasks(self) -> List[Dict]:
        """Genera tareas de validación"""
        return [
            {'id': 'V1', 'name': 'Lanzamiento de 10 pilotos con clientes', 'days': 5, 'priority': 'high'},
            {'id': 'V2', 'name': 'Demos con 15 prospectos prioritarios', 'days': 7, 'priority': 'high'},
            {'id': 'V3', 'name': 'Feedback session con early adopters', 'days': 3, 'priority': 'high'},
            {'id': 'V4', 'name': 'Análisis de feedback de pilotos', 'days': 3, 'priority': 'high'},
            {'id': 'V5', 'name': 'Iteración rápida de productos', 'days': 5, 'priority': 'medium'},
            {'id': 'V6', 'name': 'Optimización de pricing', 'days': 2, 'priority': 'medium'},
            {'id': 'V7', 'name': 'Cierre de primeros 3 deals', 'days': 10, 'priority': 'high'},
            {'id': 'V8', 'name': 'Aplicación de patentes prioritarias', 'days': 7, 'priority': 'medium'},
        ]
    
    def _generate_scaling_tasks(self) -> List[Dict]:
        """Genera tareas de escalamiento"""
        return [
            {'id': 'S1', 'name': 'Lanzamiento público de productos', 'days': 3, 'priority': 'high'},
            {'id': 'S2', 'name': 'Campañas de marketing digital', 'days': 7, 'priority': 'high'},
            {'id': 'S3', 'name': 'Webinars y eventos', 'days': 5, 'priority': 'medium'},
            {'id': 'S4', 'name': 'Outreach masivo (100+ prospectos)', 'days': 10, 'priority': 'high'},
            {'id': 'S5', 'name': 'Análisis de métricas de adopción', 'days': 3, 'priority': 'medium'},
            {'id': 'S6', 'name': 'Optimización de conversión', 'days': 5, 'priority': 'medium'},
            {'id': 'S7', 'name': 'Iteración de features', 'days': 7, 'priority': 'medium'},
            {'id': 'S8', 'name': 'Expansion de pilotos a producción', 'days': 10, 'priority': 'high'},
            {'id': 'S9', 'name': 'Crecimiento de sales team', 'days': 14, 'priority': 'high'},
            {'id': 'S10', 'name': 'Preparación para Serie A', 'days': 7, 'priority': 'medium'},
        ]
    
    def _generate_milestones(self, start_date: datetime) -> List[Dict]:
        """Genera milestones"""
        milestones = [
            {'day': 30, 'name': 'Producto MVP Funcional', 'date': (start_date + timedelta(days=30)).strftime('%Y-%m-%d')},
            {'day': 45, 'name': 'Primeras Ventas Cerradas', 'date': (start_date + timedelta(days=45)).strftime('%Y-%m-%d')},
            {'day': 60, 'name': 'Product-Market Fit Validado', 'date': (start_date + timedelta(days=60)).strftime('%Y-%m-%d')},
            {'day': 90, 'name': 'Escalamiento Operacional', 'date': (start_date + timedelta(days=90)).strftime('%Y-%m-%d')},
        ]
        return milestones
    
    def _calculate_resources(self, pivote_name: str) -> Dict:
        """Calcula recursos necesarios"""
        if 'Licensing' in pivote_name or 'pivote_3' in pivote_name.lower():
            # Pivote 3: Mínimos recursos
            return {
                'budget': 200_000,
                'team_size': 8,
                'tools': ['Salesforce', 'GitHub', 'AWS', 'Mixpanel'],
                'inventory': {
                    'algorithms': 4,
                    'apis': 20,
                    'sdks': 5,
                    'datasets': 10
                }
            }
        elif 'segmentos' in pivote_name.lower() or 'pivote_1' in pivote_name.lower():
            # Pivote 1: Recursos medios
            return {
                'budget': 500_000,
                'team_size': 15,
                'tools': ['Salesforce', 'GitHub', 'AWS', 'Mixpanel', 'HubSpot'],
                'inventory': {
                    'products': 3,
                    'campaigns': 5,
                    'content_pieces': 20
                }
            }
        else:
            # Pivote 2: Recursos medios-altos
            return {
                'budget': 400_000,
                'team_size': 12,
                'tools': ['Salesforce', 'GitHub', 'AWS', 'Mixpanel', 'Intercom'],
                'inventory': {
                    'use_cases': 5,
                    'integrations': 10,
                    'features': 30
                }
            }
    
    def export_to_json(self, plan: Dict, filename: str):
        """Exporta plan a JSON"""
        with open(filename, 'w') as f:
            json.dump(plan, f, indent=2)
        print(f"Plan exportado a {filename}")
    
    def print_plan_summary(self, plan: Dict):
        """Imprime resumen del plan"""
        print("\n" + "=" * 100)
        print(f"PLAN DE IMPLEMENTACIÓN: {plan['pivote']}")
        print("=" * 100)
        print(f"Fecha de inicio: {plan['start_date']}")
        print(f"Fecha de finalización: {plan['end_date']}")
        print(f"Duración: 90 días")
        
        print(f"\n📊 RECURSOS:")
        print(f"  Presupuesto: ${plan['resources']['budget']:,.0f}")
        print(f"  Team Size: {plan['resources']['team_size']} personas")
        print(f"  Tools: {', '.join(plan['resources']['tools'])}")
        
        print(f"\n🎯 MILESTONES:")
        for milestone in plan['milestones']:
            print(f"  Día {milestone['day']}: {milestone['name']} - {milestone['date']}")
        
        print(f"\n📋 FASES:")
        for phase in plan['phases']:
            print(f"\n  {phase['name']} (Días {phase['start_day']}-{phase['end_day']}):")
            high_priority = [t for t in phase['tasks'] if t['priority'] == 'high']
            print(f"    Tareas prioritarias: {len(high_priority)}")
            for task in high_priority:
                print(f"      - {task['name']} ({task['days']} días)")


def main():
    """
    Función principal - Genera plan de implementación
    """
    planner = ImplementationPlanner()
    
    # Generar plan para Pivote 3 (Recomendado)
    start_date = datetime.now()
    pivote3_plan = planner.create_90_day_plan("Pivote 3: Licensing Technology", start_date)
    
    # Imprimir resumen
    planner.print_plan_summary(pivote3_plan)
    
    # Exportar a JSON
    planner.export_to_json(pivote3_plan, 'plan_implementacion_pivote3.json')
    
    print("\n" + "=" * 100)
    print("✅ Plan de implementación generado exitosamente")
    print("=" * 100)


if __name__ == "__main__":
    main()



