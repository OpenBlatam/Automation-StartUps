"""
Módulo para detectar correos de reembolsos de Stripe desde Gmail y procesarlos automáticamente.
Extiende el procesador de Gmail para buscar correos específicos de reembolsos.
"""
from __future__ import annotations

import os
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.exceptions import AirflowFailException

logger = logging.getLogger(__name__)

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_API_AVAILABLE = True
except ImportError:
    GMAIL_API_AVAILABLE = False
    logger.warning("Gmail API libraries not available.")


def extract_refund_info_from_email(subject: str, body: str) -> Optional[Dict[str, Any]]:
	"""
	Extrae información de reembolso desde el asunto y cuerpo del email.
	
	Busca patrones comunes en notificaciones de Stripe:
	- Refund IDs (re_xxx)
	- Amounts ($X.XX)
	- Customer emails
	
	Returns:
		Dict con stripe_refund_id, monto, correo_cliente, o None si no se encuentra
	"""
	# Patrón para ID de reembolso de Stripe
	refund_id_pattern = r'\bre_[a-zA-Z0-9]{24,}\b'
	refund_match = re.search(refund_id_pattern, subject + " " + body)
	
	if not refund_match:
		return None
	
	refund_id = refund_match.group(0)
	
	# Buscar monto en formato $X.XX o USD X.XX
	amount_patterns = [
		r'\$(\d+[.,]?\d*\.?\d{2})',
		r'USD\s+(\d+[.,]?\d*\.?\d{2})',
		r'(\d+[.,]?\d*\.?\d{2})\s*(?:USD|dollars?)',
	]
	
	amount = None
	for pattern in amount_patterns:
		match = re.search(pattern, body, re.IGNORECASE)
		if match:
			try:
				amount_str = match.group(1).replace(',', '')
				amount = float(amount_str)
				break
			except (ValueError, AttributeError):
				continue
	
	# Buscar email del cliente (formato email estándar)
	email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
	email_matches = re.findall(email_pattern, body)
	
	# Filtrar emails comunes de Stripe y usar el primero válido
	stripe_domains = ['stripe.com', 'mail.stripe.com', 'noreply']
	customer_email = None
	for email in email_matches:
		if not any(domain in email.lower() for domain in stripe_domains):
			customer_email = email
			break
	
	if refund_id and amount and customer_email:
		return {
			"stripe_refund_id": refund_id,
			"monto_reembolso": amount,
			"correo_cliente": customer_email,
			"source": "gmail_detection"
		}
	
	return None


