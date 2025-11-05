"""
Manejo centralizado de errores para la aplicación
"""
from flask import jsonify, render_template, request
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Registra manejadores de error en la aplicación Flask"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Maneja errores 404"""
        if request.is_json or request.path.startswith('/api'):
            return jsonify({
                'error': 'Recurso no encontrado',
                'message': 'La ruta solicitada no existe',
                'path': request.path
            }), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """Maneja errores 400"""
        if request.is_json or request.path.startswith('/api'):
            return jsonify({
                'error': 'Petición inválida',
                'message': str(error.description) if hasattr(error, 'description') else 'Solicitud mal formada'
            }), 400
        return render_template('errors/400.html', error=error), 400
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Maneja errores 403"""
        if request.is_json or request.path.startswith('/api'):
            return jsonify({
                'error': 'Acceso prohibido',
                'message': 'No tienes permisos para acceder a este recurso'
            }), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        """Maneja errores 500"""
        logger.error(f"Error interno: {error}", exc_info=True)
        
        if request.is_json or request.path.startswith('/api'):
            return jsonify({
                'error': 'Error interno del servidor',
                'message': 'Ocurrió un error inesperado. Por favor, contacta al administrador.',
                'timestamp': datetime.now().isoformat()
            }), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(503)
    def service_unavailable_error(error):
        """Maneja errores 503"""
        if request.is_json or request.path.startswith('/api'):
            return jsonify({
                'error': 'Servicio no disponible',
                'message': 'El servicio está temporalmente no disponible. Por favor, intenta más tarde.'
            }), 503
        return render_template('errors/503.html'), 503
    
    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        """Maneja excepciones no capturadas"""
        logger.error(f"Excepción no manejada: {e}", exc_info=True)
        
        if request.is_json or request.path.startswith('/api'):
            return jsonify({
                'error': 'Error inesperado',
                'message': str(e) if app.config.get('DEBUG') else 'Ocurrió un error inesperado',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        if app.config.get('DEBUG'):
            raise e
        return render_template('errors/500.html'), 500

def create_error_response(message: str, status_code: int = 400, details: dict = None):
    """Crea una respuesta de error estandarizada"""
    response = {
        'error': True,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    
    if details:
        response['details'] = details
    
    return jsonify(response), status_code

