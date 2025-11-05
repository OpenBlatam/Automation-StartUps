"""
Configuración avanzada de logging
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(app=None, log_level=logging.INFO):
    """Configura el sistema de logging con rotación de archivos"""
    
    # Crear directorio de logs si no existe
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Handler para archivo con rotación
    log_file = os.path.join(log_dir, 'app.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Handler para errores
    error_log_file = os.path.join(log_dir, 'errors.log')
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # Agregar handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # Configurar loggers específicos
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    if app:
        app.logger.addHandler(console_handler)
        app.logger.addHandler(file_handler)
        app.logger.addHandler(error_handler)
        app.logger.setLevel(log_level)
    
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger con el nombre especificado"""
    return logging.getLogger(name)

class RequestLogger:
    """Logger especializado para requests HTTP"""
    
    def __init__(self):
        self.logger = logging.getLogger('http.requests')
    
    def log_request(self, method: str, path: str, status_code: int, duration: float):
        """Loggea un request HTTP"""
        self.logger.info(
            f"{method} {path} - {status_code} - {duration:.3f}s"
        )
    
    def log_error(self, method: str, path: str, error: Exception):
        """Loggea un error en un request"""
        self.logger.error(
            f"{method} {path} - Error: {str(error)}",
            exc_info=True
        )

