"""
DAG para crear gastos en QuickBooks para las tarifas de Stripe.

Para cada pago exitoso en Stripe con tarifa, crea un gasto en QuickBooks
en la cuenta 'Tarifas Stripe' con la referencia del pago para conciliación.

Mejoras implementadas:
- ✅ Retry con exponential backoff (tenacity si disponible)
- ✅ Circuit breaker con auto-reset
- ✅ Health check pre-vuelo de APIs
- ✅ Manejo inteligente de rate limiting (429) para Stripe y QuickBooks
- ✅ Logging estructurado con contexto completo
- ✅ Validación robusta de inputs (guard clauses)
- ✅ Timeouts configurables
- ✅ Métricas de performance detalladas (StatsD/Prometheus)
- ✅ Manejo específico de errores HTTP con excepciones personalizadas
- ✅ Prevención de duplicados mejorada con índices en DB
- ✅ Transacciones atómicas con rollback en errores
- ✅ Context managers para tracking de API calls
- ✅ Procesamiento en batches con delays configurables
- ✅ Dry-run mode para testing
"""
from __future__ import annotations

from datetime import timedelta
import logging
import os
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from typing import TypedDict
from contextlib import contextmanager
import json

import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable, Param
from airflow.operators.python import get_current_context
from airflow.exceptions import AirflowFailException
from data.airflow.plugins.db import get_conn

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

# Intentar importar cachetools para cache con TTL
try:
	from cachetools import TTLCache
	CACHETOOLS_AVAILABLE = True
except ImportError:
	CACHETOOLS_AVAILABLE = False

# Intentar importar Pydantic para validación
try:
	from pydantic import BaseModel, Field, ValidationError
	PYDANTIC_AVAILABLE = True
except ImportError:
	PYDANTIC_AVAILABLE = False

# Intentar importar requests.adapters para connection pooling
try:
	import requests
	from requests.adapters import HTTPAdapter
	from urllib3.util.retry import Retry
	REQUESTS_ADAPTER_AVAILABLE = True
except ImportError:
	REQUESTS_ADAPTER_AVAILABLE = False

logger = logging.getLogger(__name__)

# Excepciones personalizadas para mejor manejo de errores
class StripeAPIError(Exception):
	"""Excepción para errores de API de Stripe."""
	def __init__(self, message: str, status_code: Optional[int] = None):
		super().__init__(message)
		self.status_code = status_code


class QuickBooksAPIError(Exception):
	"""Excepción para errores de API de QuickBooks."""
	def __init__(self, message: str, status_code: Optional[int] = None, error_data: Optional[Dict] = None):
		super().__init__(message)
		self.status_code = status_code
		self.error_data = error_data


class ValidationError(Exception):
	"""Excepción para errores de validación."""
	pass


# Modelos Pydantic para validación (si está disponible)
if PYDANTIC_AVAILABLE:
	from decimal import Decimal
	
	class FeeData(BaseModel):
		"""Modelo de validación para datos de tarifa."""
		payment_id: str = Field(..., min_length=1, max_length=255, description="ID del pago en Stripe")
		fee_amount: Decimal = Field(..., ge=0, decimal_places=2, description="Monto de la tarifa")
		currency: str = Field(..., min_length=3, max_length=3, description="Código de moneda (ISO 4217)")
		description: str = Field(..., min_length=1, max_length=500, description="Descripción de la tarifa")
		payment_date: int = Field(..., ge=0, description="Timestamp Unix del pago")
		balance_transaction_id: Optional[str] = Field(None, max_length=255)
		payment_amount: Optional[Decimal] = Field(None, ge=0)
		
		class Config:
			"""Configuración del modelo."""
			json_encoders = {Decimal: lambda v: float(v)}
			extra = "allow"  # Permitir campos adicionales

# Constantes de configuración
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0  # segundos
DEFAULT_TIMEOUT = 30  # segundos
RATE_LIMIT_MAX_WAIT = 300  # 5 minutos máximo de espera por rate limit
STRIPE_RATE_LIMIT_HEADER = "retry-after"
QB_RATE_LIMIT_HEADER = "retry-after"
DEFAULT_BATCH_SIZE = 10  # Procesar gastos en batches
DEFAULT_BATCH_DELAY = 0.5  # Delay entre batches en segundos
CB_FAILURE_THRESHOLD = 5  # Circuit breaker: fallos antes de abrir
CB_RESET_MINUTES = 15  # Circuit breaker: minutos antes de auto-reset

# Cache configuration
DEFAULT_CACHE_SIZE = 100  # Tamaño máximo del cache
DEFAULT_CACHE_TTL = 300  # TTL del cache en segundos (5 minutos)

# Connection pooling
DEFAULT_POOL_MAXSIZE = 10  # Tamaño máximo del pool de conexiones

# Sesiones HTTP globales reutilizables
_stripe_session: Optional[Any] = None
_quickbooks_session: Optional[Any] = None

# Cache para cuentas de QuickBooks (TTL de 5 minutos)
_account_cache: Optional[Any] = None
if CACHETOOLS_AVAILABLE:
	_account_cache = TTLCache(maxsize=DEFAULT_CACHE_SIZE, ttl=DEFAULT_CACHE_TTL)


@dataclass
class ExpenseCreationResult:
	"""Resultado de la creación de un gasto en QuickBooks."""
	success: bool
	payment_id: str
	quickbooks_id: Optional[str] = None
	fee_amount: float = 0.0
	error_message: Optional[str] = None
	duration_ms: float = 0.0
	retries: int = 0
	
	def to_dict(self) -> Dict[str, Any]:
		"""Convierte el resultado a diccionario."""
		return {
			"success": self.success,
			"payment_id": self.payment_id,
			"quickbooks_id": self.quickbooks_id,
			"fee_amount": self.fee_amount,
			"error_message": self.error_message,
			"duration_ms": self.duration_ms,
			"retries": self.retries,
		}


@dataclass
class ProcessingSummary:
	"""Resumen del procesamiento de tarifas."""
	total_fees: int = 0
	fees_to_create: int = 0
	fees_skipped: int = 0
	expenses_created: int = 0
	expenses_failed: int = 0
	total_fee_amount: float = 0.0
	duration_ms: float = 0.0
	errors: List[Dict[str, Any]] = field(default_factory=list)
	
	@property
	def success_rate(self) -> float:
		"""Calcula la tasa de éxito."""
		total = self.expenses_created + self.expenses_failed
		if total == 0:
			return 0.0
		return (self.expenses_created / total) * 100.0
	
	def to_dict(self) -> Dict[str, Any]:
		"""Convierte el resumen a diccionario."""
		return {
			"total_fees": self.total_fees,
			"fees_to_create": self.fees_to_create,
			"fees_skipped": self.fees_skipped,
			"expenses_created": self.expenses_created,
			"expenses_failed": self.expenses_failed,
			"total_fee_amount": self.total_fee_amount,
			"duration_ms": self.duration_ms,
			"success_rate": self.success_rate,
			"errors": self.errors,
		}


def _get_env_var(name: str, default: str | None = None) -> str:
	"""Get environment variable from Airflow Variables with fallback."""
	try:
		return str(Variable.get(name, default_var=default))
	except Exception:
		return default or ""


