"""
Módulo para crear facturas en QuickBooks cuando se emite una factura en Stripe.
Si se detecta un pago inmediato en Stripe, marca la factura como pagada en QuickBooks.

Mejorado con librerías modernas y patrones avanzados:
- stripe: Librería oficial de Stripe
- tenacity: Retries automáticos con exponential backoff
- httpx: Cliente HTTP moderno (alternativa a requests)
- pendulum: Manejo mejorado de fechas
- pydantic: Validación de datos robusta
- dataclasses: Estructuración de resultados
- cachetools: Cache para optimización
- circuitbreaker: Circuit breaker para proteger APIs (opcional)
- concurrent.futures: Procesamiento paralelo para batch
- métricas y observabilidad mejoradas
- rate limiting inteligente con manejo de 429
- HTTP session pooling para mejor performance
- context managers para gestión de recursos
- logging estructurado con contexto
- notificaciones de errores críticos
- health checks para monitoreo
- procesamiento batch con paralelización
- excepciones personalizadas para mejor manejo de errores
"""
import os
import logging
import time
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, field
from decimal import Decimal
from functools import lru_cache
from contextlib import contextmanager

# Librerías mejoradas
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False

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
        HTTPX_AVAILABLE = False
    except ImportError:
        pass

try:
    import pendulum
    PENDULUM_AVAILABLE = True
except ImportError:
    PENDULUM_AVAILABLE = False
    from datetime import datetime as dt

try:
    from pydantic import BaseModel, Field, field_validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

try:
    from cachetools import TTLCache
    CACHETOOLS_AVAILABLE = True
except ImportError:
    CACHETOOLS_AVAILABLE = False

try:
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False

try:
    from circuitbreaker import circuit
    CIRCUITBREAKER_AVAILABLE = True
except ImportError:
    CIRCUITBREAKER_AVAILABLE = False

try:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    CONCURRENT_FUTURES_AVAILABLE = True
except ImportError:
    CONCURRENT_FUTURES_AVAILABLE = False

from enum import Enum

# Importar utilidades de logging del stack si están disponibles
try:
    from plugins.etl_logging import get_task_logger, log_with_context
    LOGGING_PLUGIN_AVAILABLE = True
except ImportError:
    try:
        from data.airflow.plugins.etl_logging import get_task_logger, log_with_context
        LOGGING_PLUGIN_AVAILABLE = True
    except ImportError:
        LOGGING_PLUGIN_AVAILABLE = False
        get_task_logger = lambda x: logging.getLogger(__name__)
        def log_with_context(logger, level, msg, **kwargs):
            logger.log(level, msg, extra=kwargs)

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


# Configuración
logger = get_task_logger("stripe_invoice_to_quickbooks")

QUICKBOOKS_ACCESS_TOKEN = os.environ.get("QUICKBOOKS_ACCESS_TOKEN", "")
QUICKBOOKS_REALM_ID = os.environ.get("QUICKBOOKS_REALM_ID", "")
QUICKBOOKS_COMPANY_ID = os.environ.get("QUICKBOOKS_COMPANY_ID", "")
QUICKBOOKS_BASE = os.environ.get("QUICKBOOKS_BASE", "https://sandbox-quickbooks.api.intuit.com")
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")

# Configurar Stripe si está disponible
if STRIPE_AVAILABLE and STRIPE_API_KEY:
    stripe.api_key = STRIPE_API_KEY

# Constantes
DEFAULT_TIMEOUT = 30
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1  # segundos
RATE_LIMIT_DELAY = 0.5  # Delay base entre requests (segundos)
MAX_RATE_LIMIT_WAIT = 300  # Máximo de espera por rate limit (5 minutos)
CUSTOMER_CACHE_TTL = 3600  # Cache de clientes por 1 hora
QUICKBOOKS_RATE_LIMIT_DELAY = 0.5  # Delay entre requests a QuickBooks

# Cache para clientes (evitar búsquedas repetidas)
_customer_cache: Optional[Any] = None
if CACHETOOLS_AVAILABLE:
    _customer_cache = TTLCache(maxsize=500, ttl=CUSTOMER_CACHE_TTL)

# Session pooling para mejor performance
_http_session_quickbooks: Optional[Any] = None
_http_session_stripe: Optional[Any] = None


# Excepciones personalizadas
class QuickBooksError(Exception):
    """Excepción base para errores de QuickBooks."""
    pass


class QuickBooksAuthError(QuickBooksError):
    """Error de autenticación con QuickBooks."""
    pass


