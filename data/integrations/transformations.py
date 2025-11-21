"""
Transformaciones de datos comunes
==================================

Funciones de transformación reutilizables para mapear datos entre diferentes sistemas.
"""
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


def normalize_email(email: Optional[str]) -> Optional[str]:
    """Normaliza email a minúsculas y sin espacios"""
    if not email:
        return None
    return email.strip().lower()


def normalize_phone(phone: Optional[str]) -> Optional[str]:
    """Normaliza número de teléfono removiendo caracteres especiales"""
    if not phone:
        return None
    # Remover espacios, guiones, paréntesis
    normalized = re.sub(r'[\s\-\(\)]', '', phone)
    return normalized


def format_currency(amount: Optional[float], currency: str = "USD") -> Optional[str]:
    """Formatea cantidad como moneda"""
    if amount is None:
        return None
    
    currency_symbols = {
        "USD": "$",
        "EUR": "€",
        "MXN": "$",
        "GBP": "£"
    }
    
    symbol = currency_symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def parse_date(date_str: Optional[str], formats: Optional[List[str]] = None) -> Optional[datetime]:
    """Parsea fecha desde string con múltiples formatos"""
    if not date_str:
        return None
    
    if formats is None:
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S%z"
        ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    logger.warning(f"No se pudo parsear fecha: {date_str}")
    return None


def format_date(date: Optional[datetime], format_str: str = "%Y-%m-%d") -> Optional[str]:
    """Formatea datetime a string"""
    if not date:
        return None
    return date.strftime(format_str)


def map_field_mapping(
    data: Dict[str, Any],
    field_mapping: Dict[str, str],
    default_value: Any = None
) -> Dict[str, Any]:
    """
    Mapea campos de un diccionario usando un mapeo de campos.
    
    Args:
        data: Diccionario de datos fuente
        field_mapping: Mapeo {campo_destino: campo_origen}
        default_value: Valor por defecto si el campo no existe
    
    Returns:
        Diccionario con campos mapeados
    """
    result = {}
    for dest_field, source_field in field_mapping.items():
        if source_field in data:
            result[dest_field] = data[source_field]
        elif default_value is not None:
            result[dest_field] = default_value
    return result


