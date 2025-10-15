#!/usr/bin/env python3
"""
🌐 MARKETING BRAIN API
API REST para el Advanced Marketing Brain System
Endpoints para generación de conceptos y análisis de documentos
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime
import logging
from pathlib import Path
import sys

# Agregar el directorio actual al path para importar el sistema
sys.path.append(str(Path(__file__).parent))
from advanced_marketing_brain_system import AdvancedMarketingBrain, MarketingConcept

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask app
app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

# Inicializar el sistema de IA
brain_system = None

def initialize_brain_system():
    """Inicializar el sistema de IA"""
    global brain_system
    try:
        brain_system = AdvancedMarketingBrain()
        logger.info("✅ Advanced Marketing Brain System initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error initializing brain system: {str(e)}")
        return False

@app.route('/', methods=['GET'])
def home():
    """Endpoint principal - Información del API"""
    return jsonify({
        'message': '🧠 Advanced Marketing Brain API',
        'version': '1.0.0',
        'description': 'API REST para generación de conceptos de marketing con IA',
        'endpoints': {
            'GET /': 'Información del API',
            'GET /status': 'Estado del sistema',
            'GET /themes': 'Listar temas disponibles',
            'GET /campaigns': 'Listar campañas analizadas',
            'POST /concepts/generate': 'Generar conceptos de marketing',
            'POST /concepts/filter': 'Filtrar conceptos existentes',
            'POST /documents/analyze': 'Analizar documento y extraer insights',
            'POST /suggestions/generate': 'Generar sugerencias accionables',
            'GET /export/concepts': 'Exportar conceptos a JSON',
            'GET /export/suggestions': 'Exportar sugerencias a JSON'
        },
        'status': 'active' if brain_system else 'initializing'
    })

@app.route('/status', methods=['GET'])
def get_status():
    """Obtener estado del sistema"""
    if not brain_system:
        return jsonify({
            'status': 'error',
            'message': 'Sistema no inicializado'
        }), 500
    
    try:
        summary = brain_system.get_system_summary()
        return jsonify({
            'status': 'active',
            'system_summary': summary,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/themes', methods=['GET'])
def get_themes():
    """Obtener temas disponibles"""
    if not brain_system:
        return jsonify({
            'status': 'error',
            'message': 'Sistema no inicializado'
        }), 500
    
    try:
        themes_data = []
        for theme_name, theme_obj in brain_system.themes.items():
            themes_data.append({
                'name': theme_name,
                'frequency': theme_obj.frequency,
                'success_rate': theme_obj.success_rate,
                'avg_metrics': theme_obj.avg_metrics,
                'related_technologies': theme_obj.related_technologies,
                'related_channels': theme_obj.related_channels,
                'related_verticals': theme_obj.related_verticals
            })
        
        return jsonify({
            'status': 'success',
            'themes': themes_data,
            'total_themes': len(themes_data)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/campaigns', methods=['GET'])
def get_campaigns():
    """Obtener campañas analizadas"""
    if not brain_system:
        return jsonify({
            'status': 'error',
            'message': 'Sistema no inicializado'
        }), 500
    
    try:
        # Parámetros de consulta
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        min_success = request.args.get('min_success', 0.0, type=float)
        
        # Filtrar campañas
        filtered_campaigns = [
            campaign for campaign in brain_system.campaigns
            if campaign.get('success_probability', 0) >= min_success
        ]
        
        # Aplicar paginación
        total_campaigns = len(filtered_campaigns)
        paginated_campaigns = filtered_campaigns[offset:offset + limit]
        
        return jsonify({
            'status': 'success',
            'campaigns': paginated_campaigns,
            'pagination': {
                'total': total_campaigns,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_campaigns
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/concepts/generate', methods=['POST'])
def generate_concepts():
    """Generar conceptos de marketing frescos"""
    if not brain_system:
        return jsonify({
            'status': 'error',
            'message': 'Sistema no inicializado'
        }), 500
    
    try:
        # Obtener parámetros del request
        data = request.get_json() or {}
        
        num_concepts = data.get('num_concepts', 10)
        focus_theme = data.get('focus_theme')
        target_vertical = data.get('target_vertical')
        min_success_probability = data.get('min_success_probability', 0.7)
        
        # Validar parámetros
        if num_concepts < 1 or num_concepts > 100:
            return jsonify({
                'status': 'error',
                'message': 'num_concepts debe estar entre 1 y 100'
            }), 400
        
        if min_success_probability < 0 or min_success_probability > 1:
            return jsonify({
                'status': 'error',
                'message': 'min_success_probability debe estar entre 0 y 1'
            }), 400
        
        # Generar conceptos
        concepts = brain_system.generate_fresh_concepts(
            num_concepts=num_concepts,
            focus_theme=focus_theme,
            target_vertical=target_vertical,
            min_success_probability=min_success_probability
        )
        
        # Convertir conceptos a diccionarios
        concepts_data = []
        for concept in concepts:
            concept_dict = {
                'id': concept.concept_id,
                'name': concept.name,
                'description': concept.description,
                'category': concept.category,
                'technology': concept.technology,
                'channel': concept.channel,
                'vertical': concept.vertical,
                'objective': concept.objective,
                'inspiration_campaigns': concept.inspiration_campaigns,
                'success_probability': concept.success_probability,
                'complexity': concept.complexity,
                'priority': concept.priority,
                'budget': concept.estimated_budget,
                'timeline': concept.timeline,
                'metrics': concept.expected_metrics,
                'tags': concept.tags,
                'created_at': concept.created_at
            }
            concepts_data.append(concept_dict)
        
        return jsonify({
            'status': 'success',
            'concepts': concepts_data,
            'total_generated': len(concepts_data),
            'parameters': {
                'num_concepts': num_concepts,
                'focus_theme': focus_theme,
                'target_vertical': target_vertical,
                'min_success_probability': min_success_probability
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error generating concepts: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/concepts/filter', methods=['POST'])
def filter_concepts():
    """Filtrar conceptos existentes"""
    if not brain_system:
        return jsonify({
            'status': 'error',
            'message': 'Sistema no inicializado'
        }), 500
    
    try:
        data = request.get_json() or {}
        
        # Generar conceptos base
        num_concepts = data.get('num_concepts', 50)
        base_concepts = brain_system.generate_fresh_concepts(num_concepts=num_concepts)
        
        # Aplicar filtros
        filters = data.get('filters', {})
        filtered_concepts = []
        
        for concept in base_concepts:
            # Filtro por tema
            if 'theme' in filters and filters['theme'] and concept.category != filters['theme']:
                continue
            
            # Filtro por tecnología
            if 'technology' in filters and filters['technology'] and concept.technology != filters['technology']:
                continue
            
            # Filtro por canal
            if 'channel' in filters and filters['channel'] and concept.channel != filters['channel']:
                continue
            
            # Filtro por vertical
            if 'vertical' in filters and filters['vertical'] and concept.vertical != filters['vertical']:
                continue
            
            # Filtro por complejidad
            if 'complexity' in filters and filters['complexity'] and concept.complexity != filters['complexity']:
                continue
            
            # Filtro por prioridad
            if 'priority' in filters and filters['priority'] and concept.priority != filters['priority']:
                continue
            
            # Filtro por probabilidad de éxito
            min_success = filters.get('min_success_probability', 0.0)
            if concept.success_probability < min_success:
                continue
            
            # Filtro por presupuesto
            if 'max_budget' in filters and concept.estimated_budget['amount'] > filters['max_budget']:
                continue
            
            if 'min_budget' in filters and concept.estimated_budget['amount'] < filters['min_budget']:
                continue
            
            filtered_concepts.append(concept)
        
        # Convertir a diccionarios
        concepts_data = []
        for concept in filtered_concepts:
            concept_dict = {
                'id': concept.concept_id,
                'name': concept.name,
                'description': concept.description,
                'category': concept.category,
                'technology': concept.technology,
                'channel': concept.channel,
                'vertical': concept.vertical,
                'objective': concept.objective,
                'inspiration_campaigns': concept.inspiration_campaigns,
                'success_probability': concept.success_probability,
                'complexity': concept.complexity,
                'priority': concept.priority,
                'budget': concept.estimated_budget,
                'timeline': concept.timeline,
                'metrics': concept.expected_metrics,
                'tags': concept.tags,
                'created_at': concept.created_at
            }
            concepts_data.append(concept_dict)
        
        return jsonify({
            'status': 'success',
            'concepts': concepts_data,
            'total_filtered': len(concepts_data),
            'total_base': len(base_concepts),
            'filters_applied': filters,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error filtering concepts: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/documents/analyze', methods=['POST'])
def analyze_document():
    """Analizar documento y extraer insights"""
    if not brain_system:
        return jsonify({
            'status': 'error',
            'message': 'Sistema no inicializado'
        }), 500
    
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Se requiere el campo "content" en el JSON'
            }), 400
        
        document_content = data['content']
        
        if not document_content or len(document_content.strip()) < 50:
            return jsonify({
                'status': 'error',
                'message': 'El contenido del documento debe tener al menos 50 caracteres'
            }), 400
        
        # Analizar documento
        insights = brain_system.analyze_document_insights(document_content)
        
        return jsonify({
            'status': 'success',
            'insights': insights,
            'document_length': len(document_content),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/suggestions/generate', methods=['POST'])
def generate_suggestions():
    """Generar sugerencias accionables"""
    if not brain_system:
        return jsonify({
            'status': 'error',
            'message': 'Sistema no inicializado'
        }), 500
    
    try:
        data = request.get_json() or {}
        
        # Obtener insights del request o generar nuevos
        insights = data.get('insights')
        document_content = data.get('document_content')
        
        if not insights and not document_content:
            return jsonify({
                'status': 'error',
                'message': 'Se requiere "insights" o "document_content" en el JSON'
            }), 400
        
        # Si no hay insights pero hay contenido, analizar documento
        if not insights and document_content:
            insights = brain_system.analyze_document_insights(document_content)
        
        if not insights:
            return jsonify({
                'status': 'error',
                'message': 'No se pudieron extraer insights del documento'
            }), 400
        
        # Generar sugerencias
        num_suggestions = data.get('num_suggestions', 10)
        suggestions = brain_system.generate_actionable_marketing_suggestions(
            insights, num_suggestions=num_suggestions
        )
        
        return jsonify({
            'status': 'success',
            'suggestions': suggestions,
            'total_generated': len(suggestions),
            'insights_used': insights,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/export/concepts', methods=['GET'])
def export_concepts():
    """Exportar conceptos a JSON"""
    if not brain_system:
        return jsonify({
            'status': 'error',
            'message': 'Sistema no inicializado'
        }), 500
    
    try:
        # Parámetros de consulta
        num_concepts = request.args.get('num_concepts', 20, type=int)
        focus_theme = request.args.get('focus_theme')
        target_vertical = request.args.get('target_vertical')
        min_success_probability = request.args.get('min_success_probability', 0.7, type=float)
        
        # Generar conceptos
        concepts = brain_system.generate_fresh_concepts(
            num_concepts=num_concepts,
            focus_theme=focus_theme,
            target_vertical=target_vertical,
            min_success_probability=min_success_probability
        )
        
        # Exportar a archivo
        filename = brain_system.export_concepts_to_json(concepts)
        
        return send_file(
            filename,
            as_attachment=True,
            download_name=f"marketing_concepts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mimetype='application/json'
        )
    
    except Exception as e:
        logger.error(f"Error exporting concepts: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/export/suggestions', methods=['GET'])
def export_suggestions():
    """Exportar sugerencias a JSON"""
    if not brain_system:
        return jsonify({
            'status': 'error',
            'message': 'Sistema no inicializado'
        }), 500
    
    try:
        # Parámetros de consulta
        num_suggestions = request.args.get('num_suggestions', 15, type=int)
        document_content = request.args.get('document_content')
        
        # Generar sugerencias
        if document_content:
            insights = brain_system.analyze_document_insights(document_content)
            suggestions = brain_system.generate_actionable_marketing_suggestions(
                insights, num_suggestions=num_suggestions
            )
        else:
            # Usar insights del sistema si está disponible
            if brain_system.strategies:
                insights = brain_system.analyze_document_insights(brain_system.strategies)
                suggestions = brain_system.generate_actionable_marketing_suggestions(
                    insights, num_suggestions=num_suggestions
                )
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'No hay contenido de documento disponible para generar sugerencias'
                }), 400
        
        # Exportar a archivo
        filename = brain_system.export_suggestions_to_json(suggestions)
        
        return send_file(
            filename,
            as_attachment=True,
            download_name=f"marketing_suggestions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mimetype='application/json'
        )
    
    except Exception as e:
        logger.error(f"Error exporting suggestions: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'system_initialized': brain_system is not None
    })

@app.errorhandler(404)
def not_found(error):
    """Manejar errores 404"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint no encontrado',
        'available_endpoints': [
            'GET /', 'GET /status', 'GET /themes', 'GET /campaigns',
            'POST /concepts/generate', 'POST /concepts/filter',
            'POST /documents/analyze', 'POST /suggestions/generate',
            'GET /export/concepts', 'GET /export/suggestions'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejar errores 500"""
    return jsonify({
        'status': 'error',
        'message': 'Error interno del servidor'
    }), 500

def create_sample_requests():
    """Crear archivo con ejemplos de requests para el API"""
    sample_requests = {
        "generate_concepts": {
            "url": "POST /concepts/generate",
            "body": {
                "num_concepts": 10,
                "focus_theme": "Personalización con IA",
                "target_vertical": "E-commerce",
                "min_success_probability": 0.8
            }
        },
        "filter_concepts": {
            "url": "POST /concepts/filter",
            "body": {
                "num_concepts": 50,
                "filters": {
                    "theme": "Análisis Predictivo",
                    "technology": "Machine Learning",
                    "min_success_probability": 0.7,
                    "max_budget": 50000,
                    "complexity": "Media"
                }
            }
        },
        "analyze_document": {
            "url": "POST /documents/analyze",
            "body": {
                "content": "Este es un documento de estrategias de marketing que incluye temas como personalización, automatización y análisis predictivo..."
            }
        },
        "generate_suggestions": {
            "url": "POST /suggestions/generate",
            "body": {
                "document_content": "Documento con estrategias de marketing...",
                "num_suggestions": 15
            }
        }
    }
    
    with open('api_sample_requests.json', 'w', encoding='utf-8') as f:
        json.dump(sample_requests, f, indent=2, ensure_ascii=False)
    
    logger.info("📝 Sample requests file created: api_sample_requests.json")

def main():
    """Función principal para ejecutar el API"""
    print("🌐 MARKETING BRAIN API")
    print("=" * 50)
    
    # Inicializar sistema
    if not initialize_brain_system():
        print("❌ Error al inicializar el sistema")
        return
    
    # Crear archivo de ejemplos
    create_sample_requests()
    
    print("✅ Sistema inicializado correctamente")
    print("🚀 Iniciando servidor API...")
    print("📡 API disponible en: http://localhost:5000")
    print("📋 Documentación disponible en: http://localhost:5000/")
    print("🔍 Health check: http://localhost:5000/health")
    print("\n📝 Ejemplos de requests guardados en: api_sample_requests.json")
    
    # Ejecutar servidor
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )

if __name__ == "__main__":
    main()








