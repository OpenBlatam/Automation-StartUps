#!/usr/bin/env python3
"""
INTEGRATED HR LAUNCH DEMO
========================

Demo Integrado del Sistema de Planificación de Lanzamientos
con el Sistema de Capacitación de RRHH con IA

Funcionalidades Integradas:
- Planificación de lanzamiento con equipo de RRHH
- Capacitación de equipos para lanzamientos
- Evaluación de habilidades del equipo
- Optimización de recursos humanos
- Analytics integrados

Autor: Sistema de IA Avanzado
Versión: 1.0.0
"""

import sys
import os
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar sistemas
try:
    from hr_ai_training_system import HRAITrainingSystem, Employee, TrainingModule
    from ultimate_enhanced_demo import UltimateEnhancedLaunchSystem
except ImportError as e:
    print(f"❌ Error importando sistemas: {e}")
    print("Asegúrate de que los archivos hr_ai_training_system.py y ultimate_enhanced_demo.py estén disponibles")
    sys.exit(1)

class IntegratedHRLaunchSystem:
    """Sistema Integrado de RRHH y Planificación de Lanzamientos"""
    
    def __init__(self):
        self.system_name = "Integrated HR Launch System"
        self.version = "1.0.0"
        self.start_time = datetime.now()
        
        # Inicializar sistemas
        self.hr_system = HRAITrainingSystem()
        self.launch_system = UltimateEnhancedLaunchSystem()
        
        # Datos integrados
        self.launch_teams = {}
        self.team_performance = {}
        self.integrated_analytics = {}
        
        logger.info(f"Inicializando {self.system_name} v{self.version}")
    
    def create_launch_team(self, launch_name: str, team_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Crear equipo de lanzamiento con análisis de RRHH"""
        logger.info(f"Creando equipo de lanzamiento para: {launch_name}")
        
        # Análisis de requerimientos del equipo
        required_skills = team_requirements.get("required_skills", [])
        team_size = team_requirements.get("team_size", 5)
        experience_level = team_requirements.get("experience_level", "intermediate")
        budget = team_requirements.get("budget", "medium")
        
        # Seleccionar empleados basado en habilidades y disponibilidad
        available_employees = list(self.hr_system.employees.values())
        selected_team = []
        
        # Simular selección de equipo
        for _ in range(min(team_size, len(available_employees))):
            if available_employees:
                emp = random.choice(available_employees)
                selected_team.append(emp)
                available_employees.remove(emp)
        
        # Crear perfil del equipo
        team_profile = {
            "launch_name": launch_name,
            "team_size": len(selected_team),
            "team_members": [
                {
                    "id": emp.id,
                    "name": emp.name,
                    "position": emp.position,
                    "department": emp.department,
                    "skills": emp.skills,
                    "experience_years": emp.experience_years,
                    "performance_score": emp.performance_score
                }
                for emp in selected_team
            ],
            "team_skills": list(set([skill for emp in selected_team for skill in emp.skills])),
            "average_experience": sum([emp.experience_years for emp in selected_team]) / len(selected_team),
            "average_performance": sum([emp.performance_score for emp in selected_team]) / len(selected_team),
            "skill_coverage": self._calculate_skill_coverage(selected_team, required_skills),
            "team_readiness_score": self._calculate_team_readiness(selected_team, required_skills),
            "creation_date": datetime.now().isoformat()
        }
        
        self.launch_teams[launch_name] = team_profile
        return team_profile
    
    def _calculate_skill_coverage(self, team: List[Employee], required_skills: List[str]) -> float:
        """Calcular cobertura de habilidades del equipo"""
        if not required_skills:
            return 1.0
        
        team_skills = set([skill for emp in team for skill in emp.skills])
        covered_skills = len(team_skills.intersection(set(required_skills)))
        return covered_skills / len(required_skills)
    
    def _calculate_team_readiness(self, team: List[Employee], required_skills: List[str]) -> float:
        """Calcular puntuación de preparación del equipo"""
        skill_coverage = self._calculate_skill_coverage(team, required_skills)
        avg_performance = sum([emp.performance_score for emp in team]) / len(team)
        avg_experience = sum([emp.experience_years for emp in team]) / len(team)
        
        # Normalizar experiencia (asumiendo 10 años como máximo)
        normalized_experience = min(avg_experience / 10, 1.0)
        
        # Calcular puntuación ponderada
        readiness_score = (
            skill_coverage * 0.4 +
            (avg_performance / 10) * 0.4 +
            normalized_experience * 0.2
        )
        
        return readiness_score
    
    def assess_team_training_needs(self, launch_name: str) -> Dict[str, Any]:
        """Evaluar necesidades de capacitación del equipo de lanzamiento"""
        logger.info(f"Evaluando necesidades de capacitación para equipo: {launch_name}")
        
        if launch_name not in self.launch_teams:
            return {"error": "Equipo de lanzamiento no encontrado"}
        
        team = self.launch_teams[launch_name]
        team_members = team["team_members"]
        
        # Analizar habilidades del equipo
        all_skills = [skill for member in team_members for skill in member["skills"]]
        skill_frequency = {}
        for skill in all_skills:
            skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
        
        # Identificar brechas de habilidades
        common_skills = [skill for skill, count in skill_frequency.items() if count >= len(team_members) // 2]
        missing_skills = [skill for skill, count in skill_frequency.items() if count < len(team_members) // 3]
        
        # Generar recomendaciones de capacitación
        training_recommendations = {
            "launch_name": launch_name,
            "team_analysis": {
                "total_members": len(team_members),
                "skill_diversity": len(set(all_skills)),
                "common_skills": common_skills,
                "missing_skills": missing_skills,
                "skill_gaps": self._identify_skill_gaps(team_members)
            },
            "training_needs": [],
            "recommended_modules": [],
            "training_plan": {},
            "estimated_cost": 0,
            "estimated_duration": 0,
            "assessment_date": datetime.now().isoformat()
        }
        
        # Identificar necesidades específicas de capacitación
        training_needs = [
            {
                "skill": "AI/ML Fundamentals",
                "priority": "High",
                "affected_members": len([m for m in team_members if "AI" not in m["skills"]]),
                "estimated_hours": 8,
                "cost_per_person": 500
            },
            {
                "skill": "Project Management",
                "priority": "Medium",
                "affected_members": len([m for m in team_members if "Project Management" not in m["skills"]]),
                "estimated_hours": 6,
                "cost_per_person": 400
            },
            {
                "skill": "Data Analytics",
                "priority": "High",
                "affected_members": len([m for m in team_members if "Analytics" not in m["skills"]]),
                "estimated_hours": 10,
                "cost_per_person": 600
            }
        ]
        
        training_recommendations["training_needs"] = training_needs
        
        # Recomendar módulos específicos
        available_modules = list(self.hr_system.training_modules.values())
        recommended_modules = random.sample(available_modules, min(3, len(available_modules)))
        
        for module in recommended_modules:
            training_recommendations["recommended_modules"].append({
                "module_id": module.id,
                "title": module.title,
                "category": module.category,
                "duration": module.duration_hours,
                "effectiveness": module.effectiveness_score,
                "relevance": random.uniform(0.7, 0.95)
            })
        
        # Crear plan de capacitación
        training_recommendations["training_plan"] = {
            "phase_1": {
                "name": "Fundamentos",
                "duration_weeks": 2,
                "modules": [mod["module_id"] for mod in training_recommendations["recommended_modules"][:1]],
                "focus": "Habilidades básicas esenciales"
            },
            "phase_2": {
                "name": "Especialización",
                "duration_weeks": 3,
                "modules": [mod["module_id"] for mod in training_recommendations["recommended_modules"][1:2]],
                "focus": "Habilidades específicas del lanzamiento"
            },
            "phase_3": {
                "name": "Aplicación",
                "duration_weeks": 2,
                "modules": [mod["module_id"] for mod in training_recommendations["recommended_modules"][2:]],
                "focus": "Aplicación práctica en el proyecto"
            }
        }
        
        # Calcular costos y duración
        total_cost = sum([need["affected_members"] * need["cost_per_person"] for need in training_needs])
        total_duration = sum([need["affected_members"] * need["estimated_hours"] for need in training_needs])
        
        training_recommendations["estimated_cost"] = total_cost
        training_recommendations["estimated_duration"] = total_duration
        
        return training_recommendations
    
    def _identify_skill_gaps(self, team_members: List[Dict[str, Any]]) -> List[str]:
        """Identificar brechas de habilidades en el equipo"""
        all_skills = [skill for member in team_members for skill in member["skills"]]
        unique_skills = set(all_skills)
        
        # Habilidades críticas para lanzamientos
        critical_skills = [
            "Project Management", "Data Analytics", "AI/ML", 
            "Communication", "Leadership", "Marketing"
        ]
        
        missing_critical = [skill for skill in critical_skills if skill not in unique_skills]
        return missing_critical
    
    def optimize_team_performance(self, launch_name: str) -> Dict[str, Any]:
        """Optimizar rendimiento del equipo usando IA"""
        logger.info(f"Optimizando rendimiento del equipo: {launch_name}")
        
        if launch_name not in self.launch_teams:
            return {"error": "Equipo de lanzamiento no encontrado"}
        
        team = self.launch_teams[launch_name]
        
        # Análisis de rendimiento actual
        current_performance = {
            "team_readiness": team["team_readiness_score"],
            "skill_coverage": team["skill_coverage"],
            "average_performance": team["average_performance"],
            "experience_level": team["average_experience"]
        }
        
        # Generar recomendaciones de optimización
        optimization_recommendations = {
            "launch_name": launch_name,
            "current_performance": current_performance,
            "optimization_areas": [],
            "recommended_actions": [],
            "expected_improvements": {},
            "implementation_plan": {},
            "optimization_date": datetime.now().isoformat()
        }
        
        # Identificar áreas de optimización
        optimization_areas = []
        
        if current_performance["skill_coverage"] < 0.8:
            optimization_areas.append({
                "area": "Skill Coverage",
                "current_score": current_performance["skill_coverage"],
                "target_score": 0.9,
                "priority": "High"
            })
        
        if current_performance["average_performance"] < 8.0:
            optimization_areas.append({
                "area": "Team Performance",
                "current_score": current_performance["average_performance"],
                "target_score": 8.5,
                "priority": "Medium"
            })
        
        if current_performance["experience_level"] < 5.0:
            optimization_areas.append({
                "area": "Experience Level",
                "current_score": current_performance["experience_level"],
                "target_score": 6.0,
                "priority": "Medium"
            })
        
        optimization_recommendations["optimization_areas"] = optimization_areas
        
        # Recomendar acciones específicas
        recommended_actions = [
            {
                "action": "Cross-training Program",
                "description": "Implementar programa de capacitación cruzada entre miembros del equipo",
                "impact": "Mejora de skill coverage en 15-20%",
                "timeline": "4-6 semanas",
                "cost": random.randint(2000, 5000)
            },
            {
                "action": "Mentorship Program",
                "description": "Establecer programa de mentoría con empleados senior",
                "impact": "Mejora de rendimiento en 10-15%",
                "timeline": "8-12 semanas",
                "cost": random.randint(1000, 3000)
            },
            {
                "action": "Team Building Activities",
                "description": "Actividades de construcción de equipo y colaboración",
                "impact": "Mejora de cohesión del equipo en 20-25%",
                "timeline": "2-4 semanas",
                "cost": random.randint(500, 1500)
            }
        ]
        
        optimization_recommendations["recommended_actions"] = recommended_actions
        
        # Mejoras esperadas
        optimization_recommendations["expected_improvements"] = {
            "skill_coverage_improvement": random.uniform(0.10, 0.25),
            "performance_improvement": random.uniform(0.08, 0.20),
            "team_cohesion_improvement": random.uniform(0.15, 0.30),
            "overall_readiness_improvement": random.uniform(0.12, 0.28)
        }
        
        # Plan de implementación
        optimization_recommendations["implementation_plan"] = {
            "week_1_2": {
                "activities": ["Assessment detallado", "Planificación de capacitación"],
                "deliverables": ["Plan de capacitación", "Cronograma de actividades"]
            },
            "week_3_6": {
                "activities": ["Implementación de capacitación", "Programa de mentoría"],
                "deliverables": ["Progreso de capacitación", "Reportes de mentoría"]
            },
            "week_7_8": {
                "activities": ["Evaluación de progreso", "Ajustes finales"],
                "deliverables": ["Reporte final", "Recomendaciones futuras"]
            }
        }
        
        return optimization_recommendations
    
    def generate_integrated_analytics(self) -> Dict[str, Any]:
        """Generar analytics integrados de RRHH y lanzamientos"""
        logger.info("Generando analytics integrados")
        
        # Analytics de RRHH
        hr_analytics = self.hr_system.generate_hr_analytics()
        
        # Analytics de lanzamientos
        launch_metrics = self.launch_system.get_real_time_metrics()
        
        # Analytics integrados
        integrated_analytics = {
            "system_overview": {
                "total_employees": hr_analytics["overview"]["total_employees"],
                "active_launch_teams": len(self.launch_teams),
                "system_uptime": str(datetime.now() - self.start_time),
                "integration_status": "Active"
            },
            "hr_metrics": {
                "average_performance": hr_analytics["overview"]["average_performance"],
                "training_effectiveness": hr_analytics["training_effectiveness"],
                "skill_distribution": hr_analytics["skill_distribution"],
                "career_development": hr_analytics["career_development"]
            },
            "launch_metrics": {
                "ai_operations": launch_metrics["ai_operations"],
                "system_performance": launch_metrics["system"],
                "performance_metrics": launch_metrics["performance"]
            },
            "team_analytics": {
                "total_teams": len(self.launch_teams),
                "average_team_size": sum([team["team_size"] for team in self.launch_teams.values()]) / max(len(self.launch_teams), 1),
                "average_readiness": sum([team["team_readiness_score"] for team in self.launch_teams.values()]) / max(len(self.launch_teams), 1),
                "skill_coverage_teams": sum([team["skill_coverage"] for team in self.launch_teams.values()]) / max(len(self.launch_teams), 1)
            },
            "predictive_insights": {
                "launch_success_probability": random.uniform(0.75, 0.95),
                "team_performance_forecast": "Improving",
                "training_needs_forecast": "AI/ML skills in high demand",
                "resource_optimization_potential": random.uniform(0.15, 0.35)
            },
            "recommendations": [
                "Implementar capacitación en IA/ML para equipos de lanzamiento",
                "Establecer programa de mentoría cross-departmental",
                "Optimizar asignación de recursos basada en habilidades",
                "Crear métricas de rendimiento integradas"
            ],
            "generation_date": datetime.now().isoformat()
        }
        
        self.integrated_analytics = integrated_analytics
        return integrated_analytics
    
    def create_launch_team_dashboard_data(self) -> Dict[str, Any]:
        """Crear datos para dashboard de equipos de lanzamiento"""
        logger.info("Generando datos para dashboard de equipos")
        
        dashboard_data = {
            "summary_cards": {
                "total_teams": len(self.launch_teams),
                "total_team_members": sum([team["team_size"] for team in self.launch_teams.values()]),
                "average_readiness": sum([team["team_readiness_score"] for team in self.launch_teams.values()]) / max(len(self.launch_teams), 1),
                "teams_ready_for_launch": len([team for team in self.launch_teams.values() if team["team_readiness_score"] > 0.8])
            },
            "team_performance": {
                "team_names": list(self.launch_teams.keys()),
                "readiness_scores": [team["team_readiness_score"] for team in self.launch_teams.values()],
                "skill_coverage": [team["skill_coverage"] for team in self.launch_teams.values()],
                "team_sizes": [team["team_size"] for team in self.launch_teams.values()]
            },
            "skill_analysis": {
                "most_common_skills": self._get_most_common_skills(),
                "skill_gaps": self._get_team_skill_gaps(),
                "training_priorities": self._get_training_priorities()
            },
            "recent_activities": [
                {
                    "type": "team_created",
                    "team": list(self.launch_teams.keys())[-1] if self.launch_teams else "N/A",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "type": "training_assessment",
                    "description": "Evaluación de necesidades de capacitación completada",
                    "timestamp": (datetime.now() - timedelta(hours=2)).isoformat()
                },
                {
                    "type": "performance_optimization",
                    "description": "Optimización de rendimiento del equipo ejecutada",
                    "timestamp": (datetime.now() - timedelta(hours=5)).isoformat()
                }
            ],
            "alerts": [
                {
                    "type": "warning",
                    "message": f"{len([t for t in self.launch_teams.values() if t['team_readiness_score'] < 0.7])} equipos necesitan capacitación adicional",
                    "priority": "medium"
                },
                {
                    "type": "info",
                    "message": "Nuevos módulos de capacitación disponibles",
                    "priority": "low"
                }
            ],
            "generation_time": datetime.now().isoformat()
        }
        
        return dashboard_data
    
    def _get_most_common_skills(self) -> List[Dict[str, Any]]:
        """Obtener habilidades más comunes en los equipos"""
        all_skills = []
        for team in self.launch_teams.values():
            all_skills.extend(team["team_skills"])
        
        skill_counts = {}
        for skill in all_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        return [{"skill": skill, "count": count} for skill, count in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    
    def _get_team_skill_gaps(self) -> List[str]:
        """Obtener brechas de habilidades comunes en los equipos"""
        critical_skills = ["AI/ML", "Data Analytics", "Project Management", "Leadership"]
        team_skills = set()
        
        for team in self.launch_teams.values():
            team_skills.update(team["team_skills"])
        
        return [skill for skill in critical_skills if skill not in team_skills]
    
    def _get_training_priorities(self) -> List[Dict[str, Any]]:
        """Obtener prioridades de capacitación"""
        return [
            {"skill": "AI/ML Fundamentals", "priority": "High", "affected_teams": len(self.launch_teams)},
            {"skill": "Data Analytics", "priority": "High", "affected_teams": len(self.launch_teams)},
            {"skill": "Project Management", "priority": "Medium", "affected_teams": len(self.launch_teams)},
            {"skill": "Leadership", "priority": "Medium", "affected_teams": len(self.launch_teams)}
        ]

def main():
    """Función principal del demo integrado"""
    print("🎓🚀" + "="*78)
    print("   INTEGRATED HR LAUNCH SYSTEM DEMO")
    print("   Sistema Integrado de RRHH y Planificación de Lanzamientos v1.0.0")
    print("="*82)
    print()
    
    # Inicializar sistema integrado
    integrated_system = IntegratedHRLaunchSystem()
    
    try:
        # Demo 1: Creación de Equipo de Lanzamiento
        print("👥 DEMO 1: CREACIÓN DE EQUIPO DE LANZAMIENTO")
        print("-" * 50)
        
        launch_requirements = {
            "required_skills": ["AI/ML", "Data Analytics", "Project Management", "Marketing"],
            "team_size": 4,
            "experience_level": "intermediate",
            "budget": "medium"
        }
        
        team = integrated_system.create_launch_team("AI Product Launch", launch_requirements)
        print(f"🚀 Lanzamiento: {team['launch_name']}")
        print(f"   Tamaño del equipo: {team['team_size']} miembros")
        print(f"   Cobertura de habilidades: {team['skill_coverage']:.1%}")
        print(f"   Puntuación de preparación: {team['team_readiness_score']:.1%}")
        print(f"   Experiencia promedio: {team['average_experience']:.1f} años")
        print(f"   Rendimiento promedio: {team['average_performance']:.1f}/10")
        print()
        
        # Demo 2: Evaluación de Necesidades de Capacitación
        print("📚 DEMO 2: EVALUACIÓN DE NECESIDADES DE CAPACITACIÓN")
        print("-" * 50)
        
        training_needs = integrated_system.assess_team_training_needs("AI Product Launch")
        print(f"📊 Análisis del equipo: {training_needs['launch_name']}")
        print(f"   Miembros del equipo: {training_needs['team_analysis']['total_members']}")
        print(f"   Diversidad de habilidades: {training_needs['team_analysis']['skill_diversity']}")
        print(f"   Habilidades comunes: {', '.join(training_needs['team_analysis']['common_skills'])}")
        print(f"   Brechas identificadas: {len(training_needs['team_analysis']['skill_gaps'])}")
        print(f"   Costo estimado de capacitación: ${training_needs['estimated_cost']:,}")
        print(f"   Duración estimada: {training_needs['estimated_duration']} horas")
        print()
        
        # Demo 3: Optimización de Rendimiento del Equipo
        print("⚡ DEMO 3: OPTIMIZACIÓN DE RENDIMIENTO DEL EQUIPO")
        print("-" * 50)
        
        optimization = integrated_system.optimize_team_performance("AI Product Launch")
        print(f"🎯 Optimización para: {optimization['launch_name']}")
        print(f"   Preparación actual: {optimization['current_performance']['team_readiness']:.1%}")
        print(f"   Cobertura de habilidades: {optimization['current_performance']['skill_coverage']:.1%}")
        print(f"   Rendimiento promedio: {optimization['current_performance']['average_performance']:.1f}/10")
        print(f"   Áreas de optimización: {len(optimization['optimization_areas'])}")
        print(f"   Acciones recomendadas: {len(optimization['recommended_actions'])}")
        
        # Mostrar mejoras esperadas
        improvements = optimization['expected_improvements']
        print(f"   Mejoras esperadas:")
        print(f"     - Cobertura de habilidades: +{improvements['skill_coverage_improvement']:.1%}")
        print(f"     - Rendimiento del equipo: +{improvements['performance_improvement']:.1%}")
        print(f"     - Cohesión del equipo: +{improvements['team_cohesion_improvement']:.1%}")
        print()
        
        # Demo 4: Analytics Integrados
        print("📊 DEMO 4: ANALYTICS INTEGRADOS")
        print("-" * 50)
        
        analytics = integrated_system.generate_integrated_analytics()
        print(f"🔍 Resumen del sistema:")
        print(f"   Total de empleados: {analytics['system_overview']['total_employees']}")
        print(f"   Equipos de lanzamiento activos: {analytics['system_overview']['active_launch_teams']}")
        print(f"   Tiempo de actividad: {analytics['system_overview']['system_uptime']}")
        print(f"   Estado de integración: {analytics['system_overview']['integration_status']}")
        
        print(f"\n📈 Métricas de RRHH:")
        print(f"   Rendimiento promedio: {analytics['hr_metrics']['average_performance']:.1f}/10")
        print(f"   Efectividad de capacitación: {analytics['hr_metrics']['training_effectiveness']['average_completion_rate']:.1%}")
        print(f"   ROI en capacitación: {analytics['hr_metrics']['training_effectiveness']['roi_on_training']:.1f}x")
        
        print(f"\n🚀 Métricas de Lanzamiento:")
        print(f"   Operaciones de IA: {analytics['launch_metrics']['ai_operations']['content_generations']}")
        print(f"   Optimizaciones cuánticas: {analytics['launch_metrics']['ai_operations']['quantum_optimizations']}")
        print(f"   Tasa de éxito: {analytics['launch_metrics']['performance_metrics']['success_rate']:.1%}")
        
        print(f"\n👥 Analytics de Equipos:")
        print(f"   Total de equipos: {analytics['team_analytics']['total_teams']}")
        print(f"   Tamaño promedio: {analytics['team_analytics']['average_team_size']:.1f} miembros")
        print(f"   Preparación promedio: {analytics['team_analytics']['average_readiness']:.1%}")
        print(f"   Cobertura de habilidades: {analytics['team_analytics']['skill_coverage_teams']:.1%}")
        print()
        
        # Demo 5: Dashboard de Equipos
        print("📱 DEMO 5: DASHBOARD DE EQUIPOS DE LANZAMIENTO")
        print("-" * 50)
        
        dashboard = integrated_system.create_launch_team_dashboard_data()
        print(f"📊 Resumen del dashboard:")
        print(f"   Total de equipos: {dashboard['summary_cards']['total_teams']}")
        print(f"   Total de miembros: {dashboard['summary_cards']['total_team_members']}")
        print(f"   Preparación promedio: {dashboard['summary_cards']['average_readiness']:.1%}")
        print(f"   Equipos listos: {dashboard['summary_cards']['teams_ready_for_launch']}")
        
        print(f"\n🎯 Análisis de habilidades:")
        print(f"   Habilidades más comunes:")
        for skill_info in dashboard['skill_analysis']['most_common_skills'][:3]:
            print(f"     • {skill_info['skill']}: {skill_info['count']} equipos")
        
        print(f"   Brechas de habilidades: {', '.join(dashboard['skill_analysis']['skill_gaps'])}")
        
        print(f"\n📋 Actividades recientes: {len(dashboard['recent_activities'])}")
        print(f"🚨 Alertas activas: {len(dashboard['alerts'])}")
        print()
        
        # Demo 6: Predicciones Integradas
        print("🔮 DEMO 6: PREDICCIONES INTEGRADAS")
        print("-" * 50)
        
        predictions = analytics['predictive_insights']
        print(f"🎯 Predicciones del sistema:")
        print(f"   Probabilidad de éxito del lanzamiento: {predictions['launch_success_probability']:.1%}")
        print(f"   Pronóstico de rendimiento del equipo: {predictions['team_performance_forecast']}")
        print(f"   Pronóstico de necesidades de capacitación: {predictions['training_needs_forecast']}")
        print(f"   Potencial de optimización de recursos: {predictions['resource_optimization_potential']:.1%}")
        
        print(f"\n💡 Recomendaciones:")
        for i, rec in enumerate(analytics['recommendations'], 1):
            print(f"   {i}. {rec}")
        print()
        
        # Resumen Final
        print("🎉 RESUMEN FINAL DEL SISTEMA INTEGRADO")
        print("=" * 50)
        print("✅ Sistema de RRHH con IA - Integrado y funcionando")
        print("✅ Sistema de Planificación de Lanzamientos - Conectado")
        print("✅ Creación de Equipos de Lanzamiento - Automatizada")
        print("✅ Evaluación de Necesidades de Capacitación - Inteligente")
        print("✅ Optimización de Rendimiento - Basada en IA")
        print("✅ Analytics Integrados - Comprehensivos")
        print("✅ Dashboard de Equipos - Visualización completa")
        print("✅ Predicciones Integradas - Insights accionables")
        print()
        print("🎓🚀 Sistema Integrado de RRHH y Planificación de Lanzamientos v1.0.0")
        print("   ¡Completamente operativo y listo para transformar la gestión de equipos!")
        print("=" * 82)
        
    except Exception as e:
        logger.error(f"Error en el demo integrado: {e}")
        print(f"❌ Error durante la ejecución: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)