def hubspot_to_quickbooks_contact(hubspot_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transforma contacto de HubSpot a formato QuickBooks Customer"""
    # Mapeo de campos
    qb_data = {
        "GivenName": hubspot_data.get("firstname", ""),
        "FamilyName": hubspot_data.get("lastname", ""),
        "DisplayName": f"{hubspot_data.get('firstname', '')} {hubspot_data.get('lastname', '')}".strip(),
        "PrimaryEmailAddr": {
            "Address": normalize_email(hubspot_data.get("email"))
        },
        "PrimaryPhone": {
            "FreeFormNumber": normalize_phone(hubspot_data.get("phone"))
        }
    }
    
    # Agregar dirección si existe
    if hubspot_data.get("address"):
        qb_data["BillAddr"] = {
            "Line1": hubspot_data.get("address", {}).get("address"),
            "City": hubspot_data.get("address", {}).get("city"),
            "CountrySubDivisionCode": hubspot_data.get("address", {}).get("state"),
            "PostalCode": hubspot_data.get("address", {}).get("zip"),
            "Country": hubspot_data.get("address", {}).get("country", "US")
        }
    
    # Remover campos vacíos
    return {k: v for k, v in qb_data.items() if v}


def hubspot_to_sheets_contact(hubspot_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transforma contacto de HubSpot a formato para Google Sheets"""
    return {
        "ID": hubspot_data.get("hs_object_id"),
        "First Name": hubspot_data.get("firstname", ""),
        "Last Name": hubspot_data.get("lastname", ""),
        "Email": normalize_email(hubspot_data.get("email")),
        "Phone": normalize_phone(hubspot_data.get("phone")),
        "Company": hubspot_data.get("company", ""),
        "Created Date": hubspot_data.get("createdate", ""),
        "Last Modified": hubspot_data.get("hs_lastmodifieddate", ""),
    }


def quickbooks_to_hubspot_contact(qb_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transforma Customer de QuickBooks a formato HubSpot Contact"""
    # Extraer email y phone de objetos anidados
    email = ""
    phone = ""
    
    if isinstance(qb_data.get("PrimaryEmailAddr"), dict):
        email = qb_data["PrimaryEmailAddr"].get("Address", "")
    elif isinstance(qb_data.get("PrimaryEmailAddr"), str):
        email = qb_data["PrimaryEmailAddr"]
    
    if isinstance(qb_data.get("PrimaryPhone"), dict):
        phone = qb_data["PrimaryPhone"].get("FreeFormNumber", "")
    elif isinstance(qb_data.get("PrimaryPhone"), str):
        phone = qb_data["PrimaryPhone"]
    
    return {
        "firstname": qb_data.get("GivenName", ""),
        "lastname": qb_data.get("FamilyName", ""),
        "email": normalize_email(email),
        "phone": normalize_phone(phone),
        "company": qb_data.get("CompanyName", ""),
    }


def sheets_to_hubspot_contact(sheets_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transforma fila de Google Sheets a formato HubSpot Contact"""
    return {
        "firstname": sheets_data.get("First Name", ""),
        "lastname": sheets_data.get("Last Name", ""),
        "email": normalize_email(sheets_data.get("Email")),
        "phone": normalize_phone(sheets_data.get("Phone")),
        "company": sheets_data.get("Company", ""),
    }


def salesforce_to_hubspot_contact(sf_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transforma Contact de Salesforce a formato HubSpot Contact"""
    return {
        "firstname": sf_data.get("FirstName", ""),
        "lastname": sf_data.get("LastName", ""),
        "email": normalize_email(sf_data.get("Email")),
        "phone": normalize_phone(sf_data.get("Phone")),
        "company": sf_data.get("Account", {}).get("Name", "") if isinstance(sf_data.get("Account"), dict) else sf_data.get("AccountName", ""),
    }


def hubspot_deal_to_quickbooks_invoice(hubspot_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transforma Deal de HubSpot a Invoice de QuickBooks"""
    amount = float(hubspot_data.get("amount", 0) or 0)
    
    qb_data = {
        "DocNumber": hubspot_data.get("dealname", ""),
        "TxnDate": format_date(parse_date(hubspot_data.get("closedate")), "%Y-%m-%d"),
        "Line": [
            {
                "Amount": amount,
                "DetailType": "SalesItemLineDetail",
                "SalesItemLineDetail": {
                    "ItemRef": {
                        "value": hubspot_data.get("quickbooks_item_id", "1")
                    }
                }
            }
        ],
        "CustomerRef": {
            "value": hubspot_data.get("quickbooks_customer_id", "")
        }
    }
    
    return {k: v for k, v in qb_data.items() if v}


def apply_defaults(data: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
    """Aplica valores por defecto a campos faltantes"""
    result = data.copy()
    for key, value in defaults.items():
        if key not in result or not result[key]:
            result[key] = value
    return result


def remove_empty_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remueve campos vacíos o None del diccionario"""
    return {k: v for k, v in data.items() if v is not None and v != ""}


def convert_types(data: Dict[str, Any], type_mapping: Dict[str, type]) -> Dict[str, Any]:
    """Convierte tipos de datos según mapeo"""
    result = {}
    for key, value in data.items():
        if key in type_mapping:
            try:
                result[key] = type_mapping[key](value)
            except (ValueError, TypeError):
                logger.warning(f"No se pudo convertir {key} a {type_mapping[key]}")
                result[key] = value
        else:
            result[key] = value
    return result


def create_transformer(
    field_mapping: Dict[str, str],
    transformations: Optional[Dict[str, Callable]] = None,
    defaults: Optional[Dict[str, Any]] = None
) -> Callable:
    """
    Crea una función de transformación personalizada.
    
    Args:
        field_mapping: Mapeo {campo_destino: campo_origen}
        transformations: Funciones de transformación por campo {campo: func}
        defaults: Valores por defecto {campo: valor}
    
    Returns:
        Función de transformación
    """
    def transform(data: Dict[str, Any]) -> Dict[str, Any]:
        result = map_field_mapping(data, field_mapping, None)
        
        # Aplicar transformaciones
        if transformations:
            for field, transform_func in transformations.items():
                if field in result:
                    result[field] = transform_func(result[field])
        
        # Aplicar defaults
        if defaults:
            result = apply_defaults(result, defaults)
        
        # Remover campos vacíos
        result = remove_empty_fields(result)
        
        return result
    
    return transform


