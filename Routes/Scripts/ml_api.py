from flask import Blueprint, request, jsonify
from app import db
from models import Product, SalesRecord, Alert, ReorderRecommendation
from services.advanced_ml_service import advanced_ml_service
from services.inventory_optimization_service import inventory_optimization_service, OptimizationResult
from services.advanced_analytics_service import advanced_analytics_service
from datetime import datetime, timedelta
import logging
import json

# Crear blueprint para funcionalidades avanzadas
ml_bp = Blueprint('ml', __name__)

# Configurar logging
logger = logging.getLogger(__name__)

# ==================== MACHINE LEARNING ====================

@ml_bp.route('/ml/train-models', methods=['POST'])
def train_ml_models():
    """Entrena modelos de machine learning"""
    try:
        data = request.get_json() or {}
        product_id = data.get('product_id')
        test_size = data.get('test_size', 0.2)
        
        result = advanced_ml_service.train_models(product_id, test_size)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'message': f'Modelos entrenados exitosamente',
            'models_trained': result['models_trained'],
            'best_model': result['best_model'],
            'best_r2': result['best_r2'],
            'results': {
                name: {
                    'r2_score': res.get('r2', 0),
                    'mae': res.get('mae', 0),
                    'rmse': res.get('rmse', 0)
                } for name, res in result['results'].items() if 'error' not in res
            }
        })
        
    except Exception as e:
        logger.error(f'Error entrenando modelos ML: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ml_bp.route('/ml/predict-demand/<int:product_id>', methods=['GET'])
def predict_demand(product_id):
    """Predice la demanda futura para un producto"""
    try:
        days_ahead = request.args.get('days', 30, type=int)
        
        prediction = advanced_ml_service.predict_demand(product_id, days_ahead)
        
        if 'error' in prediction:
            return jsonify({'error': prediction['error']}), 400
        
        return jsonify({
            'success': True,
            'product_id': product_id,
            'predictions': prediction['predictions'],
            'dates': prediction['dates'],
            'model_used': prediction['model_used'],
            'confidence': prediction['confidence'],
            'total_predicted_demand': prediction['total_predicted_demand'],
            'average_daily_demand': prediction['average_daily_demand']
        })
        
    except Exception as e:
        logger.error(f'Error prediciendo demanda: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ml_bp.route('/ml/model-performance', methods=['GET'])
def get_model_performance():
    """Obtiene el rendimiento de los modelos entrenados"""
    try:
        product_id = request.args.get('product_id', type=int)
        
        performance = advanced_ml_service.get_model_performance(product_id)
        
        if 'error' in performance:
            return jsonify({'error': performance['error']}), 400
        
        return jsonify({
            'success': True,
            'performance': performance
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo rendimiento de modelos: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ml_bp.route('/ml/feature-importance', methods=['GET'])
def get_feature_importance():
    """Obtiene la importancia de las características"""
    try:
        product_id = request.args.get('product_id', type=int)
        
        importance = advanced_ml_service.get_feature_importance(product_id)
        
        if 'error' in importance:
            return jsonify({'error': importance['error']}), 400
        
        return jsonify({
            'success': True,
            'feature_importance': importance
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo importancia de características: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== OPTIMIZACIÓN DE INVENTARIO ====================

@ml_bp.route('/optimization/run', methods=['POST'])
def run_inventory_optimization():
    """Ejecuta optimización de inventario"""
    try:
        data = request.get_json() or {}
        products = data.get('products')  # Lista de IDs de productos
        budget_constraint = data.get('budget_constraint')
        warehouse_capacity = data.get('warehouse_capacity')
        
        result = inventory_optimization_service.optimize_inventory(
            products, budget_constraint, warehouse_capacity
        )
        
        if not result.solution:
            return jsonify({'error': 'No se pudo encontrar una solución óptima'}), 400
        
        return jsonify({
            'success': True,
            'total_cost': result.total_cost,
            'total_value': result.total_value,
            'service_level': result.service_level,
            'solution': result.solution,
            'iterations': result.iterations,
            'convergence_time': result.convergence_time,
            'fitness_history': result.fitness_history
        })
        
    except Exception as e:
        logger.error(f'Error ejecutando optimización: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ml_bp.route('/optimization/recommendations', methods=['POST'])
def get_optimization_recommendations():
    """Obtiene recomendaciones de optimización"""
    try:
        data = request.get_json() or {}
        products = data.get('products')
        budget_constraint = data.get('budget_constraint')
        warehouse_capacity = data.get('warehouse_capacity')
        
        # Ejecutar optimización
        result = inventory_optimization_service.optimize_inventory(
            products, budget_constraint, warehouse_capacity
        )
        
        if not result.solution:
            return jsonify({'error': 'No se pudo encontrar una solución óptima'}), 400
        
        # Generar recomendaciones
        recommendations = inventory_optimization_service.get_optimization_recommendations(result)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'optimization_result': {
                'total_cost': result.total_cost,
                'total_value': result.total_value,
                'service_level': result.service_level,
                'iterations': result.iterations,
                'convergence_time': result.convergence_time
            }
        })
        
    except Exception as e:
        logger.error(f'Error generando recomendaciones: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== ANÁLISIS AVANZADO ====================

@ml_bp.route('/analytics/abc-detailed', methods=['GET'])
def get_detailed_abc_analysis():
    """Obtiene análisis ABC detallado"""
    try:
        days_back = request.args.get('days', 90, type=int)
        
        analysis = advanced_analytics_service.analyze_product_performance(days_back)
        
        if 'error' in analysis:
            return jsonify({'error': analysis['error']}), 400
        
        abc_data = analysis.get('abc_analysis', {})
        
        return jsonify({
            'success': True,
            'abc_analysis': abc_data,
            'analysis_period': analysis.get('analysis_period'),
            'total_products_analyzed': analysis.get('total_products_analyzed')
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo análisis ABC detallado: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ml_bp.route('/analytics/clustering-detailed', methods=['GET'])
def get_detailed_clustering():
    """Obtiene análisis de clustering detallado"""
    try:
        days_back = request.args.get('days', 90, type=int)
        
        analysis = advanced_analytics_service.analyze_product_performance(days_back)
        
        if 'error' in analysis:
            return jsonify({'error': analysis['error']}), 400
        
        clustering_data = analysis.get('clusters', {})
        
        return jsonify({
            'success': True,
            'clustering': clustering_data,
            'analysis_period': analysis.get('analysis_period'),
            'total_products_analyzed': analysis.get('total_products_analyzed')
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo clustering detallado: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ml_bp.route('/analytics/correlations-detailed', methods=['GET'])
def get_detailed_correlations():
    """Obtiene análisis de correlaciones detallado"""
    try:
        days_back = request.args.get('days', 90, type=int)
        
        analysis = advanced_analytics_service.analyze_product_performance(days_back)
        
        if 'error' in analysis:
            return jsonify({'error': analysis['error']}), 400
        
        correlations_data = analysis.get('correlations', {})
        
        return jsonify({
            'success': True,
            'correlations': correlations_data,
            'analysis_period': analysis.get('analysis_period'),
            'total_products_analyzed': analysis.get('total_products_analyzed')
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo correlaciones detalladas: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== DASHBOARD AVANZADO ====================

@ml_bp.route('/dashboard/ml-insights', methods=['GET'])
def get_ml_insights():
    """Obtiene insights de machine learning para el dashboard"""
    try:
        # Obtener productos con más ventas para entrenar modelos
        top_products = db.session.query(SalesRecord.product_id, 
                                      db.func.sum(SalesRecord.quantity_sold).label('total_sold'))\
            .group_by(SalesRecord.product_id)\
            .order_by(db.func.sum(SalesRecord.quantity_sold).desc())\
            .limit(5).all()
        
        insights = []
        
        for product_id, total_sold in top_products:
            product = Product.query.get(product_id)
            if not product:
                continue
            
            # Predecir demanda
            prediction = advanced_ml_service.predict_demand(product_id, 30)
            
            if 'error' not in prediction:
                insights.append({
                    'product_id': product_id,
                    'product_name': product.name,
                    'predicted_demand_30_days': prediction['total_predicted_demand'],
                    'average_daily_demand': prediction['average_daily_demand'],
                    'model_confidence': prediction['confidence'],
                    'model_used': prediction['model_used']
                })
        
        return jsonify({
            'success': True,
            'ml_insights': insights,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo insights de ML: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ml_bp.route('/dashboard/optimization-summary', methods=['GET'])
def get_optimization_summary():
    """Obtiene resumen de optimización para el dashboard"""
    try:
        # Obtener productos críticos (bajo stock)
        critical_products = Product.query.filter(
            Product.min_stock_level > 0
        ).limit(10).all()
        
        product_ids = [p.id for p in critical_products]
        
        if not product_ids:
            return jsonify({
                'success': True,
                'optimization_summary': {
                    'message': 'No hay productos críticos para optimizar'
                }
            })
        
        # Ejecutar optimización rápida
        result = inventory_optimization_service.optimize_inventory(
            product_ids, 
            budget_constraint=100000,  # $100,000
            warehouse_capacity=1000     # 1000 unidades
        )
        
        if not result.solution:
            return jsonify({
                'success': True,
                'optimization_summary': {
                    'message': 'No se pudo optimizar con los parámetros dados'
                }
            })
        
        # Generar recomendaciones
        recommendations = inventory_optimization_service.get_optimization_recommendations(result)
        
        return jsonify({
            'success': True,
            'optimization_summary': {
                'total_cost': result.total_cost,
                'total_value': result.total_value,
                'service_level': result.service_level,
                'recommendations_count': len(recommendations),
                'high_priority_recommendations': len([r for r in recommendations if r['priority'] == 'high']),
                'estimated_savings': sum(r['estimated_cost'] for r in recommendations if r['action'] == 'decrease'),
                'convergence_time': result.convergence_time
            }
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo resumen de optimización: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== CONFIGURACIÓN DE MODELOS ====================

@ml_bp.route('/ml/config', methods=['GET'])
def get_ml_config():
    """Obtiene configuración de modelos ML"""
    try:
        config = {
            'algorithms_available': [
                'RandomForest',
                'GradientBoosting', 
                'LinearRegression',
                'Ridge',
                'Lasso',
                'SVR'
            ],
            'optimization_parameters': {
                'population_size': inventory_optimization_service.population_size,
                'generations': inventory_optimization_service.generations,
                'mutation_rate': inventory_optimization_service.mutation_rate,
                'crossover_rate': inventory_optimization_service.crossover_rate,
                'service_level_target': inventory_optimization_service.service_level_target
            },
            'feature_engineering': {
                'time_features': True,
                'lag_features': True,
                'rolling_features': True,
                'seasonal_features': True
            },
            'constraints': {
                'budget_constraint': True,
                'warehouse_capacity': True,
                'min_max_stock': True
            }
        }
        
        return jsonify({
            'success': True,
            'config': config
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo configuración ML: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ml_bp.route('/ml/config', methods=['POST'])
def update_ml_config():
    """Actualiza configuración de modelos ML"""
    try:
        data = request.get_json() or {}
        
        # Actualizar parámetros de optimización
        if 'optimization_parameters' in data:
            params = data['optimization_parameters']
            
            if 'population_size' in params:
                inventory_optimization_service.population_size = params['population_size']
            if 'generations' in params:
                inventory_optimization_service.generations = params['generations']
            if 'mutation_rate' in params:
                inventory_optimization_service.mutation_rate = params['mutation_rate']
            if 'crossover_rate' in params:
                inventory_optimization_service.crossover_rate = params['crossover_rate']
            if 'service_level_target' in params:
                inventory_optimization_service.service_level_target = params['service_level_target']
        
        return jsonify({
            'success': True,
            'message': 'Configuración actualizada exitosamente'
        })
        
    except Exception as e:
        logger.error(f'Error actualizando configuración ML: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500



