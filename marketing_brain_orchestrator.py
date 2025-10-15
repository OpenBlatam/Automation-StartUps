#!/usr/bin/env python3
"""
🎭 MARKETING BRAIN ORCHESTRATOR
Sistema Avanzado de Orquestación y Gestión de Workflows
Incluye automatización inteligente, gestión de procesos y coordinación de componentes
"""

import json
import asyncio
import threading
import time
import queue
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid
import schedule
import signal
import os
from contextlib import asynccontextmanager

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Estados de workflow"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class TaskPriority(Enum):
    """Prioridades de tareas"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

@dataclass
class WorkflowTask:
    """Tarea de workflow"""
    task_id: str
    task_name: str
    task_type: str
    function: Callable
    parameters: Dict[str, Any]
    dependencies: List[str]
    priority: TaskPriority
    timeout: int
    retry_count: int
    max_retries: int
    status: WorkflowStatus
    result: Any = None
    error: str = None
    created_at: str = None
    started_at: str = None
    completed_at: str = None

@dataclass
class Workflow:
    """Workflow completo"""
    workflow_id: str
    workflow_name: str
    description: str
    tasks: List[WorkflowTask]
    status: WorkflowStatus
    created_at: str
    started_at: str = None
    completed_at: str = None
    metadata: Dict[str, Any] = None

@dataclass
class OrchestrationEvent:
    """Evento de orquestación"""
    event_id: str
    event_type: str
    workflow_id: str
    task_id: str = None
    message: str = ""
    data: Dict[str, Any] = None
    timestamp: str = None

@dataclass
class SystemResource:
    """Recurso del sistema"""
    resource_id: str
    resource_type: str
    name: str
    status: str
    capacity: int
    current_usage: int
    metadata: Dict[str, Any] = None

class MarketingBrainOrchestrator:
    """
    Sistema Avanzado de Orquestación y Gestión de Workflows
    Incluye automatización inteligente, gestión de procesos y coordinación de componentes
    """
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.workflows = {}
        self.active_workflows = {}
        self.completed_workflows = {}
        self.failed_workflows = {}
        
        # Sistema de colas
        self.task_queue = queue.PriorityQueue()
        self.event_queue = queue.Queue()
        
        # Pool de workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.workers = []
        
        # Sistema de recursos
        self.resources = {}
        self.resource_monitor = {}
        
        # Configuración
        self.config = self._load_config()
        
        # Métricas
        self.metrics = {
            'total_workflows': 0,
            'completed_workflows': 0,
            'failed_workflows': 0,
            'active_workflows': 0,
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'average_execution_time': 0.0,
            'system_uptime': 0.0
        }
        
        # Estado del sistema
        self.is_running = False
        self.start_time = None
        
        # Event handlers
        self.event_handlers = {}
        
        # Scheduler para tareas programadas
        self.scheduler = schedule
        
        logger.info("🎭 Marketing Brain Orchestrator initialized successfully")
    
    def _load_config(self) -> Dict[str, Any]:
        """Cargar configuración del orquestador"""
        return {
            'workflow': {
                'max_concurrent_workflows': 5,
                'default_timeout': 300,
                'max_retries': 3,
                'retry_delay': 5
            },
            'resources': {
                'cpu_threshold': 80,
                'memory_threshold': 80,
                'disk_threshold': 90,
                'monitoring_interval': 30
            },
            'events': {
                'max_event_history': 1000,
                'event_retention_days': 30
            },
            'scheduling': {
                'timezone': 'UTC',
                'max_scheduled_tasks': 100
            }
        }
    
    def start_orchestrator(self):
        """Iniciar el orquestador"""
        logger.info("🚀 Starting Marketing Brain Orchestrator...")
        
        self.is_running = True
        self.start_time = datetime.now()
        
        # Iniciar workers
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.start()
            self.workers.append(worker)
        
        # Iniciar monitor de recursos
        resource_monitor = threading.Thread(target=self._resource_monitor_loop, daemon=True)
        resource_monitor.start()
        
        # Iniciar procesador de eventos
        event_processor = threading.Thread(target=self._event_processor_loop, daemon=True)
        event_processor.start()
        
        # Iniciar scheduler
        scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        scheduler_thread.start()
        
        logger.info("✅ Orchestrator started successfully")
    
    def stop_orchestrator(self):
        """Detener el orquestador"""
        logger.info("🛑 Stopping Marketing Brain Orchestrator...")
        
        self.is_running = False
        
        # Cancelar workflows activos
        for workflow_id, workflow in self.active_workflows.items():
            self.cancel_workflow(workflow_id)
        
        # Cerrar executor
        self.executor.shutdown(wait=True)
        
        logger.info("✅ Orchestrator stopped successfully")
    
    def _worker_loop(self):
        """Loop principal de workers"""
        while self.is_running:
            try:
                # Obtener tarea de la cola
                priority, task = self.task_queue.get(timeout=1)
                
                if task is None:
                    continue
                
                # Ejecutar tarea
                self._execute_task(task)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
    
    def _execute_task(self, task: WorkflowTask):
        """Ejecutar una tarea"""
        try:
            # Actualizar estado
            task.status = WorkflowStatus.RUNNING
            task.started_at = datetime.now().isoformat()
            
            # Emitir evento
            self._emit_event("task_started", task.workflow_id, task.task_id, f"Task {task.task_name} started")
            
            # Ejecutar función
            if asyncio.iscoroutinefunction(task.function):
                # Función asíncrona
                result = asyncio.run(task.function(**task.parameters))
            else:
                # Función síncrona
                result = task.function(**task.parameters)
            
            # Actualizar resultado
            task.result = result
            task.status = WorkflowStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            
            # Actualizar métricas
            self.metrics['completed_tasks'] += 1
            
            # Emitir evento
            self._emit_event("task_completed", task.workflow_id, task.task_id, f"Task {task.task_name} completed")
            
        except Exception as e:
            # Manejar error
            task.error = str(e)
            task.status = WorkflowStatus.FAILED
            task.completed_at = datetime.now().isoformat()
            
            # Actualizar métricas
            self.metrics['failed_tasks'] += 1
            
            # Emitir evento
            self._emit_event("task_failed", task.workflow_id, task.task_id, f"Task {task.task_name} failed: {e}")
            
            # Reintentar si es necesario
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = WorkflowStatus.PENDING
                time.sleep(self.config['workflow']['retry_delay'])
                self._queue_task(task)
    
    def _resource_monitor_loop(self):
        """Loop de monitoreo de recursos"""
        while self.is_running:
            try:
                # Monitorear recursos del sistema
                self._monitor_system_resources()
                
                # Actualizar métricas
                self._update_metrics()
                
                time.sleep(self.config['resources']['monitoring_interval'])
                
            except Exception as e:
                logger.error(f"Error in resource monitor: {e}")
    
    def _event_processor_loop(self):
        """Loop de procesamiento de eventos"""
        while self.is_running:
            try:
                # Procesar eventos
                if not self.event_queue.empty():
                    event = self.event_queue.get()
                    self._process_event(event)
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in event processor: {e}")
    
    def _scheduler_loop(self):
        """Loop del scheduler"""
        while self.is_running:
            try:
                self.scheduler.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
    
    def create_workflow(self, workflow_name: str, description: str = "", 
                       metadata: Dict[str, Any] = None) -> str:
        """Crear un nuevo workflow"""
        workflow_id = str(uuid.uuid4())
        
        workflow = Workflow(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            description=description,
            tasks=[],
            status=WorkflowStatus.PENDING,
            created_at=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        self.workflows[workflow_id] = workflow
        self.metrics['total_workflows'] += 1
        
        logger.info(f"Created workflow: {workflow_name} ({workflow_id})")
        return workflow_id
    
    def add_task_to_workflow(self, workflow_id: str, task_name: str, 
                           task_type: str, function: Callable,
                           parameters: Dict[str, Any] = None,
                           dependencies: List[str] = None,
                           priority: TaskPriority = TaskPriority.MEDIUM,
                           timeout: int = None,
                           max_retries: int = None) -> str:
        """Agregar tarea a un workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        task_id = str(uuid.uuid4())
        
        task = WorkflowTask(
            task_id=task_id,
            task_name=task_name,
            task_type=task_type,
            function=function,
            parameters=parameters or {},
            dependencies=dependencies or [],
            priority=priority,
            timeout=timeout or self.config['workflow']['default_timeout'],
            retry_count=0,
            max_retries=max_retries or self.config['workflow']['max_retries'],
            status=WorkflowStatus.PENDING,
            created_at=datetime.now().isoformat()
        )
        
        self.workflows[workflow_id].tasks.append(task)
        self.metrics['total_tasks'] += 1
        
        logger.info(f"Added task {task_name} to workflow {workflow_id}")
        return task_id
    
    def execute_workflow(self, workflow_id: str) -> str:
        """Ejecutar un workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        
        # Verificar límite de workflows concurrentes
        if len(self.active_workflows) >= self.config['workflow']['max_concurrent_workflows']:
            raise RuntimeError("Maximum concurrent workflows reached")
        
        # Actualizar estado
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now().isoformat()
        
        # Agregar a workflows activos
        self.active_workflows[workflow_id] = workflow
        self.metrics['active_workflows'] += 1
        
        # Emitir evento
        self._emit_event("workflow_started", workflow_id, message=f"Workflow {workflow.workflow_name} started")
        
        # Ejecutar tareas
        self._execute_workflow_tasks(workflow)
        
        logger.info(f"Started execution of workflow: {workflow.workflow_name}")
        return workflow_id
    
    def _execute_workflow_tasks(self, workflow: Workflow):
        """Ejecutar tareas de un workflow"""
        # Ordenar tareas por dependencias y prioridad
        sorted_tasks = self._sort_tasks_by_dependencies(workflow.tasks)
        
        # Ejecutar tareas
        for task in sorted_tasks:
            self._queue_task(task)
    
    def _sort_tasks_by_dependencies(self, tasks: List[WorkflowTask]) -> List[WorkflowTask]:
        """Ordenar tareas por dependencias"""
        # Implementación simple de ordenamiento topológico
        sorted_tasks = []
        remaining_tasks = tasks.copy()
        
        while remaining_tasks:
            # Encontrar tareas sin dependencias pendientes
            ready_tasks = []
            for task in remaining_tasks:
                if not task.dependencies or all(
                    dep_id in [t.task_id for t in sorted_tasks] 
                    for dep_id in task.dependencies
                ):
                    ready_tasks.append(task)
            
            if not ready_tasks:
                # Ciclo de dependencias detectado
                logger.warning("Circular dependency detected, executing remaining tasks")
                ready_tasks = remaining_tasks
            
            # Ordenar por prioridad
            ready_tasks.sort(key=lambda t: t.priority.value)
            
            # Agregar a la lista ordenada
            for task in ready_tasks:
                sorted_tasks.append(task)
                remaining_tasks.remove(task)
        
        return sorted_tasks
    
    def _queue_task(self, task: WorkflowTask):
        """Agregar tarea a la cola de ejecución"""
        priority = task.priority.value
        self.task_queue.put((priority, task))
    
    def cancel_workflow(self, workflow_id: str):
        """Cancelar un workflow"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow.status = WorkflowStatus.CANCELLED
            workflow.completed_at = datetime.now().isoformat()
            
            # Cancelar tareas pendientes
            for task in workflow.tasks:
                if task.status == WorkflowStatus.PENDING:
                    task.status = WorkflowStatus.CANCELLED
            
            # Mover a workflows completados
            self.completed_workflows[workflow_id] = workflow
            del self.active_workflows[workflow_id]
            
            self.metrics['active_workflows'] -= 1
            
            # Emitir evento
            self._emit_event("workflow_cancelled", workflow_id, message=f"Workflow {workflow.workflow_name} cancelled")
            
            logger.info(f"Cancelled workflow: {workflow.workflow_name}")
    
    def pause_workflow(self, workflow_id: str):
        """Pausar un workflow"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow.status = WorkflowStatus.PAUSED
            
            # Pausar tareas pendientes
            for task in workflow.tasks:
                if task.status == WorkflowStatus.PENDING:
                    task.status = WorkflowStatus.PAUSED
            
            # Emitir evento
            self._emit_event("workflow_paused", workflow_id, message=f"Workflow {workflow.workflow_name} paused")
            
            logger.info(f"Paused workflow: {workflow.workflow_name}")
    
    def resume_workflow(self, workflow_id: str):
        """Reanudar un workflow"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow.status = WorkflowStatus.RUNNING
            
            # Reanudar tareas pausadas
            for task in workflow.tasks:
                if task.status == WorkflowStatus.PAUSED:
                    task.status = WorkflowStatus.PENDING
                    self._queue_task(task)
            
            # Emitir evento
            self._emit_event("workflow_resumed", workflow_id, message=f"Workflow {workflow.workflow_name} resumed")
            
            logger.info(f"Resumed workflow: {workflow.workflow_name}")
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Obtener estado de un workflow"""
        if workflow_id in self.workflows:
            workflow = self.workflows[workflow_id]
            
            return {
                'workflow_id': workflow_id,
                'workflow_name': workflow.workflow_name,
                'status': workflow.status.value,
                'created_at': workflow.created_at,
                'started_at': workflow.started_at,
                'completed_at': workflow.completed_at,
                'total_tasks': len(workflow.tasks),
                'completed_tasks': len([t for t in workflow.tasks if t.status == WorkflowStatus.COMPLETED]),
                'failed_tasks': len([t for t in workflow.tasks if t.status == WorkflowStatus.FAILED]),
                'running_tasks': len([t for t in workflow.tasks if t.status == WorkflowStatus.RUNNING]),
                'pending_tasks': len([t for t in workflow.tasks if t.status == WorkflowStatus.PENDING])
            }
        
        return None
    
    def schedule_workflow(self, workflow_id: str, schedule_time: str, 
                         schedule_type: str = "once"):
        """Programar un workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        def execute_scheduled_workflow():
            try:
                self.execute_workflow(workflow_id)
            except Exception as e:
                logger.error(f"Error executing scheduled workflow {workflow_id}: {e}")
        
        if schedule_type == "once":
            # Programar una sola vez
            schedule_time_dt = datetime.fromisoformat(schedule_time)
            delay = (schedule_time_dt - datetime.now()).total_seconds()
            
            if delay > 0:
                threading.Timer(delay, execute_scheduled_workflow).start()
            else:
                logger.warning(f"Scheduled time {schedule_time} is in the past")
        
        elif schedule_type == "daily":
            # Programar diariamente
            self.scheduler.every().day.at(schedule_time).do(execute_scheduled_workflow)
        
        elif schedule_type == "weekly":
            # Programar semanalmente
            day, time_str = schedule_time.split(' ')
            getattr(self.scheduler.every(), day.lower()).at(time_str).do(execute_scheduled_workflow)
        
        logger.info(f"Scheduled workflow {workflow_id} for {schedule_time} ({schedule_type})")
    
    def _monitor_system_resources(self):
        """Monitorear recursos del sistema"""
        try:
            import psutil
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self.resources['cpu'] = SystemResource(
                resource_id='cpu',
                resource_type='processor',
                name='CPU',
                status='healthy' if cpu_percent < self.config['resources']['cpu_threshold'] else 'warning',
                capacity=100,
                current_usage=cpu_percent
            )
            
            # Memoria
            memory = psutil.virtual_memory()
            self.resources['memory'] = SystemResource(
                resource_id='memory',
                resource_type='memory',
                name='Memory',
                status='healthy' if memory.percent < self.config['resources']['memory_threshold'] else 'warning',
                capacity=100,
                current_usage=memory.percent
            )
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.resources['disk'] = SystemResource(
                resource_id='disk',
                resource_type='storage',
                name='Disk',
                status='healthy' if disk_percent < self.config['resources']['disk_threshold'] else 'warning',
                capacity=100,
                current_usage=disk_percent
            )
            
        except ImportError:
            logger.warning("psutil not available, skipping system resource monitoring")
        except Exception as e:
            logger.error(f"Error monitoring system resources: {e}")
    
    def _update_metrics(self):
        """Actualizar métricas del sistema"""
        if self.start_time:
            self.metrics['system_uptime'] = (datetime.now() - self.start_time).total_seconds()
        
        # Calcular tiempo promedio de ejecución
        if self.metrics['completed_tasks'] > 0:
            # Simplificado - en implementación real calcular basado en tiempos reales
            self.metrics['average_execution_time'] = 5.0
    
    def _emit_event(self, event_type: str, workflow_id: str, task_id: str = None, 
                   message: str = "", data: Dict[str, Any] = None):
        """Emitir evento"""
        event = OrchestrationEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            workflow_id=workflow_id,
            task_id=task_id,
            message=message,
            data=data or {},
            timestamp=datetime.now().isoformat()
        )
        
        self.event_queue.put(event)
    
    def _process_event(self, event: OrchestrationEvent):
        """Procesar evento"""
        # Ejecutar handlers registrados
        if event.event_type in self.event_handlers:
            for handler in self.event_handlers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")
        
        # Verificar si el workflow está completo
        if event.event_type == "task_completed":
            self._check_workflow_completion(event.workflow_id)
    
    def _check_workflow_completion(self, workflow_id: str):
        """Verificar si un workflow está completo"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            
            # Verificar si todas las tareas están completadas
            all_completed = all(
                task.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]
                for task in workflow.tasks
            )
            
            if all_completed:
                # Workflow completo
                workflow.status = WorkflowStatus.COMPLETED
                workflow.completed_at = datetime.now().isoformat()
                
                # Mover a workflows completados
                self.completed_workflows[workflow_id] = workflow
                del self.active_workflows[workflow_id]
                
                self.metrics['active_workflows'] -= 1
                self.metrics['completed_workflows'] += 1
                
                # Emitir evento
                self._emit_event("workflow_completed", workflow_id, message=f"Workflow {workflow.workflow_name} completed")
                
                logger.info(f"Workflow completed: {workflow.workflow_name}")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Registrar handler de eventos"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered event handler for {event_type}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema"""
        return {
            'orchestrator_status': 'running' if self.is_running else 'stopped',
            'uptime': self.metrics['system_uptime'],
            'metrics': self.metrics,
            'resources': {
                resource_id: {
                    'name': resource.name,
                    'status': resource.status,
                    'usage': resource.current_usage,
                    'capacity': resource.capacity
                }
                for resource_id, resource in self.resources.items()
            },
            'workflows': {
                'total': len(self.workflows),
                'active': len(self.active_workflows),
                'completed': len(self.completed_workflows),
                'failed': len(self.failed_workflows)
            },
            'tasks': {
                'total': self.metrics['total_tasks'],
                'completed': self.metrics['completed_tasks'],
                'failed': self.metrics['failed_tasks']
            }
        }
    
    def export_workflows(self, export_dir: str = "workflows") -> Dict[str, str]:
        """Exportar workflows"""
        Path(export_dir).mkdir(exist_ok=True)
        exported_files = {}
        
        # Exportar workflows
        workflows_data = {
            workflow_id: {
                'workflow_id': workflow.workflow_id,
                'workflow_name': workflow.workflow_name,
                'description': workflow.description,
                'status': workflow.status.value,
                'created_at': workflow.created_at,
                'started_at': workflow.started_at,
                'completed_at': workflow.completed_at,
                'metadata': workflow.metadata,
                'tasks': [
                    {
                        'task_id': task.task_id,
                        'task_name': task.task_name,
                        'task_type': task.task_type,
                        'status': task.status.value,
                        'priority': task.priority.value,
                        'dependencies': task.dependencies,
                        'created_at': task.created_at,
                        'started_at': task.started_at,
                        'completed_at': task.completed_at,
                        'error': task.error
                    }
                    for task in workflow.tasks
                ]
            }
            for workflow_id, workflow in self.workflows.items()
        }
        
        workflows_path = Path(export_dir) / f"workflows_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(workflows_path, 'w', encoding='utf-8') as f:
            json.dump(workflows_data, f, indent=2, ensure_ascii=False)
        exported_files['workflows'] = str(workflows_path)
        
        # Exportar métricas
        metrics_path = Path(export_dir) / f"orchestrator_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)
        exported_files['metrics'] = str(metrics_path)
        
        logger.info(f"📦 Exported workflows to {export_dir}")
        return exported_files


