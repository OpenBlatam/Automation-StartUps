"""
Configuración robusta para clientes de API.

Características:
- Dataclasses para configuración tipada
- Carga desde variables de entorno
- Validación de configuración
- Valores por defecto sensatos
- Helpers para cargar config
"""
import os
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Entornos disponibles."""
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    TEST = "test"


@dataclass
class APIConfig:
    """Configuración base para clientes de API."""
    
    base_url: str = ""
    max_retries: int = 3
    timeout: int = 30
    retry_backoff_factor: float = 1.0
    rate_limit_max_wait: int = 300  # 5 minutos
    environment: Environment = Environment.PRODUCTION
    
    # Circuit Breaker
    circuit_breaker_enabled: bool = True
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_timeout_seconds: int = 60
    
    # Cache
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutos
    cache_max_size: int = 100
    
    # Metrics
    metrics_enabled: bool = True
    
    def validate(self) -> Optional[str]:
        """
        Valida la configuración.
        
        Returns:
            Mensaje de error si hay problemas, None si es válida
        """
        if not self.base_url:
            return "base_url is required"
        
        if self.max_retries < 0:
            return "max_retries must be >= 0"
        
        if self.timeout <= 0:
            return "timeout must be > 0"
        
        if self.circuit_breaker_failure_threshold < 1:
            return "circuit_breaker_failure_threshold must be >= 1"
        
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la configuración a diccionario."""
        return {
            "base_url": self.base_url,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "retry_backoff_factor": self.retry_backoff_factor,
            "rate_limit_max_wait": self.rate_limit_max_wait,
            "environment": self.environment.value,
            "circuit_breaker_enabled": self.circuit_breaker_enabled,
            "circuit_breaker_failure_threshold": self.circuit_breaker_failure_threshold,
            "circuit_breaker_timeout_seconds": self.circuit_breaker_timeout_seconds,
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "cache_max_size": self.cache_max_size,
            "metrics_enabled": self.metrics_enabled
        }


@dataclass
class HubSpotConfig(APIConfig):
    """Configuración para HubSpot API."""
    
    api_token: str = ""
    base_url: str = "https://api.hubapi.com"
    
    @classmethod
    def from_env(cls, env_prefix: str = "HUBSPOT_") -> "HubSpotConfig":
        """
        Carga configuración desde variables de entorno.
        
        Args:
            env_prefix: Prefijo para variables de entorno
        
        Returns:
            HubSpotConfig cargada desde entorno
        """
        def get_env(key: str, default: Any = None, type_cast: type = str) -> Any:
            """Helper para obtener variables de entorno con type casting."""
            value = os.getenv(f"{env_prefix}{key}", default)
            if value is None:
                return default
            try:
                if type_cast == bool:
                    return str(value).lower() in ("true", "1", "yes", "on")
                elif type_cast == int:
                    return int(value)
                elif type_cast == float:
                    return float(value)
                elif type_cast == Environment:
                    return Environment(value.lower())
                return type_cast(value)
            except (ValueError, TypeError):
                logger.warning(f"Failed to cast {key}={value} to {type_cast}, using default")
                return default
        
        environment = get_env("ENVIRONMENT", "production", Environment)
        
        return cls(
            api_token=get_env("TOKEN", ""),
            base_url=get_env("BASE_URL", "https://api.hubapi.com"),
            max_retries=get_env("MAX_RETRIES", 3, int),
            timeout=get_env("TIMEOUT", 30, int),
            retry_backoff_factor=get_env("RETRY_BACKOFF_FACTOR", 1.0, float),
            rate_limit_max_wait=get_env("RATE_LIMIT_MAX_WAIT", 300, int),
            environment=environment,
            circuit_breaker_enabled=get_env("CIRCUIT_BREAKER_ENABLED", True, bool),
            circuit_breaker_failure_threshold=get_env("CIRCUIT_BREAKER_FAILURE_THRESHOLD", 5, int),
            circuit_breaker_timeout_seconds=get_env("CIRCUIT_BREAKER_TIMEOUT", 60, int),
            cache_enabled=get_env("CACHE_ENABLED", True, bool),
            cache_ttl=get_env("CACHE_TTL", 300, int),
            cache_max_size=get_env("CACHE_MAX_SIZE", 100, int),
            metrics_enabled=get_env("METRICS_ENABLED", True, bool)
        )
    
    def validate(self) -> Optional[str]:
        """Valida la configuración de HubSpot."""
        base_validation = super().validate()
        if base_validation:
            return base_validation
        
        if not self.api_token:
            return "api_token is required for HubSpot"
        
        return None


