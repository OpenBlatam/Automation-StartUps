#!/usr/bin/env python3
"""
API REST Flask para convertir testimonios en publicaciones para redes sociales
Permite integración fácil con n8n y otros sistemas
"""

import os
import sys
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# Agregar el directorio del script al path para importar el módulo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from testimonial_to_social_post import TestimonialToSocialPostConverter
except ImportError:
    print("Error: No se pudo importar TestimonialToSocialPostConverter")
    print("Asegúrate de que testimonial_to_social_post.py esté en el mismo directorio")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Permitir CORS para integraciones


@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return jsonify({
        "status": "healthy",
        "service": "testimonial-to-social-post-api"
    }), 200


@app.route('/convert', methods=['POST'])
def convert_testimonial():
    """
    Convierte un testimonio en una publicación para redes sociales
    
    Body JSON esperado:
    {
        "testimonial": "Texto del testimonio",
        "target_audience": "Problema/resultado buscado",
        "platform": "instagram|facebook|linkedin|twitter|tiktok|general",
        "tone": "cálido y profesional",
        "max_length": 1000,
        "include_hashtags": true,
        "include_call_to_action": true,
        "model": "gpt-4o-mini"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No se proporcionó JSON en el body"
            }), 400
        
        # Validar campos requeridos
        testimonial = data.get('testimonial') or data.get('testimonio') or data.get('text')
        target_audience = (
            data.get('target_audience') or 
            data.get('target_audience_problem') or
            data.get('problema_resultado') or
            data.get('problema') or
            data.get('resultado')
        )
        
        if not testimonial:
            return jsonify({
                "success": False,
                "error": "Campo 'testimonial' es requerido"
            }), 400
        
        if not target_audience:
            return jsonify({
                "success": False,
                "error": "Campo 'target_audience' es requerido"
            }), 400
        
        # Obtener parámetros opcionales
        platform = data.get('platform', 'general')
        tone = data.get('tone', 'cálido y profesional')
        max_length = data.get('max_length')
        include_hashtags = data.get('include_hashtags', True)
        include_call_to_action = data.get('include_call_to_action', True)
        model = data.get('model', 'gpt-4o-mini')
        api_key = data.get('api_key') or os.getenv('OPENAI_API_KEY')
        
        logger.info(f"Convirtiendo testimonio para plataforma: {platform}")
        
        # Crear convertidor
        converter = TestimonialToSocialPostConverter(
            openai_api_key=api_key,
            model=model
        )
        
        # Convertir testimonio
        result = converter.convert_testimonial(
            testimonial=testimonial,
            target_audience_problem=target_audience,
            platform=platform,
            tone=tone,
            max_length=max_length,
            include_hashtags=include_hashtags,
            include_call_to_action=include_call_to_action
        )
        
        return jsonify({
            "success": True,
            **result
        }), 200
        
    except ValueError as e:
        logger.error(f"Error de validación: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error al procesar solicitud: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/variations', methods=['POST'])
def generate_variations():
    """
    Genera múltiples variaciones de una publicación
    
    Body JSON esperado:
    {
        "testimonial": "Texto del testimonio",
        "target_audience": "Problema/resultado buscado",
        "platform": "instagram",
        "count": 3,
        "model": "gpt-4o-mini"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No se proporcionó JSON en el body"
            }), 400
        
        testimonial = data.get('testimonial') or data.get('testimonio')
        target_audience = (
            data.get('target_audience') or 
            data.get('target_audience_problem') or
            data.get('problema_resultado')
        )
        
        if not testimonial or not target_audience:
            return jsonify({
                "success": False,
                "error": "Campos 'testimonial' y 'target_audience' son requeridos"
            }), 400
        
        platform = data.get('platform', 'general')
        count = data.get('count', 3)
        model = data.get('model', 'gpt-4o-mini')
        api_key = data.get('api_key') or os.getenv('OPENAI_API_KEY')
        
        converter = TestimonialToSocialPostConverter(
            openai_api_key=api_key,
            model=model
        )
        
        variations = converter.generate_multiple_variations(
            testimonial=testimonial,
            target_audience_problem=target_audience,
            platforms=[platform],
            count=count
        )
        
        return jsonify({
            "success": True,
            "variations": variations,
            "count": len(variations)
        }), 200
        
    except Exception as e:
        logger.error(f"Error al generar variaciones: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint no encontrado"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Error interno del servidor"
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Iniciando servidor en {host}:{port}")
    app.run(host=host, port=port, debug=debug)



