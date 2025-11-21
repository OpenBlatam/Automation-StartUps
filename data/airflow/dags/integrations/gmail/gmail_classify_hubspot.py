"""
DAG mejorado para consultar correos nuevos en Gmail, clasificarlos y actualizar HubSpot.

Mejoras implementadas:
- Retry con exponential backoff usando tenacity
- Validación con Pydantic
- Logging estructurado mejorado
- Métricas de Stats
- Cache para búsquedas de contactos
- Mejor manejo de errores y rate limiting
- Integración con notificaciones del stack
- Soporte para variables de entorno del stack
- Context managers para recursos
- Batch processing optimizado
- Circuit Breaker pattern para APIs externas
- Timeouts configurables por operación
- Rate limiting adaptativo
- Validación de schemas de respuesta
- Health checks robustos con validación completa de APIs
- Métricas detalladas de health checks por servicio
- Rate limiting con sliding window por servicio usando Airflow Variables
- Jitter en delays para evitar thundering herd effect
- Rate limiting preventivo antes de cada llamada a API
- Configuración de rate limits por servicio (HubSpot y Gmail)
- Progress tracking con logging periódico del progreso de procesamiento
- Connection pooling optimizado con más conexiones keepalive y mejor configuración
- HTTP session management mejorado con validación de sesiones y recreación automática
"""

from __future__ import annotations

import os
import json
import base64
import re
import logging
import time
from datetime import datetime, timedelta
from time import perf_counter
from typing import Dict, List, Optional, Tuple, Any, TypedDict, Union
from dataclasses import dataclass, field
from functools import lru_cache
from contextlib import contextmanager
from collections import Counter, defaultdict
from email.utils import parseaddr, parsedate_to_datetime

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.models import Variable
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
        before_sleep_log,
        after_log,
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
    from pydantic import BaseModel, Field, ValidationError
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

try:
    from cachetools import TTLCache
    CACHETOOLS_AVAILABLE = True
except ImportError:
    CACHETOOLS_AVAILABLE = False

try:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    CONCURRENT_FUTURES_AVAILABLE = True
except ImportError:
    CONCURRENT_FUTURES_AVAILABLE = False

try:
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_ADAPTER_AVAILABLE = True
except ImportError:
    REQUESTS_ADAPTER_AVAILABLE = False

logger = logging.getLogger(__name__)

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
    logger.warning(
        "Gmail API libraries not available. Install: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
    )

# Importar módulo de HubSpot mejorado
try:
    from hubspot_update_contact import (
        actualizar_propiedad_contacto,
        HubSpotUpdateResult,
        DEFAULT_MAX_RETRIES,
        DEFAULT_TIMEOUT,
    )
    HUBSPOT_MODULE_AVAILABLE = True
except ImportError:
    HUBSPOT_MODULE_AVAILABLE = False
    logger.warning("hubspot_update_contact module not available")
    actualizar_propiedad_contacto = None

# Scopes necesarios para la API de Gmail
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Constantes de configuración para normalización
MAX_SUBJECT_LENGTH = 500
MAX_BODY_LENGTH = 50000
MAX_NOTE_LENGTH = 5000
MIN_CONTACT_ID_LENGTH = 5
EMAIL_VALIDATION_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Constantes para Circuit Breaker
CB_FAILURE_THRESHOLD = int(os.getenv("CB_FAILURE_THRESHOLD", "5"))
CB_RESET_MINUTES = int(os.getenv("CB_RESET_MINUTES", "15"))
CB_KEY_PREFIX = "cb:failures:gmail_classify:"

# Constantes para timeouts configurables (en segundos)
TIMEOUT_GMAIL_SEARCH = int(os.getenv("TIMEOUT_GMAIL_SEARCH", "30"))
TIMEOUT_HUBSPOT_SEARCH = int(os.getenv("TIMEOUT_HUBSPOT_SEARCH", "30"))
TIMEOUT_HUBSPOT_UPDATE = int(os.getenv("TIMEOUT_HUBSPOT_UPDATE", "30"))
TIMEOUT_HUBSPOT_NOTE = int(os.getenv("TIMEOUT_HUBSPOT_NOTE", "30"))
TIMEOUT_HEALTH_CHECK = int(os.getenv("TIMEOUT_HEALTH_CHECK", "10"))

# Constantes para batch processing
NOTE_BATCH_SIZE = int(os.getenv("NOTE_BATCH_SIZE", "10"))
NOTE_BATCH_DELAY = float(os.getenv("NOTE_BATCH_DELAY", "0.5"))

# Constantes para rate limiting adaptativo
RATE_LIMIT_BASE_DELAY = float(os.getenv("RATE_LIMIT_BASE_DELAY", "0.1"))
RATE_LIMIT_MAX_DELAY = float(os.getenv("RATE_LIMIT_MAX_DELAY", "5.0"))
RATE_LIMIT_MAX_JITTER = float(os.getenv("RATE_LIMIT_MAX_JITTER", "0.5"))

# Constantes para rate limiting por servicio (sliding window)
HUBSPOT_RATE_LIMIT_MAX_CALLS = int(os.getenv("HUBSPOT_RATE_LIMIT_MAX_CALLS", "100"))
HUBSPOT_RATE_LIMIT_WINDOW_SEC = int(os.getenv("HUBSPOT_RATE_LIMIT_WINDOW_SEC", "10"))
GMAIL_RATE_LIMIT_MAX_CALLS = int(os.getenv("GMAIL_RATE_LIMIT_MAX_CALLS", "250"))
GMAIL_RATE_LIMIT_WINDOW_SEC = int(os.getenv("GMAIL_RATE_LIMIT_WINDOW_SEC", "100"))

# Cache para contactos de HubSpot (TTL de 1 hora)
_contact_cache: Optional[Any] = None
if CACHETOOLS_AVAILABLE:
    _contact_cache = TTLCache(maxsize=500, ttl=3600)

# Sesión HTTP reutilizable para HubSpot (con retry strategy)
_hubspot_session: Optional[Any] = None

# Excepciones personalizadas
class GmailClassifyError(Exception):
    """Excepción base para errores de clasificación de Gmail."""
    pass


class GmailAuthError(GmailClassifyError):
    """Error de autenticación con Gmail API."""
    pass


