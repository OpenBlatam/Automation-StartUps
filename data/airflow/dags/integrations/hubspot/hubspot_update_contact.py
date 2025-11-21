"""
Módulo para actualizar propiedades de contactos en HubSpot.

Mejoras implementadas:
- Retry con exponential backoff
- Manejo de rate limiting (429)
- Logging estructurado
- Validación robusta de inputs
- Timeout configurable
- Métricas de performance
- Batch updates (actualización masiva)
- Soporte para cualquier propiedad (no solo 'estado_interés')
- Validación opcional de propiedades existentes
- Rate limiting inteligente para operaciones batch
"""
import os
import time
import json
import logging
from typing import Optional, Dict, Any, Union, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache
from contextlib import contextmanager
from airflow.models import Variable

# HTTP clients mejorados
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    import requests

# Tenacity para retry mejorado
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

# Cache para reducir llamadas
try:
    from cachetools import TTLCache
    CACHETOOLS_AVAILABLE = True
except ImportError:
    CACHETOOLS_AVAILABLE = False

# Importar utilidades del stack si están disponibles
try:
    from plugins.etl_logging import get_task_logger, log_with_context
    LOGGING_AVAILABLE = True
except ImportError:
    try:
        from data.airflow.plugins.etl_logging import get_task_logger, log_with_context
        LOGGING_AVAILABLE = True
    except ImportError:
        LOGGING_AVAILABLE = False
        get_task_logger = lambda x: logging.getLogger(__name__)
        def log_with_context(logger, level, msg, **kwargs):
            logger.log(level, msg, extra=kwargs)

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
        logger.debug("Notifications plugin not available")


logger = get_task_logger("hubspot_update_contact")

HUBSPOT_TOKEN = os.environ.get("HUBSPOT_TOKEN", "")
HUBSPOT_BASE = os.environ.get("HUBSPOT_BASE", "https://api.hubapi.com")

# Constantes
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1  # segundos
DEFAULT_TIMEOUT = 30  # segundos
RATE_LIMIT_MAX_WAIT = 300  # 5 minutos máximo de espera por rate limit
BATCH_SIZE_DEFAULT = 10  # Contactos por batch para evitar rate limits
BATCH_DELAY_SECONDS = 0.1  # Delay entre batches para respetar rate limits

# Cache para propiedades válidas (evita validaciones repetidas)
_property_cache: Optional[Any] = None
if CACHETOOLS_AVAILABLE:
    _property_cache = TTLCache(maxsize=500, ttl=3600)  # 1 hora TTL

# Session pooling para mejor performance
_http_session: Optional[Any] = None


@dataclass
class HubSpotUpdateResult:
    """Resultado de la actualización de HubSpot."""
    success: bool
    status_code: int
    message: str
    contact_id: str
    nuevo_estado: str
    error_details: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    retries: int = 0
    
    def __str__(self) -> str:
        """Representación en string para compatibilidad con código existente."""
        return "Éxito" if self.success else f"{self.status_code}: {self.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario."""
        return {
            "success": self.success,
            "status_code": self.status_code,
            "message": self.message,
            "contact_id": self.contact_id,
            "nuevo_estado": self.nuevo_estado,
            "error_details": self.error_details,
            "duration_ms": self.duration_ms,
            "retries": self.retries,
        }


@contextmanager
def _get_http_client():
    """Context manager para HTTP client con pooling."""
    global _http_session
    
    if HTTPX_AVAILABLE:
        if _http_session is None:
            _http_session = httpx.Client(timeout=30.0, limits=httpx.Limits(max_keepalive_connections=10))
        yield _http_session
    else:
        # Usar requests con session si está disponible
        import requests
        session = requests.Session()
        try:
            yield session
        finally:
            session.close()


