#!/usr/bin/env python3
"""
Sistema de Monitoreo en Tiempo Real para Neural Marketing Consciousness Platform
"""

import json
import time
import sqlite3
import threading
import psutil
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import random
import asyncio
import websockets
from collections import deque

class RealtimeMonitoringSystem:
    def __init__(self, db_path="monitoring.db"):
        self.db_path = db_path
        self.monitoring_active = False
        self.metrics_buffer = deque(maxlen=1000)
        self.alert_handlers = {}
        self.websocket_clients = set()
        self.init_monitoring_database()
        self.load_monitoring_configs()
    
    def init_monitoring_database(self):
        """Inicializar base de datos de monitoreo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de métricas del sistema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                metric_name TEXT,
                metric_value REAL,
                metric_type TEXT,
                component TEXT,
                severity TEXT DEFAULT 'info'
            )
        ''')
        
        # Tabla de alertas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT UNIQUE,
                alert_type TEXT,
                severity TEXT,
                title TEXT,
                message TEXT,
                component TEXT,
                status TEXT DEFAULT 'active',
                created_at TEXT,
                resolved_at TEXT,
                acknowledged_by TEXT
            )
        ''')
        
        # Tabla de eventos de usuario
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                event_type TEXT,
                event_data TEXT,
                timestamp TEXT,
                session_id TEXT
            )
        ''')
        
        # Tabla de métricas de rendimiento
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT,
                response_time_ms REAL,
                status_code INTEGER,
                user_id TEXT,
                timestamp TEXT,
                request_size INTEGER,
                response_size INTEGER
            )
        ''')
        
        # Tabla de métricas de IA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT,
                task_type TEXT,
                processing_time_ms REAL,
                tokens_processed INTEGER,
                accuracy REAL,
                cost REAL,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_monitoring_configs(self):
        """Cargar configuraciones de monitoreo"""
        self.monitoring_configs = {
            'system_metrics': {
                'cpu_threshold': 80.0,
                'memory_threshold': 85.0,
                'disk_threshold': 90.0,
                'network_threshold': 1000,  # MB/s
                'collection_interval': 30  # segundos
            },
            'application_metrics': {
                'response_time_threshold': 2000,  # ms
                'error_rate_threshold': 5.0,  # %
                'throughput_threshold': 100,  # requests/min
                'collection_interval': 10  # segundos
            },
            'ai_metrics': {
                'processing_time_threshold': 5000,  # ms
                'accuracy_threshold': 80.0,  # %
                'cost_threshold': 1.0,  # USD per request
                'collection_interval': 60  # segundos
            },
            'user_metrics': {
                'consciousness_growth_threshold': 5.0,  # % per day
                'engagement_threshold': 70.0,  # %
                'churn_risk_threshold': 30.0,  # %
                'collection_interval': 300  # segundos
            }
        }
        
        self.alert_rules = {
            'high_cpu_usage': {
                'condition': 'cpu_percent > 80',
                'severity': 'warning',
                'message': 'High CPU usage detected',
                'action': 'scale_up'
            },
            'high_memory_usage': {
                'condition': 'memory_percent > 85',
                'severity': 'critical',
                'message': 'High memory usage detected',
                'action': 'restart_service'
            },
            'slow_response_time': {
                'condition': 'avg_response_time > 2000',
                'severity': 'warning',
                'message': 'Slow response times detected',
                'action': 'optimize_queries'
            },
            'high_error_rate': {
                'condition': 'error_rate > 5',
                'severity': 'critical',
                'message': 'High error rate detected',
                'action': 'investigate_errors'
            },
            'ai_processing_slow': {
                'condition': 'ai_processing_time > 5000',
                'severity': 'warning',
                'message': 'AI processing is slow',
                'action': 'optimize_ai_models'
            }
        }
    
    def start_monitoring(self):
        """Iniciar monitoreo en tiempo real"""
        self.monitoring_active = True
        
        # Iniciar hilos de monitoreo
        threads = [
            threading.Thread(target=self._monitor_system_metrics, daemon=True),
            threading.Thread(target=self._monitor_application_metrics, daemon=True),
            threading.Thread(target=self._monitor_ai_metrics, daemon=True),
            threading.Thread(target=self._monitor_user_metrics, daemon=True),
            threading.Thread(target=self._process_alerts, daemon=True),
            threading.Thread(target=self._cleanup_old_data, daemon=True)
        ]
        
        for thread in threads:
            thread.start()
        
        print("🔍 Monitoreo en tiempo real iniciado")
        return True
    
    def stop_monitoring(self):
        """Detener monitoreo"""
        self.monitoring_active = False
        print("⏹️ Monitoreo detenido")
    
    def _monitor_system_metrics(self):
        """Monitorear métricas del sistema"""
        while self.monitoring_active:
            try:
                # CPU
                cpu_percent = psutil.cpu_percent(interval=1)
                self._record_metric('cpu_percent', cpu_percent, 'system', 'system')
                
                # Memoria
                memory = psutil.virtual_memory()
                self._record_metric('memory_percent', memory.percent, 'system', 'system')
                self._record_metric('memory_available_gb', memory.available / (1024**3), 'system', 'system')
                
                # Disco
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                self._record_metric('disk_percent', disk_percent, 'system', 'system')
                
                # Red
                network = psutil.net_io_counters()
                self._record_metric('network_bytes_sent', network.bytes_sent, 'system', 'system')
                self._record_metric('network_bytes_recv', network.bytes_recv, 'system', 'system')
                
                # Procesos
                process_count = len(psutil.pids())
                self._record_metric('process_count', process_count, 'system', 'system')
                
                time.sleep(self.monitoring_configs['system_metrics']['collection_interval'])
                
            except Exception as e:
                print(f"Error monitoring system metrics: {e}")
                time.sleep(10)
    
    def _monitor_application_metrics(self):
        """Monitorear métricas de aplicación"""
        while self.monitoring_active:
            try:
                # Simular métricas de aplicación
                response_time = random.uniform(100, 3000)
                error_rate = random.uniform(0, 10)
                throughput = random.uniform(50, 200)
                
                self._record_metric('response_time', response_time, 'application', 'performance')
                self._record_metric('error_rate', error_rate, 'application', 'performance')
                self._record_metric('throughput', throughput, 'application', 'performance')
                
                # Métricas de base de datos
                db_connections = random.randint(10, 100)
                db_query_time = random.uniform(10, 500)
                
                self._record_metric('db_connections', db_connections, 'database', 'performance')
                self._record_metric('db_query_time', db_query_time, 'database', 'performance')
                
                time.sleep(self.monitoring_configs['application_metrics']['collection_interval'])
                
            except Exception as e:
                print(f"Error monitoring application metrics: {e}")
                time.sleep(10)
    
    def _monitor_ai_metrics(self):
        """Monitorear métricas de IA"""
        while self.monitoring_active:
            try:
                # Simular métricas de IA
                models = ['gpt-4', 'claude-3', 'gemini-pro', 'dall-e-3']
                
                for model in models:
                    processing_time = random.uniform(500, 8000)
                    accuracy = random.uniform(70, 98)
                    cost = random.uniform(0.01, 2.0)
                    tokens = random.randint(100, 5000)
                    
                    self._record_ai_metric(model, 'text_generation', processing_time, tokens, accuracy, cost)
                
                time.sleep(self.monitoring_configs['ai_metrics']['collection_interval'])
                
            except Exception as e:
                print(f"Error monitoring AI metrics: {e}")
                time.sleep(10)
    
    def _monitor_user_metrics(self):
        """Monitorear métricas de usuarios"""
        while self.monitoring_active:
            try:
                # Simular métricas de usuarios
                active_users = random.randint(100, 1000)
                consciousness_growth = random.uniform(0, 10)
                engagement_rate = random.uniform(50, 95)
                churn_risk = random.uniform(10, 50)
                
                self._record_metric('active_users', active_users, 'user', 'engagement')
                self._record_metric('consciousness_growth', consciousness_growth, 'user', 'engagement')
                self._record_metric('engagement_rate', engagement_rate, 'user', 'engagement')
                self._record_metric('churn_risk', churn_risk, 'user', 'engagement')
                
                time.sleep(self.monitoring_configs['user_metrics']['collection_interval'])
                
            except Exception as e:
                print(f"Error monitoring user metrics: {e}")
                time.sleep(10)
    
    def _record_metric(self, metric_name: str, metric_value: float, 
                      component: str, metric_type: str, severity: str = 'info'):
        """Registrar métrica"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_metrics 
                (timestamp, metric_name, metric_value, metric_type, component, severity)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), metric_name, metric_value, 
                  metric_type, component, severity))
            
            conn.commit()
            conn.close()
            
            # Agregar al buffer para alertas en tiempo real
            self.metrics_buffer.append({
                'timestamp': datetime.now().isoformat(),
                'metric_name': metric_name,
                'metric_value': metric_value,
                'component': component,
                'metric_type': metric_type
            })
            
        except Exception as e:
            print(f"Error recording metric: {e}")
    
    def _record_ai_metric(self, model_name: str, task_type: str, 
                         processing_time: float, tokens: int, 
                         accuracy: float, cost: float):
        """Registrar métrica de IA"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO ai_metrics 
                (model_name, task_type, processing_time_ms, tokens_processed, 
                 accuracy, cost, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (model_name, task_type, processing_time, tokens, 
                  accuracy, cost, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error recording AI metric: {e}")
    
    def _process_alerts(self):
        """Procesar alertas en tiempo real"""
        while self.monitoring_active:
            try:
                # Obtener métricas recientes
                recent_metrics = list(self.metrics_buffer)[-100:]  # Últimas 100 métricas
                
                # Evaluar reglas de alerta
                for rule_name, rule in self.alert_rules.items():
                    if self._evaluate_alert_rule(rule_name, rule, recent_metrics):
                        self._trigger_alert(rule_name, rule, recent_metrics)
                
                time.sleep(5)  # Verificar alertas cada 5 segundos
                
            except Exception as e:
                print(f"Error processing alerts: {e}")
                time.sleep(10)
    
    def _evaluate_alert_rule(self, rule_name: str, rule: Dict, metrics: List[Dict]) -> bool:
        """Evaluar si una regla de alerta se cumple"""
        try:
            condition = rule['condition']
            
            # Obtener métricas relevantes
            metric_values = {}
            for metric in metrics:
                metric_values[metric['metric_name']] = metric['metric_value']
            
            # Evaluar condición (simplificado)
            if 'cpu_percent' in condition and 'cpu_percent' in metric_values:
                if '>' in condition:
                    threshold = float(condition.split('>')[1].strip())
                    return metric_values['cpu_percent'] > threshold
            
            elif 'memory_percent' in condition and 'memory_percent' in metric_values:
                if '>' in condition:
                    threshold = float(condition.split('>')[1].strip())
                    return metric_values['memory_percent'] > threshold
            
            elif 'response_time' in condition and 'response_time' in metric_values:
                if '>' in condition:
                    threshold = float(condition.split('>')[1].strip())
                    return metric_values['response_time'] > threshold
            
            return False
            
        except Exception as e:
            print(f"Error evaluating alert rule: {e}")
            return False
    
    def _trigger_alert(self, rule_name: str, rule: Dict, metrics: List[Dict]):
        """Disparar alerta"""
        try:
            alert_id = f"{rule_name}_{int(time.time())}"
            
            # Verificar si la alerta ya existe
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM alerts WHERE alert_id = ? AND status = "active"', (alert_id,))
            if cursor.fetchone():
                conn.close()
                return
            
            # Crear nueva alerta
            cursor.execute('''
                INSERT INTO alerts 
                (alert_id, alert_type, severity, title, message, component, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (alert_id, rule_name, rule['severity'], rule['message'], 
                  rule['message'], 'system', datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            # Notificar a clientes WebSocket
            self._notify_websocket_clients({
                'type': 'alert',
                'alert_id': alert_id,
                'severity': rule['severity'],
                'message': rule['message'],
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"🚨 ALERTA [{rule['severity'].upper()}] {rule['message']}")
            
        except Exception as e:
            print(f"Error triggering alert: {e}")
    
    def _notify_websocket_clients(self, data: Dict):
        """Notificar a clientes WebSocket"""
        if self.websocket_clients:
            message = json.dumps(data)
            for client in self.websocket_clients.copy():
                try:
                    asyncio.create_task(client.send(message))
                except:
                    self.websocket_clients.discard(client)
    
    def _cleanup_old_data(self):
        """Limpiar datos antiguos"""
        while self.monitoring_active:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Eliminar métricas más antiguas de 7 días
                cutoff_date = (datetime.now() - timedelta(days=7)).isoformat()
                
                cursor.execute('DELETE FROM system_metrics WHERE timestamp < ?', (cutoff_date,))
                cursor.execute('DELETE FROM performance_metrics WHERE timestamp < ?', (cutoff_date,))
                cursor.execute('DELETE FROM ai_metrics WHERE timestamp < ?', (cutoff_date,))
                cursor.execute('DELETE FROM user_events WHERE timestamp < ?', (cutoff_date,))
                
                # Resolver alertas antiguas
                old_alerts_cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
                cursor.execute('''
                    UPDATE alerts 
                    SET status = 'resolved', resolved_at = ?
                    WHERE status = 'active' AND created_at < ?
                ''', (datetime.now().isoformat(), old_alerts_cutoff))
                
                conn.commit()
                conn.close()
                
                time.sleep(3600)  # Limpiar cada hora
                
            except Exception as e:
                print(f"Error cleaning up old data: {e}")
                time.sleep(3600)
    
    def get_dashboard_data(self) -> Dict:
        """Obtener datos para dashboard"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Métricas del sistema (última hora)
            hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
            
            cursor.execute('''
                SELECT metric_name, AVG(metric_value), MAX(metric_value), MIN(metric_value)
                FROM system_metrics
                WHERE timestamp > ? AND component = 'system'
                GROUP BY metric_name
            ''', (hour_ago,))
            
            system_metrics = {}
            for row in cursor.fetchall():
                system_metrics[row[0]] = {
                    'avg': round(row[1], 2),
                    'max': round(row[2], 2),
                    'min': round(row[3], 2)
                }
            
            # Alertas activas
            cursor.execute('''
                SELECT COUNT(*) FROM alerts WHERE status = 'active'
            ''')
            active_alerts = cursor.fetchone()[0]
            
            # Métricas de rendimiento (última hora)
            cursor.execute('''
                SELECT 
                    AVG(response_time_ms) as avg_response_time,
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count
                FROM performance_metrics
                WHERE timestamp > ?
            ''', (hour_ago,))
            
            perf_result = cursor.fetchone()
            performance_metrics = {
                'avg_response_time': round(perf_result[0] or 0, 2),
                'total_requests': perf_result[1] or 0,
                'error_count': perf_result[2] or 0,
                'error_rate': round((perf_result[2] / max(perf_result[1], 1)) * 100, 2)
            }
            
            # Métricas de IA (última hora)
            cursor.execute('''
                SELECT 
                    model_name,
                    AVG(processing_time_ms) as avg_processing_time,
                    AVG(accuracy) as avg_accuracy,
                    AVG(cost) as avg_cost,
                    COUNT(*) as request_count
                FROM ai_metrics
                WHERE timestamp > ?
                GROUP BY model_name
            ''', (hour_ago,))
            
            ai_metrics = {}
            for row in cursor.fetchall():
                ai_metrics[row[0]] = {
                    'avg_processing_time': round(row[1], 2),
                    'avg_accuracy': round(row[2], 2),
                    'avg_cost': round(row[3], 4),
                    'request_count': row[4]
                }
            
            conn.close()
            
            return {
                'success': True,
                'data': {
                    'system_metrics': system_metrics,
                    'performance_metrics': performance_metrics,
                    'ai_metrics': ai_metrics,
                    'active_alerts': active_alerts,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_alerts(self, status: str = 'active', limit: int = 50) -> Dict:
        """Obtener alertas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT alert_id, alert_type, severity, title, message, 
                       component, created_at, resolved_at, acknowledged_by
                FROM alerts
                WHERE status = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (status, limit))
            
            alerts = []
            for row in cursor.fetchall():
                alerts.append({
                    'alert_id': row[0],
                    'alert_type': row[1],
                    'severity': row[2],
                    'title': row[3],
                    'message': row[4],
                    'component': row[5],
                    'created_at': row[6],
                    'resolved_at': row[7],
                    'acknowledged_by': row[8]
                })
            
            conn.close()
            
            return {
                'success': True,
                'alerts': alerts,
                'count': len(alerts)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> Dict:
        """Reconocer alerta"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE alerts 
                SET acknowledged_by = ?, status = 'acknowledged'
                WHERE alert_id = ? AND status = 'active'
            ''', (acknowledged_by, alert_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return {'success': True, 'message': 'Alert acknowledged'}
            else:
                conn.close()
                return {'success': False, 'error': 'Alert not found or already acknowledged'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def resolve_alert(self, alert_id: str, resolved_by: str) -> Dict:
        """Resolver alerta"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE alerts 
                SET status = 'resolved', resolved_at = ?, acknowledged_by = ?
                WHERE alert_id = ?
            ''', (datetime.now().isoformat(), resolved_by, alert_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return {'success': True, 'message': 'Alert resolved'}
            else:
                conn.close()
                return {'success': False, 'error': 'Alert not found'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def record_user_event(self, user_id: str, event_type: str, 
                         event_data: Dict = None, session_id: str = None) -> Dict:
        """Registrar evento de usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_events 
                (user_id, event_type, event_data, timestamp, session_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, event_type, json.dumps(event_data or {}), 
                  datetime.now().isoformat(), session_id))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'User event recorded'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def record_performance_metric(self, endpoint: str, response_time: float, 
                                status_code: int, user_id: str = None,
                                request_size: int = 0, response_size: int = 0) -> Dict:
        """Registrar métrica de rendimiento"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_metrics 
                (endpoint, response_time_ms, status_code, user_id, timestamp, 
                 request_size, response_size)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (endpoint, response_time, status_code, user_id, 
                  datetime.now().isoformat(), request_size, response_size))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'Performance metric recorded'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

def main():
    monitoring = RealtimeMonitoringSystem()
    
    print("📊 Sistema de Monitoreo en Tiempo Real")
    print("=" * 50)
    print("1. Iniciar monitoreo")
    print("2. Detener monitoreo")
    print("3. Ver dashboard")
    print("4. Ver alertas")
    print("5. Reconocer alerta")
    print("6. Resolver alerta")
    print("7. Registrar evento de usuario")
    print("8. Registrar métrica de rendimiento")
    print("9. Simular eventos")
    print("10. Salir")
    
    while True:
        choice = input("\nSeleccione una opción (1-10): ").strip()
        
        if choice == '1':
            result = monitoring.start_monitoring()
            if result:
                print("✅ Monitoreo iniciado")
            else:
                print("❌ Error iniciando monitoreo")
        
        elif choice == '2':
            monitoring.stop_monitoring()
        
        elif choice == '3':
            result = monitoring.get_dashboard_data()
            if result['success']:
                data = result['data']
                print(f"\n📊 Dashboard - {data['timestamp']}")
                print(f"  🚨 Alertas Activas: {data['active_alerts']}")
                print(f"  📈 Métricas del Sistema:")
                for metric, values in data['system_metrics'].items():
                    print(f"    {metric}: {values['avg']} (max: {values['max']})")
                print(f"  ⚡ Rendimiento:")
                print(f"    Tiempo de respuesta: {data['performance_metrics']['avg_response_time']}ms")
                print(f"    Total requests: {data['performance_metrics']['total_requests']}")
                print(f"    Tasa de errores: {data['performance_metrics']['error_rate']}%")
            else:
                print(f"❌ {result['error']}")
        
        elif choice == '4':
            status = input("Estado de alertas (active/acknowledged/resolved): ").strip() or 'active'
            result = monitoring.get_alerts(status)
            if result['success']:
                print(f"\n🚨 {result['count']} alertas {status}:")
                for alert in result['alerts'][:10]:
                    print(f"  • [{alert['severity'].upper()}] {alert['title']} - {alert['created_at']}")
            else:
                print(f"❌ {result['error']}")
        
        elif choice == '5':
            alert_id = input("ID de alerta: ").strip()
            acknowledged_by = input("Reconocido por: ").strip()
            result = monitoring.acknowledge_alert(alert_id, acknowledged_by)
            print(f"✅ {result['message']}" if result['success'] else f"❌ {result['error']}")
        
        elif choice == '6':
            alert_id = input("ID de alerta: ").strip()
            resolved_by = input("Resuelto por: ").strip()
            result = monitoring.resolve_alert(alert_id, resolved_by)
            print(f"✅ {result['message']}" if result['success'] else f"❌ {result['error']}")
        
        elif choice == '7':
            user_id = input("ID de usuario: ").strip()
            event_type = input("Tipo de evento: ").strip()
            event_data = input("Datos del evento (JSON, opcional): ").strip()
            event_data = json.loads(event_data) if event_data else {}
            
            result = monitoring.record_user_event(user_id, event_type, event_data)
            print(f"✅ {result['message']}" if result['success'] else f"❌ {result['error']}")
        
        elif choice == '8':
            endpoint = input("Endpoint: ").strip()
            response_time = float(input("Tiempo de respuesta (ms): ").strip())
            status_code = int(input("Código de estado: ").strip())
            user_id = input("ID de usuario (opcional): ").strip() or None
            
            result = monitoring.record_performance_metric(endpoint, response_time, status_code, user_id)
            print(f"✅ {result['message']}" if result['success'] else f"❌ {result['error']}")
        
        elif choice == '9':
            print("🔄 Simulando eventos...")
            
            # Simular eventos de usuario
            users = ['user1', 'user2', 'user3', 'user4', 'user5']
            event_types = ['login', 'content_view', 'ai_interaction', 'consciousness_update', 'logout']
            
            for _ in range(20):
                user_id = random.choice(users)
                event_type = random.choice(event_types)
                event_data = {'simulated': True, 'timestamp': datetime.now().isoformat()}
                monitoring.record_user_event(user_id, event_type, event_data)
            
            # Simular métricas de rendimiento
            endpoints = ['/api/content', '/api/ai/generate', '/api/analytics', '/api/users']
            for _ in range(15):
                endpoint = random.choice(endpoints)
                response_time = random.uniform(100, 3000)
                status_code = random.choice([200, 200, 200, 400, 500])  # Más 200s
                monitoring.record_performance_metric(endpoint, response_time, status_code)
            
            print("✅ Eventos simulados generados")
        
        elif choice == '10':
            monitoring.stop_monitoring()
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()