class QuickBooksAPIError(QuickBooksError):
    """Error en la respuesta de la API de QuickBooks."""
    def __init__(self, message: str, status_code: Optional[int] = None, error_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_data = error_data


class QuickBooksValidationError(QuickBooksError):
    """Error de validación de parámetros."""
    pass


class StripeAPIError(Exception):
    """Error en la API de Stripe."""
    pass


# Enum para tipos de operaciones
class InvoiceOperationType(Enum):
    """Tipos de operaciones con facturas."""
    CREATE = "create"
    PAYMENT = "payment"
    LOOKUP = "lookup"


# Circuit breaker state tracking
_cb_failures = 0
_cb_last_failure_time = 0.0
_cb_state = "closed"  # closed, open, half_open


def _cb_record_failure() -> None:
    """Registra un fallo en el circuit breaker."""
    global _cb_failures, _cb_last_failure_time, _cb_state
    _cb_failures += 1
    _cb_last_failure_time = time.time()
    if _cb_failures >= 5:  # Abrir después de 5 fallos consecutivos
        _cb_state = "open"
        _record_metric("quickbooks.circuit_breaker.opened")
        logger.warning("Circuit breaker abierto después de 5 fallos consecutivos")


def _cb_record_success() -> None:
    """Registra un éxito en el circuit breaker."""
    global _cb_failures, _cb_state
    _cb_failures = 0
    if _cb_state == "open":
        _cb_state = "half_open"
        logger.info("Circuit breaker en half-open después de éxito")


def _cb_can_proceed() -> bool:
    """Verifica si el circuit breaker permite proceder."""
    global _cb_state, _cb_last_failure_time
    
    if _cb_state == "closed":
        return True
    
    if _cb_state == "open":
        # Intentar cerrar después de 60 segundos
        if time.time() - _cb_last_failure_time > 60:
            _cb_state = "half_open"
            logger.info("Circuit breaker intentando recuperarse (half-open)")
            return True
        return False
    
    if _cb_state == "half_open":
        return True
    
    return False


# Dataclasses para resultados estructurados
@dataclass
class StripeInvoiceResult:
    """Resultado de la obtención de factura de Stripe."""
    pagada: bool
    payment_intent_id: Optional[str] = None
    amount_paid: float = 0.0
    status: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario."""
        return {
            "pagada": self.pagada,
            "payment_intent_id": self.payment_intent_id,
            "amount_paid": self.amount_paid,
            "status": self.status,
            "error": self.error,
        }


@dataclass
class QuickBooksInvoiceResult:
    """Resultado de la creación de factura en QuickBooks."""
    qb_invoice_id: Optional[str]
    estado: str
    pagada: bool
    qb_payment_id: Optional[str] = None
    stripe_invoice_id: Optional[str] = None
    duration_ms: Optional[float] = None
    retries: int = 0
    error_details: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:
        """Representación en string para compatibilidad."""
        return self.estado if self.qb_invoice_id else self.estado

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario."""
        return {
            "qb_invoice_id": self.qb_invoice_id,
            "estado": self.estado,
            "pagada": self.pagada,
            "qb_payment_id": self.qb_payment_id,
            "stripe_invoice_id": self.stripe_invoice_id,
            "duration_ms": self.duration_ms,
            "retries": self.retries,
            "error_details": self.error_details,
        }

    @property
    def success(self) -> bool:
        """Indica si la operación fue exitosa."""
        return self.estado == "Éxito" and self.qb_invoice_id is not None


@dataclass
class BatchInvoiceResult:
    """Resultado de procesamiento batch de facturas."""
    total: int
    successful: int
    failed: int
    results: List[QuickBooksInvoiceResult]
    duration_ms: float
    
    @property
    def success_rate(self) -> float:
        """Tasa de éxito en porcentaje."""
        if self.total == 0:
            return 0.0
        return (self.successful / self.total) * 100.0
    
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


# Modelos Pydantic para validación (si está disponible)
if PYDANTIC_AVAILABLE:
    class StripeInvoiceInput(BaseModel):
        """Modelo de validación para entrada de factura de Stripe."""
        stripe_invoice_id: str = Field(..., min_length=1, max_length=255, description="ID de la factura en Stripe")
        correo_cliente: str = Field(..., pattern=r'^[^\s@]+@[^\s@]+\.[^\s@]+$', description="Correo electrónico válido")
        monto_factura: Decimal = Field(..., gt=0, decimal_places=2, description="Monto mayor que cero")
        fecha_vencimiento: str = Field(..., min_length=10, description="Fecha de vencimiento")
        cuenta_ingresos: Optional[str] = Field(default="Services", max_length=100)

        @field_validator('fecha_vencimiento')
        @classmethod
        def validate_date(cls, v: str) -> str:
            """Valida que la fecha sea parseable."""
            try:
                if PENDULUM_AVAILABLE:
                    pendulum.parse(v)
                else:
                    datetime.strptime(v[:10], "%Y-%m-%d")
            except Exception:
                raise ValueError(f"Fecha inválida: {v}")
            return v
else:
    # Fallback sin Pydantic
    class StripeInvoiceInput:
        """Fallback sin Pydantic."""
        def __init__(self, stripe_invoice_id: str, correo_cliente: str, 
                     monto_factura: float, fecha_vencimiento: str, 
                     cuenta_ingresos: str = "Services"):
            self.stripe_invoice_id = stripe_invoice_id
            self.correo_cliente = correo_cliente
            self.monto_factura = float(monto_factura)
            self.fecha_vencimiento = fecha_vencimiento
            self.cuenta_ingresos = cuenta_ingresos


def _formatear_fecha_quickbooks(fecha: str) -> str:
    """
    Formatea una fecha para QuickBooks API (YYYY-MM-DD).
    Usa pendulum si está disponible para mejor parsing.
    
    Args:
        fecha: Fecha en formato ISO o similar (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)
    
    Returns:
        str: Fecha formateada como YYYY-MM-DD
    """
    try:
        if PENDULUM_AVAILABLE:
            # Pendulum maneja automáticamente múltiples formatos
            fecha_obj = pendulum.parse(fecha)
            return fecha_obj.format("YYYY-MM-DD")
        else:
            # Fallback a datetime estándar
            if 'T' in fecha:
                fecha_obj = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
            else:
                fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
            return fecha_obj.strftime("%Y-%m-%d")
    except Exception as e:
        logger.warning(f"Error al formatear fecha '{fecha}': {e}")
        # Si falla, intentar devolver los primeros 10 caracteres (YYYY-MM-DD)
        return fecha[:10] if len(fecha) >= 10 else fecha


@contextmanager
def _get_http_client(pool_name: str = "default"):
    """
    Context manager para HTTP client con pooling y reutilización de conexiones.
    
    Args:
        pool_name: Nombre del pool ('quickbooks' o 'stripe' para pools específicos)
    
    Yields:
        HTTP client (httpx.Client o requests.Session)
    """
    global _http_session_quickbooks, _http_session_stripe
    
    if HTTPX_AVAILABLE:
        if pool_name == "quickbooks":
            if _http_session_quickbooks is None:
                _http_session_quickbooks = httpx.Client(
                    timeout=30.0,
                    limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
                )
            yield _http_session_quickbooks
        elif pool_name == "stripe":
            if _http_session_stripe is None:
                _http_session_stripe = httpx.Client(
                    timeout=30.0,
                    limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
                )
            yield _http_session_stripe
        else:
            # Pool genérico
            client = httpx.Client(timeout=30.0)
            try:
                yield client
            finally:
                client.close()
    else:
        # Usar requests con session
        import requests
        session = requests.Session()
        try:
            yield session
        finally:
            session.close()


def _handle_rate_limit(response: Any, operation: str = "") -> None:
    """
    Maneja rate limiting (429) de APIs.
    Espera según el header Retry-After si está disponible.
    
    Args:
        response: Objeto de respuesta HTTP
        operation: Nombre de la operación (para logging)
    """
    if hasattr(response, 'status_code') and response.status_code == 429:
        retry_after = 60  # Default: 60 segundos
        
        # Intentar obtener Retry-After del header
        if hasattr(response, 'headers'):
            headers = dict(response.headers) if HTTPX_AVAILABLE else response.headers
            retry_after_str = headers.get('Retry-After', headers.get('retry-after', ''))
            if retry_after_str:
                try:
                    retry_after = int(retry_after_str)
                except (ValueError, TypeError):
                    pass
        
        wait_time = min(retry_after, MAX_RATE_LIMIT_WAIT)
        
        _record_metric("quickbooks.api.rate_limit_hit", tags={"operation": operation})
        _cb_record_failure()  # Registrar rate limit como fallo en circuit breaker
        
        log_with_context(
            logger,
            logging.WARNING,
            f"Rate limited en {operation}, esperando {wait_time}s",
            operation=operation,
            retry_after=wait_time
        )
        
        time.sleep(wait_time)
        
        if hasattr(response, 'raise_for_status'):
            response.raise_for_status()


def crear_facturas_batch(
    facturas: List[Dict[str, Any]],
    qb_access_token: Optional[str] = None,
    qb_realm_id: Optional[str] = None,
    qb_base: Optional[str] = None,
    max_workers: int = 3,
    continue_on_error: bool = True
) -> BatchInvoiceResult:
    """
    Procesa múltiples facturas en batch con procesamiento paralelo opcional.
    
    Args:
        facturas: Lista de diccionarios con datos de facturas:
            - stripe_invoice_id: ID de la factura en Stripe
            - correo_cliente: Correo electrónico del cliente
            - monto_factura: Monto total de la factura
            - fecha_vencimiento: Fecha de vencimiento
            - cuenta_ingresos: (opcional) Nombre de cuenta de ingresos
        qb_access_token: Token de acceso de QuickBooks (opcional)
        qb_realm_id: ID de la compañía en QuickBooks (opcional)
        qb_base: URL base de QuickBooks API (opcional)
        max_workers: Número máximo de workers paralelos (default: 3)
        continue_on_error: Si True, continúa procesando aunque falle alguna (default: True)
    
    Returns:
        BatchInvoiceResult con estadísticas agregadas
    """
    start_time = time.time()
    results: List[QuickBooksInvoiceResult] = []
    successful = 0
    failed = 0
    
    if not facturas:
        return BatchInvoiceResult(
            total=0,
            successful=0,
            failed=0,
            results=[],
            duration_ms=0.0
        )
    
    def process_invoice(invoice_data: Dict[str, Any]) -> QuickBooksInvoiceResult:
        """Procesa una factura individual."""
        try:
            return crear_factura_quickbooks(
                stripe_invoice_id=invoice_data.get("stripe_invoice_id", ""),
                correo_cliente=invoice_data.get("correo_cliente", ""),
                monto_factura=invoice_data.get("monto_factura", 0.0),
                fecha_vencimiento=invoice_data.get("fecha_vencimiento", ""),
                cuenta_ingresos=invoice_data.get("cuenta_ingresos", "Services"),
                qb_access_token=qb_access_token,
                qb_realm_id=qb_realm_id,
                qb_base=qb_base
            )
        except Exception as e:
            logger.error(f"Error al procesar factura {invoice_data.get('stripe_invoice_id')}: {e}")
            return QuickBooksInvoiceResult(
                qb_invoice_id=None,
                estado=f"ERROR: {str(e)}",
                pagada=False,
                stripe_invoice_id=invoice_data.get("stripe_invoice_id"),
                error_details={"exception": str(e)}
            )
    
    # Procesamiento paralelo si está disponible y max_workers > 1
    if CONCURRENT_FUTURES_AVAILABLE and max_workers > 1 and len(facturas) > 1:
        logger.info(f"Procesando {len(facturas)} facturas en paralelo con {max_workers} workers")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_invoice = {
                executor.submit(process_invoice, invoice): invoice 
                for invoice in facturas
            }
            
            for future in as_completed(future_to_invoice):
                invoice = future_to_invoice[future]
                try:
                    result = future.result()
                    results.append(result)
                    if result.success:
                        successful += 1
                        _cb_record_success()
                    else:
                        failed += 1
                        if not continue_on_error:
                            logger.warning(f"Error en factura {invoice.get('stripe_invoice_id')}, deteniendo batch")
                            break
                        _cb_record_failure()
                except Exception as e:
                    failed += 1
                    _cb_record_failure()
                    error_result = QuickBooksInvoiceResult(
                        qb_invoice_id=None,
                        estado=f"ERROR_EXCEPTION: {str(e)}",
                        pagada=False,
                        stripe_invoice_id=invoice.get("stripe_invoice_id"),
                        error_details={"exception": str(e), "type": type(e).__name__}
                    )
                    results.append(error_result)
                    if not continue_on_error:
                        logger.error(f"Excepción en factura {invoice.get('stripe_invoice_id')}, deteniendo batch")
                        break
    else:
        # Procesamiento secuencial
        logger.info(f"Procesando {len(facturas)} facturas secuencialmente")
        for invoice in facturas:
            result = process_invoice(invoice)
            results.append(result)
            if result.success:
                successful += 1
                _cb_record_success()
            else:
                failed += 1
                _cb_record_failure()
                if not continue_on_error:
                    logger.warning(f"Error en factura {invoice.get('stripe_invoice_id')}, deteniendo batch")
                    break
    
    duration_ms = (time.time() - start_time) * 1000
    
    batch_result = BatchInvoiceResult(
        total=len(facturas),
        successful=successful,
        failed=failed,
        results=results,
        duration_ms=duration_ms
    )
    
    _record_metric("quickbooks.invoice.batch.processed", value=len(facturas))
    _record_metric("quickbooks.invoice.batch.success", value=successful)
    _record_metric("quickbooks.invoice.batch.failed", value=failed)
    _record_metric("quickbooks.invoice.batch.duration", value=duration_ms)
    
    logger.info(
        f"Batch processing completado: {successful}/{len(facturas)} exitosos "
        f"({batch_result.success_rate:.1f}%), duración: {duration_ms:.2f}ms"
    )
    
    return batch_result


def health_check(
    qb_access_token: Optional[str] = None,
    qb_realm_id: Optional[str] = None,
    stripe_api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Realiza un health check del sistema de sincronización.
    
    Args:
        qb_access_token: Token de acceso de QuickBooks (opcional)
        qb_realm_id: ID de la compañía en QuickBooks (opcional)
        stripe_api_key: API key de Stripe (opcional)
    
    Returns:
        Dict con el estado de salud de cada componente
    """
    health_status = {
        "status": "ok",
        "timestamp": time.time(),
        "checks": {}
    }
    
    # Verificar QuickBooks
    access_token = qb_access_token or QUICKBOOKS_ACCESS_TOKEN
    realm_id = qb_realm_id or QUICKBOOKS_REALM_ID
    
    try:
        if access_token and realm_id:
            # Intentar una búsqueda simple para verificar conectividad
            base_url = QUICKBOOKS_BASE
            url = f"{base_url}/v3/company/{realm_id}/query"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
                "Content-Type": "application/text"
            }
            params = {"minorversion": "65", "query": "SELECT COUNT(*) FROM Customer MAXRESULTS 1"}
            
            with _get_http_client("quickbooks") as client:
                if HTTPX_AVAILABLE:
                    response = client.get(url, headers=headers, params=params)
                else:
                    response = client.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    health_status["checks"]["quickbooks"] = {
                        "status": "ok",
                        "message": "QuickBooks API accesible"
                    }
                else:
                    health_status["checks"]["quickbooks"] = {
                        "status": "error",
                        "error": f"HTTP {response.status_code}"
                    }
                    health_status["status"] = "error"
        else:
            health_status["checks"]["quickbooks"] = {
                "status": "warning",
                "message": "Credenciales de QuickBooks no configuradas"
            }
    except Exception as e:
        health_status["checks"]["quickbooks"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "error"
    
    # Verificar Stripe
    api_key = stripe_api_key or STRIPE_API_KEY
    try:
        if api_key:
            if STRIPE_AVAILABLE:
                stripe.api_key = api_key
                # Intentar obtener cuenta
                account = stripe.Account.retrieve()
                health_status["checks"]["stripe"] = {
                    "status": "ok",
                    "message": f"Stripe conectado (Account: {account.id})"
                }
            else:
                # Fallback a HTTP
                url = "https://api.stripe.com/v1/account"
                headers = {"Authorization": f"Bearer {api_key}"}
                
                with _get_http_client("stripe") as client:
                    if HTTPX_AVAILABLE:
                        response = client.get(url, headers=headers)
                    else:
                        response = client.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        health_status["checks"]["stripe"] = {
                            "status": "ok",
                            "message": "Stripe API accesible"
                        }
                    else:
                        health_status["checks"]["stripe"] = {
                            "status": "error",
                            "error": f"HTTP {response.status_code}"
                        }
                        health_status["status"] = "error"
        else:
            health_status["checks"]["stripe"] = {
                "status": "warning",
                "message": "API key de Stripe no configurada"
            }
    except Exception as e:
        health_status["checks"]["stripe"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "error"
    
    # Verificar circuit breaker
    health_status["checks"]["circuit_breaker"] = {
        "status": "ok" if _cb_can_proceed() else "open",
        "state": _cb_state,
        "failures": _cb_failures
    }
    if not _cb_can_proceed():
        health_status["status"] = "degraded"
    
    # Verificar cache
    if CACHETOOLS_AVAILABLE and _customer_cache is not None:
        cache_size = len(_customer_cache)
        health_status["checks"]["cache"] = {
            "status": "ok",
            "size": cache_size,
            "max_size": _customer_cache.maxsize
        }
    else:
        health_status["checks"]["cache"] = {
            "status": "warning",
            "message": "Cache no disponible"
        }
    
    return health_status


def _buscar_cliente_por_email(
    email: str,
    access_token: str,
    realm_id: str,
    quickbooks_base: Optional[str] = None,
    use_cache: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Busca un cliente en QuickBooks por su correo electrónico.
    Usa retries automáticos si tenacity está disponible y cache para optimización.
    
    Args:
        email: Correo electrónico del cliente
        access_token: Token de acceso de QuickBooks
        realm_id: ID de la compañía en QuickBooks
        quickbooks_base: URL base de QuickBooks API (opcional)
        use_cache: Si True, usa cache para evitar búsquedas repetidas
    
    Returns:
        dict con datos del cliente si se encuentra, None si no existe
    """
    base_url = quickbooks_base or QUICKBOOKS_BASE
    
    if not email:
        return None
    
    # Verificar cache primero
    cache_key = f"{realm_id}:{email.lower()}"
    if use_cache and CACHETOOLS_AVAILABLE and _customer_cache is not None:
        cached = _customer_cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Cliente encontrado en cache: {email}")
            _record_metric("quickbooks.customer.lookup.cache_hit")
            return cached
        _record_metric("quickbooks.customer.lookup.cache_miss")
    
    # Query para buscar cliente por email (escapar comillas para SQL injection)
    email_escaped = email.replace("'", "''")
    query = f"SELECT * FROM Customer WHERE PrimaryEmailAddr.Address = '{email_escaped}' MAXRESULTS 1"
    url = f"{base_url}/v3/company/{realm_id}/query"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/text"
    }
    params = {"minorversion": "65", "query": query}
    
    def _make_request():
        """Función interna para hacer la petición (para retries)."""
        with _get_http_client("quickbooks") as client:
            if HTTPX_AVAILABLE:
                response = client.get(url, headers=headers, params=params)
                _handle_rate_limit(response, "customer_lookup")
                response.raise_for_status()
                result = response.json()
            else:
                response = client.get(url, headers=headers, params=params)
                _handle_rate_limit(response, "customer_lookup")
                response.raise_for_status()
                result = response.json()
            
            # Delay para respetar rate limits
            time.sleep(QUICKBOOKS_RATE_LIMIT_DELAY)
            return result
    
    # Aplicar retries si tenacity está disponible
    if TENACITY_AVAILABLE:
        try:
            make_request_with_retry = retry(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=2, max=10),
                retry=retry_if_exception_type((httpx.HTTPError if HTTPX_AVAILABLE else Exception)),
                reraise=True
            )(_make_request)
            data = make_request_with_retry()
        except RetryError as e:
            logger.error(f"Error después de reintentos al buscar cliente: {e}")
            return None
        except Exception as e:
            logger.warning(f"Error al buscar cliente: {e}")
            return None
    else:
        try:
            data = _make_request()
        except Exception as e:
            logger.warning(f"Error al buscar cliente: {e}")
            return None
    
    try:
        query_response = data.get("QueryResponse", {})
        customers = query_response.get("Customer", [])
        
        if customers:
            # QuickBooks puede devolver un array o un objeto único
            customer = customers[0] if isinstance(customers, list) else customers
            
            # Guardar en cache
            if use_cache and CACHETOOLS_AVAILABLE and _customer_cache is not None:
                _customer_cache[cache_key] = customer
            
            _record_metric("quickbooks.customer.lookup.success")
            return customer
        
        _record_metric("quickbooks.customer.lookup.not_found")
        return None
    except Exception as e:
        logger.error(f"Error al procesar respuesta de QuickBooks: {e}")
        _record_metric("quickbooks.customer.lookup.error")
        return None


