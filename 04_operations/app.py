#!/usr/bin/env python3
"""
Punto de entrada principal para el Sistema de Control de Inventario Inteligente.
Este archivo permite ejecutar la aplicación desde la raíz del proyecto.
"""
import sys
import os

# Agregar el directorio actual y 05_Technology al path para que los imports funcionen
current_dir = os.path.dirname(os.path.abspath(__file__))
tech_dir = os.path.join(current_dir, '05_Technology')
sys.path.insert(0, current_dir)
sys.path.insert(0, tech_dir)

# Importar configuración
try:
    from config import config
    import os as os_module
    config_name = os_module.getenv('FLASK_ENV', 'default')
    if config_name not in config:
        config_name = 'default'
except ImportError:
    config = None
    config_name = None

# Crear módulos de compatibilidad para imports
# Primero necesitamos inicializar Flask y db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_mail import Mail
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar extensiones (estas serán compartidas)
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app(config_name='default'):
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    # Cargar configuración
    if config:
        app.config.from_object(config[config_name])
        config[config_name].init_app(app) if hasattr(config[config_name], 'init_app') else None
    else:
        # Configuración básica si no hay archivo config.py
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///inventory.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuración de email
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1', 'yes']
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['ADMIN_EMAIL'] = os.getenv('ADMIN_EMAIL', 'admin@company.com')
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    mail.init_app(app)
    
    # Configurar logging (soporte JSON opcional)
    import logging
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    use_json = os.getenv('LOG_JSON', 'false').lower() in ['true', '1', 'yes']
    
    if use_json:
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                import json, time
                data = {
                    'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(record.created)),
                    'level': record.levelname,
                    'logger': record.name,
                    'message': record.getMessage()
                }
                # Incluir extras comunes si están presentes
                for extra_key in ('request_id', 'path', 'method', 'status'):
                    if hasattr(record, extra_key):
                        data[extra_key] = getattr(record, extra_key)
                return json.dumps(data)
        handler = logging.StreamHandler()
        handler.setLevel(log_level)
        handler.setFormatter(JsonFormatter())
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(log_level)
        root_logger.addHandler(handler)
    else:
        try:
            from utils.logger_config import setup_logging
            setup_logging(app, log_level=log_level)
        except ImportError:
            logging.basicConfig(
                level=log_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    
    # Cargar y configurar modelos ANTES de importar blueprints
    # Esto es crítico porque los blueprints importan desde models
    with app.app_context():
        try:
            import importlib.util
            models_path = os.path.join(tech_dir, 'models.py')
            if os.path.exists(models_path):
                # Crear un namespace con db inyectado y dependencias
                from datetime import datetime as dt_module
                models_namespace = {
                    'db': db,
                    'datetime': dt_module,
                    '__name__': '__main__'
                }
                
                # Leer y ejecutar el archivo de modelos con el namespace
                with open(models_path, 'r', encoding='utf-8') as f:
                    models_code = f.read()
                
                # Ejecutar el código en el namespace preparado
                exec(compile(models_code, models_path, 'exec'), models_namespace)
                
                # Ahora actualizar el módulo models.py en la raíz
                import models as root_models
                root_models.Product = models_namespace['Product']
                root_models.InventoryRecord = models_namespace['InventoryRecord']
                root_models.Alert = models_namespace['Alert']
                root_models.SalesRecord = models_namespace['SalesRecord']
                root_models.ReorderRecommendation = models_namespace['ReorderRecommendation']
                root_models.Supplier = models_namespace['Supplier']
                root_models.Customer = models_namespace['Customer']
                root_models.KPIMetric = models_namespace['KPIMetric']
                
                logging.info("✓ Modelos cargados correctamente")
            else:
                logging.error(f"Archivo de modelos no encontrado: {models_path}")
        except Exception as e:
            logging.error(f"Error cargando modelos: {e}")
            import traceback
            logging.error(traceback.format_exc())
    
    # Registrar blueprints
    try:
        from routes.main import main_bp
        from routes.api import api_bp
        from routes.api_advanced import api_advanced_bp
        from routes.ml_api import ml_bp
        from routes.integration_api import integration_bp
        from routes.ai_blockchain_api import ai_blockchain_bp
        from routes.iot_ar_api import iot_ar_bp
        from routes.predictive_logistics_api import predictive_logistics_bp
        from routes.quality_sustainability_api import quality_sustainability_bp
        from routes.realtime import realtime_bp, init_realtime_system
        
        app.register_blueprint(main_bp)
        app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(api_advanced_bp, url_prefix='/api')
        app.register_blueprint(ml_bp, url_prefix='/api')
        app.register_blueprint(integration_bp, url_prefix='/api')
        app.register_blueprint(ai_blockchain_bp, url_prefix='/api')
        app.register_blueprint(iot_ar_bp, url_prefix='/api')
        app.register_blueprint(predictive_logistics_bp, url_prefix='/api')
        app.register_blueprint(quality_sustainability_bp, url_prefix='/api')
        app.register_blueprint(realtime_bp)
        
        # Inicializar sistema de tiempo real
        init_realtime_system(app)
            
    except ImportError as e:
        logging.warning(f'Algunos blueprints no están disponibles: {e}')
    
    # Registrar manejadores de error
    try:
        from utils.error_handlers import register_error_handlers
        register_error_handlers(app)
    except ImportError:
        pass  # Si no hay error handlers, continuar sin ellos
    
    # Registrar middlewares
    try:
        from utils.middleware import register_all_middleware
        register_all_middleware(app)
    except ImportError:
        logging.warning("Middlewares no disponibles")
    
    # Inicializar servicio de notificaciones
    try:
        from utils.notifications import init_notification_service
        init_notification_service(mail)
        logging.info("✓ Servicio de notificaciones inicializado")
    except ImportError:
        logging.warning("Servicio de notificaciones no disponible")

    # Iniciar scheduler diario (opcional)
    try:
        from utils.scheduler import init_scheduler
        init_scheduler(app)
    except Exception as e:
        logging.warning(f"Scheduler no iniciado: {e}")
    
    return app

if __name__ == '__main__':
    # Determinar configuración basada en variable de entorno
    env_config = os.getenv('FLASK_ENV', 'development')
    app = create_app(config_name=env_config if config else 'default')
    
    # Mensaje informativo
    print("\n" + "="*60)
    print("Sistema de Control de Inventario Inteligente")
    print("="*60)
    print(f"Base de datos: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Modo debug: {app.config.get('DEBUG', False)}")
    print("="*60)
    print("\nServidor iniciado en http://0.0.0.0:5000")
    print("Presiona Ctrl+C para detener el servidor\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
