#!/usr/bin/env python3
"""
ClickUp Brain - Sistema de Notificaciones Push y Alertas Inteligentes
====================================================================

Sistema avanzado de notificaciones con alertas inteligentes, notificaciones push,
integración con múltiples canales y personalización basada en comportamiento.
"""

import os
import sys
import json
import smtplib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import logging
import threading
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationChannel:
    """Canal de notificación base."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.name = config.get('name', 'Unknown')
    
    def send(self, message: Dict) -> bool:
        """Enviar notificación a través del canal."""
        raise NotImplementedError("Subclases deben implementar send()")
    
    def is_available(self) -> bool:
        """Verificar si el canal está disponible."""
        return self.enabled

class EmailChannel(NotificationChannel):
    """Canal de notificación por email."""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port', 587)
        self.username = config.get('username')
        self.password = config.get('password')
        self.from_email = config.get('from_email')
    
    def send(self, message: Dict) -> bool:
        """Enviar email."""
        try:
            if not self.is_available():
                return False
            
            # Crear mensaje
            msg = MimeMultipart()
            msg['From'] = self.from_email
            msg['To'] = message.get('recipient')
            msg['Subject'] = message.get('subject', 'ClickUp Brain Notification')
            
            # Contenido del mensaje
            body = message.get('body', '')
            if message.get('html_body'):
                msg.attach(MimeText(message['html_body'], 'html'))
            else:
                msg.attach(MimeText(body, 'plain'))
            
            # Enviar email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.from_email, message.get('recipient'), text)
            server.quit()
            
            logger.info(f"Email enviado a {message.get('recipient')}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email: {str(e)}")
            return False

class SlackChannel(NotificationChannel):
    """Canal de notificación para Slack."""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.webhook_url = config.get('webhook_url')
        self.channel = config.get('channel', '#general')
        self.username = config.get('username', 'ClickUp Brain')
    
    def send(self, message: Dict) -> bool:
        """Enviar mensaje a Slack."""
        try:
            if not self.is_available() or not self.webhook_url:
                return False
            
            # Preparar payload para Slack
            payload = {
                'channel': self.channel,
                'username': self.username,
                'text': message.get('text', ''),
                'attachments': message.get('attachments', [])
            }
            
            # Enviar a Slack
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Mensaje enviado a Slack canal {self.channel}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando a Slack: {str(e)}")
            return False

class TeamsChannel(NotificationChannel):
    """Canal de notificación para Microsoft Teams."""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.webhook_url = config.get('webhook_url')
        self.title = config.get('title', 'ClickUp Brain Alert')
    
    def send(self, message: Dict) -> bool:
        """Enviar mensaje a Microsoft Teams."""
        try:
            if not self.is_available() or not self.webhook_url:
                return False
            
            # Preparar payload para Teams
            payload = {
                '@type': 'MessageCard',
                '@context': 'http://schema.org/extensions',
                'themeColor': message.get('color', '0076D7'),
                'summary': message.get('summary', 'ClickUp Brain Notification'),
                'sections': [{
                    'activityTitle': self.title,
                    'activitySubtitle': message.get('subtitle', ''),
                    'text': message.get('text', ''),
                    'facts': message.get('facts', [])
                }]
            }
            
            # Enviar a Teams
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info("Mensaje enviado a Microsoft Teams")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando a Teams: {str(e)}")
            return False

class PushNotificationChannel(NotificationChannel):
    """Canal de notificaciones push."""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.app_id = config.get('app_id')
        self.base_url = config.get('base_url', 'https://onesignal.com/api/v1')
    
    def send(self, message: Dict) -> bool:
        """Enviar notificación push."""
        try:
            if not self.is_available() or not self.api_key:
                return False
            
            # Preparar payload para OneSignal (ejemplo)
            payload = {
                'app_id': self.app_id,
                'included_segments': message.get('segments', ['All']),
                'headings': {'en': message.get('title', 'ClickUp Brain')},
                'contents': {'en': message.get('body', '')},
                'data': message.get('data', {})
            }
            
            headers = {
                'Authorization': f'Basic {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Enviar notificación push
            response = requests.post(f'{self.base_url}/notifications', 
                                   json=payload, headers=headers)
            response.raise_for_status()
            
            logger.info("Notificación push enviada")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando notificación push: {str(e)}")
            return False

class IntelligentAlertSystem:
    """Sistema de alertas inteligentes."""
    
    def __init__(self):
        self.alert_rules = []
        self.alert_history = []
        self.user_preferences = {}
        self.alert_thresholds = {
            'efficiency_drop': 10,  # Caída de eficiencia en %
            'overdue_tasks': 5,     # Número de tareas vencidas
            'response_time': 24,    # Tiempo de respuesta en horas
            'team_sentiment': -0.2  # Score de sentimiento negativo
        }
    
    def add_alert_rule(self, rule: Dict):
        """Agregar regla de alerta."""
        rule['id'] = f"rule_{len(self.alert_rules) + 1}"
        rule['created_at'] = datetime.now().isoformat()
        rule['enabled'] = rule.get('enabled', True)
        self.alert_rules.append(rule)
        logger.info(f"Regla de alerta agregada: {rule['name']}")
    
    def check_alerts(self, data: Dict) -> List[Dict]:
        """Verificar condiciones de alerta."""
        triggered_alerts = []
        
        for rule in self.alert_rules:
            if not rule.get('enabled', True):
                continue
            
            if self._evaluate_rule(rule, data):
                alert = {
                    'rule_id': rule['id'],
                    'rule_name': rule['name'],
                    'severity': rule.get('severity', 'medium'),
                    'message': rule.get('message', ''),
                    'data': data,
                    'triggered_at': datetime.now().isoformat(),
                    'recommendations': rule.get('recommendations', [])
                }
                triggered_alerts.append(alert)
                self.alert_history.append(alert)
        
        return triggered_alerts
    
    def _evaluate_rule(self, rule: Dict, data: Dict) -> bool:
        """Evaluar si una regla se cumple."""
        try:
            condition = rule.get('condition', {})
            condition_type = condition.get('type')
            
            if condition_type == 'efficiency_drop':
                current_efficiency = data.get('efficiency_score', 0)
                previous_efficiency = data.get('previous_efficiency_score', current_efficiency)
                drop = previous_efficiency - current_efficiency
                return drop >= self.alert_thresholds['efficiency_drop']
            
            elif condition_type == 'overdue_tasks':
                overdue_count = data.get('overdue_tasks', 0)
                return overdue_count >= self.alert_thresholds['overdue_tasks']
            
            elif condition_type == 'response_time':
                avg_response_time = data.get('avg_response_time', 0)
                return avg_response_time >= self.alert_thresholds['response_time']
            
            elif condition_type == 'team_sentiment':
                sentiment_score = data.get('sentiment_score', 0)
                return sentiment_score <= self.alert_thresholds['team_sentiment']
            
            elif condition_type == 'custom':
                # Evaluar condición personalizada
                return self._evaluate_custom_condition(condition.get('expression', ''), data)
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluando regla {rule.get('name', 'Unknown')}: {str(e)}")
            return False
    
    def _evaluate_custom_condition(self, expression: str, data: Dict) -> bool:
        """Evaluar condición personalizada."""
        try:
            # Evaluación segura de expresión (simplificada)
            # En producción, usar una librería como `ast` para evaluación segura
            return eval(expression, {"__builtins__": {}}, data)
        except Exception as e:
            logger.error(f"Error evaluando condición personalizada: {str(e)}")
            return False
    
    def setup_default_rules(self):
        """Configurar reglas de alerta por defecto."""
        default_rules = [
            {
                'name': 'Caída de Eficiencia',
                'condition': {'type': 'efficiency_drop'},
                'severity': 'high',
                'message': 'La eficiencia del equipo ha caído significativamente',
                'recommendations': [
                    'Revisar carga de trabajo actual',
                    'Identificar cuellos de botella',
                    'Programar reunión de equipo'
                ]
            },
            {
                'name': 'Tareas Vencidas',
                'condition': {'type': 'overdue_tasks'},
                'severity': 'medium',
                'message': 'Hay múltiples tareas vencidas que requieren atención',
                'recommendations': [
                    'Priorizar tareas vencidas',
                    'Revisar estimaciones de tiempo',
                    'Comunicar retrasos a stakeholders'
                ]
            },
            {
                'name': 'Tiempo de Respuesta Lento',
                'condition': {'type': 'response_time'},
                'severity': 'medium',
                'message': 'El tiempo de respuesta promedio es demasiado alto',
                'recommendations': [
                    'Implementar SLA más estrictos',
                    'Configurar alertas automáticas',
                    'Revisar procesos de comunicación'
                ]
            },
            {
                'name': 'Sentimiento del Equipo Bajo',
                'condition': {'type': 'team_sentiment'},
                'severity': 'high',
                'message': 'El sentimiento del equipo ha bajado significativamente',
                'recommendations': [
                    'Programar sesión de feedback',
                    'Revisar carga de trabajo',
                    'Implementar actividades de team building'
                ]
            }
        ]
        
        for rule in default_rules:
            self.add_alert_rule(rule)

class NotificationManager:
    """Gestor principal de notificaciones."""
    
    def __init__(self, config: Dict = None):
        self.channels = {}
        self.alert_system = IntelligentAlertSystem()
        self.notification_queue = []
        self.user_preferences = {}
        self.config = config or {}
        
        # Inicializar canales
        self._initialize_channels()
        
        # Configurar reglas por defecto
        self.alert_system.setup_default_rules()
    
    def _initialize_channels(self):
        """Inicializar canales de notificación."""
        channels_config = self.config.get('channels', {})
        
        # Canal de email
        if 'email' in channels_config:
            self.channels['email'] = EmailChannel(channels_config['email'])
        
        # Canal de Slack
        if 'slack' in channels_config:
            self.channels['slack'] = SlackChannel(channels_config['slack'])
        
        # Canal de Teams
        if 'teams' in channels_config:
            self.channels['teams'] = TeamsChannel(channels_config['teams'])
        
        # Canal de notificaciones push
        if 'push' in channels_config:
            self.channels['push'] = PushNotificationChannel(channels_config['push'])
    
    def send_notification(self, message: Dict, channels: List[str] = None) -> Dict:
        """Enviar notificación a través de canales especificados."""
        try:
            if channels is None:
                channels = list(self.channels.keys())
            
            results = {}
            for channel_name in channels:
                if channel_name in self.channels:
                    channel = self.channels[channel_name]
                    success = channel.send(message)
                    results[channel_name] = success
                else:
                    results[channel_name] = False
                    logger.warning(f"Canal no encontrado: {channel_name}")
            
            # Registrar en cola de notificaciones
            notification_record = {
                'message': message,
                'channels': channels,
                'results': results,
                'sent_at': datetime.now().isoformat()
            }
            self.notification_queue.append(notification_record)
            
            return results
            
        except Exception as e:
            logger.error(f"Error enviando notificación: {str(e)}")
            return {'error': str(e)}
    
    def process_alerts(self, data: Dict) -> List[Dict]:
        """Procesar alertas basadas en datos."""
        try:
            # Verificar alertas
            triggered_alerts = self.alert_system.check_alerts(data)
            
            # Enviar notificaciones para alertas activadas
            for alert in triggered_alerts:
                self._send_alert_notification(alert)
            
            return triggered_alerts
            
        except Exception as e:
            logger.error(f"Error procesando alertas: {str(e)}")
            return []
    
    def _send_alert_notification(self, alert: Dict):
        """Enviar notificación de alerta."""
        try:
            # Preparar mensaje de alerta
            message = {
                'type': 'alert',
                'severity': alert['severity'],
                'title': f"🚨 {alert['rule_name']}",
                'body': alert['message'],
                'data': alert['data'],
                'recommendations': alert['recommendations'],
                'timestamp': alert['triggered_at']
            }
            
            # Determinar canales basado en severidad
            channels = self._get_channels_for_severity(alert['severity'])
            
            # Enviar notificación
            self.send_notification(message, channels)
            
        except Exception as e:
            logger.error(f"Error enviando notificación de alerta: {str(e)}")
    
    def _get_channels_for_severity(self, severity: str) -> List[str]:
        """Obtener canales apropiados para nivel de severidad."""
        if severity == 'high':
            return ['email', 'slack', 'push']
        elif severity == 'medium':
            return ['slack', 'email']
        else:
            return ['slack']
    
    def send_daily_summary(self, team_data: Dict) -> bool:
        """Enviar resumen diario del equipo."""
        try:
            # Preparar resumen
            summary = self._generate_daily_summary(team_data)
            
            # Crear mensaje
            message = {
                'type': 'daily_summary',
                'title': '📊 Resumen Diario - ClickUp Brain',
                'body': summary['text'],
                'html_body': summary['html'],
                'data': team_data
            }
            
            # Enviar a canales apropiados
            channels = ['email', 'slack']
            results = self.send_notification(message, channels)
            
            return all(results.values())
            
        except Exception as e:
            logger.error(f"Error enviando resumen diario: {str(e)}")
            return False
    
    def _generate_daily_summary(self, team_data: Dict) -> Dict:
        """Generar resumen diario."""
        try:
            efficiency = team_data.get('efficiency_score', 0)
            completed_tasks = team_data.get('completed_tasks', 0)
            overdue_tasks = team_data.get('overdue_tasks', 0)
            
            text = f"""
