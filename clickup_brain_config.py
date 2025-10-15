#!/usr/bin/env python3
"""
ClickUp Brain Configuration System
=================================

Centralized configuration management with YAML/JSON support,
environment variable overrides, and validation.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, field
import logging

ROOT = Path(__file__).parent

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str = "localhost"
    port: int = 5432
    name: str = "clickup_brain"
    user: str = "postgres"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False

@dataclass
class APIConfig:
    """API configuration settings."""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    timeout: int = 30
    cors_origins: list[str] = field(default_factory=lambda: ["*"])
    rate_limit: int = 1000
    api_key_required: bool = False

@dataclass
class SecurityConfig:
    """Security configuration settings."""
    secret_key: str = ""
    jwt_expiry: int = 3600
    encryption_key: str = ""
    mfa_required: bool = False
    session_timeout: int = 1800
    max_login_attempts: int = 5
    lockout_duration: int = 900

@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/clickup_brain.log"
    max_size: int = 10485760  # 10MB
    backup_count: int = 5
    console_output: bool = True

@dataclass
class MLConfig:
    """Machine Learning configuration settings."""
    model_path: str = "models/"
    batch_size: int = 32
    learning_rate: float = 0.001
    epochs: int = 100
    validation_split: float = 0.2
    early_stopping_patience: int = 10
    gpu_enabled: bool = False

@dataclass
class IntegrationConfig:
    """External integration configuration."""
    clickup_api_key: str = ""
    slack_token: str = ""
    github_token: str = ""
    google_credentials: str = ""
    webhook_secret: str = ""
    sync_interval: int = 300

@dataclass
class SystemConfig:
    """Main system configuration."""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    api: APIConfig = field(default_factory=APIConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    ml: MLConfig = field(default_factory=MLConfig)
    integration: IntegrationConfig = field(default_factory=IntegrationConfig)
    
    # System-wide settings
    debug: bool = False
    environment: str = "development"
    timezone: str = "UTC"
    max_memory_usage: float = 0.8
    cleanup_interval: int = 3600

class ConfigManager:
    """Configuration manager with validation and environment overrides."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or ROOT / "config.yaml"
        self.config: Optional[SystemConfig] = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file and environment variables."""
        config_data = self._load_from_file()
        config_data = self._apply_env_overrides(config_data)
        self.config = self._create_config_object(config_data)
        self._validate_config()
    
    def _load_from_file(self) -> Dict[str, Any]:
        """Load configuration from YAML or JSON file."""
        if not self.config_path.exists():
            return {}
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_path.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    return yaml.safe_load(f) or {}
        except Exception as e:
            logging.warning(f"Failed to load config file {self.config_path}: {e}")
            return {}
    
    def _apply_env_overrides(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration."""
        env_mappings = {
            'CLICKUP_BRAIN_DEBUG': ('debug', bool),
            'CLICKUP_BRAIN_ENVIRONMENT': ('environment', str),
            'CLICKUP_BRAIN_DB_HOST': ('database.host', str),
            'CLICKUP_BRAIN_DB_PORT': ('database.port', int),
            'CLICKUP_BRAIN_DB_NAME': ('database.name', str),
            'CLICKUP_BRAIN_DB_USER': ('database.user', str),
            'CLICKUP_BRAIN_DB_PASSWORD': ('database.password', str),
            'CLICKUP_BRAIN_API_HOST': ('api.host', str),
            'CLICKUP_BRAIN_API_PORT': ('api.port', int),
            'CLICKUP_BRAIN_SECRET_KEY': ('security.secret_key', str),
            'CLICKUP_BRAIN_CLICKUP_API_KEY': ('integration.clickup_api_key', str),
            'CLICKUP_BRAIN_SLACK_TOKEN': ('integration.slack_token', str),
        }
        
        for env_var, (config_path, type_func) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    typed_value = type_func(value)
                    self._set_nested_value(config_data, config_path, typed_value)
                except ValueError as e:
                    logging.warning(f"Invalid environment variable {env_var}: {e}")
        
        return config_data
    
    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """Set a nested dictionary value using dot notation."""
        keys = path.split('.')
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
    
    def _create_config_object(self, config_data: Dict[str, Any]) -> SystemConfig:
        """Create SystemConfig object from dictionary data."""
        # Create nested config objects
        database_config = DatabaseConfig(**config_data.get('database', {}))
        api_config = APIConfig(**config_data.get('api', {}))
        security_config = SecurityConfig(**config_data.get('security', {}))
        logging_config = LoggingConfig(**config_data.get('logging', {}))
        ml_config = MLConfig(**config_data.get('ml', {}))
        integration_config = IntegrationConfig(**config_data.get('integration', {}))
        
        # Create main config
        system_config = SystemConfig(
            database=database_config,
            api=api_config,
            security=security_config,
            logging=logging_config,
            ml=ml_config,
            integration=integration_config,
            debug=config_data.get('debug', False),
            environment=config_data.get('environment', 'development'),
            timezone=config_data.get('timezone', 'UTC'),
            max_memory_usage=config_data.get('max_memory_usage', 0.8),
            cleanup_interval=config_data.get('cleanup_interval', 3600)
        )
        
        return system_config
    
    def _validate_config(self) -> None:
        """Validate configuration values."""
        if not self.config:
            return
        
        # Validate required fields
        if not self.config.security.secret_key:
            logging.warning("No secret key configured - using default (not recommended for production)")
            self.config.security.secret_key = "default-secret-key-change-in-production"
        
        if not self.config.security.encryption_key:
            logging.warning("No encryption key configured - using default (not recommended for production)")
            self.config.security.encryption_key = "default-encryption-key-change-in-production"
        
        # Validate ranges
        if not 0 < self.config.api.port < 65536:
            raise ValueError(f"Invalid API port: {self.config.api.port}")
        
        if not 0 < self.config.database.port < 65536:
            raise ValueError(f"Invalid database port: {self.config.database.port}")
        
        if not 0 < self.config.ml.learning_rate < 1:
            raise ValueError(f"Invalid learning rate: {self.config.ml.learning_rate}")
    
    def get_config(self) -> SystemConfig:
        """Get the current configuration."""
        if not self.config:
            self._load_config()
        return self.config
    
    def reload_config(self) -> None:
        """Reload configuration from file."""
        self._load_config()
    
    def save_config(self, config: Optional[SystemConfig] = None) -> None:
        """Save configuration to file."""
        if config:
            self.config = config
        
        if not self.config:
            return
        
        # Convert to dictionary
        config_dict = {
            'debug': self.config.debug,
            'environment': self.config.environment,
            'timezone': self.config.timezone,
            'max_memory_usage': self.config.max_memory_usage,
            'cleanup_interval': self.config.cleanup_interval,
            'database': {
                'host': self.config.database.host,
                'port': self.config.database.port,
                'name': self.config.database.name,
                'user': self.config.database.user,
                'password': self.config.database.password,
                'pool_size': self.config.database.pool_size,
                'max_overflow': self.config.database.max_overflow,
                'echo': self.config.database.echo,
            },
            'api': {
                'host': self.config.api.host,
                'port': self.config.api.port,
                'workers': self.config.api.workers,
                'timeout': self.config.api.timeout,
                'cors_origins': self.config.api.cors_origins,
                'rate_limit': self.config.api.rate_limit,
                'api_key_required': self.config.api.api_key_required,
            },
            'security': {
                'secret_key': self.config.security.secret_key,
                'jwt_expiry': self.config.security.jwt_expiry,
                'encryption_key': self.config.security.encryption_key,
                'mfa_required': self.config.security.mfa_required,
                'session_timeout': self.config.security.session_timeout,
                'max_login_attempts': self.config.security.max_login_attempts,
                'lockout_duration': self.config.security.lockout_duration,
            },
            'logging': {
                'level': self.config.logging.level,
                'format': self.config.logging.format,
                'file_path': self.config.logging.file_path,
                'max_size': self.config.logging.max_size,
                'backup_count': self.config.logging.backup_count,
                'console_output': self.config.logging.console_output,
            },
            'ml': {
                'model_path': self.config.ml.model_path,
                'batch_size': self.config.ml.batch_size,
                'learning_rate': self.config.ml.learning_rate,
                'epochs': self.config.ml.epochs,
                'validation_split': self.config.ml.validation_split,
                'early_stopping_patience': self.config.ml.early_stopping_patience,
                'gpu_enabled': self.config.ml.gpu_enabled,
            },
            'integration': {
                'clickup_api_key': self.config.integration.clickup_api_key,
                'slack_token': self.config.integration.slack_token,
                'github_token': self.config.integration.github_token,
                'google_credentials': self.config.integration.google_credentials,
                'webhook_secret': self.config.integration.webhook_secret,
                'sync_interval': self.config.integration.sync_interval,
            }
        }
        
        # Save to file
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                if self.config_path.suffix.lower() == '.json':
                    json.dump(config_dict, f, indent=2)
                else:
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            logging.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logging.error(f"Failed to save configuration: {e}")
            raise

# Global configuration instance
config_manager = ConfigManager()

def get_config() -> SystemConfig:
    """Get the global configuration instance."""
    return config_manager.get_config()

def reload_config() -> None:
    """Reload the global configuration."""
    config_manager.reload_config()

def save_config(config: Optional[SystemConfig] = None) -> None:
    """Save the global configuration."""
    config_manager.save_config(config)

if __name__ == "__main__":
    # Demo configuration system
    print("ClickUp Brain Configuration System Demo")
    print("=" * 50)
    
    config = get_config()
    print(f"Environment: {config.environment}")
    print(f"Debug mode: {config.debug}")
    print(f"API host: {config.api.host}:{config.api.port}")
    print(f"Database: {config.database.host}:{config.database.port}/{config.database.name}")
    print(f"Logging level: {config.logging.level}")
    print(f"ML learning rate: {config.ml.learning_rate}")
    
    # Test environment variable override
    os.environ['CLICKUP_BRAIN_DEBUG'] = 'true'
    os.environ['CLICKUP_BRAIN_API_PORT'] = '9000'
    
    reload_config()
    config = get_config()
    print(f"\nAfter environment overrides:")
    print(f"Debug mode: {config.debug}")
    print(f"API port: {config.api.port}")