def _get_stripe_session():
	"""Obtiene o crea una sesión HTTP reutilizable para Stripe con retry strategy."""
	global _stripe_session
	import requests
	
	if _stripe_session is not None:
		return _stripe_session
	
	if HTTPX_AVAILABLE:
		# Sesión httpx con límites y timeout
		limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
		timeout = httpx.Timeout(30.0, connect=10.0)
		_stripe_session = httpx.Client(
			limits=limits,
			timeout=timeout,
			follow_redirects=True,
		)
	elif REQUESTS_ADAPTER_AVAILABLE:
		session = requests.Session()
		
		# Retry strategy mejorada
		retry_strategy = Retry(
			total=DEFAULT_MAX_RETRIES,
			backoff_factor=DEFAULT_RETRY_DELAY,
			status_forcelist=[429, 500, 502, 503, 504],
			allowed_methods=["GET", "POST"],
			raise_on_status=False,
		)
		adapter = HTTPAdapter(max_retries=retry_strategy, pool_maxsize=DEFAULT_POOL_MAXSIZE)
		session.mount("http://", adapter)
		session.mount("https://", adapter)
		_stripe_session = session
	else:
		# Fallback sin sesión reutilizable
		_stripe_session = None
	
	return _stripe_session


def _get_quickbooks_session():
	"""Obtiene o crea una sesión HTTP reutilizable para QuickBooks con retry strategy."""
	global _quickbooks_session
	import requests
	
	if _quickbooks_session is not None:
		return _quickbooks_session
	
	if HTTPX_AVAILABLE:
		# Sesión httpx con límites y timeout
		limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
		timeout = httpx.Timeout(30.0, connect=10.0)
		_quickbooks_session = httpx.Client(
			limits=limits,
			timeout=timeout,
			follow_redirects=True,
		)
	elif REQUESTS_ADAPTER_AVAILABLE:
		session = requests.Session()
		
		# Retry strategy mejorada
		retry_strategy = Retry(
			total=DEFAULT_MAX_RETRIES,
			backoff_factor=DEFAULT_RETRY_DELAY,
			status_forcelist=[429, 500, 502, 503, 504],
			allowed_methods=["GET", "POST"],
			raise_on_status=False,
		)
		adapter = HTTPAdapter(max_retries=retry_strategy, pool_maxsize=DEFAULT_POOL_MAXSIZE)
		session.mount("http://", adapter)
		session.mount("https://", adapter)
		_quickbooks_session = session
	else:
		# Fallback sin sesión reutilizable
		_quickbooks_session = None
	
	return _quickbooks_session


@contextmanager
def _track_api_call(api_name: str, operation: str):
	"""Context manager para trackear llamadas API con métricas."""
	start = time.time()
	if STATS_AVAILABLE and Stats:
		try:
			Stats.incr(f"stripe_fees_to_quickbooks.api.{api_name}.{operation}.attempt", 1)
		except Exception:
			pass
	try:
		yield
		duration_ms = (time.time() - start) * 1000
		if STATS_AVAILABLE and Stats:
			try:
				Stats.incr(f"stripe_fees_to_quickbooks.api.{api_name}.{operation}.success", 1)
				Stats.timing(f"stripe_fees_to_quickbooks.api.{api_name}.{operation}.duration_ms", int(duration_ms))
			except Exception:
				pass
	except Exception as e:
		duration_ms = (time.time() - start) * 1000
		if STATS_AVAILABLE and Stats:
			try:
				Stats.incr(f"stripe_fees_to_quickbooks.api.{api_name}.{operation}.failed", 1)
			except Exception:
				pass
		raise


def _make_stripe_request_with_retry(
	url: str,
	headers: Dict[str, str],
	method: str = "GET",
	params: Optional[Dict[str, Any]] = None,
	max_retries: int = DEFAULT_MAX_RETRIES,
	retry_delay: float = DEFAULT_RETRY_DELAY,
	timeout: int = DEFAULT_TIMEOUT
) -> requests.Response:
	"""
	Realiza una petición a Stripe API con retry y manejo de rate limiting.
	Usa sesiones HTTP reutilizables y tenacity si está disponible.
	"""
	import requests
	
	# Intentar usar sesión reutilizable
	session = _get_stripe_session()
	use_session = session is not None
	
	if TENACITY_AVAILABLE:
		@retry(
			stop=stop_after_attempt(max_retries + 1),
			wait=wait_exponential(multiplier=retry_delay, min=retry_delay, max=RATE_LIMIT_MAX_WAIT),
			retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError)),
			before_sleep=before_sleep_log(logger, logging.WARNING),
			after=after_log(logger, logging.INFO),
		)
		def _make_request():
			if use_session and session:
				if method.upper() == "GET":
					response = session.get(url, headers=headers, params=params, timeout=timeout)
				else:
					response = session.request(method, url, headers=headers, json=params, timeout=timeout)
			else:
				if method.upper() == "GET":
					response = requests.get(url, headers=headers, params=params, timeout=timeout)
				else:
					response = requests.request(method, url, headers=headers, json=params, timeout=timeout)
			
			# Manejar rate limiting (429)
			if response.status_code == 429:
				retry_after = int(response.headers.get(STRIPE_RATE_LIMIT_HEADER, retry_delay))
				retry_after = min(retry_after, RATE_LIMIT_MAX_WAIT)
				
				if STATS_AVAILABLE and Stats:
					try:
						Stats.incr("stripe_fees_to_quickbooks.api.stripe.rate_limit", 1)
						Stats.timing("stripe_fees_to_quickbooks.api.stripe.rate_limit_wait", retry_after)
					except Exception:
						pass
				
				logger.warning(
					f"Rate limited by Stripe, waiting {retry_after}s",
					extra={"url": url, "retry_after": retry_after}
				)
				time.sleep(retry_after)
				raise StripeAPIError(f"Rate limited, retry after {retry_after}s", status_code=429)
			
			response.raise_for_status()
			return response
		
		return _make_request()
	else:
		# Fallback sin tenacity
		for attempt in range(max_retries + 1):
			try:
				if use_session and session:
					if method.upper() == "GET":
						response = session.get(url, headers=headers, params=params, timeout=timeout)
					else:
						response = session.request(method, url, headers=headers, json=params, timeout=timeout)
				else:
					if method.upper() == "GET":
						response = requests.get(url, headers=headers, params=params, timeout=timeout)
					else:
						response = requests.request(method, url, headers=headers, json=params, timeout=timeout)
				
				# Manejar rate limiting (429)
				if response.status_code == 429:
					retry_after = int(response.headers.get(STRIPE_RATE_LIMIT_HEADER, retry_delay))
					retry_after = min(retry_after, RATE_LIMIT_MAX_WAIT)
					
					if STATS_AVAILABLE and Stats:
						try:
							Stats.incr("stripe_fees_to_quickbooks.api.stripe.rate_limit", 1)
						except Exception:
							pass
					
					if attempt < max_retries:
						logger.warning(
							f"Rate limited by Stripe, waiting {retry_after}s before retry {attempt + 1}/{max_retries}",
							extra={"url": url, "attempt": attempt + 1, "retry_after": retry_after}
						)
						time.sleep(retry_after)
						continue
					else:
						response.raise_for_status()
				
				response.raise_for_status()
				return response
				
			except requests.exceptions.Timeout:
				if attempt < max_retries:
					delay = retry_delay * (2 ** attempt)
					logger.warning(f"Timeout on Stripe request, retrying in {delay}s", extra={"attempt": attempt + 1})
					time.sleep(delay)
					continue
				raise
			except requests.exceptions.RequestException as e:
				if attempt < max_retries:
					delay = retry_delay * (2 ** attempt)
					logger.warning(f"Request error on Stripe API, retrying in {delay}s: {e}", extra={"attempt": attempt + 1})
					time.sleep(delay)
					continue
				raise
		
		raise requests.exceptions.RequestException(f"Max retries ({max_retries}) exceeded for {url}")