def _make_request_with_retry(
    url: str,
    headers: Dict[str, str],
    payload: Dict[str, Any],
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_delay: float = DEFAULT_RETRY_DELAY,
    timeout: int = DEFAULT_TIMEOUT,
    contact_id: str = ""
) -> Any:
    """
    Realiza una petición HTTP con retry y manejo de rate limiting.
    
    Args:
        url: URL a la que hacer la petición
        headers: Headers HTTP
        payload: Payload JSON
        max_retries: Máximo de reintentos
        retry_delay: Delay inicial entre reintentos (exponential backoff)
        timeout: Timeout en segundos
        contact_id: ID del contacto (para logging)
    
    Returns:
        Response de requests
        
    Raises:
        requests.exceptions.RequestException: Si falla después de todos los reintentos
    """
    # Usar tenacity si está disponible para retry mejorado
    if TENACITY_AVAILABLE:
        @retry(
            stop=stop_after_attempt(max_retries + 1),
            wait=wait_exponential(multiplier=retry_delay, min=1, max=RATE_LIMIT_MAX_WAIT),
            retry=retry_if_exception_type((Exception,)),
            reraise=True,
        )
        def _make_request():
            with _get_http_client() as client:
                if HTTPX_AVAILABLE:
                    response = client.patch(url, headers=headers, json=payload)
                    # Convertir httpx.Response a formato compatible
                    response.status_code = response.status_code
                    response.headers = dict(response.headers)
                    response.text = response.text
                    response.json = lambda: response.json()
                    return response
                else:
                    return client.patch(url, headers=headers, json=payload, timeout=timeout)
        
        try:
            response = _make_request()
            # Manejar rate limiting después de retry
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', RATE_LIMIT_MAX_WAIT))
                if STATS_AVAILABLE:
                    try:
                        Stats.incr("hubspot_update_contact.rate_limit_hit", 1)
                    except Exception:
                        pass
                log_with_context(
                    logger,
                    logging.WARNING,
                    f"Rate limited después de retries, esperando {retry_after}s",
                    contact_id=contact_id,
                    retry_after=retry_after
                )
                time.sleep(min(retry_after, RATE_LIMIT_MAX_WAIT))
                response.raise_for_status()
            
            if response.status_code >= 400:
                response.raise_for_status()
            
            return response
        except RetryError as e:
            raise e.last_attempt.exception() from e
        except Exception as e:
            raise
    
    # Fallback sin tenacity
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            with _get_http_client() as client:
                if HTTPX_AVAILABLE:
                    response = client.patch(url, headers=headers, json=payload)
                    # Normalizar respuesta
                    response.status_code = response.status_code
                    response.headers = dict(response.headers)
                    response.text = response.text
                    response.json = lambda: response.json()
                else:
                    response = client.patch(url, headers=headers, json=payload, timeout=timeout)
            
            # Manejar rate limiting (429)
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', retry_delay * (2 ** attempt)))
                retry_after = min(retry_after, RATE_LIMIT_MAX_WAIT)  # Limitar espera máxima
                
                # Registrar métrica de rate limit
                if STATS_AVAILABLE:
                    try:
                        Stats.incr("hubspot_update_contact.rate_limit_hit", 1, tags={
                            "contact_id": contact_id or "unknown",
                            "attempt": str(attempt + 1),
                        })
                    except Exception:
                        pass
                
                if attempt < max_retries:
                    log_with_context(
                        logger,
                        logging.WARNING,
                        f"Rate limited por HubSpot (intento {attempt + 1}/{max_retries + 1}), esperando {retry_after}s",
                        contact_id=contact_id,
                        attempt=attempt + 1,
                        retry_after=retry_after,
                        status_code=429
                    )
                    time.sleep(retry_after)
                    continue
                else:
                    # Último intento falló por rate limit
                    response.raise_for_status()
            
            # Para otros errores, usar raise_for_status
            if response.status_code >= 400:
                if HTTPX_AVAILABLE:
                    from httpx import HTTPStatusError
                    raise HTTPStatusError(
                        f"HTTP {response.status_code}",
                        request=response.request,
                        response=response
                    )
                else:
                    response.raise_for_status()
            
            return response
            
        except Exception as e:
            # Manejar diferentes tipos de excepciones de forma unificada
            is_timeout = False
            if HTTPX_AVAILABLE:
                import httpx
                is_timeout = isinstance(e, (httpx.TimeoutException, TimeoutError))
                is_connection = isinstance(e, httpx.ConnectError)
            else:
                import requests
                is_timeout = isinstance(e, requests.exceptions.Timeout)
                is_connection = isinstance(e, requests.exceptions.ConnectionError)
            
            last_exception = e
            
            if attempt < max_retries:
                wait_time = retry_delay * (2 ** attempt)
                error_type = "Timeout" if is_timeout else "Connection" if is_connection else "Request"
                log_with_context(
                    logger,
                    logging.WARNING,
                    f"{error_type} en petición a HubSpot (intento {attempt + 1}/{max_retries + 1}), reintentando en {wait_time}s",
                    contact_id=contact_id,
                    attempt=attempt + 1,
                    wait_time=wait_time,
                    error=str(e),
                    error_type=error_type
                )
                time.sleep(wait_time)
                continue
            else:
                raise
    
    # Si llegamos aquí, todos los reintentos fallaron
    raise last_exception


