"""
Webhook para Captura de Leads Orgánicos

Este script puede ser usado como endpoint webhook para capturar
leads desde formularios, landing pages, o lead magnets.
"""

from flask import Flask, request, jsonify
from typing import Dict, Any, Optional
import logging
import os
from datetime import datetime
import secrets
import hashlib

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuración de base de datos (ajustar según tu setup)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "tu_base_de_datos"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "")
}


def get_db_connection():
    """Obtiene conexión a la base de datos."""
    try:
        import psycopg2
        return psycopg2.connect(**DB_CONFIG)
    except ImportError:
        logger.error("psycopg2 no está instalado. Instala con: pip install psycopg2-binary")
        return None
    except Exception as e:
        logger.error(f"Error conectando a base de datos: {e}")
        return None


def generate_lead_id() -> str:
    """Genera ID único para lead."""
    return f"lead_{secrets.token_hex(8)}"


def validate_lead_data(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Valida datos del lead.
    
    Returns:
        (is_valid, error_message)
    """
    if not data.get("email"):
        return False, "Email es requerido"
    
    email = data["email"].strip().lower()
    
    # Validación básica de email
    if "@" not in email or "." not in email.split("@")[1]:
        return False, "Email inválido"
    
    return True, None


def insert_lead(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inserta lead en base de datos.
    
    Returns:
        Dict con resultado de inserción
    """
    conn = get_db_connection()
    if not conn:
        return {
            "success": False,
            "error": "Error de conexión a base de datos"
        }
    
    try:
        cursor = conn.cursor()
        
        # Generar ID único
        lead_id = generate_lead_id()
        
        # Extraer datos
        email = data.get("email", "").strip().lower()
        first_name = data.get("first_name", "").strip()
        last_name = data.get("last_name", "").strip()
        source = data.get("source", "organic")
        utm_source = data.get("utm_source")
        utm_campaign = data.get("utm_campaign")
        utm_medium = data.get("utm_medium")
        interest_area = data.get("interest_area", "general")
        lead_magnet_downloaded = data.get("lead_magnet_downloaded", False)
        referral_code = data.get("referral_code")  # Si viene de referido
        
        # Si hay referral_code, obtener referrer_lead_id
        referrer_lead_id = None
        if referral_code:
            cursor.execute(
                """
                SELECT lead_id 
                FROM referral_programs 
                WHERE referral_code = %s AND status = 'active'
                LIMIT 1
                """,
                (referral_code,)
            )
            result = cursor.fetchone()
            if result:
                referrer_lead_id = result[0]
        
        # Insertar lead
        insert_query = """
            INSERT INTO organic_leads (
                lead_id,
                email,
                first_name,
                last_name,
                source,
                utm_source,
                utm_campaign,
                utm_medium,
                interest_area,
                lead_magnet_downloaded,
                referral_code,
                referrer_lead_id,
                status,
                created_at,
                updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'new', NOW(), NOW())
            ON CONFLICT (lead_id) DO NOTHING
        """
        
        cursor.execute(
            insert_query,
            (
                lead_id,
                email,
                first_name,
                last_name,
                source,
                utm_source,
                utm_campaign,
                utm_medium,
                interest_area,
                lead_magnet_downloaded,
                referral_code,
                referrer_lead_id
            )
        )
        
        # Si es un referido, crear registro en tabla referrals
        if referral_code and referrer_lead_id:
            referral_id = f"ref_{secrets.token_hex(8)}"
            cursor.execute(
                """
                INSERT INTO referrals (
                    referral_id,
                    referrer_lead_id,
                    referral_code,
                    referred_email,
                    referred_first_name,
                    referred_last_name,
                    ip_address,
                    status,
                    created_at,
                    updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', NOW(), NOW())
                """,
                (
                    referral_id,
                    referrer_lead_id,
                    referral_code,
                    email,
                    first_name,
                    last_name,
                    request.remote_addr
                )
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Lead insertado: {lead_id} - {email}")
        
        return {
            "success": True,
            "lead_id": lead_id,
            "message": "Lead capturado exitosamente"
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error insertando lead: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        if conn:
            conn.close()


@app.route("/webhook/lead-capture", methods=["POST"])
def capture_lead():
    """
    Endpoint webhook para capturar leads.
    
    Body esperado:
    {
        "email": "usuario@example.com",
        "first_name": "Juan",
        "last_name": "Pérez",
        "source": "organic",
        "utm_source": "google",
        "utm_campaign": "summer2024",
        "utm_medium": "cpc",
        "interest_area": "marketing",
        "lead_magnet_downloaded": true,
        "referral_code": "REF-XXXXXXXXXXXX"  // Opcional
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No se recibieron datos"
            }), 400
        
        # Validar datos
        is_valid, error_message = validate_lead_data(data)
        if not is_valid:
            return jsonify({
                "success": False,
                "error": error_message
            }), 400
        
        # Insertar lead
        result = insert_lead(data)
        
        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error en webhook: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Error interno del servidor"
        }), 500


@app.route("/webhook/lead-capture/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }), 200


if __name__ == "__main__":
    # Configurar puerto desde variable de entorno
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    logger.info(f"Iniciando servidor webhook en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)

