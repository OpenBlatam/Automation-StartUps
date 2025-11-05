from datetime import datetime, timedelta
from app import db
from models import Product, InventoryRecord, SalesRecord
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import json
import os
import uuid
from enum import Enum

class ProjectStatus(Enum):
    """Estado del proyecto"""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskStatus(Enum):
    """Estado de la tarea"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

class ResourceType(Enum):
    """Tipo de recurso"""
    HUMAN = "human"
    EQUIPMENT = "equipment"
    MATERIAL = "material"
    FINANCIAL = "financial"
    TECHNOLOGICAL = "technological"

class Priority(Enum):
    """Prioridad"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Project:
    """Proyecto"""
    id: str
    name: str
    description: str
    status: ProjectStatus
    priority: Priority
    start_date: datetime
    end_date: datetime
    budget: float
    actual_cost: float = 0.0
    progress: float = 0.0
    project_manager: str
    team_members: List[str] = None
    stakeholders: List[str] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class Task:
    """Tarea"""
    id: str
    project_id: str
    name: str
    description: str
    status: TaskStatus
    priority: Priority
    assigned_to: str
    start_date: datetime
    due_date: datetime
    estimated_hours: float
    actual_hours: float = 0.0
    progress: float = 0.0
    dependencies: List[str] = None
    tags: List[str] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class Resource:
    """Recurso"""
    id: str
    name: str
    resource_type: ResourceType
    description: str
    capacity: float
    unit: str
    cost_per_unit: float
    availability: float = 1.0
    skills: List[str] = None
    location: str = None
    is_active: bool = True

@dataclass
class ResourceAllocation:
    """Asignación de recursos"""
    id: str
    project_id: str
    task_id: str
    resource_id: str
    allocated_quantity: float
    start_date: datetime
    end_date: datetime
    cost: float
    is_active: bool = True

@dataclass
class ProjectMilestone:
    """Hito del proyecto"""
    id: str
    project_id: str
    name: str
    description: str
    target_date: datetime
    actual_date: datetime = None
    status: str = "pending"  # pending, achieved, delayed
    deliverables: List[str] = None

