"""
Módulo para crear recibos de ingreso y asientos de impuesto en QuickBooks cuando se confirma un pago en Stripe.

Este módulo crea un recibo de venta (Sales Receipt) en QuickBooks Online cuando se confirma
un pago en Stripe, registrando el monto neto (monto total menos tarifa de Stripe) y
asignándolo a la cuenta de ingresos especificada.

También permite crear asientos de impuesto (Journal Entry) vinculados a recibos existentes
para registrar impuestos cobrados en Stripe.

Variables de entorno requeridas:
- QUICKBOOKS_ACCESS_TOKEN: Token de acceso OAuth2 de QuickBooks
- QUICKBOOKS_REALM_ID: ID de la compañía en QuickBooks
- QUICKBOOKS_BASE: URL base de la API (default: sandbox, usar producción en producción)

Variables de entorno opcionales:
- QUICKBOOKS_CLIENT_ID: ID del cliente OAuth (solo para refresh tokens)
- QUICKBOOKS_CLIENT_SECRET: Secret del cliente OAuth (solo para refresh tokens)
- QUICKBOOKS_FEE_ACCOUNT: Nombre de la cuenta para registrar tarifas (si se requiere)

Ejemplo de uso - Crear recibo:
    resultado = crear_recibo_ingreso_quickbooks(
        stripe_charge_id="ch_1234567890",
        monto=1000.00,
        correo_cliente="cliente@ejemplo.com",
        tarifa=29.00,
        cuenta_ingresos="Ventas de Productos"
    )
    print(resultado["qb_receipt_id"])  # ID del recibo en QuickBooks
    print(resultado["estado"])  # "Éxito" o mensaje de error

Ejemplo de uso - Crear asiento de impuesto:
    resultado = crear_asiento_impuesto_quickbooks(
        impuesto_monto=160.00,
        stripe_charge_id="ch_1234567890",
        qb_receipt_id="123",
        cuenta_impuesto="Impuestos por pagar",
        currency="MXN",  # Opcional
        tipo_impuesto="IVA",  # Opcional: "IVA", "ISR", "IEPS" - usa cuenta predefinida
        validar_cuentas=True  # Validar que las cuentas existan
    )
    print(resultado["qb_tax_entry_id"])  # ID del asiento de impuesto en QuickBooks
    print(resultado["estado"])  # "Éxito" o mensaje de error
    print(resultado["currency"])  # Moneda del asiento
    print(resultado["tipo_impuesto"])  # Tipo de impuesto si se especificó
    
Ejemplo de uso - Verificar asiento creado:
    verificacion = verificar_asiento_impuesto_quickbooks(
        qb_tax_entry_id="456",
        stripe_charge_id="ch_1234567890"
    )
    print(verificacion["existe"])  # True/False
    print(verificacion["monto"])  # Monto del asiento
    
Ejemplo de uso - Limpiar cache:
    limpiar_cache_recibos()  # Limpia el cache de recibos
    
Ejemplo de uso - Buscar asientos por recibo:
    asientos = buscar_asientos_por_recibo(
        qb_receipt_id="123",
        limite=10
    )
    print(f"Encontrados {asientos['total']} asientos")
    for asiento in asientos['asientos']:
        print(f"  - {asiento['qb_tax_entry_id']}: {asiento['monto']}")
    
Ejemplo de uso - Obtener estadísticas:
    stats = obtener_estadisticas_operaciones()
    print(f"Tasa de éxito: {stats['tasa_exito_porcentaje']}%")
    print(f"Cache hit rate: {stats['cache']['hit_rate']}%")
    
Ejemplo de uso - Procesar múltiples asientos en batch:
    asientos = [
        {
            "impuesto_monto": 160.00,
            "stripe_charge_id": "ch_123",
            "qb_receipt_id": "456",
            "tipo_impuesto": "IVA"
        },
        {
            "impuesto_monto": 200.00,
            "stripe_charge_id": "ch_124",
            "qb_receipt_id": "457",
            "tipo_impuesto": "IVA"
        }
    ]
    resultado_batch = crear_asientos_impuesto_batch(
        asientos=asientos,
        batch_delay=0.5,
        continue_on_error=True
    )
    print(f"Procesados: {resultado_batch['exitosos']}/{resultado_batch['total']}")
    
Ejemplo de uso - Health check:
    health = verificar_health_quickbooks()
    if health["healthy"]:
        print(f"✓ QuickBooks está disponible ({health['entorno']})")
    else:
        print(f"✗ Error: {health['error']}")
"""
import os
import requests
import time
import logging
import re
from datetime import datetime
from typing import Optional, Dict, Any, List

# Configurar logger para esta función
logger = logging.getLogger(__name__)


QUICKBOOKS_CLIENT_ID = os.environ.get("QUICKBOOKS_CLIENT_ID", "")
QUICKBOOKS_CLIENT_SECRET = os.environ.get("QUICKBOOKS_CLIENT_SECRET", "")
QUICKBOOKS_REALM_ID = os.environ.get("QUICKBOOKS_REALM_ID", "")
QUICKBOOKS_ACCESS_TOKEN = os.environ.get("QUICKBOOKS_ACCESS_TOKEN", "")
# URL base: usar sandbox para desarrollo, producción para producción
# Sandbox: https://sandbox-quickbooks.api.intuit.com
# Producción: https://quickbooks.api.intuit.com
QUICKBOOKS_BASE = os.environ.get("QUICKBOOKS_BASE", "https://sandbox-quickbooks.api.intuit.com")

# Configuración de retry para peticiones a QuickBooks
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0  # segundos
DEFAULT_TIMEOUT = 30

# Cache simple en memoria para información de recibos (evita llamadas repetidas)
_receipt_cache: Dict[str, Dict[str, Any]] = {}
_receipt_cache_ttl = 300  # 5 minutos

# Constantes para tipos de impuestos comunes
TIPOS_IMPUESTO = {
    "IVA": "Impuestos por pagar",
    "ISR": "Impuestos sobre la renta por pagar",
    "IEPS": "IEPS por pagar",
    "DEFAULT": "Impuestos por pagar"
}

# Monedas soportadas por QuickBooks
MONEDAS_SOPORTADAS = ["USD", "MXN", "EUR", "GBP", "CAD", "AUD", "JPY", "CNY"]

# Límites de validación
MIN_IMPUESTO_MONTO = 0.01  # Mínimo monto de impuesto permitido
MAX_IMPUESTO_MONTO = 1000000000.00  # Máximo monto de impuesto permitido

# Límites de longitud de strings
MAX_STRIPE_CHARGE_ID_LENGTH = 128
MAX_QB_RECEIPT_ID_LENGTH = 64
MAX_QB_ENTRY_ID_LENGTH = 64

# Patrones de validación
STRIPE_CHARGE_ID_PATTERN = r"^ch_[a-zA-Z0-9]{24,}$"  # ch_ seguido de al menos 24 caracteres alfanuméricos

# Contadores para métricas (simple, en memoria)
_operation_stats = {
    "total_operations": 0,
    "successful_operations": 0,
    "failed_operations": 0,
    "duplicate_preventions": 0,
    "cache_hits": 0,
    "cache_misses": 0
}


