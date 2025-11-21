"""
DAG para extraer transacciones de Stripe y generar reporte CSV para QuickBooks.

Al final del día, extrae todas las transacciones de Stripe (pagos, reembolsos, tarifas)
entre {fecha_inicio} y {fecha_fin}. Genera un reporte en QuickBooks como archivo CSV,
con columnas: fecha, tipo (pago/reembolso/tarifa), cliente, monto bruto, monto neto,
cuenta asignada. Adjunta al sistema de contabilidad y envía resumen.

Mejoras adicionales:
- Upload a S3/cloud storage
- Tracking de métricas (Stats, MLflow)
- Persistencia en base de datos
- Notificaciones a Slack
- Validaciones y detección de anomalías
"""
import os
import csv
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from time import perf_counter
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pendulum
from airflow import DAG
from airflow.decorators import task, dag
from airflow.models import Variable
from airflow.exceptions import AirflowFailException
from airflow.operators.python import get_current_context
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
from airflow.operators.python import ShortCircuitOperator
from plugins.etl_notifications import notify_email, notify_slack

# Intentar importar dependencias opcionales
try:
    from airflow.stats import Stats  # type: ignore
except Exception:
    Stats = None  # type: ignore

try:
    from plugins.db import get_conn  # type: ignore
except Exception:
    get_conn = None  # type: ignore

# Verificar disponibilidad de boto3 para S3
try:
    import boto3  # type: ignore
    _BOTO3_AVAILABLE = True
except ImportError:
    _BOTO3_AVAILABLE = False

# Verificar disponibilidad de MLflow
try:
    import mlflow  # type: ignore
    _MLFLOW_AVAILABLE = True
except ImportError:
    _MLFLOW_AVAILABLE = False

logger = logging.getLogger(__name__)

STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")
REPORT_OUTPUT_DIR = os.environ.get("STRIPE_REPORT_OUTPUT_DIR", "/tmp/stripe_reports")
ACCOUNTING_EMAIL = os.environ.get("ACCOUNTING_EMAIL", "")
QUICKBOOKS_ACCOUNT_MAP = {
    "pago": os.environ.get("QUICKBOOKS_ACCOUNT_PAYMENTS", "Ingresos de Ventas"),
    "reembolso": os.environ.get("QUICKBOOKS_ACCOUNT_REFUNDS", "Reembolsos"),
    "tarifa": os.environ.get("QUICKBOOKS_ACCOUNT_FEES", "Tarifas de Stripe"),
}

# Configuración de pools y recursos
FINANCE_POOL = os.environ.get("FINANCE_POOL", "default_pool")
REPORTING_POOL = os.environ.get("REPORTING_POOL", "default_pool")


def _fetch_stripe_api(
    stripe_key: str,
    endpoint: str,
    start_timestamp: int,
    end_timestamp: int,
    max_pages: int = 1000,
) -> List[Dict[str, Any]]:
    """
    Obtiene datos de la API de Stripe con paginación.
    
    Args:
        stripe_key: API key de Stripe
        endpoint: Endpoint de la API (ej: "charges", "refunds")
        start_timestamp: Timestamp de inicio
        end_timestamp: Timestamp de fin
        max_pages: Número máximo de páginas a obtener (límite de seguridad)
    
    Returns:
        Lista de todas las transacciones obtenidas
    """
    # Configurar session con retry automático
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {stripe_key}"})
    
    # Configurar retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    params = {
        "limit": 100,
        "created[gte]": start_timestamp,
        "created[lte]": end_timestamp,
    }
    
    all_items = []
    starting_after = None
    page_count = 0
    
    while page_count < max_pages:
        p = dict(params)
        if starting_after:
            p["starting_after"] = starting_after
            
        try:
            response = session.get(
                f"https://api.stripe.com/v1/{endpoint}",
                params=p,
                timeout=60  # Timeout más largo para grandes volúmenes
            )
            
            # Manejar rate limiting
            if response.status_code == 429:
                if _handle_stripe_rate_limit(response):
                    # Reintentar después de esperar
                    continue
            
            response.raise_for_status()
            data = response.json()
            
            items = data.get("data", [])
            all_items.extend(items)
            
            if data.get("has_more") and items:
                starting_after = items[-1].get("id")
                page_count += 1
            else:
                break
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching {endpoint} page {page_count + 1}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Stripe {endpoint}: {e}", exc_info=True)
            raise
    
    if page_count >= max_pages:
        logger.warning(
            f"Reached max pages limit ({max_pages}) for {endpoint}. "
            f"Total items fetched: {len(all_items)}"
        )
    
    return all_items


def _fetch_stripe_customer(stripe_key: str, customer_id: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
    """Obtiene información de un cliente de Stripe con caché."""
    if not customer_id or not customer_id.startswith("cus_"):
        return None
    
    # Verificar caché
    if use_cache and customer_id in _customer_cache:
        return _customer_cache[customer_id]
    
    try:
        session = requests.Session()
        session.headers.update({"Authorization": f"Bearer {stripe_key}"})
        response = session.get(
            f"https://api.stripe.com/v1/customers/{customer_id}",
            timeout=30
        )
        response.raise_for_status()
        customer_data = response.json()
        
        # Guardar en caché
        if use_cache:
            _customer_cache[customer_id] = customer_data
        
        return customer_data
    except requests.exceptions.RequestException as e:
        logger.warning(f"Error fetching customer {customer_id}: {e}")
        if use_cache:
            _customer_cache[customer_id] = None
        return None


def _get_customer_email(charge: Dict[str, Any], stripe_key: Optional[str] = None, use_cache: bool = True) -> str:
    """Extrae el email del cliente de un cargo de Stripe con caché."""
    # Intentar obtener el email de diferentes lugares
    billing_details = charge.get("billing_details", {})
    email = billing_details.get("email", "")
    
    if not email:
        # Intentar obtener de metadata
        metadata = charge.get("metadata", {})
        email = metadata.get("customer_email", "")
    
    # Si hay customer ID y tenemos la API key, intentar obtener el email del customer
    if not email and charge.get("customer") and stripe_key:
        customer = _fetch_stripe_customer(stripe_key, charge.get("customer"), use_cache=use_cache)
        if customer:
            email = customer.get("email", "")
    
    if not email and charge.get("customer"):
        # Fallback: usar el ID del customer
        email = f"customer_{charge.get('customer')}"
    
    return email or "No disponible"


def _calculate_fee_from_balance_transaction(bt: Dict[str, Any]) -> Dict[str, float]:
    """Calcula las tarifas desde una balance transaction."""
    fee_amount = abs(bt.get("fee", 0)) / 100.0
    fee_details = bt.get("fee_details", [])
    
    # Sumar todas las tarifas desglosadas
    total_fee = sum(
        abs(fd.get("amount", 0)) / 100.0
        for fd in fee_details
    ) if fee_details else fee_amount
    
    return {
        "gross": total_fee if total_fee > 0 else fee_amount,
        "net": abs(bt.get("net", 0)) / 100.0,
    }


def _send_email_with_attachment(
    to: str,
    subject: str,
    body: str,
    html: Optional[str] = None,
    attachment_path: Optional[str] = None,
    attachment_name: Optional[str] = None,
) -> None:
    """
    Envía un email con un archivo adjunto.
    
    Args:
        to: Email destinatario
        subject: Asunto del email
        body: Cuerpo en texto plano
        html: Cuerpo HTML (opcional)
        attachment_path: Ruta al archivo a adjuntar
        attachment_name: Nombre del archivo adjunto
    """
    smtp_host = os.getenv("SMTP_HOST")
    if not smtp_host:
        logger.warning("SMTP_HOST not configured, skipping email")
        return
    
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "airflow@example.com")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = to
        
        # Añadir cuerpo del mensaje
        part_text = MIMEText(body, "plain")
        msg.attach(part_text)
        
        if html:
            part_html = MIMEText(html, "html")
            msg.attach(part_html)
        
        # Añadir adjunto si existe
        if attachment_path and Path(attachment_path).exists():
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f'attachment; filename= "{attachment_name or Path(attachment_path).name}"',
                )
                msg.attach(part)
        
        # Enviar email
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        if smtp_password:
            server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, [to], msg.as_string())
        server.quit()
        
        logger.info(f"Email sent successfully with attachment to {to}")
        
    except Exception as e:
        logger.error(f"Failed to send email with attachment: {e}", exc_info=True)
        raise


def _check_idempotency(date_range_key: str) -> bool:
    """Verifica si el reporte ya fue generado para este rango de fechas."""
    try:
        lock_key = f"stripe_report:{date_range_key}"
        lock_data = Variable.get(lock_key, default_var=None)
        if lock_data:
            data = json.loads(lock_data)
            expires_at = data.get("expires_at", 0)
            now = pendulum.now("UTC").int_timestamp
            if expires_at > now:
                logger.info(f"Report already generated for date range: {date_range_key}")
                return True
        return False
    except Exception as e:
        logger.warning(f"Failed to check idempotency: {e}")
        return False


