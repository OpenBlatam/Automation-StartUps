"""
Módulo para procesar reembolsos de Stripe y crear notas de crédito en QuickBooks.
Versión mejorada con retry logic, métricas y mejor manejo de errores.
"""
from __future__ import annotations

from datetime import timedelta
import logging
import os
from typing import Any, Dict, Optional
from functools import lru_cache
from contextlib import contextmanager

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.models import Variable
from airflow.exceptions import AirflowFailException

from data.airflow.plugins.db import get_conn

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
    import requests

try:
    from pydantic import BaseModel, Field, ValidationError
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

try:
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False

try:
    from data.airflow.plugins.etl_notifications import notify_slack
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    try:
        from plugins.etl_notifications import notify_slack
        NOTIFICATIONS_AVAILABLE = True
    except ImportError:
        NOTIFICATIONS_AVAILABLE = False

logger = logging.getLogger(__name__)


def _get_env_var(name: str, default: str | None = None) -> str:
	"""Obtiene variable de entorno o Airflow Variable."""
	value = Variable.get(name, default_var=default)
	if value is None:
		value = os.environ.get(name, default)
	return str(value) if value else ""


# Variables de entorno para QuickBooks
QUICKBOOKS_API_VERSION = "v3"


def get_quickbooks_base_url() -> str:
	"""
	Obtiene la URL base de QuickBooks según el entorno.
	
	Returns:
		URL base de QuickBooks (sandbox o production)
	"""
	environment = _get_env_var("QUICKBOOKS_ENVIRONMENT", default="production")
	if environment.lower() in ["sandbox", "development", "dev", "test"]:
		return "https://sandbox-quickbooks.api.intuit.com"
	else:
		return "https://quickbooks.api.intuit.com"


def get_quickbooks_headers(access_token: Optional[str] = None) -> Dict[str, str]:
	"""
	Obtiene los headers necesarios para las peticiones a QuickBooks API.
	
	Args:
		access_token: Token de acceso de OAuth (opcional, usa env var si no se proporciona)
	
	Returns:
		Dict con los headers necesarios
	"""
	token = access_token or _get_env_var("QUICKBOOKS_ACCESS_TOKEN")
	if not token:
		raise AirflowFailException("ERROR: QUICKBOOKS_ACCESS_TOKEN no configurado")
	
	return {
		"Authorization": f"Bearer {token}",
		"Content-Type": "application/json",
		"Accept": "application/json",
	}


@lru_cache(maxsize=100)
def _get_realm_and_headers_cached(access_token: Optional[str] = None) -> tuple[str, Dict[str, str]]:
	"""Cache para realm y headers (útil para múltiples llamadas)."""
	realm = _get_env_var("QUICKBOOKS_REALM_ID")
	if not realm:
		raise AirflowFailException("ERROR: QUICKBOOKS_REALM_ID no configurado")
	return realm, get_quickbooks_headers(access_token)


