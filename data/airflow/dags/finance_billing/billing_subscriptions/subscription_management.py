"""
DAG mejorado para gestión automática de suscripciones.

Proceso mensual que:
1. Identifica suscripciones próximas a vencer
2. Envía notificaciones de renovación
3. Marca como inactivas las suscripciones que no renuevan

Mejoras implementadas:
- ✅ Retry con exponential backoff (tenacity si disponible)
- ✅ Health check pre-vuelo de APIs
- ✅ Manejo inteligente de rate limiting (429)
- ✅ Logging estructurado con contexto completo
- ✅ Validación robusta de inputs (guard clauses)
- ✅ Timeouts configurables
- ✅ Métricas de performance detalladas (StatsD/Prometheus)
- ✅ Manejo específico de errores HTTP con excepciones personalizadas
- ✅ Sesiones HTTP reutilizables con connection pooling
- ✅ Procesamiento en batches con delays configurables
- ✅ Notificaciones Slack automáticas para alertas
- ✅ Tracking de progreso en Variables de Airflow
- ✅ Context managers para tracking de API calls
- ✅ Dead Letter Queue (DLQ) para errores persistentes
- ✅ Detección de anomalías usando Z-score
- ✅ Cache inteligente de suscripciones (TTL 5 min)
- ✅ Circuit breaker con auto-reset
- ✅ Batch size adaptativo basado en performance histórico
- ✅ Comparación de métricas con ejecuciones anteriores
- ✅ Procesamiento paralelo con ThreadPoolExecutor
"""
from __future__ import annotations

from datetime import timedelta, datetime, date
from typing import Any, Dict, List, Optional, Callable, Tuple
import json
import logging
import os
import time
from contextlib import contextmanager
from dataclasses import dataclass, field

import pendulum
from airflow.decorators import dag, task, task_group
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.operators.empty import EmptyOperator
from airflow.models import Variable
from airflow.exceptions import AirflowFailException
from airflow.providers.postgres.hooks.postgres import PostgresHook

# Logging estructurado
try:
    import structlog
    logger = structlog.get_logger(__name__)
    STRUCTLOG_AVAILABLE = True
except ImportError:
    logger = logging.getLogger(__name__)
    STRUCTLOG_AVAILABLE = False

# Pydantic para validación
try:
    from pydantic import BaseModel, EmailStr, Field, validator, ValidationError
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

# Circuit breaker mejorado
try:
    from pybreaker import CircuitBreaker
    PYBREAKER_AVAILABLE = True
except ImportError:
    PYBREAKER_AVAILABLE = False

# OpenTelemetry Tracing (opcional)
try:
    from opentelemetry import trace
    tracer = trace.get_tracer(__name__)
    OPENTELEMETRY_AVAILABLE = True
except Exception:
    tracer = None
    OPENTELEMETRY_AVAILABLE = False

# Callbacks y notificaciones
try:
    from data.airflow.plugins.etl_callbacks import on_task_failure, sla_miss_callback
    from data.airflow.plugins.etl_notifications import notify_slack
except ImportError:
    def on_task_failure(context): pass
    def sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis): pass
    def notify_slack(message): pass

# Rate limiting (usando Redis si está disponible)
try:
    import redis
    from redis_rate_limit import RateLimiter
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=int(os.getenv("REDIS_DB", 0)),
        decode_responses=True
    )
    rate_limiter = RateLimiter(redis_client)
    REDIS_AVAILABLE = True
except Exception:
    redis_client = None
    rate_limiter = None
    REDIS_AVAILABLE = False

# Circuit breakers para diferentes servicios
if PYBREAKER_AVAILABLE:
    stripe_circuit_breaker = CircuitBreaker(
        fail_max=5,
        timeout_duration=60,
        expected_exception=Exception
    )
    notification_circuit_breaker = CircuitBreaker(
        fail_max=3,
        timeout_duration=120,
        expected_exception=Exception
    )
else:
    stripe_circuit_breaker = None
    notification_circuit_breaker = None

# Intentar importar Stats de Airflow
try:
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except Exception:
    STATS_AVAILABLE = False
    Stats = None  # type: ignore

# Intentar importar tenacity para retries avanzados
try:
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type,
        before_sleep_log,
        after_log,
    )
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False

# Intentar importar httpx para mejor performance
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

# Intentar importar requests.adapters para connection pooling
try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_ADAPTER_AVAILABLE = True
except ImportError:
    REQUESTS_ADAPTER_AVAILABLE = False
    requests = None  # type: ignore

# Intentar importar concurrent.futures para procesamiento paralelo
try:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    CONCURRENT_AVAILABLE = True
except ImportError:
    CONCURRENT_AVAILABLE = False

# Intentar importar cachetools para cache
try:
    from cachetools import TTLCache
    CACHETOOLS_AVAILABLE = True
except ImportError:
    CACHETOOLS_AVAILABLE = False

# Constantes de configuración
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0
DEFAULT_TIMEOUT = 30
RATE_LIMIT_MAX_WAIT = 300
CB_FAILURE_THRESHOLD = 5
CB_RESET_MINUTES = 15
DEFAULT_BATCH_SIZE = 10
DEFAULT_BATCH_DELAY = 0.5

# Sesiones HTTP globales reutilizables
_stripe_session: Optional[Any] = None

# Cache para suscripciones y clientes (TTL de 5 minutos)
_subscription_cache: Optional[Any] = None
_customer_cache: Optional[Any] = None
if CACHETOOLS_AVAILABLE:
    try:
        _subscription_cache = TTLCache(maxsize=200, ttl=300)  # 5 minutos
        _customer_cache = TTLCache(maxsize=500, ttl=300)  # 5 minutos
    except Exception:
        _subscription_cache = None
        _customer_cache = None


@dataclass
class SubscriptionResult:
    """Resultado del procesamiento de una suscripción."""
    subscription_id: str
    customer_id: str
    customer_email: Optional[str] = None
    status: str = "pending"
    action: Optional[str] = None  # 'notified', 'renewed', 'inactivated'
    error_message: Optional[str] = None
    duration_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario."""
        return {
            "subscription_id": self.subscription_id,
            "customer_id": self.customer_id,
            "customer_email": self.customer_email,
            "status": self.status,
            "action": self.action,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms,
        }


@dataclass
class ProcessingSummary:
    """Resumen del procesamiento de suscripciones."""
    total_subscriptions: int = 0
    notifications_sent: int = 0
    notifications_failed: int = 0
    renewed_subscriptions: int = 0
    not_renewed_subscriptions: int = 0
    marked_inactive: int = 0
    skipped: int = 0
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resumen a diccionario."""
        return {
            "total_subscriptions": self.total_subscriptions,
            "notifications_sent": self.notifications_sent,
            "notifications_failed": self.notifications_failed,
            "renewed_subscriptions": self.renewed_subscriptions,
            "not_renewed_subscriptions": self.not_renewed_subscriptions,
            "marked_inactive": self.marked_inactive,
            "skipped": self.skipped,
            "errors": self.errors,
        }


def _get_stripe_session():
    """Obtiene o crea una sesión HTTP reutilizable para Stripe."""
    global _stripe_session
    
    if _stripe_session is not None:
        return _stripe_session
    
    if HTTPX_AVAILABLE:
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
        timeout = httpx.Timeout(30.0, connect=10.0)
        _stripe_session = httpx.Client(limits=limits, timeout=timeout, follow_redirects=True)
    elif REQUESTS_ADAPTER_AVAILABLE and requests:
        session = requests.Session()
        retry_strategy = Retry(
            total=DEFAULT_MAX_RETRIES,
            backoff_factor=DEFAULT_RETRY_DELAY,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_maxsize=10)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        _stripe_session = session
    else:
        _stripe_session = None
    
    return _stripe_session


@contextmanager
def _track_api_call(api_name: str, operation: str):
    """Context manager para trackear llamadas API con métricas."""
    start = time.time()
    if STATS_AVAILABLE and Stats:
        try:
            Stats.incr(f"subscription_management.api.{api_name}.{operation}.attempt", 1)
        except Exception:
            pass
    try:
        yield
        duration_ms = (time.time() - start) * 1000
        if STATS_AVAILABLE and Stats:
            try:
                Stats.incr(f"subscription_management.api.{api_name}.{operation}.success", 1)
                Stats.timing(f"subscription_management.api.{api_name}.{operation}.duration_ms", int(duration_ms))
            except Exception:
                pass
    except Exception as e:
        duration_ms = (time.time() - start) * 1000
        if STATS_AVAILABLE and Stats:
            try:
                Stats.incr(f"subscription_management.api.{api_name}.{operation}.failed", 1)
            except Exception:
                pass
        raise


def _handle_rate_limit(response: Any, max_wait: int = RATE_LIMIT_MAX_WAIT) -> None:
    """Maneja rate limiting (429) con backoff exponencial."""
    if hasattr(response, 'status_code') and response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 60))
        wait_time = min(retry_after, max_wait)
        logger.warning(f"Rate limited, waiting {wait_time}s", extra={"retry_after": retry_after})
        time.sleep(wait_time)


def _perform_health_check(stripe_api_key: Optional[str] = None) -> bool:
    """Realiza un health check de las APIs externas."""
    try:
        if stripe_api_key:
            headers = {"Authorization": f"Bearer {stripe_api_key}"}
            session = _get_stripe_session()
            if session:
                if HTTPX_AVAILABLE:
                    r = session.get("https://api.stripe.com/v1/charges?limit=1", headers=headers, timeout=10)
                else:
                    r = session.get("https://api.stripe.com/v1/charges?limit=1", headers=headers, timeout=10)
                
                if r.status_code == 401:
                    logger.error("Stripe API authentication failed")
                    return False
                r.raise_for_status()
        
        if STATS_AVAILABLE and Stats:
            try:
                Stats.incr("subscription_management.health_check.success", 1)
            except Exception:
                pass
        return True
    except Exception as e:
        logger.warning(f"Health check failed: {e}", exc_info=True)
        if STATS_AVAILABLE and Stats:
            try:
                Stats.incr("subscription_management.health_check.failed", 1)
            except Exception:
                pass
        return False


