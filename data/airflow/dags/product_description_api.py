"""
API REST para generación masiva de descripciones de productos.

Endpoints:
- POST /api/v1/product-descriptions/generate - Generar descripción única
- POST /api/v1/product-descriptions/generate-batch - Generar múltiples descripciones
- GET /api/v1/product-descriptions/{id} - Obtener descripción generada
- GET /api/v1/product-descriptions/{id}/variations - Obtener variaciones para A/B testing
- POST /api/v1/product-descriptions/{id}/variations - Generar variaciones adicionales
- GET /api/v1/product-descriptions - Listar descripciones (con filtros)

Uso para automatización:
- Integración con catálogos de productos
- Sincronización con Shopify/Amazon
- Webhooks para nuevos productos
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import logging
from typing import Dict, List, Optional
import os

from product_description_generator import (
    LLMClient, ProductDescriptionGenerator, SEOOptimizer,
    get_cache_key, check_cache, save_to_cache
)
from airflow.models import Variable

app = Flask(__name__)
CORS(app)
logger = logging.getLogger(__name__)

# Configuración
DEFAULT_LLM_PROVIDER = os.getenv('DEFAULT_LLM_PROVIDER', 'openai')
SUPPORTED_PLATFORMS = ['amazon', 'shopify', 'generic']


class ProductDescriptionAPI:
    """API para generación de descripciones de productos."""
    
    def __init__(self):
        self.llm_client = None
        self.generator = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Inicializa el cliente LLM."""
        try:
            provider = Variable.get("DEFAULT_LLM_PROVIDER", default_var=DEFAULT_LLM_PROVIDER)
            self.llm_client = LLMClient(provider)
            self.generator = ProductDescriptionGenerator(self.llm_client)
        except Exception as e:
            logger.error(f"Error inicializando LLM: {str(e)}")
            raise
    
    def generate_single(self, product_data: Dict) -> Dict:
        """Genera una descripción única."""
        # Validar datos requeridos
        required_fields = ['product_name', 'key_benefits', 'technical_features', 'target_audience']
        for field in required_fields:
            if not product_data.get(field):
                raise ValueError(f"Campo requerido faltante: {field}")
        
        # Verificar caché
        cache_key = get_cache_key(product_data)
        cached = check_cache(cache_key)
        if cached:
            logger.info(f"Usando descripción desde caché para {product_data['product_name']}")
            return {
                'success': True,
                'data': cached,
                'from_cache': True
            }
        
        # Generar descripción
        result = self.generator.generate_description(
            product_name=product_data['product_name'],
            product_type=product_data.get('product_type', ''),
            key_benefits=product_data['key_benefits'],
            technical_features=product_data['technical_features'],
            target_audience=product_data['target_audience'],
            platform=product_data.get('platform', 'generic'),
            keywords=product_data.get('keywords'),
            brand_story=product_data.get('brand_story'),
            word_count=product_data.get('word_count', 300)
        )
        
        # Guardar en caché
        save_to_cache(cache_key, result)
        
        return {
            'success': True,
            'data': result,
            'from_cache': False
        }
    
    def generate_batch(self, products: List[Dict]) -> Dict:
        """Genera descripciones para múltiples productos."""
        results = {
            'success': [],
            'failed': [],
            'total': len(products),
            'processed': 0
        }
        
        for i, product_data in enumerate(products):
            try:
                result = self.generate_single(product_data)
                results['success'].append({
                    'index': i,
                    'product_name': product_data.get('product_name', f'Producto {i+1}'),
                    'result': result['data']
                })
                results['processed'] += 1
            except Exception as e:
                logger.error(f"Error generando descripción para producto {i+1}: {str(e)}")
                results['failed'].append({
                    'index': i,
                    'product_name': product_data.get('product_name', f'Producto {i+1}'),
                    'error': str(e)
                })
        
        results['success_count'] = len(results['success'])
        results['failed_count'] = len(results['failed'])
        
        return results
    
    def generate_variations(self, product_data: Dict, num_variations: int = 3, variation_types: List[str] = None) -> Dict:
        """Genera variaciones para A/B testing."""
        if variation_types is None:
            variation_types = ['emotional', 'technical', 'benefit_focused']
        
        variations = self.generator.generate_variations(
            base_product_info=product_data,
            num_variations=num_variations,
            variation_types=variation_types
        )
        
        return {
            'success': True,
            'variations': variations,
            'count': len(variations)
        }


