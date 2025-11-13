#!/usr/bin/env python3
"""
API REST Server para el Testimonial to Social Post Converter
Permite usar el sistema vía HTTP requests para integración fácil con n8n, webhooks, etc.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from functools import lru_cache

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
except ImportError:
    print("Error: Flask no está instalado. Instálalo con: pip install flask flask-cors")
    sys.exit(1)

try:
    from testimonial_to_social_post_v2 import TestimonialToSocialPostConverterV2
except ImportError:
    print("Error: testimonial_to_social_post_v2 no está disponible")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Permitir CORS para integraciones

# Inicializar el convertidor
converter = None

def init_converter():
    """Inicializa el convertidor con la API key"""
    global converter
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY no está configurada")
    converter = TestimonialToSocialPostConverterV2(openai_api_key=api_key)
    logger.info("Convertidor inicializado correctamente")

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return jsonify({
        "status": "healthy",
        "service": "testimonial-to-social-post-api",
        "version": "2.0",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/convert', methods=['POST'])
def convert_testimonial():
    """
    Convierte un testimonio en publicación para redes sociales
    
    Body JSON esperado:
    {
        "testimonial": "texto del testimonio",
        "target_audience": "problema/resultado buscado",
        "platform": "instagram|facebook|linkedin|twitter|tiktok|general",
        "tone": "cálido y profesional",
        "language": "es|en|pt|fr",
        "generate_hooks": true,
        "analyze_quality": true,
        "include_hashtags": true,
        "include_cta": true,
        "max_length": 1000
    }
    """
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        if not data or 'testimonial' not in data or 'target_audience' not in data:
            return jsonify({
                "error": "Campos requeridos: testimonial, target_audience"
            }), 400
        
        # Extraer parámetros
        testimonial = data['testimonial']
        target_audience = data['target_audience']
        platform = data.get('platform', 'general')
        tone = data.get('tone', 'cálido y profesional')
        language = data.get('language', 'es')
        generate_hooks = data.get('generate_hooks', False)
        analyze_quality = data.get('analyze_quality', True)
        include_hashtags = data.get('include_hashtags', True)
        include_cta = data.get('include_cta', True)
        max_length = data.get('max_length')
        
        logger.info(f"Convirtiendo testimonio para plataforma: {platform}")
        
        # Convertir
        result = converter.convert_testimonial(
            testimonial=testimonial,
            target_audience_problem=target_audience,
            platform=platform,
            tone=tone,
            language=language,
            generate_hooks=generate_hooks,
            analyze_quality=analyze_quality,
            include_hashtags=include_hashtags,
            include_call_to_action=include_cta,
            max_length=max_length
        )
        
        return jsonify({
            "success": True,
            "data": result
        }), 200
        
    except Exception as e:
        logger.error(f"Error al convertir testimonio: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/convert/batch', methods=['POST'])
def convert_batch():
    """
    Convierte múltiples testimonios en un solo request
    
    Body JSON esperado:
    {
        "testimonials": [
            {
                "testimonial": "...",
                "target_audience": "...",
                "platform": "..."
            },
            ...
        ],
        "default_options": {
            "tone": "...",
            "language": "..."
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'testimonials' not in data:
            return jsonify({
                "error": "Campo requerido: testimonials (array)"
            }), 400
        
        testimonials = data['testimonials']
        default_options = data.get('default_options', {})
        
        results = []
        errors = []
        
        for i, testimonial_data in enumerate(testimonials):
            try:
                result = converter.convert_testimonial(
                    testimonial=testimonial_data['testimonial'],
                    target_audience_problem=testimonial_data['target_audience'],
                    platform=testimonial_data.get('platform', default_options.get('platform', 'general')),
                    tone=testimonial_data.get('tone', default_options.get('tone', 'cálido y profesional')),
                    language=testimonial_data.get('language', default_options.get('language', 'es')),
                    generate_hooks=testimonial_data.get('generate_hooks', False),
                    analyze_quality=testimonial_data.get('analyze_quality', True)
                )
                results.append({
                    "index": i,
                    "success": True,
                    "data": result
                })
            except Exception as e:
                errors.append({
                    "index": i,
                    "error": str(e)
                })
        
        return jsonify({
            "success": True,
            "results": results,
            "errors": errors,
            "total": len(testimonials),
            "successful": len(results),
            "failed": len(errors)
        }), 200
        
    except Exception as e:
        logger.error(f"Error en conversión batch: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/variations', methods=['POST'])
def generate_variations():
    """
    Genera múltiples variaciones de un testimonio
    
    Body JSON esperado:
    {
        "testimonial": "...",
        "target_audience": "...",
        "platforms": ["instagram", "facebook"],
        "count": 3,
        "language": "es"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'testimonial' not in data or 'target_audience' not in data:
            return jsonify({
                "error": "Campos requeridos: testimonial, target_audience"
            }), 400
        
        variations = converter.generate_multiple_variations(
            testimonial=data['testimonial'],
            target_audience_problem=data['target_audience'],
            platforms=data.get('platforms', ['general']),
            count=data.get('count', 3),
            language=data.get('language', 'es')
        )
        
        return jsonify({
            "success": True,
            "variations": variations,
            "count": len(variations)
        }), 200
        
    except Exception as e:
        logger.error(f"Error al generar variaciones: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze_testimonial():
    """
    Solo analiza un testimonio sin generar publicación
    
    Body JSON esperado:
    {
        "testimonial": "..."
    }
    """
    try:
        from testimonial_to_social_post_v2 import TestimonialAnalyzer
        
        data = request.get_json()
        
        if not data or 'testimonial' not in data:
            return jsonify({
                "error": "Campo requerido: testimonial"
            }), 400
        
        analyzer = TestimonialAnalyzer()
        
        analysis = {
            "metrics": analyzer.extract_metrics(data['testimonial']),
            "sentiment": analyzer.analyze_sentiment(data['testimonial']),
            "readability": analyzer.calculate_readability(data['testimonial'])
        }
        
        return jsonify({
            "success": True,
            "analysis": analysis
        }), 200
        
    except Exception as e:
        logger.error(f"Error al analizar testimonio: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/platforms', methods=['GET'])
def get_platforms():
    """Obtiene información sobre las plataformas soportadas"""
    platforms_info = {
        "instagram": {
            "max_length": 2200,
            "hashtags_recommended": 5,
            "emoji_supported": True,
            "best_times": ["9:00", "13:00", "17:00", "21:00"]
        },
        "facebook": {
            "max_length": 5000,
            "hashtags_recommended": 3,
            "emoji_supported": True,
            "best_times": ["8:00", "13:00", "17:00"]
        },
        "linkedin": {
            "max_length": 3000,
            "hashtags_recommended": 5,
            "emoji_supported": False,
            "best_times": ["8:00", "12:00", "17:00"]
        },
        "twitter": {
            "max_length": 280,
            "hashtags_recommended": 2,
            "emoji_supported": True,
            "best_times": ["8:00", "12:00", "17:00", "21:00"]
        },
        "tiktok": {
            "max_length": 300,
            "hashtags_recommended": 5,
            "emoji_supported": True,
            "best_times": ["9:00", "12:00", "19:00", "21:00"]
        },
        "general": {
            "max_length": 1000,
            "hashtags_recommended": 5,
            "emoji_supported": True,
            "best_times": ["9:00", "13:00", "17:00"]
        }
    }
    
    return jsonify({
        "success": True,
        "platforms": platforms_info
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint no encontrado",
        "available_endpoints": [
            "/health",
            "/convert",
            "/convert/batch",
            "/variations",
            "/analyze",
            "/platforms"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Error interno del servidor",
        "message": str(error)
    }), 500

def main():
    """Función principal para ejecutar el servidor"""
    import argparse
    
    parser = argparse.ArgumentParser(description="API Server para Testimonial to Social Post Converter")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host para el servidor (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Puerto para el servidor (default: 5000)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Modo debug"
    )
    
    args = parser.parse_args()
    
    # Inicializar convertidor
    try:
        init_converter()
    except Exception as e:
        logger.error(f"Error al inicializar convertidor: {e}")
        sys.exit(1)
    
    logger.info(f"Iniciando servidor en http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()