def buscar_cliente_por_email(
	correo_cliente: str, 
	realm_id: Optional[str] = None, 
	access_token: Optional[str] = None,
	use_retry: bool = True
) -> Optional[str]:
	"""
	Busca un cliente en QuickBooks por su email con retry logic mejorado.
	
	Args:
		correo_cliente: Email del cliente
		realm_id: Company ID de QuickBooks (opcional, usa env var si no se proporciona)
		access_token: Token de acceso de OAuth (opcional, usa env var si no se proporciona)
		use_retry: Si usar retry logic (default: True)
	
	Returns:
		ID del cliente en QuickBooks o None si no se encuentra
	"""
	if not correo_cliente:
		return None
	
	realm = realm_id or _get_env_var("QUICKBOOKS_REALM_ID")
	if not realm:
		raise AirflowFailException("ERROR: QUICKBOOKS_REALM_ID no configurado")
	
	headers = get_quickbooks_headers(access_token)
	base_url = get_quickbooks_base_url()
	
	# Escapar comillas simples en el email para la consulta
	escaped_email = correo_cliente.replace("'", "''")
	
	def _execute_query(query: str) -> Optional[str]:
		"""Ejecuta query y retorna customer_id si encuentra."""
		url = f"{base_url}/{QUICKBOOKS_API_VERSION}/company/{realm}/query"
		params = {"query": query}
		
		if HTTPX_AVAILABLE:
			with httpx.Client(timeout=30.0) as client:
				response = client.get(url, headers=headers, params=params)
		else:
			response = requests.get(url, headers=headers, params=params, timeout=30)
		
		if response.status_code == 200:
			data = response.json()
			query_response = data.get("QueryResponse", {})
			customers = query_response.get("Customer", [])
			
			if customers:
				customer_id = customers[0].get("Id")
				if customer_id:
					return customer_id
		
		return None
	
	# Query exacta primero
	query_exact = f"SELECT Id, PrimaryEmailAddr FROM Customer WHERE PrimaryEmailAddr.Address = '{escaped_email}'"
	
	if TENACITY_AVAILABLE and use_retry:
		@retry(
			stop=stop_after_attempt(3),
			wait=wait_exponential(multiplier=1, min=2, max=10),
			retry=retry_if_exception_type((Exception,)),
			reraise=False,
		)
		def _search_with_retry():
			customer_id = _execute_query(query_exact)
			if customer_id:
				return customer_id
			
			# Si no encontró, intentar case-insensitive
			query_lower = f"SELECT Id, PrimaryEmailAddr FROM Customer WHERE LOWER(PrimaryEmailAddr.Address) = LOWER('{escaped_email}')"
			return _execute_query(query_lower)
		
		try:
			return _search_with_retry()
		except Exception as e:
			logger.error(f"Error al buscar cliente en QuickBooks después de retries: {e}")
			return None
	else:
		try:
			customer_id = _execute_query(query_exact)
			if customer_id:
				return customer_id
			
			# Intentar case-insensitive
			query_lower = f"SELECT Id, PrimaryEmailAddr FROM Customer WHERE LOWER(PrimaryEmailAddr.Address) = LOWER('{escaped_email}')"
			return _execute_query(query_lower)
		except Exception as e:
			logger.error(f"Error al buscar cliente en QuickBooks: {e}")
			return None


def crear_nota_credito_quickbooks(
	customer_id: str,
	monto: float,
	currency: str,
	receipt_id: str,
	descripcion: str = "Reembolso de Stripe",
	realm_id: Optional[str] = None,
	access_token: Optional[str] = None
) -> Dict[str, Any]:
	"""
	Crea una nota de crédito (CreditMemo) en QuickBooks y la aplica al recibo original.
	
	Args:
		customer_id: ID del cliente en QuickBooks
		monto: Monto del reembolso (positivo, será convertido a negativo)
		currency: Código de moneda (USD, MXN, etc.)
		receipt_id: ID del recibo original en QuickBooks
		descripcion: Descripción de la nota de crédito
		realm_id: Company ID de QuickBooks (opcional, usa env var si no se proporciona)
		access_token: Token de acceso de OAuth (opcional, usa env var si no se proporciona)
	
	Returns:
		Dict con status y qb_credit_id
	"""
	realm = realm_id or _get_env_var("QUICKBOOKS_REALM_ID")
	if not realm:
		raise AirflowFailException("ERROR: QUICKBOOKS_REALM_ID no configurado")
	
	headers = get_quickbooks_headers(access_token)
	
	# Obtener item ID para reembolsos (configurable)
	refund_item_id = _get_env_var("QUICKBOOKS_REFUND_ITEM_ID", default="")
	
	# Construir el payload para crear el CreditMemo
	line_detail = {
		"Amount": -abs(monto),  # Negativo para nota de crédito
		"DetailType": "SalesItemLineDetail",
		"Description": descripcion
	}
	
	# Solo agregar ItemRef si está configurado, de lo contrario usar línea de descripción
	if refund_item_id:
		line_detail["SalesItemLineDetail"] = {
			"ItemRef": {
				"value": refund_item_id
			}
		}
	else:
		# Usar línea de descripción si no hay item configurado
		line_detail["DetailType"] = "DescriptionOnly"
	
	payload = {
		"Line": [line_detail],
		"CustomerRef": {
			"value": customer_id
		},
		"TxnDate": pendulum.now().to_date_string(),
		"TotalAmt": -abs(monto),
		"PrivateNote": f"Reembolso Stripe relacionado con recibo QB: {receipt_id}"
	}
	
	# Agregar CurrencyRef solo si es diferente de USD
	if currency.upper() != "USD":
		payload["CurrencyRef"] = {
			"value": currency.upper()
		}
	
	def _create_credit_memo() -> Dict[str, Any]:
		"""Función interna para crear CreditMemo."""
		base_url = get_quickbooks_base_url()
		url = f"{base_url}/{QUICKBOOKS_API_VERSION}/company/{realm}/creditmemo"
		
		if HTTPX_AVAILABLE:
			with httpx.Client(timeout=30.0) as client:
				response = client.post(url, headers=headers, json=payload)
		else:
			response = requests.post(url, headers=headers, json=payload, timeout=30)
		
		if response.status_code not in [200, 201]:
			try:
				error_data = response.json()
				error_msg = error_data.get("Fault", {}).get("Error", [{}])[0].get("Message", response.text)
			except:
				error_msg = response.text or "Error desconocido"
			raise AirflowFailException(f"Error al crear nota de crédito en QuickBooks: {error_msg}")
		
		data = response.json()
		credit_memo = data.get("CreditMemo", {})
		credit_id = credit_memo.get("Id")
		
		if not credit_id:
			raise AirflowFailException("Error: QuickBooks no retornó ID de la nota de crédito")
		
		return {
			"status": "Éxito",
			"qb_credit_id": credit_id,
			"credit_memo": credit_memo
		}
	
	# Ejecutar con retry si está disponible
	if TENACITY_AVAILABLE:
		@retry(
			stop=stop_after_attempt(3),
			wait=wait_exponential(multiplier=1, min=2, max=10),
			retry=retry_if_exception_type((Exception,)),
			reraise=True,
		)
		def _create_with_retry():
			return _create_credit_memo()
		
		try:
			return _create_with_retry()
		except RetryError as e:
			logger.error(f"Error después de todos los retries: {e}")
			raise AirflowFailException(f"ERROR: No se pudo crear nota de crédito después de múltiples intentos: {str(e)}")
	else:
		try:
			return _create_credit_memo()
		except requests.exceptions.Timeout:
			raise AirflowFailException("ERROR_TIMEOUT: La petición a QuickBooks excedió el tiempo límite")
		except requests.exceptions.ConnectionError:
			raise AirflowFailException("ERROR_CONNECTION: No se pudo conectar con QuickBooks API")
		except requests.exceptions.RequestException as e:
			raise AirflowFailException(f"ERROR_REQUEST: {str(e)}")
		except Exception as e:
			raise AirflowFailException(f"ERROR_INESPERADO: {str(e)}")


