"""
Utilidades extendidas para operaciones comunes.

Incluye:
- Funciones de limpieza de datos
- Transformaciones útiles
- Helpers de conversión
- Validaciones rápidas
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def clean_campaign_name(name: str) -> str:
    """
    Limpia nombre de campaña removiendo caracteres especiales.
    
    Args:
        name: Nombre de campaña
        
    Returns:
        Nombre limpio
    """
    if not name:
        return ""
    
    # Remover caracteres especiales excepto espacios, guiones y guiones bajos
    cleaned = re.sub(r'[^\w\s\-_]', '', name)
    
    # Normalizar espacios múltiples
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned.strip()


def normalize_currency(value: Any, default: float = 0.0) -> float:
    """
    Normaliza valor de moneda a float.
    
    Args:
        value: Valor a normalizar
        default: Valor por defecto
        
    Returns:
        Float normalizado
    """
    if value is None:
        return default
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        # Remover símbolos de moneda y espacios
        cleaned = re.sub(r'[^\d.+-]', '', value)
        try:
            return float(cleaned)
        except ValueError:
            return default
    
    return default


def normalize_percentage(value: Any, default: float = 0.0) -> float:
    """
    Normaliza porcentaje a float.
    
    Args:
        value: Valor a normalizar
        default: Valor por defecto
        
    Returns:
        Float normalizado (ya dividido por 100 si viene como porcentaje)
    """
    if value is None:
        return default
    
    if isinstance(value, (int, float)):
        # Si es > 1, probablemente es porcentaje sin dividir
        if value > 1:
            return float(value) / 100
        return float(value)
    
    if isinstance(value, str):
        cleaned = re.sub(r'[^\d.+-]', '', value)
        try:
            num_value = float(cleaned)
            if num_value > 1:
                return num_value / 100
            return num_value
        except ValueError:
            return default
    
    return default


def sanitize_id(id_value: Any) -> str:
    """
    Sanitiza un ID removiendo caracteres inválidos.
    
    Args:
        id_value: ID a sanitizar
        
    Returns:
        ID sanitizado
    """
    if id_value is None:
        return ""
    
    id_str = str(id_value)
    
    # Remover caracteres no alfanuméricos excepto guiones y guiones bajos
    sanitized = re.sub(r'[^\w\-_]', '', id_str)
    
    return sanitized


def extract_domain(url: str) -> Optional[str]:
    """
    Extrae dominio de una URL.
    
    Args:
        url: URL completa
        
    Returns:
        Dominio extraído o None
    """
    if not url:
        return None
    
    try:
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc or None
    except Exception:
        return None


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Trunca texto a longitud máxima.
    
    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo a agregar si se trunca
        
    Returns:
        Texto truncado
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def flatten_dict(
    data: Dict[str, Any],
    separator: str = "_",
    prefix: str = ""
) -> Dict[str, Any]:
    """
    Aplana un diccionario anidado.
    
    Args:
        data: Diccionario a aplanar
        separator: Separador para keys anidadas
        prefix: Prefijo para keys
        
    Returns:
        Diccionario aplanado
    """
    items = []
    
    for key, value in data.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key
        
        if isinstance(value, dict):
            items.extend(flatten_dict(value, separator, new_key).items())
        else:
            items.append((new_key, value))
    
    return dict(items)


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fusiona múltiples diccionarios.
    
    Args:
        *dicts: Diccionarios a fusionar
        
    Returns:
        Diccionario fusionado
    """
    result = {}
    
    for d in dicts:
        if d:
            result.update(d)
    
    return result


def safe_get(
    data: Dict[str, Any],
    key_path: str,
    default: Any = None,
    separator: str = "."
) -> Any:
    """
    Obtiene valor de diccionario anidado de forma segura.
    
    Args:
        data: Diccionario
        key_path: Ruta de la key (ej: "user.profile.name")
        default: Valor por defecto
        separator: Separador de niveles
        
    Returns:
        Valor o default
    """
    keys = key_path.split(separator)
    value = data
    
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default
        
        if value is None:
            return default
    
    return value


def chunk_list(data: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Divide lista en chunks.
    
    Args:
        data: Lista a dividir
        chunk_size: Tamaño de cada chunk
        
    Returns:
        Lista de chunks
    """
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


def remove_duplicates(
    data: List[Dict[str, Any]],
    key_fields: List[str]
) -> List[Dict[str, Any]]:
    """
    Remueve duplicados basados en campos clave.
    
    Args:
        data: Lista de datos
        key_fields: Campos que definen unicidad
        
    Returns:
        Lista sin duplicados
    """
    seen = set()
    unique = []
    
    for record in data:
        key = tuple(str(record.get(field, "")) for field in key_fields)
        
        if key not in seen:
            seen.add(key)
            unique.append(record)
    
    return unique


def validate_email(email: str) -> bool:
    """
    Valida formato de email.
    
    Args:
        email: Email a validar
        
    Returns:
        True si es válido
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def parse_date_range(date_string: str) -> Optional[tuple]:
    """
    Parsea rango de fechas desde string.
    
    Args:
        date_string: String con rango (ej: "2024-01-01 to 2024-01-31")
        
    Returns:
        Tuple (start, end) o None
    """
    if not date_string:
        return None
    
    # Intentar diferentes formatos
    patterns = [
        r'(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})',
        r'(\d{4}-\d{2}-\d{2})\s*-\s*(\d{4}-\d{2}-\d{2})',
        r'(\d{4}/\d{2}/\d{2})\s+to\s+(\d{4}/\d{2}/\d{2})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, date_string)
        if match:
            start, end = match.groups()
            try:
                start_dt = datetime.strptime(start, "%Y-%m-%d")
                end_dt = datetime.strptime(end, "%Y-%m-%d")
                return (start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d"))
            except ValueError:
                try:
                    start_dt = datetime.strptime(start, "%Y/%m/%d")
                    end_dt = datetime.strptime(end, "%Y/%m/%d")
                    return (start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d"))
                except ValueError:
                    continue
    
    return None

