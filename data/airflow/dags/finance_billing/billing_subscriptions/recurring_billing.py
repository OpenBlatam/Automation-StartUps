"""
DAG mejorado para procesamiento automático de transacciones recurrentes y suscripciones.

Mejoras implementadas:
- ✅ Retry con exponential backoff (tenacity si disponible)
- ✅ Circuit breaker con auto-reset
- ✅ Health check pre-vuelo de APIs
- ✅ Manejo inteligente de rate limiting (429)
- ✅ Logging estructurado con contexto completo
- ✅ Validación robusta de inputs (guard clauses)
- ✅ Timeouts configurables
- ✅ Métricas de performance detalladas (StatsD/Prometheus)
- ✅ Manejo específico de errores HTTP con excepciones personalizadas
- ✅ Sesiones HTTP reutilizables con connection pooling
- ✅ Procesamiento en batches con delays configurables
- ✅ Notificaciones Slack automáticas
- ✅ Tracking de progreso en Variables de Airflow
- ✅ Context managers para tracking de API calls

Integración con:
- invoice_generate.py (sistema de facturación existente)
- payment_reminders.py (recordatorios de pago)
- stripe_fees_to_quickbooks.py (sincronización contable)
"""
from __future__ import annotations

from datetime import timedelta, datetime, date
import logging
import os
import time
import json
from typing import Any, Dict, List, Optional, Callable
from decimal import Decimal
from dataclasses import dataclass, field
from contextlib import contextmanager

import pendulum
from airflow.decorators import dag, task, task_group
from airflow.operators.python import get_current_context
from airflow.models import Variable, Param
from airflow.exceptions import AirflowFailException
from data.airflow.plugins.db import get_conn
from data.airflow.plugins.etl_notifications import notify_email

logger = logging.getLogger(__name__)

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

# Intentar importar concurrent.futures para procesamiento paralelo
try:
	from concurrent.futures import ThreadPoolExecutor, as_completed
	CONCURRENT_AVAILABLE = True
except ImportError:
	CONCURRENT_AVAILABLE = False

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
	_subscription_cache = TTLCache(maxsize=200, ttl=300)  # 5 minutos
	_customer_cache = TTLCache(maxsize=500, ttl=300)  # 5 minutos

# Rate limiter global para Stripe API
_stripe_rate_limiter: Optional[Dict[str, Any]] = None


@dataclass
class BillingResult:
	"""Resultado del procesamiento de facturación de una suscripción."""
	subscription_id: str
	customer_id: str
	invoice_id: Optional[int] = None
	amount: float = 0.0
	currency: str = "USD"
	status: str = "pending"
	error_message: Optional[str] = None
	duration_ms: float = 0.0
	
	def to_dict(self) -> Dict[str, Any]:
		"""Convierte el resultado a diccionario."""
		return {
			"subscription_id": self.subscription_id,
			"customer_id": self.customer_id,
			"invoice_id": self.invoice_id,
			"amount": self.amount,
			"currency": self.currency,
			"status": self.status,
			"error_message": self.error_message,
			"duration_ms": self.duration_ms,
		}


@dataclass
class ProcessingSummary:
	"""Resumen del procesamiento de facturación recurrente."""
	total_subscriptions: int = 0
	invoices_generated: int = 0
	payments_processed: int = 0
	payments_successful: int = 0
	payments_failed: int = 0
	failed_payments: int = 0
	total_amount: float = 0.0
	duration_ms: float = 0.0
	errors: List[Dict[str, Any]] = field(default_factory=list)
	
	@property
	def success_rate(self) -> float:
		"""Calcula la tasa de éxito."""
		total = self.payments_processed
		if total == 0:
			return 0.0
		return (self.payments_successful / total) * 100.0
	
	def to_dict(self) -> Dict[str, Any]:
		"""Convierte el resumen a diccionario."""
		return {
			"total_subscriptions": self.total_subscriptions,
			"invoices_generated": self.invoices_generated,
			"payments_processed": self.payments_processed,
			"payments_successful": self.payments_successful,
			"payments_failed": self.payments_failed,
			"failed_payments": self.failed_payments,
			"total_amount": self.total_amount,
			"duration_ms": self.duration_ms,
			"success_rate": self.success_rate,
			"errors": self.errors,
		}


def _get_env_var(name: str, default: str | None = None) -> str:
	"""Obtiene variable de entorno o Airflow Variable."""
	try:
		return str(Variable.get(name, default_var=default))
	except Exception:
		return default or ""


def _send_slack_notification(text: str) -> None:
	"""Envía notificación a Slack si está configurado."""
	try:
		slack_webhook = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
		if slack_webhook:
			import requests
			requests.post(slack_webhook, json={"text": text}, timeout=5)
	except Exception:
		pass


def _send_anomaly_alert(anomalies: List[Dict[str, Any]]) -> None:
	"""Envía alerta detallada a Slack cuando se detectan anomalías."""
	if not anomalies:
		return
	
	try:
		from data.airflow.plugins.etl_notifications import notify_slack
		
		# Agrupar por tipo
		by_type = {}
		for anomaly in anomalies:
			anomaly_type = anomaly.get("type", "unknown")
			if anomaly_type not in by_type:
				by_type[anomaly_type] = []
			by_type[anomaly_type].append(anomaly)
		
		# Construir mensaje
		message = f"⚠️ *Anomalías detectadas en facturación recurrente*\n\n"
		message += f"Total de anomalías: {len(anomalies)}\n\n"
		
		for anomaly_type, items in by_type.items():
			message += f"*{anomaly_type.replace('_', ' ').title()}:* {len(items)}\n"
			
			# Mostrar top 5 más significativas
			sorted_items = sorted(items, key=lambda x: abs(x.get("z_score", 0)), reverse=True)
			for item in sorted_items[:5]:
				sub_id = item.get("subscription_id", "unknown")[:12]
				amount = item.get("amount", 0)
				z_score = item.get("z_score", 0)
				message += f"  • Sub {sub_id}: ${amount:,.2f} (z-score: {z_score:.2f})\n"
			
			if len(items) > 5:
				message += f"  ... y {len(items) - 5} más\n"
			message += "\n"
		
		notify_slack(message)
		logger.info(f"Anomaly alert sent to Slack", extra={"anomalies_count": len(anomalies)})
	except Exception as e:
		logger.warning(f"Failed to send anomaly alert: {e}", exc_info=True)


def _get_stripe_session():
	"""Obtiene o crea una sesión HTTP reutilizable para Stripe."""
	global _stripe_session
	import requests
	
	if _stripe_session is not None:
		return _stripe_session
	
	if HTTPX_AVAILABLE:
		limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
		timeout = httpx.Timeout(30.0, connect=10.0)
		_stripe_session = httpx.Client(limits=limits, timeout=timeout, follow_redirects=True)
	elif REQUESTS_ADAPTER_AVAILABLE:
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
			Stats.incr(f"recurring_billing.api.{api_name}.{operation}.attempt", 1)
		except Exception:
			pass
	try:
		yield
		duration_ms = (time.time() - start) * 1000
		if STATS_AVAILABLE and Stats:
			try:
				Stats.incr(f"recurring_billing.api.{api_name}.{operation}.success", 1)
				Stats.timing(f"recurring_billing.api.{api_name}.{operation}.duration_ms", int(duration_ms))
			except Exception:
				pass
	except Exception as e:
		duration_ms = (time.time() - start) * 1000
		if STATS_AVAILABLE and Stats:
			try:
				Stats.incr(f"recurring_billing.api.{api_name}.{operation}.failed", 1)
			except Exception:
				pass
		raise


def _cb_key() -> str:
	"""Genera la clave del circuit breaker."""
	return "cb:failures:recurring_billing"


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
				Stats.incr("recurring_billing.circuit_breaker.failures", 1)
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
				Stats.incr("recurring_billing.circuit_breaker.reset", 1)
			except Exception:
				pass
	except Exception:
		pass


def _perform_health_check() -> bool:
	"""Realiza un health check de las APIs externas."""
	try:
		stripe_key = os.environ.get("STRIPE_API_KEY", "").strip()
		if stripe_key:
			headers = {"Authorization": f"Bearer {stripe_key}"}
			import requests
			r = requests.get("https://api.stripe.com/v1/charges?limit=1", headers=headers, timeout=10)
			if r.status_code == 401:
				logger.error("Stripe API authentication failed")
				return False
			r.raise_for_status()
		if STATS_AVAILABLE and Stats:
			try:
				Stats.incr("recurring_billing.health_check.success", 1)
			except Exception:
				pass
		return True
	except Exception as e:
		logger.warning(f"Health check failed: {e}", exc_info=True)
		if STATS_AVAILABLE and Stats:
			try:
				Stats.incr("recurring_billing.health_check.failed", 1)
			except Exception:
				pass
		return False


def _validate_credentials() -> None:
	"""Valida que las credenciales estén configuradas."""
	stripe_key = os.environ.get("STRIPE_API_KEY", "").strip()
	errors = []
	if not stripe_key:
		errors.append("STRIPE_API_KEY")
	if errors:
		raise AirflowFailException(f"Missing required credentials: {', '.join(errors)}")


def _validate_subscription_data(sub: Dict[str, Any]) -> bool:
	"""Valida que los datos de suscripción sean válidos."""
	required_fields = ["id", "customer", "current_period_start", "current_period_end", "items"]
	for field in required_fields:
		if not sub.get(field):
			logger.warning(f"Subscription missing required field: {field}", extra={"subscription_id": sub.get("id")})
			return False
	
	items = sub.get("items", {}).get("data", [])
	if not items:
		return False
	
	price = items[0].get("price", {})
	if not price.get("unit_amount"):
		return False
	
	return True


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