def _record_metric(metric_name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None) -> None:
    """Registra una métrica si Stats está disponible."""
    if STATS_AVAILABLE:
        try:
            Stats.incr(metric_name, value, tags=tags or {})
        except Exception as e:
            logger.debug(f"Error al registrar métrica {metric_name}: {e}")


def _notify_error(error_msg: str, details: Optional[Dict[str, Any]] = None, level: str = "error") -> None:
    """
    Notifica errores críticos a Slack si está disponible.
    
    Args:
        error_msg: Mensaje de error
        details: Detalles adicionales del error
        level: Nivel de severidad ('error', 'warning', 'critical')
    """
    if NOTIFICATIONS_AVAILABLE:
        try:
            message = f"⚠️ Error en Stripe→QuickBooks Sync: {error_msg}"
            if details:
                message += f"\nDetalles: {details}"
            notify_slack(message, level=level)
        except Exception as e:
            logger.debug(f"Error al enviar notificación: {e}")


def _obtener_estado_pago_stripe(stripe_invoice_id: str, stripe_api_key: Optional[str] = None) -> StripeInvoiceResult:
    """
    Obtiene el estado de pago de una factura de Stripe.
    Usa la librería oficial de Stripe si está disponible.
    
    Args:
        stripe_invoice_id: ID de la factura en Stripe
        stripe_api_key: API key de Stripe (opcional)
    
    Returns:
        StripeInvoiceResult con el estado de la factura
    """
    start_time = time.time()
    api_key = stripe_api_key or STRIPE_API_KEY
    
    if not api_key:
        logger.warning("STRIPE_API_KEY no configurado, no se puede verificar estado de pago")
        _record_metric("stripe.invoice.status_check.failed", tags={"reason": "no_api_key"})
        return StripeInvoiceResult(pagada=False, error="STRIPE_API_KEY no configurado")
    
    if not stripe_invoice_id:
        _record_metric("stripe.invoice.status_check.failed", tags={"reason": "invalid_id"})
        return StripeInvoiceResult(pagada=False, error="stripe_invoice_id requerido")
    
    try:
        if STRIPE_AVAILABLE:
            # Usar librería oficial de Stripe (recomendado)
            stripe.api_key = api_key
            invoice = stripe.Invoice.retrieve(stripe_invoice_id)
            
            result = StripeInvoiceResult(
                pagada=invoice.paid or invoice.status == "paid",
                payment_intent_id=invoice.payment_intent if hasattr(invoice, 'payment_intent') else None,
                amount_paid=(invoice.amount_paid or 0) / 100.0,
                status=invoice.status
            )
            
            duration_ms = (time.time() - start_time) * 1000
            _record_metric("stripe.invoice.status_check.success", tags={"paid": str(result.pagada)})
            _record_metric("stripe.invoice.status_check.duration", value=duration_ms)
            
            return result
        else:
            # Fallback a requests/httpx
            url = f"https://api.stripe.com/v1/invoices/{stripe_invoice_id}"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            with _get_http_client("stripe") as client:
                if HTTPX_AVAILABLE:
                    response = client.get(url, headers=headers)
                    _handle_rate_limit(response, "stripe_invoice_get")
                    response.raise_for_status()
                    invoice_data = response.json()
                else:
                    response = client.get(url, headers=headers)
                    _handle_rate_limit(response, "stripe_invoice_get")
                    response.raise_for_status()
                    invoice_data = response.json()
            
            result = StripeInvoiceResult(
                pagada=invoice_data.get("paid", False) or invoice_data.get("status", "") == "paid",
                payment_intent_id=invoice_data.get("payment_intent"),
                amount_paid=(invoice_data.get("amount_paid", 0) or 0) / 100.0,
                status=invoice_data.get("status")
            )
            
            duration_ms = (time.time() - start_time) * 1000
            _record_metric("stripe.invoice.status_check.success", tags={"paid": str(result.pagada)})
            _record_metric("stripe.invoice.status_check.duration", value=duration_ms)
            
            return result
            
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"Error al obtener estado de pago de Stripe para {stripe_invoice_id}: {e}")
        _record_metric("stripe.invoice.status_check.failed", tags={"reason": "exception"})
        _record_metric("stripe.invoice.status_check.duration", value=duration_ms)
        return StripeInvoiceResult(pagada=False, error=str(e))