@dag(
	dag_id="stripe_refund_email_detector",
	start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
	schedule="0 */2 * * *",  # Cada 2 horas
	catchup=False,
	default_args={
		"owner": "finance",
		"retries": 1,
		"retry_delay": timedelta(minutes=5),
		"email_on_failure": False,
	},
	doc_md="""
	### Detector de Reembolsos de Stripe desde Gmail
	
	Busca correos de notificaciones de reembolsos de Stripe y los procesa automáticamente.
	Requiere configuración de Gmail API y acceso a la base de datos para buscar qb_receipt_id.
	
	**Parámetros:**
	- `gmail_credentials_json`: JSON string con credenciales OAuth2 de Gmail
	- `gmail_token_json`: JSON string con token almacenado
	- `gmail_query`: Query de búsqueda en Gmail (default: busca correos de Stripe sobre refunds)
	- `dry_run`: Solo detectar sin procesar (default: false)
	""",
	params={
		"gmail_credentials_json": Param("", type="string", minLength=1),
		"gmail_token_json": Param("", type="string"),
		"gmail_query": Param("from:stripe.com refund OR \"refund processed\"", type="string"),
		"dry_run": Param(False, type="boolean"),
	},
	tags=["finance", "gmail", "stripe", "automation"],
)
def stripe_refund_email_detector() -> None:
	"""
	DAG para detectar correos de reembolsos de Stripe.
	"""
	
	@task(task_id="detect_refund_emails")
	def detect_refund_emails() -> List[Dict[str, Any]]:
		"""
		Busca correos de reembolsos en Gmail y extrae información.
		"""
		ctx = get_current_context()
		params = ctx["params"]
		
		if not GMAIL_API_AVAILABLE:
			raise AirflowFailException("Gmail API libraries not available")
		
		credentials_json = str(params["gmail_credentials_json"])
		token_json = str(params.get("gmail_token_json", ""))
		query = str(params.get("gmail_query", "from:stripe.com refund OR \"refund processed\""))
		
		# Reutilizar lógica de autenticación de gmail_processor
		# Importar función helper desde gmail_processor si está disponible
		try:
			# Intentar obtener servicio de Gmail (simplificado)
			creds = None
			if token_json:
				try:
					if os.path.isfile(token_json):
						with open(token_json, 'r') as token_file:
							token_data = json.load(token_file)
					else:
						token_data = json.loads(token_json)
					creds = Credentials.from_authorized_user_info(token_data, ['https://www.googleapis.com/auth/gmail.readonly'])
					if creds.expired and creds.refresh_token:
						creds.refresh(Request())
				except Exception as e:
					logger.warning(f"Could not load token: {e}")
			
			if not creds or not creds.valid:
				# Cargar credenciales y autorizar
				if os.path.isfile(credentials_json):
					with open(credentials_json, 'r') as creds_file:
						creds_data = json.load(creds_file)
				else:
					creds_data = json.loads(credentials_json)
				
				flow = InstalledAppFlow.from_client_config(creds_data, ['https://www.googleapis.com/auth/gmail.readonly'])
				creds = flow.run_local_server(port=0)
			
			service = build('gmail', 'v1', credentials=creds)
			
			# Buscar mensajes
			logger.info(f"Buscando correos con query: {query}")
			results = service.users().messages().list(
				userId='me',
				q=query,
				maxResults=50
			).execute()
			
			messages = results.get('messages', [])
			if not messages:
				logger.info("No se encontraron correos de reembolsos")
				return []
			
			refunds_detected = []
			
			# Procesar cada mensaje
			for msg in messages:
				try:
					# Obtener mensaje completo
					message = service.users().messages().get(
						userId='me',
						id=msg['id'],
						format='full'
					).execute()
					
					# Extraer headers
					headers = message['payload'].get('headers', [])
					header_dict = {h['name'].lower(): h['value'] for h in headers}
					
					subject = header_dict.get('subject', '')
					
					# Extraer body (simplificado)
					body = ""
					parts = message['payload'].get('parts', [])
					for part in parts:
						if part.get('mimeType') == 'text/plain':
							data = part.get('body', {}).get('data', '')
							if data:
								import base64
								body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
								break
					
					# Si no hay parts, intentar body directo
					if not body and 'body' in message['payload']:
						data = message['payload']['body'].get('data', '')
						if data:
							import base64
							body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
					
					# Extraer información de reembolso
					refund_info = extract_refund_info_from_email(subject, body)
					
					if refund_info:
						refund_info['email_id'] = msg['id']
						refund_info['subject'] = subject
						refunds_detected.append(refund_info)
						logger.info(f"Reembolso detectado: {refund_info.get('stripe_refund_id')}")
				
				except HttpError as error:
					logger.warning(f"Error procesando mensaje {msg.get('id')}: {error}")
					continue
			
			logger.info(f"Total de reembolsos detectados: {len(refunds_detected)}")
			return refunds_detected
			
		except Exception as e:
			logger.error(f"Error en búsqueda de Gmail: {e}", exc_info=True)
			raise AirflowFailException(f"Error al buscar correos en Gmail: {e}")
	
	@task(task_id="enrich_with_receipt_info")
	def enrich_with_receipt_info(refunds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
		"""
		Enriquece información de reembolsos con qb_receipt_id desde BD.
		"""
		from data.airflow.plugins.db import get_conn
		
		if not refunds:
			return []
		
		enriched = []
		
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					for refund in refunds:
						correo_cliente = refund.get("correo_cliente", "")
						
						# Buscar recibo más reciente del cliente
						cur.execute("""
							SELECT 
								p.payment_id,
								p.metadata->>'qb_receipt_id' as qb_receipt_id
							FROM payments p
							WHERE p.customer = %s
							ORDER BY p.created_at DESC
							LIMIT 1
						""", (correo_cliente,))
						
						result = cur.fetchone()
						if result:
							qb_receipt_id = result[1]
							if qb_receipt_id:
								refund["qb_receipt_id"] = qb_receipt_id
								enriched.append(refund)
						else:
							logger.warning(f"No se encontró recibo para cliente {correo_cliente}")
		except Exception as e:
			logger.error(f"Error al enriquecer datos: {e}", exc_info=True)
		
		return enriched
	
	@task(task_id="trigger_refund_processing")
	def trigger_refund_processing(enriched_refunds: List[Dict[str, Any]]) -> Dict[str, Any]:
		"""
		Trigger el DAG de procesamiento de reembolsos para cada uno encontrado.
		"""
		from airflow.api.client.local_client import Client as AirflowClient
		
		ctx = get_current_context()
		params = ctx["params"]
		dry_run = bool(params.get("dry_run", False))
		
		triggered = 0
		failed = 0
		
		if dry_run:
			logger.info(f"DRY RUN: Se procesarían {len(enriched_refunds)} reembolsos")
			return {
				"triggered": 0,
				"failed": 0,
				"dry_run": True,
				"would_process": len(enriched_refunds)
			}
		
		# Importar función de procesamiento directamente
		try:
			from data.airflow.dags.stripe_refund_to_quickbooks import procesar_reembolso_stripe_quickbooks
		except ImportError:
			from stripe_refund_to_quickbooks import procesar_reembolso_stripe_quickbooks
		
		for refund in enriched_refunds:
			try:
				if not dry_run:
					# Procesar directamente
					resultado = procesar_reembolso_stripe_quickbooks(
						stripe_refund_id=refund.get('stripe_refund_id'),
						monto_reembolso=refund.get('monto_reembolso'),
						correo_cliente=refund.get('correo_cliente'),
						qb_receipt_id=refund.get('qb_receipt_id')
					)
					
					if resultado.get('status') == 'Éxito':
						logger.info(
							f"Reembolso procesado: {refund.get('stripe_refund_id')} → "
							f"QB Credit: {resultado.get('qb_credit_id')}"
						)
						triggered += 1
					else:
						logger.warning(f"Reembolso falló: {refund.get('stripe_refund_id')}")
						failed += 1
				else:
					logger.info(f"DRY RUN: Procesaría reembolso: {refund.get('stripe_refund_id')}")
					triggered += 1
			except Exception as e:
				logger.error(f"Error al procesar reembolso {refund.get('stripe_refund_id')}: {e}", exc_info=True)
				failed += 1
		
		return {
			"triggered": triggered,
			"failed": failed,
			"dry_run": False
		}
	
	detected = detect_refund_emails()
	enriched = enrich_with_receipt_info(detected)
	trigger_refund_processing(enriched)


dag = stripe_refund_email_detector()

