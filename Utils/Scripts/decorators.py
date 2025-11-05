"""
Decoradores útiles para el sistema
"""
from functools import wraps
from flask import jsonify, request
from datetime import datetime
import logging
import traceback
from typing import Callable

logger = logging.getLogger(__name__)

def handle_exceptions(f: Callable) -> Callable:
    """Decorador para manejar excepciones de forma centralizada"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"Error de validación en {f.__name__}: {str(e)}")
            return jsonify({'error': 'Error de validación', 'message': str(e)}), 400
        except KeyError as e:
            logger.warning(f"Clave faltante en {f.__name__}: {str(e)}")
            return jsonify({'error': 'Datos incompletos', 'message': f'Campo requerido: {str(e)}'}), 400
        except Exception as e:
            logger.error(f"Error no esperado en {f.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': 'Error interno del servidor', 'message': str(e)}), 500
    return decorated_function

def require_json(f: Callable) -> Callable:
    """Decorador para requerir que el request sea JSON"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Content-Type debe ser application/json'}), 400
        return f(*args, **kwargs)
    return decorated_function

def log_request(f: Callable) -> Callable:
    """Decorador para loggear requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = datetime.now()
        logger.info(f"Iniciando {f.__name__} - {request.method} {request.path}")
        
        try:
            result = f(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Completado {f.__name__} en {duration:.2f}s")
            return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error en {f.__name__} después de {duration:.2f}s: {str(e)}")
            raise
    return decorated_function

def validate_json_fields(*required_fields):
    """Decorador para validar que campos JSON estén presentes"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type debe ser application/json'}), 400
            
            data = request.get_json()
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return jsonify({
                    'error': 'Campos requeridos faltantes',
                    'missing_fields': missing_fields
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def cache_response(timeout: int = 300):
    """Decorador simple para cachear respuestas (implementación básica)"""
    _cache = {}
    
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Crear clave de cache basada en función y argumentos
            cache_key = f"{f.__name__}:{str(args)}:{str(kwargs)}"
            current_time = datetime.now().timestamp()
            
            # Verificar si hay una entrada válida en cache
            if cache_key in _cache:
                cached_time, cached_response = _cache[cache_key]
                if current_time - cached_time < timeout:
                    logger.debug(f"Cache hit para {f.__name__}")
                    return cached_response
            
            # Ejecutar función y cachear resultado
            result = f(*args, **kwargs)
            _cache[cache_key] = (current_time, result)
            
            return result
        return decorated_function
    return decorator

def timing(f: Callable) -> Callable:
    """Decorador para medir tiempo de ejecución"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start = datetime.now()
        result = f(*args, **kwargs)
        duration = (datetime.now() - start).total_seconds()
        logger.info(f"{f.__name__} tomó {duration:.3f} segundos")
        return result
    return decorated_function

