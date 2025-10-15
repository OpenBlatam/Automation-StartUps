"""
Dynamic Configuration Management System for Ultimate Launch Planning System
Provides hot-reloading configuration, environment-specific settings, and validation
"""

import json
import yaml
import os
import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)

class ConfigSource(Enum):
    FILE = "file"
    ENVIRONMENT = "environment"
    DATABASE = "database"
    API = "api"
    DEFAULT = "default"

@dataclass
class ConfigItem:
    key: str
    value: Any
    source: ConfigSource
    timestamp: datetime
    description: str = ""
    validation_rules: Dict[str, Any] = None
    sensitive: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value if not self.sensitive else "***REDACTED***",
            "source": self.source.value,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "validation_rules": self.validation_rules,
            "sensitive": self.sensitive
        }

class ConfigValidator:
    """Configuration validation system"""
    
    @staticmethod
    def validate_string(value: Any, min_length: int = 0, max_length: int = None, 
                       pattern: str = None) -> bool:
        """Validate string value"""
        if not isinstance(value, str):
            return False
        if len(value) < min_length:
            return False
        if max_length and len(value) > max_length:
            return False
        if pattern:
            import re
            if not re.match(pattern, value):
                return False
        return True
    
    @staticmethod
    def validate_number(value: Any, min_val: float = None, max_val: float = None, 
                       integer_only: bool = False) -> bool:
        """Validate numeric value"""
        try:
            if integer_only:
                num = int(value)
            else:
                num = float(value)
            
            if min_val is not None and num < min_val:
                return False
            if max_val is not None and num > max_val:
                return False
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_boolean(value: Any) -> bool:
        """Validate boolean value"""
        return isinstance(value, bool)
    
    @staticmethod
    def validate_list(value: Any, min_items: int = 0, max_items: int = None, 
                     item_type: type = None) -> bool:
        """Validate list value"""
        if not isinstance(value, list):
            return False
        if len(value) < min_items:
            return False
        if max_items and len(value) > max_items:
            return False
        if item_type:
            if not all(isinstance(item, item_type) for item in value):
                return False
        return True
    
    @staticmethod
    def validate_dict(value: Any, required_keys: List[str] = None, 
                     allowed_keys: List[str] = None) -> bool:
        """Validate dictionary value"""
        if not isinstance(value, dict):
            return False
        if required_keys:
            if not all(key in value for key in required_keys):
                return False
        if allowed_keys:
            if not all(key in allowed_keys for key in value.keys()):
                return False
        return True

