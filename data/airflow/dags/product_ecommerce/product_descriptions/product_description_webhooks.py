"""
Sistema de webhooks para notificaciones y integraciones.

Permite:
- Notificaciones cuando se genera una descripción
- Webhooks para sincronización con plataformas externas
- Eventos de actualización y cambios
"""

import logging
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class WebhookEvent(Enum):
    """Tipos de eventos para webhooks."""
    DESCRIPTION_GENERATED = 'description_generated'
    DESCRIPTION_UPDATED = 'description_updated'
    VARIATION_CREATED = 'variation_created'
    ANALYSIS_COMPLETED = 'analysis_completed'
    EXPORT_COMPLETED = 'export_completed'
    QUALITY_THRESHOLD_MET = 'quality_threshold_met'


class WebhookManager:
    """Gestor de webhooks para notificaciones."""
    
    def __init__(self, webhook_urls: Dict[str, List[str]] = None):
        """
        Inicializa el gestor de webhooks.
        
        Args:
            webhook_urls: Dict con URLs por tipo de evento
                Ejemplo: {
                    'description_generated': ['https://api.example.com/webhook'],
                    'all': ['https://api.example.com/webhook-all']
                }
        """
        self.webhook_urls = webhook_urls or {}
        self.default_timeout = 10
    
    def register_webhook(self, event_type: str, url: str):
        """
        Registra una URL de webhook para un tipo de evento.
        
        Args:
            event_type: Tipo de evento o 'all' para todos
            url: URL del webhook
        """
        if event_type not in self.webhook_urls:
            self.webhook_urls[event_type] = []
        
        if url not in self.webhook_urls[event_type]:
            self.webhook_urls[event_type].append(url)
            logger.info(f"Webhook registrado: {event_type} -> {url}")
    
    def trigger_webhook(self, event: WebhookEvent, data: Dict, metadata: Dict = None):
        """
        Dispara un webhook para un evento específico.
        
        Args:
            event: Tipo de evento
            data: Datos del evento
            metadata: Metadata adicional
        """
        urls = []
        
        # Obtener URLs específicas del evento
        event_key = event.value
        if event_key in self.webhook_urls:
            urls.extend(self.webhook_urls[event_key])
        
        # Obtener URLs para todos los eventos
        if 'all' in self.webhook_urls:
            urls.extend(self.webhook_urls['all'])
        
        if not urls:
            logger.debug(f"No hay webhooks registrados para evento: {event.value}")
            return
        
        payload = {
            'event': event.value,
            'timestamp': datetime.now().isoformat(),
            'data': data,
            'metadata': metadata or {}
        }
        
        # Enviar a todas las URLs
        results = []
        for url in urls:
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=self.default_timeout
                )
                
                result = {
                    'url': url,
                    'status_code': response.status_code,
                    'success': response.ok,
                    'response': response.text[:200] if response.text else None
                }
                results.append(result)
                
                if response.ok:
                    logger.info(f"Webhook enviado exitosamente a {url}")
                else:
                    logger.warning(f"Webhook falló en {url}: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Error enviando webhook a {url}: {str(e)}")
                results.append({
                    'url': url,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def notify_description_generated(self, description_data: Dict):
        """Notifica cuando se genera una descripción."""
        return self.trigger_webhook(
            WebhookEvent.DESCRIPTION_GENERATED,
            {
                'product_name': description_data.get('product_name', ''),
                'product_description_id': description_data.get('product_description_id'),
                'platform': description_data.get('platform', ''),
                'word_count': description_data.get('word_count', 0),
                'seo_score': description_data.get('seo_analysis', {}).get('score', 0)
            },
            {
                'provider': description_data.get('metadata', {}).get('provider'),
                'model': description_data.get('metadata', {}).get('model')
            }
        )
    
    def notify_quality_threshold(self, description_data: Dict, threshold: float = 80.0):
        """Notifica cuando se alcanza un umbral de calidad."""
        quality_score = description_data.get('full_analysis', {}).get('quality_score', {}).get('total_score', 0)
        
        if quality_score >= threshold:
            return self.trigger_webhook(
                WebhookEvent.QUALITY_THRESHOLD_MET,
                {
                    'product_name': description_data.get('product_name', ''),
                    'quality_score': quality_score,
                    'threshold': threshold
                }
            )
        
        return None


class BatchProgressTracker:
    """Tracker de progreso para procesamiento por lotes."""
    
    def __init__(self, total_items: int):
        """
        Inicializa el tracker.
        
        Args:
            total_items: Número total de items a procesar
        """
        self.total_items = total_items
        self.processed = 0
        self.successful = 0
        self.failed = 0
        self.results = []
    
    def update(self, success: bool, result: Dict = None, error: str = None):
        """
        Actualiza el progreso.
        
        Args:
            success: Si el procesamiento fue exitoso
            result: Resultado del procesamiento
            error: Mensaje de error si falló
        """
        self.processed += 1
        
        if success:
            self.successful += 1
            if result:
                self.results.append(result)
        else:
            self.failed += 1
            if error:
                self.results.append({'error': error})
    
    def get_progress(self) -> Dict:
        """
        Obtiene el progreso actual.
        
        Returns:
            Dict con métricas de progreso
        """
        percentage = (self.processed / self.total_items * 100) if self.total_items > 0 else 0
        
        return {
            'total': self.total_items,
            'processed': self.processed,
            'successful': self.successful,
            'failed': self.failed,
            'percentage': round(percentage, 2),
            'remaining': self.total_items - self.processed
        }
    
    def is_complete(self) -> bool:
        """Verifica si el procesamiento está completo."""
        return self.processed >= self.total_items






