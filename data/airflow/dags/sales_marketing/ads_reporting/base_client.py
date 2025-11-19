"""
Cliente base para APIs de Ads con funcionalidades compartidas.

Proporciona:
- Manejo de errores estándar
- Retry logic
- Rate limiting
- Sesiones HTTP reutilizables
- Métricas y tracking
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

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

try:
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False


class AdsAPIError(Exception):
    """Excepción base para errores de APIs de Ads."""
    def __init__(self, message: str, status_code: Optional[int] = None, error_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_data = error_data


class AdsAuthError(AdsAPIError):
    """Error de autenticación."""
    pass


class AdsRateLimitError(AdsAPIError):
    """Error de rate limiting."""
    pass


@dataclass
class APIConfig:
    """Configuración base para APIs."""
    access_token: str
    api_version: str = "v1"
    max_retries: int = 3
    retry_backoff: float = 1.0
    rate_limit_delay: float = 0.5
    request_timeout: int = 30
    platform: str = "unknown"
    
    def validate(self) -> None:
        """Valida la configuración básica."""
        if not self.access_token or not self.access_token.strip():
            raise AdsAuthError(f"{self.platform.upper()}_ACCESS_TOKEN es requerido")


class BaseAdsClient(ABC):
    """
    Cliente base abstracto para APIs de Ads.
    
    Implementa funcionalidades comunes:
    - Sesiones HTTP reutilizables
    - Retry logic
    - Rate limiting
    - Métricas
    """
    
    def __init__(self, config: APIConfig):
        """
        Inicializa el cliente.
        
        Args:
            config: Configuración de la API
        """
        self.config = config
        self.config.validate()
        self._session: Optional[requests.Session] = None
    
    def _create_session(self) -> requests.Session:
        """Crea una sesión HTTP con retry strategy."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    @property
    def session(self) -> requests.Session:
        """Obtiene o crea la sesión HTTP."""
        if self._session is None:
            self._session = self._create_session()
        return self._session
    
    def _handle_rate_limit(self, response: requests.Response) -> None:
        """Maneja rate limiting."""
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', self.config.rate_limit_delay))
            logger.warning(
                f"[{self.config.platform}] Rate limit alcanzado, esperando {retry_after}s"
            )
            time.sleep(min(retry_after, 300))  # Máximo 5 minutos
            raise AdsRateLimitError(f"Rate limit: {response.text}")
    
    def _parse_error_response(self, response: requests.Response) -> AdsAPIError:
        """Parsea errores de la respuesta."""
        try:
            data = response.json()
        except Exception:
            data = {}
        
        error_msg = data.get('message') or data.get('error') or response.text
        error_code = data.get('code') or response.status_code
        
        return AdsAPIError(
            f"{self.config.platform} API Error: {error_msg}",
            status_code=error_code,
            error_data=data
        )
    
    def _execute_request_with_retry(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """
        Ejecuta una petición HTTP con retry logic.
        
        Args:
            method: Método HTTP (GET, POST)
            url: URL completa
            headers: Headers HTTP
            params: Parámetros de query
            json_data: Datos JSON para el body
            
        Returns:
            Response object
            
        Raises:
            AdsAPIError: Si hay error en la petición
            AdsRateLimitError: Si hay rate limiting
        """
        def _execute():
            if method.upper() == "GET":
                response = self.session.get(
                    url, headers=headers, params=params,
                    timeout=self.config.request_timeout
                )
            elif method.upper() == "POST":
                response = self.session.post(
                    url, headers=headers, json=json_data, params=params,
                    timeout=self.config.request_timeout
                )
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
            
            # Manejar rate limiting
            self._handle_rate_limit(response)
            
            # Manejar errores HTTP
            if response.status_code >= 400:
                raise self._parse_error_response(response)
            
            return response
        
        # Usar tenacity para retry si está disponible
        if TENACITY_AVAILABLE:
            @retry(
                stop=stop_after_attempt(self.config.max_retries + 1),
                wait=wait_exponential(
                    multiplier=self.config.retry_backoff,
                    min=1, max=10
                ),
                retry=retry_if_exception_type((
                    requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError,
                    AdsRateLimitError
                )),
                before_sleep=before_sleep_log(logger, logging.WARNING),
                after=after_log(logger, logging.INFO),
                reraise=True
            )
            def _retry_execute():
                return _execute()
            
            try:
                return _retry_execute()
            except Exception as e:
                if isinstance(e, (AdsAPIError, AdsAuthError)):
                    raise
                raise AdsAPIError(f"Error en petición: {str(e)}")
        else:
            try:
                return _execute()
            except requests.exceptions.RequestException as e:
                raise AdsAPIError(f"Request Error: {str(e)}")
    
    @contextmanager
    def _track_operation(self, operation_name: str, tags: Optional[Dict[str, str]] = None):
        """Context manager para trackear operaciones."""
        start_time = time.time()
        full_tags = {**(tags or {}), "platform": self.config.platform}
        
        if STATS_AVAILABLE:
            try:
                stats = Stats()
                stats.incr(
                    f"ads_reporting.{self.config.platform}.{operation_name}.start",
                    tags=full_tags
                )
            except Exception:
                pass
        
        try:
            yield
            if STATS_AVAILABLE:
                try:
                    stats = Stats()
                    duration_ms = (time.time() - start_time) * 1000
                    stats.incr(
                        f"ads_reporting.{self.config.platform}.{operation_name}.success",
                        tags=full_tags
                    )
                    stats.timing(
                        f"ads_reporting.{self.config.platform}.{operation_name}.duration_ms",
                        int(duration_ms),
                        tags=full_tags
                    )
                except Exception:
                    pass
        except Exception as e:
            if STATS_AVAILABLE:
                try:
                    stats = Stats()
                    stats.incr(
                        f"ads_reporting.{self.config.platform}.{operation_name}.error",
                        tags={**full_tags, "error_type": type(e).__name__}
                    )
                except Exception:
                    pass
            raise
    
    @abstractmethod
    def get_base_url(self) -> str:
        """Retorna la URL base de la API."""
        pass
    
    @abstractmethod
    def get_default_headers(self) -> Dict[str, str]:
        """Retorna los headers por defecto."""
        pass
    
    def close(self):
        """Cierra la sesión HTTP."""
        if self._session:
            self._session.close()
            self._session = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