class HubSpotAPIError(GmailClassifyError):
    """Error en la respuesta de la API de HubSpot."""
    def __init__(self, message: str, status_code: Optional[int] = None, error_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_data = error_data


class HubSpotValidationError(GmailClassifyError):
    """Error de validación de parámetros."""
    pass


# Funciones de validación y normalización
def _normalize_email(email: str) -> Optional[str]:
    """
    Normaliza y valida un email.
    
    Returns:
        Email normalizado o None si es inválido
    """
    if not email or not isinstance(email, str):
        return None
    
    email = email.strip().lower()
    
    # Validación básica de formato usando constante
    if not re.match(EMAIL_VALIDATION_PATTERN, email):
        return None
    
    return email


def _normalize_text(text: str, max_length: Optional[int] = None) -> str:
    """
    Normaliza texto: trim, limpieza básica.
    
    Args:
        text: Texto a normalizar
        max_length: Longitud máxima (opcional)
    
    Returns:
        Texto normalizado
    """
    if not text or not isinstance(text, str):
        return ""
    
    text = text.strip()
    
    if max_length and len(text) > max_length:
        text = text[:max_length]
        logger.debug(f"Texto truncado a {max_length} caracteres")
    
    return text


def _validate_contact_id(contact_id: str) -> bool:
    """Valida que un contact_id de HubSpot sea válido."""
    if not contact_id or not isinstance(contact_id, str):
        return False
    
    contact_id = contact_id.strip()
    
    # HubSpot IDs son alfanuméricos, típicamente largos
    if not contact_id or len(contact_id) < MIN_CONTACT_ID_LENGTH:
        return False
    
    return True


def _validate_classification(clasificacion: str) -> bool:
    """
    Valida que una clasificación sea válida.
    
    Args:
        clasificacion: Clasificación a validar
    
    Returns:
        True si es válida, False en caso contrario
    """
    valid_classifications = ["Consulta", "Soporte", "Otro"]
    return clasificacion in valid_classifications


# Funciones de Circuit Breaker
def _cb_key(service: str) -> str:
    """Retorna la clave de variable para circuit breaker."""
    return f"{CB_KEY_PREFIX}{service}"


def _cb_is_open(service: str, threshold: int = CB_FAILURE_THRESHOLD, reset_minutes: int = CB_RESET_MINUTES) -> bool:
    """
    Verifica si el circuit breaker está abierto para un servicio.
    
    Args:
        service: Nombre del servicio ('hubspot' o 'gmail')
        threshold: Umbral de fallos
        reset_minutes: Minutos para reset automático
    
    Returns:
        True si está abierto, False si está cerrado
    """
    try:
        key = _cb_key(service)
        data_str = Variable.get(key, default_var=None)
        
        if not data_str:
            return False
        
        data = json.loads(data_str)
        count = int(data.get("count", 0))
        last_failure_ts = int(data.get("last_failure_ts", 0))
        now_ts = int(time.time())
        
        # Reset si ha pasado el tiempo de reset
        if now_ts - last_failure_ts >= (reset_minutes * 60):
            Variable.delete(key)
            logger.info(f"Circuit breaker reset for {service} (timeout expired)")
            return False
        
        is_open = count >= threshold
        if is_open:
            logger.warning(
                f"Circuit breaker OPEN for {service} ({count} failures >= {threshold})",
                extra={"service": service, "failure_count": count, "threshold": threshold}
            )
        return is_open
    except Exception as e:
        logger.debug(f"Circuit breaker check failed for {service}: {e}")
        return False


def _cb_record_failure(service: str) -> None:
    """Registra un fallo en el circuit breaker."""
    try:
        key = _cb_key(service)
        now_ts = int(time.time())
        
        data_str = Variable.get(key, default_var=None)
        if data_str:
            data = json.loads(data_str)
            count = int(data.get("count", 0))
            data = {"count": count + 1, "last_failure_ts": now_ts}
        else:
            data = {"count": 1, "last_failure_ts": now_ts}
        
        Variable.set(key, json.dumps(data))
        logger.debug(f"Recorded failure for {service} (count: {data['count']})", extra={"service": service, "failure_count": data['count']})
    except Exception as e:
        logger.debug(f"Failed to record circuit breaker failure for {service}: {e}")


def _cb_record_success(service: str) -> None:
    """Registra un éxito en el circuit breaker (cierra el breaker si estaba abierto)."""
    try:
        key = _cb_key(service)
        Variable.delete(key)
        logger.debug(f"Circuit breaker closed for {service} (success recorded)")
    except Exception as e:
        logger.debug(f"Failed to record circuit breaker success for {service}: {e}")


def _adaptive_rate_limit_delay(attempt: int, base_delay: float = RATE_LIMIT_BASE_DELAY, max_delay: float = RATE_LIMIT_MAX_DELAY) -> float:
    """
    Calcula un delay adaptativo para rate limiting basado en intentos previos.
    
    Args:
        attempt: Número de intento actual (1-indexed)
        base_delay: Delay base en segundos
        max_delay: Delay máximo en segundos
    
    Returns:
        Delay calculado en segundos
    """
    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
    return delay


def _add_jitter(delay: float, max_jitter: float = RATE_LIMIT_MAX_JITTER) -> float:
    """
    Agrega jitter aleatorio a un delay para evitar thundering herd.
    
    Args:
        delay: Delay base en segundos
        max_jitter: Máximo jitter a agregar en segundos
    
    Returns:
        Delay con jitter agregado
    """
    import random
    jitter = random.uniform(0, min(max_jitter, delay * 0.1))  # Jitter máximo 10% del delay
    return delay + jitter


def _check_rate_limit(service: str, max_calls: int, window_seconds: int) -> bool:
    """
    Verifica rate limit usando sliding window en Airflow Variables.
    
    Args:
        service: Nombre del servicio ('hubspot' o 'gmail')
        max_calls: Máximo de llamadas permitidas en la ventana
        window_seconds: Duración de la ventana en segundos
    
    Returns:
        True si está dentro del límite, False si debe esperar
    """
    try:
        key = f"rate_limit:{service}:gmail_classify"
        now_ts = int(time.time())
        
        data_str = Variable.get(key, default_var=None)
        if data_str:
            data = json.loads(data_str)
            window_start = int(data.get("window_start", 0))
            count = int(data.get("count", 0))
            
            # Reset si la ventana expiró
            if now_ts - window_start >= window_seconds:
                count = 0
                window_start = now_ts
        else:
            count = 0
            window_start = now_ts
        
        # Verificar límite
        if count >= max_calls:
            wait_seconds = window_seconds - (now_ts - window_start)
            if wait_seconds > 0:
                logger.warning(
                    f"Rate limit exceeded for {service}, waiting {wait_seconds}s",
                    extra={
                        "service": service,
                        "calls": count,
                        "max": max_calls,
                        "window_sec": window_seconds,
                        "wait_seconds": wait_seconds
                    }
                )
                
                # Registrar métrica
                if STATS_AVAILABLE:
                    try:
                        Stats.incr(f"gmail_classify_hubspot.rate_limit.{service}.hits", 1)
                    except Exception:
                        pass
                
                # Esperar con jitter
                wait_with_jitter = _add_jitter(float(wait_seconds))
                time.sleep(min(wait_with_jitter, 60))  # Cap a 60s
                
                # Reset después de esperar
                count = 0
                window_start = int(time.time())
        
        # Incrementar y guardar
        count += 1
        Variable.set(key, json.dumps({
            "window_start": window_start,
            "count": count,
        }))
        
        return True
    except Exception as e:
        logger.debug(f"Rate limit check failed for {service}: {e}, proceeding")
        return True  # Continuar si falla la verificación


def _apply_rate_limit(service: str):
    """
    Aplica rate limiting antes de una llamada a API.
    
    Args:
        service: Nombre del servicio ('hubspot' o 'gmail')
    """
    if service == "hubspot":
        _check_rate_limit(service, HUBSPOT_RATE_LIMIT_MAX_CALLS, HUBSPOT_RATE_LIMIT_WINDOW_SEC)
    elif service == "gmail":
        _check_rate_limit(service, GMAIL_RATE_LIMIT_MAX_CALLS, GMAIL_RATE_LIMIT_WINDOW_SEC)


def _health_check_gmail(service: Any, timeout: int = TIMEOUT_HEALTH_CHECK) -> Dict[str, Any]:
    """
    Realiza un health check robusto de la API de Gmail.
    
    Args:
        service: Servicio de Gmail autenticado
        timeout: Timeout para el health check en segundos
    
    Returns:
        Dict con status, message, duration_ms y detalles
    """
    start_time = perf_counter()
    
    try:
        # Verificar perfil del usuario (operación ligera)
        profile = service.users().getProfile(userId="me").execute()
        
        if not isinstance(profile, dict) or "emailAddress" not in profile:
            return {
                "status": "unhealthy",
                "message": "Invalid Gmail profile response",
                "duration_ms": (perf_counter() - start_time) * 1000,
                "details": {"response_type": type(profile).__name__}
            }
        
        duration_ms = (perf_counter() - start_time) * 1000
        
        return {
            "status": "healthy",
            "message": "Gmail API is responding",
            "duration_ms": duration_ms,
            "details": {
                "email": profile.get("emailAddress", "unknown"),
                "messages_total": profile.get("messagesTotal", 0),
                "threads_total": profile.get("threadsTotal", 0),
            }
        }
    except HttpError as e:
        duration_ms = (perf_counter() - start_time) * 1000
        status_code = e.resp.status if hasattr(e, 'resp') else None
        
        return {
            "status": "unhealthy",
            "message": f"Gmail API HTTP error: {str(e)}",
            "duration_ms": duration_ms,
            "details": {
                "status_code": status_code,
                "error_type": "HttpError"
            }
        }
    except Exception as e:
        duration_ms = (perf_counter() - start_time) * 1000
        
        return {
            "status": "unhealthy",
            "message": f"Gmail API health check failed: {str(e)}",
            "duration_ms": duration_ms,
            "details": {
                "error_type": type(e).__name__,
                "error": str(e)
            }
        }


def _health_check_hubspot(timeout: int = TIMEOUT_HEALTH_CHECK) -> Dict[str, Any]:
    """
    Realiza un health check robusto de la API de HubSpot.
    
    Args:
        timeout: Timeout para el health check en segundos
    
    Returns:
        Dict con status, message, duration_ms y detalles
    """
    start_time = perf_counter()
    hubspot_token = os.environ.get("HUBSPOT_TOKEN", "")
    hubspot_base = os.environ.get("HUBSPOT_BASE_URL", "https://api.hubapi.com")
    
    if not hubspot_token:
        return {
            "status": "unhealthy",
            "message": "HUBSPOT_TOKEN not configured",
            "duration_ms": (perf_counter() - start_time) * 1000,
            "details": {}
        }
    
    try:
        # Operación ligera: obtener información básica del portal
        url = f"{hubspot_base}/integrations/v1/me"
        headers = {
            "Authorization": f"Bearer {hubspot_token}",
            "Content-Type": "application/json",
        }
        
        session = _get_hubspot_session()
        
        if session is not None:
            if isinstance(session, httpx.Client):
                timeout_obj = httpx.Timeout(timeout, connect=5.0)
                response = session.get(url, headers=headers, timeout=timeout_obj)
            else:
                response = session.get(url, headers=headers, timeout=timeout)
        else:
            if HTTPX_AVAILABLE:
                timeout_obj = httpx.Timeout(timeout, connect=5.0)
                with httpx.Client(timeout=timeout_obj) as client:
                    response = client.get(url, headers=headers)
            else:
                import requests
                response = requests.get(url, headers=headers, timeout=timeout)
        
        response.raise_for_status()
        data = response.json() if hasattr(response, 'json') else {}
        
        duration_ms = (perf_counter() - start_time) * 1000
        
        if isinstance(data, dict):
            return {
                "status": "healthy",
                "message": "HubSpot API is responding",
                "duration_ms": duration_ms,
                "details": {
                    "portal_id": data.get("portalId", "unknown"),
                    "time_zone": data.get("timeZone", "unknown"),
                }
            }
        else:
            return {
                "status": "healthy",
                "message": "HubSpot API is responding",
                "duration_ms": duration_ms,
                "details": {}
            }
    except Exception as e:
        duration_ms = (perf_counter() - start_time) * 1000
        
        status_code = None
        if HTTPX_AVAILABLE and isinstance(e, httpx.HTTPStatusError):
            status_code = e.response.status_code
        elif hasattr(e, 'response') and hasattr(e.response, 'status_code'):
            status_code = e.response.status_code
        
        return {
            "status": "unhealthy",
            "message": f"HubSpot API health check failed: {str(e)}",
            "duration_ms": duration_ms,
            "details": {
                "status_code": status_code,
                "error_type": type(e).__name__,
                "error": str(e)
            }
        }


# Palabras clave para clasificación
CONSULTA_KEYWORDS = [
    "consulta",
    "pregunta",
    "información",
    "info",
    "quiero saber",
    "cotización",
    "precio",
    "costo",
    "tarifa",
    "planes",
    "servicios",
    "productos",
    "demo",
    "demostración",
    "interesado",
    "interés",
    "oportunidad",
    "solicitud",
]

SOPORTE_KEYWORDS = [
    "soporte",
    "ayuda",
    "problema",
    "error",
    "no funciona",
    "falla",
    "bug",
    "issue",
    "incidente",
    "técnico",
    "asistencia",
    "urgencia",
    "urgente",
    "reclamo",
    "queja",
    "mal funcionamiento",
    "ticket",
    "solución",
]

# Modelos Pydantic para validación
if PYDANTIC_AVAILABLE:
    class EmailData(BaseModel):
        """Modelo de datos de email con validación."""
        message_id: str = Field(..., description="ID del mensaje")
        subject: str = Field(default="(Sin asunto)", description="Asunto")
        body: str = Field(default="", description="Cuerpo del correo")
        sender_email: str = Field(..., description="Email del remitente")
        from_header: str = Field(..., alias="from", description="Header From completo")
        date: str = Field(..., description="Fecha del correo")
        
        class Config:
            populate_by_name = True
    
    class ClassificationResult(BaseModel):
        """Resultado de clasificación."""
        email: str = Field(..., description="Email del remitente")
        clasificacion: str = Field(..., description="Clasificación (Consulta/Soporte/Otro)")
        hubspot_id: Optional[str] = Field(None, description="ID del contacto en HubSpot")
        estado: str = Field(..., description="Estado de la operación")
        duration_ms: Optional[float] = Field(None, description="Duración en ms")
        
    class ProcessingSummary(BaseModel):
        """Resumen del procesamiento."""
        processed: int = Field(..., ge=0, description="Correos procesados")
        failed: int = Field(..., ge=0, description="Correos fallidos")
        skipped: int = Field(default=0, ge=0, description="Correos saltados (idempotencia)")
        total: int = Field(..., ge=0, description="Total de correos")
        success_rate: float = Field(..., ge=0.0, le=100.0, description="Tasa de éxito %")
        throughput_per_sec: float = Field(default=0.0, ge=0.0, description="Throughput por segundo")
        dry_run: bool = Field(..., description="Modo dry run")
        results: List[ClassificationResult] = Field(default_factory=list)
        duration_ms: Optional[float] = Field(None, description="Duración total en ms")
        duration_seconds: Optional[float] = Field(None, description="Duración total en segundos")
        error_breakdown: Dict[str, Any] = Field(default_factory=dict, description="Desglose de errores")
        run_id: Optional[str] = Field(None, description="Run ID de Airflow")
        timestamp: Optional[str] = Field(None, description="Timestamp ISO format")
else:
    # Fallback sin Pydantic
    EmailData = Dict[str, Any]
    ClassificationResult = Dict[str, Any]
    ProcessingSummary = Dict[str, Any]


@dag(
    dag_id="gmail_classify_hubspot",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="*/30 * * * *",  # Cada 30 minutos
    catchup=False,
    default_args={
        "owner": "support",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=30),
        "depends_on_past": False,
    },
    doc_md="""
    ### Clasificación de Correos Gmail → HubSpot (Mejorado)
    
    DAG que procesa correos nuevos en Gmail, los clasifica automáticamente y actualiza HubSpot:
    1. Consulta correos nuevos no leídos (últimas 24 horas)
    2. Clasifica cada correo como 'Consulta', 'Soporte' o 'Otro'
    3. Busca el contacto en HubSpot por email (con cache)
    4. Actualiza la propiedad 'tipo_solicitud' del contacto (con retry y rate limiting)
    5. Crea una nota en HubSpot con la clasificación
    
    **Configuración:**
    - Las credenciales se cargan desde variables de entorno (configuradas en values.yaml)
    - Variables de entorno: GMAIL_CREDENTIALS_JSON, GMAIL_TOKEN_JSON, HUBSPOT_TOKEN, etc.
    - Los parámetros pueden sobreescribir las variables de entorno si se proporcionan
    
    **Parámetros opcionales (sobreescriben variables de entorno):**
    - `gmail_credentials_json`: JSON string con credenciales OAuth2 de Gmail
    - `gmail_token_json`: JSON string con token almacenado
    - `max_emails`: Máximo de correos a procesar por ejecución (default: 10)
    - `max_workers`: Número de workers para procesamiento paralelo (0=secuencial, default: 0)
    - `dry_run`: Solo simular sin modificar HubSpot
    
    **Mejoras implementadas:**
    - Procesamiento paralelo opcional con ThreadPoolExecutor
    - Sesiones HTTP reutilizables con retry strategy (HTTPAdapter)
    - Health check básico de Gmail API
    - Retry automático con exponential backoff
    - Cache de contactos de HubSpot (TTL 1h, LRU)
    - Validación y normalización mejoradas de inputs
    - Clasificación mejorada con scoring ponderado y limpieza de texto
    - Validación con Pydantic
    - Métricas de Stats con tags (run_id, dry_run, parallel)
    - Logging estructurado mejorado
    - Notificaciones a Slack con detalles completos
    - Rate limiting inteligente
    - Error breakdown detallado por tipo
    - Throughput tracking
    - Execution timeout (15 min)
    - Connection pooling para mejor performance
    - Excepciones personalizadas para mejor manejo de errores (GmailClassifyError, HubSpotAPIError, HubSpotValidationError)
    - Funciones de validación robustas (_validate_classification, _validate_contact_id)
    - Normalización de emails y texto con límites configurables
    - Manejo diferenciado de errores por tipo (validación, API, rate limiting)
    - Clasificación mejorada con resolución de empates (prioriza Soporte)
    - **Circuit Breaker pattern** para Gmail y HubSpot APIs (protección contra cascading failures)
    - **Timeouts configurables** por operación (búsqueda, actualización, notas)
    - **Rate limiting adaptativo** con backoff exponencial
    - **Validación de schemas** de respuesta de APIs
    - **Batch processing optimizado** para notas (configurable)
    - **Health checks robustos** con validación completa de APIs y métricas detalladas
    - **Métricas de health checks** con duración y estado por servicio
    - **Rate limiting con sliding window** por servicio usando Airflow Variables
    - **Jitter en delays** para evitar thundering herd effect
    - **Rate limiting preventivo** antes de cada llamada a API
    - **Configuración de rate limits** por servicio (HubSpot y Gmail)
    - **Progress tracking** con logging periódico del progreso de procesamiento
    - **Connection pooling optimizado** con más conexiones keepalive y mejor configuración
    - **HTTP session management mejorado** con validación de sesiones y recreación automática
    """,
    params={
        "gmail_credentials_json": Param("", type="string"),
        "gmail_token_json": Param("", type="string"),
        "max_emails": Param(0, type="integer", minimum=0, maximum=50),  # 0 = usar env
        "max_workers": Param(0, type="integer", minimum=0, maximum=10),  # 0 = usar env o secuencial
        "dry_run": Param(False, type="boolean"),
    },
    tags=["gmail", "hubspot", "classification", "support", "automation"],
)
def gmail_classify_hubspot() -> None:
    """
    DAG principal mejorado para clasificar correos de Gmail y actualizar HubSpot.
    """
    
    @contextmanager
    def gmail_service_context(credentials_json: str, token_json: str):
        """Context manager para el servicio de Gmail API."""
        service = get_gmail_service(credentials_json, token_json)
        try:
            yield service
        finally:
            # Cleanup si es necesario
            pass
    
    def get_gmail_service(credentials_json: str, token_json: str) -> Any:
        """
        Autentica y retorna el servicio de Gmail API.
        Reutiliza el patrón de autenticación de gmail_processor.py
        """
        if not GMAIL_API_AVAILABLE:
            raise AirflowFailException(
                "Gmail API libraries not available. Install required packages."
            )

        creds = None

        # Cargar token si existe
        if token_json:
            try:
                if os.path.isfile(token_json):
                    with open(token_json, "r") as token_file:
                        token_data = json.load(token_file)
                else:
                    token_data = json.loads(token_json)
                creds = Credentials.from_authorized_user_info(token_data, SCOPES)
            except Exception as e:
                logger.warning(f"Could not load token: {e}")

        # Si no hay credenciales válidas, intentar refrescar o solicitar autorización
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Token refreshed successfully")
                except Exception as e:
                    logger.warning(
                        f"Token refresh failed: {e}. New authorization may be required."
                    )
                    creds = None

            # Si aún no hay credenciales válidas, cargar credenciales y autorizar
            if not creds or not creds.valid:
                try:
                    if os.path.isfile(credentials_json):
                        with open(credentials_json, "r") as creds_file:
                            creds_data = json.load(creds_file)
                    else:
                        creds_data = json.loads(credentials_json)

                    flow = InstalledAppFlow.from_client_config(creds_data, SCOPES)
                    creds = flow.run_local_server(port=0)
                    logger.info("New OAuth authorization completed")
                except Exception as e:
                    logger.error(f"Failed to get credentials: {e}")
                    raise AirflowFailException(
                        f"Gmail authentication error: {e}. "
                        "If in production, ensure a valid token exists or run initial authorization."
                    )

            # Guardar token actualizado
            if creds and token_json:
                try:
                    token_data = json.loads(creds.to_json())
                    if os.path.isfile(token_json):
                        with open(token_json, "w") as token_file:
                            json.dump(token_data, token_file, indent=2)
                    logger.debug("Token saved successfully")
                except Exception as e:
                    logger.warning(f"Could not save token: {e}")

        return build("gmail", "v1", credentials=creds)

    def classify_email(subject: str, body: str) -> str:
        """
        Clasifica un correo como 'Consulta', 'Soporte' o 'Otro'.
        Mejora: Scoring más sofisticado con ponderación y normalización.
        """
        # Normalizar inputs con límites razonables usando constantes
        subject = _normalize_text(subject or "", max_length=MAX_SUBJECT_LENGTH)
        body = _normalize_text(body or "", max_length=MAX_BODY_LENGTH)
        
        # Si no hay contenido, retornar 'Otro'
        if not subject and not body:
            logger.debug("Email sin contenido para clasificar")
            return "Otro"
        
        text = f"{subject} {body}".lower()
        
        # Limpiar texto básico (remover URLs, emails comunes, etc.)
        text = re.sub(r'http[s]?://\S+', '', text)  # Remover URLs
        text = re.sub(r'\S+@\S+', '', text)  # Remover emails en el cuerpo
        text = re.sub(r'\s+', ' ', text)  # Normalizar espacios múltiples
        text = text.strip()

        # Scoring con ponderación (palabras más relevantes tienen más peso)
        consulta_score = 0
        soporte_score = 0
        
        # Palabras clave de alta relevancia (peso 2)
        alta_relevancia_consulta = ["cotización", "demo", "precio", "planes", "interesado"]
        alta_relevancia_soporte = ["problema", "error", "no funciona", "urgente", "incidente"]
        
        for keyword in CONSULTA_KEYWORDS:
            count = text.count(keyword)
            if count > 0:
                peso = 2 if keyword in alta_relevancia_consulta else 1
                consulta_score += peso * min(count, 3)  # Limitar a 3 ocurrencias
        
        for keyword in SOPORTE_KEYWORDS:
            count = text.count(keyword)
            if count > 0:
                peso = 2 if keyword in alta_relevancia_soporte else 1
                soporte_score += peso * min(count, 3)  # Limitar a 3 ocurrencias

        # Clasificar basado en scores (umbral mínimo para evitar falsos positivos)
        # Si hay empate, priorizar Soporte (más crítico)
        if soporte_score > consulta_score and soporte_score >= 2:
            return "Soporte"
        elif consulta_score > soporte_score and consulta_score >= 1:
            return "Consulta"
        elif soporte_score == consulta_score and soporte_score >= 2:
            # Empate: priorizar Soporte
            return "Soporte"
        else:
            return "Otro"

    @lru_cache(maxsize=100)
    def _find_hubspot_contact_cached(email: str) -> Optional[str]:
        """
        Caché LRU para búsquedas de contactos (helper interno).
        """
        return _find_hubspot_contact_impl(email)
    
    def _get_hubspot_session():
        """Obtiene o crea una sesión HTTP reutilizable para HubSpot con retry strategy."""
        global _hubspot_session
        
        if _hubspot_session is not None:
            # Verificar que la sesión aún es válida
            try:
                if isinstance(_hubspot_session, httpx.Client):
                    # httpx clients son válidos hasta que se cierren
                    return _hubspot_session
                elif hasattr(_hubspot_session, 'get'):
                    # requests.Session es válida
                    return _hubspot_session
            except Exception:
                # Si hay error, recrear sesión
                _hubspot_session = None
        
        if HTTPX_AVAILABLE:
            # Sesión httpx con límites y timeout optimizados
            limits = httpx.Limits(
                max_keepalive_connections=10,  # Más conexiones keepalive para mejor performance
                max_connections=20,  # Más conexiones totales
                keepalive_expiry=30.0  # Mantener conexiones vivas por 30s
            )
            timeout = httpx.Timeout(30.0, connect=10.0, read=30.0, write=10.0, pool=5.0)
            _hubspot_session = httpx.Client(
                limits=limits,
                timeout=timeout,
                follow_redirects=True,
                http2=False,  # HTTP/2 puede causar problemas con algunos proxies
            )
            logger.debug("HubSpot HTTP session created (httpx)")
        elif REQUESTS_ADAPTER_AVAILABLE:
            import requests
            session = requests.Session()
            
            # Retry strategy mejorada con jitter
            retry_strategy = Retry(
                total=3,
                backoff_factor=1.0,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET", "POST", "PUT", "PATCH"],
                raise_on_status=False,
            )
            adapter = HTTPAdapter(
                max_retries=retry_strategy,
                pool_connections=10,  # Pool de conexiones
                pool_maxsize=20,  # Más conexiones en el pool
                pool_block=False  # No bloquear si el pool está lleno
            )
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            _hubspot_session = session
            logger.debug("HubSpot HTTP session created (requests)")
        else:
            # Fallback sin sesión reutilizable
            _hubspot_session = None
        
        return _hubspot_session
    
    def _find_hubspot_contact_impl(email: str) -> Optional[str]:
        """
        Implementación interna para buscar contacto en HubSpot.
        Usa sesión HTTP reutilizable si está disponible.
        """
        hubspot_token = os.environ.get("HUBSPOT_TOKEN", "")
        hubspot_base = os.environ.get("HUBSPOT_BASE_URL", "https://api.hubapi.com")

        if not hubspot_token:
            logger.warning("HUBSPOT_TOKEN no configurado")
            return None

        # Normalizar y validar email antes de buscar
        normalized_email = _normalize_email(email)
        if not normalized_email:
            logger.warning("Email inválido para búsqueda en HubSpot", extra={"email": email[:50] if email else None})
            return None

        url = f"{hubspot_base}/crm/v3/objects/contacts/search"
        headers = {
            "Authorization": f"Bearer {hubspot_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "filterGroups": [
                {"filters": [{"propertyName": "email", "operator": "EQ", "value": normalized_email}]}
            ],
            "properties": ["email", "firstname", "lastname"],
        }

        # Circuit breaker check
        if _cb_is_open("hubspot"):
            logger.warning("Circuit breaker OPEN for HubSpot, skipping contact search", extra={"email": normalized_email})
            return None
        
        # Rate limiting antes de la llamada
        _apply_rate_limit("hubspot")
        
        try:
            session = _get_hubspot_session()
            
            timeout_config = TIMEOUT_HUBSPOT_SEARCH
            
            if session is not None:
                # Usar sesión reutilizable
                if isinstance(session, httpx.Client):
                    timeout_obj = httpx.Timeout(timeout_config, connect=10.0)
                    response = session.post(url, headers=headers, json=payload, timeout=timeout_obj)
                    response.raise_for_status()
                    data = response.json()
                else:
                    # requests.Session
                    response = session.post(url, headers=headers, json=payload, timeout=timeout_config)
                    response.raise_for_status()
                    data = response.json()
            else:
                # Fallback: crear cliente temporal
                if HTTPX_AVAILABLE:
                    timeout_obj = httpx.Timeout(timeout_config, connect=10.0)
                    with httpx.Client(timeout=timeout_obj) as client:
                        response = client.post(url, headers=headers, json=payload)
                        response.raise_for_status()
                        data = response.json()
                else:
                    import requests
                    response = requests.post(url, headers=headers, json=payload, timeout=timeout_config)
                    response.raise_for_status()
                    data = response.json()
            
            # Validar schema de respuesta
            if not isinstance(data, dict) or "results" not in data:
                logger.warning(f"Invalid HubSpot response schema: {type(data)}", extra={"email": normalized_email})
                return None
            
            # Registrar éxito en circuit breaker
            _cb_record_success("hubspot")

            results = data.get("results", [])
            if results:
                contact_id = results[0]["id"]
                if _validate_contact_id(contact_id):
                    return contact_id
                else:
                    logger.warning(f"Contact ID inválido recibido de HubSpot: {contact_id}", extra={"email": normalized_email})
                    return None

            return None
        except Exception as e:
            # Registrar fallo en circuit breaker
            _cb_record_failure("hubspot")
            
            # Detectar si es HTTPError de requests
            if HTTPX_AVAILABLE and isinstance(e, httpx.HTTPStatusError):
                status_code = e.response.status_code
                error_msg = f"HTTP error buscando contacto en HubSpot: {e}"
                logger.error(error_msg, extra={"email": normalized_email, "status_code": status_code})
                if status_code == 429:
                    logger.warning("Rate limit excedido en HubSpot, retornando None para reintento posterior")
                    return None
                elif status_code in [401, 403]:
                    logger.error("Error de autenticación en HubSpot")
                    return None
                return None
            elif hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                # requests.exceptions.HTTPError
                status_code = e.response.status_code
                error_msg = f"HTTP error buscando contacto en HubSpot: {e}"
                logger.error(error_msg, extra={"email": normalized_email, "status_code": status_code})
                if status_code == 429:
                    logger.warning("Rate limit excedido en HubSpot, retornando None para reintento posterior")
                    return None
                elif status_code in [401, 403]:
                    logger.error("Error de autenticación en HubSpot")
                    return None
                return None
            status_code = e.response.status_code if hasattr(e, 'response') and e.response else None
            error_msg = f"HTTP error buscando contacto en HubSpot: {e}"
            logger.error(error_msg, extra={"email": normalized_email, "status_code": status_code})
            if status_code == 429:
                raise HubSpotAPIError("Rate limit excedido en HubSpot", status_code=429)
            elif status_code in [401, 403]:
                raise HubSpotAPIError("Error de autenticación en HubSpot", status_code=status_code)
            raise HubSpotAPIError(error_msg, status_code=status_code)
        except Exception as e:
            logger.error(f"Error buscando contacto en HubSpot: {e}", extra={"email": normalized_email})
            if isinstance(e, HubSpotAPIError):
                raise
            raise HubSpotAPIError(f"Error inesperado buscando contacto: {str(e)}")
    
    def find_hubspot_contact(email: str) -> Optional[str]:
        """
        Busca un contacto en HubSpot por email y retorna su ID.
        Usa cache si está disponible.
        """
        if _contact_cache is not None and email in _contact_cache:
            return _contact_cache[email]
        
        contact_id = _find_hubspot_contact_impl(email)
        
        if _contact_cache is not None and contact_id:
            _contact_cache[email] = contact_id
        
        return contact_id

    def update_hubspot_contact_and_note(
        contact_id: str, tipo_solicitud: str, nota: str, dry_run: bool = False
    ) -> Tuple[bool, str, Optional[float]]:
        """
        Actualiza la propiedad 'tipo_solicitud' de un contacto en HubSpot y crea una nota.
        Mejora: Usa módulo mejorado de HubSpot con retry y rate limiting.
        
        Raises:
            HubSpotValidationError: Si los parámetros son inválidos
        """
        # Validar inputs
        if not _validate_contact_id(contact_id):
            raise HubSpotValidationError(f"contact_id inválido: {contact_id}")
        
        if not _validate_classification(tipo_solicitud):
            raise HubSpotValidationError(f"tipo_solicitud inválido: {tipo_solicitud}")
        
        # Normalizar nota usando constante
        nota = _normalize_text(nota or "", max_length=MAX_NOTE_LENGTH)
        if not nota:
            logger.warning("nota vacía después de normalización, no se creará")
        
        if dry_run:
            logger.info(
                f"[DRY RUN] Would update contact {contact_id} with tipo_solicitud={tipo_solicitud}"
            )
            return (True, "Dry run: actualización simulada", None)

        start_time = perf_counter()

        # Usar módulo mejorado de HubSpot si está disponible
        if HUBSPOT_MODULE_AVAILABLE:
            try:
                result = actualizar_propiedad_contacto(
                    hubspot_contact_id=contact_id,
                    propiedad="tipo_solicitud",
                    valor=tipo_solicitud,
                    max_retries=DEFAULT_MAX_RETRIES,
                    timeout=DEFAULT_TIMEOUT,
                    return_result_object=True,
                )
                
                if isinstance(result, HubSpotUpdateResult):
                    if not result.success:
                        return (False, result.message, result.duration_ms)
                    
                    # Si la actualización fue exitosa, crear nota
                    duration_ms = result.duration_ms or ((perf_counter() - start_time) * 1000)
                    
                    # Crear nota (puede fallar sin afectar la actualización)
                    note_success = _create_hubspot_note(contact_id, nota)
                    if note_success:
                        return (True, "Contacto actualizado y nota creada", duration_ms)
                    else:
                        return (True, "Contacto actualizado (nota falló)", duration_ms)
                else:
                    # Fallback si retorna string
                    if result == "Éxito":
                        duration_ms = (perf_counter() - start_time) * 1000
                        _create_hubspot_note(contact_id, nota)
                        return (True, "Contacto actualizado y nota creada", duration_ms)
                    else:
                        return (False, result, (perf_counter() - start_time) * 1000)
            except HubSpotValidationError:
                # No hacer fallback para errores de validación
                raise
            except Exception as e:
                logger.error(f"Error en actualización mejorada de HubSpot: {e}", exc_info=True)
                # Fallback a implementación básica solo para errores no críticos
                if isinstance(e, HubSpotAPIError) and e.status_code in [401, 403]:
                    # Errores de autenticación no deben hacer fallback
                    raise
        
        # Implementación básica (fallback)
        hubspot_token = os.environ.get("HUBSPOT_TOKEN", "")
        hubspot_base = os.environ.get("HUBSPOT_BASE_URL", "https://api.hubapi.com")

        if not hubspot_token:
            return (False, "HUBSPOT_TOKEN no configurado", None)

        try:
            if HTTPX_AVAILABLE:
                client = httpx.Client(timeout=30.0)
                try:
                    headers = {
                        "Authorization": f"Bearer {hubspot_token}",
                        "Content-Type": "application/json",
                    }
                    url = f"{hubspot_base}/crm/v3/objects/contacts/{contact_id}"
                    payload = {"properties": {"tipo_solicitud": tipo_solicitud}}
                    
                    response = client.patch(url, headers=headers, json=payload)
                    response.raise_for_status()
                    
                    _create_hubspot_note(contact_id, nota)
                    duration_ms = (perf_counter() - start_time) * 1000
                    return (True, "Contacto actualizado y nota creada", duration_ms)
                finally:
                    client.close()
            else:
                # Usar sesión reutilizable si está disponible
                session = _get_hubspot_session()
                if session is not None and not isinstance(session, httpx.Client):
                    # requests.Session
                    response = session.patch(url, headers=headers, json=payload, timeout=30)
                    response.raise_for_status()
                else:
                    import requests
                    response = requests.patch(url, headers=headers, json=payload, timeout=30)
                    response.raise_for_status()
                
                _create_hubspot_note(contact_id, nota)
                duration_ms = (perf_counter() - start_time) * 1000
                return (True, "Contacto actualizado y nota creada", duration_ms)
        except HubSpotValidationError:
            raise  # Re-lanzar errores de validación
        except Exception as e:
            logger.error(
                f"Error actualizando contacto en HubSpot: {e}",
                extra={"contact_id": contact_id},
                exc_info=True
            )
            duration_ms = (perf_counter() - start_time) * 1000
            
            # Clasificar error para mejor reporting
            if HTTPX_AVAILABLE and isinstance(e, httpx.HTTPStatusError):
                status_code = e.response.status_code
                if status_code == 429:
                    return (False, "Rate limit excedido en HubSpot", duration_ms)
                elif status_code in [401, 403]:
                    return (False, f"Error de autenticación en HubSpot (status {status_code})", duration_ms)
                else:
                    return (False, f"Error HTTP {status_code}: {str(e)}", duration_ms)
            elif hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                status_code = e.response.status_code
                if status_code == 429:
                    return (False, "Rate limit excedido en HubSpot", duration_ms)
                elif status_code in [401, 403]:
                    return (False, f"Error de autenticación en HubSpot (status {status_code})", duration_ms)
                else:
                    return (False, f"Error HTTP {status_code}: {str(e)}", duration_ms)
            
            return (False, f"Error: {str(e)}", duration_ms)
    
    def _create_hubspot_note(contact_id: str, nota: str) -> bool:
        """
        Crea una nota en HubSpot asociada al contacto.
        Retorna True si se creó exitosamente, False en caso contrario.
        Usa sesión HTTP reutilizable si está disponible.
        """
        hubspot_token = os.environ.get("HUBSPOT_TOKEN", "")
        hubspot_base = os.environ.get("HUBSPOT_BASE_URL", "https://api.hubapi.com")
        
        if not hubspot_token:
            return False
        
        # Validar contact_id
        if not _validate_contact_id(contact_id):
            logger.warning("contact_id inválido para crear nota", extra={"contact_id": contact_id[:50] if contact_id else None})
            return False
        
        # Normalizar nota usando constante
        nota_normalized = _normalize_text(nota, max_length=MAX_NOTE_LENGTH)
        if not nota_normalized:
            logger.warning("nota vacía después de normalización, no se creará")
            return False
        
        # Circuit breaker check
        if _cb_is_open("hubspot"):
            logger.warning("Circuit breaker OPEN for HubSpot, skipping note creation", extra={"contact_id": contact_id})
            return False
        
        # Rate limiting antes de la llamada
        _apply_rate_limit("hubspot")
        
        try:
            url_note = f"{hubspot_base}/crm/v3/objects/notes"
            headers = {
                "Authorization": f"Bearer {hubspot_token}",
                "Content-Type": "application/json",
            }
            payload_note = {
                "properties": {"hs_note_body": nota_normalized},
                "associations": [
                    {
                        "to": {"id": contact_id},
                        "types": [
                            {
                                "associationCategory": "HUBSPOT_DEFINED",
                                "associationTypeId": 214,  # Note to Contact association
                            }
                        ],
                    }
                ],
            }
            
            timeout_config = TIMEOUT_HUBSPOT_NOTE
            session = _get_hubspot_session()
            
            if session is not None:
                # Usar sesión reutilizable
                if isinstance(session, httpx.Client):
                    timeout_obj = httpx.Timeout(timeout_config, connect=10.0)
                    response = session.post(url_note, headers=headers, json=payload_note, timeout=timeout_obj)
                    response.raise_for_status()
                else:
                    # requests.Session
                    response = session.post(url_note, headers=headers, json=payload_note, timeout=timeout_config)
                    response.raise_for_status()
            else:
                # Fallback: crear cliente temporal
                if HTTPX_AVAILABLE:
                    timeout_obj = httpx.Timeout(timeout_config, connect=10.0)
                    with httpx.Client(timeout=timeout_obj) as client:
                        response = client.post(url_note, headers=headers, json=payload_note)
                        response.raise_for_status()
                else:
                    import requests
                    response = requests.post(url_note, headers=headers, json=payload_note, timeout=timeout_config)
                    response.raise_for_status()
            
            # Validar schema de respuesta
            try:
                if hasattr(response, 'json'):
                    data = response.json()
                    if isinstance(data, dict) and ("id" in data or "status" in data):
                        # Respuesta válida
                        _cb_record_success("hubspot")
                        logger.info(f"Nota creada exitosamente para contacto {contact_id}")
                        return True
                    else:
                        logger.warning(f"Invalid note creation response schema: {type(data)}", extra={"contact_id": contact_id})
                        return False
                else:
                    # Si no hay método json(), asumir éxito por status code
                    _cb_record_success("hubspot")
                    logger.info(f"Nota creada exitosamente para contacto {contact_id}")
                    return True
            except Exception as schema_error:
                logger.warning(f"Could not validate note response schema: {schema_error}", extra={"contact_id": contact_id})
                # Asumir éxito si el status code fue OK
                _cb_record_success("hubspot")
                return True
        except Exception as e:
            # Registrar fallo en circuit breaker
            _cb_record_failure("hubspot")
            
            logger.warning(f"No se pudo crear nota para contacto {contact_id}: {e}", extra={"contact_id": contact_id}, exc_info=True)
            return False

    def get_new_emails(service: Any, max_results: int = 10) -> List[Dict]:
        """
        Obtiene correos nuevos no leídos desde Gmail (últimas 24 horas).
        Mejora: Mejor parsing de headers y validación.
        """
        # Circuit breaker check
        if _cb_is_open("gmail"):
            logger.warning("Circuit breaker OPEN for Gmail, skipping email fetch")
            return []
        
        # Rate limiting antes de la llamada
        _apply_rate_limit("gmail")
        
        try:
            query = "is:unread newer_than:1d"

            results = (
                service.users()
                .messages()
                .list(userId="me", q=query, maxResults=max_results)
                .execute()
            )
            
            # Validar schema de respuesta
            if not isinstance(results, dict) or "messages" not in results:
                logger.warning(f"Invalid Gmail response schema: {type(results)}")
                return []
            
            # Registrar éxito en circuit breaker
            _cb_record_success("gmail")

            messages = results.get("messages", [])
            emails = []

            for msg in messages:
                try:
                    message = (
                        service.users()
                        .messages()
                        .get(userId="me", id=msg["id"], format="full")
                        .execute()
                    )

                    headers = message["payload"].get("headers", [])
                    header_dict = {h["name"].lower(): h["value"] for h in headers}
                    
                    subject = header_dict.get("subject", "(Sin asunto)") or "(Sin asunto)"
                    from_raw = header_dict.get("from", "")
                    _, sender_email = parseaddr(from_raw)
                    
                    if not sender_email:
                        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", from_raw)
                        sender_email = email_match.group(0) if email_match else ""
                    
                    date_raw = header_dict.get("date", "")
                    try:
                        if date_raw:
                            parsed_date = parsedate_to_datetime(date_raw)
                            date_str = parsed_date.isoformat()
                        else:
                            date_str = message.get("internalDate", "")
                    except (ValueError, TypeError):
                        date_str = message.get("internalDate", "")

                    # Obtener cuerpo del mensaje
                    body = ""
                    if "parts" in message["payload"]:
                        for part in message["payload"]["parts"]:
                            if part["mimeType"] == "text/plain":
                                data = part["body"].get("data")
                                if data:
                                    body = base64.urlsafe_b64decode(data).decode(
                                        "utf-8", errors="ignore"
                                    )
                                    break
                            elif part["mimeType"] == "text/html":
                                data = part["body"].get("data")
                                if data:
                                    body = base64.urlsafe_b64decode(data).decode(
                                        "utf-8", errors="ignore"
                                    )
                                    body = re.sub(r"<[^>]+>", "", body)
                                    break
                    else:
                        if message["payload"]["body"].get("data"):
                            data = message["payload"]["body"]["data"]
                            body = base64.urlsafe_b64decode(data).decode(
                                "utf-8", errors="ignore"
                            )

                    email_dict = {
                        "message_id": msg["id"],
                        "subject": subject,
                        "body": body,
                        "sender_email": sender_email,
                        "from": from_raw,
                        "date": date_str,
                    }
                    
                    # Validar con Pydantic si está disponible
                    if PYDANTIC_AVAILABLE:
                        try:
                            email_data = EmailData(**email_dict)
                            emails.append(email_data.model_dump(by_alias=True))
                        except ValidationError as e:
                            logger.warning(f"Email data validation failed for {msg['id']}: {e}")
                            emails.append(email_dict)
                    else:
                        emails.append(email_dict)
                except Exception as e:
                    logger.warning(f"Error procesando mensaje {msg.get('id')}: {e}")
                    continue

            return emails
        except HttpError as e:
            # Registrar fallo en circuit breaker
            _cb_record_failure("gmail")
            
            logger.error(f"Error consultando Gmail: {e}", exc_info=True)
            raise
        except Exception as e:
            # Registrar fallo en circuit breaker
            _cb_record_failure("gmail")
            
            logger.error(f"Error inesperado consultando Gmail: {e}", exc_info=True)
            raise

    @task(task_id="classify_and_update", execution_timeout=timedelta(minutes=15))
    def classify_and_update() -> Dict[str, Any]:
        """
        Función principal mejorada que procesa correos nuevos, los clasifica y actualiza HubSpot.
        Lee configuración desde variables de entorno (integración con stack) o parámetros.
        """
        ctx = get_current_context()
        params = ctx.get("params", {})

        # Leer desde variables de entorno (integración con stack) o parámetros
        credentials_json = str(
            params.get("gmail_credentials_json") or os.getenv("GMAIL_CREDENTIALS_JSON", "")
        )
        token_json = str(
            params.get("gmail_token_json") or os.getenv("GMAIL_TOKEN_JSON", "")
        )
        max_emails = int(
            params.get("max_emails") or os.getenv("GMAIL_CLASSIFY_MAX_EMAILS", "10")
        )
        max_workers = int(
            params.get("max_workers") or os.getenv("GMAIL_CLASSIFY_MAX_WORKERS", "0")
        )
        # Si max_workers es 0, procesar secuencialmente (más seguro para rate limits)
        use_parallel = CONCURRENT_FUTURES_AVAILABLE and max_workers > 1
        dry_run = bool(params.get("dry_run", False))

        # Guard clauses
        if not credentials_json:
            raise AirflowFailException(
                "gmail_credentials_json is required. "
                "Set GMAIL_CREDENTIALS_JSON env var or provide as parameter."
            )

        results = []
        start_time = perf_counter()
        
        # Obtener run ID para tracking
        dag_run_id = ctx.get("dag_run", {}).run_id if ctx else None

        # Trackers para error breakdown
        error_types = Counter()
        contact_not_found_count = 0
        hubspot_update_failures = 0
        classification_errors = 0
        skipped = 0

        try:
            # Registrar inicio en métricas
            if STATS_AVAILABLE:
                try:
                    tags = {"run_id": dag_run_id, "dry_run": str(dry_run)} if dag_run_id else {"dry_run": str(dry_run)}
                    Stats.incr("gmail_classify_hubspot.run_started", 1, tags=tags)
                except Exception:
                    pass

            # Health checks robustos antes de procesar
            health_checks = {}
            
            # Health check de Gmail
            try:
                gmail_service_check = get_gmail_service(credentials_json, token_json)
                gmail_health = _health_check_gmail(gmail_service_check)
                health_checks["gmail"] = gmail_health
                
                if gmail_health["status"] == "healthy":
                    logger.info(
                        "Gmail API health check passed",
                        extra={
                            "run_id": dag_run_id,
                            "duration_ms": gmail_health["duration_ms"],
                            **gmail_health.get("details", {})
                        }
                    )
                else:
                    logger.warning(
                        f"Gmail API health check warning: {gmail_health['message']}",
                        extra={
                            "run_id": dag_run_id,
                            "duration_ms": gmail_health["duration_ms"],
                            **gmail_health.get("details", {})
                        }
                    )
                    # Continuar de todas formas, puede ser temporal
            except Exception as e:
                logger.warning(
                    f"Gmail API health check error: {e}",
                    extra={"run_id": dag_run_id},
                    exc_info=True
                )
                health_checks["gmail"] = {
                    "status": "error",
                    "message": str(e),
                    "duration_ms": 0
                }
            
            # Health check de HubSpot
            try:
                hubspot_health = _health_check_hubspot()
                health_checks["hubspot"] = hubspot_health
                
                if hubspot_health["status"] == "healthy":
                    logger.info(
                        "HubSpot API health check passed",
                        extra={
                            "run_id": dag_run_id,
                            "duration_ms": hubspot_health["duration_ms"],
                            **hubspot_health.get("details", {})
                        }
                    )
                else:
                    logger.warning(
                        f"HubSpot API health check warning: {hubspot_health['message']}",
                        extra={
                            "run_id": dag_run_id,
                            "duration_ms": hubspot_health["duration_ms"],
                            **hubspot_health.get("details", {})
                        }
                    )
                    # Continuar de todas formas, puede ser temporal
            except Exception as e:
                logger.warning(
                    f"HubSpot API health check error: {e}",
                    extra={"run_id": dag_run_id},
                    exc_info=True
                )
                health_checks["hubspot"] = {
                    "status": "error",
                    "message": str(e),
                    "duration_ms": 0
                }
            
            # Registrar métricas de health checks
            if STATS_AVAILABLE:
                try:
                    tags = {"run_id": dag_run_id} if dag_run_id else {}
                    for service, health in health_checks.items():
                        Stats.gauge(
                            f"gmail_classify_hubspot.health_check.{service}.duration_ms",
                            health.get("duration_ms", 0),
                            tags=tags
                        )
                        Stats.incr(
                            f"gmail_classify_hubspot.health_check.{service}.{health.get('status', 'unknown')}",
                            1,
                            tags=tags
                        )
                except Exception:
                    pass

            # Inicializar servicio de Gmail con context manager
            with gmail_service_context(credentials_json, token_json) as gmail_service:
                logger.info("Gmail API authentication successful", extra={"run_id": dag_run_id})

                # Obtener correos nuevos
                emails = get_new_emails(gmail_service, max_results=max_emails)

                if not emails:
                    logger.info("No se encontraron correos nuevos", extra={"run_id": dag_run_id})
                    return {
                        "results": [],
                        "summary": "No hay correos nuevos para procesar",
                        "formatted_results": [],
                        "processed": 0,
                        "failed": 0,
                        "skipped": 0,
                        "total": 0,
                        "success_rate": 0.0,
                        "throughput_per_sec": 0.0,
                        "duration_ms": 0,
                        "duration_seconds": 0.0,
                        "health_checks": health_checks,  # Incluir health checks incluso sin emails
                        "run_id": dag_run_id,
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                    }

                logger.info(f"Procesando {len(emails)} correos nuevos", extra={"run_id": dag_run_id, "total": len(emails)})
                
                if STATS_AVAILABLE:
                    try:
                        tags = {"run_id": dag_run_id} if dag_run_id else {}
                        Stats.gauge("gmail_classify_hubspot.emails_found", len(emails), tags=tags)
                    except Exception:
                        pass

                # Función helper para procesar un email individual
                def process_single_email(email_data: Dict[str, Any]) -> Dict[str, Any]:
                    """Procesa un email individual: clasifica, busca contacto y actualiza HubSpot."""
                    email_start_time = perf_counter()
                    sender_email = email_data.get("sender_email", "")
                    subject = email_data.get("subject", "")
                    body = email_data.get("body", "")

                    # Guard clause: normalizar y validar email
                    normalized_email = _normalize_email(sender_email)
                    if not normalized_email:
                        logger.warning("Email sin remitente válido, saltando", extra={"sender": sender_email[:50] if sender_email else None, "run_id": dag_run_id})
                        return {
                            "email": sender_email or "",
                            "clasificacion": "Error",
                            "hubspot_id": None,
                            "estado": "Email sin remitente válido",
                            "duration_ms": (perf_counter() - email_start_time) * 1000,
                            "success": False,
                            "error_type": "invalid_sender",
                        }
                    
                    # Usar email normalizado para búsqueda
                    sender_email = normalized_email

                    try:
                        # Normalizar inputs para clasificación usando constantes
                        subject_normalized = _normalize_text(subject or "", max_length=MAX_SUBJECT_LENGTH)
                        body_normalized = _normalize_text(body or "", max_length=MAX_BODY_LENGTH)
                        
                        # Clasificar correo
                        clasificacion = classify_email(subject_normalized, body_normalized)
                        
                        # Validar clasificación
                        if not _validate_classification(clasificacion):
                            logger.warning(
                                f"Clasificación inválida: {clasificacion}, usando 'Otro'",
                                extra={"sender_email": sender_email, "run_id": dag_run_id}
                            )
                            clasificacion = "Otro"
                        
                        logger.info(
                            f"Correo de {sender_email} clasificado como: {clasificacion}",
                            extra={
                                "sender_email": sender_email,
                                "clasificacion": clasificacion,
                                "run_id": dag_run_id
                            }
                        )

                        # Buscar contacto en HubSpot (con cache)
                        contact_id = find_hubspot_contact(sender_email)

                        if not contact_id:
                            logger.warning(
                                f"Contacto no encontrado en HubSpot para email: {sender_email}",
                                extra={"sender_email": sender_email, "run_id": dag_run_id}
                            )
                            return {
                                "email": sender_email,
                                "clasificacion": clasificacion,
                                "hubspot_id": None,
                                "estado": "Contacto no encontrado en HubSpot",
                                "duration_ms": (perf_counter() - email_start_time) * 1000,
                                "success": False,
                                "error_type": "contact_not_found",
                            }
                        
                        # Validar contact_id antes de actualizar
                        if not _validate_hubspot_contact_id(contact_id):
                            logger.error(
                                f"contact_id inválido obtenido de HubSpot: {contact_id}",
                                extra={"sender_email": sender_email, "run_id": dag_run_id}
                            )
                            return {
                                "email": sender_email,
                                "clasificacion": clasificacion,
                                "hubspot_id": contact_id,
                                "estado": "Contact ID inválido",
                                "duration_ms": (perf_counter() - email_start_time) * 1000,
                                "success": False,
                                "error_type": "invalid_contact_id",
                            }

                        # Actualizar HubSpot con manejo de errores mejorado
                        nota = f"Correo clasificado como {clasificacion}. Asunto: {subject_normalized[:100]}"
                        try:
                            success, message, duration_ms = update_hubspot_contact_and_note(
                                contact_id, clasificacion, nota, dry_run
                            )
                        except HubSpotValidationError as e:
                            logger.error(
                                f"Error de validación en HubSpot: {e}",
                                extra={"sender_email": sender_email, "contact_id": contact_id, "run_id": dag_run_id},
                                exc_info=True
                            )
                            return {
                                "email": sender_email,
                                "clasificacion": clasificacion,
                                "hubspot_id": contact_id,
                                "estado": f"Error de validación: {str(e)}",
                                "duration_ms": (perf_counter() - email_start_time) * 1000,
                                "success": False,
                                "error_type": "validation_error",
                            }
                        except HubSpotAPIError as e:
                            logger.error(
                                f"Error de API en HubSpot: {e}",
                                extra={"sender_email": sender_email, "contact_id": contact_id, "status_code": e.status_code, "run_id": dag_run_id},
                                exc_info=True
                            )
                            return {
                                "email": sender_email,
                                "clasificacion": clasificacion,
                                "hubspot_id": contact_id,
                                "estado": f"Error de API HubSpot (status {e.status_code}): {str(e)}",
                                "duration_ms": (perf_counter() - email_start_time) * 1000,
                                "success": False,
                                "error_type": "hubspot_api_error",
                            }

                        estado = "Actualizado correctamente" if success else message

                        result_item = {
                            "email": sender_email,
                            "clasificacion": clasificacion,
                            "hubspot_id": contact_id,
                            "estado": estado,
                            "duration_ms": duration_ms or ((perf_counter() - email_start_time) * 1000),
                            "success": success,
                            "error_type": None if success else "hubspot_update_error",
                        }

                        # Log con formato solicitado
                        logger.info(
                            f"✅ Clasificación: {clasificacion} | HubSpot ID: {contact_id} | Estado: {estado}",
                            extra={
                                "clasificacion": clasificacion,
                                "hubspot_id": contact_id,
                                "estado": estado,
                                "duration_ms": result_item["duration_ms"],
                                "run_id": dag_run_id,
                            }
                        )

                        return result_item

                    except Exception as e:
                        error_type = type(e).__name__
                        
                        logger.error(
                            f"Error procesando correo de {sender_email}: {e}",
                            extra={
                                "sender_email": sender_email,
                                "error": str(e),
                                "error_type": error_type,
                                "run_id": dag_run_id,
                            },
                            exc_info=True
                        )
                        return {
                            "email": sender_email,
                            "clasificacion": "Error",
                            "hubspot_id": None,
                            "estado": f"Error: {str(e)[:100]}",
                            "duration_ms": (perf_counter() - email_start_time) * 1000,
                            "success": False,
                            "error_type": error_type,
                        }

                # Procesar emails (paralelo o secuencial)
                processed = 0
                failed = 0
                classification_counts = Counter()
                
                # Progress tracking
                total_emails = len(emails)
                progress_checkpoint = max(1, total_emails // 10)  # Log cada 10% o cada email si < 10

                if use_parallel:
                    logger.info(f"Procesando {len(emails)} emails en paralelo con {max_workers} workers", extra={"run_id": dag_run_id})
                    
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        future_to_email = {
                            executor.submit(process_single_email, email_data): email_data
                            for email_data in emails
                        }
                        
                        for future in as_completed(future_to_email):
                            email_data = future_to_email[future]
                            try:
                                result_item = future.result()
                                
                                # Validar con Pydantic si está disponible
                                if PYDANTIC_AVAILABLE:
                                    try:
                                        validated_result = ClassificationResult(**{k: v for k, v in result_item.items() if k != "success" and k != "error_type"})
                                        results.append(validated_result.model_dump())
                                    except ValidationError as e:
                                        logger.warning(f"Result validation failed: {e}")
                                        results.append({k: v for k, v in result_item.items() if k != "success" and k != "error_type"})
                                else:
                                    results.append({k: v for k, v in result_item.items() if k != "success" and k != "error_type"})
                                
                                # Actualizar contadores
                                clasificacion = result_item.get("clasificacion", "Otro")
                                if clasificacion != "Error":
                                    classification_counts[clasificacion] += 1
                                
                                if result_item.get("success", False):
                                    processed += 1
                                else:
                                    failed += 1
                                    error_type = result_item.get("error_type")
                                    if error_type:
                                        error_types[error_type] += 1
                                        if error_type == "contact_not_found":
                                            contact_not_found_count += 1
                                        elif error_type == "hubspot_update_error":
                                            hubspot_update_failures += 1
                                        else:
                                            classification_errors += 1
                                
                                # Progress tracking
                                total_processed = processed + failed
                                if total_processed % progress_checkpoint == 0 or total_processed == total_emails:
                                    progress_pct = (total_processed / total_emails * 100) if total_emails > 0 else 0
                                    logger.info(
                                        f"Progress: {total_processed}/{total_emails} emails procesados ({progress_pct:.1f}%) - {processed} exitosos, {failed} fallidos",
                                        extra={
                                            "run_id": dag_run_id,
                                            "processed": total_processed,
                                            "total": total_emails,
                                            "successful": processed,
                                            "failed": failed,
                                            "progress_pct": round(progress_pct, 1)
                                        }
                                    )
                                
                            except Exception as e:
                                logger.error(f"Error obteniendo resultado de future: {e}", exc_info=True)
                                failed += 1
                                error_types["future_error"] += 1
                                
                                # Progress tracking incluso en errores
                                total_processed = processed + failed
                                if total_processed % progress_checkpoint == 0 or total_processed == total_emails:
                                    progress_pct = (total_processed / total_emails * 100) if total_emails > 0 else 0
                                    logger.info(
                                        f"Progress: {total_processed}/{total_emails} emails procesados ({progress_pct:.1f}%) - {processed} exitosos, {failed} fallidos",
                                        extra={
                                            "run_id": dag_run_id,
                                            "processed": total_processed,
                                            "total": total_emails,
                                            "successful": processed,
                                            "failed": failed,
                                            "progress_pct": round(progress_pct, 1)
                                        }
                                    )
                else:
                    # Procesamiento secuencial (más seguro para rate limits)
                    logger.info(f"Procesando {len(emails)} emails secuencialmente", extra={"run_id": dag_run_id})
                    
                    for email_data in emails:
                        result_item = process_single_email(email_data)
                        
                        # Validar con Pydantic si está disponible
                        if PYDANTIC_AVAILABLE:
                            try:
                                validated_result = ClassificationResult(**{k: v for k, v in result_item.items() if k != "success" and k != "error_type"})
                                results.append(validated_result.model_dump())
                            except ValidationError as e:
                                logger.warning(f"Result validation failed: {e}")
                                results.append({k: v for k, v in result_item.items() if k != "success" and k != "error_type"})
                        else:
                            results.append({k: v for k, v in result_item.items() if k != "success" and k != "error_type"})
                        
                        # Actualizar contadores
                        clasificacion = result_item.get("clasificacion", "Otro")
                        if clasificacion != "Error":
                            classification_counts[clasificacion] += 1
                        
                        if result_item.get("success", False):
                            processed += 1
                        else:
                            failed += 1
                            error_type = result_item.get("error_type")
                            if error_type:
                                error_types[error_type] += 1
                                if error_type == "contact_not_found":
                                    contact_not_found_count += 1
                                elif error_type == "hubspot_update_error":
                                    hubspot_update_failures += 1
                                elif error_type != "invalid_sender":
                                    classification_errors += 1
                        
                        # Progress tracking en modo secuencial
                        total_processed = processed + failed
                        if total_processed % progress_checkpoint == 0 or total_processed == total_emails:
                            progress_pct = (total_processed / total_emails * 100) if total_emails > 0 else 0
                            logger.info(
                                f"Progress: {total_processed}/{total_emails} emails procesados ({progress_pct:.1f}%) - {processed} exitosos, {failed} fallidos",
                                extra={
                                    "run_id": dag_run_id,
                                    "processed": total_processed,
                                    "total": total_emails,
                                    "successful": processed,
                                    "failed": failed,
                                    "progress_pct": round(progress_pct, 1)
                                }
                            )

                # Calcular duración y estadísticas
                duration_seconds = perf_counter() - start_time
                duration_ms = duration_seconds * 1000
                success_rate = (processed / len(emails) * 100) if emails else 0.0
                throughput = processed / duration_seconds if duration_seconds > 0 else 0.0

                error_breakdown = {
                    "contact_not_found": contact_not_found_count,
                    "hubspot_update_failures": hubspot_update_failures,
                    "classification_errors": classification_errors,
                    "error_types": dict(error_types),
                    "classification_distribution": dict(classification_counts),
                }

                summary_dict = {
                    "processed": processed,
                    "failed": failed,
                    "skipped": skipped,
                    "total": len(emails),
                    "success_rate": round(success_rate, 2),
                    "throughput_per_sec": round(throughput, 2),
                    "dry_run": dry_run,
                    "use_parallel": use_parallel,
                    "max_workers": max_workers if use_parallel else 1,
                    "results": results,
                    "duration_ms": round(duration_ms, 2),
                    "duration_seconds": round(duration_seconds, 2),
                    "error_breakdown": error_breakdown,
                    "health_checks": health_checks,  # Incluir health checks en el resultado
                    "run_id": dag_run_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }

                # Validar resumen con Pydantic si está disponible
                if PYDANTIC_AVAILABLE:
                    try:
                        summary = ProcessingSummary(**summary_dict)
                        summary_final = summary.model_dump(mode="json")
                    except ValidationError as e:
                        logger.warning(f"Summary validation failed: {e}, using raw dict")
                        summary_final = summary_dict
                else:
                    summary_final = summary_dict

                processing_mode = f"paralelo ({max_workers} workers)" if use_parallel else "secuencial"
                summary_str = f"Procesados {processed} correos exitosamente, {failed} fallidos, {skipped} saltados de {len(emails)} total ({processing_mode})"

                # Log estructurado completo
                logger.info(
                    f"Clasificación completada: {processed} procesados, {failed} fallidos de {len(emails)} total",
                    extra={
                        "duration_ms": round(duration_ms, 2),
                        "duration_seconds": round(duration_seconds, 2),
                        "processed": processed,
                        "failed": failed,
                        "skipped": skipped,
                        "total": len(emails),
                        "success_rate": round(success_rate, 2),
                        "throughput_per_sec": round(throughput, 2),
                        "error_breakdown": error_breakdown,
                        "classification_distribution": dict(classification_counts),
                        "dry_run": dry_run,
                        "use_parallel": use_parallel,
                        "max_workers": max_workers if use_parallel else 1,
                        "run_id": dag_run_id,
                    },
                )

                # Registrar métricas finales detalladas con tags
                if STATS_AVAILABLE:
                    try:
                        tags = {"run_id": dag_run_id, "dry_run": str(dry_run), "parallel": str(use_parallel)} if dag_run_id else {"dry_run": str(dry_run), "parallel": str(use_parallel)}
                        
                        # Métricas principales
                        Stats.incr("gmail_classify_hubspot.emails_processed", processed, tags=tags)
                        Stats.incr("gmail_classify_hubspot.emails_failed", failed, tags=tags)
                        Stats.incr("gmail_classify_hubspot.run_completed", 1, tags=tags)
                        Stats.timing("gmail_classify_hubspot.duration_seconds", duration_seconds, tags=tags)
                        Stats.timing("gmail_classify_hubspot.duration_ms", duration_ms, tags=tags)
                        
                        # Métricas de paralelismo
                        if use_parallel:
                            Stats.gauge("gmail_classify_hubspot.max_workers", max_workers, tags=tags)
                        
                        # Métricas de idempotencia
                        if skipped > 0:
                            Stats.incr("gmail_classify_hubspot.emails_skipped", skipped, tags=tags)
                        
                        # Métricas de tasa
                        if emails:
                            Stats.gauge("gmail_classify_hubspot.success_rate", success_rate, tags=tags)
                            Stats.gauge("gmail_classify_hubspot.throughput_per_sec", throughput, tags=tags)
                        
                        # Métricas de errores por tipo
                        for error_type, count in error_types.items():
                            Stats.incr("gmail_classify_hubspot.errors_by_type", count, tags={
                                **tags,
                                "error_type": error_type,
                            })
                        
                        # Métricas de fallos específicos
                        if contact_not_found_count > 0:
                            Stats.incr("gmail_classify_hubspot.contact_not_found", contact_not_found_count, tags=tags)
                        if hubspot_update_failures > 0:
                            Stats.incr("gmail_classify_hubspot.hubspot_update_failures", hubspot_update_failures, tags=tags)
                        
                        # Métricas de clasificación
                        for clasif, count in classification_counts.items():
                            Stats.incr("gmail_classify_hubspot.classification_counts", count, tags={
                                **tags,
                                "classification": clasif,
                            })
                        
                        # Métricas de rendimiento
                        if processed > 0:
                            avg_email_duration = duration_seconds / processed
                            Stats.timing("gmail_classify_hubspot.avg_email_duration_seconds", avg_email_duration, tags=tags)
                        
                        # Métricas de progress tracking
                        if len(emails) > 0:
                            final_progress_pct = ((processed + failed) / len(emails) * 100)
                            Stats.gauge("gmail_classify_hubspot.progress_pct", final_progress_pct, tags=tags)
                            
                    except Exception as e:
                        logger.debug(f"Error recording final stats: {e}")

                # Notificación a Slack mejorada
                if NOTIFICATIONS_AVAILABLE and os.getenv("ENABLE_SLACK", "false").lower() == "true":
                    try:
                        status_emoji = "✅" if failed == 0 else "⚠️" if processed > 0 else "❌"
                        duration_str = f"{duration_seconds:.1f}s"
                        throughput_str = f"{throughput:.1f}/s" if throughput > 0 else "N/A"
                        
                        # Mensaje mejorado con más detalles
                        processing_mode = f"Paralelo ({max_workers} workers)" if use_parallel else "Secuencial"
                        message_parts = [
                            f"{status_emoji} *Gmail Classify HubSpot* completado",
                            f"• Procesados: {processed}",
                            f"• Fallidos: {failed}",
                            f"• Saltados: {skipped}",
                            f"• Total: {len(emails)}",
                            f"• Tasa éxito: {success_rate:.1f}%",
                            f"• Duración: {duration_str}",
                            f"• Throughput: {throughput_str}",
                            f"• Procesamiento: {processing_mode}",
                            f"• Modo: {'Dry Run' if dry_run else 'Producción'}",
                        ]
                        
                        # Agregar distribución de clasificaciones
                        if classification_counts:
                            clasif_summary = ", ".join([f"{k}: {v}" for k, v in classification_counts.items()])
                            message_parts.append(f"• Clasificaciones: {clasif_summary}")
                        
                        # Agregar desglose de errores si hay
                        if error_types:
                            error_summary = ", ".join([f"{k}: {v}" for k, v in list(error_types.items())[:3]])
                            message_parts.append(f"• Errores: {error_summary}")
                        
                        message = "\n".join(message_parts)

                        notify_slack(
                            message,
                            extra_context={
                                "dag_id": "gmail_classify_hubspot",
                                "run_id": dag_run_id,
                                "processed": processed,
                                "failed": failed,
                                "skipped": skipped,
                                "total": len(emails),
                                "success_rate": success_rate,
                                "duration_seconds": duration_seconds,
                                "throughput": throughput,
                                "dry_run": dry_run,
                                "error_types": dict(error_types),
                                "classification_distribution": dict(classification_counts),
                            },
                            username="Gmail Classify",
                            icon_emoji=":email:"
                        )
                    except Exception as e:
                        logger.warning(f"Failed to send Slack notification: {e}", exc_info=True)

                # Retornar resultados en formato claro
                return {
                    **summary_final,
                    "summary": summary_str,
                    "formatted_results": [
                        f"Clasificación: {r['clasificacion']} | HubSpot ID: {r['hubspot_id']} | Estado: {r['estado']}"
                        for r in results
                    ],
                }

        except Exception as e:
            duration_seconds = perf_counter() - start_time
            duration_ms = duration_seconds * 1000
            logger.error(f"Error procesando correos: {e}", exc_info=True, extra={"run_id": dag_run_id})
            
            if STATS_AVAILABLE:
                try:
                    tags = {"run_id": dag_run_id} if dag_run_id else {}
                    Stats.incr("gmail_classify_hubspot.run_failed", 1, tags=tags)
                except Exception:
                    pass
            
            return {
                "results": [],
                "summary": f"Error: {str(e)}",
                "error": str(e),
                "processed": 0,
                "failed": 0,
                "skipped": 0,
                "total": 0,
                "duration_ms": round(duration_ms, 2),
                "duration_seconds": round(duration_seconds, 2),
                "run_id": dag_run_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

    # Ejecutar tarea
    classify_and_update()


# Generar DAG
gmail_classify_hubspot()
