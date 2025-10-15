"""
Real-Time Monitoring & Alerting System
Sistema de monitoreo y alertas en tiempo real para lanzamientos
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from enhanced_launch_planner import EnhancedLaunchPlanner
from ai_powered_insights import AIPoweredInsightsEngine
from workflow_automation import WorkflowAutomationEngine

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class MetricType(Enum):
    SUCCESS_PROBABILITY = "success_probability"
    BUDGET_UTILIZATION = "budget_utilization"
    TIMELINE_ADHERENCE = "timeline_adherence"
    TEAM_EFFICIENCY = "team_efficiency"
    RISK_LEVEL = "risk_level"
    MARKET_CONDITIONS = "market_conditions"

@dataclass
class Metric:
    """Métrica de monitoreo"""
    id: str
    name: str
    metric_type: MetricType
    value: float
    threshold_warning: float
    threshold_critical: float
    unit: str
    timestamp: datetime
    trend: str  # "up", "down", "stable"
    change_rate: float

@dataclass
class Alert:
    """Alerta del sistema"""
    id: str
    title: str
    message: str
    level: AlertLevel
    metric_id: str
    current_value: float
    threshold_value: float
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False
    actions_taken: List[str] = None

    def __post_init__(self):
        if self.actions_taken is None:
            self.actions_taken = []

@dataclass
class MonitoringConfig:
    """Configuración de monitoreo"""
    check_interval: int  # segundos
    alert_cooldown: int  # segundos
    email_notifications: bool
    slack_notifications: bool
    webhook_url: Optional[str] = None
    email_recipients: List[str] = None

    def __post_init__(self):
        if self.email_recipients is None:
            self.email_recipients = []

@dataclass
class LaunchProject:
    """Proyecto de lanzamiento monitoreado"""
    id: str
    name: str
    description: str
    scenario_type: str
    requirements: str
    start_date: datetime
    target_launch_date: datetime
    budget: float
    team_size: int
    status: str
    metrics: Dict[str, Metric] = None
    alerts: List[Alert] = None
    last_updated: datetime = None

    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}
        if self.alerts is None:
            self.alerts = []
        if self.last_updated is None:
            self.last_updated = datetime.now()

class RealTimeMonitoringSystem:
    """Sistema de monitoreo en tiempo real"""
    
    def __init__(self):
        self.enhanced_planner = EnhancedLaunchPlanner()
        self.insights_engine = AIPoweredInsightsEngine()
        self.workflow_engine = WorkflowAutomationEngine()
        
        self.projects = {}
        self.monitoring_config = MonitoringConfig(
            check_interval=60,  # 1 minuto
            alert_cooldown=300,  # 5 minutos
            email_notifications=True,
            slack_notifications=False,
            email_recipients=["admin@company.com", "pm@company.com"]
        )
        
        self.alert_handlers = self._register_alert_handlers()
        self.metric_calculators = self._register_metric_calculators()
        self.is_monitoring = False
        self.monitoring_thread = None
        
    def _register_alert_handlers(self) -> Dict[AlertLevel, Callable]:
        """Registrar manejadores de alertas"""
        return {
            AlertLevel.INFO: self._handle_info_alert,
            AlertLevel.WARNING: self._handle_warning_alert,
            AlertLevel.CRITICAL: self._handle_critical_alert,
            AlertLevel.EMERGENCY: self._handle_emergency_alert
        }
    
    def _register_metric_calculators(self) -> Dict[MetricType, Callable]:
        """Registrar calculadores de métricas"""
        return {
            MetricType.SUCCESS_PROBABILITY: self._calculate_success_probability,
            MetricType.BUDGET_UTILIZATION: self._calculate_budget_utilization,
            MetricType.TIMELINE_ADHERENCE: self._calculate_timeline_adherence,
            MetricType.TEAM_EFFICIENCY: self._calculate_team_efficiency,
            MetricType.RISK_LEVEL: self._calculate_risk_level,
            MetricType.MARKET_CONDITIONS: self._calculate_market_conditions
        }
    
    def add_project(self, project: LaunchProject) -> str:
        """Agregar proyecto para monitoreo"""
        self.projects[project.id] = project
        logger.info(f"Proyecto agregado para monitoreo: {project.name}")
        return project.id
    
    def remove_project(self, project_id: str) -> bool:
        """Remover proyecto del monitoreo"""
        if project_id in self.projects:
            del self.projects[project_id]
            logger.info(f"Proyecto removido del monitoreo: {project_id}")
            return True
        return False
    
    def start_monitoring(self):
        """Iniciar monitoreo en tiempo real"""
        if self.is_monitoring:
            logger.warning("El monitoreo ya está activo")
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logger.info("Sistema de monitoreo iniciado")
    
    def stop_monitoring(self):
        """Detener monitoreo"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        
        logger.info("Sistema de monitoreo detenido")
    
    def _monitoring_loop(self):
        """Loop principal de monitoreo"""
        while self.is_monitoring:
            try:
                for project_id, project in self.projects.items():
                    self._update_project_metrics(project)
                    self._check_alerts(project)
                
                time.sleep(self.monitoring_config.check_interval)
                
            except Exception as e:
                logger.error(f"Error en loop de monitoreo: {str(e)}")
                time.sleep(5)  # Esperar antes de reintentar
    
    def _update_project_metrics(self, project: LaunchProject):
        """Actualizar métricas del proyecto"""
        try:
            # Calcular métricas
            for metric_type, calculator in self.metric_calculators.items():
                metric_data = calculator(project)
                
                if metric_data:
                    metric = Metric(
                        id=f"{project.id}_{metric_type.value}",
                        name=metric_data["name"],
                        metric_type=metric_type,
                        value=metric_data["value"],
                        threshold_warning=metric_data["threshold_warning"],
                        threshold_critical=metric_data["threshold_critical"],
                        unit=metric_data["unit"],
                        timestamp=datetime.now(),
                        trend=metric_data.get("trend", "stable"),
                        change_rate=metric_data.get("change_rate", 0.0)
                    )
                    
                    project.metrics[metric_type.value] = metric
            
            project.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"Error actualizando métricas para proyecto {project.id}: {str(e)}")
    
    def _calculate_success_probability(self, project: LaunchProject) -> Dict[str, Any]:
        """Calcular probabilidad de éxito"""
        try:
            # Análisis con IA
            insights = self.insights_engine.generate_comprehensive_insights(
                project.requirements, project.scenario_type
            )
            
            success_prob = insights["insights_summary"]["overall_success_probability"]
            
            return {
                "name": "Success Probability",
                "value": success_prob,
                "threshold_warning": 0.6,
                "threshold_critical": 0.4,
                "unit": "%",
                "trend": "stable",
                "change_rate": 0.0
            }
            
        except Exception as e:
            logger.error(f"Error calculando probabilidad de éxito: {str(e)}")
            return None
    
    def _calculate_budget_utilization(self, project: LaunchProject) -> Dict[str, Any]:
        """Calcular utilización de presupuesto"""
        try:
            # Simular utilización de presupuesto basada en tiempo transcurrido
            days_elapsed = (datetime.now() - project.start_date).days
            total_days = (project.target_launch_date - project.start_date).days
            
            if total_days > 0:
                time_progress = days_elapsed / total_days
                # Simular utilización de presupuesto (puede variar)
                budget_utilization = min(1.0, time_progress * 1.2)  # 20% más rápido que el tiempo
            else:
                budget_utilization = 0.0
            
            return {
                "name": "Budget Utilization",
                "value": budget_utilization,
                "threshold_warning": 0.8,
                "threshold_critical": 0.95,
                "unit": "%",
                "trend": "up",
                "change_rate": 0.05
            }
            
        except Exception as e:
            logger.error(f"Error calculando utilización de presupuesto: {str(e)}")
            return None
    
    def _calculate_timeline_adherence(self, project: LaunchProject) -> Dict[str, Any]:
        """Calcular adherencia al cronograma"""
        try:
            # Calcular progreso del tiempo vs progreso real
            days_elapsed = (datetime.now() - project.start_date).days
            total_days = (project.target_launch_date - project.start_date).days
            
            if total_days > 0:
                expected_progress = days_elapsed / total_days
                # Simular progreso real (puede variar)
                actual_progress = expected_progress * 0.9  # 10% atrasado
                timeline_adherence = max(0.0, min(1.0, actual_progress / expected_progress))
            else:
                timeline_adherence = 1.0
            
            return {
                "name": "Timeline Adherence",
                "value": timeline_adherence,
                "threshold_warning": 0.8,
                "threshold_critical": 0.6,
                "unit": "%",
                "trend": "down",
                "change_rate": -0.02
            }
            
        except Exception as e:
            logger.error(f"Error calculando adherencia al cronograma: {str(e)}")
            return None
    
    def _calculate_team_efficiency(self, project: LaunchProject) -> Dict[str, Any]:
        """Calcular eficiencia del equipo"""
        try:
            # Simular eficiencia del equipo basada en tamaño y complejidad
            base_efficiency = 0.8
            
            # Ajustar por tamaño del equipo
            if project.team_size < 5:
                team_factor = 0.9  # Equipos pequeños más eficientes
            elif project.team_size > 10:
                team_factor = 0.7  # Equipos grandes menos eficientes
            else:
                team_factor = 1.0
            
            # Ajustar por tiempo transcurrido (fatiga)
            days_elapsed = (datetime.now() - project.start_date).days
            fatigue_factor = max(0.6, 1.0 - (days_elapsed * 0.01))
            
            team_efficiency = base_efficiency * team_factor * fatigue_factor
            
            return {
                "name": "Team Efficiency",
                "value": team_efficiency,
                "threshold_warning": 0.7,
                "threshold_critical": 0.5,
                "unit": "%",
                "trend": "down",
                "change_rate": -0.01
            }
            
        except Exception as e:
            logger.error(f"Error calculando eficiencia del equipo: {str(e)}")
            return None
    
    def _calculate_risk_level(self, project: LaunchProject) -> Dict[str, Any]:
        """Calcular nivel de riesgo"""
        try:
            # Análisis de riesgos
            basic_analysis = self.enhanced_planner.base_planner.analyze_launch_requirements(
                project.requirements
            )
            
            # Convertir nivel de riesgo a número
            risk_levels = {"low": 0.3, "medium": 0.6, "high": 0.8}
            risk_value = risk_levels.get(basic_analysis["risk_level"], 0.5)
            
            return {
                "name": "Risk Level",
                "value": risk_value,
                "threshold_warning": 0.6,
                "threshold_critical": 0.8,
                "unit": "level",
                "trend": "stable",
                "change_rate": 0.0
            }
            
        except Exception as e:
            logger.error(f"Error calculando nivel de riesgo: {str(e)}")
            return None
    
    def _calculate_market_conditions(self, project: LaunchProject) -> Dict[str, Any]:
        """Calcular condiciones del mercado"""
        try:
            # Análisis de tendencias del mercado
            trend_analysis = self.insights_engine.analyze_trends(project.scenario_type)
            
            # Convertir tendencia a valor numérico
            trend_values = {"up": 0.8, "stable": 0.5, "down": 0.2}
            market_conditions = trend_values.get(trend_analysis.trend_direction, 0.5)
            
            return {
                "name": "Market Conditions",
                "value": market_conditions,
                "threshold_warning": 0.3,
                "threshold_critical": 0.2,
                "unit": "index",
                "trend": trend_analysis.trend_direction,
                "change_rate": 0.0
            }
            
        except Exception as e:
            logger.error(f"Error calculando condiciones del mercado: {str(e)}")
            return None
    
    def _check_alerts(self, project: LaunchProject):
        """Verificar alertas para el proyecto"""
        try:
            for metric_type, metric in project.metrics.items():
                # Verificar umbrales
                if metric.value <= metric.threshold_critical:
                    level = AlertLevel.CRITICAL
                elif metric.value <= metric.threshold_warning:
                    level = AlertLevel.WARNING
                else:
                    continue
                
                # Verificar si ya existe una alerta similar reciente
                recent_alerts = [
                    alert for alert in project.alerts
                    if alert.metric_id == metric.id and 
                    alert.level == level and
                    not alert.resolved and
                    (datetime.now() - alert.timestamp).seconds < self.monitoring_config.alert_cooldown
                ]
                
                if recent_alerts:
                    continue  # Ya existe una alerta reciente
                
                # Crear nueva alerta
                alert = Alert(
                    id=f"alert_{project.id}_{metric_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    title=f"{level.value.title()} Alert: {metric.name}",
                    message=f"{metric.name} is {metric.value:.1f}{metric.unit}, below threshold of {metric.threshold_warning:.1f}{metric.unit}",
                    level=level,
                    metric_id=metric.id,
                    current_value=metric.value,
                    threshold_value=metric.threshold_warning,
                    timestamp=datetime.now()
                )
                
                project.alerts.append(alert)
                
                # Manejar alerta
                self._handle_alert(alert, project)
                
        except Exception as e:
            logger.error(f"Error verificando alertas para proyecto {project.id}: {str(e)}")
    
    def _handle_alert(self, alert: Alert, project: LaunchProject):
        """Manejar alerta"""
        try:
            handler = self.alert_handlers.get(alert.level)
            if handler:
                handler(alert, project)
            
            logger.info(f"Alerta manejada: {alert.title} para proyecto {project.name}")
            
        except Exception as e:
            logger.error(f"Error manejando alerta {alert.id}: {str(e)}")
    
    def _handle_info_alert(self, alert: Alert, project: LaunchProject):
        """Manejar alerta informativa"""
        logger.info(f"INFO: {alert.message} - Proyecto: {project.name}")
        
        # Agregar acción tomada
        alert.actions_taken.append("Logged as information")
    
    def _handle_warning_alert(self, alert: Alert, project: LaunchProject):
        """Manejar alerta de advertencia"""
        logger.warning(f"WARNING: {alert.message} - Proyecto: {project.name}")
        
        # Enviar notificación por email si está configurado
        if self.monitoring_config.email_notifications:
            self._send_email_notification(alert, project)
        
        # Agregar acción tomada
        alert.actions_taken.append("Email notification sent")
    
    def _handle_critical_alert(self, alert: Alert, project: LaunchProject):
        """Manejar alerta crítica"""
        logger.critical(f"CRITICAL: {alert.message} - Proyecto: {project.name}")
        
        # Enviar notificaciones
        if self.monitoring_config.email_notifications:
            self._send_email_notification(alert, project, urgent=True)
        
        # Crear tarea de workflow para mitigación
        self._create_mitigation_workflow(alert, project)
        
        # Agregar acciones tomadas
        alert.actions_taken.extend([
            "Urgent email notification sent",
            "Mitigation workflow triggered"
        ])
    
    def _handle_emergency_alert(self, alert: Alert, project: LaunchProject):
        """Manejar alerta de emergencia"""
        logger.critical(f"EMERGENCY: {alert.message} - Proyecto: {project.name}")
        
        # Enviar notificaciones urgentes
        if self.monitoring_config.email_notifications:
            self._send_email_notification(alert, project, urgent=True)
        
        # Crear workflow de emergencia
        self._create_emergency_workflow(alert, project)
        
        # Agregar acciones tomadas
        alert.actions_taken.extend([
            "Emergency email notification sent",
            "Emergency workflow triggered",
            "Stakeholders notified"
        ])
    
    def _send_email_notification(self, alert: Alert, project: LaunchProject, urgent: bool = False):
        """Enviar notificación por email"""
        try:
            # Configurar email (simulado)
            subject = f"{'[URGENT] ' if urgent else ''}Launch Monitoring Alert: {alert.title}"
            
            body = f"""
            Alert Details:
            - Project: {project.name}
            - Level: {alert.level.value.upper()}
            - Message: {alert.message}
            - Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
            - Current Value: {alert.current_value}
            - Threshold: {alert.threshold_value}
            
            Actions Taken:
            {chr(10).join(f'- {action}' for action in alert.actions_taken)}
            
            Please review and take appropriate action.
            """
            
            # Simular envío de email
            logger.info(f"Email notification sent: {subject}")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
    
    def _create_mitigation_workflow(self, alert: Alert, project: LaunchProject):
        """Crear workflow de mitigación"""
        try:
            parameters = {
                "project_id": project.id,
                "alert_id": alert.id,
                "metric_type": alert.metric_id,
                "current_value": alert.current_value,
                "threshold_value": alert.threshold_value
            }
            
            # Ejecutar workflow de evaluación de riesgos
            execution_id = self.workflow_engine.execute_workflow("risk_assessment", parameters)
            logger.info(f"Mitigation workflow triggered: {execution_id}")
            
        except Exception as e:
            logger.error(f"Error creating mitigation workflow: {str(e)}")
    
    def _create_emergency_workflow(self, alert: Alert, project: LaunchProject):
        """Crear workflow de emergencia"""
        try:
            # Crear workflow personalizado para emergencias
            emergency_parameters = {
                "project_id": project.id,
                "alert_id": alert.id,
                "emergency_level": "high",
                "immediate_actions": [
                    "Notify all stakeholders",
                    "Schedule emergency meeting",
                    "Review project status",
                    "Implement contingency plan"
                ]
            }
            
            logger.info(f"Emergency workflow created for project {project.name}")
            
        except Exception as e:
            logger.error(f"Error creating emergency workflow: {str(e)}")
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Obtener estado del proyecto"""
        if project_id not in self.projects:
            return {"error": "Project not found"}
        
        project = self.projects[project_id]
        
        return {
            "id": project.id,
            "name": project.name,
            "status": project.status,
            "last_updated": project.last_updated.isoformat(),
            "metrics": {
                metric_type: {
                    "name": metric.name,
                    "value": metric.value,
                    "unit": metric.unit,
                    "trend": metric.trend,
                    "timestamp": metric.timestamp.isoformat()
                }
                for metric_type, metric in project.metrics.items()
            },
            "alerts": [
                {
                    "id": alert.id,
                    "title": alert.title,
                    "level": alert.level.value,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "acknowledged": alert.acknowledged,
                    "resolved": alert.resolved
                }
                for alert in project.alerts
            ],
            "active_alerts": len([a for a in project.alerts if not a.resolved])
        }
    
    def acknowledge_alert(self, project_id: str, alert_id: str) -> bool:
        """Reconocer alerta"""
        if project_id not in self.projects:
            return False
        
        project = self.projects[project_id]
        alert = next((a for a in project.alerts if a.id == alert_id), None)
        
        if alert:
            alert.acknowledged = True
            alert.actions_taken.append("Alert acknowledged by user")
            return True
        
        return False
    
    def resolve_alert(self, project_id: str, alert_id: str) -> bool:
        """Resolver alerta"""
        if project_id not in self.projects:
            return False
        
        project = self.projects[project_id]
        alert = next((a for a in project.alerts if a.id == alert_id), None)
        
        if alert:
            alert.resolved = True
            alert.actions_taken.append("Alert resolved by user")
            return True
        
        return False

def main():
    """Demostración del sistema de monitoreo en tiempo real"""
    print("📊 Real-Time Monitoring & Alerting System Demo")
    print("=" * 60)
    
    # Inicializar sistema de monitoreo
    monitoring_system = RealTimeMonitoringSystem()
    
    # Crear proyecto de ejemplo
    project = LaunchProject(
        id="proj_001",
        name="SaaS Platform Launch",
        description="Lanzamiento de plataforma SaaS con IA",
        scenario_type="saas_platform",
        requirements="""
        Lanzar plataforma SaaS de análisis de datos con IA.
        Objetivo: 2,000 usuarios pagos en el primer año.
        Presupuesto: $150,000 para desarrollo y marketing.
        Necesitamos 6 desarrolladores, 2 diseñadores, 1 especialista en IA.
        Lanzamiento objetivo: Q2 2024.
        """,
        start_date=datetime.now() - timedelta(days=30),
        target_launch_date=datetime.now() + timedelta(days=60),
        budget=150000,
        team_size=9,
        status="in_progress"
    )
    
    print("📋 Configuración del Sistema:")
    print(f"   Intervalo de verificación: {monitoring_system.monitoring_config.check_interval} segundos")
    print(f"   Cooldown de alertas: {monitoring_system.monitoring_config.alert_cooldown} segundos")
    print(f"   Notificaciones por email: {monitoring_system.monitoring_config.email_notifications}")
    
    # Agregar proyecto
    project_id = monitoring_system.add_project(project)
    print(f"\n✅ Proyecto agregado: {project.name} (ID: {project_id})")
    
    # Iniciar monitoreo
    print("\n🚀 Iniciando monitoreo en tiempo real...")
    monitoring_system.start_monitoring()
    
    # Simular monitoreo por 30 segundos
    print("\n📊 Monitoreando métricas por 30 segundos...")
    for i in range(6):  # 6 iteraciones de 5 segundos cada una
        time.sleep(5)
        
        # Obtener estado del proyecto
        status = monitoring_system.get_project_status(project_id)
        
        if "error" not in status:
            print(f"\n⏰ Iteración {i+1} - {datetime.now().strftime('%H:%M:%S')}")
            print(f"   Estado: {status['status']}")
            print(f"   Alertas activas: {status['active_alerts']}")
            
            # Mostrar métricas
            print("   📊 Métricas:")
            for metric_type, metric in status['metrics'].items():
                print(f"      • {metric['name']}: {metric['value']:.1f}{metric['unit']} ({metric['trend']})")
            
            # Mostrar alertas recientes
            recent_alerts = [a for a in status['alerts'] if not a['resolved']]
            if recent_alerts:
                print("   ⚠️ Alertas activas:")
                for alert in recent_alerts[-3:]:  # Últimas 3 alertas
                    level_emoji = {
                        'info': 'ℹ️',
                        'warning': '⚠️',
                        'critical': '🚨',
                        'emergency': '🆘'
                    }
                    emoji = level_emoji.get(alert['level'], '❓')
                    print(f"      {emoji} {alert['title']}")
        else:
            print(f"❌ Error obteniendo estado: {status['error']}")
    
    # Detener monitoreo
    print("\n🛑 Deteniendo monitoreo...")
    monitoring_system.stop_monitoring()
    
    # Mostrar resumen final
    final_status = monitoring_system.get_project_status(project_id)
    if "error" not in final_status:
        print(f"\n📋 Resumen Final:")
        print(f"   Proyecto: {final_status['name']}")
        print(f"   Estado: {final_status['status']}")
        print(f"   Última actualización: {final_status['last_updated']}")
        print(f"   Total de alertas: {len(final_status['alerts'])}")
        print(f"   Alertas activas: {final_status['active_alerts']}")
        
        # Mostrar todas las métricas finales
        print(f"\n📊 Métricas Finales:")
        for metric_type, metric in final_status['metrics'].items():
            print(f"   • {metric['name']}: {metric['value']:.1f}{metric['unit']}")
    
    print("\n🎉 Demo del Real-Time Monitoring System completado!")

if __name__ == "__main__":
    main()








