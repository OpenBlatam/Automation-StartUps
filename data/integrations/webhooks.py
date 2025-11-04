"""
Webhooks para triggers en tiempo real
======================================

Permite activar sincronizaciones automáticamente cuando hay cambios en sistemas externos.
"""
from flask import Flask, request, jsonify
from typing import Dict, Any, Optional, Callable
import logging
import hmac
import hashlib
import json
from datetime import datetime

from .sync_framework import SyncFramework, SyncConfig, SyncDirection

logger = logging.getLogger(__name__)


class WebhookHandler:
    """Maneja webhooks de diferentes sistemas"""
    
    def __init__(self, framework: SyncFramework):
        self.framework = framework
        self.app = Flask(__name__)
        self.handlers: Dict[str, Callable] = {}
        self._setup_routes()
    
    def _setup_routes(self):
        """Configura rutas de webhooks"""
        
        @self.app.route('/webhook/hubspot', methods=['POST'])
        def hubspot_webhook():
            return self.handle_hubspot(request)
        
        @self.app.route('/webhook/quickbooks', methods=['POST'])
        def quickbooks_webhook():
            return self.handle_quickbooks(request)
        
        @self.app.route('/webhook/generic', methods=['POST'])
        def generic_webhook():
            return self.handle_generic(request)
        
        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({"status": "healthy"})
    
    def register_handler(self, event_type: str, handler: Callable):
        """Registra handler personalizado para tipo de evento"""
        self.handlers[event_type] = handler
    
    def verify_hubspot_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verifica firma HMAC de HubSpot"""
        try:
            expected_signature = hmac.new(
                secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False
    
    def handle_hubspot(self, request) -> Dict[str, Any]:
        """Maneja webhook de HubSpot"""
        try:
            # Verificar firma si hay secret
            secret = request.headers.get('X-HubSpot-Secret')
            if secret:
                signature = request.headers.get('X-HubSpot-Signature-v2', '')
                if not self.verify_hubspot_signature(
                    request.data,
                    signature,
                    secret
                ):
                    return jsonify({"error": "Invalid signature"}), 401
            
            data = request.get_json()
            event_type = data.get('eventType') or data.get('subscriptionType')
            
            # Procesar eventos
            if event_type in ['contact.creation', 'contact.propertyChange']:
                return self._trigger_contact_sync(data)
            elif event_type in ['deal.creation', 'deal.propertyChange']:
                return self._trigger_deal_sync(data)
            
            return jsonify({"status": "received", "event_type": event_type})
        
        except Exception as e:
            logger.error(f"Error procesando webhook HubSpot: {e}")
            return jsonify({"error": str(e)}), 500
    
    def handle_quickbooks(self, request) -> Dict[str, Any]:
        """Maneja webhook de QuickBooks"""
        try:
            data = request.get_json()
            event_type = data.get('eventNotifications', [{}])[0].get('eventType', '')
            
            if event_type in ['Create', 'Update']:
                return self._trigger_quickbooks_sync(data)
            
            return jsonify({"status": "received", "event_type": event_type})
        
        except Exception as e:
            logger.error(f"Error procesando webhook QuickBooks: {e}")
            return jsonify({"error": str(e)}), 500
    
    def handle_generic(self, request) -> Dict[str, Any]:
        """Maneja webhook genérico"""
        try:
            data = request.get_json()
            event_type = data.get('event_type', 'unknown')
            
            # Buscar handler personalizado
            if event_type in self.handlers:
                return self.handlers[event_type](data)
            
            return jsonify({"status": "received", "event_type": event_type})
        
        except Exception as e:
            logger.error(f"Error procesando webhook genérico: {e}")
            return jsonify({"error": str(e)}), 500
    
    def _trigger_contact_sync(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger sincronización de contacto"""
        contact_id = webhook_data.get('objectId') or webhook_data.get('id')
        
        config = SyncConfig(
            sync_id=f"webhook_contact_{contact_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source_connector_type="hubspot",
            source_config={"api_token": self._get_hubspot_token()},
            target_connector_type="quickbooks",
            target_config={
                "access_token": self._get_quickbooks_token(),
                "realm_id": self._get_quickbooks_realm()
            },
            direction=SyncDirection.SOURCE_TO_TARGET,
            batch_size=1,
            filters={"object_id": contact_id},
            conflict_resolution="latest"
        )
        
        result = self.framework.sync(config, dry_run=False)
        return jsonify(result.to_dict())
    
    def _trigger_deal_sync(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger sincronización de deal"""
        deal_id = webhook_data.get('objectId') or webhook_data.get('id')
        
        # Similar a contact sync pero para deals
        return jsonify({"status": "triggered", "deal_id": deal_id})
    
    def _trigger_quickbooks_sync(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger sincronización desde QuickBooks"""
        # Implementar según necesidad
        return jsonify({"status": "triggered"})
    
    def _get_hubspot_token(self) -> str:
        """Obtiene token de HubSpot desde config"""
        import os
        return os.getenv("HUBSPOT_API_TOKEN", "")
    
    def _get_quickbooks_token(self) -> str:
        """Obtiene token de QuickBooks desde config"""
        import os
        return os.getenv("QUICKBOOKS_ACCESS_TOKEN", "")
    
    def _get_quickbooks_realm(self) -> str:
        """Obtiene realm de QuickBooks desde config"""
        import os
        return os.getenv("QUICKBOOKS_REALM_ID", "")
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Ejecuta servidor de webhooks"""
        self.app.run(host=host, port=port, debug=debug)


def create_webhook_server(framework: SyncFramework) -> WebhookHandler:
    """Crea servidor de webhooks"""
    return WebhookHandler(framework)


