#!/usr/bin/env python3
"""
API REST para Chatbot de Rastreo de Pedidos
Proporciona endpoints HTTP para integrar el chatbot en aplicaciones web, móviles, etc.

🎯 Uso:
    python3 chatbot_rastreo_api.py
    
    O con gunicorn:
    gunicorn -w 4 -b 0.0.0.0:5000 chatbot_rastreo_api:app

✨ Endpoints:
- POST /api/chat - Procesar mensaje del usuario
- GET /api/health - Health check
- GET /api/metrics - Métricas del chatbot
- GET /api/order/{order_id} - Obtener información de pedido
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import logging
import functools
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

# Importar el chatbot
try:
    from chatbot_rastreo_pedidos import OrderTrackingChatbot, OrderInfo
except ImportError:
    print("Error: No se pudo importar chatbot_rastreo_pedidos")
    print("Asegúrate de que el archivo chatbot_rastreo_pedidos.py esté en el mismo directorio")
    OrderTrackingChatbot = None

app = Flask(__name__)
CORS(app)  # Permitir CORS para integraciones web

# Configuración
COMPANY_NAME = os.getenv("COMPANY_NAME", "[Nombre de la Empresa]")
BOT_NAME = os.getenv("BOT_NAME", "[Nombre del Bot]")
DATABASE_URL = os.getenv("DATABASE_URL")
PORT = int(os.getenv("PORT", 5000))
API_KEY = os.getenv("API_KEY")  # API key opcional para autenticación
ENABLE_AUTH = os.getenv("ENABLE_AUTH", "false").lower() == "true"

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OrderTrackingAPI")

# Inicializar chatbot
chatbot = None
db_connection = None

# Rate limiting simple para API
api_rate_limits = {}  # ip -> [timestamps]
MAX_REQUESTS_PER_MINUTE = 60


def get_db_connection():
    """Obtiene conexión a la base de datos"""
    global db_connection
    
    if not DATABASE_URL:
        logger.warning("DATABASE_URL no configurada, funcionando en modo simulado")
        return None
    
    try:
        if db_connection is None or db_connection.closed:
            db_connection = psycopg2.connect(DATABASE_URL)
            logger.info("Conexión a base de datos establecida")
        return db_connection
    except Exception as e:
        logger.error(f"Error conectando a base de datos: {e}")
        return None


def init_chatbot():
    """Inicializa el chatbot"""
    global chatbot
    
    if OrderTrackingChatbot is None:
        logger.error("No se pudo importar OrderTrackingChatbot")
        return None
    
    db_conn = get_db_connection()
    
    chatbot = OrderTrackingChatbot(
        company_name=COMPANY_NAME,
        bot_name=BOT_NAME,
        db_connection=db_conn,
        enable_logging=True,
        persist_conversations=True,
        conversation_dir="chatbot_conversations"
    )
    
    logger.info(f"Chatbot inicializado: {BOT_NAME} para {COMPANY_NAME}")
    return chatbot


def require_auth(f):
    """Decorador para requerir autenticación"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if ENABLE_AUTH:
            api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
            if not api_key or api_key != API_KEY:
                return jsonify({"error": "API key requerida o inválida"}), 401
        return f(*args, **kwargs)
    return decorated_function


