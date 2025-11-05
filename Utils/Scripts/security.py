"""
Funciones de seguridad y validación
"""
import re
import hashlib
import secrets
from typing import Optional

def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """Sanitiza input del usuario eliminando caracteres peligrosos"""
    if not text:
        return ''
    
    # Remover caracteres de control
    sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    # Limitar longitud
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()

def validate_sql_injection(text: str) -> bool:
    """Detecta posibles intentos de SQL injection"""
    sql_patterns = [
        r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
        r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",
        r"\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))",
        r"((\%27)|(\'))union",
        r"exec(\s|\+)+(s|x)p\w+",
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False
    
    return True

def generate_csrf_token() -> str:
    """Genera un token CSRF"""
    return secrets.token_urlsafe(32)

def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hashea una contraseña usando SHA256 con salt"""
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Combinar password y salt
    combined = f"{password}{salt}".encode('utf-8')
    hashed = hashlib.sha256(combined).hexdigest()
    
    return hashed, salt

def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verifica una contraseña contra su hash"""
    new_hash, _ = hash_password(password, salt)
    return new_hash == hashed

def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """Valida la extensión de un archivo"""
    if not filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return extension in [ext.lower() for ext in allowed_extensions]

def rate_limit_key(ip: str, endpoint: str) -> str:
    """Genera una clave única para rate limiting"""
    return f"{ip}:{endpoint}"

def is_safe_path(path: str) -> bool:
    """Verifica que un path sea seguro (sin directory traversal)"""
    import os
    # Remover componentes peligrosos
    dangerous = ['..', '~', '/etc', '/root', '/var']
    
    normalized = os.path.normpath(path)
    for danger in dangerous:
        if danger in normalized:
            return False
    
    return True

