from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_mail import Mail
import logging
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar extensiones
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app():
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///inventory.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuración de email
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1', 'yes']
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    mail.init_app(app)
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Registrar blueprints
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
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)