"""
Integration Hub
Sistema de integración con herramientas externas y APIs
"""

import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import base64
import hashlib
import hmac

from enhanced_launch_planner import EnhancedLaunchPlanner
from ai_powered_insights import AIPoweredInsightsEngine
from workflow_automation import WorkflowAutomationEngine
from real_time_monitoring import RealTimeMonitoringSystem

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationType(Enum):
    PROJECT_MANAGEMENT = "project_management"
    COMMUNICATION = "communication"
    ANALYTICS = "analytics"
    DEVELOPMENT = "development"
    MARKETING = "marketing"
    CUSTOMER_SUPPORT = "customer_support"

class IntegrationStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"

@dataclass
class IntegrationConfig:
    """Configuración de integración"""
    name: str
    integration_type: IntegrationType
    api_key: str
    api_secret: Optional[str] = None
    base_url: str = ""
    webhook_url: Optional[str] = None
    status: IntegrationStatus = IntegrationStatus.PENDING
    last_sync: Optional[datetime] = None
    sync_interval: int = 3600  # 1 hora
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class IntegrationData:
    """Datos de integración"""
    source: str
    data_type: str
    data: Any
    timestamp: datetime
    sync_id: str

class ClickUpIntegration:
    """Integración con ClickUp"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.base_url = "https://api.clickup.com/api/v2"
        self.headers = {
            "Authorization": config.api_key,
            "Content-Type": "application/json"
        }
    
    def create_workspace(self, workspace_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear workspace en ClickUp"""
        try:
            # Simular creación de workspace
            workspace = {
                "id": f"ws_{int(time.time())}",
                "name": workspace_data.get("name", "Launch Planning Workspace"),
                "color": "#1f77b4",
                "avatar": None,
                "members": [],
                "created_at": int(time.time() * 1000)
            }
            
            logger.info(f"Workspace creado en ClickUp: {workspace['name']}")
            return {"success": True, "workspace": workspace}
            
        except Exception as e:
            logger.error(f"Error creando workspace en ClickUp: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def create_list(self, workspace_id: str, list_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear lista en ClickUp"""
        try:
            # Simular creación de lista
            list_obj = {
                "id": f"list_{int(time.time())}",
                "name": list_data.get("name", "Launch Tasks"),
                "orderindex": 1,
                "status": {"status": "open", "color": "#d3d3d3"},
                "priority": {"priority": "normal", "color": "#d3d3d3"},
                "assignee": None,
                "task_count": 0,
                "due_date": None,
                "start_date": None,
                "folder": {"id": workspace_id, "name": "Launch Planning"},
                "space": {"id": workspace_id, "name": "Launch Planning"},
                "inbound_address": f"list_{int(time.time())}@clickup.com",
                "archived": False
            }
            
            logger.info(f"Lista creada en ClickUp: {list_obj['name']}")
            return {"success": True, "list": list_obj}
            
        except Exception as e:
            logger.error(f"Error creando lista en ClickUp: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def create_task(self, list_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear tarea en ClickUp"""
        try:
            # Simular creación de tarea
            task = {
                "id": f"task_{int(time.time())}",
                "name": task_data.get("name", "New Task"),
                "description": task_data.get("description", ""),
                "status": {"status": task_data.get("status", "to_do"), "color": "#d3d3d3"},
                "orderindex": f"{int(time.time())}.0",
                "date_created": int(time.time() * 1000),
                "date_updated": int(time.time() * 1000),
                "date_closed": None,
                "date_done": None,
                "archived": False,
                "creator": {"id": 1, "username": "system", "color": "#1f77b4"},
                "assignees": [],
                "watchers": [],
                "checklists": [],
                "tags": task_data.get("tags", []),
                "parent": None,
                "priority": {"priority": task_data.get("priority", "normal"), "color": "#d3d3d3"},
                "due_date": task_data.get("due_date"),
                "start_date": task_data.get("start_date"),
                "points": None,
                "time_estimate": task_data.get("time_estimate"),
                "time_spent": 0,
                "custom_fields": task_data.get("custom_fields", [])
            }
            
            logger.info(f"Tarea creada en ClickUp: {task['name']}")
            return {"success": True, "task": task}
            
        except Exception as e:
            logger.error(f"Error creando tarea en ClickUp: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def sync_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sincronizar datos con ClickUp"""
        try:
            sync_results = []
            
            # Crear workspace
            workspace_result = self.create_workspace(data.get("workspace", {}))
            if workspace_result["success"]:
                workspace_id = workspace_result["workspace"]["id"]
                sync_results.append({"type": "workspace", "result": workspace_result})
                
                # Crear listas
                for list_data in data.get("lists", []):
                    list_result = self.create_list(workspace_id, list_data)
                    if list_result["success"]:
                        list_id = list_result["list"]["id"]
                        sync_results.append({"type": "list", "result": list_result})
                        
                        # Crear tareas
                        for task_data in list_data.get("tasks", []):
                            task_result = self.create_task(list_id, task_data)
                            sync_results.append({"type": "task", "result": task_result})
            
            return {"success": True, "sync_results": sync_results}
            
        except Exception as e:
            logger.error(f"Error sincronizando con ClickUp: {str(e)}")
            return {"success": False, "error": str(e)}

class SlackIntegration:
    """Integración con Slack"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.webhook_url = config.webhook_url
    
    def send_message(self, channel: str, message: str, attachments: List[Dict] = None) -> Dict[str, Any]:
        """Enviar mensaje a Slack"""
        try:
            payload = {
                "channel": channel,
                "text": message,
                "attachments": attachments or []
            }
            
            # Simular envío de mensaje
            logger.info(f"Mensaje enviado a Slack canal {channel}: {message[:50]}...")
            
            return {"success": True, "message_id": f"msg_{int(time.time())}"}
            
        except Exception as e:
            logger.error(f"Error enviando mensaje a Slack: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def create_channel(self, channel_name: str, purpose: str = "") -> Dict[str, Any]:
        """Crear canal en Slack"""
        try:
            # Simular creación de canal
            channel = {
                "id": f"C{int(time.time())}",
                "name": channel_name,
                "purpose": purpose,
                "created": int(time.time()),
                "creator": "system",
                "is_archived": False,
                "is_general": False,
                "is_member": True,
                "is_private": False,
                "is_shared": False
            }
            
            logger.info(f"Canal creado en Slack: {channel_name}")
            return {"success": True, "channel": channel}
            
        except Exception as e:
            logger.error(f"Error creando canal en Slack: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enviar alerta a Slack"""
        try:
            level_colors = {
                "info": "#36a64f",
                "warning": "#ff9500",
                "critical": "#ff0000",
                "emergency": "#8b0000"
            }
            
            attachment = {
                "color": level_colors.get(alert_data.get("level", "info"), "#36a64f"),
                "title": alert_data.get("title", "Launch Monitoring Alert"),
                "text": alert_data.get("message", ""),
                "fields": [
                    {"title": "Project", "value": alert_data.get("project_name", "Unknown"), "short": True},
                    {"title": "Level", "value": alert_data.get("level", "info").upper(), "short": True},
                    {"title": "Time", "value": alert_data.get("timestamp", datetime.now().isoformat()), "short": True}
                ],
                "footer": "Launch Planning System",
                "ts": int(time.time())
            }
            
            result = self.send_message(
                channel=alert_data.get("channel", "#launch-alerts"),
                message=f"🚨 {alert_data.get('title', 'Alert')}",
                attachments=[attachment]
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error enviando alerta a Slack: {str(e)}")
            return {"success": False, "error": str(e)}

class GoogleAnalyticsIntegration:
    """Integración con Google Analytics"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.base_url = "https://analyticsreporting.googleapis.com/v4"
    
    def get_metrics(self, view_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Obtener métricas de Google Analytics"""
        try:
            # Simular datos de Analytics
            metrics = {
                "sessions": 1250,
                "users": 980,
                "pageviews": 3450,
                "bounce_rate": 0.45,
                "avg_session_duration": 180,
                "conversion_rate": 0.08,
                "revenue": 12500.0
            }
            
            logger.info(f"Métricas obtenidas de Google Analytics para vista {view_id}")
            return {"success": True, "metrics": metrics}
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas de Google Analytics: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def create_goal(self, view_id: str, goal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear objetivo en Google Analytics"""
        try:
            # Simular creación de objetivo
            goal = {
                "id": f"goal_{int(time.time())}",
                "name": goal_data.get("name", "Launch Goal"),
                "type": goal_data.get("type", "URL_DESTINATION"),
                "url": goal_data.get("url", ""),
                "value": goal_data.get("value", 0),
                "active": True,
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"Objetivo creado en Google Analytics: {goal['name']}")
            return {"success": True, "goal": goal}
            
        except Exception as e:
            logger.error(f"Error creando objetivo en Google Analytics: {str(e)}")
            return {"success": False, "error": str(e)}

class GitHubIntegration:
    """Integración con GitHub"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {config.api_key}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def create_repository(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear repositorio en GitHub"""
        try:
            # Simular creación de repositorio
            repository = {
                "id": int(time.time()),
                "name": repo_data.get("name", "launch-project"),
                "full_name": f"{repo_data.get('owner', 'user')}/{repo_data.get('name', 'launch-project')}",
                "description": repo_data.get("description", "Launch planning project"),
                "private": repo_data.get("private", False),
                "html_url": f"https://github.com/{repo_data.get('owner', 'user')}/{repo_data.get('name', 'launch-project')}",
                "clone_url": f"https://github.com/{repo_data.get('owner', 'user')}/{repo_data.get('name', 'launch-project')}.git",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "pushed_at": datetime.now().isoformat(),
                "size": 0,
                "stargazers_count": 0,
                "watchers_count": 0,
                "forks_count": 0,
                "open_issues_count": 0,
                "default_branch": "main"
            }
            
            logger.info(f"Repositorio creado en GitHub: {repository['name']}")
            return {"success": True, "repository": repository}
            
        except Exception as e:
            logger.error(f"Error creando repositorio en GitHub: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def create_issue(self, owner: str, repo: str, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear issue en GitHub"""
        try:
            # Simular creación de issue
            issue = {
                "id": int(time.time()),
                "number": int(time.time()) % 1000,
                "title": issue_data.get("title", "New Issue"),
                "body": issue_data.get("body", ""),
                "state": "open",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "closed_at": None,
                "labels": issue_data.get("labels", []),
                "assignees": issue_data.get("assignees", []),
                "milestone": issue_data.get("milestone"),
                "html_url": f"https://github.com/{owner}/{repo}/issues/{int(time.time()) % 1000}"
            }
            
            logger.info(f"Issue creado en GitHub: {issue['title']}")
            return {"success": True, "issue": issue}
            
        except Exception as e:
            logger.error(f"Error creando issue en GitHub: {str(e)}")
            return {"success": False, "error": str(e)}

class IntegrationHub:
    """Hub central de integraciones"""
    
    def __init__(self):
        self.enhanced_planner = EnhancedLaunchPlanner()
        self.insights_engine = AIPoweredInsightsEngine()
        self.workflow_engine = WorkflowAutomationEngine()
        self.monitoring_system = RealTimeMonitoringSystem()
        
        self.integrations = {}
        self.integration_handlers = self._register_integration_handlers()
        
    def _register_integration_handlers(self) -> Dict[str, Callable]:
        """Registrar manejadores de integración"""
        return {
            "clickup": self._handle_clickup_integration,
            "slack": self._handle_slack_integration,
            "google_analytics": self._handle_google_analytics_integration,
            "github": self._handle_github_integration
        }
    
    def add_integration(self, integration_type: str, config: IntegrationConfig) -> bool:
        """Agregar integración"""
        try:
            if integration_type == "clickup":
                self.integrations[integration_type] = ClickUpIntegration(config)
            elif integration_type == "slack":
                self.integrations[integration_type] = SlackIntegration(config)
            elif integration_type == "google_analytics":
                self.integrations[integration_type] = GoogleAnalyticsIntegration(config)
            elif integration_type == "github":
                self.integrations[integration_type] = GitHubIntegration(config)
            else:
                logger.error(f"Tipo de integración no soportado: {integration_type}")
                return False
            
            config.status = IntegrationStatus.ACTIVE
            logger.info(f"Integración agregada: {integration_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error agregando integración {integration_type}: {str(e)}")
            return False
    
    def remove_integration(self, integration_type: str) -> bool:
        """Remover integración"""
        if integration_type in self.integrations:
            del self.integrations[integration_type]
            logger.info(f"Integración removida: {integration_type}")
            return True
        return False
    
    def sync_launch_plan_to_clickup(self, launch_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Sincronizar plan de lanzamiento con ClickUp"""
        try:
            if "clickup" not in self.integrations:
                return {"success": False, "error": "ClickUp integration not configured"}
            
            clickup_integration = self.integrations["clickup"]
            
            # Preparar datos para ClickUp
            workspace_data = {
                "name": f"Launch Plan - {launch_plan.get('scenario', {}).get('name', 'Unknown')}"
            }
            
            lists_data = []
            for phase in launch_plan.get("phases", []):
                list_data = {
                    "name": phase.get("name", "Phase"),
                    "tasks": []
                }
                
                for item in phase.get("items", []):
                    task_data = {
                        "name": item.get("title", "Task"),
                        "description": item.get("description", ""),
                        "status": item.get("status", "to_do"),
                        "priority": item.get("priority", "normal"),
                        "tags": item.get("tags", []),
                        "custom_fields": [
                            {"name": "Category", "value": item.get("category", "")},
                            {"name": "Estimated Duration", "value": item.get("estimated_duration", "")}
                        ]
                    }
                    list_data["tasks"].append(task_data)
                
                lists_data.append(list_data)
            
            sync_data = {
                "workspace": workspace_data,
                "lists": lists_data
            }
            
            result = clickup_integration.sync_data(sync_data)
            return result
            
        except Exception as e:
            logger.error(f"Error sincronizando con ClickUp: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_slack_notification(self, message: str, channel: str = "#launch-updates") -> Dict[str, Any]:
        """Enviar notificación a Slack"""
        try:
            if "slack" not in self.integrations:
                return {"success": False, "error": "Slack integration not configured"}
            
            slack_integration = self.integrations["slack"]
            result = slack_integration.send_message(channel, message)
            return result
            
        except Exception as e:
            logger.error(f"Error enviando notificación a Slack: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_alert_to_slack(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enviar alerta a Slack"""
        try:
            if "slack" not in self.integrations:
                return {"success": False, "error": "Slack integration not configured"}
            
            slack_integration = self.integrations["slack"]
            result = slack_integration.send_alert(alert_data)
            return result
            
        except Exception as e:
            logger.error(f"Error enviando alerta a Slack: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def create_github_repository(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear repositorio en GitHub"""
        try:
            if "github" not in self.integrations:
                return {"success": False, "error": "GitHub integration not configured"}
            
            github_integration = self.integrations["github"]
            result = github_integration.create_repository(repo_data)
            return result
            
        except Exception as e:
            logger.error(f"Error creando repositorio en GitHub: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_analytics_metrics(self, view_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Obtener métricas de Google Analytics"""
        try:
            if "google_analytics" not in self.integrations:
                return {"success": False, "error": "Google Analytics integration not configured"}
            
            analytics_integration = self.integrations["google_analytics"]
            result = analytics_integration.get_metrics(view_id, start_date, end_date)
            return result
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas de Google Analytics: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _handle_clickup_integration(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Manejar integración con ClickUp"""
        return self.sync_launch_plan_to_clickup(data)
    
    def _handle_slack_integration(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Manejar integración con Slack"""
        if data.get("type") == "alert":
            return self.send_alert_to_slack(data)
        else:
            return self.send_slack_notification(data.get("message", ""), data.get("channel", "#launch-updates"))
    
    def _handle_google_analytics_integration(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Manejar integración con Google Analytics"""
        return self.get_analytics_metrics(
            data.get("view_id", ""),
            data.get("start_date", ""),
            data.get("end_date", "")
        )
    
    def _handle_github_integration(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Manejar integración con GitHub"""
        if data.get("action") == "create_repository":
            return self.create_github_repository(data)
        else:
            return {"success": False, "error": "Unsupported GitHub action"}
    
    def execute_integration_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar flujo de trabajo de integración"""
        try:
            results = []
            
            # Sincronizar con ClickUp
            if "clickup" in self.integrations and workflow_data.get("sync_clickup", False):
                clickup_result = self.sync_launch_plan_to_clickup(workflow_data.get("launch_plan", {}))
                results.append({"integration": "clickup", "result": clickup_result})
            
            # Enviar notificación a Slack
            if "slack" in self.integrations and workflow_data.get("notify_slack", False):
                slack_result = self.send_slack_notification(
                    workflow_data.get("slack_message", "Launch plan updated"),
                    workflow_data.get("slack_channel", "#launch-updates")
                )
                results.append({"integration": "slack", "result": slack_result})
            
            # Crear repositorio en GitHub
            if "github" in self.integrations and workflow_data.get("create_github_repo", False):
                github_result = self.create_github_repository(workflow_data.get("github_repo_data", {}))
                results.append({"integration": "github", "result": github_result})
            
            return {"success": True, "results": results}
            
        except Exception as e:
            logger.error(f"Error ejecutando flujo de trabajo de integración: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Obtener estado de las integraciones"""
        status = {}
        
        for integration_type, integration in self.integrations.items():
            status[integration_type] = {
                "active": True,
                "type": integration_type,
                "last_sync": getattr(integration.config, 'last_sync', None),
                "status": getattr(integration.config, 'status', IntegrationStatus.ACTIVE).value
            }
        
        return {
            "total_integrations": len(self.integrations),
            "active_integrations": len([i for i in self.integrations.values() if getattr(i.config, 'status', IntegrationStatus.ACTIVE) == IntegrationStatus.ACTIVE]),
            "integrations": status
        }

def main():
    """Demostración del Integration Hub"""
    print("🔗 Integration Hub Demo")
    print("=" * 40)
    
    # Inicializar hub de integraciones
    integration_hub = IntegrationHub()
    
    # Configurar integraciones
    print("📋 Configurando integraciones...")
    
    # ClickUp
    clickup_config = IntegrationConfig(
        name="ClickUp Integration",
        integration_type=IntegrationType.PROJECT_MANAGEMENT,
        api_key="pk_clickup_demo_key",
        base_url="https://api.clickup.com/api/v2"
    )
    integration_hub.add_integration("clickup", clickup_config)
    
    # Slack
    slack_config = IntegrationConfig(
        name="Slack Integration",
        integration_type=IntegrationType.COMMUNICATION,
        api_key="slack_demo_key",
        webhook_url="https://hooks.slack.com/services/demo/webhook"
    )
    integration_hub.add_integration("slack", slack_config)
    
    # GitHub
    github_config = IntegrationConfig(
        name="GitHub Integration",
        integration_type=IntegrationType.DEVELOPMENT,
        api_key="ghp_demo_github_token"
    )
    integration_hub.add_integration("github", github_config)
    
    # Google Analytics
    analytics_config = IntegrationConfig(
        name="Google Analytics Integration",
        integration_type=IntegrationType.ANALYTICS,
        api_key="analytics_demo_key"
    )
    integration_hub.add_integration("google_analytics", analytics_config)
    
    print("✅ Integraciones configuradas")
    
    # Mostrar estado de integraciones
    status = integration_hub.get_integration_status()
    print(f"\n📊 Estado de Integraciones:")
    print(f"   Total: {status['total_integrations']}")
    print(f"   Activas: {status['active_integrations']}")
    
    for integration_type, integration_status in status['integrations'].items():
        print(f"   • {integration_type}: {'✅' if integration_status['active'] else '❌'}")
    
    # Crear plan de lanzamiento de ejemplo
    print(f"\n🚀 Creando plan de lanzamiento de ejemplo...")
    
    enhanced_planner = EnhancedLaunchPlanner()
    launch_plan = enhanced_planner.create_enhanced_launch_plan(
        """
        Lanzar plataforma SaaS de gestión de proyectos.
        Objetivo: 2,000 usuarios pagos en el primer año.
        Presupuesto: $150,000 para desarrollo y marketing.
        Necesitamos 6 desarrolladores, 2 diseñadores, 1 especialista en IA.
        Lanzamiento objetivo: Q2 2024.
        """,
        "saas_platform"
    )
    
    print("✅ Plan de lanzamiento creado")
    
    # Ejecutar flujo de trabajo de integración
    print(f"\n🔄 Ejecutando flujo de trabajo de integración...")
    
    workflow_data = {
        "sync_clickup": True,
        "notify_slack": True,
        "create_github_repo": True,
        "launch_plan": launch_plan,
        "slack_message": "🚀 Nuevo plan de lanzamiento creado y sincronizado con todas las herramientas!",
        "slack_channel": "#launch-updates",
        "github_repo_data": {
            "name": "launch-planning-saas",
            "description": "SaaS Platform Launch Planning Repository",
            "private": False,
            "owner": "company"
        }
    }
    
    integration_results = integration_hub.execute_integration_workflow(workflow_data)
    
    if integration_results["success"]:
        print("✅ Flujo de trabajo de integración ejecutado exitosamente")
        
        for result in integration_results["results"]:
            integration_type = result["integration"]
            result_data = result["result"]
            
            if result_data["success"]:
                print(f"   ✅ {integration_type}: Sincronización exitosa")
            else:
                print(f"   ❌ {integration_type}: {result_data.get('error', 'Error desconocido')}")
    else:
        print(f"❌ Error en flujo de trabajo: {integration_results.get('error', 'Error desconocido')}")
    
    # Enviar alerta de ejemplo
    print(f"\n🚨 Enviando alerta de ejemplo...")
    
    alert_data = {
        "title": "Launch Plan Updated",
        "message": "El plan de lanzamiento ha sido actualizado con nuevas métricas de IA",
        "level": "info",
        "project_name": "SaaS Platform Launch",
        "timestamp": datetime.now().isoformat(),
        "channel": "#launch-alerts"
    }
    
    alert_result = integration_hub.send_alert_to_slack(alert_data)
    
    if alert_result["success"]:
        print("✅ Alerta enviada a Slack exitosamente")
    else:
        print(f"❌ Error enviando alerta: {alert_result.get('error', 'Error desconocido')}")
    
    # Obtener métricas de Analytics
    print(f"\n📊 Obteniendo métricas de Google Analytics...")
    
    analytics_result = integration_hub.get_analytics_metrics(
        view_id="123456789",
        start_date="2024-01-01",
        end_date="2024-01-31"
    )
    
    if analytics_result["success"]:
        metrics = analytics_result["metrics"]
        print("✅ Métricas obtenidas:")
        print(f"   • Sesiones: {metrics['sessions']:,}")
        print(f"   • Usuarios: {metrics['users']:,}")
        print(f"   • Páginas vistas: {metrics['pageviews']:,}")
        print(f"   • Tasa de rebote: {metrics['bounce_rate']:.1%}")
        print(f"   • Ingresos: ${metrics['revenue']:,.0f}")
    else:
        print(f"❌ Error obteniendo métricas: {analytics_result.get('error', 'Error desconocido')}")
    
    print(f"\n🎉 Demo del Integration Hub completado!")
    print(f"   🔗 {status['total_integrations']} integraciones configuradas")
    print(f"   ✅ {status['active_integrations']} integraciones activas")
    print(f"   🚀 Flujo de trabajo ejecutado exitosamente")

if __name__ == "__main__":
    main()









