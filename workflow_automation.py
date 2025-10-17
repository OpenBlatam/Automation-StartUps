"""
Workflow Automation System
Sistema de automatización avanzado para flujos de trabajo de lanzamiento
"""

import json
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
import threading
import logging
from enum import Enum

from enhanced_launch_planner import EnhancedLaunchPlanner
from ai_powered_insights import AIPoweredInsightsEngine
from clickup_brain_integration import ClickUpBrainBehavior

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AutomatedTask:
    """Tarea automatizada"""
    id: str
    name: str
    description: str
    task_type: str
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    dependencies: List[str] = None
    parameters: Dict[str, Any] = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.parameters is None:
            self.parameters = {}

@dataclass
class WorkflowTemplate:
    """Plantilla de flujo de trabajo"""
    name: str
    description: str
    tasks: List[AutomatedTask]
    triggers: List[str]
    conditions: Dict[str, Any]
    estimated_duration: str
    success_criteria: List[str]

@dataclass
class WorkflowExecution:
    """Ejecución de flujo de trabajo"""
    id: str
    template_name: str
    status: TaskStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    tasks: List[AutomatedTask] = None
    progress: float = 0.0
    error_log: List[str] = None

    def __post_init__(self):
        if self.tasks is None:
            self.tasks = []
        if self.error_log is None:
            self.error_log = []

