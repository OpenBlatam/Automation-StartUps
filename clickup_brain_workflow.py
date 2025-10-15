#!/usr/bin/env python3
"""
ClickUp Brain Workflow Engine
============================

Advanced workflow automation system with visual workflow designer,
conditional logic, and integration capabilities.
"""

import asyncio
import json
import yaml
from typing import Any, Dict, List, Optional, Union, Callable, Type
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging
from enum import Enum
import threading
from contextlib import asynccontextmanager
import uuid
from abc import ABC, abstractmethod

ROOT = Path(__file__).parent

class NodeType(Enum):
    """Workflow node types."""
    START = "start"
    END = "end"
    TASK = "task"
    CONDITION = "condition"
    PARALLEL = "parallel"
    MERGE = "merge"
    TIMER = "timer"
    WEBHOOK = "webhook"
    SCRIPT = "script"
    API_CALL = "api_call"
    DATABASE = "database"
    EMAIL = "email"
    NOTIFICATION = "notification"

class WorkflowStatus(Enum):
    """Workflow execution status."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ExecutionStatus(Enum):
    """Node execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class WorkflowNode:
    """Workflow node structure."""
    id: str
    type: NodeType
    name: str
    description: str = ""
    position: Dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0})
    properties: Dict[str, Any] = field(default_factory=dict)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    conditions: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class WorkflowConnection:
    """Workflow connection structure."""
    id: str
    source_node: str
    target_node: str
    source_output: str = "default"
    target_input: str = "default"
    condition: Optional[str] = None

@dataclass
class Workflow:
    """Workflow structure."""
    id: str
    name: str
    description: str = ""
    version: str = "1.0.0"
    status: WorkflowStatus = WorkflowStatus.DRAFT
    nodes: Dict[str, WorkflowNode] = field(default_factory=dict)
    connections: List[WorkflowConnection] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""

@dataclass
class ExecutionContext:
    """Workflow execution context."""
    execution_id: str
    workflow_id: str
    variables: Dict[str, Any] = field(default_factory=dict)
    node_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    execution_log: List[Dict[str, Any]] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: ExecutionStatus = ExecutionStatus.PENDING

class WorkflowNodeExecutor(ABC):
    """Base class for workflow node executors."""
    
    @abstractmethod
    async def execute(self, node: WorkflowNode, context: ExecutionContext) -> Dict[str, Any]:
        """Execute the workflow node."""
        pass
    
    @abstractmethod
    def validate(self, node: WorkflowNode) -> bool:
        """Validate node configuration."""
        pass

class TaskNodeExecutor(WorkflowNodeExecutor):
    """Executor for task nodes."""
    
    async def execute(self, node: WorkflowNode, context: ExecutionContext) -> Dict[str, Any]:
        """Execute task node."""
        task_type = node.properties.get('task_type', 'manual')
        
        if task_type == 'manual':
            return await self._execute_manual_task(node, context)
        elif task_type == 'automated':
            return await self._execute_automated_task(node, context)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _execute_manual_task(self, node: WorkflowNode, context: ExecutionContext) -> Dict[str, Any]:
        """Execute manual task."""
        # Simulate manual task execution
        await asyncio.sleep(1)
        
        return {
            'status': 'completed',
            'result': f"Manual task '{node.name}' completed",
            'outputs': {
                'default': f"Task {node.name} result"
            }
        }
    
    async def _execute_automated_task(self, node: WorkflowNode, context: ExecutionContext) -> Dict[str, Any]:
        """Execute automated task."""
        # Simulate automated task execution
        await asyncio.sleep(0.5)
        
        return {
            'status': 'completed',
            'result': f"Automated task '{node.name}' completed",
            'outputs': {
                'default': f"Automated {node.name} result"
            }
        }
    
    def validate(self, node: WorkflowNode) -> bool:
        """Validate task node."""
        return 'task_type' in node.properties

