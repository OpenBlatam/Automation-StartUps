"""
DAG para procesar correos de Gmail sin etiqueta 'SinRevisar':
- Obtiene correos sin la etiqueta 'SinRevisar'
- Añade la etiqueta 'Procesado' a cada correo procesado
- Envía detalles (de, asunto, fecha) a un log externo
- Retorna resumen de procesados y fallidos
"""
from __future__ import annotations

import os
import json
import logging
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, TypedDict
from dataclasses import dataclass, field
from email.utils import parseaddr, parsedate_to_datetime
from functools import lru_cache
from contextlib import contextmanager
from airflow.models import Variable
import re
from urllib.parse import urlparse

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.exceptions import AirflowFailException

# Librerías mejoradas
try:
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type,
        RetryError,
    )
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    try:
        import requests
    except ImportError:
        pass

try:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    CONCURRENT_FUTURES_AVAILABLE = True
except ImportError:
    CONCURRENT_FUTURES_AVAILABLE = False

try:
    from pydantic import BaseModel, Field, ValidationError
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

try:
    from cachetools import TTLCache
    CACHETOOLS_AVAILABLE = True
except ImportError:
    CACHETOOLS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Importar utilidades de logging estructurado del stack
try:
    from plugins.etl_logging import get_task_logger, log_with_context
    STRUCTURED_LOGGING_AVAILABLE = True
except ImportError:
    try:
        from data.airflow.plugins.etl_logging import get_task_logger, log_with_context
        STRUCTURED_LOGGING_AVAILABLE = True
    except ImportError:
        STRUCTURED_LOGGING_AVAILABLE = False
        get_task_logger = lambda x: logging.getLogger(x or __name__)
        def log_with_context(logger, level, msg, **kwargs):
            logger.log(level, msg, extra=kwargs)

# Usar logger estructurado si está disponible
if STRUCTURED_LOGGING_AVAILABLE:
    logger = get_task_logger("gmail_processor")

# Importar Stats para métricas
try:
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False
    logger.debug("Stats not available for metrics")

# Importar utilidades de notificaciones del stack
try:
    from data.airflow.plugins.etl_notifications import notify_slack
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    try:
        from plugins.etl_notifications import notify_slack
        NOTIFICATIONS_AVAILABLE = True
    except ImportError:
        NOTIFICATIONS_AVAILABLE = False
        logger.warning("Notifications plugin not available")

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_API_AVAILABLE = True
except ImportError:
    GMAIL_API_AVAILABLE = False
    logger.warning("Gmail API libraries not available. Install: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")


# Scopes necesarios para la API de Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Rate limiting para Gmail API
# Gmail API tiene límites:
# - 250 quota units por usuario por segundo
# - messages.list: 5 units
# - messages.get: 5 units
# - messages.modify: 100 units
GMAIL_RATE_LIMIT_DELAY = float(os.getenv("GMAIL_RATE_LIMIT_DELAY", "0.2"))  # Delay base entre requests
GMAIL_MAX_RETRY_AFTER = int(os.getenv("GMAIL_MAX_RETRY_AFTER", "300"))  # Máximo Retry-After (5 min)
GMAIL_USE_JITTER = os.getenv("GMAIL_USE_JITTER", "true").lower() == "true"  # Usar jitter en delays

# Circuit breaker configuración
CB_FAILURE_THRESHOLD = int(os.getenv("GMAIL_CB_FAILURE_THRESHOLD", "10"))  # Fallos antes de abrir
CB_RESET_MINUTES = int(os.getenv("GMAIL_CB_RESET_MINUTES", "15"))  # Minutos antes de reset

# Batch processing
GMAIL_BATCH_SIZE = int(os.getenv("GMAIL_BATCH_SIZE", "10"))  # Emails por batch
GMAIL_BATCH_DELAY = float(os.getenv("GMAIL_BATCH_DELAY", "1.0"))  # Delay entre batches

# Parallel processing
GMAIL_MAX_WORKERS = int(os.getenv("GMAIL_MAX_WORKERS", "0"))  # 0 = secuencial, >0 = paralelo
GMAIL_PARALLEL_THRESHOLD = int(os.getenv("GMAIL_PARALLEL_THRESHOLD", "5"))  # Mínimo emails para paralelo

# Query optimization
GMAIL_QUERY_OPTIMIZATION = os.getenv("GMAIL_QUERY_OPTIMIZATION", "true").lower() == "true"  # Optimizar queries
GMAIL_QUERY_TIME_LIMIT_DAYS = int(os.getenv("GMAIL_QUERY_TIME_LIMIT_DAYS", "30"))  # Límite de tiempo en queries (días)
GMAIL_PAGE_SIZE = int(os.getenv("GMAIL_PAGE_SIZE", "100"))  # Tamaño de página para paginación

# Health check configuración
HEALTH_CHECK_ENABLED = os.getenv("GMAIL_HEALTH_CHECK_ENABLED", "true").lower() == "true"

# Timeouts configurables (en segundos)
GMAIL_API_TIMEOUT = int(os.getenv("GMAIL_API_TIMEOUT", "30"))  # Timeout para operaciones API
GMAIL_LIST_TIMEOUT = int(os.getenv("GMAIL_LIST_TIMEOUT", "30"))  # Timeout para list
GMAIL_GET_TIMEOUT = int(os.getenv("GMAIL_GET_TIMEOUT", "10"))  # Timeout para get
GMAIL_MODIFY_TIMEOUT = int(os.getenv("GMAIL_MODIFY_TIMEOUT", "15"))  # Timeout para modify
LOG_WEBHOOK_TIMEOUT = int(os.getenv("GMAIL_LOG_WEBHOOK_TIMEOUT", "30"))  # Timeout para webhook

# Cache para labels (TTL de 1 hora)
_label_cache: Optional[Any] = None
if CACHETOOLS_AVAILABLE:
    _label_cache = TTLCache(maxsize=100, ttl=3600)

# Cache para emails procesados (para evitar procesar duplicados en mismo run)
_processed_emails_cache: Optional[Any] = None
if CACHETOOLS_AVAILABLE:
    _processed_emails_cache = TTLCache(maxsize=1000, ttl=86400)  # 24 horas

# HTTP Client reutilizable para webhooks
_http_client: Optional[Any] = None

# Memory monitoring
MEMORY_MONITORING_ENABLED = os.getenv("GMAIL_MEMORY_MONITORING_ENABLED", "false").lower() == "true"


def _cb_key(dag_id: str) -> str:
    """Retorna la clave de variable para circuit breaker."""
    return f"cb:failures:gmail_processor:{dag_id}"


def _cb_is_open(dag_id: str, threshold: int = CB_FAILURE_THRESHOLD, reset_minutes: int = CB_RESET_MINUTES) -> bool:
    """
    Verifica si el circuit breaker está abierto.
    
    Args:
        dag_id: ID del DAG
        threshold: Umbral de fallos
        reset_minutes: Minutos para reset automático
    
    Returns:
        True si está abierto, False si está cerrado
    """
    try:
        key = _cb_key(dag_id)
        data_str = Variable.get(key, default_var=None)
        
        if not data_str:
            return False
        
        import json
        data = json.loads(data_str)
        count = int(data.get("count", 0))
        last_failure_ts = int(data.get("last_failure_ts", 0))
        now_ts = int(datetime.utcnow().timestamp())
        
        # Reset si ha pasado el tiempo de reset
        if now_ts - last_failure_ts >= (reset_minutes * 60):
            Variable.delete(key)
            return False
        
        return count >= threshold
    except Exception as e:
        logger.debug(f"Circuit breaker check failed: {e}")
        return False


def _cb_record_failure(dag_id: str) -> None:
    """Registra un fallo en el circuit breaker."""
    try:
        key = _cb_key(dag_id)
        now_ts = int(datetime.utcnow().timestamp())
        
        try:
            data_str = Variable.get(key, default_var=None)
            if data_str:
                import json
                data = json.loads(data_str)
                count = int(data.get("count", 0)) + 1
            else:
                count = 1
        except Exception:
            count = 1
        
        Variable.set(key, json.dumps({
            "count": count,
            "last_failure_ts": now_ts,
        }))
        
        if STATS_AVAILABLE:
            try:
                Stats.incr("gmail_processor.circuit_breaker.failures", 1)
                Stats.gauge("gmail_processor.circuit_breaker.count", count)
            except Exception:
                pass
        
        # Alertar si se acerca al threshold
        if count >= CB_FAILURE_THRESHOLD:
            logger.error(
                f"Circuit breaker opened for {dag_id} after {count} failures",
                extra={"dag_id": dag_id, "failures": count, "threshold": CB_FAILURE_THRESHOLD}
            )
            if STATS_AVAILABLE:
                try:
                    Stats.incr("gmail_processor.circuit_breaker.opened", 1)
                except Exception:
                    pass
    except Exception as e:
        logger.warning(f"Failed to record circuit breaker failure: {e}")


def _cb_reset(dag_id: str) -> None:
    """Resetea el circuit breaker."""
    try:
        key = _cb_key(dag_id)
        Variable.delete(key)
        
        if STATS_AVAILABLE:
            try:
                Stats.incr("gmail_processor.circuit_breaker.reset", 1)
            except Exception:
                pass
    except Exception as e:
        logger.debug(f"Failed to reset circuit breaker: {e}")


def _validate_webhook_url(url: str) -> bool:
    """
    Valida que una URL de webhook sea válida.
    
    Args:
        url: URL a validar
        
    Returns:
        True si es válida, False en caso contrario
    """
    if not url or not isinstance(url, str):
        return False
    
    try:
        parsed = urlparse(url)
        # Debe tener scheme (http/https) y netloc (dominio)
        if not parsed.scheme or not parsed.netloc:
            return False
        if parsed.scheme not in ['http', 'https']:
            return False
        return True
    except Exception:
        return False


def _validate_email_label_name(label_name: str) -> bool:
    """
    Valida que un nombre de etiqueta sea válido para Gmail.
    
    Args:
        label_name: Nombre de etiqueta a validar
        
    Returns:
        True si es válido, False en caso contrario
    """
    if not label_name or not isinstance(label_name, str):
        return False
    
    # Gmail labels: máximo 225 caracteres, sin caracteres especiales problemáticos
    if len(label_name) > 225:
        return False
    
    # No puede estar vacío después de strip
    if not label_name.strip():
        return False
    
    return True


