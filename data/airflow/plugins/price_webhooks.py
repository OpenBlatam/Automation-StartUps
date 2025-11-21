"""
Sistema de Webhooks para Automatización de Precios

Notifica eventos importantes a sistemas externos
"""

import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class PriceWebhooks:
    """Gestiona webhooks para notificar eventos de precios"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.webhooks = config.get('webhooks', [])
        self.timeout = config.get('webhook_timeout', 10)
        self.retry_attempts = config.get('webhook_retry_attempts', 3)
    
    def send_webhook(
        self,
        event_type: str,
        data: Dict,
        webhook_url: Optional[str] = None
    ) -> bool:
        """
        Envía webhook para un evento
        
        Args:
            event_type: Tipo de evento
            data: Datos del evento
            webhook_url: URL específica (opcional, usa config si no se proporciona)
        
        Returns:
            True si se envió exitosamente
        """
        if webhook_url:
            urls = [webhook_url]
        else:
            # Buscar webhooks configurados para este tipo de evento
            urls = [
                wh['url'] for wh in self.webhooks
                if event_type in wh.get('events', []) or 'all' in wh.get('events', [])
            ]
        
        if not urls:
            logger.debug(f"No hay webhooks configurados para evento: {event_type}")
            return False
        
        success = True
        for url in urls:
            try:
                payload = {
                    'event_type': event_type,
                    'timestamp': datetime.now().isoformat(),
                    'data': data,
                }
                
                # Intentar enviar con retry
                for attempt in range(self.retry_attempts):
                    try:
                        response = requests.post(
                            url,
                            json=payload,
                            headers={'Content-Type': 'application/json'},
                            timeout=self.timeout
                        )
                        response.raise_for_status()
                        logger.info(f"Webhook enviado exitosamente: {event_type} -> {url}")
                        break
                    except requests.RequestException as e:
                        if attempt == self.retry_attempts - 1:
                            raise
                        logger.warning(f"Intento {attempt + 1} falló, reintentando...")
                
            except Exception as e:
                logger.error(f"Error enviando webhook a {url}: {e}")
                success = False
        
        return success
    
    def notify_price_extracted(
        self,
        competitor_prices_count: int,
        extraction_failures: int
    ):
        """Notifica cuando se extraen precios"""
        self.send_webhook('price_extracted', {
            'competitor_prices_count': competitor_prices_count,
            'extraction_failures': extraction_failures,
        })
    
    def notify_price_analyzed(
        self,
        adjustments_count: int,
        extreme_changes: int
    ):
        """Notifica cuando se analizan precios"""
        self.send_webhook('price_analyzed', {
            'adjustments_count': adjustments_count,
            'extreme_changes': extreme_changes,
        })
    
    def notify_price_published(
        self,
        products_updated: int,
        total_products: int,
        success: bool
    ):
        """Notifica cuando se publican precios"""
        self.send_webhook('price_published', {
            'products_updated': products_updated,
            'total_products': total_products,
            'success': success,
        })
    
    def notify_price_changed(
        self,
        product_id: str,
        product_name: str,
        old_price: float,
        new_price: float,
        change_percent: float
    ):
        """Notifica cuando cambia un precio"""
        self.send_webhook('price_changed', {
            'product_id': product_id,
            'product_name': product_name,
            'old_price': old_price,
            'new_price': new_price,
            'change_percent': change_percent,
        })
    
    def notify_alert_triggered(
        self,
        alert_type: str,
        severity: str,
        message: str
    ):
        """Notifica cuando se dispara una alerta"""
        self.send_webhook('alert_triggered', {
            'alert_type': alert_type,
            'severity': severity,
            'message': message,
        })








