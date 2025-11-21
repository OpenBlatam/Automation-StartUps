"""
Módulo de Encriptación para Backups y Datos Sensibles.

Proporciona:
- Encriptación simétrica (AES-256)
- Encriptación de archivos
- Encriptación de datos en memoria
- Gestión de claves
"""
import logging
import os
from typing import Optional, Union, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

logger = logging.getLogger(__name__)


class BackupEncryption:
    """Gestor de encriptación para backups."""
    
    def __init__(self, encryption_key: Optional[Union[bytes, str]] = None):
        """
        Inicializa encriptación.
        
        Args:
            encryption_key: Clave de encriptación (bytes o string). 
                          Si None, se genera una nueva.
        """
        if encryption_key is None:
            self.key = Fernet.generate_key()
            logger.warning("Generated new encryption key. Store it securely!")
        elif isinstance(encryption_key, str):
            # Deriva clave desde password usando PBKDF2
            self.key = self._derive_key_from_password(encryption_key)
        else:
            self.key = encryption_key
        
        self.cipher = Fernet(self.key)
    
    @staticmethod
    def _derive_key_from_password(password: str, salt: Optional[bytes] = None) -> bytes:
        """
        Deriva clave desde password usando PBKDF2.
        
        Args:
            password: Password para derivar clave
            salt: Salt (opcional, se genera si no se proporciona)
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_file(
        self,
        input_path: str,
        output_path: str,
        chunk_size: int = 64 * 1024
    ) -> bool:
        """
        Encripta un archivo.
        
        Args:
            input_path: Ruta del archivo a encriptar
            output_path: Ruta del archivo encriptado
            chunk_size: Tamaño de chunk para procesamiento
        """
        try:
            with open(input_path, 'rb') as infile:
                with open(output_path, 'wb') as outfile:
                    # Leer y encriptar en chunks
                    while True:
                        chunk = infile.read(chunk_size)
                        if not chunk:
                            break
                        encrypted_chunk = self.cipher.encrypt(chunk)
                        outfile.write(encrypted_chunk)
            
            logger.info(f"Encrypted file: {input_path} -> {output_path}")
            return True
        except Exception as e:
            logger.error(f"Encryption failed: {e}", exc_info=True)
            return False
    
    def decrypt_file(
        self,
        input_path: str,
        output_path: str,
        chunk_size: int = 64 * 1024
    ) -> bool:
        """
        Desencripta un archivo.
        
        Args:
            input_path: Ruta del archivo encriptado
            output_path: Ruta del archivo desencriptado
            chunk_size: Tamaño de chunk para procesamiento
        """
        try:
            with open(input_path, 'rb') as infile:
                with open(output_path, 'wb') as outfile:
                    # Leer y desencriptar en chunks
                    while True:
                        chunk = infile.read(chunk_size)
                        if not chunk:
                            break
                        try:
                            decrypted_chunk = self.cipher.decrypt(chunk)
                            outfile.write(decrypted_chunk)
                        except Exception as e:
                            logger.error(f"Decryption error: {e}")
                            return False
            
            logger.info(f"Decrypted file: {input_path} -> {output_path}")
            return True
        except Exception as e:
            logger.error(f"Decryption failed: {e}", exc_info=True)
            return False
    
    def encrypt_data(self, data: Union[str, bytes]) -> bytes:
        """
        Encripta datos en memoria.
        
        Args:
            data: Datos a encriptar (str o bytes)
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return self.cipher.encrypt(data)
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """
        Desencripta datos en memoria.
        
        Args:
            encrypted_data: Datos encriptados
        """
        return self.cipher.decrypt(encrypted_data)
    
    def encrypt_string(self, text: str) -> str:
        """
        Encripta string y retorna base64.
        
        Args:
            text: Texto a encriptar
        """
        encrypted = self.encrypt_data(text)
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_string(self, encrypted_text: str) -> str:
        """
        Desencripta string desde base64.
        
        Args:
            encrypted_text: Texto encriptado en base64
        """
        encrypted_bytes = base64.b64decode(encrypted_text.encode('utf-8'))
        decrypted = self.decrypt_data(encrypted_bytes)
        return decrypted.decode('utf-8')
    
    def get_key_base64(self) -> str:
        """Retorna la clave en formato base64 para almacenamiento seguro."""
        return base64.b64encode(self.key).decode('utf-8')
    
    @staticmethod
    def load_key_from_base64(key_base64: str) -> bytes:
        """Carga clave desde base64."""
        return base64.b64decode(key_base64.encode('utf-8'))
    
    @staticmethod
    def load_key_from_env(env_var: str = "BACKUP_ENCRYPTION_KEY") -> Optional[bytes]:
        """
        Carga clave desde variable de entorno.
        
        Args:
            env_var: Nombre de la variable de entorno
        """
        key_str = os.getenv(env_var)
        if not key_str:
            return None
        
        try:
            return BackupEncryption.load_key_from_base64(key_str)
        except Exception as e:
            logger.error(f"Failed to load key from env: {e}")
            return None


class SensitiveDataEncryption:
    """Encriptación específica para datos sensibles (PII, etc.)."""
    
    def __init__(self, encryption_key: Optional[Union[bytes, str]] = None):
        """Inicializa encriptación para datos sensibles."""
        self.encryption = BackupEncryption(encryption_key)
    
    def encrypt_sensitive_field(self, value: str, field_name: str = "") -> Dict[str, Any]:
        """
        Encripta un campo sensible.
        
        Args:
            value: Valor a encriptar
            field_name: Nombre del campo (para logging)
        """
        encrypted = self.encryption.encrypt_string(value)
        return {
            'encrypted': True,
            'value': encrypted,
            'field': field_name
        }
    
    def decrypt_sensitive_field(self, encrypted_data: Dict[str, Any]) -> str:
        """
        Desencripta un campo sensible.
        
        Args:
            encrypted_data: Datos encriptados con formato {'encrypted': True, 'value': '...'}
        """
        if not encrypted_data.get('encrypted'):
            return encrypted_data.get('value', '')
        
        return self.encryption.decrypt_string(encrypted_data['value'])
    
    def encrypt_dict(self, data: Dict[str, Any], sensitive_fields: list) -> Dict[str, Any]:
        """
        Encripta campos sensibles en un diccionario.
        
        Args:
            data: Diccionario con datos
            sensitive_fields: Lista de campos a encriptar
        """
        encrypted_data = data.copy()
        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt_sensitive_field(
                    str(encrypted_data[field]),
                    field
                )
        return encrypted_data
    
    def decrypt_dict(self, encrypted_data: Dict[str, Any], sensitive_fields: list) -> Dict[str, Any]:
        """
        Desencripta campos sensibles en un diccionario.
        
        Args:
            encrypted_data: Diccionario con datos encriptados
            sensitive_fields: Lista de campos a desencriptar
        """
        decrypted_data = encrypted_data.copy()
        for field in sensitive_fields:
            if field in decrypted_data:
                value = decrypted_data[field]
                if isinstance(value, dict) and value.get('encrypted'):
                    decrypted_data[field] = self.decrypt_sensitive_field(value)
        return decrypted_data

