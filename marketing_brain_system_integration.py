#!/usr/bin/env python3
"""
🔗 MARKETING BRAIN SYSTEM INTEGRATION
Framework de Integración Completo del Sistema
Incluye APIs externas, servicios de terceros, webhooks y sincronización de datos
"""

import json
import asyncio
import aiohttp
import requests
import websockets
import ssl
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
from enum import Enum
import uuid
import hashlib
import hmac
import base64
from urllib.parse import urlencode, urlparse
import xml.etree.ElementTree as ET
import csv
import sqlite3
import redis
import pymongo
from sqlalchemy import create_engine, text
import schedule
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import pickle
import gzip
import zlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import jwt
from functools import wraps
import retrying
from tenacity import retry, stop_after_attempt, wait_exponential

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

logger = logging.getLogger(__name__)

class IntegrationType(Enum):
    """Tipos de integración"""
    API_REST = "api_rest"
    API_GRAPHQL = "api_graphql"
    WEBHOOK = "webhook"
    WEBSOCKET = "websocket"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    EMAIL = "email"
    SMS = "sms"
    SOCIAL_MEDIA = "social_media"
    CRM = "crm"
    ANALYTICS = "analytics"
    PAYMENT = "payment"
    CLOUD_STORAGE = "cloud_storage"

class DataFormat(Enum):
    """Formatos de datos"""
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    YAML = "yaml"
    PROTOBUF = "protobuf"
    AVRO = "avro"
    PARQUET = "parquet"
    BINARY = "binary"

class AuthenticationMethod(Enum):
    """Métodos de autenticación"""
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    JWT = "jwt"
    HMAC = "hmac"
    CERTIFICATE = "certificate"
    NONE = "none"

@dataclass
class IntegrationConfig:
    """Configuración de integración"""
    integration_id: str
    name: str
    integration_type: IntegrationType
    endpoint: str
    authentication: AuthenticationMethod
    credentials: Dict[str, Any]
    data_format: DataFormat
    rate_limit: Dict[str, int]
    timeout: int
    retry_config: Dict[str, Any]
    headers: Dict[str, str]
    enabled: bool
    created_at: str
    updated_at: str

@dataclass
class DataMapping:
    """Mapeo de datos"""
    source_field: str
    target_field: str
    transformation: Optional[str]
    required: bool
    default_value: Any = None

@dataclass
class IntegrationEvent:
    """Evento de integración"""
    event_id: str
    integration_id: str
    event_type: str
    data: Dict[str, Any]
    timestamp: str
    status: str
    error_message: Optional[str] = None
    retry_count: int = 0

@dataclass
class WebhookConfig:
    """Configuración de webhook"""
    webhook_id: str
    name: str
    url: str
    events: List[str]
    secret: str
    headers: Dict[str, str]
    enabled: bool
    created_at: str

@dataclass
class SyncJob:
    """Trabajo de sincronización"""
    job_id: str
    source_integration: str
    target_integration: str
    data_mapping: List[DataMapping]
    schedule: str
    last_run: Optional[str]
    next_run: Optional[str]
    status: str
    error_count: int = 0