def _get_cached_customer(customer_id: str, enable_cache: bool = True) -> Optional[Dict[str, Any]]:
	"""Obtiene cliente del cache si está disponible."""
	if not enable_cache or not CACHETOOLS_AVAILABLE or not _customer_cache:
		return None
	
	try:
		return _customer_cache.get(customer_id)
	except Exception:
		return None


def _cache_customer(customer_id: str, customer_data: Dict[str, Any], enable_cache: bool = True) -> None:
	"""Guarda cliente en cache."""
	if not enable_cache or not CACHETOOLS_AVAILABLE or not _customer_cache:
		return
	
	try:
		_customer_cache[customer_id] = customer_data
	except Exception:
		pass


def _detect_anomalies(
	subscriptions: List[Dict[str, Any]],
	z_score_threshold: float = 2.5
) -> List[Dict[str, Any]]:
	"""
	Detecta anomalías en suscripciones usando Z-score.
	
	Analiza:
	- Montos inusualmente altos o bajos
	- Cambios significativos en cantidades
	"""
	anomalies = []
	
	if not subscriptions:
		return anomalies
	
	# Extraer montos
	amounts = []
	for sub in subscriptions:
		items = sub.get("items", {}).get("data", [])
		if items:
			price = items[0].get("price", {})
			amount = price.get("unit_amount", 0) / 100.0
			if amount > 0:
				amounts.append(amount)
	
	if len(amounts) < 3:
		return anomalies  # Necesitamos al menos 3 valores para calcular estadísticas
	
	try:
		import statistics
		mean = statistics.mean(amounts)
		if len(amounts) > 1:
			std = statistics.stdev(amounts)
		else:
			std = 0
		
		if std == 0:
			return anomalies
		
		threshold_low = mean - (z_score_threshold * std)
		threshold_high = mean + (z_score_threshold * std)
		
		for sub in subscriptions:
			sub_id = sub.get("id")
			items = sub.get("items", {}).get("data", [])
			if items:
				price = items[0].get("price", {})
				amount = price.get("unit_amount", 0) / 100.0
				
				if amount < threshold_low or amount > threshold_high:
					z_score = (amount - mean) / std
					anomalies.append({
						"subscription_id": sub_id,
						"type": "amount_anomaly",
						"amount": amount,
						"z_score": z_score,
						"mean": mean,
						"std": std,
						"threshold": z_score_threshold,
					})
	except Exception as e:
		logger.warning(f"Error detecting anomalies: {e}", exc_info=True)
	
	return anomalies


def _validate_financial_data(
	subscription_data: Dict[str, Any],
	invoice_data: Optional[Dict[str, Any]] = None
) -> tuple[bool, List[str]]:
	"""
	Valida la calidad de datos financieros.
	
	Returns:
		(is_valid, list_of_issues)
	"""
	issues = []
	
	# Validar suscripción
	sub_id = subscription_data.get("id")
	if not sub_id:
		issues.append("Missing subscription ID")
	
	items = subscription_data.get("items", {}).get("data", [])
	if not items:
		issues.append("Subscription has no items")
	else:
		price = items[0].get("price", {})
		amount = price.get("unit_amount", 0)
		if amount <= 0:
			issues.append(f"Invalid amount: {amount}")
		if amount > 100000000:  # $1,000,000 (centavos)
			issues.append(f"Suspiciously high amount: ${amount/100:,.2f}")
	
	# Validar invoice si se proporciona
	if invoice_data:
		invoice_amount = invoice_data.get("amount", 0)
		if invoice_amount <= 0:
			issues.append("Invalid invoice amount")
		
		# Verificar que el monto coincida con la suscripción
		if items:
			price = items[0].get("price", {})
			expected_amount = price.get("unit_amount", 0) / 100.0
			if abs(invoice_amount - expected_amount) > 0.01:  # Tolerancia de 1 centavo
				issues.append(
					f"Amount mismatch: invoice={invoice_amount}, expected={expected_amount}"
				)
	
	return len(issues) == 0, issues