class ProjectResourceService:
    """Servicio de gestión de proyectos y recursos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.projects = {}
        self.tasks = {}
        self.resources = {}
        self.resource_allocations = {}
        self.milestones = {}
        
        # Configurar recursos por defecto
        self._setup_default_resources()
        self._setup_sample_projects()
    
    def _setup_default_resources(self):
        """Configura recursos por defecto"""
        resources = [
            Resource(
                id="RES_001",
                name="Desarrollador Senior",
                resource_type=ResourceType.HUMAN,
                description="Desarrollador con experiencia en Python y Flask",
                capacity=40.0,  # horas por semana
                unit="hours",
                cost_per_unit=75.0,  # USD por hora
                skills=["Python", "Flask", "SQLAlchemy", "Machine Learning"],
                location="Oficina Principal"
            ),
            Resource(
                id="RES_002",
                name="Analista de Datos",
                resource_type=ResourceType.HUMAN,
                description="Analista especializado en análisis de datos y estadísticas",
                capacity=40.0,
                unit="hours",
                cost_per_unit=60.0,
                skills=["Pandas", "NumPy", "Scikit-learn", "Statistics"],
                location="Oficina Principal"
            ),
            Resource(
                id="RES_003",
                name="Servidor de Desarrollo",
                resource_type=ResourceType.TECHNOLOGICAL,
                description="Servidor para desarrollo y testing",
                capacity=1.0,
                unit="server",
                cost_per_unit=200.0,  # USD por mes
                location="Data Center"
            ),
            Resource(
                id="RES_004",
                name="Licencia de Software",
                resource_type=ResourceType.TECHNOLOGICAL,
                description="Licencias de software especializado",
                capacity=10.0,
                unit="licenses",
                cost_per_unit=500.0,  # USD por año
                location="Cloud"
            ),
            Resource(
                id="RES_005",
                name="Material de Oficina",
                resource_type=ResourceType.MATERIAL,
                description="Suministros de oficina y materiales",
                capacity=1000.0,
                unit="units",
                cost_per_unit=5.0,
                location="Almacén"
            )
        ]
        
        for resource in resources:
            self.resources[resource.id] = resource
    
    def _setup_sample_projects(self):
        """Configura proyectos de ejemplo"""
        projects = [
            Project(
                id="PROJ_001",
                name="Implementación de Sistema de Inventario Inteligente",
                description="Desarrollo e implementación de sistema completo de gestión de inventario",
                status=ProjectStatus.ACTIVE,
                priority=Priority.HIGH,
                start_date=datetime.utcnow() - timedelta(days=30),
                end_date=datetime.utcnow() + timedelta(days=60),
                budget=50000.0,
                actual_cost=15000.0,
                progress=30.0,
                project_manager="Juan Pérez",
                team_members=["Ana García", "Carlos López", "María Rodríguez"],
                stakeholders=["CEO", "CTO", "Operations Manager"],
                created_at=datetime.utcnow() - timedelta(days=30),
                updated_at=datetime.utcnow()
            ),
            Project(
                id="PROJ_002",
                name="Optimización de Procesos de Almacén",
                description="Optimización de procesos y flujos de trabajo en el almacén",
                status=ProjectStatus.PLANNING,
                priority=Priority.MEDIUM,
                start_date=datetime.utcnow() + timedelta(days=7),
                end_date=datetime.utcnow() + timedelta(days=45),
                budget=25000.0,
                project_manager="Ana García",
                team_members=["Carlos López", "Luis Martínez"],
                stakeholders=["Operations Manager", "Warehouse Manager"],
                created_at=datetime.utcnow() - timedelta(days=7),
                updated_at=datetime.utcnow()
            ),
            Project(
                id="PROJ_003",
                name="Integración con Sistemas Externos",
                description="Integración con sistemas de proveedores y clientes",
                status=ProjectStatus.ON_HOLD,
                priority=Priority.LOW,
                start_date=datetime.utcnow() - timedelta(days=15),
                end_date=datetime.utcnow() + timedelta(days=30),
                budget=15000.0,
                actual_cost=5000.0,
                progress=15.0,
                project_manager="Carlos López",
                team_members=["María Rodríguez"],
                stakeholders=["IT Manager", "Integration Team"],
                created_at=datetime.utcnow() - timedelta(days=15),
                updated_at=datetime.utcnow()
            )
        ]
        
        for project in projects:
            self.projects[project.id] = project
    
    def create_project(self, name: str, description: str, status: ProjectStatus,
                      priority: Priority, start_date: datetime, end_date: datetime,
                      budget: float, project_manager: str, team_members: List[str] = None,
                      stakeholders: List[str] = None) -> Dict:
        """Crea un nuevo proyecto"""
        try:
            project_id = f"PROJ_{uuid.uuid4().hex[:8].upper()}"
            
            project = Project(
                id=project_id,
                name=name,
                description=description,
                status=status,
                priority=priority,
                start_date=start_date,
                end_date=end_date,
                budget=budget,
                project_manager=project_manager,
                team_members=team_members or [],
                stakeholders=stakeholders or [],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.projects[project_id] = project
            
            return {
                'success': True,
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'description': project.description,
                    'status': project.status.value,
                    'priority': project.priority.value,
                    'start_date': project.start_date.isoformat(),
                    'end_date': project.end_date.isoformat(),
                    'budget': project.budget,
                    'project_manager': project.project_manager,
                    'team_members': project.team_members,
                    'stakeholders': project.stakeholders,
                    'created_at': project.created_at.isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error creando proyecto: {str(e)}')
            return {'error': str(e)}
    
    def create_task(self, project_id: str, name: str, description: str,
                   status: TaskStatus, priority: Priority, assigned_to: str,
                   start_date: datetime, due_date: datetime, estimated_hours: float,
                   dependencies: List[str] = None, tags: List[str] = None) -> Dict:
        """Crea una nueva tarea"""
        try:
            if project_id not in self.projects:
                return {'error': 'Proyecto no encontrado'}
            
            task_id = f"TASK_{uuid.uuid4().hex[:8].upper()}"
            
            task = Task(
                id=task_id,
                project_id=project_id,
                name=name,
                description=description,
                status=status,
                priority=priority,
                assigned_to=assigned_to,
                start_date=start_date,
                due_date=due_date,
                estimated_hours=estimated_hours,
                dependencies=dependencies or [],
                tags=tags or [],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.tasks[task_id] = task
            
            return {
                'success': True,
                'task': {
                    'id': task.id,
                    'project_id': task.project_id,
                    'name': task.name,
                    'description': task.description,
                    'status': task.status.value,
                    'priority': task.priority.value,
                    'assigned_to': task.assigned_to,
                    'start_date': task.start_date.isoformat(),
                    'due_date': task.due_date.isoformat(),
                    'estimated_hours': task.estimated_hours,
                    'dependencies': task.dependencies,
                    'tags': task.tags,
                    'created_at': task.created_at.isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error creando tarea: {str(e)}')
            return {'error': str(e)}
    
    def allocate_resource(self, project_id: str, task_id: str, resource_id: str,
                         allocated_quantity: float, start_date: datetime,
                         end_date: datetime) -> Dict:
        """Asigna un recurso a una tarea"""
        try:
            if project_id not in self.projects:
                return {'error': 'Proyecto no encontrado'}
            
            if task_id not in self.tasks:
                return {'error': 'Tarea no encontrada'}
            
            if resource_id not in self.resources:
                return {'error': 'Recurso no encontrado'}
            
            allocation_id = f"ALLOC_{uuid.uuid4().hex[:8].upper()}"
            
            # Calcular costo
            resource = self.resources[resource_id]
            duration_days = (end_date - start_date).days
            cost = allocated_quantity * resource.cost_per_unit * duration_days
            
            allocation = ResourceAllocation(
                id=allocation_id,
                project_id=project_id,
                task_id=task_id,
                resource_id=resource_id,
                allocated_quantity=allocated_quantity,
                start_date=start_date,
                end_date=end_date,
                cost=cost
            )
            
            self.resource_allocations[allocation_id] = allocation
            
            return {
                'success': True,
                'allocation': {
                    'id': allocation.id,
                    'project_id': allocation.project_id,
                    'task_id': allocation.task_id,
                    'resource_id': allocation.resource_id,
                    'allocated_quantity': allocation.allocated_quantity,
                    'start_date': allocation.start_date.isoformat(),
                    'end_date': allocation.end_date.isoformat(),
                    'cost': allocation.cost
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error asignando recurso: {str(e)}')
            return {'error': str(e)}
    
    def create_milestone(self, project_id: str, name: str, description: str,
                        target_date: datetime, deliverables: List[str] = None) -> Dict:
        """Crea un hito del proyecto"""
        try:
            if project_id not in self.projects:
                return {'error': 'Proyecto no encontrado'}
            
            milestone_id = f"MILESTONE_{uuid.uuid4().hex[:8].upper()}"
            
            milestone = ProjectMilestone(
                id=milestone_id,
                project_id=project_id,
                name=name,
                description=description,
                target_date=target_date,
                deliverables=deliverables or []
            )
            
            self.milestones[milestone_id] = milestone
            
            return {
                'success': True,
                'milestone': {
                    'id': milestone.id,
                    'project_id': milestone.project_id,
                    'name': milestone.name,
                    'description': milestone.description,
                    'target_date': milestone.target_date.isoformat(),
                    'status': milestone.status,
                    'deliverables': milestone.deliverables
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error creando hito: {str(e)}')
            return {'error': str(e)}
    
    def get_project_dashboard(self) -> Dict:
        """Obtiene datos para dashboard de proyectos"""
        try:
            # Estadísticas de proyectos
            total_projects = len(self.projects)
            active_projects = len([p for p in self.projects.values() if p.status == ProjectStatus.ACTIVE])
            completed_projects = len([p for p in self.projects.values() if p.status == ProjectStatus.COMPLETED])
            
            # Distribución por estado
            status_distribution = {}
            for project in self.projects.values():
                status = project.status.value
                status_distribution[status] = status_distribution.get(status, 0) + 1
            
            # Distribución por prioridad
            priority_distribution = {}
            for project in self.projects.values():
                priority = project.priority.value
                priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
            
            # Proyectos por presupuesto
            total_budget = sum(project.budget for project in self.projects.values())
            total_actual_cost = sum(project.actual_cost for project in self.projects.values())
            budget_utilization = (total_actual_cost / total_budget * 100) if total_budget > 0 else 0
            
            # Estadísticas de tareas
            total_tasks = len(self.tasks)
            completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
            in_progress_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])
            
            # Estadísticas de recursos
            total_resources = len(self.resources)
            active_resources = len([r for r in self.resources.values() if r.is_active])
            total_allocations = len(self.resource_allocations)
            
            # Proyectos próximos a vencer
            upcoming_deadlines = []
            for project in self.projects.values():
                if project.status == ProjectStatus.ACTIVE:
                    days_remaining = (project.end_date - datetime.utcnow()).days
                    if 0 <= days_remaining <= 30:
                        upcoming_deadlines.append({
                            'id': project.id,
                            'name': project.name,
                            'end_date': project.end_date.isoformat(),
                            'days_remaining': days_remaining,
                            'progress': project.progress
                        })
            
            return {
                'success': True,
                'dashboard': {
                    'projects': {
                        'total': total_projects,
                        'active': active_projects,
                        'completed': completed_projects,
                        'status_distribution': status_distribution,
                        'priority_distribution': priority_distribution
                    },
                    'budget': {
                        'total_budget': total_budget,
                        'total_actual_cost': total_actual_cost,
                        'budget_utilization': budget_utilization,
                        'remaining_budget': total_budget - total_actual_cost
                    },
                    'tasks': {
                        'total': total_tasks,
                        'completed': completed_tasks,
                        'in_progress': in_progress_tasks,
                        'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                    },
                    'resources': {
                        'total': total_resources,
                        'active': active_resources,
                        'allocations': total_allocations
                    },
                    'upcoming_deadlines': sorted(upcoming_deadlines, key=lambda x: x['days_remaining'])
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo dashboard de proyectos: {str(e)}')
            return {'error': str(e)}
    
    def get_resource_utilization(self) -> Dict:
        """Obtiene utilización de recursos"""
        try:
            resource_utilization = []
            
            for resource_id, resource in self.resources.items():
                if not resource.is_active:
                    continue
                
                # Calcular utilización actual
                current_allocations = [
                    alloc for alloc in self.resource_allocations.values()
                    if alloc.resource_id == resource_id and alloc.is_active
                ]
                
                total_allocated = sum(alloc.allocated_quantity for alloc in current_allocations)
                utilization_percentage = (total_allocated / resource.capacity * 100) if resource.capacity > 0 else 0
                
                # Calcular costo total
                total_cost = sum(alloc.cost for alloc in current_allocations)
                
                resource_utilization.append({
                    'resource_id': resource.id,
                    'name': resource.name,
                    'resource_type': resource.resource_type.value,
                    'capacity': resource.capacity,
                    'allocated': total_allocated,
                    'utilization_percentage': utilization_percentage,
                    'total_cost': total_cost,
                    'unit': resource.unit,
                    'cost_per_unit': resource.cost_per_unit
                })
            
            return {
                'success': True,
                'resource_utilization': resource_utilization,
                'total_resources': len(resource_utilization),
                'average_utilization': sum(r['utilization_percentage'] for r in resource_utilization) / len(resource_utilization) if resource_utilization else 0
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo utilización de recursos: {str(e)}')
            return {'error': str(e)}
    
    def generate_project_report(self, project_id: str) -> Dict:
        """Genera reporte de proyecto"""
        try:
            if project_id not in self.projects:
                return {'error': 'Proyecto no encontrado'}
            
            project = self.projects[project_id]
            
            # Obtener tareas del proyecto
            project_tasks = [task for task in self.tasks.values() if task.project_id == project_id]
            
            # Obtener asignaciones de recursos
            project_allocations = [alloc for alloc in self.resource_allocations.values() if alloc.project_id == project_id]
            
            # Obtener hitos del proyecto
            project_milestones = [milestone for milestone in self.milestones.values() if milestone.project_id == project_id]
            
            # Calcular métricas
            total_estimated_hours = sum(task.estimated_hours for task in project_tasks)
            total_actual_hours = sum(task.actual_hours for task in project_tasks)
            completed_tasks = len([task for task in project_tasks if task.status == TaskStatus.COMPLETED])
            
            # Calcular progreso promedio
            if project_tasks:
                avg_progress = sum(task.progress for task in project_tasks) / len(project_tasks)
            else:
                avg_progress = 0
            
            # Calcular costo total de recursos
            total_resource_cost = sum(alloc.cost for alloc in project_allocations)
            
            # Tareas por estado
            task_status_distribution = {}
            for task in project_tasks:
                status = task.status.value
                task_status_distribution[status] = task_status_distribution.get(status, 0) + 1
            
            # Tareas por prioridad
            task_priority_distribution = {}
            for task in project_tasks:
                priority = task.priority.value
                task_priority_distribution[priority] = task_priority_distribution.get(priority, 0) + 1
            
            return {
                'success': True,
                'report': {
                    'project': {
                        'id': project.id,
                        'name': project.name,
                        'description': project.description,
                        'status': project.status.value,
                        'priority': project.priority.value,
                        'start_date': project.start_date.isoformat(),
                        'end_date': project.end_date.isoformat(),
                        'budget': project.budget,
                        'actual_cost': project.actual_cost,
                        'progress': project.progress,
                        'project_manager': project.project_manager
                    },
                    'summary': {
                        'total_tasks': len(project_tasks),
                        'completed_tasks': completed_tasks,
                        'total_estimated_hours': total_estimated_hours,
                        'total_actual_hours': total_actual_hours,
                        'average_progress': avg_progress,
                        'total_resource_cost': total_resource_cost,
                        'budget_variance': project.actual_cost - project.budget
                    },
                    'task_distribution': {
                        'by_status': task_status_distribution,
                        'by_priority': task_priority_distribution
                    },
                    'milestones': [
                        {
                            'id': milestone.id,
                            'name': milestone.name,
                            'target_date': milestone.target_date.isoformat(),
                            'status': milestone.status,
                            'deliverables': milestone.deliverables
                        } for milestone in project_milestones
                    ],
                    'generated_at': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error generando reporte de proyecto: {str(e)}')
            return {'error': str(e)}

# Instancia global del servicio de gestión de proyectos y recursos
project_resource_service = ProjectResourceService()



