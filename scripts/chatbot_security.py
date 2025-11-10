#!/usr/bin/env python3
"""
Mejoras de Seguridad para Chatbots
Incluye validación de entrada, sanitización y protección contra ataques
"""

import re
import html
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote, unquote


class SecurityValidator:
    """Validador de seguridad para chatbots"""
    
    # Patrones de ataques comunes
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|#|/\*|\*/)",
        r"(\b(UNION|OR|AND)\s+\d+)",
        r"('|;|\"|`|\\|/)",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
    ]
    
    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`$(){}[\]<>]",
        r"\b(cat|ls|pwd|whoami|id|uname|ps|kill|rm|mv|cp)\b",
        r"\.\./",
        r"\.\.\\",
    ]
    
    def __init__(self):
        self.max_length = 2000
        self.blocked_patterns = []
        self.allowed_chars_pattern = re.compile(r'^[a-zA-Z0-9\s\.,;:!?¡¿áéíóúÁÉÍÓÚñÑüÜ\-_@#$%&()]+$', re.UNICODE)
    
    def validate_input(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Valida entrada del usuario.
        
        Returns:
            (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, "El mensaje no puede estar vacío"
        
        if len(text) > self.max_length:
            return False, f"El mensaje es demasiado largo (máximo {self.max_length} caracteres)"
        
        # Verificar SQL injection
        if self._check_patterns(text, self.SQL_INJECTION_PATTERNS):
            return False, "Entrada no válida detectada"
        
        # Verificar XSS
        if self._check_patterns(text, self.XSS_PATTERNS):
            return False, "Entrada no válida detectada"
        
        # Verificar command injection
        if self._check_patterns(text, self.COMMAND_INJECTION_PATTERNS):
            return False, "Entrada no válida detectada"
        
        # Verificar caracteres permitidos (opcional, puede ser muy restrictivo)
        # if not self.allowed_chars_pattern.match(text):
        #     return False, "Caracteres no permitidos detectados"
        
        return True, None
    
    def _check_patterns(self, text: str, patterns: List[str]) -> bool:
        """Verifica si el texto coincide con algún patrón de ataque"""
        text_lower = text.lower()
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False
    
    def sanitize_input(self, text: str) -> str:
        """
        Sanitiza entrada del usuario.
        Remueve caracteres peligrosos pero mantiene el mensaje legible.
        """
        # Escapar HTML
        sanitized = html.escape(text)
        
        # Remover caracteres de control
        sanitized = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', sanitized)
        
        # Limitar longitud
        if len(sanitized) > self.max_length:
            sanitized = sanitized[:self.max_length]
        
        return sanitized.strip()
    
    def validate_email(self, email: str) -> bool:
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_url(self, url: str) -> bool:
        """Valida formato de URL"""
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))


class InputRateLimiter:
    """Rate limiter mejorado con detección de patrones sospechosos"""
    
    def __init__(self, max_requests: int = 60, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.suspicious_patterns = []
        self.blocked_ips = {}  # En producción, usar Redis
    
    def is_suspicious(self, user_id: str, message: str) -> Tuple[bool, Optional[str]]:
        """
        Detecta patrones sospechosos en el comportamiento.
        
        Returns:
            (is_suspicious, reason)
        """
        # Mensajes muy cortos repetidos (posible bot)
        if len(message) < 5:
            return True, "Mensaje muy corto"
        
        # Mismo mensaje repetido muchas veces
        # (esto se debería trackear en el rate limiter principal)
        
        return False, None


def create_secure_chatbot_wrapper(chatbot_instance, security_validator: SecurityValidator):
    """
    Crea un wrapper seguro para un chatbot.
    
    Args:
        chatbot_instance: Instancia del chatbot
        security_validator: Validador de seguridad
    
    Returns:
        Función wrapper segura
    """
    def secure_process_message(user_message: str, **kwargs) -> Dict:
        # Validar entrada
        is_valid, error = security_validator.validate_input(user_message)
        if not is_valid:
            return {
                "error": error or "Entrada no válida",
                "security_blocked": True
            }
        
        # Sanitizar
        sanitized_message = security_validator.sanitize_input(user_message)
        
        # Procesar con el chatbot
        try:
            response = chatbot_instance.process_message(sanitized_message, **kwargs)
            return response
        except Exception as e:
            return {
                "error": "Error procesando mensaje",
                "security_blocked": False
            }
    
    return secure_process_message


# Configuración de seguridad recomendada
SECURITY_CONFIG = {
    "max_message_length": 2000,
    "enable_sql_injection_protection": True,
    "enable_xss_protection": True,
    "enable_command_injection_protection": True,
    "enable_input_sanitization": True,
    "rate_limit_per_user": 60,
    "rate_limit_window": 60,
    "block_duration": 300
}