def procesar_reembolso_stripe_quickbooks(
	stripe_refund_id: str,
	monto_reembolso: float,
	correo_cliente: str,
	qb_receipt_id: str,
	realm_id: Optional[str] = None,
	access_token: Optional[str] = None
) -> Dict[str, Any]:
	"""
	Procesa un reembolso de Stripe y crea una nota de crédito en QuickBooks.
	
	Args:
		stripe_refund_id: ID del reembolso en Stripe
		monto_reembolso: Monto del reembolso
		correo_cliente: Email del cliente
		qb_receipt_id: ID del recibo original en QuickBooks
		realm_id: Company ID de QuickBooks (opcional, usa env var si no se proporciona)
		access_token: Token de acceso de OAuth (opcional, usa env var si no se proporciona)
	
	Returns:
		Dict con status y qb_credit_id
	"""
	logger = logging.getLogger("airflow.task")
	
	# Validar parámetros
	if not stripe_refund_id:
		raise AirflowFailException("ERROR: stripe_refund_id es requerido")
	if not monto_reembolso or monto_reembolso <= 0:
		raise AirflowFailException("ERROR: monto_reembolso debe ser mayor a 0")
	if not correo_cliente:
		raise AirflowFailException("ERROR: correo_cliente es requerido")
	if not qb_receipt_id:
		raise AirflowFailException("ERROR: qb_receipt_id es requerido")
	
	# Buscar cliente en QuickBooks por email
	logger.info(f"Buscando cliente con email: {correo_cliente}")
	customer_id = buscar_cliente_por_email(correo_cliente, realm_id, access_token)
	
	if not customer_id:
		raise AirflowFailException(f"ERROR: No se encontró cliente con email {correo_cliente} en QuickBooks")
	
	logger.info(f"Cliente encontrado en QuickBooks: {customer_id}")
	
	# Crear nota de crédito
	descripcion = f"Reembolso Stripe {stripe_refund_id} - Recibo original: {qb_receipt_id}"
	resultado = crear_nota_credito_quickbooks(
		customer_id=customer_id,
		monto=monto_reembolso,
		currency="USD",  # Ajustar según necesidad
		receipt_id=qb_receipt_id,
		descripcion=descripcion,
		realm_id=realm_id,
		access_token=access_token
	)
	
		logger.info(
			"Nota de crédito creada en QuickBooks",
			extra={
				"stripe_refund_id": stripe_refund_id,
				"qb_credit_id": resultado.get("qb_credit_id"),
				"customer_id": customer_id,
				"monto": monto_reembolso
			}
		)
		
		# Registrar métricas si está disponible
		if STATS_AVAILABLE:
			try:
				Stats.incr("stripe_refund.quickbooks_credit_created", 1)
				Stats.gauge("stripe_refund.amount", monto_reembolso)
			except Exception:
				pass
	
	return resultado


