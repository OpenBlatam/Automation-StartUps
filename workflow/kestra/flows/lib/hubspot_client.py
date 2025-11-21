"""
Cliente mejorado para interacciones con HubSpot API.

Características:
- Retry automático con exponential backoff (tenacity)
- Manejo de rate limiting (429)
- Logging estructurado
- Validación de respuestas
- Timeout configurable
"""
import os
import logging
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
    REQUESTS_ADAPTER_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    REQUESTS_ADAPTER_AVAILABLE = False

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type,
        RetryError,
    )
    from requests.exceptions import RequestException, HTTPError
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False

try:
    from .circuit_breaker import get_circuit_breaker, CircuitBreakerConfig
    from .cache import get_cache
    from .metrics import get_metrics_collector
    CIRCUIT_BREAKER_AVAILABLE = True
    CACHE_AVAILABLE = True
    METRICS_AVAILABLE = True
except ImportError:
    CIRCUIT_BREAKER_AVAILABLE = False
    CACHE_AVAILABLE = False
    METRICS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Constantes
DEFAULT_MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
DEFAULT_RATE_LIMIT_WAIT = 60
HUBSPOT_BASE_URL = "https://api.hubapi.com"


@dataclass
class HubSpotContact:
    """Modelo de contacto de HubSpot."""
    id: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[str] = None
    interes_producto: Optional[str] = None
    manychat_user_id: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    
    @property
    def nombre(self) -> str:
        """Obtiene el nombre completo del contacto."""
        nombre_parts = [p for p in [self.firstname, self.lastname] if p]
        return " ".join(nombre_parts) if nombre_parts else "Cliente"
    
    @classmethod
    def from_api_response(cls, response_data: Dict[str, Any]) -> "HubSpotContact":
        """Crea un HubSpotContact desde la respuesta de la API."""
        properties = response_data.get("properties", {})
        return cls(
            id=str(response_data.get("id", "")),
            firstname=properties.get("firstname", "").strip() or None,
            lastname=properties.get("lastname", "").strip() or None,
            email=properties.get("email", "").strip() or None,
            interes_producto=(
                properties.get("interés_producto") or 
                properties.get("interes_producto") or 
                ""
            ).strip() or None,
            manychat_user_id=(
                properties.get("manychat_user_id") or
                properties.get("ManyChat User ID") or
                ""
            ).strip() or None,
            properties=properties
        )


@dataclass
class HubSpotResult:
    """Resultado de operación con HubSpot."""
    success: bool
    status_code: int
    message: str
    data: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None
    retries: int = 0