@dataclass
class ManyChatConfig(APIConfig):
    """Configuración para ManyChat API."""
    
    api_key: str = ""
    page_id: Optional[str] = None
    base_url: str = "https://api.manychat.com"
    
    @classmethod
    def from_env(cls, env_prefix: str = "MANYCHAT_") -> "ManyChatConfig":
        """
        Carga configuración desde variables de entorno.
        
        Args:
            env_prefix: Prefijo para variables de entorno
        
        Returns:
            ManyChatConfig cargada desde entorno
        """
        def get_env(key: str, default: Any = None, type_cast: type = str) -> Any:
            """Helper para obtener variables de entorno con type casting."""
            value = os.getenv(f"{env_prefix}{key}", default)
            if value is None:
                return default
            try:
                if type_cast == bool:
                    return str(value).lower() in ("true", "1", "yes", "on")
                elif type_cast == int:
                    return int(value)
                elif type_cast == float:
                    return float(value)
                elif type_cast == Environment:
                    return Environment(value.lower())
                return type_cast(value)
            except (ValueError, TypeError):
                logger.warning(f"Failed to cast {key}={value} to {type_cast}, using default")
                return default
        
        environment = get_env("ENVIRONMENT", "production", Environment)
        
        return cls(
            api_key=get_env("API_KEY", ""),
            page_id=get_env("PAGE_ID", None),
            base_url=get_env("BASE_URL", "https://api.manychat.com"),
            max_retries=get_env("MAX_RETRIES", 3, int),
            timeout=get_env("TIMEOUT", 30, int),
            retry_backoff_factor=get_env("RETRY_BACKOFF_FACTOR", 1.0, float),
            rate_limit_max_wait=get_env("RATE_LIMIT_MAX_WAIT", 300, int),
            environment=environment,
            circuit_breaker_enabled=get_env("CIRCUIT_BREAKER_ENABLED", True, bool),
            circuit_breaker_failure_threshold=get_env("CIRCUIT_BREAKER_FAILURE_THRESHOLD", 5, int),
            circuit_breaker_timeout_seconds=get_env("CIRCUIT_BREAKER_TIMEOUT", 60, int),
            metrics_enabled=get_env("METRICS_ENABLED", True, bool)
        )
    
    def validate(self) -> Optional[str]:
        """Valida la configuración de ManyChat."""
        base_validation = super().validate()
        if base_validation:
            return base_validation
        
        if not self.api_key:
            return "api_key is required for ManyChat"
        
        return None


def load_config_from_env(
    api_name: str,
    env_prefix: Optional[str] = None
) -> APIConfig:
    """
    Carga configuración desde variables de entorno por nombre de API.
    
    Args:
        api_name: Nombre de la API ("hubspot" o "manychat")
        env_prefix: Prefijo opcional (usa default si None)
    
    Returns:
        Configuración cargada
    
    Raises:
        ValueError: Si el nombre de API no es reconocido
    """
    api_name = api_name.lower()
    
    if api_name == "hubspot":
        prefix = env_prefix or "HUBSPOT_"
        return HubSpotConfig.from_env(prefix)
    elif api_name == "manychat":
        prefix = env_prefix or "MANYCHAT_"
        return ManyChatConfig.from_env(prefix)
    else:
        raise ValueError(f"Unknown API name: {api_name}. Supported: hubspot, manychat")


def validate_config(config: APIConfig) -> bool:
    """
    Valida una configuración y lanza excepción si es inválida.
    
    Args:
        config: Configuración a validar
    
    Returns:
        True si es válida
    
    Raises:
        ValueError: Si la configuración es inválida
    """
    error = config.validate()
    if error:
        raise ValueError(f"Invalid configuration: {error}")
    return True
