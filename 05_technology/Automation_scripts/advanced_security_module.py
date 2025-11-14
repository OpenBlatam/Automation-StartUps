#!/usr/bin/env python3
"""
Advanced Security Module for Competitive Pricing Analysis System
==============================================================

Módulo de seguridad avanzado que proporciona:
- Autenticación y autorización
- Encriptación de datos sensibles
- Gestión de sesiones
- Auditoría de seguridad
- Protección contra ataques
- Gestión de tokens
- Validación de entrada
- Logging de seguridad
"""

import hashlib
import hmac
import secrets
import jwt
import bcrypt
import sqlite3
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import re
import ipaddress
from functools import wraps
import threading
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class User:
    """Usuario del sistema"""
    id: str
    username: str
    email: str
    role: str
    permissions: List[str]
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None

@dataclass
class SecurityEvent:
    """Evento de seguridad"""
    id: str
    event_type: str
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    timestamp: datetime
    details: Dict[str, Any]
    severity: str  # low, medium, high, critical
    resolved: bool = False

@dataclass
class SecurityConfig:
    """Configuración de seguridad"""
    jwt_secret: str
    jwt_expiry: int = 3600  # 1 hora
    max_failed_attempts: int = 5
    lockout_duration: int = 1800  # 30 minutos
    password_min_length: int = 8
    password_require_special: bool = True
    session_timeout: int = 7200  # 2 horas
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hora
    encryption_key: str = None

