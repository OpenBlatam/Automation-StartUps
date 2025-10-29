from datetime import datetime
from app import db
import json
import logging

class SystemConfig(db.Model):
    """Configuración del sistema"""
    __tablename__ = 'system_config'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    data_type = db.Column(db.String(20), default='string')  # string, int, float, bool, json
    category = db.Column(db.String(50), default='general')
    description = db.Column(db.Text)
    is_editable = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_value(self):
        """Obtiene el valor con el tipo correcto"""
        if self.data_type == 'int':
            return int(self.value) if self.value else 0
        elif self.data_type == 'float':
            return float(self.value) if self.value else 0.0
        elif self.data_type == 'bool':
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.data_type == 'json':
            return json.loads(self.value) if self.value else {}
        else:
            return self.value
    
    def set_value(self, value):
        """Establece el valor con el tipo correcto"""
        if self.data_type == 'json':
            self.value = json.dumps(value)
        else:
            self.value = str(value)
    
    @staticmethod
    def get_config(key, default=None):
        """Obtiene configuración por clave"""
        config = SystemConfig.query.filter_by(key=key).first()
        if config:
            return config.get_value()
        return default
    
    @staticmethod
    def set_config(key, value, data_type='string', category='general', description=''):
        """Establece configuración"""
        config = SystemConfig.query.filter_by(key=key).first()
        if not config:
            config = SystemConfig(key=key, data_type=data_type, category=category, description=description)
            db.session.add(config)
        
        config.set_value(value)
        db.session.commit()
        return config
    
    def __repr__(self):
        return f'<SystemConfig {self.key}={self.value}>'

class NotificationTemplate(db.Model):
    """Plantillas de notificaciones"""
    __tablename__ = 'notification_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    template_type = db.Column(db.String(50), nullable=False)  # email, sms, webhook
    subject = db.Column(db.String(200))
    body_template = db.Column(db.Text, nullable=False)
    variables = db.Column(db.Text)  # JSON con variables disponibles
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_variables(self):
        """Obtiene variables como diccionario"""
        return json.loads(self.variables) if self.variables else {}
    
    def set_variables(self, variables):
        """Establece variables"""
        self.variables = json.dumps(variables)
    
    def render_template(self, context):
        """Renderiza la plantilla con el contexto"""
        try:
            return self.body_template.format(**context)
        except KeyError as e:
            logging.error(f"Variable faltante en plantilla {self.name}: {e}")
            return self.body_template
    
    def __repr__(self):
        return f'<NotificationTemplate {self.name}>'

class BackupConfig(db.Model):
    """Configuración de respaldos"""
    __tablename__ = 'backup_config'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    backup_type = db.Column(db.String(20), nullable=False)  # full, incremental, differential
    schedule = db.Column(db.String(50), nullable=False)  # cron expression
    retention_days = db.Column(db.Integer, default=30)
    is_active = db.Column(db.Boolean, default=True)
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BackupConfig {self.name}>'

class IntegrationConfig(db.Model):
    """Configuración de integraciones"""
    __tablename__ = 'integration_config'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    integration_type = db.Column(db.String(50), nullable=False)  # erp, crm, api
    config_data = db.Column(db.Text)  # JSON con configuración
    is_active = db.Column(db.Boolean, default=True)
    last_sync = db.Column(db.DateTime)
    sync_frequency = db.Column(db.Integer, default=3600)  # segundos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_config(self):
        """Obtiene configuración como diccionario"""
        return json.loads(self.config_data) if self.config_data else {}
    
    def set_config(self, config):
        """Establece configuración"""
        self.config_data = json.dumps(config)
    
    def __repr__(self):
        return f'<IntegrationConfig {self.name}>'



