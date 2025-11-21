"""
Webhooks para Integración con Zapier/Make
==========================================

Permite enviar eventos de procesamiento de documentos a servicios externos
como Zapier o Make.com para automatización adicional.
"""

from typing import Dict, Any, List, Optional
import logging
import requests
import json
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class WebhookEvent:
    """Evento de webhook"""
    event_type: str  # document_processed, document_classified, document_archived
    document_id: str
    document_type: str
    timestamp: str
    data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para envío"""
        return {
            "event": self.event_type,
            "document_id": self.document_id,
            "document_type": self.document_type,
            "timestamp": self.timestamp,
            "data": self.data
        }


class WebhookSender:
    """Enviador de webhooks para integraciones"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.timeout = self.config.get("timeout", 30)
        self.retry_count = self.config.get("retry_count", 3)
        self.retry_delay = self.config.get("retry_delay", 5)
    
    def send_document_processed(
        self,
        webhook_url: str,
        document: Dict[str, Any],
        secret_token: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Envía evento cuando un documento es procesado
        
        Args:
            webhook_url: URL del webhook
            document: Datos del documento procesado
            secret_token: Token de autenticación (opcional)
            headers: Headers adicionales (opcional)
        
        Returns:
            True si se envió exitosamente
        """
        event = WebhookEvent(
            event_type="document_processed",
            document_id=document.get("document_id", ""),
            document_type=document.get("document_type", ""),
            timestamp=datetime.now().isoformat(),
            data={
                "document": document,
                "extracted_fields": document.get("extracted_fields", {}),
                "classification": {
                    "type": document.get("document_type"),
                    "confidence": document.get("classification_confidence")
                },
                "ocr": {
                    "provider": document.get("ocr_provider"),
                    "confidence": document.get("ocr_confidence"),
                    "text_length": len(document.get("extracted_text", ""))
                }
            }
        )
        
        return self._send_webhook(webhook_url, event, secret_token, headers)
    
    def send_document_classified(
        self,
        webhook_url: str,
        document_id: str,
        document_type: str,
        confidence: float,
        extracted_fields: Dict[str, Any],
        secret_token: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Envía evento cuando un documento es clasificado"""
        event = WebhookEvent(
            event_type="document_classified",
            document_id=document_id,
            document_type=document_type,
            timestamp=datetime.now().isoformat(),
            data={
                "classification": {
                    "type": document_type,
                    "confidence": confidence
                },
                "extracted_fields": extracted_fields
            }
        )
        
        return self._send_webhook(webhook_url, event, secret_token, headers)
    
    def send_document_archived(
        self,
        webhook_url: str,
        document_id: str,
        archive_path: str,
        document_type: str,
        secret_token: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Envía evento cuando un documento es archivado"""
        event = WebhookEvent(
            event_type="document_archived",
            document_id=document_id,
            document_type=document_type,
            timestamp=datetime.now().isoformat(),
            data={
                "archive_path": archive_path,
                "document_type": document_type
            }
        )
        
        return self._send_webhook(webhook_url, event, secret_token, headers)
    
    def send_batch_processed(
        self,
        webhook_url: str,
        documents: List[Dict[str, Any]],
        secret_token: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Envía evento cuando se procesa un lote de documentos"""
        event = WebhookEvent(
            event_type="batch_processed",
            document_id="batch",
            document_type="multiple",
            timestamp=datetime.now().isoformat(),
            data={
                "count": len(documents),
                "documents": documents,
                "summary": {
                    "by_type": self._count_by_type(documents),
                    "total_size": sum(d.get("file_size", 0) for d in documents)
                }
            }
        )
        
        return self._send_webhook(webhook_url, event, secret_token, headers)
    
    def _send_webhook(
        self,
        url: str,
        event: WebhookEvent,
        secret_token: Optional[str] = None,
        custom_headers: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Envía webhook con reintentos"""
        payload = event.to_dict()
        
        # Headers por defecto
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "DocumentProcessor/1.0"
        }
        
        # Agregar token de autenticación si está presente
        if secret_token:
            headers["Authorization"] = f"Bearer {secret_token}"
            headers["X-Webhook-Token"] = secret_token
        
        # Agregar headers personalizados
        if custom_headers:
            headers.update(custom_headers)
        
        # Reintentos
        for attempt in range(self.retry_count):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                
                # Verificar respuesta
                if response.status_code in [200, 201, 202, 204]:
                    self.logger.info(
                        f"Webhook enviado exitosamente a {url} "
                        f"(intento {attempt + 1}/{self.retry_count})"
                    )
                    return True
                else:
                    self.logger.warning(
                        f"Webhook retornó código {response.status_code} "
                        f"(intento {attempt + 1}/{self.retry_count})"
                    )
                    if attempt < self.retry_count - 1:
                        continue
                    return False
            
            except requests.exceptions.Timeout:
                self.logger.warning(
                    f"Timeout al enviar webhook (intento {attempt + 1}/{self.retry_count})"
                )
                if attempt < self.retry_count - 1:
                    continue
            
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error al enviar webhook: {e}")
                if attempt < self.retry_count - 1:
                    continue
                return False
        
        return False
    
    def _count_by_type(self, documents: List[Dict[str, Any]]) -> Dict[str, int]:
        """Cuenta documentos por tipo"""
        counts = {}
        for doc in documents:
            doc_type = doc.get("document_type", "unknown")
            counts[doc_type] = counts.get(doc_type, 0) + 1
        return counts


class WebhookManager:
    """Gestor de múltiples webhooks configurados"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.sender = WebhookSender()
        self.logger = logging.getLogger(__name__)
    
    def register_webhook(
        self,
        webhook_name: str,
        webhook_url: str,
        trigger_events: List[str],
        document_types: Optional[List[str]] = None,
        secret_token: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
        enabled: bool = True
    ) -> bool:
        """Registra un nuevo webhook"""
        if self.db:
            # Guardar en base de datos
            try:
                cursor = self.db.cursor()
                cursor.execute("""
                    INSERT INTO document_webhooks 
                    (webhook_name, webhook_url, trigger_events, document_types, 
                     enabled, secret_token, headers)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (webhook_name) DO UPDATE SET
                        webhook_url = EXCLUDED.webhook_url,
                        trigger_events = EXCLUDED.trigger_events,
                        document_types = EXCLUDED.document_types,
                        enabled = EXCLUDED.enabled,
                        secret_token = EXCLUDED.secret_token,
                        headers = EXCLUDED.headers,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    webhook_name, webhook_url, trigger_events, document_types,
                    enabled, secret_token, json.dumps(headers) if headers else None
                ))
                self.db.commit()
                self.logger.info(f"Webhook registrado: {webhook_name}")
                return True
            except Exception as e:
                self.logger.error(f"Error registrando webhook: {e}")
                return False
        return True
    
    def trigger_webhooks(
        self,
        event_type: str,
        document: Dict[str, Any],
        document_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Activa webhooks configurados para un evento
        
        Returns:
            Lista de resultados de envío
        """
        if not self.db:
            return []
        
        results = []
        
        try:
            cursor = self.db.cursor()
            
            # Buscar webhooks activos para este evento
            query = """
                SELECT id, webhook_name, webhook_url, trigger_events, 
                       document_types, secret_token, headers
                FROM document_webhooks
                WHERE enabled = true
                  AND %s = ANY(trigger_events)
            """
            params = [event_type]
            
            if document_type:
                query += " AND (%s = ANY(document_types) OR document_types IS NULL)"
                params.append(document_type)
            else:
                query += " AND (document_types IS NULL OR array_length(document_types, 1) IS NULL)"
            
            cursor.execute(query, params)
            webhooks = cursor.fetchall()
            
            # Enviar a cada webhook
            for webhook in webhooks:
                (webhook_id, name, url, events, types, token, headers_json) = webhook
                
                headers = json.loads(headers_json) if headers_json else None
                
                # Enviar según tipo de evento
                success = False
                if event_type == "document_processed":
                    success = self.sender.send_document_processed(
                        url, document, token, headers
                    )
                elif event_type == "document_classified":
                    success = self.sender.send_document_classified(
                        url,
                        document.get("document_id", ""),
                        document.get("document_type", ""),
                        document.get("classification_confidence", 0),
                        document.get("extracted_fields", {}),
                        token,
                        headers
                    )
                elif event_type == "document_archived":
                    success = self.sender.send_document_archived(
                        url,
                        document.get("document_id", ""),
                        document.get("archive_path", ""),
                        document.get("document_type", ""),
                        token,
                        headers
                    )
                
                # Registrar en log
                self._log_webhook(webhook_id, document.get("document_id"), 
                                event_type, success)
                
                results.append({
                    "webhook_name": name,
                    "url": url,
                    "success": success,
                    "event_type": event_type
                })
        
        except Exception as e:
            self.logger.error(f"Error activando webhooks: {e}")
        
        return results
    
    def _log_webhook(
        self,
        webhook_id: int,
        document_id: str,
        event_type: str,
        success: bool
    ):
        """Registra envío de webhook en base de datos"""
        if not self.db:
            return
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO webhook_logs 
                (webhook_id, document_id, event_type, status, sent_at)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (webhook_id, document_id, event_type, 
                  "sent" if success else "failed"))
            self.db.commit()
        except Exception as e:
            self.logger.error(f"Error registrando log de webhook: {e}")

