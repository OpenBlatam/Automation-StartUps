"""
Webhook Receiver para Actualizaciones desde CRM
================================================

Recibe webhooks de Salesforce/Pipedrive cuando hay cambios en el CRM
y actualiza el pipeline local automáticamente.
"""
from flask import Flask, request, jsonify
from typing import Dict, Any, Optional
import logging
import json
import os
import hmac
import hashlib
from datetime import datetime

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    logging.warning("psycopg2 no disponible")

logger = logging.getLogger(__name__)

app = Flask(__name__)


class CRMWebhookReceiver:
    """Recibe y procesa webhooks desde CRM"""
    
    def __init__(self, db_connection_string: Optional[str] = None):
        """
        Args:
            db_connection_string: String de conexión PostgreSQL
        """
        if not PSYCOPG2_AVAILABLE:
            raise ImportError("psycopg2 es requerido")
        
        self.db_conn_str = db_connection_string or os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/sales_db"
        )
    
    def get_db_connection(self):
        """Obtiene conexión a la base de datos"""
        return psycopg2.connect(self.db_conn_str)
    
    def process_salesforce_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa webhook de Salesforce"""
        try:
            # Salesforce envía datos en formato específico
            lead_id = webhook_data.get("Id") or webhook_data.get("id")
            email = webhook_data.get("Email")
            status = webhook_data.get("Status")
            
            if not email:
                return {"error": "Email no encontrado en webhook"}
            
            # Buscar lead en BD por email
            with self.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, lead_ext_id, metadata
                        FROM sales_pipeline
                        WHERE email = %s
                        LIMIT 1
                    """, (email,))
                    
                    result = cur.fetchone()
                    
                    if result:
                        pipeline_id, lead_ext_id, metadata = result
                        
                        # Mapear status de Salesforce a stage
                        stage_mapping = {
                            "Open - Not Contacted": "qualified",
                            "Working - Contacted": "contacted",
                            "Qualified - Qualified": "proposal_sent",
                            "Closed - Converted": "closed_won",
                            "Closed - Not Converted": "closed_lost"
                        }
                        stage = stage_mapping.get(status, "qualified")
                        
                        # Actualizar metadata con CRM ID
                        metadata_dict = json.loads(metadata) if isinstance(metadata, str) else (metadata or {})
                        metadata_dict.update({
                            "crm_id": lead_id,
                            "crm_type": "salesforce",
                            "last_synced_from_crm": datetime.utcnow().isoformat()
                        })
                        
                        # Actualizar pipeline
                        cur.execute("""
                            UPDATE sales_pipeline
                            SET 
                                stage = %s,
                                metadata = %s::jsonb,
                                updated_at = NOW()
                            WHERE id = %s
                        """, (stage, json.dumps(metadata_dict), pipeline_id))
                        
                        conn.commit()
                        
                        logger.info(f"Pipeline actualizado desde Salesforce: {lead_ext_id} -> {stage}")
                        return {"success": True, "lead_ext_id": lead_ext_id, "stage": stage}
                    else:
                        logger.warning(f"Lead no encontrado en BD para email: {email}")
                        return {"error": "Lead no encontrado"}
        
        except Exception as e:
            logger.error(f"Error procesando webhook Salesforce: {e}", exc_info=True)
            return {"error": str(e)}
    
    def process_pipedrive_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa webhook de Pipedrive"""
        try:
            # Pipedrive envía datos en formato específico
            event_type = webhook_data.get("event")
            data = webhook_data.get("current", {})
            
            person_id = data.get("id")
            emails = data.get("email", [])
            email_obj = next((e for e in emails if e.get("primary")), emails[0] if emails else {})
            email = email_obj.get("value") if email_obj else None
            
            if not email:
                return {"error": "Email no encontrado en webhook"}
            
            # Buscar lead en BD por email
            with self.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, lead_ext_id, metadata
                        FROM sales_pipeline
                        WHERE email = %s
                        LIMIT 1
                    """, (email,))
                    
                    result = cur.fetchone()
                    
                    if result:
                        pipeline_id, lead_ext_id, metadata = result
                        
                        # Actualizar metadata
                        metadata_dict = json.loads(metadata) if isinstance(metadata, str) else (metadata or {})
                        metadata_dict.update({
                            "crm_id": str(person_id),
                            "crm_type": "pipedrive",
                            "last_synced_from_crm": datetime.utcnow().isoformat()
                        })
                        
                        # Si hay deal, actualizar también
                        if webhook_data.get("related_object_type") == "deal":
                            deal_id = webhook_data.get("related_object_id")
                            if deal_id:
                                metadata_dict["deal_id"] = str(deal_id)
                        
                        # Actualizar pipeline
                        cur.execute("""
                            UPDATE sales_pipeline
                            SET 
                                metadata = %s::jsonb,
                                updated_at = NOW()
                            WHERE id = %s
                        """, (json.dumps(metadata_dict), pipeline_id))
                        
                        conn.commit()
                        
                        logger.info(f"Pipeline actualizado desde Pipedrive: {lead_ext_id}")
                        return {"success": True, "lead_ext_id": lead_ext_id}
                    else:
                        logger.warning(f"Lead no encontrado en BD para email: {email}")
                        return {"error": "Lead no encontrado"}
        
        except Exception as e:
            logger.error(f"Error procesando webhook Pipedrive: {e}", exc_info=True)
            return {"error": str(e)}


# Inicializar receiver
receiver = CRMWebhookReceiver()


@app.route('/webhook/crm/salesforce', methods=['POST'])
def salesforce_webhook():
    """Endpoint para webhooks de Salesforce"""
    try:
        # Verificar firma si está configurada
        secret = os.getenv("SALESFORCE_WEBHOOK_SECRET")
        if secret:
            signature = request.headers.get("X-Salesforce-Signature")
            if not verify_signature(request.data, signature, secret):
                return jsonify({"error": "Invalid signature"}), 401
        
        data = request.get_json() or request.form.to_dict()
        result = receiver.process_salesforce_webhook(data)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error procesando webhook Salesforce: {e}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route('/webhook/crm/pipedrive', methods=['POST'])
def pipedrive_webhook():
    """Endpoint para webhooks de Pipedrive"""
    try:
        # Verificar firma si está configurada
        secret = os.getenv("PIPEDRIVE_WEBHOOK_SECRET")
        if secret:
            signature = request.headers.get("X-Pipedrive-Signature")
            if not verify_signature(request.data, signature, secret):
                return jsonify({"error": "Invalid signature"}), 401
        
        data = request.get_json()
        result = receiver.process_pipedrive_webhook(data)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error procesando webhook Pipedrive: {e}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verifica firma HMAC"""
    if not signature:
        return False
    
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)


@app.route('/webhook/crm/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }), 200


if __name__ == '__main__':
    port = int(os.getenv("CRM_WEBHOOK_PORT", 5002))
    debug = os.getenv("CRM_WEBHOOK_DEBUG", "false").lower() == "true"
    
    logger.info(f"Iniciando CRM webhook receiver en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

