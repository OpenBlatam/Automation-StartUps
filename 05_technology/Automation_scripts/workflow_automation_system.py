#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Automatización de Workflows para Marketing con IA
===========================================================
Automatiza procesos de marketing y optimiza flujos de trabajo.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Callable
import random
from enum import Enum
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

class WorkflowStatus(Enum):
    """Estados de un workflow"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskStatus(Enum):
    """Estados de una tarea"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class TriggerType(Enum):
    """Tipos de triggers"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"
    CONDITION_BASED = "condition_based"

@dataclass
class WorkflowTask:
    """Representa una tarea en un workflow"""
    id: str
    name: str
    task_type: str
    parameters: Dict[str, Any]
    dependencies: List[str]
    timeout_minutes: int = 30
    retry_count: int = 3
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    started_at: datetime = None
    completed_at: datetime = None
    error_message: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class Workflow:
    """Representa un workflow completo"""
    id: str
    name: str
    description: str
    tasks: List[WorkflowTask]
    triggers: List[Dict[str, Any]]
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_at: datetime = None
    updated_at: datetime = None
    last_run: datetime = None
    next_run: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

class WorkflowAutomationSystem:
    def __init__(self, campaigns_file='enhanced_1000_ai_marketing_campaigns.json'):
        """Inicializa el sistema de automatización de workflows"""
        with open(campaigns_file, 'r', encoding='utf-8') as f:
            self.campaigns = json.load(f)
        
        self.df = pd.DataFrame(self.campaigns)
        
        # Workflows almacenados
        self.workflows = {}
        
        # Historial de ejecuciones
        self.execution_history = []
        
        # Tipos de tareas disponibles
        self.task_types = {
            'send_email': self._execute_send_email,
            'create_campaign': self._execute_create_campaign,
            'analyze_performance': self._execute_analyze_performance,
            'optimize_budget': self._execute_optimize_budget,
            'generate_content': self._execute_generate_content,
            'run_ab_test': self._execute_run_ab_test,
            'send_alert': self._execute_send_alert,
            'update_campaign': self._execute_update_campaign,
            'generate_report': self._execute_generate_report,
            'schedule_post': self._execute_schedule_post
        }
        
        # Configuración del sistema
        self.config = {
            'max_concurrent_workflows': 10,
            'default_timeout': 30,
            'max_retries': 3,
            'cleanup_after_days': 30
        }
    
    def create_workflow(self, name: str, description: str, 
                       tasks: List[Dict], triggers: List[Dict] = None) -> Dict[str, Any]:
        """Crea un nuevo workflow"""
        workflow_id = f"workflow_{len(self.workflows) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Crear tareas
        workflow_tasks = []
        for i, task_data in enumerate(tasks):
            task = WorkflowTask(
                id=f"{workflow_id}_task_{i+1}",
                name=task_data['name'],
                task_type=task_data['type'],
                parameters=task_data.get('parameters', {}),
                dependencies=task_data.get('dependencies', []),
                timeout_minutes=task_data.get('timeout_minutes', self.config['default_timeout']),
                retry_count=task_data.get('retry_count', self.config['max_retries'])
            )
            workflow_tasks.append(task)
        
        # Crear workflow
        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=description,
            tasks=workflow_tasks,
            triggers=triggers or [{'type': 'manual', 'enabled': True}]
        )
        
        # Validar workflow
        validation_result = self._validate_workflow(workflow)
        if not validation_result['valid']:
            return {"error": f"Workflow inválido: {validation_result['errors']}"}
        
        # Guardar workflow
        self.workflows[workflow_id] = workflow
        
        return {
            'workflow_id': workflow_id,
            'status': 'created',
            'message': 'Workflow creado exitosamente',
            'workflow': {
                'id': workflow.id,
                'name': workflow.name,
                'description': workflow.description,
                'tasks_count': len(workflow.tasks),
                'triggers_count': len(workflow.triggers)
            }
        }
    
    def _validate_workflow(self, workflow: Workflow) -> Dict[str, Any]:
        """Valida un workflow antes de guardarlo"""
        errors = []
        
        # Validar que todas las tareas tengan tipos válidos
        for task in workflow.tasks:
            if task.task_type not in self.task_types:
                errors.append(f"Tipo de tarea '{task.task_type}' no válido en tarea '{task.name}'")
        
        # Validar dependencias
        task_ids = [task.id for task in workflow.tasks]
        for task in workflow.tasks:
            for dep in task.dependencies:
                if dep not in task_ids:
                    errors.append(f"Dependencia '{dep}' no encontrada para tarea '{task.name}'")
        
        # Validar que no haya dependencias circulares
        if self._has_circular_dependencies(workflow.tasks):
            errors.append("Dependencias circulares detectadas")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _has_circular_dependencies(self, tasks: List[WorkflowTask]) -> bool:
        """Verifica si hay dependencias circulares"""
        visited = set()
        rec_stack = set()
        
        def has_cycle(task_id):
            if task_id in rec_stack:
                return True
            if task_id in visited:
                return False
            
            visited.add(task_id)
            rec_stack.add(task_id)
            
            task = next((t for t in tasks if t.id == task_id), None)
            if task:
                for dep in task.dependencies:
                    if has_cycle(dep):
                        return True
            
            rec_stack.remove(task_id)
            return False
        
        for task in tasks:
            if has_cycle(task.id):
                return True
        
        return False
    
    def execute_workflow(self, workflow_id: str, trigger_data: Dict = None) -> Dict[str, Any]:
        """Ejecuta un workflow"""
        if workflow_id not in self.workflows:
            return {"error": f"Workflow {workflow_id} no encontrado"}
        
        workflow = self.workflows[workflow_id]
        
        if workflow.status != WorkflowStatus.ACTIVE:
            return {"error": f"Workflow {workflow_id} no está activo"}
        
        # Crear ejecución
        execution_id = f"exec_{workflow_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        execution = {
            'execution_id': execution_id,
            'workflow_id': workflow_id,
            'status': 'running',
            'started_at': datetime.now().isoformat(),
            'tasks_completed': 0,
            'tasks_failed': 0,
            'tasks_total': len(workflow.tasks),
            'trigger_data': trigger_data or {},
            'task_results': []
        }
        
        # Ejecutar tareas en orden de dependencias
        task_execution_order = self._calculate_execution_order(workflow.tasks)
        
        for task_id in task_execution_order:
            task = next((t for t in workflow.tasks if t.id == task_id), None)
            if not task:
                continue
            
            # Verificar dependencias
            if not self._check_dependencies(task, execution['task_results']):
                task.status = TaskStatus.SKIPPED
                execution['task_results'].append({
                    'task_id': task.id,
                    'status': 'skipped',
                    'reason': 'Dependencias no cumplidas'
                })
                continue
            
            # Ejecutar tarea
            task_result = self._execute_task(task, execution['trigger_data'])
            execution['task_results'].append(task_result)
            
            if task_result['status'] == 'completed':
                execution['tasks_completed'] += 1
            else:
                execution['tasks_failed'] += 1
        
        # Finalizar ejecución
        execution['status'] = 'completed' if execution['tasks_failed'] == 0 else 'failed'
        execution['completed_at'] = datetime.now().isoformat()
        
        # Guardar en historial
        self.execution_history.append(execution)
        
        # Actualizar workflow
        workflow.last_run = datetime.now()
        
        return execution
    
    def _calculate_execution_order(self, tasks: List[WorkflowTask]) -> List[str]:
        """Calcula el orden de ejecución de las tareas basado en dependencias"""
        # Crear grafo de dependencias
        graph = {}
        in_degree = {}
        
        for task in tasks:
            graph[task.id] = []
            in_degree[task.id] = 0
        
        for task in tasks:
            for dep in task.dependencies:
                if dep in graph:
                    graph[dep].append(task.id)
                    in_degree[task.id] += 1
        
        # Topological sort
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    def _check_dependencies(self, task: WorkflowTask, completed_tasks: List[Dict]) -> bool:
        """Verifica si las dependencias de una tarea están cumplidas"""
        completed_task_ids = [t['task_id'] for t in completed_tasks if t['status'] == 'completed']
        
        for dep in task.dependencies:
            if dep not in completed_task_ids:
                return False
        
        return True
    
    def _execute_task(self, task: WorkflowTask, trigger_data: Dict) -> Dict[str, Any]:
        """Ejecuta una tarea específica"""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        try:
            # Obtener función de ejecución
            execute_func = self.task_types.get(task.task_type)
            if not execute_func:
                raise ValueError(f"Tipo de tarea '{task.task_type}' no soportado")
            
            # Ejecutar tarea
            result = execute_func(task.parameters, trigger_data)
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            return {
                'task_id': task.id,
                'status': 'completed',
                'result': result,
                'started_at': task.started_at.isoformat(),
                'completed_at': task.completed_at.isoformat(),
                'duration_seconds': (task.completed_at - task.started_at).total_seconds()
            }
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.now()
            
            return {
                'task_id': task.id,
                'status': 'failed',
                'error': str(e),
                'started_at': task.started_at.isoformat(),
                'completed_at': task.completed_at.isoformat(),
                'duration_seconds': (task.completed_at - task.started_at).total_seconds()
            }
    
    # Funciones de ejecución de tareas
    def _execute_send_email(self, parameters: Dict, trigger_data: Dict) -> Dict[str, Any]:
        """Ejecuta tarea de envío de email"""
        # Simular envío de email
        email_data = {
            'to': parameters.get('to', 'cliente@ejemplo.com'),
            'subject': parameters.get('subject', 'Email automático'),
            'template': parameters.get('template', 'default'),
            'sent_at': datetime.now().isoformat(),
            'status': 'sent'
        }
        
        return {
            'action': 'email_sent',
            'data': email_data,
            'message': f"Email enviado a {email_data['to']}"
        }
    
    def _execute_create_campaign(self, parameters: Dict, trigger_data: Dict) -> Dict[str, Any]:
        """Ejecuta tarea de creación de campaña"""
        # Simular creación de campaña
        campaign_data = {
            'name': parameters.get('name', 'Campaña automática'),
            'type': parameters.get('type', 'email'),
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'budget': parameters.get('budget', 1000)
        }
        
        return {
            'action': 'campaign_created',
            'data': campaign_data,
            'message': f"Campaña '{campaign_data['name']}' creada exitosamente"
        }
    
    def _execute_analyze_performance(self, parameters: Dict, trigger_data: Dict) -> Dict[str, Any]:
        """Ejecuta tarea de análisis de rendimiento"""
        # Simular análisis de rendimiento
        analysis_data = {
            'campaign_id': parameters.get('campaign_id', '1'),
            'metrics': {
                'conversion_rate': random.uniform(2, 8),
                'click_through_rate': random.uniform(1, 5),
                'cost_per_acquisition': random.uniform(20, 100),
                'return_on_ad_spend': random.uniform(2, 6)
            },
            'analyzed_at': datetime.now().isoformat()
        }
        
        return {
            'action': 'performance_analyzed',
            'data': analysis_data,
            'message': f"Análisis completado para campaña {analysis_data['campaign_id']}"
        }
    
    def _execute_optimize_budget(self, parameters: Dict, trigger_data: Dict) -> Dict[str, Any]:
        """Ejecuta tarea de optimización de presupuesto"""
        # Simular optimización de presupuesto
        optimization_data = {
            'campaign_id': parameters.get('campaign_id', '1'),
            'original_budget': parameters.get('budget', 1000),
            'optimized_budget': parameters.get('budget', 1000) * random.uniform(0.8, 1.2),
            'optimization_percent': random.uniform(-20, 20),
            'optimized_at': datetime.now().isoformat()
        }
        
        return {
            'action': 'budget_optimized',
            'data': optimization_data,
            'message': f"Presupuesto optimizado para campaña {optimization_data['campaign_id']}"
        }
    
    def _execute_generate_content(self, parameters: Dict, trigger_data: Dict) -> Dict[str, Any]:
        """Ejecuta tarea de generación de contenido"""
        # Simular generación de contenido
        content_data = {
            'type': parameters.get('type', 'email'),
            'content': f"Contenido generado automáticamente para {parameters.get('type', 'email')}",
            'variants': random.randint(1, 5),
            'generated_at': datetime.now().isoformat()
        }
        
        return {
            'action': 'content_generated',
            'data': content_data,
            'message': f"Contenido {content_data['type']} generado exitosamente"
        }
    
    def _execute_run_ab_test(self, parameters: Dict, trigger_data: Dict) -> Dict[str, Any]:
        """Ejecuta tarea de A/B testing"""
        # Simular A/B test
        test_data = {
            'test_id': f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'variants': parameters.get('variants', 2),
            'status': 'running',
            'started_at': datetime.now().isoformat(),
            'duration_days': parameters.get('duration_days', 7)
        }
        
        return {
            'action': 'ab_test_started',
            'data': test_data,
            'message': f"A/B test iniciado con {test_data['variants']} variantes"
        }
    
    def _execute_send_alert(self, parameters: Dict, trigger_data: Dict) -> Dict[str, Any]:
        """Ejecuta tarea de envío de alerta"""
        # Simular envío de alerta
        alert_data = {
            'type': parameters.get('type', 'info'),
            'message': parameters.get('message', 'Alerta automática'),
            'recipients': parameters.get('recipients', ['admin@ejemplo.com']),
            'sent_at': datetime.now().isoformat()
        }
        
        return {
            'action': 'alert_sent',
            'data': alert_data,
            'message': f"Alerta {alert_data['type']} enviada exitosamente"
        }
    
    def _execute_update_campaign(self, parameters: Dict, trigger_data: Dict) -> Dict[str, Any]:
        """Ejecuta tarea de actualización de campaña"""
        # Simular actualización de campaña
        update_data = {
            'campaign_id': parameters.get('campaign_id', '1'),
            'updates': parameters.get('updates', {}),
            'updated_at': datetime.now().isoformat()
        }
        
        return {
            'action': 'campaign_updated',
            'data': update_data,
            'message': f"Campaña {update_data['campaign_id']} actualizada exitosamente"
        }
    
    def _execute_generate_report(self, parameters: Dict, trigger_data: Dict) -> Dict[str, Any]:
        """Ejecuta tarea de generación de reporte"""
        # Simular generación de reporte
        report_data = {
            'report_id': f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'type': parameters.get('type', 'performance'),
            'period': parameters.get('period', 'weekly'),
            'generated_at': datetime.now().isoformat(),
            'file_path': f"/reports/{datetime.now().strftime('%Y%m%d')}_report.pdf"
        }
        
        return {
            'action': 'report_generated',
            'data': report_data,
            'message': f"Reporte {report_data['type']} generado exitosamente"
        }
    
    def _execute_schedule_post(self, parameters: Dict, trigger_data: Dict) -> Dict[str, Any]:
        """Ejecuta tarea de programación de post"""
        # Simular programación de post
        post_data = {
            'platform': parameters.get('platform', 'facebook'),
            'content': parameters.get('content', 'Post programado'),
            'scheduled_for': parameters.get('scheduled_for', datetime.now().isoformat()),
            'status': 'scheduled'
        }
        
        return {
            'action': 'post_scheduled',
            'data': post_data,
            'message': f"Post programado para {post_data['platform']}"
        }
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Obtiene el estado de un workflow"""
        if workflow_id not in self.workflows:
            return {"error": f"Workflow {workflow_id} no encontrado"}
        
        workflow = self.workflows[workflow_id]
        
        return {
            'workflow_id': workflow_id,
            'name': workflow.name,
            'status': workflow.status.value,
            'tasks_count': len(workflow.tasks),
            'created_at': workflow.created_at.isoformat(),
            'updated_at': workflow.updated_at.isoformat(),
            'last_run': workflow.last_run.isoformat() if workflow.last_run else None,
            'next_run': workflow.next_run.isoformat() if workflow.next_run else None
        }
    
    def get_execution_history(self, workflow_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene el historial de ejecuciones"""
        history = self.execution_history
        
        if workflow_id:
            history = [exec for exec in history if exec['workflow_id'] == workflow_id]
        
        # Ordenar por fecha de inicio (más reciente primero)
        history.sort(key=lambda x: x['started_at'], reverse=True)
        
        return history[:limit]
    
    def pause_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Pausa un workflow"""
        if workflow_id not in self.workflows:
            return {"error": f"Workflow {workflow_id} no encontrado"}
        
        workflow = self.workflows[workflow_id]
        workflow.status = WorkflowStatus.PAUSED
        workflow.updated_at = datetime.now()
        
        return {
            'workflow_id': workflow_id,
            'status': 'paused',
            'message': 'Workflow pausado exitosamente'
        }
    
    def resume_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Reanuda un workflow"""
        if workflow_id not in self.workflows:
            return {"error": f"Workflow {workflow_id} no encontrado"}
        
        workflow = self.workflows[workflow_id]
        workflow.status = WorkflowStatus.ACTIVE
        workflow.updated_at = datetime.now()
        
        return {
            'workflow_id': workflow_id,
            'status': 'active',
            'message': 'Workflow reanudado exitosamente'
        }
    
    def delete_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Elimina un workflow"""
        if workflow_id not in self.workflows:
            return {"error": f"Workflow {workflow_id} no encontrado"}
        
        del self.workflows[workflow_id]
        
        return {
            'workflow_id': workflow_id,
            'status': 'deleted',
            'message': 'Workflow eliminado exitosamente'
        }
    
    def get_workflow_templates(self) -> List[Dict[str, Any]]:
        """Obtiene plantillas de workflows predefinidos"""
        templates = [
            {
                'id': 'email_campaign_workflow',
                'name': 'Workflow de Campaña de Email',
                'description': 'Automatiza la creación, envío y análisis de campañas de email',
                'tasks': [
                    {
                        'name': 'Crear Campaña',
                        'type': 'create_campaign',
                        'parameters': {'type': 'email', 'budget': 1000}
                    },
                    {
                        'name': 'Generar Contenido',
                        'type': 'generate_content',
                        'parameters': {'type': 'email'},
                        'dependencies': ['Crear Campaña']
                    },
                    {
                        'name': 'Enviar Email',
                        'type': 'send_email',
                        'parameters': {'template': 'campaign_template'},
                        'dependencies': ['Generar Contenido']
                    },
                    {
                        'name': 'Analizar Rendimiento',
                        'type': 'analyze_performance',
                        'parameters': {'campaign_id': '1'},
                        'dependencies': ['Enviar Email']
                    }
                ]
            },
            {
                'id': 'social_media_workflow',
                'name': 'Workflow de Redes Sociales',
                'description': 'Automatiza la programación y análisis de contenido en redes sociales',
                'tasks': [
                    {
                        'name': 'Generar Contenido Social',
                        'type': 'generate_content',
                        'parameters': {'type': 'social_media'}
                    },
                    {
                        'name': 'Programar Post Facebook',
                        'type': 'schedule_post',
                        'parameters': {'platform': 'facebook'},
                        'dependencies': ['Generar Contenido Social']
                    },
                    {
                        'name': 'Programar Post Twitter',
                        'type': 'schedule_post',
                        'parameters': {'platform': 'twitter'},
                        'dependencies': ['Generar Contenido Social']
                    },
                    {
                        'name': 'Generar Reporte Social',
                        'type': 'generate_report',
                        'parameters': {'type': 'social_media'},
                        'dependencies': ['Programar Post Facebook', 'Programar Post Twitter']
                    }
                ]
            },
            {
                'id': 'ab_testing_workflow',
                'name': 'Workflow de A/B Testing',
                'description': 'Automatiza el proceso completo de A/B testing',
                'tasks': [
                    {
                        'name': 'Crear Variantes',
                        'type': 'generate_content',
                        'parameters': {'type': 'ab_test', 'variants': 3}
                    },
                    {
                        'name': 'Iniciar A/B Test',
                        'type': 'run_ab_test',
                        'parameters': {'variants': 3, 'duration_days': 7},
                        'dependencies': ['Crear Variantes']
                    },
                    {
                        'name': 'Monitorear Test',
                        'type': 'analyze_performance',
                        'parameters': {'campaign_id': 'ab_test'},
                        'dependencies': ['Iniciar A/B Test']
                    },
                    {
                        'name': 'Enviar Resultados',
                        'type': 'send_alert',
                        'parameters': {'type': 'info', 'message': 'A/B test completado'},
                        'dependencies': ['Monitorear Test']
                    }
                ]
            }
        ]
        
        return templates
    
    def create_workflow_from_template(self, template_id: str, custom_parameters: Dict = None) -> Dict[str, Any]:
        """Crea un workflow a partir de una plantilla"""
        templates = self.get_workflow_templates()
        template = next((t for t in templates if t['id'] == template_id), None)
        
        if not template:
            return {"error": f"Plantilla {template_id} no encontrada"}
        
        # Aplicar parámetros personalizados
        tasks = template['tasks'].copy()
        if custom_parameters:
            for task in tasks:
                if task['name'] in custom_parameters:
                    task['parameters'].update(custom_parameters[task['name']])
        
        return self.create_workflow(
            name=template['name'],
            description=template['description'],
            tasks=tasks
        )

def main():
    """Función principal de demostración"""
    print("=== SISTEMA DE AUTOMATIZACIÓN DE WORKFLOWS ===")
    
    # Inicializar sistema
    workflow_system = WorkflowAutomationSystem()
    
    # Crear workflow personalizado
    print("Creando workflow personalizado...")
    custom_workflow = workflow_system.create_workflow(
        name="Workflow de Marketing Completo",
        description="Automatiza todo el proceso de marketing desde creación hasta análisis",
        tasks=[
            {
                'name': 'Crear Campaña',
                'type': 'create_campaign',
                'parameters': {'type': 'email', 'budget': 2000}
            },
            {
                'name': 'Generar Contenido',
                'type': 'generate_content',
                'parameters': {'type': 'email'},
                'dependencies': ['Crear Campaña']
            },
            {
                'name': 'Optimizar Presupuesto',
                'type': 'optimize_budget',
                'parameters': {'campaign_id': '1', 'budget': 2000},
                'dependencies': ['Crear Campaña']
            },
            {
                'name': 'Enviar Email',
                'type': 'send_email',
                'parameters': {'template': 'campaign_template'},
                'dependencies': ['Generar Contenido', 'Optimizar Presupuesto']
            },
            {
                'name': 'Analizar Rendimiento',
                'type': 'analyze_performance',
                'parameters': {'campaign_id': '1'},
                'dependencies': ['Enviar Email']
            },
            {
                'name': 'Generar Reporte',
                'type': 'generate_report',
                'parameters': {'type': 'performance'},
                'dependencies': ['Analizar Rendimiento']
            }
        ]
    )
    
    if 'error' not in custom_workflow:
        workflow_id = custom_workflow['workflow_id']
        print(f"✅ Workflow creado: {workflow_id}")
        
        # Activar workflow
        workflow_system.workflows[workflow_id].status = WorkflowStatus.ACTIVE
        
        # Ejecutar workflow
        print("Ejecutando workflow...")
        execution = workflow_system.execute_workflow(workflow_id)
        
        if 'error' not in execution:
            print(f"\n📊 RESULTADOS DE EJECUCIÓN")
            print(f"ID de ejecución: {execution['execution_id']}")
            print(f"Estado: {execution['status']}")
            print(f"Tareas completadas: {execution['tasks_completed']}")
            print(f"Tareas fallidas: {execution['tasks_failed']}")
            print(f"Total de tareas: {execution['tasks_total']}")
            
            print(f"\n📋 DETALLES DE TAREAS")
            for task_result in execution['task_results']:
                print(f"• {task_result['task_id']}: {task_result['status']}")
                if task_result['status'] == 'completed':
                    print(f"  Resultado: {task_result['result']['message']}")
                elif task_result['status'] == 'failed':
                    print(f"  Error: {task_result['error']}")
    
    # Crear workflow desde plantilla
    print(f"\n🔄 CREANDO WORKFLOW DESDE PLANTILLA...")
    template_workflow = workflow_system.create_workflow_from_template(
        'email_campaign_workflow',
        custom_parameters={
            'Crear Campaña': {'budget': 1500, 'type': 'email'},
            'Generar Contenido': {'type': 'email', 'variants': 3}
        }
    )
    
    if 'error' not in template_workflow:
        template_workflow_id = template_workflow['workflow_id']
        print(f"✅ Workflow desde plantilla creado: {template_workflow_id}")
        
        # Activar y ejecutar
        workflow_system.workflows[template_workflow_id].status = WorkflowStatus.ACTIVE
        template_execution = workflow_system.execute_workflow(template_workflow_id)
        
        if 'error' not in template_execution:
            print(f"✅ Workflow de plantilla ejecutado exitosamente")
    
    # Mostrar plantillas disponibles
    print(f"\n📋 PLANTILLAS DISPONIBLES")
    templates = workflow_system.get_workflow_templates()
    for template in templates:
        print(f"• {template['name']}: {template['description']}")
    
    # Mostrar historial de ejecuciones
    print(f"\n📊 HISTORIAL DE EJECUCIONES")
    history = workflow_system.get_execution_history(limit=5)
    for exec in history:
        print(f"• {exec['execution_id']}: {exec['status']} ({exec['tasks_completed']}/{exec['tasks_total']} tareas)")
    
    print(f"\n✅ Sistema de automatización de workflows configurado y funcionando")

if __name__ == "__main__":
    main()
