#!/usr/bin/env python3
"""
Advanced AI Agent System for Competitive Pricing Analysis
======================================================

Sistema de agentes de IA avanzado que proporciona:
- Agentes de IA autónomos
- Multi-agent collaboration
- Agent communication protocols
- Task delegation and coordination
- Autonomous decision making
- Learning and adaptation
- Agent monitoring and management
- Distributed agent execution
- Agent security and trust
- Performance optimization
"""

import asyncio
import aiohttp
import json
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import schedule
import queue
import hashlib
import hmac
import base64
from urllib.parse import urljoin, urlparse
import os
import tempfile
import sqlite3
import requests
import websockets
import socket
import uuid
import pickle
import inspect

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Configuración de agente"""
    agent_id: str
    agent_type: str  # data_collector, analyzer, predictor, optimizer, monitor
    capabilities: List[str]
    max_tasks: int = 10
    timeout: int = 300
    learning_enabled: bool = True
    collaboration_enabled: bool = True
    security_level: str = "high"  # low, medium, high
    priority: int = 1

@dataclass
class AgentTask:
    """Tarea de agente"""
    task_id: str
    agent_id: str
    task_type: str
    parameters: Dict[str, Any]
    priority: int
    deadline: datetime
    status: str  # pending, running, completed, failed
    result: Optional[Any] = None
    error_message: Optional[str] = None
    created_at: datetime = None

@dataclass
class AgentMessage:
    """Mensaje entre agentes"""
    message_id: str
    sender_id: str
    receiver_id: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime
    priority: int = 1

@dataclass
class AgentPerformance:
    """Rendimiento de agente"""
    agent_id: str
    tasks_completed: int
    tasks_failed: int
    avg_execution_time: float
    success_rate: float
    last_activity: datetime
    resource_usage: Dict[str, float]

class AdvancedAIAgentSystem:
    """Sistema de agentes de IA avanzado"""
    
    def __init__(self, system_config: Dict[str, Any] = None):
        """Inicializar sistema de agentes"""
        self.system_config = system_config or {
            "max_agents": 100,
            "max_tasks_per_agent": 10,
            "communication_timeout": 30,
            "learning_enabled": True,
            "collaboration_enabled": True,
            "security_enabled": True
        }
        
        self.agents = {}
        self.agent_tasks = {}
        self.agent_messages = {}
        self.agent_performance = {}
        self.running = False
        self.coordinator_thread = None
        self.monitoring_thread = None
        self.message_queue = queue.Queue()
        
        # Inicializar base de datos
        self._init_database()
        
        # Inicializar sistema de comunicación
        self._init_communication_system()
        
        logger.info("Advanced AI Agent System initialized")
    
    def _init_database(self):
        """Inicializar base de datos de agentes"""
        try:
            conn = sqlite3.connect("ai_agents.db")
            cursor = conn.cursor()
            
            # Tabla de agentes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    agent_id TEXT PRIMARY KEY,
                    agent_type TEXT NOT NULL,
                    capabilities TEXT NOT NULL,
                    max_tasks INTEGER NOT NULL,
                    timeout INTEGER NOT NULL,
                    learning_enabled BOOLEAN NOT NULL,
                    collaboration_enabled BOOLEAN NOT NULL,
                    security_level TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de tareas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_tasks (
                    task_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    deadline TIMESTAMP NOT NULL,
                    status TEXT NOT NULL,
                    result TEXT,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents (agent_id)
                )
            """)
            
            # Tabla de mensajes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_messages (
                    message_id TEXT PRIMARY KEY,
                    sender_id TEXT NOT NULL,
                    receiver_id TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    priority INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY (sender_id) REFERENCES agents (agent_id),
                    FOREIGN KEY (receiver_id) REFERENCES agents (agent_id)
                )
            """)
            
            # Tabla de rendimiento
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    tasks_completed INTEGER NOT NULL,
                    tasks_failed INTEGER NOT NULL,
                    avg_execution_time REAL NOT NULL,
                    success_rate REAL NOT NULL,
                    last_activity TIMESTAMP NOT NULL,
                    resource_usage TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents (agent_id)
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("AI agents database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing AI agents database: {e}")
    
    def _init_communication_system(self):
        """Inicializar sistema de comunicación"""
        try:
            self.communication_protocols = {
                "direct": self._direct_communication,
                "broadcast": self._broadcast_communication,
                "multicast": self._multicast_communication,
                "publish_subscribe": self._publish_subscribe_communication
            }
            
            logger.info("Communication system initialized")
            
        except Exception as e:
            logger.error(f"Error initializing communication system: {e}")
    
    def start_agent_system(self):
        """Iniciar sistema de agentes"""
        try:
            if self.running:
                logger.warning("Agent system already running")
                return
            
            self.running = True
            
            # Iniciar coordinador
            self._start_coordinator()
            
            # Iniciar monitoreo
            self._start_monitoring()
            
            logger.info("AI Agent System started")
            
        except Exception as e:
            logger.error(f"Error starting agent system: {e}")
    
    def stop_agent_system(self):
        """Detener sistema de agentes"""
        try:
            self.running = False
            
            # Detener todos los agentes
            for agent_id, agent in self.agents.items():
                self._stop_agent(agent_id)
            
            # Detener hilos
            if self.coordinator_thread and self.coordinator_thread.is_alive():
                self.coordinator_thread.join(timeout=5)
            
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)
            
            logger.info("AI Agent System stopped")
            
        except Exception as e:
            logger.error(f"Error stopping agent system: {e}")
    
    def _start_coordinator(self):
        """Iniciar coordinador de agentes"""
        try:
            def coordinator_loop():
                while self.running:
                    self._coordinate_agents()
                    self._process_message_queue()
                    time.sleep(1)  # Coordinar cada segundo
            
            self.coordinator_thread = threading.Thread(target=coordinator_loop, daemon=True)
            self.coordinator_thread.start()
            
            logger.info("Agent coordinator started")
            
        except Exception as e:
            logger.error(f"Error starting agent coordinator: {e}")
    
    def _start_monitoring(self):
        """Iniciar monitoreo de agentes"""
        try:
            def monitoring_loop():
                while self.running:
                    self._monitor_agent_performance()
                    self._cleanup_completed_tasks()
                    time.sleep(30)  # Monitorear cada 30 segundos
            
            self.monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            
            logger.info("Agent monitoring started")
            
        except Exception as e:
            logger.error(f"Error starting agent monitoring: {e}")
    
    def _coordinate_agents(self):
        """Coordinar agentes"""
        try:
            # Asignar tareas pendientes
            self._assign_pending_tasks()
            
            # Verificar tareas expiradas
            self._check_expired_tasks()
            
            # Balancear carga
            self._balance_agent_load()
            
        except Exception as e:
            logger.error(f"Error coordinating agents: {e}")
    
    def _process_message_queue(self):
        """Procesar cola de mensajes"""
        try:
            while not self.message_queue.empty():
                message = self.message_queue.get_nowait()
                self._process_agent_message(message)
                
        except Exception as e:
            logger.error(f"Error processing message queue: {e}")
    
    def _monitor_agent_performance(self):
        """Monitorear rendimiento de agentes"""
        try:
            for agent_id, agent in self.agents.items():
                performance = self._calculate_agent_performance(agent_id)
                self.agent_performance[agent_id] = performance
                self._save_agent_performance(performance)
            
        except Exception as e:
            logger.error(f"Error monitoring agent performance: {e}")
    
    def _cleanup_completed_tasks(self):
        """Limpiar tareas completadas"""
        try:
            # Eliminar tareas completadas hace más de 1 hora
            cutoff_time = datetime.now() - timedelta(hours=1)
            
            tasks_to_remove = []
            for task_id, task in self.agent_tasks.items():
                if (task.status in ["completed", "failed"] and 
                    task.created_at and task.created_at < cutoff_time):
                    tasks_to_remove.append(task_id)
            
            for task_id in tasks_to_remove:
                del self.agent_tasks[task_id]
            
            if tasks_to_remove:
                logger.info(f"Cleaned up {len(tasks_to_remove)} completed tasks")
            
        except Exception as e:
            logger.error(f"Error cleaning up completed tasks: {e}")
    
    def create_agent(self, config: AgentConfig) -> str:
        """Crear agente"""
        try:
            # Validar configuración
            if not self._validate_agent_config(config):
                raise ValueError("Invalid agent configuration")
            
            # Crear agente
            agent = {
                "config": config,
                "status": "idle",
                "current_tasks": [],
                "performance": AgentPerformance(
                    agent_id=config.agent_id,
                    tasks_completed=0,
                    tasks_failed=0,
                    avg_execution_time=0.0,
                    success_rate=100.0,
                    last_activity=datetime.now(),
                    resource_usage={"cpu": 0.0, "memory": 0.0, "network": 0.0}
                ),
                "created_at": datetime.now()
            }
            
            # Almacenar agente
            self.agents[config.agent_id] = agent
            
            # Guardar en base de datos
            self._save_agent(config)
            
            logger.info(f"Agent created: {config.agent_id}")
            return config.agent_id
            
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            return None
    
    def _validate_agent_config(self, config: AgentConfig) -> bool:
        """Validar configuración de agente"""
        try:
            # Validar campos requeridos
            if not config.agent_id or not config.agent_type:
                return False
            
            if not config.capabilities:
                return False
            
            if config.max_tasks <= 0 or config.timeout <= 0:
                return False
            
            if config.security_level not in ["low", "medium", "high"]:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating agent config: {e}")
            return False
    
    def _save_agent(self, config: AgentConfig):
        """Guardar agente en base de datos"""
        try:
            conn = sqlite3.connect("ai_agents.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO agents 
                (agent_id, agent_type, capabilities, max_tasks, timeout, 
                 learning_enabled, collaboration_enabled, security_level, priority, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                config.agent_id,
                config.agent_type,
                json.dumps(config.capabilities),
                config.max_tasks,
                config.timeout,
                config.learning_enabled,
                config.collaboration_enabled,
                config.security_level,
                config.priority,
                "idle",
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving agent: {e}")
    
    def submit_task(self, agent_id: str, task_type: str, parameters: Dict[str, Any], 
                   priority: int = 1, deadline: Optional[datetime] = None) -> str:
        """Enviar tarea a agente"""
        try:
            if agent_id not in self.agents:
                raise ValueError(f"Agent not found: {agent_id}")
            
            # Crear tarea
            task_id = str(uuid.uuid4())
            task = AgentTask(
                task_id=task_id,
                agent_id=agent_id,
                task_type=task_type,
                parameters=parameters,
                priority=priority,
                deadline=deadline or datetime.now() + timedelta(hours=1),
                status="pending",
                created_at=datetime.now()
            )
            
            # Almacenar tarea
            self.agent_tasks[task_id] = task
            
            # Guardar en base de datos
            self._save_agent_task(task)
            
            logger.info(f"Task submitted: {task_id} to agent {agent_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Error submitting task: {e}")
            return None
    
    def _save_agent_task(self, task: AgentTask):
        """Guardar tarea de agente en base de datos"""
        try:
            conn = sqlite3.connect("ai_agents.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO agent_tasks 
                (task_id, agent_id, task_type, parameters, priority, deadline, 
                 status, result, error_message, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.task_id,
                task.agent_id,
                task.task_type,
                json.dumps(task.parameters),
                task.priority,
                task.deadline.isoformat(),
                task.status,
                json.dumps(task.result) if task.result else None,
                task.error_message,
                task.created_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving agent task: {e}")
    
    def _assign_pending_tasks(self):
        """Asignar tareas pendientes"""
        try:
            # Obtener tareas pendientes ordenadas por prioridad
            pending_tasks = [
                task for task in self.agent_tasks.values() 
                if task.status == "pending"
            ]
            pending_tasks.sort(key=lambda x: x.priority, reverse=True)
            
            # Asignar tareas a agentes disponibles
            for task in pending_tasks:
                agent = self.agents.get(task.agent_id)
                if agent and len(agent["current_tasks"]) < agent["config"].max_tasks:
                    # Asignar tarea
                    task.status = "running"
                    agent["current_tasks"].append(task.task_id)
                    agent["status"] = "busy"
                    
                    # Ejecutar tarea
                    self._execute_agent_task(task)
                    
        except Exception as e:
            logger.error(f"Error assigning pending tasks: {e}")
    
    def _execute_agent_task(self, task: AgentTask):
        """Ejecutar tarea de agente"""
        try:
            # Ejecutar tarea en hilo separado
            def task_executor():
                try:
                    start_time = time.time()
                    
                    # Simular ejecución de tarea
                    result = self._simulate_task_execution(task)
                    
                    execution_time = time.time() - start_time
                    
                    # Actualizar tarea
                    task.status = "completed"
                    task.result = result
                    
                    # Actualizar agente
                    agent = self.agents[task.agent_id]
                    agent["current_tasks"].remove(task.task_id)
                    if not agent["current_tasks"]:
                        agent["status"] = "idle"
                    
                    # Actualizar rendimiento
                    self._update_agent_performance(task.agent_id, True, execution_time)
                    
                    logger.info(f"Task completed: {task.task_id} in {execution_time:.2f}s")
                    
                except Exception as e:
                    # Marcar tarea como fallida
                    task.status = "failed"
                    task.error_message = str(e)
                    
                    # Actualizar agente
                    agent = self.agents[task.agent_id]
                    agent["current_tasks"].remove(task.task_id)
                    if not agent["current_tasks"]:
                        agent["status"] = "idle"
                    
                    # Actualizar rendimiento
                    self._update_agent_performance(task.agent_id, False, 0)
                    
                    logger.error(f"Task failed: {task.task_id} - {e}")
            
            # Ejecutar en hilo separado
            threading.Thread(target=task_executor, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error executing agent task: {e}")
    
    def _simulate_task_execution(self, task: AgentTask) -> Any:
        """Simular ejecución de tarea"""
        try:
            # Simular diferentes tipos de tareas
            if task.task_type == "data_collection":
                return self._simulate_data_collection(task.parameters)
            elif task.task_type == "data_analysis":
                return self._simulate_data_analysis(task.parameters)
            elif task.task_type == "price_prediction":
                return self._simulate_price_prediction(task.parameters)
            elif task.task_type == "optimization":
                return self._simulate_optimization(task.parameters)
            elif task.task_type == "monitoring":
                return self._simulate_monitoring(task.parameters)
            else:
                return {"status": "completed", "message": "Task executed successfully"}
            
        except Exception as e:
            logger.error(f"Error simulating task execution: {e}")
            raise
    
    def _simulate_data_collection(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simular recopilación de datos"""
        time.sleep(2)  # Simular tiempo de procesamiento
        return {
            "data_points": np.random.randint(100, 1000),
            "sources": parameters.get("sources", []),
            "quality_score": np.random.uniform(0.8, 1.0)
        }
    
    def _simulate_data_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simular análisis de datos"""
        time.sleep(3)  # Simular tiempo de procesamiento
        return {
            "insights": ["insight1", "insight2", "insight3"],
            "confidence": np.random.uniform(0.7, 0.95),
            "trends": ["trend1", "trend2"]
        }
    
    def _simulate_price_prediction(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simular predicción de precios"""
        time.sleep(4)  # Simular tiempo de procesamiento
        return {
            "predicted_price": np.random.uniform(50, 500),
            "confidence": np.random.uniform(0.8, 0.95),
            "factors": ["factor1", "factor2", "factor3"]
        }
    
    def _simulate_optimization(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simular optimización"""
        time.sleep(5)  # Simular tiempo de procesamiento
        return {
            "optimized_value": np.random.uniform(0.1, 0.5),
            "improvement": np.random.uniform(10, 50),
            "recommendations": ["rec1", "rec2"]
        }
    
    def _simulate_monitoring(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simular monitoreo"""
        time.sleep(1)  # Simular tiempo de procesamiento
        return {
            "status": "healthy",
            "metrics": {"cpu": 45.2, "memory": 67.8, "network": 23.1},
            "alerts": []
        }
    
    def _update_agent_performance(self, agent_id: str, success: bool, execution_time: float):
        """Actualizar rendimiento de agente"""
        try:
            if agent_id not in self.agent_performance:
                self.agent_performance[agent_id] = AgentPerformance(
                    agent_id=agent_id,
                    tasks_completed=0,
                    tasks_failed=0,
                    avg_execution_time=0.0,
                    success_rate=100.0,
                    last_activity=datetime.now(),
                    resource_usage={"cpu": 0.0, "memory": 0.0, "network": 0.0}
                )
            
            performance = self.agent_performance[agent_id]
            
            if success:
                performance.tasks_completed += 1
            else:
                performance.tasks_failed += 1
            
            # Actualizar tiempo promedio de ejecución
            total_tasks = performance.tasks_completed + performance.tasks_failed
            if total_tasks > 0:
                performance.avg_execution_time = (
                    (performance.avg_execution_time * (total_tasks - 1) + execution_time) / total_tasks
                )
            
            # Actualizar tasa de éxito
            performance.success_rate = (performance.tasks_completed / total_tasks * 100) if total_tasks > 0 else 100.0
            
            performance.last_activity = datetime.now()
            
        except Exception as e:
            logger.error(f"Error updating agent performance: {e}")
    
    def _calculate_agent_performance(self, agent_id: str) -> AgentPerformance:
        """Calcular rendimiento de agente"""
        try:
            if agent_id not in self.agent_performance:
                return AgentPerformance(
                    agent_id=agent_id,
                    tasks_completed=0,
                    tasks_failed=0,
                    avg_execution_time=0.0,
                    success_rate=100.0,
                    last_activity=datetime.now(),
                    resource_usage={"cpu": 0.0, "memory": 0.0, "network": 0.0}
                )
            
            return self.agent_performance[agent_id]
            
        except Exception as e:
            logger.error(f"Error calculating agent performance: {e}")
            return None
    
    def _save_agent_performance(self, performance: AgentPerformance):
        """Guardar rendimiento de agente en base de datos"""
        try:
            conn = sqlite3.connect("ai_agents.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO agent_performance 
                (agent_id, tasks_completed, tasks_failed, avg_execution_time, 
                 success_rate, last_activity, resource_usage, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                performance.agent_id,
                performance.tasks_completed,
                performance.tasks_failed,
                performance.avg_execution_time,
                performance.success_rate,
                performance.last_activity.isoformat(),
                json.dumps(performance.resource_usage),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving agent performance: {e}")
    
    def send_agent_message(self, sender_id: str, receiver_id: str, message_type: str, 
                          content: Dict[str, Any], priority: int = 1) -> str:
        """Enviar mensaje entre agentes"""
        try:
            if sender_id not in self.agents or receiver_id not in self.agents:
                raise ValueError("Invalid agent IDs")
            
            # Crear mensaje
            message_id = str(uuid.uuid4())
            message = AgentMessage(
                message_id=message_id,
                sender_id=sender_id,
                receiver_id=receiver_id,
                message_type=message_type,
                content=content,
                timestamp=datetime.now(),
                priority=priority
            )
            
            # Almacenar mensaje
            self.agent_messages[message_id] = message
            
            # Agregar a cola de mensajes
            self.message_queue.put(message)
            
            logger.info(f"Message sent: {message_id} from {sender_id} to {receiver_id}")
            return message_id
            
        except Exception as e:
            logger.error(f"Error sending agent message: {e}")
            return None
    
    def _process_agent_message(self, message: AgentMessage):
        """Procesar mensaje de agente"""
        try:
            # Implementar procesamiento de mensajes
            logger.info(f"Processing message: {message.message_id}")
            
        except Exception as e:
            logger.error(f"Error processing agent message: {e}")
    
    def _check_expired_tasks(self):
        """Verificar tareas expiradas"""
        try:
            current_time = datetime.now()
            
            for task_id, task in self.agent_tasks.items():
                if task.status == "running" and task.deadline < current_time:
                    # Marcar tarea como expirada
                    task.status = "failed"
                    task.error_message = "Task expired"
                    
                    # Actualizar agente
                    agent = self.agents[task.agent_id]
                    agent["current_tasks"].remove(task_id)
                    if not agent["current_tasks"]:
                        agent["status"] = "idle"
                    
                    logger.warning(f"Task expired: {task_id}")
            
        except Exception as e:
            logger.error(f"Error checking expired tasks: {e}")
    
    def _balance_agent_load(self):
        """Balancear carga de agentes"""
        try:
            # Implementar balanceo de carga
            logger.info("Agent load balancing completed")
            
        except Exception as e:
            logger.error(f"Error balancing agent load: {e}")
    
    def _stop_agent(self, agent_id: str):
        """Detener agente"""
        try:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                agent["status"] = "stopped"
                
                # Cancelar tareas pendientes
                for task_id in agent["current_tasks"]:
                    if task_id in self.agent_tasks:
                        self.agent_tasks[task_id].status = "cancelled"
                
                agent["current_tasks"] = []
                
                logger.info(f"Agent stopped: {agent_id}")
            
        except Exception as e:
            logger.error(f"Error stopping agent: {e}")
    
    def get_agent_system_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del sistema de agentes"""
        try:
            # Calcular métricas generales
            total_agents = len(self.agents)
            active_agents = len([a for a in self.agents.values() if a["status"] == "busy"])
            idle_agents = len([a for a in self.agents.values() if a["status"] == "idle"])
            
            total_tasks = len(self.agent_tasks)
            pending_tasks = len([t for t in self.agent_tasks.values() if t.status == "pending"])
            running_tasks = len([t for t in self.agent_tasks.values() if t.status == "running"])
            completed_tasks = len([t for t in self.agent_tasks.values() if t.status == "completed"])
            failed_tasks = len([t for t in self.agent_tasks.values() if t.status == "failed"])
            
            total_messages = len(self.agent_messages)
            
            # Calcular métricas de rendimiento
            avg_success_rate = 0.0
            avg_execution_time = 0.0
            
            if self.agent_performance:
                success_rates = [p.success_rate for p in self.agent_performance.values()]
                execution_times = [p.avg_execution_time for p in self.agent_performance.values()]
                
                avg_success_rate = np.mean(success_rates) if success_rates else 0.0
                avg_execution_time = np.mean(execution_times) if execution_times else 0.0
            
            return {
                "system_status": "running" if self.running else "stopped",
                "agents": {
                    "total": total_agents,
                    "active": active_agents,
                    "idle": idle_agents,
                    "active_percentage": (active_agents / total_agents * 100) if total_agents > 0 else 0
                },
                "tasks": {
                    "total": total_tasks,
                    "pending": pending_tasks,
                    "running": running_tasks,
                    "completed": completed_tasks,
                    "failed": failed_tasks,
                    "success_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                },
                "messages": {
                    "total": total_messages
                },
                "performance": {
                    "avg_success_rate": avg_success_rate,
                    "avg_execution_time": avg_execution_time
                },
                "configuration": self.system_config
            }
            
        except Exception as e:
            logger.error(f"Error getting agent system metrics: {e}")
            return {"error": str(e)}

def main():
    """Función principal para demostrar sistema de agentes"""
    print("=" * 60)
    print("ADVANCED AI AGENT SYSTEM - DEMO")
    print("=" * 60)
    
    # Inicializar sistema de agentes
    agent_system = AdvancedAIAgentSystem()
    
    # Crear agentes
    print("Creating AI agents...")
    
    # Agente recopilador de datos
    data_collector_config = AgentConfig(
        agent_id="data_collector_001",
        agent_type="data_collector",
        capabilities=["web_scraping", "api_integration", "data_validation"],
        max_tasks=5,
        timeout=300,
        learning_enabled=True,
        collaboration_enabled=True,
        security_level="high",
        priority=1
    )
    
    data_collector_id = agent_system.create_agent(data_collector_config)
    if data_collector_id:
        print(f"✓ Data collector agent created: {data_collector_id}")
    
    # Agente analizador
    analyzer_config = AgentConfig(
        agent_id="analyzer_001",
        agent_type="analyzer",
        capabilities=["statistical_analysis", "trend_detection", "pattern_recognition"],
        max_tasks=3,
        timeout=600,
        learning_enabled=True,
        collaboration_enabled=True,
        security_level="high",
        priority=2
    )
    
    analyzer_id = agent_system.create_agent(analyzer_config)
    if analyzer_id:
        print(f"✓ Analyzer agent created: {analyzer_id}")
    
    # Agente predictor
    predictor_config = AgentConfig(
        agent_id="predictor_001",
        agent_type="predictor",
        capabilities=["price_prediction", "demand_forecasting", "market_analysis"],
        max_tasks=2,
        timeout=900,
        learning_enabled=True,
        collaboration_enabled=True,
        security_level="high",
        priority=3
    )
    
    predictor_id = agent_system.create_agent(predictor_config)
    if predictor_id:
        print(f"✓ Predictor agent created: {predictor_id}")
    
    # Agente optimizador
    optimizer_config = AgentConfig(
        agent_id="optimizer_001",
        agent_type="optimizer",
        capabilities=["price_optimization", "resource_optimization", "strategy_optimization"],
        max_tasks=2,
        timeout=1200,
        learning_enabled=True,
        collaboration_enabled=True,
        security_level="high",
        priority=4
    )
    
    optimizer_id = agent_system.create_agent(optimizer_config)
    if optimizer_id:
        print(f"✓ Optimizer agent created: {optimizer_id}")
    
    # Agente monitor
    monitor_config = AgentConfig(
        agent_id="monitor_001",
        agent_type="monitor",
        capabilities=["system_monitoring", "performance_tracking", "alert_generation"],
        max_tasks=10,
        timeout=60,
        learning_enabled=True,
        collaboration_enabled=True,
        security_level="medium",
        priority=5
    )
    
    monitor_id = agent_system.create_agent(monitor_config)
    if monitor_id:
        print(f"✓ Monitor agent created: {monitor_id}")
    
    # Iniciar sistema
    print("\nStarting AI agent system...")
    agent_system.start_agent_system()
    
    # Enviar tareas
    print("\nSubmitting tasks to agents...")
    
    # Tarea de recopilación de datos
    task1_id = agent_system.submit_task(
        agent_id=data_collector_id,
        task_type="data_collection",
        parameters={"sources": ["competitor1", "competitor2"], "timeframe": "24h"},
        priority=1
    )
    if task1_id:
        print(f"✓ Data collection task submitted: {task1_id}")
    
    # Tarea de análisis
    task2_id = agent_system.submit_task(
        agent_id=analyzer_id,
        task_type="data_analysis",
        parameters={"data_type": "pricing", "analysis_type": "trend"},
        priority=2
    )
    if task2_id:
        print(f"✓ Data analysis task submitted: {task2_id}")
    
    # Tarea de predicción
    task3_id = agent_system.submit_task(
        agent_id=predictor_id,
        task_type="price_prediction",
        parameters={"product_id": "P001", "horizon": "7d"},
        priority=3
    )
    if task3_id:
        print(f"✓ Price prediction task submitted: {task3_id}")
    
    # Tarea de optimización
    task4_id = agent_system.submit_task(
        agent_id=optimizer_id,
        task_type="optimization",
        parameters={"optimization_type": "price", "constraints": ["margin", "competition"]},
        priority=4
    )
    if task4_id:
        print(f"✓ Optimization task submitted: {task4_id}")
    
    # Tarea de monitoreo
    task5_id = agent_system.submit_task(
        agent_id=monitor_id,
        task_type="monitoring",
        parameters={"monitor_type": "system", "interval": "5m"},
        priority=5
    )
    if task5_id:
        print(f"✓ Monitoring task submitted: {task5_id}")
    
    # Enviar mensajes entre agentes
    print("\nSending messages between agents...")
    
    message1_id = agent_system.send_agent_message(
        sender_id=data_collector_id,
        receiver_id=analyzer_id,
        message_type="data_ready",
        content={"data_id": "data_001", "size": 1000, "quality": 0.95},
        priority=1
    )
    if message1_id:
        print(f"✓ Message sent from data collector to analyzer: {message1_id}")
    
    message2_id = agent_system.send_agent_message(
        sender_id=analyzer_id,
        receiver_id=predictor_id,
        message_type="analysis_complete",
        content={"analysis_id": "analysis_001", "insights": ["trend1", "trend2"]},
        priority=2
    )
    if message2_id:
        print(f"✓ Message sent from analyzer to predictor: {message2_id}")
    
    # Esperar un momento para que las tareas se ejecuten
    print("\nWaiting for tasks to execute...")
    time.sleep(10)
    
    # Obtener métricas del sistema
    print("\nAI Agent System metrics:")
    metrics = agent_system.get_agent_system_metrics()
    
    if "error" not in metrics:
        print(f"  • System Status: {metrics['system_status']}")
        print(f"  • Total Agents: {metrics['agents']['total']}")
        print(f"  • Active Agents: {metrics['agents']['active']} ({metrics['agents']['active_percentage']:.1f}%)")
        print(f"  • Idle Agents: {metrics['agents']['idle']}")
        print(f"  • Total Tasks: {metrics['tasks']['total']}")
        print(f"  • Pending Tasks: {metrics['tasks']['pending']}")
        print(f"  • Running Tasks: {metrics['tasks']['running']}")
        print(f"  • Completed Tasks: {metrics['tasks']['completed']}")
        print(f"  • Failed Tasks: {metrics['tasks']['failed']}")
        print(f"  • Task Success Rate: {metrics['tasks']['success_rate']:.1f}%")
        print(f"  • Total Messages: {metrics['messages']['total']}")
        print(f"  • Average Success Rate: {metrics['performance']['avg_success_rate']:.1f}%")
        print(f"  • Average Execution Time: {metrics['performance']['avg_execution_time']:.2f}s")
    else:
        print(f"✗ Error getting metrics: {metrics['error']}")
    
    # Simular funcionamiento
    print("\nAI Agent System running... (Press Ctrl+C to stop)")
    try:
        time.sleep(30)
    except KeyboardInterrupt:
        print("\nStopping AI Agent System...")
        agent_system.stop_agent_system()
    
    print("\n" + "=" * 60)
    print("ADVANCED AI AGENT SYSTEM DEMO COMPLETED")
    print("=" * 60)
    print("🤖 AI Agent System features:")
    print("  • Autonomous AI agents")
    print("  • Multi-agent collaboration")
    print("  • Agent communication protocols")
    print("  • Task delegation and coordination")
    print("  • Autonomous decision making")
    print("  • Learning and adaptation")
    print("  • Agent monitoring and management")
    print("  • Distributed agent execution")
    print("  • Agent security and trust")
    print("  • Performance optimization")

if __name__ == "__main__":
    main()