def crear_factura_quickbooks(
    stripe_invoice_id: str,
    correo_cliente: str,
    monto_factura: float,
    fecha_vencimiento: str,
    qb_access_token: Optional[str] = None,
    qb_realm_id: Optional[str] = None,
    qb_base: Optional[str] = None,
    cuenta_ingresos: str = "Services",
    stripe_api_key: Optional[str] = None,
    validate_input: bool = True
) -> QuickBooksInvoiceResult:
    """
    Crea una factura en QuickBooks basada en una factura de Stripe.
    Si se detecta un pago inmediato, marca la factura como pagada.
    
    Args:
        stripe_invoice_id: ID de la factura en Stripe
        correo_cliente: Correo electrónico del cliente
        monto_factura: Monto total de la factura
        fecha_vencimiento: Fecha de vencimiento (YYYY-MM-DD o ISO format)
        qb_access_token: Token de acceso de QuickBooks (opcional, usa env var si no se proporciona)
        qb_realm_id: ID de la compañía en QuickBooks (opcional, usa env var si no se proporciona)
        qb_base: URL base de la API de QuickBooks (opcional, usa env var si no se proporciona)
        cuenta_ingresos: Nombre de la cuenta de ingresos en QuickBooks (default: "Services")
        stripe_api_key: API key de Stripe para verificar estado de pago (opcional)
        validate_input: Si True, valida los parámetros con Pydantic (si está disponible)
    
    Returns:
        QuickBooksInvoiceResult con el resultado de la operación
    """
    start_time = time.time()
    retries_count = 0
    
    # Validar entrada si Pydantic está disponible
    if validate_input and PYDANTIC_AVAILABLE:
        try:
            validated = StripeInvoiceInput(
                stripe_invoice_id=stripe_invoice_id,
                correo_cliente=correo_cliente,
                monto_factura=Decimal(str(monto_factura)),
                fecha_vencimiento=fecha_vencimiento,
                cuenta_ingresos=cuenta_ingresos
            )
            monto_factura = float(validated.monto_factura)
            fecha_vencimiento = validated.fecha_vencimiento
            cuenta_ingresos = validated.cuenta_ingresos
        except Exception as e:
            error_msg = f"Error de validación: {str(e)}"
            logger.error(error_msg)
            _record_metric("quickbooks.invoice.create.validation_error")
            return QuickBooksInvoiceResult(
                qb_invoice_id=None,
                estado=f"ERROR_VALIDACION: {error_msg}",
                pagada=False,
                error_details={"validation_error": str(e)}
            )
    # Usar parámetros proporcionados o variables de entorno
    access_token = qb_access_token or QUICKBOOKS_ACCESS_TOKEN
    realm_id = qb_realm_id or QUICKBOOKS_REALM_ID
    base_url = qb_base or QUICKBOOKS_BASE
    
    if not access_token:
        duration_ms = (time.time() - start_time) * 1000
        _record_metric("quickbooks.invoice.create.failed", tags={"reason": "no_token"})
        return QuickBooksInvoiceResult(
            qb_invoice_id=None,
            estado="ERROR: QUICKBOOKS_ACCESS_TOKEN no configurado",
            pagada=False,
            duration_ms=duration_ms
        )
    
    if not realm_id:
        duration_ms = (time.time() - start_time) * 1000
        _record_metric("quickbooks.invoice.create.failed", tags={"reason": "no_realm_id"})
        return QuickBooksInvoiceResult(
            qb_invoice_id=None,
            estado="ERROR: QUICKBOOKS_REALM_ID no configurado",
            pagada=False,
            duration_ms=duration_ms
        )
    
    if not stripe_invoice_id:
        duration_ms = (time.time() - start_time) * 1000
        _record_metric("quickbooks.invoice.create.failed", tags={"reason": "no_invoice_id"})
        return QuickBooksInvoiceResult(
            qb_invoice_id=None,
            estado="ERROR: stripe_invoice_id es requerido",
            pagada=False,
            duration_ms=duration_ms
        )
    
    if monto_factura <= 0:
        duration_ms = (time.time() - start_time) * 1000
        _record_metric("quickbooks.invoice.create.failed", tags={"reason": "invalid_amount"})
        return QuickBooksInvoiceResult(
            qb_invoice_id=None,
            estado="ERROR: monto_factura debe ser mayor que cero",
            pagada=False,
            duration_ms=duration_ms
        )
    
    if not correo_cliente:
        duration_ms = (time.time() - start_time) * 1000
        _record_metric("quickbooks.invoice.create.failed", tags={"reason": "no_email"})
        return QuickBooksInvoiceResult(
            qb_invoice_id=None,
            estado="ERROR: correo_cliente es requerido",
            pagada=False,
            duration_ms=duration_ms
        )
    
    try:
        # 1. Buscar cliente por email
        cliente = _buscar_cliente_por_email(
            email=correo_cliente,
            access_token=access_token,
            realm_id=realm_id,
            quickbooks_base=base_url
        )
        
        if not cliente:
            duration_ms = (time.time() - start_time) * 1000
            _record_metric("quickbooks.invoice.create.failed", tags={"reason": "customer_not_found"})
            return QuickBooksInvoiceResult(
                qb_invoice_id=None,
                estado=f"ERROR: No se encontró cliente con email {correo_cliente} en QuickBooks. Cree el cliente primero.",
                pagada=False,
                stripe_invoice_id=stripe_invoice_id,
                duration_ms=duration_ms
            )
        
        customer_id = cliente.get("Id")
        if not customer_id:
            duration_ms = (time.time() - start_time) * 1000
            _record_metric("quickbooks.invoice.create.failed", tags={"reason": "customer_id_missing"})
            return QuickBooksInvoiceResult(
                qb_invoice_id=None,
                estado="ERROR: No se pudo obtener el ID del cliente de QuickBooks",
                pagada=False,
                stripe_invoice_id=stripe_invoice_id,
                duration_ms=duration_ms
            )
        
        # 2. Verificar estado de pago en Stripe
        estado_pago = _obtener_estado_pago_stripe(stripe_invoice_id, stripe_api_key)
        pago_inmediato = estado_pago.pagada
        
        # 3. Formatear fecha de vencimiento
        fecha_vencimiento_formateada = _formatear_fecha_quickbooks(fecha_vencimiento)
        if PENDULUM_AVAILABLE:
            fecha_actual = pendulum.now().format("YYYY-MM-DD")
        else:
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
        
        # 4. Crear factura en QuickBooks
        url = f"{base_url}/v3/company/{realm_id}/invoice"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        params = {"minorversion": "65"}
        
        # Construir línea de item para la factura
        line_item = {
            "DetailType": "SalesItemLineDetail",
            "Amount": str(monto_factura),
            "Description": f"Factura Stripe - {stripe_invoice_id}",
            "SalesItemLineDetail": {
                "ItemRef": {
                    "name": cuenta_ingresos
                }
            }
        }
        
        # Construir payload de la factura
        # Nota: No establecemos Balance aquí, QuickBooks lo calculará automáticamente
        # Si hay pago inmediato, crearemos un Payment después para marcar como pagada
        payload = {
            "Line": [line_item],
            "CustomerRef": {
                "value": str(customer_id)
            },
            "TxnDate": fecha_actual,
            "DueDate": fecha_vencimiento_formateada,
            "PrivateNote": f"Factura Stripe ID: {stripe_invoice_id}",
            "DocNumber": stripe_invoice_id[:20] if len(stripe_invoice_id) > 20 else stripe_invoice_id,
            "TotalAmt": str(monto_factura)
        }
        
        # Crear la factura con retries si está disponible
        def _create_invoice():
            with _get_http_client("quickbooks") as client:
                if HTTPX_AVAILABLE:
                    response = client.post(url, headers=headers, json=payload, params=params)
                    _handle_rate_limit(response, "invoice_create")
                    response.raise_for_status()
                    result = response
                else:
                    response = client.post(url, headers=headers, json=payload, params=params)
                    _handle_rate_limit(response, "invoice_create")
                    result = response
                
                # Delay para respetar rate limits
                time.sleep(QUICKBOOKS_RATE_LIMIT_DELAY)
                return result
        
        if TENACITY_AVAILABLE:
            try:
                create_with_retry = retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=2, max=10),
                    retry=retry_if_exception_type((httpx.HTTPError if HTTPX_AVAILABLE else Exception)),
                    reraise=True
                )(_create_invoice)
                response = create_with_retry()
            except RetryError as e:
                duration_ms = (time.time() - start_time) * 1000
                retries_count = 3
                logger.error(f"Error después de reintentos al crear factura: {e}")
                _record_metric("quickbooks.invoice.create.failed", tags={"reason": "retry_exhausted"})
                _notify_error(
                    f"Error después de reintentos al crear factura {stripe_invoice_id}",
                    {"error": str(e), "retries": retries_count},
                    level="critical"
                )
                return QuickBooksInvoiceResult(
                    qb_invoice_id=None,
                    estado=f"ERROR_RETRY: Error después de múltiples intentos: {str(e)}",
                    pagada=False,
                    stripe_invoice_id=stripe_invoice_id,
                    duration_ms=duration_ms,
                    retries=retries_count
                )
        else:
            response = _create_invoice()
        
        # Obtener status code de forma compatible
        if HTTPX_AVAILABLE:
            status_code = response.status_code
        else:
            status_code = response.status_code if hasattr(response, 'status_code') else 200
        
        if status_code in [200, 201]:
            try:
                response_data = response.json()
                invoice = response_data.get("Invoice", {})
                qb_invoice_id = invoice.get("Id") or invoice.get("id")
                
                if not qb_invoice_id:
                    duration_ms = (time.time() - start_time) * 1000
                    _record_metric("quickbooks.invoice.create.failed", tags={"reason": "no_id_in_response"})
                    return QuickBooksInvoiceResult(
                        qb_invoice_id=None,
                        estado=f"Éxito pero no se pudo obtener el ID de la factura. Respuesta: {response_data}",
                        pagada=False,
                        stripe_invoice_id=stripe_invoice_id,
                        duration_ms=duration_ms
                    )
                
                qb_invoice_id = str(qb_invoice_id)
                
                # 5. Si hay pago inmediato, crear un Payment para marcar la factura como pagada
                if pago_inmediato:
                    payment_result = _crear_pago_quickbooks(
                        invoice_id=qb_invoice_id,
                        amount=monto_factura,
                        customer_id=customer_id,
                        access_token=access_token,
                        realm_id=realm_id,
                        quickbooks_base=base_url,
                        stripe_reference=stripe_invoice_id
                    )
                    
                    duration_ms = (time.time() - start_time) * 1000
                    
                    if payment_result.get("exitoso"):
                        _record_metric("quickbooks.invoice.create.success", tags={"paid": "true"})
                        _record_metric("quickbooks.invoice.create.duration", value=duration_ms)
                        _cb_record_success()  # Registrar éxito en circuit breaker
                        return QuickBooksInvoiceResult(
                            qb_invoice_id=qb_invoice_id,
                            estado="Éxito",
                            pagada=True,
                            qb_payment_id=payment_result.get("payment_id"),
                            stripe_invoice_id=stripe_invoice_id,
                            duration_ms=duration_ms,
                            retries=retries_count
                        )
                    else:
                        # La factura se creó pero no se pudo crear el pago
                        _record_metric("quickbooks.invoice.create.success", tags={"paid": "false", "payment_error": "true"})
                        _cb_record_success()  # La factura se creó, es un éxito parcial
                        return QuickBooksInvoiceResult(
                            qb_invoice_id=qb_invoice_id,
                            estado=f"Factura creada exitosamente, pero error al crear pago: {payment_result.get('error')}",
                            pagada=False,
                            stripe_invoice_id=stripe_invoice_id,
                            duration_ms=duration_ms,
                            retries=retries_count,
                            error_details={"payment_error": payment_result.get("error")}
                        )
                
                duration_ms = (time.time() - start_time) * 1000
                _record_metric("quickbooks.invoice.create.success", tags={"paid": "false"})
                _record_metric("quickbooks.invoice.create.duration", value=duration_ms)
                _cb_record_success()  # Registrar éxito en circuit breaker
                return QuickBooksInvoiceResult(
                    qb_invoice_id=qb_invoice_id,
                    estado="Éxito",
                    pagada=False,
                    stripe_invoice_id=stripe_invoice_id,
                    duration_ms=duration_ms,
                    retries=retries_count
                )
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                response_text = response.text if hasattr(response, 'text') else str(getattr(response, 'content', ''))[:200]
                _record_metric("quickbooks.invoice.create.failed", tags={"reason": "parse_error"})
                _cb_record_failure()  # Registrar fallo en circuit breaker
                return QuickBooksInvoiceResult(
                    qb_invoice_id=None,
                    estado=f"Éxito pero error al parsear respuesta: {str(e)}. Respuesta raw: {response_text}",
                    pagada=False,
                    stripe_invoice_id=stripe_invoice_id,
                    duration_ms=duration_ms,
                    error_details={"parse_error": str(e), "response_preview": response_text}
                )
        
        # Manejar errores de la API
        error_code = status_code
        try:
            if HTTPX_AVAILABLE:
                response_text = response.text
            else:
                response_text = getattr(response, 'text', '') or str(getattr(response, 'content', ''))
            
            error_data = response.json()
            faults = error_data.get("Fault", {})
            errors = faults.get("Error", [])
            if errors:
                error_message = errors[0].get("Message", "Error desconocido")
                error_detail = errors[0].get("Detail", "")
                full_message = f"{error_message}. {error_detail}" if error_detail else error_message
            else:
                error_message = error_data.get("message", response_text)
                full_message = error_message
        except Exception as e:
            full_message = response_text if 'response_text' in locals() else "Error desconocido"
            full_message = f"{full_message} (parse error: {str(e)})"
        
        duration_ms = (time.time() - start_time) * 1000
        _record_metric("quickbooks.invoice.create.failed", tags={"reason": f"http_{error_code}"})
        _cb_record_failure()  # Registrar fallo en circuit breaker
        return QuickBooksInvoiceResult(
            qb_invoice_id=None,
            estado=f"{error_code}: {full_message}",
            pagada=False,
            stripe_invoice_id=stripe_invoice_id,
            duration_ms=duration_ms,
            retries=retries_count,
            error_details={"http_status": error_code, "error_message": full_message}
        )
        
    except Exception as e:
        # Manejar diferentes tipos de excepciones
        error_type = type(e).__name__
        
        duration_ms = (time.time() - start_time) * 1000
        
        if HTTPX_AVAILABLE:
            if isinstance(e, httpx.TimeoutException):
                _record_metric("quickbooks.invoice.create.failed", tags={"reason": "timeout"})
                return QuickBooksInvoiceResult(
                    qb_invoice_id=None,
                    estado="ERROR_TIMEOUT: La petición a QuickBooks excedió el tiempo límite",
                    pagada=False,
                    stripe_invoice_id=stripe_invoice_id,
                    duration_ms=duration_ms,
                    retries=retries_count
                )
            elif isinstance(e, httpx.ConnectError):
                _record_metric("quickbooks.invoice.create.failed", tags={"reason": "connection_error"})
                return QuickBooksInvoiceResult(
                    qb_invoice_id=None,
                    estado="ERROR_CONNECTION: No se pudo conectar con QuickBooks API",
                    pagada=False,
                    stripe_invoice_id=stripe_invoice_id,
                    duration_ms=duration_ms,
                    retries=retries_count
                )
            elif isinstance(e, httpx.HTTPError):
                _record_metric("quickbooks.invoice.create.failed", tags={"reason": "http_error"})
                return QuickBooksInvoiceResult(
                    qb_invoice_id=None,
                    estado=f"ERROR_HTTP: {str(e)}",
                    pagada=False,
                    stripe_invoice_id=stripe_invoice_id,
                    duration_ms=duration_ms,
                    retries=retries_count
                )
        
        # Fallback para requests o errores genéricos
        import requests
        if isinstance(e, requests.exceptions.Timeout):
            _record_metric("quickbooks.invoice.create.failed", tags={"reason": "timeout"})
            _cb_record_failure()
            return QuickBooksInvoiceResult(
                qb_invoice_id=None,
                estado="ERROR_TIMEOUT: La petición a QuickBooks excedió el tiempo límite",
                pagada=False,
                stripe_invoice_id=stripe_invoice_id,
                duration_ms=duration_ms,
                retries=retries_count
            )
        elif isinstance(e, requests.exceptions.ConnectionError):
            _record_metric("quickbooks.invoice.create.failed", tags={"reason": "connection_error"})
            _cb_record_failure()
            return QuickBooksInvoiceResult(
                qb_invoice_id=None,
                estado="ERROR_CONNECTION: No se pudo conectar con QuickBooks API",
                pagada=False,
                stripe_invoice_id=stripe_invoice_id,
                duration_ms=duration_ms,
                retries=retries_count
            )
        elif "Timeout" in error_type or "timeout" in str(e).lower():
            _record_metric("quickbooks.invoice.create.failed", tags={"reason": "timeout"})
            _cb_record_failure()
            return QuickBooksInvoiceResult(
                qb_invoice_id=None,
                estado="ERROR_TIMEOUT: La petición a QuickBooks excedió el tiempo límite",
                pagada=False,
                stripe_invoice_id=stripe_invoice_id,
                duration_ms=duration_ms,
                retries=retries_count
            )
        elif "Connection" in error_type or "connect" in str(e).lower():
            _record_metric("quickbooks.invoice.create.failed", tags={"reason": "connection_error"})
            _cb_record_failure()
            return QuickBooksInvoiceResult(
                qb_invoice_id=None,
                estado="ERROR_CONNECTION: No se pudo conectar con QuickBooks API",
                pagada=False,
                stripe_invoice_id=stripe_invoice_id,
                duration_ms=duration_ms,
                retries=retries_count
            )
        else:
            _record_metric("quickbooks.invoice.create.failed", tags={"reason": "unexpected_error"})
            _cb_record_failure()
            return QuickBooksInvoiceResult(
                qb_invoice_id=None,
                estado=f"ERROR_INESPERADO: {str(e)}",
                pagada=False,
                stripe_invoice_id=stripe_invoice_id,
                duration_ms=duration_ms,
                retries=retries_count,
                error_details={"exception_type": error_type, "exception": str(e)}
            )