def _get_stripe_fees_for_charge(charge_id: str, stripe_key: str) -> List[Dict[str, Any]]:
	"""
	Obtiene las tarifas de Stripe para un charge específico.
	Las tarifas están en las balance_transactions relacionadas.
	"""
	import requests
	
	fees: List[Dict[str, Any]] = []
	start_time = time.time()
	
	try:
		headers = {"Authorization": f"Bearer {stripe_key}"}
		
		# Obtener el charge completo para acceder a balance_transaction
		charge_r = _make_stripe_request_with_retry(
			f"https://api.stripe.com/v1/charges/{charge_id}",
			headers
		)
		charge = charge_r.json()
		
		# El charge tiene un campo balance_transaction que contiene la tarifa
		balance_transaction_id = charge.get("balance_transaction")
		
		if balance_transaction_id:
			# Obtener los detalles de la balance_transaction que contiene la tarifa
			bt_r = _make_stripe_request_with_retry(
				f"https://api.stripe.com/v1/balance_transactions/{balance_transaction_id}",
				headers
			)
			balance_transaction = bt_r.json()
			
			# La tarifa está en el campo 'fee'
			fee_amount = balance_transaction.get("fee", 0)
			fee_details = balance_transaction.get("fee_details", [])
			
			# Si hay una tarifa
			if fee_amount > 0:
				fee_description = balance_transaction.get("description") or f"Tarifa Stripe - {charge_id}"
				
				# Construir descripción detallada si hay fee_details
				if fee_details:
					fee_type_parts = []
					for fd in fee_details:
						fee_type = fd.get("type", "unknown")
						fee_amount_detail = fd.get("amount", 0) / 100.0
						fee_type_parts.append(f"{fee_type}: ${fee_amount_detail:.2f}")
					fee_description = f"{fee_description} ({', '.join(fee_type_parts)})"
				
				duration_ms = (time.time() - start_time) * 1000
				
				fees.append({
					"payment_id": charge_id,
					"fee_amount": fee_amount / 100.0,  # Convertir de centavos a dólares
					"currency": balance_transaction.get("currency", charge.get("currency", "usd")).upper(),
					"description": fee_description,
					"payment_date": charge.get("created"),  # Timestamp Unix
					"balance_transaction_id": balance_transaction_id,
					"payment_amount": (charge.get("amount") or 0) / 100.0,
				})
				
				logger.debug(
					f"Found fee for charge {charge_id}",
					extra={
						"charge_id": charge_id,
						"fee_amount": fee_amount / 100.0,
						"duration_ms": duration_ms
					}
				)
		
	except requests.exceptions.HTTPError as e:
		if e.response.status_code == 404:
			logger.debug(f"Charge {charge_id} not found in Stripe", extra={"charge_id": charge_id})
		else:
			logger.warning(
				f"HTTP error getting fees for charge {charge_id}: {e}",
				extra={"charge_id": charge_id, "status_code": e.response.status_code},
				exc_info=True
			)
	except Exception as e:
		logger.warning(
			f"Error obteniendo tarifas para charge {charge_id}: {e}",
			extra={"charge_id": charge_id},
			exc_info=True
		)
	
	return fees


def _make_quickbooks_request_with_retry(
	url: str,
	headers: Dict[str, str],
	method: str = "GET",
	json_data: Optional[Dict[str, Any]] = None,
	params: Optional[Dict[str, Any]] = None,
	max_retries: int = DEFAULT_MAX_RETRIES,
	retry_delay: float = DEFAULT_RETRY_DELAY,
	timeout: int = DEFAULT_TIMEOUT
) -> requests.Response:
	"""
	Realiza una petición a QuickBooks API con retry y manejo de rate limiting.
	Usa sesiones HTTP reutilizables y tenacity si está disponible.
	"""
	import requests
	
	# Intentar usar sesión reutilizable
	session = _get_quickbooks_session()
	use_session = session is not None
	
	if TENACITY_AVAILABLE:
		@retry(
			stop=stop_after_attempt(max_retries + 1),
			wait=wait_exponential(multiplier=retry_delay, min=retry_delay, max=RATE_LIMIT_MAX_WAIT),
			retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError)),
			before_sleep=before_sleep_log(logger, logging.WARNING),
			after=after_log(logger, logging.INFO),
		)
		def _make_request():
			if use_session and session:
				if method.upper() == "GET":
					response = session.get(url, headers=headers, params=params, timeout=timeout)
				elif method.upper() == "POST":
					response = session.post(url, headers=headers, json=json_data, timeout=timeout)
				else:
					response = session.request(method, url, headers=headers, json=json_data, params=params, timeout=timeout)
			else:
				if method.upper() == "GET":
					response = requests.get(url, headers=headers, params=params, timeout=timeout)
				elif method.upper() == "POST":
					response = requests.post(url, headers=headers, json=json_data, timeout=timeout)
				else:
					response = requests.request(method, url, headers=headers, json=json_data, params=params, timeout=timeout)
			
			# Manejar rate limiting (429)
			if response.status_code == 429:
				retry_after = int(response.headers.get(QB_RATE_LIMIT_HEADER, retry_delay))
				retry_after = min(retry_after, RATE_LIMIT_MAX_WAIT)
				
				if STATS_AVAILABLE and Stats:
					try:
						Stats.incr("stripe_fees_to_quickbooks.api.quickbooks.rate_limit", 1)
						Stats.timing("stripe_fees_to_quickbooks.api.quickbooks.rate_limit_wait", retry_after)
					except Exception:
						pass
				
				logger.warning(
					f"Rate limited by QuickBooks, waiting {retry_after}s",
					extra={"url": url, "retry_after": retry_after}
				)
				time.sleep(retry_after)
				raise QuickBooksAPIError(f"Rate limited, retry after {retry_after}s", status_code=429)
			
			# Manejar errores de autorización (401)
			if response.status_code == 401:
				logger.error("QuickBooks authentication failed - token may be expired")
				raise QuickBooksAPIError("QuickBooks authentication failed", status_code=401)
			
			response.raise_for_status()
			return response
		
		return _make_request()
	else:
		# Fallback sin tenacity
		for attempt in range(max_retries + 1):
			try:
				if use_session and session:
					if method.upper() == "GET":
						response = session.get(url, headers=headers, params=params, timeout=timeout)
					elif method.upper() == "POST":
						response = session.post(url, headers=headers, json=json_data, timeout=timeout)
					else:
						response = session.request(method, url, headers=headers, json=json_data, params=params, timeout=timeout)
				else:
					if method.upper() == "GET":
						response = requests.get(url, headers=headers, params=params, timeout=timeout)
					elif method.upper() == "POST":
						response = requests.post(url, headers=headers, json=json_data, timeout=timeout)
					else:
						response = requests.request(method, url, headers=headers, json=json_data, params=params, timeout=timeout)
				
				# Manejar rate limiting (429)
				if response.status_code == 429:
					retry_after = int(response.headers.get(QB_RATE_LIMIT_HEADER, retry_delay))
					retry_after = min(retry_after, RATE_LIMIT_MAX_WAIT)
					
					if STATS_AVAILABLE and Stats:
						try:
							Stats.incr("stripe_fees_to_quickbooks.api.quickbooks.rate_limit", 1)
						except Exception:
							pass
					
					if attempt < max_retries:
						logger.warning(
							f"Rate limited by QuickBooks, waiting {retry_after}s before retry {attempt + 1}/{max_retries}",
							extra={"url": url, "attempt": attempt + 1, "retry_after": retry_after}
						)
						time.sleep(retry_after)
						continue
					else:
						response.raise_for_status()
				
				# Manejar errores de autorización (401)
				if response.status_code == 401:
					logger.error("QuickBooks authentication failed - token may be expired")
					raise QuickBooksAPIError("QuickBooks authentication failed", status_code=401)
				
				response.raise_for_status()
				return response
				
			except requests.exceptions.Timeout:
				if attempt < max_retries:
					delay = retry_delay * (2 ** attempt)
					logger.warning(f"Timeout on QuickBooks request, retrying in {delay}s", extra={"attempt": attempt + 1})
					time.sleep(delay)
					continue
				raise
			except requests.exceptions.RequestException as e:
				if attempt < max_retries and not isinstance(e, requests.exceptions.HTTPError):
					delay = retry_delay * (2 ** attempt)
					logger.warning(f"Request error on QuickBooks API, retrying in {delay}s: {e}", extra={"attempt": attempt + 1})
					time.sleep(delay)
					continue
				raise
		
		raise requests.exceptions.RequestException(f"Max retries ({max_retries}) exceeded for {url}")