Resumen Diario del Equipo:

📈 Eficiencia: {efficiency:.1f}/100
✅ Tareas Completadas: {completed_tasks}
⚠️ Tareas Vencidas: {overdue_tasks}

Recomendaciones:
- Continuar con el buen trabajo
- Revisar tareas vencidas
- Mantener momentum positivo
"""
            
            html = f"""
<html>
<body>
<h2>📊 Resumen Diario - ClickUp Brain</h2>
<p><strong>📈 Eficiencia:</strong> {efficiency:.1f}/100</p>
<p><strong>✅ Tareas Completadas:</strong> {completed_tasks}</p>
<p><strong>⚠️ Tareas Vencidas:</strong> {overdue_tasks}</p>
<h3>Recomendaciones:</h3>
<ul>
<li>Continuar con el buen trabajo</li>
<li>Revisar tareas vencidas</li>
<li>Mantener momentum positivo</li>
</ul>
</body>
</html>
"""
            
            return {'text': text, 'html': html}
            
        except Exception as e:
            logger.error(f"Error generando resumen diario: {str(e)}")
            return {'text': 'Error generando resumen', 'html': '<p>Error generando resumen</p>'}

class ClickUpBrainNotifications:
    """Sistema principal de notificaciones de ClickUp Brain."""
    
    def __init__(self, config: Dict = None):
        self.notification_manager = NotificationManager(config)
        self.monitoring_active = False
        self.monitoring_thread = None
    
    def start_monitoring(self, data_source_func, interval_minutes: int = 30):
        """Iniciar monitoreo continuo."""
        try:
            if self.monitoring_active:
                logger.warning("Monitoreo ya está activo")
                return False
            
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                args=(data_source_func, interval_minutes)
            )
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            
            logger.info(f"Monitoreo iniciado con intervalo de {interval_minutes} minutos")
            return True
            
        except Exception as e:
            logger.error(f"Error iniciando monitoreo: {str(e)}")
            return False
    
    def stop_monitoring(self):
        """Detener monitoreo."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Monitoreo detenido")
    
    def _monitoring_loop(self, data_source_func, interval_minutes: int):
        """Loop de monitoreo."""
        while self.monitoring_active:
            try:
                # Obtener datos
                data = data_source_func()
                
                # Procesar alertas
                alerts = self.notification_manager.process_alerts(data)
                
                if alerts:
                    logger.info(f"{len(alerts)} alertas procesadas")
                
                # Esperar siguiente ciclo
                time.sleep(interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Error en loop de monitoreo: {str(e)}")
                time.sleep(60)  # Esperar 1 minuto antes de reintentar
    
    def send_custom_notification(self, message: str, channels: List[str] = None, 
                               severity: str = 'medium') -> bool:
        """Enviar notificación personalizada."""
        try:
            notification = {
                'type': 'custom',
                'severity': severity,
                'title': 'ClickUp Brain Notification',
                'body': message,
                'timestamp': datetime.now().isoformat()
            }
            
            results = self.notification_manager.send_notification(notification, channels)
            return all(results.values())
            
        except Exception as e:
            logger.error(f"Error enviando notificación personalizada: {str(e)}")
            return False
    
    def get_notification_history(self, limit: int = 50) -> List[Dict]:
        """Obtener historial de notificaciones."""
        return self.notification_manager.notification_queue[-limit:]
    
    def get_alert_history(self, limit: int = 50) -> List[Dict]:
        """Obtener historial de alertas."""
        return self.notification_manager.alert_system.alert_history[-limit:]

def main():
    """Función principal para demostrar el sistema de notificaciones."""
    print("🔔 ClickUp Brain - Sistema de Notificaciones Push y Alertas Inteligentes")
    print("=" * 70)
    
    # Configuración de ejemplo
    config = {
        'channels': {
            'email': {
                'enabled': True,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': 'your-email@gmail.com',
                'password': 'your-password',
                'from_email': 'your-email@gmail.com'
            },
            'slack': {
                'enabled': True,
                'webhook_url': 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK',
                'channel': '#clickup-brain',
                'username': 'ClickUp Brain'
            },
            'teams': {
                'enabled': True,
                'webhook_url': 'https://your-org.webhook.office.com/webhookb2/YOUR/TEAMS/WEBHOOK'
            },
            'push': {
                'enabled': True,
                'api_key': 'your-onesignal-api-key',
                'app_id': 'your-onesignal-app-id'
            }
        }
    }
    
    # Inicializar sistema de notificaciones
    notification_system = ClickUpBrainNotifications(config)
    
    print("✅ Sistema de notificaciones inicializado")
    
    # Simular datos del equipo
    team_data = {
        'efficiency_score': 75,
        'previous_efficiency_score': 85,
        'completed_tasks': 12,
        'overdue_tasks': 3,
        'avg_response_time': 18,
        'sentiment_score': 0.1
    }
    
    print("\n🔍 Procesando alertas...")
    
    # Procesar alertas
    alerts = notification_system.notification_manager.process_alerts(team_data)
    
    if alerts:
        print(f"🚨 {len(alerts)} alertas activadas:")
        for alert in alerts:
            print(f"   • {alert['rule_name']} ({alert['severity']})")
    else:
        print("✅ No se activaron alertas")
    
    # Enviar notificación personalizada
    print("\n📤 Enviando notificación personalizada...")
    success = notification_system.send_custom_notification(
        "El sistema ClickUp Brain está funcionando correctamente",
        channels=['slack'],
        severity='low'
    )
    
    if success:
        print("✅ Notificación enviada exitosamente")
    else:
        print("❌ Error enviando notificación")
    
    # Enviar resumen diario
    print("\n📊 Enviando resumen diario...")
    summary_success = notification_system.notification_manager.send_daily_summary(team_data)
    
    if summary_success:
        print("✅ Resumen diario enviado")
    else:
        print("❌ Error enviando resumen diario")
    
    # Mostrar historial
    print(f"\n📋 Historial de notificaciones: {len(notification_system.get_notification_history())} entradas")
    print(f"📋 Historial de alertas: {len(notification_system.get_alert_history())} entradas")
    
    print("\n🎉 Sistema de notificaciones funcionando correctamente!")
    print("🚀 Listo para alertas inteligentes y notificaciones push")
    
    return True

if __name__ == "__main__":
    main()