class ConditionNodeExecutor(WorkflowNodeExecutor):
    """Executor for condition nodes."""
    
    async def execute(self, node: WorkflowNode, context: ExecutionContext) -> Dict[str, Any]:
        """Execute condition node."""
        condition = node.properties.get('condition', 'true')
        
        # Evaluate condition
        result = self._evaluate_condition(condition, context.variables)
        
        return {
            'status': 'completed',
            'result': f"Condition evaluated to {result}",
            'outputs': {
                'true': result,
                'false': not result
            }
        }
    
    def _evaluate_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        """Evaluate condition expression."""
        try:
            # Simple condition evaluation (can be extended with more complex logic)
            if '==' in condition:
                parts = condition.split('==')
                var_name = parts[0].strip()
                value = parts[1].strip().strip('"\'')
                return str(variables.get(var_name, '')) == value
            elif '!=' in condition:
                parts = condition.split('!=')
                var_name = parts[0].strip()
                value = parts[1].strip().strip('"\'')
                return str(variables.get(var_name, '')) != value
            elif '>' in condition:
                parts = condition.split('>')
                var_name = parts[0].strip()
                value = float(parts[1].strip())
                return float(variables.get(var_name, 0)) > value
            elif '<' in condition:
                parts = condition.split('<')
                var_name = parts[0].strip()
                value = float(parts[1].strip())
                return float(variables.get(var_name, 0)) < value
            else:
                return condition.lower() == 'true'
        except Exception:
            return False
    
    def validate(self, node: WorkflowNode) -> bool:
        """Validate condition node."""
        return 'condition' in node.properties

class APICallNodeExecutor(WorkflowNodeExecutor):
    """Executor for API call nodes."""
    
    async def execute(self, node: WorkflowNode, context: ExecutionContext) -> Dict[str, Any]:
        """Execute API call node."""
        url = node.properties.get('url', '')
        method = node.properties.get('method', 'GET')
        headers = node.properties.get('headers', {})
        body = node.properties.get('body', '')
        
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                if method.upper() == 'GET':
                    async with session.get(url, headers=headers) as response:
                        result = await response.text()
                elif method.upper() == 'POST':
                    async with session.post(url, headers=headers, data=body) as response:
                        result = await response.text()
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                return {
                    'status': 'completed',
                    'result': f"API call to {url} completed",
                    'outputs': {
                        'default': result,
                        'status_code': response.status
                    }
                }
        except Exception as e:
            return {
                'status': 'failed',
                'result': f"API call failed: {str(e)}",
                'outputs': {
                    'default': None,
                    'error': str(e)
                }
            }
    
    def validate(self, node: WorkflowNode) -> bool:
        """Validate API call node."""
        return 'url' in node.properties and 'method' in node.properties

class EmailNodeExecutor(WorkflowNodeExecutor):
    """Executor for email nodes."""
    
    async def execute(self, node: WorkflowNode, context: ExecutionContext) -> Dict[str, Any]:
        """Execute email node."""
        to = node.properties.get('to', '')
        subject = node.properties.get('subject', '')
        body = node.properties.get('body', '')
        
        # Simulate email sending
        await asyncio.sleep(0.5)
        
        return {
            'status': 'completed',
            'result': f"Email sent to {to}",
            'outputs': {
                'default': f"Email sent successfully to {to}"
            }
        }
    
    def validate(self, node: WorkflowNode) -> bool:
        """Validate email node."""
        return 'to' in node.properties and 'subject' in node.properties

class TimerNodeExecutor(WorkflowNodeExecutor):
    """Executor for timer nodes."""
    
    async def execute(self, node: WorkflowNode, context: ExecutionContext) -> Dict[str, Any]:
        """Execute timer node."""
        duration = node.properties.get('duration', 1)  # seconds
        
        await asyncio.sleep(duration)
        
        return {
            'status': 'completed',
            'result': f"Timer completed after {duration} seconds",
            'outputs': {
                'default': f"Timer {duration}s completed"
            }
        }
    
    def validate(self, node: WorkflowNode) -> bool:
        """Validate timer node."""
        return 'duration' in node.properties

