"""
Bibliotecas mejoradas para workflows de Kestra.

Este módulo contiene clientes y utilidades mejoradas para:
- HubSpot API (con retry, rate limiting, validación, circuit breaker, cache, metrics)
- ManyChat API (con validación, manejo de errores, circuit breaker, metrics)
- Validación de webhooks (verificación de firma HMAC)
- Circuit Breaker pattern (protección contra cascading failures)
- Caché simple (reduce llamadas repetidas)
- Métricas Prometheus (observabilidad)
"""

__version__ = "2.3.0"

# Exportar clases principales
from .hubspot_client import HubSpotClient, HubSpotContact, HubSpotResult
from .manychat_client import ManyChatClient, ManyChatMessage, ManyChatResult
from .webhook_validator import WebhookValidator
from .circuit_breaker import CircuitBreaker, CircuitBreakerConfig, get_circuit_breaker
from .cache import SimpleCache, get_cache
from .metrics import MetricsCollector, Metric, get_metrics_collector, record_workflow_metric
from .health import HealthChecker, HealthCheckResult, HealthStatus, create_api_health_check
from .batch import BatchProcessor, BatchResult
from .config import (
    APIConfig,
    HubSpotConfig,
    ManyChatConfig,
    Environment,
    load_config_from_env,
    validate_config as validate_api_config
)
from .exceptions import (
    APIError,
    HubSpotError,
    HubSpotAPIError,
    HubSpotRateLimitError,
    HubSpotValidationError,
    HubSpotNotFoundError,
    ManyChatError,
    ManyChatAPIError,
    ManyChatRateLimitError,
    ManyChatValidationError,
    ConfigurationError,
    CircuitBreakerOpenError,
    TimeoutError,
    ErrorContext,
    enrich_error
)
from .middleware import (
    Middleware,
    MiddlewarePipeline,
    LoggingMiddleware,
    MetricsMiddleware,
    RetryMiddleware,
    HeaderMiddleware,
    Request,
    Response,
    create_default_pipeline
)
from .rate_limiter import (
    RateLimiter,
    TokenBucket,
    get_default_rate_limiter,
    set_default_rate_limiter
)

__all__ = [
    "HubSpotClient",
    "HubSpotContact",
    "HubSpotResult",
    "ManyChatClient",
    "ManyChatMessage",
    "ManyChatResult",
    "WebhookValidator",
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "get_circuit_breaker",
    "SimpleCache",
    "get_cache",
    "MetricsCollector",
    "Metric",
    "get_metrics_collector",
    "record_workflow_metric",
    "HealthChecker",
    "HealthCheckResult",
    "HealthStatus",
    "create_api_health_check",
    "BatchProcessor",
    "BatchResult",
    "APIConfig",
    "HubSpotConfig",
    "ManyChatConfig",
    "Environment",
    "load_config_from_env",
    "validate_api_config",
]