def _create_quickbooks_expense(
	fee_amount: float,
	fee_description: str,
	payment_date: int,  # Unix timestamp
	payment_id: str,
	currency: str,
	quickbooks_access_token: str,
	quickbooks_realm_id: str,
	expense_account_name: str = "Tarifas Stripe"
) -> Dict[str, Any]:
	"""
	Crea un gasto en QuickBooks Online usando la API v3.
	
	Args:
		fee_amount: Monto de la tarifa
		fee_description: Descripción del gasto
		payment_date: Fecha del pago (Unix timestamp)
		payment_id: ID del pago Stripe para referencia
		currency: Moneda del gasto
		quickbooks_access_token: Access token de OAuth2 de QuickBooks
		quickbooks_realm_id: Realm ID (Company ID) de QuickBooks
		expense_account_name: Nombre de la cuenta de gastos
	
	Returns:
		Dict con la respuesta de QuickBooks
	"""
	import requests
	from datetime import datetime
	
	if not quickbooks_access_token or not quickbooks_realm_id:
		raise AirflowFailException("QuickBooks credentials not configured")
	
	# Validar inputs
	if fee_amount <= 0:
		raise ValueError(f"fee_amount must be positive, got {fee_amount}")
	if not payment_id:
		raise ValueError("payment_id is required")
	
	# Convertir timestamp a fecha
	try:
		payment_date_str = datetime.utcfromtimestamp(payment_date).strftime("%Y-%m-%d")
	except (ValueError, OSError) as e:
		logger.error(f"Invalid payment_date timestamp: {payment_date}", exc_info=True)
		raise ValueError(f"Invalid payment_date: {payment_date}") from e
	
	# Configurar headers
	headers = {
		"Authorization": f"Bearer {quickbooks_access_token}",
		"Accept": "application/json",
		"Content-Type": "application/json",
	}
	
	# Determinar URL base
	use_sandbox = _get_env_var("QUICKBOOKS_USE_SANDBOX", default="true").lower() == "true"
	if use_sandbox:
		base_url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{quickbooks_realm_id}"
	else:
		base_url = f"https://quickbooks.api.intuit.com/v3/company/{quickbooks_realm_id}"
	
	# Escapar comillas en el nombre de cuenta para la query
	escaped_account_name = expense_account_name.replace("'", "''")
	
	# Buscar cuenta de gastos (con cache si está disponible)
	cache_key = f"account:{expense_account_name}"
	account_id = None
	
	if CACHETOOLS_AVAILABLE and _account_cache:
		try:
			cached_id = _account_cache.get(cache_key)
			if cached_id:
				logger.debug(f"Account ID found in cache: {expense_account_name}", extra={"cache_key": cache_key})
				account_id = cached_id
		except Exception as e:
			logger.debug(f"Cache lookup failed: {e}")
	
	if not account_id:
		account_query = f"SELECT * FROM Account WHERE Name = '{escaped_account_name}' AND Active = true MAXRESULTS 1"
		query_url = f"{base_url}/query"
		
		try:
			with _track_api_call("quickbooks", "query_account"):
				query_response = _make_quickbooks_request_with_retry(
					query_url,
					headers,
					method="GET",
					params={"query": account_query}
				)
			query_data = query_response.json()
			
			if query_data.get("QueryResponse", {}).get("Account"):
				accounts = query_data["QueryResponse"]["Account"]
				if isinstance(accounts, list) and len(accounts) > 0:
					account_id = accounts[0].get("Id")
				elif isinstance(accounts, dict):
					account_id = accounts.get("Id")
			
			# Guardar en cache si se encontró
			if account_id and CACHETOOLS_AVAILABLE and _account_cache:
				try:
					_account_cache[cache_key] = account_id
					logger.debug(f"Cached account ID for {expense_account_name}", extra={"account_id": account_id})
				except Exception as e:
					logger.debug(f"Failed to cache account ID: {e}")
		except Exception as e:
			logger.warning(f"Error querying account: {e}", exc_info=True)
	
	if not account_id:
		# Si la cuenta no existe, intentar crearla
		logger.warning(f"Account '{expense_account_name}' not found, attempting to create it")
		account_payload = {
			"Name": expense_account_name,
			"AccountType": "Expense",
			"AccountSubType": "OfficeExpenses",
		}
		with _track_api_call("quickbooks", "create_account"):
			account_create_r = _make_quickbooks_request_with_retry(
				f"{base_url}/account",
				headers,
				method="POST",
				json_data=account_payload
			)
		
		if account_create_r.status_code in (200, 201):
			account_data = account_create_r.json()
			account_id = account_data.get("Account", {}).get("Id")
			logger.info(f"Created expense account '{expense_account_name}' in QuickBooks", extra={"account_id": account_id})
			
			# Guardar en cache inmediatamente
			if account_id and CACHETOOLS_AVAILABLE and _account_cache:
				try:
					_account_cache[cache_key] = account_id
				except Exception:
					pass
		else:
			raise AirflowFailException(
				f"Failed to find or create account '{expense_account_name}': {account_create_r.text}"
			)
		
	# Validar datos con Pydantic si está disponible
	if PYDANTIC_AVAILABLE:
		try:
			fee_data_validated = FeeData(
				payment_id=payment_id,
				fee_amount=fee_amount,
				currency=currency,
				description=fee_description,
				payment_date=payment_date,
			)
			# Usar valores validados
			fee_amount = float(fee_data_validated.fee_amount)
		except ValidationError as ve:
			logger.warning(f"Pydantic validation warning (continuing): {ve}", extra={"payment_id": payment_id})
		except Exception as e:
			logger.debug(f"Pydantic validation skipped: {e}")
	
	# Crear el gasto (Purchase)
	purchase_payload = {
		"PaymentType": "Cash",
		"AccountRef": {
			"value": account_id,
			"name": expense_account_name,
		},
		"Line": [
			{
				"Amount": round(fee_amount, 2),  # Redondear a 2 decimales
				"DetailType": "AccountBasedExpenseLineDetail",
				"AccountBasedExpenseLineDetail": {
					"AccountRef": {
						"value": account_id,
						"name": expense_account_name,
					},
				},
			},
		],
		"TxnDate": payment_date_str,
		"DocNumber": f"STRIPE-{payment_id}",  # Referencia del pago Stripe
		"PrivateNote": f"Tarifa Stripe para pago {payment_id}. {fee_description}",
	}
	
	# Crear el gasto en QuickBooks
	start_time = time.time()
	try:
		with _track_api_call("quickbooks", "create_purchase"):
			expense_r = _make_quickbooks_request_with_retry(
				f"{base_url}/purchase",
				headers,
				method="POST",
				json_data=purchase_payload
			)
		duration_ms = (time.time() - start_time) * 1000
		
		result = expense_r.json()
		qb_expense_id = result.get("Purchase", {}).get("Id")
		
		logger.info(
			"Expense created in QuickBooks",
			extra={
				"payment_id": payment_id,
				"fee_amount": fee_amount,
				"quickbooks_id": qb_expense_id,
				"account_name": expense_account_name,
				"duration_ms": duration_ms
			},
		)
		
		return result
	except requests.exceptions.HTTPError as e:
		status_code = e.response.status_code if hasattr(e, 'response') else None
		error_details = {}
		
		if hasattr(e, 'response') and e.response is not None:
			try:
				error_details = e.response.json()
			except:
				error_details = {"text": e.response.text[:500]}
		
		# Categorizar errores para mejor manejo
		if status_code == 401:
			raise QuickBooksAPIError(
				"QuickBooks authentication failed - token may be expired",
				status_code=401,
				error_data=error_details
			) from e
		elif status_code == 429:
			raise QuickBooksAPIError(
				"QuickBooks rate limit exceeded",
				status_code=429,
				error_data=error_details
			) from e
		elif status_code in (400, 422):
			raise QuickBooksAPIError(
				f"QuickBooks validation error: {error_details}",
				status_code=status_code,
				error_data=error_details
			) from e
		else:
			error_msg = f"QuickBooks API error (HTTP {status_code or 'unknown'}): {error_details}"
			logger.error(
				error_msg,
				extra={
					"payment_id": payment_id,
					"error_details": error_details,
					"status_code": status_code
				},
				exc_info=True
			)
			raise QuickBooksAPIError(error_msg, status_code=status_code, error_data=error_details) from e
	except Exception as e:
		logger.error(
			f"Error creating QuickBooks expense: {e}",
			extra={"payment_id": payment_id},
			exc_info=True
		)
		raise


