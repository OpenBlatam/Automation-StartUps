from flask import Blueprint, request, jsonify
from app import db
from models import Product, SalesRecord, InventoryRecord
from services.predictive_analytics_service import advanced_predictive_analytics_service
from services.logistics_service import logistics_optimization_service, DeliveryStatus
from datetime import datetime, timedelta
import logging
import json

# Crear blueprint para análisis predictivo y logística
predictive_logistics_bp = Blueprint('predictive_logistics', __name__)

# Configurar logging
logger = logging.getLogger(__name__)

# ==================== ANÁLISIS PREDICTIVO AVANZADO ====================

@predictive_logistics_bp.route('/predictive/train-models', methods=['POST'])
def train_predictive_models():
    """Entrena modelos de análisis predictivo"""
    try:
        data = request.get_json() or {}
        product_id = data.get('product_id')
        
        result = advanced_predictive_analytics_service.train_time_series_models(product_id)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'message': 'Modelos de análisis predictivo entrenados exitosamente',
            'models_trained': result['models_trained'],
            'products': result['products'],
            'total_models': result['total_models']
        })
        
    except Exception as e:
        logger.error(f'Error entrenando modelos predictivos: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@predictive_logistics_bp.route('/predictive/forecast/<int:product_id>', methods=['GET'])
def generate_forecast(product_id):
    """Genera pronóstico para un producto"""
    try:
        periods = request.args.get('periods', 30, type=int)
        
        forecast = advanced_predictive_analytics_service.generate_forecast(product_id, periods)
        
        if 'error' in forecast:
            return jsonify({'error': forecast['error']}), 400
        
        return jsonify({
            'success': True,
            'forecast': forecast
        })
        
    except Exception as e:
        logger.error(f'Error generando pronóstico: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@predictive_logistics_bp.route('/predictive/analyze-patterns', methods=['POST'])
def analyze_demand_patterns():
    """Analiza patrones de demanda"""
    try:
        data = request.get_json() or {}
        product_id = data.get('product_id')
        
        analysis = advanced_predictive_analytics_service.analyze_demand_patterns(product_id)
        
        if 'error' in analysis:
            return jsonify({'error': analysis['error']}), 400
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f'Error analizando patrones de demanda: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@predictive_logistics_bp.route('/predictive/detect-anomalies', methods=['POST'])
def detect_anomalies_advanced():
    """Detecta anomalías avanzadas"""
    try:
        data = request.get_json() or {}
        product_id = data.get('product_id')
        
        anomalies = advanced_predictive_analytics_service.detect_anomalies_advanced(product_id)
        
        if 'error' in anomalies:
            return jsonify({'error': anomalies['error']}), 400
        
        return jsonify({
            'success': True,
            'anomalies': anomalies
        })
        
    except Exception as e:
        logger.error(f'Error detectando anomalías avanzadas: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@predictive_logistics_bp.route('/predictive/model-performance', methods=['GET'])
def get_predictive_model_performance():
    """Obtiene rendimiento de modelos predictivos"""
    try:
        performance = advanced_predictive_analytics_service.get_model_performance()
        
        if 'error' in performance:
            return jsonify({'error': performance['error']}), 400
        
        return jsonify({
            'success': True,
            'performance': performance
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo rendimiento de modelos predictivos: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@predictive_logistics_bp.route('/predictive/forecast-history', methods=['GET'])
def get_forecast_history():
    """Obtiene historial de pronósticos"""
    try:
        history = advanced_predictive_analytics_service.get_forecast_history()
        
        return jsonify({
            'success': True,
            'forecast_history': history,
            'total_forecasts': len(history)
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo historial de pronósticos: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== OPTIMIZACIÓN DE LOGÍSTICA ====================

@predictive_logistics_bp.route('/logistics/create-order', methods=['POST'])
def create_delivery_order():
    """Crea orden de entrega"""
    try:
        data = request.get_json()
        
        required_fields = ['customer_id', 'products', 'delivery_location_id', 'delivery_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} es requerido'}), 400
        
        # Convertir fecha
        try:
            delivery_date = datetime.fromisoformat(data['delivery_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido'}), 400
        
        result = logistics_optimization_service.create_delivery_order(
            customer_id=data['customer_id'],
            products=data['products'],
            delivery_location_id=data['delivery_location_id'],
            delivery_date=delivery_date,
            priority=data.get('priority', 3)
        )
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'order': result['delivery_order']
        })
        
    except Exception as e:
        logger.error(f'Error creando orden de entrega: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@predictive_logistics_bp.route('/logistics/optimize-routes', methods=['POST'])
def optimize_routes():
    """Optimiza rutas de entrega"""
    try:
        data = request.get_json() or {}
        date_str = data.get('date')
        
        date = None
        if date_str:
            try:
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
            except ValueError:
                return jsonify({'error': 'Formato de fecha inválido'}), 400
        
        result = logistics_optimization_service.optimize_routes(date)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'optimization': result
        })
        
    except Exception as e:
        logger.error(f'Error optimizando rutas: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@predictive_logistics_bp.route('/logistics/route/<route_id>', methods=['GET'])
def get_route_details(route_id):
    """Obtiene detalles de una ruta"""
    try:
        result = logistics_optimization_service.get_route_details(route_id)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'route': result['route']
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo detalles de ruta: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@predictive_logistics_bp.route('/logistics/vehicles/status', methods=['GET'])
def get_vehicle_status():
    """Obtiene estado de vehículos"""
    try:
        result = logistics_optimization_service.get_vehicle_status()
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'vehicles': result['vehicles'],
            'total_vehicles': result['total_vehicles'],
            'available_vehicles': result['available_vehicles']
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo estado de vehículos: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@predictive_logistics_bp.route('/logistics/update-delivery-status', methods=['POST'])
def update_delivery_status():
    """Actualiza estado de entrega"""
    try:
        data = request.get_json()
        
        if 'order_id' not in data or 'status' not in data:
            return jsonify({'error': 'order_id y status son requeridos'}), 400
        
        # Validar estado
        try:
            status = DeliveryStatus(data['status'])
        except ValueError:
            return jsonify({'error': 'Estado de entrega inválido'}), 400
        
        result = logistics_optimization_service.update_delivery_status(data['order_id'], status)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'order_id': result['order_id'],
            'new_status': result['new_status'],
            'updated_at': result['updated_at']
        })
        
    except Exception as e:
        logger.error(f'Error actualizando estado de entrega: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@predictive_logistics_bp.route('/logistics/dashboard', methods=['GET'])
def get_logistics_dashboard():
    """Obtiene datos para dashboard de logística"""
    try:
        result = logistics_optimization_service.get_logistics_dashboard()
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'dashboard': result['dashboard']
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo dashboard de logística: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== DASHBOARD COMBINADO ====================

@predictive_logistics_bp.route('/predictive-logistics/dashboard', methods=['GET'])
def get_predictive_logistics_dashboard():
    """Obtiene datos para dashboard combinado"""
    try:
        # Obtener datos de análisis predictivo
        predictive_performance = advanced_predictive_analytics_service.get_model_performance()
        forecast_history = advanced_predictive_analytics_service.get_forecast_history()
        
        # Obtener datos de logística
        logistics_dashboard = logistics_optimization_service.get_logistics_dashboard()
        
        return jsonify({
            'success': True,
            'dashboard': {
                'predictive': {
                    'models_trained': predictive_performance.get('total_models', 0) if predictive_performance.get('success') else 0,
                    'products_with_models': predictive_performance.get('total_products', 0) if predictive_performance.get('success') else 0,
                    'recent_forecasts': len(forecast_history)
                },
                'logistics': logistics_dashboard.get('dashboard', {}) if logistics_dashboard.get('success') else {},
                'combined': {
                    'total_models': predictive_performance.get('total_models', 0) if predictive_performance.get('success') else 0,
                    'total_vehicles': logistics_dashboard.get('dashboard', {}).get('vehicles', {}).get('total', 0) if logistics_dashboard.get('success') else 0,
                    'pending_orders': logistics_dashboard.get('dashboard', {}).get('orders', {}).get('pending', 0) if logistics_dashboard.get('success') else 0,
                    'active_routes': logistics_dashboard.get('dashboard', {}).get('routes', {}).get('active', 0) if logistics_dashboard.get('success') else 0
                }
            }
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo dashboard combinado: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== ANÁLISIS AVANZADO COMBINADO ====================

@predictive_logistics_bp.route('/predictive-logistics/advanced-analysis', methods=['POST'])
def advanced_combined_analysis():
    """Realiza análisis avanzado combinando predictivo y logística"""
    try:
        data = request.get_json() or {}
        analysis_type = data.get('analysis_type', 'comprehensive')
        
        results = {}
        
        if analysis_type in ['comprehensive', 'predictive']:
            # Análisis predictivo
            patterns = advanced_predictive_analytics_service.analyze_demand_patterns()
            anomalies = advanced_predictive_analytics_service.detect_anomalies_advanced()
            
            results['predictive_analysis'] = {
                'patterns': patterns,
                'anomalies': anomalies,
                'total_patterns': patterns.get('total_products', 0) if patterns.get('success') else 0,
                'total_anomalies': anomalies.get('total_anomalies', 0) if anomalies.get('success') else 0
            }
        
        if analysis_type in ['comprehensive', 'logistics']:
            # Análisis de logística
            logistics_dashboard = logistics_optimization_service.get_logistics_dashboard()
            vehicle_status = logistics_optimization_service.get_vehicle_status()
            
            results['logistics_analysis'] = {
                'dashboard': logistics_dashboard.get('dashboard', {}) if logistics_dashboard.get('success') else {},
                'vehicles': vehicle_status.get('vehicles', []) if vehicle_status.get('success') else [],
                'total_vehicles': vehicle_status.get('total_vehicles', 0) if vehicle_status.get('success') else 0,
                'available_vehicles': vehicle_status.get('available_vehicles', 0) if vehicle_status.get('success') else 0
            }
        
        return jsonify({
            'success': True,
            'analysis_type': analysis_type,
            'results': results,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f'Error realizando análisis avanzado combinado: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500