def main():
    """Función principal para demostrar el Orchestrator"""
    print("🎭 MARKETING BRAIN ORCHESTRATOR")
    print("=" * 50)
    
    # Crear orquestador
    orchestrator = MarketingBrainOrchestrator(max_workers=5)
    
    # Iniciar orquestador
    orchestrator.start_orchestrator()
    
    try:
        # Crear workflow de ejemplo
        print(f"\n📋 CREANDO WORKFLOW DE EJEMPLO...")
        workflow_id = orchestrator.create_workflow(
            workflow_name="Marketing Campaign Workflow",
            description="Workflow completo para campaña de marketing",
            metadata={'campaign_type': 'product_launch', 'target_audience': 'millennials'}
        )
        
        # Definir funciones de ejemplo
        def generate_concepts():
            print("   🧠 Generating marketing concepts...")
            time.sleep(2)
            return ["Concept 1", "Concept 2", "Concept 3"]
        
        def enhance_concepts(concepts):
            print(f"   🚀 Enhancing {len(concepts)} concepts with AI...")
            time.sleep(3)
            return [f"Enhanced {concept}" for concept in concepts]
        
        def generate_content(enhanced_concepts):
            print(f"   🎨 Generating content for {len(enhanced_concepts)} concepts...")
            time.sleep(2)
            return [f"Content for {concept}" for concept in enhanced_concepts]
        
        def optimize_performance(content_list):
            print(f"   ⚡ Optimizing performance for {len(content_list)} content pieces...")
            time.sleep(2)
            return {"optimization_score": 0.85, "recommendations": ["A", "B", "C"]}
        
        def deploy_campaign(optimization_data):
            print(f"   🚀 Deploying campaign with score {optimization_data['optimization_score']}...")
            time.sleep(1)
            return {"deployment_id": "deploy_001", "status": "active"}
        
        # Agregar tareas al workflow
        print(f"\n🔧 AGREGANDO TAREAS AL WORKFLOW...")
        
        task1_id = orchestrator.add_task_to_workflow(
            workflow_id=workflow_id,
            task_name="Generate Concepts",
            task_type="concept_generation",
            function=generate_concepts,
            priority=TaskPriority.HIGH
        )
        
        task2_id = orchestrator.add_task_to_workflow(
            workflow_id=workflow_id,
            task_name="Enhance Concepts",
            task_type="ai_enhancement",
            function=enhance_concepts,
            parameters={'concepts': []},  # Se llenará dinámicamente
            dependencies=[task1_id],
            priority=TaskPriority.HIGH
        )
        
        task3_id = orchestrator.add_task_to_workflow(
            workflow_id=workflow_id,
            task_name="Generate Content",
            task_type="content_generation",
            function=generate_content,
            parameters={'enhanced_concepts': []},  # Se llenará dinámicamente
            dependencies=[task2_id],
            priority=TaskPriority.MEDIUM
        )
        
        task4_id = orchestrator.add_task_to_workflow(
            workflow_id=workflow_id,
            task_name="Optimize Performance",
            task_type="performance_optimization",
            function=optimize_performance,
            parameters={'content_list': []},  # Se llenará dinámicamente
            dependencies=[task3_id],
            priority=TaskPriority.MEDIUM
        )
        
        task5_id = orchestrator.add_task_to_workflow(
            workflow_id=workflow_id,
            task_name="Deploy Campaign",
            task_type="deployment",
            function=deploy_campaign,
            parameters={'optimization_data': {}},  # Se llenará dinámicamente
            dependencies=[task4_id],
            priority=TaskPriority.CRITICAL
        )
        
        # Registrar handlers de eventos
        def on_task_completed(event):
            print(f"   ✅ Task completed: {event.task_id}")
        
        def on_workflow_completed(event):
            print(f"   🎉 Workflow completed: {event.workflow_id}")
        
        orchestrator.register_event_handler("task_completed", on_task_completed)
        orchestrator.register_event_handler("workflow_completed", on_workflow_completed)
        
        # Ejecutar workflow
        print(f"\n🚀 EJECUTANDO WORKFLOW...")
        orchestrator.execute_workflow(workflow_id)
        
        # Monitorear progreso
        print(f"\n📊 MONITOREANDO PROGRESO...")
        for i in range(30):  # Monitorear por 30 segundos
            status = orchestrator.get_workflow_status(workflow_id)
            if status:
                print(f"   Workflow Status: {status['status']}")
                print(f"   Tasks: {status['completed_tasks']}/{status['total_tasks']} completed")
                
                if status['status'] == 'completed':
                    break
            
            time.sleep(1)
        
        # Mostrar estado del sistema
        print(f"\n📈 ESTADO DEL SISTEMA:")
        system_status = orchestrator.get_system_status()
        print(f"   • Orquestador: {system_status['orchestrator_status']}")
        print(f"   • Uptime: {system_status['uptime']:.1f}s")
        print(f"   • Workflows: {system_status['workflows']['total']} total, {system_status['workflows']['active']} active")
        print(f"   • Tasks: {system_status['tasks']['completed']} completed, {system_status['tasks']['failed']} failed")
        
        # Exportar workflows
        print(f"\n💾 EXPORTANDO WORKFLOWS...")
        exported_files = orchestrator.export_workflows()
        print(f"   • Archivos exportados: {len(exported_files)}")
        for file_type, path in exported_files.items():
            print(f"     - {file_type}: {Path(path).name}")
        
        print(f"\n✅ ORCHESTRATOR DEMO COMPLETADO EXITOSAMENTE")
        print(f"🎉 El sistema de orquestación ha gestionado el workflow completo")
        print(f"   de marketing de forma automatizada y eficiente.")
        
    finally:
        # Detener orquestador
        orchestrator.stop_orchestrator()


if __name__ == "__main__":
    main()