class MarketingBrainSystemIntegration:
    """
    Framework de Integración Completo del Sistema
    Incluye APIs externas, servicios de terceros, webhooks y sincronización de datos
    """
    
    def __init__(self):
        self.integrations = {}
        self.webhooks = {}
        self.sync_jobs = {}
        self.event_queue = queue.Queue()
        self.data_cache = {}
        
        # Configuración
        self.config = self._load_config()
        
        # Clientes HTTP
        self.http_session = None
        self.websocket_connections = {}
        
        # Bases de datos
        self.databases = {}
        
        # Threads y ejecutores
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.scheduler_thread = None
        self.event_processor_thread = None
        
        # Estado del sistema
        self.is_running = False
        
        # Métricas
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'webhook_deliveries': 0,
            'sync_jobs_completed': 0,
            'data_transferred': 0
        }
        
        logger.info("🔗 Marketing Brain System Integration initialized successfully")
    
    def _load_config(self) -> Dict[str, Any]:
        """Cargar configuración del sistema de integración"""
        return {
            'general': {
                'max_retries': 3,
                'default_timeout': 30,
                'rate_limit_window': 60,
                'cache_ttl': 3600,
                'encryption_key': 'default_key_change_in_production'
            },
            'integrations': {
                'max_concurrent': 10,
                'health_check_interval': 300,
                'auto_retry_failed': True,
                'circuit_breaker_threshold': 5
            },
            'webhooks': {
                'max_delivery_attempts': 3,
                'delivery_timeout': 10,
                'signature_validation': True,
                'async_delivery': True
            },
            'sync': {
                'batch_size': 1000,
                'max_batch_processing_time': 300,
                'incremental_sync': True,
                'conflict_resolution': 'source_wins'
            },
            'security': {
                'encrypt_sensitive_data': True,
                'validate_ssl_certificates': True,
                'log_sensitive_operations': False,
                'audit_trail': True
            }
        }
    
    async def start_integration_system(self):
        """Iniciar sistema de integración"""
        logger.info("🚀 Starting Marketing Brain System Integration...")
        
        self.is_running = True
        
        # Inicializar sesión HTTP
        self.http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config['general']['default_timeout']),
            connector=aiohttp.TCPConnector(limit=100, limit_per_host=30)
        )
        
        # Cargar integraciones existentes
        await self._load_integrations()
        
        # Iniciar threads
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        self.event_processor_thread = threading.Thread(target=self._event_processor_loop, daemon=True)
        self.event_processor_thread.start()
        
        # Inicializar bases de datos
        await self._initialize_databases()
        
        # Configurar integraciones por defecto
        await self._setup_default_integrations()
        
        logger.info("✅ Integration system started successfully")
    
    async def stop_integration_system(self):
        """Detener sistema de integración"""
        logger.info("🛑 Stopping Marketing Brain System Integration...")
        
        self.is_running = False
        
        # Cerrar sesión HTTP
        if self.http_session:
            await self.http_session.close()
        
        # Cerrar conexiones WebSocket
        for connection in self.websocket_connections.values():
            await connection.close()
        
        # Cerrar bases de datos
        for db in self.databases.values():
            if hasattr(db, 'close'):
                db.close()
        
        # Cerrar ejecutor
        self.executor.shutdown(wait=True)
        
        logger.info("✅ Integration system stopped successfully")
    
    async def _load_integrations(self):
        """Cargar integraciones desde configuración"""
        try:
            # Cargar desde archivo de configuración
            config_file = Path("integration_config.json")
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    integrations_data = json.load(f)
                
                for integration_data in integrations_data.get('integrations', []):
                    integration = IntegrationConfig(**integration_data)
                    self.integrations[integration.integration_id] = integration
                
                logger.info(f"Loaded {len(self.integrations)} integrations from config")
            else:
                logger.info("No integration config file found, using defaults")
                
        except Exception as e:
            logger.error(f"Error loading integrations: {e}")
    
    async def _initialize_databases(self):
        """Inicializar bases de datos"""
        try:
            # SQLite para metadatos
            self.databases['sqlite'] = sqlite3.connect('integration_metadata.db', check_same_thread=False)
            
            # Redis para cache
            self.databases['redis'] = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            
            # MongoDB para documentos (opcional)
            try:
                self.databases['mongodb'] = pymongo.MongoClient('mongodb://localhost:27017/')
                self.databases['mongodb'].admin.command('ping')
                logger.info("MongoDB connection established")
            except Exception as e:
                logger.warning(f"MongoDB not available: {e}")
                self.databases['mongodb'] = None
            
            # Crear tablas necesarias
            await self._create_database_tables()
            
        except Exception as e:
            logger.error(f"Error initializing databases: {e}")
    
    async def _create_database_tables(self):
        """Crear tablas de base de datos"""
        try:
            cursor = self.databases['sqlite'].cursor()
            
            # Tabla de eventos de integración
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS integration_events (
                    event_id TEXT PRIMARY KEY,
                    integration_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL,
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0
                )
            ''')
            
            # Tabla de trabajos de sincronización
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_jobs (
                    job_id TEXT PRIMARY KEY,
                    source_integration TEXT NOT NULL,
                    target_integration TEXT NOT NULL,
                    data_mapping TEXT NOT NULL,
                    schedule TEXT NOT NULL,
                    last_run TEXT,
                    next_run TEXT,
                    status TEXT NOT NULL,
                    error_count INTEGER DEFAULT 0
                )
            ''')
            
            # Tabla de métricas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS integration_metrics (
                    metric_name TEXT PRIMARY KEY,
                    metric_value REAL NOT NULL,
                    timestamp TEXT NOT NULL
                )
            ''')
            
            self.databases['sqlite'].commit()
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
    
    async def _setup_default_integrations(self):
        """Configurar integraciones por defecto"""
        default_integrations = [
            {
                'integration_id': 'google_analytics',
                'name': 'Google Analytics',
                'integration_type': IntegrationType.API_REST,
                'endpoint': 'https://analyticsreporting.googleapis.com/v4/reports:batchGet',
                'authentication': AuthenticationMethod.OAUTH2,
                'credentials': {'client_id': '', 'client_secret': '', 'refresh_token': ''},
                'data_format': DataFormat.JSON,
                'rate_limit': {'requests_per_minute': 100, 'requests_per_day': 10000},
                'timeout': 30,
                'retry_config': {'max_retries': 3, 'backoff_factor': 2},
                'headers': {'Content-Type': 'application/json'},
                'enabled': False,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            },
            {
                'integration_id': 'facebook_marketing',
                'name': 'Facebook Marketing API',
                'integration_type': IntegrationType.API_REST,
                'endpoint': 'https://graph.facebook.com/v18.0',
                'authentication': AuthenticationMethod.OAUTH2,
                'credentials': {'access_token': '', 'app_id': '', 'app_secret': ''},
                'data_format': DataFormat.JSON,
                'rate_limit': {'requests_per_hour': 200, 'requests_per_day': 4800},
                'timeout': 30,
                'retry_config': {'max_retries': 3, 'backoff_factor': 2},
                'headers': {'Content-Type': 'application/json'},
                'enabled': False,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            },
            {
                'integration_id': 'salesforce_crm',
                'name': 'Salesforce CRM',
                'integration_type': IntegrationType.API_REST,
                'endpoint': 'https://your-instance.salesforce.com/services/data/v58.0',
                'authentication': AuthenticationMethod.OAUTH2,
                'credentials': {'client_id': '', 'client_secret': '', 'username': '', 'password': ''},
                'data_format': DataFormat.JSON,
                'rate_limit': {'requests_per_minute': 1000, 'requests_per_day': 15000},
                'timeout': 30,
                'retry_config': {'max_retries': 3, 'backoff_factor': 2},
                'headers': {'Content-Type': 'application/json'},
                'enabled': False,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            },
            {
                'integration_id': 'mailchimp_email',
                'name': 'Mailchimp Email Marketing',
                'integration_type': IntegrationType.API_REST,
                'endpoint': 'https://us1.api.mailchimp.com/3.0',
                'authentication': AuthenticationMethod.API_KEY,
                'credentials': {'api_key': '', 'server_prefix': 'us1'},
                'data_format': DataFormat.JSON,
                'rate_limit': {'requests_per_minute': 10, 'requests_per_hour': 1000},
                'timeout': 30,
                'retry_config': {'max_retries': 3, 'backoff_factor': 2},
                'headers': {'Content-Type': 'application/json'},
                'enabled': False,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            },
            {
                'integration_id': 'stripe_payments',
                'name': 'Stripe Payment Processing',
                'integration_type': IntegrationType.API_REST,
                'endpoint': 'https://api.stripe.com/v1',
                'authentication': AuthenticationMethod.API_KEY,
                'credentials': {'secret_key': '', 'publishable_key': ''},
                'data_format': DataFormat.JSON,
                'rate_limit': {'requests_per_second': 100, 'requests_per_day': 100000},
                'timeout': 30,
                'retry_config': {'max_retries': 3, 'backoff_factor': 2},
                'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
                'enabled': False,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        ]
        
        for integration_data in default_integrations:
            integration = IntegrationConfig(**integration_data)
            self.integrations[integration.integration_id] = integration
        
        logger.info(f"Setup {len(default_integrations)} default integrations")
    
    def _scheduler_loop(self):
        """Loop del programador de tareas"""
        while self.is_running:
            try:
                # Procesar trabajos de sincronización programados
                current_time = datetime.now()
                
                for job_id, job in self.sync_jobs.items():
                    if job.status == 'active' and job.next_run:
                        next_run_time = datetime.fromisoformat(job.next_run)
                        if current_time >= next_run_time:
                            # Ejecutar trabajo de sincronización
                            asyncio.run(self._execute_sync_job(job))
                
                time.sleep(60)  # Verificar cada minuto
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)
    
    def _event_processor_loop(self):
        """Loop del procesador de eventos"""
        while self.is_running:
            try:
                # Procesar eventos de la cola
                if not self.event_queue.empty():
                    event = self.event_queue.get_nowait()
                    asyncio.run(self._process_integration_event(event))
                
                time.sleep(1)  # Verificar cada segundo
                
            except queue.Empty:
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in event processor loop: {e}")
                time.sleep(1)
    
    async def add_integration(self, integration_config: IntegrationConfig) -> bool:
        """Agregar nueva integración"""
        try:
            # Validar configuración
            if not await self._validate_integration_config(integration_config):
                return False
            
            # Encriptar credenciales sensibles
            if self.config['security']['encrypt_sensitive_data']:
                integration_config.credentials = await self._encrypt_credentials(
                    integration_config.credentials
                )
            
            # Agregar a integraciones
            self.integrations[integration_config.integration_id] = integration_config
            
            # Probar conexión
            if await self._test_integration_connection(integration_config):
                logger.info(f"Integration {integration_config.name} added successfully")
                return True
            else:
                logger.warning(f"Integration {integration_config.name} added but connection test failed")
                return True  # Agregar de todos modos para configuración manual
                
        except Exception as e:
            logger.error(f"Error adding integration: {e}")
            return False
    
    async def _validate_integration_config(self, config: IntegrationConfig) -> bool:
        """Validar configuración de integración"""
        try:
            # Validar campos requeridos
            if not config.integration_id or not config.name or not config.endpoint:
                logger.error("Missing required fields in integration config")
                return False
            
            # Validar URL del endpoint
            parsed_url = urlparse(config.endpoint)
            if not parsed_url.scheme or not parsed_url.netloc:
                logger.error("Invalid endpoint URL")
                return False
            
            # Validar método de autenticación
            if config.authentication != AuthenticationMethod.NONE:
                if not config.credentials:
                    logger.error("Credentials required for authentication method")
                    return False
            
            # Validar límites de tasa
            if config.rate_limit:
                required_fields = ['requests_per_minute', 'requests_per_hour', 'requests_per_day']
                if not any(field in config.rate_limit for field in required_fields):
                    logger.error("Rate limit must specify at least one time window")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating integration config: {e}")
            return False
    
    async def _encrypt_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Encriptar credenciales sensibles"""
        try:
            # Generar clave de encriptación
            key = self._derive_encryption_key()
            fernet = Fernet(key)
            
            encrypted_credentials = {}
            for key, value in credentials.items():
                if isinstance(value, str) and value:
                    encrypted_value = fernet.encrypt(value.encode())
                    encrypted_credentials[key] = base64.b64encode(encrypted_value).decode()
                else:
                    encrypted_credentials[key] = value
            
            return encrypted_credentials
            
        except Exception as e:
            logger.error(f"Error encrypting credentials: {e}")
            return credentials
    
    def _derive_encryption_key(self) -> bytes:
        """Derivar clave de encriptación"""
        password = self.config['general']['encryption_key'].encode()
        salt = b'marketing_brain_salt'  # En producción, usar salt único
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    async def _test_integration_connection(self, config: IntegrationConfig) -> bool:
        """Probar conexión de integración"""
        try:
            if config.integration_type == IntegrationType.API_REST:
                return await self._test_rest_api_connection(config)
            elif config.integration_type == IntegrationType.WEBSOCKET:
                return await self._test_websocket_connection(config)
            elif config.integration_type == IntegrationType.DATABASE:
                return await self._test_database_connection(config)
            else:
                logger.warning(f"Connection test not implemented for {config.integration_type}")
                return True
                
        except Exception as e:
            logger.error(f"Error testing integration connection: {e}")
            return False
    
    async def _test_rest_api_connection(self, config: IntegrationConfig) -> bool:
        """Probar conexión API REST"""
        try:
            headers = config.headers.copy()
            
            # Agregar autenticación
            if config.authentication == AuthenticationMethod.API_KEY:
                headers['Authorization'] = f"Bearer {config.credentials.get('api_key', '')}"
            elif config.authentication == AuthenticationMethod.BEARER_TOKEN:
                headers['Authorization'] = f"Bearer {config.credentials.get('access_token', '')}"
            
            # Hacer request de prueba (usualmente GET a endpoint de health o info)
            test_url = config.endpoint.rstrip('/') + '/health'
            
            async with self.http_session.get(test_url, headers=headers) as response:
                if response.status in [200, 201, 204]:
                    return True
                else:
                    logger.warning(f"API test returned status {response.status}")
                    return False
                    
        except Exception as e:
            logger.warning(f"API connection test failed: {e}")
            return False
    
    async def _test_websocket_connection(self, config: IntegrationConfig) -> bool:
        """Probar conexión WebSocket"""
        try:
            # Implementar prueba de WebSocket
            # Por simplicidad, asumir que funciona
            return True
            
        except Exception as e:
            logger.warning(f"WebSocket connection test failed: {e}")
            return False
    
    async def _test_database_connection(self, config: IntegrationConfig) -> bool:
        """Probar conexión de base de datos"""
        try:
            # Implementar prueba de base de datos
            # Por simplicidad, asumir que funciona
            return True
            
        except Exception as e:
            logger.warning(f"Database connection test failed: {e}")
            return False
    
    async def make_api_request(self, integration_id: str, method: str, endpoint: str,
                              data: Optional[Dict[str, Any]] = None,
                              params: Optional[Dict[str, Any]] = None,
                              headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Hacer request a API externa"""
        try:
            if integration_id not in self.integrations:
                raise ValueError(f"Integration {integration_id} not found")
            
            integration = self.integrations[integration_id]
            
            if not integration.enabled:
                raise ValueError(f"Integration {integration_id} is disabled")
            
            # Verificar límites de tasa
            if not await self._check_rate_limit(integration_id):
                raise Exception(f"Rate limit exceeded for integration {integration_id}")
            
            # Construir URL completa
            full_url = integration.endpoint.rstrip('/') + '/' + endpoint.lstrip('/')
            
            # Preparar headers
            request_headers = integration.headers.copy()
            if headers:
                request_headers.update(headers)
            
            # Agregar autenticación
            await self._add_authentication(integration, request_headers)
            
            # Preparar datos
            request_data = None
            if data:
                if integration.data_format == DataFormat.JSON:
                    request_data = json.dumps(data)
                    request_headers['Content-Type'] = 'application/json'
                elif integration.data_format == DataFormat.XML:
                    request_data = self._dict_to_xml(data)
                    request_headers['Content-Type'] = 'application/xml'
                else:
                    request_data = data
            
            # Hacer request con retry
            response_data = await self._make_request_with_retry(
                method, full_url, request_headers, request_data, params, integration
            )
            
            # Actualizar métricas
            self.metrics['total_requests'] += 1
            self.metrics['successful_requests'] += 1
            
            return response_data
            
        except Exception as e:
            # Actualizar métricas de error
            self.metrics['total_requests'] += 1
            self.metrics['failed_requests'] += 1
            
            logger.error(f"API request failed: {e}")
            raise
    
    async def _check_rate_limit(self, integration_id: str) -> bool:
        """Verificar límites de tasa"""
        try:
            integration = self.integrations[integration_id]
            rate_limits = integration.rate_limit
            
            # Implementar verificación de límites de tasa
            # Por simplicidad, siempre permitir
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True
    
    async def _add_authentication(self, integration: IntegrationConfig, headers: Dict[str, str]):
        """Agregar autenticación a headers"""
        try:
            if integration.authentication == AuthenticationMethod.API_KEY:
                api_key = integration.credentials.get('api_key', '')
                if api_key:
                    headers['Authorization'] = f"Bearer {api_key}"
            
            elif integration.authentication == AuthenticationMethod.BEARER_TOKEN:
                token = integration.credentials.get('access_token', '')
                if token:
                    headers['Authorization'] = f"Bearer {token}"
            
            elif integration.authentication == AuthenticationMethod.BASIC_AUTH:
                username = integration.credentials.get('username', '')
                password = integration.credentials.get('password', '')
                if username and password:
                    auth_string = base64.b64encode(f"{username}:{password}".encode()).decode()
                    headers['Authorization'] = f"Basic {auth_string}"
            
            elif integration.authentication == AuthenticationMethod.JWT:
                token = integration.credentials.get('jwt_token', '')
                if token:
                    headers['Authorization'] = f"Bearer {token}"
            
            elif integration.authentication == AuthenticationMethod.HMAC:
                # Implementar autenticación HMAC
                pass
            
        except Exception as e:
            logger.error(f"Error adding authentication: {e}")
    
    async def _make_request_with_retry(self, method: str, url: str, headers: Dict[str, str],
                                     data: Optional[str], params: Optional[Dict[str, Any]],
                                     integration: IntegrationConfig) -> Dict[str, Any]:
        """Hacer request con retry automático"""
        
        @retry(
            stop=stop_after_attempt(integration.retry_config.get('max_retries', 3)),
            wait=wait_exponential(multiplier=integration.retry_config.get('backoff_factor', 2))
        )
        async def _make_request():
            async with self.http_session.request(
                method, url, headers=headers, data=data, params=params
            ) as response:
                
                if response.status >= 400:
                    raise Exception(f"HTTP {response.status}: {await response.text()}")
                
                # Parsear respuesta
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    return await response.json()
                elif 'application/xml' in content_type or 'text/xml' in content_type:
                    xml_text = await response.text()
                    return self._xml_to_dict(xml_text)
                else:
                    return {'data': await response.text()}
        
        return await _make_request()
    
    def _dict_to_xml(self, data: Dict[str, Any]) -> str:
        """Convertir diccionario a XML"""
        try:
            root = ET.Element('root')
            self._dict_to_xml_recursive(data, root)
            return ET.tostring(root, encoding='unicode')
        except Exception as e:
            logger.error(f"Error converting dict to XML: {e}")
            return str(data)
    
    def _dict_to_xml_recursive(self, data: Dict[str, Any], parent: ET.Element):
        """Convertir diccionario a XML recursivamente"""
        for key, value in data.items():
            if isinstance(value, dict):
                child = ET.SubElement(parent, key)
                self._dict_to_xml_recursive(value, child)
            elif isinstance(value, list):
                for item in value:
                    child = ET.SubElement(parent, key)
                    if isinstance(item, dict):
                        self._dict_to_xml_recursive(item, child)
                    else:
                        child.text = str(item)
            else:
                child = ET.SubElement(parent, key)
                child.text = str(value)
    
    def _xml_to_dict(self, xml_text: str) -> Dict[str, Any]:
        """Convertir XML a diccionario"""
        try:
            root = ET.fromstring(xml_text)
            return self._xml_to_dict_recursive(root)
        except Exception as e:
            logger.error(f"Error converting XML to dict: {e}")
            return {'error': str(e)}
    
    def _xml_to_dict_recursive(self, element: ET.Element) -> Dict[str, Any]:
        """Convertir XML a diccionario recursivamente"""
        result = {}
        
        if element.text and element.text.strip():
            return element.text.strip()
        
        for child in element:
            child_data = self._xml_to_dict_recursive(child)
            
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result
    
    async def create_webhook(self, webhook_config: WebhookConfig) -> bool:
        """Crear webhook"""
        try:
            # Validar configuración
            if not webhook_config.url or not webhook_config.events:
                logger.error("Webhook URL and events are required")
                return False
            
            # Agregar webhook
            self.webhooks[webhook_config.webhook_id] = webhook_config
            
            logger.info(f"Webhook {webhook_config.name} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating webhook: {e}")
            return False
    
    async def trigger_webhook(self, webhook_id: str, event_type: str, data: Dict[str, Any]) -> bool:
        """Disparar webhook"""
        try:
            if webhook_id not in self.webhooks:
                logger.error(f"Webhook {webhook_id} not found")
                return False
            
            webhook = self.webhooks[webhook_id]
            
            if not webhook.enabled:
                logger.warning(f"Webhook {webhook_id} is disabled")
                return False
            
            if event_type not in webhook.events:
                logger.warning(f"Event type {event_type} not configured for webhook {webhook_id}")
                return False
            
            # Preparar payload
            payload = {
                'event_type': event_type,
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            # Agregar firma si está configurada
            if webhook.secret:
                signature = self._generate_webhook_signature(payload, webhook.secret)
                payload['signature'] = signature
            
            # Enviar webhook
            success = await self._deliver_webhook(webhook, payload)
            
            if success:
                self.metrics['webhook_deliveries'] += 1
            
            return success
            
        except Exception as e:
            logger.error(f"Error triggering webhook: {e}")
            return False
    
    def _generate_webhook_signature(self, payload: Dict[str, Any], secret: str) -> str:
        """Generar firma de webhook"""
        try:
            payload_string = json.dumps(payload, sort_keys=True)
            signature = hmac.new(
                secret.encode(),
                payload_string.encode(),
                hashlib.sha256
            ).hexdigest()
            return f"sha256={signature}"
        except Exception as e:
            logger.error(f"Error generating webhook signature: {e}")
            return ""
    
    async def _deliver_webhook(self, webhook: WebhookConfig, payload: Dict[str, Any]) -> bool:
        """Entregar webhook"""
        try:
            headers = webhook.headers.copy()
            headers['Content-Type'] = 'application/json'
            
            async with self.http_session.post(
                webhook.url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.config['webhooks']['delivery_timeout'])
            ) as response:
                
                if response.status in [200, 201, 204]:
                    logger.info(f"Webhook delivered successfully to {webhook.url}")
                    return True
                else:
                    logger.error(f"Webhook delivery failed with status {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error delivering webhook: {e}")
            return False
    
    async def create_sync_job(self, sync_job: SyncJob) -> bool:
        """Crear trabajo de sincronización"""
        try:
            # Validar integraciones
            if sync_job.source_integration not in self.integrations:
                logger.error(f"Source integration {sync_job.source_integration} not found")
                return False
            
            if sync_job.target_integration not in self.integrations:
                logger.error(f"Target integration {sync_job.target_integration} not found")
                return False
            
            # Programar trabajo
            if sync_job.schedule:
                next_run = self._calculate_next_run(sync_job.schedule)
                sync_job.next_run = next_run.isoformat()
            
            # Agregar trabajo
            self.sync_jobs[sync_job.job_id] = sync_job
            
            logger.info(f"Sync job {sync_job.job_id} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating sync job: {e}")
            return False
    
    def _calculate_next_run(self, schedule: str) -> datetime:
        """Calcular próxima ejecución"""
        try:
            # Implementar cálculo de próxima ejecución
            # Por simplicidad, agregar 1 hora
            return datetime.now() + timedelta(hours=1)
        except Exception as e:
            logger.error(f"Error calculating next run: {e}")
            return datetime.now() + timedelta(hours=1)
    
    async def _execute_sync_job(self, job: SyncJob):
        """Ejecutar trabajo de sincronización"""
        try:
            logger.info(f"Executing sync job {job.job_id}")
            
            # Obtener datos de fuente
            source_data = await self._fetch_source_data(job.source_integration)
            
            # Transformar datos
            transformed_data = await self._transform_data(source_data, job.data_mapping)
            
            # Enviar datos a destino
            success = await self._send_target_data(job.target_integration, transformed_data)
            
            if success:
                job.last_run = datetime.now().isoformat()
                job.next_run = self._calculate_next_run(job.schedule).isoformat()
                job.error_count = 0
                self.metrics['sync_jobs_completed'] += 1
                logger.info(f"Sync job {job.job_id} completed successfully")
            else:
                job.error_count += 1
                logger.error(f"Sync job {job.job_id} failed")
            
        except Exception as e:
            job.error_count += 1
            logger.error(f"Error executing sync job {job.job_id}: {e}")
    
    async def _fetch_source_data(self, integration_id: str) -> List[Dict[str, Any]]:
        """Obtener datos de integración fuente"""
        try:
            # Implementar obtención de datos
            # Por simplicidad, retornar datos de ejemplo
            return [
                {'id': 1, 'name': 'Sample Data 1', 'value': 100},
                {'id': 2, 'name': 'Sample Data 2', 'value': 200}
            ]
        except Exception as e:
            logger.error(f"Error fetching source data: {e}")
            return []
    
    async def _transform_data(self, source_data: List[Dict[str, Any]], 
                            data_mapping: List[DataMapping]) -> List[Dict[str, Any]]:
        """Transformar datos según mapeo"""
        try:
            transformed_data = []
            
            for item in source_data:
                transformed_item = {}
                
                for mapping in data_mapping:
                    source_value = item.get(mapping.source_field)
                    
                    if source_value is not None:
                        # Aplicar transformación si existe
                        if mapping.transformation:
                            transformed_value = self._apply_transformation(
                                source_value, mapping.transformation
                            )
                        else:
                            transformed_value = source_value
                        
                        transformed_item[mapping.target_field] = transformed_value
                    elif mapping.required:
                        # Usar valor por defecto si es requerido
                        transformed_item[mapping.target_field] = mapping.default_value
                
                transformed_data.append(transformed_item)
            
            return transformed_data
            
        except Exception as e:
            logger.error(f"Error transforming data: {e}")
            return []
    
    def _apply_transformation(self, value: Any, transformation: str) -> Any:
        """Aplicar transformación a valor"""
        try:
            if transformation == 'uppercase':
                return str(value).upper()
            elif transformation == 'lowercase':
                return str(value).lower()
            elif transformation == 'trim':
                return str(value).strip()
            elif transformation.startswith('format:'):
                format_string = transformation.split(':', 1)[1]
                return format_string.format(value)
            else:
                return value
        except Exception as e:
            logger.error(f"Error applying transformation: {e}")
            return value
    
    async def _send_target_data(self, integration_id: str, data: List[Dict[str, Any]]) -> bool:
        """Enviar datos a integración destino"""
        try:
            # Implementar envío de datos
            # Por simplicidad, asumir éxito
            self.metrics['data_transferred'] += len(data)
            return True
        except Exception as e:
            logger.error(f"Error sending target data: {e}")
            return False
    
    async def _process_integration_event(self, event: IntegrationEvent):
        """Procesar evento de integración"""
        try:
            # Procesar evento según tipo
            if event.event_type == 'webhook_triggered':
                await self._handle_webhook_event(event)
            elif event.event_type == 'sync_completed':
                await self._handle_sync_event(event)
            elif event.event_type == 'api_request_failed':
                await self._handle_api_error_event(event)
            else:
                logger.warning(f"Unknown event type: {event.event_type}")
            
        except Exception as e:
            logger.error(f"Error processing integration event: {e}")
    
    async def _handle_webhook_event(self, event: IntegrationEvent):
        """Manejar evento de webhook"""
        # Implementar manejo de eventos de webhook
        pass
    
    async def _handle_sync_event(self, event: IntegrationEvent):
        """Manejar evento de sincronización"""
        # Implementar manejo de eventos de sincronización
        pass
    
    async def _handle_api_error_event(self, event: IntegrationEvent):
        """Manejar evento de error de API"""
        # Implementar manejo de errores de API
        pass
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema de integración"""
        return {
            'system_status': 'running' if self.is_running else 'stopped',
            'total_integrations': len(self.integrations),
            'active_integrations': len([i for i in self.integrations.values() if i.enabled]),
            'total_webhooks': len(self.webhooks),
            'active_webhooks': len([w for w in self.webhooks.values() if w.enabled]),
            'total_sync_jobs': len(self.sync_jobs),
            'active_sync_jobs': len([j for j in self.sync_jobs.values() if j.status == 'active']),
            'metrics': self.metrics,
            'last_updated': datetime.now().isoformat()
        }
    
    def export_integration_data(self, export_dir: str = "integration_data") -> Dict[str, str]:
        """Exportar datos de integración"""
        Path(export_dir).mkdir(exist_ok=True)
        exported_files = {}
        
        # Exportar configuraciones de integración
        integrations_data = {
            integration_id: asdict(integration)
            for integration_id, integration in self.integrations.items()
        }
        integrations_path = Path(export_dir) / f"integrations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(integrations_path, 'w', encoding='utf-8') as f:
            json.dump(integrations_data, f, indent=2, ensure_ascii=False)
        exported_files['integrations'] = str(integrations_path)
        
        # Exportar configuraciones de webhooks
        webhooks_data = {
            webhook_id: asdict(webhook)
            for webhook_id, webhook in self.webhooks.items()
        }
        webhooks_path = Path(export_dir) / f"webhooks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(webhooks_path, 'w', encoding='utf-8') as f:
            json.dump(webhooks_data, f, indent=2, ensure_ascii=False)
        exported_files['webhooks'] = str(webhooks_path)
        
        # Exportar trabajos de sincronización
        sync_jobs_data = {
            job_id: asdict(job)
            for job_id, job in self.sync_jobs.items()
        }
        sync_jobs_path = Path(export_dir) / f"sync_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(sync_jobs_path, 'w', encoding='utf-8') as f:
            json.dump(sync_jobs_data, f, indent=2, ensure_ascii=False)
        exported_files['sync_jobs'] = str(sync_jobs_path)
        
        # Exportar métricas
        metrics_path = Path(export_dir) / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)
        exported_files['metrics'] = str(metrics_path)
        
        logger.info(f"📦 Exported integration data to {export_dir}")
        return exported_files


def main():
    """Función principal para demostrar el Sistema de Integración"""
    print("🔗 MARKETING BRAIN SYSTEM INTEGRATION")
    print("=" * 60)
    
    # Crear sistema de integración
    integration_system = MarketingBrainSystemIntegration()
    
    async def run_demo():
        print(f"\n🚀 INICIANDO SISTEMA DE INTEGRACIÓN...")
        
        # Iniciar sistema
        await integration_system.start_integration_system()
        
        # Mostrar estado inicial
        status = integration_system.get_integration_status()
        print(f"\n📊 ESTADO DEL SISTEMA:")
        print(f"   • Estado: {status['system_status']}")
        print(f"   • Integraciones totales: {status['total_integrations']}")
        print(f"   • Integraciones activas: {status['active_integrations']}")
        print(f"   • Webhooks totales: {status['total_webhooks']}")
        print(f"   • Trabajos de sincronización: {status['total_sync_jobs']}")
        
        # Mostrar integraciones disponibles
        print(f"\n🔌 INTEGRACIONES DISPONIBLES:")
        for integration_id, integration in integration_system.integrations.items():
            status_icon = "✅" if integration.enabled else "❌"
            print(f"   {status_icon} {integration.name} ({integration.integration_type.value})")
            print(f"      • Endpoint: {integration.endpoint}")
            print(f"      • Autenticación: {integration.authentication.value}")
            print(f"      • Formato: {integration.data_format.value}")
        
        # Simular request a API
        print(f"\n🌐 SIMULANDO REQUEST A API...")
        try:
            # Intentar hacer request a Google Analytics (fallará por falta de credenciales)
            response = await integration_system.make_api_request(
                integration_id='google_analytics',
                method='GET',
                endpoint='reports',
                params={'test': 'true'}
            )
            print(f"   ✅ Request exitoso: {response}")
        except Exception as e:
            print(f"   ⚠️ Request falló (esperado): {str(e)[:100]}...")
        
        # Crear webhook de ejemplo
        print(f"\n🎣 CREANDO WEBHOOK DE EJEMPLO...")
        webhook_config = WebhookConfig(
            webhook_id=str(uuid.uuid4()),
            name='Test Webhook',
            url='https://httpbin.org/post',
            events=['test_event'],
            secret='test_secret',
            headers={'User-Agent': 'MarketingBrain/1.0'},
            enabled=True,
            created_at=datetime.now().isoformat()
        )
        
        webhook_created = await integration_system.create_webhook(webhook_config)
        if webhook_created:
            print(f"   ✅ Webhook creado: {webhook_config.name}")
            
            # Disparar webhook
            webhook_triggered = await integration_system.trigger_webhook(
                webhook_id=webhook_config.webhook_id,
                event_type='test_event',
                data={'message': 'Test webhook from Marketing Brain System'}
            )
            
            if webhook_triggered:
                print(f"   ✅ Webhook disparado exitosamente")
            else:
                print(f"   ❌ Error al disparar webhook")
        else:
            print(f"   ❌ Error al crear webhook")
        
        # Crear trabajo de sincronización
        print(f"\n🔄 CREANDO TRABAJO DE SINCRONIZACIÓN...")
        data_mapping = [
            DataMapping('id', 'external_id', None, True),
            DataMapping('name', 'title', 'uppercase', True),
            DataMapping('value', 'amount', None, False, 0)
        ]
        
        sync_job = SyncJob(
            job_id=str(uuid.uuid4()),
            source_integration='google_analytics',
            target_integration='salesforce_crm',
            data_mapping=data_mapping,
            schedule='0 */6 * * *',  # Cada 6 horas
            last_run=None,
            next_run=None,
            status='active'
        )
        
        sync_created = await integration_system.create_sync_job(sync_job)
        if sync_created:
            print(f"   ✅ Trabajo de sincronización creado: {sync_job.job_id}")
            print(f"      • Fuente: {sync_job.source_integration}")
            print(f"      • Destino: {sync_job.target_integration}")
            print(f"      • Mapeos: {len(sync_job.data_mapping)}")
            print(f"      • Programación: {sync_job.schedule}")
        else:
            print(f"   ❌ Error al crear trabajo de sincronización")
        
        # Mostrar métricas finales
        print(f"\n📈 MÉTRICAS DEL SISTEMA:")
        final_status = integration_system.get_integration_status()
        metrics = final_status['metrics']
        print(f"   • Requests totales: {metrics['total_requests']}")
        print(f"   • Requests exitosos: {metrics['successful_requests']}")
        print(f"   • Requests fallidos: {metrics['failed_requests']}")
        print(f"   • Webhooks entregados: {metrics['webhook_deliveries']}")
        print(f"   • Trabajos de sync completados: {metrics['sync_jobs_completed']}")
        print(f"   • Datos transferidos: {metrics['data_transferred']}")
        
        # Exportar datos
        print(f"\n💾 EXPORTANDO DATOS DE INTEGRACIÓN...")
        exported_files = integration_system.export_integration_data()
        print(f"   • Archivos exportados: {len(exported_files)}")
        for file_type, path in exported_files.items():
            print(f"     - {file_type}: {Path(path).name}")
        
        print(f"\n✅ SISTEMA DE INTEGRACIÓN DEMO COMPLETADO EXITOSAMENTE")
        print(f"🎉 El sistema de integración ha sido configurado con:")
        print(f"   • Múltiples integraciones de APIs externas")
        print(f"   • Sistema de webhooks para eventos")
        print(f"   • Trabajos de sincronización programados")
        print(f"   • Manejo de autenticación y seguridad")
        print(f"   • Monitoreo y métricas en tiempo real")
        
        # Detener sistema
        await integration_system.stop_integration_system()
    
    # Ejecutar demo
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()








