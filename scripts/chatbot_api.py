#!/usr/bin/env python3
"""
API REST para los Chatbots
Proporciona endpoints HTTP para integrar los chatbots en aplicaciones web
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from typing import Optional
import logging

# Intentar importar Flask, si no está disponible, crear una versión básica
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask no está instalado. Instala con: pip install flask flask-cors")

if FLASK_AVAILABLE:
    from chatbot_curso_ia_webinars import CursoIAWebinarChatbot
    from chatbot_saas_ia_marketing import SaaSIAMarketingChatbot
    from chatbot_ia_bulk_documentos import IABulkDocumentosChatbot
    
    app = Flask(__name__)
    CORS(app)  # Permitir CORS para desarrollo
    
    # Inicializar chatbots
    chatbots = {
        "curso_ia": CursoIAWebinarChatbot(
            enable_logging=True,
            persist_conversations=True,
            enable_rate_limiting=True,
            enable_feedback=True
        ),
        "saas_marketing": SaaSIAMarketingChatbot(
            enable_logging=True,
            persist_conversations=True
        ),
        "ia_bulk": IABulkDocumentosChatbot(
            enable_logging=True,
            persist_conversations=True
        )
    }
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "chatbots_available": list(chatbots.keys())
        }), 200
    
    
    @app.route('/api/<chatbot_id>/message', methods=['POST'])
    def process_message(chatbot_id: str):
        """
        Procesa un mensaje en el chatbot especificado.
        
        Body:
        {
            "message": "texto del mensaje",
            "conversation_id": "opcional",
            "user_id": "opcional",
            "conversation_history": []
        }
        """
        if chatbot_id not in chatbots:
            return jsonify({
                "error": f"Chatbot '{chatbot_id}' no encontrado",
                "available": list(chatbots.keys())
            }), 404
        
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Campo 'message' requerido"}), 400
        
        chatbot = chatbots[chatbot_id]
        
        try:
            response = chatbot.process_message(
                user_message=data['message'],
                conversation_history=data.get('conversation_history'),
                conversation_id=data.get('conversation_id'),
                user_id=data.get('user_id')
            )
            
            return jsonify(response), 200
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            return jsonify({"error": str(e)}), 500
    
    
    @app.route('/api/<chatbot_id>/metrics', methods=['GET'])
    def get_metrics(chatbot_id: str):
        """Obtiene métricas del chatbot"""
        if chatbot_id not in chatbots:
            return jsonify({"error": f"Chatbot '{chatbot_id}' no encontrado"}), 404
        
        chatbot = chatbots[chatbot_id]
        metrics = chatbot.get_metrics()
        
        return jsonify(metrics), 200
    
    
    @app.route('/api/<chatbot_id>/health', methods=['GET'])
    def chatbot_health(chatbot_id: str):
        """Health check del chatbot específico"""
        if chatbot_id not in chatbots:
            return jsonify({"error": f"Chatbot '{chatbot_id}' no encontrado"}), 404
        
        chatbot = chatbots[chatbot_id]
        health = chatbot.health_check()
        
        return jsonify(health), 200
    
    
    @app.route('/api/<chatbot_id>/feedback', methods=['POST'])
    def add_feedback(chatbot_id: str):
        """
        Agrega feedback sobre una respuesta.
        
        Body:
        {
            "conversation_id": "required",
            "message_id": "required",
            "feedback_type": "positive|negative|helpful|not_helpful",
            "comment": "opcional",
            "user_id": "opcional"
        }
        """
        if chatbot_id not in chatbots:
            return jsonify({"error": f"Chatbot '{chatbot_id}' no encontrado"}), 404
        
        data = request.get_json()
        required_fields = ['conversation_id', 'message_id', 'feedback_type']
        
        if not all(field in data for field in required_fields):
            return jsonify({
                "error": f"Campos requeridos: {', '.join(required_fields)}"
            }), 400
        
        chatbot = chatbots[chatbot_id]
        
        success = chatbot.add_feedback(
            conversation_id=data['conversation_id'],
            message_id=data['message_id'],
            feedback_type=data['feedback_type'],
            comment=data.get('comment'),
            user_id=data.get('user_id')
        )
        
        if success:
            return jsonify({"success": True, "message": "Feedback agregado"}), 200
        else:
            return jsonify({"error": "No se pudo agregar feedback"}), 500
    
    
    @app.route('/api/<chatbot_id>/trends', methods=['GET'])
    def get_trends(chatbot_id: str):
        """Obtiene análisis de tendencias"""
        if chatbot_id not in chatbots:
            return jsonify({"error": f"Chatbot '{chatbot_id}' no encontrado"}), 404
        
        chatbot = chatbots[chatbot_id]
        days = request.args.get('days', 7, type=int)
        
        trends = chatbot.get_trends(days=days)
        return jsonify(trends), 200
    
    
    @app.route('/api/<chatbot_id>/suggestions', methods=['GET'])
    def get_suggestions(chatbot_id: str):
        """Obtiene sugerencias de IA"""
        if chatbot_id not in chatbots:
            return jsonify({"error": f"Chatbot '{chatbot_id}' no encontrado"}), 404
        
        chatbot = chatbots[chatbot_id]
        suggestions = chatbot.get_ai_suggestions()
        
        return jsonify({"suggestions": suggestions}), 200
    
    
    @app.route('/api/<chatbot_id>/export-metrics', methods=['POST'])
    def export_metrics(chatbot_id: str):
        """Exporta métricas a archivo"""
        if chatbot_id not in chatbots:
            return jsonify({"error": f"Chatbot '{chatbot_id}' no encontrado"}), 404
        
        data = request.get_json() or {}
        format_type = data.get('format', 'json')
        
        chatbot = chatbots[chatbot_id]
        output_file = chatbot.export_metrics(format=format_type)
        
        return jsonify({
            "success": True,
            "file": output_file,
            "message": f"Métricas exportadas a {output_file}"
        }), 200
    
    
    @app.route('/api/<chatbot_id>/conversation/<conversation_id>', methods=['GET'])
    def get_conversation_summary(chatbot_id: str, conversation_id: str):
        """Obtiene resumen de una conversación"""
        if chatbot_id not in chatbots:
            return jsonify({"error": f"Chatbot '{chatbot_id}' no encontrado"}), 404
        
        chatbot = chatbots[chatbot_id]
        summary = chatbot.get_conversation_summary(conversation_id)
        
        if summary:
            return jsonify(summary), 200
        else:
            return jsonify({"error": "Conversación no encontrada"}), 404
    
    
    @app.route('/api/docs', methods=['GET'])
    def api_docs():
        """Documentación de la API"""
        docs = {
            "version": "1.0",
            "endpoints": {
                "GET /health": "Health check general",
                "POST /api/<chatbot_id>/message": "Procesar mensaje",
                "GET /api/<chatbot_id>/metrics": "Obtener métricas",
                "GET /api/<chatbot_id>/health": "Health check del chatbot",
                "POST /api/<chatbot_id>/feedback": "Agregar feedback",
                "GET /api/<chatbot_id>/trends?days=7": "Obtener tendencias",
                "GET /api/<chatbot_id>/suggestions": "Obtener sugerencias",
                "POST /api/<chatbot_id>/export-metrics": "Exportar métricas",
                "GET /api/<chatbot_id>/conversation/<id>": "Resumen de conversación"
            },
            "chatbots_available": list(chatbots.keys()),
            "example_request": {
                "url": "/api/curso_ia/message",
                "method": "POST",
                "body": {
                    "message": "¿Cuánto cuesta el curso?",
                    "user_id": "user123"
                }
            }
        }
        return jsonify(docs), 200
    
    
    if __name__ == '__main__':
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('DEBUG', 'False').lower() == 'true'
        
        print(f"""
    🤖 Chatbot API Server
    ====================
    Disponible en: http://localhost:{port}
    Documentación: http://localhost:{port}/api/docs
    Health Check: http://localhost:{port}/health
    
    Chatbots disponibles:
    - curso_ia
    - saas_marketing
    - ia_bulk
        """)
        
        app.run(host='0.0.0.0', port=port, debug=debug)
else:
    print("""
    ⚠️  Flask no está disponible
    
    Para usar la API REST, instala las dependencias:
    
    pip install flask flask-cors
    
    Luego ejecuta:
    python scripts/chatbot_api.py
    """)