def _send_slack_notification(text: str) -> None:
	"""Envía notificación a Slack si está configurado."""
	try:
		slack_webhook = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
		if slack_webhook:
			import requests
			requests.post(slack_webhook, json={"text": text}, timeout=5)
	except Exception:
		# Best effort, no fallar el DAG por notificaciones
		pass


def _cb_key() -> str:
	"""Genera la clave del circuit breaker para este DAG."""
	return "cb:failures:stripe_fees_to_quickbooks"


def _cb_is_open(threshold: int = CB_FAILURE_THRESHOLD, reset_minutes: int = CB_RESET_MINUTES) -> bool:
	"""
	Verifica si el circuit breaker está abierto.
	
	Returns:
		True si el circuit breaker está abierto (demasiados fallos)
	"""
	try:
		key = _cb_key()
		data_str = Variable.get(key, default_var=None)
		if not data_str:
			return False
		
		data = json.loads(data_str)
		failures = data.get("count", 0)
		last_failure_ts = data.get("last_failure_ts", 0)
		
		# Auto-reset después del tiempo configurado
		now = pendulum.now("UTC").int_timestamp
		if (now - last_failure_ts) > (reset_minutes * 60) and failures > 0:
			logger.info("Circuit breaker auto-reset after timeout")
			Variable.delete(key)
			if STATS_AVAILABLE and Stats:
				try:
					Stats.incr("stripe_fees_to_quickbooks.circuit_breaker.auto_reset", 1)
				except Exception:
					pass
			return False
		
		return failures >= threshold
	except Exception as e:
		logger.warning(f"Error checking circuit breaker: {e}")
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
		
		Variable.set(key, json.dumps({
			"count": count,
			"last_failure_ts": now_ts,
		}))
		
		if STATS_AVAILABLE and Stats:
			try:
				Stats.incr("stripe_fees_to_quickbooks.circuit_breaker.failures", 1)
				Stats.gauge("stripe_fees_to_quickbooks.circuit_breaker.count", count)
			except Exception:
				pass
		
		if count >= CB_FAILURE_THRESHOLD:
			logger.error(
				f"Circuit breaker opened after {count} failures",
				extra={"failures": count, "threshold": CB_FAILURE_THRESHOLD}
			)
			if STATS_AVAILABLE and Stats:
				try:
					Stats.incr("stripe_fees_to_quickbooks.circuit_breaker.opened", 1)
				except Exception:
					pass
	except Exception as e:
		logger.warning(f"Failed to record circuit breaker failure: {e}")


def _cb_reset() -> None:
	"""Resetea el circuit breaker."""
	try:
		key = _cb_key()
		Variable.delete(key)
		
		if STATS_AVAILABLE and Stats:
			try:
				Stats.incr("stripe_fees_to_quickbooks.circuit_breaker.reset", 1)
			except Exception:
				pass
	except Exception as e:
		logger.debug(f"Failed to reset circuit breaker: {e}")


def _perform_health_check() -> bool:
	"""
	Realiza un health check de las APIs externas antes de procesar.
	
	Returns:
		True si todos los health checks pasan
	"""
	try:
		# Health check de Stripe
		stripe_key = os.environ.get("STRIPE_API_KEY", "").strip()
		if stripe_key:
			headers = {"Authorization": f"Bearer {stripe_key}"}
			import requests
			r = requests.get("https://api.stripe.com/v1/charges?limit=1", headers=headers, timeout=10)
			if r.status_code == 401:
				logger.error("Stripe API authentication failed")
				return False
			r.raise_for_status()
		
		# Health check de QuickBooks
		qb_token = os.environ.get("QUICKBOOKS_ACCESS_TOKEN", "").strip()
		qb_realm = os.environ.get("QUICKBOOKS_REALM_ID", "").strip()
		if qb_token and qb_realm:
			use_sandbox = _get_env_var("QUICKBOOKS_USE_SANDBOX", default="true").lower() == "true"
			if use_sandbox:
				base_url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{qb_realm}"
			else:
				base_url = f"https://quickbooks.api.intuit.com/v3/company/{qb_realm}"
			
			qb_headers = {
				"Authorization": f"Bearer {qb_token}",
				"Accept": "application/json",
			}
			import requests
			r = requests.get(f"{base_url}/companyinfo/{qb_realm}", headers=qb_headers, timeout=10)
			if r.status_code == 401:
				logger.error("QuickBooks API authentication failed")
				return False
			if r.status_code not in (200, 201):
				logger.warning(f"QuickBooks health check returned {r.status_code}")
		
		if STATS_AVAILABLE and Stats:
			try:
				Stats.incr("stripe_fees_to_quickbooks.health_check.success", 1)
			except Exception:
				pass
		
		return True
	except Exception as e:
		logger.warning(f"Health check failed: {e}", exc_info=True)
		if STATS_AVAILABLE and Stats:
			try:
				Stats.incr("stripe_fees_to_quickbooks.health_check.failed", 1)
			except Exception:
				pass
		return False


def _validate_credentials() -> None:
	"""
	Valida que las credenciales estén configuradas (guard clause).
	"""
	stripe_key = os.environ.get("STRIPE_API_KEY", "").strip()
	qb_token = os.environ.get("QUICKBOOKS_ACCESS_TOKEN", "").strip()
	qb_realm = os.environ.get("QUICKBOOKS_REALM_ID", "").strip()
	
	errors = []
	if not stripe_key:
		errors.append("STRIPE_API_KEY")
	if not qb_token:
		errors.append("QUICKBOOKS_ACCESS_TOKEN")
	if not qb_realm:
		errors.append("QUICKBOOKS_REALM_ID")
	
	if errors:
		raise AirflowFailException(f"Missing required credentials: {', '.join(errors)}")


