"""
Cliente mejorado para interacciones con ManyChat API.

Características:
- Retry automático con exponential backoff
- Validación de respuestas
- Logging estructurado
- Soporte para diferentes formatos de mensaje
"""
import logging
import time
from typing import Optional, Dict, Any
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
    )
    from requests.exceptions import RequestException, HTTPError
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False

try:
    from .circuit_breaker import get_circuit_breaker, CircuitBreakerConfig
    from .metrics import get_metrics_collector
    CIRCUIT_BREAKER_AVAILABLE = True
    METRICS_AVAILABLE = True
except ImportError:
    CIRCUIT_BREAKER_AVAILABLE = False
    METRICS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Constantes
DEFAULT_MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
MANYCHAT_BASE_URL = "https://api.manychat.com"


@dataclass
class ManyChatMessage:
    """Modelo de mensaje para ManyChat."""
    subscriber_id: str
    text: str
    page_id: Optional[str] = None
    
    def to_api_payload(self) -> Dict[str, Any]:
        """Convierte el mensaje al formato de la API de ManyChat."""
        payload = {
            "subscriber_id": self.subscriber_id,
            "data": {
                "messages": [
                    {
                        "type": "text",
                        "text": self.text
                    }
                ]
            }
        }
        if self.page_id:
            payload["page_id"] = self.page_id
        return payload


@dataclass
class ManyChatResult:
    """Resultado de operación con ManyChat."""
    success: bool
    status_code: int
    message: str
    subscriber_id: str
    sent_message: str
    api_response: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None
    retries: int = 0


