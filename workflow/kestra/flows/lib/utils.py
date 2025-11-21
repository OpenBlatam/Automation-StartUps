"""
Utilidades generales para las librerías de workflows.

Características:
- Transformación de datos
- Validación de inputs
- Serialización/deserialización
- Helpers para logging
- Formateo de datos
"""
import json
import logging
import re
import time
from typing import Any, Dict, Optional, List, Callable, TypeVar
from datetime import datetime
from dataclasses import asdict, is_dataclass

logger = logging.getLogger(__name__)

T = TypeVar('T')


def safe_json_loads(s: str, default: Any = None) -> Any:
    """
    Carga JSON de forma segura.
    
    Args:
        s: String JSON
        default: Valor por defecto si falla
    
    Returns:
        Objeto parseado o default
    """
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        logger.debug(f"Failed to parse JSON: {s[:100]}")
        return default


def safe_json_dumps(obj: Any, default: Optional[str] = None) -> str:
    """
    Serializa objeto a JSON de forma segura.
    
    Args:
        obj: Objeto a serializar
        default: Valor por defecto si falla
    
    Returns:
        String JSON o default
    """
    try:
        if is_dataclass(obj):
            obj = asdict(obj)
        return json.dumps(obj, default=str, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        logger.debug(f"Failed to serialize to JSON: {e}")
        return default or "{}"


def normalize_string(s: str, max_length: Optional[int] = None, strip: bool = True) -> str:
    """
    Normaliza un string.
    
    Args:
        s: String a normalizar
        max_length: Longitud máxima (None para sin límite)
        strip: Si eliminar espacios al inicio/fin
    
    Returns:
        String normalizado
    """
    if not isinstance(s, str):
        s = str(s)
    
    if strip:
        s = s.strip()
    
    # Normalizar espacios múltiples
    s = re.sub(r'\s+', ' ', s)
    
    if max_length and len(s) > max_length:
        s = s[:max_length]
    
    return s


def normalize_email(email: str) -> Optional[str]:
    """
    Normaliza un email.
    
    Args:
        email: Email a normalizar
    
    Returns:
        Email normalizado o None si es inválido
    """
    if not email or not isinstance(email, str):
        return None
    
    email = email.strip().lower()
    
    # Validación básica
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return None
    
    return email


def truncate_string(s: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Trunca un string a una longitud máxima.
    
    Args:
        s: String a truncar
        max_length: Longitud máxima
        suffix: Sufijo a agregar si se trunca
    
    Returns:
        String truncado
    """
    if not s or len(s) <= max_length:
        return s or ""
    
    return s[:max_length - len(suffix)] + suffix


def sanitize_for_logging(data: Dict[str, Any], keys_to_mask: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Sanitiza datos para logging (oculta valores sensibles).
    
    Args:
        data: Diccionario con datos
        keys_to_mask: Lista de keys a ocultar (por defecto: password, token, secret, key, api_key)
    
    Returns:
        Diccionario sanitizado
    """
    if keys_to_mask is None:
        keys_to_mask = ["password", "token", "secret", "key", "api_key", "authorization", "auth"]
    
    sanitized = {}
    for key, value in data.items():
        key_lower = key.lower()
        if any(mask in key_lower for mask in keys_to_mask):
            sanitized[key] = "***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_for_logging(value, keys_to_mask)
        elif isinstance(value, str) and len(value) > 100:
            sanitized[key] = truncate_string(value, 100)
        else:
            sanitized[key] = value
    
    return sanitized


def format_duration(seconds: float) -> str:
    """
    Formatea una duración en segundos a string legible.
    
    Args:
        seconds: Duración en segundos
    
    Returns:
        String formateado (ej: "1.5s", "2m 30s")
    """
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"


def parse_timestamp(ts: Any) -> Optional[datetime]:
    """
    Parsea un timestamp a datetime.
    
    Args:
        ts: Timestamp (int, float, str ISO 8601, datetime)
    
    Returns:
        Datetime o None si no se puede parsear
    """
    if ts is None:
        return None
    
    if isinstance(ts, datetime):
        return ts
    
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts)
    
    if isinstance(ts, str):
        # Intentar ISO 8601
        try:
            return datetime.fromisoformat(ts.replace('Z', '+00:00'))
        except ValueError:
            pass
        
        # Intentar timestamp
        try:
            return datetime.fromtimestamp(float(ts))
        except (ValueError, TypeError):
            pass
    
    return None


def chunk_list(items: List[T], chunk_size: int) -> List[List[T]]:
    """
    Divide una lista en chunks.
    
    Args:
        items: Lista a dividir
        chunk_size: Tamaño de cada chunk
    
    Returns:
        Lista de chunks
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def get_nested_value(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Obtiene un valor anidado de un diccionario usando path con puntos.
    
    Args:
        data: Diccionario
        path: Path con puntos (ej: "user.profile.name")
        default: Valor por defecto
    
    Returns:
        Valor encontrado o default
    """
    keys = path.split(".")
    current = data
    
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    
    return current


def set_nested_value(data: Dict[str, Any], path: str, value: Any) -> None:
    """
    Establece un valor anidado en un diccionario usando path con puntos.
    
    Args:
        data: Diccionario
        path: Path con puntos (ej: "user.profile.name")
        value: Valor a establecer
    """
    keys = path.split(".")
    current = data
    
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value


def retry_on_exception(
    func: Callable[[], T],
    max_attempts: int = 3,
    exceptions: tuple = (Exception,),
    delay: float = 1.0,
    backoff: float = 2.0
) -> T:
    """
    Ejecuta una función con retry automático.
    
    Args:
        func: Función a ejecutar
        max_attempts: Número máximo de intentos
        exceptions: Tupla de excepciones a capturar
        delay: Delay inicial en segundos
        backoff: Multiplicador de backoff
    
    Returns:
        Resultado de la función
    
    Raises:
        Última excepción si todos los intentos fallan
    """
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            if attempt < max_attempts - 1:
                wait_time = delay * (backoff ** attempt)
                logger.debug(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
    
    raise last_exception

