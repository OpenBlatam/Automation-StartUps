#!/usr/bin/env python3
"""
Configuración de seguridad para TikTok Auto Edit
Validaciones, rate limiting, y medidas de seguridad
"""

import os
import hashlib
import hmac
import time
import logging
from typing import Dict, Any, Optional, List
from functools import wraps
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityManager:
    """Gestor de seguridad del sistema"""
    
    def __init__(self):
        """Inicializa el gestor de seguridad"""
        self.rate_limits = {}  # {ip: [timestamps]}
        self.blocked_ips = set()
        self.max_requests_per_minute = int(os.getenv('MAX_REQUESTS_PER_MINUTE', '60'))
        self.block_duration_minutes = int(os.getenv('BLOCK_DURATION_MINUTES', '60'))
    
    def validate_tiktok_url(self, url: str) -> tuple[bool, Optional[str]]:
        """
        Valida que una URL sea de TikTok válida
        
        Args:
            url: URL a validar
            
        Returns:
            (es_válida, mensaje_error)
        """
        if not url or not isinstance(url, str):
            return False, "URL inválida"
        
        url = url.strip()
        
        # Verificar que sea URL válida
        if not url.startswith('http://') and not url.startswith('https://'):
            return False, "URL debe empezar con http:// o https://"
        
        # Verificar dominio de TikTok
        valid_domains = [
            'tiktok.com',
            'www.tiktok.com',
            'vm.tiktok.com',
            'vt.tiktok.com'
        ]
        
        if not any(domain in url for domain in valid_domains):
            return False, "URL debe ser de TikTok"
        
        # Verificar formato básico
        if '/video/' not in url and 'vm.tiktok.com' not in url and 'vt.tiktok.com' not in url:
            return False, "URL de TikTok inválida"
        
        return True, None
    
    def check_rate_limit(self, identifier: str) -> tuple[bool, Optional[int]]:
        """
        Verifica rate limit para un identificador (IP, user, etc.)
        
        Args:
            identifier: Identificador único
            
        Returns:
            (puede_proceder, segundos_restantes)
        """
        now = time.time()
        minute_ago = now - 60
        
        # Limpiar IPs bloqueadas expiradas
        if identifier in self.blocked_ips:
            # Asumimos que el bloqueo expira después de block_duration_minutes
            # En producción, esto debería estar en una base de datos
            self.blocked_ips.discard(identifier)
        
        if identifier in self.blocked_ips:
            return False, self.block_duration_minutes * 60
        
        # Obtener requests recientes
        if identifier not in self.rate_limits:
            self.rate_limits[identifier] = []
        
        # Filtrar requests del último minuto
        self.rate_limits[identifier] = [
            ts for ts in self.rate_limits[identifier] if ts > minute_ago
        ]
        
        # Verificar límite
        if len(self.rate_limits[identifier]) >= self.max_requests_per_minute:
            # Bloquear temporalmente
            self.blocked_ips.add(identifier)
            logger.warning(f"Rate limit excedido para {identifier}, bloqueado")
            return False, self.block_duration_minutes * 60
        
        # Agregar request actual
        self.rate_limits[identifier].append(now)
        
        # Calcular tiempo hasta siguiente request permitido
        if len(self.rate_limits[identifier]) >= self.max_requests_per_minute - 5:
            oldest = min(self.rate_limits[identifier])
            remaining = int(60 - (now - oldest))
            return True, remaining
        else:
            return True, 0
    
    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """
        Verifica firma HMAC de webhook
        
        Args:
            payload: Cuerpo del request
            signature: Firma recibida
            secret: Secret compartido
            
        Returns:
            True si la firma es válida
        """
        if not secret:
            logger.warning("Webhook secret no configurado")
            return False
        
        expected = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, signature)
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitiza nombre de archivo para seguridad
        
        Args:
            filename: Nombre de archivo original
            
        Returns:
            Nombre sanitizado
        """
        import re
        
        # Remover caracteres peligrosos
        sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Limitar longitud
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:250] + ext
        
        # Prevenir path traversal
        sanitized = os.path.basename(sanitized)
        
        return sanitized
    
    def validate_file_size(self, file_path: str, max_size_mb: float = 500) -> tuple[bool, Optional[str]]:
        """
        Valida tamaño de archivo
        
        Args:
            file_path: Ruta al archivo
            max_size_mb: Tamaño máximo en MB
            
        Returns:
            (es_válido, mensaje_error)
        """
        if not os.path.exists(file_path):
            return False, "Archivo no existe"
        
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        if size_mb > max_size_mb:
            return False, f"Archivo muy grande: {size_mb:.2f} MB (máx: {max_size_mb} MB)"
        
        return True, None


def rate_limit_decorator(max_requests: int = 60, window_seconds: int = 60):
    """
    Decorador para rate limiting en funciones
    
    Args:
        max_requests: Máximo de requests
        window_seconds: Ventana de tiempo en segundos
    """
    def decorator(func):
        manager = SecurityManager()
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Obtener identificador (IP, user ID, etc.)
            identifier = kwargs.get('identifier') or 'default'
            
            can_proceed, remaining = manager.check_rate_limit(identifier)
            
            if not can_proceed:
                raise Exception(f"Rate limit excedido. Intenta en {remaining} segundos")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def main():
    """Tests de seguridad"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Configuración de seguridad')
    parser.add_argument('test', choices=['validate-url', 'rate-limit', 'signature'],
                       help='Test a ejecutar')
    parser.add_argument('-u', '--url', help='URL para validar')
    parser.add_argument('-i', '--identifier', help='Identificador para rate limit')
    
    args = parser.parse_args()
    
    manager = SecurityManager()
    
    if args.test == 'validate-url':
        if not args.url:
            print("Error: URL requerida")
            return
        
        valid, error = manager.validate_tiktok_url(args.url)
        if valid:
            print(f"✅ URL válida: {args.url}")
        else:
            print(f"❌ URL inválida: {error}")
    
    elif args.test == 'rate-limit':
        identifier = args.identifier or 'test'
        can_proceed, remaining = manager.check_rate_limit(identifier)
        if can_proceed:
            print(f"✅ Rate limit OK para {identifier}")
            if remaining > 0:
                print(f"   Próximo request permitido en {remaining}s")
        else:
            print(f"❌ Rate limit excedido para {identifier}")
            print(f"   Bloqueado por {remaining}s")
    
    elif args.test == 'signature':
        # Test de verificación de firma
        secret = "test_secret"
        payload = b'{"test": "data"}'
        signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        
        valid = manager.verify_webhook_signature(payload, signature, secret)
        print(f"✅ Firma válida: {valid}")


if __name__ == '__main__':
    main()

