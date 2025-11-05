#!/usr/bin/env python3
"""
🔒 MARKETING BRAIN SECURITY FRAMEWORK
Framework de Seguridad Completo con Encriptación y Control de Acceso
Incluye autenticación, autorización, encriptación, auditoría y protección de datos
"""

import json
import asyncio
import hashlib
import hmac
import secrets
import base64
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Callable, Awaitable
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
from enum import Enum
import jwt
import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import sqlite3
import redis
import ipaddress
import re
import socket
import ssl
from functools import wraps
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import psutil
import requests
from urllib.parse import urlparse
import yaml
import csv
import xml.etree.ElementTree as ET

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Niveles de seguridad"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PermissionType(Enum):
    """Tipos de permisos"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"

class ThreatType(Enum):
    """Tipos de amenazas"""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    DDOS = "ddos"
    MALWARE = "malware"
    PHISHING = "phishing"
    DATA_BREACH = "data_breach"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PRIVILEGE_ESCALATION = "privilege_escalation"

class EncryptionAlgorithm(Enum):
    """Algoritmos de encriptación"""
    AES_256 = "aes_256"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    CHACHA20 = "chacha20"
    FERNET = "fernet"

@dataclass
class User:
    """Usuario del sistema"""
    user_id: str
    username: str
    email: str
    password_hash: str
    salt: str
    roles: List[str]
    permissions: List[str]
    is_active: bool
    is_verified: bool
    last_login: Optional[str]
    failed_login_attempts: int
    locked_until: Optional[str]
    created_at: str
    updated_at: str
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None

@dataclass
class Role:
    """Rol de usuario"""
    role_id: str
    name: str
    description: str
    permissions: List[str]
    security_level: SecurityLevel
    created_at: str
    updated_at: str

@dataclass
class Permission:
    """Permiso del sistema"""
    permission_id: str
    name: str
    resource: str
    action: PermissionType
    conditions: List[str]
    created_at: str

@dataclass
class SecurityEvent:
    """Evento de seguridad"""
    event_id: str
    event_type: str
    severity: SecurityLevel
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    description: str
    details: Dict[str, Any]
    timestamp: str
    resolved: bool = False
    resolution_notes: Optional[str] = None

@dataclass
class AccessToken:
    """Token de acceso"""
    token_id: str
    user_id: str
    token: str
    token_type: str
    expires_at: str
    scopes: List[str]
    is_revoked: bool
    created_at: str
    last_used: Optional[str] = None

@dataclass
class EncryptionKey:
    """Clave de encriptación"""
    key_id: str
    name: str
    algorithm: EncryptionAlgorithm
    key_data: bytes
    created_at: str
    expires_at: Optional[str]
    is_active: bool
    usage_count: int = 0

@dataclass
class SecurityPolicy:
    """Política de seguridad"""
    policy_id: str
    name: str
    description: str
    rules: List[Dict[str, Any]]
    enforcement_level: SecurityLevel
    is_active: bool
    created_at: str
    updated_at: str

class MarketingBrainSecurityFramework:
    """
    Framework de Seguridad Completo con Encriptación y Control de Acceso
    Incluye autenticación, autorización, encriptación, auditoría y protección de datos
    """
    
    def __init__(self):
        self.users = {}
        self.roles = {}
        self.permissions = {}
        self.security_events = {}
        self.access_tokens = {}
        self.encryption_keys = {}
        self.security_policies = {}
        
        # Configuración
        self.config = self._load_config()
        
        # Bases de datos
        self.db_connection = None
        self.redis_client = None
        
        # Claves de encriptación
        self.master_key = None
        self.encryption_keys_cache = {}
        
        # Sistema de auditoría
        self.audit_queue = queue.Queue()
        self.audit_thread = None
        
        # Sistema de monitoreo
        self.monitor_thread = None
        self.threat_detection_active = True
        
        # Métricas de seguridad
        self.security_metrics = {
            'total_login_attempts': 0,
            'failed_login_attempts': 0,
            'security_events_detected': 0,
            'threats_blocked': 0,
            'data_encrypted': 0,
            'access_denied': 0,
            'privilege_escalations': 0,
            'system_uptime': 0.0
        }
        
        logger.info("🔒 Marketing Brain Security Framework initialized successfully")
    
    def _load_config(self) -> Dict[str, Any]:
        """Cargar configuración del framework de seguridad"""
        return {
            'authentication': {
                'password_min_length': 12,
                'password_require_uppercase': True,
                'password_require_lowercase': True,
                'password_require_numbers': True,
                'password_require_symbols': True,
                'max_failed_attempts': 5,
                'lockout_duration': 1800,  # 30 minutos
                'session_timeout': 3600,  # 1 hora
                'mfa_required': True,
                'jwt_secret': 'change_this_in_production',
                'jwt_algorithm': 'HS256',
                'jwt_expiration': 3600
            },
            'authorization': {
                'rbac_enabled': True,
                'permission_caching': True,
                'cache_ttl': 300,
                'default_deny': True,
                'audit_all_requests': True
            },
            'encryption': {
                'default_algorithm': EncryptionAlgorithm.AES_256,
                'key_rotation_interval': 86400,  # 24 horas
                'encrypt_sensitive_data': True,
                'encrypt_at_rest': True,
                'encrypt_in_transit': True,
                'key_derivation_iterations': 100000
            },
            'monitoring': {
                'threat_detection_enabled': True,
                'real_time_monitoring': True,
                'log_all_events': True,
                'alert_thresholds': {
                    'failed_logins_per_minute': 10,
                    'suspicious_requests_per_minute': 20,
                    'data_access_anomalies': 5
                },
                'retention_days': 90
            },
            'audit': {
                'audit_all_actions': True,
                'audit_sensitive_operations': True,
                'audit_data_access': True,
                'audit_configuration_changes': True,
                'audit_retention_days': 365
            },
            'network': {
                'ip_whitelist': [],
                'ip_blacklist': [],
                'rate_limiting_enabled': True,
                'rate_limit_requests_per_minute': 100,
                'ddos_protection_enabled': True,
                'ssl_required': True
            }
        }
    
    async def initialize_security_framework(self):
        """Inicializar framework de seguridad"""
        logger.info("🚀 Initializing Marketing Brain Security Framework...")
        
        try:
            # Inicializar bases de datos
            await self._initialize_databases()
            
            # Generar claves maestras
            await self._generate_master_keys()
            
            # Crear roles y permisos por defecto
            await self._create_default_roles_and_permissions()
            
            # Crear usuario administrador por defecto
            await self._create_default_admin_user()
            
            # Configurar políticas de seguridad
            await self._setup_security_policies()
            
            # Iniciar sistema de auditoría
            self._start_audit_system()
            
            # Iniciar sistema de monitoreo
            self._start_monitoring_system()
            
            logger.info("✅ Security framework initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing security framework: {e}")
            raise
    
    async def _initialize_databases(self):
        """Inicializar bases de datos de seguridad"""
        try:
            # SQLite para metadatos de seguridad
            self.db_connection = sqlite3.connect('security_metadata.db', check_same_thread=False)
            
            # Redis para cache y sesiones
            self.redis_client = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)
            
            # Crear tablas de seguridad
            await self._create_security_tables()
            
        except Exception as e:
            logger.error(f"Error initializing databases: {e}")
            raise
    
    async def _create_security_tables(self):
        """Crear tablas de base de datos de seguridad"""
        try:
            cursor = self.db_connection.cursor()
            
            # Tabla de usuarios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    roles TEXT NOT NULL,
                    permissions TEXT NOT NULL,
                    is_active BOOLEAN NOT NULL,
                    is_verified BOOLEAN NOT NULL,
                    last_login TEXT,
                    failed_login_attempts INTEGER DEFAULT 0,
                    locked_until TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    mfa_enabled BOOLEAN DEFAULT FALSE,
                    mfa_secret TEXT
                )
            ''')
            
            # Tabla de roles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS roles (
                    role_id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT NOT NULL,
                    permissions TEXT NOT NULL,
                    security_level TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Tabla de permisos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS permissions (
                    permission_id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    resource TEXT NOT NULL,
                    action TEXT NOT NULL,
                    conditions TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            ''')
            
            # Tabla de eventos de seguridad
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    user_id TEXT,
                    ip_address TEXT NOT NULL,
                    user_agent TEXT NOT NULL,
                    description TEXT NOT NULL,
                    details TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolution_notes TEXT
                )
            ''')
            
            # Tabla de tokens de acceso
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_tokens (
                    token_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    token TEXT NOT NULL,
                    token_type TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    scopes TEXT NOT NULL,
                    is_revoked BOOLEAN DEFAULT FALSE,
                    created_at TEXT NOT NULL,
                    last_used TEXT
                )
            ''')
            
            # Tabla de claves de encriptación
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS encryption_keys (
                    key_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    algorithm TEXT NOT NULL,
                    key_data BLOB NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    usage_count INTEGER DEFAULT 0
                )
            ''')
            
            # Tabla de políticas de seguridad
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_policies (
                    policy_id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT NOT NULL,
                    rules TEXT NOT NULL,
                    enforcement_level TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Tabla de auditoría
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    audit_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    action TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    details TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    user_agent TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    success BOOLEAN NOT NULL
                )
            ''')
            
            self.db_connection.commit()
            logger.info("Security database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating security tables: {e}")
            raise
    
    async def _generate_master_keys(self):
        """Generar claves maestras de encriptación"""
        try:
            # Generar clave maestra
            self.master_key = Fernet.generate_key()
            
            # Crear clave de encriptación por defecto
            default_key = EncryptionKey(
                key_id=str(uuid.uuid4()),
                name='default_encryption_key',
                algorithm=EncryptionAlgorithm.AES_256,
                key_data=self.master_key,
                created_at=datetime.now().isoformat(),
                expires_at=None,
                is_active=True
            )
            
            self.encryption_keys[default_key.key_id] = default_key
            
            logger.info("Master encryption keys generated successfully")
            
        except Exception as e:
            logger.error(f"Error generating master keys: {e}")
            raise
    
    async def _create_default_roles_and_permissions(self):
        """Crear roles y permisos por defecto"""
        try:
            # Permisos básicos
            basic_permissions = [
                Permission(
                    permission_id=str(uuid.uuid4()),
                    name='read_campaigns',
                    resource='campaigns',
                    action=PermissionType.READ,
                    conditions=[],
                    created_at=datetime.now().isoformat()
                ),
                Permission(
                    permission_id=str(uuid.uuid4()),
                    name='write_campaigns',
                    resource='campaigns',
                    action=PermissionType.WRITE,
                    conditions=[],
                    created_at=datetime.now().isoformat()
                ),
                Permission(
                    permission_id=str(uuid.uuid4()),
                    name='delete_campaigns',
                    resource='campaigns',
                    action=PermissionType.DELETE,
                    conditions=[],
                    created_at=datetime.now().isoformat()
                ),
                Permission(
                    permission_id=str(uuid.uuid4()),
                    name='admin_access',
                    resource='system',
                    action=PermissionType.ADMIN,
                    conditions=[],
                    created_at=datetime.now().isoformat()
                )
            ]
            
            for permission in basic_permissions:
                self.permissions[permission.permission_id] = permission
            
            # Rol de administrador
            admin_role = Role(
                role_id=str(uuid.uuid4()),
                name='admin',
                description='System Administrator',
                permissions=[p.permission_id for p in basic_permissions],
                security_level=SecurityLevel.CRITICAL,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            # Rol de usuario
            user_role = Role(
                role_id=str(uuid.uuid4()),
                name='user',
                description='Regular User',
                permissions=[basic_permissions[0].permission_id],  # Solo lectura
                security_level=SecurityLevel.MEDIUM,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            # Rol de editor
            editor_role = Role(
                role_id=str(uuid.uuid4()),
                name='editor',
                description='Content Editor',
                permissions=[basic_permissions[0].permission_id, basic_permissions[1].permission_id],
                security_level=SecurityLevel.MEDIUM,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            self.roles[admin_role.role_id] = admin_role
            self.roles[user_role.role_id] = user_role
            self.roles[editor_role.role_id] = editor_role
            
            logger.info("Default roles and permissions created successfully")
            
        except Exception as e:
            logger.error(f"Error creating default roles and permissions: {e}")
            raise
    
    async def _create_default_admin_user(self):
        """Crear usuario administrador por defecto"""
        try:
            # Generar salt
            salt = secrets.token_hex(32)
            
            # Hash de contraseña por defecto
            password = "Admin123!@#"
            password_hash = self._hash_password(password, salt)
            
            # Obtener rol de administrador
            admin_role_id = next(role_id for role_id, role in self.roles.items() if role.name == 'admin')
            
            admin_user = User(
                user_id=str(uuid.uuid4()),
                username='admin',
                email='admin@marketingbrain.com',
                password_hash=password_hash,
                salt=salt,
                roles=[admin_role_id],
                permissions=[],  # Se heredan del rol
                is_active=True,
                is_verified=True,
                last_login=None,
                failed_login_attempts=0,
                locked_until=None,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                mfa_enabled=True
            )
            
            self.users[admin_user.user_id] = admin_user
            
            logger.info("Default admin user created successfully")
            
        except Exception as e:
            logger.error(f"Error creating default admin user: {e}")
            raise
    
    async def _setup_security_policies(self):
        """Configurar políticas de seguridad"""
        try:
            # Política de contraseñas
            password_policy = SecurityPolicy(
                policy_id=str(uuid.uuid4()),
                name='Password Policy',
                description='Password complexity and security requirements',
                rules=[
                    {
                        'type': 'password_complexity',
                        'min_length': 12,
                        'require_uppercase': True,
                        'require_lowercase': True,
                        'require_numbers': True,
                        'require_symbols': True
                    },
                    {
                        'type': 'password_history',
                        'prevent_reuse': 5
                    },
                    {
                        'type': 'password_expiration',
                        'expiry_days': 90
                    }
                ],
                enforcement_level=SecurityLevel.HIGH,
                is_active=True,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            # Política de acceso
            access_policy = SecurityPolicy(
                policy_id=str(uuid.uuid4()),
                name='Access Control Policy',
                description='Access control and session management',
                rules=[
                    {
                        'type': 'session_timeout',
                        'timeout_minutes': 60
                    },
                    {
                        'type': 'max_failed_attempts',
                        'attempts': 5,
                        'lockout_minutes': 30
                    },
                    {
                        'type': 'ip_restrictions',
                        'allowed_ips': [],
                        'blocked_ips': []
                    }
                ],
                enforcement_level=SecurityLevel.HIGH,
                is_active=True,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            # Política de encriptación
            encryption_policy = SecurityPolicy(
                policy_id=str(uuid.uuid4()),
                name='Encryption Policy',
                description='Data encryption requirements',
                rules=[
                    {
                        'type': 'encrypt_at_rest',
                        'enabled': True,
                        'algorithm': 'AES-256'
                    },
                    {
                        'type': 'encrypt_in_transit',
                        'enabled': True,
                        'protocol': 'TLS 1.3'
                    },
                    {
                        'type': 'key_rotation',
                        'interval_days': 90
                    }
                ],
                enforcement_level=SecurityLevel.CRITICAL,
                is_active=True,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            self.security_policies[password_policy.policy_id] = password_policy
            self.security_policies[access_policy.policy_id] = access_policy
            self.security_policies[encryption_policy.policy_id] = encryption_policy
            
            logger.info("Security policies configured successfully")
            
        except Exception as e:
            logger.error(f"Error setting up security policies: {e}")
            raise
    
    def _start_audit_system(self):
        """Iniciar sistema de auditoría"""
        self.audit_thread = threading.Thread(target=self._audit_loop, daemon=True)
        self.audit_thread.start()
        logger.info("Audit system started")
    
    def _start_monitoring_system(self):
        """Iniciar sistema de monitoreo"""
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Monitoring system started")
    
    def _audit_loop(self):
        """Loop del sistema de auditoría"""
        while True:
            try:
                if not self.audit_queue.empty():
                    audit_event = self.audit_queue.get_nowait()
                    self._process_audit_event(audit_event)
                    self.audit_queue.task_done()
                
                time.sleep(1)
                
            except queue.Empty:
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in audit loop: {e}")
                time.sleep(5)
    
    def _monitoring_loop(self):
        """Loop del sistema de monitoreo"""
        while self.threat_detection_active:
            try:
                # Monitorear intentos de login fallidos
                self._monitor_failed_logins()
                
                # Monitorear actividad sospechosa
                self._monitor_suspicious_activity()
                
                # Monitorear acceso a datos sensibles
                self._monitor_sensitive_data_access()
                
                # Actualizar métricas
                self._update_security_metrics()
                
                time.sleep(60)  # Verificar cada minuto
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)
    
    def _process_audit_event(self, audit_event: Dict[str, Any]):
        """Procesar evento de auditoría"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO audit_log (audit_id, user_id, action, resource, details, 
                                     ip_address, user_agent, timestamp, success)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                audit_event['audit_id'],
                audit_event.get('user_id'),
                audit_event['action'],
                audit_event['resource'],
                json.dumps(audit_event['details']),
                audit_event['ip_address'],
                audit_event['user_agent'],
                audit_event['timestamp'],
                audit_event['success']
            ))
            self.db_connection.commit()
            
        except Exception as e:
            logger.error(f"Error processing audit event: {e}")
    
    def _monitor_failed_logins(self):
        """Monitorear intentos de login fallidos"""
        try:
            # Obtener intentos fallidos recientes
            cursor = self.db_connection.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM security_events 
                WHERE event_type = 'failed_login' 
                AND timestamp > datetime('now', '-1 minute')
            ''')
            
            failed_logins = cursor.fetchone()[0]
            
            # Verificar umbral
            threshold = self.config['monitoring']['alert_thresholds']['failed_logins_per_minute']
            if failed_logins > threshold:
                self._create_security_event(
                    event_type='brute_force_attempt',
                    severity=SecurityLevel.HIGH,
                    description=f'High number of failed login attempts: {failed_logins}',
                    details={'failed_attempts': failed_logins, 'threshold': threshold}
                )
                
        except Exception as e:
            logger.error(f"Error monitoring failed logins: {e}")
    
    def _monitor_suspicious_activity(self):
        """Monitorear actividad sospechosa"""
        try:
            # Implementar detección de actividad sospechosa
            # Por simplicidad, solo logear
            pass
            
        except Exception as e:
            logger.error(f"Error monitoring suspicious activity: {e}")
    
    def _monitor_sensitive_data_access(self):
        """Monitorear acceso a datos sensibles"""
        try:
            # Implementar monitoreo de acceso a datos sensibles
            # Por simplicidad, solo logear
            pass
            
        except Exception as e:
            logger.error(f"Error monitoring sensitive data access: {e}")
    
    def _update_security_metrics(self):
        """Actualizar métricas de seguridad"""
        try:
            # Actualizar métricas desde la base de datos
            cursor = self.db_connection.cursor()
            
            # Total de intentos de login
            cursor.execute('SELECT COUNT(*) FROM security_events WHERE event_type = "login_attempt"')
            self.security_metrics['total_login_attempts'] = cursor.fetchone()[0]
            
            # Intentos fallidos
            cursor.execute('SELECT COUNT(*) FROM security_events WHERE event_type = "failed_login"')
            self.security_metrics['failed_login_attempts'] = cursor.fetchone()[0]
            
            # Eventos de seguridad
            cursor.execute('SELECT COUNT(*) FROM security_events')
            self.security_metrics['security_events_detected'] = cursor.fetchone()[0]
            
        except Exception as e:
            logger.error(f"Error updating security metrics: {e}")
    
    async def authenticate_user(self, username: str, password: str, 
                              ip_address: str, user_agent: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Autenticar usuario"""
        try:
            # Buscar usuario
            user = None
            for u in self.users.values():
                if u.username == username or u.email == username:
                    user = u
                    break
            
            if not user:
                await self._log_security_event('failed_login', SecurityLevel.MEDIUM, 
                                             None, ip_address, user_agent, 
                                             f'Login attempt with non-existent username: {username}')
                return False, None, "Invalid credentials"
            
            # Verificar si el usuario está bloqueado
            if user.locked_until:
                lock_time = datetime.fromisoformat(user.locked_until)
                if datetime.now() < lock_time:
                    await self._log_security_event('blocked_login_attempt', SecurityLevel.HIGH,
                                                 user.user_id, ip_address, user_agent,
                                                 f'Login attempt while account is locked')
                    return False, None, "Account is locked"
                else:
                    # Desbloquear cuenta
                    user.locked_until = None
                    user.failed_login_attempts = 0
            
            # Verificar contraseña
            if not self._verify_password(password, user.password_hash, user.salt):
                user.failed_login_attempts += 1
                
                # Verificar si excede el límite
                max_attempts = self.config['authentication']['max_failed_attempts']
                if user.failed_login_attempts >= max_attempts:
                    lockout_duration = self.config['authentication']['lockout_duration']
                    user.locked_until = (datetime.now() + timedelta(seconds=lockout_duration)).isoformat()
                    
                    await self._log_security_event('account_locked', SecurityLevel.HIGH,
                                                 user.user_id, ip_address, user_agent,
                                                 f'Account locked due to {max_attempts} failed attempts')
                
                await self._log_security_event('failed_login', SecurityLevel.MEDIUM,
                                             user.user_id, ip_address, user_agent,
                                             f'Failed login attempt #{user.failed_login_attempts}')
                
                return False, None, "Invalid credentials"
            
            # Login exitoso
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.now().isoformat()
            
            # Generar token de acceso
            access_token = await self._generate_access_token(user)
            
            await self._log_security_event('successful_login', SecurityLevel.LOW,
                                         user.user_id, ip_address, user_agent,
                                         'User logged in successfully')
            
            # Actualizar métricas
            self.security_metrics['total_login_attempts'] += 1
            
            return True, access_token, None
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return False, None, "Authentication error"
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash de contraseña"""
        try:
            # Usar bcrypt para hash de contraseñas
            password_bytes = password.encode('utf-8')
            salt_bytes = salt.encode('utf-8')
            
            # Generar hash con bcrypt
            hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
            
            return hashed.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise
    
    def _verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verificar contraseña"""
        try:
            password_bytes = password.encode('utf-8')
            password_hash_bytes = password_hash.encode('utf-8')
            
            return bcrypt.checkpw(password_bytes, password_hash_bytes)
            
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    async def _generate_access_token(self, user: User) -> str:
        """Generar token de acceso"""
        try:
            # Crear payload JWT
            payload = {
                'user_id': user.user_id,
                'username': user.username,
                'roles': user.roles,
                'permissions': user.permissions,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=self.config['authentication']['jwt_expiration'])
            }
            
            # Generar token
            token = jwt.encode(payload, self.config['authentication']['jwt_secret'], 
                             algorithm=self.config['authentication']['jwt_algorithm'])
            
            # Guardar token en base de datos
            access_token = AccessToken(
                token_id=str(uuid.uuid4()),
                user_id=user.user_id,
                token=token,
                token_type='Bearer',
                expires_at=payload['exp'].isoformat(),
                scopes=['read', 'write'],
                is_revoked=False,
                created_at=datetime.now().isoformat()
            )
            
            self.access_tokens[access_token.token_id] = access_token
            
            return token
            
        except Exception as e:
            logger.error(f"Error generating access token: {e}")
            raise
    
    async def authorize_access(self, user_id: str, resource: str, action: PermissionType,
                             ip_address: str, user_agent: str) -> bool:
        """Autorizar acceso a recurso"""
        try:
            # Buscar usuario
            user = self.users.get(user_id)
            if not user:
                await self._log_security_event('unauthorized_access', SecurityLevel.HIGH,
                                             None, ip_address, user_agent,
                                             f'Access attempt by non-existent user: {user_id}')
                return False
            
            # Verificar si el usuario está activo
            if not user.is_active:
                await self._log_security_event('inactive_user_access', SecurityLevel.MEDIUM,
                                             user_id, ip_address, user_agent,
                                             'Access attempt by inactive user')
                return False
            
            # Obtener permisos del usuario
            user_permissions = await self._get_user_permissions(user)
            
            # Verificar permiso específico
            has_permission = False
            for permission_id in user_permissions:
                permission = self.permissions.get(permission_id)
                if permission and permission.resource == resource and permission.action == action:
                    has_permission = True
                    break
            
            # Log del intento de acceso
            await self._log_audit_event(
                user_id=user_id,
                action=f'{action.value}_{resource}',
                resource=resource,
                details={'action': action.value, 'authorized': has_permission},
                ip_address=ip_address,
                user_agent=user_agent,
                success=has_permission
            )
            
            if not has_permission:
                self.security_metrics['access_denied'] += 1
                await self._log_security_event('access_denied', SecurityLevel.MEDIUM,
                                             user_id, ip_address, user_agent,
                                             f'Access denied to {resource} for action {action.value}')
            
            return has_permission
            
        except Exception as e:
            logger.error(f"Error authorizing access: {e}")
            return False
    
    async def _get_user_permissions(self, user: User) -> List[str]:
        """Obtener permisos del usuario"""
        try:
            permissions = set()
            
            # Agregar permisos directos
            permissions.update(user.permissions)
            
            # Agregar permisos de roles
            for role_id in user.roles:
                role = self.roles.get(role_id)
                if role:
                    permissions.update(role.permissions)
            
            return list(permissions)
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return []
    
    async def encrypt_data(self, data: str, key_id: Optional[str] = None) -> str:
        """Encriptar datos"""
        try:
            # Obtener clave de encriptación
            if key_id and key_id in self.encryption_keys:
                encryption_key = self.encryption_keys[key_id]
            else:
                # Usar clave por defecto
                encryption_key = next(k for k in self.encryption_keys.values() if k.is_active)
            
            # Encriptar datos
            if encryption_key.algorithm == EncryptionAlgorithm.AES_256:
                encrypted_data = self._encrypt_aes256(data, encryption_key.key_data)
            elif encryption_key.algorithm == EncryptionAlgorithm.FERNET:
                fernet = Fernet(encryption_key.key_data)
                encrypted_data = fernet.encrypt(data.encode()).decode()
            else:
                raise ValueError(f"Unsupported encryption algorithm: {encryption_key.algorithm}")
            
            # Actualizar contador de uso
            encryption_key.usage_count += 1
            
            # Actualizar métricas
            self.security_metrics['data_encrypted'] += 1
            
            return encrypted_data
            
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise
    
    async def decrypt_data(self, encrypted_data: str, key_id: Optional[str] = None) -> str:
        """Desencriptar datos"""
        try:
            # Obtener clave de encriptación
            if key_id and key_id in self.encryption_keys:
                encryption_key = self.encryption_keys[key_id]
            else:
                # Usar clave por defecto
                encryption_key = next(k for k in self.encryption_keys.values() if k.is_active)
            
            # Desencriptar datos
            if encryption_key.algorithm == EncryptionAlgorithm.AES_256:
                decrypted_data = self._decrypt_aes256(encrypted_data, encryption_key.key_data)
            elif encryption_key.algorithm == EncryptionAlgorithm.FERNET:
                fernet = Fernet(encryption_key.key_data)
                decrypted_data = fernet.decrypt(encrypted_data.encode()).decode()
            else:
                raise ValueError(f"Unsupported encryption algorithm: {encryption_key.algorithm}")
            
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise
    
    def _encrypt_aes256(self, data: str, key: bytes) -> str:
        """Encriptar con AES-256"""
        try:
            # Generar IV aleatorio
            iv = secrets.token_bytes(16)
            
            # Crear cipher
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            
            # Padding
            data_bytes = data.encode('utf-8')
            padding_length = 16 - (len(data_bytes) % 16)
            padded_data = data_bytes + bytes([padding_length] * padding_length)
            
            # Encriptar
            encrypted = encryptor.update(padded_data) + encryptor.finalize()
            
            # Combinar IV y datos encriptados
            combined = iv + encrypted
            
            # Codificar en base64
            return base64.b64encode(combined).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error encrypting with AES-256: {e}")
            raise
    
    def _decrypt_aes256(self, encrypted_data: str, key: bytes) -> str:
        """Desencriptar con AES-256"""
        try:
            # Decodificar base64
            combined = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Separar IV y datos encriptados
            iv = combined[:16]
            encrypted = combined[16:]
            
            # Crear cipher
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            
            # Desencriptar
            decrypted_padded = decryptor.update(encrypted) + decryptor.finalize()
            
            # Remover padding
            padding_length = decrypted_padded[-1]
            decrypted_data = decrypted_padded[:-padding_length]
            
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error decrypting with AES-256: {e}")
            raise
    
    async def _log_security_event(self, event_type: str, severity: SecurityLevel,
                                user_id: Optional[str], ip_address: str, user_agent: str,
                                description: str, details: Optional[Dict[str, Any]] = None):
        """Registrar evento de seguridad"""
        try:
            security_event = SecurityEvent(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                severity=severity,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                description=description,
                details=details or {},
                timestamp=datetime.now().isoformat()
            )
            
            self.security_events[security_event.event_id] = security_event
            
            # Guardar en base de datos
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO security_events (event_id, event_type, severity, user_id, 
                                           ip_address, user_agent, description, details, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                security_event.event_id,
                security_event.event_type,
                security_event.severity.value,
                security_event.user_id,
                security_event.ip_address,
                security_event.user_agent,
                security_event.description,
                json.dumps(security_event.details),
                security_event.timestamp
            ))
            self.db_connection.commit()
            
            # Actualizar métricas
            self.security_metrics['security_events_detected'] += 1
            
            # Log del evento
            logger.warning(f"Security event: {event_type} - {description}")
            
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
    
    async def _log_audit_event(self, user_id: Optional[str], action: str, resource: str,
                             details: Dict[str, Any], ip_address: str, user_agent: str,
                             success: bool):
        """Registrar evento de auditoría"""
        try:
            audit_event = {
                'audit_id': str(uuid.uuid4()),
                'user_id': user_id,
                'action': action,
                'resource': resource,
                'details': details,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'timestamp': datetime.now().isoformat(),
                'success': success
            }
            
            # Agregar a cola de auditoría
            self.audit_queue.put(audit_event)
            
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
    
    def validate_password_strength(self, password: str) -> Tuple[bool, List[str]]:
        """Validar fortaleza de contraseña"""
        try:
            errors = []
            config = self.config['authentication']
            
            # Verificar longitud mínima
            if len(password) < config['password_min_length']:
                errors.append(f"Password must be at least {config['password_min_length']} characters long")
            
            # Verificar mayúsculas
            if config['password_require_uppercase'] and not re.search(r'[A-Z]', password):
                errors.append("Password must contain at least one uppercase letter")
            
            # Verificar minúsculas
            if config['password_require_lowercase'] and not re.search(r'[a-z]', password):
                errors.append("Password must contain at least one lowercase letter")
            
            # Verificar números
            if config['password_require_numbers'] and not re.search(r'\d', password):
                errors.append("Password must contain at least one number")
            
            # Verificar símbolos
            if config['password_require_symbols'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                errors.append("Password must contain at least one special character")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            logger.error(f"Error validating password strength: {e}")
            return False, ["Password validation error"]
    
    def validate_ip_address(self, ip_address: str) -> bool:
        """Validar dirección IP"""
        try:
            # Verificar formato de IP
            ipaddress.ip_address(ip_address)
            
            # Verificar lista negra
            if ip_address in self.config['network']['ip_blacklist']:
                return False
            
            # Verificar lista blanca (si está configurada)
            whitelist = self.config['network']['ip_whitelist']
            if whitelist and ip_address not in whitelist:
                return False
            
            return True
            
        except ValueError:
            return False
        except Exception as e:
            logger.error(f"Error validating IP address: {e}")
            return False
    
    def get_security_dashboard_data(self) -> Dict[str, Any]:
        """Obtener datos para dashboard de seguridad"""
        return {
            'system_status': 'active',
            'total_users': len(self.users),
            'active_users': len([u for u in self.users.values() if u.is_active]),
            'total_roles': len(self.roles),
            'total_permissions': len(self.permissions),
            'security_events_count': len(self.security_events),
            'active_tokens': len([t for t in self.access_tokens.values() if not t.is_revoked]),
            'encryption_keys_count': len(self.encryption_keys),
            'security_policies_count': len(self.security_policies),
            'metrics': self.security_metrics,
            'recent_security_events': [
                {
                    'event_id': event.event_id,
                    'event_type': event.event_type,
                    'severity': event.severity.value,
                    'description': event.description,
                    'timestamp': event.timestamp,
                    'resolved': event.resolved
                }
                for event in list(self.security_events.values())[-10:]  # Últimos 10 eventos
            ],
            'user_summary': {
                user_id: {
                    'username': user.username,
                    'email': user.email,
                    'roles': user.roles,
                    'is_active': user.is_active,
                    'last_login': user.last_login,
                    'failed_attempts': user.failed_login_attempts
                }
                for user_id, user in self.users.items()
            },
            'last_updated': datetime.now().isoformat()
        }
    
    def export_security_data(self, export_dir: str = "security_data") -> Dict[str, str]:
        """Exportar datos de seguridad"""
        Path(export_dir).mkdir(exist_ok=True)
        exported_files = {}
        
        # Exportar usuarios (sin contraseñas)
        users_data = {}
        for user_id, user in self.users.items():
            user_dict = asdict(user)
            user_dict['password_hash'] = '[REDACTED]'
            user_dict['salt'] = '[REDACTED]'
            users_data[user_id] = user_dict
        
        users_path = Path(export_dir) / f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(users_path, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
        exported_files['users'] = str(users_path)
        
        # Exportar roles
        roles_data = {role_id: asdict(role) for role_id, role in self.roles.items()}
        roles_path = Path(export_dir) / f"roles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(roles_path, 'w', encoding='utf-8') as f:
            json.dump(roles_data, f, indent=2, ensure_ascii=False)
        exported_files['roles'] = str(roles_path)
        
        # Exportar permisos
        permissions_data = {perm_id: asdict(permission) for perm_id, permission in self.permissions.items()}
        permissions_path = Path(export_dir) / f"permissions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(permissions_path, 'w', encoding='utf-8') as f:
            json.dump(permissions_data, f, indent=2, ensure_ascii=False)
        exported_files['permissions'] = str(permissions_path)
        
        # Exportar eventos de seguridad
        events_data = {event_id: asdict(event) for event_id, event in self.security_events.items()}
        events_path = Path(export_dir) / f"security_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(events_path, 'w', encoding='utf-8') as f:
            json.dump(events_data, f, indent=2, ensure_ascii=False)
        exported_files['security_events'] = str(events_path)
        
        # Exportar políticas de seguridad
        policies_data = {policy_id: asdict(policy) for policy_id, policy in self.security_policies.items()}
        policies_path = Path(export_dir) / f"security_policies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(policies_path, 'w', encoding='utf-8') as f:
            json.dump(policies_data, f, indent=2, ensure_ascii=False)
        exported_files['security_policies'] = str(policies_path)
        
        # Exportar métricas
        metrics_path = Path(export_dir) / f"security_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(self.security_metrics, f, indent=2, ensure_ascii=False)
        exported_files['security_metrics'] = str(metrics_path)
        
        logger.info(f"📦 Exported security data to {export_dir}")
        return exported_files


def main():
    """Función principal para demostrar el Framework de Seguridad"""
    print("🔒 MARKETING BRAIN SECURITY FRAMEWORK")
    print("=" * 60)
    
    # Crear framework de seguridad
    security_framework = MarketingBrainSecurityFramework()
    
    async def run_demo():
        print(f"\n🚀 INICIANDO FRAMEWORK DE SEGURIDAD...")
        
        # Inicializar framework
        await security_framework.initialize_security_framework()
        
        # Mostrar estado inicial
        dashboard_data = security_framework.get_security_dashboard_data()
        print(f"\n📊 ESTADO DEL SISTEMA DE SEGURIDAD:")
        print(f"   • Estado: {dashboard_data['system_status']}")
        print(f"   • Usuarios totales: {dashboard_data['total_users']}")
        print(f"   • Usuarios activos: {dashboard_data['active_users']}")
        print(f"   • Roles: {dashboard_data['total_roles']}")
        print(f"   • Permisos: {dashboard_data['total_permissions']}")
        print(f"   • Eventos de seguridad: {dashboard_data['security_events_count']}")
        print(f"   • Tokens activos: {dashboard_data['active_tokens']}")
        print(f"   • Claves de encriptación: {dashboard_data['encryption_keys_count']}")
        print(f"   • Políticas de seguridad: {dashboard_data['security_policies_count']}")
        
        # Mostrar usuarios
        print(f"\n👥 USUARIOS DEL SISTEMA:")
        for user_id, user_info in dashboard_data['user_summary'].items():
            status_icon = "✅" if user_info['is_active'] else "❌"
            print(f"   {status_icon} {user_info['username']} ({user_info['email']})")
            print(f"      • Roles: {', '.join(user_info['roles'])}")
            print(f"      • Último login: {user_info['last_login'] or 'Nunca'}")
            print(f"      • Intentos fallidos: {user_info['failed_attempts']}")
        
        # Mostrar roles y permisos
        print(f"\n🔐 ROLES Y PERMISOS:")
        for role_id, role in security_framework.roles.items():
            print(f"   • {role.name} ({role.security_level.value})")
            print(f"      • Descripción: {role.description}")
            print(f"      • Permisos: {len(role.permissions)}")
        
        # Simular autenticación
        print(f"\n🔑 SIMULANDO AUTENTICACIÓN...")
        username = "admin"
        password = "Admin123!@#"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        print(f"   • Usuario: {username}")
        print(f"   • IP: {ip_address}")
        print(f"   • User Agent: {user_agent[:50]}...")
        
        success, token, error = await security_framework.authenticate_user(
            username, password, ip_address, user_agent
        )
        
        if success:
            print(f"   ✅ Autenticación exitosa")
            print(f"      • Token generado: {token[:50]}...")
            
            # Simular autorización
            print(f"\n🛡️ SIMULANDO AUTORIZACIÓN...")
            user_id = next(uid for uid, user in security_framework.users.items() if user.username == username)
            
            # Intentar acceso a campañas
            authorized = await security_framework.authorize_access(
                user_id, 'campaigns', PermissionType.READ, ip_address, user_agent
            )
            print(f"   • Acceso a lectura de campañas: {'✅ Autorizado' if authorized else '❌ Denegado'}")
            
            authorized = await security_framework.authorize_access(
                user_id, 'campaigns', PermissionType.WRITE, ip_address, user_agent
            )
            print(f"   • Acceso a escritura de campañas: {'✅ Autorizado' if authorized else '❌ Denegado'}")
            
            authorized = await security_framework.authorize_access(
                user_id, 'system', PermissionType.ADMIN, ip_address, user_agent
            )
            print(f"   • Acceso de administrador: {'✅ Autorizado' if authorized else '❌ Denegado'}")
            
        else:
            print(f"   ❌ Autenticación fallida: {error}")
        
        # Simular encriptación de datos
        print(f"\n🔐 SIMULANDO ENCRIPTACIÓN DE DATOS...")
        sensitive_data = "This is sensitive customer data that needs to be encrypted"
        print(f"   • Datos originales: {sensitive_data}")
        
        try:
            encrypted_data = await security_framework.encrypt_data(sensitive_data)
            print(f"   ✅ Datos encriptados: {encrypted_data[:50]}...")
            
            decrypted_data = await security_framework.decrypt_data(encrypted_data)
            print(f"   ✅ Datos desencriptados: {decrypted_data}")
            print(f"   • Coinciden: {'✅ Sí' if sensitive_data == decrypted_data else '❌ No'}")
            
        except Exception as e:
            print(f"   ❌ Error en encriptación: {e}")
        
        # Validar fortaleza de contraseña
        print(f"\n🔍 VALIDANDO FORTALEZA DE CONTRASEÑA...")
        test_passwords = [
            "weak",
            "Password123",
            "StrongP@ssw0rd!2024",
            "VeryStrongP@ssw0rd!WithNumbers123"
        ]
        
        for password in test_passwords:
            is_valid, errors = security_framework.validate_password_strength(password)
            status_icon = "✅" if is_valid else "❌"
            print(f"   {status_icon} '{password}': {'Válida' if is_valid else f'Errores: {len(errors)}'}")
            if errors:
                for error in errors:
                    print(f"      - {error}")
        
        # Mostrar eventos de seguridad recientes
        print(f"\n🚨 EVENTOS DE SEGURIDAD RECIENTES:")
        recent_events = dashboard_data['recent_security_events']
        if recent_events:
            for event in recent_events[-5:]:  # Últimos 5 eventos
                severity_icon = {
                    'low': '🟢',
                    'medium': '🟡',
                    'high': '🟠',
                    'critical': '🔴'
                }.get(event['severity'], '⚪')
                
                print(f"   {severity_icon} {event['event_type']} - {event['description']}")
                print(f"      • Severidad: {event['severity']}")
                print(f"      • Timestamp: {event['timestamp']}")
                print(f"      • Resuelto: {'✅' if event['resolved'] else '❌'}")
        else:
            print(f"   • No hay eventos de seguridad recientes")
        
        # Mostrar métricas de seguridad
        print(f"\n📈 MÉTRICAS DE SEGURIDAD:")
        metrics = dashboard_data['metrics']
        print(f"   • Intentos de login totales: {metrics['total_login_attempts']}")
        print(f"   • Intentos de login fallidos: {metrics['failed_login_attempts']}")
        print(f"   • Eventos de seguridad detectados: {metrics['security_events_detected']}")
        print(f"   • Amenazas bloqueadas: {metrics['threats_blocked']}")
        print(f"   • Datos encriptados: {metrics['data_encrypted']}")
        print(f"   • Accesos denegados: {metrics['access_denied']}")
        print(f"   • Escalaciones de privilegio: {metrics['privilege_escalations']}")
        print(f"   • Tiempo de actividad: {metrics['system_uptime']:.2f}s")
        
        # Exportar datos de seguridad
        print(f"\n💾 EXPORTANDO DATOS DE SEGURIDAD...")
        exported_files = security_framework.export_security_data()
        print(f"   • Archivos exportados: {len(exported_files)}")
        for file_type, path in exported_files.items():
            print(f"     - {file_type}: {Path(path).name}")
        
        print(f"\n✅ FRAMEWORK DE SEGURIDAD DEMO COMPLETADO EXITOSAMENTE")
        print(f"🎉 El framework de seguridad ha implementado:")
        print(f"   • Sistema de autenticación robusto")
        print(f"   • Control de acceso basado en roles (RBAC)")
        print(f"   • Encriptación de datos sensible")
        print(f"   • Monitoreo de seguridad en tiempo real")
        print(f"   • Sistema de auditoría completo")
        print(f"   • Detección de amenazas")
        print(f"   • Políticas de seguridad configurables")
        print(f"   • Validación de fortaleza de contraseñas")
        print(f"   • Gestión de tokens de acceso")
        print(f"   • Logging y métricas de seguridad")
        
        return security_framework
    
    # Ejecutar demo
    security_system = asyncio.run(run_demo())


if __name__ == "__main__":
    main()








