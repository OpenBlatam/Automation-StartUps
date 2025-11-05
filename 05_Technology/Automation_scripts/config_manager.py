"""
Sistema de Configuración Avanzado
=================================

Sistema de configuración robusto con validación, encriptación
y gestión de múltiples entornos.
"""

import json
import os
import base64
from cryptography.fernet import Fernet
from typing import Dict, Any, Optional
import logging
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class Environment(Enum):
    """Entornos del sistema"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

@dataclass
class DatabaseConfig:
    """Configuración de base de datos"""
    path: str = "inventory.db"
    backup_interval: int = 24  # horas
    max_backups: int = 7
    connection_pool_size: int = 10
    timeout: int = 30
    enable_wal_mode: bool = True
    enable_foreign_keys: bool = True

@dataclass
class NotificationConfig:
    """Configuración de notificaciones"""
    email_enabled: bool = True
    sms_enabled: bool = False
    webhook_enabled: bool = False
    dashboard_enabled: bool = True
    
    # Email settings
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    email_recipients: list = None
    
    # Webhook settings
    webhook_url: str = ""
    webhook_timeout: int = 10
    
    # SMS settings
    sms_provider: str = ""
    sms_api_key: str = ""
    
    def __post_init__(self):
        if self.email_recipients is None:
            self.email_recipients = []

@dataclass
class APIConfig:
    """Configuración de API"""
    rate_limit: int = 100  # requests per minute
    api_key_required: bool = True
    cors_enabled: bool = True
    jwt_secret_key: str = ""
    jwt_expiration_hours: int = 24
    max_request_size: int = 16 * 1024 * 1024  # 16MB

@dataclass
class AnalyticsConfig:
    """Configuración de análisis"""
    prediction_horizon: int = 30  # días
    confidence_threshold: float = 0.8
    seasonal_analysis: bool = True
    ml_model_retrain_interval: int = 7  # días
    enable_real_time_metrics: bool = True
    metrics_retention_days: int = 90

@dataclass
class AlertConfig:
    """Configuración de alertas"""
    check_interval: int = 300  # segundos
    escalation_enabled: bool = True
    auto_resolve: bool = False
    max_alerts_per_product: int = 10
    alert_cooldown_minutes: int = 30

@dataclass
class SecurityConfig:
    """Configuración de seguridad"""
    encryption_key: str = ""
    enable_audit_log: bool = True
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    password_min_length: int = 8
    require_2fa: bool = False

@dataclass
class SystemConfig:
    """Configuración completa del sistema"""
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    log_level: str = "INFO"
    timezone: str = "UTC"
    
    # Sub-configuraciones
    database: DatabaseConfig = None
    notifications: NotificationConfig = None
    api: APIConfig = None
    analytics: AnalyticsConfig = None
    alerts: AlertConfig = None
    security: SecurityConfig = None
    
    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig()
        if self.notifications is None:
            self.notifications = NotificationConfig()
        if self.api is None:
            self.api = APIConfig()
        if self.analytics is None:
            self.analytics = AnalyticsConfig()
        if self.alerts is None:
            self.alerts = AlertConfig()
        if self.security is None:
            self.security = SecurityConfig()

class ConfigManager:
    """Gestor de configuración del sistema"""
    
    def __init__(self, config_file: str = "config.json", environment: Environment = None):
        self.config_file = config_file
        self.environment = environment or Environment.DEVELOPMENT
        self.config = None
        self.encryption_key = None
        
    def load_config(self) -> SystemConfig:
        """Cargar configuración desde archivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convertir a objeto de configuración
                self.config = self._dict_to_config(data)
                logger.info(f"Configuración cargada desde {self.config_file}")
            else:
                logger.info("Archivo de configuración no encontrado, usando configuración por defecto")
                self.config = SystemConfig()
                self.save_config()
            
            # Generar claves de encriptación si no existen
            if not self.config.security.encryption_key:
                self._generate_encryption_key()
            
            return self.config
            
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            logger.info("Usando configuración por defecto")
            self.config = SystemConfig()
            return self.config
    
    def save_config(self):
        """Guardar configuración a archivo"""
        try:
            data = self._config_to_dict(self.config)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuración guardada en {self.config_file}")
            
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
    
    def _dict_to_config(self, data: Dict[str, Any]) -> SystemConfig:
        """Convertir diccionario a objeto de configuración"""
        config = SystemConfig()
        
        # Configuración principal
        if 'environment' in data:
            config.environment = Environment(data['environment'])
        if 'debug' in data:
            config.debug = data['debug']
        if 'log_level' in data:
            config.log_level = data['log_level']
        if 'timezone' in data:
            config.timezone = data['timezone']
        
        # Sub-configuraciones
        if 'database' in data:
            config.database = DatabaseConfig(**data['database'])
        
        if 'notifications' in data:
            config.notifications = NotificationConfig(**data['notifications'])
        
        if 'api' in data:
            config.api = APIConfig(**data['api'])
        
        if 'analytics' in data:
            config.analytics = AnalyticsConfig(**data['analytics'])
        
        if 'alerts' in data:
            config.alerts = AlertConfig(**data['alerts'])
        
        if 'security' in data:
            config.security = SecurityConfig(**data['security'])
        
        return config
    
    def _config_to_dict(self, config: SystemConfig) -> Dict[str, Any]:
        """Convertir objeto de configuración a diccionario"""
        data = {
            'environment': config.environment.value,
            'debug': config.debug,
            'log_level': config.log_level,
            'timezone': config.timezone,
            'database': asdict(config.database),
            'notifications': asdict(config.notifications),
            'api': asdict(config.api),
            'analytics': asdict(config.analytics),
            'alerts': asdict(config.alerts),
            'security': asdict(config.security)
        }
        
        return data
    
    def _generate_encryption_key(self):
        """Generar clave de encriptación"""
        try:
            key = Fernet.generate_key()
            self.config.security.encryption_key = key.decode()
            logger.info("Clave de encriptación generada")
        except Exception as e:
            logger.error(f"Error generando clave de encriptación: {e}")
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encriptar datos sensibles"""
        try:
            if not self.config.security.encryption_key:
                return data
            
            key = self.config.security.encryption_key.encode()
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
            
        except Exception as e:
            logger.error(f"Error encriptando datos: {e}")
            return data
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Desencriptar datos sensibles"""
        try:
            if not self.config.security.encryption_key:
                return encrypted_data
            
            key = self.config.security.encryption_key.encode()
            fernet = Fernet(key)
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = fernet.decrypt(decoded_data)
            return decrypted_data.decode()
            
        except Exception as e:
            logger.error(f"Error desencriptando datos: {e}")
            return encrypted_data
    
    def validate_config(self) -> bool:
        """Validar configuración"""
        try:
            # Validar configuración de base de datos
            if not self.config.database.path:
                logger.error("Ruta de base de datos no especificada")
                return False
            
            # Validar configuración de notificaciones
            if self.config.notifications.email_enabled:
                if not self.config.notifications.smtp_server:
                    logger.error("Servidor SMTP no especificado")
                    return False
                if not self.config.notifications.email_recipients:
                    logger.error("Destinatarios de email no especificados")
                    return False
            
            # Validar configuración de API
            if not self.config.api.jwt_secret_key:
                logger.warning("Clave JWT no especificada, se generará automáticamente")
                self.config.api.jwt_secret_key = base64.b64encode(os.urandom(32)).decode()
            
            # Validar configuración de seguridad
            if not self.config.security.encryption_key:
                logger.warning("Clave de encriptación no especificada, se generará automáticamente")
                self._generate_encryption_key()
            
            logger.info("Configuración validada correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error validando configuración: {e}")
            return False
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Obtener configuración específica del entorno"""
        env_configs = {
            Environment.DEVELOPMENT: {
                'debug': True,
                'log_level': 'DEBUG',
                'database': {'path': 'inventory_dev.db'},
                'api': {'rate_limit': 1000}
            },
            Environment.STAGING: {
                'debug': False,
                'log_level': 'INFO',
                'database': {'path': 'inventory_staging.db'},
                'api': {'rate_limit': 500}
            },
            Environment.PRODUCTION: {
                'debug': False,
                'log_level': 'WARNING',
                'database': {'path': 'inventory_prod.db'},
                'api': {'rate_limit': 100}
            },
            Environment.TESTING: {
                'debug': True,
                'log_level': 'DEBUG',
                'database': {'path': 'inventory_test.db'},
                'api': {'rate_limit': 10000}
            }
        }
        
        return env_configs.get(self.environment, {})
    
    def apply_environment_config(self):
        """Aplicar configuración específica del entorno"""
        env_config = self.get_environment_config()
        
        for key, value in env_config.items():
            if hasattr(self.config, key):
                if isinstance(value, dict) and hasattr(self.config, key):
                    sub_config = getattr(self.config, key)
                    for sub_key, sub_value in value.items():
                        if hasattr(sub_config, sub_key):
                            setattr(sub_config, sub_key, sub_value)
                else:
                    setattr(self.config, key, value)
        
        logger.info(f"Configuración del entorno {self.environment.value} aplicada")
    
    def create_sample_config(self):
        """Crear archivo de configuración de ejemplo"""
        sample_config = {
            "environment": "development",
            "debug": True,
            "log_level": "INFO",
            "timezone": "UTC",
            "database": {
                "path": "inventory.db",
                "backup_interval": 24,
                "max_backups": 7,
                "connection_pool_size": 10,
                "timeout": 30,
                "enable_wal_mode": True,
                "enable_foreign_keys": True
            },
            "notifications": {
                "email_enabled": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_username": "your-email@gmail.com",
                "smtp_password": "your-app-password",
                "email_recipients": ["admin@company.com"],
                "webhook_enabled": False,
                "webhook_url": "",
                "sms_enabled": False
            },
            "api": {
                "rate_limit": 100,
                "api_key_required": True,
                "cors_enabled": True,
                "jwt_secret_key": "",
                "jwt_expiration_hours": 24,
                "max_request_size": 16777216
            },
            "analytics": {
                "prediction_horizon": 30,
                "confidence_threshold": 0.8,
                "seasonal_analysis": True,
                "ml_model_retrain_interval": 7,
                "enable_real_time_metrics": True,
                "metrics_retention_days": 90
            },
            "alerts": {
                "check_interval": 300,
                "escalation_enabled": True,
                "auto_resolve": False,
                "max_alerts_per_product": 10,
                "alert_cooldown_minutes": 30
            },
            "security": {
                "encryption_key": "",
                "enable_audit_log": True,
                "max_login_attempts": 5,
                "lockout_duration_minutes": 30,
                "password_min_length": 8,
                "require_2fa": False
            }
        }
        
        with open('config.example.json', 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2, ensure_ascii=False)
        
        logger.info("Archivo de configuración de ejemplo creado: config.example.json")

# Función de utilidad para obtener configuración global
_config_manager = None

def get_config() -> SystemConfig:
    """Obtener configuración global del sistema"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
        _config_manager.load_config()
        _config_manager.validate_config()
        _config_manager.apply_environment_config()
    return _config_manager.config

def reload_config():
    """Recargar configuración"""
    global _config_manager
    _config_manager = None
    return get_config()

if __name__ == "__main__":
    # Crear configuración de ejemplo
    config_manager = ConfigManager()
    config_manager.create_sample_config()
    
    # Cargar y mostrar configuración
    config = config_manager.load_config()
    print("Configuración cargada:")
    print(f"Entorno: {config.environment.value}")
    print(f"Debug: {config.debug}")
    print(f"Nivel de log: {config.log_level}")
    print(f"Base de datos: {config.database.path}")
    print(f"Email habilitado: {config.notifications.email_enabled}")
    print(f"Rate limit API: {config.api.rate_limit}")
    
    # Validar configuración
    if config_manager.validate_config():
        print("✅ Configuración válida")
    else:
        print("❌ Configuración inválida")



