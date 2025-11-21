"""
Sistema de Workflow Builder Visual.

Permite crear workflows personalizados para procesamiento de tickets.
"""
import logging
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Tipos de nodos."""
    TRIGGER = "trigger"
    ACTION = "action"
    CONDITION = "condition"
    LOOP = "loop"
    DELAY = "delay"
    WEBHOOK = "webhook"
    NOTIFICATION = "notification"


class ActionType(Enum):
    """Tipos de acciones."""
    SET_PRIORITY = "set_priority"
    ASSIGN_AGENT = "assign_agent"
    SEND_EMAIL = "send_email"
    CREATE_TASK = "create_task"
    UPDATE_STATUS = "update_status"
    ADD_TAG = "add_tag"
    CUSTOM = "custom"


@dataclass
class WorkflowNode:
    """Nodo de workflow."""
    node_id: str
    node_type: NodeType
    label: str
    config: Dict[str, Any]
    position: Dict[str, float]  # x, y para visualización
    connections: List[str] = None  # IDs de nodos conectados
    
    def __post_init__(self):
        if self.connections is None:
            self.connections = []


@dataclass
class Workflow:
    """Workflow personalizado."""
    workflow_id: str
    name: str
    description: str
    nodes: List[WorkflowNode]
    is_active: bool = True
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class WorkflowEngine:
    """Motor de ejecución de workflows."""
    
    def __init__(self):
        """Inicializa motor."""
        self.workflows: Dict[str, Workflow] = {}
        self.action_handlers: Dict[str, callable] = {}
        self._register_default_handlers()
    
    def register_workflow(self, workflow: Workflow):
        """Registra un workflow."""
        self.workflows[workflow.workflow_id] = workflow
    
    def execute_workflow(
        self,
        workflow_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ejecuta un workflow.
        
        Args:
            workflow_id: ID del workflow
            context: Contexto del ticket
            
        Returns:
            Resultado de ejecución
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        
        if not workflow.is_active:
            raise ValueError(f"Workflow {workflow_id} is not active")
        
        # Encontrar nodo inicial (trigger)
        start_node = next(
            (n for n in workflow.nodes if n.node_type == NodeType.TRIGGER),
            None
        )
        
        if not start_node:
            raise ValueError("Workflow has no trigger node")
        
        # Ejecutar workflow
        results = {}
        executed_nodes = set()
        
        self._execute_node(start_node, workflow, context, results, executed_nodes)
        
        return {
            "workflow_id": workflow_id,
            "executed": True,
            "results": results
        }
    
    def _execute_node(
        self,
        node: WorkflowNode,
        workflow: Workflow,
        context: Dict[str, Any],
        results: Dict[str, Any],
        executed_nodes: set
    ):
        """Ejecuta un nodo individual."""
        if node.node_id in executed_nodes:
            return  # Evitar loops infinitos
        
        executed_nodes.add(node.node_id)
        
        try:
            if node.node_type == NodeType.ACTION:
                result = self._execute_action(node, context)
                results[node.node_id] = result
                
            elif node.node_type == NodeType.CONDITION:
                should_continue = self._evaluate_condition(node, context)
                results[node.node_id] = {"condition_result": should_continue}
                
                # Si la condición es falsa, no continuar
                if not should_continue:
                    return
                    
            elif node.node_type == NodeType.DELAY:
                delay_seconds = node.config.get("delay_seconds", 0)
                import time
                time.sleep(delay_seconds)
                results[node.node_id] = {"delayed": delay_seconds}
            
            # Ejecutar nodos conectados
            for connected_id in node.connections:
                connected_node = next(
                    (n for n in workflow.nodes if n.node_id == connected_id),
                    None
                )
                if connected_node:
                    self._execute_node(connected_node, workflow, context, results, executed_nodes)
                    
        except Exception as e:
            logger.error(f"Error executing node {node.node_id}: {e}")
            results[node.node_id] = {"error": str(e)}
    
    def _execute_action(
        self,
        node: WorkflowNode,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta una acción."""
        action_type = node.config.get("action_type")
        params = node.config.get("params", {})
        
        if action_type in self.action_handlers:
            handler = self.action_handlers[action_type]
            return handler(node, context, params)
        
        return {"action": action_type, "status": "not_handled"}
    
    def _evaluate_condition(
        self,
        node: WorkflowNode,
        context: Dict[str, Any]
    ) -> bool:
        """Evalúa una condición."""
        condition = node.config.get("condition", {})
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")
        
        # Obtener valor del contexto
        field_value = self._get_nested_value(context, field)
        
        # Evaluar
        if operator == "equals":
            return field_value == value
        elif operator == "contains":
            return str(value) in str(field_value)
        elif operator == "greater_than":
            return float(field_value) > float(value)
        else:
            return False
    
    def _get_nested_value(self, context: Dict[str, Any], path: str) -> Any:
        """Obtiene valor anidado."""
        parts = path.split(".")
        value = context
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
        return value
    
    def _register_default_handlers(self):
        """Registra handlers por defecto."""
        self.action_handlers["set_priority"] = self._handle_set_priority
        self.action_handlers["assign_agent"] = self._handle_assign_agent
        self.action_handlers["send_email"] = self._handle_send_email
        self.action_handlers["update_status"] = self._handle_update_status
        self.action_handlers["add_tag"] = self._handle_add_tag
    
    def _handle_set_priority(
        self,
        node: WorkflowNode,
        context: Dict[str, Any],
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handler para set_priority."""
        priority = params.get("priority")
        return {"action": "set_priority", "priority": priority, "status": "success"}
    
    def _handle_assign_agent(
        self,
        node: WorkflowNode,
        context: Dict[str, Any],
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handler para assign_agent."""
        agent_id = params.get("agent_id")
        return {"action": "assign_agent", "agent_id": agent_id, "status": "success"}
    
    def _handle_send_email(
        self,
        node: WorkflowNode,
        context: Dict[str, Any],
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handler para send_email."""
        recipient = params.get("recipient")
        subject = params.get("subject")
        return {"action": "send_email", "recipient": recipient, "status": "success"}
    
    def _handle_update_status(
        self,
        node: WorkflowNode,
        context: Dict[str, Any],
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handler para update_status."""
        status = params.get("status")
        return {"action": "update_status", "status": status, "status": "success"}
    
    def _handle_add_tag(
        self,
        node: WorkflowNode,
        context: Dict[str, Any],
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handler para add_tag."""
        tag = params.get("tag")
        return {"action": "add_tag", "tag": tag, "status": "success"}
    
    def register_handler(self, action_type: str, handler: callable):
        """Registra un handler personalizado."""
        self.action_handlers[action_type] = handler


class WorkflowBuilder:
    """Constructor de workflows."""
    
    @staticmethod
    def create_simple_workflow(
        workflow_id: str,
        name: str,
        actions: List[Dict[str, Any]]
    ) -> Workflow:
        """Crea un workflow simple."""
        nodes = []
        
        # Nodo trigger
        trigger = WorkflowNode(
            node_id="trigger-1",
            node_type=NodeType.TRIGGER,
            label="Ticket Created",
            config={"trigger_type": "ticket_created"},
            position={"x": 0, "y": 0}
        )
        nodes.append(trigger)
        
        # Nodos de acción
        prev_node_id = trigger.node_id
        for i, action in enumerate(actions):
            node = WorkflowNode(
                node_id=f"action-{i+1}",
                node_type=NodeType.ACTION,
                label=action.get("label", "Action"),
                config={
                    "action_type": action.get("action_type"),
                    "params": action.get("params", {})
                },
                position={"x": (i+1) * 200, "y": 0}
            )
            nodes.append(node)
            
            # Conectar al nodo anterior
            prev_node = next(n for n in nodes if n.node_id == prev_node_id)
            prev_node.connections.append(node.node_id)
            prev_node_id = node.node_id
        
        return Workflow(
            workflow_id=workflow_id,
            name=name,
            description=f"Workflow: {name}",
            nodes=nodes
        )

