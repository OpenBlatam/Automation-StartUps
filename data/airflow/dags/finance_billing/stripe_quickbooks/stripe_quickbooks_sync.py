"""
Módulo para sincronizar clientes de Stripe con QuickBooks.
Cuando se crea un nuevo cliente en Stripe, verifica en QuickBooks si existe por correo.
Si no existe, crea uno; si existe, actualiza los datos de dirección/país.
"""
import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)


QUICKBOOKS_CLIENT_ID = os.environ.get("QUICKBOOKS_CLIENT_ID", "")
QUICKBOOKS_CLIENT_SECRET = os.environ.get("QUICKBOOKS_CLIENT_SECRET", "")
QUICKBOOKS_REFRESH_TOKEN = os.environ.get("QUICKBOOKS_REFRESH_TOKEN", "")
QUICKBOOKS_ACCESS_TOKEN = os.environ.get("QUICKBOOKS_ACCESS_TOKEN", "")
QUICKBOOKS_COMPANY_ID = os.environ.get("QUICKBOOKS_COMPANY_ID", "")
QUICKBOOKS_REALM_ID = os.environ.get("QUICKBOOKS_REALM_ID", "")
QUICKBOOKS_ENVIRONMENT = os.environ.get("QUICKBOOKS_ENVIRONMENT", "production")  # production or sandbox
QUICKBOOKS_BASE = os.environ.get(
    "QUICKBOOKS_BASE",
    "https://quickbooks.api.intuit.com" if QUICKBOOKS_ENVIRONMENT == "production"
    else "https://sandbox-quickbooks.api.intuit.com"
)


def _get_access_token(
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    refresh_token: Optional[str] = None,
) -> str:
    """
    Obtiene un access token de QuickBooks usando OAuth2 refresh token.
    
    Returns:
        str: Access token
    """
    client_id = client_id or QUICKBOOKS_CLIENT_ID
    client_secret = client_secret or QUICKBOOKS_CLIENT_SECRET
    refresh_token = refresh_token or QUICKBOOKS_REFRESH_TOKEN
    
    if not client_id or not client_secret or not refresh_token:
        raise ValueError("QUICKBOOKS_CLIENT_ID, QUICKBOOKS_CLIENT_SECRET y QUICKBOOKS_REFRESH_TOKEN son requeridos")
    
    url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    auth = (client_id, client_secret)
    
    try:
        logger.debug("Obteniendo access token de QuickBooks OAuth2")
        response = requests.post(url, headers=headers, data=data, auth=auth, timeout=30)
        response.raise_for_status()
        access_token = response.json()["access_token"]
        logger.debug("Access token obtenido exitosamente")
        return access_token
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al obtener access token de QuickBooks: {str(e)}")
        raise RuntimeError(f"Error al obtener access token de QuickBooks: {str(e)}")


