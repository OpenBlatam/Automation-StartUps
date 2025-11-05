#!/usr/bin/env python3
"""
Sistema de Integración y Automatización para Neural Marketing Consciousness Platform
"""

import json
import time
import sqlite3
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import threading
import schedule

class IntegrationAutomation:
    def __init__(self, db_path="integrations.db"):
        self.db_path = db_path
        self.integrations = {}
        self.automations = {}
        self.webhooks = {}
        self.init_integration_database()
        self.load_integration_configs()
    
    def init_integration_database(self):
        """Inicializar base de datos de integraciones"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de integraciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS integrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL,
                status TEXT DEFAULT 'inactive',
                config TEXT,
                last_sync TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Tabla de automatizaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                trigger_type TEXT NOT NULL,
                trigger_config TEXT,
                action_type TEXT NOT NULL,
                action_config TEXT,
                status TEXT DEFAULT 'inactive',
                last_executed TEXT,
                execution_count INTEGER DEFAULT 0,
                created_at TEXT
            )
        ''')
        
        # Tabla de webhooks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS webhooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL,
                events TEXT,
                secret TEXT,
                status TEXT DEFAULT 'active',
                last_triggered TEXT,
                trigger_count INTEGER DEFAULT 0,
                created_at TEXT
            )
        ''')
        
        # Tabla de logs de integración
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS integration_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                integration_id INTEGER,
                event_type TEXT,
                message TEXT,
                status TEXT,
                data TEXT,
                timestamp TEXT,
                FOREIGN KEY (integration_id) REFERENCES integrations (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_integration_configs(self):
        """Cargar configuraciones de integración"""
        self.integrations = {
            'crm_salesforce': {
                'name': 'Salesforce CRM',
                'type': 'crm',
                'endpoints': {
                    'auth': 'https://login.salesforce.com/services/oauth2/token',
                    'api': 'https://your-instance.salesforce.com/services/data/v52.0/',
                    'webhook': 'https://your-instance.salesforce.com/services/apexrest/webhook'
                },
                'fields': ['Id', 'Name', 'Email', 'Phone', 'Company', 'LeadSource'],
                'sync_interval': 300  # 5 minutos
            },
            'email_mailchimp': {
                'name': 'Mailchimp Email Marketing',
                'type': 'email',
                'endpoints': {
                    'auth': 'https://login.mailchimp.com/oauth2/token',
                    'api': 'https://us1.api.mailchimp.com/3.0/',
                    'webhook': 'https://us1.api.mailchimp.com/3.0/webhooks'
                },
                'fields': ['email_address', 'status', 'merge_fields', 'tags'],
                'sync_interval': 600  # 10 minutos
            },
            'social_linkedin': {
                'name': 'LinkedIn Marketing',
                'type': 'social',
                'endpoints': {
                    'auth': 'https://www.linkedin.com/oauth/v2/accessToken',
                    'api': 'https://api.linkedin.com/v2/',
                    'webhook': 'https://api.linkedin.com/v2/webhooks'
                },
                'fields': ['id', 'firstName', 'lastName', 'emailAddress', 'companyName'],
                'sync_interval': 1800  # 30 minutos
            },
            'analytics_google': {
                'name': 'Google Analytics',
                'type': 'analytics',
                'endpoints': {
                    'auth': 'https://oauth2.googleapis.com/token',
                    'api': 'https://analyticsreporting.googleapis.com/v4/reports:batchGet',
                    'webhook': 'https://analytics.googleapis.com/analytics/v3/data/realtime'
                },
                'fields': ['ga:users', 'ga:sessions', 'ga:pageviews', 'ga:bounceRate'],
                'sync_interval': 3600  # 1 hora
            },
            'ai_openai': {
                'name': 'OpenAI API',
                'type': 'ai',
                'endpoints': {
                    'completions': 'https://api.openai.com/v1/completions',
                    'chat': 'https://api.openai.com/v1/chat/completions',
                    'embeddings': 'https://api.openai.com/v1/embeddings'
                },
                'models': ['gpt-4', 'gpt-3.5-turbo', 'text-davinci-003'],
                'sync_interval': 0  # On-demand
            }
        }
    
    def setup_integration(self, integration_name: str, config: Dict) -> Dict:
        """Configurar nueva integración"""
        if integration_name not in self.integrations:
            return {'success': False, 'error': 'Integration not supported'}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar si ya existe
            cursor.execute('SELECT id FROM integrations WHERE name = ?', (integration_name,))
            existing = cursor.fetchone()
            
            if existing:
                # Actualizar configuración existente
                cursor.execute('''
                    UPDATE integrations 
                    SET config = ?, status = 'active', updated_at = ?
                    WHERE name = ?
                ''', (json.dumps(config), datetime.now().isoformat(), integration_name))
            else:
                # Crear nueva integración
                cursor.execute('''
                    INSERT INTO integrations (name, type, config, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (integration_name, self.integrations[integration_name]['type'], 
                      json.dumps(config), 'active', datetime.now().isoformat(), 
                      datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            # Log de configuración
            self.log_integration_event(integration_name, 'setup', 
                                     f'Integration {integration_name} configured successfully', 'success')
            
            return {'success': True, 'message': f'Integration {integration_name} configured successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_integration(self, integration_name: str) -> Dict:
        """Probar conexión de integración"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT config FROM integrations WHERE name = ?', (integration_name,))
            result = cursor.fetchone()
            
            if not result:
                return {'success': False, 'error': 'Integration not found'}
            
            config = json.loads(result[0])
            integration_config = self.integrations[integration_name]
            
            # Probar conexión según el tipo
            if integration_config['type'] == 'crm':
                test_result = self.test_crm_connection(integration_name, config)
            elif integration_config['type'] == 'email':
                test_result = self.test_email_connection(integration_name, config)
            elif integration_config['type'] == 'social':
                test_result = self.test_social_connection(integration_name, config)
            elif integration_config['type'] == 'analytics':
                test_result = self.test_analytics_connection(integration_name, config)
            elif integration_config['type'] == 'ai':
                test_result = self.test_ai_connection(integration_name, config)
            else:
                test_result = {'success': False, 'error': 'Unknown integration type'}
            
            # Actualizar estado
            status = 'active' if test_result['success'] else 'error'
            cursor.execute('UPDATE integrations SET status = ? WHERE name = ?', (status, integration_name))
            conn.commit()
            conn.close()
            
            # Log de prueba
            self.log_integration_event(integration_name, 'test', 
                                     f'Integration test: {test_result}', status)
            
            return test_result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_crm_connection(self, integration_name: str, config: Dict) -> Dict:
        """Probar conexión CRM"""
        try:
            # Simular prueba de conexión CRM
            headers = {
                'Authorization': f"Bearer {config.get('access_token', 'test_token')}",
                'Content-Type': 'application/json'
            }
            
            # Simular llamada a API
            response = {
                'status_code': 200,
                'data': {'totalSize': 1, 'records': [{'Id': 'test123', 'Name': 'Test Lead'}]}
            }
            
            if response['status_code'] == 200:
                return {'success': True, 'message': 'CRM connection successful', 'data': response['data']}
            else:
                return {'success': False, 'error': 'CRM connection failed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_email_connection(self, integration_name: str, config: Dict) -> Dict:
        """Probar conexión de email marketing"""
        try:
            # Simular prueba de conexión email
            headers = {
                'Authorization': f"Bearer {config.get('api_key', 'test_key')}",
                'Content-Type': 'application/json'
            }
            
            # Simular llamada a API
            response = {
                'status_code': 200,
                'data': {'total_items': 1000, 'lists': [{'id': 'list123', 'name': 'Main List'}]}
            }
            
            if response['status_code'] == 200:
                return {'success': True, 'message': 'Email connection successful', 'data': response['data']}
            else:
                return {'success': False, 'error': 'Email connection failed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_social_connection(self, integration_name: str, config: Dict) -> Dict:
        """Probar conexión de redes sociales"""
        try:
            # Simular prueba de conexión social
            headers = {
                'Authorization': f"Bearer {config.get('access_token', 'test_token')}",
                'Content-Type': 'application/json'
            }
            
            # Simular llamada a API
            response = {
                'status_code': 200,
                'data': {'id': 'user123', 'firstName': 'Test', 'lastName': 'User'}
            }
            
            if response['status_code'] == 200:
                return {'success': True, 'message': 'Social connection successful', 'data': response['data']}
            else:
                return {'success': False, 'error': 'Social connection failed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_analytics_connection(self, integration_name: str, config: Dict) -> Dict:
        """Probar conexión de analytics"""
        try:
            # Simular prueba de conexión analytics
            headers = {
                'Authorization': f"Bearer {config.get('access_token', 'test_token')}",
                'Content-Type': 'application/json'
            }
            
            # Simular llamada a API
            response = {
                'status_code': 200,
                'data': {'totalsForAllResults': {'ga:users': '1000', 'ga:sessions': '1500'}}
            }
            
            if response['status_code'] == 200:
                return {'success': True, 'message': 'Analytics connection successful', 'data': response['data']}
            else:
                return {'success': False, 'error': 'Analytics connection failed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_ai_connection(self, integration_name: str, config: Dict) -> Dict:
        """Probar conexión de IA"""
        try:
            # Simular prueba de conexión IA
            headers = {
                'Authorization': f"Bearer {config.get('api_key', 'test_key')}",
                'Content-Type': 'application/json'
            }
            
            # Simular llamada a API
            response = {
                'status_code': 200,
                'data': {'id': 'chatcmpl-test', 'object': 'chat.completion', 'created': 1234567890}
            }
            
            if response['status_code'] == 200:
                return {'success': True, 'message': 'AI connection successful', 'data': response['data']}
            else:
                return {'success': False, 'error': 'AI connection failed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def sync_data(self, integration_name: str, sync_type: str = 'full') -> Dict:
        """Sincronizar datos de integración"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT config FROM integrations WHERE name = ? AND status = "active"', (integration_name,))
            result = cursor.fetchone()
            
            if not result:
                return {'success': False, 'error': 'Integration not found or inactive'}
            
            config = json.loads(result[0])
            integration_config = self.integrations[integration_name]
            
            # Simular sincronización de datos
            sync_data = self.simulate_data_sync(integration_name, sync_type)
            
            # Actualizar timestamp de última sincronización
            cursor.execute('UPDATE integrations SET last_sync = ? WHERE name = ?', 
                         (datetime.now().isoformat(), integration_name))
            conn.commit()
            conn.close()
            
            # Log de sincronización
            self.log_integration_event(integration_name, 'sync', 
                                     f'Data sync completed: {len(sync_data)} records', 'success', sync_data)
            
            return {
                'success': True, 
                'message': f'Data sync completed successfully',
                'records_synced': len(sync_data),
                'data': sync_data
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def simulate_data_sync(self, integration_name: str, sync_type: str) -> List[Dict]:
        """Simular sincronización de datos"""
        # Generar datos de ejemplo según el tipo de integración
        if 'crm' in integration_name:
            return [
                {'id': f'lead_{i}', 'name': f'Lead {i}', 'email': f'lead{i}@example.com', 'status': 'New'}
                for i in range(1, 21)
            ]
        elif 'email' in integration_name:
            return [
                {'id': f'subscriber_{i}', 'email': f'user{i}@example.com', 'status': 'subscribed', 'list_id': 'list123'}
                for i in range(1, 51)
            ]
        elif 'social' in integration_name:
            return [
                {'id': f'connection_{i}', 'name': f'Connection {i}', 'company': f'Company {i}', 'position': 'Manager'}
                for i in range(1, 31)
            ]
        elif 'analytics' in integration_name:
            return [
                {'date': f'2024-01-{i:02d}', 'users': 1000 + i*10, 'sessions': 1500 + i*15, 'pageviews': 3000 + i*30}
                for i in range(1, 16)
            ]
        else:
            return []
    
    def create_automation(self, name: str, trigger_type: str, trigger_config: Dict, 
                         action_type: str, action_config: Dict) -> Dict:
        """Crear nueva automatización"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO automations (name, trigger_type, trigger_config, action_type, action_config, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, trigger_type, json.dumps(trigger_config), action_type, 
                  json.dumps(action_config), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': f'Automation {name} created successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def execute_automation(self, automation_name: str) -> Dict:
        """Ejecutar automatización"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT trigger_type, trigger_config, action_type, action_config, execution_count
                FROM automations WHERE name = ? AND status = 'active'
            ''', (automation_name,))
            
            result = cursor.fetchone()
            if not result:
                return {'success': False, 'error': 'Automation not found or inactive'}
            
            trigger_type, trigger_config, action_type, action_config, execution_count = result
            
            # Ejecutar acción
            action_result = self.execute_action(action_type, json.loads(action_config))
            
            # Actualizar contador de ejecución
            cursor.execute('''
                UPDATE automations 
                SET last_executed = ?, execution_count = ?
                WHERE name = ?
            ''', (datetime.now().isoformat(), execution_count + 1, automation_name))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': f'Automation {automation_name} executed successfully',
                'action_result': action_result
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def execute_action(self, action_type: str, action_config: Dict) -> Dict:
        """Ejecutar acción de automatización"""
        if action_type == 'send_email':
            return self.send_email_action(action_config)
        elif action_type == 'create_content':
            return self.create_content_action(action_config)
        elif action_type == 'update_crm':
            return self.update_crm_action(action_config)
        elif action_type == 'trigger_webhook':
            return self.trigger_webhook_action(action_config)
        elif action_type == 'update_consciousness':
            return self.update_consciousness_action(action_config)
        else:
            return {'success': False, 'error': 'Unknown action type'}
    
    def send_email_action(self, config: Dict) -> Dict:
        """Acción: Enviar email"""
        # Simular envío de email
        return {
            'success': True,
            'message': f"Email sent to {config.get('recipient', 'user@example.com')}",
            'subject': config.get('subject', 'Automated Email'),
            'template': config.get('template', 'default')
        }
    
    def create_content_action(self, config: Dict) -> Dict:
        """Acción: Crear contenido"""
        # Simular creación de contenido
        return {
            'success': True,
            'message': 'Content created successfully',
            'content_type': config.get('content_type', 'blog_post'),
            'ai_model': config.get('ai_model', 'gpt-4'),
            'quality_score': 87.5
        }
    
    def update_crm_action(self, config: Dict) -> Dict:
        """Acción: Actualizar CRM"""
        # Simular actualización de CRM
        return {
            'success': True,
            'message': 'CRM updated successfully',
            'record_id': config.get('record_id', 'lead_123'),
            'fields_updated': config.get('fields', [])
        }
    
    def trigger_webhook_action(self, config: Dict) -> Dict:
        """Acción: Disparar webhook"""
        # Simular disparo de webhook
        return {
            'success': True,
            'message': 'Webhook triggered successfully',
            'url': config.get('url', 'https://example.com/webhook'),
            'payload': config.get('payload', {})
        }
    
    def update_consciousness_action(self, config: Dict) -> Dict:
        """Acción: Actualizar conciencia"""
        # Simular actualización de conciencia
        return {
            'success': True,
            'message': 'Consciousness updated successfully',
            'user_id': config.get('user_id', 'user_123'),
            'consciousness_increase': config.get('increase', 2.5)
        }
    
    def setup_webhook(self, name: str, url: str, events: List[str], secret: str = None) -> Dict:
        """Configurar webhook"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO webhooks (name, url, events, secret, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, url, json.dumps(events), secret or '', datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': f'Webhook {name} configured successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def trigger_webhook(self, webhook_name: str, event_data: Dict) -> Dict:
        """Disparar webhook"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT url, events, secret FROM webhooks WHERE name = ? AND status = "active"', (webhook_name,))
            result = cursor.fetchone()
            
            if not result:
                return {'success': False, 'error': 'Webhook not found or inactive'}
            
            url, events, secret = result
            events_list = json.loads(events)
            
            # Verificar si el evento está configurado
            if event_data.get('event_type') not in events_list:
                return {'success': False, 'error': 'Event type not configured for this webhook'}
            
            # Simular disparo de webhook
            payload = {
                'event_type': event_data.get('event_type'),
                'timestamp': datetime.now().isoformat(),
                'data': event_data.get('data', {}),
                'secret': secret
            }
            
            # Actualizar contador
            cursor.execute('''
                UPDATE webhooks 
                SET last_triggered = ?, trigger_count = trigger_count + 1
                WHERE name = ?
            ''', (datetime.now().isoformat(), webhook_name))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': f'Webhook {webhook_name} triggered successfully',
                'url': url,
                'payload': payload
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def log_integration_event(self, integration_name: str, event_type: str, 
                            message: str, status: str, data: Dict = None):
        """Registrar evento de integración"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener ID de integración
            cursor.execute('SELECT id FROM integrations WHERE name = ?', (integration_name,))
            result = cursor.fetchone()
            integration_id = result[0] if result else None
            
            cursor.execute('''
                INSERT INTO integration_logs (integration_id, event_type, message, status, data, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (integration_id, event_type, message, status, 
                  json.dumps(data) if data else None, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error logging integration event: {e}")
    
    def get_integration_status(self) -> Dict:
        """Obtener estado de todas las integraciones"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, type, status, last_sync, created_at
                FROM integrations
                ORDER BY created_at DESC
            ''')
            
            integrations = []
            for row in cursor.fetchall():
                integrations.append({
                    'name': row[0],
                    'type': row[1],
                    'status': row[2],
                    'last_sync': row[3],
                    'created_at': row[4]
                })
            
            conn.close()
            
            return {
                'total_integrations': len(integrations),
                'active_integrations': len([i for i in integrations if i['status'] == 'active']),
                'integrations': integrations
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_automation_status(self) -> Dict:
        """Obtener estado de todas las automatizaciones"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, trigger_type, action_type, status, last_executed, execution_count
                FROM automations
                ORDER BY created_at DESC
            ''')
            
            automations = []
            for row in cursor.fetchall():
                automations.append({
                    'name': row[0],
                    'trigger_type': row[1],
                    'action_type': row[2],
                    'status': row[3],
                    'last_executed': row[4],
                    'execution_count': row[5]
                })
            
            conn.close()
            
            return {
                'total_automations': len(automations),
                'active_automations': len([a for a in automations if a['status'] == 'active']),
                'automations': automations
            }
            
        except Exception as e:
            return {'error': str(e)}

def main():
    integration = IntegrationAutomation()
    
    print("🔗 Sistema de Integración y Automatización")
    print("=" * 50)
    print("1. Configurar integración")
    print("2. Probar integración")
    print("3. Sincronizar datos")
    print("4. Crear automatización")
    print("5. Ejecutar automatización")
    print("6. Configurar webhook")
    print("7. Disparar webhook")
    print("8. Ver estado de integraciones")
    print("9. Ver estado de automatizaciones")
    print("10. Salir")
    
    while True:
        choice = input("\nSeleccione una opción (1-10): ").strip()
        
        if choice == '1':
            print("\nIntegraciones disponibles:")
            for name, config in integration.integrations.items():
                print(f"  • {name}: {config['name']} ({config['type']})")
            
            integration_name = input("Nombre de integración: ").strip()
            if integration_name in integration.integrations:
                # Simular configuración
                config = {
                    'api_key': 'test_api_key_123',
                    'access_token': 'test_access_token_456',
                    'base_url': 'https://api.example.com'
                }
                
                result = integration.setup_integration(integration_name, config)
                print(f"✅ {result['message']}" if result['success'] else f"❌ {result['error']}")
            else:
                print("❌ Integración no soportada")
        
        elif choice == '2':
            integration_name = input("Nombre de integración a probar: ").strip()
            result = integration.test_integration(integration_name)
            print(f"✅ {result['message']}" if result['success'] else f"❌ {result['error']}")
        
        elif choice == '3':
            integration_name = input("Nombre de integración a sincronizar: ").strip()
            sync_type = input("Tipo de sincronización (full/incremental): ").strip() or 'full'
            result = integration.sync_data(integration_name, sync_type)
            print(f"✅ {result['message']}" if result['success'] else f"❌ {result['error']}")
            if result['success']:
                print(f"   Registros sincronizados: {result['records_synced']}")
        
        elif choice == '4':
            name = input("Nombre de automatización: ").strip()
            print("Tipos de trigger disponibles: schedule, event, webhook, manual")
            trigger_type = input("Tipo de trigger: ").strip()
            trigger_config = {'schedule': '0 9 * * *', 'event': 'user_registered'}
            print("Tipos de acción disponibles: send_email, create_content, update_crm, trigger_webhook, update_consciousness")
            action_type = input("Tipo de acción: ").strip()
            action_config = {'recipient': 'user@example.com', 'template': 'welcome'}
            
            result = integration.create_automation(name, trigger_type, trigger_config, action_type, action_config)
            print(f"✅ {result['message']}" if result['success'] else f"❌ {result['error']}")
        
        elif choice == '5':
            automation_name = input("Nombre de automatización a ejecutar: ").strip()
            result = integration.execute_automation(automation_name)
            print(f"✅ {result['message']}" if result['success'] else f"❌ {result['error']}")
        
        elif choice == '6':
            name = input("Nombre del webhook: ").strip()
            url = input("URL del webhook: ").strip()
            events = input("Eventos (separados por coma): ").strip().split(',')
            secret = input("Secret (opcional): ").strip()
            
            result = integration.setup_webhook(name, url, events, secret)
            print(f"✅ {result['message']}" if result['success'] else f"❌ {result['error']}")
        
        elif choice == '7':
            webhook_name = input("Nombre del webhook: ").strip()
            event_data = {
                'event_type': input("Tipo de evento: ").strip(),
                'data': {'test': 'data'}
            }
            
            result = integration.trigger_webhook(webhook_name, event_data)
            print(f"✅ {result['message']}" if result['success'] else f"❌ {result['error']}")
        
        elif choice == '8':
            status = integration.get_integration_status()
            print(f"\n📊 Estado de Integraciones:")
            print(f"  Total: {status['total_integrations']}")
            print(f"  Activas: {status['active_integrations']}")
            print(f"\nIntegraciones:")
            for integration in status['integrations']:
                print(f"  • {integration['name']} ({integration['type']}) - {integration['status']}")
        
        elif choice == '9':
            status = integration.get_automation_status()
            print(f"\n🤖 Estado de Automatizaciones:")
            print(f"  Total: {status['total_automations']}")
            print(f"  Activas: {status['active_automations']}")
            print(f"\nAutomatizaciones:")
            for automation in status['automations']:
                print(f"  • {automation['name']} - {automation['status']} ({automation['execution_count']} ejecuciones)")
        
        elif choice == '10':
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()