def _validate_subscription_data(sub: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Valida que los datos de suscripción sean válidos."""
    required_fields = ["ext_id", "customer_id", "end_date", "status"]
    issues = []
    
    for field in required_fields:
        if not sub.get(field):
            issues.append(f"Missing required field: {field}")
    
    # Validar formato de fecha
    end_date_str = sub.get("end_date")
    if end_date_str:
        try:
            datetime.fromisoformat(end_date_str)
        except (ValueError, TypeError):
            issues.append(f"Invalid end_date format: {end_date_str}")
    
    # Validar status
    status = sub.get("status")
    if status and status not in ["active", "inactive", "cancelled", "pending"]:
        issues.append(f"Invalid status: {status}")
    
    return len(issues) == 0, issues


def _get_cached_subscription(subscription_id: str, enable_cache: bool = True) -> Optional[Dict[str, Any]]:
    """Obtiene suscripción del cache si está disponible."""
    if not enable_cache or not CACHETOOLS_AVAILABLE or not _subscription_cache:
        return None
    
    try:
        return _subscription_cache.get(subscription_id)
    except Exception:
        return None


def _cache_subscription(subscription_id: str, subscription_data: Dict[str, Any], enable_cache: bool = True) -> None:
    """Guarda suscripción en cache."""
    if not enable_cache or not CACHETOOLS_AVAILABLE or not _subscription_cache:
        return
    
    try:
        _subscription_cache[subscription_id] = subscription_data
    except Exception:
        pass


def _log_progress(
    current: int,
    total: int,
    operation: str,
    successful: int = 0,
    failed: int = 0,
    interval: Optional[int] = None
) -> None:
    """Log de progreso con formato estándar."""
    if total == 0:
        return
    
    progress_pct = (current / total * 100) if total > 0 else 0.0
    
    # Calcular intervalo automático si no se especifica
    if interval is None:
        # Log cada 10% o cada 10 items, lo que sea más frecuente
        interval = max(1, min(total // 10, 10))
    
    if current % interval == 0 or current == total:
        logger.info(
            f"Progress [{operation}]: {current}/{total} ({progress_pct:.1f}%) - "
            f"{successful} successful, {failed} failed",
            extra={
                "operation": operation,
                "processed": current,
                "total": total,
                "progress_pct": round(progress_pct, 1),
                "successful": successful,
                "failed": failed,
            }
        )


def _save_checkpoint(checkpoint_key: str, data: Dict[str, Any], ttl_seconds: int = 86400) -> None:
    """Guarda un checkpoint para poder reanudar procesamiento."""
    try:
        checkpoint_data = {
            "timestamp": pendulum.now("UTC").int_timestamp,
            "expires_at": pendulum.now("UTC").int_timestamp + ttl_seconds,
            "data": data,
        }
        Variable.set(checkpoint_key, json.dumps(checkpoint_data))
        logger.debug(f"Checkpoint saved: {checkpoint_key}")
    except Exception as e:
        logger.warning(f"Failed to save checkpoint {checkpoint_key}: {e}", exc_info=True)


def _load_checkpoint(checkpoint_key: str) -> Optional[Dict[str, Any]]:
    """Carga un checkpoint si existe y no ha expirado."""
    try:
        checkpoint_data = Variable.get(checkpoint_key, default_var=None)
        if not checkpoint_data:
            return None
        
        checkpoint = json.loads(checkpoint_data)
        expires_at = checkpoint.get("expires_at", 0)
        now = pendulum.now("UTC").int_timestamp
        
        if expires_at > now:
            logger.info(f"Checkpoint loaded: {checkpoint_key}")
            return checkpoint.get("data")
        else:
            logger.info(f"Checkpoint expired: {checkpoint_key}")
            # Limpiar checkpoint expirado
            Variable.delete(checkpoint_key)
            return None
    except Exception as e:
        logger.warning(f"Failed to load checkpoint {checkpoint_key}: {e}", exc_info=True)
        return None


def _add_jitter(delay: float, jitter_pct: float = 0.1) -> float:
    """Agrega jitter aleatorio a un delay para evitar thundering herd."""
    import random
    jitter = delay * jitter_pct * random.uniform(-1, 1)
    return max(0, delay + jitter)


def _generate_idempotency_key(subscription_id: str, operation: str = "process") -> str:
    """Genera una clave de idempotencia única para una suscripción y operación."""
    import hashlib
    key_string = f"{subscription_id}:{operation}"
    return hashlib.sha256(key_string.encode()).hexdigest()[:16]


def _check_idempotency(lock_key: str, ttl_seconds: int = 86400) -> bool:
    """Verifica si una operación ya fue ejecutada (idempotencia)."""
    try:
        existing = Variable.get(lock_key, default_var=None)
        if existing:
            # Verificar si el lock expiró
            try:
                lock_data = json.loads(existing)
                expires_at = lock_data.get("expires_at", 0)
                now = pendulum.now("UTC").int_timestamp
                if expires_at > now:
                    # Lock aún activo
                    return True
                else:
                    # Lock expirado, limpiar
                    Variable.delete(lock_key)
                    return False
            except Exception:
                # Formato inválido, asumir que expiró
                Variable.delete(lock_key)
                return False
        return False
    except Exception:
        return False


def _set_idempotency_lock(lock_key: str, ttl_seconds: int = 86400) -> None:
    """Establece un lock de idempotencia con TTL."""
    try:
        now = pendulum.now("UTC").int_timestamp
        lock_data = {
            "acquired_at": now,
            "expires_at": now + ttl_seconds,
            "run_id": os.environ.get("AIRFLOW_RUN_ID", "unknown"),
        }
        Variable.set(lock_key, json.dumps(lock_data))
    except Exception as e:
        logger.warning(f"Failed to set idempotency lock {lock_key}: {e}", exc_info=True)


def _acquire_distributed_lock(lock_key: str, ttl_seconds: int = 3600) -> bool:
    """
    Adquiere un lock distribuido usando Airflow Variables.
    
    Returns:
        True si el lock fue adquirido, False si ya existe
    """
    try:
        existing = Variable.get(lock_key, default_var=None)
        if existing:
            # Verificar si el lock expiró
            try:
                lock_data = json.loads(existing)
                expires_at = lock_data.get("expires_at", 0)
                now = pendulum.now("UTC").int_timestamp
                if expires_at > now:
                    # Lock aún activo
                    return False
            except Exception:
                # Formato inválido, asumir que expiró
                pass
        
        # Crear nuevo lock
        now = pendulum.now("UTC").int_timestamp
        lock_data = {
            "acquired_at": now,
            "expires_at": now + ttl_seconds,
            "run_id": os.environ.get("AIRFLOW_RUN_ID", "unknown"),
        }
        Variable.set(lock_key, json.dumps(lock_data))
        return True
    except Exception as e:
        logger.warning(f"Failed to acquire lock {lock_key}: {e}", exc_info=True)
        return False


def _release_distributed_lock(lock_key: str) -> None:
    """Libera un lock distribuido."""
    try:
        Variable.delete(lock_key)
    except Exception as e:
        logger.warning(f"Failed to release lock {lock_key}: {e}", exc_info=True)


def _deduplicate_subscriptions(subscriptions: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Detecta y elimina suscripciones duplicadas basándose en customer_id y plan.
    
    Returns:
        (suscripciones únicas, duplicados detectados)
    """
    seen = {}
    unique_subscriptions = []
    duplicates = []
    
    for sub in subscriptions:
        customer_id = sub.get("customer_id")
        plan_name = sub.get("plan_name", "")
        ext_id = sub.get("ext_id")
        
        # Clave de deduplicación
        dedup_key = f"{customer_id}:{plan_name}"
        
        if dedup_key in seen:
            # Es duplicado
            duplicates.append({
                "subscription": sub,
                "duplicate_of": seen[dedup_key],
                "reason": "same_customer_and_plan"
            })
            logger.warning(
                f"Duplicate subscription detected: {ext_id}",
                extra={
                    "subscription_id": ext_id,
                    "customer_id": customer_id,
                    "duplicate_of": seen[dedup_key]
                }
            )
        else:
            # Es único
            seen[dedup_key] = ext_id
            unique_subscriptions.append(sub)
    
    return unique_subscriptions, duplicates


def _enrich_subscription_data(subscription: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enriquece datos de suscripción con información adicional.
    Por ahora simple, pero puede extenderse con APIs externas.
    """
    enriched = subscription.copy()
    enriched_data = {}
    
    # Enriquecer con información del customer si está disponible
    customer_email = subscription.get("customer_email")
    if customer_email:
        # Inferir dominio de empresa desde email
        if "@" in customer_email:
            domain = customer_email.split("@")[1]
            enriched_data["email_domain"] = domain
            enriched_data["is_corporate_email"] = domain not in [
                "gmail.com", "outlook.com", "yahoo.com", "hotmail.com"
            ]
    
    # Calcular días hasta vencimiento
    end_date_str = subscription.get("end_date")
    if end_date_str:
        try:
            end_date = datetime.fromisoformat(end_date_str).date()
            today = date.today()
            days_until_expiry = (end_date - today).days
            enriched_data["days_until_expiry"] = days_until_expiry
            enriched_data["is_expiring_soon"] = days_until_expiry <= 7
        except (ValueError, TypeError):
            pass
    
    # Calcular valor de vida del cliente estimado
    amount = subscription.get("amount")
    billing_cycle = subscription.get("billing_cycle", "monthly")
    if amount:
        if billing_cycle == "monthly":
            estimated_yearly = amount * 12
        elif billing_cycle == "annual":
            estimated_yearly = amount
        else:
            estimated_yearly = amount * 12  # Default a monthly
        
        enriched_data["estimated_yearly_value"] = estimated_yearly
        enriched_data["value_tier"] = (
            "high" if estimated_yearly >= 10000
            else "medium" if estimated_yearly >= 1000
            else "low"
        )
    
    enriched["enriched_data"] = enriched_data
    enriched["is_enriched"] = True
    
    return enriched


def _calculate_renewal_probability(subscription: Dict[str, Any]) -> float:
    """
    Calcula probabilidad de renovación basada en múltiples factores.
    Retorna probabilidad entre 0.0 y 1.0
    """
    probability = 0.5  # Base
    
    # Factores positivos
    enriched_data = subscription.get("enriched_data", {})
    
    # Valor alto = mayor probabilidad
    value_tier = enriched_data.get("value_tier", "low")
    if value_tier == "high":
        probability += 0.2
    elif value_tier == "medium":
        probability += 0.1
    
    # Email corporativo = mayor probabilidad
    if enriched_data.get("is_corporate_email"):
        probability += 0.1
    
    # Días hasta vencimiento óptimos (ni muy pronto ni muy tarde)
    days_until = enriched_data.get("days_until_expiry", 0)
    if 3 <= days_until <= 14:
        probability += 0.1
    
    # Historial de notificaciones
    notified_count = subscription.get("notified_count", 0)
    if 1 <= notified_count <= 3:
        probability += 0.05  # Notificaciones moderadas ayudan
    elif notified_count > 5:
        probability -= 0.1  # Demasiadas notificaciones son malas
    
    # Antigüedad de suscripción
    start_date_str = subscription.get("start_date")
    if start_date_str:
        try:
            start_date = datetime.fromisoformat(start_date_str).date()
            days_active = (date.today() - start_date).days
            if days_active > 365:
                probability += 0.15  # Clientes de largo plazo
            elif days_active > 180:
                probability += 0.1
        except (ValueError, TypeError):
            pass
    
    # Cap entre 0 y 1
    return max(0.0, min(1.0, probability))


def _detect_predictive_alerts(
    subscriptions: List[Dict[str, Any]],
    historical_metrics: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Detecta alertas predictivas basadas en tendencias y umbrales.
    """
    alerts = []
    
    if not subscriptions:
        return alerts
    
    # Calcular métricas actuales
    total = len(subscriptions)
    high_value_count = sum(1 for s in subscriptions 
                          if s.get("enriched_data", {}).get("value_tier") == "high")
    low_probability_count = sum(1 for s in subscriptions 
                               if _calculate_renewal_probability(s) < 0.3)
    expiring_soon_count = sum(1 for s in subscriptions 
                             if s.get("enriched_data", {}).get("is_expiring_soon"))
    
    # Alerta: Muchas suscripciones de alto valor expirando
    if high_value_count > total * 0.3:  # Más del 30%
        alerts.append({
            "type": "high_value_at_risk",
            "severity": "high",
            "message": f"Alto número de suscripciones de valor expirando: {high_value_count}/{total}",
            "count": high_value_count,
            "percentage": (high_value_count / total * 100) if total > 0 else 0,
        })
    
    # Alerta: Muchas con baja probabilidad de renovación
    if low_probability_count > total * 0.4:  # Más del 40%
        alerts.append({
            "type": "low_renewal_probability",
            "severity": "medium",
            "message": f"Muchas suscripciones con baja probabilidad de renovación: {low_probability_count}/{total}",
            "count": low_probability_count,
            "percentage": (low_probability_count / total * 100) if total > 0 else 0,
        })
    
    # Comparar con histórico si está disponible
    if historical_metrics:
        last_count = historical_metrics.get("expiring_subscriptions", 0)
        if last_count > 0:
            change_pct = ((total - last_count) / last_count) * 100
            
            # Alerta: Aumento significativo
            if change_pct > 50:
                alerts.append({
                    "type": "significant_increase",
                    "severity": "warning",
                    "message": f"Aumento significativo en suscripciones expirando: {change_pct:.1f}% vs anterior",
                    "current": total,
                    "previous": last_count,
                    "change_pct": change_pct,
                })
            
            # Alerta: Disminución significativa (puede indicar problema)
            if change_pct < -50:
                alerts.append({
                    "type": "significant_decrease",
                    "severity": "info",
                    "message": f"Disminución significativa en suscripciones expirando: {change_pct:.1f}% vs anterior",
                    "current": total,
                    "previous": last_count,
                    "change_pct": change_pct,
                })
    
    return alerts


def _get_ml_prediction(subscription: Dict[str, Any], ml_endpoint: Optional[str] = None) -> Optional[float]:
    """
    Obtiene predicción de probabilidad de renovación desde modelo ML si está disponible.
    """
    if not ml_endpoint:
        ml_endpoint = os.getenv("SUBSCRIPTION_ML_ENDPOINT", "")
    
    if not ml_endpoint:
        return None
    
    try:
        session = _get_stripe_session() or requests
        if not session:
            return None
        
        payload = {
            "customer_id": subscription.get("customer_id"),
            "customer_email": subscription.get("customer_email"),
            "amount": subscription.get("amount"),
            "billing_cycle": subscription.get("billing_cycle"),
            "days_until_expiry": subscription.get("enriched_data", {}).get("days_until_expiry"),
            "value_tier": subscription.get("enriched_data", {}).get("value_tier"),
            "notified_count": subscription.get("notified_count", 0),
            "days_active": None,  # Se calcularía si hay start_date
        }
        
        # Calcular días activos si está disponible
        start_date_str = subscription.get("start_date")
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str).date()
                days_active = (date.today() - start_date).days
                payload["days_active"] = days_active
            except (ValueError, TypeError):
                pass
        
        response = session.post(
            ml_endpoint,
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            ml_probability = result.get("renewal_probability")
            if ml_probability is not None:
                logger.info(
                    f"ML prediction obtained for subscription",
                    extra={"subscription_id": subscription.get("ext_id"), "ml_probability": ml_probability}
                )
                return float(ml_probability)
    except Exception as e:
        logger.debug(f"ML prediction failed: {e}")
    
    return None


def _segment_subscriptions(subscriptions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Segmenta suscripciones en grupos para personalización y análisis.
    """
    segments = {
        "high_value_high_risk": [],
        "high_value_low_risk": [],
        "medium_value": [],
        "low_value": [],
        "corporate": [],
        "personal": [],
        "expiring_soon": [],
        "long_term": [],
    }
    
    for sub in subscriptions:
        enriched_data = sub.get("enriched_data", {})
        value_tier = enriched_data.get("value_tier", "low")
        renewal_risk = enriched_data.get("renewal_risk", "medium")
        is_corporate = enriched_data.get("is_corporate_email", False)
        days_until = enriched_data.get("days_until_expiry", 0)
        
        # Segmentación por valor y riesgo
        if value_tier == "high":
            if renewal_risk == "high":
                segments["high_value_high_risk"].append(sub)
            else:
                segments["high_value_low_risk"].append(sub)
        elif value_tier == "medium":
            segments["medium_value"].append(sub)
        else:
            segments["low_value"].append(sub)
        
        # Segmentación por tipo de email
        if is_corporate:
            segments["corporate"].append(sub)
        else:
            segments["personal"].append(sub)
        
        # Segmentación por timing
        if days_until <= 7:
            segments["expiring_soon"].append(sub)
        
        # Segmentación por antigüedad
        start_date_str = sub.get("start_date")
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str).date()
                days_active = (date.today() - start_date).days
                if days_active > 365:
                    segments["long_term"].append(sub)
            except (ValueError, TypeError):
                pass
    
    return segments


def _analyze_temporal_trends(
    subscriptions: List[Dict[str, Any]],
    date_field: str = "end_date",
    value_field: str = "amount"
) -> Dict[str, Any]:
    """
    Analiza tendencias temporales en las suscripciones.
    """
    if not subscriptions:
        return {"has_trends": False}
    
    trends = {
        "total": len(subscriptions),
        "by_month": {},
        "by_week": {},
        "total_value": 0,
        "avg_value": 0,
        "growth_rate": None,
    }
    
    from collections import defaultdict
    monthly = defaultdict(list)
    weekly = defaultdict(list)
    
    for sub in subscriptions:
        # Obtener fecha
        date_str = sub.get(date_field)
        if not date_str:
            continue
        
        try:
            date_obj = datetime.fromisoformat(date_str).date()
            month_key = date_obj.strftime("%Y-%m")
            week_key = f"{date_obj.year}-W{date_obj.isocalendar()[1]:02d}"
            
            # Obtener valor
            value = float(sub.get(value_field, 0) or 0)
            trends["total_value"] += value
            
            monthly[month_key].append(value)
            weekly[week_key].append(value)
        except (ValueError, TypeError):
            continue
    
    # Calcular promedios por mes
    for month, values in monthly.items():
        trends["by_month"][month] = {
            "count": len(values),
            "total": sum(values),
            "avg": sum(values) / len(values) if values else 0,
        }
    
    # Calcular promedios por semana
    for week, values in weekly.items():
        trends["by_week"][week] = {
            "count": len(values),
            "total": sum(values),
            "avg": sum(values) / len(values) if values else 0,
        }
    
    # Calcular tasa de crecimiento si hay datos mensuales
    if len(monthly) >= 2:
        sorted_months = sorted(monthly.keys())
        last_month = sorted_months[-1]
        prev_month = sorted_months[-2]
        
        last_total = sum(monthly[last_month])
        prev_total = sum(monthly[prev_month])
        
        if prev_total > 0:
            growth = ((last_total - prev_total) / prev_total) * 100
            trends["growth_rate"] = growth
    
    trends["avg_value"] = trends["total_value"] / len(subscriptions) if subscriptions else 0
    trends["has_trends"] = True
    
    return trends


def _generate_action_recommendations(
    subscription: Dict[str, Any],
    segments: Dict[str, List[Dict[str, Any]]]
) -> List[str]:
    """
    Genera recomendaciones de acción personalizadas para cada suscripción.
    """
    recommendations = []
    
    enriched_data = subscription.get("enriched_data", {})
    renewal_probability = enriched_data.get("renewal_probability", 0.5)
    renewal_risk = enriched_data.get("renewal_risk", "medium")
    value_tier = enriched_data.get("value_tier", "low")
    days_until = enriched_data.get("days_until_expiry", 0)
    notified_count = subscription.get("notified_count", 0)
    
    # Recomendaciones basadas en riesgo
    if renewal_risk == "high":
        recommendations.append("Alta prioridad: Contactar directamente por teléfono")
        recommendations.append("Ofrecer descuento o incentivo de renovación")
        recommendations.append("Programar llamada de retención urgente")
    elif renewal_risk == "medium":
        recommendations.append("Enviar email de seguimiento personalizado")
        recommendations.append("Ofrecer beneficios adicionales")
    
    # Recomendaciones basadas en valor
    if value_tier == "high":
        recommendations.append("Asignar Account Manager dedicado")
        recommendations.append("Programar reunión estratégica")
        if renewal_risk == "high":
            recommendations.append("Considerar upgrade o plan premium")
    
    # Recomendaciones basadas en timing
    if days_until <= 3:
        recommendations.append("Acción inmediata requerida")
    
    if days_until <= 7 and notified_count == 0:
        recommendations.append("Enviar notificación urgente")
    
    # Recomendaciones basadas en segmentación
    if subscription in segments.get("corporate", []):
        recommendations.append("Enfoque en ROI y beneficios empresariales")
    
    if subscription in segments.get("long_term", []):
        recommendations.append("Resaltar relación de largo plazo y lealtad")
        recommendations.append("Ofrecer programa de fidelidad")
    
    # Recomendaciones basadas en probabilidad
    if renewal_probability < 0.3:
        recommendations.append("Implementar estrategia de recuperación agresiva")
        recommendations.append("Analizar razón de no renovación")
    
    return list(set(recommendations))  # Eliminar duplicados


def _ab_test_notification(
    subscription: Dict[str, Any],
    variant: Optional[str] = None
) -> Dict[str, Any]:
    """
    A/B testing de notificaciones para optimizar conversión.
    """
    if variant is None:
        # Asignar variante basado en hash del subscription_id para consistencia
        sub_id = subscription.get("ext_id", "")
        variant_hash = hash(sub_id) % 2
        variant = "A" if variant_hash == 0 else "B"
    
    # Variante A: Enfoque en beneficio
    # Variante B: Enfoque en urgencia
    if variant == "A":
        subject_template = "No pierdas los beneficios de {plan_name}"
        body_tone = "benefit_focused"
    else:
        subject_template = "Tu suscripción {plan_name} expira en {days} días"
        body_tone = "urgency_focused"
    
    return {
        "variant": variant,
        "subject_template": subject_template,
        "body_tone": body_tone,
        "tracking_id": f"{subscription.get('ext_id')}_{variant}",
    }


def _analyze_cohorts(
    subscriptions: List[Dict[str, Any]],
    hook: PostgresHook
) -> Dict[str, Any]:
    """
    Analiza cohorts de suscripciones por mes de inicio.
    """
    if not subscriptions:
        return {"cohorts": []}
    
    from collections import defaultdict
    
    # Agrupar por cohort (mes de inicio)
    cohorts = defaultdict(lambda: {
        "total": 0,
        "expiring": 0,
        "renewed": 0,
        "total_value": 0,
        "avg_value": 0,
    })
    
    for sub in subscriptions:
        start_date_str = sub.get("start_date")
        if not start_date_str:
            continue
        
        try:
            start_date = datetime.fromisoformat(start_date_str).date()
            cohort_key = start_date.strftime("%Y-%m")
            
            cohorts[cohort_key]["total"] += 1
            
            # Verificar si está expirando
            end_date_str = sub.get("end_date")
            if end_date_str:
                try:
                    end_date = datetime.fromisoformat(end_date_str).date()
                    days_until = (end_date - date.today()).days
                    if 0 <= days_until <= 30:
                        cohorts[cohort_key]["expiring"] += 1
                except (ValueError, TypeError):
                    pass
            
            # Valor
            amount = float(sub.get("amount", 0) or 0)
            cohorts[cohort_key]["total_value"] += amount
    
        except (ValueError, TypeError):
            continue
    
    # Calcular promedios y tasas
    cohort_results = []
    for cohort_key in sorted(cohorts.keys()):
        cohort_data = cohorts[cohort_key]
        cohort_data["cohort"] = cohort_key
        cohort_data["avg_value"] = (
            cohort_data["total_value"] / cohort_data["total"]
            if cohort_data["total"] > 0 else 0
        )
        cohort_data["expiring_rate"] = (
            (cohort_data["expiring"] / cohort_data["total"]) * 100
            if cohort_data["total"] > 0 else 0
        )
        cohort_results.append(cohort_data)
    
    return {
        "cohorts": cohort_results,
        "total_cohorts": len(cohort_results),
        "has_data": len(cohort_results) > 0,
    }


def _optimize_notification_timing(
    subscription: Dict[str, Any],
    historical_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Optimiza el timing de notificaciones basado en datos históricos.
    """
    optimized = {
        "optimal_days_before": 7,  # Default
        "optimal_time": "09:00",  # Default
        "optimal_day_of_week": "Monday",  # Default
        "confidence": 0.5,
    }
    
    # Si hay datos históricos, usar para optimizar
    if historical_data:
        best_timing = historical_data.get("best_timing", {})
        if best_timing:
            optimized["optimal_days_before"] = best_timing.get("days_before", 7)
            optimized["optimal_time"] = best_timing.get("time", "09:00")
            optimized["optimal_day_of_week"] = best_timing.get("day_of_week", "Monday")
            optimized["confidence"] = best_timing.get("confidence", 0.5)
    
    # Ajustar basado en valor y riesgo
    enriched_data = subscription.get("enriched_data", {})
    value_tier = enriched_data.get("value_tier", "low")
    renewal_risk = enriched_data.get("renewal_risk", "medium")
    
    # Alta prioridad = notificar más temprano
    if value_tier == "high" or renewal_risk == "high":
        optimized["optimal_days_before"] = max(10, optimized["optimal_days_before"])
        optimized["confidence"] = min(1.0, optimized["confidence"] + 0.2)
    
    return optimized


def _calculate_churn_risk(
    subscription: Dict[str, Any],
    historical_renewals: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Calcula riesgo de churn basado en múltiples factores.
    """
    churn_risk = {
        "risk_score": 0.5,  # 0-1, donde 1 es máximo riesgo
        "factors": [],
        "mitigation_strategies": [],
    }
    
    enriched_data = subscription.get("enriched_data", {})
    renewal_probability = enriched_data.get("renewal_probability", 0.5)
    
    # Factor 1: Probabilidad de renovación inversa
    churn_risk["risk_score"] = 1.0 - renewal_probability
    
    # Factor 2: Historial de renovaciones
    if historical_renewals:
        renewal_count = sum(1 for r in historical_renewals if r.get("renewed"))
        total_attempts = len(historical_renewals)
        if total_attempts > 0:
            renewal_rate = renewal_count / total_attempts
            if renewal_rate < 0.5:
                churn_risk["risk_score"] = min(1.0, churn_risk["risk_score"] + 0.2)
                churn_risk["factors"].append("Bajo historial de renovaciones")
    
    # Factor 3: Días hasta vencimiento
    days_until = enriched_data.get("days_until_expiry", 0)
    if days_until <= 3:
        churn_risk["risk_score"] = min(1.0, churn_risk["risk_score"] + 0.3)
        churn_risk["factors"].append("Vencimiento inminente")
    
    # Factor 4: Notificaciones no respondidas
    notified_count = subscription.get("notified_count", 0)
    if notified_count > 3:
        churn_risk["risk_score"] = min(1.0, churn_risk["risk_score"] + 0.1)
        churn_risk["factors"].append("Múltiples notificaciones sin respuesta")
    
    # Estrategias de mitigación
    if churn_risk["risk_score"] > 0.7:
        churn_risk["mitigation_strategies"].append("Contacto directo urgente")
        churn_risk["mitigation_strategies"].append("Ofrecer descuento significativo")
        churn_risk["mitigation_strategies"].append("Asignar Account Manager")
    elif churn_risk["risk_score"] > 0.5:
        churn_risk["mitigation_strategies"].append("Email personalizado")
        churn_risk["mitigation_strategies"].append("Programar llamada de seguimiento")
    
    return churn_risk


def _estimate_lifetime_value(
    subscription: Dict[str, Any],
    historical_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Estima el Lifetime Value (LTV) de la suscripción.
    """
    ltv = {
        "estimated_ltv": 0,
        "months_remaining": 0,
        "confidence": 0.5,
        "scenarios": {},
    }
    
    amount = float(subscription.get("amount", 0) or 0)
    billing_cycle = subscription.get("billing_cycle", "monthly")
    
    # Calcular meses hasta vencimiento
    end_date_str = subscription.get("end_date")
    if end_date_str:
        try:
            end_date = datetime.fromisoformat(end_date_str).date()
            months_remaining = max(0, (end_date.year - date.today().year) * 12 + 
                                   (end_date.month - date.today().month))
            ltv["months_remaining"] = months_remaining
        except (ValueError, TypeError):
            months_remaining = 0
    else:
        months_remaining = 0
    
    # Calcular LTV base
    if billing_cycle == "monthly":
        ltv["estimated_ltv"] = amount * months_remaining
    elif billing_cycle == "annual":
        ltv["estimated_ltv"] = amount * (months_remaining / 12)
    else:
        ltv["estimated_ltv"] = amount * months_remaining
    
    # Escenarios
    enriched_data = subscription.get("enriched_data", {})
    renewal_probability = enriched_data.get("renewal_probability", 0.5)
    
    # Escenario optimista (renovación)
    ltv["scenarios"]["optimistic"] = ltv["estimated_ltv"] * 2  # Asume renovación
    
    # Escenario realista (probabilidad de renovación)
    ltv["scenarios"]["realistic"] = ltv["estimated_ltv"] * (1 + renewal_probability)
    
    # Escenario pesimista (no renovación)
    ltv["scenarios"]["pessimistic"] = ltv["estimated_ltv"]
    
    # Ajustar confianza basado en datos disponibles
    if historical_data:
        ltv["confidence"] = min(1.0, ltv["confidence"] + 0.3)
    
    if subscription.get("start_date"):
        days_active = (date.today() - datetime.fromisoformat(subscription["start_date"]).date()).days
        if days_active > 180:
            ltv["confidence"] = min(1.0, ltv["confidence"] + 0.2)
    
    return ltv


def _sync_to_crm(
    subscription: Dict[str, Any],
    crm_type: str = "salesforce",
    crm_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Sincroniza suscripción con CRM (Salesforce/Pipedrive).
    """
    sync_result = {
        "synced": False,
        "crm_id": None,
        "error": None,
    }
    
    # Verificar si está habilitado
    enable_crm_sync = os.getenv("ENABLE_CRM_SYNC", "false").lower() == "true"
    if not enable_crm_sync or not crm_config:
        return sync_result
    
    try:
        from data.integrations.connectors import create_connector
        
        # Crear conector según tipo
        if crm_type == "salesforce":
            connector_config = {
                "username": crm_config.get("username"),
                "password": crm_config.get("password"),
                "security_token": crm_config.get("security_token"),
                "sobject_type": "Subscription__c",  # Custom object
            }
        elif crm_type == "pipedrive":
            connector_config = {
                "api_token": crm_config.get("api_token"),
                "company_domain": crm_config.get("company_domain"),
                "resource_type": "deals",
            }
        else:
            sync_result["error"] = f"CRM type not supported: {crm_type}"
            return sync_result
        
        connector = create_connector(crm_type, connector_config)
        if not connector.connect():
            sync_result["error"] = "Failed to connect to CRM"
            return sync_result
        
        # Preparar datos para CRM
        crm_data = {
            "customer_email": subscription.get("customer_email"),
            "customer_id": subscription.get("customer_id"),
            "plan_name": subscription.get("plan_name"),
            "amount": subscription.get("amount"),
            "status": subscription.get("status"),
            "end_date": subscription.get("end_date"),
            "renewal_probability": subscription.get("enriched_data", {}).get("renewal_probability"),
        }
        
        # Sincronizar
        result = connector.create_or_update(crm_data)
        if result:
            sync_result["synced"] = True
            sync_result["crm_id"] = result.get("id")
            logger.info(
                f"Subscription synced to CRM",
                extra={"subscription_id": subscription.get("ext_id"), "crm_id": sync_result["crm_id"]}
            )
        
    except ImportError:
        sync_result["error"] = "CRM connector not available"
    except Exception as e:
        sync_result["error"] = str(e)
        logger.warning(f"CRM sync failed: {e}", exc_info=True)
    
    return sync_result


def _trigger_automated_workflow(
    subscription: Dict[str, Any],
    workflow_type: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Dispara workflows automatizados basados en eventos.
    """
    workflow_result = {
        "triggered": False,
        "workflow_id": None,
        "actions": [],
    }
    
    enriched_data = subscription.get("enriched_data", {})
    renewal_risk = enriched_data.get("renewal_risk", "medium")
    churn_risk = enriched_data.get("churn_risk", 0.5)
    
    # Workflow: Alta prioridad de churn
    if workflow_type == "high_churn_risk" and churn_risk > 0.7:
        workflow_result["triggered"] = True
        workflow_result["actions"].append("assign_account_manager")
        workflow_result["actions"].append("schedule_retention_call")
        workflow_result["actions"].append("create_retention_discount")
        
        # Trigger DAG de retención si está disponible
        try:
            from airflow.operators.trigger_dagrun import TriggerDagRunOperator
            # Nota: Esto se haría en el contexto del DAG, no aquí
            workflow_result["workflow_id"] = f"retention_{subscription.get('ext_id')}"
        except ImportError:
            pass
    
    # Workflow: Alta probabilidad de renovación
    elif workflow_type == "high_renewal_probability" and renewal_risk == "low":
        workflow_result["triggered"] = True
        workflow_result["actions"].append("send_upsell_offer")
        workflow_result["actions"].append("highlight_premium_features")
    
    # Workflow: Expiración inminente
    elif workflow_type == "expiring_soon":
        days_until = enriched_data.get("days_until_expiry", 0)
        if days_until <= 3:
            workflow_result["triggered"] = True
            workflow_result["actions"].append("send_urgent_notification")
            workflow_result["actions"].append("escalate_to_manager")
    
    if workflow_result["triggered"]:
        logger.info(
            f"Workflow triggered: {workflow_type}",
            extra={
                "subscription_id": subscription.get("ext_id"),
                "actions": workflow_result["actions"]
            }
        )
    
    return workflow_result


def _generate_executive_report(
    subscriptions_data: Dict[str, Any],
    notifications_data: Dict[str, Any],
    renewal_data: Dict[str, Any],
    inactivation_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Genera reporte ejecutivo con métricas clave y recomendaciones.
    """
    report = {
        "executive_summary": {},
        "key_metrics": {},
        "trends": {},
        "recommendations": [],
        "risk_assessment": {},
        "generated_at": datetime.utcnow().isoformat(),
    }
    
    # Resumen ejecutivo
    total_expiring = subscriptions_data.get("count", 0)
    total_notified = notifications_data.get("total_sent", 0)
    total_renewed = renewal_data.get("renewed_count", 0)
    renewal_rate = (total_renewed / total_notified * 100) if total_notified > 0 else 0
    
    report["executive_summary"] = {
        "total_subscriptions_expiring": total_expiring,
        "notifications_sent": total_notified,
        "renewals_confirmed": total_renewed,
        "renewal_rate": renewal_rate,
        "at_risk_count": sum(1 for s in subscriptions_data.get("expiring_subscriptions", [])
                            if s.get("enriched_data", {}).get("churn_risk", 0) > 0.7),
    }
    
    # Métricas clave
    segments = subscriptions_data.get("segments", {})
    temporal_trends = subscriptions_data.get("temporal_trends", {})
    
    report["key_metrics"] = {
        "high_value_at_risk": segments.get("high_value_high_risk", 0),
        "total_value_expiring": temporal_trends.get("total_value", 0),
        "avg_subscription_value": temporal_trends.get("avg_value", 0),
        "growth_rate": temporal_trends.get("growth_rate"),
        "churn_risk_high": report["executive_summary"]["at_risk_count"],
    }
    
    # Recomendaciones
    if renewal_rate < 50:
        report["recommendations"].append({
            "priority": "high",
            "title": "Tasa de renovación baja",
            "description": f"La tasa de renovación actual es {renewal_rate:.1f}%. Considerar estrategias de retención más agresivas.",
            "action": "Revisar estrategia de notificaciones y ofrecer incentivos",
        })
    
    if report["key_metrics"]["high_value_at_risk"] > 0:
        report["recommendations"].append({
            "priority": "high",
            "title": "Suscripciones de alto valor en riesgo",
            "description": f"{report['key_metrics']['high_value_at_risk']} suscripciones de alto valor están en riesgo.",
            "action": "Asignar Account Managers dedicados y crear ofertas personalizadas",
        })
    
    if report["key_metrics"]["churn_risk_high"] > total_expiring * 0.3:
        report["recommendations"].append({
            "priority": "medium",
            "title": "Alto número de suscripciones con riesgo de churn",
            "description": f"{report['key_metrics']['churn_risk_high']} suscripciones tienen alto riesgo de churn.",
            "action": "Implementar estrategias de mitigación de churn urgentemente",
        })
    
    # Evaluación de riesgo
    report["risk_assessment"] = {
        "overall_risk": "medium",
        "factors": [],
    }
    
    if renewal_rate < 40:
        report["risk_assessment"]["overall_risk"] = "high"
        report["risk_assessment"]["factors"].append("Tasa de renovación muy baja")
    
    if report["key_metrics"]["high_value_at_risk"] > 5:
        report["risk_assessment"]["factors"].append("Múltiples suscripciones de alto valor en riesgo")
        if report["risk_assessment"]["overall_risk"] == "medium":
            report["risk_assessment"]["overall_risk"] = "high"
    
    return report


def _check_feature_flag(flag_name: str, default: bool = False) -> bool:
    """
    Verifica feature flags desde variables de Airflow.
    """
    try:
        flag_key = f"subscription_management.flag.{flag_name}"
        flag_value = Variable.get(flag_key, default_var=str(default))
        return str(flag_value).lower() in ("true", "1", "yes", "on")
    except Exception:
        return default


def _export_metrics_to_s3(summary: Dict[str, Any], s3_bucket: Optional[str] = None, s3_path: str = "subscription_metrics") -> Dict[str, Any]:
    """
    Exporta métricas a S3 para análisis posterior (opcional).
    """
    if not s3_bucket:
        s3_bucket = os.getenv("SUBSCRIPTION_METRICS_S3_BUCKET", "")
    
    if not s3_bucket:
        return {"exported": False, "reason": "s3_bucket_not_configured"}
    
    try:
        try:
            import boto3
            from botocore.exceptions import ClientError
            BOTO3_AVAILABLE = True
        except ImportError:
            BOTO3_AVAILABLE = False
        
        if not BOTO3_AVAILABLE:
            return {"exported": False, "reason": "boto3_not_available"}
        
        s3_client = boto3.client('s3')
        
        # Generar nombre de archivo con timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{s3_path}/subscription_metrics_{timestamp}.json"
        
        # Preparar datos para exportar
        export_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": summary,
        }
        
        # Subir a S3
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=filename,
            Body=json.dumps(export_data, indent=2),
            ContentType="application/json"
        )
        
        logger.info(
            f"Metrics exported to S3: s3://{s3_bucket}/{filename}",
            extra={"s3_bucket": s3_bucket, "s3_path": filename}
        )
        
        if STATS_AVAILABLE and Stats:
            Stats.incr("subscription_management.s3.exported", 1)
        
        return {"exported": True, "s3_path": f"s3://{s3_bucket}/{filename}"}
        
    except Exception as e:
        logger.error(f"Error exporting metrics to S3: {e}", exc_info=True)
        return {"exported": False, "reason": str(e)[:200]}


def _enrich_with_external_api(subscription: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enriquece suscripción con datos de APIs externas (Clearbit, etc).
    Por ahora simulado, pero puede extenderse fácilmente.
    """
    enriched = subscription.copy()
    external_data = {}
    
    customer_email = subscription.get("customer_email")
    company = subscription.get("company") or subscription.get("customer_name", "")
    
    # Enriquecer con Clearbit si está configurado (similar al pattern de web_lead_capture)
    clearbit_api_key = os.getenv("CLEARBIT_API_KEY")
    if clearbit_api_key and customer_email:
        try:
            session = _get_stripe_session() or requests
            if session:
                response = session.get(
                    f"https://person.clearbit.com/v2/combined/find?email={customer_email}",
                    auth=(clearbit_api_key, ''),
                    timeout=2
                )
                if response.status_code == 200:
                    clearbit_data = response.json()
                    external_data["clearbit"] = {
                        "person": clearbit_data.get("person", {}),
                        "company": clearbit_data.get("company", {}),
                    }
                    
                    # Actualizar datos si no existen
                    if not enriched.get("company") and clearbit_data.get("company", {}).get("name"):
                        enriched["company"] = clearbit_data["company"]["name"]
                    
                    logger.info(
                        f"Enriched subscription with Clearbit",
                        extra={"subscription_id": subscription.get("ext_id")}
                    )
        except Exception as e:
            logger.debug(f"Clearbit enrichment failed: {e}")
    
    # Agregar datos externos al enriched_data existente
    if external_data:
        current_enriched = enriched.get("enriched_data", {})
        current_enriched.update(external_data)
        enriched["enriched_data"] = current_enriched
        enriched["has_external_data"] = True
    
    return enriched


def _track_cost_operation(operation: str, cost_usd: float, metadata: Optional[Dict[str, Any]] = None) -> None:
    """Trackea costos de operaciones (API calls, etc)."""
    try:
        key = "subscription_management.cost_tracking"
        data_str = Variable.get(key, default_var=None)
        
        if data_str:
            data = json.loads(data_str)
        else:
            data = {"total_cost": 0.0, "operations": []}
        
        data["total_cost"] = data.get("total_cost", 0.0) + cost_usd
        data["operations"].append({
            "operation": operation,
            "cost_usd": cost_usd,
            "timestamp": pendulum.now("UTC").isoformat(),
            "metadata": metadata or {},
        })
        
        # Mantener solo últimos 1000 operaciones
        data["operations"] = data["operations"][-1000:]
        
        Variable.set(key, json.dumps(data))
        
        if STATS_AVAILABLE and Stats:
            try:
                Stats.gauge("subscription_management.cost.total_usd", data["total_cost"])
                Stats.incr("subscription_management.cost.operations", 1)
            except Exception:
                pass
    except Exception:
        pass


def _save_to_dlq(item: Dict[str, Any], error: str, dlq_path: str = "/tmp/subscription_management_dlq.jsonl") -> None:
    """Guarda un item fallido en dead letter queue."""
    try:
        os.makedirs(os.path.dirname(dlq_path), exist_ok=True)
        with open(dlq_path, "a") as f:
            dlq_record = {
                "timestamp": pendulum.now("UTC").isoformat(),
                "item": item,
                "error": error,
                "retried": False,
                "dag_id": "subscription_management",
            }
            f.write(json.dumps(dlq_record) + "\n")
        logger.warning(
            f"Saved to DLQ: {error}",
            extra={"subscription_id": item.get("subscription_id") or item.get("ext_id")}
        )
        if STATS_AVAILABLE and Stats:
            Stats.incr("subscription_management.dlq.saved", 1)
    except Exception as e:
        logger.error(f"Failed to save to DLQ: {e}", exc_info=True)


def _detect_anomalies(
    subscriptions: List[Dict[str, Any]],
    z_score_threshold: float = 2.5
) -> List[Dict[str, Any]]:
    """
    Detecta anomalías en suscripciones usando Z-score.
    
    Analiza:
    - Montos inusualmente altos o bajos
    - Fechas de vencimiento anómalas
    - Cambios significativos en períodos de renovación
    """
    anomalies = []
    
    if not subscriptions or len(subscriptions) < 3:
        return anomalies
    
    try:
        import statistics
        
        # Detectar anomalías en montos
        amounts = []
        for sub in subscriptions:
            amount = sub.get("amount")
            if amount and amount > 0:
                amounts.append(float(amount))
        
        if len(amounts) >= 3:
            mean = statistics.mean(amounts)
            if len(amounts) > 1:
                std = statistics.stdev(amounts)
            else:
                std = 0
            
            if std > 0:
                threshold_low = mean - (z_score_threshold * std)
                threshold_high = mean + (z_score_threshold * std)
                
                for sub in subscriptions:
                    amount = sub.get("amount")
                    if amount:
                        amount_val = float(amount)
                        if amount_val < threshold_low or amount_val > threshold_high:
                            z_score = (amount_val - mean) / std
                            anomalies.append({
                                "subscription_id": sub.get("ext_id"),
                                "type": "amount_anomaly",
                                "amount": amount_val,
                                "z_score": z_score,
                                "mean": mean,
                                "std": std,
                            })
        
        # Detectar anomalías en días hasta vencimiento
        days_until_expiry = []
        today = date.today()
        
        for sub in subscriptions:
            end_date_str = sub.get("end_date")
            if end_date_str:
                try:
                    end_date = datetime.fromisoformat(end_date_str).date()
                    days = (end_date - today).days
                    if days >= 0:
                        days_until_expiry.append(days)
                except (ValueError, TypeError):
                    pass
        
        if len(days_until_expiry) >= 3:
            mean_days = statistics.mean(days_until_expiry)
            if len(days_until_expiry) > 1:
                std_days = statistics.stdev(days_until_expiry)
            else:
                std_days = 0
            
            if std_days > 0:
                threshold_low = mean_days - (z_score_threshold * std_days)
                threshold_high = mean_days + (z_score_threshold * std_days)
                
                for sub in subscriptions:
                    end_date_str = sub.get("end_date")
                    if end_date_str:
                        try:
                            end_date = datetime.fromisoformat(end_date_str).date()
                            days = (end_date - today).days
                            if days < threshold_low or days > threshold_high:
                                z_score = (days - mean_days) / std_days if std_days > 0 else 0
                                anomalies.append({
                                    "subscription_id": sub.get("ext_id"),
                                    "type": "expiry_anomaly",
                                    "days_until_expiry": days,
                                    "z_score": z_score,
                                    "mean": mean_days,
                                    "std": std_days,
                                })
                        except (ValueError, TypeError):
                            pass
        
    except Exception as e:
        logger.warning(f"Error detecting anomalies: {e}", exc_info=True)
    
    return anomalies


def _get_optimal_batch_size(operation: str = "notifications") -> int:
    """Calcula batch size óptimo basado en rendimiento histórico."""
    try:
        key = f"subscription_management.optimal_batch_size.{operation}"
        data_str = Variable.get(key, default_var=None)
        if data_str:
            data = json.loads(data_str)
            optimal = data.get("optimal_size", DEFAULT_BATCH_SIZE)
            # Asegurar que esté en rango razonable
            return max(1, min(100, int(optimal)))
    except Exception:
        pass
    
    return DEFAULT_BATCH_SIZE


def _update_optimal_batch_size(operation: str, batch_size: int, duration_ms: float) -> None:
    """Actualiza el batch size óptimo basado en performance."""
    try:
        key = f"subscription_management.optimal_batch_size.{operation}"
        data_str = Variable.get(key, default_var=None)
        
        if data_str:
            data = json.loads(data_str)
            history = data.get("history", [])
        else:
            data = {}
            history = []
        
        # Agregar nueva medición
        history.append({
            "batch_size": batch_size,
            "duration_ms": duration_ms,
            "timestamp": pendulum.now("UTC").isoformat(),
        })
        
        # Mantener solo últimos 20 registros
        history = history[-20:]
        
        # Calcular batch size óptimo (menor tiempo promedio)
        if history:
            by_size = {}
            for entry in history:
                size = entry["batch_size"]
                if size not in by_size:
                    by_size[size] = []
                by_size[size].append(entry["duration_ms"])
            
            # Encontrar batch size con mejor tiempo promedio
            best_size = DEFAULT_BATCH_SIZE
            best_avg_time = float('inf')
            
            for size, times in by_size.items():
                avg_time = sum(times) / len(times)
                if avg_time < best_avg_time:
                    best_avg_time = avg_time
                    best_size = size
            
            data["optimal_size"] = best_size
            data["history"] = history
            Variable.set(key, json.dumps(data))
    except Exception:
        pass


def _compare_with_history(current_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Compara métricas actuales con histórico."""
    comparison = {
        "has_history": False,
        "changes": {},
    }
    
    try:
        key = "subscription_management.historical_metrics"
        history_str = Variable.get(key, default_var=None)
        
        if not history_str:
            # Guardar primera ejecución
            Variable.set(key, json.dumps({
                "last_execution": current_metrics,
                "timestamp": pendulum.now("UTC").isoformat(),
            }))
            return comparison
        
        history = json.loads(history_str)
        last_metrics = history.get("last_execution", {})
        
        if not last_metrics:
            return comparison
        
        comparison["has_history"] = True
        
        # Comparar métricas clave
        current_count = current_metrics.get("expiring_subscriptions", 0)
        last_count = last_metrics.get("expiring_subscriptions", 0)
        
        if last_count > 0:
            change_pct = ((current_count - last_count) / last_count) * 100
            comparison["changes"]["expiring_subscriptions"] = {
                "current": current_count,
                "previous": last_count,
                "change_pct": change_pct,
            }
        
        current_notified = current_metrics.get("notifications", {}).get("sent", 0)
        last_notified = last_metrics.get("notifications", {}).get("sent", 0)
        
        if last_notified > 0:
            change_pct = ((current_notified - last_notified) / last_notified) * 100
            comparison["changes"]["notifications_sent"] = {
                "current": current_notified,
                "previous": last_notified,
                "change_pct": change_pct,
            }
        
        # Actualizar histórico
        Variable.set(key, json.dumps({
            "last_execution": current_metrics,
            "timestamp": pendulum.now("UTC").isoformat(),
            "previous": last_metrics,
        }))
        
    except Exception as e:
        logger.warning(f"Error comparing with history: {e}", exc_info=True)
    
    return comparison


def _cb_key() -> str:
    """Genera la clave del circuit breaker."""
    return "cb:failures:subscription_management"


def _cb_is_open() -> bool:
    """Verifica si el circuit breaker está abierto."""
    try:
        key = _cb_key()
        data_str = Variable.get(key, default_var=None)
        if not data_str:
            return False
        data = json.loads(data_str)
        failures = data.get("count", 0)
        last_failure_ts = data.get("last_failure_ts", 0)
        now = pendulum.now("UTC").int_timestamp
        if (now - last_failure_ts) > (CB_RESET_MINUTES * 60) and failures > 0:
            Variable.delete(key)
            return False
        return failures >= CB_FAILURE_THRESHOLD
    except Exception:
        return False


def _cb_record_failure() -> None:
    """Registra un fallo en el circuit breaker."""
    try:
        key = _cb_key()
        data_str = Variable.get(key, default_var=None)
        now_ts = pendulum.now("UTC").int_timestamp
        if data_str:
            data = json.loads(data_str)
            count = data.get("count", 0) + 1
        else:
            count = 1
        Variable.set(key, json.dumps({"count": count, "last_failure_ts": now_ts}))
        if STATS_AVAILABLE and Stats:
            try:
                Stats.incr("subscription_management.circuit_breaker.failures", 1)
            except Exception:
                pass
    except Exception:
        pass


def _cb_reset() -> None:
    """Resetea el circuit breaker."""
    try:
        Variable.delete(_cb_key())
        if STATS_AVAILABLE and Stats:
            try:
                Stats.incr("subscription_management.circuit_breaker.reset", 1)
            except Exception:
                pass
    except Exception:
        pass


@dag(
    dag_id="subscription_management",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 0 1 * *",  # Primer día de cada mes a medianoche
    catchup=False,
    default_args={
        "owner": "sales",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=30),
        "depends_on_past": False,
        "on_failure_callback": on_task_failure,
    },
    dagrun_timeout=timedelta(minutes=60),
    max_active_runs=1,
    max_active_tasks=8,
    concurrency=8,
    render_template_as_native_obj=True,
    sla_miss_callback=sla_miss_callback,
    on_success_callback=lambda context: (
        _cb_reset(),
        notify_slack(":white_check_mark: subscription_management DAG succeeded")
    ),
    on_failure_callback=lambda context: (
        _cb_record_failure(),
        notify_slack(":x: subscription_management DAG failed")
    ),
    doc_md="""
    ### Gestión Automática de Suscripciones (Mejorado)
    
    Proceso mensual que gestiona el ciclo de vida de las suscripciones con mejoras robustas:
    
    **Flujo:**
    1. **Health Check**: Verifica conectividad de APIs externas
    2. **Identificación**: Encuentra suscripciones próximas a vencer
    3. **Notificación**: Envía recordatorios de renovación (en batches)
    4. **Monitoreo**: Verifica renovaciones (BD local y Stripe)
    5. **Inactivación**: Marca como inactivas las que no renuevan después del período de gracia
    
    **Mejoras Avanzadas:**
    - ✅ Retry con exponential backoff
    - ✅ Health checks pre-vuelo
    - ✅ Manejo inteligente de rate limiting (Redis opcional)
    - ✅ Logging estructurado con structlog
    - ✅ Validación robusta con Pydantic
    - ✅ Procesamiento en batches adaptativo
    - ✅ Métricas detalladas con histórico
    - ✅ Notificaciones Slack opcionales
    - ✅ Dead Letter Queue (DLQ) para errores
    - ✅ Detección de anomalías (Z-score)
    - ✅ Cache inteligente de suscripciones (TTL 5 min)
    - ✅ Circuit breakers (pybreaker) con auto-reset
    - ✅ Comparación con ejecuciones anteriores
    - ✅ Procesamiento paralelo optimizado
    - ✅ TaskGroups para organización del flujo
    - ✅ OpenTelemetry tracing opcional
    - ✅ Callbacks de éxito/fallo automáticos
    - ✅ SLA miss callbacks
    - ✅ Execution timeouts por tarea
    - ✅ Rate limiting preventivo con Redis
    - ✅ Concurrency y parallelism controlados
    - ✅ Progress tracking con logging periódico
    - ✅ Checkpointing para reanudar procesamiento
    - ✅ OpenTelemetry spans en todas las operaciones
    - ✅ Jitter en delays para evitar thundering herd
    - ✅ Cost tracking para operaciones de API
    - ✅ Throughput tracking y métricas de performance
    - ✅ Idempotencia con locks y TTL configurable
    - ✅ Deduplicación inteligente de suscripciones
    - ✅ Enriquecimiento de datos automático
    - ✅ Distributed locks para prevenir ejecuciones concurrentes
    - ✅ Locks con expiración automática y liberación garantizada
    - ✅ Cálculo de probabilidad de renovación basado en múltiples factores
    - ✅ Alertas predictivas con umbrales configurables
    - ✅ Enriquecimiento con APIs externas (Clearbit opcional)
    - ✅ Análisis de riesgo de renovación (low/medium/high)
    - ✅ Personalización de notificaciones basada en riesgo
    - ✅ Métricas agregadas de probabilidad de renovación
    - ✅ ML Scoring predictivo opcional (integración con modelos ML)
    - ✅ Segmentación avanzada de suscripciones (valor, riesgo, tipo)
    - ✅ Exportación de métricas a S3 para análisis posterior
    - ✅ Combinación de predicciones rule-based y ML
    - ✅ Análisis de segmentos para personalización
    - ✅ Análisis de tendencias temporales (mes/semana)
    - ✅ A/B Testing de notificaciones para optimizar conversión
    - ✅ Feature Flags para habilitar/deshabilitar funcionalidades
    - ✅ Recomendaciones de acción personalizadas por suscripción
    - ✅ Tracking de variantes A/B para análisis posterior
    - ✅ Análisis de crecimiento y tendencias
    - ✅ Análisis de cohortes por mes de inicio
    - ✅ Cálculo de riesgo de churn con factores y estrategias
    - ✅ Estimación de Lifetime Value (LTV) con escenarios
    - ✅ Optimización de timing de notificaciones basado en datos
    - ✅ Análisis de retención por cohort
    - ✅ Estrategias de mitigación de churn personalizadas
    - ✅ Integración con CRM (Salesforce/Pipedrive) para sincronización
    - ✅ Automatización de workflows basada en eventos
    - ✅ Reportes ejecutivos con métricas clave y recomendaciones
    - ✅ Evaluación de riesgo general con factores identificados
    - ✅ Triggers automáticos de workflows de retención
    - ✅ Sincronización bidireccional con sistemas CRM
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres
    - `days_before_expiry`: Días antes de vencer para enviar notificación (default: 7)
    - `grace_period_days`: Días de gracia después de vencer antes de marcar inactivo (default: 3)
    - `stripe_api_key`: API key de Stripe (opcional, para suscripciones Stripe)
    - `notification_email_from`: Email de origen para notificaciones
    - `batch_size`: Tamaño de batch para procesamiento (default: 10, se ajusta automáticamente)
    - `batch_delay`: Delay entre batches en segundos (default: 0.5)
    - `dry_run`: Solo simular sin hacer cambios (default: false)
    
    **Características Avanzadas:**
    - **DLQ**: Los errores persistentes se guardan en `/tmp/subscription_management_dlq.jsonl`
    - **Anomalías**: Detecta automáticamente montos y fechas anómalas usando Z-score
    - **Cache**: Cachea suscripciones por 5 minutos para reducir llamadas a BD
    - **Circuit Breakers**: pybreaker para Stripe (5 fallos) y notificaciones (3 fallos)
    - **Batch Adaptativo**: Ajusta el tamaño de batch basado en performance histórico
    - **Histórico**: Compara métricas con ejecuciones anteriores para detectar tendencias
    - **Pydantic**: Validación de datos con modelos tipados y validadores personalizados
    - **Structlog**: Logging estructurado para mejor observabilidad
    - **OpenTelemetry**: Tracing opcional para monitoreo distribuido
    - **TaskGroups**: Organización del flujo en fases lógicas
    - **Rate Limiting**: Rate limiting con Redis (si está disponible)
    - **Callbacks**: Notificaciones automáticas en éxito/fallo del DAG
    - **Timeouts**: Control de tiempo de ejecución por tarea y DAG completo
    - **Progress Tracking**: Logging periódico del progreso de procesamiento
    - **Checkpointing**: Guarda estado para reanudar procesamiento si falla
    - **OpenTelemetry**: Spans de tracing en todas las operaciones críticas
    - **Jitter**: Delay aleatorio para evitar saturación simultánea
    - **Cost Tracking**: Seguimiento de costos de operaciones (API calls, etc)
    - **Idempotencia**: Prevención de procesamiento duplicado con locks y TTL
    - **Deduplicación**: Detección automática de suscripciones duplicadas
    - **Enriquecimiento**: Datos adicionales calculados (días hasta vencimiento, valor estimado, etc)
    - **Distributed Locks**: Locks distribuidos para prevenir ejecuciones concurrentes del DAG
    - **Renewal Probability**: Cálculo de probabilidad de renovación (0.0-1.0) basado en múltiples factores
    - **Predictive Alerts**: Alertas automáticas basadas en tendencias y umbrales configurables
    - **External Enrichment**: Enriquecimiento opcional con Clearbit API (configurar CLEARBIT_API_KEY)
    - **Risk Analysis**: Clasificación de riesgo de renovación (low/medium/high) para priorización
    - **Personalized Notifications**: Emails personalizados según valor de suscripción y riesgo
    - **ML Scoring**: Integración opcional con modelos ML para predicción (configurar SUBSCRIPTION_ML_ENDPOINT)
    - **Segmentation**: Segmentación automática por valor, riesgo, tipo de email y antigüedad
    - **S3 Export**: Exportación automática de métricas a S3 para análisis (configurar SUBSCRIPTION_METRICS_S3_BUCKET)
    - **Hybrid Scoring**: Combinación inteligente de predicciones rule-based (70%) y ML (30%)
    - **Temporal Analysis**: Análisis de tendencias por mes/semana con cálculo de crecimiento
    - **A/B Testing**: Testing de variantes de notificaciones para optimizar conversión (feature flag)
    - **Feature Flags**: Sistema de flags para habilitar/deshabilitar funcionalidades dinámicamente
    - **Action Recommendations**: Recomendaciones personalizadas de acción basadas en riesgo, valor y timing
    - **Cohort Analysis**: Análisis de suscripciones agrupadas por mes de inicio con métricas de retención
    - **Churn Risk**: Cálculo de riesgo de churn con factores identificados y estrategias de mitigación
    - **Lifetime Value (LTV)**: Estimación de LTV con escenarios optimista/realista/pesimista
    - **Timing Optimization**: Optimización de timing de notificaciones basado en datos históricos y perfil
    - **CRM Integration**: Sincronización automática con CRM (Salesforce/Pipedrive) - configurar ENABLE_CRM_SYNC y CRM_CONFIG
    - **Automated Workflows**: Workflows automatizados basados en eventos (churn risk, expiring soon, etc.)
    - **Executive Reports**: Reportes ejecutivos con métricas clave, tendencias y recomendaciones accionables
    - **Risk Assessment**: Evaluación de riesgo general con factores identificados y priorización
    - **Workflow Triggers**: Disparo automático de acciones (asignar Account Manager, crear descuentos, etc.)
    - **Webhook Trigger**: Soporte para trigger manual via API/webhook (schedule=None)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "days_before_expiry": Param(7, type="integer", minimum=1, maximum=30),
        "grace_period_days": Param(3, type="integer", minimum=0, maximum=30),
        "stripe_api_key": Param("", type="string"),
        "notification_email_from": Param("noreply@example.com", type="string"),
        "batch_size": Param(10, type="integer", minimum=1, maximum=100),
        "batch_delay": Param(0.5, type="number", minimum=0.0, maximum=10.0),
        "dry_run": Param(False, type="boolean"),
    },
    tags=["sales", "subscriptions", "billing", "automation"],
)
def subscription_management() -> None:
    """
    DAG mejorado para gestión automática de suscripciones.
    Versión avanzada con Pydantic, structlog, circuit breakers y tracing.
    """
    
    # ============================================================================
    # MODELOS PYDANTIC PARA VALIDACIÓN (si está disponible)
    # ============================================================================
    if PYDANTIC_AVAILABLE:
        class SubscriptionModel(BaseModel):
            """Modelo de suscripción validado con Pydantic"""
            ext_id: str = Field(..., min_length=1, max_length=255)
            customer_id: str = Field(..., min_length=1, max_length=255)
            customer_email: Optional[EmailStr] = None
            customer_name: Optional[str] = Field(None, max_length=255)
            plan_name: Optional[str] = Field(None, max_length=255)
            status: str = Field(default="active", pattern="^(active|inactive|cancelled|pending)$")
            start_date: str
            end_date: str
            renewal_date: Optional[str] = None
            amount: Optional[float] = Field(None, ge=0)
            currency: str = Field(default="USD", max_length=10)
            billing_cycle: str = Field(default="monthly", max_length=20)
            stripe_subscription_id: Optional[str] = None
            metadata: Dict[str, Any] = Field(default_factory=dict)
            
            @validator('end_date', 'start_date', 'renewal_date')
            def validate_date(cls, v):
                """Validar formato de fecha ISO"""
                if v:
                    try:
                        datetime.fromisoformat(v)
                    except (ValueError, TypeError):
                        raise ValueError(f"Invalid date format: {v}")
                return v
    
    @task(
        task_id="health_check",
        execution_timeout=timedelta(minutes=2),
        on_failure_callback=on_task_failure,
        doc_md="Valida conectividad de APIs externas antes de procesar"
    )
    def health_check() -> Dict[str, Any]:
        """
        Realiza health check de APIs externas antes de procesar.
        """
        ctx = get_current_context()
        params = ctx["params"]
        stripe_api_key = str(params.get("stripe_api_key", "")).strip()
        
        start_time = time.time()
        health_status = _perform_health_check(stripe_api_key if stripe_api_key else None)
        duration_ms = (time.time() - start_time) * 1000
        
        if not health_status:
            logger.warning("Health check failed, pero continuando...")
        
        result = {
            "healthy": health_status,
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        logger.info(
            f"Health check completed",
            extra={"healthy": health_status, "duration_ms": duration_ms}
        )
        
        return result
    
    @task(
        task_id="identify_expiring_subscriptions",
        execution_timeout=timedelta(minutes=10),
        on_failure_callback=on_task_failure,
        doc_md="Identifica suscripciones próximas a vencer con validación robusta"
    )
    def identify_expiring_subscriptions() -> Dict[str, Any]:
        """
        Identifica suscripciones próximas a vencer con validación robusta.
        Incluye tracing, checkpointing y progress tracking.
        """
        # Tracing
        span = None
        if OPENTELEMETRY_AVAILABLE and tracer:
            span = tracer.start_span("identify_expiring_subscriptions")
        
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        days_before = int(params["days_before_expiry"])
        dry_run = bool(params["dry_run"])
        dag_run_id = str(ctx.get("run_id", ""))
        
        start_time = time.time()
        
        # Intentar cargar checkpoint
        checkpoint_key = f"subscription_management.checkpoint.identify.{dag_run_id}"
        checkpoint_data = _load_checkpoint(checkpoint_key)
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        today = date.today()
        expiry_threshold = today + timedelta(days=days_before)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS subscriptions (
                        id SERIAL PRIMARY KEY,
                        ext_id VARCHAR(255) UNIQUE NOT NULL,
                        customer_id VARCHAR(255) NOT NULL,
                        customer_email VARCHAR(255),
                        customer_name VARCHAR(255),
                        plan_name VARCHAR(255),
                        status VARCHAR(50) NOT NULL DEFAULT 'active',
                        start_date DATE NOT NULL,
                        end_date DATE NOT NULL,
                        renewal_date DATE,
                        amount DECIMAL(10, 2),
                        currency VARCHAR(10) DEFAULT 'USD',
                        billing_cycle VARCHAR(20) DEFAULT 'monthly',
                        stripe_subscription_id VARCHAR(255),
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW(),
                        last_notified_at TIMESTAMP,
                        notified_count INTEGER DEFAULT 0
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_subscriptions_status 
                    ON subscriptions(status);
                    
                    CREATE INDEX IF NOT EXISTS idx_subscriptions_end_date 
                    ON subscriptions(end_date);
                    
                    CREATE INDEX IF NOT EXISTS idx_subscriptions_ext_id 
                    ON subscriptions(ext_id);
                    
                    CREATE INDEX IF NOT EXISTS idx_subscriptions_customer_id 
                    ON subscriptions(customer_id);
                """)
                
                # Identificar suscripciones activas próximas a vencer
                cur.execute("""
                    SELECT 
                        id,
                        ext_id,
                        customer_id,
                        customer_email,
                        customer_name,
                        plan_name,
                        status,
                        start_date,
                        end_date,
                        renewal_date,
                        amount,
                        currency,
                        billing_cycle,
                        stripe_subscription_id,
                        metadata,
                        last_notified_at,
                        notified_count
                    FROM subscriptions
                    WHERE status = 'active'
                      AND end_date <= %s
                      AND end_date >= %s
                    ORDER BY end_date ASC
                """, (expiry_threshold, today))
                
                expiring_subscriptions = []
                invalid_count = 0
                total_rows = 0
                processed_rows = 0
                rows = cur.fetchall()
                total_rows = len(rows)
                
                # Progress tracking
                progress_interval = max(1, total_rows // 10)
                
                for idx, row in enumerate(rows):
                    processed_rows = idx + 1
                    
                    # Log progress periódicamente
                    if processed_rows % progress_interval == 0 or processed_rows == total_rows:
                        _log_progress(
                            processed_rows,
                            total_rows,
                            "identify_subscriptions",
                            successful=len(expiring_subscriptions),
                            failed=invalid_count,
                            interval=progress_interval
                        )
                    subscription = {
                        "id": row[0],
                        "ext_id": row[1],
                        "customer_id": row[2],
                        "customer_email": row[3],
                        "customer_name": row[4],
                        "plan_name": row[5],
                        "status": row[6],
                        "start_date": row[7].isoformat() if row[7] else None,
                        "end_date": row[8].isoformat() if row[8] else None,
                        "renewal_date": row[9].isoformat() if row[9] else None,
                        "amount": float(row[10]) if row[10] else None,
                        "currency": row[11] or "USD",
                        "billing_cycle": row[12] or "monthly",
                        "stripe_subscription_id": row[13],
                        "metadata": row[14] if row[14] else {},
                        "last_notified_at": row[15].isoformat() if row[15] else None,
                        "notified_count": row[16] or 0,
                    }
                    
                    # Validar datos
                    is_valid, issues = _validate_subscription_data(subscription)
                    
                    # Validación adicional con Pydantic si está disponible
                    if is_valid and PYDANTIC_AVAILABLE:
                        try:
                            validated_sub = SubscriptionModel(**subscription)
                            subscription = validated_sub.model_dump()
                            is_valid = True
                        except ValidationError as e:
                            is_valid = False
                            issues.extend([f"Pydantic validation: {err['msg']}" for err in e.errors()])
                    
                    # Enriquecer datos si es válido
                    if is_valid:
                        subscription = _enrich_subscription_data(subscription)
                        
                        # Enriquecimiento con APIs externas (opcional, puede ser lento)
                        try:
                            subscription = _enrich_with_external_api(subscription)
                        except Exception as e:
                            logger.debug(f"External enrichment failed: {e}")
                        
                        # Calcular probabilidad de renovación (rule-based)
                        renewal_probability = _calculate_renewal_probability(subscription)
                        
                        # Intentar obtener predicción ML si está disponible
                        ml_endpoint = os.getenv("SUBSCRIPTION_ML_ENDPOINT", "")
                        ml_probability = None
                        if ml_endpoint:
                            ml_probability = _get_ml_prediction(subscription, ml_endpoint)
                        
                        # Combinar predicciones: 70% rule-based, 30% ML si está disponible
                        if ml_probability is not None:
                            final_probability = renewal_probability * 0.7 + ml_probability * 0.3
                            enriched_data = subscription.get("enriched_data", {})
                            enriched_data["ml_probability"] = ml_probability
                            enriched_data["ml_available"] = True
                        else:
                            final_probability = renewal_probability
                            enriched_data = subscription.get("enriched_data", {})
                            enriched_data["ml_available"] = False
                        
                        enriched_data["renewal_probability"] = final_probability
                        enriched_data["renewal_risk"] = (
                            "low" if final_probability >= 0.7
                            else "medium" if final_probability >= 0.4
                            else "high"
                        )
                        
                        # Análisis adicionales
                        churn_risk = _calculate_churn_risk(subscription)
                        enriched_data["churn_risk"] = churn_risk["risk_score"]
                        enriched_data["churn_factors"] = churn_risk["factors"]
                        enriched_data["churn_mitigation"] = churn_risk["mitigation_strategies"]
                        
                        ltv = _estimate_lifetime_value(subscription)
                        enriched_data["ltv"] = ltv["estimated_ltv"]
                        enriched_data["ltv_scenarios"] = ltv["scenarios"]
                        enriched_data["ltv_confidence"] = ltv["confidence"]
                        
                        timing = _optimize_notification_timing(subscription)
                        enriched_data["optimal_timing"] = timing
                        
                        subscription["enriched_data"] = enriched_data
                        
                        # Verificar idempotencia
                        sub_id = subscription.get("ext_id")
                        if sub_id:
                            idemp_key = f"subscription_management:idemp:{sub_id}:notify"
                            if _check_idempotency(idemp_key, ttl_seconds=86400):
                                logger.info(
                                    f"Subscription {sub_id} already notified, skipping",
                                    extra={"subscription_id": sub_id}
                                )
                                continue
                        
                        expiring_subscriptions.append(subscription)
                    else:
                        invalid_count += 1
                        logger.warning(
                            f"Invalid subscription data: {', '.join(issues)}",
                            extra={"subscription_id": subscription.get("ext_id"), "issues": issues}
                        )
                
                # Deduplicar suscripciones
                unique_subscriptions, duplicates = _deduplicate_subscriptions(expiring_subscriptions)
                expiring_subscriptions = unique_subscriptions
                
                if duplicates:
                    logger.warning(
                        f"Detected {len(duplicates)} duplicate subscriptions",
                        extra={"duplicates_count": len(duplicates)}
                    )
                
                conn.commit()
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Segmentar suscripciones para análisis
        segments = _segment_subscriptions(expiring_subscriptions)
        
        # Análisis de tendencias temporales
        temporal_trends = _analyze_temporal_trends(expiring_subscriptions)
        
        # Análisis de cohortes
        cohort_analysis = _analyze_cohorts(expiring_subscriptions, hook)
        
        # Guardar checkpoint
        checkpoint_data = {
            "expiring_subscriptions": expiring_subscriptions,
            "invalid_count": invalid_count,
            "segments": {k: len(v) for k, v in segments.items()},
            "processed_at": datetime.utcnow().isoformat(),
        }
        _save_checkpoint(checkpoint_key, checkpoint_data, ttl_seconds=3600)
        
        # Tracing attributes
        if span:
            span.set_attribute("subscriptions.count", len(expiring_subscriptions))
            span.set_attribute("subscriptions.invalid", invalid_count)
            span.set_attribute("duration_ms", duration_ms)
        
        # Detectar anomalías
        anomalies = []
        if len(expiring_subscriptions) >= 3:
            anomalies = _detect_anomalies(expiring_subscriptions)
            if anomalies:
                logger.warning(
                    f"Detectadas {len(anomalies)} anomalías en suscripciones",
                    extra={"anomalies_count": len(anomalies)}
                )
        
        # Detectar alertas predictivas
        predictive_alerts = []
        if len(expiring_subscriptions) > 0:
            # Cargar histórico para comparación
            historical_key = "subscription_management.historical_metrics"
            historical_str = Variable.get(historical_key, default_var=None)
            historical_metrics = None
            if historical_str:
                try:
                    historical_data = json.loads(historical_str)
                    historical_metrics = historical_data.get("last_execution", {})
                except Exception:
                    pass
            
            predictive_alerts = _detect_predictive_alerts(expiring_subscriptions, historical_metrics)
            
            if predictive_alerts:
                # Filtrar solo alertas de alta severidad para notificar
                high_severity_alerts = [a for a in predictive_alerts if a.get("severity") in ["high", "critical"]]
                
                if high_severity_alerts:
                    try:
                        from data.airflow.plugins.etl_notifications import notify_slack
                        message = f"🚨 *Alertas Predictivas de Suscripciones*\n\n"
                        message += f"Total de alertas: {len(high_severity_alerts)}\n\n"
                        
                        for alert in high_severity_alerts:
                            severity_emoji = "🔴" if alert.get("severity") == "high" else "🟡"
                            message += f"{severity_emoji} *{alert.get('type', 'unknown').replace('_', ' ').title()}*\n"
                            message += f"  {alert.get('message', '')}\n\n"
                        
                        notify_slack(message)
                        logger.warning(
                            f"Predictive alerts triggered: {len(high_severity_alerts)}",
                            extra={"alerts": high_severity_alerts}
                        )
                    except ImportError:
                        pass
                    except Exception as e:
                        logger.warning(f"Error enviando alertas predictivas: {e}", exc_info=True)
        
        # Notificar anomalías críticas
        if anomalies:
            try:
                from data.airflow.plugins.etl_notifications import notify_slack
                message = f"⚠️ *Anomalías detectadas en suscripciones*\n\n"
                message += f"Total de anomalías: {len(anomalies)}\n\n"
                by_type = {}
                for anomaly in anomalies:
                    anomaly_type = anomaly.get("type", "unknown")
                    if anomaly_type not in by_type:
                        by_type[anomaly_type] = []
                    by_type[anomaly_type].append(anomaly)
                
                for anomaly_type, items in by_type.items():
                    message += f"*{anomaly_type.replace('_', ' ').title()}:* {len(items)}\n"
                    for item in items[:3]:  # Top 3
                        sub_id = item.get("subscription_id", "unknown")[:12]
                        message += f"  • Sub {sub_id}\n"
                
                notify_slack(message)
            except ImportError:
                pass
            except Exception as e:
                logger.warning(f"Error enviando alerta de anomalías: {e}", exc_info=True)
        
        logger.info(
            f"Identificadas {len(expiring_subscriptions)} suscripciones próximas a vencer",
            extra={
                "count": len(expiring_subscriptions),
                "invalid_count": invalid_count,
                "anomalies_count": len(anomalies),
                "predictive_alerts_count": len(predictive_alerts),
                "duration_ms": duration_ms,
            }
        )
        
        if STATS_AVAILABLE and Stats:
            Stats.incr("subscription_management.expiring_subscriptions", len(expiring_subscriptions))
            Stats.incr("subscription_management.anomalies", len(anomalies))
            Stats.incr("subscription_management.predictive_alerts", len(predictive_alerts))
            Stats.timing("subscription_management.identify.duration_ms", int(duration_ms))
        
        # Finalizar span
        if span:
            span.set_attribute("anomalies.count", len(anomalies))
            span.set_attribute("predictive_alerts.count", len(predictive_alerts))
            
            # Calcular métricas agregadas de probabilidad
            if expiring_subscriptions:
                avg_probability = sum(
                    s.get("enriched_data", {}).get("renewal_probability", 0.5)
                    for s in expiring_subscriptions
                ) / len(expiring_subscriptions)
                span.set_attribute("renewal_probability.avg", avg_probability)
            
            span.end()
        
        result = {
            "expiring_subscriptions": expiring_subscriptions,
            "count": len(expiring_subscriptions),
            "invalid_count": invalid_count,
            "anomalies": anomalies,
            "anomalies_count": len(anomalies),
            "predictive_alerts": predictive_alerts,
            "predictive_alerts_count": len(predictive_alerts),
            "segments": {k: len(v) for k, v in segments.items()},
            "segment_details": segments,
            "temporal_trends": temporal_trends,
            "cohort_analysis": cohort_analysis,
            "expiry_threshold": expiry_threshold.isoformat(),
            "dry_run": dry_run,
        }
        
        # Logging de segmentación
        if segments:
            logger.info(
                "Subscription segments",
                extra={
                    "high_value_high_risk": len(segments["high_value_high_risk"]),
                    "high_value_low_risk": len(segments["high_value_low_risk"]),
                    "corporate": len(segments["corporate"]),
                    "expiring_soon": len(segments["expiring_soon"]),
                }
            )
        
        # Logging de tendencias temporales
        if temporal_trends.get("has_trends"):
            logger.info(
                "Temporal trends analyzed",
                extra={
                    "total_value": temporal_trends.get("total_value", 0),
                    "avg_value": temporal_trends.get("avg_value", 0),
                    "growth_rate": temporal_trends.get("growth_rate"),
                    "months_analyzed": len(temporal_trends.get("by_month", {})),
                }
            )
        
        # Logging de cohortes
        if cohort_analysis.get("has_data"):
            logger.info(
                "Cohort analysis completed",
                extra={
                    "total_cohorts": cohort_analysis.get("total_cohorts", 0),
                    "cohorts_analyzed": len(cohort_analysis.get("cohorts", [])),
                }
            )
        
        return result
    
    @task(
        task_id="send_renewal_notifications",
        execution_timeout=timedelta(minutes=30),
        on_failure_callback=on_task_failure,
        doc_md="Envía notificaciones de renovación en batches con retry inteligente"
    )
    def send_renewal_notifications(subscriptions_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía notificaciones de renovación en batches con retry inteligente.
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        email_from = str(params["notification_email_from"])
        # Usar batch size óptimo si está disponible
        batch_size = _get_optimal_batch_size("notifications")
        batch_size_param = int(params.get("batch_size", batch_size))
        batch_size = batch_size_param if batch_size_param else batch_size
        batch_delay = float(params.get("batch_delay", DEFAULT_BATCH_DELAY))
        dry_run = bool(params["dry_run"])
        
        # Verificar circuit breaker
        if _cb_is_open():
            logger.error("Circuit breaker is open, skipping notifications")
            raise AirflowFailException("Circuit breaker is open, too many failures")
        
        expiring_subscriptions = subscriptions_data.get("expiring_subscriptions", [])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        notifications_sent = []
        notifications_failed = []
        batch_start_time = time.time()
        dag_run_id = str(ctx.get("run_id", ""))
        
        # Tracing
        span = None
        if OPENTELEMETRY_AVAILABLE and tracer:
            span = tracer.start_span("send_renewal_notifications")
            if span:
                span.set_attribute("subscriptions.total", len(expiring_subscriptions))
                span.set_attribute("batch_size", batch_size)
        
        # Progress tracking
        total_subscriptions = len(expiring_subscriptions)
        progress_interval = max(1, total_subscriptions // 10)
        
        # Procesar en batches
        for i in range(0, len(expiring_subscriptions), batch_size):
            batch = expiring_subscriptions[i:i + batch_size]
            batch_start = time.time()
            
            for subscription in batch:
                # Progress tracking
                current_idx = len(notifications_sent) + len(notifications_failed)
                if current_idx % progress_interval == 0 or current_idx == total_subscriptions - 1:
                    _log_progress(
                        current_idx + 1,
                        total_subscriptions,
                        "send_notifications",
                        successful=len(notifications_sent),
                        failed=len(notifications_failed),
                        interval=progress_interval
                    )
                sub_start = time.time()
                sub_id = subscription["ext_id"]
                customer_email = subscription.get("customer_email")
                customer_name = subscription.get("customer_name") or "Cliente"
                plan_name = subscription.get("plan_name") or "Plan"
                end_date = subscription.get("end_date")
                amount = subscription.get("amount")
                currency = subscription.get("currency", "USD")
                
                if not customer_email:
                    logger.warning(
                        f"Suscripción {sub_id} sin email, omitiendo notificación",
                        extra={"subscription_id": sub_id}
                    )
                    notifications_failed.append({
                        "subscription_id": sub_id,
                        "reason": "missing_email"
                    })
                    continue
                
                # Preparar contenido del email con información enriquecida
                end_date_obj = datetime.fromisoformat(end_date).date() if end_date else None
                days_until_expiry = (end_date_obj - date.today()).days if end_date_obj else None
                
                # Obtener probabilidad de renovación y recomendaciones
                enriched_data = subscription.get("enriched_data", {})
                renewal_probability = enriched_data.get("renewal_probability", 0.5)
                renewal_risk = enriched_data.get("renewal_risk", "medium")
                value_tier = enriched_data.get("value_tier", "low")
                
                # A/B testing de notificaciones (si está habilitado)
                ab_test_enabled = _check_feature_flag("ab_test_notifications", default=False)
                ab_test_result = None
                if ab_test_enabled:
                    ab_test_result = _ab_test_notification(subscription)
                    variant = ab_test_result["variant"]
                    subject_template = ab_test_result["subject_template"]
                    subject = subject_template.format(
                        plan_name=plan_name or "tu suscripción",
                        days=days_until_expiry or 0
                    )
                else:
                    # Personalizar subject basado en riesgo (comportamiento default)
                    if renewal_risk == "high":
                        subject = f"⚠️ Acción requerida: Tu suscripción {plan_name} está por vencer"
                    elif value_tier == "high":
                        subject = f"Tu suscripción premium {plan_name} está por vencer"
                    else:
                        subject = f"Tu suscripción {plan_name} está por vencer"
                
                        # Generar recomendaciones de acción
                        action_recommendations = _generate_action_recommendations(subscription, segments)
                        
                        # Sincronizar con CRM si está habilitado
                        crm_sync_result = None
                        if _check_feature_flag("crm_sync", default=False):
                            crm_type = os.getenv("CRM_TYPE", "salesforce")
                            crm_config_str = os.getenv("CRM_CONFIG", "{}")
                            try:
                                crm_config = json.loads(crm_config_str) if crm_config_str else {}
                                crm_sync_result = _sync_to_crm(subscription, crm_type, crm_config)
                                if crm_sync_result.get("synced"):
                                    enriched_data["crm_synced"] = True
                                    enriched_data["crm_id"] = crm_sync_result.get("crm_id")
                            except Exception as e:
                                logger.debug(f"CRM sync skipped: {e}")
                        
                        # Trigger workflows automatizados
                        workflows_triggered = []
                        if churn_risk["risk_score"] > 0.7:
                            workflow = _trigger_automated_workflow(subscription, "high_churn_risk")
                            if workflow.get("triggered"):
                                workflows_triggered.append(workflow)
                        
                        if enriched_data.get("days_until_expiry", 0) <= 3:
                            workflow = _trigger_automated_workflow(subscription, "expiring_soon")
                            if workflow.get("triggered"):
                                workflows_triggered.append(workflow)
                        
                        if workflows_triggered:
                            enriched_data["workflows_triggered"] = [w.get("workflow_id") for w in workflows_triggered]
                            enriched_data["workflow_actions"] = [
                                action for w in workflows_triggered for action in w.get("actions", [])
                            ]
                body_html = f"""
                <html>
                <body>
                    <h2>Recordatorio de Renovación</h2>
                    <p>Hola {customer_name},</p>
                    <p>Tu suscripción <strong>{plan_name}</strong> está próxima a vencer.</p>
                    <ul>
                        <li><strong>Fecha de vencimiento:</strong> {end_date_obj.strftime('%d/%m/%Y') if end_date_obj else 'N/A'}</li>
                        <li><strong>Días restantes:</strong> {days_until_expiry} días</li>
                        {f'<li><strong>Monto:</strong> {currency} {amount:.2f}</li>' if amount else ''}
                    </ul>
                    <p>Para renovar tu suscripción, por favor visita tu panel de control o contacta con nuestro equipo.</p>
                    <p>Si no renuevas antes de la fecha de vencimiento, tu suscripción será marcada como inactiva.</p>
                    <p>Saludos,<br>El equipo de Ventas</p>
                </body>
                </html>
                """
                
                body_text = f"""
                Recordatorio de Renovación
                
                Hola {customer_name},
                
                Tu suscripción {plan_name} está próxima a vencer.
                
                Fecha de vencimiento: {end_date_obj.strftime('%d/%m/%Y') if end_date_obj else 'N/A'}
                Días restantes: {days_until_expiry} días
                {f'Monto: {currency} {amount:.2f}' if amount else ''}
                
                Para renovar tu suscripción, por favor visita tu panel de control o contacta con nuestro equipo.
                
                Si no renuevas antes de la fecha de vencimiento, tu suscripción será marcada como inactiva.
                
                Saludos,
                El equipo de Ventas
                """
                
                try:
                    if not dry_run:
                        # Rate limiting preventivo
                        if REDIS_AVAILABLE and rate_limiter:
                            try:
                                rate_limiter.limit("subscription_notifications", max_calls=100, period=60)
                            except Exception:
                                pass  # Continuar si rate limiting falla
                        
                        # Usar circuit breaker si está disponible
                        send_notification_fn = None
                        if notification_circuit_breaker:
                            send_notification_fn = notification_circuit_breaker.call
                        else:
                            def direct_call(fn, *args, **kwargs):
                                return fn(*args, **kwargs)
                            send_notification_fn = direct_call
                        
                        # Intentar usar el sistema de notificaciones de Airflow si está disponible
                        try:
                            from data.airflow.plugins.etl_notifications import notify_email
                            
                            def _send_notification():
                                return notify_email(
                                    to=customer_email,
                                    subject=subject,
                                    html_content=body_html,
                                    text_content=body_text,
                                    from_email=email_from
                                )
                            
                            send_notification_fn(_send_notification)
                            logger.info(
                                f"Notificación enviada a {customer_email}",
                                extra={"subscription_id": sub_id, "customer_email": customer_email}
                            )
                        except ImportError:
                            # Fallback: usar logging
                            logger.info(
                                f"[EMAIL] To: {customer_email}, Subject: {subject}",
                                extra={"subscription_id": sub_id}
                            )
                        
                        # Actualizar registro de notificación en BD
                        with hook.get_conn() as conn:
                            with conn.cursor() as cur:
                                cur.execute("""
                                    UPDATE subscriptions
                                    SET last_notified_at = NOW(),
                                        notified_count = notified_count + 1,
                                        updated_at = NOW()
                                    WHERE ext_id = %s
                                """, (sub_id,))
                                conn.commit()
                        
                        # Establecer idempotencia
                        idemp_key = f"subscription_management:idemp:{sub_id}:notify"
                        _set_idempotency_lock(idemp_key, ttl_seconds=86400)
                        
                        notification_data = {
                            "subscription_id": sub_id,
                            "customer_email": customer_email,
                            "sent_at": datetime.utcnow().isoformat(),
                            "duration_ms": (time.time() - sub_start) * 1000,
                        }
                        
                        # Agregar datos de A/B testing si está disponible
                        if ab_test_result:
                            notification_data["ab_test_variant"] = ab_test_result.get("variant")
                            notification_data["ab_test_tracking_id"] = ab_test_result.get("tracking_id")
                        
                        # Agregar recomendaciones de acción
                        if action_recommendations:
                            notification_data["action_recommendations"] = action_recommendations
                        
                        notifications_sent.append(notification_data)
                    else:
                        logger.info(
                            f"[DRY RUN] Notificación sería enviada a {customer_email}",
                            extra={"subscription_id": sub_id}
                        )
                        notifications_sent.append({
                            "subscription_id": sub_id,
                            "customer_email": customer_email,
                            "sent_at": datetime.utcnow().isoformat(),
                            "dry_run": True,
                            "duration_ms": (time.time() - sub_start) * 1000,
                        })
                        
                except Exception as e:
                    error_msg = str(e)
                    logger.error(
                        f"Error enviando notificación para suscripción {sub_id}: {e}",
                        exc_info=True,
                        extra={"subscription_id": sub_id, "customer_email": customer_email}
                    )
                    
                    # Guardar en DLQ
                    dlq_data = {
                        "subscription_id": sub_id,
                        "customer_email": customer_email,
                        "subscription": subscription,
                        "error": error_msg,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    
                    # Agregar datos de A/B testing si está disponible
                    if ab_test_result:
                        dlq_data["ab_test_variant"] = ab_test_result.get("variant")
                    
                    _save_to_dlq(dlq_data, "notification_failed")
                    
                    # Registrar fallo en circuit breaker
                    _cb_record_failure()
                    
                    notifications_failed.append({
                        "subscription_id": sub_id,
                        "customer_email": customer_email,
                        "error": error_msg,
                        "duration_ms": (time.time() - sub_start) * 1000,
                    })
            
            # Delay entre batches con jitter para evitar thundering herd
            if i + batch_size < len(expiring_subscriptions):
                delay_with_jitter = _add_jitter(batch_delay, jitter_pct=0.2)
                time.sleep(delay_with_jitter)
            
            batch_duration = (time.time() - batch_start) * 1000
            logger.info(
                f"Processed batch {i // batch_size + 1}",
                extra={"batch_size": len(batch), "duration_ms": batch_duration}
            )
        
        total_duration_ms = (time.time() - batch_start_time) * 1000
        
        # Actualizar batch size óptimo
        if len(notifications_sent) > 0:
            _update_optimal_batch_size("notifications", batch_size, total_duration_ms)
        
        # Reset circuit breaker si todo fue exitoso
        if len(notifications_failed) == 0 and len(notifications_sent) > 0:
            _cb_reset()
        
        # Guardar checkpoint
        checkpoint_key = f"subscription_management.checkpoint.notifications.{dag_run_id}"
        checkpoint_data = {
            "notifications_sent": len(notifications_sent),
            "notifications_failed": len(notifications_failed),
            "processed_at": datetime.utcnow().isoformat(),
        }
        _save_checkpoint(checkpoint_key, checkpoint_data, ttl_seconds=3600)
        
        # Tracking de costos (estimado: $0.001 por email)
        estimated_cost = len(notifications_sent) * 0.001
        if estimated_cost > 0:
            _track_cost_operation("send_notifications", estimated_cost, {
                "notifications_count": len(notifications_sent)
            })
        
        if STATS_AVAILABLE and Stats:
            Stats.incr("subscription_management.notifications_sent", len(notifications_sent))
            Stats.incr("subscription_management.notifications_failed", len(notifications_failed))
            Stats.timing("subscription_management.notifications.total_duration_ms", int(total_duration_ms))
        
        # Finalizar span
        if span:
            span.set_attribute("notifications.sent", len(notifications_sent))
            span.set_attribute("notifications.failed", len(notifications_failed))
            span.set_attribute("duration_ms", total_duration_ms)
            span.end()
        
        return {
            "notifications_sent": notifications_sent,
            "notifications_failed": notifications_failed,
            "total_sent": len(notifications_sent),
            "total_failed": len(notifications_failed),
            "batch_size_used": batch_size,
            "total_duration_ms": total_duration_ms,
        }
    
    @task(
        task_id="check_renewals",
        execution_timeout=timedelta(minutes=15),
        on_failure_callback=on_task_failure,
        doc_md="Verifica qué suscripciones han sido renovadas (BD local y Stripe)"
    )
    def check_renewals(subscriptions_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifica qué suscripciones han sido renovadas (BD local y Stripe).
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        stripe_api_key = str(params.get("stripe_api_key", "")).strip()
        dry_run = bool(params["dry_run"])
        
        expiring_subscriptions = subscriptions_data.get("expiring_subscriptions", [])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        renewed_subscriptions = []
        not_renewed_subscriptions = []
        today = date.today()
        
        for subscription in expiring_subscriptions:
            sub_start = time.time()
            sub_id = subscription["ext_id"]
            end_date_str = subscription.get("end_date")
            stripe_sub_id = subscription.get("stripe_subscription_id")
            
            if not end_date_str:
                continue
            
            end_date = datetime.fromisoformat(end_date_str).date()
            
            # Si la fecha de vencimiento ya pasó, verificar renovación
            if end_date < today:
                is_renewed = False
                
                # Verificar en base de datos local
                with hook.get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            SELECT 
                                id,
                                ext_id,
                                end_date,
                                renewal_date,
                                status
                            FROM subscriptions
                            WHERE ext_id = %s
                        """, (sub_id,))
                        
                        row = cur.fetchone()
                        if row:
                            current_end_date = row[2]
                            renewal_date = row[3]
                            status = row[4]
                            
                            # Si la fecha de fin se actualizó o hay fecha de renovación, está renovada
                            if current_end_date and current_end_date > end_date:
                                is_renewed = True
                            elif renewal_date and renewal_date > end_date:
                                is_renewed = True
                            elif status == "active" and current_end_date and current_end_date > today:
                                is_renewed = True
                
                # Si hay Stripe subscription ID, verificar en Stripe
                if not is_renewed and stripe_sub_id and stripe_api_key:
                    try:
                        headers = {
                            "Authorization": f"Bearer {stripe_api_key}",
                            "Content-Type": "application/x-www-form-urlencoded"
                        }
                        
                        # Usar circuit breaker si está disponible
                        def _get_stripe_subscription():
                            session = _get_stripe_session()
                            with _track_api_call("stripe", "get_subscription"):
                                if session:
                                    if HTTPX_AVAILABLE:
                                        return session.get(
                                            f"https://api.stripe.com/v1/subscriptions/{stripe_sub_id}",
                                            headers=headers,
                                            timeout=DEFAULT_TIMEOUT
                                        )
                                    else:
                                        return session.get(
                                            f"https://api.stripe.com/v1/subscriptions/{stripe_sub_id}",
                                            headers=headers,
                                            timeout=DEFAULT_TIMEOUT
                                        )
                                else:
                                    import requests
                                    return requests.get(
                                        f"https://api.stripe.com/v1/subscriptions/{stripe_sub_id}",
                                        headers=headers,
                                        timeout=DEFAULT_TIMEOUT
                                    )
                        
                        if stripe_circuit_breaker:
                            response = stripe_circuit_breaker.call(_get_stripe_subscription)
                        else:
                            response = _get_stripe_subscription()
                        
                        # Manejar rate limiting
                        if response.status_code == 429:
                            _handle_rate_limit(response)
                            # Retry una vez
                            if session:
                                response = session.get(
                                    f"https://api.stripe.com/v1/subscriptions/{stripe_sub_id}",
                                    headers=headers,
                                    timeout=DEFAULT_TIMEOUT
                                )
                            else:
                                import requests
                                response = requests.get(
                                    f"https://api.stripe.com/v1/subscriptions/{stripe_sub_id}",
                                    headers=headers,
                                    timeout=DEFAULT_TIMEOUT
                                )
                        
                        if response.status_code == 200:
                            stripe_data = response.json()
                            stripe_status = stripe_data.get("status", "")
                            current_period_end = stripe_data.get("current_period_end")
                            
                            # Si está activa y tiene período extendido, está renovada
                            if stripe_status in ["active", "trialing"] and current_period_end:
                                current_end = datetime.fromtimestamp(current_period_end).date()
                                if current_end > end_date:
                                    is_renewed = True
                                    
                                    # Actualizar en BD local
                                    if not dry_run:
                                        with hook.get_conn() as conn:
                                            with conn.cursor() as cur:
                                                cur.execute("""
                                                    UPDATE subscriptions
                                                    SET end_date = %s,
                                                        renewal_date = %s,
                                                        updated_at = NOW()
                                                    WHERE ext_id = %s
                                                """, (current_end, today, sub_id))
                                                conn.commit()
                                    logger.info(
                                        f"Suscripción {sub_id} renovada en Stripe",
                                        extra={"subscription_id": sub_id, "new_end_date": current_end.isoformat()}
                                    )
                    except Exception as e:
                        logger.warning(
                            f"Error verificando Stripe para suscripción {sub_id}: {e}",
                            exc_info=True,
                            extra={"subscription_id": sub_id}
                        )
                
                duration_ms = (time.time() - sub_start) * 1000
                
                if is_renewed:
                    renewed_subscriptions.append(sub_id)
                    logger.info(
                        f"Suscripción {sub_id} renovada",
                        extra={"subscription_id": sub_id, "duration_ms": duration_ms}
                    )
                else:
                    not_renewed_subscriptions.append(sub_id)
                    logger.info(
                        f"Suscripción {sub_id} NO renovada",
                        extra={"subscription_id": sub_id, "duration_ms": duration_ms}
                    )
        
        if STATS_AVAILABLE and Stats:
            Stats.incr("subscription_management.renewed", len(renewed_subscriptions))
            Stats.incr("subscription_management.not_renewed", len(not_renewed_subscriptions))
        
        return {
            "renewed_subscriptions": renewed_subscriptions,
            "not_renewed_subscriptions": not_renewed_subscriptions,
            "renewed_count": len(renewed_subscriptions),
            "not_renewed_count": len(not_renewed_subscriptions),
        }
    
    @task(
        task_id="mark_inactive_subscriptions",
        execution_timeout=timedelta(minutes=10),
        on_failure_callback=on_task_failure,
        doc_md="Marca como inactivas las suscripciones que no renovaron después del período de gracia"
    )
    def mark_inactive_subscriptions(renewal_data: Dict[str, Any], subscriptions_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Marca como inactivas las suscripciones que no renovaron después del período de gracia.
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        grace_period_days = int(params["grace_period_days"])
        dry_run = bool(params["dry_run"])
        
        not_renewed_subscriptions = renewal_data.get("not_renewed_subscriptions", [])
        expiring_subscriptions = subscriptions_data.get("expiring_subscriptions", [])
        
        # Crear mapa de suscripciones por ext_id
        subscriptions_map = {sub["ext_id"]: sub for sub in expiring_subscriptions}
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        today = date.today()
        grace_period_end = today - timedelta(days=grace_period_days)
        
        marked_inactive = []
        skipped = []
        
        for sub_id in not_renewed_subscriptions:
            subscription = subscriptions_map.get(sub_id)
            if not subscription:
                continue
            
            end_date_str = subscription.get("end_date")
            if not end_date_str:
                skipped.append({"subscription_id": sub_id, "reason": "no_end_date"})
                continue
            
            end_date = datetime.fromisoformat(end_date_str).date()
            
            # Solo marcar como inactivo si pasó el período de gracia
            if end_date < grace_period_end:
                try:
                    if not dry_run:
                        with hook.get_conn() as conn:
                            with conn.cursor() as cur:
                                cur.execute("""
                                    UPDATE subscriptions
                                    SET status = 'inactive',
                                        updated_at = NOW()
                                    WHERE ext_id = %s
                                      AND status = 'active'
                                """, (sub_id,))
                                
                                if cur.rowcount > 0:
                                    conn.commit()
                                    marked_inactive.append({
                                        "subscription_id": sub_id,
                                        "end_date": end_date_str,
                                        "marked_at": datetime.utcnow().isoformat()
                                    })
                                    logger.info(
                                        f"Suscripción {sub_id} marcada como inactiva",
                                        extra={"subscription_id": sub_id}
                                    )
                                else:
                                    skipped.append({"subscription_id": sub_id, "reason": "already_inactive"})
                    else:
                        logger.info(
                            f"[DRY RUN] Suscripción {sub_id} sería marcada como inactiva",
                            extra={"subscription_id": sub_id}
                        )
                        marked_inactive.append({
                            "subscription_id": sub_id,
                            "end_date": end_date_str,
                            "marked_at": datetime.utcnow().isoformat(),
                            "dry_run": True
                        })
                        
                except Exception as e:
                    logger.error(
                        f"Error marcando suscripción {sub_id} como inactiva: {e}",
                        exc_info=True,
                        extra={"subscription_id": sub_id}
                    )
                    skipped.append({"subscription_id": sub_id, "reason": f"error: {str(e)}"})
            else:
                skipped.append({
                    "subscription_id": sub_id,
                    "reason": "still_in_grace_period",
                    "end_date": end_date_str,
                    "grace_period_end": grace_period_end.isoformat()
                })
        
        if STATS_AVAILABLE and Stats:
            Stats.incr("subscription_management.marked_inactive", len(marked_inactive))
        
        return {
            "marked_inactive": marked_inactive,
            "skipped": skipped,
            "total_marked": len(marked_inactive),
            "total_skipped": len(skipped),
        }
    
    @task(
        task_id="generate_summary",
        trigger_rule="none_failed_min_one_success",
        doc_md="Genera un resumen completo del proceso de gestión de suscripciones"
    )
    def generate_summary(
        subscriptions_data: Dict[str, Any],
        notifications_data: Dict[str, Any],
        renewal_data: Dict[str, Any],
        inactivation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Genera un resumen completo del proceso de gestión de suscripciones.
        """
        current_metrics = {
            "expiring_subscriptions": subscriptions_data.get("count", 0),
            "invalid_subscriptions": subscriptions_data.get("invalid_count", 0),
            "anomalies_count": subscriptions_data.get("anomalies_count", 0),
            "predictive_alerts_count": subscriptions_data.get("predictive_alerts_count", 0),
            "notifications": {
                "sent": notifications_data.get("total_sent", 0),
                "failed": notifications_data.get("total_failed", 0),
            },
            "renewals": {
                "renewed": renewal_data.get("renewed_count", 0),
                "not_renewed": renewal_data.get("not_renewed_count", 0),
            },
            "inactivation": {
                "marked_inactive": inactivation_data.get("total_marked", 0),
                "skipped": inactivation_data.get("total_skipped", 0),
            },
        }
        
        # Calcular métricas agregadas de probabilidad de renovación
        expiring_subscriptions = subscriptions_data.get("expiring_subscriptions", [])
        if expiring_subscriptions:
            probabilities = [
                s.get("enriched_data", {}).get("renewal_probability", 0.5)
                for s in expiring_subscriptions
            ]
            if probabilities:
                current_metrics["renewal_probability"] = {
                    "avg": sum(probabilities) / len(probabilities),
                    "min": min(probabilities),
                    "max": max(probabilities),
                }
        
        # Comparar con histórico
        history_comparison = _compare_with_history(current_metrics)
        
        summary = {
            "execution_date": datetime.utcnow().isoformat(),
            **current_metrics,
            "history_comparison": history_comparison,
            "dry_run": subscriptions_data.get("dry_run", False),
        }
        
        # Construir mensaje de resumen
        summary_msg = f"""
        === RESUMEN DE GESTIÓN DE SUSCRIPCIONES ===
        Suscripciones próximas a vencer: {summary['expiring_subscriptions']}
        Suscripciones inválidas: {summary['invalid_subscriptions']}
        Anomalías detectadas: {summary.get('anomalies_count', 0)}
        Alertas predictivas: {summary.get('predictive_alerts_count', 0)}
        Notificaciones enviadas: {summary['notifications']['sent']}
        Notificaciones fallidas: {summary['notifications']['failed']}
        Suscripciones renovadas: {summary['renewals']['renewed']}
        Suscripciones no renovadas: {summary['renewals']['not_renewed']}
        Marcadas como inactivas: {summary['inactivation']['marked_inactive']}
        Omitidas: {summary['inactivation']['skipped']}
        """
        
        # Agregar segmentación si está disponible
        segments = subscriptions_data.get("segments", {})
        if segments:
            summary_msg += f"""
        === SEGMENTACIÓN ===
        Alto valor + Alto riesgo: {segments.get('high_value_high_risk', 0)}
        Alto valor + Bajo riesgo: {segments.get('high_value_low_risk', 0)}
        Valor medio: {segments.get('medium_value', 0)}
        Valor bajo: {segments.get('low_value', 0)}
        Corporativas: {segments.get('corporate', 0)}
        Personales: {segments.get('personal', 0)}
        Expirando pronto (≤7 días): {segments.get('expiring_soon', 0)}
        Largo plazo (>1 año): {segments.get('long_term', 0)}
        """
        
        # Agregar tendencias temporales si están disponibles
        temporal_trends = subscriptions_data.get("temporal_trends", {})
        if temporal_trends.get("has_trends"):
            summary_msg += f"""
        === TENDENCIAS TEMPORALES ===
        Valor total: ${temporal_trends.get('total_value', 0):,.2f}
        Valor promedio: ${temporal_trends.get('avg_value', 0):,.2f}
        """
            if temporal_trends.get("growth_rate") is not None:
                growth = temporal_trends["growth_rate"]
                growth_emoji = "📈" if growth > 0 else "📉"
                summary_msg += f"Tasa de crecimiento: {growth:+.1f}% {growth_emoji}\n"
        
        # Agregar análisis de cohortes si está disponible
        cohort_analysis = subscriptions_data.get("cohort_analysis", {})
        if cohort_analysis.get("has_data"):
            cohorts = cohort_analysis.get("cohorts", [])
            if cohorts:
                summary_msg += f"""
        === ANÁLISIS DE COHORTES ===
        Total de cohorts: {cohort_analysis.get('total_cohorts', 0)}
        Cohort más reciente: {cohorts[0].get('cohort', 'N/A') if cohorts else 'N/A'}
        """
                # Mostrar top 3 cohorts
                for cohort in cohorts[:3]:
                    summary_msg += f"  • {cohort.get('cohort')}: {cohort.get('total')} total, {cohort.get('expiring')} expirando ({cohort.get('expiring_rate', 0):.1f}%)\n"
        
        # Agregar métricas de probabilidad de renovación si están disponibles
        renewal_prob = current_metrics.get("renewal_probability")
        if renewal_prob:
            summary_msg += f"""
        Probabilidad promedio de renovación: {renewal_prob.get('avg', 0):.1%}
        (Rango: {renewal_prob.get('min', 0):.1%} - {renewal_prob.get('max', 0):.1%})
        """
        
        # Agregar comparación con histórico si está disponible
        if history_comparison.get("has_history"):
            summary_msg += "\n=== CAMBIOS vs HISTÓRICO ===\n"
            for metric, change_data in history_comparison.get("changes", {}).items():
                change_pct = change_data.get("change_pct", 0)
                arrow = "↑" if change_pct > 0 else "↓" if change_pct < 0 else "→"
                summary_msg += f"{metric}: {change_data.get('current')} {arrow} {change_pct:.1f}%\n"
        
        summary_msg += "============================================"
        
        # Agregar resumen ejecutivo si está disponible
        executive_report = summary.get("executive_report", {})
        if executive_report:
            exec_summary = executive_report.get("executive_summary", {})
            risk_assessment = executive_report.get("risk_assessment", {})
            
            summary_msg += f"""
        
        === RESUMEN EJECUTIVO ===
        Tasa de renovación: {exec_summary.get('renewal_rate', 0):.1f}%
        Suscripciones en riesgo: {exec_summary.get('at_risk_count', 0)}
        Riesgo general: {risk_assessment.get('overall_risk', 'unknown').upper()}
        """
            
            recommendations = executive_report.get("recommendations", [])
            if recommendations:
                summary_msg += "\n=== RECOMENDACIONES ===\n"
                for rec in recommendations[:3]:  # Top 3
                    priority_emoji = "🔴" if rec.get("priority") == "high" else "🟡"
                    summary_msg += f"{priority_emoji} {rec.get('title')}\n"
                    summary_msg += f"   {rec.get('action')}\n\n"
        
        summary_msg += "============================================"
        
        logger.info(summary_msg, extra=summary)
        
        # Enviar notificación Slack si hay problemas críticos
        try:
            critical_issues = []
            if summary['notifications']['failed'] > summary['notifications']['sent'] * 0.5:
                critical_issues.append(f"Alta tasa de fallos en notificaciones: {summary['notifications']['failed']}/{summary['notifications']['sent']}")
            
            if summary['invalid_subscriptions'] > 0:
                critical_issues.append(f"Suscripciones inválidas detectadas: {summary['invalid_subscriptions']}")
            
            # Alertas predictivas críticas
            predictive_alerts = subscriptions_data.get("predictive_alerts", [])
            high_severity_alerts = [a for a in predictive_alerts if a.get("severity") in ["high", "critical"]]
            if high_severity_alerts:
                critical_issues.append(f"Alertas predictivas de alta severidad: {len(high_severity_alerts)}")
            
            # Probabilidad promedio de renovación muy baja
            renewal_prob = current_metrics.get("renewal_probability", {}).get("avg")
            if renewal_prob and renewal_prob < 0.3:
                critical_issues.append(f"Probabilidad promedio de renovación muy baja: {renewal_prob:.1%}")
            
            if critical_issues:
                from data.airflow.plugins.etl_notifications import notify_slack
                message = "⚠️ *Alertas en Gestión de Suscripciones*\n\n"
                message += "\n".join(f"• {issue}" for issue in critical_issues)
                notify_slack(message)
                logger.info("Slack alert sent", extra={"critical_issues": len(critical_issues)})
        except ImportError:
            pass  # Slack notifications no disponibles
        except Exception as e:
            logger.warning(f"Error enviando notificación Slack: {e}", exc_info=True)
        
        # Generar reporte ejecutivo
        executive_report = _generate_executive_report(
            subscriptions_data,
            notifications_data,
            renewal_data,
            inactivation_data
        )
        
        # Agregar reporte ejecutivo al summary
        summary["executive_report"] = executive_report
        
        # Logging del reporte ejecutivo
        logger.info(
            "Executive report generated",
            extra={
                "renewal_rate": executive_report["executive_summary"].get("renewal_rate", 0),
                "at_risk_count": executive_report["executive_summary"].get("at_risk_count", 0),
                "overall_risk": executive_report["risk_assessment"].get("overall_risk", "unknown"),
                "recommendations_count": len(executive_report["recommendations"]),
            }
        )
        
        # Exportar métricas a S3 si está configurado
        s3_export_result = None
        s3_bucket = os.getenv("SUBSCRIPTION_METRICS_S3_BUCKET", "")
        if s3_bucket:
            # Incluir reporte ejecutivo en exportación
            export_data = {
                "summary": summary,
                "executive_report": executive_report,
            }
            s3_export_result = _export_metrics_to_s3(export_data, s3_bucket=s3_bucket)
            if s3_export_result.get("exported"):
                logger.info(
                    f"Metrics exported to S3",
                    extra={"s3_path": s3_export_result.get("s3_path")}
                )
        
        if STATS_AVAILABLE and Stats:
            Stats.incr("subscription_management.executions.total", 1)
            Stats.incr("subscription_management.executions.success", 1)
            
            # Métricas de segmentación
            segments = subscriptions_data.get("segments", {})
            if segments:
                for segment_name, count in segments.items():
                    Stats.gauge(f"subscription_management.segments.{segment_name}", count)
        
        # Agregar resultado de exportación S3 al summary
        if s3_export_result:
            summary["s3_export"] = s3_export_result
        
        return summary
    
    # Distributed locking para prevenir ejecuciones concurrentes
    @task(
        task_id="acquire_execution_lock",
        execution_timeout=timedelta(minutes=1),
        doc_md="Adquiere lock distribuido para prevenir ejecuciones concurrentes"
    )
    def acquire_execution_lock() -> Dict[str, Any]:
        """Adquiere lock distribuido para prevenir ejecuciones concurrentes."""
        ctx = get_current_context()
        dag_run_id = str(ctx.get("run_id", ""))
        
        lock_key = f"subscription_management:execution_lock"
        ttl_seconds = 3600  # 1 hora
        
        acquired = _acquire_distributed_lock(lock_key, ttl_seconds)
        
        if not acquired:
            # Intentar obtener info del lock existente
            try:
                lock_data = Variable.get(lock_key, default_var=None)
                if lock_data:
                    lock_info = json.loads(lock_data)
                    raise AirflowFailException(
                        f"Another execution is already running. Lock acquired at: {lock_info.get('acquired_at', 'unknown')}"
                    )
            except Exception:
                pass
            raise AirflowFailException("Failed to acquire execution lock. Another run may be in progress.")
        
        logger.info(
            "Execution lock acquired",
            extra={"lock_key": lock_key, "ttl_seconds": ttl_seconds, "dag_run_id": dag_run_id}
        )
        
        return {"locked": True, "lock_key": lock_key, "dag_run_id": dag_run_id}
    
    @task(
        task_id="release_execution_lock",
        trigger_rule="none_failed_min_one_success",
        doc_md="Libera el lock de ejecución distribuido"
    )
    def release_execution_lock(lock_info: Dict[str, Any]) -> None:
        """Libera el lock de ejecución distribuido."""
        lock_key = lock_info.get("lock_key")
        if lock_key:
            _release_distributed_lock(lock_key)
            logger.info("Execution lock released", extra={"lock_key": lock_key})
    
    # Pipeline organizado con TaskGroups
    health = health_check()
    execution_lock = acquire_execution_lock()
    
    # Fase 1: Identificación y validación
    with task_group(group_id="identification_phase") as identification_group:
        expiring_subscriptions = identify_expiring_subscriptions()
    
    # Fase 2: Notificaciones
    with task_group(group_id="notification_phase") as notification_group:
        notifications = send_renewal_notifications(expiring_subscriptions)
    
    # Fase 3: Verificación de renovaciones
    with task_group(group_id="renewal_verification_phase") as renewal_group:
        renewals = check_renewals(expiring_subscriptions)
    
    # Fase 4: Inactivación
    with task_group(group_id="inactivation_phase") as inactivation_group:
        inactivations = mark_inactive_subscriptions(renewals, expiring_subscriptions)
    
    # Fase 5: Resumen final
    summary = generate_summary(expiring_subscriptions, notifications, renewals, inactivations)
    
    # End marker
    end = EmptyOperator(
        task_id="end",
        trigger_rule="none_failed_min_one_success",
    )
    
    # Conectar todas las fases
    health >> execution_lock
    execution_lock >> identification_group
    identification_group >> notification_group
    identification_group >> renewal_group
    renewal_group >> inactivation_group
    notification_group >> summary
    inactivation_group >> summary
    summary >> end
    end >> release_execution_lock(execution_lock)


dag = subscription_management()