class HubSpotClient:
    """Cliente para interactuar con HubSpot API."""
    
    def __init__(
        self,
        api_token: Optional[str] = None,
        base_url: Optional[str] = None,
        max_retries: Optional[int] = None,
        timeout: Optional[int] = None,
        config: Optional["HubSpotConfig"] = None
    ):
        """
        Inicializa el cliente de HubSpot.
        
        Args:
            api_token: Token de API de HubSpot (opcional si se usa config)
            base_url: URL base de la API (opcional si se usa config)
            max_retries: Máximo de reintentos (opcional si se usa config)
            timeout: Timeout en segundos (opcional si se usa config)
            config: Configuración completa (opcional, puede cargar desde env)
        """
        from .config import HubSpotConfig, validate_config
        
        # Cargar configuración
        if config is None:
            try:
                config = HubSpotConfig.from_env()
            except Exception as e:
                logger.debug(f"Failed to load config from env: {e}, using defaults")
                config = HubSpotConfig()
        
        # Override con parámetros explícitos
        if api_token:
            config.api_token = api_token
        if base_url:
            config.base_url = base_url
        if max_retries is not None:
            config.max_retries = max_retries
        if timeout is not None:
            config.timeout = timeout
        
        # Validar configuración
        validate_config(config)
        
        self.config = config
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library is required. Install: pip install requests")
        
        self.api_token = config.api_token
        self.base_url = config.base_url.rstrip("/")
        self.max_retries = config.max_retries
        self.timeout = config.timeout
        
        # Configurar sesión HTTP con connection pooling
        self._setup_session()
        
        # Circuit breaker para protección
        if CIRCUIT_BREAKER_AVAILABLE and config.circuit_breaker_enabled:
            from .circuit_breaker import CircuitBreakerConfig
            cb_config = CircuitBreakerConfig(
                failure_threshold=config.circuit_breaker_failure_threshold,
                timeout_seconds=config.circuit_breaker_timeout_seconds,
                expected_exception=RequestException
            )
            self.circuit_breaker = get_circuit_breaker("hubspot_api", cb_config)
        else:
            self.circuit_breaker = None
        
        # Cache para reducir llamadas repetidas
        if CACHE_AVAILABLE and config.cache_enabled:
            self.cache = get_cache("hubspot", default_ttl=config.cache_ttl)
        else:
            self.cache = None
        
        # Metrics collector
        if METRICS_AVAILABLE and config.metrics_enabled:
            self.metrics = get_metrics_collector()
        else:
            self.metrics = None
        
        logger.info("HubSpotClient initialized", extra={
            "base_url": self.base_url,
            "max_retries": self.max_retries,
            "circuit_breaker": CIRCUIT_BREAKER_AVAILABLE,
            "cache": CACHE_AVAILABLE,
            "metrics": METRICS_AVAILABLE,
            "http_client": "httpx" if HTTPX_AVAILABLE else "requests"
        })
    
    def _setup_session(self):
        """
        Configura la sesión HTTP con connection pooling y retry strategy.
        Prioriza httpx si está disponible, luego requests con HTTPAdapter.
        """
        if HTTPX_AVAILABLE:
            # Usar httpx con connection pooling
            limits = httpx.Limits(
                max_keepalive_connections=10,
                max_connections=20
            )
            timeout = httpx.Timeout(self.timeout, connect=10.0)
            self.http_client = httpx.Client(
                limits=limits,
                timeout=timeout,
                follow_redirects=True
            )
            self.http_client.headers.update({
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            })
            self.use_httpx = True
            logger.debug("Using httpx client with connection pooling")
        elif REQUESTS_ADAPTER_AVAILABLE:
            # Usar requests con HTTPAdapter y retry strategy
            session = requests.Session()
            session.headers.update({
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            })
            
            # Retry strategy mejorada
            retry_strategy = Retry(
                total=self.max_retries,
                backoff_factor=self.config.retry_backoff_factor,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET", "POST", "PATCH", "PUT"],
                raise_on_status=False
            )
            adapter = HTTPAdapter(
                max_retries=retry_strategy,
                pool_maxsize=10,
                pool_connections=10
            )
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            self.session = session
            self.use_httpx = False
            logger.debug("Using requests.Session with HTTPAdapter and connection pooling")
        else:
            # Fallback básico
            self.session = requests.Session()
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            })
            self.use_httpx = False
            logger.warning("Using basic requests.Session without advanced features")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if hasattr(self, 'http_client') and self.http_client:
            self.http_client.close()
        elif hasattr(self, 'session') and self.session:
            self.session.close()
        return False
    
    def _handle_rate_limit(self, response) -> bool:
        """
        Maneja rate limiting (429) para requests.
        
        Returns:
            True si debe reintentar, False si no
        """
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", DEFAULT_RATE_LIMIT_WAIT))
            logger.warning(
                "Rate limited by HubSpot",
                extra={
                    "retry_after": retry_after,
                    "status_code": 429
                }
            )
            time.sleep(min(retry_after, self.config.rate_limit_max_wait))
            return True
        return False
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ):
        """
        Realiza una petición HTTP con manejo de rate limiting.
        
        Args:
            method: Método HTTP (GET, POST, PATCH, etc.)
            endpoint: Endpoint relativo (ej: "/crm/v3/objects/contacts")
            **kwargs: Argumentos adicionales para requests/httpx
        
        Returns:
            Response de requests o httpx
        """
        url = f"{self.base_url}{endpoint}"
        
        if self.use_httpx:
            # Usar httpx
            kwargs.setdefault("timeout", self.timeout)
            
            if TENACITY_AVAILABLE:
                @retry(
                    stop=stop_after_attempt(self.max_retries + 1),
                    wait=wait_exponential(multiplier=1, min=2, max=60),
                    retry=retry_if_exception_type((Exception,)),
                    reraise=True
                )
                def _retryable_request():
                    response = self.http_client.request(method, url, **kwargs)
                    if self._handle_rate_limit_httpx(response):
                        # Si es rate limit, lanzar excepción para que retry
                        response.raise_for_status()
                    return response
                
                return _retryable_request()
            else:
                # Fallback sin tenacity
                for attempt in range(self.max_retries + 1):
                    try:
                        response = self.http_client.request(method, url, **kwargs)
                        if self._handle_rate_limit_httpx(response):
                            continue
                        return response
                    except Exception as e:
                        if attempt == self.max_retries:
                            raise
                        wait_time = 2 ** attempt
                        logger.warning(f"Request failed, retrying in {wait_time}s", extra={
                            "attempt": attempt + 1,
                            "error": str(e)
                        })
                        time.sleep(wait_time)
                raise Exception("Max retries exceeded")
        else:
            # Usar requests
            kwargs.setdefault("timeout", self.timeout)
            
            if TENACITY_AVAILABLE:
                @retry(
                    stop=stop_after_attempt(self.max_retries + 1),
                    wait=wait_exponential(multiplier=1, min=2, max=60),
                    retry=retry_if_exception_type((RequestException, HTTPError)),
                    reraise=True
                )
                def _retryable_request():
                    response = self.session.request(method, url, **kwargs)
                    if self._handle_rate_limit(response):
                        # Si es rate limit, lanzar excepción para que retry
                        response.raise_for_status()
                    return response
                
                return _retryable_request()
            else:
                # Fallback sin tenacity
                for attempt in range(self.max_retries + 1):
                    try:
                        response = self.session.request(method, url, **kwargs)
                        if self._handle_rate_limit(response):
                            continue
                        return response
                    except (RequestException, HTTPError) as e:
                        if attempt == self.max_retries:
                            raise
                        wait_time = 2 ** attempt
                        logger.warning(f"Request failed, retrying in {wait_time}s", extra={
                            "attempt": attempt + 1,
                            "error": str(e)
                        })
                        time.sleep(wait_time)
                raise Exception("Max retries exceeded")
    
    def _handle_rate_limit_httpx(self, response) -> bool:
        """
        Maneja rate limiting (429) para httpx.
        
        Returns:
            True si debe reintentar, False si no
        """
        if response.status_code == 429:
            retry_after = int(response.headers.get("retry-after", DEFAULT_RATE_LIMIT_WAIT))
            logger.warning(
                "Rate limited by HubSpot (httpx)",
                extra={
                    "retry_after": retry_after,
                    "status_code": 429
                }
            )
            time.sleep(min(retry_after, self.config.rate_limit_max_wait))
            return True
        return False
    
    def health_check(self, timeout_seconds: float = 3.0) -> Dict[str, Any]:
        """
        Health check para verificar conectividad con HubSpot API.
        
        Args:
            timeout_seconds: Timeout del health check
        
        Returns:
            Diccionario con el resultado del health check
        """
        from .health import HealthStatus, HealthCheckResult, create_api_health_check
        import time
        from datetime import datetime
        
        start_time = time.time()
        
        def _check():
            # Intentar hacer una request simple (get current user o similar)
            try:
                # Usar un endpoint lightweight para health check
                test_endpoint = "/integrations/v1/me"
                response = self._make_request("GET", test_endpoint)
                # Compatibilidad con httpx y requests
                status = getattr(response, 'status_code', None)
                if status is None and hasattr(response, 'status'):
                    status = response.status
                return status == 200
            except Exception:
                return False
        
        result = create_api_health_check("HubSpot", _check, timeout_seconds)
        
        return result.to_dict()
    
    def get_contact(
        self,
        contact_id: str,
        properties: Optional[List[str]] = None,
        use_cache: bool = True
    ) -> HubSpotResult:
        """
        Obtiene un contacto por ID.
        
        Args:
            contact_id: ID del contacto
            properties: Lista de propiedades a obtener (opcional)
            use_cache: Si usar caché (default: True)
        
        Returns:
            HubSpotResult con los datos del contacto
        """
        # Intentar obtener del caché
        if use_cache and self.cache:
            cache_key = f"contact:{contact_id}:{','.join(properties or [])}"
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.debug(f"Cache hit for contact {contact_id}")
                return cached_result
        
        # Start metrics timer
        if self.metrics:
            self.metrics.start_timer(f"hubspot_get_contact_{contact_id}")
        
        def _make_request():
            endpoint = f"/crm/v3/objects/contacts/{contact_id}"
            params = {}
            if properties:
                params["properties"] = ",".join(properties)
            
            return self._make_request("GET", endpoint, params=params)
        
        try:
            # Usar circuit breaker si está disponible
            if self.circuit_breaker:
                response = self.circuit_breaker.call(_make_request)
            else:
                response = _make_request()
            
            response.raise_for_status()
            
            data = response.json()
            result = HubSpotResult(
                success=True,
                status_code=response.status_code,
                message="Contact retrieved successfully",
                data=data
            )
            
            # Guardar en caché si está disponible
            if use_cache and self.cache:
                cache_key = f"contact:{contact_id}:{','.join(properties or [])}"
                self.cache.set(cache_key, result, ttl=300)
            
            # Record metrics
            if self.metrics:
                duration = self.metrics.record_duration(f"hubspot_get_contact_{contact_id}")
                self.metrics.add_counter(
                    "hubspot_api_requests_total",
                    labels={"operation": "get_contact", "status": "success"}
                )
                self.metrics.add_histogram(
                    "hubspot_api_request_duration_seconds",
                    duration,
                    labels={"operation": "get_contact"}
                )
            
            return result
        except requests.exceptions.HTTPError as e:
            error_data = {}
            try:
                error_data = e.response.json()
            except:
                error_data = {"message": str(e)}
            
            logger.error("Failed to get contact", extra={
                "contact_id": contact_id,
                "status_code": e.response.status_code,
                "error": error_data
            })
            
            # Record metrics
            if self.metrics:
                if self.metrics.start_times.get(f"hubspot_get_contact_{contact_id}"):
                    self.metrics.record_duration(f"hubspot_get_contact_{contact_id}")
                self.metrics.add_counter(
                    "hubspot_api_requests_total",
                    labels={"operation": "get_contact", "status": "error"}
                )
            
            return HubSpotResult(
                success=False,
                status_code=e.response.status_code,
                message=f"Failed to retrieve contact: {error_data.get('message', str(e))}",
                error_details=error_data
            )
        except Exception as e:
            logger.error("Unexpected error getting contact", extra={
                "contact_id": contact_id,
                "error": str(e)
            })
            return HubSpotResult(
                success=False,
                status_code=0,
                message=f"Unexpected error: {str(e)}",
                error_details={"error": str(e)}
            )
    
    def parse_webhook_payload(self, payload: Dict[str, Any]) -> Optional[HubSpotContact]:
        """
        Parsea un payload de webhook de HubSpot.
        
        Args:
            payload: Payload del webhook
        
        Returns:
            HubSpotContact si se puede parsear, None si no es válido
        """
        try:
            # Intentar diferentes estructuras de webhook
            contact_data = None
            properties = {}
            
            if "subscriptionType" in payload and "properties" in payload:
                contact_data = payload
                properties = payload.get("properties", {})
            elif "objectId" in payload:
                contact_data = payload
                properties = payload.get("properties", {})
            elif "contacts" in payload and len(payload["contacts"]) > 0:
                contact_data = payload["contacts"][0]
                properties = contact_data.get("properties", {})
            else:
                logger.warning("Unknown webhook payload structure", extra={
                    "payload_keys": list(payload.keys())
                })
                return None
            
            contacto_id = str(
                contact_data.get("objectId") or
                contact_data.get("vid") or
                contact_data.get("id") or
                ""
            )
            
            if not contacto_id:
                logger.warning("No contact ID found in payload")
                return None
            
            # Crear contacto desde propiedades
            contact = HubSpotContact(
                id=contacto_id,
                firstname=properties.get("firstname", "").strip() or None,
                lastname=properties.get("lastname", "").strip() or None,
                email=properties.get("email", "").strip() or None,
                interes_producto=(
                    properties.get("interés_producto") or
                    properties.get("interes_producto") or
                    ""
                ).strip() or None,
                manychat_user_id=(
                    properties.get("manychat_user_id") or
                    properties.get("ManyChat User ID") or
                    ""
                ).strip() or None,
                properties=properties
            )
            
            return contact
            
        except Exception as e:
            logger.error("Failed to parse webhook payload", extra={
                "error": str(e),
                "payload_keys": list(payload.keys()) if isinstance(payload, dict) else None
            })
            return None