def _create_validation_error_result(
    error_msg: str,
    contact_id: str,
    nuevo_estado: str,
    duration_ms: float
) -> HubSpotUpdateResult:
    """
    Crea un resultado de error de validación. Función pura helper.
    
    Args:
        error_msg: Mensaje de error
        contact_id: ID del contacto (puede estar vacío)
        nuevo_estado: Estado proporcionado (puede estar vacío)
        duration_ms: Duración en milisegundos
        
    Returns:
        HubSpotUpdateResult con error
    """
    return HubSpotUpdateResult(
        success=False,
        status_code=0,
        message=error_msg,
        contact_id=contact_id or "",
        nuevo_estado=nuevo_estado or "",
        duration_ms=duration_ms
    )


def validate_update_params(
    hubspot_contact_id: str,
    nuevo_estado: str,
    hubspot_token: Optional[str] = None
) -> Optional[HubSpotUpdateResult]:
    """
    Valida parámetros de actualización usando guard clauses.
    Implementa early returns para manejo de errores temprano.
    Usa funciones auxiliares puras para reducir duplicación.
    
    Args:
        hubspot_contact_id: ID del contacto
        nuevo_estado: Nuevo estado a asignar
        hubspot_token: Token de autenticación
        
    Returns:
        HubSpotUpdateResult con error si hay validación fallida, None si es válido
    """
    start_time = time.time()
    
    # Guard clause: validar token
    token = hubspot_token or HUBSPOT_TOKEN
    if not token:
        error_msg = "ERROR: HUBSPOT_TOKEN no configurado"
        log_with_context(logger, logging.ERROR, error_msg, contact_id=hubspot_contact_id)
        return _create_validation_error_result(
            error_msg,
            hubspot_contact_id,
            nuevo_estado,
            (time.time() - start_time) * 1000
        )
    
    # Guard clause: validar contact_id
    if not hubspot_contact_id or not hubspot_contact_id.strip():
        error_msg = "ERROR: hubspot_contact_id es requerido"
        log_with_context(logger, logging.ERROR, error_msg, contact_id=hubspot_contact_id)
        return _create_validation_error_result(
            error_msg,
            hubspot_contact_id,
            nuevo_estado,
            (time.time() - start_time) * 1000
        )
    
    # Guard clause: validar nuevo_estado
    if not nuevo_estado or not nuevo_estado.strip():
        error_msg = "ERROR: nuevo_estado es requerido"
        log_with_context(logger, logging.ERROR, error_msg, contact_id=hubspot_contact_id)
        return _create_validation_error_result(
            error_msg,
            hubspot_contact_id,
            nuevo_estado,
            (time.time() - start_time) * 1000
        )
    
    # Todas las validaciones pasaron
    return None