@dag(
	dag_id="stripe_refund_to_quickbooks",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule=None,  # Manual trigger only
	catchup=False,
	default_args={
		"owner": "finance",
		"retries": 1,
		"retry_delay": timedelta(minutes=2),
		"email_on_failure": False,
		"email_on_retry": False,
	},
	description="Procesa reembolsos de Stripe y crea notas de crédito en QuickBooks",
	tags=["finance", "stripe", "quickbooks", "refunds"],
)
def stripe_refund_to_quickbooks() -> None:
	logger = logging.getLogger("airflow.task")

	@task(task_id="guardar_resultado_bd")
	def guardar_resultado_bd(resultado: Dict[str, Any], **context) -> Dict[str, Any]:
		"""
		Guarda el resultado del procesamiento en la base de datos.
		"""
		ctx = get_current_context()
		params = ctx.get("params", {}) or {}
		
		stripe_refund_id = params.get("stripe_refund_id", "")
		qb_credit_id = resultado.get("qb_credit_id", "")
		status = resultado.get("status", "Error")
		
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					# Crear tabla si no existe
					cur.execute("""
						CREATE TABLE IF NOT EXISTS stripe_refunds (
							id SERIAL PRIMARY KEY,
							stripe_refund_id TEXT NOT NULL UNIQUE,
							stripe_charge_id TEXT,
							amount NUMERIC(12,2) NOT NULL,
							currency VARCHAR(8) NOT NULL,
							customer_email TEXT NOT NULL,
							qb_receipt_id TEXT NOT NULL,
							qb_credit_id TEXT,
							status TEXT NOT NULL DEFAULT 'pending',
							reason TEXT,
							metadata JSONB,
							created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
							processed_at TIMESTAMPTZ,
							error_message TEXT
						)
					""")
					
					# Actualizar registro con resultado
					cur.execute("""
						UPDATE stripe_refunds
						SET 
							qb_credit_id = %s,
							status = CASE 
								WHEN %s = 'Éxito' THEN 'completed'
								ELSE 'failed'
							END,
							processed_at = NOW(),
							error_message = CASE 
								WHEN %s != 'Éxito' THEN %s
								ELSE NULL
							END
						WHERE stripe_refund_id = %s
					""", (qb_credit_id, status, status, resultado.get("error_message", status), stripe_refund_id))
					
					conn.commit()
					logger.info(f"Resultado guardado en BD para reembolso {stripe_refund_id}")
					
					# Registrar métricas
					if STATS_AVAILABLE:
						try:
							Stats.incr("stripe_refund.db_saved", 1)
							if status == "Éxito":
								Stats.incr("stripe_refund.completed", 1)
							else:
								Stats.incr("stripe_refund.failed", 1)
						except Exception:
							pass
		except Exception as e:
			logger.warning(f"Error al guardar resultado en BD: {e}", exc_info=True)
			if STATS_AVAILABLE:
				try:
					Stats.incr("stripe_refund.db_error", 1)
				except Exception:
					pass
		
		return resultado

	@task(task_id="procesar_reembolso")
	def procesar_reembolso(**context) -> Dict[str, Any]:
		"""
		Procesa un reembolso de Stripe y crea nota de crédito en QuickBooks.
		
		Parámetros esperados (via context['params'] o context['conf']):
		- stripe_refund_id: ID del reembolso en Stripe
		- monto_reembolso: Monto del reembolso (float)
		- correo_cliente: Email del cliente
		- qb_receipt_id: ID del recibo original en QuickBooks
		"""
		ctx = get_current_context()
		# Intentar obtener de conf (cuando se trigger desde webhook) o params
		conf = ctx.get("dag_run", {}).get("conf", {}) or {}
		params = ctx.get("params", {}) or {}
		
		# Usar conf primero (desde webhook), luego params (desde UI)
		stripe_refund_id = conf.get("stripe_refund_id") or params.get("stripe_refund_id", "")
		monto_reembolso = conf.get("monto_reembolso") or params.get("monto_reembolso", 0)
		correo_cliente = conf.get("correo_cliente") or params.get("correo_cliente", "")
		qb_receipt_id = conf.get("qb_receipt_id") or params.get("qb_receipt_id", "")
		
		# Validar parámetros
		if not stripe_refund_id:
			raise AirflowFailException("Parámetro requerido: stripe_refund_id")
		if not monto_reembolso or monto_reembolso <= 0:
			raise AirflowFailException("Parámetro requerido: monto_reembolso (debe ser > 0)")
		if not correo_cliente:
			raise AirflowFailException("Parámetro requerido: correo_cliente")
		if not qb_receipt_id:
			raise AirflowFailException("Parámetro requerido: qb_receipt_id")
		
		# Convertir monto a float si viene como string
		try:
			monto_reembolso = float(monto_reembolso)
		except (ValueError, TypeError):
			raise AirflowFailException(f"monto_reembolso debe ser un número válido, recibido: {monto_reembolso}")
		
		# Procesar reembolso
		resultado = procesar_reembolso_stripe_quickbooks(
			stripe_refund_id=stripe_refund_id,
			monto_reembolso=monto_reembolso,
			correo_cliente=correo_cliente,
			qb_receipt_id=qb_receipt_id
		)
		
		logger.info(
			"Reembolso procesado exitosamente",
			extra={
				"stripe_refund_id": stripe_refund_id,
				"qb_credit_id": resultado.get("qb_credit_id"),
				"status": resultado.get("status")
			}
		)
		
		# Notificación a Slack si está disponible y hay error
		if NOTIFICATIONS_AVAILABLE and resultado.get("status") != "Éxito":
			try:
				notify_slack(
					f"⚠️ Reembolso Stripe falló\n"
					f"• Refund ID: {stripe_refund_id}\n"
					f"• Error: {resultado.get('error_message', 'Desconocido')}",
					extra_context={
						"stripe_refund_id": stripe_refund_id,
						"status": resultado.get("status")
					},
					username="Stripe Refund Processor",
					icon_emoji=":credit_card:"
				)
			except Exception as e:
				logger.warning(f"Failed to send Slack notification: {e}")
		
		return resultado

	resultado = procesar_reembolso()
	guardar_resultado_bd(resultado)
	return None