def _crear_pago_quickbooks(
    invoice_id: str,
    amount: float,
    customer_id: str,
    access_token: str,
    realm_id: str,
    quickbooks_base: str,
    stripe_reference: str
) -> Dict[str, Any]:
    """
    Crea un pago en QuickBooks para marcar una factura como pagada.
    Usa retries automáticos si tenacity está disponible.
    
    Args:
        invoice_id: ID de la factura en QuickBooks
        amount: Monto del pago
        customer_id: ID del cliente en QuickBooks
        access_token: Token de acceso de QuickBooks
        realm_id: ID de la compañía en QuickBooks
        quickbooks_base: URL base de QuickBooks API
        stripe_reference: Referencia de Stripe (para el PrivateNote)
    
    Returns:
        Dict con:
            - exitoso: bool indicando si fue exitoso
            - payment_id: ID del pago creado (si exitoso)
            - error: Mensaje de error (si falló)
    """
    try:
        url = f"{quickbooks_base}/v3/company/{realm_id}/payment"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        params = {"minorversion": "65"}
        
        payload = {
            "CustomerRef": {
                "value": str(customer_id)
            },
            "TotalAmt": str(amount),
            "PrivateNote": f"Pago automático para factura Stripe: {stripe_reference}",
            "Line": [
                {
                    "Amount": str(amount),
                    "LinkedTxn": [
                        {
                            "TxnId": str(invoice_id),
                            "TxnType": "Invoice"
                        }
                    ]
                }
            ]
        }
        
        def _create_payment():
            with _get_http_client("quickbooks") as client:
                if HTTPX_AVAILABLE:
                    response = client.post(url, headers=headers, json=payload, params=params)
                    _handle_rate_limit(response, "payment_create")
                    response.raise_for_status()
                    result = response
                else:
                    response = client.post(url, headers=headers, json=payload, params=params)
                    _handle_rate_limit(response, "payment_create")
                    result = response
                
                # Delay para respetar rate limits
                time.sleep(QUICKBOOKS_RATE_LIMIT_DELAY)
                return result
        
        if TENACITY_AVAILABLE:
            try:
                create_with_retry = retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=2, max=10),
                    retry=retry_if_exception_type((httpx.HTTPError if HTTPX_AVAILABLE else Exception)),
                    reraise=True
                )(_create_payment)
                response = create_with_retry()
            except RetryError as e:
                logger.error(f"Error después de reintentos al crear pago: {e}")
                return {
                    "exitoso": False,
                    "payment_id": None,
                    "error": f"ERROR_RETRY: Error después de múltiples intentos: {str(e)}"
                }
        else:
            response = _create_payment()
        
        # Obtener status code de forma compatible
        if HTTPX_AVAILABLE:
            status_code = response.status_code
        else:
            status_code = response.status_code if hasattr(response, 'status_code') else 200
        
        if status_code in [200, 201]:
            try:
                response_data = response.json()
                payment = response_data.get("Payment", {})
                payment_id = payment.get("Id") or payment.get("id")
                
                return {
                    "exitoso": True,
                    "payment_id": str(payment_id) if payment_id else None,
                    "error": None
                }
            except Exception as e:
                logger.warning(f"Error al parsear respuesta de pago: {e}")
                # Si la respuesta fue exitosa pero no se pudo parsear, considerarlo exitoso de todas formas
                return {
                    "exitoso": True,
                    "payment_id": None,
                    "error": None
                }
        else:
            try:
                if HTTPX_AVAILABLE:
                    response_text = response.text
                else:
                    response_text = getattr(response, 'text', '') or str(getattr(response, 'content', ''))
                
                error_data = response.json()
                faults = error_data.get("Fault", {})
                errors = faults.get("Error", [])
                if errors:
                    error_message = errors[0].get("Message", "Error desconocido")
                else:
                    error_message = response_text
            except Exception:
                response_text = str(response) if not HTTPX_AVAILABLE else (response.text if hasattr(response, 'text') else str(response))
                error_message = response_text or "Error desconocido"
            
            return {
                "exitoso": False,
                "payment_id": None,
                "error": f"{status_code}: {error_message}"
            }
            
    except Exception as e:
        logger.error(f"Error inesperado al crear pago: {e}")
        return {
            "exitoso": False,
            "payment_id": None,
            "error": f"ERROR: {str(e)}"
        }


