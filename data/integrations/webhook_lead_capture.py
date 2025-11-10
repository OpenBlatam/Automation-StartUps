"""
Webhook Endpoint para Captura de Leads desde Web
=================================================

Endpoint Flask que recibe leads desde formularios web y los procesa automáticamente.
"""
from flask import Flask, request, jsonify
from typing import Dict, Any, Optional
import logging
import hmac
import hashlib
import json
import os
import re
from datetime import datetime

try:
    from airflow.models import DagRun
    from airflow.api.client.local_client import Client
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    logging.warning("Airflow no disponible, webhook funcionará en modo standalone")

logger = logging.getLogger(__name__)

app = Flask(__name__)


class LeadWebhookHandler:
    """Maneja webhooks de captura de leads"""
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Args:
            secret_key: Secret key para verificar firmas HMAC (opcional)
        """
        self.secret_key = secret_key or os.getenv("WEBHOOK_SECRET_KEY")
        self.airflow_client = None
        
        if AIRFLOW_AVAILABLE:
            try:
                self.airflow_client = Client()
            except Exception as e:
                logger.warning(f"No se pudo inicializar cliente Airflow: {e}")
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verifica firma HMAC del webhook"""
        if not self.secret_key:
            return True  # Sin verificación si no hay secret key
        
        expected_signature = hmac.new(
            self.secret_key.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    def normalize_lead_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza y valida datos del lead"""
        # Extraer datos básicos
        email = (raw_data.get("email") or "").strip().lower()
        if not email:
            raise ValueError("Email es requerido")
        
        # Validar formato de email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Email inválido")
        
        # Normalizar nombre
        first_name = (raw_data.get("first_name") or "").strip()
        last_name = (raw_data.get("last_name") or "").strip()
        
        # Si no hay nombres pero hay full_name, extraer
        if not first_name and not last_name:
            full_name = (raw_data.get("full_name") or "").strip()
            if full_name:
                parts = full_name.split(maxsplit=1)
                first_name = parts[0]
                last_name = parts[1] if len(parts) > 1 else ""
        
        # Normalizar teléfono
        phone = (raw_data.get("phone") or "").strip()
        if phone:
            # Remover caracteres no numéricos excepto +
            phone = re.sub(r'[^\d+]', '', phone)
        
        # Extraer metadata adicional
        metadata = {
            "ip_address": request.remote_addr,
            "user_agent": request.headers.get("User-Agent"),
            "referrer": request.headers.get("Referer"),
            "timestamp": datetime.utcnow().isoformat(),
            **raw_data.get("metadata", {})
        }
        
        # Extraer UTM parameters
        utm_params = {
            "utm_source": raw_data.get("utm_source"),
            "utm_campaign": raw_data.get("utm_campaign"),
            "utm_medium": raw_data.get("utm_medium"),
            "utm_term": raw_data.get("utm_term"),
            "utm_content": raw_data.get("utm_content")
        }
        
        return {
            "email": email,
            "first_name": first_name or None,
            "last_name": last_name or None,
            "phone": phone or None,
            "company": (raw_data.get("company") or "").strip() or None,
            "source": raw_data.get("source", "web"),
            "message": raw_data.get("message"),
            "landing_page": raw_data.get("landing_page") or request.headers.get("Referer"),
            "metadata": metadata,
            **utm_params
        }
    
    def trigger_airflow_dag(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dispara el DAG de Airflow para procesar el lead"""
        if not self.airflow_client:
            logger.warning("Airflow no disponible, guardando lead en modo standalone")
            return {"status": "queued", "mode": "standalone"}
        
        try:
            # Configurar parámetros del DAG
            config = {
                "lead_data": json.dumps(lead_data),
                "auto_assign_enabled": True,
                "auto_sync_crm": True,
                "create_followup_tasks": True
            }
            
            # Obtener configuración de CRM desde variables de entorno
            crm_type = os.getenv("CRM_TYPE", "salesforce")
            crm_config = {
                "username": os.getenv("SALESFORCE_USERNAME"),
                "password": os.getenv("SALESFORCE_PASSWORD"),
                "security_token": os.getenv("SALESFORCE_SECURITY_TOKEN"),
                "client_id": os.getenv("SALESFORCE_CLIENT_ID"),
                "client_secret": os.getenv("SALESFORCE_CLIENT_SECRET"),
                "sandbox": os.getenv("SALESFORCE_SANDBOX", "false").lower() == "true",
                "api_token": os.getenv("PIPEDRIVE_API_TOKEN"),
                "company_domain": os.getenv("PIPEDRIVE_COMPANY_DOMAIN"),
                "default_stage_id": os.getenv("PIPEDRIVE_DEFAULT_STAGE_ID")
            }
            
            config["crm_type"] = crm_type
            config["crm_config"] = json.dumps(crm_config)
            
            # Trigger DAG
            dag_run = self.airflow_client.trigger_dag(
                dag_id="web_lead_capture",
                conf=config,
                run_id=f"webhook_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
            )
            
            logger.info(f"DAG triggerado: {dag_run.run_id}")
            return {
                "status": "queued",
                "dag_run_id": dag_run.run_id,
                "mode": "airflow"
            }
            
        except Exception as e:
            logger.error(f"Error triggerando DAG: {e}", exc_info=True)
            raise


# Inicializar handler
handler = LeadWebhookHandler()


@app.route('/webhook/lead', methods=['POST'])
def webhook_lead():
    """Endpoint principal para recibir leads desde web"""
    try:
        # Verificar firma si está configurada
        signature = request.headers.get("X-Webhook-Signature")
        if handler.secret_key and signature:
            if not handler.verify_signature(request.data, signature):
                return jsonify({"error": "Invalid signature"}), 401
        
        # Obtener datos
        raw_data = request.get_json() or {}
        
        # Normalizar datos
        lead_data = handler.normalize_lead_data(raw_data)
        
        # Trigger DAG de Airflow
        result = handler.trigger_airflow_dag(lead_data)
        
        return jsonify({
            "success": True,
            "message": "Lead recibido y en proceso",
            "lead_email": lead_data["email"],
            **result
        }), 202
        
    except ValueError as e:
        logger.error(f"Error de validación: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error procesando webhook: {e}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route('/webhook/lead/batch', methods=['POST'])
def webhook_lead_batch():
    """Endpoint para recibir múltiples leads en un lote"""
    try:
        signature = request.headers.get("X-Webhook-Signature")
        if handler.secret_key and signature:
            if not handler.verify_signature(request.data, signature):
                return jsonify({"error": "Invalid signature"}), 401
        
        raw_data = request.get_json() or {}
        leads = raw_data.get("leads", [])
        
        if not isinstance(leads, list):
            return jsonify({"error": "leads debe ser un array"}), 400
        
        results = []
        errors = []
        
        for idx, raw_lead in enumerate(leads):
            try:
                lead_data = handler.normalize_lead_data(raw_lead)
                result = handler.trigger_airflow_dag(lead_data)
                results.append({
                    "index": idx,
                    "email": lead_data["email"],
                    "status": "queued",
                    **result
                })
            except Exception as e:
                errors.append({
                    "index": idx,
                    "error": str(e)
                })
                logger.error(f"Error procesando lead {idx}: {e}")
        
        return jsonify({
            "success": True,
            "processed": len(results),
            "errors": len(errors),
            "results": results,
            "errors_detail": errors
        }), 202
        
    except Exception as e:
        logger.error(f"Error procesando batch: {e}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route('/webhook/lead/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "airflow_available": AIRFLOW_AVAILABLE,
        "timestamp": datetime.utcnow().isoformat()
    }), 200


if __name__ == '__main__':
    import re
    port = int(os.getenv("WEBHOOK_PORT", 5000))
    debug = os.getenv("WEBHOOK_DEBUG", "false").lower() == "true"
    
    logger.info(f"Iniciando webhook server en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