class ConfigManager:
    """Main configuration management system"""
    
    def __init__(self, config_dir: str = "config", auto_reload: bool = True):
        self.config_dir = Path(config_dir)
        self.auto_reload = auto_reload
        self.configs: Dict[str, ConfigItem] = {}
        self.config_files: Dict[str, str] = {}
        self.watchers: List[Callable] = []
        self.lock = threading.RLock()
        self.last_reload = datetime.now()
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        
        # Load default configurations
        self._load_default_configs()
        
        # Start file watcher if auto_reload is enabled
        if self.auto_reload:
            self._start_file_watcher()
    
    def _load_default_configs(self):
        """Load default configuration values"""
        default_configs = {
            # System settings
            "system.log_level": "INFO",
            "system.debug": False,
            "system.timezone": "UTC",
            "system.max_workers": 4,
            
            # API settings
            "api.host": "0.0.0.0",
            "api.port": 8000,
            "api.workers": 1,
            "api.timeout": 30,
            "api.cors_origins": ["*"],
            
            # Database settings
            "database.url": "sqlite:///launch_planning.db",
            "database.pool_size": 10,
            "database.max_overflow": 20,
            "database.echo": False,
            
            # Launch planning settings
            "launch.default_phases": ["pre_launch", "launch", "post_launch"],
            "launch.max_tasks_per_phase": 50,
            "launch.default_budget": 100000.0,
            "launch.success_threshold": 0.8,
            
            # AI/ML settings
            "ai.models_enabled": ["success_predictor", "trend_analyzer", "competitor_analyzer"],
            "ai.prediction_confidence_threshold": 0.7,
            "ai.model_retrain_interval_hours": 24,
            
            # Monitoring settings
            "monitoring.metrics_retention_hours": 24,
            "monitoring.alert_cooldown_minutes": 5,
            "monitoring.health_check_interval_seconds": 30,
            
            # Notification settings
            "notifications.email_enabled": False,
            "notifications.slack_enabled": False,
            "notifications.webhook_enabled": False,
            
            # Security settings
            "security.secret_key": "your-secret-key-here",
            "security.token_expiry_hours": 24,
            "security.rate_limit_per_minute": 100,
            
            # Performance settings
            "performance.cache_ttl_seconds": 300,
            "performance.max_memory_usage_mb": 1024,
            "performance.gc_threshold": 0.8
        }
        
        for key, value in default_configs.items():
            self.set_config(key, value, ConfigSource.DEFAULT, 
                          f"Default configuration for {key}")
    
    def set_config(self, key: str, value: Any, source: ConfigSource = ConfigSource.DEFAULT,
                   description: str = "", validation_rules: Dict[str, Any] = None,
                   sensitive: bool = False) -> bool:
        """Set a configuration value"""
        with self.lock:
            # Validate the value if rules are provided
            if validation_rules and not self._validate_value(value, validation_rules):
                logger.error(f"Validation failed for config key: {key}")
                return False
            
            config_item = ConfigItem(
                key=key,
                value=value,
                source=source,
                timestamp=datetime.now(),
                description=description,
                validation_rules=validation_rules,
                sensitive=sensitive
            )
            
            self.configs[key] = config_item
            logger.debug(f"Set config {key} = {value if not sensitive else '***REDACTED***'}")
            return True
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        with self.lock:
            if key in self.configs:
                return self.configs[key].value
            return default
    
    def get_config_item(self, key: str) -> Optional[ConfigItem]:
        """Get a configuration item with metadata"""
        with self.lock:
            return self.configs.get(key)
    
    def get_all_configs(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Get all configuration values"""
        with self.lock:
            result = {}
            for key, item in self.configs.items():
                if not item.sensitive or include_sensitive:
                    result[key] = item.value
                else:
                    result[key] = "***REDACTED***"
            return result
    
    def get_configs_by_source(self, source: ConfigSource) -> Dict[str, Any]:
        """Get configurations by source"""
        with self.lock:
            result = {}
            for key, item in self.configs.items():
                if item.source == source:
                    result[key] = item.value
            return result
    
    def delete_config(self, key: str) -> bool:
        """Delete a configuration"""
        with self.lock:
            if key in self.configs:
                del self.configs[key]
                logger.info(f"Deleted config: {key}")
                return True
            return False
    
    def load_from_file(self, file_path: str, source: ConfigSource = ConfigSource.FILE) -> bool:
        """Load configuration from file"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"Config file not found: {file_path}")
                return False
            
            with open(file_path, 'r') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                elif file_path.suffix.lower() == '.json':
                    data = json.load(f)
                else:
                    logger.error(f"Unsupported config file format: {file_path.suffix}")
                    return False
            
            # Store file path for watching
            self.config_files[str(file_path)] = str(file_path)
            
            # Load configurations
            self._load_config_data(data, source, str(file_path))
            
            logger.info(f"Loaded config from file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading config file {file_path}: {e}")
            return False
    
    def save_to_file(self, file_path: str, format: str = "yaml") -> bool:
        """Save current configuration to file"""
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data for saving
            data = {}
            for key, item in self.configs.items():
                if not item.sensitive:
                    data[key] = item.value
            
            with open(file_path, 'w') as f:
                if format.lower() == 'yaml':
                    yaml.dump(data, f, default_flow_style=False, indent=2)
                elif format.lower() == 'json':
                    json.dump(data, f, indent=2)
                else:
                    logger.error(f"Unsupported save format: {format}")
                    return False
            
            logger.info(f"Saved config to file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving config file {file_path}: {e}")
            return False
    
    def load_from_environment(self, prefix: str = "LAUNCH_") -> int:
        """Load configuration from environment variables"""
        loaded_count = 0
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower().replace('_', '.')
                
                # Try to convert to appropriate type
                converted_value = self._convert_env_value(value)
                
                self.set_config(config_key, converted_value, ConfigSource.ENVIRONMENT,
                              f"Environment variable {key}")
                loaded_count += 1
        
        logger.info(f"Loaded {loaded_count} configs from environment variables")
        return loaded_count
    
    def add_watcher(self, callback: Callable[[str, Any, Any], None]):
        """Add a configuration change watcher"""
        with self.lock:
            self.watchers.append(callback)
    
    def remove_watcher(self, callback: Callable[[str, Any, Any], None]):
        """Remove a configuration change watcher"""
        with self.lock:
            if callback in self.watchers:
                self.watchers.remove(callback)
    
    def _load_config_data(self, data: Dict[str, Any], source: ConfigSource, file_path: str):
        """Load configuration data from dictionary"""
        def _flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.'):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(_flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)
        
        flattened_data = _flatten_dict(data)
        
        for key, value in flattened_data.items():
            self.set_config(key, value, source, f"Loaded from {file_path}")
    
    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type"""
        # Boolean values
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        
        # Numeric values
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # List values (comma-separated)
        if ',' in value:
            return [item.strip() for item in value.split(',')]
        
        # JSON values
        if value.startswith('{') or value.startswith('['):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        
        # Default to string
        return value
    
    def _validate_value(self, value: Any, rules: Dict[str, Any]) -> bool:
        """Validate a value against rules"""
        validator = ConfigValidator()
        
        for rule_type, rule_value in rules.items():
            if rule_type == "type":
                if rule_value == "string" and not validator.validate_string(value):
                    return False
                elif rule_value == "number" and not validator.validate_number(value):
                    return False
                elif rule_value == "boolean" and not validator.validate_boolean(value):
                    return False
                elif rule_value == "list" and not validator.validate_list(value):
                    return False
                elif rule_value == "dict" and not validator.validate_dict(value):
                    return False
            
            elif rule_type == "min_length" and not validator.validate_string(value, min_length=rule_value):
                return False
            elif rule_type == "max_length" and not validator.validate_string(value, max_length=rule_value):
                return False
            elif rule_type == "min_value" and not validator.validate_number(value, min_val=rule_value):
                return False
            elif rule_type == "max_value" and not validator.validate_number(value, max_val=rule_value):
                return False
            elif rule_type == "required_keys" and not validator.validate_dict(value, required_keys=rule_value):
                return False
            elif rule_type == "allowed_keys" and not validator.validate_dict(value, allowed_keys=rule_value):
                return False
        
        return True
    
    def _start_file_watcher(self):
        """Start file watching for auto-reload"""
        def watch_files():
            while True:
                try:
                    for file_path in self.config_files.values():
                        if os.path.exists(file_path):
                            # Simple file modification check
                            mtime = os.path.getmtime(file_path)
                            if mtime > self.last_reload.timestamp():
                                logger.info(f"Config file changed: {file_path}")
                                self.load_from_file(file_path)
                                self.last_reload = datetime.now()
                    
                    time.sleep(5)  # Check every 5 seconds
                    
                except Exception as e:
                    logger.error(f"Error in file watcher: {e}")
                    time.sleep(30)  # Wait longer on error
        
        watcher_thread = threading.Thread(target=watch_files, daemon=True)
        watcher_thread.start()
    
    def _notify_watchers(self, key: str, old_value: Any, new_value: Any):
        """Notify watchers of configuration changes"""
        for callback in self.watchers:
            try:
                callback(key, old_value, new_value)
            except Exception as e:
                logger.error(f"Error in config watcher: {e}")

class LaunchConfigManager:
    """Specialized configuration manager for launch planning"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self._setup_launch_configs()
    
    def _setup_launch_configs(self):
        """Setup launch-specific configurations with validation"""
        launch_configs = {
            "launch.phases.pre_launch.duration_days": {
                "value": 30,
                "description": "Pre-launch phase duration in days",
                "validation": {"type": "number", "min_value": 1, "max_value": 365}
            },
            "launch.phases.launch.duration_days": {
                "value": 7,
                "description": "Launch phase duration in days",
                "validation": {"type": "number", "min_value": 1, "max_value": 30}
            },
            "launch.phases.post_launch.duration_days": {
                "value": 90,
                "description": "Post-launch phase duration in days",
                "validation": {"type": "number", "min_value": 1, "max_value": 365}
            },
            "launch.budget.allocation.marketing": {
                "value": 0.4,
                "description": "Marketing budget allocation percentage",
                "validation": {"type": "number", "min_value": 0.0, "max_value": 1.0}
            },
            "launch.budget.allocation.development": {
                "value": 0.3,
                "description": "Development budget allocation percentage",
                "validation": {"type": "number", "min_value": 0.0, "max_value": 1.0}
            },
            "launch.budget.allocation.operations": {
                "value": 0.2,
                "description": "Operations budget allocation percentage",
                "validation": {"type": "number", "min_value": 0.0, "max_value": 1.0}
            },
            "launch.budget.allocation.contingency": {
                "value": 0.1,
                "description": "Contingency budget allocation percentage",
                "validation": {"type": "number", "min_value": 0.0, "max_value": 1.0}
            },
            "launch.success_criteria.min_user_engagement": {
                "value": 0.7,
                "description": "Minimum user engagement score for success",
                "validation": {"type": "number", "min_value": 0.0, "max_value": 1.0}
            },
            "launch.success_criteria.min_revenue_target": {
                "value": 10000.0,
                "description": "Minimum revenue target for success",
                "validation": {"type": "number", "min_value": 0.0}
            },
            "launch.success_criteria.min_market_penetration": {
                "value": 0.05,
                "description": "Minimum market penetration percentage",
                "validation": {"type": "number", "min_value": 0.0, "max_value": 1.0}
            }
        }
        
        for key, config_data in launch_configs.items():
            self.config_manager.set_config(
                key=key,
                value=config_data["value"],
                source=ConfigSource.DEFAULT,
                description=config_data["description"],
                validation_rules=config_data["validation"]
            )
    
    def get_phase_duration(self, phase: str) -> int:
        """Get duration for a launch phase"""
        return self.config_manager.get_config(f"launch.phases.{phase}.duration_days", 30)
    
    def get_budget_allocation(self, category: str) -> float:
        """Get budget allocation for a category"""
        return self.config_manager.get_config(f"launch.budget.allocation.{category}", 0.0)
    
    def get_success_criteria(self, criterion: str) -> float:
        """Get success criteria threshold"""
        return self.config_manager.get_config(f"launch.success_criteria.{criterion}", 0.0)
    
    def update_phase_duration(self, phase: str, duration_days: int) -> bool:
        """Update phase duration"""
        return self.config_manager.set_config(
            f"launch.phases.{phase}.duration_days",
            duration_days,
            ConfigSource.API,
            f"Updated {phase} phase duration"
        )
    
    def update_budget_allocation(self, category: str, percentage: float) -> bool:
        """Update budget allocation"""
        return self.config_manager.set_config(
            f"launch.budget.allocation.{category}",
            percentage,
            ConfigSource.API,
            f"Updated {category} budget allocation"
        )

# Global config manager instance
_config_manager = None

def get_config_manager() -> ConfigManager:
    """Get global config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_launch_config_manager() -> LaunchConfigManager:
    """Get global launch config manager instance"""
    return LaunchConfigManager(get_config_manager())

# Example usage
if __name__ == "__main__":
    # Initialize config manager
    config_manager = get_config_manager()
    launch_config = get_launch_config_manager()
    
    # Load from environment
    config_manager.load_from_environment("LAUNCH_")
    
    # Load from file
    config_manager.load_from_file("config/app.yaml")
    
    # Add a watcher
    def config_changed(key, old_value, new_value):
        print(f"Config changed: {key} = {old_value} -> {new_value}")
    
    config_manager.add_watcher(config_changed)
    
    # Test configuration access
    print("API Port:", config_manager.get_config("api.port"))
    print("Pre-launch Duration:", launch_config.get_phase_duration("pre_launch"))
    print("Marketing Budget:", launch_config.get_budget_allocation("marketing"))
    
    # Update configuration
    config_manager.set_config("api.port", 8080, ConfigSource.API, "Updated API port")
    
    # Save configuration
    config_manager.save_to_file("config/current.yaml")
    
    print("All configs:")
    print(json.dumps(config_manager.get_all_configs(), indent=2))