@dag(
	dag_id="stripe_fees_to_quickbooks",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule="0 3 * * *",  # daily at 03:00 UTC
	catchup=False,
	default_args={
		"owner": "finance",
		"retries": 2,
		"retry_delay": timedelta(minutes=5),
		"retry_exponential_backoff": True,
		"max_retry_delay": timedelta(minutes=30),
		"email_on_failure": False,
		"email_on_retry": False,
	},
	dagrun_timeout=timedelta(minutes=60),
	max_active_runs=1,
	description="Crea gastos en QuickBooks para las tarifas de Stripe de pagos exitosos",
	tags=["finance", "stripe", "quickbooks", "accounting"],
	params={
		"batch_size": Param(
			10,
			type="integer",
			minimum=1,
			maximum=50,
			description="Número de gastos a procesar por batch",
		),
		"batch_delay": Param(
			0.5,
			type="number",
			minimum=0,
			maximum=10,
			description="Delay entre batches en segundos",
		),
		"continue_on_error": Param(
			True,
			type="boolean",
			description="Continuar procesando otros gastos si uno falla",
		),
		"dry_run": Param(
			False,
			type="boolean",
			description="Simular sin crear gastos en QuickBooks",
		),
	},
	doc_md="""
	# Stripe Fees to QuickBooks
	
	Para cada pago exitoso en Stripe con tarifa, crea un gasto en QuickBooks
	en la cuenta 'Tarifas Stripe' por el monto de la tarifa.
	
	## Características
	
	- ✅ Health check pre-vuelo de APIs externas
	- ✅ Circuit breaker con auto-reset (protección contra fallos en cascada)
	- ✅ Obtiene pagos exitosos de Stripe del período configurado
	- ✅ Extrae las tarifas de cada pago desde balance_transactions
	- ✅ Crea gastos en QuickBooks con referencia del pago Stripe
	- ✅ Evita duplicados verificando si el gasto ya fue creado
	- ✅ Procesamiento en batches con rate limiting inteligente
	- ✅ Métricas de performance y estadísticas completas (StatsD/Prometheus)
	- ✅ Soporte para dry-run mode
	- ✅ Validación robusta de credenciales (guard clauses)
	- ✅ Retry con exponential backoff para todas las APIs
	- ✅ Manejo inteligente de rate limiting (429)
	- ✅ Notificaciones Slack automáticas
	- ✅ Tracking de progreso en Variables de Airflow
	
	## Parámetros Opcionales
	
	- `batch_size`: Número de gastos por batch (default: 10)
	- `batch_delay`: Delay entre batches en segundos (default: 0.5)
	- `continue_on_error`: Continuar si un gasto falla (default: true)
	- `dry_run`: Simular sin crear gastos (default: false)
	
	## Configuración Requerida
	
	### Variables de Entorno
	
	- `STRIPE_API_KEY`: API key de Stripe
	- `QUICKBOOKS_ACCESS_TOKEN`: Access token OAuth2 de QuickBooks
	- `QUICKBOOKS_REALM_ID`: Company ID (Realm ID) de QuickBooks
	
	### Variables de Airflow
	
	- `QUICKBOOKS_EXPENSE_ACCOUNT`: Nombre de la cuenta de gastos (default: "Tarifas Stripe")
	- `QUICKBOOKS_USE_SANDBOX`: Usar sandbox de QuickBooks (default: "true")
	- `STRIPE_FEES_LOOKBACK_DAYS`: Días hacia atrás para buscar pagos (default: "1")
	""",
	on_success_callback=lambda context: _send_slack_notification(
		f":white_check_mark: stripe_fees_to_quickbooks completed successfully"
	),
	on_failure_callback=lambda context: _send_slack_notification(
		f":x: stripe_fees_to_quickbooks failed"
	),
)
def stripe_fees_to_quickbooks() -> None:
	"""DAG principal para procesar tarifas de Stripe y crear gastos en QuickBooks."""
	
	@task(
		task_id="health_check",
		execution_timeout=timedelta(minutes=2),
		retries=0,  # No retry en health checks
	)
	def health_check() -> None:
		"""
		Health check pre-vuelo de APIs externas.
		"""
		_validate_credentials()
		
		if not _perform_health_check():
			_cb_record_failure()
			raise AirflowFailException("Health check failed - one or more APIs are not accessible")
		
		# Si health check pasa, resetear circuit breaker si estaba abierto
		if _cb_is_open():
			logger.info("Health check passed, resetting circuit breaker")
			_cb_reset()
		
		logger.info("Health check passed for all APIs")
	
	@task(
		task_id="fetch_stripe_fees",
		execution_timeout=timedelta(minutes=10),
		retries=2,
		retry_delay=timedelta(minutes=2),
	)
	def fetch_stripe_fees() -> Dict[str, Any]:
		"""
		Obtiene pagos exitosos de Stripe y extrae sus tarifas.
		"""
		import os
		import requests
		
		# Verificar circuit breaker
		if _cb_is_open():
			raise AirflowFailException(
				f"Circuit breaker is open - too many failures. "
				f"Wait {CB_RESET_MINUTES} minutes or reset manually."
			)
		
		stripe_key = os.environ.get("STRIPE_API_KEY", "").strip()
		if not stripe_key:
			raise AirflowFailException("STRIPE_API_KEY not configured")
		
		ctx = get_current_context()
		lookback_days = int(_get_env_var("STRIPE_FEES_LOOKBACK_DAYS", default="1"))
		
		# Calcular ventana de tiempo
		since_timestamp = int(
			(ctx["data_interval_start"] - timedelta(days=lookback_days)).int_timestamp
		)
		until_timestamp = int(ctx["data_interval_end"].int_timestamp)
		
		logger.info(
			"Fetching Stripe fees",
			extra={
				"since": since_timestamp,
				"until": until_timestamp,
				"lookback_days": lookback_days,
			},
		)
		
		all_fees: List[Dict[str, Any]] = []
		headers = {"Authorization": f"Bearer {stripe_key}"}
		
		# Obtener charges exitosos
		params = {
			"limit": 100,
			"created[gte]": since_timestamp,
			"created[lte]": until_timestamp,
			"paid": True,
		}
		
		starting_after = None
		charges_processed = 0
		start_time = time.time()
		
		while True:
			p = dict(params)
			if starting_after:
				p["starting_after"] = starting_after
			
			try:
				# Usar función de retry mejorada
				r = _make_stripe_request_with_retry(
					"https://api.stripe.com/v1/charges",
					headers,
					method="GET",
					params=p
				)
				out = r.json()
				data = out.get("data", [])
				
				for charge in data:
					charges_processed += 1
					charge_id = charge.get("id")
					
					if not charge_id:
						logger.warning("Charge without ID found, skipping", extra={"charge": charge})
						continue
					
					# Obtener tarifas para este charge
					with _track_api_call("stripe", "get_charge_fees"):
						fees = _get_stripe_fees_for_charge(charge_id, stripe_key)
					
					# Validar fees con Pydantic si está disponible
					validated_fees = []
					for fee in fees:
						try:
							if PYDANTIC_AVAILABLE:
								from decimal import Decimal
								fee_data = FeeData(
									payment_id=fee.get("payment_id", ""),
									fee_amount=Decimal(str(fee.get("fee_amount", 0))),
									currency=fee.get("currency", "USD").upper(),
									description=fee.get("description", ""),
									payment_date=fee.get("payment_date", 0),
									balance_transaction_id=fee.get("balance_transaction_id"),
									payment_amount=Decimal(str(fee.get("payment_amount", 0))) if fee.get("payment_amount") else None,
								)
								# Convertir de vuelta a dict para compatibilidad
								validated_fee = fee.copy()
								validated_fee["fee_amount"] = float(fee_data.fee_amount)
								validated_fee["currency"] = fee_data.currency
								validated_fees.append(validated_fee)
							else:
								# Validación básica sin Pydantic
								if fee.get("fee_amount", 0) > 0 and fee.get("payment_id"):
									validated_fees.append(fee)
								else:
									logger.warning(f"Invalid fee data, skipping: {fee}")
						except Exception as e:
							logger.warning(
								f"Fee validation failed, skipping: {e}",
								extra={"fee": fee, "charge_id": charge_id},
								exc_info=True
							)
					
					all_fees.extend(validated_fees)
					
					if validated_fees:
						logger.debug(
							"Found fees for charge",
							extra={
								"fee_count": len(validated_fees),
								"charge_id": charge_id,
								"total_fee": sum(f.get("fee_amount", 0) for f in validated_fees)
							},
						)
				
				if out.get("has_more") and data:
					starting_after = data[-1].get("id")
				else:
					break
			except requests.exceptions.HTTPError as e:
				error_msg = f"HTTP error fetching Stripe charges: {e}"
				if e.response.status_code == 401:
					logger.error("Stripe authentication failed - check STRIPE_API_KEY")
					_cb_record_failure()
					raise AirflowFailException("Stripe authentication failed") from e
				logger.error(error_msg, extra={"status_code": e.response.status_code}, exc_info=True)
				_cb_record_failure()
				break
			except Exception as e:
				logger.error(
					"Error fetching Stripe charges",
					extra={"error": str(e)},
					exc_info=True
				)
				_cb_record_failure()
				break
		
		duration_ms = (time.time() - start_time) * 1000
		
		total_fee_amount = sum(f.get("fee_amount", 0) for f in all_fees)
		throughput = charges_processed / (duration_ms / 1000.0) if duration_ms > 0 else 0
		
		# Métricas de Stats si está disponible
		if STATS_AVAILABLE and Stats:
			try:
				Stats.incr("stripe_fees_to_quickbooks.fetch.charges", charges_processed)
				Stats.incr("stripe_fees_to_quickbooks.fetch.fees", len(all_fees))
				Stats.timing("stripe_fees_to_quickbooks.fetch.duration_ms", int(duration_ms))
				Stats.gauge("stripe_fees_to_quickbooks.fetch.total_amount", total_fee_amount)
			except Exception:
				pass
		
		logger.info(
			"Fetched Stripe fees",
			extra={
				"charges_processed": charges_processed,
				"fees_found": len(all_fees),
				"total_fee_amount": total_fee_amount,
				"duration_ms": duration_ms,
				"throughput_per_sec": throughput,
			},
		)
		
		# Si éxito, resetear circuit breaker
		if charges_processed > 0:
			_cb_reset()
		
		return {"fees": all_fees}
	
	@task(
		task_id="check_existing_expenses",
		execution_timeout=timedelta(minutes=5),
	)
	def check_existing_expenses(fees_payload: Dict[str, Any]) -> Dict[str, Any]:
		"""
		Verifica qué gastos ya fueron creados en QuickBooks para evitar duplicados.
		Usa la base de datos para tracking y crea índices para performance.
		"""
		fees = fees_payload.get("fees", []) or []
		if not fees:
			return {"fees_to_create": [], "fees_skipped": []}
		
		start_time = time.time()
		existing_payment_ids = set()
		
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					# Crear tabla de tracking si no existe con índices
					cur.execute(
						"""
						CREATE TABLE IF NOT EXISTS stripe_fees_quickbooks (
							id SERIAL PRIMARY KEY,
							payment_id TEXT NOT NULL,
							fee_amount NUMERIC(12,2) NOT NULL,
							currency VARCHAR(8) NOT NULL,
							quickbooks_expense_id TEXT,
							created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
							updated_at TIMESTAMPTZ,
							UNIQUE(payment_id)
						);
						"""
					)
					
					# Crear índices para performance
					cur.execute(
						"""
						CREATE INDEX IF NOT EXISTS idx_stripe_fees_payment_id 
						ON stripe_fees_quickbooks(payment_id);
						"""
					)
					cur.execute(
						"""
						CREATE INDEX IF NOT EXISTS idx_stripe_fees_created_at 
						ON stripe_fees_quickbooks(created_at);
						"""
					)
					
					# Obtener payment_ids ya procesados usando query eficiente
					payment_ids = [f.get("payment_id") for f in fees if f.get("payment_id")]
					if payment_ids:
						# Procesar en chunks para evitar queries muy grandes
						chunk_size = 1000
						for i in range(0, len(payment_ids), chunk_size):
							chunk = payment_ids[i:i + chunk_size]
							placeholders = ",".join(["%s"] * len(chunk))
							cur.execute(
								f"SELECT payment_id FROM stripe_fees_quickbooks WHERE payment_id IN ({placeholders})",
								chunk,
							)
							existing_payment_ids.update(row[0] for row in cur.fetchall())
					
					conn.commit()
		except Exception as e:
			logger.warning(
				f"Error checking existing expenses: {e}",
				extra={"total_fees": len(fees)},
				exc_info=True
			)
		
		fees_to_create = [f for f in fees if f.get("payment_id") not in existing_payment_ids]
		fees_skipped = [f for f in fees if f.get("payment_id") in existing_payment_ids]
		duration_ms = (time.time() - start_time) * 1000
		
		# Métricas
		if STATS_AVAILABLE and Stats:
			try:
				Stats.timing("stripe_fees_to_quickbooks.check_existing.duration_ms", int(duration_ms))
				Stats.gauge("stripe_fees_to_quickbooks.check_existing.duplicates_found", len(fees_skipped))
			except Exception:
				pass
		
		logger.info(
			"Checked existing expenses",
			extra={
				"total_fees": len(fees),
				"to_create": len(fees_to_create),
				"skipped": len(fees_skipped),
				"duplicate_rate_pct": (len(fees_skipped) / len(fees) * 100.0) if fees else 0.0,
				"duration_ms": duration_ms,
			},
		)
		
		return {"fees_to_create": fees_to_create, "fees_skipped": fees_skipped}
	
	@task(
		task_id="create_quickbooks_expenses",
		execution_timeout=timedelta(minutes=30),
		retries=2,
		retry_delay=timedelta(minutes=5),
	)
	def create_quickbooks_expenses(checked_payload: Dict[str, Any]) -> Dict[str, Any]:
		"""
		Crea los gastos en QuickBooks para las tarifas pendientes.
		Procesa en batches con delays configurables.
		"""
		ctx = get_current_context()
		params = ctx.get("params", {})
		
		fees_to_create = checked_payload.get("fees_to_create", []) or []
		dry_run = params.get("dry_run", False)
		batch_size = params.get("batch_size", DEFAULT_BATCH_SIZE)
		batch_delay = float(params.get("batch_delay", DEFAULT_BATCH_DELAY))
		continue_on_error = params.get("continue_on_error", True)
		
		if not fees_to_create:
			logger.info("No fees to create in QuickBooks")
			return ProcessingSummary().to_dict()
		
		if dry_run:
			logger.info(f"[DRY RUN] Would create {len(fees_to_create)} expenses in QuickBooks")
			return ProcessingSummary(
				total_fees=len(fees_to_create),
				fees_to_create=len(fees_to_create),
				total_fee_amount=sum(f.get("fee_amount", 0) for f in fees_to_create),
			).to_dict()
		
		quickbooks_token = os.environ.get("QUICKBOOKS_ACCESS_TOKEN", "").strip()
		quickbooks_realm_id = os.environ.get("QUICKBOOKS_REALM_ID", "").strip()
		expense_account = _get_env_var("QUICKBOOKS_EXPENSE_ACCOUNT", default="Tarifas Stripe")
		
		if not quickbooks_token or not quickbooks_realm_id:
			raise AirflowFailException(
				"QuickBooks credentials not configured (QUICKBOOKS_ACCESS_TOKEN, QUICKBOOKS_REALM_ID)"
			)
		
		summary = ProcessingSummary(
			total_fees=len(fees_to_create),
			fees_to_create=len(fees_to_create),
			total_fee_amount=sum(f.get("fee_amount", 0) for f in fees_to_create),
		)
		start_time = time.time()
		results: List[ExpenseCreationResult] = []
		
		# Procesar en batches
		for batch_idx in range(0, len(fees_to_create), batch_size):
			batch = fees_to_create[batch_idx:batch_idx + batch_size]
			batch_num = (batch_idx // batch_size) + 1
			total_batches = (len(fees_to_create) + batch_size - 1) // batch_size
			
			logger.info(
				f"Processing batch {batch_num}/{total_batches}",
				extra={
					"batch_size": len(batch),
					"batch_num": batch_num,
					"total_batches": total_batches,
					"progress_pct": (batch_idx / len(fees_to_create)) * 100.0,
				}
			)
			
			for fee in batch:
				payment_id = fee.get("payment_id")
				fee_amount = fee.get("fee_amount", 0)
				fee_description = fee.get("description", f"Tarifa Stripe - {payment_id}")
				payment_date = fee.get("payment_date", 0)
				currency = fee.get("currency", "USD")
				
				if fee_amount <= 0:
					logger.warning(f"Skipping fee with zero or negative amount: {payment_id}")
					continue
				
				expense_start = time.time()
				result_obj = ExpenseCreationResult(
					success=False,
					payment_id=payment_id,
					fee_amount=fee_amount,
				)
				
				try:
					# Trackear llamada API
					with _track_api_call("quickbooks", "create_expense"):
						result = _create_quickbooks_expense(
							fee_amount=fee_amount,
							fee_description=fee_description,
							payment_date=payment_date,
							payment_id=payment_id,
							currency=currency,
							quickbooks_access_token=quickbooks_token,
							quickbooks_realm_id=quickbooks_realm_id,
							expense_account_name=expense_account,
						)
					
					# Guardar en base de datos para tracking
					quickbooks_id = result.get("Purchase", {}).get("Id") if result else None
					
					# Guardar en base de datos con transacción atómica
					with get_conn() as conn:
						try:
							with conn.cursor() as cur:
								cur.execute(
									"""
									INSERT INTO stripe_fees_quickbooks 
										(payment_id, fee_amount, currency, quickbooks_expense_id)
									VALUES (%s, %s, %s, %s)
									ON CONFLICT (payment_id) DO UPDATE SET
										quickbooks_expense_id = EXCLUDED.quickbooks_expense_id,
										updated_at = NOW()
									""",
									(payment_id, fee_amount, currency, quickbooks_id),
								)
								conn.commit()
						except Exception as db_err:
							conn.rollback()
							logger.error(
								f"Failed to save expense tracking to database for {payment_id}: {db_err}",
								extra={"payment_id": payment_id, "error": str(db_err)},
								exc_info=True
							)
							# No fallar el DAG por error de DB, pero loguear
							if STATS_AVAILABLE and Stats:
								try:
									Stats.incr("stripe_fees_to_quickbooks.db.save_failed", 1)
								except Exception:
									pass
					
					result_obj.success = True
					result_obj.quickbooks_id = quickbooks_id
					result_obj.duration_ms = (time.time() - expense_start) * 1000
					
					summary.expenses_created += 1
					
					# Métricas de Stats
					if STATS_AVAILABLE and Stats:
						try:
							Stats.incr("stripe_fees_to_quickbooks.expense.created", 1)
							Stats.timing("stripe_fees_to_quickbooks.expense.duration_ms", int(result_obj.duration_ms))
						except Exception:
							pass
					
					logger.info(
						"Created expense in QuickBooks",
						extra={
							"payment_id": payment_id,
							"quickbooks_id": quickbooks_id,
							"fee_amount": fee_amount,
							"duration_ms": result_obj.duration_ms,
						}
					)
					
				except QuickBooksAPIError as e:
					# Error específico de QuickBooks API
					result_obj.error_message = str(e)[:500]
					result_obj.duration_ms = (time.time() - expense_start) * 1000
					
					summary.expenses_failed += 1
					summary.errors.append(result_obj.to_dict())
					
					# Métricas de Stats por tipo de error
					if STATS_AVAILABLE and Stats:
						try:
							Stats.incr("stripe_fees_to_quickbooks.expense.failed", 1)
							if e.status_code:
								Stats.incr(f"stripe_fees_to_quickbooks.expense.error.{e.status_code}", 1)
						except Exception:
							pass
					
					logger.error(
						"Failed to create expense for payment",
						extra={
							"payment_id": payment_id,
							"error": str(e)[:500],
							"status_code": e.status_code,
							"duration_ms": result_obj.duration_ms,
						},
						exc_info=True
					)
					
					# Registrar fallo crítico en circuit breaker si es error de autenticación
					if e.status_code == 401:
						_cb_record_failure()
					
					if not continue_on_error:
						raise
				except Exception as e:
					# Otros errores
					result_obj.error_message = str(e)[:500]
					result_obj.duration_ms = (time.time() - expense_start) * 1000
					
					summary.expenses_failed += 1
					summary.errors.append(result_obj.to_dict())
					
					# Métricas de Stats
					if STATS_AVAILABLE and Stats:
						try:
							Stats.incr("stripe_fees_to_quickbooks.expense.failed", 1)
							Stats.incr("stripe_fees_to_quickbooks.expense.error.unknown", 1)
						except Exception:
							pass
					
					logger.error(
						"Failed to create expense for payment",
						extra={
							"payment_id": payment_id,
							"error": str(e)[:500],
							"duration_ms": result_obj.duration_ms,
						},
						exc_info=True
					)
					
					# Registrar fallo crítico en circuit breaker si es error de autenticación
					if "authentication" in str(e).lower() or "401" in str(e):
						_cb_record_failure()
					
					if not continue_on_error:
						raise
				
				results.append(result_obj)
			
			# Delay entre batches
			if batch_idx + batch_size < len(fees_to_create) and batch_delay > 0:
				time.sleep(batch_delay)
		
		summary.duration_ms = (time.time() - start_time) * 1000
		
		# Métricas agregadas
		if STATS_AVAILABLE and Stats:
			try:
				Stats.incr("stripe_fees_to_quickbooks.processing.total", summary.total_fees)
				Stats.incr("stripe_fees_to_quickbooks.processing.created", summary.expenses_created)
				Stats.incr("stripe_fees_to_quickbooks.processing.failed", summary.expenses_failed)
				Stats.gauge("stripe_fees_to_quickbooks.processing.success_rate", summary.success_rate)
				Stats.timing("stripe_fees_to_quickbooks.processing.duration_ms", int(summary.duration_ms))
			except Exception:
				pass
		
		# Si hay muchos fallos, registrar en circuit breaker
		if summary.success_rate < 50.0 and summary.expenses_failed > 0:
			_cb_record_failure()
		
		# Si éxito completo, resetear circuit breaker
		if summary.expenses_failed == 0 and summary.expenses_created > 0:
			_cb_reset()
		
		logger.info(
			"Created QuickBooks expenses",
			extra=summary.to_dict(),
		)
		
		return summary.to_dict()
	
	@task(task_id="report_results")
	def report_results(created_payload: Dict[str, Any]) -> None:
		"""
		Reporta los resultados del procesamiento y actualiza progreso.
		"""
		summary = ProcessingSummary(**created_payload)
		
		# Actualizar progreso en Variables de Airflow
		try:
			progress_key = f"stripe_fees_to_quickbooks:last_run"
			progress_data = {
				"timestamp": pendulum.now("UTC").int_timestamp,
				"summary": summary.to_dict(),
			}
			Variable.set(progress_key, json.dumps(progress_data))
		except Exception as e:
			logger.warning(f"Failed to save progress to Variables: {e}")
		
		# Log resumen completo
		logger.info(
			"Stripe fees to QuickBooks processing completed",
			extra=summary.to_dict(),
		)
		
		# Mostrar errores si los hay
		if summary.errors:
			error_sample = summary.errors[:5]
			logger.warning(
				f"Errors during processing ({len(summary.errors)} total)",
				extra={"error_sample": error_sample}
			)
		
		# Notificación si hay fallos significativos
		if summary.expenses_failed > 0 and summary.success_rate < 50.0:
			_send_slack_notification(
				f":warning: stripe_fees_to_quickbooks: Low success rate ({summary.success_rate:.1f}%). "
				f"Created: {summary.expenses_created}, Failed: {summary.expenses_failed}"
			)
		
		return None
	
	# Construir el DAG con health check inicial
	health = health_check()
	fees_data = fetch_stripe_fees()
	checked_data = check_existing_expenses(fees_data)
	created_data = create_quickbooks_expenses(checked_data)
	report_results(created_data)
	
	# Dependencias: health check debe pasar antes de continuar
	health >> fees_data >> checked_data >> created_data >> report_results
	
	return None


dag = stripe_fees_to_quickbooks()

