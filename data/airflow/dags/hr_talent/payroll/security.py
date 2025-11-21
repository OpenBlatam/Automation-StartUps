"""
Funciones de Seguridad para Nómina
Encriptación, validación de permisos, sanitización de datos
"""

import logging
import hashlib
import hmac
import base64
from typing import Optional, Dict, Any
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class PayrollSecurity:
    """Sistema de seguridad para nómina"""
    
    @staticmethod
    def hash_sensitive_data(data: str, salt: Optional[str] = None) -> str:
        """Hashea datos sensibles"""
        if salt is None:
            salt = ""
        combined = f"{salt}{data}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    @staticmethod
    def generate_hmac_signature(
        data: str,
        secret_key: str
    ) -> str:
        """Genera firma HMAC para datos"""
        signature = hmac.new(
            secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    @staticmethod
    def verify_hmac_signature(
        data: str,
        signature: str,
        secret_key: str
    ) -> bool:
        """Verifica firma HMAC"""
        expected = PayrollSecurity.generate_hmac_signature(data, secret_key)
        return hmac.compare_digest(expected, signature)
    
    @staticmethod
    def sanitize_input(input_str: str, max_length: int = 1000) -> str:
        """Sanitiza entrada de usuario"""
        if not input_str:
            return ""
        
        # Limitar longitud
        input_str = input_str[:max_length]
        
        # Remover caracteres peligrosos (SQL injection, XSS)
        dangerous_chars = ['<', '>', '"', "'", ';', '--', '/*', '*/']
        for char in dangerous_chars:
            input_str = input_str.replace(char, '')
        
        # Remover caracteres de control
        input_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', input_str)
        
        return input_str.strip()
    
    @staticmethod
    def validate_employee_id(employee_id: str) -> bool:
        """Valida formato de employee ID"""
        if not employee_id:
            return False
        
        # Solo alfanuméricos, guiones y guiones bajos
        pattern = r'^[A-Za-z0-9_-]+$'
        return bool(re.match(pattern, employee_id))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato de email"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
        """Enmascara datos sensibles (ej: SSN, números de cuenta)"""
        if len(data) <= visible_chars:
            return '*' * len(data)
        
        visible = data[:visible_chars]
        masked = '*' * (len(data) - visible_chars)
        return f"{visible}{masked}"
    
    @staticmethod
    def check_permission(
        user_role: str,
        required_role: str,
        role_hierarchy: Dict[str, int] = None
    ) -> bool:
        """Verifica si un usuario tiene permisos"""
        if role_hierarchy is None:
            role_hierarchy = {
                "employee": 1,
                "manager": 2,
                "hr": 3,
                "finance": 4,
                "admin": 5
            }
        
        user_level = role_hierarchy.get(user_role.lower(), 0)
        required_level = role_hierarchy.get(required_role.lower(), 0)
        
        return user_level >= required_level
    
    @staticmethod
    def generate_audit_token(
        entity_type: str,
        entity_id: str,
        timestamp: datetime,
        secret: str
    ) -> str:
        """Genera token de auditoría"""
        data = f"{entity_type}:{entity_id}:{timestamp.isoformat()}"
        signature = PayrollSecurity.generate_hmac_signature(data, secret)
        token_data = f"{data}:{signature}"
        return base64.b64encode(token_data.encode()).decode()
    
    @staticmethod
    def verify_audit_token(
        token: str,
        secret: str
    ) -> Optional[Dict[str, Any]]:
        """Verifica token de auditoría"""
        try:
            decoded = base64.b64decode(token.encode()).decode()
            parts = decoded.rsplit(':', 1)
            
            if len(parts) != 2:
                return None
            
            data, signature = parts
            
            if not PayrollSecurity.verify_hmac_signature(data, signature, secret):
                return None
            
            entity_parts = data.split(':')
            if len(entity_parts) != 3:
                return None
            
            return {
                "entity_type": entity_parts[0],
                "entity_id": entity_parts[1],
                "timestamp": datetime.fromisoformat(entity_parts[2])
            }
        except Exception as e:
            logger.error(f"Error verifying audit token: {e}")
            return None

