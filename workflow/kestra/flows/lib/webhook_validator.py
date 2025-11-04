"""
Validador de webhooks con verificación de firma.

Soporta verificación de firma HMAC para webhooks de HubSpot.
"""
import hmac
import hashlib
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class WebhookValidator:
    """Validador de webhooks con verificación de firma."""
    
    @staticmethod
    def verify_hubspot_signature(
        raw_body: str,
        signature_header: Optional[str],
        secret: str
    ) -> bool:
        """
        Verifica la firma de un webhook de HubSpot.
        
        HubSpot usa X-HubSpot-Signature-v2 o X-HubSpot-Signature-v3.
        
        Args:
            raw_body: Cuerpo raw del webhook (string)
            signature_header: Valor del header X-HubSpot-Signature-v3 o v2
            secret: Secret compartido para verificación
        
        Returns:
            True si la firma es válida, False si no
        """
        if not signature_header:
            logger.warning("No signature header found")
            return False
        
        if not secret:
            logger.warning("Webhook secret not configured")
            return False
        
        try:
            # HubSpot v3 signature verification
            expected_sig = hmac.new(
                secret.encode('utf-8'),
                raw_body.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            is_valid = hmac.compare_digest(expected_sig, signature_header)
            
            if is_valid:
                logger.info("Webhook signature verified successfully")
            else:
                logger.warning("Invalid webhook signature")
            
            return is_valid
        except Exception as e:
            logger.error("Signature verification failed", extra={"error": str(e)})
            return False
    
    @staticmethod
    def get_signature_from_headers(headers: Dict[str, Any]) -> Optional[str]:
        """
        Extrae la firma de los headers HTTP.
        
        Args:
            headers: Diccionario de headers HTTP
        
        Returns:
            Valor del header de firma o None si no existe
        """
        # Buscar en diferentes formatos de header
        signature = (
            headers.get('X-HubSpot-Signature-v3') or
            headers.get('X-HubSpot-Signature-v2') or
            headers.get('x-hubspot-signature-v3') or
            headers.get('x-hubspot-signature-v2') or
            headers.get('X-HubSpot-Signature')
        )
        
        return signature



