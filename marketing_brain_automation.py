#!/usr/bin/env python3
"""
🤖 MARKETING BRAIN AUTOMATION
Sistema de Automatización Inteligente para Marketing
Ejecución Automática de Campañas y Optimización Continua
"""

import json
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
import threading
import queue
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))
from advanced_marketing_brain_system import AdvancedMarketingBrain, MarketingConcept
from marketing_brain_analytics import MarketingBrainAnalytics

logger = logging.getLogger(__name__)

@dataclass
class AutomationRule:
    """Regla de automatización"""
    rule_id: str
    name: str
    description: str
    trigger_conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    enabled: bool
    created_at: str
    last_executed: Optional[str] = None

@dataclass
class CampaignExecution:
    """Ejecución de campaña"""
    execution_id: str
    concept_id: str
    status: str  # pending, running, completed, failed
    start_time: str
    end_time: Optional[str] = None
    metrics: Dict[str, Any] = None
    logs: List[str] = None

@dataclass
class AutomationAlert:
    """Alerta de automatización"""
    alert_id: str
    type: str  # info, warning, error, success
    title: str
    message: str
    timestamp: str
    resolved: bool = False

class MarketingBrainAutomation:
    """
    Sistema de Automatización Inteligente para Marketing
    Ejecuta campañas automáticamente y optimiza continuamente
    """
    
    def __init__(self, brain_system: AdvancedMarketingBrain = None, analytics: MarketingBrainAnalytics = None):
        self.brain = brain_system or AdvancedMarketingBrain()
        self.analytics = analytics or MarketingBrainAnalytics(self.brain)
        
        # Estado del sistema
        self.is_running = False
        self.automation_rules = self._load_automation_rules()
        self.active_executions = {}
        self.execution_history = []
        self.alerts = []
        
        # Cola de tareas
        self.task_queue = queue.Queue()
        self.worker_thread = None
        
        # Configuración
        self.config = self._load_config()
        
        # Métricas del sistema
        self.system_metrics = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'active_campaigns': 0,
            'automation_uptime': 0
        }
        
        logger.info("🤖 Marketing Brain Automation initialized successfully")
    
    def _load_automation_rules(self) -> List[AutomationRule]:
        """Cargar reglas de automatización"""
        default_rules = [
            AutomationRule(
                rule_id="RULE_001",
                name="Generación Diaria de Conceptos",
                description="Genera conceptos frescos diariamente basados en tendencias",
                trigger_conditions={
                    "schedule": "daily",
                    "time": "09:00",
                    "min_success_probability": 0.8
                },
                actions=[
                    {
                        "type": "generate_concepts",
                        "params": {
                            "num_concepts": 5,
                            "focus_theme": None,
                            "target_vertical": None
                        }
                    },
                    {
                        "type": "send_notification",
                        "params": {
                            "message": "Conceptos diarios generados exitosamente"
                        }
                    }
                ],
                enabled=True,
                created_at=datetime.now().isoformat()
            ),
            AutomationRule(
                rule_id="RULE_002",
                name="Análisis Semanal de Tendencias",
                description="Analiza tendencias del mercado semanalmente",
                trigger_conditions={
                    "schedule": "weekly",
                    "day": "monday",
                    "time": "10:00"
                },
                actions=[
                    {
                        "type": "analyze_trends",
                        "params": {
                            "category": None,
                            "timeframe": "7_days"
                        }
                    },
                    {
                        "type": "generate_report",
                        "params": {
                            "report_type": "trend_analysis"
                        }
                    }
                ],
                enabled=True,
                created_at=datetime.now().isoformat()
            ),
            AutomationRule(
                rule_id="RULE_003",
                name="Optimización de Campañas Activas",
                description="Optimiza campañas activas basado en métricas",
                trigger_conditions={
                    "schedule": "interval",
                    "interval_minutes": 30,
                    "min_campaigns": 1
                },
                actions=[
                    {
                        "type": "optimize_campaigns",
                        "params": {
                            "optimization_type": "performance"
                        }
                    }
                ],
                enabled=True,
                created_at=datetime.now().isoformat()
            ),
            AutomationRule(
                rule_id="RULE_004",
                name="Alerta de Rendimiento Bajo",
                description="Envía alerta cuando el rendimiento es bajo",
                trigger_conditions={
                    "type": "metric_threshold",
                    "metric": "conversion_rate",
                    "threshold": 3.0,
                    "comparison": "less_than"
                },
                actions=[
                    {
                        "type": "send_alert",
                        "params": {
                            "alert_type": "warning",
                            "message": "Rendimiento de conversión por debajo del umbral"
                        }
                    }
                ],
                enabled=True,
                created_at=datetime.now().isoformat()
            )
        ]
        
        return default_rules
    
    def _load_config(self) -> Dict[str, Any]:
        """Cargar configuración del sistema"""
        return {
            'email_notifications': {
                'enabled': True,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'recipients': []
            },
            'execution_settings': {
                'max_concurrent_executions': 5,
                'execution_timeout_minutes': 60,
                'retry_attempts': 3,
                'retry_delay_minutes': 5
            },
            'monitoring': {
                'metrics_collection_interval': 300,  # 5 minutos
                'alert_thresholds': {
                    'success_rate': 0.8,
                    'execution_time': 30,
                    'error_rate': 0.1
                }
            }
        }
    
    def start_automation(self):
        """Iniciar el sistema de automatización"""
        if self.is_running:
            logger.warning("Sistema de automatización ya está ejecutándose")
            return
        
        self.is_running = True
        self.start_time = datetime.now()
        
        # Iniciar worker thread
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        
        # Programar reglas de automatización
        self._schedule_automation_rules()
        
        # Iniciar monitoreo
        self._start_monitoring()
        
        logger.info("🤖 Sistema de automatización iniciado")
        self._add_alert("info", "Sistema Iniciado", "El sistema de automatización ha sido iniciado exitosamente")
    
    def stop_automation(self):
        """Detener el sistema de automatización"""
        if not self.is_running:
            logger.warning("Sistema de automatización no está ejecutándose")
            return
        
        self.is_running = False
        
        # Limpiar programaciones
        schedule.clear()
        
        # Esperar a que termine el worker thread
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
        
        logger.info("🤖 Sistema de automatización detenido")
        self._add_alert("info", "Sistema Detenido", "El sistema de automatización ha sido detenido")
    
    def _worker_loop(self):
        """Loop principal del worker thread"""
        while self.is_running:
            try:
                # Procesar tareas de la cola
                if not self.task_queue.empty():
                    task = self.task_queue.get(timeout=1)
                    self._execute_task(task)
                    self.task_queue.task_done()
                
                # Ejecutar programaciones
                schedule.run_pending()
                
                # Actualizar métricas del sistema
                self._update_system_metrics()
                
                time.sleep(1)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error en worker loop: {e}")
                self._add_alert("error", "Error del Sistema", f"Error en el worker loop: {str(e)}")
                time.sleep(5)
    
    def _schedule_automation_rules(self):
        """Programar reglas de automatización"""
        for rule in self.automation_rules:
            if not rule.enabled:
                continue
            
            conditions = rule.trigger_conditions
            
            if conditions.get('schedule') == 'daily':
                time_str = conditions.get('time', '09:00')
                schedule.every().day.at(time_str).do(
                    self._execute_rule, rule.rule_id
                ).tag(rule.rule_id)
            
            elif conditions.get('schedule') == 'weekly':
                day = conditions.get('day', 'monday')
                time_str = conditions.get('time', '10:00')
                getattr(schedule.every(), day).at(time_str).do(
                    self._execute_rule, rule.rule_id
                ).tag(rule.rule_id)
            
            elif conditions.get('schedule') == 'interval':
                interval = conditions.get('interval_minutes', 30)
                schedule.every(interval).minutes.do(
                    self._execute_rule, rule.rule_id
                ).tag(rule.rule_id)
        
        logger.info(f"📅 Programadas {len([r for r in self.automation_rules if r.enabled])} reglas de automatización")
    
    def _execute_rule(self, rule_id: str):
        """Ejecutar una regla de automatización"""
        rule = next((r for r in self.automation_rules if r.rule_id == rule_id), None)
        if not rule:
            logger.error(f"Regla {rule_id} no encontrada")
            return
        
        logger.info(f"🔄 Ejecutando regla: {rule.name}")
        
        try:
            # Verificar condiciones de trigger
            if not self._check_trigger_conditions(rule):
                logger.info(f"Condiciones de trigger no cumplidas para {rule.name}")
                return
            
            # Ejecutar acciones
            for action in rule.actions:
                self._execute_action(action)
            
            # Actualizar última ejecución
            rule.last_executed = datetime.now().isoformat()
            
            logger.info(f"✅ Regla {rule.name} ejecutada exitosamente")
            self._add_alert("success", "Regla Ejecutada", f"Regla '{rule.name}' ejecutada exitosamente")
            
        except Exception as e:
            logger.error(f"Error ejecutando regla {rule.name}: {e}")
            self._add_alert("error", "Error de Regla", f"Error ejecutando regla '{rule.name}': {str(e)}")
    
    def _check_trigger_conditions(self, rule: AutomationRule) -> bool:
        """Verificar condiciones de trigger de una regla"""
        conditions = rule.trigger_conditions
        
        # Verificar condiciones específicas por tipo
        if conditions.get('type') == 'metric_threshold':
            return self._check_metric_threshold(conditions)
        
        if conditions.get('min_campaigns'):
            return len(self.active_executions) >= conditions['min_campaigns']
        
        return True
    
    def _check_metric_threshold(self, conditions: Dict[str, Any]) -> bool:
        """Verificar umbral de métrica"""
        metric = conditions.get('metric')
        threshold = conditions.get('threshold')
        comparison = conditions.get('comparison', 'greater_than')
        
        # Obtener valor actual de la métrica
        current_value = self._get_current_metric_value(metric)
        
        if comparison == 'greater_than':
            return current_value > threshold
        elif comparison == 'less_than':
            return current_value < threshold
        elif comparison == 'equals':
            return current_value == threshold
        
        return False
    
    def _get_current_metric_value(self, metric: str) -> float:
        """Obtener valor actual de una métrica"""
        # Implementación simplificada - en producción se obtendría de métricas reales
        metric_values = {
            'conversion_rate': 5.2,
            'engagement_rate': 7.8,
            'click_through_rate': 3.1,
            'cost_per_acquisition': 42.5,
            'return_on_ad_spend': 4.8
        }
        
        return metric_values.get(metric, 0.0)
    
    def _execute_action(self, action: Dict[str, Any]):
        """Ejecutar una acción específica"""
        action_type = action.get('type')
        params = action.get('params', {})
        
        if action_type == 'generate_concepts':
            self._action_generate_concepts(params)
        elif action_type == 'analyze_trends':
            self._action_analyze_trends(params)
        elif action_type == 'optimize_campaigns':
            self._action_optimize_campaigns(params)
        elif action_type == 'send_notification':
            self._action_send_notification(params)
        elif action_type == 'send_alert':
            self._action_send_alert(params)
        elif action_type == 'generate_report':
            self._action_generate_report(params)
        else:
            logger.warning(f"Tipo de acción no reconocido: {action_type}")
    
    def _action_generate_concepts(self, params: Dict[str, Any]):
        """Acción: Generar conceptos"""
        num_concepts = params.get('num_concepts', 5)
        focus_theme = params.get('focus_theme')
        target_vertical = params.get('target_vertical')
        min_success_probability = params.get('min_success_probability', 0.8)
        
        concepts = self.brain.generate_fresh_concepts(
            num_concepts=num_concepts,
            focus_theme=focus_theme,
            target_vertical=target_vertical,
            min_success_probability=min_success_probability
        )
        
        # Guardar conceptos generados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"auto_generated_concepts_{timestamp}.json"
        self.brain.export_concepts_to_json(concepts, filename)
        
        logger.info(f"📝 Generados {len(concepts)} conceptos automáticamente")
    
    def _action_analyze_trends(self, params: Dict[str, Any]):
        """Acción: Analizar tendencias"""
        category = params.get('category')
        timeframe = params.get('timeframe', '7_days')
        
        trends = self.analytics.analyze_market_trends(category=category)
        
        # Guardar análisis de tendencias
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"auto_trend_analysis_{timestamp}.json"
        
        trends_data = [self.analytics._trend_to_dict(trend) for trend in trends]
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(trends_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📈 Análisis de tendencias completado: {len(trends)} tendencias identificadas")
    
    def _action_optimize_campaigns(self, params: Dict[str, Any]):
        """Acción: Optimizar campañas activas"""
        optimization_type = params.get('optimization_type', 'performance')
        
        # Obtener campañas activas
        active_campaigns = [exec for exec in self.active_executions.values() 
                          if exec.status == 'running']
        
        if not active_campaigns:
            logger.info("No hay campañas activas para optimizar")
            return
        
        # Aplicar optimizaciones
        for execution in active_campaigns:
            self._optimize_campaign_execution(execution, optimization_type)
        
        logger.info(f"🔧 Optimizadas {len(active_campaigns)} campañas activas")
    
    def _optimize_campaign_execution(self, execution: CampaignExecution, optimization_type: str):
        """Optimizar una ejecución de campaña específica"""
        # Implementación simplificada de optimización
        if optimization_type == 'performance':
            # Simular optimización de rendimiento
            if execution.metrics:
                execution.metrics['optimization_applied'] = True
                execution.metrics['optimization_timestamp'] = datetime.now().isoformat()
        
        logger.info(f"🔧 Campaña {execution.execution_id} optimizada")
    
    def _action_send_notification(self, params: Dict[str, Any]):
        """Acción: Enviar notificación"""
        message = params.get('message', 'Notificación del sistema')
        
        # Enviar notificación por email si está configurado
        if self.config['email_notifications']['enabled']:
            self._send_email_notification(message)
        
        # Agregar alerta al sistema
        self._add_alert("info", "Notificación", message)
        
        logger.info(f"📧 Notificación enviada: {message}")
    
    def _action_send_alert(self, params: Dict[str, Any]):
        """Acción: Enviar alerta"""
        alert_type = params.get('alert_type', 'warning')
        message = params.get('message', 'Alerta del sistema')
        
        self._add_alert(alert_type, "Alerta Automática", message)
        
        logger.info(f"🚨 Alerta enviada: {message}")
    
    def _action_generate_report(self, params: Dict[str, Any]):
        """Acción: Generar reporte"""
        report_type = params.get('report_type', 'general')
        
        if report_type == 'trend_analysis':
            report = self.analytics.generate_market_opportunity_report()
            filename = self.analytics.export_analytics_report(report)
        else:
            # Generar reporte general del sistema
            report = self._generate_system_report()
            filename = self._export_system_report(report)
        
        logger.info(f"📊 Reporte {report_type} generado: {filename}")
    
    def _send_email_notification(self, message: str):
        """Enviar notificación por email"""
        email_config = self.config['email_notifications']
        
        if not email_config.get('username') or not email_config.get('password'):
            logger.warning("Configuración de email incompleta")
            return
        
        try:
            # Crear mensaje
            msg = MimeMultipart()
            msg['From'] = email_config['username']
            msg['To'] = ', '.join(email_config['recipients'])
            msg['Subject'] = "Marketing Brain Automation - Notificación"
            
            body = f"""
            <h2>Marketing Brain Automation</h2>
            <p>{message}</p>
            <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Sistema:</strong> Advanced Marketing Brain</p>
            """
            
            msg.attach(MimeText(body, 'html'))
            
            # Enviar email
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info("📧 Email enviado exitosamente")
            
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
    
    def _add_alert(self, alert_type: str, title: str, message: str):
        """Agregar alerta al sistema"""
        alert = AutomationAlert(
            alert_id=f"ALERT_{len(self.alerts) + 1:04d}",
            type=alert_type,
            title=title,
            message=message,
            timestamp=datetime.now().isoformat()
        )
        
        self.alerts.append(alert)
        
        # Mantener solo las últimas 100 alertas
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def _start_monitoring(self):
        """Iniciar monitoreo del sistema"""
        def monitor_loop():
            while self.is_running:
                try:
                    # Verificar métricas del sistema
                    self._check_system_health()
                    
                    # Limpiar ejecuciones completadas
                    self._cleanup_completed_executions()
                    
                    time.sleep(self.config['monitoring']['metrics_collection_interval'])
                    
                except Exception as e:
                    logger.error(f"Error en monitoreo: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
        logger.info("📊 Monitoreo del sistema iniciado")
    
    def _check_system_health(self):
        """Verificar salud del sistema"""
        thresholds = self.config['monitoring']['alert_thresholds']
        
        # Verificar tasa de éxito
        if self.system_metrics['total_executions'] > 0:
            success_rate = self.system_metrics['successful_executions'] / self.system_metrics['total_executions']
            if success_rate < thresholds['success_rate']:
                self._add_alert("warning", "Baja Tasa de Éxito", 
                              f"Tasa de éxito: {success_rate:.1%} (umbral: {thresholds['success_rate']:.1%})")
        
        # Verificar tiempo de ejecución
        if self.system_metrics['active_campaigns'] > 0:
            avg_execution_time = self._calculate_average_execution_time()
            if avg_execution_time > thresholds['execution_time']:
                self._add_alert("warning", "Tiempo de Ejecución Alto", 
                              f"Tiempo promedio: {avg_execution_time:.1f} min (umbral: {thresholds['execution_time']} min)")
    
    def _calculate_average_execution_time(self) -> float:
        """Calcular tiempo promedio de ejecución"""
        if not self.execution_history:
            return 0.0
        
        total_time = 0
        count = 0
        
        for execution in self.execution_history:
            if execution.end_time:
                start = datetime.fromisoformat(execution.start_time)
                end = datetime.fromisoformat(execution.end_time)
                total_time += (end - start).total_seconds() / 60
                count += 1
        
        return total_time / count if count > 0 else 0.0
    
    def _cleanup_completed_executions(self):
        """Limpiar ejecuciones completadas"""
        completed_executions = []
        
        for exec_id, execution in self.active_executions.items():
            if execution.status in ['completed', 'failed']:
                completed_executions.append(exec_id)
        
        for exec_id in completed_executions:
            execution = self.active_executions.pop(exec_id)
            self.execution_history.append(execution)
        
        if completed_executions:
            logger.info(f"🧹 Limpiadas {len(completed_executions)} ejecuciones completadas")
    
    def _update_system_metrics(self):
        """Actualizar métricas del sistema"""
        if hasattr(self, 'start_time'):
            uptime = (datetime.now() - self.start_time).total_seconds() / 3600
            self.system_metrics['automation_uptime'] = uptime
        
        self.system_metrics['active_campaigns'] = len(self.active_executions)
    
    def _generate_system_report(self) -> Dict[str, Any]:
        """Generar reporte del sistema"""
        return {
            'system_status': {
                'is_running': self.is_running,
                'uptime_hours': self.system_metrics['automation_uptime'],
                'active_campaigns': self.system_metrics['active_campaigns']
            },
            'execution_metrics': {
                'total_executions': self.system_metrics['total_executions'],
                'successful_executions': self.system_metrics['successful_executions'],
                'failed_executions': self.system_metrics['failed_executions'],
                'success_rate': (self.system_metrics['successful_executions'] / 
                               max(1, self.system_metrics['total_executions']))
            },
            'automation_rules': [
                {
                    'id': rule.rule_id,
                    'name': rule.name,
                    'enabled': rule.enabled,
                    'last_executed': rule.last_executed
                }
                for rule in self.automation_rules
            ],
            'recent_alerts': [
                {
                    'id': alert.alert_id,
                    'type': alert.type,
                    'title': alert.title,
                    'message': alert.message,
                    'timestamp': alert.timestamp,
                    'resolved': alert.resolved
                }
                for alert in self.alerts[-10:]  # Últimas 10 alertas
            ],
            'generated_at': datetime.now().isoformat()
        }
    
    def _export_system_report(self, report: Dict[str, Any]) -> str:
        """Exportar reporte del sistema"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"system_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def execute_concept_automatically(self, concept: MarketingConcept) -> str:
        """Ejecutar un concepto automáticamente"""
        execution_id = f"EXEC_{len(self.active_executions) + 1:04d}"
        
        execution = CampaignExecution(
            execution_id=execution_id,
            concept_id=concept.concept_id,
            status='pending',
            start_time=datetime.now().isoformat(),
            logs=[]
        )
        
        # Agregar a ejecuciones activas
        self.active_executions[execution_id] = execution
        
        # Agregar tarea a la cola
        task = {
            'type': 'execute_campaign',
            'execution_id': execution_id,
            'concept': concept
        }
        self.task_queue.put(task)
        
        logger.info(f"🚀 Concepto {concept.concept_id} programado para ejecución automática")
        return execution_id
    
    def _execute_task(self, task: Dict[str, Any]):
        """Ejecutar una tarea de la cola"""
        task_type = task.get('type')
        
        if task_type == 'execute_campaign':
            self._execute_campaign_task(task)
        else:
            logger.warning(f"Tipo de tarea no reconocido: {task_type}")
    
    def _execute_campaign_task(self, task: Dict[str, Any]):
        """Ejecutar tarea de campaña"""
        execution_id = task['execution_id']
        concept = task['concept']
        
        execution = self.active_executions.get(execution_id)
        if not execution:
            logger.error(f"Ejecución {execution_id} no encontrada")
            return
        
        try:
            # Marcar como ejecutándose
            execution.status = 'running'
            execution.logs.append(f"Iniciando ejecución de {concept.name}")
            
            # Simular ejecución de campaña
            self._simulate_campaign_execution(execution, concept)
            
            # Marcar como completada
            execution.status = 'completed'
            execution.end_time = datetime.now().isoformat()
            execution.logs.append("Ejecución completada exitosamente")
            
            # Actualizar métricas
            self.system_metrics['total_executions'] += 1
            self.system_metrics['successful_executions'] += 1
            
            logger.info(f"✅ Campaña {execution_id} ejecutada exitosamente")
            
        except Exception as e:
            # Marcar como fallida
            execution.status = 'failed'
            execution.end_time = datetime.now().isoformat()
            execution.logs.append(f"Error en ejecución: {str(e)}")
            
            # Actualizar métricas
            self.system_metrics['total_executions'] += 1
            self.system_metrics['failed_executions'] += 1
            
            logger.error(f"❌ Error ejecutando campaña {execution_id}: {e}")
            self._add_alert("error", "Error de Ejecución", f"Error ejecutando campaña {execution_id}: {str(e)}")
    
    def _simulate_campaign_execution(self, execution: CampaignExecution, concept: MarketingConcept):
        """Simular ejecución de campaña"""
        # Simular tiempo de ejecución
        time.sleep(2)  # En producción sería el tiempo real de ejecución
        
        # Simular métricas generadas
        execution.metrics = {
            'impressions': np.random.randint(10000, 100000),
            'clicks': np.random.randint(500, 5000),
            'conversions': np.random.randint(50, 500),
            'cost': concept.estimated_budget['amount'] * np.random.uniform(0.8, 1.2),
            'execution_time_minutes': np.random.randint(5, 30)
        }
        
        execution.logs.append(f"Métricas generadas: {execution.metrics}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema"""
        return {
            'is_running': self.is_running,
            'automation_rules': len([r for r in self.automation_rules if r.enabled]),
            'active_executions': len(self.active_executions),
            'total_executions': self.system_metrics['total_executions'],
            'system_metrics': self.system_metrics,
            'recent_alerts': [
                {
                    'type': alert.type,
                    'title': alert.title,
                    'message': alert.message,
                    'timestamp': alert.timestamp
                }
                for alert in self.alerts[-5:]
            ]
        }
    
    def add_automation_rule(self, rule: AutomationRule):
        """Agregar nueva regla de automatización"""
        self.automation_rules.append(rule)
        
        # Reprogramar si el sistema está ejecutándose
        if self.is_running and rule.enabled:
            self._schedule_automation_rules()
        
        logger.info(f"➕ Regla de automatización agregada: {rule.name}")
    
    def update_automation_rule(self, rule_id: str, updates: Dict[str, Any]):
        """Actualizar regla de automatización"""
        rule = next((r for r in self.automation_rules if r.rule_id == rule_id), None)
        if not rule:
            logger.error(f"Regla {rule_id} no encontrada")
            return
        
        # Actualizar campos
        for key, value in updates.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        # Reprogramar si el sistema está ejecutándose
        if self.is_running:
            schedule.clear()
            self._schedule_automation_rules()
        
        logger.info(f"✏️ Regla {rule_id} actualizada")
    
    def export_automation_config(self, filename: str = None) -> str:
        """Exportar configuración de automatización"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"automation_config_{timestamp}.json"
        
        config_data = {
            'automation_rules': [asdict(rule) for rule in self.automation_rules],
            'system_config': self.config,
            'exported_at': datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Configuración de automatización exportada a {filename}")
        return filename


def main():
    """Función principal para demostrar el sistema de automatización"""
    print("🤖 MARKETING BRAIN AUTOMATION")
    print("=" * 50)
    
    # Inicializar sistemas
    brain = AdvancedMarketingBrain()
    analytics = MarketingBrainAnalytics(brain)
    automation = MarketingBrainAutomation(brain, analytics)
    
    # Mostrar estado inicial
    print(f"\n📊 ESTADO INICIAL DEL SISTEMA:")
    status = automation.get_system_status()
    print(f"   • Sistema ejecutándose: {status['is_running']}")
    print(f"   • Reglas de automatización: {status['automation_rules']}")
    print(f"   • Ejecuciones activas: {status['active_executions']}")
    
    # Iniciar automatización
    print(f"\n🚀 INICIANDO SISTEMA DE AUTOMATIZACIÓN...")
    automation.start_automation()
    
    # Generar concepto de prueba
    print(f"\n🎨 GENERANDO CONCEPTO DE PRUEBA...")
    concepts = brain.generate_fresh_concepts(num_concepts=1, min_success_probability=0.8)
    test_concept = concepts[0]
    
    print(f"   • Concepto: {test_concept.name}")
    print(f"   • Tecnología: {test_concept.technology}")
    print(f"   • Canal: {test_concept.channel}")
    print(f"   • Probabilidad de éxito: {test_concept.success_probability:.1%}")
    
    # Ejecutar concepto automáticamente
    print(f"\n⚡ EJECUTANDO CONCEPTO AUTOMÁTICAMENTE...")
    execution_id = automation.execute_concept_automatically(test_concept)
    print(f"   • ID de ejecución: {execution_id}")
    
    # Esperar un poco para ver la ejecución
    print(f"\n⏳ Esperando ejecución...")
    time.sleep(5)
    
    # Mostrar estado actualizado
    print(f"\n📊 ESTADO ACTUALIZADO:")
    status = automation.get_system_status()
    print(f"   • Ejecuciones totales: {status['total_executions']}")
    print(f"   • Ejecuciones exitosas: {status['system_metrics']['successful_executions']}")
    print(f"   • Ejecuciones fallidas: {status['system_metrics']['failed_executions']}")
    print(f"   • Campañas activas: {status['active_campaigns']}")
    
    # Mostrar alertas recientes
    if status['recent_alerts']:
        print(f"\n🚨 ALERTAS RECIENTES:")
        for alert in status['recent_alerts']:
            print(f"   • [{alert['type'].upper()}] {alert['title']}: {alert['message']}")
    
    # Exportar configuración
    print(f"\n💾 EXPORTANDO CONFIGURACIÓN...")
    config_file = automation.export_automation_config()
    print(f"   • Configuración exportada a: {config_file}")
    
    # Detener sistema
    print(f"\n🛑 DETENIENDO SISTEMA...")
    automation.stop_automation()
    
    print(f"\n✅ DEMOSTRACIÓN COMPLETADA")
    print(f"🎉 El sistema de automatización ha ejecutado exitosamente")
    print(f"   un concepto de marketing y demostrado sus capacidades")
    print(f"   de automatización inteligente.")


if __name__ == "__main__":
    main()








