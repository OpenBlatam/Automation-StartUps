"""
API REST para integración del Chatbot
Versión: 2.0.0
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from typing import Dict
import logging
from chatbot_engine import (
    ChatbotEngine, ChatMessage, Channel, Language, 
    Sentiment, Intent
)

app = Flask(__name__)
CORS(app)  # Permitir CORS para integraciones web

logger = logging.getLogger(__name__)

# Instancia global del chatbot
chatbot = ChatbotEngine()


@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de salud del servicio"""
    return jsonify({
        "status": "healthy",
        "service": "chatbot-api",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/v1/chat', methods=['POST'])
def chat():
    """
    Endpoint principal para procesar mensajes del chatbot
    
    Body esperado:
    {
        "user_id": "string",
        "message": "string",
        "channel": "web|whatsapp|email|telegram",
        "language": "es|en|pt|fr" (opcional),
        "session_id": "string" (opcional)
    }
    """
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data or 'user_id' not in data or 'message' not in data:
            return jsonify({
                "error": "Missing required fields: user_id, message"
            }), 400
        
        # Mapear canal
        channel_map = {
            "web": Channel.WEB,
            "whatsapp": Channel.WHATSAPP,
            "email": Channel.EMAIL,
            "telegram": Channel.TELEGRAM,
            "intercom": Channel.INTERCOM
        }
        
        channel_str = data.get("channel", "web").lower()
        channel = channel_map.get(channel_str, Channel.WEB)
        
        # Mapear idioma
        language_map = {
            "es": Language.ES,
            "en": Language.EN,
            "pt": Language.PT,
            "fr": Language.FR
        }
        
        language_str = data.get("language", "").lower()
        language = language_map.get(language_str) if language_str else None
        
        # Crear mensaje
        chat_message = ChatMessage(
            user_id=data["user_id"],
            message=data["message"],
            timestamp=datetime.now(),
            channel=channel,
            language=language,
            session_id=data.get("session_id", "")
        )
        
        # Procesar mensaje (async en producción)
        import asyncio
        response = asyncio.run(chatbot.process_message(chat_message))
        
        # Preparar respuesta
        return jsonify({
            "success": True,
            "response": {
                "message": response.message,
                "confidence": response.confidence,
                "action": response.action,
                "ticket_id": response.ticket_id,
                "suggested_actions": response.suggested_actions,
                "sentiment": response.sentiment.value if response.sentiment else None,
                "intent": response.intent.value if response.intent else None,
                "ab_test_variant": response.ab_test_variant
            },
            "session_id": chat_message.session_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route('/api/v1/metrics', methods=['GET'])
def get_metrics():
    """Obtiene las métricas del chatbot"""
    try:
        metrics = chatbot.get_metrics()
        return jsonify({
            "success": True,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error obteniendo métricas: {e}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route('/api/v1/satisfaction', methods=['POST'])
def record_satisfaction():
    """
    Registra calificación de satisfacción
    
    Body esperado:
    {
        "session_id": "string",
        "score": 1-5 (int)
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'session_id' not in data or 'score' not in data:
            return jsonify({
                "error": "Missing required fields: session_id, score"
            }), 400
        
        score = int(data["score"])
        if not (1 <= score <= 5):
            return jsonify({
                "error": "Score must be between 1 and 5"
            }), 400
        
        chatbot.record_satisfaction(score, data["session_id"])
        
        return jsonify({
            "success": True,
            "message": "Satisfaction recorded",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error registrando satisfacción: {e}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route('/api/v1/conversations/<session_id>', methods=['GET'])
def get_conversation(session_id: str):
    """Obtiene el historial de una conversación"""
    try:
        if session_id not in chatbot.conversations:
            return jsonify({
                "error": "Conversation not found"
            }), 404
        
        conversation = chatbot.conversations[session_id]
        
        return jsonify({
            "success": True,
            "conversation": {
                "session_id": conversation.session_id,
                "user_id": conversation.user_id,
                "language": conversation.language.value,
                "created_at": conversation.created_at.isoformat(),
                "last_activity": conversation.last_activity.isoformat(),
                "message_count": len(conversation.messages),
                "messages": list(conversation.messages),
                "sentiment_history": [s.value for s in conversation.sentiment_history],
                "intents_history": [i.value for i in conversation.intents_history]
            }
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo conversación: {e}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route('/api/v1/faqs', methods=['GET'])
def get_faqs():
    """Obtiene las FAQs disponibles"""
    try:
        language = request.args.get('language', 'es')
        
        if language not in chatbot.faqs:
            return jsonify({
                "error": f"Language {language} not supported"
            }), 400
        
        return jsonify({
            "success": True,
            "language": language,
            "faqs": chatbot.faqs[language],
            "count": len(chatbot.faqs[language])
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo FAQs: {e}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


# Webhook para Zapier
@app.route('/api/v1/webhooks/zapier', methods=['POST'])
def zapier_webhook():
    """
    Webhook para integración con Zapier
    
    Recibe eventos del chatbot y los envía a Zapier
    """
    try:
        data = request.get_json()
        
        # Aquí se integraría con Zapier
        # Por ahora, solo logueamos el evento
        logger.info(f"Zapier webhook recibido: {data}")
        
        return jsonify({
            "success": True,
            "message": "Webhook processed",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error procesando webhook Zapier: {e}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    print("🚀 Iniciando API REST del Chatbot...")
    print("📡 Endpoints disponibles:")
    print("   POST /api/v1/chat - Procesar mensaje")
    print("   GET  /api/v1/metrics - Obtener métricas")
    print("   POST /api/v1/satisfaction - Registrar satisfacción")
    print("   GET  /api/v1/conversations/<session_id> - Obtener conversación")
    print("   GET  /api/v1/faqs - Obtener FAQs")
    print("   POST /api/v1/webhooks/zapier - Webhook Zapier")
    
    app.run(host='0.0.0.0', port=8000, debug=True)