class WorkflowAutomationEngine:
    """Motor de automatización de flujos de trabajo"""
    
    def __init__(self):
        self.enhanced_planner = EnhancedLaunchPlanner()
        self.insights_engine = AIPoweredInsightsEngine()
        self.brain_system = ClickUpBrainBehavior()
        
        self.workflow_templates = self._load_workflow_templates()
        self.active_executions = {}
        self.task_handlers = self._register_task_handlers()
        self.scheduler = schedule
        self.is_running = False
        
    def _load_workflow_templates(self) -> Dict[str, WorkflowTemplate]:
        """Cargar plantillas de flujo de trabajo"""
        return {
            "launch_planning": WorkflowTemplate(
                name="Launch Planning Workflow",
                description="Flujo completo de planificación de lanzamiento",
                tasks=[
                    AutomatedTask(
                        id="analyze_requirements",
                        name="Analyze Launch Requirements",
                        description="Análisis automático de requisitos de lanzamiento",
                        task_type="analysis",
                        priority=TaskPriority.HIGH,
                        status=TaskStatus.PENDING,
                        created_at=datetime.now()
                    ),
                    AutomatedTask(
                        id="generate_insights",
                        name="Generate AI Insights",
                        description="Generación de insights con IA",
                        task_type="ai_analysis",
                        priority=TaskPriority.HIGH,
                        status=TaskStatus.PENDING,
                        created_at=datetime.now(),
                        dependencies=["analyze_requirements"]
                    ),
                    AutomatedTask(
                        id="create_clickup_workspace",
                        name="Create ClickUp Workspace",
                        description="Creación automática de workspace en ClickUp",
                        task_type="clickup_integration",
                        priority=TaskPriority.MEDIUM,
                        status=TaskStatus.PENDING,
                        created_at=datetime.now(),
                        dependencies=["generate_insights"]
                    ),
                    AutomatedTask(
                        id="generate_report",
                        name="Generate Launch Report",
                        description="Generación de reporte de lanzamiento",
                        task_type="reporting",
                        priority=TaskPriority.MEDIUM,
                        status=TaskStatus.PENDING,
                        created_at=datetime.now(),
                        dependencies=["create_clickup_workspace"]
                    )
                ],
                triggers=["manual", "schedule", "webhook"],
                conditions={"min_budget": 10000, "max_complexity": 10},
                estimated_duration="2-4 hours",
                success_criteria=["All tasks completed", "No critical errors", "Report generated"]
            ),
            "market_analysis": WorkflowTemplate(
                name="Market Analysis Workflow",
                description="Análisis automático de mercado y competencia",
                tasks=[
                    AutomatedTask(
                        id="gather_market_data",
                        name="Gather Market Data",
                        description="Recopilación de datos de mercado",
                        task_type="data_collection",
                        priority=TaskPriority.HIGH,
                        status=TaskStatus.PENDING,
                        created_at=datetime.now()
                    ),
                    AutomatedTask(
                        id="analyze_competitors",
                        name="Analyze Competitors",
                        description="Análisis de competidores",
                        task_type="competitive_analysis",
                        priority=TaskPriority.HIGH,
                        status=TaskStatus.PENDING,
                        created_at=datetime.now(),
                        dependencies=["gather_market_data"]
                    ),
                    AutomatedTask(
                        id="generate_trends",
                        name="Generate Trend Analysis",
                        description="Generación de análisis de tendencias",
                        task_type="trend_analysis",
                        priority=TaskPriority.MEDIUM,
                        status=TaskStatus.PENDING,
                        created_at=datetime.now(),
                        dependencies=["analyze_competitors"]
                    )
                ],
                triggers=["schedule", "manual"],
                conditions={"scenario_type": ["mobile_app", "saas_platform", "ecommerce"]},
                estimated_duration="1-2 hours",
                success_criteria=["Market data collected", "Competitor analysis complete", "Trends identified"]
            ),
            "risk_assessment": WorkflowTemplate(
                name="Risk Assessment Workflow",
                description="Evaluación automática de riesgos",
                tasks=[
                    AutomatedTask(
                        id="identify_risks",
                        name="Identify Risks",
                        description="Identificación automática de riesgos",
                        task_type="risk_identification",
                        priority=TaskPriority.HIGH,
                        status=TaskStatus.PENDING,
                        created_at=datetime.now()
                    ),
                    AutomatedTask(
                        id="assess_impact",
                        name="Assess Risk Impact",
                        description="Evaluación del impacto de riesgos",
                        task_type="impact_assessment",
                        priority=TaskPriority.HIGH,
                        status=TaskStatus.PENDING,
                        created_at=datetime.now(),
                        dependencies=["identify_risks"]
                    ),
                    AutomatedTask(
                        id="generate_mitigation",
                        name="Generate Mitigation Strategies",
                        description="Generación de estrategias de mitigación",
                        task_type="mitigation_planning",
                        priority=TaskPriority.MEDIUM,
                        status=TaskStatus.PENDING,
                        created_at=datetime.now(),
                        dependencies=["assess_impact"]
                    )
                ],
                triggers=["manual", "schedule"],
                conditions={"complexity_threshold": 5},
                estimated_duration="1-3 hours",
                success_criteria=["Risks identified", "Impact assessed", "Mitigation strategies generated"]
            )
        }
    
    def _register_task_handlers(self) -> Dict[str, Callable]:
        """Registrar manejadores de tareas"""
        return {
            "analysis": self._handle_analysis_task,
            "ai_analysis": self._handle_ai_analysis_task,
            "clickup_integration": self._handle_clickup_integration_task,
            "reporting": self._handle_reporting_task,
            "data_collection": self._handle_data_collection_task,
            "competitive_analysis": self._handle_competitive_analysis_task,
            "trend_analysis": self._handle_trend_analysis_task,
            "risk_identification": self._handle_risk_identification_task,
            "impact_assessment": self._handle_impact_assessment_task,
            "mitigation_planning": self._handle_mitigation_planning_task
        }
    
    def _handle_analysis_task(self, task: AutomatedTask) -> bool:
        """Manejar tarea de análisis"""
        try:
            logger.info(f"Ejecutando análisis: {task.name}")
            
            requirements = task.parameters.get("requirements", "")
            scenario_type = task.parameters.get("scenario_type", "mobile_app")
            
            # Realizar análisis
            analysis = self.enhanced_planner.base_planner.analyze_launch_requirements(requirements)
            
            # Guardar resultados
            task.parameters["analysis_result"] = analysis
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            logger.info(f"Análisis completado: {task.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error en análisis {task.name}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            return False
    
    def _handle_ai_analysis_task(self, task: AutomatedTask) -> bool:
        """Manejar tarea de análisis de IA"""
        try:
            logger.info(f"Ejecutando análisis de IA: {task.name}")
            
            requirements = task.parameters.get("requirements", "")
            scenario_type = task.parameters.get("scenario_type", "mobile_app")
            
            # Generar insights con IA
            insights = self.insights_engine.generate_comprehensive_insights(requirements, scenario_type)
            
            # Guardar resultados
            task.parameters["ai_insights"] = insights
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            logger.info(f"Análisis de IA completado: {task.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error en análisis de IA {task.name}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            return False
    
    def _handle_clickup_integration_task(self, task: AutomatedTask) -> bool:
        """Manejar tarea de integración ClickUp"""
        try:
            logger.info(f"Ejecutando integración ClickUp: {task.name}")
            
            requirements = task.parameters.get("requirements", "")
            
            # Procesar con ClickUp Brain
            result = self.brain_system.process_launch_requirements(requirements)
            
            # Guardar resultados
            task.parameters["clickup_result"] = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            logger.info(f"Integración ClickUp completada: {task.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error en integración ClickUp {task.name}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            return False
    
    def _handle_reporting_task(self, task: AutomatedTask) -> bool:
        """Manejar tarea de generación de reportes"""
        try:
            logger.info(f"Generando reporte: {task.name}")
            
            # Recopilar datos de tareas anteriores
            analysis_result = task.parameters.get("analysis_result", {})
            ai_insights = task.parameters.get("ai_insights", {})
            clickup_result = task.parameters.get("clickup_result", {})
            
            # Generar reporte comprehensivo
            report = self._generate_comprehensive_report(
                analysis_result, ai_insights, clickup_result
            )
            
            # Guardar reporte
            task.parameters["report"] = report
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            logger.info(f"Reporte generado: {task.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error generando reporte {task.name}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            return False
    
    def _handle_data_collection_task(self, task: AutomatedTask) -> bool:
        """Manejar tarea de recopilación de datos"""
        try:
            logger.info(f"Recopilando datos: {task.name}")
            
            scenario_type = task.parameters.get("scenario_type", "mobile_app")
            
            # Simular recopilación de datos
            market_data = {
                "scenario_type": scenario_type,
                "data_collected": True,
                "timestamp": datetime.now().isoformat(),
                "sources": ["market_research", "competitor_analysis", "trend_data"]
            }
            
            task.parameters["market_data"] = market_data
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            logger.info(f"Datos recopilados: {task.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error recopilando datos {task.name}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            return False
    
    def _handle_competitive_analysis_task(self, task: AutomatedTask) -> bool:
        """Manejar tarea de análisis competitivo"""
        try:
            logger.info(f"Analizando competencia: {task.name}")
            
            scenario_type = task.parameters.get("scenario_type", "mobile_app")
            
            # Generar análisis competitivo
            competitive_intelligence = self.insights_engine.generate_competitive_intelligence(scenario_type)
            
            task.parameters["competitive_analysis"] = asdict(competitive_intelligence)
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            logger.info(f"Análisis competitivo completado: {task.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error en análisis competitivo {task.name}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            return False
    
    def _handle_trend_analysis_task(self, task: AutomatedTask) -> bool:
        """Manejar tarea de análisis de tendencias"""
        try:
            logger.info(f"Analizando tendencias: {task.name}")
            
            scenario_type = task.parameters.get("scenario_type", "mobile_app")
            
            # Generar análisis de tendencias
            trend_analysis = self.insights_engine.analyze_trends(scenario_type)
            
            task.parameters["trend_analysis"] = asdict(trend_analysis)
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            logger.info(f"Análisis de tendencias completado: {task.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error en análisis de tendencias {task.name}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            return False
    
    def _handle_risk_identification_task(self, task: AutomatedTask) -> bool:
        """Manejar tarea de identificación de riesgos"""
        try:
            logger.info(f"Identificando riesgos: {task.name}")
            
            requirements = task.parameters.get("requirements", "")
            scenario_type = task.parameters.get("scenario_type", "mobile_app")
            
            # Identificar riesgos
            basic_analysis = self.enhanced_planner.base_planner.analyze_launch_requirements(requirements)
            market_analysis = self.enhanced_planner._perform_market_analysis(scenario_type)
            risks = self.enhanced_planner._identify_ai_risk_factors(basic_analysis, market_analysis)
            
            task.parameters["identified_risks"] = risks
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            logger.info(f"Riesgos identificados: {task.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error identificando riesgos {task.name}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            return False
    
    def _handle_impact_assessment_task(self, task: AutomatedTask) -> bool:
        """Manejar tarea de evaluación de impacto"""
        try:
            logger.info(f"Evaluando impacto: {task.name}")
            
            risks = task.parameters.get("identified_risks", [])
            
            # Evaluar impacto de riesgos
            impact_assessment = {
                "high_impact_risks": [r for r in risks if "alta" in r.lower() or "high" in r.lower()],
                "medium_impact_risks": [r for r in risks if "media" in r.lower() or "medium" in r.lower()],
                "low_impact_risks": [r for r in risks if "baja" in r.lower() or "low" in r.lower()],
                "total_risks": len(risks),
                "assessment_date": datetime.now().isoformat()
            }
            
            task.parameters["impact_assessment"] = impact_assessment
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            logger.info(f"Evaluación de impacto completada: {task.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error evaluando impacto {task.name}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            return False
    
    def _handle_mitigation_planning_task(self, task: AutomatedTask) -> bool:
        """Manejar tarea de planificación de mitigación"""
        try:
            logger.info(f"Planificando mitigación: {task.name}")
            
            impact_assessment = task.parameters.get("impact_assessment", {})
            
            # Generar estrategias de mitigación
            mitigation_strategies = [
                "Implementar monitoreo continuo de riesgos",
                "Establecer planes de contingencia",
                "Crear equipos de respuesta rápida",
                "Desarrollar protocolos de comunicación",
                "Realizar pruebas de recuperación regulares"
            ]
            
            mitigation_plan = {
                "strategies": mitigation_strategies,
                "high_priority_actions": [
                    "Revisar y actualizar planes de contingencia",
                    "Capacitar al equipo en gestión de riesgos",
                    "Establecer métricas de monitoreo"
                ],
                "timeline": "2-4 semanas",
                "resources_needed": ["Risk management specialist", "Communication tools", "Monitoring systems"]
            }
            
            task.parameters["mitigation_plan"] = mitigation_plan
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            logger.info(f"Plan de mitigación completado: {task.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error planificando mitigación {task.name}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            return False
    
    def _generate_comprehensive_report(self, analysis_result: Dict, ai_insights: Dict, clickup_result: Dict) -> str:
        """Generar reporte comprehensivo"""
        report = f"""
# 🚀 Comprehensive Launch Planning Report
*Generado automáticamente: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## 📊 Executive Summary
Este reporte ha sido generado automáticamente por el Workflow Automation System.

## 🧠 AI Analysis Results
"""
        
        if ai_insights:
            summary = ai_insights.get("insights_summary", {})
            report += f"""
- **Probabilidad de Éxito**: {summary.get('overall_success_probability', 'N/A'):.1%}
- **Nivel de Confianza**: {summary.get('confidence_level', 'N/A'):.1%}
- **Tendencia del Mercado**: {summary.get('market_trend', 'N/A').title()}
- **Posición de Mercado**: {summary.get('market_position', 'N/A')}
"""
        
        report += f"""
## 📋 Analysis Results
"""
        
        if analysis_result:
            report += f"""
- **Complejidad del Proyecto**: {analysis_result.get('complexity_score', 'N/A')}/10
- **Nivel de Riesgo**: {analysis_result.get('risk_level', 'N/A').title()}
- **Timeline Estimado**: {analysis_result.get('estimated_timeline', 'N/A')}
- **Rango de Presupuesto**: {analysis_result.get('budget_range', 'N/A')}
"""
        
        report += f"""
## 🏗️ ClickUp Integration
"""
        
        if clickup_result:
            workspace = clickup_result.get("workspace_structure", {})
            report += f"""
- **Carpetas Generadas**: {len(workspace.get('folders', []))}
- **Listas Generadas**: {len(workspace.get('lists', []))}
- **Criterios Extraídos**: {len(clickup_result.get('extracted_criteria', []))}
"""
        
        report += f"""
## 🎯 Recommendations
"""
        
        if ai_insights:
            recommendations = ai_insights.get("recommendations", [])
            for i, rec in enumerate(recommendations[:5], 1):
                report += f"{i}. {rec}\n"
        
        report += f"""
## 📈 Next Steps
1. Revisar y aprobar el plan de lanzamiento
2. Implementar las recomendaciones prioritarias
3. Configurar el workspace de ClickUp
4. Establecer métricas de seguimiento
5. Iniciar la ejecución del plan

---
*Reporte generado por Workflow Automation System*
"""
        
        return report
    
    def execute_workflow(self, template_name: str, parameters: Dict[str, Any]) -> str:
        """Ejecutar flujo de trabajo"""
        if template_name not in self.workflow_templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.workflow_templates[template_name]
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Crear ejecución
        execution = WorkflowExecution(
            id=execution_id,
            template_name=template_name,
            status=TaskStatus.IN_PROGRESS,
            started_at=datetime.now(),
            tasks=[]
        )
        
        # Clonar tareas del template
        for task_template in template.tasks:
            task = AutomatedTask(
                id=task_template.id,
                name=task_template.name,
                description=task_template.description,
                task_type=task_template.task_type,
                priority=task_template.priority,
                status=TaskStatus.PENDING,
                created_at=datetime.now(),
                dependencies=task_template.dependencies.copy(),
                parameters=parameters.copy()
            )
            execution.tasks.append(task)
        
        # Agregar a ejecuciones activas
        self.active_executions[execution_id] = execution
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=self._execute_workflow_thread, args=(execution_id,))
        thread.start()
        
        return execution_id
    
    def _execute_workflow_thread(self, execution_id: str):
        """Ejecutar flujo de trabajo en hilo separado"""
        execution = self.active_executions[execution_id]
        
        try:
            logger.info(f"Iniciando ejecución de workflow: {execution.template_name}")
            
            completed_tasks = 0
            total_tasks = len(execution.tasks)
            
            while completed_tasks < total_tasks:
                # Encontrar tareas listas para ejecutar
                ready_tasks = []
                for task in execution.tasks:
                    if task.status == TaskStatus.PENDING:
                        # Verificar dependencias
                        dependencies_met = True
                        for dep_id in task.dependencies:
                            dep_task = next((t for t in execution.tasks if t.id == dep_id), None)
                            if dep_task and dep_task.status != TaskStatus.COMPLETED:
                                dependencies_met = False
                                break
                        
                        if dependencies_met:
                            ready_tasks.append(task)
                
                if not ready_tasks:
                    # No hay tareas listas, verificar si hay errores
                    failed_tasks = [t for t in execution.tasks if t.status == TaskStatus.FAILED]
                    if failed_tasks:
                        execution.status = TaskStatus.FAILED
                        execution.error_log.append(f"Failed tasks: {[t.name for t in failed_tasks]}")
                        break
                    else:
                        # Esperar un poco y reintentar
                        time.sleep(1)
                        continue
                
                # Ejecutar tareas listas
                for task in ready_tasks:
                    task.status = TaskStatus.IN_PROGRESS
                    
                    # Ejecutar tarea
                    handler = self.task_handlers.get(task.task_type)
                    if handler:
                        success = handler(task)
                        if success:
                            task.status = TaskStatus.COMPLETED
                            completed_tasks += 1
                        else:
                            # Reintentar si es posible
                            if task.retry_count < task.max_retries:
                                task.retry_count += 1
                                task.status = TaskStatus.PENDING
                                time.sleep(2)  # Esperar antes de reintentar
                            else:
                                task.status = TaskStatus.FAILED
                                execution.error_log.append(f"Task failed after {task.max_retries} retries: {task.name}")
                    else:
                        task.status = TaskStatus.FAILED
                        execution.error_log.append(f"No handler found for task type: {task.task_type}")
                
                # Actualizar progreso
                execution.progress = (completed_tasks / total_tasks) * 100
            
            # Finalizar ejecución
            if execution.status != TaskStatus.FAILED:
                execution.status = TaskStatus.COMPLETED
                execution.completed_at = datetime.now()
            
            logger.info(f"Workflow execution completed: {execution.template_name} - Status: {execution.status.value}")
            
        except Exception as e:
            logger.error(f"Error executing workflow {execution_id}: {str(e)}")
            execution.status = TaskStatus.FAILED
            execution.error_log.append(str(e))
    
    def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Obtener estado de ejecución"""
        if execution_id not in self.active_executions:
            return {"error": "Execution not found"}
        
        execution = self.active_executions[execution_id]
        
        return {
            "id": execution.id,
            "template_name": execution.template_name,
            "status": execution.status.value,
            "progress": execution.progress,
            "started_at": execution.started_at.isoformat(),
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "tasks": [
                {
                    "id": task.id,
                    "name": task.name,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "error_message": task.error_message
                }
                for task in execution.tasks
            ],
            "error_log": execution.error_log
        }
    
    def schedule_workflow(self, template_name: str, schedule_time: str, parameters: Dict[str, Any]):
        """Programar flujo de trabajo"""
        def job():
            self.execute_workflow(template_name, parameters)
        
        # Programar trabajo
        self.scheduler.every().day.at(schedule_time).do(job)
        logger.info(f"Workflow '{template_name}' scheduled for {schedule_time}")
    
    def start_scheduler(self):
        """Iniciar programador"""
        self.is_running = True
        while self.is_running:
            self.scheduler.run_pending()
            time.sleep(1)
    
    def stop_scheduler(self):
        """Detener programador"""
        self.is_running = False

def main():
    """Demostración del sistema de automatización"""
    print("🤖 Workflow Automation System Demo")
    print("=" * 50)
    
    # Inicializar motor de automatización
    automation_engine = WorkflowAutomationEngine()
    
    # Parámetros de ejemplo
    parameters = {
        "requirements": """
        Lanzar una plataforma SaaS de gestión de proyectos con IA.
        Objetivo: 3,000 usuarios pagos en el primer año.
        Presupuesto: $180,000 para desarrollo y marketing.
        Necesitamos 7 desarrolladores, 2 diseñadores, 1 especialista en IA.
        Debe integrar con Slack, Microsoft Teams, y sistemas de pago.
        Lanzamiento objetivo: Q3 2024.
        """,
        "scenario_type": "saas_platform"
    }
    
    print("📋 Plantillas de Workflow Disponibles:")
    for name, template in automation_engine.workflow_templates.items():
        print(f"   • {name}: {template.description}")
        print(f"     Duración estimada: {template.estimated_duration}")
        print(f"     Tareas: {len(template.tasks)}")
    
    print(f"\n🚀 Ejecutando workflow: Launch Planning")
    
    try:
        # Ejecutar workflow
        execution_id = automation_engine.execute_workflow("launch_planning", parameters)
        print(f"   ID de Ejecución: {execution_id}")
        
        # Monitorear progreso
        print("\n📊 Monitoreando progreso...")
        while True:
            status = automation_engine.get_execution_status(execution_id)
            
            if "error" in status:
                print(f"❌ Error: {status['error']}")
                break
            
            print(f"   Estado: {status['status']} - Progreso: {status['progress']:.1f}%")
            
            # Mostrar tareas
            for task in status['tasks']:
                status_emoji = {
                    'pending': '⏳',
                    'in_progress': '🔄',
                    'completed': '✅',
                    'failed': '❌'
                }
                emoji = status_emoji.get(task['status'], '❓')
                print(f"     {emoji} {task['name']}: {task['status']}")
            
            if status['status'] in ['completed', 'failed']:
                break
            
            time.sleep(2)
        
        # Mostrar resultado final
        if status['status'] == 'completed':
            print(f"\n✅ Workflow completado exitosamente!")
            print(f"   Duración: {status['completed_at']}")
        else:
            print(f"\n❌ Workflow falló")
            if status['error_log']:
                print("   Errores:")
                for error in status['error_log']:
                    print(f"     • {error}")
        
    except Exception as e:
        print(f"❌ Error ejecutando workflow: {str(e)}")
    
    print("\n🎉 Demo del Workflow Automation System completado!")

if __name__ == "__main__":
    main()









