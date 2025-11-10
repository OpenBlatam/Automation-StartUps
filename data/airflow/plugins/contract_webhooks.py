"""
Módulo de Webhooks para Eventos de Firma Electrónica
Maneja webhooks de DocuSign Connect y PandaDoc
"""

from __future__ import annotations

import json
import logging
import hmac
import hashlib
import os
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from data.airflow.plugins.contract_integrations import (
    check_contract_signature_status,
    store_contract_version
)

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

logger = logging.getLogger("airflow.task")


class DocuSignWebhookHandler:
    """Manejador de webhooks de DocuSign Connect"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or os.getenv("DOCUSIGN_WEBHOOK_SECRET", "")
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verifica la firma HMAC del webhook de DocuSign"""
        if not self.secret_key:
            logger.warning("DocuSign webhook secret no configurado, saltando verificación")
            return True
        
        try:
            expected_signature = hmac.new(
                self.secret_key.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"Error verificando firma DocuSign: {e}")
            return False
    
    def process_event(self, event_data: Dict[str, Any], postgres_conn_id: str = "postgres_default") -> Dict[str, Any]:
        """Procesa un evento de webhook de DocuSign"""
        event_type = event_data.get("event", "")
        envelope_id = event_data.get("data", {}).get("envelopeId", "")
        
        logger.info(
            f"Procesando evento DocuSign",
            extra={
                "event_type": event_type,
                "envelope_id": envelope_id
            }
        )
        
        if not POSTGRES_AVAILABLE:
            raise ImportError("PostgreSQL hook no disponible")
        
        hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        
        # Buscar contrato por envelope_id
        contract_query = """
            SELECT contract_id, status
            FROM contracts
            WHERE esignature_envelope_id = %s
        """
        contract = hook.get_first(contract_query, parameters=(envelope_id,))
        
        if not contract:
            logger.warning(f"Contrato no encontrado para envelope_id: {envelope_id}")
            return {"status": "not_found", "envelope_id": envelope_id}
        
        contract_id = contract[0]
        
        # Procesar según tipo de evento
        if event_type in ("envelope-completed", "envelope-signed"):
            # Verificar y actualizar estado
            status_result = check_contract_signature_status(contract_id=contract_id)
            
            # Actualizar estado del contrato a fully_signed
            if status_result.get("status") == "fully_signed":
                signed_date = status_result.get("signed_date") or datetime.now()
                hook.run("""
                    UPDATE contracts
                    SET status = 'fully_signed',
                        signed_date = %s,
                        updated_at = NOW()
                    WHERE contract_id = %s
                """, parameters=(signed_date, contract_id))
                
                # Activar servicios automáticamente si está configurado
                try:
                    # Obtener información del cliente y servicios a activar
                    customer_query = """
                        SELECT 
                            c.primary_party_email,
                            c.metadata as contract_metadata,
                            co.metadata as onboarding_metadata
                        FROM contracts c
                        LEFT JOIN customer_onboarding co ON c.primary_party_email = co.customer_email
                        WHERE c.contract_id = %s
                    """
                    customer_data = hook.get_first(customer_query, parameters=(contract_id,))
                    
                    if customer_data:
                        customer_email = customer_data[0]
                        contract_metadata = customer_data[1] if isinstance(customer_data[1], dict) else json.loads(customer_data[1] or '{}')
                        onboarding_metadata = customer_data[2] if isinstance(customer_data[2], dict) else json.loads(customer_data[2] or '{}')
                        
                        # Verificar si auto_activate está habilitado
                        auto_activate = onboarding_metadata.get("auto_activate_services", True)
                        
                        if auto_activate:
                            # Obtener servicios a activar
                            services_to_activate = (
                                onboarding_metadata.get("services_to_activate") or
                                contract_metadata.get("services_to_activate") or
                                ["api_access", "dashboard", "support"]
                            )
                            
                            # Importar función de activación
                            from data.airflow.dags.contract_signature_activation import activate_customer_services
                            
                            # Activar servicios
                            activation_result = activate_customer_services(
                                customer_email=customer_email,
                                services_to_activate=services_to_activate,
                                contract_id=contract_id,
                            )
                            
                            logger.info(
                                f"Servicios activados automáticamente tras firma",
                                extra={
                                    "contract_id": contract_id,
                                    "customer_email": customer_email,
                                    "activated_services": activation_result.get("activated_services", []),
                                },
                            )
                            
                            # Registrar evento de activación
                            hook.run("""
                                INSERT INTO contract_events (contract_id, event_type, event_description, event_data)
                                VALUES (%s, 'services_activated', %s, %s::jsonb)
                            """, parameters=(
                                contract_id,
                                f"Servicios activados automáticamente para {customer_email}",
                                json.dumps(activation_result)
                            ))
                except Exception as e:
                    logger.error(f"Error activando servicios automáticamente: {e}", exc_info=True)
                    # No fallar el procesamiento del webhook si la activación falla
            
            # Enviar notificación
            try:
                from data.airflow.plugins.contract_notifications import send_contract_notification
                contract_info_query = "SELECT title, primary_party_name FROM contracts WHERE contract_id = %s"
                contract_info = hook.get_first(contract_info_query, parameters=(contract_id,))
                if contract_info:
                    send_contract_notification("signed", contract_id, {
                        "title": contract_info[0],
                        "primary_party_name": contract_info[1],
                        "signed_date": datetime.now().isoformat()
                    })
            except Exception as e:
                logger.warning(f"Error enviando notificación: {e}")
            
            return {
                "status": "processed",
                "contract_id": contract_id,
                "event_type": event_type,
                "new_status": status_result.get("status")
            }
        
        elif event_type in ("envelope-declined", "envelope-voided"):
            # Actualizar estado a cancelado
            hook.run(
                "UPDATE contracts SET status = 'cancelled', updated_at = NOW() WHERE contract_id = %s",
                parameters=(contract_id,)
            )
            
            hook.run(
                """
                INSERT INTO contract_events (
                    contract_id, event_type, event_description, event_data
                ) VALUES (%s, %s, %s, %s)
                """,
                parameters=(
                    contract_id,
                    event_type.replace("-", "_"),
                    f"Contrato {event_type} desde DocuSign",
                    json.dumps({"envelope_id": envelope_id})
                )
            )
            
            return {
                "status": "processed",
                "contract_id": contract_id,
                "event_type": event_type,
                "new_status": "cancelled"
            }
        
        else:
            # Registrar evento genérico
            hook.run(
                """
                INSERT INTO contract_events (
                    contract_id, event_type, event_description, event_data
                ) VALUES (%s, %s, %s, %s)
                """,
                parameters=(
                    contract_id,
                    event_type.replace("-", "_"),
                    f"Evento DocuSign: {event_type}",
                    json.dumps(event_data)
                )
            )
            
            return {
                "status": "logged",
                "contract_id": contract_id,
                "event_type": event_type
            }