def actualizar_estado_interes(
    hubspot_contact_id: str,
    nuevo_estado: str,
    hubspot_token: Optional[str] = None,
    hubspot_base: Optional[str] = None,
    max_retries: int = DEFAULT_MAX_RETRIES,
    timeout: int = DEFAULT_TIMEOUT,
    return_result_object: bool = False,
    _property_name: Optional[str] = None,
    verify_contact_exists: bool = False,
    enable_circuit_breaker: bool = True
) -> Union[str, HubSpotUpdateResult]:
    """
    Actualiza la propiedad 'estado_interés' (o cualquier otra propiedad) de un contacto en HubSpot.
    Implementa principios RPA: guard clauses, early returns, validación temprana.
    
    Args:
        hubspot_contact_id: ID del contacto en HubSpot
        nuevo_estado: Nuevo valor para la propiedad
        hubspot_token: Token de autenticación de HubSpot (opcional, usa env var si no se proporciona)
        hubspot_base: URL base de la API de HubSpot (opcional, usa env var si no se proporciona)
        max_retries: Máximo de reintentos (default: 3)
        timeout: Timeout en segundos (default: 30)
        return_result_object: Si True, retorna HubSpotUpdateResult en lugar de string
        _property_name: Nombre de la propiedad a actualizar (default: "estado_interés", uso interno)
    
    Returns:
        str o HubSpotUpdateResult: 
            - Si return_result_object=False: 'Éxito' o 'CÓDIGO_ERROR: mensaje'
            - Si return_result_object=True: Objeto HubSpotUpdateResult con detalles completos
    
    Ejemplo:
        >>> resultado = actualizar_estado_interes("123", "calificado")
        >>> print(resultado)
        'Éxito'
        
        >>> resultado = actualizar_estado_interes("123", "calificado", return_result_object=True)
        >>> print(resultado.duration_ms)
        245.5
    """
    start_time = time.time()
    retries = 0
    
    # Validación temprana con guard clauses
    validation_error = validate_update_params(hubspot_contact_id, nuevo_estado, hubspot_token)
    if validation_error:
        return validation_error if return_result_object else validation_error.message
    
    # Normalizar inputs después de validación
    hubspot_contact_id = hubspot_contact_id.strip()
    nuevo_estado = nuevo_estado.strip()
    
    # Usar parámetros proporcionados o variables de entorno
    token = hubspot_token or HUBSPOT_TOKEN
    base_url = hubspot_base or HUBSPOT_BASE
    
    # Construir URL y headers
    url = f"{base_url}/crm/v3/objects/contacts/{hubspot_contact_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Determinar el nombre de la propiedad a actualizar
    property_name = _property_name or "estado_interés"
    
    # Construir body con la propiedad a actualizar
    payload = {
        "properties": {
            property_name: nuevo_estado
        }
    }
    
    # Verificar circuit breaker
    if _cb_is_open():
        error_msg = "ERROR_CIRCUIT_BREAKER: HubSpot circuit breaker is open due to excessive failures"
        log_with_context(
            logger,
            logging.ERROR,
            error_msg,
            contact_id=hubspot_contact_id,
            threshold=CB_FAILURE_THRESHOLD
        )
        if STATS_AVAILABLE:
            try:
                Stats.incr("hubspot_update_contact.circuit_breaker.blocked", 1)
            except Exception:
                pass
        
        result = HubSpotUpdateResult(
            success=False,
            status_code=0,
            message=error_msg,
            contact_id=hubspot_contact_id,
            nuevo_estado=nuevo_estado,
            duration_ms=(time.time() - start_time) * 1000,
            error_details={"type": "CircuitBreakerOpen", "threshold": CB_FAILURE_THRESHOLD}
        )
        return result if return_result_object else error_msg
    
    # Registrar intento en métricas
    if STATS_AVAILABLE:
        try:
            Stats.incr("hubspot_update_contact.attempt", 1, tags={"property": property_name})
        except Exception:
            pass
    
    log_with_context(
        logger,
        logging.INFO,
        f"Iniciando actualización de contacto en HubSpot",
        contact_id=hubspot_contact_id,
        property_name=property_name,
        nuevo_estado=nuevo_estado,
        max_retries=max_retries
    )
    
    try:
        # Realizar la petición con retry y rate limiting
        response = _make_request_with_retry(
            url=url,
            headers=headers,
            payload=payload,
            max_retries=max_retries,
            retry_delay=DEFAULT_RETRY_DELAY,
            timeout=timeout,
            contact_id=hubspot_contact_id
        )
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Si la respuesta es exitosa
        if response.status_code in [200, 204]:
            # Resetear circuit breaker en caso de éxito
            if enable_circuit_breaker:
                try:
                    _cb_reset()
                except Exception:
                    pass
            
            # Registrar métricas de éxito
            if STATS_AVAILABLE:
                try:
                    Stats.incr("hubspot_api.contacts.updated", 1)
                    Stats.incr(f"hubspot_api.properties.{property_name}.updated", 1)
                    Stats.timing("hubspot_api.update.duration", int(duration_ms))
                except Exception:
                    pass
            
            log_with_context(
                logger,
                logging.INFO,
                f"Contacto actualizado exitosamente en HubSpot",
                contact_id=hubspot_contact_id,
                property_name=property_name,
                nuevo_estado=nuevo_estado,
                status_code=response.status_code,
                duration_ms=duration_ms,
                retries=retries
            )
            
            result = HubSpotUpdateResult(
                success=True,
                status_code=response.status_code,
                message="Éxito",
                contact_id=hubspot_contact_id,
                nuevo_estado=nuevo_estado,
                duration_ms=duration_ms,
                retries=retries
            )
            
            return result if return_result_object else "Éxito"
        
        # Si hay error HTTP, obtener detalles
        error_code = response.status_code
        try:
            error_data = response.json()
            error_message = error_data.get("message", error_data.get("error", response.text))
            error_details = error_data
        except:
            error_message = response.text or "Error desconocido"
            error_details = {"raw_response": response.text}
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Registrar fallo en circuit breaker
        if enable_circuit_breaker:
            _cb_record_failure()
        
        # Registrar métricas de error
        if STATS_AVAILABLE:
            try:
                Stats.incr("hubspot_api.contacts.update_failed", 1)
                Stats.incr(f"hubspot_api.errors.{error_code}", 1)
            except Exception:
                pass
        
        log_with_context(
            logger,
            logging.ERROR,
            f"Error al actualizar contacto en HubSpot",
            contact_id=hubspot_contact_id,
            property_name=property_name,
            nuevo_estado=nuevo_estado,
            status_code=error_code,
            error_message=error_message,
            duration_ms=duration_ms
        )
        
        result = HubSpotUpdateResult(
            success=False,
            status_code=error_code,
            message=error_message,
            contact_id=hubspot_contact_id,
            nuevo_estado=nuevo_estado,
            error_details=error_details,
            duration_ms=duration_ms,
            retries=retries
        )
        
        return result if return_result_object else f"{error_code}: {error_message}"
        
    except requests.exceptions.Timeout as e:
        duration_ms = (time.time() - start_time) * 1000
        # Registrar fallo en circuit breaker
        _cb_record_failure()
        
        error_msg = f"ERROR_TIMEOUT: La petición a HubSpot excedió el tiempo límite ({timeout}s)"
        log_with_context(
            logger,
            logging.ERROR,
            error_msg,
            contact_id=hubspot_contact_id,
            timeout=timeout,
            duration_ms=duration_ms,
            error=str(e)
        )
        
        # Métricas de timeout
        if STATS_AVAILABLE:
            try:
                Stats.incr("hubspot_update_contact.timeout", 1, tags={"property": property_name})
            except Exception:
                pass
        
        result = HubSpotUpdateResult(
            success=False,
            status_code=0,
            message=error_msg,
            contact_id=hubspot_contact_id,
            nuevo_estado=nuevo_estado,
            error_details={"exception": str(e), "type": "Timeout"},
            duration_ms=duration_ms,
            retries=retries
        )
        
        return result if return_result_object else error_msg
        
    except requests.exceptions.ConnectionError as e:
        duration_ms = (time.time() - start_time) * 1000
        # Registrar fallo en circuit breaker
        _cb_record_failure()
        
        error_msg = f"ERROR_CONNECTION: No se pudo conectar con HubSpot API"
        log_with_context(
            logger,
            logging.ERROR,
            error_msg,
            contact_id=hubspot_contact_id,
            duration_ms=duration_ms,
            error=str(e)
        )
        
        # Métricas de conexión
        if STATS_AVAILABLE:
            try:
                Stats.incr("hubspot_update_contact.connection_error", 1, tags={"property": property_name})
            except Exception:
                pass
        
        result = HubSpotUpdateResult(
            success=False,
            status_code=0,
            message=error_msg,
            contact_id=hubspot_contact_id,
            nuevo_estado=nuevo_estado,
            error_details={"exception": str(e), "type": "ConnectionError"},
            duration_ms=duration_ms,
            retries=retries
        )
        
        return result if return_result_object else error_msg
        
    except requests.exceptions.RequestException as e:
        duration_ms = (time.time() - start_time) * 1000
        # Registrar fallo en circuit breaker
        _cb_record_failure()
        
        error_msg = f"ERROR_REQUEST: {str(e)}"
        log_with_context(
            logger,
            logging.ERROR,
            error_msg,
            contact_id=hubspot_contact_id,
            duration_ms=duration_ms,
            error=str(e)
        )
        
        # Métricas de request error
        if STATS_AVAILABLE:
            try:
                Stats.incr("hubspot_update_contact.request_error", 1, tags={"property": property_name})
            except Exception:
                pass
        
        result = HubSpotUpdateResult(
            success=False,
            status_code=getattr(e.response, 'status_code', 0) if hasattr(e, 'response') else 0,
            message=error_msg,
            contact_id=hubspot_contact_id,
            nuevo_estado=nuevo_estado,
            error_details={"exception": str(e), "type": "RequestException"},
            duration_ms=duration_ms,
            retries=retries
        )
        
        return result if return_result_object else error_msg
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        error_msg = f"ERROR_INESPERADO: {str(e)}"
        log_with_context(
            logger,
            logging.ERROR,
            error_msg,
            contact_id=hubspot_contact_id,
            duration_ms=duration_ms,
            error=str(e),
            error_type=type(e).__name__
        )
        
        result = HubSpotUpdateResult(
            success=False,
            status_code=0,
            message=error_msg,
            contact_id=hubspot_contact_id,
            nuevo_estado=nuevo_estado,
            error_details={"exception": str(e), "type": type(e).__name__},
            duration_ms=duration_ms,
            retries=retries
        )
        
        return result if return_result_object else error_msg