dag = stripe_refund_to_quickbooks()


# Función auxiliar para uso directo (sin DAG)
def procesar_reembolso_task(**context) -> Dict[str, Any]:
	"""
	Wrapper para usar la función en otros DAGs de Airflow.
	Espera los parámetros en context['params'] o context['ti'].xcom_pull().
	"""
	params = context.get('params', {})
	
	# Si no hay params directo, intentar obtener desde xcom
	if not params:
		if 'ti' in context:
			params = context['ti'].xcom_pull(key='refund_data') or {}
	
	stripe_refund_id = params.get('stripe_refund_id')
	monto_reembolso = params.get('monto_reembolso')
	correo_cliente = params.get('correo_cliente')
	qb_receipt_id = params.get('qb_receipt_id')
	
	if not all([stripe_refund_id, monto_reembolso, correo_cliente, qb_receipt_id]):
		raise ValueError(
			"Parámetros requeridos: stripe_refund_id, monto_reembolso, correo_cliente, qb_receipt_id"
		)
	
	resultado = procesar_reembolso_stripe_quickbooks(
		stripe_refund_id=stripe_refund_id,
		monto_reembolso=float(monto_reembolso),
		correo_cliente=correo_cliente,
		qb_receipt_id=qb_receipt_id
	)
	
	if resultado.get("status") == "Éxito":
		logger = logging.getLogger("airflow.task")
		logger.info(
			f"✓ Reembolso {stripe_refund_id} procesado exitosamente. "
			f"Nota de crédito QB: {resultado.get('qb_credit_id')}"
		)
	else:
		logger = logging.getLogger("airflow.task")
		logger.error(f"✗ Error al procesar reembolso {stripe_refund_id}: {resultado}")
	
	return resultado