def rate_limit(f):
    """Decorador para rate limiting"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if ENABLE_AUTH:  # Solo aplicar rate limiting si auth está habilitado
            client_ip = request.remote_addr
            now = datetime.now().timestamp()
            
            if client_ip not in api_rate_limits:
                api_rate_limits[client_ip] = []
            
            # Limpiar timestamps antiguos (último minuto)
            api_rate_limits[client_ip] = [
                ts for ts in api_rate_limits[client_ip]
                if now - ts < 60
            ]
            
            if len(api_rate_limits[client_ip]) >= MAX_REQUESTS_PER_MINUTE:
                return jsonify({
                    "error": "Rate limit excedido",
                    "message": "Demasiadas requests. Intenta de nuevo en un minuto."
                }), 429
            
            api_rate_limits[client_ip].append(now)
        
        return f(*args, **kwargs)
    return decorated_function


@app.before_first_request
def setup():
    """Configuración inicial"""
    init_chatbot()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "order-tracking-chatbot",
        "timestamp": datetime.now().isoformat(),
        "bot_name": BOT_NAME,
        "company_name": COMPANY_NAME
    }), 200


@app.route('/api/metrics', methods=['GET'])
@require_auth
def get_metrics():
    """Obtiene métricas del chatbot"""
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        metrics = chatbot.get_metrics()
        return jsonify({
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error obteniendo métricas: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/order/<order_id>', methods=['GET'])
@rate_limit
def get_order_info(order_id: str):
    """
    Obtiene información de un pedido
    
    Args:
        order_id: ID del pedido
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        customer_email = request.args.get('customer_email', None)
        order_info = chatbot._get_order_from_db(order_id, customer_email)
        
        if not order_info:
            return jsonify({
                "error": "Pedido no encontrado",
                "order_id": order_id
            }), 404
        
        return jsonify({
            "order": {
                "order_id": order_info.order_id,
                "status": order_info.status,
                "payment_status": order_info.payment_status,
                "tracking_number": order_info.tracking_number,
                "shipping_carrier": order_info.shipping_carrier,
                "estimated_delivery_date": order_info.estimated_delivery_date,
                "actual_delivery_date": order_info.actual_delivery_date,
                "total_amount": order_info.total_amount,
                "currency": order_info.currency,
                "items": order_info.items,
                "shipping_address": order_info.shipping_address,
                "tracking_history": order_info.tracking_history,
                "payment_history": order_info.payment_history,
                "created_at": order_info.created_at,
                "updated_at": order_info.updated_at
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error obteniendo pedido: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/chat', methods=['POST'])
@rate_limit
def chat():
    """
    Procesa un mensaje del usuario y retorna respuesta del chatbot
    
    Body (JSON):
    {
        "message": "¿Dónde está mi pedido ORD-2024-001234?",
        "customer_email": "cliente@example.com",  # Opcional
        "conversation_id": "conv-123"  # Opcional
    }
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Body JSON requerido"}), 400
        
        message = data.get('message')
        if not message or not message.strip():
            return jsonify({"error": "Campo 'message' es requerido"}), 400
        
        customer_email = data.get('customer_email')
        conversation_id = data.get('conversation_id')
        
        # Obtener user_id del request
        user_id = data.get('user_id') or request.headers.get('X-User-ID')
        
        # Procesar mensaje
        response = chatbot.process_message(
            message=message,
            customer_email=customer_email,
            conversation_id=conversation_id,
            user_id=user_id
        )
        
        # Preparar respuesta
        response_data = {
            "response": response.message,
            "confidence": response.confidence,
            "intent": response.intent,
            "requires_escalation": response.requires_escalation,
            "escalation_reason": response.escalation_reason,
            "processing_time": response.processing_time,
            "timestamp": datetime.now().isoformat()
        }
        
        # Agregar información del pedido si está disponible
        if response.order_info:
            response_data["order_info"] = {
                "order_id": response.order_info.order_id,
                "status": response.order_info.status,
                "payment_status": response.order_info.payment_status,
                "tracking_number": response.order_info.tracking_number,
                "estimated_delivery_date": response.order_info.estimated_delivery_date
            }
        
        return jsonify(response_data), 200
    
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id: str):
    """
    Obtiene el historial de una conversación
    
    Args:
        conversation_id: ID de la conversación
    """
    try:
        conversation_file = chatbot.conversation_dir / f"{conversation_id}.json"
        
        if not conversation_file.exists():
            return jsonify({"error": "Conversación no encontrada"}), 404
        
        import json as json_lib
        with open(conversation_file, 'r', encoding='utf-8') as f:
            conversation_data = json_lib.load(f)
        
        return jsonify(conversation_data), 200
    
    except Exception as e:
        logger.error(f"Error obteniendo conversación: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/orders/search', methods=['GET'])
def search_orders():
    """
    Busca pedidos por email del cliente
    
    Query params:
    - customer_email: Email del cliente (requerido)
    - limit: Límite de resultados (default: 10)
    """
    if not db_connection:
        return jsonify({"error": "Base de datos no disponible"}), 500
    
    try:
        customer_email = request.args.get('customer_email')
        if not customer_email:
            return jsonify({"error": "customer_email es requerido"}), 400
        
        limit = int(request.args.get('limit', 10))
        
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                order_id, status, payment_status, total_amount, currency,
                created_at, estimated_delivery_date
            FROM ecommerce_orders
            WHERE customer_email = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        
        cursor.execute(query, (customer_email, limit))
        orders = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            "orders": [dict(order) for order in orders],
            "count": len(orders)
        }), 200
    
    except Exception as e:
        logger.error(f"Error buscando pedidos: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Manejo de errores 404"""
    return jsonify({"error": "Endpoint no encontrado"}), 404


@app.route('/api/webhook/carrier-update', methods=['POST'])
@rate_limit
def carrier_update_webhook():
    """
    Webhook para recibir actualizaciones de carriers
    
    Body:
    {
        "tracking_number": "TRACK123",
        "order_id": "ORD-2024-001234",  # Opcional
        "status": "in_transit",
        "carrier": "fedex",
        "location": "Ciudad",
        "carrier_status": "In Transit",
        "message": "En camino",
        "estimated_delivery": "2024-01-15"
    }
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        data = request.get_json()
        
        tracking_number = data.get('tracking_number')
        order_id = data.get('order_id')
        status = data.get('status')
        
        if not tracking_number and not order_id:
            return jsonify({"error": "tracking_number o order_id requerido"}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Error de conexión"}), 500
        
        cursor = conn.cursor()
        
        # Buscar pedido
        if order_id:
            query = "SELECT id FROM ecommerce_orders WHERE order_id = %s"
            cursor.execute(query, (order_id,))
        else:
            query = "SELECT id, order_id FROM ecommerce_orders WHERE tracking_number = %s"
            cursor.execute(query, (tracking_number,))
        
        order = cursor.fetchone()
        
        if not order:
            cursor.close()
            conn.close()
            return jsonify({"error": "Pedido no encontrado"}), 404
        
        order_id_db = order[0]
        found_order_id = order[1] if len(order) > 1 else order_id
        
        # Insertar tracking update
        tracking_query = """
            INSERT INTO ecommerce_order_tracking
            (order_id, status, location, carrier_status, carrier_message, timestamp, metadata)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s)
        """
        cursor.execute(tracking_query, (
            order_id_db,
            status,
            data.get('location', ''),
            data.get('carrier_status', ''),
            data.get('message', ''),
            json.dumps(data)
        ))
        
        # Actualizar estado del pedido si cambió
        if status:
            update_query = """
                UPDATE ecommerce_orders
                SET status = %s, updated_at = NOW()
                WHERE id = %s AND status != %s
            """
            cursor.execute(update_query, (status, order_id_db, status))
            
            if status == 'delivered':
                delivery_query = """
                    UPDATE ecommerce_orders
                    SET actual_delivery_date = CURRENT_DATE
                    WHERE id = %s
                """
                cursor.execute(delivery_query, (order_id_db,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Actualización de carrier procesada para pedido {found_order_id}")
        
        return jsonify({
            "success": True,
            "order_id": found_order_id,
            "status": status
        }), 200
    
    except Exception as e:
        logger.error(f"Error procesando webhook de carrier: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/notifications/send', methods=['POST'])
@require_auth
def send_proactive_notification():
    """
    Envía una notificación proactiva a un cliente
    
    Body:
    {
        "order_id": "ORD-2024-001234",
        "customer_email": "cliente@example.com",
        "type": "status_update|delay|delivery",
        "message": "Mensaje personalizado (opcional)"
    }
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        data = request.get_json()
        
        order_id = data.get('order_id')
        customer_email = data.get('customer_email')
        notification_type = data.get('type', 'status_update')
        custom_message = data.get('message')
        
        if not order_id:
            return jsonify({"error": "order_id requerido"}), 400
        
        # Obtener información del pedido
        order_info = chatbot._get_order_from_db(order_id, customer_email)
        
        if not order_info:
            return jsonify({"error": "Pedido no encontrado"}), 404
        
        # Generar mensaje según tipo
        if custom_message:
            message = custom_message
        elif notification_type == 'status_update':
            message = chatbot._generate_tracking_response(order_info)
        elif notification_type == 'delivery':
            message = f"✅ Tu pedido {order_id} ha sido entregado. ¡Esperamos que disfrutes tu compra!"
        elif notification_type == 'delay':
            message = f"⏰ Tu pedido {order_id} está experimentando un pequeño retraso. Te mantendremos informado."
        else:
            message = chatbot._generate_tracking_response(order_info)
        
        # Aquí podrías integrar con webhook, email, Telegram, etc.
        webhook_url = os.getenv("NOTIFICATION_WEBHOOK_URL")
        if webhook_url:
            import requests
            try:
                requests.post(webhook_url, json={
                    'order_id': order_id,
                    'customer_email': customer_email,
                    'type': notification_type,
                    'message': message
                }, timeout=5)
            except Exception as e:
                logger.warning(f"Error enviando webhook de notificación: {e}")
        
        return jsonify({
            "success": True,
            "order_id": order_id,
            "notification_type": notification_type,
            "message": message
        }), 200
    
    except Exception as e:
        logger.error(f"Error enviando notificación: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/orders/<order_id>/problems', methods=['GET'])
@rate_limit
def detect_order_problems(order_id: str):
    """
    Detecta problemas potenciales en un pedido
    
    Query params:
    - customer_email: Email del cliente (opcional, para validación)
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        customer_email = request.args.get('customer_email')
        order_info = chatbot._get_order_from_db(order_id, customer_email)
        
        if not order_info:
            return jsonify({"error": "Pedido no encontrado"}), 404
        
        problems = chatbot._detect_problems(order_info)
        
        return jsonify({
            "order_id": order_id,
            "problems": [
                {
                    "type": p.problem_type,
                    "severity": p.severity,
                    "description": p.description,
                    "suggested_action": p.suggested_action,
                    "confidence": p.confidence
                }
                for p in problems
            ],
            "problems_count": len(problems),
            "has_critical_problems": any(p.severity in ['critical', 'high'] for p in problems)
        }), 200
    
    except Exception as e:
        logger.error(f"Error detectando problemas: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/users/<customer_email>/pattern', methods=['GET'])
@rate_limit
def get_user_pattern(customer_email: str):
    """
    Obtiene el patrón de comportamiento de un usuario
    
    Args:
        customer_email: Email del cliente
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        pattern = chatbot.get_user_pattern(customer_email)
        
        if not pattern:
            return jsonify({
                "customer_email": customer_email,
                "message": "No hay suficiente historial para este usuario"
            }), 404
        
        return jsonify(pattern), 200
    
    except Exception as e:
        logger.error(f"Error obteniendo patrón de usuario: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/orders/<order_id>/predictions', methods=['GET'])
@rate_limit
def get_order_predictions(order_id: str):
    """
    Obtiene predicciones de problemas futuros para un pedido
    
    Query params:
    - customer_email: Email del cliente (opcional, para validación)
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        customer_email = request.args.get('customer_email')
        order_info = chatbot._get_order_from_db(order_id, customer_email)
        
        if not order_info:
            return jsonify({"error": "Pedido no encontrado"}), 404
        
        predictions = chatbot.predict_order_problems(order_info)
        
        return jsonify({
            "order_id": order_id,
            "predictions": predictions,
            "predictions_count": len(predictions),
            "high_risk_predictions": [p for p in predictions if p['probability'] > 0.6]
        }), 200
    
    except Exception as e:
        logger.error(f"Error obteniendo predicciones: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/feedback', methods=['POST'])
@rate_limit
def add_feedback():
    """
    Agrega feedback sobre una respuesta del chatbot
    
    Body:
    {
        "order_id": "ORD-2024-001234",
        "feedback_type": "positive|negative|helpful|not_helpful",
        "comment": "Comentario opcional",
        "customer_email": "cliente@example.com"
    }
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        data = request.get_json()
        
        order_id = data.get('order_id')
        feedback_type = data.get('feedback_type')
        comment = data.get('comment')
        customer_email = data.get('customer_email')
        
        if not order_id or not feedback_type:
            return jsonify({"error": "order_id y feedback_type son requeridos"}), 400
        
        valid_types = ['positive', 'negative', 'helpful', 'not_helpful']
        if feedback_type not in valid_types:
            return jsonify({
                "error": f"feedback_type debe ser uno de: {', '.join(valid_types)}"
            }), 400
        
        success = chatbot.add_feedback(order_id, feedback_type, comment, customer_email)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Feedback guardado correctamente"
            }), 200
        else:
            return jsonify({"error": "Error guardando feedback"}), 500
    
    except Exception as e:
        logger.error(f"Error agregando feedback: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/feedback/stats', methods=['GET'])
@rate_limit
def get_feedback_stats():
    """
    Obtiene estadísticas de feedback
    
    Query params:
    - order_id: ID del pedido (opcional, si no se proporciona retorna global)
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        order_id = request.args.get('order_id')
        stats = chatbot.get_feedback_stats(order_id)
        
        return jsonify(stats), 200
    
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de feedback: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/trends', methods=['GET'])
@rate_limit
def get_trends():
    """
    Obtiene análisis de tendencias
    
    Query params:
    - days: Número de días a analizar (default: 7)
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        days = int(request.args.get('days', 7))
        trends = chatbot.analyze_trends(days)
        
        return jsonify(trends), 200
    
    except Exception as e:
        logger.error(f"Error obteniendo tendencias: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/alerts/proactive', methods=['GET'])
@require_auth
def get_proactive_alerts():
    """
    Obtiene alertas proactivas que deben enviarse
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        alerts = chatbot.check_proactive_alerts()
        
        return jsonify({
            "alerts": alerts,
            "alerts_count": len(alerts),
            "high_priority": len([a for a in alerts if a['severity'] == 'high'])
        }), 200
    
    except Exception as e:
        logger.error(f"Error obteniendo alertas proactivas: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/export', methods=['GET'])
@require_auth
def export_data():
    """
    Exporta datos del chatbot
    
    Query params:
    - format: Formato ('json' o 'csv', default: 'json')
    - include_feedback: Incluir feedback (default: true)
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        export_format = request.args.get('format', 'json')
        include_feedback = request.args.get('include_feedback', 'true').lower() == 'true'
        
        file_path = chatbot.export_data(export_format, include_feedback)
        
        return jsonify({
            "success": True,
            "file_path": file_path,
            "format": export_format
        }), 200
    
    except Exception as e:
        logger.error(f"Error exportando datos: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/language', methods=['POST'])
@rate_limit
def set_language():
    """
    Establece el idioma del chatbot
    
    Body:
    {
        "language": "es|en|pt|fr"
    }
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        data = request.get_json()
        language = data.get('language', 'es')
        
        chatbot.set_language(language)
        
        return jsonify({
            "success": True,
            "language": language,
            "language_name": chatbot.supported_languages.get(language, 'unknown')
        }), 200
    
    except Exception as e:
        logger.error(f"Error estableciendo idioma: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/dashboard', methods=['GET'])
@rate_limit
def get_dashboard():
    """
    Obtiene datos completos del dashboard
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        dashboard_data = chatbot.get_dashboard_data()
        return jsonify(dashboard_data), 200
    
    except Exception as e:
        logger.error(f"Error obteniendo dashboard: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/nps', methods=['POST'])
@rate_limit
def record_nps():
    """
    Registra un score NPS
    
    Body:
    {
        "order_id": "ORD-2024-001234",
        "score": 9,
        "comment": "Excelente servicio",
        "customer_email": "cliente@example.com"
    }
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        data = request.get_json()
        
        order_id = data.get('order_id')
        score = data.get('score')
        comment = data.get('comment')
        customer_email = data.get('customer_email')
        
        if not order_id or score is None:
            return jsonify({"error": "order_id y score son requeridos"}), 400
        
        if not (0 <= score <= 10):
            return jsonify({"error": "score debe estar entre 0 y 10"}), 400
        
        success = chatbot.record_nps_score(order_id, score, comment, customer_email)
        
        if success:
            return jsonify({
                "success": True,
                "message": "NPS score registrado correctamente"
            }), 200
        else:
            return jsonify({"error": "Error registrando NPS score"}), 500
    
    except Exception as e:
        logger.error(f"Error registrando NPS: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/nps/analysis', methods=['GET'])
@rate_limit
def get_nps_analysis():
    """
    Obtiene análisis NPS
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        analysis = chatbot.get_nps_analysis()
        return jsonify(analysis), 200
    
    except Exception as e:
        logger.error(f"Error obteniendo análisis NPS: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/ab-test', methods=['POST'])
@require_auth
def create_ab_test():
    """
    Crea un test A/B
    
    Body:
    {
        "test_id": "test_response_style",
        "test_name": "Test de Estilo de Respuesta",
        "variants": [
            {"id": "variant_0", "name": "Estilo Amigable", "config": {...}},
            {"id": "variant_1", "name": "Estilo Profesional", "config": {...}}
        ],
        "traffic_split": {"variant_0": 0.5, "variant_1": 0.5}
    }
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        data = request.get_json()
        
        test_id = data.get('test_id')
        test_name = data.get('test_name')
        variants = data.get('variants')
        traffic_split = data.get('traffic_split')
        
        if not test_id or not test_name or not variants:
            return jsonify({"error": "test_id, test_name y variants son requeridos"}), 400
        
        success = chatbot.create_ab_test(test_id, test_name, variants, traffic_split)
        
        if success:
            return jsonify({
                "success": True,
                "test_id": test_id,
                "message": "Test A/B creado correctamente"
            }), 200
        else:
            return jsonify({"error": "Error creando test A/B"}), 500
    
    except Exception as e:
        logger.error(f"Error creando test A/B: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/ab-test/<test_id>/results', methods=['GET'])
@require_auth
def get_ab_test_results(test_id: str):
    """
    Obtiene resultados de un test A/B
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        results = chatbot.get_ab_test_results(test_id)
        return jsonify(results), 200
    
    except Exception as e:
        logger.error(f"Error obteniendo resultados de test A/B: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/roi', methods=['GET'])
@rate_limit
def get_roi():
    """
    Obtiene análisis de ROI del chatbot
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        roi = chatbot.calculate_roi()
        return jsonify(roi), 200
    
    except Exception as e:
        logger.error(f"Error calculando ROI: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/reports/generate', methods=['POST'])
@require_auth
def generate_report():
    """
    Genera un reporte automático
    
    Body:
    {
        "report_type": "daily|weekly|monthly"
    }
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        data = request.get_json() or {}
        report_type = data.get('report_type', 'daily')
        
        report = chatbot.generate_auto_report(report_type)
        
        return jsonify(report), 200
    
    except Exception as e:
        logger.error(f"Error generando reporte: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/reports/history', methods=['GET'])
@require_auth
def get_report_history():
    """
    Obtiene historial de reportes generados
    
    Query params:
    - limit: Número de reportes a retornar (default: 10)
    - report_type: Filtrar por tipo (opcional)
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        limit = int(request.args.get('limit', 10))
        report_type = request.args.get('report_type')
        
        history = chatbot.report_history
        
        if report_type:
            history = [r for r in history if r.get('report_type') == report_type]
        
        # Ordenar por fecha (más recientes primero)
        history.sort(key=lambda x: x.get('generated_at', ''), reverse=True)
        
        return jsonify({
            'reports': history[:limit],
            'total': len(history)
        }), 200
    
    except Exception as e:
        logger.error(f"Error obteniendo historial de reportes: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/troubleshooting/start', methods=['POST'])
@rate_limit
def start_troubleshooting():
    """
    Inicia una sesión de troubleshooting guiado
    
    Body:
    {
        "problem_description": "Mi pedido tiene retraso",
        "order_id": "ORD-2024-001234",
        "customer_email": "cliente@example.com",
        "ticket_id": "TICKET-123"  # Opcional
    }
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        data = request.get_json()
        
        problem_description = data.get('problem_description')
        if not problem_description:
            return jsonify({"error": "problem_description es requerido"}), 400
        
        order_id = data.get('order_id')
        customer_email = data.get('customer_email')
        ticket_id = data.get('ticket_id')
        
        session = chatbot.start_troubleshooting_session(
            problem_description=problem_description,
            order_id=order_id,
            customer_email=customer_email,
            ticket_id=ticket_id
        )
        
        if not session:
            return jsonify({"error": "No se pudo iniciar la sesión de troubleshooting"}), 500
        
        # Obtener primer paso
        first_step = chatbot.get_troubleshooting_step(session.session_id)
        
        return jsonify({
            "success": True,
            "session_id": session.session_id,
            "problem_detected": session.detected_problem_id,
            "problem_title": session.guide.problem_title if session.guide else None,
            "total_steps": len(session.guide.steps) if session.guide else 0,
            "first_step": first_step
        }), 200
    
    except Exception as e:
        logger.error(f"Error iniciando troubleshooting: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/troubleshooting/<session_id>/step', methods=['GET'])
@rate_limit
def get_troubleshooting_step(session_id: str):
    """
    Obtiene el siguiente paso de troubleshooting o un paso específico
    
    Query params:
    - step_number: Número de paso específico (opcional)
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        step_number = request.args.get('step_number', type=int)
        step = chatbot.get_troubleshooting_step(session_id, step_number)
        
        if not step:
            return jsonify({"error": "Paso no encontrado o sesión inválida"}), 404
        
        return jsonify(step), 200
    
    except Exception as e:
        logger.error(f"Error obteniendo paso de troubleshooting: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/troubleshooting/<session_id>/step', methods=['POST'])
@rate_limit
def complete_troubleshooting_step(session_id: str):
    """
    Completa un paso de troubleshooting
    
    Body:
    {
        "step_number": 1,
        "success": true,
        "notes": "Paso completado exitosamente",
        "user_response": "Sí, vi la actualización"
    }
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        data = request.get_json()
        
        step_number = data.get('step_number')
        success = data.get('success')
        notes = data.get('notes')
        user_response = data.get('user_response')
        
        if step_number is None or success is None:
            return jsonify({"error": "step_number y success son requeridos"}), 400
        
        result = chatbot.complete_troubleshooting_step(
            session_id=session_id,
            step_number=step_number,
            success=success,
            notes=notes,
            user_response=user_response
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error completando paso de troubleshooting: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/troubleshooting/<session_id>', methods=['GET'])
@rate_limit
def get_troubleshooting_session(session_id: str):
    """
    Obtiene información de una sesión de troubleshooting
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        session = chatbot.get_troubleshooting_session(session_id)
        
        if not session:
            return jsonify({"error": "Sesión no encontrada"}), 404
        
        return jsonify(session), 200
    
    except Exception as e:
        logger.error(f"Error obteniendo sesión de troubleshooting: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/troubleshooting/similar', methods=['GET'])
@rate_limit
def find_similar_problems():
    """
    Encuentra problemas similares basándose en descripciones anteriores
    
    Query params:
    - problem_description: Descripción del problema
    - limit: Número máximo de resultados (default: 5)
    """
    if not chatbot:
        return jsonify({"error": "Chatbot no inicializado"}), 500
    
    try:
        problem_description = request.args.get('problem_description')
        if not problem_description:
            return jsonify({"error": "problem_description es requerido"}), 400
        
        limit = int(request.args.get('limit', 5))
        
        similar = chatbot.find_similar_problems(problem_description, limit)
        
        return jsonify({
            "similar_problems": similar,
            "count": len(similar)
        }), 200
    
    except Exception as e:
        logger.error(f"Error buscando problemas similares: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/orders/<order_id>/subscribe', methods=['POST'])
@rate_limit
def subscribe_to_updates(order_id: str):
    """
    Suscribe a un cliente para recibir notificaciones proactivas
    
    Body:
    {
        "customer_email": "cliente@example.com",
        "notification_types": ["status_update", "delivery", "delay"]
    }
    """
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión"}), 500
    
    try:
        data = request.get_json()
        customer_email = data.get('customer_email')
        notification_types = data.get('notification_types', ['status_update', 'delivery'])
        
        if not customer_email:
            return jsonify({"error": "customer_email requerido"}), 400
        
        # Verificar que el pedido existe y pertenece al cliente
        cursor = conn.cursor()
        query = """
            SELECT id FROM ecommerce_orders
            WHERE order_id = %s AND customer_email = %s
        """
        cursor.execute(query, (order_id, customer_email))
        order = cursor.fetchone()
        
        if not order:
            cursor.close()
            conn.close()
            return jsonify({"error": "Pedido no encontrado o no autorizado"}), 404
        
        # Aquí podrías guardar la suscripción en una tabla
        # Por ahora solo retornamos éxito
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "order_id": order_id,
            "subscribed": True,
            "notification_types": notification_types
        }), 200
    
    except Exception as e:
        logger.error(f"Error suscribiendo a actualizaciones: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.errorhandler(500)
def internal_error(error):
    """Manejo de errores 500"""
    logger.error(f"Error interno: {error}", exc_info=True)
    return jsonify({"error": "Error interno del servidor"}), 500


if __name__ == '__main__':
    # Inicializar chatbot antes de iniciar el servidor
    init_chatbot()
    
    if not chatbot:
        logger.error("No se pudo inicializar el chatbot. Verifica la configuración.")
        exit(1)
    
    logger.info(f"Iniciando servidor en puerto {PORT}")
    logger.info(f"Endpoints disponibles:")
    logger.info(f"  - POST /api/chat - Procesar mensaje")
    logger.info(f"  - GET /api/health - Health check")
    logger.info(f"  - GET /api/metrics - Métricas")
    logger.info(f"  - GET /api/order/<order_id> - Información de pedido")
    logger.info(f"  - GET /api/conversation/<id> - Historial de conversación")
    logger.info(f"  - GET /api/orders/search?customer_email=... - Buscar pedidos")
    logger.info(f"  - POST /api/webhook/carrier-update - Webhook para carriers")
    logger.info(f"  - POST /api/notifications/send - Enviar notificación proactiva")
    logger.info(f"  - GET /api/orders/<order_id>/problems - Detectar problemas en pedido")
    logger.info(f"  - GET /api/orders/<order_id>/predictions - Predicciones de problemas futuros")
    logger.info(f"  - GET /api/users/<email>/pattern - Patrón de comportamiento del usuario")
    logger.info(f"  - POST /api/feedback - Agregar feedback")
    logger.info(f"  - GET /api/feedback/stats - Estadísticas de feedback")
    logger.info(f"  - GET /api/trends - Análisis de tendencias")
    logger.info(f"  - GET /api/alerts/proactive - Alertas proactivas")
    logger.info(f"  - GET /api/export - Exportar datos")
    logger.info(f"  - POST /api/language - Establecer idioma")
    logger.info(f"  - GET /api/dashboard - Dashboard completo")
    logger.info(f"  - POST /api/nps - Registrar score NPS")
    logger.info(f"  - GET /api/nps/analysis - Análisis NPS")
    logger.info(f"  - POST /api/ab-test - Crear test A/B")
    logger.info(f"  - GET /api/ab-test/<test_id>/results - Resultados test A/B")
    logger.info(f"  - GET /api/roi - Análisis de ROI")
    logger.info(f"  - POST /api/reports/generate - Generar reporte automático")
    logger.info(f"  - GET /api/reports/history - Historial de reportes")
    logger.info(f"  - POST /api/orders/<order_id>/subscribe - Suscribirse a actualizaciones")
    logger.info(f"  - POST /api/troubleshooting/start - Iniciar sesión de troubleshooting")
    logger.info(f"  - GET /api/troubleshooting/<session_id>/step - Obtener paso de troubleshooting")
    logger.info(f"  - POST /api/troubleshooting/<session_id>/step - Completar paso de troubleshooting")
    logger.info(f"  - GET /api/troubleshooting/<session_id> - Obtener sesión de troubleshooting")
    logger.info(f"  - GET /api/troubleshooting/similar - Buscar problemas similares")
    
    app.run(host='0.0.0.0', port=PORT, debug=True)