def _buscar_cliente_por_email(
    email: str,
    access_token: str,
    company_id: Optional[str] = None,
    quickbooks_base: Optional[str] = None
) -> Optional[dict]:
    """
    Busca un cliente en QuickBooks por su correo electrónico.
    
    Args:
        email: Correo electrónico del cliente
        access_token: Token de acceso de QuickBooks
        company_id: ID de la compañía en QuickBooks (opcional, usa env var si no se proporciona)
        quickbooks_base: URL base de QuickBooks API (opcional, usa env var si no se proporciona)
    
    Returns:
        dict con datos del cliente si se encuentra, None si no existe
    """
    # Usar QUICKBOOKS_REALM_ID si está disponible (común en el proyecto), sino QUICKBOOKS_COMPANY_ID
    company_id = company_id or QUICKBOOKS_REALM_ID or QUICKBOOKS_COMPANY_ID
    base_url = quickbooks_base or QUICKBOOKS_BASE
    
    if not company_id:
        raise ValueError("QUICKBOOKS_REALM_ID o QUICKBOOKS_COMPANY_ID es requerido")
    
    if not email:
        return None
    
    # Escapar comillas simples en el email para la query (QuickBooks usa comillas simples para strings)
    escaped_email = email.replace("'", "''")
    
    # Query para buscar cliente por email (QuickBooks Query Language)
    query = f"SELECT * FROM Customer WHERE PrimaryEmailAddr.Address = '{escaped_email}' MAXRESULTS 1"
    url = f"{base_url}/v3/company/{company_id}/query"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/text"
    }
    params = {"minorversion": "65"}
    
    try:
        logger.debug(f"Buscando cliente en QuickBooks por email: {email}")
        response = requests.get(url, headers=headers, params={**params, "query": query}, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            query_response = data.get("QueryResponse", {})
            
            # QuickBooks devuelve Customer como objeto único si hay 1 resultado, o array si hay múltiples
            customers = query_response.get("Customer")
            
            if customers:
                # QuickBooks puede devolver un array o un objeto único
                customer = customers[0] if isinstance(customers, list) else customers
                customer_id = customer.get("Id", "unknown")
                logger.info(f"Cliente encontrado en QuickBooks: ID={customer_id}, email={email}")
                return customer
            
            # Si maxResults es 0 o no hay resultados, Customer no existe en la respuesta
            logger.debug(f"No se encontró cliente en QuickBooks para email: {email}")
            return None
        elif response.status_code == 400:
            # Puede ser que no haya resultados o error de sintaxis
            try:
                error_data = response.json()
                # Si es un error de "no results", es válido retornar None
                fault = error_data.get("Fault", {})
                error_detail = fault.get("Error", [{}])[0].get("Detail", "")
                if "no results" in error_detail.lower() or "record not found" in error_detail.lower():
                    return None
            except:
                pass
            return None
        
        return None
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error al buscar cliente en QuickBooks: {str(e)}")


def sincronizar_cliente_stripe_quickbooks(
    nombre_cliente: str,
    correo_cliente: str,
    pais: str,
    quickbooks_client_id: Optional[str] = None,
    quickbooks_client_secret: Optional[str] = None,
    quickbooks_refresh_token: Optional[str] = None,
    quickbooks_company_id: Optional[str] = None,
    quickbooks_base: Optional[str] = None
) -> str:
    """
    Sincroniza un cliente de Stripe con QuickBooks.
    Verifica si existe un cliente con ese correo en QuickBooks.
    Si no existe, crea uno; si existe, actualiza los datos de dirección/país.
    
    Args:
        nombre_cliente: Nombre del cliente
        correo_cliente: Correo electrónico del cliente (usado para buscar)
        pais: País del cliente
        quickbooks_client_id: Client ID de QuickBooks (opcional, usa env var si no se proporciona)
        quickbooks_client_secret: Client Secret de QuickBooks (opcional, usa env var si no se proporciona)
        quickbooks_refresh_token: Refresh Token de QuickBooks (opcional, usa env var si no se proporciona)
        quickbooks_company_id: Company ID de QuickBooks (opcional, usa env var si no se proporciona)
        quickbooks_base: URL base de QuickBooks API (opcional, usa env var si no se proporciona)
    
    Returns:
        str: 'creado {qb_customer_id}' o 'actualizado {qb_customer_id}', o mensaje de error
    """
    # Validar parámetros requeridos
    if not nombre_cliente:
        return "ERROR: nombre_cliente es requerido"
    if not correo_cliente:
        return "ERROR: correo_cliente es requerido"
    if not pais:
        return "ERROR: pais es requerido"
    
    try:
        # Obtener access token (usar directo si está disponible, sino obtener con OAuth2)
        access_token = None
        if QUICKBOOKS_ACCESS_TOKEN:
            access_token = QUICKBOOKS_ACCESS_TOKEN
        else:
            access_token = _get_access_token(
                client_id=quickbooks_client_id,
                client_secret=quickbooks_client_secret,
                refresh_token=quickbooks_refresh_token
            )
        
        # Usar QUICKBOOKS_REALM_ID si está disponible (común en el proyecto), sino QUICKBOOKS_COMPANY_ID
        company_id = quickbooks_company_id or QUICKBOOKS_REALM_ID or QUICKBOOKS_COMPANY_ID
        base_url = quickbooks_base or QUICKBOOKS_BASE
        
        if not company_id:
            return "ERROR: QUICKBOOKS_REALM_ID o QUICKBOOKS_COMPANY_ID no configurado"
        
        logger.info(
            f"Iniciando sincronización cliente Stripe → QuickBooks",
            extra={
                "nombre_cliente": nombre_cliente,
                "correo_cliente": correo_cliente,
                "pais": pais,
            }
        )
        
        # Buscar cliente por email
        cliente_existente = _buscar_cliente_por_email(
            email=correo_cliente,
            access_token=access_token,
            company_id=company_id,
            quickbooks_base=base_url
        )
        
        url = f"{base_url}/v3/company/{company_id}/customer"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        params = {"minorversion": "65"}
        
        # Preparar datos del cliente
        # Dividir nombre en FirstName y LastName (si es posible)
        partes_nombre = nombre_cliente.strip().split(maxsplit=1)
        first_name = partes_nombre[0] if partes_nombre else nombre_cliente
        last_name = partes_nombre[1] if len(partes_nombre) > 1 else ""
        
        if cliente_existente:
            # Actualizar cliente existente
            qb_customer_id = cliente_existente.get("Id")
            sync_token = cliente_existente.get("SyncToken")
            
            # Actualizar dirección/país
            bill_addr = cliente_existente.get("BillAddr", {})
            
            payload = {
                "Id": qb_customer_id,
                "SyncToken": sync_token,
                "DisplayName": nombre_cliente,
                "GivenName": first_name,
                "FamilyName": last_name,
                "PrimaryEmailAddr": {
                    "Address": correo_cliente
                },
                "BillAddr": {
                    **bill_addr,
                    "Country": pais,
                    "CountrySubDivisionCode": ""  # Se puede actualizar si se proporciona estado/provincia
                }
            }
            
            try:
                logger.debug(f"Actualizando cliente existente en QuickBooks: ID={qb_customer_id}")
                response = requests.post(url, headers=headers, json=payload, params=params, timeout=30)
                
                # Manejo de rate limiting (429 Too Many Requests)
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", "60"))
                    logger.warning(f"Rate limited por QuickBooks, retry after {retry_after}s")
                    return f"ERROR_RATE_LIMIT: Rate limited, retry after {retry_after} seconds"
                
                if response.status_code == 200:
                    customer_data = response.json().get("Customer", {})
                    updated_id = customer_data.get("Id", qb_customer_id)
                    logger.info(f"Cliente actualizado exitosamente en QuickBooks: ID={updated_id}")
                    return f"actualizado {updated_id}"
                else:
                    error_data = response.json() if response.headers.get("Content-Type", "").startswith("application/json") else {}
                    error_message = error_data.get("Fault", {}).get("Error", [{}])[0].get("Detail", response.text)
                    logger.error(f"Error al actualizar cliente en QuickBooks: {error_message}")
                    return f"ERROR_{response.status_code}: {error_message}"
            except requests.exceptions.Timeout:
                logger.error("Timeout al actualizar cliente en QuickBooks")
                return "ERROR_TIMEOUT: La petición a QuickBooks excedió el tiempo límite"
            except requests.exceptions.ConnectionError:
                logger.error("Error de conexión al actualizar cliente en QuickBooks")
                return "ERROR_CONNECTION: No se pudo conectar con QuickBooks API"
            except requests.exceptions.RequestException as e:
                logger.error(f"Error de red al actualizar cliente en QuickBooks: {str(e)}")
                return f"ERROR_REQUEST: {str(e)}"
        else:
            # Crear nuevo cliente
            payload = {
                "DisplayName": nombre_cliente,
                "GivenName": first_name,
                "FamilyName": last_name,
                "PrimaryEmailAddr": {
                    "Address": correo_cliente
                },
                "BillAddr": {
                    "Country": pais
                }
            }
            
            try:
                logger.debug("Creando nuevo cliente en QuickBooks")
                response = requests.post(url, headers=headers, json=payload, params=params, timeout=30)
                
                # Manejo de rate limiting (429 Too Many Requests)
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", "60"))
                    logger.warning(f"Rate limited por QuickBooks, retry after {retry_after}s")
                    return f"ERROR_RATE_LIMIT: Rate limited, retry after {retry_after} seconds"
                
                if response.status_code == 200:
                    customer_data = response.json().get("Customer", {})
                    qb_customer_id = customer_data.get("Id")
                    if qb_customer_id:
                        logger.info(f"Cliente creado exitosamente en QuickBooks: ID={qb_customer_id}")
                        return f"creado {qb_customer_id}"
                    else:
                        logger.error("No se pudo obtener el ID del cliente creado en QuickBooks")
                        return "ERROR: No se pudo obtener el ID del cliente creado"
                else:
                    error_data = response.json() if response.headers.get("Content-Type", "").startswith("application/json") else {}
                    error_message = error_data.get("Fault", {}).get("Error", [{}])[0].get("Detail", response.text)
                    logger.error(f"Error al crear cliente en QuickBooks: {error_message}")
                    return f"ERROR_{response.status_code}: {error_message}"
            except requests.exceptions.Timeout:
                logger.error("Timeout al crear cliente en QuickBooks")
                return "ERROR_TIMEOUT: La petición a QuickBooks excedió el tiempo límite"
            except requests.exceptions.ConnectionError:
                logger.error("Error de conexión al crear cliente en QuickBooks")
                return "ERROR_CONNECTION: No se pudo conectar con QuickBooks API"
            except requests.exceptions.RequestException as e:
                logger.error(f"Error de red al crear cliente en QuickBooks: {str(e)}")
                return f"ERROR_REQUEST: {str(e)}"
                
    except ValueError as e:
        return f"ERROR_VALIDATION: {str(e)}"
    except RuntimeError as e:
        return f"ERROR_AUTH: {str(e)}"
    except requests.exceptions.Timeout:
        return "ERROR_TIMEOUT: La petición a QuickBooks excedió el tiempo límite"
    except requests.exceptions.ConnectionError:
        return "ERROR_CONNECTION: No se pudo conectar con QuickBooks API"
    except Exception as e:
        return f"ERROR_INESPERADO: {str(e)}"


# Función auxiliar para uso en DAGs de Airflow
def sincronizar_cliente_stripe_quickbooks_task(**context):
    """
    Wrapper para usar la función en DAGs de Airflow.
    Espera 'nombre_cliente', 'correo_cliente' y 'pais' en los parámetros del contexto.
    """
    params = context.get('params', {})
    nombre_cliente = params.get('nombre_cliente')
    correo_cliente = params.get('correo_cliente')
    pais = params.get('pais')
    
    if not nombre_cliente:
        raise ValueError("nombre_cliente es requerido en los parámetros")
    if not correo_cliente:
        raise ValueError("correo_cliente es requerido en los parámetros")
    if not pais:
        raise ValueError("pais es requerido en los parámetros")
    
    resultado = sincronizar_cliente_stripe_quickbooks(
        nombre_cliente=nombre_cliente,
        correo_cliente=correo_cliente,
        pais=pais
    )
    
    if resultado.startswith("creado") or resultado.startswith("actualizado"):
        print(f"✓ Cliente sincronizado exitosamente: {resultado}")
    else:
        print(f"✗ Error al sincronizar cliente: {resultado}")
    
    return resultado