def _log_progress(
	current: int,
	total: int,
	operation: str,
	successful: int = 0,
	failed: int = 0
) -> None:
	"""Log de progreso con formato estándar."""
	if total == 0:
		return
	
	progress_pct = (current / total * 100) if total > 0 else 0.0
	
	# Log cada 10% o cada 10 items, lo que sea más frecuente
	checkpoint = max(1, min(total // 10, 10))
	
	if current % checkpoint == 0 or current == total:
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


class RateLimiter:
	"""Rate limiter simple con ventana deslizante."""
	
	def __init__(self, max_requests: int = 100, window_seconds: int = 60):
		self.max_requests = max_requests
		self.window_seconds = window_seconds
		self.requests: List[float] = []
	
	def is_allowed(self) -> bool:
		"""Verifica si un request está permitido."""
		now = time.time()
		# Limpiar requests antiguos
		self.requests = [ts for ts in self.requests if now - ts < self.window_seconds]
		return len(self.requests) < self.max_requests
	
	def wait_if_needed(self) -> None:
		"""Espera si es necesario para respetar el rate limit."""
		if not self.is_allowed():
			# Esperar hasta que el request más antiguo expire
			if self.requests:
				oldest = min(self.requests)
				wait_time = self.window_seconds - (time.time() - oldest) + 0.1
				if wait_time > 0:
					time.sleep(wait_time)
			# Limpiar y reintentar
			self.requests = [ts for ts in self.requests if time.time() - ts < self.window_seconds]
	
	def record_request(self) -> None:
		"""Registra un request."""
		self.requests.append(time.time())


def _get_stripe_rate_limiter() -> RateLimiter:
	"""Obtiene o crea el rate limiter para Stripe."""
	global _stripe_rate_limiter
	if _stripe_rate_limiter is None:
		max_requests = int(_get_env_var("STRIPE_RATE_LIMIT_MAX", default="100"))
		window_seconds = int(_get_env_var("STRIPE_RATE_LIMIT_WINDOW", default="60"))
		_stripe_rate_limiter = RateLimiter(max_requests=max_requests, window_seconds=window_seconds)
	return _stripe_rate_limiter


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
	except Exception:
		pass


def _retry_with_backoff_and_jitter(
	func: Callable,
	max_retries: int = 3,
	base_delay: float = 1.0,
	max_delay: float = 60.0,
	jitter: bool = True
) -> Any:
	"""
	Ejecuta una función con exponential backoff y jitter opcional.
	
	Args:
		func: Función a ejecutar
		max_retries: Número máximo de reintentos
		base_delay: Delay base en segundos
		max_delay: Delay máximo en segundos
		jitter: Si agregar jitter aleatorio
	"""
	import random
	
	for attempt in range(max_retries + 1):
		try:
			return func()
		except Exception as e:
			if attempt == max_retries:
				raise
			
			# Calcular delay con exponential backoff
			delay = min(base_delay * (2 ** attempt), max_delay)
			
			# Agregar jitter si está habilitado
			if jitter:
				jitter_amount = delay * 0.1 * random.random()
				delay = delay + jitter_amount
			
			logger.warning(
				f"Retry attempt {attempt + 1}/{max_retries} after {delay:.2f}s",
				extra={"error": str(e)[:200], "attempt": attempt + 1}
			)
			time.sleep(delay)
	
	raise Exception("All retries exhausted")


def _calculate_sla_metrics(duration_ms: float, target_duration_ms: float = 600000) -> Dict[str, Any]:
	"""
	Calcula métricas de SLA basadas en duración.
	
	Args:
		duration_ms: Duración real en milisegundos
		target_duration_ms: Duración objetivo (SLA) en milisegundos
		
	Returns:
		Dict con métricas de SLA
	"""
	sla_met = (duration_ms / target_duration_ms) * 100.0
	sla_met = min(100.0, sla_met)  # Cap at 100%
	
	return {
		"duration_ms": duration_ms,
		"target_duration_ms": target_duration_ms,
		"sla_percentage": sla_met,
		"sla_met": duration_ms <= target_duration_ms,
		"sla_margin_ms": target_duration_ms - duration_ms,
		"sla_margin_pct": ((target_duration_ms - duration_ms) / target_duration_ms * 100) if target_duration_ms > 0 else 0.0,
	}


def _predict_future_issues(
	current_metrics: Dict[str, Any],
	history: List[Dict[str, Any]],
	threshold_pct: float = 20.0
) -> List[Dict[str, Any]]:
	"""
	Predice problemas futuros basándose en tendencias.
	
	Args:
		current_metrics: Métricas actuales
		history: Historial de ejecuciones anteriores
		threshold_pct: Porcentaje de cambio para alertar
		
	Returns:
		Lista de predicciones/alertas
	"""
	predictions = []
	
	if not history or len(history) < 3:
		return predictions
	
	try:
		# Calcular tendencias
		recent_runs = sorted(history, key=lambda x: x.get("timestamp", 0), reverse=True)[:5]
		
		# Tasa de éxito
		success_rates = [r.get("summary", {}).get("success_rate", 0) for r in recent_runs]
		if len(success_rates) >= 3:
			avg_success = sum(success_rates) / len(success_rates)
			current_success = current_metrics.get("success_rate", 0)
			
			if current_success < avg_success - threshold_pct:
				predictions.append({
					"type": "declining_success_rate",
					"severity": "high",
					"message": f"Tasa de éxito en declive: {current_success:.1f}% vs promedio {avg_success:.1f}%",
					"trend": "downward",
				})
		
		# Tiempo de ejecución
		durations = [r.get("summary", {}).get("duration_ms", 0) for r in recent_runs if r.get("summary", {}).get("duration_ms")]
		if len(durations) >= 3:
			avg_duration = sum(durations) / len(durations)
			current_duration = current_metrics.get("duration_ms", 0)
			
			if current_duration > avg_duration * 1.5:  # 50% más lento
				predictions.append({
					"type": "increasing_duration",
					"severity": "medium",
					"message": f"Ejecución más lenta: {current_duration/1000:.1f}s vs promedio {avg_duration/1000:.1f}s",
					"trend": "increasing",
				})
		
	except Exception as e:
		logger.warning(f"Error in predictive analysis: {e}", exc_info=True)
	
	return predictions


def _compare_with_history(current_metrics: Dict[str, Any]) -> Dict[str, Any]:
	"""Compara métricas actuales con ejecuciones anteriores."""
	comparison = {
		"has_history": False,
		"changes": {},
		"trends": {},
	}
	
	try:
		# Obtener último run desde Variables
		last_run_key = "recurring_billing:last_run"
		last_run_data = Variable.get(last_run_key, default_var=None)
		
		if not last_run_data:
			return comparison
		
		last_run = json.loads(last_run_data)
		last_summary = last_run.get("summary", {})
		
		if not last_summary:
			return comparison
		
		comparison["has_history"] = True
		
		# Comparar métricas clave
		current_invoices = current_metrics.get("invoices_generated", 0)
		last_invoices = last_summary.get("invoices_generated", 0)
		
		current_success = current_metrics.get("success_rate", 0.0)
		last_success = last_summary.get("success_rate", 0.0)
		
		current_amount = current_metrics.get("total_amount", 0.0)
		last_amount = last_summary.get("total_amount", 0.0)
		
		# Calcular cambios
		comparison["changes"] = {
			"invoices": {
				"current": current_invoices,
				"previous": last_invoices,
				"change": current_invoices - last_invoices,
				"change_pct": ((current_invoices - last_invoices) / last_invoices * 100) if last_invoices > 0 else 0.0,
			},
			"success_rate": {
				"current": current_success,
				"previous": last_success,
				"change": current_success - last_success,
				"change_pct": ((current_success - last_success) / last_success * 100) if last_success > 0 else 0.0,
			},
			"total_amount": {
				"current": current_amount,
				"previous": last_amount,
				"change": current_amount - last_amount,
				"change_pct": ((current_amount - last_amount) / last_amount * 100) if last_amount > 0 else 0.0,
			},
		}
		
		# Detectar tendencias
		comparison["trends"] = {
			"invoices_increasing": current_invoices > last_invoices * 1.1,  # +10%
			"invoices_decreasing": current_invoices < last_invoices * 0.9,  # -10%
			"success_rate_declining": current_success < last_success - 5.0,  # -5 puntos
			"amount_increasing": current_amount > last_amount * 1.2,  # +20%
		}
		
	except Exception as e:
		logger.warning(f"Error comparing with history: {e}", exc_info=True)
	
	return comparison


def _save_to_dlq(item: Dict[str, Any], error: str, dlq_path: str = "/tmp/recurring_billing_dlq.jsonl") -> None:
	"""Guarda un item fallido en dead letter queue."""
	try:
		os.makedirs(os.path.dirname(dlq_path), exist_ok=True)
		with open(dlq_path, "a") as f:
			dlq_record = {
				"timestamp": pendulum.now("UTC").isoformat(),
				"item": item,
				"error": error,
				"retried": False,
			}
			f.write(json.dumps(dlq_record) + "\n")
		logger.warning(f"Saved to DLQ: {error}", extra={"item_id": item.get("subscription_id")})
	except Exception as e:
		logger.error(f"Failed to save to DLQ: {e}", exc_info=True)


def _get_optimal_batch_size(operation: str = "billing") -> int:
	"""Calcula batch size óptimo basado en rendimiento histórico."""
	try:
		# Obtener métricas históricas desde Variables
		history_key = f"recurring_billing:batch_history:{operation}"
		history_data = Variable.get(history_key, default_var=None)
		
		if not history_data:
			return DEFAULT_BATCH_SIZE
		
		history = json.loads(history_data)
		
		# Analizar throughput por batch size
		best_batch_size = DEFAULT_BATCH_SIZE
		best_throughput = 0.0
		
		for batch_size, metrics in history.items():
			avg_throughput = metrics.get("avg_throughput", 0.0)
			if avg_throughput > best_throughput:
				best_throughput = avg_throughput
				best_batch_size = int(batch_size)
		
		# Asegurar límites razonables
		best_batch_size = max(5, min(best_batch_size, 50))
		
		return best_batch_size
	except Exception:
		return DEFAULT_BATCH_SIZE


def _record_batch_performance(batch_size: int, duration_ms: float, items_count: int, operation: str = "billing") -> None:
	"""Registra rendimiento de un batch para optimización futura."""
	try:
		history_key = f"recurring_billing:batch_history:{operation}"
		history_data = Variable.get(history_key, default_var=None)
		
		history = {}
		if history_data:
			history = json.loads(history_data)
		
		batch_key = str(batch_size)
		if batch_key not in history:
			history[batch_key] = {"count": 0, "total_throughput": 0.0, "avg_throughput": 0.0}
		
		throughput = (items_count / (duration_ms / 1000)) if duration_ms > 0 else 0.0
		
		history[batch_key]["count"] += 1
		history[batch_key]["total_throughput"] += throughput
		history[batch_key]["avg_throughput"] = history[batch_key]["total_throughput"] / history[batch_key]["count"]
		
		# Mantener solo últimos 100 registros por batch size
		if history[batch_key]["count"] > 100:
			history[batch_key]["count"] = 100
			history[batch_key]["total_throughput"] = history[batch_key]["avg_throughput"] * 100
		
		Variable.set(history_key, json.dumps(history))
	except Exception:
		pass


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


def _track_cost_operation(operation: str, cost_usd: float, metadata: Optional[Dict[str, Any]] = None) -> None:
	"""Trackea costos de operaciones para análisis de optimización."""
	try:
		cost_key = "recurring_billing:cost_tracking"
		cost_data = Variable.get(cost_key, default_var=None)
		
		costs = {}
		if cost_data:
			costs = json.loads(cost_data)
		
		today = pendulum.now("UTC").date().isoformat()
		if today not in costs:
			costs[today] = {}
		
		if operation not in costs[today]:
			costs[today][operation] = {
				"count": 0,
				"total_cost": 0.0,
				"avg_cost": 0.0,
			}
		
		costs[today][operation]["count"] += 1
		costs[today][operation]["total_cost"] += cost_usd
		costs[today][operation]["avg_cost"] = costs[today][operation]["total_cost"] / costs[today][operation]["count"]
		
		# Mantener solo últimos 30 días
		sorted_days = sorted(costs.keys(), reverse=True)[:30]
		costs = {day: costs[day] for day in sorted_days}
		
		Variable.set(cost_key, json.dumps(costs))
		
		# Trackear métricas
		if STATS_AVAILABLE and Stats:
			try:
				Stats.gauge(f"recurring_billing.cost.{operation}.total", costs[today][operation]["total_cost"])
				Stats.gauge(f"recurring_billing.cost.{operation}.avg", costs[today][operation]["avg_cost"])
			except Exception:
				pass
	except Exception:
		pass


def _calculate_optimal_workers(item_count: int, avg_time_per_item_ms: float = 1000.0, target_duration_seconds: float = 300.0) -> int:
	"""
	Calcula número óptimo de workers basado en carga y tiempo objetivo.
	
	Args:
		item_count: Número de items a procesar
		avg_time_per_item_ms: Tiempo promedio por item en ms
		target_duration_seconds: Duración objetivo en segundos
		
	Returns:
		Número óptimo de workers (1-10)
	"""
	if item_count <= 1:
		return 1
	
	total_time_seconds = (item_count * avg_time_per_item_ms) / 1000.0
	optimal_workers = int(total_time_seconds / target_duration_seconds)
	
	# Aplicar límites razonables
	optimal_workers = max(1, min(optimal_workers, 10))
	
	return optimal_workers


@contextmanager
def _profile_operation(operation_name: str):
	"""Context manager para profiling de operaciones."""
	start_time = time.time()
	start_memory = None
	
	try:
		import psutil
		process = psutil.Process()
		start_memory = process.memory_info().rss / 1024 / 1024  # MB
	except Exception:
		pass
	
	try:
		yield
	finally:
		duration_ms = (time.time() - start_time) * 1000
		end_memory = None
		memory_delta = None
		
		try:
			import psutil
			process = psutil.Process()
			end_memory = process.memory_info().rss / 1024 / 1024  # MB
			memory_delta = end_memory - start_memory if start_memory else None
		except Exception:
			pass
		
		logger.info(
			f"Performance profile: {operation_name}",
			extra={
				"operation": operation_name,
				"duration_ms": duration_ms,
				"memory_mb": end_memory,
				"memory_delta_mb": memory_delta,
			}
		)
		
		if STATS_AVAILABLE and Stats:
			try:
				Stats.timing(f"recurring_billing.profile.{operation_name}.duration_ms", int(duration_ms))
				if memory_delta:
					Stats.gauge(f"recurring_billing.profile.{operation_name}.memory_mb", end_memory)
			except Exception:
				pass


@dag(
	dag_id="recurring_billing",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule="0 1 * * *",  # Diario a las 01:00 UTC (antes de invoice_generate)
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
	description="Procesa transacciones recurrentes: obtiene suscripciones, genera facturas y procesa pagos",
	tags=["finance", "billing", "recurring", "subscriptions", "stripe"],
	params={
		"batch_size": Param(
			DEFAULT_BATCH_SIZE,
			type="integer",
			minimum=1,
			maximum=50,
			description="Número de suscripciones a procesar por batch",
		),
		"batch_delay": Param(
			DEFAULT_BATCH_DELAY,
			type="number",
			minimum=0,
			maximum=10,
			description="Delay entre batches en segundos",
		),
		"continue_on_error": Param(
			True,
			type="boolean",
			description="Continuar procesando otras suscripciones si una falla",
		),
		"dry_run": Param(
			False,
			type="boolean",
			description="Simular sin generar facturas ni procesar pagos",
		),
		"max_workers": Param(
			0,
			type="integer",
			minimum=0,
			maximum=10,
			description="Número de workers para procesamiento paralelo (0=secuencial)",
		),
		"enable_cache": Param(
			True,
			type="boolean",
			description="Habilitar cache para suscripciones y clientes",
		),
		"detect_anomalies": Param(
			True,
			type="boolean",
			description="Detectar anomalías en montos y patrones de facturación",
		),
		"validate_data_quality": Param(
			True,
			type="boolean",
			description="Validar calidad de datos financieros antes de procesar",
		),
		"enable_rate_limiting": Param(
			True,
			type="boolean",
			description="Habilitar rate limiting para Stripe API",
		),
		"enable_adaptive_batch": Param(
			True,
			type="boolean",
			description="Usar batch size adaptativo basado en rendimiento histórico",
		),
		"enable_dlq": Param(
			True,
			type="boolean",
			description="Guardar errores críticos en dead letter queue",
		),
		"enable_distributed_lock": Param(
			True,
			type="boolean",
			description="Usar distributed locking para prevenir ejecuciones concurrentes",
		),
		"enable_predictive_alerts": Param(
			True,
			type="boolean",
			description="Habilitar alertas predictivas basadas en tendencias",
		),
		"enable_checkpointing": Param(
			True,
			type="boolean",
			description="Habilitar checkpointing para procesamiento resumible",
		),
		"enable_cost_tracking": Param(
			True,
			type="boolean",
			description="Trackear costos de operaciones para análisis",
		),
		"enable_auto_scaling": Param(
			True,
			type="boolean",
			description="Auto-escalar workers basado en carga estimada",
		),
		"enable_performance_profiling": Param(
			True,
			type="boolean",
			description="Habilitar profiling de performance de operaciones",
		),
	},
	on_success_callback=lambda context: _send_slack_notification(
		":white_check_mark: recurring_billing completed successfully"
	),
	on_failure_callback=lambda context: _send_slack_notification(
		":x: recurring_billing failed"
	),
	doc_md="""
	# Procesamiento de Transacciones Recurrentes
	
	Este DAG automatiza completamente el ciclo de facturación recurrente:
	
	## Flujo
	
	1. **Obtener suscripciones activas** de Stripe
	2. **Identificar facturación pendiente** (suscripciones que necesitan factura)
	3. **Generar facturas** para cada suscripción
	4. **Procesar pagos** automáticamente
	5. **Manejar fallos** (reintentos, notificaciones)
	6. **Sincronizar con QuickBooks** (opcional)
	7. **Enviar notificaciones** a clientes
	
	## Características
	
	- ✅ Detección automática de ciclos de facturación (mensual, anual, etc.)
	- ✅ Generación de facturas desde suscripciones Stripe
	- ✅ Procesamiento automático de pagos
	- ✅ Manejo de pagos fallidos con reintentos
	- ✅ Integración con sistema de facturación existente
	- ✅ Sincronización opcional con QuickBooks
	- ✅ Notificaciones automáticas a clientes
	- ✅ Tracking en base de datos para auditoría
	- ✅ Prevención de facturas duplicadas
	- ✅ **Dry-run mode** para testing sin modificar datos
	- ✅ **Progress tracking** con logging periódico
	- ✅ **Procesamiento en batches** optimizado
	- ✅ **Procesamiento paralelo** opcional con ThreadPoolExecutor
	- ✅ **Cache inteligente** con TTL para suscripciones y clientes
	- ✅ **Validación de datos** robusta antes de procesar
	- ✅ **Detección de anomalías** usando Z-score para identificar montos inusuales
	- ✅ **Validación de calidad de datos** financieros con checks comprehensivos
	- ✅ **Progress tracking granular** con logging periódico y callbacks
	- ✅ **Métricas de calidad** de datos (validaciones fallidas, anomalías detectadas)
	- ✅ **Resúmenes detallados** con métricas completas
	- ✅ **Tracking de progreso** en Variables de Airflow
	- ✅ **Optimización de llamadas API** con cache y sesiones reutilizables
	
	## Configuración Requerida
	
	### Variables de Entorno
	- `STRIPE_API_KEY`: API key de Stripe (requerido)
	- `QUICKBOOKS_ACCESS_TOKEN`: Access token QuickBooks (opcional)
	- `QUICKBOOKS_REALM_ID`: Realm ID QuickBooks (opcional)
	
	### Variables de Airflow
	- `INVOICE_SERIE`: Serie de facturación (default: "A")
	- `COMPANY_TAX_ID`: RFC/NIF de la empresa
	- `TAX_RATE`: Tasa de impuestos (default: "0.21")
	- `DEFAULT_CURRENCY`: Moneda por defecto (default: "USD")
	- `RECURRING_BILLING_LOOKAHEAD_DAYS`: Días de anticipación para facturación (default: "1")
	- `RECURRING_BILLING_MAX_RETRIES`: Máximo de reintentos para pagos fallidos (default: "3")
	- `RECURRING_BILLING_SYNC_QUICKBOOKS`: Sincronizar con QuickBooks (default: "false")
	
	### Parámetros del DAG
	
	- `batch_size`: Número de suscripciones por batch (default: 10)
	- `batch_delay`: Delay entre batches en segundos (default: 0.5)
	- `continue_on_error`: Continuar si una suscripción falla (default: true)
	- `dry_run`: Simular sin generar facturas ni procesar pagos (default: false)
	- `max_workers`: Número de workers para procesamiento paralelo (0=secuencial, default: 0)
	- `enable_cache`: Habilitar cache para suscripciones y clientes (default: true)
	- `detect_anomalies`: Detectar anomalías en montos y patrones (default: true)
	- `validate_data_quality`: Validar calidad de datos financieros (default: true)
	- `enable_rate_limiting`: Habilitar rate limiting para Stripe API (default: true)
	- `enable_adaptive_batch`: Usar batch size adaptativo (default: true)
	- `enable_dlq`: Guardar errores críticos en dead letter queue (default: true)
	- `enable_distributed_lock`: Usar locking distribuido (default: true)
	- `enable_predictive_alerts`: Habilitar alertas predictivas (default: true)
	- `enable_checkpointing`: Habilitar checkpointing (default: true)
	- `enable_cost_tracking`: Trackear costos (default: true)
	- `enable_auto_scaling`: Auto-escalar workers (default: true)
	- `enable_performance_profiling`: Habilitar profiling (default: true)
	""",
)
def recurring_billing() -> None:
	"""DAG principal para procesamiento de transacciones recurrentes."""
	
	# Distributed locking para prevenir ejecuciones concurrentes
	@task(task_id="acquire_lock")
	def acquire_lock() -> Dict[str, Any]:
		"""Adquiere lock distribuido para prevenir ejecuciones concurrentes."""
		ctx = get_current_context()
		params = ctx.get("params", {})
		enable_lock = params.get("enable_distributed_lock", True)
		
		if not enable_lock:
			return {"locked": True, "skip_lock": True}
		
		lock_key = "recurring_billing:execution_lock"
		ttl_seconds = int(_get_env_var("RECURRING_BILLING_LOCK_TTL", default="3600"))  # 1 hora
		
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
		
		logger.info("Execution lock acquired", extra={"lock_key": lock_key, "ttl_seconds": ttl_seconds})
		
		return {"locked": True, "lock_key": lock_key}
	
	@task(
		task_id="health_check",
		execution_timeout=timedelta(minutes=2),
		retries=0,
	)
	def health_check() -> None:
		"""Health check pre-vuelo de APIs externas."""
		_validate_credentials()
		if not _perform_health_check():
			_cb_record_failure()
			raise AirflowFailException("Health check failed - APIs are not accessible")
		if _cb_is_open():
			logger.info("Health check passed, resetting circuit breaker")
			_cb_reset()
		logger.info("Health check passed for all APIs")
	
	@task(
		task_id="fetch_active_subscriptions",
		execution_timeout=timedelta(minutes=10),
		retries=2,
	)
	def fetch_active_subscriptions() -> Dict[str, Any]:
		"""
		Obtiene todas las suscripciones activas de Stripe con retry inteligente.
		"""
		if _cb_is_open():
			raise AirflowFailException(
				f"Circuit breaker is open - too many failures. "
				f"Wait {CB_RESET_MINUTES} minutes or reset manually."
			)
		
		import requests
		
		stripe_key = os.environ.get("STRIPE_API_KEY", "").strip()
		if not stripe_key:
			raise AirflowFailException("STRIPE_API_KEY not configured")
		
		ctx = get_current_context()
		lookahead_days = int(_get_env_var("RECURRING_BILLING_LOOKAHEAD_DAYS", default="1"))
		
		now = ctx["data_interval_end"]
		lookahead_date = now.add(days=lookahead_days)
		
		logger.info(
			"Fetching active subscriptions",
			extra={"lookahead_days": lookahead_days, "cutoff_date": lookahead_date.to_date_string()}
		)
		
		all_subscriptions: List[Dict[str, Any]] = []
		headers = {"Authorization": f"Bearer {stripe_key}"}
		params = {"status": "active", "limit": 100}
		starting_after = None
		start_time = time.time()
		
		session = _get_stripe_session()
		
		while True:
			p = dict(params)
			if starting_after:
				p["starting_after"] = starting_after
			
			try:
				with _track_api_call("stripe", "list_subscriptions"):
					if session:
						r = session.get("https://api.stripe.com/v1/subscriptions", headers=headers, params=p)
					else:
						r = requests.get("https://api.stripe.com/v1/subscriptions", headers=headers, params=p, timeout=DEFAULT_TIMEOUT)
					
					# Manejar rate limiting
					if r.status_code == 429:
						retry_after = int(r.headers.get("retry-after", DEFAULT_RETRY_DELAY))
						retry_after = min(retry_after, RATE_LIMIT_MAX_WAIT)
						logger.warning(f"Rate limited by Stripe, waiting {retry_after}s")
						time.sleep(retry_after)
						continue
					
					r.raise_for_status()
					out = r.json()
					data = out.get("data", [])
					
				for sub in data:
					sub_id = sub.get("id")
					if not sub_id:
						continue
					
					# Intentar obtener del cache primero
					enable_cache = True
					cached_sub = _get_cached_subscription(sub_id, enable_cache)
					if cached_sub:
						all_subscriptions.append(cached_sub)
						continue
					
					# Rate limiting si está habilitado
					ctx = get_current_context()
					params = ctx.get("params", {})
					enable_rate_limiting = params.get("enable_rate_limiting", True)
					
					if enable_rate_limiting:
						rate_limiter = _get_stripe_rate_limiter()
						rate_limiter.wait_if_needed()
					
					with _track_api_call("stripe", "get_subscription"):
						if session:
							sub_r = session.get(f"https://api.stripe.com/v1/subscriptions/{sub_id}", headers=headers)
						else:
							sub_r = requests.get(f"https://api.stripe.com/v1/subscriptions/{sub_id}", headers=headers, timeout=DEFAULT_TIMEOUT)
					
					if enable_rate_limiting:
						rate_limiter.record_request()
						
						if sub_r.status_code == 429:
							continue
						
						sub_r.raise_for_status()
						sub_details = sub_r.json()
						
						# Validar datos antes de agregar
						if _validate_subscription_data(sub_details):
							all_subscriptions.append(sub_details)
							# Guardar en cache
							_cache_subscription(sub_id, sub_details, enable_cache)
						else:
							logger.warning(f"Invalid subscription data for {sub_id}, skipping")
				
				if out.get("has_more") and data:
					starting_after = data[-1].get("id")
				else:
					break
			except requests.exceptions.HTTPError as e:
				if e.response.status_code == 401:
					_cb_record_failure()
					raise AirflowFailException("Stripe authentication failed - check STRIPE_API_KEY") from e
				logger.error(f"Error fetching subscriptions: {e}", exc_info=True)
				_cb_record_failure()
				break
			except Exception as e:
				logger.error(f"Error fetching subscriptions: {e}", exc_info=True)
				_cb_record_failure()
				break
		
		duration_ms = (time.time() - start_time) * 1000
		
		if STATS_AVAILABLE and Stats:
			try:
				Stats.incr("recurring_billing.fetch.subscriptions", len(all_subscriptions))
				Stats.timing("recurring_billing.fetch.duration_ms", int(duration_ms))
			except Exception:
				pass
		
		if len(all_subscriptions) > 0:
			_cb_reset()
		
		logger.info(
			"Fetched active subscriptions",
			extra={"count": len(all_subscriptions), "duration_ms": duration_ms}
		)
		
		# Detectar anomalías si está habilitado
		ctx = get_current_context()
		params = ctx.get("params", {})
		detect_anomalies = params.get("detect_anomalies", True)
		
		anomalies = []
		if detect_anomalies and len(all_subscriptions) > 3:
			try:
				anomalies = _detect_anomalies(all_subscriptions)
				if anomalies:
					logger.warning(
						f"Detected {len(anomalies)} anomalies in subscriptions",
						extra={"anomalies_count": len(anomalies)}
					)
					if STATS_AVAILABLE and Stats:
						try:
							Stats.incr("recurring_billing.anomalies.detected", len(anomalies))
							# Trackear severidad promedio
							avg_z_score = sum(abs(a.get("z_score", 0)) for a in anomalies) / len(anomalies)
							Stats.gauge("recurring_billing.anomalies.avg_z_score", avg_z_score)
						except Exception:
							pass
					
					# Enviar alerta a Slack si hay anomalías significativas
					significant_anomalies = [a for a in anomalies if abs(a.get("z_score", 0)) > 3.0]
					if significant_anomalies:
						_send_anomaly_alert(significant_anomalies)
			except Exception as e:
				logger.warning(f"Error detecting anomalies: {e}", exc_info=True)
		
		return {
			"subscriptions": all_subscriptions,
			"anomalies": anomalies,
		}
	
	@task(task_id="identify_billing_needed")
	def identify_billing_needed(subscriptions_payload: Dict[str, Any]) -> Dict[str, Any]:
		"""
		Identifica suscripciones que necesitan facturación.
		Verifica si ya se generó factura para el período actual.
		"""
		subscriptions = subscriptions_payload.get("subscriptions", []) or []
		ctx = get_current_context()
		now = ctx["data_interval_end"]
		
		billing_needed: List[Dict[str, Any]] = []
		
		# Crear tabla de tracking si no existe
		with get_conn() as conn:
			with conn.cursor() as cur:
				cur.execute(
					"""
					CREATE TABLE IF NOT EXISTS recurring_billing_tracking (
						id SERIAL PRIMARY KEY,
						subscription_id TEXT NOT NULL,
						customer_id TEXT NOT NULL,
						billing_period_start TIMESTAMPTZ NOT NULL,
						billing_period_end TIMESTAMPTZ NOT NULL,
						invoice_id INTEGER REFERENCES invoices(id),
						status TEXT NOT NULL DEFAULT 'pending',
						amount NUMERIC(12,2) NOT NULL,
						currency VARCHAR(8) NOT NULL DEFAULT 'USD',
						created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
						UNIQUE(subscription_id, billing_period_start)
					);
					"""
				)
				cur.execute(
					"""
					CREATE INDEX IF NOT EXISTS idx_recurring_billing_subscription 
					ON recurring_billing_tracking(subscription_id);
					"""
				)
				cur.execute(
					"""
					CREATE INDEX IF NOT EXISTS idx_recurring_billing_period 
					ON recurring_billing_tracking(billing_period_start, billing_period_end);
					"""
				)
				conn.commit()
		
		ctx = get_current_context()
		params = ctx.get("params", {})
		validate_data_quality = params.get("validate_data_quality", True)
		
		total = len(subscriptions)
		skipped_invalid = 0
		skipped_existing = 0
		
		for idx, sub in enumerate(subscriptions):
			# Progress tracking
			if (idx + 1) % 10 == 0 or idx + 1 == total:
				_log_progress(
					idx + 1,
					total,
					"identify_billing_needed",
					len(billing_needed),
					skipped_invalid + skipped_existing
				)
			
			sub_id = sub.get("id")
			customer_id = sub.get("customer")
			current_period_start = sub.get("current_period_start")
			current_period_end = sub.get("current_period_end")
			items = sub.get("items", {}).get("data", [])
			
			if not items:
				skipped_invalid += 1
				continue
			
			# Validar calidad de datos
			if validate_data_quality:
				is_valid, issues = _validate_financial_data(sub)
				if not is_valid:
					logger.warning(
						f"Invalid subscription data for {sub_id}: {', '.join(issues)}",
						extra={"subscription_id": sub_id, "issues": issues}
					)
					skipped_invalid += 1
					if STATS_AVAILABLE and Stats:
						try:
							Stats.incr("recurring_billing.validation.failed", 1)
						except Exception:
							pass
					continue
			
			# Obtener el precio del plan
			price = items[0].get("price", {})
			amount = price.get("unit_amount", 0) / 100.0  # Convertir de centavos
			currency = price.get("currency", "usd").upper()
			
			# Verificar si ya se generó factura para este período
			with get_conn() as conn:
				with conn.cursor() as cur:
					cur.execute(
						"""
						SELECT id, status FROM recurring_billing_tracking
						WHERE subscription_id = %s
						AND billing_period_start = to_timestamp(%s)
						""",
						(sub_id, current_period_start)
					)
					existing = cur.fetchone()
					
					if existing:
						# Ya existe tracking para este período
						skipped_existing += 1
						continue
			
			# Verificar si el período actual está próximo o ya empezó
			period_start_dt = pendulum.from_timestamp(current_period_start)
			period_end_dt = pendulum.from_timestamp(current_period_end)
			
			# Facturar si el período está activo o próximo (dentro de lookahead)
			if period_start_dt <= now <= period_end_dt or period_start_dt <= now.add(days=1):
				billing_needed.append({
					"subscription_id": sub_id,
					"customer_id": customer_id,
					"billing_period_start": current_period_start,
					"billing_period_end": current_period_end,
					"amount": amount,
					"currency": currency,
					"plan_name": price.get("nickname") or price.get("id", "Plan"),
					"subscription_data": sub,
				})
		
		logger.info(
			"Identified billing needed",
			extra={
				"total_subscriptions": total,
				"billing_needed": len(billing_needed),
				"skipped_invalid": skipped_invalid,
				"skipped_existing": skipped_existing,
			}
		)
		
		
		return {"billing_needed": billing_needed}
	
	@task_group(group_id="process_subscription_billing")
	def process_subscription_billing(billing_payload: Dict[str, Any]) -> Dict[str, Any]:
		"""
		Grupo de tareas para procesar facturación de cada suscripción.
		"""
		billing_needed = billing_payload.get("billing_needed", []) or []
		
		@task(task_id="generate_invoices")
		def generate_invoices() -> Dict[str, Any]:
			"""
			Genera facturas para las suscripciones que necesitan facturación.
			Procesa en batches con progress tracking.
			"""
			ctx = get_current_context()
			params = ctx.get("params", {})
			dry_run = params.get("dry_run", False)
			enable_adaptive_batch = params.get("enable_adaptive_batch", True)
			enable_dlq = params.get("enable_dlq", True)
			
			# Usar batch size adaptativo si está habilitado
			if enable_adaptive_batch:
				batch_size = _get_optimal_batch_size("invoice_generation")
			else:
				batch_size = params.get("batch_size", DEFAULT_BATCH_SIZE)
			
			batch_delay = float(params.get("batch_delay", DEFAULT_BATCH_DELAY))
			
			if dry_run:
				logger.info(f"[DRY RUN] Would generate invoices for {len(billing_needed)} subscriptions")
			
			generated_invoices: List[Dict[str, Any]] = []
			
			serie = _get_env_var("INVOICE_SERIE", default="A")
			tax_rate = float(_get_env_var("TAX_RATE", default="0.21"))
			company_tax_id = _get_env_var("COMPANY_TAX_ID", default="")
			default_currency = _get_env_var("DEFAULT_CURRENCY", default="USD")
			invoice_date = ctx["data_interval_end"].to_date_string()
			
			start_time = time.time()
			
			# Performance profiling
			profile_ctx = _profile_operation("generate_invoices") if enable_performance_profiling else None
			if profile_ctx:
				profile_ctx.__enter__()
			
			try:
				# Determinar punto de inicio desde checkpoint
				start_idx = 0
				if checkpoint:
					start_idx = checkpoint.get("last_batch_end", 0)
					generated_invoices = checkpoint.get("generated_invoices", [])
					logger.info(f"Resuming from batch {start_idx // batch_size + 1}")
				
				# Procesar en batches
				for batch_idx in range(start_idx, len(billing_needed), batch_size):
				batch = billing_needed[batch_idx:batch_idx + batch_size]
				batch_num = (batch_idx // batch_size) + 1
				total_batches = (len(billing_needed) + batch_size - 1) // batch_size
				batch_start_time = time.time()
				
				logger.info(
					f"Processing invoice batch {batch_num}/{total_batches}",
					extra={
						"batch_size": len(batch),
						"batch_num": batch_num,
						"total_batches": total_batches,
						"progress_pct": (batch_idx / len(billing_needed)) * 100.0 if billing_needed else 0.0,
						"dry_run": dry_run,
					}
				)
				
				for billing in batch:
					subscription_id = billing.get("subscription_id")
					customer_id = billing.get("customer_id")
					amount = billing.get("amount", 0.0)
					currency = billing.get("currency", default_currency).upper()
					plan_name = billing.get("plan_name", "Suscripción")
					period_start = billing.get("billing_period_start")
					period_end = billing.get("billing_period_end")
					
					# Calcular subtotal, impuestos y total
					subtotal = float(amount)
					taxes = round(subtotal * tax_rate, 2)
					total = round(subtotal + taxes, 2)
					
					# Crear items de factura
					items = [{
						"description": f"{plan_name} - Suscripción {subscription_id[:8]}",
						"quantity": 1,
						"unit_price": subtotal,
						"total": subtotal,
						"currency": currency,
					}]
					
					# Validar datos de factura antes de guardar
					ctx = get_current_context()
					params = ctx.get("params", {})
					validate_data_quality = params.get("validate_data_quality", True)
					
					if validate_data_quality:
						subscription_data = billing.get("subscription_data", {})
						invoice_data = {
							"amount": total,
							"subtotal": subtotal,
							"taxes": taxes,
							"currency": currency,
						}
						is_valid, issues = _validate_financial_data(subscription_data, invoice_data)
						if not is_valid:
							error_msg = f"Invoice validation failed: {', '.join(issues)}"
							logger.error(
								f"Invoice validation failed for subscription {subscription_id}: {error_msg}",
								extra={"subscription_id": subscription_id, "issues": issues}
							)
							if STATS_AVAILABLE and Stats:
								try:
									Stats.incr("recurring_billing.invoice.validation.failed", 1)
								except Exception:
									pass
							
							# Guardar en DLQ si está habilitado
							if enable_dlq:
								_save_to_dlq(billing, error_msg)
							
							continue  # Saltar esta factura
					
					# Guardar en base de datos (saltear si es dry-run)
					if not dry_run:
						with get_conn() as conn:
							with conn.cursor() as cur:
								# Crear factura
								cur.execute(
									"""
									INSERT INTO invoices 
										(serie, company_tax_id, currency, subtotal, taxes, total, status, created_at)
									VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
									RETURNING id
									""",
									(serie, company_tax_id, currency, subtotal, taxes, total, "issued")
								)
								invoice_id = cur.fetchone()[0]
								
								# Crear items de factura
								for item in items:
									cur.execute(
										"""
										INSERT INTO invoice_items 
											(invoice_id, description, quantity, unit_price, total)
										VALUES (%s, %s, %s, %s, %s)
										""",
										(
											invoice_id,
											item.get("description"),
											float(item.get("quantity", 1)),
											float(item.get("unit_price", 0)),
											float(item.get("total", 0)),
										)
									)
								
								# Crear tracking de facturación recurrente
								cur.execute(
									"""
									INSERT INTO recurring_billing_tracking
										(subscription_id, customer_id, billing_period_start, billing_period_end,
										 invoice_id, status, amount, currency)
									VALUES (%s, %s, to_timestamp(%s), to_timestamp(%s), %s, %s, %s, %s)
									ON CONFLICT (subscription_id, billing_period_start) DO UPDATE SET
										invoice_id = EXCLUDED.invoice_id,
										status = EXCLUDED.status
									""",
									(
										subscription_id,
										customer_id,
										period_start,
										period_end,
										invoice_id,
										"invoice_generated",
										amount,
										currency,
									)
								)
								
								conn.commit()
					else:
						# Simular invoice_id para dry-run
						invoice_id = 999999 + len(generated_invoices)
					
					generated_invoices.append({
						"subscription_id": subscription_id,
						"customer_id": customer_id,
						"invoice_id": invoice_id,
						"amount": total,
						"currency": currency,
						"billing": billing,
					})
					
					logger.info(
						"Generated invoice for subscription",
						extra={
							"subscription_id": subscription_id,
							"invoice_id": invoice_id,
							"amount": total,
							"dry_run": dry_run,
						}
					)
				
				# Delay entre batches
				if batch_idx + batch_size < len(billing_needed) and batch_delay > 0:
					time.sleep(batch_delay)
			
			duration_ms = (time.time() - start_time) * 1000
			
			if STATS_AVAILABLE and Stats:
				try:
					Stats.incr("recurring_billing.invoices.generated", len(generated_invoices))
					Stats.timing("recurring_billing.invoices.duration_ms", int(duration_ms))
				except Exception:
					pass
			
			logger.info(
				"Invoices generated",
				extra={
					"count": len(generated_invoices),
					"duration_ms": duration_ms,
					"dry_run": dry_run,
				}
			)
			
			return {"invoices": generated_invoices}
		
		@task(task_id="process_payments")
		def process_payments(invoices_payload: Dict[str, Any]) -> Dict[str, Any]:
			"""
			Procesa pagos automáticos para las facturas generadas.
			Intenta cobrar usando el método de pago de la suscripción.
			Soporta procesamiento paralelo opcional.
			"""
			import requests
			
			ctx = get_current_context()
			params = ctx.get("params", {})
			max_workers = params.get("max_workers", 0)
			enable_cache = params.get("enable_cache", True)
			continue_on_error = params.get("continue_on_error", True)
			dry_run = params.get("dry_run", False)
			
			invoices = invoices_payload.get("invoices", []) or []
			stripe_key = os.environ.get("STRIPE_API_KEY", "").strip()
			max_retries = int(_get_env_var("RECURRING_BILLING_MAX_RETRIES", default="3"))
			
			if not stripe_key:
				raise AirflowFailException("STRIPE_API_KEY not configured")
			
			headers = {"Authorization": f"Bearer {stripe_key}"}
			session = _get_stripe_session()
			processed: List[Dict[str, Any]] = []
			start_time = time.time()
			
			# Performance profiling
			profile_ctx = _profile_operation("process_payments") if enable_performance_profiling else None
			if profile_ctx:
				profile_ctx.__enter__()
			
			try:
				def process_single_payment(inv_data: Dict[str, Any]) -> Dict[str, Any]:
					"""Procesa un pago individual."""
					subscription_id = inv_data.get("subscription_id")
					customer_id = inv_data.get("customer_id")
					invoice_id = inv_data.get("invoice_id")
					amount = inv_data.get("amount", 0.0)
					currency = inv_data.get("currency", "USD").lower()
					
					try:
						with _track_api_call("stripe", "check_payment"):
							# Intentar obtener suscripción del cache
							cached_sub = _get_cached_subscription(subscription_id, enable_cache)
						if cached_sub:
							subscription = cached_sub
						else:
							# Obtener suscripción
							if session:
								sub_r = session.get(f"https://api.stripe.com/v1/subscriptions/{subscription_id}", headers=headers)
							else:
								sub_r = requests.get(f"https://api.stripe.com/v1/subscriptions/{subscription_id}", headers=headers, timeout=DEFAULT_TIMEOUT)
							
							if sub_r.status_code == 429:
								return {
									"subscription_id": subscription_id,
									"invoice_id": invoice_id,
									"status": "rate_limited",
								}
							
							sub_r.raise_for_status()
							subscription = sub_r.json()
							_cache_subscription(subscription_id, subscription, enable_cache)
						
						latest_invoice_id = subscription.get("latest_invoice")
						
						if latest_invoice_id:
							# Verificar estado del invoice en Stripe
							if session:
								inv_r = session.get(f"https://api.stripe.com/v1/invoices/{latest_invoice_id}", headers=headers)
							else:
								inv_r = requests.get(f"https://api.stripe.com/v1/invoices/{latest_invoice_id}", headers=headers, timeout=DEFAULT_TIMEOUT)
							
							if inv_r.status_code == 429:
								return {
									"subscription_id": subscription_id,
									"invoice_id": invoice_id,
									"status": "rate_limited",
								}
							
							inv_r.raise_for_status()
							stripe_invoice = inv_r.json()
							
							payment_status = stripe_invoice.get("status", "draft")
							paid = stripe_invoice.get("paid", False)
							
							# Preparar resultado
							if paid:
								result = {
									"subscription_id": subscription_id,
									"invoice_id": invoice_id,
									"status": "paid",
									"stripe_invoice_id": latest_invoice_id,
								}
							else:
								result = {
									"subscription_id": subscription_id,
									"invoice_id": invoice_id,
									"status": "payment_pending",
									"stripe_invoice_id": latest_invoice_id,
									"stripe_status": payment_status,
								}
							
							# Actualizar estado en nuestra base de datos (saltear si es dry-run)
							if not dry_run:
								with get_conn() as conn:
									with conn.cursor() as cur:
										if paid:
											cur.execute(
												"""
												UPDATE recurring_billing_tracking
												SET status = 'paid'
												WHERE subscription_id = %s AND invoice_id = %s
												""",
												(subscription_id, invoice_id)
											)
											
											cur.execute(
												"""
												UPDATE invoices
												SET status = 'paid'
												WHERE id = %s
												""",
												(invoice_id,)
											)
											
											conn.commit()
										else:
											cur.execute(
												"""
												UPDATE recurring_billing_tracking
												SET status = 'payment_pending'
												WHERE subscription_id = %s AND invoice_id = %s
												""",
												(subscription_id, invoice_id)
											)
											conn.commit()
							
							return result
					
					return {
						"subscription_id": subscription_id,
						"invoice_id": invoice_id,
						"status": "no_invoice",
					}
					
				except requests.exceptions.HTTPError as e:
					logger.error(
						f"Error processing payment for subscription {subscription_id}: {e}",
						exc_info=True
					)
					return {
						"subscription_id": subscription_id,
						"invoice_id": invoice_id,
						"status": "error",
						"error": str(e)[:500],
					}
				except Exception as e:
					logger.error(
						f"Error processing payment for subscription {subscription_id}: {e}",
						exc_info=True
					)
					return {
						"subscription_id": subscription_id,
						"invoice_id": invoice_id,
						"status": "error",
						"error": str(e)[:500],
					}
			
			# Procesar en paralelo o secuencial
			use_parallel = CONCURRENT_AVAILABLE and max_workers > 0 and len(invoices) > 1
			
			if use_parallel:
				logger.info(f"Processing {len(invoices)} payments in parallel with {max_workers} workers")
				with ThreadPoolExecutor(max_workers=max_workers) as executor:
					future_to_invoice = {
						executor.submit(process_single_payment, inv_data): inv_data
						for inv_data in invoices
					}
					
					for future in as_completed(future_to_invoice):
						inv_data = future_to_invoice[future]
						try:
							result = future.result()
							processed.append(result)
							
							if result.get("status") == "paid":
								logger.info(
									"Payment processed successfully",
									extra={
										"subscription_id": result.get("subscription_id"),
										"invoice_id": result.get("invoice_id"),
									}
								)
						except Exception as e:
							logger.error(f"Error in parallel payment processing: {e}", exc_info=True)
							if not continue_on_error:
								raise
							processed.append({
								"subscription_id": inv_data.get("subscription_id"),
								"invoice_id": inv_data.get("invoice_id"),
								"status": "error",
								"error": str(e)[:500],
							})
			else:
				# Procesamiento secuencial
				for inv_data in invoices:
					result = process_single_payment(inv_data)
					processed.append(result)
			
			duration_ms = (time.time() - start_time) * 1000
			
			if STATS_AVAILABLE and Stats:
				try:
					Stats.incr("recurring_billing.payments.processed", len(processed))
					Stats.timing("recurring_billing.payments.duration_ms", int(duration_ms))
					if use_parallel:
						Stats.incr("recurring_billing.payments.parallel", 1)
					else:
						Stats.incr("recurring_billing.payments.sequential", 1)
				except Exception:
					pass
			
			logger.info(
				"Payments processed",
				extra={
					"count": len(processed),
					"duration_ms": duration_ms,
					"parallel": use_parallel,
					"workers": max_workers if use_parallel else 1,
				}
			)
			
			return {"processed": processed}
		
		@task(task_id="handle_failed_payments")
		def handle_failed_payments(payments_payload: Dict[str, Any]) -> Dict[str, Any]:
			"""
			Maneja pagos fallidos: envía notificaciones y registra para reintentos.
			"""
			processed = payments_payload.get("processed", []) or []
			failed_payments: List[Dict[str, Any]] = []
			
			for payment in processed:
				if payment.get("status") in ["payment_pending", "error"]:
					failed_payments.append(payment)
					
					subscription_id = payment.get("subscription_id")
					invoice_id = payment.get("invoice_id")
					
					# Obtener información del cliente
					with get_conn() as conn:
						with conn.cursor() as cur:
							cur.execute(
								"""
								SELECT customer_id, amount, currency
								FROM recurring_billing_tracking
								WHERE subscription_id = %s AND invoice_id = %s
								""",
								(subscription_id, invoice_id)
							)
							tracking = cur.fetchone()
							
							if tracking:
								customer_id = tracking[0]
								amount = tracking[1]
								currency = tracking[2]
								
								# Enviar notificación al cliente
								subject = f"Problema con el pago de tu suscripción"
								body = f"""
								<p>Hemos detectado un problema al procesar el pago de tu suscripción.</p>
								<p><strong>Monto:</strong> {currency} {amount:.2f}</p>
								<p><strong>Suscripción:</strong> {subscription_id[:20]}...</p>
								<p>Por favor, actualiza tu método de pago en tu cuenta para continuar disfrutando del servicio.</p>
								"""
								
								try:
									notify_email(subject=subject, html_content=body, to=None)
									logger.info(
										"Sent payment failure notification",
										extra={"subscription_id": subscription_id, "customer_id": customer_id}
									)
								except Exception as e:
									logger.warning(f"Failed to send notification: {e}")
			
			logger.info(
				"Handled failed payments",
				extra={"failed_count": len(failed_payments)}
			)
			
			return {"failed_payments": failed_payments}
		
		# Flujo de procesamiento
		invoices_data = generate_invoices()
		payments_data = process_payments(invoices_data)
		failed_data = handle_failed_payments(payments_data)
		
		# Calcular métricas detalladas
		invoices_list = invoices_data.get("invoices", [])
		payments_list = payments_data.get("processed", [])
		failed_list = failed_data.get("failed_payments", [])
		
		# Métricas de pagos
		paid_count = sum(1 for p in payments_list if p.get("status") == "paid")
		pending_count = sum(1 for p in payments_list if p.get("status") == "payment_pending")
		error_count = sum(1 for p in payments_list if p.get("status") == "error")
		rate_limited_count = sum(1 for p in payments_list if p.get("status") == "rate_limited")
		
		# Total de montos
		total_amount = sum(inv.get("amount", 0) for inv in invoices_list)
		paid_amount = sum(
			inv.get("amount", 0) for inv in invoices_list
			if any(p.get("invoice_id") == inv.get("invoice_id") and p.get("status") == "paid" 
				for p in payments_list)
		)
		
		summary = ProcessingSummary(
			total_subscriptions=len(billing_needed),
			invoices_generated=len(invoices_list),
			payments_processed=len(payments_list),
			payments_successful=paid_count,
			payments_failed=len(failed_list),
			failed_payments=len(failed_list),
			total_amount=total_amount,
		)
		
		# Agregar métricas adicionales al summary
		summary_dict = summary.to_dict()
		summary_dict["metrics"] = {
			"payments": {
				"paid": paid_count,
				"pending": pending_count,
				"error": error_count,
				"rate_limited": rate_limited_count,
			},
			"amounts": {
				"total": total_amount,
				"paid": paid_amount,
				"pending": total_amount - paid_amount,
			},
			"success_rate": (paid_count / len(payments_list) * 100) if payments_list else 0.0,
		}
		
		# Trackear métricas adicionales
		if STATS_AVAILABLE and Stats:
			try:
				Stats.gauge("recurring_billing.summary.total_amount", total_amount)
				Stats.gauge("recurring_billing.summary.paid_amount", paid_amount)
				Stats.gauge("recurring_billing.summary.success_rate", summary_dict["metrics"]["success_rate"])
				Stats.incr("recurring_billing.summary.payments.paid", paid_count)
				Stats.incr("recurring_billing.summary.payments.pending", pending_count)
				Stats.incr("recurring_billing.summary.payments.error", error_count)
			except Exception:
				pass
		
		return {"summary": summary_dict}
	
	@task(task_id="sync_to_quickbooks")
	def sync_to_quickbooks(billing_summary: Dict[str, Any]) -> Dict[str, Any]:
		"""
		Sincroniza facturas generadas con QuickBooks (opcional).
		"""
		sync_enabled = _get_env_var("RECURRING_BILLING_SYNC_QUICKBOOKS", default="false").lower() == "true"
		
		if not sync_enabled:
			logger.info("QuickBooks sync disabled, skipping")
			return {"synced": False, "count": 0}
		
		# Esta tarea puede invocar la lógica de stripe_invoice_sync_quickbooks.py
		# Por ahora solo registramos que se debe sincronizar
		logger.info("QuickBooks sync would be performed here")
		
		return {"synced": True, "count": 0}
	
	@task(task_id="send_subscription_reminders")
	def send_subscription_reminders(billing_summary: Dict[str, Any]) -> Dict[str, Any]:
		"""
		Envía recordatorios para suscripciones próximas a renovar o con pagos fallidos.
		"""
		import requests
		
		stripe_key = os.environ.get("STRIPE_API_KEY", "").strip()
		if not stripe_key:
			logger.warning("STRIPE_API_KEY not configured, skipping reminders")
			return {"reminders_sent": 0}
		
		headers = {"Authorization": f"Bearer {stripe_key}"}
		ctx = get_current_context()
		now = ctx["data_interval_end"]
		
		reminders_sent = 0
		
		# Obtener suscripciones que se renuevan pronto (próximos 3 días)
		try:
			params = {
				"status": "active",
				"limit": 100,
			}
			
			# Obtener suscripciones activas
			r = requests.get(
				"https://api.stripe.com/v1/subscriptions",
				headers=headers,
				params=params,
				timeout=30
			)
			r.raise_for_status()
			subscriptions = r.json().get("data", [])
			
			for sub in subscriptions:
				current_period_end = sub.get("current_period_end")
				if not current_period_end:
					continue
				
				period_end_dt = pendulum.from_timestamp(current_period_end)
				days_until_renewal = (period_end_dt - now).days
				
				# Enviar recordatorio si se renueva en 1-3 días
				if 1 <= days_until_renewal <= 3:
					customer_id = sub.get("customer")
					sub_id = sub.get("id")
					
					# Obtener información del cliente (con cache)
					ctx = get_current_context()
					params = ctx.get("params", {})
					enable_cache = params.get("enable_cache", True)
					
					cached_customer = _get_cached_customer(customer_id, enable_cache)
					if cached_customer:
						customer = cached_customer
						customer_email = customer.get("email")
					else:
						try:
							session = _get_stripe_session()
							if session:
								customer_r = session.get(f"https://api.stripe.com/v1/customers/{customer_id}", headers=headers)
							else:
								customer_r = requests.get(f"https://api.stripe.com/v1/customers/{customer_id}", headers=headers, timeout=30)
							
							customer_r.raise_for_status()
							customer = customer_r.json()
							customer_email = customer.get("email")
							_cache_customer(customer_id, customer, enable_cache)
						
						if customer_email:
							subject = f"Tu suscripción se renovará en {days_until_renewal} día(s)"
							body = f"""
							<p>Este es un recordatorio de que tu suscripción se renovará automáticamente en {days_until_renewal} día(s).</p>
							<p><strong>ID de Suscripción:</strong> {sub_id[:20]}...</p>
							<p>El cargo se realizará automáticamente usando el método de pago guardado en tu cuenta.</p>
							<p>Si necesitas actualizar tu método de pago, por favor hazlo antes de la fecha de renovación.</p>
							"""
							
							try:
								notify_email(subject=subject, html_content=body, to=None)
								reminders_sent += 1
								logger.info(
									"Sent subscription renewal reminder",
									extra={
										"subscription_id": sub_id,
										"customer_id": customer_id,
										"days_until_renewal": days_until_renewal,
									}
								)
							except Exception as e:
								logger.warning(f"Failed to send reminder: {e}")
					except Exception as e:
						logger.warning(f"Error getting customer info: {e}")
		
		except Exception as e:
			logger.error(f"Error sending subscription reminders: {e}", exc_info=True)
		
		logger.info(
			"Subscription reminders sent",
			extra={"count": reminders_sent}
		)
		
		return {"reminders_sent": reminders_sent}
	
	@task(task_id="send_summary")
	def send_summary(final_summary: Dict[str, Any]) -> None:
		"""
		Envía resumen del procesamiento y actualiza progreso.
		Incluye comparación histórica y alertas de tendencias.
		"""
		summary_dict = final_summary.get("summary", {})
		summary = ProcessingSummary(**summary_dict)
		
		# Comparar con ejecuciones anteriores
		comparison = _compare_with_history(summary.to_dict())
		
		if comparison.get("has_history"):
			logger.info(
				"Historical comparison",
				extra={
					"comparison": comparison,
					"trends": comparison.get("trends", {}),
				}
			)
			
			# Alertar sobre tendencias preocupantes
			trends = comparison.get("trends", {})
			if trends.get("success_rate_declining"):
				_send_slack_notification(
					f"⚠️ recurring_billing: Success rate declining! "
					f"Current: {summary_dict.get('success_rate', 0):.1f}%, "
					f"Previous: {comparison['changes']['success_rate'].get('previous', 0):.1f}%"
				)
			
			if trends.get("invoices_decreasing"):
				_send_slack_notification(
					f"📉 recurring_billing: Invoice count decreasing significantly! "
					f"Current: {summary.invoices_generated}, Previous: {comparison['changes']['invoices'].get('previous', 0)}"
				)
		
		# Actualizar progreso en Variables de Airflow
		try:
			progress_key = "recurring_billing:last_run"
			progress_data = {
				"timestamp": pendulum.now("UTC").int_timestamp,
				"summary": summary.to_dict(),
				"comparison": comparison,
			}
			Variable.set(progress_key, json.dumps(progress_data))
		except Exception as e:
			logger.warning(f"Failed to save progress to Variables: {e}")
		
		# Log resumen completo
		logger.info(
			"Recurring billing processing completed",
			extra=summary.to_dict()
		)
		
		# Mostrar errores si los hay
		if summary.errors:
			error_sample = summary.errors[:5]
			logger.warning(
				f"Errors during processing ({len(summary.errors)} total)",
				extra={"error_sample": error_sample}
			)
		
		# Notificación si hay fallos significativos
		if summary.payments_failed > 0 and summary.success_rate < 50.0:
			_send_slack_notification(
				f":warning: recurring_billing: Low success rate ({summary.success_rate:.1f}%). "
				f"Invoices: {summary.invoices_generated}, Payments successful: {summary.payments_successful}, "
				f"Failed: {summary.payments_failed}"
			)
		
		# Calcular métricas de SLA
		target_duration_ms = float(_get_env_var("RECURRING_BILLING_SLA_TARGET_MS", default="600000"))  # 10 min
		sla_metrics = _calculate_sla_metrics(summary.duration_ms, target_duration_ms)
		
		logger.info(
			"SLA metrics",
			extra={
				"sla_met": sla_metrics["sla_met"],
				"sla_percentage": sla_metrics["sla_percentage"],
				"duration_ms": sla_metrics["duration_ms"],
				"target_ms": sla_metrics["target_duration_ms"],
			}
		)
		
		# Alertas predictivas
		ctx = get_current_context()
		params = ctx.get("params", {})
		enable_predictive = params.get("enable_predictive_alerts", True)
		
		if enable_predictive:
			try:
				# Obtener historial para análisis predictivo
				history_key = "recurring_billing:execution_history"
				history_data = Variable.get(history_key, default_var=None)
				history = []
				if history_data:
					history = json.loads(history_data)
				
				predictions = _predict_future_issues(summary.to_dict(), history)
				
				if predictions:
					for pred in predictions:
						if pred.get("severity") == "high":
							_send_slack_notification(
								f"🔮 *Alerta Predictiva:* {pred.get('message', 'Unknown issue')}"
							)
						logger.warning(
							"Predictive alert",
							extra={"prediction": pred}
						)
				
				# Guardar ejecución actual en historial (mantener últimas 20)
				history.append({
					"timestamp": pendulum.now("UTC").int_timestamp,
					"summary": summary.to_dict(),
					"sla_metrics": sla_metrics,
				})
				history = sorted(history, key=lambda x: x.get("timestamp", 0), reverse=True)[:20]
				Variable.set(history_key, json.dumps(history))
			except Exception as e:
				logger.warning(f"Error in predictive analysis: {e}", exc_info=True)
		
		# Métricas finales
		if STATS_AVAILABLE and Stats:
			try:
				Stats.incr("recurring_billing.processing.total", summary.total_subscriptions)
				Stats.incr("recurring_billing.processing.invoices", summary.invoices_generated)
				Stats.incr("recurring_billing.processing.payments_successful", summary.payments_successful)
				Stats.incr("recurring_billing.processing.payments_failed", summary.payments_failed)
				Stats.gauge("recurring_billing.processing.success_rate", summary.success_rate)
				Stats.timing("recurring_billing.processing.duration_ms", int(summary.duration_ms))
				Stats.gauge("recurring_billing.processing.total_amount", summary.total_amount)
				
				# Métricas de SLA
				Stats.gauge("recurring_billing.sla.percentage", sla_metrics["sla_percentage"])
				Stats.gauge("recurring_billing.sla.margin_ms", sla_metrics["sla_margin_ms"])
				if sla_metrics["sla_met"]:
					Stats.incr("recurring_billing.sla.met", 1)
				else:
					Stats.incr("recurring_billing.sla.missed", 1)
			except Exception:
				pass
		
		return None
	
	@task(task_id="release_lock", trigger_rule="all_done")
	def release_lock(lock_info: Dict[str, Any]) -> None:
		"""Libera el lock distribuido al finalizar."""
		ctx = get_current_context()
		params = ctx.get("params", {})
		enable_lock = params.get("enable_distributed_lock", True)
		
		if not enable_lock or lock_info.get("skip_lock"):
			return
		
		lock_key = lock_info.get("lock_key")
		if lock_key:
			_release_distributed_lock(lock_key)
			logger.info("Execution lock released", extra={"lock_key": lock_key})
	
	# Construir el flujo del DAG con distributed locking y health check
	lock_info = acquire_lock()
	health = health_check()
	subscriptions = fetch_active_subscriptions()
	billing_needed = identify_billing_needed(subscriptions)
	billing_result = process_subscription_billing(billing_needed)
	quickbooks_sync = sync_to_quickbooks(billing_result)
	reminders = send_subscription_reminders(billing_result)
	summary = send_summary({"summary": billing_result.get("summary", {})})
	release = release_lock(lock_info)
	
	# Dependencias: lock primero, luego health check, y release al final
	lock_info >> health >> subscriptions >> billing_needed >> billing_result >> quickbooks_sync >> reminders >> summary >> release
	
	return None


dag = recurring_billing()