class WorkflowEngine:
    """Main workflow engine."""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.executions: Dict[str, ExecutionContext] = {}
        self.executors: Dict[NodeType, WorkflowNodeExecutor] = {}
        self.logger = logging.getLogger("workflow_engine")
        self._lock = threading.RLock()
        
        self._setup_executors()
    
    def _setup_executors(self) -> None:
        """Setup node executors."""
        self.executors[NodeType.TASK] = TaskNodeExecutor()
        self.executors[NodeType.CONDITION] = ConditionNodeExecutor()
        self.executors[NodeType.API_CALL] = APICallNodeExecutor()
        self.executors[NodeType.EMAIL] = EmailNodeExecutor()
        self.executors[NodeType.TIMER] = TimerNodeExecutor()
    
    def create_workflow(self, name: str, description: str = "", created_by: str = "") -> Workflow:
        """Create new workflow."""
        workflow_id = str(uuid.uuid4())
        
        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=description,
            created_by=created_by
        )
        
        with self._lock:
            self.workflows[workflow_id] = workflow
        
        self.logger.info(f"Created workflow: {name}")
        return workflow
    
    def add_node(self, workflow_id: str, node: WorkflowNode) -> None:
        """Add node to workflow."""
        with self._lock:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow = self.workflows[workflow_id]
            workflow.nodes[node.id] = node
            workflow.updated_at = datetime.now()
        
        self.logger.info(f"Added node {node.name} to workflow {workflow_id}")
    
    def add_connection(self, workflow_id: str, connection: WorkflowConnection) -> None:
        """Add connection to workflow."""
        with self._lock:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow = self.workflows[workflow_id]
            workflow.connections.append(connection)
            workflow.updated_at = datetime.now()
        
        self.logger.info(f"Added connection to workflow {workflow_id}")
    
    def validate_workflow(self, workflow_id: str) -> List[str]:
        """Validate workflow structure."""
        with self._lock:
            if workflow_id not in self.workflows:
                return [f"Workflow {workflow_id} not found"]
            
            workflow = self.workflows[workflow_id]
        
        errors = []
        
        # Check for start and end nodes
        start_nodes = [node for node in workflow.nodes.values() if node.type == NodeType.START]
        end_nodes = [node for node in workflow.nodes.values() if node.type == NodeType.END]
        
        if not start_nodes:
            errors.append("Workflow must have at least one start node")
        
        if not end_nodes:
            errors.append("Workflow must have at least one end node")
        
        # Validate each node
        for node in workflow.nodes.values():
            if node.type in self.executors:
                executor = self.executors[node.type]
                if not executor.validate(node):
                    errors.append(f"Node {node.name} has invalid configuration")
        
        # Check connections
        node_ids = set(workflow.nodes.keys())
        for connection in workflow.connections:
            if connection.source_node not in node_ids:
                errors.append(f"Connection references non-existent source node: {connection.source_node}")
            if connection.target_node not in node_ids:
                errors.append(f"Connection references non-existent target node: {connection.target_node}")
        
        return errors
    
    async def execute_workflow(self, workflow_id: str, variables: Dict[str, Any] = None) -> str:
        """Execute workflow."""
        with self._lock:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow = self.workflows[workflow_id]
        
        # Validate workflow
        errors = self.validate_workflow(workflow_id)
        if errors:
            raise ValueError(f"Workflow validation failed: {errors}")
        
        # Create execution context
        execution_id = str(uuid.uuid4())
        context = ExecutionContext(
            execution_id=execution_id,
            workflow_id=workflow_id,
            variables=variables or {}
        )
        
        with self._lock:
            self.executions[execution_id] = context
        
        # Start execution
        asyncio.create_task(self._execute_workflow_async(context))
        
        self.logger.info(f"Started workflow execution: {execution_id}")
        return execution_id
    
    async def _execute_workflow_async(self, context: ExecutionContext) -> None:
        """Execute workflow asynchronously."""
        try:
            with self._lock:
                workflow = self.workflows[context.workflow_id]
            
            # Find start nodes
            start_nodes = [node for node in workflow.nodes.values() if node.type == NodeType.START]
            
            if not start_nodes:
                raise ValueError("No start nodes found")
            
            # Execute from start nodes
            for start_node in start_nodes:
                await self._execute_node_path(start_node, context, workflow)
            
            context.status = ExecutionStatus.COMPLETED
            context.end_time = datetime.now()
            
            self.logger.info(f"Workflow execution completed: {context.execution_id}")
            
        except Exception as e:
            context.status = ExecutionStatus.FAILED
            context.end_time = datetime.now()
            self.logger.error(f"Workflow execution failed: {e}")
    
    async def _execute_node_path(self, node: WorkflowNode, context: ExecutionContext, workflow: Workflow) -> None:
        """Execute node and follow connections."""
        if node.id in context.node_states:
            return  # Already executed
        
        # Mark node as running
        context.node_states[node.id] = {
            'status': ExecutionStatus.RUNNING,
            'start_time': datetime.now()
        }
        
        try:
            # Execute node
            if node.type in self.executors:
                executor = self.executors[node.type]
                result = await executor.execute(node, context)
                
                # Update node state
                context.node_states[node.id].update({
                    'status': ExecutionStatus.COMPLETED,
                    'result': result,
                    'end_time': datetime.now()
                })
                
                # Log execution
                context.execution_log.append({
                    'node_id': node.id,
                    'node_name': node.name,
                    'status': 'completed',
                    'result': result,
                    'timestamp': datetime.now()
                })
                
                # Follow connections
                await self._follow_connections(node, result, context, workflow)
                
            else:
                # Handle special node types
                if node.type == NodeType.END:
                    context.node_states[node.id] = {
                        'status': ExecutionStatus.COMPLETED,
                        'end_time': datetime.now()
                    }
                else:
                    raise ValueError(f"Unknown node type: {node.type}")
        
        except Exception as e:
            # Mark node as failed
            context.node_states[node.id].update({
                'status': ExecutionStatus.FAILED,
                'error': str(e),
                'end_time': datetime.now()
            })
            
            # Log error
            context.execution_log.append({
                'node_id': node.id,
                'node_name': node.name,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now()
            })
            
            raise
    
    async def _follow_connections(self, node: WorkflowNode, result: Dict[str, Any], context: ExecutionContext, workflow: Workflow) -> None:
        """Follow connections from executed node."""
        # Find outgoing connections
        outgoing_connections = [
            conn for conn in workflow.connections
            if conn.source_node == node.id
        ]
        
        for connection in outgoing_connections:
            # Check condition if present
            if connection.condition:
                if not self._evaluate_connection_condition(connection.condition, result, context.variables):
                    continue
            
            # Get target node
            target_node = workflow.nodes.get(connection.target_node)
            if target_node:
                # Execute target node
                await self._execute_node_path(target_node, context, workflow)
    
    def _evaluate_connection_condition(self, condition: str, node_result: Dict[str, Any], variables: Dict[str, Any]) -> bool:
        """Evaluate connection condition."""
        try:
            # Simple condition evaluation
            if condition == 'success':
                return node_result.get('status') == 'completed'
            elif condition == 'failure':
                return node_result.get('status') == 'failed'
            else:
                # Evaluate as expression
                return self._evaluate_expression(condition, {**variables, **node_result})
        except Exception:
            return False
    
    def _evaluate_expression(self, expression: str, context: Dict[str, Any]) -> bool:
        """Evaluate expression in context."""
        try:
            # Simple expression evaluation (can be extended)
            return eval(expression, {"__builtins__": {}}, context)
        except Exception:
            return False
    
    def get_execution_status(self, execution_id: str) -> Optional[ExecutionContext]:
        """Get execution status."""
        with self._lock:
            return self.executions.get(execution_id)
    
    def list_workflows(self) -> List[Workflow]:
        """List all workflows."""
        with self._lock:
            return list(self.workflows.values())
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID."""
        with self._lock:
            return self.workflows.get(workflow_id)
    
    def export_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Export workflow to dictionary."""
        with self._lock:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow = self.workflows[workflow_id]
        
        return {
            'id': workflow.id,
            'name': workflow.name,
            'description': workflow.description,
            'version': workflow.version,
            'nodes': {
                node_id: {
                    'id': node.id,
                    'type': node.type.value,
                    'name': node.name,
                    'description': node.description,
                    'position': node.position,
                    'properties': node.properties,
                    'inputs': node.inputs,
                    'outputs': node.outputs,
                    'conditions': node.conditions
                }
                for node_id, node in workflow.nodes.items()
            },
            'connections': [
                {
                    'id': conn.id,
                    'source_node': conn.source_node,
                    'target_node': conn.target_node,
                    'source_output': conn.source_output,
                    'target_input': conn.target_input,
                    'condition': conn.condition
                }
                for conn in workflow.connections
            ],
            'variables': workflow.variables
        }
    
    def import_workflow(self, workflow_data: Dict[str, Any]) -> Workflow:
        """Import workflow from dictionary."""
        workflow = Workflow(
            id=workflow_data['id'],
            name=workflow_data['name'],
            description=workflow_data.get('description', ''),
            version=workflow_data.get('version', '1.0.0'),
            variables=workflow_data.get('variables', {})
        )
        
        # Import nodes
        for node_data in workflow_data.get('nodes', {}).values():
            node = WorkflowNode(
                id=node_data['id'],
                type=NodeType(node_data['type']),
                name=node_data['name'],
                description=node_data.get('description', ''),
                position=node_data.get('position', {'x': 0, 'y': 0}),
                properties=node_data.get('properties', {}),
                inputs=node_data.get('inputs', []),
                outputs=node_data.get('outputs', []),
                conditions=node_data.get('conditions', [])
            )
            workflow.nodes[node.id] = node
        
        # Import connections
        for conn_data in workflow_data.get('connections', []):
            connection = WorkflowConnection(
                id=conn_data['id'],
                source_node=conn_data['source_node'],
                target_node=conn_data['target_node'],
                source_output=conn_data.get('source_output', 'default'),
                target_input=conn_data.get('target_input', 'default'),
                condition=conn_data.get('condition')
            )
            workflow.connections.append(connection)
        
        with self._lock:
            self.workflows[workflow.id] = workflow
        
        self.logger.info(f"Imported workflow: {workflow.name}")
        return workflow

