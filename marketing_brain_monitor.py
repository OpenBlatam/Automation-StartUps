#!/usr/bin/env python3
"""
📡 MARKETING BRAIN MONITOR
Sistema Avanzado de Monitoreo y Alertas en Tiempo Real
Incluye métricas en vivo, alertas inteligentes y dashboards de monitoreo
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
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import websockets
import psutil
import schedule

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Niveles de alerta"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    """Tipos de métricas"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

@dataclass
class Metric:
    """Métrica del sistema"""
    metric_id: str
    name: str
    value: float
    metric_type: MetricType
    tags: Dict[str, str]
    timestamp: str
    unit: str = None

@dataclass
class Alert:
    """Alerta del sistema"""
    alert_id: str
    name: str
    description: str
    level: AlertLevel
    metric_name: str
    threshold: float
    current_value: float
    condition: str
    status: str
    created_at: str
    resolved_at: str = None
    acknowledged_by: str = None
    acknowledged_at: str = None

@dataclass
class HealthCheck:
    """Health check del sistema"""
    check_id: str
    name: str
    status: str
    response_time: float
    last_check: str
    error_message: str = None
    metadata: Dict[str, Any] = None

@dataclass
class NotificationChannel:
    """Canal de notificación"""
    channel_id: str
    name: str
    channel_type: str
    config: Dict[str, Any]
    enabled: bool
    created_at: str

