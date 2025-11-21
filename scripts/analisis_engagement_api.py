#!/usr/bin/env python3
"""
API REST para Análisis de Engagement
=====================================
Proporciona acceso programático al sistema de análisis de engagement
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
except ImportError:
    print("Error: Flask no está instalado. Instálalo con: pip install flask flask-cors")
    sys.exit(1)

try:
    from analisis_engagement_contenido import AnalizadorEngagement, Publicacion
    from analisis_engagement_ai import AnalizadorEngagementAI
except ImportError:
    print("Error: Módulos de análisis no encontrados")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Instancias globales
analizador_base = None
analizador_ai = None


def init_analizadores():
    """Inicializa los analizadores"""
    global analizador_base, analizador_ai
    
    analizador_base = AnalizadorEngagement()
    analizador_ai = AnalizadorEngagementAI(analizador_base)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "engagement-analysis-api",
        "version": "2.0",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/analyze', methods=['POST'])
def analyze_engagement():
    """
    Analiza engagement de publicaciones
    
    Body JSON esperado:
    {
        "publicaciones": [
            {
                "id": "...",
                "tipo_contenido": "X|Y|Z",
                "titulo": "...",
                "plataforma": "...",
                "fecha_publicacion": "YYYY-MM-DD HH:MM:SS",
                "likes": 100,
                "comentarios": 10,
                "shares": 5,
                "impresiones": 1000,
                "reach": 800,
                "hashtags": ["#tag1", "#tag2"],
                "tiene_media": true
            }
        ],
        "options": {
            "use_ai": true,
            "compare_benchmarks": true,
            "generate_recommendations": true
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'publicaciones' not in data:
            return jsonify({"error": "Campo 'publicaciones' requerido"}), 400
        
        # Cargar publicaciones
        analizador_temp = AnalizadorEngagement()
        for pub_data in data['publicaciones']:
            pub = Publicacion(
                id=pub_data.get('id', f"post_{datetime.now().timestamp()}"),
                tipo_contenido=pub_data.get('tipo_contenido', 'Z'),
                titulo=pub_data.get('titulo', ''),
                plataforma=pub_data.get('plataforma', 'Instagram'),
                fecha_publicacion=datetime.fromisoformat(pub_data['fecha_publicacion'].replace('Z', '+00:00')) if isinstance(pub_data.get('fecha_publicacion'), str) else datetime.now(),
                likes=pub_data.get('likes', 0),
                comentarios=pub_data.get('comentarios', 0),
                shares=pub_data.get('shares', 0),
                impresiones=pub_data.get('impresiones', 0),
                reach=pub_data.get('reach', 0),
                hashtags=pub_data.get('hashtags', []),
                tiene_media=pub_data.get('tiene_media', False),
                metadata=pub_data.get('metadata', {})
            )
            analizador_temp.publicaciones.append(pub)
        
        # Generar reporte
        reporte = analizador_temp.generar_reporte()
        
        resultado = {
            "success": True,
            "reporte": reporte,
            "timestamp": datetime.now().isoformat()
        }
        
        # Análisis con IA si está habilitado
        options = data.get('options', {})
        if options.get('use_ai', False):
            analizador_ai_temp = AnalizadorEngagementAI(analizador_temp)
            analisis_ia = analizador_ai_temp.analizar_con_ia(reporte)
            resultado["analisis_ia"] = analisis_ia
        
        # Comparación con benchmarks
        if options.get('compare_benchmarks', False):
            analizador_ai_temp = AnalizadorEngagementAI(analizador_temp)
            benchmarks = analizador_ai_temp.comparar_con_benchmarks(reporte)
            resultado["benchmarks"] = benchmarks
        
        # Recomendaciones
        if options.get('generate_recommendations', False):
            analizador_ai_temp = AnalizadorEngagementAI(analizador_temp)
            recomendaciones = analizador_ai_temp.generar_recomendaciones_inteligentes(reporte)
            resultado["recomendaciones"] = recomendaciones
        
        return jsonify(resultado), 200
        
    except Exception as e:
        logger.error(f"Error en análisis: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/predict', methods=['POST'])
def predict_engagement():
    """
    Predice engagement para una publicación futura
    
    Body JSON esperado:
    {
        "tipo": "X|Y|Z",
        "plataforma": "...",
        "hora": 10,
        "dia_semana": "Monday",
        "tiene_media": true,
        "num_hashtags": 5
    }
    """
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['tipo', 'plataforma', 'hora', 'dia_semana']):
            return jsonify({"error": "Campos requeridos: tipo, plataforma, hora, dia_semana"}), 400
        
        # Usar analizador base si hay datos
        if analizador_base and len(analizador_base.publicaciones) > 0:
            analizador_ai_temp = AnalizadorEngagementAI(analizador_base)
            prediccion = analizador_ai_temp.predecir_engagement_mejorado(
                tipo=data['tipo'],
                plataforma=data['plataforma'],
                hora=data['hora'],
                dia_semana=data['dia_semana'],
                tiene_media=data.get('tiene_media', True),
                num_hashtags=data.get('num_hashtags', 5)
            )
        else:
            # Predicción básica sin datos históricos
            return jsonify({
                "error": "Se necesitan datos históricos para predicción precisa. Use /analyze primero o cargue datos."
            }), 400
        
        return jsonify({
            "success": True,
            "prediccion": prediccion
        }), 200
        
    except Exception as e:
        logger.error(f"Error en predicción: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/load-sample', methods=['POST'])
def load_sample_data():
    """
    Carga datos de ejemplo para análisis
    
    Body JSON opcional:
    {
        "num_publicaciones": 30
    }
    """
    try:
        data = request.get_json() or {}
        num_pubs = data.get('num_publicaciones', 30)
        
        global analizador_base, analizador_ai
        
        analizador_base = AnalizadorEngagement()
        analizador_base.generar_datos_ejemplo(num_publicaciones=num_pubs)
        analizador_ai = AnalizadorEngagementAI(analizador_base)
        
        return jsonify({
            "success": True,
            "publicaciones_cargadas": len(analizador_base.publicaciones),
            "message": f"{num_pubs} publicaciones de ejemplo cargadas"
        }), 200
        
    except Exception as e:
        logger.error(f"Error cargando datos: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/report', methods=['GET'])
def get_report():
    """Obtiene el reporte completo si hay datos cargados"""
    try:
        if not analizador_base or len(analizador_base.publicaciones) == 0:
            return jsonify({
                "error": "No hay datos cargados. Use /load-sample o /analyze primero."
            }), 400
        
        reporte = analizador_base.generar_reporte()
        
        resultado = {
            "success": True,
            "reporte": reporte
        }
        
        # Agregar análisis con IA si está disponible
        if analizador_ai and analizador_ai.client:
            analisis_ia = analizador_ai.analizar_con_ia(reporte)
            resultado["analisis_ia"] = analisis_ia
            
            benchmarks = analizador_ai.comparar_con_benchmarks(reporte)
            resultado["benchmarks"] = benchmarks
            
            recomendaciones = analizador_ai.generar_recomendaciones_inteligentes(reporte)
            resultado["recomendaciones"] = recomendaciones
        
        return jsonify(resultado), 200
        
    except Exception as e:
        logger.error(f"Error generando reporte: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='API REST para Análisis de Engagement')
    parser.add_argument('--host', default='0.0.0.0', help='Host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5001, help='Puerto (default: 5001)')
    parser.add_argument('--debug', action='store_true', help='Modo debug')
    parser.add_argument('--load-sample', action='store_true', help='Cargar datos de ejemplo al inicio')
    
    args = parser.parse_args()
    
    # Inicializar analizadores
    init_analizadores()
    
    # Cargar datos de ejemplo si se solicita
    if args.load_sample:
        analizador_base.generar_datos_ejemplo(num_publicaciones=30)
        logger.info(f"Cargadas {len(analizador_base.publicaciones)} publicaciones de ejemplo")
    
    logger.info(f"Iniciando servidor en http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()



