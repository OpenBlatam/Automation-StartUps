"""
Motor de Workflow para Documentos
==================================

Define y ejecuta workflows personalizados para procesamiento de documentos.
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class WorkflowStepType(Enum):
    """Tipos de pasos en workflow"""
    PROCESS = "process"
    VALIDATE = "validate"
    CLASSIFY = "classify"
    EXTRACT = "extract"
    NOTIFY = "notify"
    ARCHIVE = "archive"
    CUSTOM = "custom"


@dataclass
class WorkflowStep:
    """Paso de workflow"""
    step_id: str
    step_type: WorkflowStepType
    name: str
    config: Dict[str, Any]
    condition: Optional[str] = None  # Condición para ejecutar
    on_success: Optional[str] = None  # Siguiente paso si éxito
    on_failure: Optional[str] = None  # Siguiente paso si falla
    retry_count: int = 0
    timeout: int = 300  # segundos


@dataclass
class WorkflowDefinition:
    """Definición de workflow"""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    trigger_conditions: Dict[str, Any]
    enabled: bool = True
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class WorkflowEngine:
    """Motor de ejecución de workflows"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.logger = logging.getLogger(__name__)
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.step_handlers: Dict[WorkflowStepType, Callable] = {}
        self._load_workflows()
        self._register_default_handlers()
    
    def register_workflow(self, workflow: WorkflowDefinition):
        """Registra un workflow"""
        self.workflows[workflow.workflow_id] = workflow
        
        if self.db:
            self._save_workflow_to_db(workflow)
    
    def execute_workflow(
        self,
        workflow_id: str,
        document: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Ejecuta un workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow no encontrado: {workflow_id}")
        
        if not workflow.enabled:
            raise ValueError(f"Workflow deshabilitado: {workflow_id}")
        
        # Verificar condiciones de trigger
        if not self._check_trigger_conditions(workflow.trigger_conditions, document):
            return {"status": "skipped", "reason": "trigger_conditions_not_met"}
        
        context = context or {}
        context["workflow_id"] = workflow_id
        context["document"] = document
        context["results"] = {}
        context["current_step"] = workflow.steps[0].step_id if workflow.steps else None
        
        # Ejecutar pasos
        for step in workflow.steps:
            try:
                result = self._execute_step(step, context)
                context["results"][step.step_id] = result
                
                # Determinar siguiente paso
                if result.get("success"):
                    if step.on_success:
                        next_step = self._find_step(workflow, step.on_success)
                        if next_step:
                            context["current_step"] = next_step.step_id
                            continue
                else:
                    if step.on_failure:
                        next_step = self._find_step(workflow, step.on_failure)
                        if next_step:
                            context["current_step"] = next_step.step_id
                            continue
                    break  # Detener workflow si falla
                
            except Exception as e:
                self.logger.error(f"Error ejecutando paso {step.step_id}: {e}")
                if step.on_failure:
                    next_step = self._find_step(workflow, step.on_failure)
                    if next_step:
                        context["current_step"] = next_step.step_id
                        continue
                break
        
        return {
            "status": "completed",
            "workflow_id": workflow_id,
            "results": context["results"]
        }
    
    def _execute_step(
        self,
        step: WorkflowStep,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta un paso del workflow"""
        handler = self.step_handlers.get(step.step_type)
        if not handler:
            raise ValueError(f"Handler no registrado para: {step.step_type}")
        
        # Verificar condición
        if step.condition:
            if not self._evaluate_condition(step.condition, context):
                return {"success": True, "skipped": True, "reason": "condition_not_met"}
        
        # Ejecutar handler
        result = handler(step, context)
        return result
    
    def _register_default_handlers(self):
        """Registra handlers por defecto"""
        self.step_handlers[WorkflowStepType.PROCESS] = self._handle_process
        self.step_handlers[WorkflowStepType.VALIDATE] = self._handle_validate
        self.step_handlers[WorkflowStepType.NOTIFY] = self._handle_notify
        self.step_handlers[WorkflowStepType.ARCHIVE] = self._handle_archive
    
    def _handle_process(self, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para procesar documento"""
        # Implementación simplificada
        return {"success": True, "message": "Documento procesado"}
    
    def _handle_validate(self, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para validar documento"""
        # Implementación simplificada
        return {"success": True, "message": "Documento validado"}
    
    def _handle_notify(self, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para notificar"""
        # Implementación simplificada
        return {"success": True, "message": "Notificación enviada"}
    
    def _handle_archive(self, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para archivar"""
        # Implementación simplificada
        return {"success": True, "message": "Documento archivado"}
    
    def _check_trigger_conditions(
        self,
        conditions: Dict[str, Any],
        document: Dict[str, Any]
    ) -> bool:
        """Verifica condiciones de trigger"""
        for key, value in conditions.items():
            if key == "document_type":
                if document.get("document_type") != value:
                    return False
            elif key == "min_confidence":
                if document.get("classification_confidence", 0) < value:
                    return False
        return True
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evalúa condición (simplificado)"""
        # En producción usaría un motor de expresiones más robusto
        try:
            # Ejemplo: "document.document_type == 'invoice'"
            return eval(condition, {"document": context.get("document"), "__builtins__": {}})
        except:
            return False
    
    def _find_step(self, workflow: WorkflowDefinition, step_id: str) -> Optional[WorkflowStep]:
        """Encuentra paso por ID"""
        for step in workflow.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def _load_workflows(self):
        """Carga workflows desde BD"""
        if not self.db:
            return
        
        # Implementación simplificada
        pass
    
    def _save_workflow_to_db(self, workflow: WorkflowDefinition):
        """Guarda workflow en BD"""
        if not self.db:
            return
        
        # Implementación simplificada
        pass

