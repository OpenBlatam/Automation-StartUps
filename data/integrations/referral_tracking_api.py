"""
API para Tracking de Referidos

Este módulo proporciona endpoints para:
- Generar enlaces de referido
- Trackear clicks en enlaces
- Validar referidos
- Obtener estadísticas de referidos
"""

from flask import Flask, request, jsonify, redirect
from typing import Dict, Any, Optional
import logging
import os
from datetime import datetime
import hashlib
import secrets

from referral_validator import ReferralValidator, generate_referral_link

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuración
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "tu_base_de_datos"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "")
}

BASE_URL = os.getenv("BASE_URL", "https://tu-dominio.com")


def get_db_connection():
    """Obtiene conexión a la base de datos."""
    try:
        import psycopg2
        return psycopg2.connect(**DB_CONFIG)
    except ImportError:
        logger.error("psycopg2 no está instalado")
        return None
    except Exception as e:
        logger.error(f"Error conectando a base de datos: {e}")
        return None


def get_db_hook():
    """Obtiene hook de Airflow (si está disponible)."""
    try:
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        return PostgresHook(postgres_conn_id="postgres_default")
    except:
        return None


@app.route("/api/referral/generate", methods=["POST"])
def generate_referral():
    """
    Genera código y enlace de referido para un lead.
    
    Body:
    {
        "lead_id": "lead_123",
        "email": "usuario@example.com"
    }
    """
    try:
        data = request.get_json()
        lead_id = data.get("lead_id")
        email = data.get("email")
        
        if not lead_id or not email:
            return jsonify({
                "success": False,
                "error": "lead_id y email son requeridos"
            }), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                "success": False,
                "error": "Error de conexión"
            }), 500
        
        try:
            cursor = conn.cursor()
            
            # Verificar si ya existe programa de referidos
            cursor.execute(
                "SELECT referral_code, referral_link FROM referral_programs WHERE lead_id = %s",
                (lead_id,)
            )
            existing = cursor.fetchone()
            
            if existing:
                return jsonify({
                    "success": True,
                    "referral_code": existing[0],
                    "referral_link": existing[1],
                    "message": "Código ya existente"
                })
            
            # Generar código único
            from referral_validator import generate_referral_code
            referral_code = generate_referral_code(email)
            referral_link = generate_referral_link(BASE_URL, referral_code)
            
            # Obtener incentivo
            cursor.execute(
                "SELECT incentive_amount FROM referral_programs WHERE lead_id = %s LIMIT 1",
                (lead_id,)
            )
            incentive_result = cursor.fetchone()
            incentive_amount = float(incentive_result[0]) if incentive_result else 10.0
            
            # Insertar programa de referidos
            cursor.execute(
                """
                INSERT INTO referral_programs (
                    lead_id,
                    referral_code,
                    referral_link,
                    incentive_amount,
                    status,
                    invited_at,
                    created_at,
                    updated_at
                ) VALUES (%s, %s, %s, %s, 'active', NOW(), NOW(), NOW())
                """,
                (lead_id, referral_code, referral_link, incentive_amount)
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                "success": True,
                "referral_code": referral_code,
                "referral_link": referral_link,
                "incentive_amount": incentive_amount
            }), 201
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error generando referido: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
        finally:
            if conn:
                conn.close()
                
    except Exception as e:
        logger.error(f"Error en endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Error interno"
        }), 500


@app.route("/refer/<code>", methods=["GET"])
def track_referral_click(code: str):
    """
    Endpoint que trackea clicks en enlaces de referido y redirige.
    
    Parámetros de query:
    - redirect: URL a la que redirigir (default: página de registro)
    """
    try:
        redirect_url = request.args.get("redirect", f"{BASE_URL}/register?ref={code}")
        ip_address = request.remote_addr
        user_agent = request.headers.get("User-Agent", "")
        
        conn = get_db_connection()
        if not conn:
            # Si no hay conexión, redirigir de todas formas
            return redirect(redirect_url)
        
        try:
            cursor = conn.cursor()
            
            # Verificar que el código existe
            cursor.execute(
                """
                SELECT rp.referral_code, rp.lead_id, ol.email
                FROM referral_programs rp
                JOIN organic_leads ol ON rp.lead_id = ol.lead_id
                WHERE rp.referral_code = %s AND rp.status = 'active'
                """,
                (code,)
            )
            
            result = cursor.fetchone()
            if not result:
                # Código inválido, redirigir sin tracking
                return redirect(redirect_url)
            
            referral_code, lead_id, referrer_email = result
            
            # Registrar click (opcional: crear tabla de clicks)
            # Por ahora solo logueamos
            
            logger.info(f"Click en referido: {code} desde IP {ip_address}")
            
            cursor.close()
            conn.close()
            
            # Redirigir con código en URL
            if "?" in redirect_url:
                redirect_url = f"{redirect_url}&ref={code}"
            else:
                redirect_url = f"{redirect_url}?ref={code}"
            
            return redirect(redirect_url)
            
        except Exception as e:
            logger.error(f"Error tracking click: {e}")
            return redirect(redirect_url)
        finally:
            if conn:
                conn.close()
                
    except Exception as e:
        logger.error(f"Error en endpoint de tracking: {e}")
        return redirect(redirect_url)