# Global workflow engine
workflow_engine = WorkflowEngine()

def get_workflow_engine() -> WorkflowEngine:
    """Get global workflow engine."""
    return workflow_engine

async def execute_workflow(workflow_id: str, variables: Dict[str, Any] = None) -> str:
    """Execute workflow using global engine."""
    return await workflow_engine.execute_workflow(workflow_id, variables)

if __name__ == "__main__":
    # Demo workflow system
    print("ClickUp Brain Workflow Engine Demo")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    async def demo():
        # Get workflow engine
        engine = get_workflow_engine()
        
        # Create workflow
        workflow = engine.create_workflow("Demo Workflow", "A simple demo workflow")
        
        # Add nodes
        start_node = WorkflowNode(
            id="start",
            type=NodeType.START,
            name="Start",
            position={"x": 100, "y": 100}
        )
        engine.add_node(workflow.id, start_node)
        
        task_node = WorkflowNode(
            id="task1",
            type=NodeType.TASK,
            name="Process Data",
            properties={"task_type": "automated"},
            position={"x": 300, "y": 100}
        )
        engine.add_node(workflow.id, task_node)
        
        condition_node = WorkflowNode(
            id="condition1",
            type=NodeType.CONDITION,
            name="Check Result",
            properties={"condition": "value > 50"},
            position={"x": 500, "y": 100}
        )
        engine.add_node(workflow.id, condition_node)
        
        email_node = WorkflowNode(
            id="email1",
            type=NodeType.EMAIL,
            name="Send Notification",
            properties={
                "to": "admin@example.com",
                "subject": "Workflow Completed",
                "body": "The workflow has completed successfully."
            },
            position={"x": 700, "y": 50}
        )
        engine.add_node(workflow.id, email_node)
        
        end_node = WorkflowNode(
            id="end",
            type=NodeType.END,
            name="End",
            position={"x": 900, "y": 100}
        )
        engine.add_node(workflow.id, end_node)
        
        # Add connections
        connection1 = WorkflowConnection(
            id="conn1",
            source_node="start",
            target_node="task1"
        )
        engine.add_connection(workflow.id, connection1)
        
        connection2 = WorkflowConnection(
            id="conn2",
            source_node="task1",
            target_node="condition1"
        )
        engine.add_connection(workflow.id, connection2)
        
        connection3 = WorkflowConnection(
            id="conn3",
            source_node="condition1",
            target_node="email1",
            condition="true"
        )
        engine.add_connection(workflow.id, connection3)
        
        connection4 = WorkflowConnection(
            id="conn4",
            source_node="email1",
            target_node="end"
        )
        engine.add_connection(workflow.id, connection4)
        
        # Validate workflow
        errors = engine.validate_workflow(workflow.id)
        if errors:
            print(f"Workflow validation errors: {errors}")
        else:
            print("Workflow validation passed")
        
        # Execute workflow
        execution_id = await engine.execute_workflow(workflow.id, {"value": 75})
        print(f"Started workflow execution: {execution_id}")
        
        # Wait for execution to complete
        await asyncio.sleep(5)
        
        # Check execution status
        execution = engine.get_execution_status(execution_id)
        if execution:
            print(f"Execution status: {execution.status.value}")
            print(f"Execution log: {len(execution.execution_log)} entries")
            for log_entry in execution.execution_log:
                print(f"  - {log_entry['node_name']}: {log_entry['status']}")
        
        # Export workflow
        exported = engine.export_workflow(workflow.id)
        print(f"Exported workflow with {len(exported['nodes'])} nodes and {len(exported['connections'])} connections")
        
        print("\nWorkflow engine demo completed!")
    
    asyncio.run(demo())