class AdvancedSecurityModule:
    """Módulo de seguridad avanzado"""
    
    def __init__(self, db_path: str = "security.db", config: SecurityConfig = None):
        """Inicializar módulo de seguridad"""
        self.db_path = db_path
        self.config = config or SecurityConfig(
            jwt_secret=secrets.token_urlsafe(32),
            encryption_key=secrets.token_urlsafe(32)
        )
        
        # Inicializar base de datos
        self._init_database()
        
        # Cache de sesiones activas
        self.active_sessions = {}
        self.session_lock = threading.Lock()
        
        # Rate limiting
        self.rate_limits = defaultdict(lambda: deque())
        self.rate_limit_lock = threading.Lock()
        
        # Cache de intentos fallidos
        self.failed_attempts = defaultdict(int)
        self.lockouts = {}
        
        logger.info("Advanced Security Module initialized")
    
    def _init_database(self):
        """Inicializar base de datos de seguridad"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabla de usuarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    permissions TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    failed_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP
                )
            """)
            
            # Tabla de sesiones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    token TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Tabla de eventos de seguridad
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_events (
                    id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    user_id TEXT,
                    ip_address TEXT NOT NULL,
                    user_agent TEXT,
                    timestamp TIMESTAMP NOT NULL,
                    details TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Tabla de tokens de API
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_tokens (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    token_hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    permissions TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP,
                    last_used TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("Security database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing security database: {e}")
            raise
    
    def hash_password(self, password: str) -> str:
        """Encriptar contraseña"""
        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verificar contraseña"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def validate_password_strength(self, password: str) -> Tuple[bool, List[str]]:
        """Validar fortaleza de contraseña"""
        errors = []
        
        if len(password) < self.config.password_min_length:
            errors.append(f"Password must be at least {self.config.password_min_length} characters long")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if self.config.password_require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        return len(errors) == 0, errors
    
    def create_user(self, username: str, email: str, password: str, role: str = "user", permissions: List[str] = None) -> str:
        """Crear usuario"""
        try:
            # Validar contraseña
            is_valid, errors = self.validate_password_strength(password)
            if not is_valid:
                raise ValueError(f"Password validation failed: {', '.join(errors)}")
            
            # Verificar si usuario ya existe
            if self.get_user_by_username(username):
                raise ValueError("Username already exists")
            
            if self.get_user_by_email(email):
                raise ValueError("Email already exists")
            
            # Crear usuario
            user_id = secrets.token_urlsafe(16)
            password_hash = self.hash_password(password)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (id, username, email, password_hash, role, permissions, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                username,
                email,
                password_hash,
                role,
                json.dumps(permissions or []),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            # Log evento de seguridad
            self.log_security_event(
                event_type="user_created",
                user_id=user_id,
                ip_address="127.0.0.1",
                user_agent="system",
                details={"username": username, "role": role},
                severity="low"
            )
            
            logger.info(f"User created: {username}")
            return user_id
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    def authenticate_user(self, username: str, password: str, ip_address: str, user_agent: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Autenticar usuario"""
        try:
            # Verificar rate limiting
            if not self._check_rate_limit(ip_address):
                self.log_security_event(
                    event_type="rate_limit_exceeded",
                    user_id=None,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={"username": username},
                    severity="medium"
                )
                return False, None, "Rate limit exceeded"
            
            # Obtener usuario
            user = self.get_user_by_username(username)
            if not user:
                self._increment_failed_attempts(ip_address)
                self.log_security_event(
                    event_type="login_failed",
                    user_id=None,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={"username": username, "reason": "user_not_found"},
                    severity="low"
                )
                return False, None, "Invalid credentials"
            
            # Verificar si usuario está bloqueado
            if user.locked_until and datetime.now() < user.locked_until:
                self.log_security_event(
                    event_type="login_blocked",
                    user_id=user.id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={"username": username, "locked_until": user.locked_until.isoformat()},
                    severity="medium"
                )
                return False, None, "Account locked"
            
            # Verificar si usuario está activo
            if not user.is_active:
                self.log_security_event(
                    event_type="login_inactive",
                    user_id=user.id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={"username": username},
                    severity="medium"
                )
                return False, None, "Account inactive"
            
            # Verificar contraseña
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user.id,))
            result = cursor.fetchone()
            
            if not result or not self.verify_password(password, result[0]):
                self._increment_failed_attempts(ip_address)
                self._increment_user_failed_attempts(user.id)
                
                self.log_security_event(
                    event_type="login_failed",
                    user_id=user.id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={"username": username, "reason": "invalid_password"},
                    severity="low"
                )
                
                conn.close()
                return False, None, "Invalid credentials"
            
            # Autenticación exitosa
            self._reset_failed_attempts(ip_address)
            self._reset_user_failed_attempts(user.id)
            
            # Actualizar último login
            cursor.execute("""
                UPDATE users SET last_login = ?, failed_attempts = 0, locked_until = NULL
                WHERE id = ?
            """, (datetime.now().isoformat(), user.id))
            
            conn.commit()
            conn.close()
            
            # Crear sesión
            session_id = self.create_session(user.id, ip_address, user_agent)
            
            # Log evento de seguridad
            self.log_security_event(
                event_type="login_success",
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"username": username},
                severity="low"
            )
            
            logger.info(f"User authenticated: {username}")
            return True, user.id, session_id
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return False, None, "Authentication error"
    
    def create_session(self, user_id: str, ip_address: str, user_agent: str) -> str:
        """Crear sesión de usuario"""
        try:
            session_id = secrets.token_urlsafe(32)
            token = self.generate_jwt_token(user_id)
            expires_at = datetime.now() + timedelta(seconds=self.config.session_timeout)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO sessions (id, user_id, token, created_at, expires_at, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                user_id,
                token,
                datetime.now().isoformat(),
                expires_at.isoformat(),
                ip_address,
                user_agent
            ))
            
            conn.commit()
            conn.close()
            
            # Agregar a cache
            with self.session_lock:
                self.active_sessions[session_id] = {
                    'user_id': user_id,
                    'created_at': datetime.now(),
                    'expires_at': expires_at,
                    'ip_address': ip_address,
                    'user_agent': user_agent
                }
            
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
    
    def generate_jwt_token(self, user_id: str) -> str:
        """Generar token JWT"""
        try:
            payload = {
                'user_id': user_id,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=self.config.jwt_expiry)
            }
            
            token = jwt.encode(payload, self.config.jwt_secret, algorithm='HS256')
            return token
            
        except Exception as e:
            logger.error(f"Error generating JWT token: {e}")
            raise
    
    def verify_jwt_token(self, token: str) -> Tuple[bool, Optional[str]]:
        """Verificar token JWT"""
        try:
            payload = jwt.decode(token, self.config.jwt_secret, algorithms=['HS256'])
            return True, payload.get('user_id')
        except jwt.ExpiredSignatureError:
            return False, None
        except jwt.InvalidTokenError:
            return False, None
        except Exception as e:
            logger.error(f"Error verifying JWT token: {e}")
            return False, None
    
    def validate_session(self, session_id: str) -> Tuple[bool, Optional[str]]:
        """Validar sesión"""
        try:
            # Verificar en cache primero
            with self.session_lock:
                if session_id in self.active_sessions:
                    session = self.active_sessions[session_id]
                    if datetime.now() < session['expires_at']:
                        return True, session['user_id']
                    else:
                        # Sesión expirada
                        del self.active_sessions[session_id]
            
            # Verificar en base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, expires_at FROM sessions
                WHERE id = ? AND is_active = 1
            """, (session_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                user_id, expires_at = result
                if datetime.now() < datetime.fromisoformat(expires_at):
                    # Actualizar cache
                    with self.session_lock:
                        self.active_sessions[session_id] = {
                            'user_id': user_id,
                            'created_at': datetime.now(),
                            'expires_at': datetime.fromisoformat(expires_at),
                            'ip_address': 'unknown',
                            'user_agent': 'unknown'
                        }
                    return True, user_id
                else:
                    # Sesión expirada
                    self.invalidate_session(session_id)
            
            return False, None
            
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return False, None
    
    def invalidate_session(self, session_id: str):
        """Invalidar sesión"""
        try:
            # Remover de cache
            with self.session_lock:
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]
            
            # Marcar como inactiva en base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE sessions SET is_active = 0 WHERE id = ?
            """, (session_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error invalidating session: {e}")
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Obtener usuario por nombre de usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, email, role, permissions, created_at, last_login,
                       is_active, failed_attempts, locked_until
                FROM users WHERE username = ?
            """, (username,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return User(
                    id=result[0],
                    username=result[1],
                    email=result[2],
                    role=result[3],
                    permissions=json.loads(result[4]),
                    created_at=datetime.fromisoformat(result[5]),
                    last_login=datetime.fromisoformat(result[6]) if result[6] else None,
                    is_active=bool(result[7]),
                    failed_attempts=result[8],
                    locked_until=datetime.fromisoformat(result[9]) if result[9] else None
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, email, role, permissions, created_at, last_login,
                       is_active, failed_attempts, locked_until
                FROM users WHERE email = ?
            """, (email,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return User(
                    id=result[0],
                    username=result[1],
                    email=result[2],
                    role=result[3],
                    permissions=json.loads(result[4]),
                    created_at=datetime.fromisoformat(result[5]),
                    last_login=datetime.fromisoformat(result[6]) if result[6] else None,
                    is_active=bool(result[7]),
                    failed_attempts=result[8],
                    locked_until=datetime.fromisoformat(result[9]) if result[9] else None
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    def check_permission(self, user_id: str, permission: str) -> bool:
        """Verificar permiso de usuario"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            return permission in user.permissions or user.role == 'admin'
            
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Obtener usuario por ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, email, role, permissions, created_at, last_login,
                       is_active, failed_attempts, locked_until
                FROM users WHERE id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return User(
                    id=result[0],
                    username=result[1],
                    email=result[2],
                    role=result[3],
                    permissions=json.loads(result[4]),
                    created_at=datetime.fromisoformat(result[5]),
                    last_login=datetime.fromisoformat(result[6]) if result[6] else None,
                    is_active=bool(result[7]),
                    failed_attempts=result[8],
                    locked_until=datetime.fromisoformat(result[9]) if result[9] else None
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    def log_security_event(self, event_type: str, user_id: Optional[str], ip_address: str, 
                          user_agent: str, details: Dict[str, Any], severity: str):
        """Registrar evento de seguridad"""
        try:
            event_id = secrets.token_urlsafe(16)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO security_events (id, event_type, user_id, ip_address, user_agent,
                                           timestamp, details, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id,
                event_type,
                user_id,
                ip_address,
                user_agent,
                datetime.now().isoformat(),
                json.dumps(details),
                severity
            ))
            
            conn.commit()
            conn.close()
            
            # Log crítico
            if severity in ['high', 'critical']:
                logger.warning(f"Security event: {event_type} - {severity} - {details}")
            
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
    
    def _check_rate_limit(self, ip_address: str) -> bool:
        """Verificar rate limiting"""
        try:
            with self.rate_limit_lock:
                now = time.time()
                window_start = now - self.config.rate_limit_window
                
                # Limpiar requests antiguos
                while self.rate_limits[ip_address] and self.rate_limits[ip_address][0] < window_start:
                    self.rate_limits[ip_address].popleft()
                
                # Verificar límite
                if len(self.rate_limits[ip_address]) >= self.config.rate_limit_requests:
                    return False
                
                # Agregar request actual
                self.rate_limits[ip_address].append(now)
                return True
                
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True  # Permitir en caso de error
    
    def _increment_failed_attempts(self, ip_address: str):
        """Incrementar intentos fallidos por IP"""
        try:
            self.failed_attempts[ip_address] += 1
            
            if self.failed_attempts[ip_address] >= self.config.max_failed_attempts:
                self.lockouts[ip_address] = datetime.now() + timedelta(seconds=self.config.lockout_duration)
                
                self.log_security_event(
                    event_type="ip_locked",
                    user_id=None,
                    ip_address=ip_address,
                    user_agent="system",
                    details={"failed_attempts": self.failed_attempts[ip_address]},
                    severity="high"
                )
                
        except Exception as e:
            logger.error(f"Error incrementing failed attempts: {e}")
    
    def _reset_failed_attempts(self, ip_address: str):
        """Resetear intentos fallidos por IP"""
        try:
            self.failed_attempts[ip_address] = 0
            if ip_address in self.lockouts:
                del self.lockouts[ip_address]
        except Exception as e:
            logger.error(f"Error resetting failed attempts: {e}")
    
    def _increment_user_failed_attempts(self, user_id: str):
        """Incrementar intentos fallidos de usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users SET failed_attempts = failed_attempts + 1
                WHERE id = ?
            """, (user_id,))
            
            # Verificar si debe bloquearse
            cursor.execute("SELECT failed_attempts FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            
            if result and result[0] >= self.config.max_failed_attempts:
                lockout_until = datetime.now() + timedelta(seconds=self.config.lockout_duration)
                cursor.execute("""
                    UPDATE users SET locked_until = ? WHERE id = ?
                """, (lockout_until.isoformat(), user_id))
                
                self.log_security_event(
                    event_type="user_locked",
                    user_id=user_id,
                    ip_address="unknown",
                    user_agent="system",
                    details={"failed_attempts": result[0]},
                    severity="high"
                )
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error incrementing user failed attempts: {e}")
    
    def _reset_user_failed_attempts(self, user_id: str):
        """Resetear intentos fallidos de usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users SET failed_attempts = 0, locked_until = NULL
                WHERE id = ?
            """, (user_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error resetting user failed attempts: {e}")
    
    def encrypt_data(self, data: str) -> str:
        """Encriptar datos sensibles"""
        try:
            from cryptography.fernet import Fernet
            key = self.config.encryption_key.encode()
            f = Fernet(key)
            encrypted = f.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Desencriptar datos sensibles"""
        try:
            from cryptography.fernet import Fernet
            key = self.config.encryption_key.encode()
            f = Fernet(key)
            decrypted = f.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise
    
    def get_security_events(self, limit: int = 100, severity: str = None) -> List[SecurityEvent]:
        """Obtener eventos de seguridad"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
                SELECT id, event_type, user_id, ip_address, user_agent, timestamp,
                       details, severity, resolved
                FROM security_events
            """
            params = []
            
            if severity:
                query += " WHERE severity = ?"
                params.append(severity)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            events = []
            for result in results:
                events.append(SecurityEvent(
                    id=result[0],
                    event_type=result[1],
                    user_id=result[2],
                    ip_address=result[3],
                    user_agent=result[4],
                    timestamp=datetime.fromisoformat(result[5]),
                    details=json.loads(result[6]),
                    severity=result[7],
                    resolved=bool(result[8])
                ))
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting security events: {e}")
            return []
    
    def cleanup_expired_sessions(self):
        """Limpiar sesiones expiradas"""
        try:
            now = datetime.now()
            
            # Limpiar cache
            with self.session_lock:
                expired_sessions = [
                    session_id for session_id, session in self.active_sessions.items()
                    if now >= session['expires_at']
                ]
                for session_id in expired_sessions:
                    del self.active_sessions[session_id]
            
            # Limpiar base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE sessions SET is_active = 0
                WHERE expires_at < ? AND is_active = 1
            """, (now.isoformat(),))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")

def require_auth(security_module: AdvancedSecurityModule):
    """Decorador para requerir autenticación"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Obtener session_id de los argumentos o headers
            session_id = kwargs.get('session_id') or args[0] if args else None
            
            if not session_id:
                return {"error": "Authentication required"}, 401
            
            # Validar sesión
            is_valid, user_id = security_module.validate_session(session_id)
            if not is_valid:
                return {"error": "Invalid session"}, 401
            
            # Agregar user_id a los argumentos
            kwargs['user_id'] = user_id
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def require_permission(security_module: AdvancedSecurityModule, permission: str):
    """Decorador para requerir permiso específico"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id')
            if not user_id:
                return {"error": "Authentication required"}, 401
            
            if not security_module.check_permission(user_id, permission):
                return {"error": "Insufficient permissions"}, 403
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def main():
    """Función principal para demostrar módulo de seguridad"""
    print("=" * 60)
    print("ADVANCED SECURITY MODULE - DEMO")
    print("=" * 60)
    
    # Inicializar módulo de seguridad
    security = AdvancedSecurityModule()
    
    # Crear usuario de prueba
    print("Creating test user...")
    try:
        user_id = security.create_user(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!",
            role="admin",
            permissions=["read", "write", "admin"]
        )
        print(f"✓ User created with ID: {user_id}")
    except ValueError as e:
        print(f"User creation failed: {e}")
        return
    
    # Autenticar usuario
    print("\nAuthenticating user...")
    success, auth_user_id, session_id = security.authenticate_user(
        username="testuser",
        password="SecurePass123!",
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0 (Test Browser)"
    )
    
    if success:
        print(f"✓ Authentication successful")
        print(f"  User ID: {auth_user_id}")
        print(f"  Session ID: {session_id}")
    else:
        print(f"✗ Authentication failed")
        return
    
    # Validar sesión
    print("\nValidating session...")
    is_valid, session_user_id = security.validate_session(session_id)
    if is_valid:
        print(f"✓ Session valid for user: {session_user_id}")
    else:
        print("✗ Session invalid")
    
    # Verificar permisos
    print("\nChecking permissions...")
    permissions_to_check = ["read", "write", "admin", "delete"]
    for permission in permissions_to_check:
        has_permission = security.check_permission(auth_user_id, permission)
        status = "✓" if has_permission else "✗"
        print(f"  {status} {permission}: {has_permission}")
    
    # Obtener eventos de seguridad
    print("\nSecurity events:")
    events = security.get_security_events(limit=5)
    for event in events:
        print(f"  • {event.event_type} - {event.severity} - {event.timestamp}")
    
    # Limpiar sesiones expiradas
    print("\nCleaning up expired sessions...")
    security.cleanup_expired_sessions()
    print("✓ Cleanup completed")
    
    print("\n" + "=" * 60)
    print("SECURITY MODULE DEMO COMPLETED")
    print("=" * 60)
    print("🔒 Security features:")
    print("  • User authentication and authorization")
    print("  • Session management")
    print("  • Rate limiting")
    print("  • Security event logging")
    print("  • Password strength validation")
    print("  • Account lockout protection")
    print("  • Data encryption")

if __name__ == "__main__":
    main()






