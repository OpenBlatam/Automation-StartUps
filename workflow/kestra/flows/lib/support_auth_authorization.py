"""
Sistema de Autenticación y Autorización para Soporte.

Gestión de usuarios, roles, permisos y seguridad.
"""
import logging
import hashlib
import secrets
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logger.warning("PyJWT no disponible. Instala con: pip install PyJWT")
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class Role(Enum):
    """Roles del sistema."""
    ADMIN = "admin"
    AGENT = "agent"
    MANAGER = "manager"
    VIEWER = "viewer"
    CUSTOMER = "customer"
    API_USER = "api_user"


class Permission(Enum):
    """Permisos del sistema."""
    # Tickets
    CREATE_TICKET = "create_ticket"
    VIEW_TICKET = "view_ticket"
    EDIT_TICKET = "edit_ticket"
    DELETE_TICKET = "delete_ticket"
    ASSIGN_TICKET = "assign_ticket"
    CLOSE_TICKET = "close_ticket"
    
    # Agentes
    VIEW_AGENTS = "view_agents"
    MANAGE_AGENTS = "manage_agents"
    
    # Reportes
    VIEW_REPORTS = "view_reports"
    VIEW_EXECUTIVE_REPORTS = "view_executive_reports"
    
    # Configuración
    MANAGE_SETTINGS = "manage_settings"
    MANAGE_RULES = "manage_rules"
    
    # API
    USE_API = "use_api"
    MANAGE_API_KEYS = "manage_api_keys"


# Mapeo de roles a permisos
ROLE_PERMISSIONS = {
    Role.ADMIN: set(Permission),
    Role.MANAGER: {
        Permission.VIEW_TICKET,
        Permission.EDIT_TICKET,
        Permission.ASSIGN_TICKET,
        Permission.CLOSE_TICKET,
        Permission.VIEW_AGENTS,
        Permission.MANAGE_AGENTS,
        Permission.VIEW_REPORTS,
        Permission.VIEW_EXECUTIVE_REPORTS,
        Permission.MANAGE_RULES,
        Permission.USE_API
    },
    Role.AGENT: {
        Permission.CREATE_TICKET,
        Permission.VIEW_TICKET,
        Permission.EDIT_TICKET,
        Permission.CLOSE_TICKET,
        Permission.VIEW_REPORTS,
        Permission.USE_API
    },
    Role.VIEWER: {
        Permission.VIEW_TICKET,
        Permission.VIEW_REPORTS
    },
    Role.CUSTOMER: {
        Permission.CREATE_TICKET,
        Permission.VIEW_TICKET
    },
    Role.API_USER: {
        Permission.CREATE_TICKET,
        Permission.VIEW_TICKET,
        Permission.USE_API
    }
}


@dataclass
class User:
    """Usuario del sistema."""
    user_id: str
    email: str
    username: str
    role: Role
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    metadata: Dict[str, Any]


@dataclass
class APIKey:
    """Clave de API."""
    key_id: str
    user_id: str
    key_hash: str
    name: str
    permissions: Set[Permission]
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class AuthToken:
    """Token de autenticación."""
    token: str
    user_id: str
    expires_at: datetime
    created_at: datetime


