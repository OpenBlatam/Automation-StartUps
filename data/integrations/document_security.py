"""
Seguridad y Encriptación de Documentos
========================================

Funciones de seguridad para proteger documentos sensibles.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
import hashlib
import secrets
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DocumentSecurity:
    """Gestor de seguridad para documentos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def encrypt_file(
        self,
        file_path: str,
        password: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """Encripta un archivo"""
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import base64
        except ImportError:
            raise ImportError(
                "cryptography es requerido. Instala con: pip install cryptography"
            )
        
        if output_path is None:
            output_path = str(Path(file_path).with_suffix('.encrypted'))
        
        # Generar clave
        if password:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'fixed_salt',  # En producción usar salt único
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        else:
            key = Fernet.generate_key()
        
        fernet = Fernet(key)
        
        # Leer y encriptar
        with open(file_path, 'rb') as f:
            data = f.read()
        
        encrypted_data = fernet.encrypt(data)
        
        # Guardar
        with open(output_path, 'wb') as f:
            f.write(encrypted_data)
        
        self.logger.info(f"Archivo encriptado: {output_path}")
        return output_path
    
    def decrypt_file(
        self,
        encrypted_path: str,
        password: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """Desencripta un archivo"""
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import base64
        except ImportError:
            raise ImportError("cryptography es requerido")
        
        if output_path is None:
            output_path = str(Path(encrypted_path).with_suffix('.decrypted'))
        
        # Generar clave (debe ser la misma que encriptación)
        if password:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'fixed_salt',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        else:
            raise ValueError("Password requerido para desencriptar")
        
        fernet = Fernet(key)
        
        # Leer y desencriptar
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = fernet.decrypt(encrypted_data)
        
        # Guardar
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
        
        self.logger.info(f"Archivo desencriptado: {output_path}")
        return output_path
    
    def redact_sensitive_data(
        self,
        text: str,
        patterns: Optional[List[str]] = None
    ) -> str:
        """Redacta datos sensibles del texto"""
        import re
        
        if patterns is None:
            # Patrones por defecto
            patterns = [
                (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '****-****-****-****'),  # Tarjeta
                (r'\b\d{3}-\d{2}-\d{4}\b', '***-**-****'),  # SSN
                (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***'),  # Email
                (r'\b\d{3}-\d{3}-\d{4}\b', '***-***-****'),  # Teléfono
            ]
        
        redacted_text = text
        
        for pattern, replacement in patterns:
            redacted_text = re.sub(pattern, replacement, redacted_text, flags=re.IGNORECASE)
        
        return redacted_text
    
    def generate_access_token(
        self,
        document_id: str,
        expires_hours: int = 24
    ) -> str:
        """Genera token de acceso temporal"""
        import jwt
        import os
        
        secret = os.getenv('JWT_SECRET', secrets.token_urlsafe(32))
        
        payload = {
            'document_id': document_id,
            'exp': datetime.utcnow() + timedelta(hours=expires_hours),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, secret, algorithm='HS256')
        return token
    
    def validate_access_token(self, token: str) -> Optional[str]:
        """Valida token de acceso"""
        try:
            import jwt
            import os
            
            secret = os.getenv('JWT_SECRET', secrets.token_urlsafe(32))
            
            payload = jwt.decode(token, secret, algorithms=['HS256'])
            return payload.get('document_id')
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expirado")
            return None
        except Exception as e:
            self.logger.error(f"Error validando token: {e}")
            return None
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitiza nombre de archivo para seguridad"""
        import re
        
        # Remover caracteres peligrosos
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Limitar longitud
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:250] + ext
        
        return sanitized
    
    def calculate_file_integrity(self, file_path: str) -> Dict[str, str]:
        """Calcula checksums para verificar integridad"""
        hashes = {}
        
        algorithms = ['md5', 'sha1', 'sha256']
        
        for algorithm in algorithms:
            hash_obj = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            hashes[algorithm] = hash_obj.hexdigest()
        
        return hashes

