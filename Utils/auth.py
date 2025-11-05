"""
Sistema de autenticación JWT para la API
"""
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

# Configuración JWT
JWT_SECRET_KEY = 'inventory_system_secret_key_2024'  # En producción usar variable de entorno
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Usuarios básicos (en producción usar base de datos)
USERS = {
    'admin': {
        'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
        'role': 'admin',
        'permissions': ['read', 'write', 'delete', 'admin']
    },
    'manager': {
        'password_hash': hashlib.sha256('manager123'.encode()).hexdigest(),
        'role': 'manager',
        'permissions': ['read', 'write']
    },
    'viewer': {
        'password_hash': hashlib.sha256('viewer123'.encode()).hexdigest(),
        'role': 'viewer',
        'permissions': ['read']
    }
}

def hash_password(password):
    """Genera hash de contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verifica contraseña contra hash"""
    return hash_password(password) == password_hash

def generate_token(username, role, permissions):
    """Genera token JWT"""
    payload = {
        'username': username,
        'role': role,
        'permissions': permissions,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(token):
    """Verifica y decodifica token JWT"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def authenticate_user(username, password):
    """Autentica usuario y devuelve token si es válido"""
    if username not in USERS:
        return None
    
    user = USERS[username]
    if not verify_password(password, user['password_hash']):
        return None
    
    token = generate_token(
        username=username,
        role=user['role'],
        permissions=user['permissions']
    )
    
    return {
        'token': token,
        'username': username,
        'role': user['role'],
        'permissions': user['permissions']
    }

def require_auth(f):
    """Decorator para requerir autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Buscar token en header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Token malformado'}), 401
        
        if not token:
            return jsonify({'error': 'Token de acceso requerido'}), 401
        
        # Verificar token
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
        # Agregar información del usuario al contexto
        request.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_permission(permission):
    """Decorator para requerir permiso específico"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Autenticación requerida'}), 401
            
            user_permissions = request.current_user.get('permissions', [])
            if permission not in user_permissions:
                return jsonify({
                    'error': f'Permiso {permission} requerido'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_role(role):
    """Decorator para requerir rol específico"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Autenticación requerida'}), 401
            
            user_role = request.current_user.get('role')
            if user_role != role:
                return jsonify({
                    'error': f'Rol {role} requerido'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """Obtiene información del usuario actual"""
    if hasattr(request, 'current_user'):
        return request.current_user
    return None

def is_admin():
    """Verifica si el usuario actual es admin"""
    user = get_current_user()
    return user and user.get('role') == 'admin'

def has_permission(permission):
    """Verifica si el usuario actual tiene un permiso"""
    user = get_current_user()
    if not user:
        return False
    return permission in user.get('permissions', [])



