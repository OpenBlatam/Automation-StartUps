"""
API REST Completa para Sistema de Adquisición Orgánica

Endpoints para gestión completa del sistema desde aplicaciones externas.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import os

from organic_acquisition_ab_testing import ABTestingManager
from organic_acquisition_ml_scoring import LeadScoringService
from organic_acquisition_multichannel import MultiChannelMessaging
from organic_acquisition_gamification import GamificationSystem
from referral_validator import ReferralValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Permitir CORS para frontend

# Configuración
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "tu_base_de_datos"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "")
}


def get_db_connection():
    """Obtiene conexión a base de datos."""
    try:
        import psycopg2
        return psycopg2.connect(**DB_CONFIG)
    except:
        return None


def get_db_hook():
    """Obtiene hook de Airflow."""
    try:
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        return PostgresHook(postgres_conn_id="postgres_default")
    except:
        return None


# ============================================================================
# ENDPOINTS DE LEADS
# ============================================================================

@app.route("/api/v1/leads", methods=["GET"])
def list_leads():
    """Lista leads con filtros."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Filtros
        status = request.args.get("status")
        source = request.args.get("source")
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
        
        query = "SELECT * FROM organic_leads WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = %s"
            params.append(status)
        if source:
            query += " AND source = %s"
            params.append(source)
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        leads = []
        columns = [desc[0] for desc in cursor.description]
        for row in results:
            leads.append(dict(zip(columns, row)))
        
        cursor.close()
        conn.close()
        
        return jsonify({"leads": leads, "total": len(leads)})
        
    except Exception as e:
        logger.error(f"Error listando leads: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/leads/<lead_id>", methods=["GET"])
def get_lead(lead_id: str):
    """Obtiene un lead específico."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM organic_leads WHERE lead_id = %s",
            (lead_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"error": "Lead no encontrado"}), 404
        
        columns = [desc[0] for desc in cursor.description]
        lead = dict(zip(columns, result))
        
        cursor.close()
        conn.close()
        
        return jsonify(lead)
        
    except Exception as e:
        logger.error(f"Error obteniendo lead: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/leads/<lead_id>/score", methods=["GET"])
def get_lead_score(lead_id: str):
    """Obtiene score ML de un lead."""
    hook = get_db_hook()
    if not hook:
        return jsonify({"error": "No hay conexión"}), 500
    
    scoring = LeadScoringService(db_hook=hook)
    prediction = scoring.score_lead(lead_id)
    
    return jsonify(prediction)


# ============================================================================
# ENDPOINTS DE REFERIDOS
# ============================================================================

@app.route("/api/v1/referrals", methods=["GET"])
def list_referrals():
    """Lista referidos."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.*, ol.email as referrer_email
            FROM referrals r
            JOIN organic_leads ol ON r.referrer_lead_id = ol.lead_id
            ORDER BY r.created_at DESC
            LIMIT 50
        """)
        
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        referrals = [dict(zip(columns, row)) for row in results]
        
        cursor.close()
        conn.close()
        
        return jsonify({"referrals": referrals})
        
    except Exception as e:
        logger.error(f"Error listando referidos: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/referrals/validate", methods=["POST"])
def validate_referral():
    """Valida un referido."""
    data = request.get_json()
    
    hook = get_db_hook()
    validator = ReferralValidator(db_hook=hook)
    
    validation = validator.validate_referral(
        referral_id=data.get("referral_id"),
        referrer_email=data.get("referrer_email"),
        referred_email=data.get("referred_email"),
        ip_address=data.get("ip_address")
    )
    
    return jsonify(validation)


# ============================================================================
# ENDPOINTS DE GAMIFICACIÓN
# ============================================================================

@app.route("/api/v1/gamification/leaderboard", methods=["GET"])
def get_leaderboard():
    """Obtiene leaderboard."""
    hook = get_db_hook()
    if not hook:
        return jsonify({"error": "No hay conexión"}), 500
    
    period = request.args.get("period", "all_time")
    limit = int(request.args.get("limit", 10))
    
    gamification = GamificationSystem(db_hook=hook)
    leaderboard = gamification.get_leaderboard(limit=limit, period=period)
    
    return jsonify({"leaderboard": leaderboard})


@app.route("/api/v1/gamification/stats/<lead_id>", methods=["GET"])
def get_gamification_stats(lead_id: str):
    """Obtiene stats de gamificación de un usuario."""
    hook = get_db_hook()
    if not hook:
        return jsonify({"error": "No hay conexión"}), 500
    
    gamification = GamificationSystem(db_hook=hook)
    stats = gamification.get_user_stats(lead_id)
    
    return jsonify(stats)


# ============================================================================
# ENDPOINTS DE A/B TESTING
# ============================================================================

@app.route("/api/v1/ab-tests", methods=["GET"])
def list_ab_tests():
    """Lista tests A/B activos."""
    hook = get_db_hook()
    if not hook:
        return jsonify({"error": "No hay conexión"}), 500
    
    try:
        results = hook.get_records("""
            SELECT test_id, test_name, content_type, status
            FROM ab_tests
            WHERE status = 'active'
            ORDER BY created_at DESC
        """)
        
        tests = [
            {
                "test_id": r[0],
                "test_name": r[1],
                "content_type": r[2],
                "status": r[3]
            }
            for r in results
        ]
        
        return jsonify({"tests": tests})
        
    except Exception as e:
        logger.error(f"Error listando tests: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/ab-tests/<test_id>/results", methods=["GET"])
def get_ab_test_results(test_id: str):
    """Obtiene resultados de un test A/B."""
    hook = get_db_hook()
    if not hook:
        return jsonify({"error": "No hay conexión"}), 500
    
    manager = ABTestingManager(db_hook=hook)
    results = manager.get_test_results(test_id)
    
    return jsonify(results)


# ============================================================================
# ENDPOINTS DE MÉTRICAS
# ============================================================================

@app.route("/api/v1/metrics", methods=["GET"])
def get_metrics():
    """Obtiene métricas agregadas."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Total leads
        cursor.execute("SELECT COUNT(*) FROM organic_leads")
        total_leads = cursor.fetchone()[0]
        
        # Leads enganchados
        cursor.execute("SELECT COUNT(*) FROM organic_leads WHERE status = 'engaged'")
        engaged_leads = cursor.fetchone()[0]
        
        # Referidos validados
        cursor.execute("SELECT COUNT(*) FROM referrals WHERE status = 'validated'")
        validated_referrals = cursor.fetchone()[0]
        
        # Recompensas pagadas
        cursor.execute("""
            SELECT COALESCE(SUM(reward_amount), 0) 
            FROM referral_rewards 
            WHERE status = 'paid'
        """)
        rewards_paid = float(cursor.fetchone()[0] or 0)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "total_leads": total_leads,
            "engaged_leads": engaged_leads,
            "conversion_rate": (engaged_leads / total_leads * 100) if total_leads > 0 else 0,
            "validated_referrals": validated_referrals,
            "rewards_paid": rewards_paid
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route("/api/v1/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5003))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    logger.info(f"Iniciando API REST en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)