# Función auxiliar para uso en DAGs de Airflow
def crear_factura_quickbooks_task(**context):
    """
    Wrapper para usar la función en DAGs de Airflow.
    Espera los siguientes parámetros en context['params']:
    - stripe_invoice_id: ID de la factura en Stripe
    - correo_cliente: Correo electrónico del cliente
    - monto_factura: Monto total de la factura
    - fecha_vencimiento: Fecha de vencimiento (YYYY-MM-DD)
    - cuenta_ingresos: (opcional) Nombre de la cuenta de ingresos en QuickBooks (default: "Services")
    """
    params = context.get('params', {})
    stripe_invoice_id = params.get('stripe_invoice_id')
    correo_cliente = params.get('correo_cliente')
    monto_factura = params.get('monto_factura')
    fecha_vencimiento = params.get('fecha_vencimiento')
    cuenta_ingresos = params.get('cuenta_ingresos', 'Services')
    
    if not stripe_invoice_id:
        raise ValueError("stripe_invoice_id es requerido en los parámetros")
    if not correo_cliente:
        raise ValueError("correo_cliente es requerido en los parámetros")
    if not monto_factura:
        raise ValueError("monto_factura es requerido en los parámetros")
    if not fecha_vencimiento:
        raise ValueError("fecha_vencimiento es requerido en los parámetros")
    
    # Convertir monto a float si es string
    try:
        monto_factura = float(monto_factura)
    except (ValueError, TypeError):
        raise ValueError(f"monto_factura debe ser un número válido: {monto_factura}")
    
    resultado = crear_factura_quickbooks(
        stripe_invoice_id=stripe_invoice_id,
        correo_cliente=correo_cliente,
        monto_factura=monto_factura,
        fecha_vencimiento=fecha_vencimiento,
        cuenta_ingresos=cuenta_ingresos
    )
    
    # Compatibilidad: convertir a dict si el código espera dict
    if resultado.success:
        print(f"✓ Factura creada exitosamente en QuickBooks")
        print(f"  - ID Stripe: {stripe_invoice_id}")
        print(f"  - ID QuickBooks: {resultado.qb_invoice_id}")
        print(f"  - Cliente: {correo_cliente}")
        print(f"  - Monto: {monto_factura}")
        print(f"  - Fecha vencimiento: {fecha_vencimiento}")
        if resultado.duration_ms:
            print(f"  - Duración: {resultado.duration_ms:.2f}ms")
        if resultado.pagada:
            print(f"  - Estado: Pagada automáticamente (pago inmediato detectado)")
            if resultado.qb_payment_id:
                print(f"  - ID Pago QuickBooks: {resultado.qb_payment_id}")
        else:
            print(f"  - Estado: Pendiente de pago")
    else:
        print(f"✗ Error al crear factura en QuickBooks: {resultado.estado}")
        if resultado.error_details:
            print(f"  - Detalles: {resultado.error_details}")
    
    # Retornar como dict para compatibilidad con código existente
    return resultado.to_dict()