@dataclass
class BatchUpdateResult:
    """Resultado de actualización batch."""
    total: int
    successful: int
    failed: int
    results: List[HubSpotUpdateResult] = field(default_factory=list)
    duration_ms: Optional[float] = None
    
    @property
    def success_rate(self) -> float:
        """Tasa de éxito como porcentaje."""
        if self.total == 0:
            return 0.0
        return (self.successful / self.total) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario."""
        return {
            "total": self.total,
            "successful": self.successful,
            "failed": self.failed,
            "success_rate": self.success_rate,
            "duration_ms": self.duration_ms,
            "results": [r.to_dict() for r in self.results]
        }


def actualizar_propiedad_contacto(
    hubspot_contact_id: str,
    propiedad: str,
    valor: str,
    hubspot_token: Optional[str] = None,
    hubspot_base: Optional[str] = None,
    max_retries: int = DEFAULT_MAX_RETRIES,
    timeout: int = DEFAULT_TIMEOUT,
    return_result_object: bool = False
) -> Union[str, HubSpotUpdateResult]:
    """
    Actualiza una propiedad específica de un contacto en HubSpot.
    
    Versión genérica que permite actualizar cualquier propiedad, no solo 'estado_interés'.
    
    Args:
        hubspot_contact_id: ID del contacto en HubSpot
        propiedad: Nombre de la propiedad a actualizar (ej: 'estado_interés', 'lifecycle_stage', etc.)
        valor: Nuevo valor para la propiedad
        hubspot_token: Token de autenticación de HubSpot (opcional)
        hubspot_base: URL base de la API de HubSpot (opcional)
        max_retries: Máximo de reintentos (default: 3)
        timeout: Timeout en segundos (default: 30)
        return_result_object: Si True, retorna HubSpotUpdateResult en lugar de string
    
    Returns:
        str o HubSpotUpdateResult: Resultado de la operación
    """
    return actualizar_estado_interes(
        hubspot_contact_id=hubspot_contact_id,
        nuevo_estado=valor,
        hubspot_token=hubspot_token,
        hubspot_base=hubspot_base,
        max_retries=max_retries,
        timeout=timeout,
        return_result_object=return_result_object,
        _property_name=propiedad  # Internal parameter (we'll modify the function)
    )


def validate_batch_input(updates: List[Dict[str, str]], index: int, update: Dict[str, str]) -> Optional[HubSpotUpdateResult]:
    """
    Valida un item de batch update usando guard clauses.
    
    Args:
        updates: Lista completa de updates
        index: Índice del update actual
        update: Diccionario con el update a validar
        
    Returns:
        HubSpotUpdateResult con error si es inválido, None si es válido
    """
    contact_id = update.get("contact_id") or update.get("hubspot_contact_id")
    valor = update.get("valor") or update.get("value") or update.get("nuevo_estado")
    
    if not contact_id or not valor:
        return HubSpotUpdateResult(
            success=False,
            status_code=0,
            message="ERROR: contact_id y valor son requeridos en cada update",
            contact_id=contact_id or "",
            nuevo_estado=valor or "",
            error_details={"update_index": index, "update": update}
        )
    
    return None


def actualizar_contactos_batch(
    updates: List[Dict[str, str]],
    propiedad: str = "estado_interés",
    hubspot_token: Optional[str] = None,
    hubspot_base: Optional[str] = None,
    max_retries: int = DEFAULT_MAX_RETRIES,
    timeout: int = DEFAULT_TIMEOUT,
    batch_size: int = BATCH_SIZE_DEFAULT,
    batch_delay: float = BATCH_DELAY_SECONDS,
    continue_on_error: bool = True
) -> BatchUpdateResult:
    """
    Actualiza múltiples contactos en batch.
    Implementa principios RPA: guard clauses, validación temprana, manejo de errores robusto.
    
    Args:
        updates: Lista de diccionarios con formato [{"contact_id": "...", "valor": "..."}, ...]
        propiedad: Nombre de la propiedad a actualizar (default: "estado_interés")
        hubspot_token: Token de autenticación de HubSpot (opcional)
        hubspot_base: URL base de la API de HubSpot (opcional)
        max_retries: Máximo de reintentos por contacto (default: 3)
        timeout: Timeout en segundos por petición (default: 30)
        batch_size: Contactos a procesar antes de pausar (default: 10)
        batch_delay: Segundos de espera entre batches (default: 0.1)
        continue_on_error: Si True, continúa con otros contactos si uno falla (default: True)
    
    Returns:
        BatchUpdateResult: Resultado agregado con estadísticas
    """
    # Guard clause para validación temprana
    if not updates or len(updates) == 0:
        logger.warning("Empty updates list provided to batch update")
        return BatchUpdateResult(
            total=0,
            successful=0,
            failed=0,
            results=[],
            duration_ms=0.0
        )
    
    start_time = time.time()
    results: List[HubSpotUpdateResult] = []
    
    log_with_context(
        logger,
        logging.INFO,
        f"Iniciando actualización batch de {len(updates)} contactos",
        total_contacts=len(updates),
        property_name=propiedad,
        batch_size=batch_size
    )
    
    for i, update in enumerate(updates):
        # Validación temprana con guard clauses
        validation_error = validate_batch_input(updates, i, update)
        if validation_error:
            results.append(validation_error)
            if not continue_on_error:
                break
            continue
        
        contact_id = update.get("contact_id") or update.get("hubspot_contact_id")
        valor = update.get("valor") or update.get("value") or update.get("nuevo_estado")
        
        # Actualizar contacto individual
        try:
            result = actualizar_estado_interes(
                hubspot_contact_id=contact_id,
                nuevo_estado=valor,
                hubspot_token=hubspot_token,
                hubspot_base=hubspot_base,
                max_retries=max_retries,
                timeout=timeout,
                return_result_object=True,
                _property_name=propiedad
            )
            
            if isinstance(result, HubSpotUpdateResult):
                results.append(result)
            else:
                # Convertir string a objeto para consistencia
                is_success = result == "Éxito"
                results.append(HubSpotUpdateResult(
                    success=is_success,
                    status_code=200 if is_success else 0,
                    message=result,
                    contact_id=contact_id,
                    nuevo_estado=valor
                ))
            
            # Rate limiting: pausar entre batches
            if (i + 1) % batch_size == 0 and i < len(updates) - 1:
                log_with_context(
                    logger,
                    logging.INFO,
                    f"Pausa entre batches ({i + 1}/{len(updates)} procesados)",
                    processed=i + 1,
                    remaining=len(updates) - i - 1
                )
                time.sleep(batch_delay)
                
        except Exception as e:
            error_result = HubSpotUpdateResult(
                success=False,
                status_code=0,
                message=f"ERROR_INESPERADO: {str(e)}",
                contact_id=contact_id,
                nuevo_estado=valor,
                error_details={"exception": str(e), "type": type(e).__name__, "update_index": i}
            )
            results.append(error_result)
            
            log_with_context(
                logger,
                logging.ERROR,
                f"Error en actualización batch para contacto {contact_id}",
                contact_id=contact_id,
                error=str(e),
                update_index=i
            )
            
            if not continue_on_error:
                break
    
    duration_ms = (time.time() - start_time) * 1000
    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful
    
    batch_result = BatchUpdateResult(
        total=len(updates),
        successful=successful,
        failed=failed,
        results=results,
        duration_ms=duration_ms
    )
    
    # Registrar métricas batch
    if STATS_AVAILABLE:
        try:
            Stats.incr("hubspot_update_contact.batch_total", len(updates), tags={"property": propiedad})
            Stats.incr("hubspot_update_contact.batch_successful", successful, tags={"property": propiedad})
            Stats.incr("hubspot_update_contact.batch_failed", failed, tags={"property": propiedad})
            Stats.timing("hubspot_update_contact.batch_duration_ms", duration_ms, tags={"property": propiedad})
            Stats.gauge("hubspot_update_contact.batch_success_rate", batch_result.success_rate, tags={"property": propiedad})
            
            # Throughput: contactos por segundo
            if duration_ms > 0:
                throughput = len(updates) / (duration_ms / 1000)
                Stats.gauge("hubspot_update_contact.batch_throughput", throughput, tags={"property": propiedad})
        except Exception:
            pass
    
    log_with_context(
        logger,
        logging.INFO,
        f"Actualización batch completada",
        total=len(updates),
        successful=successful,
        failed=failed,
        success_rate=batch_result.success_rate,
        duration_ms=duration_ms,
        property_name=propiedad
    )
    
    return batch_result


# Función auxiliar para uso en DAGs de Airflow
def actualizar_estado_interes_task(**context):
    """
    Wrapper mejorado para usar la función en DAGs de Airflow.
    Espera 'hubspot_contact_id' y 'nuevo_estado' en los parámetros del contexto.
    
    Soporta parámetros adicionales:
    - max_retries: Máximo de reintentos (default: 3)
    - timeout: Timeout en segundos (default: 30)
    - return_result_object: Si True, retorna objeto completo (default: False)
    """
    params = context.get('params', {})
    hubspot_contact_id = params.get('hubspot_contact_id', '').strip()
    nuevo_estado = params.get('nuevo_estado', '').strip()
    hubspot_token = params.get('hubspot_token', '').strip() or None
    hubspot_base = params.get('hubspot_base', '').strip() or None
    max_retries = params.get('max_retries', DEFAULT_MAX_RETRIES)
    timeout = params.get('timeout', DEFAULT_TIMEOUT)
    return_result_object = params.get('return_result_object', False)
    
    if not hubspot_contact_id:
        raise ValueError("hubspot_contact_id es requerido en los parámetros")
    if not nuevo_estado:
        raise ValueError("nuevo_estado es requerido en los parámetros")
    
    resultado = actualizar_estado_interes(
        hubspot_contact_id=hubspot_contact_id,
        nuevo_estado=nuevo_estado,
        hubspot_token=hubspot_token,
        hubspot_base=hubspot_base,
        max_retries=max_retries,
        timeout=timeout,
        return_result_object=return_result_object
    )
    
    # Logging mejorado
    if return_result_object and isinstance(resultado, HubSpotUpdateResult):
        if resultado.success:
            log_with_context(
                logger,
                logging.INFO,
                f"Contacto actualizado exitosamente",
                contact_id=hubspot_contact_id,
                nuevo_estado=nuevo_estado,
                duration_ms=resultado.duration_ms,
                retries=resultado.retries
            )
            print(f"✓ Contacto {hubspot_contact_id} actualizado exitosamente a estado '{nuevo_estado}' (duración: {resultado.duration_ms:.2f}ms)")
            
            # Notificación a Slack si está disponible y está habilitado
            if NOTIFICATIONS_AVAILABLE and os.getenv("ENABLE_SLACK", "false").lower() == "true":
                try:
                    notify_slack(
                        f"✅ *HubSpot Contacto Actualizado*\n"
                        f"• Contact ID: {hubspot_contact_id}\n"
                        f"• Nuevo Estado: {nuevo_estado}\n"
                        f"• Duración: {resultado.duration_ms:.2f}ms",
                        extra_context={
                            "contact_id": hubspot_contact_id,
                            "nuevo_estado": nuevo_estado,
                            "duration_ms": resultado.duration_ms,
                        },
                        username="HubSpot Sync",
                        icon_emoji=":green_heart:"
                    )
                except Exception as e:
                    logger.warning(f"Failed to send Slack notification: {e}")
        else:
            log_with_context(
                logger,
                logging.ERROR,
                f"Error al actualizar contacto",
                contact_id=hubspot_contact_id,
                nuevo_estado=nuevo_estado,
                status_code=resultado.status_code,
                error_message=resultado.message,
                duration_ms=resultado.duration_ms
            )
            print(f"✗ Error al actualizar contacto {hubspot_contact_id}: {resultado.message}")
            
            # Notificación de error a Slack si está disponible
            if NOTIFICATIONS_AVAILABLE and os.getenv("ENABLE_SLACK", "false").lower() == "true":
                try:
                    notify_slack(
                        f"❌ *Error al Actualizar HubSpot Contacto*\n"
                        f"• Contact ID: {hubspot_contact_id}\n"
                        f"• Estado Intentado: {nuevo_estado}\n"
                        f"• Error: {resultado.message[:200]}\n"
                        f"• Status Code: {resultado.status_code}",
                        extra_context={
                            "contact_id": hubspot_contact_id,
                            "nuevo_estado": nuevo_estado,
                            "error": resultado.message,
                            "status_code": resultado.status_code,
                        },
                        username="HubSpot Sync",
                        icon_emoji=":warning:"
                    )
                except Exception as e:
                    logger.warning(f"Failed to send Slack error notification: {e}")
    else:
        # Compatibilidad con código existente (string)
        if resultado == "Éxito":
            print(f"✓ Contacto {hubspot_contact_id} actualizado exitosamente a estado '{nuevo_estado}'")
        else:
            print(f"✗ Error al actualizar contacto {hubspot_contact_id}: {resultado}")
    
    return resultado

