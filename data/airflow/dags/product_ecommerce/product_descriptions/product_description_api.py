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


@app.route('/api/v1/product-descriptions/analyze', methods=['POST'])
def analyze_description():
    """Analiza una descripción existente y proporciona insights."""
    try:
        from product_description_analyzer import ProductDescriptionAnalyzer
        
        data = request.get_json()
        
        if not data or 'description_data' not in data:
            return jsonify({'error': 'Se requiere "description_data"'}), 400
        
        analyzer = ProductDescriptionAnalyzer()
        analysis = analyzer.analyze_complete(data['description_data'])
        
        return jsonify({
            'success': True,
            'analysis': analysis
        }), 200
        
    except Exception as e:
        logger.error(f"Error analizando descripción: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/templates/categories', methods=['GET'])
def get_template_categories():
    """Lista todas las categorías de templates disponibles."""
    try:
        from product_description_templates import ProductCategoryTemplates
        
        categories = ProductCategoryTemplates.list_categories()
        
        return jsonify({
            'success': True,
            'categories': categories,
            'count': len(categories)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo categorías: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/templates/<category>', methods=['GET'])
def get_template_for_category(category):
    """Obtiene el template para una categoría específica."""
    try:
        from product_description_templates import ProductCategoryTemplates
        
        template = ProductCategoryTemplates.get_template(category)
        
        if not template:
            return jsonify({
                'success': False,
                'error': f'Categoría "{category}" no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'category': category,
            'template': template
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo template: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/enhance', methods=['POST'])
def enhance_with_template():
    """Enriquece datos de producto usando templates de categoría."""
    try:
        from product_description_templates import ProductCategoryTemplates
        
        data = request.get_json()
        
        if not data or 'category' not in data:
            return jsonify({'error': 'Se requiere "category"'}), 400
        
        enhanced = ProductCategoryTemplates.enhance_product_data(
            data.get('product_data', {}),
            data['category']
        )
        
        return jsonify({
            'success': True,
            'enhanced_data': enhanced
        }), 200
        
    except Exception as e:
        logger.error(f"Error enriqueciendo datos: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/optimize/bullets', methods=['POST'])
def optimize_bullets():
    """Optimiza bullets de una descripción."""
    try:
        from product_description_optimizer import BulletOptimizer
        
        data = request.get_json()
        
        if not data or 'bullets' not in data:
            return jsonify({'error': 'Se requiere "bullets" (array)'}), 400
        
        bullets = data['bullets']
        max_bullets = data.get('max_bullets', 5)
        
        optimized = BulletOptimizer.optimize_bullets(bullets, max_bullets)
        
        return jsonify({
            'success': True,
            'original_count': len(bullets),
            'optimized_count': len(optimized),
            'optimized_bullets': optimized
        }), 200
        
    except Exception as e:
        logger.error(f"Error optimizando bullets: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/optimize/conversion', methods=['POST'])
def analyze_conversion():
    """Analiza el potencial de conversión de una descripción."""
    try:
        from product_description_optimizer import ConversionOptimizer
        
        data = request.get_json()
        
        if not data or 'description_data' not in data:
            return jsonify({'error': 'Se requiere "description_data"'}), 400
        
        analysis = ConversionOptimizer.calculate_conversion_potential(data['description_data'])
        
        return jsonify({
            'success': True,
            'analysis': analysis
        }), 200
        
    except Exception as e:
        logger.error(f"Error analizando conversión: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/recommendations', methods=['POST'])
def get_recommendations():
    """Obtiene recomendaciones para mejorar una descripción."""
    try:
        from product_description_optimizer import DescriptionRecommender
        
        data = request.get_json()
        
        if not data or 'description_data' not in data:
            return jsonify({'error': 'Se requiere "description_data"'}), 400
        
        recommendations = DescriptionRecommender.generate_recommendations(data['description_data'])
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        }), 200
        
    except Exception as e:
        logger.error(f"Error generando recomendaciones: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/compare', methods=['POST'])
def compare_versions():
    """Compara dos versiones de descripción."""
    try:
        from product_description_optimizer import VersionComparator
        
        data = request.get_json()
        
        if not data or 'version1' not in data or 'version2' not in data:
            return jsonify({'error': 'Se requieren "version1" y "version2"'}), 400
        
        comparison = VersionComparator.compare_versions(data['version1'], data['version2'])
        
        return jsonify({
            'success': True,
            'comparison': comparison
        }), 200
        
    except Exception as e:
        logger.error(f"Error comparando versiones: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/ml/predict', methods=['POST'])
def predict_conversion_ml():
    """Predice conversión usando ML basado en datos históricos."""
    try:
        from product_description_ml import DescriptionMLOptimizer
        
        data = request.get_json()
        
        if not data or 'description_data' not in data:
            return jsonify({'error': 'Se requiere "description_data"'}), 400
        
        optimizer = DescriptionMLOptimizer()
        prediction = optimizer.predict_conversion(data['description_data'])
        
        return jsonify({
            'success': True,
            'prediction': prediction
        }), 200
        
    except Exception as e:
        logger.error(f"Error prediciendo conversión ML: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/ml/learn', methods=['POST'])
def learn_from_success():
    """Aprende de una descripción exitosa."""
    try:
        from product_description_ml import DescriptionMLOptimizer
        
        data = request.get_json()
        
        if not data or 'description_data' not in data or 'metrics' not in data:
            return jsonify({'error': 'Se requieren "description_data" y "metrics"'}), 400
        
        optimizer = DescriptionMLOptimizer()
        optimizer.learn_from_success(data['description_data'], data['metrics'])
        
        return jsonify({
            'success': True,
            'message': 'Aprendizaje registrado exitosamente'
        }), 200
        
    except Exception as e:
        logger.error(f"Error en aprendizaje ML: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/reviews/analyze', methods=['POST'])
def analyze_reviews():
    """Analiza reviews de clientes para mejorar descripciones."""
    try:
        from product_description_ml import ReviewAnalyzer
        
        data = request.get_json()
        
        if not data or 'reviews' not in data:
            return jsonify({'error': 'Se requiere "reviews" (array)'}), 400
        
        insights = ReviewAnalyzer.extract_insights_from_reviews(data['reviews'])
        
        return jsonify({
            'success': True,
            'insights': insights
        }), 200
        
    except Exception as e:
        logger.error(f"Error analizando reviews: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/cta/generate', methods=['POST'])
def generate_cta():
    """Genera un CTA optimizado."""
    try:
        from product_description_ml import CTAOptimizer
        
        data = request.get_json()
        
        context = data.get('context', {})
        language = data.get('language', 'es')
        
        cta = CTAOptimizer.generate_optimized_cta(context, language)
        
        return jsonify({
            'success': True,
            'cta': cta
        }), 200
        
    except Exception as e:
        logger.error(f"Error generando CTA: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/analytics/stats/<description_id>', methods=['GET'])
def get_analytics_stats(description_id):
    """Obtiene estadísticas de analytics para una descripción."""
    try:
        from product_description_analytics import DescriptionAnalytics
        
        days = request.args.get('days', 30, type=int)
        
        analytics = DescriptionAnalytics()
        stats = analytics.get_description_stats(description_id, days)
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo stats: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/analytics/report', methods=['GET'])
def get_analytics_report():
    """Genera reporte completo de analytics."""
    try:
        from product_description_analytics import DescriptionAnalytics
        
        days = request.args.get('days', 30, type=int)
        
        analytics = DescriptionAnalytics()
        report = analytics.generate_report(days)
        
        return jsonify({
            'success': True,
            'report': report
        }), 200
        
    except Exception as e:
        logger.error(f"Error generando reporte: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/translate', methods=['POST'])
def translate_description():
    """Traduce una descripción a otro idioma."""
    try:
        from product_description_translator import ProductDescriptionTranslator
        from product_description_generator import LLMClient
        
        data = request.get_json()
        
        if not data or 'description_data' not in data or 'target_language' not in data:
            return jsonify({'error': 'Se requieren "description_data" y "target_language"'}), 400
        
        llm_client = LLMClient()
        translator = ProductDescriptionTranslator(llm_client)
        
        translated = translator.translate_description(
            data['description_data'],
            data['target_language'],
            preserve_seo=data.get('preserve_seo', True)
        )
        
        return jsonify({
            'success': True,
            'translated': translated
        }), 200
        
    except Exception as e:
        logger.error(f"Error traduciendo: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/translate/languages', methods=['GET'])
def get_supported_languages():
    """Obtiene lista de idiomas soportados para traducción."""
    try:
        from product_description_translator import ProductDescriptionTranslator
        
        languages = ProductDescriptionTranslator.get_supported_languages()
        
        return jsonify({
            'success': True,
            'languages': languages,
            'count': len(languages)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo idiomas: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/trends/keywords', methods=['POST'])
def analyze_keyword_trends():
    """Analiza tendencias de keywords."""
    try:
        from product_description_trends import MarketTrendsAnalyzer
        
        data = request.get_json()
        
        if not data or 'keywords' not in data:
            return jsonify({'error': 'Se requiere "keywords" (array)'}), 400
        
        analyzer = MarketTrendsAnalyzer()
        trends = analyzer.analyze_keyword_trends(
            data['keywords'],
            days=data.get('days', 90)
        )
        
        return jsonify({
            'success': True,
            'trends': trends
        }), 200
        
    except Exception as e:
        logger.error(f"Error analizando tendencias: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/trends/product', methods=['POST'])
def analyze_product_trends():
    """Analiza tendencias de un tipo de producto."""
    try:
        from product_description_trends import MarketTrendsAnalyzer
        
        data = request.get_json()
        
        if not data or 'product_type' not in data:
            return jsonify({'error': 'Se requiere "product_type"'}), 400
        
        analyzer = MarketTrendsAnalyzer()
        trends = analyzer.analyze_product_trends(
            data['product_type'],
            category=data.get('category')
        )
        
        return jsonify({
            'success': True,
            'trends': trends
        }), 200
        
    except Exception as e:
        logger.error(f"Error analizando tendencias de producto: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/alerts/check', methods=['POST'])
def check_alerts():
    """Verifica alertas para una descripción."""
    try:
        from product_description_trends import SmartAlerts
        
        data = request.get_json()
        
        if not data or 'description_data' not in data:
            return jsonify({'error': 'Se requiere "description_data"'}), 400
        
        alerts_system = SmartAlerts()
        alerts = alerts_system.check_alerts(
            data['description_data'],
            metrics=data.get('metrics')
        )
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'count': len(alerts)
        }), 200
        
    except Exception as e:
        logger.error(f"Error verificando alertas: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/alerts/summary', methods=['GET'])
def get_alerts_summary():
    """Obtiene resumen de alertas."""
    try:
        from product_description_trends import SmartAlerts
        
        days = request.args.get('days', 7, type=int)
        
        alerts_system = SmartAlerts()
        summary = alerts_system.get_alert_summary(days)
        
        return jsonify({
            'success': True,
            'summary': summary
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen de alertas: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/versions/create', methods=['POST'])
def create_version():
    """Crea una nueva versión de una descripción."""
    try:
        from product_description_versioning import DescriptionVersionControl
        
        data = request.get_json()
        
        if not data or 'description_id' not in data or 'description_data' not in data:
            return jsonify({'error': 'Se requieren "description_id" y "description_data"'}), 400
        
        version_control = DescriptionVersionControl()
        version_id = version_control.create_version(
            data['description_id'],
            data['description_data'],
            metadata=data.get('metadata')
        )
        
        return jsonify({
            'success': True,
            'version_id': version_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error creando versión: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/versions/<description_id>', methods=['GET'])
def get_versions(description_id):
    """Obtiene historial de versiones de una descripción."""
    try:
        from product_description_versioning import DescriptionVersionControl
        
        version_id = request.args.get('version_id')
        
        version_control = DescriptionVersionControl()
        
        if version_id:
            version = version_control.get_version(description_id, version_id)
            if not version:
                return jsonify({'error': 'Versión no encontrada'}), 404
            return jsonify({'success': True, 'version': version}), 200
        else:
            history = version_control.get_version_history(description_id)
            return jsonify({
                'success': True,
                'history': history,
                'count': len(history)
            }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo versiones: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/versions/compare', methods=['POST'])
def compare_versions_endpoint():
    """Compara dos versiones de una descripción."""
    try:
        from product_description_versioning import DescriptionVersionControl
        
        data = request.get_json()
        
        if not all(k in data for k in ['description_id', 'version1_id', 'version2_id']):
            return jsonify({'error': 'Se requieren description_id, version1_id y version2_id'}), 400
        
        version_control = DescriptionVersionControl()
        comparison = version_control.compare_versions(
            data['description_id'],
            data['version1_id'],
            data['version2_id']
        )
        
        return jsonify({
            'success': True,
            'comparison': comparison
        }), 200
        
    except Exception as e:
        logger.error(f"Error comparando versiones: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/social/generate', methods=['POST'])
def generate_social_content():
    """Genera contenido para redes sociales."""
    try:
        from product_description_social import SocialContentGenerator
        from product_description_generator import LLMClient
        
        data = request.get_json()
        
        if not data or 'description_data' not in data or 'platform' not in data:
            return jsonify({'error': 'Se requieren "description_data" y "platform"'}), 400
        
        llm_client = LLMClient()
        generator = SocialContentGenerator(llm_client)
        
        content = generator.generate_social_content(
            data['description_data'],
            data['platform'],
            content_type=data.get('content_type', 'post'),
            include_hashtags=data.get('include_hashtags', True)
        )
        
        return jsonify({
            'success': True,
            'content': content
        }), 200
        
    except Exception as e:
        logger.error(f"Error generando contenido social: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/competitors/scrape', methods=['POST'])
def scrape_competitors():
    """Extrae datos de productos competidores."""
    try:
        from product_description_social import CompetitorScraper
        
        data = request.get_json()
        
        if not data or 'urls' not in data:
            return jsonify({'error': 'Se requiere "urls" (array)'}), 400
        
        if not isinstance(data['urls'], list) or len(data['urls']) == 0:
            return jsonify({'error': '"urls" debe ser un array no vacío'}), 400
        
        if len(data['urls']) > 10:
            return jsonify({'error': 'Máximo 10 URLs por request'}), 400
        
        analysis = CompetitorScraper.analyze_competitor_descriptions(data['urls'])
        
        return jsonify({
            'success': True,
            'analysis': analysis
        }), 200
        
    except Exception as e:
        logger.error(f"Error scraping competidores: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/ab-test/create', methods=['POST'])
def create_ab_test():
    """Crea una nueva prueba A/B."""
    try:
        from product_description_ab_testing import ABTestManager
        
        data = request.get_json()
        
        if not all(k in data for k in ['test_name', 'description_id', 'variations']):
            return jsonify({'error': 'Se requieren test_name, description_id y variations'}), 400
        
        manager = ABTestManager()
        test = manager.create_test(
            test_name=data['test_name'],
            description_id=data['description_id'],
            variations=data['variations'],
            traffic_split=data.get('traffic_split'),
            duration_days=data.get('duration_days', 14),
            min_sample_size=data.get('min_sample_size', 100)
        )
        
        return jsonify({
            'success': True,
            'test': test
        }), 200
        
    except Exception as e:
        logger.error(f"Error creando test A/B: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/ab-test/<test_id>/results', methods=['GET'])
def get_ab_test_results(test_id):
    """Obtiene resultados de un test A/B."""
    try:
        from product_description_ab_testing import ABTestManager
        
        manager = ABTestManager()
        results = manager.get_test_results(test_id)
        
        if 'error' in results:
            return jsonify(results), 404
        
        return jsonify({
            'success': True,
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo resultados A/B: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/ab-test/<test_id>/conversion', methods=['POST'])
def record_ab_conversion(test_id):
    """Registra una conversión para un test A/B."""
    try:
        from product_description_ab_testing import ABTestManager
        
        data = request.get_json()
        
        if not data or 'variation_id' not in data:
            return jsonify({'error': 'Se requiere variation_id'}), 400
        
        manager = ABTestManager()
        manager.record_conversion(
            test_id,
            data['variation_id'],
            data.get('converted', True),
            metadata=data.get('metadata')
        )
        
        return jsonify({
            'success': True,
            'message': 'Conversión registrada'
        }), 200
        
    except Exception as e:
        logger.error(f"Error registrando conversión A/B: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/images/suggestions', methods=['POST'])
def generate_image_suggestions():
    """Genera sugerencias de imágenes con IA."""
    try:
        from product_description_image_suggestions import ImageSuggestionGenerator
        from product_description_generator import LLMClient
        
        data = request.get_json()
        
        if not data or 'description_data' not in data:
            return jsonify({'error': 'Se requiere description_data'}), 400
        
        llm_client = LLMClient()
        generator = ImageSuggestionGenerator(llm_client)
        
        suggestions = generator.generate_image_suggestions(
            data['description_data'],
            num_suggestions=data.get('num_suggestions', 5),
            image_types=data.get('image_types')
        )
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        }), 200
        
    except Exception as e:
        logger.error(f"Error generando sugerencias de imágenes: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'details': str(e)}), 500


@app.route('/api/v1/product-descriptions/analytics/ga/track', methods=['POST'])
def track_ga_event():
    """Registra un evento en Google Analytics."""
    try:
        from product_description_google_analytics import GoogleAnalyticsIntegration
        
        data = request.get_json()
        
        if not data or 'measurement_id' not in data or 'event_type' not in data:
            return jsonify({'error': 'Se requieren measurement_id y event_type'}), 400
        
        ga = GoogleAnalyticsIntegration(
            measurement_id=data['measurement_id'],
            api_secret=data.get('api_secret')
        )
        
        success = False
        if data['event_type'] == 'view':
            success = ga.track_description_view(
                data.get('description_id', ''),
                data.get('product_name', ''),
                data.get('platform', ''),
                data.get('client_id')
            )
        elif data['event_type'] == 'conversion':
            success = ga.track_description_conversion(
                data.get('description_id', ''),
                data.get('product_name', ''),
                data.get('platform', ''),
                data.get('conversion_value'),
                data.get('client_id')
            )
        
        return jsonify({
            'success': success,
            'message': 'Evento enviado a Google Analytics' if success else 'Error enviando evento'
        }), 200
        
    except Exception as e:
        logger.error(f"Error tracking GA: {str(e)}")
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