# Inicializar API
api = ProductDescriptionAPI()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'product-description-api',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/v1/product-descriptions/generate', methods=['POST'])
def generate_description():
    """Genera una descripción única de producto."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
        
        result = api.generate_single(data)
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error generando descripción: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/generate-batch', methods=['POST'])
def generate_batch():
    """Genera descripciones para múltiples productos."""
    try:
        data = request.get_json()
        
        if not data or 'products' not in data:
            return jsonify({'error': 'Se requiere un array "products"'}), 400
        
        products = data['products']
        
        if not isinstance(products, list) or len(products) == 0:
            return jsonify({'error': 'El array "products" no puede estar vacío'}), 400
        
        if len(products) > 100:
            return jsonify({'error': 'Máximo 100 productos por batch'}), 400
        
        result = api.generate_batch(products)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error generando batch: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/variations', methods=['POST'])
def generate_variations_endpoint():
    """Genera variaciones para A/B testing."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
        
        num_variations = data.get('num_variations', 3)
        variation_types = data.get('variation_types', ['emotional', 'technical', 'benefit_focused'])
        
        # Remover campos de variación del product_data
        product_data = {k: v for k, v in data.items() if k not in ['num_variations', 'variation_types']}
        
        result = api.generate_variations(product_data, num_variations, variation_types)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error generando variaciones: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/validate', methods=['POST'])
def validate_product_data():
    """Valida los datos de producto antes de generar."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
        
        errors = []
        warnings = []
        
        # Validar campos requeridos
        required_fields = {
            'product_name': 'Nombre del producto',
            'key_benefits': 'Beneficios clave',
            'technical_features': 'Características técnicas',
            'target_audience': 'Público objetivo'
        }
        
        for field, label in required_fields.items():
            if not data.get(field):
                errors.append(f'{label} es requerido')
            elif field in ['key_benefits', 'technical_features']:
                if not isinstance(data[field], list) or len(data[field]) == 0:
                    errors.append(f'{label} debe ser un array no vacío')
        
        # Validar plataforma
        if data.get('platform') and data['platform'] not in SUPPORTED_PLATFORMS:
            errors.append(f'Plataforma debe ser una de: {", ".join(SUPPORTED_PLATFORMS)}')
        
        # Validar word_count
        word_count = data.get('word_count', 300)
        if word_count < 200 or word_count > 400:
            warnings.append('word_count debería estar entre 200 y 400 para mejores resultados')
        
        # Validar keywords
        if data.get('keywords') and not isinstance(data['keywords'], list):
            warnings.append('keywords debería ser un array')
        
        return jsonify({
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }), 200
        
    except Exception as e:
        logger.error(f"Error validando datos: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/examples', methods=['GET'])
def get_examples():
    """Retorna ejemplos de uso de la API."""
    examples = {
        'single_product': {
            'product_name': 'Zapatos Ecológicos Modelo X',
            'product_type': 'Calzado sostenible',
            'key_benefits': [
                'Durabilidad 2x mayor que zapatos convencionales',
                '100% materiales reciclados y reciclables',
                'Comfort superior con tecnología de amortiguación avanzada'
            ],
            'technical_features': [
                'Suela de caucho reciclado con 70% de contenido reciclado',
                'Forro interior de algodón orgánico certificado',
                'Peso ligero: 280g por par',
                'Resistente al agua con tratamiento ecológico'
            ],
            'target_audience': 'compradores eco-friendly conscientes del medio ambiente',
            'platform': 'amazon',
            'keywords': ['zapatos ecológicos', 'calzado sostenible', 'zapatos reciclados'],
            'word_count': 300
        },
        'batch_request': {
            'products': [
                {
                    'product_name': 'Producto 1',
                    'key_benefits': ['Beneficio 1', 'Beneficio 2'],
                    'technical_features': ['Feature 1', 'Feature 2'],
                    'target_audience': 'Audiencia objetivo',
                    'platform': 'shopify'
                },
                {
                    'product_name': 'Producto 2',
                    'key_benefits': ['Beneficio 1', 'Beneficio 2'],
                    'technical_features': ['Feature 1', 'Feature 2'],
                    'target_audience': 'Audiencia objetivo',
                    'platform': 'amazon'
                }
            ]
        },
        'variations_request': {
            'product_name': 'Zapatos Ecológicos Modelo X',
            'key_benefits': ['Durabilidad 2x mayor'],
            'technical_features': ['Suela reciclada'],
            'target_audience': 'compradores eco-friendly',
            'num_variations': 3,
            'variation_types': ['emotional', 'technical', 'benefit_focused']
        }
    }
    
    return jsonify(examples), 200


if __name__ == '__main__':
    # Para desarrollo local
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    # Para producción con gunicorn/uwsgi
    pass