def _obtener_info_recibo_quickbooks(
    qb_receipt_id: str,
    access_token: str,
    realm_id: str,
    base_url: str,
    use_cache: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Obtiene información del recibo de QuickBooks con cache opcional.
    
    Args:
        qb_receipt_id: ID del recibo en QuickBooks
        access_token: Token de acceso
        realm_id: ID de la compañía
        base_url: URL base de la API
        use_cache: Si usar cache para evitar llamadas repetidas (default: True)
    
    Returns:
        Dict con información del recibo o None si no existe
    """
    # Verificar cache primero
    if use_cache and qb_receipt_id in _receipt_cache:
        cached_data = _receipt_cache[qb_receipt_id]
        cached_time = cached_data.get("_cached_at", 0)
        if time.time() - cached_time < _receipt_cache_ttl:
            logger.debug(f"Usando información del recibo {qb_receipt_id} desde cache")
            _operation_stats["cache_hits"] += 1
            return cached_data.get("data")
        else:
            # Cache expirado, eliminar
            del _receipt_cache[qb_receipt_id]
    
    _operation_stats["cache_misses"] += 1
    
    receipt_url = f"{base_url}/v3/company/{realm_id}/salesreceipt/{qb_receipt_id}"
    receipt_headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    try:
        receipt_response = requests.get(receipt_url, headers=receipt_headers, timeout=15)
        if receipt_response.status_code == 200:
            receipt_data = receipt_response.json()
            receipt_info = receipt_data.get("SalesReceipt", {})
            
            # Guardar en cache si está habilitado
            if use_cache and receipt_info:
                _receipt_cache[qb_receipt_id] = {
                    "data": receipt_info,
                    "_cached_at": time.time()
                }
            
            return receipt_info
        return None
    except Exception as e:
        logger.warning(f"Error al obtener recibo {qb_receipt_id}: {str(e)}")
        return None


def _validar_cuenta_contable(
    account_name: str,
    access_token: str,
    realm_id: str,
    base_url: str
) -> bool:
    """
    Valida que una cuenta contable exista en QuickBooks.
    
    Args:
        account_name: Nombre de la cuenta
        access_token: Token de acceso
        realm_id: ID de la compañía
        base_url: URL base de la API
    
    Returns:
        True si la cuenta existe, False si no
    """
    query_url = f"{base_url}/v3/company/{realm_id}/query"
    query_headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    # Escapar comillas simples en el nombre de la cuenta
    account_name_escaped = account_name.replace("'", "''")
    query = f"SELECT * FROM Account WHERE Name = '{account_name_escaped}' MAXRESULTS 1"
    
    try:
        query_response = requests.get(
            f"{query_url}?query={query}",
            headers=query_headers,
            timeout=10
        )
        if query_response.status_code == 200:
            query_data = query_response.json()
            accounts = query_data.get("QueryResponse", {}).get("Account", [])
            return bool(accounts)
        return False
    except Exception as e:
        logger.debug(f"Error al validar cuenta {account_name}: {str(e)}")
        # Si no podemos validar, asumimos que existe para no bloquear el proceso
        return True


def _buscar_asiento_duplicado(
    stripe_charge_id: str,
    qb_receipt_id: str,
    access_token: str,
    realm_id: str,
    base_url: str
) -> Optional[str]:
    """
    Busca si ya existe un asiento contable para esta transacción de Stripe.
    
    Args:
        stripe_charge_id: ID de la transacción en Stripe
        qb_receipt_id: ID del recibo en QuickBooks
        access_token: Token de acceso
        realm_id: ID de la compañía
        base_url: URL base de la API
    
    Returns:
        ID del asiento si existe, None si no existe
    """
    # Buscar por DocNumber que contiene el stripe_charge_id
    charge_id_clean = ''.join(c for c in stripe_charge_id if c.isalnum() or c == '-')[:12]
    doc_number_pattern = f"TAX-{charge_id_clean}"
    
    # Query para buscar journal entries por memo o DocNumber
    query_url = f"{base_url}/v3/company/{realm_id}/query"
    query_headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/text"
    }
    
    # Query SQL para QuickBooks (limitado, pero podemos buscar por texto)
    # QuickBooks no permite búsqueda directa por DocNumber en query simple,
    # así que hacemos una búsqueda por memo
    query = f"SELECT * FROM JournalEntry WHERE Memo LIKE '%{stripe_charge_id}%' OR Memo LIKE '%{qb_receipt_id}%' MAXRESULTS 10"
    
    try:
        query_response = requests.get(
            f"{query_url}?query={query}",
            headers=query_headers,
            timeout=15
        )
        if query_response.status_code == 200:
            query_data = query_response.json()
            journal_entries = query_data.get("QueryResponse", {}).get("JournalEntry", [])
            
            # Si hay múltiples, buscar el que coincide exactamente
            if isinstance(journal_entries, list):
                for entry in journal_entries:
                    doc_num = entry.get("DocNumber", "")
                    memo = entry.get("Memo", "")
                    if (stripe_charge_id in memo or stripe_charge_id in doc_num) and qb_receipt_id in memo:
                        return entry.get("Id")
            elif isinstance(journal_entries, dict):
                # Si solo hay uno, retornarlo
                doc_num = journal_entries.get("DocNumber", "")
                memo = journal_entries.get("Memo", "")
                if (stripe_charge_id in memo or stripe_charge_id in doc_num) and qb_receipt_id in memo:
                    return journal_entries.get("Id")
    except Exception as e:
        logger.debug(f"Error al buscar asiento duplicado: {str(e)}")
        # No fallar si la búsqueda falla, continuar con la creación
    
    return None


def _validar_balance_asiento(
    debit_line: Dict[str, Any],
    credit_line: Dict[str, Any]
) -> bool:
    """
    Valida que el asiento contable esté balanceado.
    
    Args:
        debit_line: Línea de débito
        credit_line: Línea de crédito
    
    Returns:
        True si está balanceado, False si no
    """
    debit_amount = float(debit_line.get("Amount", "0"))
    credit_amount = float(credit_line.get("Amount", "0"))
    
    # Tolerancia de 0.01 para diferencias de redondeo
    return abs(debit_amount - credit_amount) < 0.01


def _realizar_peticion_con_retry(
    url: str,
    headers: Dict[str, str],
    payload: Dict[str, Any],
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_delay: float = DEFAULT_RETRY_DELAY,
    timeout: int = DEFAULT_TIMEOUT
) -> requests.Response:
    """
    Realiza una petición POST a QuickBooks con retry y exponential backoff.
    
    Args:
        url: URL de la petición
        headers: Headers HTTP
        payload: Payload JSON
        max_retries: Número máximo de reintentos
        retry_delay: Delay inicial entre reintentos (segundos)
        timeout: Timeout en segundos
    
    Returns:
        Response de requests
    
    Raises:
        requests.exceptions.RequestException: Si falla después de todos los reintentos
    """
    last_exception = None
    last_response = None
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            last_response = response
            
            # Si es exitoso, retornar inmediatamente
            if response.status_code < 400:
                return response
            
            # Si es rate limit (429) o error del servidor (5xx), reintentar
            if response.status_code in [429, 500, 502, 503, 504]:
                if attempt < max_retries - 1:
                    delay = retry_delay * (2 ** attempt)  # Exponential backoff
                    time.sleep(delay)
                    continue
            
            # Para otros errores 4xx, retornar directamente
            return response
            
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_exception = e
            if attempt < max_retries - 1:
                delay = retry_delay * (2 ** attempt)
                time.sleep(delay)
                continue
            else:
                raise
    
    # Si llegamos aquí, todos los reintentos fallaron
    if last_exception:
        raise last_exception
    
    # Fallback: retornar la última respuesta (aunque sea un error)
    if last_response:
        return last_response
    
    # Si no hay respuesta, lanzar excepción
    raise requests.exceptions.RequestException("No se pudo completar la petición después de todos los reintentos")


def crear_recibo_ingreso_quickbooks(
    stripe_charge_id: str,
    monto: float,
    correo_cliente: str,
    tarifa: float,
    cuenta_ingresos: str,
    qb_access_token: Optional[str] = None,
    qb_realm_id: Optional[str] = None,
    qb_base: Optional[str] = None
) -> Dict[str, Any]:
    """
    Crea un recibo de ingreso en QuickBooks para un pago confirmado en Stripe.
    
    Args:
        stripe_charge_id: ID del cargo en Stripe
        monto: Monto total del pago
        tarifa: Tarifa de Stripe (a deducir del monto)
        correo_cliente: Correo electrónico del cliente
        cuenta_ingresos: Nombre o ID de la cuenta de ingresos en QuickBooks
        qb_access_token: Token de acceso de QuickBooks (opcional, usa env var si no se proporciona)
        qb_realm_id: ID de la compañía en QuickBooks (opcional, usa env var si no se proporciona)
        qb_base: URL base de la API de QuickBooks (opcional, usa env var si no se proporciona)
    
    Returns:
        Dict con:
            - qb_receipt_id: ID del recibo creado en QuickBooks (None si falla)
            - estado: Estado de la operación ('Éxito' o descripción del error)
    """
    # Usar parámetros proporcionados o variables de entorno
    access_token = qb_access_token or QUICKBOOKS_ACCESS_TOKEN
    realm_id = qb_realm_id or QUICKBOOKS_REALM_ID
    base_url = qb_base or QUICKBOOKS_BASE
    
    if not access_token:
        return {
            "qb_receipt_id": None,
            "estado": "ERROR: QUICKBOOKS_ACCESS_TOKEN no configurado"
        }
    
    if not realm_id:
        return {
            "qb_receipt_id": None,
            "estado": "ERROR: QUICKBOOKS_REALM_ID no configurado"
        }
    
    if not stripe_charge_id:
        return {
            "qb_receipt_id": None,
            "estado": "ERROR: stripe_charge_id es requerido"
        }
    
    if monto <= 0:
        return {
            "qb_receipt_id": None,
            "estado": "ERROR: monto debe ser mayor que cero"
        }
    
    # Calcular monto neto (monto - tarifa)
    monto_neto = max(0, monto - tarifa) if tarifa else monto
    
    # Construir URL y headers
    url = f"{base_url}/v3/company/{realm_id}/salesreceipt"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Construir payload para el recibo de ingreso (Sales Receipt)
    # QuickBooks API v3 espera montos como strings con formato decimal
    # La estructura básica requiere al menos una línea de item
    
    # Construir la línea principal de ingreso
    line_item = {
        "DetailType": "SalesItemLineDetail",
        "Amount": str(monto_neto),
        "Description": f"Pago Stripe - {stripe_charge_id}",
        "SalesItemLineDetail": {
            "ItemRef": {
                "name": cuenta_ingresos,
                "value": ""  # QuickBooks buscará por nombre si no hay value
            }
        }
    }
    
    # Construir el payload base
    payload = {
        "Line": [line_item],
        "CustomerRef": {
            "name": correo_cliente  # QuickBooks buscará el cliente por nombre/email
        },
        "TxnDate": "",  # QuickBooks usará la fecha actual si está vacío
        "PrivateNote": f"Pago Stripe ID: {stripe_charge_id} | Monto bruto: {monto} | Tarifa: {tarifa}",
        "DocNumber": stripe_charge_id[:20] if len(stripe_charge_id) > 20 else stripe_charge_id,
        "TotalAmt": str(monto_neto)
    }
    
    # Si hay tarifa y queremos registrarla como gasto separado, podríamos agregarla
    # Pero normalmente la tarifa ya está deducida del monto_neto
    # Si se requiere registrar la tarifa como gasto, se podría hacer en una transacción separada
    
    try:
        # Realizar la petición POST
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        # Si la respuesta es exitosa
        if response.status_code in [200, 201]:
            try:
                response_data = response.json()
                # QuickBooks API v3 devuelve el objeto en response_data["SalesReceipt"]
                receipt = response_data.get("SalesReceipt", {})
                qb_receipt_id = receipt.get("Id")
                
                # También intentar obtener de otros campos posibles
                if not qb_receipt_id:
                    qb_receipt_id = receipt.get("id") or receipt.get("Id") or response_data.get("Id")
                
                if qb_receipt_id:
                    sync_token = receipt.get("SyncToken", receipt.get("syncToken"))
                    return {
                        "qb_receipt_id": str(qb_receipt_id),
                        "estado": "Éxito",
                        "sync_token": sync_token if sync_token else None
                    }
                else:
                    # Si no hay ID pero la respuesta fue exitosa, revisar la estructura
                    return {
                        "qb_receipt_id": None,
                        "estado": f"Éxito pero no se pudo obtener el ID del recibo. Respuesta: {response_data}"
                    }
            except Exception as e:
                return {
                    "qb_receipt_id": None,
                    "estado": f"Éxito pero error al parsear respuesta: {str(e)}. Respuesta raw: {response.text[:200]}"
                }
        
        # Si hay error, obtener detalles del error
        error_code = response.status_code
        try:
            error_data = response.json()
            # QuickBooks puede devolver errores en diferentes formatos
            faults = error_data.get("Fault", {})
            errors = faults.get("Error", [])
            if errors:
                error_message = errors[0].get("Message", "Error desconocido")
                error_detail = errors[0].get("Detail", "")
                full_message = f"{error_message}. {error_detail}" if error_detail else error_message
            else:
                error_message = error_data.get("message", response.text)
                full_message = error_message
        except:
            error_message = response.text or "Error desconocido"
            full_message = error_message
        
        return {
            "qb_receipt_id": None,
            "estado": f"{error_code}: {full_message}"
        }
        
    except requests.exceptions.Timeout:
        return {
            "qb_receipt_id": None,
            "estado": "ERROR_TIMEOUT: La petición a QuickBooks excedió el tiempo límite"
        }
    except requests.exceptions.ConnectionError:
        return {
            "qb_receipt_id": None,
            "estado": "ERROR_CONNECTION: No se pudo conectar con QuickBooks API"
        }
    except requests.exceptions.RequestException as e:
        return {
            "qb_receipt_id": None,
            "estado": f"ERROR_REQUEST: {str(e)}"
        }
    except Exception as e:
        return {
            "qb_receipt_id": None,
            "estado": f"ERROR_INESPERADO: {str(e)}"
        }


# Función auxiliar para uso en DAGs de Airflow
def crear_recibo_ingreso_quickbooks_task(**context):
    """
    Wrapper para usar la función en DAGs de Airflow.
    Espera los siguientes parámetros en context['params']:
    - stripe_charge_id: ID del cargo en Stripe
    - monto: Monto total del pago
    - correo_cliente: Correo electrónico del cliente
    - tarifa: Tarifa de Stripe (opcional, default 0)
    - cuenta_ingresos: Nombre de la cuenta de ingresos en QuickBooks
    """
    params = context.get('params', {})
    stripe_charge_id = params.get('stripe_charge_id')
    monto = params.get('monto')
    correo_cliente = params.get('correo_cliente')
    tarifa = params.get('tarifa', 0.0)
    cuenta_ingresos = params.get('cuenta_ingresos')
    
    if not stripe_charge_id:
        raise ValueError("stripe_charge_id es requerido en los parámetros")
    if not monto:
        raise ValueError("monto es requerido en los parámetros")
    if not correo_cliente:
        raise ValueError("correo_cliente es requerido en los parámetros")
    if not cuenta_ingresos:
        raise ValueError("cuenta_ingresos es requerido en los parámetros")
    
    # Convertir monto y tarifa a float si son strings
    try:
        monto = float(monto)
    except (ValueError, TypeError):
        raise ValueError(f"monto debe ser un número válido: {monto}")
    
    try:
        tarifa = float(tarifa) if tarifa else 0.0
    except (ValueError, TypeError):
        tarifa = 0.0
    
    resultado = crear_recibo_ingreso_quickbooks(
        stripe_charge_id=stripe_charge_id,
        monto=monto,
        correo_cliente=correo_cliente,
        tarifa=tarifa,
        cuenta_ingresos=cuenta_ingresos
    )
    
    if resultado["estado"] == "Éxito":
        print(f"✓ Recibo de ingreso creado exitosamente en QuickBooks")
        print(f"  - ID Stripe: {stripe_charge_id}")
        print(f"  - ID QuickBooks: {resultado['qb_receipt_id']}")
        print(f"  - Cliente: {correo_cliente}")
        print(f"  - Monto neto: {monto - tarifa}")
    else:
        print(f"✗ Error al crear recibo de ingreso: {resultado['estado']}")
    
    return resultado


def crear_asiento_impuesto_quickbooks(
    impuesto_monto: float,
    stripe_charge_id: str,
    qb_receipt_id: str,
    cuenta_impuesto: str = "Impuestos por pagar",
    cuenta_debito: Optional[str] = None,
    currency: Optional[str] = None,
    tipo_impuesto: Optional[str] = None,
    qb_access_token: Optional[str] = None,
    qb_realm_id: Optional[str] = None,
    qb_base: Optional[str] = None,
    validar_recibo: bool = True,
    validar_cuentas: bool = False
) -> Dict[str, Any]:
    """
    Crea un asiento de impuesto en QuickBooks y lo vincula al recibo original.
    
    Se ha cobrado el impuesto en Stripe en la transacción ID {stripe_charge_id}. 
    En QuickBooks, crea un asiento de impuesto correspondiente en la cuenta 
    'Impuestos por pagar' o 'Impuesto IVA', y vincúlalo al pago original en QuickBooks.
    
    Args:
        impuesto_monto: Monto del impuesto cobrado en Stripe
        stripe_charge_id: ID de la transacción en Stripe
        qb_receipt_id: ID del recibo original en QuickBooks al que vincular el asiento
        cuenta_impuesto: Nombre de la cuenta de impuestos (default: "Impuestos por pagar")
                         También puede ser "Impuesto IVA"
        cuenta_debito: Nombre de la cuenta de débito (opcional, default: "Efectivo")
                       Para impuestos cobrados, típicamente se debita "Efectivo" o "Banco"
                       y se acredita la cuenta de impuestos por pagar
        qb_access_token: Token de acceso de QuickBooks (opcional, usa env var si no se proporciona)
        qb_realm_id: ID de la compañía en QuickBooks (opcional, usa env var si no se proporciona)
        qb_base: URL base de la API de QuickBooks (opcional, usa env var si no se proporciona)
        validar_recibo: Si True, valida que el recibo existe antes de crear el asiento (default: True)
        validar_cuentas: Si True, valida que las cuentas contables existan en QuickBooks (default: False)
        currency: Código de moneda (USD, MXN, EUR, etc.) - se usa del recibo si no se proporciona
        tipo_impuesto: Tipo de impuesto ("IVA", "ISR", "IEPS") - usa cuenta predefinida si se proporciona
    
    Returns:
        Dict con:
            - qb_tax_entry_id: ID del asiento de impuesto creado en QuickBooks (None si falla)
            - estado: Estado de la operación ('Éxito' o descripción del error)
    """
    # Usar parámetros proporcionados o variables de entorno
    access_token = qb_access_token or QUICKBOOKS_ACCESS_TOKEN
    realm_id = qb_realm_id or QUICKBOOKS_REALM_ID
    base_url = qb_base or QUICKBOOKS_BASE
    
    if not access_token:
        return {
            "qb_tax_entry_id": None,
            "estado": "ERROR: QUICKBOOKS_ACCESS_TOKEN no configurado",
            "codigo_error": "MISSING_ACCESS_TOKEN"
        }
    
    if not realm_id:
        return {
            "qb_tax_entry_id": None,
            "estado": "ERROR: QUICKBOOKS_REALM_ID no configurado",
            "codigo_error": "MISSING_REALM_ID"
        }
    
    if not stripe_charge_id:
        return {
            "qb_tax_entry_id": None,
            "estado": "ERROR: stripe_charge_id es requerido",
            "codigo_error": "MISSING_STRIPE_CHARGE_ID"
        }
    
    # Validar formato y longitud de stripe_charge_id
    if len(stripe_charge_id) > MAX_STRIPE_CHARGE_ID_LENGTH:
        return {
            "qb_tax_entry_id": None,
            "estado": f"ERROR: stripe_charge_id excede longitud máxima ({MAX_STRIPE_CHARGE_ID_LENGTH} caracteres)",
            "codigo_error": "INVALID_STRIPE_CHARGE_ID_LENGTH"
        }
    
    # Validar formato básico de Stripe charge ID (opcional, solo advertencia)
    if not stripe_charge_id.startswith("ch_") and len(stripe_charge_id) < 10:
        logger.warning(f"stripe_charge_id '{stripe_charge_id}' no parece tener formato estándar de Stripe")
    
    if not qb_receipt_id:
        return {
            "qb_tax_entry_id": None,
            "estado": "ERROR: qb_receipt_id es requerido",
            "codigo_error": "MISSING_QB_RECEIPT_ID"
        }
    
    # Validar longitud de qb_receipt_id
    if len(qb_receipt_id) > MAX_QB_RECEIPT_ID_LENGTH:
        return {
            "qb_tax_entry_id": None,
            "estado": f"ERROR: qb_receipt_id excede longitud máxima ({MAX_QB_RECEIPT_ID_LENGTH} caracteres)",
            "codigo_error": "INVALID_QB_RECEIPT_ID_LENGTH"
        }
    
    # Validar y normalizar el monto del impuesto
    try:
        impuesto_monto = float(impuesto_monto)
        impuesto_monto = round(impuesto_monto, 2)  # Redondear a 2 decimales
    except (ValueError, TypeError):
        return {
            "qb_tax_entry_id": None,
            "estado": "ERROR: impuesto_monto debe ser un número válido",
            "codigo_error": "INVALID_TAX_AMOUNT_TYPE"
        }
    
    # Validar límites del monto
    if impuesto_monto <= 0:
        return {
            "qb_tax_entry_id": None,
            "estado": f"ERROR: impuesto_monto debe ser mayor que cero. Recibido: {impuesto_monto}",
            "codigo_error": "INVALID_TAX_AMOUNT_ZERO"
        }
    
    if impuesto_monto < MIN_IMPUESTO_MONTO:
        return {
            "qb_tax_entry_id": None,
            "estado": f"ERROR: impuesto_monto ({impuesto_monto}) es menor que el mínimo permitido ({MIN_IMPUESTO_MONTO})",
            "codigo_error": "INVALID_TAX_AMOUNT_BELOW_MIN"
        }
    
    if impuesto_monto > MAX_IMPUESTO_MONTO:
        return {
            "qb_tax_entry_id": None,
            "estado": f"ERROR: impuesto_monto ({impuesto_monto}) excede el máximo permitido ({MAX_IMPUESTO_MONTO})",
            "codigo_error": "INVALID_TAX_AMOUNT_ABOVE_MAX"
        }
    
    # Iniciar logging estructurado
    log_context = {
        "stripe_charge_id": stripe_charge_id,
        "qb_receipt_id": qb_receipt_id,
        "impuesto_monto": impuesto_monto,
        "cuenta_impuesto": cuenta_impuesto,
        "cuenta_debito": cuenta_debito or "Efectivo"
    }
    logger.info("Iniciando creación de asiento de impuesto", extra=log_context)
    _operation_stats["total_operations"] += 1
    
    # Validar que el recibo existe y obtener información adicional (opcional)
    receipt_info = None
    receipt_currency = currency
    if validar_recibo:
        logger.debug(f"Validando existencia del recibo {qb_receipt_id}")
        receipt_info = _obtener_info_recibo_quickbooks(
            qb_receipt_id, access_token, realm_id, base_url, use_cache=True
        )
        if receipt_info is None:
            logger.warning(f"Recibo {qb_receipt_id} no encontrado en QuickBooks", extra=log_context)
            return {
                "qb_tax_entry_id": None,
                "estado": f"ERROR: El recibo {qb_receipt_id} no existe en QuickBooks o no se pudo obtener",
                "codigo_error": "RECEIPT_NOT_FOUND"
            }
        logger.info(f"Recibo {qb_receipt_id} validado exitosamente", extra=log_context)
        
        # Obtener moneda del recibo si no se proporcionó
        if not receipt_currency:
            receipt_currency_ref = receipt_info.get("CurrencyRef", {})
            receipt_currency = receipt_currency_ref.get("value") or receipt_info.get("CurrencyCode", "USD")
    
    # Usar USD por defecto si no hay moneda y validar que sea soportada
    if not receipt_currency:
        receipt_currency = "USD"
    else:
        receipt_currency = receipt_currency.upper()
        if receipt_currency not in MONEDAS_SOPORTADAS:
            logger.warning(
                f"Moneda '{receipt_currency}' no está en la lista de monedas soportadas. Usando {receipt_currency} de todas formas.",
                extra={**log_context, "currency": receipt_currency, "supported_currencies": MONEDAS_SOPORTADAS}
            )
    
    # Determinar cuenta de débito final (necesaria para validación)
    cuenta_debito_final = cuenta_debito or "Efectivo"
    
    # Si se proporciona tipo_impuesto, usar la cuenta predefinida si no se especificó cuenta_impuesto
    if tipo_impuesto and tipo_impuesto.upper() in TIPOS_IMPUESTO:
        if cuenta_impuesto == "Impuestos por pagar":  # Solo si es el default
            cuenta_impuesto = TIPOS_IMPUESTO[tipo_impuesto.upper()]
            logger.debug(f"Usando cuenta predefinida para {tipo_impuesto}: {cuenta_impuesto}", extra=log_context)
    
    # Validar cuentas contables si está habilitado
    if validar_cuentas:
        logger.debug("Validando existencia de cuentas contables", extra=log_context)
        
        if not _validar_cuenta_contable(cuenta_debito_final, access_token, realm_id, base_url):
            logger.error(f"Cuenta de débito '{cuenta_debito_final}' no encontrada en QuickBooks", extra=log_context)
            return {
                "qb_tax_entry_id": None,
                "estado": f"ERROR: La cuenta de débito '{cuenta_debito_final}' no existe en QuickBooks",
                "codigo_error": "DEBIT_ACCOUNT_NOT_FOUND"
            }
        
        if not _validar_cuenta_contable(cuenta_impuesto, access_token, realm_id, base_url):
            logger.error(f"Cuenta de impuesto '{cuenta_impuesto}' no encontrada en QuickBooks", extra=log_context)
            return {
                "qb_tax_entry_id": None,
                "estado": f"ERROR: La cuenta de impuesto '{cuenta_impuesto}' no existe en QuickBooks",
                "codigo_error": "TAX_ACCOUNT_NOT_FOUND"
            }
        logger.debug("Cuentas contables validadas exitosamente", extra=log_context)
    
    # Verificar si ya existe un asiento para esta transacción (prevención de duplicados)
    logger.debug("Verificando asientos duplicados")
    existing_entry_id = _buscar_asiento_duplicado(
        stripe_charge_id, qb_receipt_id, access_token, realm_id, base_url
    )
    if existing_entry_id:
        logger.warning(
            f"Asiento duplicado encontrado para transacción {stripe_charge_id}",
            extra={**log_context, "existing_entry_id": existing_entry_id}
        )
        _operation_stats["duplicate_preventions"] += 1
        return {
            "qb_tax_entry_id": str(existing_entry_id),
            "estado": "ADVERTENCIA: Ya existe un asiento de impuesto para esta transacción",
            "duplicado": True,
            "existing_entry_id": str(existing_entry_id),
            "codigo_error": "DUPLICATE_ENTRY_FOUND"
        }
    
    # Construir URL y headers
    url = f"{base_url}/v3/company/{realm_id}/journalentry"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Construir el asiento contable (Journal Entry)
    # Para un impuesto cobrado, la estructura típica es:
    # - Débito: Efectivo/Banco (porque recibimos el dinero del impuesto)
    # - Crédito: Impuestos por pagar (pasivo que debemos remitir a Hacienda)
    # 
    # La estructura del Journal Entry requiere que los débitos y créditos estén balanceados.
    
    # Formatear monto a string con 2 decimales para QuickBooks
    # (cuenta_debito_final ya está definida arriba)
    monto_formateado = f"{impuesto_monto:.2f}"
    
    debit_line = {
        "DetailType": "JournalEntryLineDetail",
        "Amount": monto_formateado,
        "Description": f"Impuesto cobrado Stripe {stripe_charge_id} - Recibo {qb_receipt_id}",
        "JournalEntryLineDetail": {
            "PostingType": "Debit",
            "AccountRef": {
                "name": cuenta_debito_final
            }
        }
    }
    
    # Línea 2: Crédito a la cuenta de impuestos por pagar (pasivo)
    credit_line = {
        "DetailType": "JournalEntryLineDetail",
        "Amount": monto_formateado,
        "Description": f"Impuesto IVA cobrado - Stripe {stripe_charge_id} - Recibo {qb_receipt_id}",
        "JournalEntryLineDetail": {
            "PostingType": "Credit",
            "AccountRef": {
                "name": cuenta_impuesto  # "Impuestos por pagar" o "Impuesto IVA"
            }
        }
    }
    
    # Validar que el asiento está balanceado
    if not _validar_balance_asiento(debit_line, credit_line):
        logger.error(
            f"Asiento no balanceado: débito={debit_line.get('Amount')}, crédito={credit_line.get('Amount')}",
            extra=log_context
        )
        return {
            "qb_tax_entry_id": None,
            "estado": f"ERROR: El asiento no está balanceado. Débito: {debit_line.get('Amount')}, Crédito: {credit_line.get('Amount')}",
            "codigo_error": "UNBALANCED_ENTRY"
        }
    logger.debug("Asiento validado: balanceado correctamente", extra=log_context)
    
    # Generar número de documento único y descriptivo
    # Limpiar stripe_charge_id para el DocNumber (solo alfanuméricos y guiones)
    charge_id_clean = ''.join(c for c in stripe_charge_id if c.isalnum() or c == '-')[:12]
    
    # Agregar tipo de impuesto al doc_number si está disponible
    tipo_prefix = f"{tipo_impuesto.upper()}-" if tipo_impuesto else "TAX-"
    doc_number = f"{tipo_prefix}{charge_id_clean}-{qb_receipt_id[:8]}"
    if len(doc_number) > 20:
        tipo_prefix_short = tipo_impuesto.upper()[:3] + "-" if tipo_impuesto else "TAX-"
        doc_number = f"{tipo_prefix_short}{charge_id_clean[:8]}-{qb_receipt_id[:6]}"
    
    # Agregar información adicional del recibo si está disponible
    receipt_date = ""
    receipt_customer = ""
    if receipt_info:
        receipt_date = receipt_info.get("TxnDate", "")
        customer_ref = receipt_info.get("CustomerRef", {})
        receipt_customer = customer_ref.get("name", "") or customer_ref.get("value", "")
    
    # Construir el payload del Journal Entry con información enriquecida
    private_note_lines = [
        f"Impuesto cobrado en Stripe",
        f"Transacción Stripe: {stripe_charge_id}",
        f"Recibo QuickBooks: {qb_receipt_id}",
        f"Monto impuesto: {monto_formateado}",
        f"Cuenta impuesto: {cuenta_impuesto}",
        f"Cuenta débito: {cuenta_debito_final}",
        f"Creado: {datetime.now().isoformat()}"
    ]
    
    if receipt_date:
        private_note_lines.append(f"Fecha recibo: {receipt_date}")
    if receipt_customer:
        private_note_lines.append(f"Cliente recibo: {receipt_customer}")
    
    payload = {
        "Line": [debit_line, credit_line],
        "TxnDate": receipt_date if receipt_date else "",  # Usar fecha del recibo si está disponible
        "PrivateNote": "\n".join(private_note_lines),
        "DocNumber": doc_number,
        "Memo": f"Impuesto Stripe {stripe_charge_id} vinculado al Recibo {qb_receipt_id}"
    }
    
    # Agregar CurrencyRef si la moneda no es USD
    if receipt_currency and receipt_currency.upper() != "USD":
        payload["CurrencyRef"] = {
            "value": receipt_currency.upper()
        }
        log_context["currency"] = receipt_currency.upper()
    
    duration_ms = 0
    try:
        logger.info("Enviando petición a QuickBooks para crear asiento", extra={
            **log_context,
            "doc_number": doc_number,
            "url": url
        })
        start_time = time.time()
        
        # Realizar la petición POST con retry
        response = _realizar_peticion_con_retry(
            url=url,
            headers=headers,
            payload=payload,
            max_retries=DEFAULT_MAX_RETRIES,
            retry_delay=DEFAULT_RETRY_DELAY,
            timeout=DEFAULT_TIMEOUT
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        logger.debug(f"Respuesta recibida de QuickBooks en {duration_ms}ms", extra={
            **log_context,
            "status_code": response.status_code,
            "duration_ms": duration_ms
        })
        
        # Si la respuesta es exitosa
        if response.status_code in [200, 201]:
            try:
                response_data = response.json()
                # QuickBooks API v3 devuelve el objeto en response_data["JournalEntry"]
                journal_entry = response_data.get("JournalEntry", {})
                qb_tax_entry_id = journal_entry.get("Id")
                
                # También intentar obtener de otros campos posibles
                if not qb_tax_entry_id:
                    qb_tax_entry_id = journal_entry.get("id") or journal_entry.get("Id") or response_data.get("Id")
                
                if qb_tax_entry_id:
                    sync_token = journal_entry.get("SyncToken", journal_entry.get("syncToken"))
                    txn_date = journal_entry.get("TxnDate", "")
                    
                    # Construir respuesta enriquecida con metadata
                    resultado = {
                        "qb_tax_entry_id": str(qb_tax_entry_id),
                        "estado": "Éxito",
                        "sync_token": sync_token if sync_token else None,
                        "monto_impuesto": monto_formateado,
                        "cuenta_impuesto": cuenta_impuesto,
                        "cuenta_debito": cuenta_debito_final,
                        "stripe_charge_id": stripe_charge_id,
                        "qb_receipt_id": qb_receipt_id,
                        "doc_number": doc_number,
                        "fecha_creacion": datetime.now().isoformat(),
                        "currency": receipt_currency.upper() if receipt_currency else "USD",
                        "tipo_impuesto": tipo_impuesto.upper() if tipo_impuesto else None
                    }
                    
                    if txn_date:
                        resultado["txn_date"] = txn_date
                    if receipt_info:
                        resultado["recibo_validado"] = True
                        if receipt_date:
                            resultado["fecha_recibo"] = receipt_date
                        if receipt_customer:
                            resultado["cliente_recibo"] = receipt_customer
                    if validar_cuentas:
                        resultado["cuentas_validadas"] = True
                    
                    # Logging estructurado de éxito
                    logger.info(
                        f"Asiento de impuesto creado exitosamente: {qb_tax_entry_id}",
                        extra={
                            **log_context,
                            "qb_tax_entry_id": str(qb_tax_entry_id),
                            "doc_number": doc_number,
                            "duration_ms": duration_ms,
                            "status": "success"
                        }
                    )
                    
                    _operation_stats["successful_operations"] += 1
                    return resultado
                else:
                    # Si no hay ID pero la respuesta fue exitosa, revisar la estructura
                    return {
                        "qb_tax_entry_id": None,
                        "estado": f"Éxito pero no se pudo obtener el ID del asiento. Respuesta: {response_data}"
                    }
            except Exception as e:
                return {
                    "qb_tax_entry_id": None,
                    "estado": f"Éxito pero error al parsear respuesta: {str(e)}. Respuesta raw: {response.text[:200]}"
                }
        
        # Si hay error, obtener detalles del error con mayor detalle
        error_code = response.status_code
        full_message = "Error desconocido"
        
        try:
            error_data = response.json()
            # QuickBooks puede devolver errores en diferentes formatos
            faults = error_data.get("Fault", {})
            errors = faults.get("Error", [])
            
            if errors:
                # Extraer todos los errores disponibles
                error_messages = []
                for err in errors:
                    err_msg = err.get("Message", "")
                    err_detail = err.get("Detail", "")
                    err_code = err.get("code", "")
                    err_element = err.get("element", "")
                    
                    msg_parts = []
                    if err_code:
                        msg_parts.append(f"Código: {err_code}")
                    if err_msg:
                        msg_parts.append(err_msg)
                    if err_detail:
                        msg_parts.append(f"Detalle: {err_detail}")
                    if err_element:
                        msg_parts.append(f"Elemento: {err_element}")
                    
                    if msg_parts:
                        error_messages.append(" | ".join(msg_parts))
                
                full_message = "; ".join(error_messages) if error_messages else "Error sin detalles"
            else:
                # Intentar otros formatos de error
                error_message = error_data.get("message") or error_data.get("error") or error_data.get("ErrorMessage")
                if error_message:
                    full_message = str(error_message)
                else:
                    full_message = response.text[:500] or "Error desconocido"
        except Exception as parse_error:
            # Si no se puede parsear, usar el texto de respuesta
            error_text = response.text[:500] if hasattr(response, 'text') else str(response)
            full_message = f"Error al parsear respuesta de QuickBooks: {error_text}. Excepción: {str(parse_error)}"
        
        # Logging estructurado de error
        logger.error(
            f"Error al crear asiento de impuesto: {error_code} - {full_message}",
            extra={
                **log_context,
                "error_code": error_code,
                "error_message": full_message,
                "status": "error"
            }
        )
        _operation_stats["failed_operations"] += 1
        return {
            "qb_tax_entry_id": None,
            "estado": f"{error_code}: {full_message}",
            "codigo_error": f"QB_API_ERROR_{error_code}"
        }
        
    except requests.exceptions.Timeout as e:
        logger.error(
            "Timeout al crear asiento de impuesto",
            extra={**log_context, "error_type": "timeout", "status": "error"}
        )
        _operation_stats["failed_operations"] += 1
        return {
            "qb_tax_entry_id": None,
            "estado": "ERROR_TIMEOUT: La petición a QuickBooks excedió el tiempo límite",
            "codigo_error": "TIMEOUT_ERROR"
        }
    except requests.exceptions.ConnectionError as e:
        logger.error(
            "Error de conexión al crear asiento de impuesto",
            extra={**log_context, "error_type": "connection", "status": "error"}
        )
        _operation_stats["failed_operations"] += 1
        return {
            "qb_tax_entry_id": None,
            "estado": "ERROR_CONNECTION: No se pudo conectar con QuickBooks API",
            "codigo_error": "CONNECTION_ERROR"
        }
    except requests.exceptions.RequestException as e:
        logger.error(
            f"Error en petición HTTP: {str(e)}",
            extra={**log_context, "error_type": "request", "error_message": str(e), "status": "error"}
        )
        _operation_stats["failed_operations"] += 1
        return {
            "qb_tax_entry_id": None,
            "estado": f"ERROR_REQUEST: {str(e)}",
            "codigo_error": "REQUEST_ERROR"
        }
    except Exception as e:
        logger.exception(
            f"Error inesperado al crear asiento de impuesto: {str(e)}",
            extra={**log_context, "error_type": "unexpected", "status": "error"}
        )
        _operation_stats["failed_operations"] += 1
        return {
            "qb_tax_entry_id": None,
            "estado": f"ERROR_INESPERADO: {str(e)}",
            "codigo_error": "UNEXPECTED_ERROR"
        }


# Función auxiliar para uso en DAGs de Airflow
def crear_asiento_impuesto_quickbooks_task(**context):
    """
    Wrapper para usar la función en DAGs de Airflow.
    Espera los siguientes parámetros en context['params']:
    - impuesto_monto: Monto del impuesto cobrado en Stripe
    - stripe_charge_id: ID de la transacción en Stripe
    - qb_receipt_id: ID del recibo original en QuickBooks
    - cuenta_impuesto: Nombre de la cuenta de impuestos (opcional, default: "Impuestos por pagar")
    - cuenta_debito: Nombre de la cuenta de débito (opcional, default: "Efectivo")
    - validar_recibo: Si validar que el recibo existe antes de crear asiento (opcional, default: True)
    - validar_cuentas: Si validar que las cuentas contables existan (opcional, default: False)
    - currency: Código de moneda (opcional, se usa del recibo si no se proporciona)
    - tipo_impuesto: Tipo de impuesto "IVA", "ISR", "IEPS" (opcional, usa cuenta predefinida)
    """
    params = context.get('params', {})
    impuesto_monto = params.get('impuesto_monto')
    stripe_charge_id = params.get('stripe_charge_id')
    qb_receipt_id = params.get('qb_receipt_id')
    cuenta_impuesto = params.get('cuenta_impuesto', 'Impuestos por pagar')
    cuenta_debito = params.get('cuenta_debito')  # Opcional
    validar_recibo = params.get('validar_recibo', True)  # Por defecto validar
    validar_cuentas = params.get('validar_cuentas', False)  # Por defecto no validar
    currency = params.get('currency')  # Opcional
    tipo_impuesto = params.get('tipo_impuesto')  # Opcional: "IVA", "ISR", "IEPS"
    
    if not impuesto_monto:
        raise ValueError("impuesto_monto es requerido en los parámetros")
    if not stripe_charge_id:
        raise ValueError("stripe_charge_id es requerido en los parámetros")
    if not qb_receipt_id:
        raise ValueError("qb_receipt_id es requerido en los parámetros")
    
    # Convertir impuesto_monto a float si es string
    try:
        impuesto_monto = float(impuesto_monto)
        impuesto_monto = round(impuesto_monto, 2)  # Redondear a 2 decimales
    except (ValueError, TypeError):
        raise ValueError(f"impuesto_monto debe ser un número válido: {impuesto_monto}")
    
    if impuesto_monto <= 0:
        raise ValueError(f"impuesto_monto debe ser mayor que cero, recibido: {impuesto_monto}")
    
    resultado = crear_asiento_impuesto_quickbooks(
        impuesto_monto=impuesto_monto,
        stripe_charge_id=stripe_charge_id,
        qb_receipt_id=qb_receipt_id,
        cuenta_impuesto=cuenta_impuesto,
        cuenta_debito=cuenta_debito,
        currency=currency,
        tipo_impuesto=tipo_impuesto,
        validar_recibo=validar_recibo,
        validar_cuentas=validar_cuentas
    )
    
    if resultado["estado"] == "Éxito":
        print(f"✓ Asiento de impuesto creado exitosamente en QuickBooks")
        print(f"  - ID Stripe: {stripe_charge_id}")
        print(f"  - ID Recibo QB: {qb_receipt_id}")
        print(f"  - ID Asiento Impuesto QB: {resultado['qb_tax_entry_id']}")
        print(f"  - Monto impuesto: {impuesto_monto}")
        print(f"  - Cuenta impuesto: {resultado.get('cuenta_impuesto', cuenta_impuesto)}")
        print(f"  - Cuenta débito: {resultado.get('cuenta_debito', cuenta_debito or 'Efectivo')}")
        if resultado.get('doc_number'):
            print(f"  - Número documento: {resultado['doc_number']}")
        if resultado.get('currency'):
            print(f"  - Moneda: {resultado['currency']}")
        if resultado.get('tipo_impuesto'):
            print(f"  - Tipo impuesto: {resultado['tipo_impuesto']}")
        if resultado.get('recibo_validado'):
            print(f"  - Recibo validado: ✓")
            if resultado.get('cliente_recibo'):
                print(f"  - Cliente: {resultado['cliente_recibo']}")
        if resultado.get('cuentas_validadas'):
            print(f"  - Cuentas validadas: ✓")
    else:
        print(f"✗ Error al crear asiento de impuesto: {resultado['estado']}")
    
    return resultado


def verificar_asiento_impuesto_quickbooks(
    qb_tax_entry_id: str,
    stripe_charge_id: Optional[str] = None,
    qb_access_token: Optional[str] = None,
    qb_realm_id: Optional[str] = None,
    qb_base: Optional[str] = None
) -> Dict[str, Any]:
    """
    Verifica que un asiento de impuesto existe en QuickBooks y obtiene su información.
    
    Args:
        qb_tax_entry_id: ID del asiento de impuesto en QuickBooks
        stripe_charge_id: ID de la transacción Stripe (opcional, para validación adicional)
        qb_access_token: Token de acceso de QuickBooks (opcional, usa env var si no se proporciona)
        qb_realm_id: ID de la compañía en QuickBooks (opcional, usa env var si no se proporciona)
        qb_base: URL base de la API de QuickBooks (opcional, usa env var si no se proporciona)
    
    Returns:
        Dict con:
            - existe: True si el asiento existe, False si no
            - monto: Monto del asiento si existe
            - fecha: Fecha del asiento si existe
            - detalles: Información adicional del asiento
    """
    access_token = qb_access_token or QUICKBOOKS_ACCESS_TOKEN
    realm_id = qb_realm_id or QUICKBOOKS_REALM_ID
    base_url = qb_base or QUICKBOOKS_BASE
    
    if not access_token or not realm_id:
        return {
            "existe": False,
            "error": "Configuración de QuickBooks incompleta"
        }
    
    url = f"{base_url}/v3/company/{realm_id}/journalentry/{qb_tax_entry_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            response_data = response.json()
            journal_entry = response_data.get("JournalEntry", {})
            
            # Validar que corresponde a la transacción Stripe si se proporciona
            memo = journal_entry.get("Memo", "")
            doc_number = journal_entry.get("DocNumber", "")
            
            if stripe_charge_id and stripe_charge_id not in memo and stripe_charge_id not in doc_number:
                return {
                    "existe": True,
                    "advertencia": "El asiento existe pero no corresponde a la transacción Stripe especificada",
                    "detalles": journal_entry
                }
            
            # Extraer monto de las líneas
            lines = journal_entry.get("Line", [])
            monto = None
            for line in lines:
                amount = line.get("Amount")
                if amount:
                    try:
                        monto = float(amount)
                        break
                    except (ValueError, TypeError):
                        continue
            
            return {
                "existe": True,
                "monto": monto,
                "fecha": journal_entry.get("TxnDate"),
                "doc_number": doc_number,
                "memo": memo,
                "detalles": journal_entry
            }
        elif response.status_code == 404:
            return {
                "existe": False,
                "error": "Asiento no encontrado en QuickBooks"
            }
        else:
            return {
                "existe": False,
                "error": f"Error al consultar asiento: {response.status_code}"
            }
    except Exception as e:
        logger.error(f"Error al verificar asiento {qb_tax_entry_id}: {str(e)}")
        return {
            "existe": False,
            "error": f"Excepción al verificar asiento: {str(e)}"
        }


def limpiar_cache_recibos() -> Dict[str, Any]:
    """
    Limpia el cache de información de recibos.
    
    Returns:
        Dict con información sobre la limpieza del cache
    """
    cantidad = len(_receipt_cache)
    _receipt_cache.clear()
    logger.info(f"Cache de recibos limpiado: {cantidad} entradas eliminadas")
    return {
        "cache_limpiado": True,
        "entradas_eliminadas": cantidad,
        "timestamp": datetime.now().isoformat()
    }


def obtener_estadisticas_cache_recibos() -> Dict[str, Any]:
    """
    Obtiene estadísticas sobre el cache de recibos.
    
    Returns:
        Dict con estadísticas del cache
    """
    cantidad = len(_receipt_cache)
    entradas_expiradas = 0
    tiempo_actual = time.time()
    
    for receipt_id, cached_data in list(_receipt_cache.items()):
        cached_time = cached_data.get("_cached_at", 0)
        if tiempo_actual - cached_time >= _receipt_cache_ttl:
            entradas_expiradas += 1
    
    return {
        "total_entradas": cantidad,
        "entradas_expiradas": entradas_expiradas,
        "entradas_activas": cantidad - entradas_expiradas,
        "ttl_segundos": _receipt_cache_ttl,
        "cache_keys": list(_receipt_cache.keys()) if cantidad <= 10 else None  # Solo si son pocas
    }


def buscar_asientos_por_recibo(
    qb_receipt_id: str,
    qb_access_token: Optional[str] = None,
    qb_realm_id: Optional[str] = None,
    qb_base: Optional[str] = None,
    limite: int = 20
) -> Dict[str, Any]:
    """
    Busca todos los asientos de impuesto vinculados a un recibo específico.
    
    Args:
        qb_receipt_id: ID del recibo en QuickBooks
        qb_access_token: Token de acceso de QuickBooks (opcional)
        qb_realm_id: ID de la compañía en QuickBooks (opcional)
        qb_base: URL base de la API de QuickBooks (opcional)
        limite: Número máximo de resultados a retornar (default: 20)
    
    Returns:
        Dict con lista de asientos encontrados y estadísticas
    """
    access_token = qb_access_token or QUICKBOOKS_ACCESS_TOKEN
    realm_id = qb_realm_id or QUICKBOOKS_REALM_ID
    base_url = qb_base or QUICKBOOKS_BASE
    
    if not access_token or not realm_id:
        return {
            "asientos": [],
            "total": 0,
            "error": "Configuración de QuickBooks incompleta"
        }
    
    query_url = f"{base_url}/v3/company/{realm_id}/query"
    query_headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    # Buscar journal entries que mencionen el recibo en el memo
    query = f"SELECT * FROM JournalEntry WHERE Memo LIKE '%{qb_receipt_id}%' MAXRESULTS {limite}"
    
    try:
        query_response = requests.get(
            f"{query_url}?query={query}",
            headers=query_headers,
            timeout=15
        )
        
        if query_response.status_code == 200:
            query_data = query_response.json()
            journal_entries = query_data.get("QueryResponse", {}).get("JournalEntry", [])
            
            # Normalizar a lista si es necesario
            if isinstance(journal_entries, dict):
                journal_entries = [journal_entries]
            elif not isinstance(journal_entries, list):
                journal_entries = []
            
            # Filtrar solo los que realmente están relacionados con el recibo
            asientos_vinculados = []
            for entry in journal_entries:
                memo = entry.get("Memo", "")
                doc_number = entry.get("DocNumber", "")
                if qb_receipt_id in memo or qb_receipt_id in doc_number:
                    # Extraer monto de las líneas
                    lines = entry.get("Line", [])
                    monto = None
                    for line in lines:
                        amount = line.get("Amount")
                        if amount:
                            try:
                                monto = float(amount)
                                break
                            except (ValueError, TypeError):
                                continue
                    
                    asientos_vinculados.append({
                        "qb_tax_entry_id": entry.get("Id"),
                        "doc_number": doc_number,
                        "monto": monto,
                        "fecha": entry.get("TxnDate"),
                        "memo": memo,
                        "sync_token": entry.get("SyncToken")
                    })
            
            return {
                "asientos": asientos_vinculados,
                "total": len(asientos_vinculados),
                "recibo_id": qb_receipt_id
            }
        else:
            return {
                "asientos": [],
                "total": 0,
                "error": f"Error al consultar QuickBooks: {query_response.status_code}"
            }
    except Exception as e:
        logger.error(f"Error al buscar asientos por recibo {qb_receipt_id}: {str(e)}")
        return {
            "asientos": [],
            "total": 0,
            "error": f"Excepción al buscar asientos: {str(e)}"
        }


def obtener_estadisticas_operaciones() -> Dict[str, Any]:
    """
    Obtiene estadísticas sobre las operaciones de creación de asientos de impuesto.
    
    Returns:
        Dict con estadísticas de operaciones
    """
    total = _operation_stats["total_operations"]
    exitosas = _operation_stats["successful_operations"]
    fallidas = _operation_stats["failed_operations"]
    
    tasa_exito = (exitosas / total * 100) if total > 0 else 0.0
    tasa_fallo = (fallidas / total * 100) if total > 0 else 0.0
    
    return {
        "total_operaciones": total,
        "operaciones_exitosas": exitosas,
        "operaciones_fallidas": fallidas,
        "prevenciones_duplicados": _operation_stats["duplicate_preventions"],
        "tasa_exito_porcentaje": round(tasa_exito, 2),
        "tasa_fallo_porcentaje": round(tasa_fallo, 2),
        "cache": {
            "hits": _operation_stats["cache_hits"],
            "misses": _operation_stats["cache_misses"],
            "hit_rate": round((_operation_stats["cache_hits"] / (_operation_stats["cache_hits"] + _operation_stats["cache_misses"]) * 100) if (_operation_stats["cache_hits"] + _operation_stats["cache_misses"]) > 0 else 0.0, 2)
        },
        "timestamp": datetime.now().isoformat()
    }


def reiniciar_estadisticas_operaciones() -> Dict[str, Any]:
    """
    Reinicia las estadísticas de operaciones.
    
    Returns:
        Dict confirmando el reinicio
    """
    global _operation_stats
    valores_anteriores = _operation_stats.copy()
    _operation_stats = {
        "total_operations": 0,
        "successful_operations": 0,
        "failed_operations": 0,
        "duplicate_preventions": 0,
        "cache_hits": 0,
        "cache_misses": 0
    }
    logger.info(f"Estadísticas reiniciadas. Valores anteriores: {valores_anteriores}")
    return {
        "estadisticas_reiniciadas": True,
        "valores_anteriores": valores_anteriores,
        "timestamp": datetime.now().isoformat()
    }


def crear_asientos_impuesto_batch(
    asientos: List[Dict[str, Any]],
    qb_access_token: Optional[str] = None,
    qb_realm_id: Optional[str] = None,
    qb_base: Optional[str] = None,
    batch_delay: float = 0.5,
    continue_on_error: bool = True
) -> Dict[str, Any]:
    """
    Crea múltiples asientos de impuesto en batch.
    
    Args:
        asientos: Lista de dicts con parámetros para cada asiento. Cada dict debe tener:
                 - impuesto_monto
                 - stripe_charge_id
                 - qb_receipt_id
                 - cuenta_impuesto (opcional)
                 - cuenta_debito (opcional)
                 - currency (opcional)
                 - tipo_impuesto (opcional)
                 - validar_recibo (opcional)
                 - validar_cuentas (opcional)
        qb_access_token: Token de acceso (opcional)
        qb_realm_id: Realm ID (opcional)
        qb_base: URL base (opcional)
        batch_delay: Delay entre asientos en segundos (default: 0.5)
        continue_on_error: Si continuar procesando aunque un asiento falle (default: True)
    
    Returns:
        Dict con resultados del batch processing
    """
    resultados = []
    exitosos = 0
    fallidos = 0
    duplicados = 0
    
    logger.info(f"Iniciando procesamiento batch de {len(asientos)} asientos de impuesto")
    start_time = time.time()
    
    for idx, asiento_params in enumerate(asientos, 1):
        try:
            logger.debug(f"Procesando asiento {idx}/{len(asientos)}")
            
            resultado = crear_asiento_impuesto_quickbooks(
                impuesto_monto=asiento_params.get("impuesto_monto"),
                stripe_charge_id=asiento_params.get("stripe_charge_id"),
                qb_receipt_id=asiento_params.get("qb_receipt_id"),
                cuenta_impuesto=asiento_params.get("cuenta_impuesto", "Impuestos por pagar"),
                cuenta_debito=asiento_params.get("cuenta_debito"),
                currency=asiento_params.get("currency"),
                tipo_impuesto=asiento_params.get("tipo_impuesto"),
                qb_access_token=qb_access_token,
                qb_realm_id=qb_realm_id,
                qb_base=qb_base,
                validar_recibo=asiento_params.get("validar_recibo", True),
                validar_cuentas=asiento_params.get("validar_cuentas", False)
            )
            
            resultados.append({
                "indice": idx,
                "stripe_charge_id": asiento_params.get("stripe_charge_id"),
                "qb_receipt_id": asiento_params.get("qb_receipt_id"),
                "resultado": resultado
            })
            
            if resultado.get("estado") == "Éxito":
                exitosos += 1
            elif resultado.get("duplicado"):
                duplicados += 1
                exitosos += 1  # Duplicado es considerado éxito
            else:
                fallidos += 1
                if not continue_on_error:
                    logger.error(f"Error en asiento {idx}, deteniendo batch")
                    break
            
            # Delay entre asientos para respetar rate limits
            if batch_delay > 0 and idx < len(asientos):
                time.sleep(batch_delay)
                
        except Exception as e:
            logger.exception(f"Excepción al procesar asiento {idx}: {str(e)}")
            resultados.append({
                "indice": idx,
                "stripe_charge_id": asiento_params.get("stripe_charge_id", "unknown"),
                "qb_receipt_id": asiento_params.get("qb_receipt_id", "unknown"),
                "resultado": {
                    "qb_tax_entry_id": None,
                    "estado": f"ERROR_EXCEPCION: {str(e)}",
                    "codigo_error": "BATCH_PROCESSING_EXCEPTION"
                }
            })
            fallidos += 1
            if not continue_on_error:
                break
    
    duration_seconds = time.time() - start_time
    
    return {
        "total": len(asientos),
        "exitosos": exitosos,
        "fallidos": fallidos,
        "duplicados": duplicados,
        "duracion_segundos": round(duration_seconds, 2),
        "tasa_exito_porcentaje": round((exitosos / len(asientos) * 100) if asientos else 0.0, 2),
        "resultados": resultados,
        "timestamp": datetime.now().isoformat()
    }


def verificar_health_quickbooks(
    qb_access_token: Optional[str] = None,
    qb_realm_id: Optional[str] = None,
    qb_base: Optional[str] = None
) -> Dict[str, Any]:
    """
    Realiza un health check de la API de QuickBooks.
    
    Args:
        qb_access_token: Token de acceso (opcional)
        qb_realm_id: Realm ID (opcional)
        qb_base: URL base (opcional)
    
    Returns:
        Dict con estado del health check
    """
    access_token = qb_access_token or QUICKBOOKS_ACCESS_TOKEN
    realm_id = qb_realm_id or QUICKBOOKS_REALM_ID
    base_url = qb_base or QUICKBOOKS_BASE
    
    if not access_token or not realm_id:
        return {
            "healthy": False,
            "error": "Configuración incompleta",
            "timestamp": datetime.now().isoformat()
        }
    
    # Detectar entorno (sandbox vs production)
    is_sandbox = "sandbox" in base_url.lower()
    
    health_url = f"{base_url}/v3/company/{realm_id}/companyinfo/{realm_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    try:
        start_time = time.time()
        response = requests.get(health_url, headers=headers, timeout=10)
        duration_ms = int((time.time() - start_time) * 1000)
        
        if response.status_code == 200:
            company_info = response.json().get("CompanyInfo", {})
            company_name = company_info.get("CompanyName", "Unknown")
            
            return {
                "healthy": True,
                "entorno": "sandbox" if is_sandbox else "production",
                "company_name": company_name,
                "realm_id": realm_id,
                "response_time_ms": duration_ms,
                "timestamp": datetime.now().isoformat()
            }
        elif response.status_code == 401:
            return {
                "healthy": False,
                "error": "Autenticación fallida - token inválido o expirado",
                "status_code": response.status_code,
                "entorno": "sandbox" if is_sandbox else "production",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "healthy": False,
                "error": f"Error HTTP {response.status_code}",
                "status_code": response.status_code,
                "entorno": "sandbox" if is_sandbox else "production",
                "timestamp": datetime.now().isoformat()
            }
    except requests.exceptions.Timeout:
        return {
            "healthy": False,
            "error": "Timeout al conectar con QuickBooks",
            "entorno": "sandbox" if is_sandbox else "production",
            "timestamp": datetime.now().isoformat()
        }
    except requests.exceptions.ConnectionError:
        return {
            "healthy": False,
            "error": "No se pudo conectar con QuickBooks API",
            "entorno": "sandbox" if is_sandbox else "production",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        return {
            "healthy": False,
            "error": f"Excepción: {str(e)}",
            "entorno": "sandbox" if is_sandbox else "production",
            "timestamp": datetime.now().isoformat()
        }


@task
def crear_asientos_impuesto_batch_task(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper de Airflow para crear múltiples asientos de impuesto en batch.
    
    Espera los siguientes parámetros en context['params']:
    - asientos: Lista de dicts con parámetros para cada asiento
    - batch_delay: Delay entre asientos en segundos (opcional, default: 0.5)
    - continue_on_error: Si continuar procesando aunque un asiento falle (opcional, default: True)
    """
    params = context.get('params', {})
    asientos = params.get('asientos', [])
    batch_delay = params.get('batch_delay', 0.5)
    continue_on_error = params.get('continue_on_error', True)
    
    if not asientos or not isinstance(asientos, list):
        raise ValueError("asientos debe ser una lista no vacía de dicts con parámetros")
    
    if len(asientos) == 0:
        raise ValueError("asientos no puede estar vacío")
    
    resultado_batch = crear_asientos_impuesto_batch(
        asientos=asientos,
        batch_delay=batch_delay,
        continue_on_error=continue_on_error
    )
    
    print(f"✓ Procesamiento batch completado")
    print(f"  - Total: {resultado_batch['total']}")
    print(f"  - Exitosos: {resultado_batch['exitosos']}")
    print(f"  - Fallidos: {resultado_batch['fallidos']}")
    print(f"  - Duplicados: {resultado_batch['duplicados']}")
    print(f"  - Tasa éxito: {resultado_batch['tasa_exito_porcentaje']}%")
    print(f"  - Duración: {resultado_batch['duracion_segundos']}s")
    
    if resultado_batch['fallidos'] > 0:
        print(f"\n✗ Detalle de fallos:")
        for r in resultado_batch['resultados']:
            if r['resultado'].get('estado') != 'Éxito' and not r['resultado'].get('duplicado'):
                print(f"  - Asiento {r['indice']} ({r['stripe_charge_id']}): {r['resultado'].get('estado')}")
    
    return resultado_batch


@task
def verificar_health_quickbooks_task(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper de Airflow para verificar el health check de QuickBooks.
    
    No requiere parámetros adicionales, usa las variables de entorno.
    """
    health = verificar_health_quickbooks()
    
    if health["healthy"]:
        print(f"✓ QuickBooks está disponible")
        print(f"  - Entorno: {health['entorno']}")
        print(f"  - Empresa: {health.get('company_name', 'N/A')}")
        print(f"  - Realm ID: {health.get('realm_id', 'N/A')}")
        print(f"  - Tiempo respuesta: {health.get('response_time_ms', 0)}ms")
    else:
        print(f"✗ QuickBooks no está disponible")
        print(f"  - Error: {health.get('error', 'Unknown')}")
        print(f"  - Entorno: {health.get('entorno', 'unknown')}")
        if health.get('status_code'):
            print(f"  - Status code: {health['status_code']}")
        raise Exception(f"Health check falló: {health.get('error', 'Unknown error')}")
    
    return health