@app.route("/api/referral/validate", methods=["POST"])
def validate_referral():
    """
    Valida un referido antes de otorgar recompensa.
    
    Body:
    {
        "referral_id": "ref_123",
        "referrer_email": "referrer@example.com",
        "referred_email": "referred@example.com",
        "ip_address": "192.168.1.1"
    }
    """
    try:
        data = request.get_json()
        
        referral_id = data.get("referral_id")
        referrer_email = data.get("referrer_email")
        referred_email = data.get("referred_email")
        ip_address = data.get("ip_address")
        
        if not all([referral_id, referrer_email, referred_email]):
            return jsonify({
                "success": False,
                "error": "Datos incompletos"
            }), 400
        
        # Validar usando ReferralValidator
        db_hook = get_db_hook()
        validator = ReferralValidator(db_hook=db_hook)
        
        validation = validator.validate_referral(
            referral_id=referral_id,
            referrer_email=referrer_email,
            referred_email=referred_email,
            ip_address=ip_address
        )
        
        return jsonify({
            "success": validation["is_valid"],
            "validation": validation
        }), 200 if validation["is_valid"] else 400
        
    except Exception as e:
        logger.error(f"Error validando referido: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/referral/stats/<lead_id>", methods=["GET"])
def get_referral_stats(lead_id: str):
    """
    Obtiene estadísticas de referidos para un lead.
    """
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                "success": False,
                "error": "Error de conexión"
            }), 500
        
        try:
            cursor = conn.cursor()
            
            # Obtener estadísticas
            cursor.execute(
                """
                SELECT 
                    rp.referral_code,
                    rp.referral_link,
                    rp.incentive_amount,
                    COUNT(r.referral_id) as total_referrals,
                    COUNT(CASE WHEN r.status = 'validated' THEN 1 END) as validated,
                    COUNT(CASE WHEN r.status = 'fraud' THEN 1 END) as fraud,
                    COALESCE(SUM(rr.reward_amount), 0) as total_earned,
                    COUNT(CASE WHEN rr.status = 'paid' THEN 1 END) as rewards_paid
                FROM referral_programs rp
                LEFT JOIN referrals r ON rp.referral_code = r.referral_code
                LEFT JOIN referral_rewards rr ON r.referral_id = rr.referral_id
                WHERE rp.lead_id = %s
                GROUP BY rp.referral_code, rp.referral_link, rp.incentive_amount
                """,
                (lead_id,)
            )
            
            result = cursor.fetchone()
            
            if not result:
                return jsonify({
                    "success": False,
                    "error": "No se encontró programa de referidos para este lead"
                }), 404
            
            stats = {
                "referral_code": result[0],
                "referral_link": result[1],
                "incentive_amount": float(result[2]),
                "total_referrals": result[3],
                "validated_referrals": result[4],
                "fraud_referrals": result[5],
                "total_earned": float(result[6]),
                "rewards_paid": result[7]
            }
            
            cursor.close()
            conn.close()
            
            return jsonify({
                "success": True,
                "stats": stats
            }), 200
            
        except Exception as e:
            logger.error(f"Error obteniendo stats: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
        finally:
            if conn:
                conn.close()
                
    except Exception as e:
        logger.error(f"Error en endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Error interno"
        }), 500


@app.route("/api/referral/health", methods=["GET"])
def health_check():
    """Health check."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    logger.info(f"Iniciando API de referidos en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)