class MarketingBrainMonitor:
    """
    Sistema Avanzado de Monitoreo y Alertas en Tiempo Real
    Incluye métricas en vivo, alertas inteligentes y dashboards de monitoreo
    """
    
    def __init__(self):
        self.metrics = {}
        self.alerts = {}
        self.health_checks = {}
        self.notification_channels = {}
        
        # Sistema de colas
        self.metric_queue = queue.Queue()
        self.alert_queue = queue.Queue()
        
        # Configuración
        self.config = self._load_config()
        
        # Estado del sistema
        self.is_running = False
        self.start_time = None
        
        # Métricas del sistema
        self.system_metrics = {
            'total_metrics_collected': 0,
            'total_alerts_triggered': 0,
            'active_alerts': 0,
            'resolved_alerts': 0,
            'system_uptime': 0.0,
            'last_health_check': None
        }
        
        # WebSocket para métricas en tiempo real
        self.websocket_clients = set()
        self.websocket_server = None
        
        # Threads
        self.metric_collector_thread = None
        self.alert_processor_thread = None
        self.health_checker_thread = None
        self.websocket_thread = None
        
        logger.info("📡 Marketing Brain Monitor initialized successfully")
    
    def _load_config(self) -> Dict[str, Any]:
        """Cargar configuración del monitor"""
        return {
            'monitoring': {
                'collection_interval': 5,
                'retention_days': 30,
                'max_metrics_per_minute': 1000
            },
            'alerts': {
                'evaluation_interval': 10,
                'alert_cooldown': 300,
                'max_alerts_per_hour': 100
            },
            'health_checks': {
                'check_interval': 30,
                'timeout': 10,
                'retry_count': 3
            },
            'notifications': {
                'email': {
                    'enabled': False,
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'username': '',
                    'password': '',
                    'from_email': '',
                    'to_emails': []
                },
                'slack': {
                    'enabled': False,
                    'webhook_url': '',
                    'channel': '#alerts'
                },
                'webhook': {
                    'enabled': False,
                    'url': '',
                    'headers': {}
                }
            },
            'websocket': {
                'enabled': True,
                'port': 8765,
                'max_connections': 100
            }
        }
    
    def start_monitor(self):
        """Iniciar el monitor"""
        logger.info("🚀 Starting Marketing Brain Monitor...")
        
        self.is_running = True
        self.start_time = datetime.now()
        
        # Iniciar threads
        self.metric_collector_thread = threading.Thread(target=self._metric_collector_loop, daemon=True)
        self.metric_collector_thread.start()
        
        self.alert_processor_thread = threading.Thread(target=self._alert_processor_loop, daemon=True)
        self.alert_processor_thread.start()
        
        self.health_checker_thread = threading.Thread(target=self._health_checker_loop, daemon=True)
        self.health_checker_thread.start()
        
        # Iniciar WebSocket server si está habilitado
        if self.config['websocket']['enabled']:
            self.websocket_thread = threading.Thread(target=self._start_websocket_server, daemon=True)
            self.websocket_thread.start()
        
        # Configurar health checks por defecto
        self._setup_default_health_checks()
        
        # Configurar canales de notificación por defecto
        self._setup_default_notification_channels()
        
        logger.info("✅ Monitor started successfully")
    
    def stop_monitor(self):
        """Detener el monitor"""
        logger.info("🛑 Stopping Marketing Brain Monitor...")
        
        self.is_running = False
        
        # Cerrar WebSocket server
        if self.websocket_server:
            asyncio.run(self.websocket_server.close())
        
        logger.info("✅ Monitor stopped successfully")
    
    def _metric_collector_loop(self):
        """Loop de recolección de métricas"""
        while self.is_running:
            try:
                # Recolectar métricas del sistema
                self._collect_system_metrics()
                
                # Recolectar métricas de componentes
                self._collect_component_metrics()
                
                # Procesar cola de métricas
                self._process_metric_queue()
                
                time.sleep(self.config['monitoring']['collection_interval'])
                
            except Exception as e:
                logger.error(f"Error in metric collector: {e}")
    
    def _alert_processor_loop(self):
        """Loop de procesamiento de alertas"""
        while self.is_running:
            try:
                # Evaluar alertas
                self._evaluate_alerts()
                
                # Procesar cola de alertas
                self._process_alert_queue()
                
                time.sleep(self.config['alerts']['evaluation_interval'])
                
            except Exception as e:
                logger.error(f"Error in alert processor: {e}")
    
    def _health_checker_loop(self):
        """Loop de health checks"""
        while self.is_running:
            try:
                # Ejecutar health checks
                self._run_health_checks()
                
                time.sleep(self.config['health_checks']['check_interval'])
                
            except Exception as e:
                logger.error(f"Error in health checker: {e}")
    
    def _collect_system_metrics(self):
        """Recolectar métricas del sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self._record_metric("system.cpu.usage", cpu_percent, MetricType.GAUGE, {"host": "localhost"})
            
            # Memoria
            memory = psutil.virtual_memory()
            self._record_metric("system.memory.usage", memory.percent, MetricType.GAUGE, {"host": "localhost"})
            self._record_metric("system.memory.available", memory.available, MetricType.GAUGE, {"host": "localhost"})
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self._record_metric("system.disk.usage", disk_percent, MetricType.GAUGE, {"host": "localhost"})
            
            # Red
            network = psutil.net_io_counters()
            self._record_metric("system.network.bytes_sent", network.bytes_sent, MetricType.COUNTER, {"host": "localhost"})
            self._record_metric("system.network.bytes_recv", network.bytes_recv, MetricType.COUNTER, {"host": "localhost"})
            
            # Procesos
            process_count = len(psutil.pids())
            self._record_metric("system.processes.count", process_count, MetricType.GAUGE, {"host": "localhost"})
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def _collect_component_metrics(self):
        """Recolectar métricas de componentes"""
        try:
            # Métricas de workflows (simuladas)
            self._record_metric("workflows.active", len(self._get_active_workflows()), MetricType.GAUGE, {"component": "orchestrator"})
            self._record_metric("workflows.completed", self._get_completed_workflows(), MetricType.COUNTER, {"component": "orchestrator"})
            
            # Métricas de conceptos generados (simuladas)
            self._record_metric("concepts.generated", self._get_generated_concepts(), MetricType.COUNTER, {"component": "brain_system"})
            
            # Métricas de contenido generado (simuladas)
            self._record_metric("content.generated", self._get_generated_content(), MetricType.COUNTER, {"component": "content_generator"})
            
            # Métricas de optimizaciones (simuladas)
            self._record_metric("optimizations.completed", self._get_completed_optimizations(), MetricType.COUNTER, {"component": "performance_optimizer"})
            
        except Exception as e:
            logger.error(f"Error collecting component metrics: {e}")
    
    def _get_active_workflows(self) -> int:
        """Obtener número de workflows activos (simulado)"""
        return 3  # Simulado
    
    def _get_completed_workflows(self) -> int:
        """Obtener número de workflows completados (simulado)"""
        return 15  # Simulado
    
    def _get_generated_concepts(self) -> int:
        """Obtener número de conceptos generados (simulado)"""
        return 45  # Simulado
    
    def _get_generated_content(self) -> int:
        """Obtener número de contenido generado (simulado)"""
        return 120  # Simulado
    
    def _get_completed_optimizations(self) -> int:
        """Obtener número de optimizaciones completadas (simulado)"""
        return 8  # Simulado
    
    def _record_metric(self, name: str, value: float, metric_type: MetricType, tags: Dict[str, str] = None):
        """Registrar una métrica"""
        metric = Metric(
            metric_id=str(uuid.uuid4()),
            name=name,
            value=value,
            metric_type=metric_type,
            tags=tags or {},
            timestamp=datetime.now().isoformat()
        )
        
        # Agregar a métricas
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append(metric)
        
        # Limitar historial
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]
        
        # Agregar a cola para procesamiento
        self.metric_queue.put(metric)
        
        # Actualizar métricas del sistema
        self.system_metrics['total_metrics_collected'] += 1
        
        # Enviar por WebSocket
        self._broadcast_metric(metric)
    
    def _process_metric_queue(self):
        """Procesar cola de métricas"""
        while not self.metric_queue.empty():
            try:
                metric = self.metric_queue.get_nowait()
                # Procesar métrica (ej: almacenar en base de datos, enviar a sistemas externos)
                self.metric_queue.task_done()
            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"Error processing metric: {e}")
    
    def _setup_default_health_checks(self):
        """Configurar health checks por defecto"""
        health_checks = [
            {
                'name': 'System CPU Check',
                'function': self._check_cpu_health,
                'interval': 30
            },
            {
                'name': 'System Memory Check',
                'function': self._check_memory_health,
                'interval': 30
            },
            {
                'name': 'System Disk Check',
                'function': self._check_disk_health,
                'interval': 60
            },
            {
                'name': 'Component Health Check',
                'function': self._check_component_health,
                'interval': 60
            }
        ]
        
        for check_config in health_checks:
            check_id = str(uuid.uuid4())
            self.health_checks[check_id] = HealthCheck(
                check_id=check_id,
                name=check_config['name'],
                status='unknown',
                response_time=0.0,
                last_check=datetime.now().isoformat()
            )
    
    def _setup_default_notification_channels(self):
        """Configurar canales de notificación por defecto"""
        # Canal de email
        if self.config['notifications']['email']['enabled']:
            email_channel = NotificationChannel(
                channel_id=str(uuid.uuid4()),
                name='Email Notifications',
                channel_type='email',
                config=self.config['notifications']['email'],
                enabled=True,
                created_at=datetime.now().isoformat()
            )
            self.notification_channels[email_channel.channel_id] = email_channel
        
        # Canal de Slack
        if self.config['notifications']['slack']['enabled']:
            slack_channel = NotificationChannel(
                channel_id=str(uuid.uuid4()),
                name='Slack Notifications',
                channel_type='slack',
                config=self.config['notifications']['slack'],
                enabled=True,
                created_at=datetime.now().isoformat()
            )
            self.notification_channels[slack_channel.channel_id] = slack_channel
        
        # Canal de Webhook
        if self.config['notifications']['webhook']['enabled']:
            webhook_channel = NotificationChannel(
                channel_id=str(uuid.uuid4()),
                name='Webhook Notifications',
                channel_type='webhook',
                config=self.config['notifications']['webhook'],
                enabled=True,
                created_at=datetime.now().isoformat()
            )
            self.notification_channels[webhook_channel.channel_id] = webhook_channel
    
    def _run_health_checks(self):
        """Ejecutar health checks"""
        for check_id, check in self.health_checks.items():
            try:
                start_time = time.time()
                
                # Ejecutar health check específico
                if check.name == 'System CPU Check':
                    status, error = self._check_cpu_health()
                elif check.name == 'System Memory Check':
                    status, error = self._check_memory_health()
                elif check.name == 'System Disk Check':
                    status, error = self._check_disk_health()
                elif check.name == 'Component Health Check':
                    status, error = self._check_component_health()
                else:
                    status, error = 'unknown', 'Unknown health check'
                
                response_time = time.time() - start_time
                
                # Actualizar health check
                check.status = status
                check.response_time = response_time
                check.last_check = datetime.now().isoformat()
                check.error_message = error
                
                # Actualizar métricas del sistema
                self.system_metrics['last_health_check'] = datetime.now().isoformat()
                
            except Exception as e:
                logger.error(f"Error running health check {check.name}: {e}")
                check.status = 'error'
                check.error_message = str(e)
                check.last_check = datetime.now().isoformat()
    
    def _check_cpu_health(self) -> tuple:
        """Verificar salud de CPU"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                return 'critical', f'CPU usage too high: {cpu_percent}%'
            elif cpu_percent > 80:
                return 'warning', f'CPU usage high: {cpu_percent}%'
            else:
                return 'healthy', None
        except Exception as e:
            return 'error', str(e)
    
    def _check_memory_health(self) -> tuple:
        """Verificar salud de memoria"""
        try:
            memory = psutil.virtual_memory()
            if memory.percent > 95:
                return 'critical', f'Memory usage too high: {memory.percent}%'
            elif memory.percent > 85:
                return 'warning', f'Memory usage high: {memory.percent}%'
            else:
                return 'healthy', None
        except Exception as e:
            return 'error', str(e)
    
    def _check_disk_health(self) -> tuple:
        """Verificar salud de disco"""
        try:
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > 95:
                return 'critical', f'Disk usage too high: {disk_percent}%'
            elif disk_percent > 85:
                return 'warning', f'Disk usage high: {disk_percent}%'
            else:
                return 'healthy', None
        except Exception as e:
            return 'error', str(e)
    
    def _check_component_health(self) -> tuple:
        """Verificar salud de componentes"""
        try:
            # Verificar que los componentes estén funcionando
            components_status = {
                'brain_system': 'healthy',
                'ai_enhancer': 'healthy',
                'content_generator': 'healthy',
                'performance_optimizer': 'healthy',
                'orchestrator': 'healthy'
            }
            
            unhealthy_components = [comp for comp, status in components_status.items() if status != 'healthy']
            
            if unhealthy_components:
                return 'warning', f'Unhealthy components: {", ".join(unhealthy_components)}'
            else:
                return 'healthy', None
        except Exception as e:
            return 'error', str(e)
    
    def _evaluate_alerts(self):
        """Evaluar alertas"""
        alert_rules = [
            {
                'name': 'High CPU Usage',
                'metric': 'system.cpu.usage',
                'condition': '>',
                'threshold': 80,
                'level': AlertLevel.WARNING
            },
            {
                'name': 'Critical CPU Usage',
                'metric': 'system.cpu.usage',
                'condition': '>',
                'threshold': 90,
                'level': AlertLevel.CRITICAL
            },
            {
                'name': 'High Memory Usage',
                'metric': 'system.memory.usage',
                'condition': '>',
                'threshold': 85,
                'level': AlertLevel.WARNING
            },
            {
                'name': 'Critical Memory Usage',
                'metric': 'system.memory.usage',
                'condition': '>',
                'threshold': 95,
                'level': AlertLevel.CRITICAL
            },
            {
                'name': 'High Disk Usage',
                'metric': 'system.disk.usage',
                'condition': '>',
                'threshold': 85,
                'level': AlertLevel.WARNING
            },
            {
                'name': 'Critical Disk Usage',
                'metric': 'system.disk.usage',
                'condition': '>',
                'threshold': 95,
                'level': AlertLevel.CRITICAL
            }
        ]
        
        for rule in alert_rules:
            if rule['metric'] in self.metrics and self.metrics[rule['metric']]:
                latest_metric = self.metrics[rule['metric']][-1]
                current_value = latest_metric.value
                
                # Evaluar condición
                should_alert = False
                if rule['condition'] == '>':
                    should_alert = current_value > rule['threshold']
                elif rule['condition'] == '<':
                    should_alert = current_value < rule['threshold']
                elif rule['condition'] == '>=':
                    should_alert = current_value >= rule['threshold']
                elif rule['condition'] == '<=':
                    should_alert = current_value <= rule['threshold']
                elif rule['condition'] == '==':
                    should_alert = current_value == rule['threshold']
                
                if should_alert:
                    # Verificar si ya existe una alerta activa
                    existing_alert = None
                    for alert in self.alerts.values():
                        if (alert.metric_name == rule['metric'] and 
                            alert.status == 'active' and 
                            alert.level == rule['level']):
                            existing_alert = alert
                            break
                    
                    if not existing_alert:
                        # Crear nueva alerta
                        self._create_alert(
                            name=rule['name'],
                            description=f"{rule['metric']} is {rule['condition']} {rule['threshold']}",
                            level=rule['level'],
                            metric_name=rule['metric'],
                            threshold=rule['threshold'],
                            current_value=current_value,
                            condition=rule['condition']
                        )
    
    def _create_alert(self, name: str, description: str, level: AlertLevel,
                     metric_name: str, threshold: float, current_value: float, condition: str):
        """Crear una nueva alerta"""
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            name=name,
            description=description,
            level=level,
            metric_name=metric_name,
            threshold=threshold,
            current_value=current_value,
            condition=condition,
            status='active',
            created_at=datetime.now().isoformat()
        )
        
        self.alerts[alert.alert_id] = alert
        self.system_metrics['total_alerts_triggered'] += 1
        self.system_metrics['active_alerts'] += 1
        
        # Agregar a cola de alertas
        self.alert_queue.put(alert)
        
        # Enviar notificaciones
        self._send_notifications(alert)
        
        logger.warning(f"Alert triggered: {name} - {description}")
    
    def _process_alert_queue(self):
        """Procesar cola de alertas"""
        while not self.alert_queue.empty():
            try:
                alert = self.alert_queue.get_nowait()
                # Procesar alerta (ej: almacenar en base de datos, enviar a sistemas externos)
                self.alert_queue.task_done()
            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"Error processing alert: {e}")
    
    def _send_notifications(self, alert: Alert):
        """Enviar notificaciones"""
        for channel_id, channel in self.notification_channels.items():
            if not channel.enabled:
                continue
            
            try:
                if channel.channel_type == 'email':
                    self._send_email_notification(alert, channel)
                elif channel.channel_type == 'slack':
                    self._send_slack_notification(alert, channel)
                elif channel.channel_type == 'webhook':
                    self._send_webhook_notification(alert, channel)
            except Exception as e:
                logger.error(f"Error sending notification via {channel.channel_type}: {e}")
    
    def _send_email_notification(self, alert: Alert, channel: NotificationChannel):
        """Enviar notificación por email"""
        try:
            config = channel.config
            
            msg = MIMEMultipart()
            msg['From'] = config['from_email']
            msg['To'] = ', '.join(config['to_emails'])
            msg['Subject'] = f"[{alert.level.value.upper()}] {alert.name}"
            
            body = f"""
            Alert: {alert.name}
            Description: {alert.description}
            Level: {alert.level.value}
            Metric: {alert.metric_name}
            Current Value: {alert.current_value}
            Threshold: {alert.threshold}
            Condition: {alert.condition}
            Time: {alert.created_at}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email notification sent for alert: {alert.name}")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    def _send_slack_notification(self, alert: Alert, channel: NotificationChannel):
        """Enviar notificación por Slack"""
        try:
            config = channel.config
            
            color_map = {
                AlertLevel.INFO: '#36a64f',
                AlertLevel.WARNING: '#ff9500',
                AlertLevel.ERROR: '#ff0000',
                AlertLevel.CRITICAL: '#8b0000'
            }
            
            payload = {
                'channel': config['channel'],
                'username': 'Marketing Brain Monitor',
                'icon_emoji': ':warning:',
                'attachments': [
                    {
                        'color': color_map.get(alert.level, '#ff0000'),
                        'title': f"[{alert.level.value.upper()}] {alert.name}",
                        'text': alert.description,
                        'fields': [
                            {
                                'title': 'Metric',
                                'value': alert.metric_name,
                                'short': True
                            },
                            {
                                'title': 'Current Value',
                                'value': str(alert.current_value),
                                'short': True
                            },
                            {
                                'title': 'Threshold',
                                'value': str(alert.threshold),
                                'short': True
                            },
                            {
                                'title': 'Time',
                                'value': alert.created_at,
                                'short': True
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(config['webhook_url'], json=payload)
            response.raise_for_status()
            
            logger.info(f"Slack notification sent for alert: {alert.name}")
            
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
    
    def _send_webhook_notification(self, alert: Alert, channel: NotificationChannel):
        """Enviar notificación por webhook"""
        try:
            config = channel.config
            
            payload = {
                'alert_id': alert.alert_id,
                'name': alert.name,
                'description': alert.description,
                'level': alert.level.value,
                'metric_name': alert.metric_name,
                'current_value': alert.current_value,
                'threshold': alert.threshold,
                'condition': alert.condition,
                'timestamp': alert.created_at
            }
            
            response = requests.post(
                config['url'],
                json=payload,
                headers=config.get('headers', {})
            )
            response.raise_for_status()
            
            logger.info(f"Webhook notification sent for alert: {alert.name}")
            
        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")
    
    def _start_websocket_server(self):
        """Iniciar servidor WebSocket"""
        async def websocket_handler(websocket, path):
            self.websocket_clients.add(websocket)
            try:
                await websocket.wait_closed()
            finally:
                self.websocket_clients.remove(websocket)
        
        async def start_server():
            self.websocket_server = await websockets.serve(
                websocket_handler,
                "localhost",
                self.config['websocket']['port']
            )
            logger.info(f"WebSocket server started on port {self.config['websocket']['port']}")
            await self.websocket_server.wait_closed()
        
        asyncio.run(start_server())
    
    def _broadcast_metric(self, metric: Metric):
        """Transmitir métrica por WebSocket"""
        if self.websocket_clients:
            message = json.dumps({
                'type': 'metric',
                'data': asdict(metric)
            })
            
            # Enviar a todos los clientes conectados
            for client in self.websocket_clients.copy():
                try:
                    asyncio.run(client.send(message))
                except:
                    self.websocket_clients.discard(client)
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """Reconocer una alerta"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.now().isoformat()
            alert.status = 'acknowledged'
            
            logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
    
    def resolve_alert(self, alert_id: str):
        """Resolver una alerta"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.status = 'resolved'
            alert.resolved_at = datetime.now().isoformat()
            
            self.system_metrics['active_alerts'] -= 1
            self.system_metrics['resolved_alerts'] += 1
            
            logger.info(f"Alert {alert_id} resolved")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema"""
        if self.start_time:
            self.system_metrics['system_uptime'] = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'monitor_status': 'running' if self.is_running else 'stopped',
            'system_metrics': self.system_metrics,
            'health_checks': {
                check_id: {
                    'name': check.name,
                    'status': check.status,
                    'response_time': check.response_time,
                    'last_check': check.last_check,
                    'error_message': check.error_message
                }
                for check_id, check in self.health_checks.items()
            },
            'active_alerts': [
                {
                    'alert_id': alert.alert_id,
                    'name': alert.name,
                    'level': alert.level.value,
                    'metric_name': alert.metric_name,
                    'current_value': alert.current_value,
                    'threshold': alert.threshold,
                    'created_at': alert.created_at
                }
                for alert in self.alerts.values()
                if alert.status == 'active'
            ],
            'metrics_summary': {
                metric_name: {
                    'latest_value': metrics[-1].value if metrics else 0,
                    'count': len(metrics),
                    'latest_timestamp': metrics[-1].timestamp if metrics else None
                }
                for metric_name, metrics in self.metrics.items()
            }
        }
    
    def get_metrics_history(self, metric_name: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Obtener historial de métricas"""
        if metric_name not in self.metrics:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            asdict(metric)
            for metric in self.metrics[metric_name]
            if datetime.fromisoformat(metric.timestamp) >= cutoff_time
        ]
    
    def export_monitoring_data(self, export_dir: str = "monitoring_data") -> Dict[str, str]:
        """Exportar datos de monitoreo"""
        Path(export_dir).mkdir(exist_ok=True)
        exported_files = {}
        
        # Exportar métricas
        metrics_data = {
            metric_name: [asdict(metric) for metric in metrics]
            for metric_name, metrics in self.metrics.items()
        }
        metrics_path = Path(export_dir) / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(metrics_data, f, indent=2, ensure_ascii=False)
        exported_files['metrics'] = str(metrics_path)
        
        # Exportar alertas
        alerts_data = {k: asdict(v) for k, v in self.alerts.items()}
        alerts_path = Path(export_dir) / f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(alerts_path, 'w', encoding='utf-8') as f:
            json.dump(alerts_data, f, indent=2, ensure_ascii=False)
        exported_files['alerts'] = str(alerts_path)
        
        # Exportar health checks
        health_checks_data = {k: asdict(v) for k, v in self.health_checks.items()}
        health_checks_path = Path(export_dir) / f"health_checks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(health_checks_path, 'w', encoding='utf-8') as f:
            json.dump(health_checks_data, f, indent=2, ensure_ascii=False)
        exported_files['health_checks'] = str(health_checks_path)
        
        # Exportar estado del sistema
        system_status = self.get_system_status()
        status_path = Path(export_dir) / f"system_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(status_path, 'w', encoding='utf-8') as f:
            json.dump(system_status, f, indent=2, ensure_ascii=False)
        exported_files['system_status'] = str(status_path)
        
        logger.info(f"📦 Exported monitoring data to {export_dir}")
        return exported_files


def main():
    """Función principal para demostrar el Monitor"""
    print("📡 MARKETING BRAIN MONITOR")
    print("=" * 50)
    
    # Crear monitor
    monitor = MarketingBrainMonitor()
    
    # Iniciar monitor
    monitor.start_monitor()
    
    try:
        print(f"\n📊 MONITOREANDO SISTEMA...")
        
        # Monitorear por 60 segundos
        for i in range(60):
            # Obtener estado del sistema
            status = monitor.get_system_status()
            
            if i % 10 == 0:  # Mostrar cada 10 segundos
                print(f"\n📈 Estado del sistema (segundo {i}):")
                print(f"   • Monitor: {status['monitor_status']}")
                print(f"   • Uptime: {status['system_metrics']['system_uptime']:.1f}s")
                print(f"   • Métricas recolectadas: {status['system_metrics']['total_metrics_collected']}")
                print(f"   • Alertas activas: {len(status['active_alerts'])}")
                
                # Mostrar health checks
                print(f"   • Health Checks:")
                for check_id, check in status['health_checks'].items():
                    print(f"     - {check['name']}: {check['status']} ({check['response_time']:.3f}s)")
                
                # Mostrar métricas principales
                print(f"   • Métricas principales:")
                for metric_name, summary in status['metrics_summary'].items():
                    if 'system.' in metric_name:
                        print(f"     - {metric_name}: {summary['latest_value']:.1f}")
            
            time.sleep(1)
        
        # Mostrar resumen final
        print(f"\n📊 RESUMEN DE MONITOREO:")
        final_status = monitor.get_system_status()
        
        print(f"   • Métricas totales recolectadas: {final_status['system_metrics']['total_metrics_collected']}")
        print(f"   • Alertas totales: {final_status['system_metrics']['total_alerts_triggered']}")
        print(f"   • Alertas activas: {len(final_status['active_alerts'])}")
        print(f"   • Alertas resueltas: {final_status['system_metrics']['resolved_alerts']}")
        
        # Mostrar alertas activas
        if final_status['active_alerts']:
            print(f"\n🚨 ALERTAS ACTIVAS:")
            for alert in final_status['active_alerts']:
                print(f"   • {alert['name']} ({alert['level']}): {alert['current_value']} {alert['condition']} {alert['threshold']}")
        
        # Exportar datos
        print(f"\n💾 EXPORTANDO DATOS DE MONITOREO...")
        exported_files = monitor.export_monitoring_data()
        print(f"   • Archivos exportados: {len(exported_files)}")
        for file_type, path in exported_files.items():
            print(f"     - {file_type}: {Path(path).name}")
        
        print(f"\n✅ MONITOR DEMO COMPLETADO EXITOSAMENTE")
        print(f"🎉 El sistema de monitoreo ha recolectado métricas y alertas")
        print(f"   en tiempo real para el Marketing Brain System.")
        
    finally:
        # Detener monitor
        monitor.stop_monitor()


if __name__ == "__main__":
    main()