def _set_idempotency_lock(date_range_key: str, ttl_hours: int = 48) -> None:
    """Establece un lock de idempotencia para el reporte."""
    try:
        lock_key = f"stripe_report:{date_range_key}"
        expires_at = pendulum.now("UTC").int_timestamp + (ttl_hours * 3600)
        data = json.dumps({
            "expires_at": expires_at,
            "created_at": pendulum.now("UTC").int_timestamp,
            "date_range": date_range_key,
        })
        Variable.set(lock_key, data)
        logger.info(f"Idempotency lock set for date range: {date_range_key}")
    except Exception as e:
        logger.warning(f"Failed to set idempotency lock: {e}")


def _validate_csv_data(rows: List[Dict[str, Any]]) -> tuple[bool, List[str]]:
    """
    Valida la calidad de los datos del CSV antes de generarlo.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    if not rows:
        errors.append("No hay filas para validar")
        return False, errors
    
    # Validar que todas las filas tengan campos requeridos
    required_fields = ["fecha", "tipo", "cliente", "monto_bruto", "monto_neto", "cuenta_asignada"]
    
    for idx, row in enumerate(rows, start=1):
        for field in required_fields:
            if field not in row or row[field] is None or str(row[field]).strip() == "":
                errors.append(f"Fila {idx}: campo '{field}' está vacío o faltante")
        
        # Validar formato de fecha
        fecha = row.get("fecha", "")
        if fecha:
            try:
                datetime.strptime(str(fecha), "%Y-%m-%d")
            except ValueError:
                errors.append(f"Fila {idx}: fecha inválida '{fecha}', debe ser YYYY-MM-DD")
        
        # Validar tipos permitidos
        tipo = row.get("tipo", "").lower()
        if tipo not in ["pago", "reembolso", "tarifa"]:
            errors.append(f"Fila {idx}: tipo inválido '{tipo}', debe ser: pago, reembolso o tarifa")
        
        # Validar montos numéricos
        try:
            monto_bruto = float(str(row.get("monto_bruto", "0")).replace(",", ""))
            monto_neto = float(str(row.get("monto_neto", "0")).replace(",", ""))
            
            if monto_bruto < 0:
                errors.append(f"Fila {idx}: monto_bruto no puede ser negativo ({monto_bruto})")
            
            if monto_neto < 0:
                errors.append(f"Fila {idx}: monto_neto no puede ser negativo ({monto_neto})")
            
            # Validar que monto_neto <= monto_bruto (excepto para tarifas que pueden ser iguales)
            if tipo != "tarifa" and monto_neto > monto_bruto:
                errors.append(
                    f"Fila {idx}: monto_neto ({monto_neto}) no puede ser mayor que monto_bruto ({monto_bruto})"
                )
        except (ValueError, TypeError) as e:
            errors.append(f"Fila {idx}: error parseando montos: {e}")
    
    return len(errors) == 0, errors


def _calculate_csv_checksum(csv_path: str) -> str:
    """Calcula el checksum MD5 del archivo CSV."""
    import hashlib
    
    hash_md5 = hashlib.md5()
    with open(csv_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def _validate_balance_reconciliation(
    rows: List[Dict[str, Any]], 
    charges: List[Dict[str, Any]], 
    refunds: List[Dict[str, Any]],
    balance_transactions: List[Dict[str, Any]]
) -> tuple[bool, List[str]]:
    """
    Valida que los totales del CSV coincidan con los datos de Stripe.
    """
    warnings = []
    
    # Calcular totales del CSV
    csv_total_pagos = sum(
        float(str(r.get("monto_neto", "0")).replace(",", ""))
        for r in rows if r.get("tipo", "").lower() == "pago"
    )
    
    csv_total_reembolsos = sum(
        float(str(r.get("monto_neto", "0")).replace(",", ""))
        for r in rows if r.get("tipo", "").lower() == "reembolso"
    )
    
    # Calcular totales de Stripe
    stripe_total_pagos = sum(
        (ch.get("amount", 0) or 0) / 100.0
        for ch in charges
        if ch.get("status") == "succeeded"
    )
    
    stripe_total_refunds = sum(
        abs((ref.get("amount", 0) or 0) / 100.0)
        for ref in refunds
    )
    
    # Comparar (permitir pequeñas diferencias por tarifas)
    tolerance = 0.01  # 1 centavo
    
    if abs(csv_total_pagos - stripe_total_pagos) > tolerance:
        warnings.append(
            f"Posible discrepancia en pagos: CSV=${csv_total_pagos:.2f} vs Stripe=${stripe_total_pagos:.2f} "
            f"(diff=${abs(csv_total_pagos - stripe_total_pagos):.2f})"
        )
    
    if abs(csv_total_reembolsos - stripe_total_refunds) > tolerance:
        warnings.append(
            f"Posible discrepancia en reembolsos: CSV=${csv_total_reembolsos:.2f} vs Stripe=${stripe_total_refunds:.2f} "
            f"(diff=${abs(csv_total_reembolsos - stripe_total_refunds):.2f})"
        )
    
    return len(warnings) == 0, warnings


# Cache para customers (evitar múltiples llamadas a API)
_customer_cache: Dict[str, Optional[Dict[str, Any]]] = {}


def _retry_with_exponential_backoff(
    func,
    *args,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    multiplier: float = 2.0,
    **kwargs
):
    """
    Ejecuta una función con retry exponencial.
    
    Args:
        func: Función a ejecutar
        max_retries: Número máximo de reintentos
        initial_delay: Delay inicial en segundos
        max_delay: Delay máximo en segundos
        multiplier: Multiplicador para el backoff exponencial
        *args, **kwargs: Argumentos para la función
    
    Returns:
        Resultado de la función
    
    Raises:
        Última excepción si todos los reintentos fallan
    """
    last_exception = None
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
            last_exception = e
            if attempt < max_retries - 1:
                wait_time = min(delay, max_delay)
                logger.warning(
                    f"Intento {attempt + 1}/{max_retries} falló, reintentando en {wait_time:.1f}s",
                    extra={"error": str(e), "attempt": attempt + 1, "wait_time": wait_time},
                )
                time.sleep(wait_time)
                delay *= multiplier
            else:
                logger.error(f"Todos los {max_retries} intentos fallaron", extra={"error": str(e)})
        except Exception as e:
            # Errores no relacionados con requests no se reintentan
            raise
    
    raise last_exception


def _handle_stripe_rate_limit(response: requests.Response) -> bool:
    """
    Maneja rate limiting de Stripe API.
    
    Returns:
        True si se debe reintentar, False si no
    """
    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            wait_time = int(retry_after)
            logger.warning(f"Rate limit alcanzado, esperando {wait_time} segundos")
            time.sleep(min(wait_time, 300))  # Máximo 5 minutos
            return True
        else:
            # Esperar tiempo predeterminado
            time.sleep(60)
            return True
    return False


def _check_volume_anomaly(
    current_count: int,
    historical_avg: Optional[float] = None,
    threshold_pct: float = 50.0
) -> tuple[bool, Optional[str]]:
    """
    Detecta anomalías en el volumen de transacciones.
    
    Returns:
        (is_anomaly, warning_message)
    """
    if historical_avg is None or historical_avg == 0:
        return False, None
    
    change_pct = abs((current_count - historical_avg) / historical_avg) * 100
    
    if change_pct > threshold_pct:
        direction = "aumento" if current_count > historical_avg else "caída"
        message = (
            f"Anomalía de volumen detectada: {direction} del {change_pct:.1f}% "
            f"({current_count} vs {historical_avg:.1f} promedio)"
        )
        return True, message
    
    return False, None


def _check_circuit_breaker(dag_id: str, threshold: int = 5, reset_minutes: int = 30) -> bool:
    """
    Verifica si el circuit breaker está abierto.
    
    Returns:
        True si el circuit breaker está abierto (demasiados fallos recientes)
    """
    try:
        lock_key = f"circuit_breaker:{dag_id}"
        fail_count_key = f"circuit_breaker_fails:{dag_id}"
        
        last_reset = Variable.get(f"{lock_key}_reset", default_var=None)
        if last_reset:
            reset_time = int(last_reset)
            now = pendulum.now("UTC").int_timestamp
            if now - reset_time > reset_minutes * 60:
                # Resetear contador
                Variable.delete(fail_count_key)
                Variable.set(f"{lock_key}_reset", str(now))
                return False
        
        fail_count = int(Variable.get(fail_count_key, default_var="0"))
        return fail_count >= threshold
    except Exception:
        return False


def _record_circuit_breaker_failure(dag_id: str) -> None:
    """Registra un fallo en el circuit breaker."""
    try:
        fail_count_key = f"circuit_breaker_fails:{dag_id}"
        current = int(Variable.get(fail_count_key, default_var="0"))
        Variable.set(fail_count_key, str(current + 1))
    except Exception:
        pass


def _reset_circuit_breaker(dag_id: str) -> None:
    """Resetea el circuit breaker después de un éxito."""
    try:
        fail_count_key = f"circuit_breaker_fails:{dag_id}"
        lock_key = f"circuit_breaker:{dag_id}"
        Variable.delete(fail_count_key)
        Variable.set(f"{lock_key}_reset", str(pendulum.now("UTC").int_timestamp))
    except Exception:
        pass


@dag(
    dag_id="stripe_quickbooks_report",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="0 23 * * *",  # Diario al final del día (23:00 UTC)
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
    max_active_tasks=8,
    concurrency=8,
    render_template_as_native_obj=True,
    on_success_callback=lambda context: (
        _reset_circuit_breaker("stripe_quickbooks_report"),
        notify_slack(":white_check_mark: stripe_quickbooks_report DAG succeeded")
    ),
    on_failure_callback=lambda context: (
        _record_circuit_breaker_failure("stripe_quickbooks_report"),
        notify_slack(":x: stripe_quickbooks_report DAG failed")
    ),
    params={
        "fecha_inicio": None,  # Formato: YYYY-MM-DD, si es None usa fecha de ayer
        "fecha_fin": None,  # Formato: YYYY-MM-DD, si es None usa fecha de hoy
        "email_destinatario": None,  # Email para enviar el resumen
        "output_dir": None,  # Directorio para guardar el CSV
        "skip_if_exists": True,  # Saltar si ya existe el reporte
        "attach_csv": True,  # Adjuntar CSV al email
        "upload_to_s3": False,  # Subir CSV a S3
        "save_to_db": True,  # Guardar métricas en base de datos
        "notify_slack": True,  # Enviar notificación a Slack
        "track_metrics": True,  # Trackear métricas con Stats
        "validate_data": True,  # Validar calidad de datos antes de generar CSV
        "validate_balance": True,  # Validar reconciliación con datos de Stripe
        "enable_cache": True,  # Usar caché para customers
    },
    description="Extrae transacciones de Stripe y genera reporte CSV para QuickBooks",
    tags=["finance", "stripe", "quickbooks", "reporting"],
    doc_md="""
    # Reporte Stripe a QuickBooks
    
    Este DAG extrae todas las transacciones de Stripe (pagos, reembolsos, tarifas)
    en un rango de fechas y genera un reporte CSV compatible con QuickBooks.
    
    ## Características mejoradas:
    
    - Extracción robusta con manejo de paginación
    - Validación de datos y deduplicación
    - Adjunto automático del CSV al email
    - Idempotencia para evitar duplicados
    - Mejor extracción de emails de clientes
    - Manejo de múltiples monedas
    - Resumen detallado por tipo de transacción
    
    ## Parámetros:
    
    - `fecha_inicio`: Fecha de inicio en formato YYYY-MM-DD (default: ayer)
    - `fecha_fin`: Fecha de fin en formato YYYY-MM-DD (default: hoy)
    - `email_destinatario`: Email para enviar el resumen (opcional)
    - `output_dir`: Directorio para guardar el CSV (default: /tmp/stripe_reports)
    - `skip_if_exists`: Saltar si ya existe el reporte (default: true)
    - `attach_csv`: Adjuntar CSV al email (default: true)
    
    ## Variables de entorno requeridas:
    
    - `STRIPE_API_KEY`: API key de Stripe
    - `QUICKBOOKS_ACCOUNT_PAYMENTS`: Nombre de cuenta en QuickBooks para pagos
    - `QUICKBOOKS_ACCOUNT_REFUNDS`: Nombre de cuenta en QuickBooks para reembolsos
    - `QUICKBOOKS_ACCOUNT_FEES`: Nombre de cuenta en QuickBooks para tarifas
    
    ## Variables de entorno opcionales:
    
    - `STRIPE_REPORT_OUTPUT_DIR`: Directorio para guardar reportes
    - `ACCOUNTING_EMAIL`: Email del departamento de contabilidad
    - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`: Configuración SMTP
    - `STRIPE_REPORT_S3_BUCKET`: Bucket S3 para almacenamiento (opcional)
    - `STRIPE_REPORT_S3_PREFIX`: Prefijo para archivos en S3 (default: stripe_reports)
    - `MLFLOW_TRACKING_URI`: URI de MLflow para tracking (opcional)
    - `FINANCE_POOL`: Pool para tareas de finanzas (default: default_pool)
    - `REPORTING_POOL`: Pool para tareas de reporting (default: default_pool)
    
    ## Arquitectura:
    
    El DAG está organizado en 4 fases con TaskGroups:
    
    1. **Preparación**: Health check, preparación de fechas, idempotencia
    2. **Extracción y Procesamiento**: Extracción de Stripe, generación de CSV, cálculo de resumen
    3. **Distribución y Notificaciones**: Email, S3, DB, Slack, métricas, anomalías (paralelas)
    4. **Finalización**: Summary final, idempotencia
    
    Las tareas no críticas usan `trigger_rule="none_failed_min_one_success"` para no bloquear el flujo.
    """,
)
def stripe_quickbooks_report() -> None:
    """
    DAG principal mejorado para extraer transacciones de Stripe y generar reporte CSV.
    """
    
    @task(
        task_id="health_check",
        execution_timeout=timedelta(minutes=2),
        pool=FINANCE_POOL,
        priority_weight=10,
    )
    def health_check() -> Dict[str, Any]:
        """
        Health check antes de ejecutar el DAG.
        Verifica configuración y disponibilidad de servicios.
        """
        checks = {
            "status": "ok",
            "checks": {},
            "timestamp": pendulum.now("UTC").isoformat(),
        }
        
        # Verificar API key de Stripe
        stripe_key = STRIPE_API_KEY.strip()
        if not stripe_key:
            checks["status"] = "error"
            checks["checks"]["stripe_api_key"] = {
                "status": "error",
                "message": "STRIPE_API_KEY no configurado",
            }
        else:
            checks["checks"]["stripe_api_key"] = {
                "status": "ok",
                "configured": True,
            }
        
        # Verificar circuit breaker
        cb_open = _check_circuit_breaker("stripe_quickbooks_report")
        if cb_open:
            checks["status"] = "degraded"
            checks["checks"]["circuit_breaker"] = {
                "status": "warning",
                "message": "Circuit breaker está abierto - fallos recientes detectados",
            }
        else:
            checks["checks"]["circuit_breaker"] = {
                "status": "ok",
            }
        
        # Verificar directorio de salida
        output_dir = REPORT_OUTPUT_DIR
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            # Verificar que es escribible
            test_file = Path(output_dir) / ".test_write"
            test_file.touch()
            test_file.unlink()
            checks["checks"]["output_dir"] = {
                "status": "ok",
                "path": output_dir,
            }
        except Exception as e:
            checks["status"] = "error"
            checks["checks"]["output_dir"] = {
                "status": "error",
                "message": f"No se puede escribir en {output_dir}: {e}",
            }
        
        # Verificar configuración de email (opcional)
        smtp_host = os.getenv("SMTP_HOST")
        if not smtp_host:
            checks["checks"]["email"] = {
                "status": "warning",
                "message": "SMTP_HOST no configurado - emails no se enviarán",
            }
        else:
            checks["checks"]["email"] = {
                "status": "ok",
            }
        
        # Verificar base de datos (opcional)
        if get_conn is None:
            checks["checks"]["database"] = {
                "status": "warning",
                "message": "plugins.db.get_conn no disponible - persistencia en DB deshabilitada",
            }
        else:
            try:
                with get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT 1")
                checks["checks"]["database"] = {
                    "status": "ok",
                }
            except Exception as e:
                checks["checks"]["database"] = {
                    "status": "warning",
                    "message": f"Conexión a DB falló: {e}",
                }
        
        if checks["status"] == "error":
            logger.error("Health check falló", extra=checks)
            raise AirflowFailException(f"Health check falló: {json.dumps(checks, indent=2)}")
        elif checks["status"] == "degraded":
            logger.warning("Health check con advertencias", extra=checks)
        else:
            logger.info("Health check exitoso", extra=checks)
        
        return checks
    
    @task(
        task_id="preparar_fechas",
        pool=FINANCE_POOL,
        priority_weight=9,
    )
    def preparar_fechas(**context) -> Dict[str, Any]:
        """Prepara las fechas de inicio y fin para la extracción."""
        params = context.get("params", {})
        ctx = context
        
        # Obtener fechas de los parámetros o usar defaults
        fecha_inicio_str = params.get("fecha_inicio")
        fecha_fin_str = params.get("fecha_fin")
        
        if fecha_inicio_str:
            fecha_inicio = pendulum.parse(fecha_inicio_str, tz="UTC")
        else:
            # Default: ayer
            fecha_inicio = ctx["data_interval_start"].subtract(days=1)
        
        if fecha_fin_str:
            fecha_fin = pendulum.parse(fecha_fin_str, tz="UTC")
        else:
            # Default: hoy
            fecha_fin = ctx["data_interval_end"]
        
        # Asegurar que fecha_inicio <= fecha_fin
        if fecha_inicio > fecha_fin:
            fecha_inicio = fecha_fin.subtract(days=1)
        
        # Validar que el rango no sea demasiado grande (máx 90 días)
        days_diff = (fecha_fin - fecha_inicio).days
        if days_diff > 90:
            logger.warning(f"Date range is large ({days_diff} days), this may take a while")
        
        # Convertir a timestamps para Stripe API
        start_timestamp = int(fecha_inicio.start_of("day").timestamp())
        end_timestamp = int(fecha_fin.end_of("day").timestamp())
        
        date_range_key = f"{fecha_inicio.to_date_string()}_{fecha_fin.to_date_string()}"
        
        logger.info(
            "Fechas preparadas",
            extra={
                "fecha_inicio": fecha_inicio.to_date_string(),
                "fecha_fin": fecha_fin.to_date_string(),
                "days": days_diff,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "date_range_key": date_range_key,
            },
        )
        
        return {
            "fecha_inicio": fecha_inicio.to_date_string(),
            "fecha_fin": fecha_fin.to_date_string(),
            "start_timestamp": start_timestamp,
            "end_timestamp": end_timestamp,
            "date_range_key": date_range_key,
            "params": params,
        }
    
    @task(
        task_id="verificar_idempotencia",
        pool=FINANCE_POOL,
        priority_weight=8,
    )
    def verificar_idempotencia(fechas: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica si el reporte ya fue generado."""
        date_range_key = fechas["date_range_key"]
        params = fechas.get("params", {})
        skip_if_exists = params.get("skip_if_exists", True)
        
        if skip_if_exists and _check_idempotency(date_range_key):
            raise AirflowFailException(
                f"Report already exists for date range {date_range_key}. "
                "Set skip_if_exists=false to regenerate."
            )
        
        return fechas
    
    @task(
        task_id="extraer_transacciones_stripe",
        execution_timeout=timedelta(minutes=30),
        pool=FINANCE_POOL,
        priority_weight=7,
        retries=3,
    )
    def extraer_transacciones_stripe(fechas: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae todas las transacciones de Stripe (pagos, reembolsos, tarifas)."""
        start_time = perf_counter()
        
        stripe_key = STRIPE_API_KEY.strip()
        
        if not stripe_key:
            raise AirflowFailException("STRIPE_API_KEY no configurado")
        
        start_timestamp = fechas["start_timestamp"]
        end_timestamp = fechas["end_timestamp"]
        
        logger.info("Extrayendo transacciones de Stripe", extra={"start": start_timestamp, "end": end_timestamp})
        
        # Extraer cargos (pagos) - solo los exitosos
        try:
            charges = _fetch_stripe_api(stripe_key, "charges", start_timestamp, end_timestamp)
            logger.info(f"Extraídos {len(charges)} cargos de Stripe")
        except Exception as e:
            logger.error(f"Error al extraer cargos: {e}", exc_info=True)
            raise AirflowFailException(f"Error al extraer cargos: {e}")
        
        # Extraer reembolsos
        try:
            refunds = _fetch_stripe_api(stripe_key, "refunds", start_timestamp, end_timestamp)
            logger.info(f"Extraídos {len(refunds)} reembolsos de Stripe")
        except Exception as e:
            logger.error(f"Error al extraer reembolsos: {e}", exc_info=True)
            # Continuar aunque falle, los reembolsos pueden no ser críticos
            refunds = []
        
        # Extraer transacciones de balance (para tarifas)
        try:
            balance_transactions = _fetch_stripe_api(
                stripe_key, "balance_transactions", start_timestamp, end_timestamp
            )
            logger.info(f"Extraídas {len(balance_transactions)} transacciones de balance de Stripe")
        except Exception as e:
            logger.error(f"Error al extraer balance transactions: {e}", exc_info=True)
            balance_transactions = []
        
        duration_ms = int((perf_counter() - start_time) * 1000)
        total_items = len(charges) + len(refunds) + len(balance_transactions)
        
        # Verificar anomalías de volumen
        if get_conn:
            try:
                with get_conn() as conn:
                    with conn.cursor() as cur:
                        # Obtener promedio histórico de los últimos 30 días
                        cur.execute("""
                            SELECT AVG(count_pagos + count_reembolsos + count_tarifas) as avg_count
                            FROM finance.stripe_quickbooks_reports
                            WHERE fecha_fin < CURRENT_DATE
                            AND fecha_fin >= CURRENT_DATE - INTERVAL '30 days';
                        """)
                        row = cur.fetchone()
                        if row and row[0]:
                            is_anomaly, warning = _check_volume_anomaly(
                                total_items,
                                float(row[0]),
                                threshold_pct=50.0
                            )
                            if is_anomaly and warning:
                                logger.warning(f"Anomalía de volumen: {warning}")
            except Exception:
                pass  # No crítico
        
        logger.info(
            "Extracción de Stripe completada",
            extra={
                "duration_ms": duration_ms,
                "total_items": total_items,
                "charges": len(charges),
                "refunds": len(refunds),
                "balance_transactions": len(balance_transactions),
                "throughput_items_per_sec": total_items / (duration_ms / 1000.0) if duration_ms > 0 else 0,
            },
        )
        
        try:
            if Stats:
                Stats.timing("stripe_report.extract.duration_ms", duration_ms)
                Stats.gauge("stripe_report.extract.total_items", total_items)
                if duration_ms > 0:
                    throughput = total_items / (duration_ms / 1000.0)
                    Stats.gauge("stripe_report.extract.throughput_items_per_sec", throughput)
        except Exception:
            pass
        
        return {
            **fechas,
            "charges": charges,
            "refunds": refunds,
            "balance_transactions": balance_transactions,
            "stripe_key": stripe_key,  # Para uso en procesamiento
            "extraction_duration_ms": duration_ms,
        }
    
    @task(
        task_id="procesar_y_generar_csv",
        execution_timeout=timedelta(minutes=20),
        pool=REPORTING_POOL,
        priority_weight=6,
        sla=timedelta(minutes=25),
    )
    def procesar_y_generar_csv(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa las transacciones y genera el archivo CSV para QuickBooks.
        """
        start_time = perf_counter()
        charges = data.get("charges", [])
        refunds = data.get("refunds", [])
        balance_transactions = data.get("balance_transactions", [])
        fecha_inicio = data["fecha_inicio"]
        fecha_fin = data["fecha_fin"]
        stripe_key = data.get("stripe_key")
        
        # Preparar directorio de salida
        params = data.get("params", {}) or {}
        output_dir = params.get("output_dir") or REPORT_OUTPUT_DIR
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Configuración de caché
        use_cache = params.get("enable_cache", True)
        validate_data = params.get("validate_data", True)
        validate_balance = params.get("validate_balance", True)
        
        # Crear mapa de tarifas por transacción usando balance_transactions
        fees_map: Dict[str, Dict[str, float]] = {}
        charges_with_fees: Set[str] = set()
        
        for bt in balance_transactions:
            bt_type = bt.get("type")
            source_id = bt.get("source")
            
            if bt_type == "charge" and source_id:
                # Tarifa asociada a un cargo
                fee_info = _calculate_fee_from_balance_transaction(bt)
                fees_map[source_id] = fee_info
                charges_with_fees.add(source_id)
            elif bt_type in ("application_fee", "stripe_fee") and source_id:
                # Tarifa independiente
                fees_map[source_id] = _calculate_fee_from_balance_transaction(bt)
        
        # Crear mapa de cargos por ID para búsqueda rápida
        charges_map = {ch.get("id"): ch for ch in charges}
        
        # Procesar cargos (pagos)
        rows = []
        processed_charges: Set[str] = set()
        
        for charge in charges:
            charge_id = charge.get("id")
            if not charge_id or charge_id in processed_charges:
                continue
            
            # Solo procesar cargos exitosos
            if charge.get("status") != "succeeded":
                continue
            
            try:
                amount = (charge.get("amount", 0) or 0) / 100.0
                currency = charge.get("currency", "usd").upper()
                created = datetime.fromtimestamp(charge.get("created", 0))
                customer_email = _get_customer_email(charge, stripe_key, use_cache=use_cache)
                
                # Obtener tarifa asociada
                fee_info = fees_map.get(charge_id, {"gross": 0.0, "net": amount})
                fee_amount = fee_info.get("gross", 0.0)
                net_amount = max(0.0, amount - fee_amount)
                
                rows.append({
                    "fecha": created.strftime("%Y-%m-%d"),
                    "tipo": "pago",
                    "cliente": customer_email,
                    "monto_bruto": amount,
                    "monto_neto": net_amount,
                    "cuenta_asignada": QUICKBOOKS_ACCOUNT_MAP["pago"],
                    "currency": currency,
                    "stripe_id": charge_id,
                })
                
                processed_charges.add(charge_id)
            except Exception as e:
                logger.warning(f"Error procesando cargo {charge_id}: {e}", exc_info=True)
        
        # Procesar reembolsos
        processed_refunds: Set[str] = set()
        for refund in refunds:
            refund_id = refund.get("id")
            if not refund_id or refund_id in processed_refunds:
                continue
            
            try:
                amount = abs((refund.get("amount", 0) or 0) / 100.0)
                currency = refund.get("currency", "usd").upper()
                created = datetime.fromtimestamp(refund.get("created", 0))
                charge_id = refund.get("charge")
                
                # Intentar obtener email del cliente desde el cargo original
                customer_email = "No disponible"
                if charge_id and charge_id in charges_map:
                    customer_email = _get_customer_email(charges_map[charge_id], stripe_key, use_cache=use_cache)
                
                rows.append({
                    "fecha": created.strftime("%Y-%m-%d"),
                    "tipo": "reembolso",
                    "cliente": customer_email,
                    "monto_bruto": amount,
                    "monto_neto": amount,  # Los reembolsos generalmente no tienen tarifa adicional
                    "cuenta_asignada": QUICKBOOKS_ACCOUNT_MAP["reembolso"],
                    "currency": currency,
                    "stripe_id": refund_id,
                })
                
                processed_refunds.add(refund_id)
            except Exception as e:
                logger.warning(f"Error procesando reembolso {refund_id}: {e}", exc_info=True)
        
        # Procesar tarifas independientes que no estén asociadas a cargos
        processed_fees: Set[str] = set()
        for bt in balance_transactions:
            bt_type = bt.get("type")
            fee_id = bt.get("id")
            
            if fee_id in processed_fees:
                continue
            
            # Incluir tarifas que no sean de tipo "charge" o que sean fees independientes
            if bt_type in ("application_fee", "stripe_fee", "fee"):
                try:
                    amount = abs((bt.get("amount", 0) or 0) / 100.0)
                    fee_info = _calculate_fee_from_balance_transaction(bt)
                    net_amount = fee_info.get("net", amount)
                    created = datetime.fromtimestamp(bt.get("created", 0))
                    
                    # Solo incluir si la tarifa es significativa (> 0)
                    if net_amount > 0:
                        rows.append({
                            "fecha": created.strftime("%Y-%m-%d"),
                            "tipo": "tarifa",
                            "cliente": "Stripe",
                            "monto_bruto": amount,
                            "monto_neto": net_amount,
                            "cuenta_asignada": QUICKBOOKS_ACCOUNT_MAP["tarifa"],
                            "currency": bt.get("currency", "usd").upper(),
                            "stripe_id": fee_id,
                        })
                        processed_fees.add(fee_id)
                except Exception as e:
                    logger.warning(f"Error procesando tarifa {fee_id}: {e}", exc_info=True)
        
        # Ordenar por fecha y luego por tipo
        rows.sort(key=lambda x: (x["fecha"], x["tipo"]))
        
        # Validar que hay datos
        if not rows:
            logger.warning("No se encontraron transacciones para el período especificado")
        
        # Validar calidad de datos si está habilitado
        validation_errors = []
        validation_warnings = []
        
        if validate_data:
            is_valid, errors = _validate_csv_data(rows)
            if not is_valid:
                validation_errors.extend(errors)
                logger.error(f"Validación de datos falló con {len(errors)} errores")
                for error in errors[:10]:  # Log primeros 10 errores
                    logger.error(f"  - {error}")
                
                if len(errors) > 10:
                    logger.error(f"  ... y {len(errors) - 10} errores más")
        
        # Validar reconciliación de balance si está habilitado
        if validate_balance and not validation_errors:
            balance_ok, warnings = _validate_balance_reconciliation(
                rows, charges, refunds, balance_transactions
            )
            if not balance_ok:
                validation_warnings.extend(warnings)
                logger.warning(f"Validación de balance detectó {len(warnings)} advertencias")
                for warning in warnings:
                    logger.warning(f"  - {warning}")
        
        # Si hay errores críticos, fallar el DAG
        if validation_errors:
            error_summary = "\n".join(validation_errors[:20])
            raise AirflowFailException(
                f"Validación de datos falló con {len(validation_errors)} errores:\n{error_summary}"
            )
        
        # Generar CSV
        csv_filename = f"stripe_report_{fecha_inicio}_to_{fecha_fin}.csv"
        csv_path = Path(output_dir) / csv_filename
        
        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "fecha",
                "tipo",
                "cliente",
                "monto_bruto",
                "monto_neto",
                "cuenta_asignada",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in rows:
                writer.writerow({
                    "fecha": row["fecha"],
                    "tipo": row["tipo"],
                    "cliente": row["cliente"],
                    "monto_bruto": f"{row['monto_bruto']:.2f}",
                    "monto_neto": f"{row['monto_neto']:.2f}",
                    "cuenta_asignada": row["cuenta_asignada"],
                })
        
        file_size = csv_path.stat().st_size
        
        # Calcular checksum del CSV
        csv_checksum = _calculate_csv_checksum(str(csv_path))
        
        duration_ms = int((perf_counter() - start_time) * 1000)
        
        logger.info(
            "CSV generado exitosamente",
            extra={
                "csv_path": str(csv_path),
                "file_size_bytes": file_size,
                "csv_checksum": csv_checksum,
                "total_rows": len(rows),
                "total_pagos": sum(1 for r in rows if r["tipo"] == "pago"),
                "total_reembolsos": sum(1 for r in rows if r["tipo"] == "reembolso"),
                "total_tarifas": sum(1 for r in rows if r["tipo"] == "tarifa"),
                "validation_errors": len(validation_errors),
                "validation_warnings": len(validation_warnings),
                "processing_duration_ms": duration_ms,
            },
        )
        
        try:
            if Stats:
                Stats.timing("stripe_report.process.duration_ms", duration_ms)
                Stats.gauge("stripe_report.process.total_rows", len(rows))
        except Exception:
            pass
        
        return {
            **data,
            "csv_path": str(csv_path),
            "csv_filename": csv_filename,
            "csv_checksum": csv_checksum,
            "rows": rows,
            "file_size_bytes": file_size,
            "validation_errors": validation_errors,
            "validation_warnings": validation_warnings,
            "processing_duration_ms": duration_ms,
            "params": params,
        }
    
    @task(
        task_id="calcular_resumen",
        pool=REPORTING_POOL,
        priority_weight=5,
    )
    def calcular_resumen(data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula el resumen de transacciones con desglose por moneda."""
        rows = data.get("rows", [])
        
        total_pagos = 0.0
        total_reembolsos = 0.0
        total_tarifas = 0.0
        
        count_pagos = 0
        count_reembolsos = 0
        count_tarifas = 0
        
        # Agrupar por moneda
        totals_by_currency: Dict[str, Dict[str, float]] = {}
        
        for row in rows:
            tipo = row["tipo"]
            monto_bruto = float(row["monto_bruto"]) if isinstance(row["monto_bruto"], str) else row["monto_bruto"]
            monto_neto = float(row["monto_neto"]) if isinstance(row["monto_neto"], str) else row["monto_neto"]
            currency = row.get("currency", "USD")
            
            if tipo == "pago":
                total_pagos += monto_neto
                count_pagos += 1
            elif tipo == "reembolso":
                total_reembolsos += monto_neto
                count_reembolsos += 1
            elif tipo == "tarifa":
                total_tarifas += monto_neto
                count_tarifas += 1
            
            # Acumular por moneda
            if currency not in totals_by_currency:
                totals_by_currency[currency] = {"pagos": 0.0, "reembolsos": 0.0, "tarifas": 0.0}
            
            if tipo == "pago":
                totals_by_currency[currency]["pagos"] += monto_neto
            elif tipo == "reembolso":
                totals_by_currency[currency]["reembolsos"] += monto_neto
            elif tipo == "tarifa":
                totals_by_currency[currency]["tarifas"] += monto_neto
        
        resumen = {
            "total_pagos": total_pagos,
            "total_reembolsos": total_reembolsos,
            "total_tarifas": total_tarifas,
            "count_pagos": count_pagos,
            "count_reembolsos": count_reembolsos,
            "count_tarifas": count_tarifas,
            "fecha_inicio": data["fecha_inicio"],
            "fecha_fin": data["fecha_fin"],
            "csv_path": data.get("csv_path"),
            "csv_filename": data.get("csv_filename"),
            "csv_checksum": data.get("csv_checksum", ""),
            "file_size_bytes": data.get("file_size_bytes", 0),
            "totals_by_currency": totals_by_currency,
            "validation_warnings": data.get("validation_warnings", []),
        }
        
        logger.info(
            "Resumen calculado",
            extra={
                "total_pagos": total_pagos,
                "total_reembolsos": total_reembolsos,
                "total_tarifas": total_tarifas,
                "currencies": list(totals_by_currency.keys()),
            },
        )
        
        return {**data, "resumen": resumen}
    
    @task(
        task_id="enviar_resumen",
        pool=REPORTING_POOL,
        priority_weight=4,
        trigger_rule="none_failed_min_one_success",
    )
    def enviar_resumen(data: Dict[str, Any]) -> None:
        """Envía el resumen por email con el CSV adjunto."""
        resumen = data.get("resumen", {})
        params = data.get("params", {})
        
        # Determinar destinatario
        email_destinatario = params.get("email_destinatario") or ACCOUNTING_EMAIL
        
        if not email_destinatario:
            logger.warning("No se configuró email_destinatario, omitiendo envío")
            return
        
        fecha_inicio = resumen["fecha_inicio"]
        fecha_fin = resumen["fecha_fin"]
        total_pagos = resumen["total_pagos"]
        total_reembolsos = resumen["total_reembolsos"]
        total_tarifas = resumen["total_tarifas"]
        csv_path = resumen["csv_path"]
        csv_filename = resumen["csv_filename"]
        csv_checksum = resumen.get("csv_checksum", "")
        totals_by_currency = resumen.get("totals_by_currency", {})
        validation_warnings = resumen.get("validation_warnings", [])
        
        subject = f"Reporte Stripe a QuickBooks - {fecha_inicio} a {fecha_fin}"
        
        # Agregar advertencias si existen
        warnings_text = ""
        if validation_warnings:
            warnings_text = "\n\n⚠️ Advertencias de validación:\n"
            for warning in validation_warnings[:5]:  # Máximo 5 advertencias en el email
                warnings_text += f"- {warning}\n"
            if len(validation_warnings) > 5:
                warnings_text += f"... y {len(validation_warnings) - 5} advertencias más"
        
        # Construir texto del resumen por moneda
        currency_summary = ""
        if totals_by_currency:
            currency_summary = "\n\nDesglose por moneda:\n"
            for currency, totals in totals_by_currency.items():
                currency_summary += f"\n{currency}:\n"
                currency_summary += f"  - Pagos: ${totals['pagos']:,.2f}\n"
                currency_summary += f"  - Reembolsos: ${totals['reembolsos']:,.2f}\n"
                currency_summary += f"  - Tarifas: ${totals['tarifas']:,.2f}\n"
        
        body_text = f"""
Reporte de Transacciones Stripe a QuickBooks

Período: {fecha_inicio} a {fecha_fin}

Resumen Total:
- Total Pagos: ${total_pagos:,.2f} ({resumen['count_pagos']} transacciones)
- Total Reembolsos: ${total_reembolsos:,.2f} ({resumen['count_reembolsos']} transacciones)
- Total Tarifas: ${total_tarifas:,.2f} ({resumen['count_tarifas']} transacciones)
{currency_summary}

El archivo CSV ha sido generado y está adjunto a este email.
Ubicación del archivo: {csv_path}
{warnings_text}

Checksum MD5: {csv_checksum}

Este archivo está listo para ser importado en QuickBooks.
"""
        
        # Construir HTML con tabla de monedas
        currency_table = ""
        if totals_by_currency:
            currency_table = """
            <h4>Desglose por Moneda:</h4>
            <table border="1" cellpadding="5" style="border-collapse: collapse; margin-bottom: 20px;">
                <tr style="background-color: #f0f0f0;">
                    <th>Moneda</th>
                    <th>Pagos</th>
                    <th>Reembolsos</th>
                    <th>Tarifas</th>
                </tr>
            """
            for currency, totals in totals_by_currency.items():
                currency_table += f"""
                <tr>
                    <td><strong>{currency}</strong></td>
                    <td>${totals['pagos']:,.2f}</td>
                    <td>${totals['reembolsos']:,.2f}</td>
                    <td>${totals['tarifas']:,.2f}</td>
                </tr>
                """
            currency_table += "</table>"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Reporte de Transacciones Stripe a QuickBooks</h2>
            <p><strong>Período:</strong> {fecha_inicio} a {fecha_fin}</p>
            
            <h3>Resumen Total:</h3>
            <table border="1" cellpadding="5" style="border-collapse: collapse; margin-bottom: 20px;">
                <tr style="background-color: #f0f0f0;">
                    <th>Tipo</th>
                    <th>Cantidad</th>
                    <th>Total</th>
                </tr>
                <tr>
                    <td>Pagos</td>
                    <td>{resumen['count_pagos']}</td>
                    <td>${total_pagos:,.2f}</td>
                </tr>
                <tr>
                    <td>Reembolsos</td>
                    <td>{resumen['count_reembolsos']}</td>
                    <td>${total_reembolsos:,.2f}</td>
                </tr>
                <tr>
                    <td>Tarifas</td>
                    <td>{resumen['count_tarifas']}</td>
                    <td>${total_tarifas:,.2f}</td>
                </tr>
            </table>
            {currency_table}
            
            <p><strong>Archivo CSV:</strong> {csv_filename}</p>
            <p><strong>Ubicación:</strong> {csv_path}</p>
            <p><strong>Tamaño:</strong> {resumen.get('file_size_bytes', 0):,} bytes</p>
            <p><strong>Checksum MD5:</strong> <code>{csv_checksum}</code></p>
            
            {f"""
            <div style='margin-top: 20px; padding: 10px; background-color: #fff3cd; border-left: 4px solid #ffc107;'>
                <strong>⚠️ Advertencias de validación:</strong>
                <ul>
                    {''.join([f'<li>{w}</li>' for w in validation_warnings[:10]])}
                </ul>
                {f'<p><em>... y {len(validation_warnings) - 10} advertencias más</em></p>' if len(validation_warnings) > 10 else ''}
            </div>
            """ if validation_warnings else ""}
            
            <p style="margin-top: 20px; color: #666;">
                Este archivo está listo para ser importado en QuickBooks.
                El archivo CSV está adjunto a este email.
            </p>
        </body>
        </html>
        """
        
        try:
            attach_csv = params.get("attach_csv", True)
            
            if attach_csv:
                _send_email_with_attachment(
                    to=email_destinatario,
                    subject=subject,
                    body=body_text,
                    html=html_body,
                    attachment_path=csv_path,
                    attachment_name=csv_filename,
                )
            else:
                notify_email(
                    to=email_destinatario,
                    subject=subject,
                    body=body_text,
                    html=html_body,
                )
            
            logger.info("Resumen enviado exitosamente", extra={"email": email_destinatario, "attached_csv": attach_csv})
        except Exception as e:
            logger.error(f"Error al enviar resumen por email: {e}", exc_info=True)
            # No fallar el DAG si falla el envío de email
    
    @task(
        task_id="upload_to_s3",
        pool=REPORTING_POOL,
        priority_weight=3,
        trigger_rule="none_failed_min_one_success",
    )
    def upload_to_s3(data: Dict[str, Any]) -> Dict[str, Any]:
        """Sube el CSV a S3 si está configurado."""
        params = data.get("params", {})
        upload_s3 = params.get("upload_to_s3", False)
        
        if not upload_s3:
            logger.info("Upload a S3 deshabilitado")
            return data
        
        csv_path = data.get("resumen", {}).get("csv_path") or data.get("csv_path")
        csv_filename = data.get("resumen", {}).get("csv_filename") or data.get("csv_filename")
        
        if not csv_path or not Path(csv_path).exists():
            logger.warning("CSV no encontrado para subir a S3")
            return data
        
        bucket = os.environ.get("STRIPE_REPORT_S3_BUCKET")
        if not bucket:
            logger.info("STRIPE_REPORT_S3_BUCKET no configurado, omitiendo upload")
            return data
        
        if not _BOTO3_AVAILABLE:
            logger.warning("boto3 no disponible, omitiendo upload a S3")
            return data
        
        try:
            s3_prefix = os.environ.get("STRIPE_REPORT_S3_PREFIX", "stripe_reports")
            fecha_inicio = data.get("fecha_inicio", "")
            fecha_fin = data.get("fecha_fin", "")
            date_str = fecha_inicio.replace("-", "_")
            
            s3_client = boto3.client("s3")
            s3_key = f"{s3_prefix}/{date_str}/{csv_filename}"
            
            s3_client.upload_file(csv_path, bucket, s3_key)
            s3_url = f"s3://{bucket}/{s3_key}"
            
            logger.info(
                "CSV subido exitosamente a S3",
                extra={"bucket": bucket, "key": s3_key, "url": s3_url},
            )
            
            # Actualizar datos con URL de S3
            resumen = data.get("resumen", {})
            resumen["s3_url"] = s3_url
            data["resumen"] = resumen
            
            try:
                if Stats:
                    Stats.incr("stripe_report.s3_upload.success", 1)
            except Exception:
                pass
            
            return data
        except Exception as e:
            logger.error(f"Error subiendo CSV a S3: {e}", exc_info=True)
            try:
                if Stats:
                    Stats.incr("stripe_report.s3_upload.failure", 1)
            except Exception:
                pass
            # No fallar el DAG si falla el upload
            return data
    
    @task(
        task_id="save_metrics_to_db",
        pool=REPORTING_POOL,
        priority_weight=3,
        trigger_rule="none_failed_min_one_success",
    )
    def save_metrics_to_db(data: Dict[str, Any]) -> Dict[str, Any]:
        """Guarda métricas del reporte en base de datos."""
        params = data.get("params", {})
        save_db = params.get("save_to_db", True)
        
        if not save_db:
            logger.info("Guardado en DB deshabilitado")
            return data
        
        if get_conn is None:
            logger.warning("plugins.db.get_conn no disponible, omitiendo guardado en DB")
            return data
        
        resumen = data.get("resumen", {})
        fecha_inicio = data.get("fecha_inicio", "")
        fecha_fin = data.get("fecha_fin", "")
        
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    # Crear tabla si no existe
                    cur.execute("""
                        CREATE SCHEMA IF NOT EXISTS finance;
                        CREATE TABLE IF NOT EXISTS finance.stripe_quickbooks_reports (
                            id BIGSERIAL PRIMARY KEY,
                            fecha_inicio DATE NOT NULL,
                            fecha_fin DATE NOT NULL,
                            total_pagos NUMERIC(15, 2) NOT NULL,
                            total_reembolsos NUMERIC(15, 2) NOT NULL,
                            total_tarifas NUMERIC(15, 2) NOT NULL,
                            count_pagos INT NOT NULL,
                            count_reembolsos INT NOT NULL,
                            count_tarifas INT NOT NULL,
                            csv_path TEXT,
                            csv_filename TEXT,
                            s3_url TEXT,
                            file_size_bytes BIGINT,
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                            dag_run_id TEXT,
                            UNIQUE(fecha_inicio, fecha_fin)
                        );
                    """)
                    
                    # Insertar métricas
                    ctx = get_current_context()
                    dag_run_id = ctx.get("run_id", "")
                    
                    cur.execute("""
                        INSERT INTO finance.stripe_quickbooks_reports 
                        (fecha_inicio, fecha_fin, total_pagos, total_reembolsos, total_tarifas,
                         count_pagos, count_reembolsos, count_tarifas, csv_path, csv_filename,
                         s3_url, file_size_bytes, dag_run_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (fecha_inicio, fecha_fin) 
                        DO UPDATE SET
                            total_pagos = EXCLUDED.total_pagos,
                            total_reembolsos = EXCLUDED.total_reembolsos,
                            total_tarifas = EXCLUDED.total_tarifas,
                            count_pagos = EXCLUDED.count_pagos,
                            count_reembolsos = EXCLUDED.count_reembolsos,
                            count_tarifas = EXCLUDED.count_tarifas,
                            csv_path = EXCLUDED.csv_path,
                            csv_filename = EXCLUDED.csv_filename,
                            s3_url = EXCLUDED.s3_url,
                            file_size_bytes = EXCLUDED.file_size_bytes,
                            dag_run_id = EXCLUDED.dag_run_id,
                            created_at = NOW();
                    """, (
                        fecha_inicio,
                        fecha_fin,
                        resumen.get("total_pagos", 0),
                        resumen.get("total_reembolsos", 0),
                        resumen.get("total_tarifas", 0),
                        resumen.get("count_pagos", 0),
                        resumen.get("count_reembolsos", 0),
                        resumen.get("count_tarifas", 0),
                        resumen.get("csv_path"),
                        resumen.get("csv_filename"),
                        resumen.get("s3_url"),
                        resumen.get("file_size_bytes", 0),
                        dag_run_id,
                    ))
                    
                    conn.commit()
                    logger.info("Métricas guardadas en base de datos exitosamente")
                    
                    try:
                        if Stats:
                            Stats.incr("stripe_report.db_save.success", 1)
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"Error guardando métricas en DB: {e}", exc_info=True)
            try:
                if Stats:
                    Stats.incr("stripe_report.db_save.failure", 1)
            except Exception:
                pass
            # No fallar el DAG si falla el guardado
        
        return data
    
    @task(
        task_id="notify_slack_summary",
        pool=REPORTING_POOL,
        priority_weight=2,
        trigger_rule="none_failed_min_one_success",
    )
    def notify_slack_summary(data: Dict[str, Any]) -> None:
        """Envía resumen a Slack."""
        params = data.get("params", {})
        notify = params.get("notify_slack", True)
        
        if not notify:
            logger.info("Notificación a Slack deshabilitada")
            return
        
        resumen = data.get("resumen", {})
        fecha_inicio = resumen.get("fecha_inicio", "")
        fecha_fin = resumen.get("fecha_fin", "")
        total_pagos = resumen.get("total_pagos", 0)
        total_reembolsos = resumen.get("total_reembolsos", 0)
        total_tarifas = resumen.get("total_tarifas", 0)
        count_pagos = resumen.get("count_pagos", 0)
        count_reembolsos = resumen.get("count_reembolsos", 0)
        count_tarifas = resumen.get("count_tarifas", 0)
        csv_filename = resumen.get("csv_filename", "")
        csv_checksum = resumen.get("csv_checksum", "")
        s3_url = resumen.get("s3_url")
        validation_warnings = resumen.get("validation_warnings", [])
        
        message = f"""
📊 *Reporte Stripe a QuickBooks*

*Período:* {fecha_inicio} a {fecha_fin}

*Resumen:*
• Pagos: ${total_pagos:,.2f} ({count_pagos} transacciones)
• Reembolsos: ${total_reembolsos:,.2f} ({count_reembolsos} transacciones)
• Tarifas: ${total_tarifas:,.2f} ({count_tarifas} transacciones)

*Archivo:* {csv_filename}
"""
        
        if csv_checksum:
            message += f"\n*Checksum:* `{csv_checksum[:16]}...`"
        
        if s3_url:
            message += f"\n*S3:* {s3_url}"
        
        if validation_warnings:
            message += f"\n\n⚠️ *Advertencias:* {len(validation_warnings)} advertencias de validación detectadas"
        
        message += "\n\n✅ Reporte generado exitosamente"
        
        try:
            notify_slack(message)
            logger.info("Resumen enviado a Slack exitosamente")
            try:
                if Stats:
                    Stats.incr("stripe_report.slack_notify.success", 1)
            except Exception:
                pass
        except Exception as e:
            logger.warning(f"Error enviando resumen a Slack: {e}", exc_info=True)
            try:
                if Stats:
                    Stats.incr("stripe_report.slack_notify.failure", 1)
            except Exception:
                pass
    
    @task(
        task_id="track_metrics",
        pool=REPORTING_POOL,
        priority_weight=2,
        trigger_rule="none_failed_min_one_success",
    )
    def track_metrics(data: Dict[str, Any]) -> None:
        """Trackea métricas con Stats y MLflow."""
        params = data.get("params", {})
        track = params.get("track_metrics", True)
        
        if not track:
            logger.info("Tracking de métricas deshabilitado")
            return
        
        resumen = data.get("resumen", {})
        
        # Trackear con Airflow Stats
        try:
            if Stats:
                Stats.incr("stripe_report.total_pagos.count", resumen.get("count_pagos", 0))
                Stats.incr("stripe_report.total_reembolsos.count", resumen.get("count_reembolsos", 0))
                Stats.incr("stripe_report.total_tarifas.count", resumen.get("count_tarifas", 0))
                
                # Montos totales como gauge
                Stats.gauge("stripe_report.total_pagos.amount", resumen.get("total_pagos", 0))
                Stats.gauge("stripe_report.total_reembolsos.amount", resumen.get("total_reembolsos", 0))
                Stats.gauge("stripe_report.total_tarifas.amount", resumen.get("total_tarifas", 0))
                
                logger.info("Métricas trackeadas con Stats")
        except Exception as e:
            logger.warning(f"Error trackeando métricas con Stats: {e}")
        
        # Trackear con MLflow si está disponible
        if _MLFLOW_AVAILABLE:
            try:
                mlflow_uri = os.environ.get("MLFLOW_TRACKING_URI")
                if mlflow_uri:
                    mlflow.set_tracking_uri(mlflow_uri)
                
                fecha_inicio = data.get("fecha_inicio", "")
                fecha_fin = data.get("fecha_fin", "")
                run_name = f"stripe_report_{fecha_inicio}_to_{fecha_fin}"
                
                with mlflow.start_run(run_name=run_name):
                    # Log métricas
                    mlflow.log_metric("total_pagos", float(resumen.get("total_pagos", 0)))
                    mlflow.log_metric("total_reembolsos", float(resumen.get("total_reembolsos", 0)))
                    mlflow.log_metric("total_tarifas", float(resumen.get("total_tarifas", 0)))
                    mlflow.log_metric("count_pagos", float(resumen.get("count_pagos", 0)))
                    mlflow.log_metric("count_reembolsos", float(resumen.get("count_reembolsos", 0)))
                    mlflow.log_metric("count_tarifas", float(resumen.get("count_tarifas", 0)))
                    
                    # Log parámetros
                    mlflow.log_param("fecha_inicio", fecha_inicio)
                    mlflow.log_param("fecha_fin", fecha_fin)
                    mlflow.log_param("dag_id", "stripe_quickbooks_report")
                    
                    # Tags
                    mlflow.set_tag("report_type", "stripe_quickbooks")
                    mlflow.set_tag("environment", os.environ.get("ENV", "dev"))
                    
                    logger.info("Métricas trackeadas con MLflow")
            except Exception as e:
                logger.warning(f"Error trackeando métricas con MLflow: {e}", exc_info=True)
    
    @task(
        task_id="detect_anomalies",
        pool=REPORTING_POOL,
        priority_weight=2,
        trigger_rule="none_failed_min_one_success",
    )
    def detect_anomalies(data: Dict[str, Any]) -> None:
        """Detecta anomalías comparando con promedios históricos."""
        if get_conn is None:
            return
        
        resumen = data.get("resumen", {})
        fecha_inicio = data.get("fecha_inicio", "")
        
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    # Obtener promedio de pagos de los últimos 30 días (excluyendo el período actual)
                    cur.execute("""
                        SELECT 
                            AVG(total_pagos) as avg_pagos,
                            AVG(total_reembolsos) as avg_reembolsos,
                            AVG(count_pagos) as avg_count_pagos
                        FROM finance.stripe_quickbooks_reports
                        WHERE fecha_fin < %s::date
                        AND fecha_fin >= %s::date - INTERVAL '30 days'
                        AND fecha_inicio != %s::date;
                    """, (fecha_inicio, fecha_inicio, fecha_inicio))
                    
                    row = cur.fetchone()
                    if not row or not row[0]:
                        logger.info("No hay datos históricos para comparar")
                        return
                    
                    avg_pagos, avg_reembolsos, avg_count_pagos = row
                    current_pagos = resumen.get("total_pagos", 0)
                    current_count = resumen.get("count_pagos", 0)
                    
                    anomalies = []
                    
                    # Detectar caída significativa en pagos (>30%)
                    if avg_pagos and avg_pagos > 0:
                        drop_pct = ((avg_pagos - current_pagos) / avg_pagos) * 100
                        if drop_pct > 30:
                            anomalies.append(
                                f"⚠️ Caída significativa en pagos: {drop_pct:.1f}% "
                                f"(${current_pagos:,.2f} vs ${avg_pagos:,.2f} promedio)"
                            )
                    
                    # Detectar caída en cantidad de transacciones
                    if avg_count_pagos and avg_count_pagos > 0:
                        count_drop = ((avg_count_pagos - current_count) / avg_count_pagos) * 100
                        if count_drop > 40:
                            anomalies.append(
                                f"⚠️ Caída en cantidad de transacciones: {count_drop:.1f}% "
                                f"({current_count} vs {int(avg_count_pagos)} promedio)"
                            )
                    
                    if anomalies:
                        alert_message = f"🚨 *Anomalías detectadas en reporte Stripe*\n\n" + "\n".join(anomalies)
                        try:
                            notify_slack(alert_message)
                            logger.warning("Anomalías detectadas y notificadas", extra={"anomalies": anomalies})
                        except Exception:
                            pass
        except Exception as e:
            logger.warning(f"Error detectando anomalías: {e}", exc_info=True)
            # No fallar el DAG si falla la detección
    
    @task(
        task_id="generar_summary_final",
        pool=REPORTING_POOL,
        priority_weight=1,
        trigger_rule="none_failed_min_one_success",
    )
    def generar_summary_final(data: Dict[str, Any]) -> None:
        """Genera un summary final con todas las métricas del proceso."""
        resumen = data.get("resumen", {})
        extraction_ms = data.get("extraction_duration_ms", 0)
        processing_ms = data.get("processing_duration_ms", 0)
        total_duration_ms = extraction_ms + processing_ms
        
        summary = {
            "dag_run_id": get_current_context().get("run_id", ""),
            "fecha_inicio": resumen.get("fecha_inicio", ""),
            "fecha_fin": resumen.get("fecha_fin", ""),
            "total_pagos": resumen.get("total_pagos", 0),
            "total_reembolsos": resumen.get("total_reembolsos", 0),
            "total_tarifas": resumen.get("total_tarifas", 0),
            "count_pagos": resumen.get("count_pagos", 0),
            "count_reembolsos": resumen.get("count_reembolsos", 0),
            "count_tarifas": resumen.get("count_tarifas", 0),
            "csv_filename": resumen.get("csv_filename", ""),
            "csv_checksum": resumen.get("csv_checksum", ""),
            "file_size_bytes": resumen.get("file_size_bytes", 0),
            "s3_url": resumen.get("s3_url"),
            "extraction_duration_ms": extraction_ms,
            "processing_duration_ms": processing_ms,
            "total_duration_ms": total_duration_ms,
            "validation_warnings": len(resumen.get("validation_warnings", [])),
            "timestamp": pendulum.now("UTC").isoformat(),
        }
        
        logger.info(
            "Summary final del reporte",
            extra=summary,
        )
        
        try:
            if Stats:
                Stats.timing("stripe_report.total_duration_ms", total_duration_ms)
                Stats.gauge("stripe_report.total_pagos", resumen.get("total_pagos", 0))
                Stats.gauge("stripe_report.total_reembolsos", resumen.get("total_reembolsos", 0))
                Stats.gauge("stripe_report.total_tarifas", resumen.get("total_tarifas", 0))
        except Exception:
            pass
    
    @task(
        task_id="establecer_idempotencia",
        pool=FINANCE_POOL,
        priority_weight=1,
        trigger_rule="none_failed_min_one_success",
    )
    def establecer_idempotencia(data: Dict[str, Any]) -> None:
        """Establece el lock de idempotencia después de generar el reporte."""
        # El date_range_key está en los datos de fechas que se pasan a través de la cadena
        date_range_key = data.get("date_range_key")
        if not date_range_key:
            # Intentar reconstruir desde fechas
            fecha_inicio = data.get("fecha_inicio")
            fecha_fin = data.get("fecha_fin")
            if fecha_inicio and fecha_fin:
                date_range_key = f"{fecha_inicio}_{fecha_fin}"
        
        if date_range_key:
            _set_idempotency_lock(date_range_key)
            logger.info(f"Idempotencia establecida para: {date_range_key}")
        else:
            logger.warning("No se pudo establecer idempotencia: date_range_key no disponible")
    
    # Definir el flujo del DAG
    
    # Fase 1: Preparación y validación
    health = health_check()
    fechas = preparar_fechas()
    fechas_verificadas = verificar_idempotencia(fechas)
    
    # Health check debe ejecutarse primero
    health >> fechas >> fechas_verificadas
    
    # Fase 2: Extracción y procesamiento (con TaskGroup para organización)
    with TaskGroup(group_id="extraction_and_processing") as extraction_group:
        transacciones = extraer_transacciones_stripe(fechas_verificadas)
        csv_data = procesar_y_generar_csv(transacciones)
        resumen_data = calcular_resumen(csv_data)
    
    # Fase 3: Distribución y notificaciones (TaskGroup para tareas paralelas)
    with TaskGroup(group_id="distribution_and_notifications") as distribution_group:
        # Enviar email (crítico)
        email_task = enviar_resumen(resumen_data)
        
        # Tareas paralelas de almacenamiento
        s3_task = upload_to_s3(resumen_data)
        db_task = save_metrics_to_db(resumen_data)
        
        # Notificaciones y tracking (paralelas, no críticas)
        slack_task = notify_slack_summary(resumen_data)
        metrics_task = track_metrics(resumen_data)
        anomalies_task = detect_anomalies(resumen_data)
    
    # Fase 4: Finalización
    with TaskGroup(group_id="finalization") as finalization_group:
        summary_task = generar_summary_final(resumen_data)
        idempotency_task = establecer_idempotencia(resumen_data)
    
    # Conectar todas las fases
    fechas_verificadas >> extraction_group
    extraction_group >> distribution_group
    distribution_group >> finalization_group
    
    # End marker
    end = EmptyOperator(
        task_id="end",
        trigger_rule="none_failed_min_one_success",
    )
    
    finalization_group >> end


dag = stripe_quickbooks_report()