class ManyChatClient:
    """Cliente para interactuar con ManyChat API."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        max_retries: Optional[int] = None,
        timeout: Optional[int] = None,
        page_id: Optional[str] = None,
        config: Optional["ManyChatConfig"] = None
    ):
        """
        Inicializa el cliente de ManyChat.
        
        Args:
            api_key: API Key de ManyChat (opcional si se usa config)
            base_url: URL base de la API (opcional si se usa config)
            max_retries: Máximo de reintentos (opcional si se usa config)
            timeout: Timeout en segundos (opcional si se usa config)
            page_id: ID de la página (opcional)
            config: Configuración completa (opcional, puede cargar desde env)
        """
        from .config import ManyChatConfig, validate_config
        
        # Cargar configuración
        if config is None:
            try:
                config = ManyChatConfig.from_env()
            except Exception as e:
                logger.debug(f"Failed to load config from env: {e}, using defaults")
                config = ManyChatConfig()
        
        # Override con parámetros explícitos
        if api_key:
            config.api_key = api_key
        if base_url:
            config.base_url = base_url
        if page_id:
            config.page_id = page_id
        if max_retries is not None:
            config.max_retries = max_retries
        if timeout is not None:
            config.timeout = timeout
        
        # Validar configuración
        validate_config(config)
        
        self.config = config
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library is required. Install: pip install requests")
        
        self.api_key = config.api_key
        self.page_id = config.page_id
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
            self.circuit_breaker = get_circuit_breaker("manychat_api", cb_config)
        else:
            self.circuit_breaker = None
        
        # Metrics collector
        if METRICS_AVAILABLE and config.metrics_enabled:
            self.metrics = get_metrics_collector()
        else:
            self.metrics = None
        
        logger.info("ManyChatClient initialized", extra={
            "base_url": self.base_url,
            "max_retries": self.max_retries,
            "circuit_breaker": CIRCUIT_BREAKER_AVAILABLE,
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
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
            self.use_httpx = True
            logger.debug("Using httpx client with connection pooling")
        elif REQUESTS_ADAPTER_AVAILABLE:
            # Usar requests con HTTPAdapter y retry strategy
            session = requests.Session()
            session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
            
            # Retry strategy mejorada
            retry_strategy = Retry(
                total=self.max_retries,
                backoff_factor=self.config.retry_backoff_factor,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET", "POST"],
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
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
            self.use_httpx = False
            logger.warning("Using basic requests.Session without advanced features")
    
    def health_check(self, timeout_seconds: float = 3.0) -> Dict[str, Any]:
        """
        Health check para verificar conectividad con ManyChat API.
        
        Args:
            timeout_seconds: Timeout del health check
        
        Returns:
            Diccionario con el resultado del health check
        """
        from .health import HealthStatus, HealthCheckResult, create_api_health_check
        import time
        
        def _check():
            # Intentar hacer una request simple para verificar API
            try:
                if self.use_httpx:
                    test_response = self.http_client.get(
                        f"{self.base_url}/fb/info",
                        timeout=timeout_seconds
                    )
                else:
                    test_response = self.session.get(
                        f"{self.base_url}/fb/info",
                        timeout=timeout_seconds
                    )
                # Compatibilidad con httpx y requests
                status = getattr(test_response, 'status_code', None)
                if status is None and hasattr(test_response, 'status'):
                    status = test_response.status
                return status in [200, 401]  # 401 también indica API activa
            except Exception:
                return False
        
        result = create_api_health_check("ManyChat", _check, timeout_seconds)
        
        return result.to_dict()
    
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
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ):
        """
        Realiza una petición HTTP con retry.
        
        Args:
            method: Método HTTP (POST, GET, etc.)
            endpoint: Endpoint relativo
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
                    wait=wait_exponential(multiplier=1, min=2, max=30),
                    retry=retry_if_exception_type((Exception,)),
                    reraise=True
                )
                def _retryable_request():
                    return self.http_client.request(method, url, **kwargs)
                
                return _retryable_request()
            else:
                # Fallback sin tenacity
                for attempt in range(self.max_retries + 1):
                    try:
                        return self.http_client.request(method, url, **kwargs)
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
                    wait=wait_exponential(multiplier=1, min=2, max=30),
                    retry=retry_if_exception_type((RequestException, HTTPError)),
                    reraise=True
                )
                def _retryable_request():
                    return self.session.request(method, url, **kwargs)
                
                return _retryable_request()
            else:
                # Fallback sin tenacity
                for attempt in range(self.max_retries + 1):
                    try:
                        return self.session.request(method, url, **kwargs)
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
    
    def send_message(
        self,
        subscriber_id: str,
        message_text: str,
        page_id: Optional[str] = None
    ) -> ManyChatResult:
        """
        Envía un mensaje a un suscriptor en ManyChat.
        
        Args:
            subscriber_id: ID del suscriptor en ManyChat
            message_text: Texto del mensaje a enviar
            page_id: ID de la página (opcional)
        
        Returns:
            ManyChatResult con el resultado del envío
        """
        # Start metrics timer
        if self.metrics:
            self.metrics.start_timer(f"manychat_send_message_{subscriber_id}")
        
        def _make_request():
            message = ManyChatMessage(
                subscriber_id=subscriber_id,
                text=message_text,
                page_id=page_id or self.page_id
            )
            
            endpoint = "/fb/sending/sendContent"
            payload = message.to_api_payload()
            
            logger.info("Sending message to ManyChat", extra={
                "subscriber_id": subscriber_id,
                "message_length": len(message_text),
                "has_page_id": bool(page_id)
            })
            
            return self._make_request("POST", endpoint, json=payload)
        
        try:
            # Usar circuit breaker si está disponible
            if self.circuit_breaker:
                response = self.circuit_breaker.call(_make_request)
            else:
                response = _make_request()
            response.raise_for_status()
            
            api_response = response.json()
            
            # ManyChat puede retornar diferentes formatos
            is_success = (
                api_response.get("status") == "success" or
                api_response.get("status") == "sent" or
                response.status_code == 200
            )
            
            if is_success:
                logger.info("Message sent successfully", extra={
                    "subscriber_id": subscriber_id
                })
            else:
                logger.warning("Message may not have been sent", extra={
                    "subscriber_id": subscriber_id,
                    "api_response": api_response
                })
            
            result = ManyChatResult(
                success=is_success,
                status_code=response.status_code,
                message="Message sent successfully" if is_success else "Message status unclear",
                subscriber_id=subscriber_id,
                sent_message=message_text,
                api_response=api_response
            )
            
            # Record metrics
            if self.metrics:
                duration = self.metrics.record_duration(f"manychat_send_message_{subscriber_id}")
                self.metrics.add_counter(
                    "manychat_api_requests_total",
                    labels={"operation": "send_message", "status": "success" if is_success else "error"}
                )
                self.metrics.add_histogram(
                    "manychat_api_request_duration_seconds",
                    duration,
                    labels={"operation": "send_message"}
                )
            
            return result
            
        except requests.exceptions.HTTPError as e:
            error_data = {}
            try:
                error_data = e.response.json()
            except:
                error_data = {"message": str(e)}
            
            logger.error("Failed to send message to ManyChat", extra={
                "subscriber_id": subscriber_id,
                "status_code": e.response.status_code,
                "error": error_data
            })
            
            # Record metrics
            if self.metrics:
                if self.metrics.start_times.get(f"manychat_send_message_{subscriber_id}"):
                    self.metrics.record_duration(f"manychat_send_message_{subscriber_id}")
                self.metrics.add_counter(
                    "manychat_api_requests_total",
                    labels={"operation": "send_message", "status": "error"}
                )
            
            return ManyChatResult(
                success=False,
                status_code=e.response.status_code,
                message=f"Failed to send message: {error_data.get('message', str(e))}",
                subscriber_id=subscriber_id,
                sent_message=message_text,
                error_details=error_data
            )
        except Exception as e:
            logger.error("Unexpected error sending message", extra={
                "subscriber_id": subscriber_id,
                "error": str(e)
            })
            return ManyChatResult(
                success=False,
                status_code=0,
                message=f"Unexpected error: {str(e)}",
                subscriber_id=subscriber_id,
                sent_message=message_text,
                error_details={"error": str(e)}
            )