class AuthManager:
    """Gestor de autenticación y autorización."""
    
    def __init__(self, db_connection, secret_key: str):
        """
        Inicializar gestor de autenticación.
        
        Args:
            db_connection: Conexión a base de datos
            secret_key: Clave secreta para JWT
        """
        self.db = db_connection
        self.secret_key = secret_key
    
    def create_user(self, email: str, username: str, password: str, role: Role, metadata: Optional[Dict[str, Any]] = None) -> User:
        """
        Crear nuevo usuario.
        
        Args:
            email: Email del usuario
            username: Nombre de usuario
            password: Contraseña (será hasheada)
            role: Rol del usuario
            metadata: Metadatos adicionales
            
        Returns:
            Usuario creado
        """
        try:
            user_id = f"user-{secrets.token_hex(8)}"
            password_hash = self._hash_password(password)
            
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO support_users
                (user_id, email, username, password_hash, role, is_active, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                email,
                username,
                password_hash,
                role.value,
                True,
                metadata or {},
                datetime.now()
            ))
            
            self.db.commit()
            
            return User(
                user_id=user_id,
                email=email,
                username=username,
                role=role,
                is_active=True,
                created_at=datetime.now(),
                last_login=None,
                metadata=metadata or {}
            )
            
        except Exception as e:
            logger.error(f"Error creando usuario: {e}")
            self.db.rollback()
            raise
    
    def authenticate(self, email: str, password: str) -> Optional[AuthToken]:
        """
        Autenticar usuario.
        
        Args:
            email: Email del usuario
            password: Contraseña
            
        Returns:
            Token de autenticación o None
        """
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT user_id, password_hash, role, is_active
                FROM support_users
                WHERE email = %s
            """, (email,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            user_id, password_hash, role_str, is_active = result
            
            if not is_active:
                return None
            
            # Verificar contraseña
            if not self._verify_password(password, password_hash):
                return None
            
            # Generar token
            token = self._generate_token(user_id, role_str)
            expires_at = datetime.now() + timedelta(hours=24)
            
            # Guardar token
            cursor.execute("""
                INSERT INTO support_auth_tokens
                (token, user_id, expires_at, created_at)
                VALUES (%s, %s, %s, %s)
            """, (token, user_id, expires_at, datetime.now()))
            
            # Actualizar último login
            cursor.execute("""
                UPDATE support_users
                SET last_login = %s
                WHERE user_id = %s
            """, (datetime.now(), user_id))
            
            self.db.commit()
            
            return AuthToken(
                token=token,
                user_id=user_id,
                expires_at=expires_at,
                created_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error autenticando: {e}")
            self.db.rollback()
            return None
    
    def verify_token(self, token: str) -> Optional[User]:
        """
        Verificar token de autenticación.
        
        Args:
            token: Token a verificar
            
        Returns:
            Usuario o None
        """
        try:
            # Verificar en base de datos
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT t.user_id, t.expires_at, u.email, u.username, u.role, u.is_active
                FROM support_auth_tokens t
                JOIN support_users u ON t.user_id = u.user_id
                WHERE t.token = %s
                AND t.expires_at > %s
            """, (token, datetime.now()))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            user_id, expires_at, email, username, role_str, is_active = result
            
            if not is_active:
                return None
            
            return User(
                user_id=user_id,
                email=email,
                username=username,
                role=Role(role_str),
                is_active=is_active,
                created_at=datetime.now(),
                last_login=None,
                metadata={}
            )
            
        except Exception as e:
            logger.error(f"Error verificando token: {e}")
            return None
    
    def check_permission(self, user: User, permission: Permission) -> bool:
        """
        Verificar si usuario tiene permiso.
        
        Args:
            user: Usuario
            permission: Permiso a verificar
            
        Returns:
            True si tiene permiso
        """
        user_permissions = ROLE_PERMISSIONS.get(user.role, set())
        return permission in user_permissions
    
    def create_api_key(self, user_id: str, name: str, permissions: Set[Permission], expires_days: Optional[int] = None) -> tuple[str, APIKey]:
        """
        Crear clave de API.
        
        Args:
            user_id: ID del usuario
            name: Nombre de la clave
            permissions: Permisos
            expires_days: Días hasta expiración (None = nunca)
            
        Returns:
            Tupla (clave_plain, APIKey)
        """
        try:
            key_id = f"key-{secrets.token_hex(12)}"
            api_key = secrets.token_urlsafe(32)
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            expires_at = None
            if expires_days:
                expires_at = datetime.now() + timedelta(days=expires_days)
            
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO support_api_keys
                (key_id, user_id, key_hash, name, permissions, expires_at, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                key_id,
                user_id,
                key_hash,
                name,
                [p.value for p in permissions],
                expires_at,
                datetime.now()
            ))
            
            self.db.commit()
            
            api_key_obj = APIKey(
                key_id=key_id,
                user_id=user_id,
                key_hash=key_hash,
                name=name,
                permissions=permissions,
                expires_at=expires_at,
                last_used=None,
                created_at=datetime.now(),
                metadata={}
            )
            
            return api_key, api_key_obj
            
        except Exception as e:
            logger.error(f"Error creando API key: {e}")
            self.db.rollback()
            raise
    
    def verify_api_key(self, api_key: str) -> Optional[APIKey]:
        """
        Verificar clave de API.
        
        Args:
            api_key: Clave a verificar
            
        Returns:
            APIKey o None
        """
        try:
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT key_id, user_id, key_hash, name, permissions, expires_at, last_used, created_at
                FROM support_api_keys
                WHERE key_hash = %s
            """, (key_hash,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            key_id, user_id, key_hash, name, permissions_list, expires_at, last_used, created_at = result
            
            # Verificar expiración
            if expires_at and expires_at < datetime.now():
                return None
            
            # Actualizar último uso
            cursor.execute("""
                UPDATE support_api_keys
                SET last_used = %s
                WHERE key_id = %s
            """, (datetime.now(), key_id))
            
            self.db.commit()
            
            return APIKey(
                key_id=key_id,
                user_id=user_id,
                key_hash=key_hash,
                name=name,
                permissions={Permission(p) for p in permissions_list},
                expires_at=expires_at,
                last_used=datetime.now(),
                created_at=created_at,
                metadata={}
            )
            
        except Exception as e:
            logger.error(f"Error verificando API key: {e}")
            return None
    
    def revoke_api_key(self, key_id: str):
        """Revocar clave de API."""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                DELETE FROM support_api_keys
                WHERE key_id = %s
            """, (key_id,))
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error revocando API key: {e}")
            self.db.rollback()
            raise
    
    def _hash_password(self, password: str) -> str:
        """Hashear contraseña."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verificar contraseña."""
        return self._hash_password(password) == password_hash
    
    def _generate_token(self, user_id: str, role: str) -> str:
        """Generar token JWT."""
        if not JWT_AVAILABLE:
            # Fallback: token simple sin JWT
            import base64
            token_data = f"{user_id}:{role}:{datetime.now().isoformat()}"
            return base64.b64encode(token_data.encode()).decode()
        
        payload = {
            "user_id": user_id,
            "role": role,
            "exp": datetime.now() + timedelta(hours=24),
            "iat": datetime.now()
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