class PandaDocWebhookHandler:
    """Manejador de webhooks de PandaDoc"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("PANDADOC_API_KEY", "")
    
    def verify_signature(self, payload: str, signature: str) -> bool:
        """Verifica la firma del webhook de PandaDoc"""
        if not self.api_key:
            logger.warning("PandaDoc API key no configurado, saltando verificación")
            return True
        
        try:
            expected_signature = hmac.new(
                self.api_key.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"Error verificando firma PandaDoc: {e}")
            return False
    
    def process_event(self, event_data: Dict[str, Any], postgres_conn_id: str = "postgres_default") -> Dict[str, Any]:
        """Procesa un evento de webhook de PandaDoc"""
        event_type = event_data.get("event", "")
        document_id = event_data.get("data", {}).get("id", "")
        
        logger.info(
            f"Procesando evento PandaDoc",
            extra={
                "event_type": event_type,
                "document_id": document_id
            }
        )
        
        if not POSTGRES_AVAILABLE:
            raise ImportError("PostgreSQL hook no disponible")
        
        hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        
        # Buscar contrato por document_id
        contract_query = """
            SELECT contract_id, status
            FROM contracts
            WHERE esignature_document_id = %s
        """
        contract = hook.get_first(contract_query, parameters=(document_id,))
        
        if not contract:
            logger.warning(f"Contrato no encontrado para document_id: {document_id}")
            return {"status": "not_found", "document_id": document_id}
        
        contract_id = contract[0]
        
        # Procesar según tipo de evento
        if event_type == "document_completed":
            # Verificar y actualizar estado
            status_result = check_contract_signature_status(contract_id=contract_id)
            
            # Actualizar estado del contrato a fully_signed
            if status_result.get("status") == "fully_signed":
                signed_date = status_result.get("signed_date") or datetime.now()
                hook.run("""
                    UPDATE contracts
                    SET status = 'fully_signed',
                        signed_date = %s,
                        updated_at = NOW()
                    WHERE contract_id = %s
                """, parameters=(signed_date, contract_id))
                
                # Activar servicios automáticamente si está configurado
                try:
                    # Obtener información del cliente y servicios a activar
                    customer_query = """
                        SELECT 
                            c.primary_party_email,
                            c.metadata as contract_metadata,
                            co.metadata as onboarding_metadata
                        FROM contracts c
                        LEFT JOIN customer_onboarding co ON c.primary_party_email = co.customer_email
                        WHERE c.contract_id = %s
                    """
                    customer_data = hook.get_first(customer_query, parameters=(contract_id,))
                    
                    if customer_data:
                        customer_email = customer_data[0]
                        contract_metadata = customer_data[1] if isinstance(customer_data[1], dict) else json.loads(customer_data[1] or '{}')
                        onboarding_metadata = customer_data[2] if isinstance(customer_data[2], dict) else json.loads(customer_data[2] or '{}')
                        
                        # Verificar si auto_activate está habilitado
                        auto_activate = onboarding_metadata.get("auto_activate_services", True)
                        
                        if auto_activate:
                            # Obtener servicios a activar
                            services_to_activate = (
                                onboarding_metadata.get("services_to_activate") or
                                contract_metadata.get("services_to_activate") or
                                ["api_access", "dashboard", "support"]
                            )
                            
                            # Importar función de activación
                            from data.airflow.dags.contract_signature_activation import activate_customer_services
                            
                            # Activar servicios
                            activation_result = activate_customer_services(
                                customer_email=customer_email,
                                services_to_activate=services_to_activate,
                                contract_id=contract_id,
                            )
                            
                            logger.info(
                                f"Servicios activados automáticamente tras firma",
                                extra={
                                    "contract_id": contract_id,
                                    "customer_email": customer_email,
                                    "activated_services": activation_result.get("activated_services", []),
                                },
                            )
                            
                            # Registrar evento de activación
                            hook.run("""
                                INSERT INTO contract_events (contract_id, event_type, event_description, event_data)
                                VALUES (%s, 'services_activated', %s, %s::jsonb)
                            """, parameters=(
                                contract_id,
                                f"Servicios activados automáticamente para {customer_email}",
                                json.dumps(activation_result)
                            ))
                except Exception as e:
                    logger.error(f"Error activando servicios automáticamente: {e}", exc_info=True)
                    # No fallar el procesamiento del webhook si la activación falla
            
            # Enviar notificación
            try:
                from data.airflow.plugins.contract_notifications import send_contract_notification
                contract_info_query = "SELECT title, primary_party_name FROM contracts WHERE contract_id = %s"
                contract_info = hook.get_first(contract_info_query, parameters=(contract_id,))
                if contract_info:
                    send_contract_notification("signed", contract_id, {
                        "title": contract_info[0],
                        "primary_party_name": contract_info[1],
                        "signed_date": datetime.now().isoformat()
                    })
            except Exception as e:
                logger.warning(f"Error enviando notificación: {e}")
            
            return {
                "status": "processed",
                "contract_id": contract_id,
                "event_type": event_type,
                "new_status": status_result.get("status")
            }
        
        elif event_type == "document_deleted":
            # Actualizar estado
            hook.run(
                "UPDATE contracts SET status = 'cancelled', updated_at = NOW() WHERE contract_id = %s",
                parameters=(contract_id,)
            )
            
            return {
                "status": "processed",
                "contract_id": contract_id,
                "event_type": event_type,
                "new_status": "cancelled"
            }
        
        else:
            # Registrar evento genérico
            hook.run(
                """
                INSERT INTO contract_events (
                    contract_id, event_type, event_description, event_data
                ) VALUES (%s, %s, %s, %s)
                """,
                parameters=(
                    contract_id,
                    event_type,
                    f"Evento PandaDoc: {event_type}",
                    json.dumps(event_data)
                )
            )
            
            return {
                "status": "logged",
                "contract_id": contract_id,
                "event_type": event_type
            }


def create_webhook_app(secret_key: str = None) -> Optional[Any]:
    """
    Crea una aplicación Flask para recibir webhooks.
    
    Args:
        secret_key: Secret key para validación (opcional)
        
    Returns:
        Flask app o None si Flask no está disponible
    """
    if not FLASK_AVAILABLE:
        logger.warning("Flask no disponible, no se puede crear app de webhooks")
        return None
    
    app = Flask(__name__)
    
    docusign_handler = DocuSignWebhookHandler()
    pandadoc_handler = PandaDocWebhookHandler()
    
    @app.route('/webhooks/docusign', methods=['POST'])
    def docusign_webhook():
        """Endpoint para webhooks de DocuSign"""
        try:
            signature = request.headers.get('X-DocuSign-Signature-1', '')
            payload = request.get_data()
            
            if not docusign_handler.verify_signature(payload, signature):
                logger.warning("Firma DocuSign inválida")
                return jsonify({"error": "Invalid signature"}), 401
            
            event_data = request.get_json()
            result = docusign_handler.process_event(event_data)
            
            return jsonify(result), 200
        except Exception as e:
            logger.error(f"Error procesando webhook DocuSign: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/webhooks/pandadoc', methods=['POST'])
    def pandadoc_webhook():
        """Endpoint para webhooks de PandaDoc"""
        try:
            signature = request.headers.get('X-PandaDoc-Signature', '')
            payload = request.get_data(as_text=True)
            
            if not pandadoc_handler.verify_signature(payload, signature):
                logger.warning("Firma PandaDoc inválida")
                return jsonify({"error": "Invalid signature"}), 401
            
            event_data = request.get_json()
            result = pandadoc_handler.process_event(event_data)
            
            return jsonify(result), 200
        except Exception as e:
            logger.error(f"Error procesando webhook PandaDoc: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/webhooks/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "handlers": {
                "docusign": bool(docusign_handler.secret_key),
                "pandadoc": bool(pandadoc_handler.api_key)
            }
        }), 200
    
    return app

