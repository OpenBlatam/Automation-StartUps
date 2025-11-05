"""
Middleware y hooks para la aplicación Flask
"""
from functools import wraps
from flask import request, jsonify, g
from datetime import datetime, timedelta
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter simple para endpoints"""
    
    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.default_limit = 60  # requests por minuto
        self.window = 60  # segundos
    
    def is_allowed(self, key: str, limit: Optional[int] = None) -> tuple[bool, int]:
        """
        Verifica si una request está permitida
        Retorna (is_allowed, remaining_requests)
        """
        limit = limit or self.default_limit
        now = datetime.now()
        
        # Limpiar requests antiguos
        if key in self.requests:
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if (now - req_time).total_seconds() < self.window
            ]
        else:
            self.requests[key] = []
        
        # Verificar límite
        if len(self.requests[key]) >= limit:
            return False, 0
        
        # Agregar nueva request
        self.requests[key].append(now)
        remaining = limit - len(self.requests[key])
        
        return True, remaining
    
    def get_client_key(self, request) -> str:
        """Obtiene una clave única para el cliente"""
        # Usar IP o session ID
        ip = request.remote_addr or 'unknown'
        return ip

# Instancia global del rate limiter
rate_limiter = RateLimiter()

def rate_limit(max_per_minute: int = 60):
    """Decorador para rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            key = rate_limiter.get_client_key(request)
            allowed, remaining = rate_limiter.is_allowed(key, max_per_minute)
            
            if not allowed:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Demasiadas solicitudes. Intenta nuevamente en un momento.',
                    'retry_after': 60
                }), 429
            
            # Agregar headers con información de rate limit
            response = f(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = str(max_per_minute)
                response.headers['X-RateLimit-Remaining'] = str(remaining)
            
            return response
        return decorated_function
    return decorator

def request_logging_middleware(app):
    """Middleware para loggear todas las requests"""
    
    @app.before_request
    def log_request_info():
        """Loggea información de la request"""
        g.start_time = datetime.now()
        
        logger.info(
            f"Request: {request.method} {request.path} - "
            f"IP: {request.remote_addr} - "
            f"User-Agent: {request.headers.get('User-Agent', 'Unknown')[:50]}"
        )
    
    @app.after_request
    def log_response_info(response):
        """Loggea información de la response"""
        if hasattr(g, 'start_time'):
            duration = (datetime.now() - g.start_time).total_seconds()
            logger.info(
                f"Response: {request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.3f}s"
            )
        return response

def cors_middleware(app):
    """Configuración de CORS básica"""
    
    @app.after_request
    def after_request(response):
        """Agrega headers CORS"""
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

def security_headers_middleware(app):
    """Middleware para agregar headers de seguridad"""
    
    @app.after_request
    def add_security_headers(response):
        """Agrega headers de seguridad HTTP"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Solo agregar CSP y HSTS en producción
        if not app.config.get('DEBUG'):
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Content-Security-Policy'] = "default-src 'self'"
        
        return response

def request_id_middleware(app):
    """Middleware para agregar ID único a cada request"""
    
    @app.before_request
    def add_request_id():
        """Agrega un ID único a cada request"""
        import uuid
        g.request_id = str(uuid.uuid4())[:8]
        logger.debug(f"Request ID: {g.request_id}")

def register_all_middleware(app):
    """Registra todos los middlewares"""
    request_logging_middleware(app)
    cors_middleware(app)
    security_headers_middleware(app)
    request_id_middleware(app)
    
    logger.info("Todos los middlewares registrados correctamente")

