"""
Configuración centralizada para ads reporting.

Proporciona:
- Carga de configuración desde variables de entorno
- Validación de configuración
- Valores por defecto
- Configuración por ambiente
"""

from __future__ import annotations

import os
import logging
from typing import Any, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AdsReportingConfig:
    """Configuración general de ads reporting."""
    # Configuración de caché
    cache_enabled: bool = True
    cache_maxsize: int = 100
    cache_ttl: int = 300  # 5 minutos
    
    # Configuración de almacenamiento
    default_storage: str = "postgres"
    postgres_conn_id: str = "postgres_default"
    
    # Configuración de retry
    default_max_retries: int = 3
    default_retry_backoff: float = 1.0
    default_rate_limit_delay: float = 0.5
    default_request_timeout: int = 30
    
    # Configuración de validación
    enable_validation: bool = True
    strict_validation: bool = False
    
    # Configuración de data quality
    enable_dq_checks: bool = True
    min_impressions_threshold: int = 0
    
    # Configuración de logging
    log_level: str = "INFO"
    
    # Ambiente
    environment: str = "production"
    
    @classmethod
    def from_env(cls) -> AdsReportingConfig:
        """Carga configuración desde variables de entorno."""
        return cls(
            cache_enabled=os.environ.get("ADS_CACHE_ENABLED", "true").lower() == "true",
            cache_maxsize=int(os.environ.get("ADS_CACHE_MAXSIZE", "100")),
            cache_ttl=int(os.environ.get("ADS_CACHE_TTL", "300")),
            default_storage=os.environ.get("ADS_DEFAULT_STORAGE", "postgres"),
            postgres_conn_id=os.environ.get("POSTGRES_CONN_ID", "postgres_default"),
            default_max_retries=int(os.environ.get("ADS_DEFAULT_MAX_RETRIES", "3")),
            default_retry_backoff=float(os.environ.get("ADS_DEFAULT_RETRY_BACKOFF", "1.0")),
            default_rate_limit_delay=float(os.environ.get("ADS_DEFAULT_RATE_LIMIT_DELAY", "0.5")),
            default_request_timeout=int(os.environ.get("ADS_DEFAULT_REQUEST_TIMEOUT", "30")),
            enable_validation=os.environ.get("ADS_ENABLE_VALIDATION", "true").lower() == "true",
            strict_validation=os.environ.get("ADS_STRICT_VALIDATION", "false").lower() == "true",
            enable_dq_checks=os.environ.get("ADS_ENABLE_DQ_CHECKS", "true").lower() == "true",
            min_impressions_threshold=int(os.environ.get("ADS_MIN_IMPRESSIONS_THRESHOLD", "0")),
            log_level=os.environ.get("ADS_LOG_LEVEL", "INFO"),
            environment=os.environ.get("ENVIRONMENT", "production")
        )


# Instancia global de configuración
_global_config: Optional[AdsReportingConfig] = None


def get_config() -> AdsReportingConfig:
    """Obtiene o crea la configuración global."""
    global _global_config
    if _global_config is None:
        _global_config = AdsReportingConfig.from_env()
    return _global_config


def set_config(config: AdsReportingConfig) -> None:
    """Establece la configuración global."""
    global _global_config
    _global_config = config

