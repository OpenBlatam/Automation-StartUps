"""
Sistema de Workflows Personalizados para Nómina
Workflows configurables y extensibles
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class WorkflowStatus(str, Enum):
    """Estados del workflow"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStepStatus(str, Enum):
    """Estados de un paso"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """Paso de un workflow"""
    name: str
    function: Callable
    depends_on: List[str] = None
    retry_on_failure: bool = True
    max_retries: int = 3
    timeout_seconds: Optional[int] = None
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []


@dataclass
class WorkflowExecution:
    """Ejecución de un workflow"""
    workflow_id: str
    status: WorkflowStatus
    steps: List[str]
    current_step: Optional[str] = None
    results: Dict[str, Any] = None
    errors: List[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.results is None:
            self.results = {}
        if self.errors is None:
            self.errors = []
        if self.started_at is None:
            self.started_at = datetime.now()


class PayrollWorkflow:
    """Sistema de workflows para nómina"""
    
    def __init__(self, workflow_id: str):
        """
        Args:
            workflow_id: ID único del workflow
        """
        self.workflow_id = workflow_id
        self.steps: Dict[str, WorkflowStep] = {}
        self.execution: Optional[WorkflowExecution] = None
    
    def add_step(
        self,
        name: str,
        function: Callable,
        depends_on: Optional[List[str]] = None,
        retry_on_failure: bool = True,
        max_retries: int = 3,
        timeout_seconds: Optional[int] = None,
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    ) -> "PayrollWorkflow":
        """Agrega un paso al workflow"""
        step = WorkflowStep(
            name=name,
            function=function,
            depends_on=depends_on or [],
            retry_on_failure=retry_on_failure,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            condition=condition
        )
        
        self.steps[name] = step
        return self
    
    def execute(self, context: Optional[Dict[str, Any]] = None) -> WorkflowExecution:
        """Ejecuta el workflow"""
        if context is None:
            context = {}
        
        self.execution = WorkflowExecution(
            workflow_id=self.workflow_id,
            status=WorkflowStatus.RUNNING,
            steps=list(self.steps.keys())
        )
        
        try:
            # Ordenar pasos por dependencias
            ordered_steps = self._topological_sort()
            
            # Ejecutar pasos
            for step_name in ordered_steps:
                step = self.steps[step_name]
                
                # Verificar condición
                if step.condition and not step.condition(context):
                    logger.info(f"Skipping step {step_name} due to condition")
                    continue
                
                # Ejecutar paso
                self.execution.current_step = step_name
                
                try:
                    result = self._execute_step(step, context)
                    context[step_name] = result
                    self.execution.results[step_name] = result
                    
                except Exception as e:
                    error_msg = f"Step {step_name} failed: {e}"
                    logger.error(error_msg)
                    self.execution.errors.append(error_msg)
                    
                    if step.retry_on_failure:
                        # Intentar retry
                        for attempt in range(step.max_retries):
                            try:
                                result = self._execute_step(step, context)
                                context[step_name] = result
                                self.execution.results[step_name] = result
                                break
                            except Exception as retry_error:
                                if attempt == step.max_retries - 1:
                                    self.execution.status = WorkflowStatus.FAILED
                                    raise
                                logger.warning(f"Retry {attempt + 1} failed for {step_name}")
                    else:
                        self.execution.status = WorkflowStatus.FAILED
                        raise
            
            self.execution.status = WorkflowStatus.COMPLETED
            self.execution.completed_at = datetime.now()
            
        except Exception as e:
            self.execution.status = WorkflowStatus.FAILED
            self.execution.completed_at = datetime.now()
            logger.error(f"Workflow {self.workflow_id} failed: {e}")
        
        return self.execution
    
    def _execute_step(self, step: WorkflowStep, context: Dict[str, Any]) -> Any:
        """Ejecuta un paso individual"""
        import time
        
        start_time = time.time()
        
        try:
            result = step.function(**context)
            
            # Verificar timeout
            if step.timeout_seconds:
                elapsed = time.time() - start_time
                if elapsed > step.timeout_seconds:
                    raise TimeoutError(f"Step {step.name} exceeded timeout")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing step {step.name}: {e}")
            raise
    
    def _topological_sort(self) -> List[str]:
        """Ordena pasos por dependencias usando topological sort"""
        visited = set()
        result = []
        
        def visit(step_name: str):
            if step_name in visited:
                return
            
            visited.add(step_name)
            step = self.steps[step_name]
            
            # Visitar dependencias primero
            for dep in step.depends_on:
                if dep not in self.steps:
                    raise ValueError(f"Dependency {dep} not found for step {step_name}")
                visit(dep)
            
            result.append(step_name)
        
        # Visitar todos los pasos
        for step_name in self.steps.keys():
            if step_name not in visited:
                visit(step_name)
        
        return result
    
    def get_execution_status(self) -> Optional[Dict[str, Any]]:
        """Obtiene estado de ejecución"""
        if not self.execution:
            return None
        
        return {
            "workflow_id": self.execution.workflow_id,
            "status": self.execution.status.value,
            "current_step": self.execution.current_step,
            "steps_completed": len(self.execution.results),
            "total_steps": len(self.execution.steps),
            "errors": self.execution.errors,
            "started_at": self.execution.started_at.isoformat() if self.execution.started_at else None,
            "completed_at": self.execution.completed_at.isoformat() if self.execution.completed_at else None
        }


def create_payroll_workflow(workflow_id: str) -> PayrollWorkflow:
    """Factory para crear workflows de nómina"""
    return PayrollWorkflow(workflow_id)