def _sanitize_email_string(value: str, max_length: int = 200) -> str:
    """
    Sanitiza un string de email removiendo caracteres problemáticos y limitando longitud.
    
    Args:
        value: String a sanitizar
        max_length: Longitud máxima permitida
        
    Returns:
        String sanitizado
    """
    if not value or not isinstance(value, str):
        return ''
    
    # Remover caracteres de control y espacios al inicio/fin
    sanitized = ''.join(c for c in value if ord(c) >= 32 or c == '\n' or c == '\t')
    sanitized = sanitized.strip()
    
    # Limitar longitud
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def _validate_email_data(email_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Valida que los datos de email tengan los campos requeridos y sean válidos.
    
    Args:
        email_data: Diccionario con datos de email
        
    Returns:
        Tuple de (es_válido, mensaje_error)
    """
    if not isinstance(email_data, dict):
        return False, "email_data must be a dictionary"
    
    # Verificar campos requeridos
    required_fields = ['id', 'from']
    for field in required_fields:
        if field not in email_data or not email_data[field]:
            return False, f"Missing required field: {field}"
    
    # Validar ID
    email_id = str(email_data.get('id', ''))
    if len(email_id) > 100 or not email_id:
        return False, f"Invalid email ID: length must be 1-100"
    
    # Validar from
    email_from = str(email_data.get('from', ''))
    if len(email_from) > 200:
        return False, f"Invalid 'from' field: length must be <= 200"
    
    return True, None


def _calculate_adaptive_delay(base_delay: float, attempt: int = 1, use_jitter: bool = True) -> float:
    """
    Calcula delay adaptativo con exponential backoff y jitter opcional.
    
    Args:
        base_delay: Delay base en segundos
        attempt: Número de intento (para exponential backoff)
        use_jitter: Si usar jitter para evitar thundering herd
        
    Returns:
        Delay calculado en segundos
    """
    # Exponential backoff: base_delay * 2^(attempt-1)
    delay = base_delay * (2 ** (attempt - 1))
    
    # Agregar jitter aleatorio (±20%) si está habilitado
    if use_jitter and GMAIL_USE_JITTER:
        import random
        jitter = delay * 0.2 * (random.random() * 2 - 1)  # ±20%
        delay = delay + jitter
    
    # Limitar delay máximo
    max_delay = GMAIL_MAX_RETRY_AFTER
    return min(delay, max_delay)


def _analyze_processing_statistics(
    processed: int,
    failed: int,
    skipped: int,
    total: int,
    duration_seconds: float,
    error_types: Dict[str, int]
) -> Dict[str, Any]:
    """
    Analiza estadísticas de procesamiento y genera insights.
    
    Args:
        processed: Número de emails procesados exitosamente
        failed: Número de emails fallidos
        skipped: Número de emails saltados
        total: Total de emails encontrados
        duration_seconds: Duración total en segundos
        error_types: Diccionario de tipos de error y sus conteos
        
    Returns:
        Diccionario con análisis estadístico
    """
    analysis = {
        "success_rate": (processed / total * 100) if total > 0 else 0,
        "failure_rate": (failed / total * 100) if total > 0 else 0,
        "skip_rate": (skipped / total * 100) if total > 0 else 0,
        "throughput": processed / duration_seconds if duration_seconds > 0 else 0,
        "avg_time_per_email": duration_seconds / processed if processed > 0 else 0,
        "error_distribution": error_types,
        "dominant_error": max(error_types.items(), key=lambda x: x[1])[0] if error_types else None,
    }
    
    # Calcular percentiles y tendencias
    if total > 0:
        analysis["efficiency"] = processed / (processed + failed) * 100 if (processed + failed) > 0 else 0
        analysis["health_score"] = min(100, analysis["success_rate"] * 0.7 + analysis["efficiency"] * 0.3)
    else:
        analysis["efficiency"] = 0
        analysis["health_score"] = 0
    
    return analysis


def _predict_optimal_batch_size(
    total_emails: int,
    avg_email_duration: float = None,
    target_batch_duration: float = 10.0
) -> int:
    """
    Predice el tamaño óptimo de batch basado en métricas históricas.
    
    Args:
        total_emails: Total de emails a procesar
        avg_email_duration: Duración promedio por email en segundos (opcional)
        target_batch_duration: Duración objetivo del batch en segundos
        
    Returns:
        Tamaño de batch recomendado
    """
    base_batch_size = GMAIL_BATCH_SIZE
    
    # Si tenemos métricas históricas, calcular basado en throughput
    if avg_email_duration and avg_email_duration > 0:
        optimal_size = int(target_batch_duration / avg_email_duration)
        # Limitar entre 1 y base_batch_size * 2
        optimal_size = max(1, min(optimal_size, base_batch_size * 2))
        
        logger.debug(
            f"Optimal batch size prediction: {optimal_size}",
            extra={
                "optimal_size": optimal_size,
                "avg_email_duration": avg_email_duration,
                "target_duration": target_batch_duration,
            }
        )
        return optimal_size
    
    # Fallback: usar batch size base con ajuste por volumen
    if total_emails > 100:
        # Para grandes volúmenes, batches más grandes
        return min(base_batch_size * 2, total_emails // 10)
    elif total_emails < 10:
        # Para pequeños volúmenes, batches más pequeños
        return max(1, total_emails)
    
    return base_batch_size


def _should_retry_operation(
    error: Exception,
    attempt: int,
    max_attempts: int = 3
) -> tuple[bool, float]:
    """
    Decide si se debe reintentar una operación y cuánto esperar.
    
    Args:
        error: Excepción que ocurrió
        attempt: Número de intento actual
        max_attempts: Máximo de intentos permitidos
        
    Returns:
        Tuple de (debe_reintentar, delay_en_segundos)
    """
    if attempt >= max_attempts:
        return False, 0.0
    
    # Reintentar errores de rate limiting y temporales
    if isinstance(error, HttpError):
        if hasattr(error, 'resp'):
            status_code = error.resp.status
            
            # Rate limiting (429) - siempre reintentar
            if status_code == 429:
                delay = _calculate_adaptive_delay(GMAIL_RATE_LIMIT_DELAY, attempt, GMAIL_USE_JITTER)
                return True, delay
            
            # Errores temporales del servidor (5xx) - reintentar
            if 500 <= status_code < 600:
                delay = _calculate_adaptive_delay(2.0, attempt, GMAIL_USE_JITTER)
                return True, delay
            
            # Timeout (408) - reintentar
            if status_code == 408:
                delay = _calculate_adaptive_delay(1.0, attempt, GMAIL_USE_JITTER)
                return True, delay
    
    # Reintentar errores de conexión y timeout genéricos
    error_str = str(error).lower()
    retriable_errors = ['timeout', 'connection', 'network', 'temporary']
    if any(err in error_str for err in retriable_errors):
        delay = _calculate_adaptive_delay(1.0, attempt, GMAIL_USE_JITTER)
        return True, delay
    
    # No reintentar otros errores
    return False, 0.0


def _cleanup_memory_if_needed(current_memory_mb: float = None, threshold_mb: float = 400) -> bool:
    """
    Limpia memoria si el uso excede el umbral.
    
    Args:
        current_memory_mb: Uso actual de memoria en MB (opcional)
        threshold_mb: Umbral en MB para activar limpieza
        
    Returns:
        True si se realizó limpieza, False en caso contrario
    """
    if not MEMORY_MONITORING_ENABLED:
        return False
    
    try:
        import psutil
        import os as os_module
        process = psutil.Process(os_module.getpid())
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        if current_memory > threshold_mb:
            # Limpiar cache si está disponible
            if _processed_emails_cache is not None:
                # Limpiar 50% de entradas más antiguas
                if len(_processed_emails_cache) > 100:
                    keys_to_remove = list(_processed_emails_cache.keys())[:len(_processed_emails_cache) // 2]
                    for key in keys_to_remove:
                        _processed_emails_cache.pop(key, None)
                    
                    logger.info(
                        f"Memory cleanup: cleared {len(keys_to_remove)} cache entries",
                        extra={
                            "memory_before_mb": round(current_memory, 2),
                            "cache_size_before": len(_processed_emails_cache) + len(keys_to_remove),
                            "cache_size_after": len(_processed_emails_cache),
                        }
                    )
                    
                    if STATS_AVAILABLE:
                        try:
                            Stats.incr("gmail_processor.memory.cleanup_performed", 1)
                        except Exception:
                            pass
                    
                    return True
        
        return False
    except Exception as e:
        logger.debug(f"Memory cleanup error: {e}")
        return False


def _validate_max_emails(max_emails: int) -> int:
    """
    Valida y normaliza el máximo de emails a procesar.
    
    Args:
        max_emails: Número de emails a validar
        
    Returns:
        Número validado (asegurado dentro de límites razonables)
    """
    # Límites razonables
    MIN_EMAILS = 1
    MAX_EMAILS_LIMIT = 500
    
    try:
        max_emails_int = int(max_emails)
        if max_emails_int < MIN_EMAILS:
            logger.warning(f"max_emails {max_emails_int} too low, using {MIN_EMAILS}")
            return MIN_EMAILS
        if max_emails_int > MAX_EMAILS_LIMIT:
            logger.warning(f"max_emails {max_emails_int} too high, capping to {MAX_EMAILS_LIMIT}")
            return MAX_EMAILS_LIMIT
        return max_emails_int
    except (ValueError, TypeError):
        logger.warning(f"Invalid max_emails value: {max_emails}, using default 50")
        return 50


@contextmanager
def gmail_service_context(credentials_json: str, token_json: str):
    """
    Context manager para el servicio de Gmail que asegura limpieza de recursos.
    
    Args:
        credentials_json: Credenciales JSON
        token_json: Token JSON
        
    Yields:
        Servicio de Gmail API
        
    Raises:
        AirflowFailException: Si no se puede obtener el servicio
    """
    service = None
    try:
        service = get_gmail_service(credentials_json, token_json)
        yield service
    except Exception as e:
        logger.error(
            f"Error in Gmail service context: {e}",
            extra={"error": str(e), "error_type": type(e).__name__},
            exc_info=True
        )
        raise
    finally:
        # Limpieza de recursos si es necesaria
        # El servicio de Gmail API no requiere cierre explícito, pero podemos loggear
        if service:
            logger.debug("Gmail service context cleaned up")


def _perform_health_check(credentials_json: str, token_json: str) -> bool:
    """
    Realiza un health check rápido de la API de Gmail.
    
    Args:
        credentials_json: Credenciales JSON
        token_json: Token JSON
    
    Returns:
        True si el health check pasa
    
    Raises:
        Exception: Si el health check falla
    """
    try:
        service = get_gmail_service(credentials_json, token_json)
        # Health check: obtener perfil del usuario (operación ligera)
        profile = service.users().getProfile(userId='me').execute()
        email_address = profile.get('emailAddress', 'unknown')
        
        logger.debug(f"Health check passed: {email_address}")
        
        if STATS_AVAILABLE:
            try:
                Stats.incr("gmail_processor.health_check.success", 1)
            except Exception:
                pass
        
        return True
    except HttpError as e:
        status_code = e.resp.status if hasattr(e, 'resp') else 0
        error_category = _get_error_category(e)
        
        logger.warning(
            f"Health check failed: {e}",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "status_code": status_code,
                "error_category": error_category,
            }
        )
        if STATS_AVAILABLE:
            try:
                Stats.incr("gmail_processor.health_check.failed", 1, tags={
                    "error": type(e).__name__,
                    "status_code": str(status_code),
                    "error_category": error_category,
                })
            except Exception:
                pass
        raise
    except Exception as e:
        logger.warning(
            f"Health check failed: {e}",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
            }
        )
        if STATS_AVAILABLE:
            try:
                Stats.incr("gmail_processor.health_check.failed", 1, tags={
                    "error": type(e).__name__,
                })
            except Exception:
                pass
        raise


def _handle_gmail_rate_limit(error: HttpError, operation: str = "") -> None:
    """
    Maneja rate limiting de Gmail API (429, 503) con mejor lógica.
    
    Args:
        error: Excepción HttpError de Gmail API
        operation: Nombre de la operación (para logging)
    
    Raises:
        HttpError: Si el error no es rate limit o después de esperar
    """
    status_code = error.resp.status if hasattr(error, 'resp') else 0
    
    # Rate limiting (429) o Service unavailable (503)
    if status_code in [429, 503]:
        retry_after = GMAIL_RATE_LIMIT_DELAY
        
        # Intentar obtener Retry-After del header
        if hasattr(error, 'resp') and error.resp:
            retry_after_header = error.resp.headers.get('Retry-After')
            if retry_after_header:
                try:
                    retry_after = min(int(retry_after_header), GMAIL_MAX_RETRY_AFTER)
                    
                    # Métrica de rate limit
                    if STATS_AVAILABLE:
                        try:
                            Stats.incr("gmail_processor.rate_limit.hit", 1, tags={
                                "operation": operation,
                                "status_code": str(status_code),
                            })
                            Stats.timing("gmail_processor.rate_limit.wait_seconds", retry_after)
                        except Exception:
                            pass
                    
                    logger.warning(
                        f"Gmail API rate limit hit for {operation}, waiting {retry_after}s",
                        extra={
                            "operation": operation,
                            "status_code": status_code,
                            "retry_after": retry_after,
                        }
                    )
                    
                    import time
                    # Usar delay adaptativo con jitter si está habilitado
                    adaptive_delay = _calculate_adaptive_delay(retry_after, attempt=1, use_jitter=GMAIL_USE_JITTER)
                    time.sleep(adaptive_delay)
                    return  # Retry después de esperar
                except (ValueError, TypeError):
                    pass
            
            # Si no hay Retry-After, usar delay configurado
            logger.warning(
                f"Gmail API rate limit for {operation}, using default delay {GMAIL_RATE_LIMIT_DELAY}s",
                extra={"operation": operation, "status_code": status_code}
            )
            
            if STATS_AVAILABLE:
                try:
                    Stats.incr("gmail_processor.rate_limit.hit", 1, tags={
                        "operation": operation,
                        "status_code": str(status_code),
                    })
                except Exception:
                    pass
            
            import time
            # Usar delay adaptativo con jitter
            adaptive_delay = _calculate_adaptive_delay(GMAIL_RATE_LIMIT_DELAY, attempt=1, use_jitter=GMAIL_USE_JITTER)
            time.sleep(adaptive_delay)
            return
    
    # No es rate limit, re-lanzar
    raise error


def _is_retriable_error(error: HttpError) -> bool:
    """
    Verifica si un error de Gmail API es recuperable.
    
    Args:
        error: Excepción HttpError de Gmail API
        
    Returns:
        True si el error es recuperable (debe reintentarse), False en caso contrario
    """
    status_code = error.resp.status if hasattr(error, 'resp') else 0
    
    # Errores recuperables: rate limits, service unavailable, timeout-like errors
    retriable_statuses = [429, 500, 502, 503, 504]
    
    if status_code in retriable_statuses:
        return True
    
    # Errores no recuperables: autenticación, autorización, not found, bad request
    non_retriable_statuses = [400, 401, 403, 404]
    
    if status_code in non_retriable_statuses:
        return False
    
    # Por defecto, no reintentar para otros errores
    return False


def _get_error_category(error: HttpError) -> str:
    """
    Categoriza un error de Gmail API para mejor logging y métricas.
    
    Args:
        error: Excepción HttpError de Gmail API
        
    Returns:
        Categoría del error (rate_limit, auth, not_found, server_error, etc.)
    """
    status_code = error.resp.status if hasattr(error, 'resp') else 0
    
    if status_code == 429:
        return "rate_limit"
    elif status_code in [500, 502, 503, 504]:
        return "server_error"
    elif status_code == 401:
        return "auth_invalid"
    elif status_code == 403:
        return "auth_forbidden"
    elif status_code == 404:
        return "not_found"
    elif status_code == 400:
        return "bad_request"
    else:
        return "unknown"


def _log_gmail_operation(
    level: int,
    message: str,
    operation: str = "",
    email_id: str = "",
    **extra: Any
) -> None:
    """
    Helper para logging estructurado de operaciones Gmail.
    
    Args:
        level: Nivel de logging (logging.INFO, logging.ERROR, etc.)
        message: Mensaje a logear
        operation: Nombre de la operación
        email_id: ID del email (si aplica)
        **extra: Campos adicionales para el contexto
    """
    context = {
        "operation": operation,
        "email_id": email_id,
        **extra
    }
    
    if STRUCTURED_LOGGING_AVAILABLE:
        log_with_context(logger, level, message, **context)
    else:
        logger.log(level, message, extra=context)


# Modelos Pydantic para validación
if PYDANTIC_AVAILABLE:
    class EmailData(BaseModel):
        """Modelo de datos de email con validación."""
        id: str = Field(..., description="ID del mensaje")
        from_address: str = Field(..., alias="from", description="Remitente")
        subject: str = Field(default="(Sin asunto)", description="Asunto")
        date: str = Field(..., description="Fecha del correo")
        threadId: Optional[str] = Field(None, description="ID del thread")
        snippet: str = Field(default="", max_length=200, description="Snippet del correo")
        
        class Config:
            populate_by_name = True
    
    class LogEntry(BaseModel):
        """Modelo para entrada de log."""
        timestamp: str = Field(..., description="Timestamp ISO format")
        source: str = Field(default="gmail_processor", description="Fuente del log")
        email: EmailData = Field(..., description="Datos del email")
    
    class ProcessingSummary(BaseModel):
        """Resumen del procesamiento."""
        processed: int = Field(..., ge=0, description="Correos procesados")
        failed: int = Field(..., ge=0, description="Correos fallidos")
        total: int = Field(..., ge=0, description="Total de correos")
        dry_run: bool = Field(..., description="Modo dry run")
        failed_details: List[Dict[str, Any]] = Field(default_factory=list, description="Detalles de errores")
else:
    # Fallback sin Pydantic
    EmailData = Dict[str, Any]
    LogEntry = Dict[str, Any]
    ProcessingSummary = Dict[str, Any]


@dag(
    dag_id="gmail_processor",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 */6 * * *",  # Cada 6 horas
    catchup=False,
    default_args={
        "owner": "data-team",
        "retries": int(os.getenv("GMAIL_DAG_RETRIES", "2")),
        "retry_delay": timedelta(minutes=int(os.getenv("GMAIL_RETRY_DELAY_MINUTES", "5"))),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=int(os.getenv("GMAIL_MAX_RETRY_DELAY_MINUTES", "30"))),
        "depends_on_past": False,
    },
    dagrun_timeout=timedelta(minutes=int(os.getenv("GMAIL_DAG_TIMEOUT_MINUTES", "60"))),
    max_active_runs=1,
    doc_md="""
    ### Procesador de Correos de Gmail
    
    DAG que procesa correos de Gmail sin la etiqueta 'SinRevisar':
    1. Obtiene los últimos correos sin la etiqueta 'SinRevisar'
    2. Añade la etiqueta 'Procesado' a cada correo procesado
    3. Envía detalles (de, asunto, fecha) a un log externo
    4. Retorna resumen de procesados y fallidos
    
    **Configuración:**
    - Las credenciales y configuración se cargan desde variables de entorno (configuradas en values.yaml)
    - Variables de entorno: GMAIL_CREDENTIALS_JSON, GMAIL_TOKEN_JSON, GMAIL_LOG_WEBHOOK_URL, etc.
    - Los parámetros pueden sobreescribir las variables de entorno si se proporcionan
    
    **Parámetros opcionales (sobreescriben variables de entorno):**
    - `gmail_credentials_json`: JSON string con las credenciales OAuth2 de Gmail (o path a archivo)
    - `gmail_token_json`: JSON string con el token almacenado (o path a archivo)
    - `max_emails`: Máximo de correos a procesar por ejecución
    - `log_webhook_url`: URL del webhook para enviar logs externos
    - `label_sin_revisar`: Nombre de la etiqueta 'SinRevisar'
    - `label_procesado`: Nombre de la etiqueta 'Procesado'
    - `dry_run`: Solo simular sin modificar correos
    
    **Requisitos:**
    - Credenciales OAuth2 de Gmail configuradas en External Secrets
    - Token de acceso válido (se genera en primera ejecución)
    - Webhook de log externo configurado
    - External Secret `gmail-secrets` debe estar aplicado
    """,
    params={
        "gmail_credentials_json": Param("", type="string"),
        "gmail_token_json": Param("", type="string"),
        "max_emails": Param(0, type="integer", minimum=0, maximum=500),  # 0 = usar env
        "max_workers": Param(0, type="integer", minimum=0, maximum=10),  # 0 = usar env o secuencial
        "log_webhook_url": Param("", type="string"),
        "label_sin_revisar": Param("", type="string"),
        "label_procesado": Param("", type="string"),
        "dry_run": Param(False, type="boolean"),
    },
    tags=["gmail", "email", "automation", "processing"],
)
@contextmanager
def _get_http_client():
    """
    Context manager para HTTP client con connection pooling y reutilización.
    
    Yields:
        HTTP client (httpx.Client o requests.Session) con configuración optimizada
    """
    global _http_client
    
    if HTTPX_AVAILABLE:
        if _http_client is None:
            limits = httpx.Limits(
                max_keepalive_connections=10,
                max_connections=20
            )
            timeout = httpx.Timeout(
                LOG_WEBHOOK_TIMEOUT,
                connect=10.0,
                read=LOG_WEBHOOK_TIMEOUT,
                write=10.0
            )
            _http_client = httpx.Client(
                limits=limits,
                timeout=timeout,
                follow_redirects=True,
                http2=True  # HTTP/2 para mejor performance
            )
        yield _http_client
    else:
        # Fallback a requests con session
        try:
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            session = requests.Session()
            
            # Retry strategy para requests
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["POST", "GET"],
                raise_on_status=False
            )
            adapter = HTTPAdapter(
                max_retries=retry_strategy,
                pool_connections=10,
                pool_maxsize=20
            )
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            try:
                yield session
            finally:
                session.close()
        except ImportError:
            # Fallback sin pooling
            yield None


def gmail_processor() -> None:
    """
    DAG principal para procesar correos de Gmail.
    """
    
    @contextmanager
    def gmail_service_context(credentials_json: str, token_json: str):
        """
        Context manager para el servicio de Gmail API.
        Asegura limpieza de recursos.
        """
        service = get_gmail_service(credentials_json, token_json)
        try:
            yield service
        finally:
            # Cleanup si es necesario
            pass
    
    def load_json_from_file_or_string(source: str) -> Dict[str, Any]:
        """
        Carga JSON desde archivo o string.
        
        Args:
            source: Path a archivo o JSON string
            
        Returns:
            Diccionario con datos JSON
        """
        if not source or not source.strip():
            return {}
        
        if os.path.isfile(source):
            with open(source, 'r') as f:
                return json.load(f)
        
        return json.loads(source)
    
    def load_credentials_from_token(token_json: str) -> Optional[Credentials]:
        """
        Carga credenciales desde token almacenado.
        
        Args:
            token_json: Path a archivo o JSON string con token
            
        Returns:
            Credentials si se cargaron correctamente, None en caso contrario
        """
        if not token_json:
            return None
        
        try:
            token_data = load_json_from_file_or_string(token_json)
            if not token_data:
                return None
            return Credentials.from_authorized_user_info(token_data, SCOPES)
        except Exception as e:
            logger.warning(f"Could not load token: {e}")
            return None
    
    def refresh_credentials(creds: Credentials) -> Optional[Credentials]:
        """
        Intenta refrescar credenciales expiradas.
        
        Args:
            creds: Credenciales a refrescar
            
        Returns:
            Credenciales refrescadas o None si falló
        """
        if not creds or not creds.expired or not creds.refresh_token:
            return creds
        
        try:
            creds.refresh(Request())
            logger.info("Token refreshed successfully")
            return creds
        except Exception as e:
            logger.warning(f"Token refresh failed: {e}. New authorization may be required.")
            return None
    
    def create_new_credentials(credentials_json: str) -> Credentials:
        """
        Crea nuevas credenciales mediante OAuth flow.
        
        Args:
            credentials_json: Path a archivo o JSON string con credenciales OAuth2
            
        Returns:
            Credenciales autorizadas
            
        Raises:
            AirflowFailException: Si falla la autenticación
        """
        if not credentials_json:
            raise AirflowFailException("credentials_json is required for new authorization")
        
        try:
            creds_data = load_json_from_file_or_string(credentials_json)
            if not creds_data:
                raise AirflowFailException("Invalid credentials_json format")
            
            flow = InstalledAppFlow.from_client_config(creds_data, SCOPES)
            creds = flow.run_local_server(port=0)
            logger.info("New OAuth authorization completed")
            return creds
        except Exception as e:
            logger.error(f"Failed to get credentials: {e}")
            raise AirflowFailException(
                f"Gmail authentication error: {e}. "
                "If in production, ensure a valid token exists or run initial authorization."
            )
    
    def save_credentials_to_token(creds: Credentials, token_json: str) -> bool:
        """
        Guarda credenciales en archivo o string JSON.
        
        Args:
            creds: Credenciales a guardar
            token_json: Path a archivo o se ignora si no es archivo
            
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        if not creds or not token_json:
            return False
        
        try:
            token_data = json.loads(creds.to_json())
            if os.path.isfile(token_json) or not os.path.exists(token_json):
                # Es un path válido o nuevo archivo
                with open(token_json, 'w') as token_file:
                    json.dump(token_data, token_file, indent=2)
                logger.debug("Token saved successfully")
                return True
        except Exception as e:
            logger.warning(f"Could not save token: {e}")
        
        return False
    
    def get_gmail_service(credentials_json: str, token_json: str) -> Any:
        """
        Autentica y retorna el servicio de Gmail API.
        Implementa guard clauses y early returns siguiendo principios RPA.
        
        Args:
            credentials_json: JSON string con credenciales OAuth2 o path a archivo
            token_json: JSON string con token almacenado o path a archivo
            
        Returns:
            Servicio de Gmail API
            
        Raises:
            AirflowFailException: Si no hay librerías disponibles o falla autenticación
        """
        if not GMAIL_API_AVAILABLE:
            raise AirflowFailException(
                "Gmail API libraries not available. Install required packages."
            )
        
        if not credentials_json:
            raise AirflowFailException("credentials_json is required")
        
        # Cargar token existente si está disponible
        creds = load_credentials_from_token(token_json)
        
        # Si hay credenciales válidas, retornar servicio
        if creds and creds.valid:
            if token_json:
                save_credentials_to_token(creds, token_json)
            return build('gmail', 'v1', credentials=creds)
        
        # Intentar refrescar credenciales expiradas
        if creds:
            creds = refresh_credentials(creds)
            if creds and creds.valid:
                if token_json:
                    save_credentials_to_token(creds, token_json)
                return build('gmail', 'v1', credentials=creds)
        
        # Crear nuevas credenciales mediante OAuth
        creds = create_new_credentials(credentials_json)
        
        # Guardar token para próximas ejecuciones
        if token_json:
            save_credentials_to_token(creds, token_json)
        
        return build('gmail', 'v1', credentials=creds)
    
    @lru_cache(maxsize=50)
    def _get_label_id_cached(service: Any, label_name: str) -> Optional[str]:
        """
        Caché LRU para IDs de labels (helper interno).
        """
        return _get_or_create_label_impl(service, label_name)
    
    def _get_or_create_label_impl(service: Any, label_name: str) -> Optional[str]:
        """
        Implementación interna para obtener/crear label.
        """
        try:
            results = service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            for label in labels:
                if label['name'] == label_name:
                    return label['id']
            
            # Crear etiqueta si no existe
            label = service.users().labels().create(
                userId='me',
                body={
                    'name': label_name,
                    'labelListVisibility': 'labelShow',
                    'messageListVisibility': 'show'
                }
            ).execute()
            
            logger.info(f"Created label: {label_name} (ID: {label['id']})")
            return label['id']
        except HttpError as error:
            logger.error(f"Error getting/creating label {label_name}: {error}")
            return None
    
    def get_or_create_label(service: Any, label_name: str) -> Optional[str]:
        """
        Obtiene el ID de una etiqueta por nombre, o la crea si no existe.
        Usa cache si está disponible.
        
        Args:
            service: Servicio de Gmail API
            label_name: Nombre de la etiqueta
            
        Returns:
            ID de la etiqueta o None si no se puede crear
        """
        if _label_cache is not None and label_name in _label_cache:
            return _label_cache[label_name]
        
        label_id = _get_or_create_label_impl(service, label_name)
        
        if _label_cache is not None and label_id:
            _label_cache[label_name] = label_id
        
        return label_id
    
    def get_emails_without_label(
        service: Any,
        label_name: str,
        label_id: str,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Obtiene correos que NO tienen la etiqueta especificada.
        Implementa guard clauses y early returns.
        
        Args:
            service: Servicio de Gmail API
            label_name: Nombre de la etiqueta a excluir (para query)
            label_id: ID de la etiqueta a excluir (para validación)
            max_results: Máximo de resultados
            
        Returns:
            Lista de IDs y metadatos de correos
            
        Raises:
            HttpError: Si falla la comunicación con Gmail API
        """
        if not service:
            logger.error("Gmail service is required")
            return []
        
        if not label_name or not label_id:
            logger.error("label_name and label_id are required")
            return []
        
        if max_results <= 0:
            logger.warning(f"Invalid max_results: {max_results}, using default 50")
            max_results = 50
        
        try:
            # Construir query optimizada
            query_parts = [f"-label:{label_name}"]
            
            # Optimización: agregar filtro de tiempo si está habilitado
            if GMAIL_QUERY_OPTIMIZATION and GMAIL_QUERY_TIME_LIMIT_DAYS > 0:
                # Filtrar correos más antiguos que el límite para mejorar performance
                query_parts.append(f"newer_than:{GMAIL_QUERY_TIME_LIMIT_DAYS}d")
            
            query = " ".join(query_parts)
            
            logger.debug(
                f"Gmail query: {query}",
                extra={
                    "query": query,
                    "max_results": max_results,
                    "label_name": label_name,
                    "query_optimization": GMAIL_QUERY_OPTIMIZATION,
                }
            )
            
            list_start = datetime.utcnow()
            messages = []
            next_page_token = None
            
            # Paginación para obtener todos los resultados necesarios
            while len(messages) < max_results:
                page_size = min(GMAIL_PAGE_SIZE, max_results - len(messages))
                
                try:
                    request_params = {
                        'userId': 'me',
                        'q': query,
                        'maxResults': page_size,
                    }
                    
                    if next_page_token:
                        request_params['pageToken'] = next_page_token
                    
                    results = service.users().messages().list(**request_params).execute()
                    
                    list_duration = (datetime.utcnow() - list_start).total_seconds()
                    
                    if STATS_AVAILABLE:
                        try:
                            Stats.timing("gmail_processor.api.list_duration_seconds", list_duration)
                            Stats.incr("gmail_processor.api.list_calls", 1)
                        except Exception:
                            pass
                    
                    # Validar schema de respuesta
                    if not isinstance(results, dict):
                        logger.warning(f"Invalid Gmail response type: {type(results)}")
                        break
                    
                    page_messages = results.get('messages', [])
                    if not page_messages:
                        break
                    
                    messages.extend(page_messages)
                    
                    # Verificar si hay más páginas
                    next_page_token = results.get('nextPageToken')
                    if not next_page_token or len(messages) >= max_results:
                        break
                        
                except HttpError as error:
                    _handle_gmail_rate_limit(error, "list_messages")
                    # Reintentar después de manejar rate limit
                    try:
                        request_params = {
                            'userId': 'me',
                            'q': query,
                            'maxResults': page_size,
                        }
                        
                        if next_page_token:
                            request_params['pageToken'] = next_page_token
                        
                        results = service.users().messages().list(**request_params).execute()
                        
                        list_duration = (datetime.utcnow() - list_start).total_seconds()
                        if STATS_AVAILABLE:
                            try:
                                Stats.timing("gmail_processor.api.list_duration_seconds", list_duration)
                                Stats.incr("gmail_processor.api.list_calls", 1)
                            except Exception:
                                pass
                        
                        page_messages = results.get('messages', [])
                        if page_messages:
                            messages.extend(page_messages)
                            next_page_token = results.get('nextPageToken')
                        else:
                            break
                    except HttpError:
                        # Si sigue fallando, usar los mensajes obtenidos hasta ahora
                        break
            
            if STATS_AVAILABLE:
                try:
                    Stats.gauge("gmail_processor.api.messages_fetched", len(messages))
                    if next_page_token:
                        Stats.incr("gmail_processor.api.pagination_used", 1)
                except Exception:
                    pass
            
            # Antigua implementación sin paginación (comentada como fallback)
            """
            try:
                results = service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=max_results
                ).execute()
                """
            
            if not messages:
                logger.info(
                    "No emails found without the specified label",
                    extra={
                        "query": query,
                        "label_name": label_name,
                        "max_results": max_results,
                    }
                )
                return []
            
            pagination_used = next_page_token is not None
            
            logger.info(
                f"Found {len(messages)} message(s) from Gmail query",
                extra={
                    "total_messages": len(messages),
                    "query": query,
                    "pagination_used": pagination_used,
                }
            )
            
            # Obtener detalles de cada mensaje y verificar que realmente no tenga la etiqueta
            emails = []
            processed_count = 0
            skipped_label_count = 0
            total_messages = len(messages)
            
            # Progress tracking: log cada 10% o cada 10 mensajes
            progress_checkpoint = max(1, min(10, total_messages // 10)) if total_messages > 0 else 1
            last_logged_progress = 0
            
            for idx, msg in enumerate(messages, 1):
                try:
                    get_start = datetime.utcnow()
                    
                    try:
                        message = service.users().messages().get(
                            userId='me',
                            id=msg['id'],
                            format='metadata',
                            metadataHeaders=['From', 'Subject', 'Date']
                        ).execute()
                        
                        get_duration = (datetime.utcnow() - get_start).total_seconds()
                        
                        if STATS_AVAILABLE:
                            try:
                                Stats.timing("gmail_processor.api.get_duration_seconds", get_duration)
                                Stats.incr("gmail_processor.api.get_calls", 1)
                            except Exception:
                                pass
                    except HttpError as error:
                        _handle_gmail_rate_limit(error, "get_message")
                        # Re-lanzar después de manejar rate limit
                        message = service.users().messages().get(
                            userId='me',
                            id=msg['id'],
                            format='metadata',
                            metadataHeaders=['From', 'Subject', 'Date']
                        ).execute()
                    
                    # Verificar que el mensaje realmente no tenga la etiqueta
                    label_ids = message.get('labelIds', [])
                    if label_id in label_ids:
                        # El mensaje tiene la etiqueta, saltarlo
                        skipped_label_count += 1
                        if STATS_AVAILABLE:
                            try:
                                Stats.incr("gmail_processor.api.messages_skipped_has_label", 1)
                            except Exception:
                                pass
                        continue
                    
                    headers = message['payload'].get('headers', [])
                    header_dict = {h['name'].lower(): h['value'] for h in headers}
                    
                    # Parsear headers de email correctamente con validación mejorada
                    from_raw = header_dict.get('from', 'Unknown')
                    from_name, from_addr = parseaddr(from_raw)
                    from_header = from_addr if from_addr else from_raw
                    
                    # Validar y limpiar email
                    if from_header and '@' not in from_header:
                        # Si no es un email válido, usar el raw
                        from_header = from_raw[:100]  # Limitar longitud
                    
                    subject_header = header_dict.get('subject', '(Sin asunto)') or '(Sin asunto)'
                    # Limpiar y limitar longitud de subject
                    subject_header = subject_header.strip()[:500] if subject_header else '(Sin asunto)'
                    
                    date_raw = header_dict.get('date', 'Unknown')
                    
                    # Intentar parsear fecha correctamente
                    try:
                        if date_raw != 'Unknown':
                            parsed_date = parsedate_to_datetime(date_raw)
                            date_header = parsed_date.isoformat()
                        else:
                            date_header = 'Unknown'
                    except (ValueError, TypeError):
                        date_header = date_raw
                    
                    # Construir email_data con validaciones adicionales
                    email_id_valid = msg.get('id', '')
                    if not email_id_valid or len(email_id_valid) > 100:
                        logger.warning(
                            f"Invalid email ID: {email_id_valid[:50]}",
                            extra={"email_id": email_id_valid[:100]}
                        )
                        continue  # Saltar emails con IDs inválidos
                    
                    email_data_raw = {
                        'id': email_id_valid,
                        'from': from_header[:200],  # Limitar longitud
                        'subject': subject_header,  # Ya limitado arriba
                        'date': date_header,
                        'threadId': message.get('threadId', '')[:100] if message.get('threadId') else None,
                        'snippet': message.get('snippet', '')[:200],
                    }
                    
                    # Validación adicional con función helper
                    is_valid, error_msg = _validate_email_data(email_data_raw)
                    if not is_valid:
                        logger.warning(
                            f"Email validation failed: {error_msg}",
                            extra={
                                "email_id": email_data_raw.get('id', 'unknown'),
                                "error": error_msg,
                            }
                        )
                        if STATS_AVAILABLE:
                            try:
                                Stats.incr("gmail_processor.validation.failed", 1, tags={
                                    "error_type": "validation_error",
                                })
                            except Exception:
                                pass
                        continue
                    
                    # Validar con Pydantic si está disponible
                    if PYDANTIC_AVAILABLE:
                        try:
                            email_data = EmailData(**email_data_raw)
                            emails.append(email_data.model_dump(by_alias=True))
                        except ValidationError as e:
                            logger.warning(f"Email data validation failed for {msg['id']}: {e}")
                            emails.append(email_data_raw)
                    else:
                        emails.append(email_data_raw)
                    
                    processed_count += 1
                    
                    # Progress tracking: log periódico del progreso
                    if idx % progress_checkpoint == 0 or idx == total_messages:
                        progress_pct = (idx / total_messages * 100) if total_messages > 0 else 0
                        if progress_pct - last_logged_progress >= 10 or idx == total_messages:
                            logger.info(
                                f"Processing progress: {idx}/{total_messages} messages ({progress_pct:.1f}%)",
                                extra={
                                    "progress": idx,
                                    "total": total_messages,
                                    "percentage": round(progress_pct, 1),
                                    "processed_count": processed_count,
                                    "skipped_label_count": skipped_label_count,
                                    "valid_emails_count": len(emails),
                                }
                            )
                            last_logged_progress = progress_pct
                            
                            if STATS_AVAILABLE:
                                try:
                                    Stats.gauge("gmail_processor.api.progress_percentage", progress_pct)
                                except Exception:
                                    pass
                    
                except HttpError as error:
                    status_code = error.resp.status if hasattr(error, 'resp') else 0
                    error_category = _get_error_category(error)
                    
                    _log_gmail_operation(
                        logging.WARNING,
                        f"Error getting message from Gmail API",
                        operation="get_message",
                        email_id=msg.get('id', 'unknown'),
                        status_code=status_code,
                        error_category=error_category,
                        error_message=str(error)[:200]
                    )
                    
                    # Registrar métrica de error por categoría
                    if STATS_AVAILABLE:
                        try:
                            Stats.incr("gmail_processor.api.get_errors", 1, tags={
                                "status_code": str(status_code),
                                "error_category": error_category,
                            })
                        except Exception:
                            pass
                    
                    # Manejar rate limiting y errores recuperables
                    if _is_retriable_error(error):
                        try:
                            _handle_gmail_rate_limit(error, "get_message")
                            # Reintentar después de esperar
                            continue
                        except HttpError:
                            # Si sigue fallando después del retry, continuar con siguiente
                            continue
                    # Para errores no recuperables, continuar con siguiente email
                    continue
            
            logger.info(
                f"Processed {processed_count} messages, skipped {skipped_label_count} with label, found {len(emails)} valid emails",
                extra={
                    "processed_count": processed_count,
                    "skipped_label_count": skipped_label_count,
                    "valid_emails_count": len(emails),
                    "total_messages": len(messages),
                }
            )
            
            if STATS_AVAILABLE:
                try:
                    Stats.gauge("gmail_processor.api.messages_processed", processed_count)
                    Stats.gauge("gmail_processor.api.messages_skipped_with_label", skipped_label_count)
                    Stats.gauge("gmail_processor.api.valid_emails_found", len(emails))
                except Exception:
                    pass
            
            return emails
        except HttpError as error:
            status_code = error.resp.status if hasattr(error, 'resp') else 0
            error_category = _get_error_category(error)
            
            _log_gmail_operation(
                logging.ERROR,
                f"Error listing messages from Gmail API",
                operation="list_messages",
                status_code=status_code,
                error_category=error_category,
                error_message=str(error)[:200]
            )
            
            # Registrar métrica de error
            if STATS_AVAILABLE:
                try:
                    Stats.incr("gmail_processor.api.list_errors", 1, tags={
                        "status_code": str(status_code),
                        "error_category": error_category,
                    })
                except Exception:
                    pass
            
            # Manejar rate limiting antes de re-lanzar
            if _is_retriable_error(error):
                _handle_gmail_rate_limit(error, "list_messages")
                # Re-lanzar después de esperar para que retry logic funcione
            raise
    
    def add_label_to_email(
        service: Any,
        message_id: str,
        label_id: str
    ) -> bool:
        """
        Añade una etiqueta a un correo con retry automático.
        Implementa guard clauses para validación temprana.
        
        Args:
            service: Servicio de Gmail API
            message_id: ID del mensaje
            label_id: ID de la etiqueta a añadir
            
        Returns:
            True si se añadió correctamente, False en caso contrario
        """
        if not service:
            logger.error("Gmail service is required")
            return False
        
        if not message_id or not label_id:
            logger.error("message_id and label_id are required")
            return False
        if TENACITY_AVAILABLE:
            @retry(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=2, max=10),
                retry=retry_if_exception_type(HttpError),
                reraise=True,
            )
            def _add_label_with_retry():
                service.users().messages().modify(
                    userId='me',
                    id=message_id,
                    body={'addLabelIds': [label_id]}
                ).execute()
                return True
            
            try:
                return _add_label_with_retry()
            except HttpError as error:
                status_code = error.resp.status if hasattr(error, 'resp') else 0
                error_category = _get_error_category(error)
                
                _log_gmail_operation(
                    logging.ERROR,
                    f"Error adding label to message after retries",
                    operation="add_label",
                    email_id=message_id,
                    status_code=status_code,
                    error_category=error_category,
                    error_message=str(error)[:200]
                )
                
                # Registrar métrica de error
                if STATS_AVAILABLE:
                    try:
                        Stats.incr("gmail_processor.api.modify_errors", 1, tags={
                            "status_code": str(status_code),
                            "error_category": error_category,
                        })
                    except Exception:
                        pass
                
                return False
            except RetryError as error:
                _log_gmail_operation(
                    logging.ERROR,
                    f"Retry exhausted for adding label",
                    operation="add_label",
                    email_id=message_id,
                    error_message=str(error)[:200]
                )
                
                if STATS_AVAILABLE:
                    try:
                        Stats.incr("gmail_processor.api.modify_retry_exhausted", 1)
                    except Exception:
                        pass
                
                return False
        else:
            # Fallback sin tenacity
            try:
                service.users().messages().modify(
                    userId='me',
                    id=message_id,
                    body={'addLabelIds': [label_id]}
                ).execute()
                return True
            except HttpError as error:
                status_code = error.resp.status if hasattr(error, 'resp') else 0
                error_category = _get_error_category(error)
                
                logger.error(
                    f"Error adding label to message {message_id}: {error}",
                    extra={
                        "email_id": message_id,
                        "status_code": status_code,
                        "error_category": error_category,
                    }
                )
                
                if STATS_AVAILABLE:
                    try:
                        Stats.incr("gmail_processor.api.modify_errors", 1, tags={
                            "status_code": str(status_code),
                            "error_category": error_category,
                        })
                    except Exception:
                        pass
                
                return False
    
    def send_to_external_log(
        webhook_url: str,
        email_data: Dict[str, Any]
    ) -> bool:
        """
        Envía detalles del correo a un log externo con retry y mejor manejo de errores.
        
        Args:
            webhook_url: URL del webhook para logs
            email_data: Diccionario con datos del correo (de, asunto, fecha)
            
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        # Construir log entry con validación Pydantic si está disponible
        email_dict = {
            'id': email_data.get('id'),
            'from': email_data.get('from', 'Unknown'),
            'subject': email_data.get('subject', '(Sin asunto)'),
            'date': email_data.get('date', 'Unknown'),
            'threadId': email_data.get('threadId'),
            'snippet': str(email_data.get('snippet', ''))[:200],
        }
        
        log_entry_dict = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'source': 'gmail_processor',
            'email': email_dict,
        }
        
        # Validar con Pydantic si está disponible
        if PYDANTIC_AVAILABLE:
            try:
                log_entry = LogEntry(**log_entry_dict)
                payload = log_entry.model_dump(mode='json')
            except ValidationError as e:
                logger.warning(f"Log entry validation failed: {e}, using raw dict")
                payload = log_entry_dict
        else:
            payload = log_entry_dict
        
        # Usar connection pooling reutilizable para mejor performance
        if TENACITY_AVAILABLE:
            @retry(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=2, max=10),
                retry=retry_if_exception_type((Exception,)),
                reraise=False,
            )
            def _send_with_retry():
                with _get_http_client() as client:
                    if client is None:
                        # Fallback sin pooling si no hay cliente disponible
                        import requests
                        response = requests.post(
                            webhook_url,
                            json=payload,
                            headers={'Content-Type': 'application/json'},
                            timeout=LOG_WEBHOOK_TIMEOUT
                        )
                        response.raise_for_status()
                    else:
                        # Usar cliente con pooling
                        if HTTPX_AVAILABLE:
                            response = client.post(
                                webhook_url,
                                json=payload,
                                headers={'Content-Type': 'application/json'},
                            )
                            response.raise_for_status()
                        else:
                            # requests.Session
                            response = client.post(
                                webhook_url,
                                json=payload,
                                headers={'Content-Type': 'application/json'},
                                timeout=LOG_WEBHOOK_TIMEOUT
                            )
                            response.raise_for_status()
                return True
            
            try:
                send_start = datetime.utcnow()
                result = _send_with_retry()
                send_duration = (datetime.utcnow() - send_start).total_seconds()
                
                if STATS_AVAILABLE and result:
                    try:
                        Stats.timing("gmail_processor.webhook.send_duration_seconds", send_duration)
                        Stats.incr("gmail_processor.webhook.send_success", 1)
                    except Exception:
                        pass
                
                return result
            except Exception as e:
                logger.error(
                    f"Error sending to external log after retries: {e}",
                    extra={
                        "webhook_url": webhook_url[:100],
                        "error": str(e)[:200],
                        "error_type": type(e).__name__,
                    }
                )
                
                if STATS_AVAILABLE:
                    try:
                        Stats.incr("gmail_processor.webhook.send_failed", 1, tags={
                            "error_type": type(e).__name__,
                        })
                    except Exception:
                        pass
                
                return False
        else:
            # Fallback sin tenacity
            try:
                send_start = datetime.utcnow()
                with _get_http_client() as client:
                    if client is None:
                        # Fallback sin pooling
                        import requests
                        response = requests.post(
                            webhook_url,
                            json=payload,
                            headers={'Content-Type': 'application/json'},
                            timeout=LOG_WEBHOOK_TIMEOUT
                        )
                        response.raise_for_status()
                    else:
                        if HTTPX_AVAILABLE:
                            response = client.post(
                                webhook_url,
                                json=payload,
                                headers={'Content-Type': 'application/json'},
                            )
                            response.raise_for_status()
                        else:
                            response = client.post(
                                webhook_url,
                                json=payload,
                                headers={'Content-Type': 'application/json'},
                                timeout=LOG_WEBHOOK_TIMEOUT
                            )
                            response.raise_for_status()
                
                send_duration = (datetime.utcnow() - send_start).total_seconds()
                
                if STATS_AVAILABLE:
                    try:
                        Stats.timing("gmail_processor.webhook.send_duration_seconds", send_duration)
                        Stats.incr("gmail_processor.webhook.send_success", 1)
                    except Exception:
                        pass
                
                return True
            except Exception as e:
                logger.error(
                    f"Error sending to external log: {e}",
                    extra={
                        "webhook_url": webhook_url[:100],
                        "error": str(e)[:200],
                        "error_type": type(e).__name__,
                    }
                )
                
                if STATS_AVAILABLE:
                    try:
                        Stats.incr("gmail_processor.webhook.send_failed", 1, tags={
                            "error_type": type(e).__name__,
                        })
                    except Exception:
                        pass
                
                return False
    
    def _check_email_processed(email_id: str, dag_run_id: Optional[str] = None) -> bool:
        """
        Verifica si un email ya fue procesado (idempotencia).
        Usa cache en memoria además de Airflow Variables para mejor performance.
        
        Args:
            email_id: ID del email
            dag_run_id: ID del DAG run (opcional)
            
        Returns:
            True si ya fue procesado, False en caso contrario
        """
        # Verificar cache en memoria primero (más rápido)
        if _processed_emails_cache is not None:
            cache_key = f"{dag_run_id}:{email_id}" if dag_run_id else email_id
            if cache_key in _processed_emails_cache:
                return True
        
        # Verificar Airflow Variables (persistente)
        lock_key = f"gmail_processed:{email_id}"
        if dag_run_id:
            lock_key = f"gmail_processed:{dag_run_id}:{email_id}"
        
        existing = Variable.get(lock_key, default_var=None)
        
        # Actualizar cache en memoria si existe
        if existing is not None and _processed_emails_cache is not None:
            cache_key = f"{dag_run_id}:{email_id}" if dag_run_id else email_id
            _processed_emails_cache[cache_key] = True
        
        return existing is not None
    
    def _mark_email_processed(email_id: str, dag_run_id: Optional[str] = None, ttl_hours: int = 24) -> None:
        """
        Marca un email como procesado (idempotencia).
        Actualiza tanto cache en memoria como Airflow Variables.
        
        Args:
            email_id: ID del email
            dag_run_id: ID del DAG run (opcional)
            ttl_hours: TTL en horas (default: 24)
        """
        # Actualizar cache en memoria primero
        if _processed_emails_cache is not None:
            cache_key = f"{dag_run_id}:{email_id}" if dag_run_id else email_id
            _processed_emails_cache[cache_key] = True
        
        lock_key = f"gmail_processed:{email_id}"
        if dag_run_id:
            lock_key = f"gmail_processed:{dag_run_id}:{email_id}"
        
        try:
            # Guardar con timestamp para debugging
            value = str(datetime.utcnow().isoformat())
            Variable.set(lock_key, value)
            # Nota: Airflow Variables no tienen TTL nativo, 
            # se puede limpiar manualmente o con task de mantenimiento
        except Exception as e:
            logger.warning(
                f"Could not mark email as processed: {e}",
                extra={
                    "email_id": email_id,
                    "dag_run_id": dag_run_id,
                    "error": str(e)[:200],
                }
            )
    
    @task(
        task_id="process_gmail_emails",
        execution_timeout=timedelta(minutes=int(os.getenv("GMAIL_TASK_TIMEOUT_MINUTES", "45"))),
    )
    def process_gmail_emails() -> Dict[str, Any]:
        """
        Procesa correos de Gmail: obtiene, etiqueta y registra.
        Lee configuración desde variables de entorno (integración con stack) o parámetros.
        """
        ctx = get_current_context()
        params = ctx.get("params", {})
        
        # Leer desde variables de entorno (integración con stack) o parámetros
        credentials_json = str(params.get("gmail_credentials_json") or os.getenv("GMAIL_CREDENTIALS_JSON", ""))
        token_json = str(params.get("gmail_token_json") or os.getenv("GMAIL_TOKEN_JSON", ""))
        max_emails_raw = params.get("max_emails") or os.getenv("GMAIL_MAX_EMAILS", "50")
        max_emails = _validate_max_emails(max_emails_raw)
        max_workers_raw = params.get("max_workers") or os.getenv("GMAIL_MAX_WORKERS", "0")
        max_workers = int(max_workers_raw) if max_workers_raw else 0
        log_webhook_url = str(params.get("log_webhook_url") or os.getenv("GMAIL_LOG_WEBHOOK_URL", ""))
        label_sin_revisar = str(params.get("label_sin_revisar") or os.getenv("GMAIL_LABEL_SIN_REVISAR", "SinRevisar"))
        label_procesado = str(params.get("label_procesado") or os.getenv("GMAIL_LABEL_PROCESADO", "Procesado"))
        dry_run = bool(params.get("dry_run", False))
        
        # Validar parámetros críticos
        if not credentials_json:
            raise AirflowFailException(
                "gmail_credentials_json is required. "
                "Set GMAIL_CREDENTIALS_JSON env var or provide as parameter."
            )
        
        # Validar webhook URL si se proporciona
        if log_webhook_url and not _validate_webhook_url(log_webhook_url):
            raise AirflowFailException(f"Invalid webhook URL format: {log_webhook_url}")
        
        # Validar nombres de etiquetas
        if not _validate_email_label_name(label_sin_revisar):
            raise AirflowFailException(f"Invalid label name 'SinRevisar': {label_sin_revisar} (must be 1-225 characters)")
        
        if not _validate_email_label_name(label_procesado):
            raise AirflowFailException(f"Invalid label name 'Procesado': {label_procesado} (must be 1-225 characters)")
        
        logger.info(
            "Starting Gmail processor with validated parameters",
            extra={
                "max_emails": max_emails,
                "max_workers": max_workers,
                "parallel_threshold": GMAIL_PARALLEL_THRESHOLD,
                "label_sin_revisar": label_sin_revisar,
                "label_procesado": label_procesado,
                "dry_run": dry_run,
                "has_webhook": bool(log_webhook_url),
                "webhook_valid": _validate_webhook_url(log_webhook_url) if log_webhook_url else False,
            }
        )
        
        if not log_webhook_url:
            raise AirflowFailException(
                "log_webhook_url is required. "
                "Set GMAIL_LOG_WEBHOOK_URL env var or provide as parameter."
            )
        
        # Verificar circuit breaker
        dag_run_id = ctx.get("dag_run", {}).run_id if ctx.get("dag_run") else "unknown"
        if _cb_is_open("gmail_processor"):
            error_msg = (
                f"Circuit breaker is OPEN. Too many recent failures. "
                f"Threshold: {CB_FAILURE_THRESHOLD}, Reset in: {CB_RESET_MINUTES} minutes"
            )
            logger.error(error_msg)
            if STATS_AVAILABLE:
                try:
                    Stats.incr("gmail_processor.circuit_breaker.blocked", 1)
                except Exception:
                    pass
            raise AirflowFailException(error_msg)
        
        # Health check opcional
        if HEALTH_CHECK_ENABLED:
            try:
                _perform_health_check(credentials_json, token_json)
            except Exception as e:
                logger.warning(f"Health check failed: {e}, continuing anyway")
                if STATS_AVAILABLE:
                    try:
                        Stats.incr("gmail_processor.health_check.failed", 1)
                    except Exception:
                        pass
        
        logger.info(
            f"Starting Gmail processing (dry_run={dry_run}, max_emails={max_emails})",
            extra={
                "dry_run": dry_run,
                "max_emails": max_emails,
                "label_sin_revisar": label_sin_revisar,
                "label_procesado": label_procesado,
                "run_id": dag_run_id,
            }
        )
        
        # Autenticar con Gmail usando context manager para asegurar limpieza de recursos
        auth_start = datetime.utcnow()
        try:
            with gmail_service_context(credentials_json, token_json) as service:
                auth_duration = (datetime.utcnow() - auth_start).total_seconds()
                logger.info(
                    "Gmail API authentication successful",
                    extra={
                        "duration_seconds": round(auth_duration, 2),
                        "run_id": dag_run_id,
                    }
                )
                if STATS_AVAILABLE:
                    try:
                        Stats.timing("gmail_processor.auth.duration_seconds", auth_duration, tags={"run_id": dag_run_id})
                        Stats.incr("gmail_processor.auth.success", 1, tags={"run_id": dag_run_id})
                    except Exception:
                        pass
                
                # Reset circuit breaker en éxito de autenticación
                _cb_reset("gmail_processor")
                
                # Obtener o crear etiquetas
                label_sin_revisar_id = get_or_create_label(service, label_sin_revisar)
                if not label_sin_revisar_id:
                    raise AirflowFailException(f"Could not get/create label: {label_sin_revisar}")
                
                label_procesado_id = get_or_create_label(service, label_procesado)
                if not label_procesado_id:
                    raise AirflowFailException(f"Could not get/create label: {label_procesado}")
                
                # Obtener correos sin etiqueta 'SinRevisar'
                try:
                    emails = get_emails_without_label(
                        service, 
                        label_sin_revisar, 
                        label_sin_revisar_id, 
                        max_emails
                    )
                    logger.info(f"Found {len(emails)} emails without label '{label_sin_revisar}'")
                except Exception as e:
                    logger.error(f"Error getting emails: {e}")
                    raise AirflowFailException(f"Error getting emails: {e}")
                
                if not emails:
                    return {
                        "processed": 0,
                        "failed": 0,
                        "total": 0,
                        "message": "No emails to process"
                    }
                
                # Registrar inicio en métricas
                if STATS_AVAILABLE:
                    try:
                        Stats.incr("gmail_processor.run_started", 1, tags={"run_id": dag_run_id})
                        Stats.gauge("gmail_processor.emails_found", len(emails), tags={"run_id": dag_run_id})
                        Stats.gauge("gmail_processor.max_emails_config", max_emails)
                    except Exception as e:
                        logger.debug(f"Stats error: {e}")
                
                start_time = datetime.utcnow()
                
                # Decidir si usar procesamiento paralelo
                use_parallel = (
                    CONCURRENT_FUTURES_AVAILABLE and 
                    max_workers > 0 and 
                    len(emails) >= GMAIL_PARALLEL_THRESHOLD
                )
                
                logger.info(
                    f"Processing mode: {'parallel' if use_parallel else 'sequential'}",
                    extra={
                        "use_parallel": use_parallel,
                        "max_workers": max_workers if use_parallel else 1,
                        "total_emails": len(emails),
                        "parallel_threshold": GMAIL_PARALLEL_THRESHOLD,
                    }
                )
                
                # Función para procesar un email individual
                def process_single_email(email_data: Dict[str, Any], idx: int, service_instance: Any) -> Dict[str, Any]:
                    """Procesa un email individual."""
                    email_id = email_data.get('id', 'unknown')
                    email_subject = email_data.get('subject', 'N/A')[:50]
                    result = {
                        'email_id': email_id,
                        'email_index': idx,
                        'success': False,
                        'skipped': False,
                        'error_type': None,
                        'error': None,
                        'duration_seconds': 0,
                    }
                    
                    # Verificar idempotencia
                    if _check_email_processed(email_id, dag_run_id):
                        result['skipped'] = True
                        return result
                    
                    email_start = datetime.utcnow()
                    
                    try:
                        # Enviar a log externo con retry inteligente
                        log_success = False
                        max_log_retries = 2
                        
                        for log_attempt in range(1, max_log_retries + 1):
                            try:
                                log_success = send_to_external_log(log_webhook_url, email_data)
                                if log_success:
                                    break
                                
                                # Decidir si reintentar
                                log_error = Exception("log_send_failed")
                                should_retry, retry_delay = _should_retry_operation(
                                    log_error,
                                    log_attempt,
                                    max_log_retries
                                )
                                
                                if should_retry and log_attempt < max_log_retries:
                                    logger.debug(
                                        f"Retrying log send for email {email_id}, attempt {log_attempt + 1}",
                                        extra={
                                            "email_id": email_id,
                                            "attempt": log_attempt + 1,
                                            "retry_delay": retry_delay,
                                        }
                                    )
                                    time.sleep(retry_delay)
                                else:
                                    break
                            except Exception as log_exception:
                                if log_attempt < max_log_retries:
                                    should_retry, retry_delay = _should_retry_operation(
                                        log_exception,
                                        log_attempt,
                                        max_log_retries
                                    )
                                    if should_retry:
                                        logger.debug(
                                            f"Retrying log send after exception: {log_exception}",
                                            extra={
                                                "email_id": email_id,
                                                "attempt": log_attempt + 1,
                                                "retry_delay": retry_delay,
                                                "error": str(log_exception)[:200],
                                            }
                                        )
                                        time.sleep(retry_delay)
                                        continue
                                break
                        
                        if not log_success:
                            result['error_type'] = 'log_send_failed'
                            result['error'] = 'log_send_failed'
                            return result
                        
                        # Añadir etiqueta 'Procesado' (si no es dry_run) con retry inteligente
                        if not dry_run:
                            label_success = False
                            max_label_retries = 3
                            
                            for label_attempt in range(1, max_label_retries + 1):
                                try:
                                    label_success = add_label_to_email(service_instance, email_id, label_procesado_id)
                                    if label_success:
                                        break
                                    
                                    # Decidir si reintentar
                                    should_retry, retry_delay = _should_retry_operation(
                                        Exception("label_add_failed"),
                                        label_attempt,
                                        max_label_retries
                                    )
                                    
                                    if should_retry and label_attempt < max_label_retries:
                                        logger.debug(
                                            f"Retrying label add for email {email_id}, attempt {label_attempt + 1}",
                                            extra={
                                                "email_id": email_id,
                                                "attempt": label_attempt + 1,
                                                "retry_delay": retry_delay,
                                            }
                                        )
                                        time.sleep(retry_delay)
                                    else:
                                        break
                                except Exception as label_error:
                                    if label_attempt < max_label_retries:
                                        should_retry, retry_delay = _should_retry_operation(
                                            label_error,
                                            label_attempt,
                                            max_label_retries
                                        )
                                        if should_retry:
                                            time.sleep(retry_delay)
                                            continue
                                    
                                    # Si es un error no recuperable, salir
                                    if not _is_retriable_error(label_error) if hasattr(_is_retriable_error, '__call__') else False:
                                        break
                            
                            if not label_success:
                                result['error_type'] = 'label_add_failed'
                                result['error'] = 'label_add_failed'
                                return result
                        
                        # Procesamiento exitoso
                        result['success'] = True
                        result['duration_seconds'] = (datetime.utcnow() - email_start).total_seconds()
                        
                        # Marcar como procesado (idempotencia)
                        _mark_email_processed(email_id, dag_run_id)
                        
                        return result
                    
                    except Exception as e:
                        error_type = type(e).__name__
                        result['error_type'] = error_type
                        result['error'] = str(e)[:200]
                        result['duration_seconds'] = (datetime.utcnow() - email_start).total_seconds()
                        
                        # Registrar fallo en circuit breaker si es error crítico
                        if isinstance(e, HttpError) and hasattr(e, 'resp') and e.resp.status >= 500:
                            _cb_record_failure("gmail_processor")
                        
                        return result
                
                # Procesar cada correo con métricas detalladas
                processed = 0
                failed = 0
                log_failures = 0
                label_failures = 0
                other_failures = 0
                error_types: Dict[str, int] = {}
                skipped = 0  # Emails ya procesados (idempotencia)
                failed_details = []
                
                # Procesar en batches con tamaño adaptativo y predicción
                # Intentar obtener métricas históricas si están disponibles
                avg_email_duration_historical = None
                if STATS_AVAILABLE:
                    try:
                        # Intentar obtener métrica histórica (esto requeriría implementación de métricas históricas)
                        # Por ahora usamos valor predeterminado
                        pass
                    except Exception:
                        pass
                
                # Calcular batch size óptimo con predicción
                base_batch_size = GMAIL_BATCH_SIZE
                predicted_size = _predict_optimal_batch_size(
                    total_emails=len(emails),
                    avg_email_duration=avg_email_duration_historical
                )
                
                if use_parallel and max_workers > 1:
                    # Con procesamiento paralelo, batches más pequeños permiten mejor distribución
                    adaptive_batch_size = max(1, min(predicted_size, base_batch_size) // max_workers)
                else:
                    adaptive_batch_size = min(predicted_size, base_batch_size * 2)
                
                batch_size = min(adaptive_batch_size, len(emails)) if emails else base_batch_size
                
                if predicted_size != base_batch_size:
                    logger.info(
                        f"Batch size prediction: {predicted_size} (base: {base_batch_size})",
                        extra={
                            "predicted_size": predicted_size,
                            "base_batch_size": base_batch_size,
                            "final_batch_size": batch_size,
                        }
                    )
                total_batches = (len(emails) + batch_size - 1) // batch_size if emails else 0
                
                logger.info(
                    f"Batch processing configuration",
                    extra={
                        "base_batch_size": base_batch_size,
                        "adaptive_batch_size": adaptive_batch_size,
                        "final_batch_size": batch_size,
                        "total_batches": total_batches,
                        "total_emails": len(emails),
                        "use_parallel": use_parallel,
                        "max_workers": max_workers if use_parallel else 1,
                    }
                )
                
                for batch_num in range(total_batches):
                    batch_start = batch_num * batch_size
                    batch_end = min(batch_start + batch_size, len(emails))
                    batch_emails = emails[batch_start:batch_end]
                    
                    batch_start_time = datetime.utcnow()
                    
                    logger.info(
                        f"Processing batch {batch_num + 1}/{total_batches} ({len(batch_emails)} emails)",
                        extra={
                            "batch_num": batch_num + 1,
                            "total_batches": total_batches,
                            "batch_size": len(batch_emails),
                            "start_idx": batch_start + 1,
                            "end_idx": batch_end,
                            "mode": "parallel" if use_parallel and len(batch_emails) > 1 else "sequential",
                        }
                    )
                    
                    batch_processed = 0
                    batch_failed = 0
                    
                    # Procesar batch (paralelo o secuencial)
                    if use_parallel and len(batch_emails) > 1:
                        # Procesamiento paralelo del batch
                        with ThreadPoolExecutor(max_workers=min(max_workers, len(batch_emails))) as executor:
                            future_to_email = {
                                executor.submit(process_single_email, email_data, batch_start + idx + 1, service): email_data
                                for idx, email_data in enumerate(batch_emails)
                            }
                            
                            for future in as_completed(future_to_email):
                                email_data = future_to_email[future]
                                try:
                                    result = future.result()
                                    
                                    email_id = result['email_id']
                                    email_subject = email_data.get('subject', 'N/A')[:50]
                                    idx = result['email_index']
                                    
                                    if result['skipped']:
                                        skipped += 1
                                        if STATS_AVAILABLE:
                                            try:
                                                Stats.incr("gmail_processor.emails_skipped", 1, tags={"run_id": dag_run_id})
                                            except Exception:
                                                pass
                                        continue
                                    
                                    if result['success']:
                                        processed += 1
                                        batch_processed += 1
                                        _cb_reset("gmail_processor")
                                        
                                        logger.info(
                                            f"Processed email {idx}/{len(emails)}: {email_subject}",
                                            extra={
                                                "email_id": email_id,
                                                "email_index": idx,
                                                "total": len(emails),
                                                "duration_seconds": result['duration_seconds'],
                                                "subject": email_subject,
                                                "batch_num": batch_num + 1,
                                            }
                                        )
                                        
                                        if STATS_AVAILABLE:
                                            try:
                                                Stats.incr("gmail_processor.email.processed", 1, tags={"run_id": dag_run_id})
                                                Stats.timing("gmail_processor.email.duration_seconds", result['duration_seconds'], tags={"run_id": dag_run_id})
                                                Stats.incr("gmail_processor.email.log_success", 1, tags={"run_id": dag_run_id})
                                                if not dry_run:
                                                    Stats.incr("gmail_processor.email.label_success", 1, tags={"run_id": dag_run_id})
                                            except Exception:
                                                pass
                                    else:
                                        # Manejar error
                                        error_type = result.get('error_type', 'unknown')
                                        error_types[error_type] = error_types.get(error_type, 0) + 1
                                        
                                        if error_type == 'log_send_failed':
                                            log_failures += 1
                                            if STATS_AVAILABLE:
                                                try:
                                                    Stats.incr("gmail_processor.email.log_failed", 1, tags={"run_id": dag_run_id})
                                                except Exception:
                                                    pass
                                        elif error_type == 'label_add_failed':
                                            label_failures += 1
                                            if STATS_AVAILABLE:
                                                try:
                                                    Stats.incr("gmail_processor.email.label_failed", 1, tags={"run_id": dag_run_id})
                                                except Exception:
                                                    pass
                                        else:
                                            other_failures += 1
                                            if STATS_AVAILABLE:
                                                try:
                                                    Stats.incr("gmail_processor.email.error", 1, tags={
                                                        "run_id": dag_run_id,
                                                        "error_type": error_type,
                                                    })
                                                except Exception:
                                                    pass
                                        
                                        failed += 1
                                        batch_failed += 1
                                        failed_details.append({
                                            'id': email_id,
                                            'error': result.get('error', 'unknown'),
                                            'error_type': error_type,
                                            'subject': email_subject,
                                        })
                                        
                                        logger.warning(
                                            f"Failed to process email {idx}/{len(emails)}: {email_subject}",
                                            extra={
                                                "email_id": email_id,
                                                "error_type": error_type,
                                                "error": result.get('error', 'unknown'),
                                                "email_index": idx,
                                                "subject": email_subject,
                                            }
                                        )
                                
                                except Exception as e:
                                    other_failures += 1
                                    error_type = type(e).__name__
                                    error_types[error_type] = error_types.get(error_type, 0) + 1
                                    failed += 1
                                    batch_failed += 1
                                    failed_details.append({
                                        'id': email_data.get('id', 'unknown'),
                                        'error': str(e)[:200],
                                        'error_type': error_type,
                                        'subject': email_data.get('subject', 'N/A')[:50],
                                    })
                                    logger.error(
                                        f"Exception processing email: {e}",
                                        extra={
                                            "email_id": email_data.get('id', 'unknown'),
                                            "error_type": error_type,
                                            "error": str(e)[:200],
                                        },
                                        exc_info=True
                                    )
                    else:
                        # Procesamiento secuencial del batch
                        for idx, email_data in enumerate(batch_emails, batch_start + 1):
                            result = process_single_email(email_data, idx, service)
                            
                            email_id = result['email_id']
                            email_subject = email_data.get('subject', 'N/A')[:50]
                            
                            if result['skipped']:
                                skipped += 1
                                logger.debug(f"Email {email_id} already processed, skipping (idempotency)")
                                if STATS_AVAILABLE:
                                    try:
                                        Stats.incr("gmail_processor.emails_skipped", 1, tags={"run_id": dag_run_id})
                                    except Exception:
                                        pass
                                continue
                            
                            if result['success']:
                                processed += 1
                                batch_processed += 1
                                _cb_reset("gmail_processor")
                                
                                logger.info(
                                    f"Processed email {idx}/{len(emails)}: {email_subject}",
                                    extra={
                                        "email_id": email_id,
                                        "email_index": idx,
                                        "total": len(emails),
                                        "duration_seconds": result['duration_seconds'],
                                        "subject": email_subject,
                                        "batch_num": batch_num + 1,
                                    }
                                )
                                
                                if STATS_AVAILABLE:
                                    try:
                                        Stats.incr("gmail_processor.email.processed", 1, tags={"run_id": dag_run_id})
                                        Stats.timing("gmail_processor.email.duration_seconds", result['duration_seconds'], tags={"run_id": dag_run_id})
                                        Stats.incr("gmail_processor.email.log_success", 1, tags={"run_id": dag_run_id})
                                        if not dry_run:
                                            Stats.incr("gmail_processor.email.label_success", 1, tags={"run_id": dag_run_id})
                                    except Exception:
                                        pass
                            else:
                                # Manejar error
                                error_type = result.get('error_type', 'unknown')
                                error_types[error_type] = error_types.get(error_type, 0) + 1
                                
                                if error_type == 'log_send_failed':
                                    log_failures += 1
                                    if STATS_AVAILABLE:
                                        try:
                                            Stats.incr("gmail_processor.email.log_failed", 1, tags={"run_id": dag_run_id})
                                        except Exception:
                                            pass
                                elif error_type == 'label_add_failed':
                                    label_failures += 1
                                    if STATS_AVAILABLE:
                                        try:
                                            Stats.incr("gmail_processor.email.label_failed", 1, tags={"run_id": dag_run_id})
                                        except Exception:
                                            pass
                                else:
                                    other_failures += 1
                                    if STATS_AVAILABLE:
                                        try:
                                            Stats.incr("gmail_processor.email.error", 1, tags={
                                                "run_id": dag_run_id,
                                                "error_type": error_type,
                                            })
                                        except Exception:
                                            pass
                                
                                failed += 1
                                batch_failed += 1
                                failed_details.append({
                                    'id': email_id,
                                    'error': result.get('error', 'unknown'),
                                    'error_type': error_type,
                                    'subject': email_subject,
                                })
                                
                                logger.warning(
                                    f"Failed to process email {idx}/{len(emails)}: {email_subject}",
                                    extra={
                                        "email_id": email_id,
                                        "error_type": error_type,
                                        "error": result.get('error', 'unknown'),
                                        "email_index": idx,
                                        "subject": email_subject,
                                    }
                                )
                    
                    # Calcular estadísticas del batch
                    batch_duration = (datetime.utcnow() - batch_start_time).total_seconds()
                    batch_success_rate = (batch_processed / len(batch_emails) * 100) if batch_emails else 0
                    
                    logger.info(
                        f"Batch {batch_num + 1}/{total_batches} completed: {batch_processed} processed, {batch_failed} failed in {batch_duration:.2f}s",
                        extra={
                            "batch_num": batch_num + 1,
                            "total_batches": total_batches,
                            "batch_processed": batch_processed,
                            "batch_failed": batch_failed,
                            "batch_duration_seconds": round(batch_duration, 2),
                            "batch_success_rate": round(batch_success_rate, 2),
                            "batch_size": len(batch_emails),
                        }
                    )
                    
                    # Delay entre batches para rate limiting
                    if batch_end < len(emails):
                        logger.debug(f"Waiting {GMAIL_BATCH_DELAY}s before next batch")
                        time.sleep(GMAIL_BATCH_DELAY)
                    
                    # Métricas de batch
                    if STATS_AVAILABLE:
                        try:
                            Stats.incr("gmail_processor.batch.completed", 1, tags={
                                "run_id": dag_run_id,
                                "batch_num": str(batch_num + 1),
                            })
                            Stats.gauge("gmail_processor.batch.processed", batch_processed, tags={"run_id": dag_run_id})
                            Stats.gauge("gmail_processor.batch.failed", batch_failed, tags={"run_id": dag_run_id})
                            Stats.timing("gmail_processor.batch.duration_seconds", batch_duration, tags={"run_id": dag_run_id})
                            Stats.gauge("gmail_processor.batch.success_rate", batch_success_rate, tags={"run_id": dag_run_id})
                            
                            # Alertar si tasa de éxito del batch es baja
                            if batch_success_rate < 50 and batch_emails:
                                Stats.incr("gmail_processor.batch.low_success_rate_alert", 1, tags={
                                    "run_id": dag_run_id,
                                    "batch_num": str(batch_num + 1),
                                })
                        except Exception:
                            pass
                
                # Limpiar memoria si es necesario antes de procesar estadísticas
                _cleanup_memory_if_needed()
                
                # Calcular duración y estadísticas
                duration_seconds = (datetime.utcnow() - start_time).total_seconds()
                success_rate = (processed / len(emails) * 100) if emails else 0
                throughput = processed / duration_seconds if duration_seconds > 0 else 0
                
                # Análisis estadístico avanzado
                stats_analysis = _analyze_processing_statistics(
                    processed=processed,
                    failed=failed,
                    skipped=skipped,
                    total=len(emails),
                    duration_seconds=duration_seconds,
                    error_types=error_types
                )
                
                # Monitoreo de memoria final
                final_memory = None
                memory_delta = None
                if MEMORY_MONITORING_ENABLED and initial_memory is not None:
                    try:
                        import psutil
                        import os as os_module
                        process = psutil.Process(os_module.getpid())
                        final_memory = process.memory_info().rss / 1024 / 1024  # MB
                        memory_delta = final_memory - initial_memory
                        
                        logger.info(
                            f"Memory usage: {initial_memory:.2f} MB -> {final_memory:.2f} MB (Δ {memory_delta:+.2f} MB)",
                            extra={
                                "initial_memory_mb": round(initial_memory, 2),
                                "final_memory_mb": round(final_memory, 2),
                                "memory_delta_mb": round(memory_delta, 2),
                            }
                        )
                        
                        if STATS_AVAILABLE:
                            try:
                                Stats.gauge("gmail_processor.memory.final_mb", final_memory)
                                Stats.gauge("gmail_processor.memory.delta_mb", memory_delta)
                                
                                # Alertar si el uso de memoria es alto
                                if final_memory > 500:  # Más de 500 MB
                                    Stats.incr("gmail_processor.memory.high_usage_alert", 1)
                            except Exception:
                                pass
                    except Exception as e:
                        logger.debug(f"Memory monitoring error: {e}")
                
                summary_dict = {
                    "processed": processed,
                    "failed": failed,
                    "skipped": skipped,
                    "total": len(emails),
                    "dry_run": dry_run,
                    "duration_seconds": round(duration_seconds, 2),
                    "success_rate": round(success_rate, 2),
                    "throughput_per_sec": round(throughput, 2),
                    "error_breakdown": {
                        "log_failures": log_failures,
                        "label_failures": label_failures,
                        "other_failures": other_failures,
                        "error_types": error_types,
                    },
                    "failed_details": failed_details[:10],  # Limitar a 10 para no sobrecargar
                    "run_id": dag_run_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "statistics": {
                        "analysis": stats_analysis,
                        "efficiency": round(stats_analysis.get("efficiency", 0), 2),
                        "health_score": round(stats_analysis.get("health_score", 0), 2),
                        "dominant_error": stats_analysis.get("dominant_error"),
                    },
                }
                
                # Agregar métricas de memoria si están disponibles
                if initial_memory is not None and final_memory is not None:
                    summary_dict["memory"] = {
                        "initial_mb": round(initial_memory, 2),
                        "final_mb": round(final_memory, 2),
                        "delta_mb": round(memory_delta, 2) if memory_delta is not None else 0,
                    }
                
                # Validar resumen con Pydantic si está disponible
                if PYDANTIC_AVAILABLE:
                    try:
                        summary = ProcessingSummary(**summary_dict)
                        summary_final = summary.model_dump()
                    except ValidationError as e:
                        logger.warning(f"Summary validation failed: {e}, using raw dict")
                        summary_final = summary_dict
                else:
                    summary_final = summary_dict
                
                # Log estructurado completo
                logger.info(
                    f"Gmail processing completed: {processed} processed, {failed} failed out of {len(emails)} total",
                    extra={
                        "duration_seconds": round(duration_seconds, 2),
                        "duration_ms": int(duration_seconds * 1000),
                        "processed": processed,
                        "failed": failed,
                        "total": len(emails),
                        "success_rate": round(success_rate, 2),
                        "throughput_per_sec": round(throughput, 2),
                        "log_failures": log_failures,
                        "label_failures": label_failures,
                        "other_failures": other_failures,
                        "error_types": error_types,
                        "dry_run": dry_run,
                        "run_id": dag_run_id,
                    }
                )
                
                # Registrar métricas finales detalladas
                if STATS_AVAILABLE:
                    try:
                        tags = {"run_id": dag_run_id, "dry_run": str(dry_run)}
                        
                        # Métricas principales
                        Stats.incr("gmail_processor.emails_processed", processed, tags=tags)
                        Stats.incr("gmail_processor.emails_failed", failed, tags=tags)
                        Stats.incr("gmail_processor.run_completed", 1, tags=tags)
                        Stats.timing("gmail_processor.duration_seconds", duration_seconds, tags=tags)
                        Stats.timing("gmail_processor.duration_ms", int(duration_seconds * 1000), tags=tags)
                        
                        # Métricas de idempotencia
                        if skipped > 0:
                            Stats.incr("gmail_processor.emails_skipped", skipped, tags=tags)
                        
                        # Métricas de tasa
                        if emails:
                            Stats.gauge("gmail_processor.success_rate", success_rate, tags=tags)
                            Stats.gauge("gmail_processor.throughput_per_sec", throughput, tags=tags)
                            
                            # Métricas de análisis estadístico
                            if stats_analysis:
                                Stats.gauge("gmail_processor.efficiency", stats_analysis.get("efficiency", 0), tags=tags)
                                Stats.gauge("gmail_processor.health_score", stats_analysis.get("health_score", 0), tags=tags)
                                Stats.gauge("gmail_processor.avg_time_per_email", stats_analysis.get("avg_time_per_email", 0), tags=tags)
                                
                                # Alertar si tasa de éxito es baja
                                if success_rate < 80 and processed > 0:
                                    Stats.incr("gmail_processor.alert.low_success_rate", 1, tags=tags)
                                
                                # Alertar si health score es bajo
                                health_score = stats_analysis.get("health_score", 0)
                                if health_score < 70:
                                    Stats.incr("gmail_processor.alert.low_health_score", 1, tags=tags)
                        
                        # Métricas de batches
                        Stats.gauge("gmail_processor.total_batches", total_batches, tags=tags)
                        
                        # Alertar si hay muchos fallos
                        if failed > len(emails) * 0.3:  # Más del 30% fallidos
                            Stats.incr("gmail_processor.alert.high_failure_rate", 1, tags=tags)
                        
                        # Reset circuit breaker si el run fue exitoso
                        if processed > 0 and failed == 0:
                            _cb_reset("gmail_processor")
                        
                        # Métricas de errores por tipo
                        for error_type, count in error_types.items():
                            Stats.incr("gmail_processor.errors_by_type", count, tags={
                                **tags,
                                "error_type": error_type,
                            })
                        
                        # Métricas de fallos específicos
                        if log_failures > 0:
                            Stats.incr("gmail_processor.log_failures", log_failures, tags=tags)
                        if label_failures > 0:
                            Stats.incr("gmail_processor.label_failures", label_failures, tags=tags)
                        if other_failures > 0:
                            Stats.incr("gmail_processor.other_failures", other_failures, tags=tags)
                        
                        # Métricas de rendimiento
                        if processed > 0:
                            avg_email_duration = duration_seconds / processed
                            Stats.timing("gmail_processor.avg_email_duration_seconds", avg_email_duration, tags=tags)
                            
                    except Exception as e:
                        logger.debug(f"Error recording final stats: {e}")
                
                # Notificación a Slack si está disponible
                if NOTIFICATIONS_AVAILABLE and os.getenv("ENABLE_SLACK", "false").lower() == "true":
                    try:
                        status_emoji = "✅" if failed == 0 else "⚠️" if processed > 0 else "❌"
                        duration_str = f"{duration_seconds:.1f}s"
                        throughput_str = f"{throughput:.1f}/s" if throughput > 0 else "N/A"
                        
                        # Mensaje mejorado con más detalles
                        message_parts = [
                            f"{status_emoji} *Gmail Processor* completado",
                            f"• Procesados: {processed}",
                            f"• Fallidos: {failed}",
                            f"• Saltados (idemp): {skipped}",
                            f"• Total: {len(emails)}",
                            f"• Tasa éxito: {success_rate:.1f}%",
                            f"• Duración: {duration_str}",
                            f"• Throughput: {throughput_str}",
                            f"• Modo: {'Dry Run' if dry_run else 'Producción'}",
                        ]
                        
                        # Agregar desglose de errores si hay
                        if error_types:
                            error_summary = ", ".join([f"{k}: {v}" for k, v in list(error_types.items())[:3]])
                            message_parts.append(f"• Errores: {error_summary}")
                        
                        message = "\n".join(message_parts)
                        
                        notify_slack(
                            message,
                            extra_context={
                                "dag_id": "gmail_processor",
                                "run_id": dag_run_id,
                                "processed": processed,
                                "failed": failed,
                                "total": len(emails),
                                "success_rate": success_rate,
                                "duration_seconds": duration_seconds,
                                "throughput": throughput,
                                "dry_run": dry_run,
                                "error_types": error_types,
                            },
                            username="Gmail Processor",
                            icon_emoji=":email:"
                        )
                    except Exception as e:
                        logger.warning(f"Failed to send Slack notification: {e}", exc_info=True)
                
                return summary_final


# Generar DAG
gmail_processor()

