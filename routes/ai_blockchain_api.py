from flask import Blueprint, request, jsonify
from app import db
from models import Product, SalesRecord, InventoryRecord
from services.advanced_ai_service import advanced_ai_service
from services.blockchain_service import blockchain_service, TransactionType
from datetime import datetime, timedelta
import logging
import json

# Crear blueprint para IA avanzada y blockchain
ai_blockchain_bp = Blueprint('ai_blockchain', __name__)

# Configurar logging
logger = logging.getLogger(__name__)

# ==================== INTELIGENCIA ARTIFICIAL AVANZADA ====================

@ai_blockchain_bp.route('/ai/train-deep-models', methods=['POST'])
def train_deep_learning_models():
    """Entrena modelos de deep learning"""
    try:
        data = request.get_json() or {}
        product_id = data.get('product_id')
        
        result = advanced_ai_service.train_deep_learning_models(product_id)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'message': 'Modelos de deep learning entrenados exitosamente',
            'models_trained': result['models_trained'],
            'models': result['models']
        })
        
    except Exception as e:
        logger.error(f'Error entrenando modelos de deep learning: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ai_blockchain_bp.route('/ai/generate-insights', methods=['POST'])
def generate_ai_insights():
    """Genera insights usando IA"""
    try:
        data = request.get_json() or {}
        product_id = data.get('product_id')
        
        insights = advanced_ai_service.generate_ai_insights(product_id)
        
        insights_data = []
        for insight in insights:
            insights_data.append({
                'type': insight.type,
                'title': insight.title,
                'description': insight.description,
                'confidence': insight.confidence,
                'impact': insight.impact,
                'recommendations': insight.recommendations,
                'generated_at': insight.generated_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'insights': insights_data,
            'total_insights': len(insights_data)
        })
        
    except Exception as e:
        logger.error(f'Error generando insights de IA: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ai_blockchain_bp.route('/ai/predict/<int:product_id>', methods=['GET'])
def predict_with_ai(product_id):
    """Predice usando modelos de IA"""
    try:
        days_ahead = request.args.get('days', 30, type=int)
        
        prediction = advanced_ai_service.predict_with_ai(product_id, days_ahead)
        
        if 'error' in prediction:
            return jsonify({'error': prediction['error']}), 400
        
        return jsonify({
            'success': True,
            'prediction': prediction
        })
        
    except Exception as e:
        logger.error(f'Error prediciendo con IA: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ai_blockchain_bp.route('/ai/detect-anomalies', methods=['POST'])
def detect_anomalies():
    """Detecta anomalías usando IA"""
    try:
        data = request.get_json() or {}
        product_id = data.get('product_id')
        
        anomalies = advanced_ai_service.detect_anomalies(product_id)
        
        if 'error' in anomalies:
            return jsonify({'error': anomalies['error']}), 400
        
        return jsonify({
            'success': True,
            'anomalies': anomalies
        })
        
    except Exception as e:
        logger.error(f'Error detectando anomalías: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ai_blockchain_bp.route('/ai/model-performance', methods=['GET'])
def get_ai_model_performance():
    """Obtiene rendimiento de modelos de IA"""
    try:
        performance = advanced_ai_service.get_model_performance()
        
        if 'error' in performance:
            return jsonify({'error': performance['error']}), 400
        
        return jsonify({
            'success': True,
            'performance': performance
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo rendimiento de modelos IA: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ai_blockchain_bp.route('/ai/insights-history', methods=['GET'])
def get_ai_insights_history():
    """Obtiene historial de insights de IA"""
    try:
        insights = advanced_ai_service.get_ai_insights_history()
        
        return jsonify({
            'success': True,
            'insights': insights,
            'total_insights': len(insights)
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo historial de insights: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== BLOCKCHAIN ====================

@ai_blockchain_bp.route('/blockchain/info', methods=['GET'])
def get_blockchain_info():
    """Obtiene información de la cadena de bloques"""
    try:
        info = blockchain_service.get_chain_info()
        
        return jsonify({
            'success': True,
            'blockchain_info': info
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo información de blockchain: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ai_blockchain_bp.route('/blockchain/mine', methods=['POST'])
def mine_block():
    """Mina un nuevo bloque"""
    try:
        block = blockchain_service.mine_block()
        
        if not block:
            return jsonify({'error': 'No hay transacciones pendientes para minar'}), 400
        
        return jsonify({
            'success': True,
            'message': 'Bloque minado exitosamente',
            'block': {
                'index': block.index,
                'hash': block.hash,
                'timestamp': block.timestamp.isoformat(),
                'transactions_count': len(block.transactions)
            }
        })
        
    except Exception as e:
        logger.error(f'Error minando bloque: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ai_blockchain_bp.route('/blockchain/product-history/<int:product_id>', methods=['GET'])
def get_product_blockchain_history(product_id):
    """Obtiene historial de un producto en blockchain"""
    try:
        history = blockchain_service.get_product_history(product_id)
        
        return jsonify({
            'success': True,
            'product_id': product_id,
            'history': history,
            'total_transactions': len(history)
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo historial de producto en blockchain: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ai_blockchain_bp.route('/blockchain/supplier-history/<int:supplier_id>', methods=['GET'])
def get_supplier_blockchain_history(supplier_id):
    """Obtiene historial de un proveedor en blockchain"""
    try:
        history = blockchain_service.get_supplier_history(supplier_id)
        
        return jsonify({
            'success': True,
            'supplier_id': supplier_id,
            'history': history,
            'total_transactions': len(history)
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo historial de proveedor en blockchain: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ai_blockchain_bp.route('/blockchain/transaction/<transaction_id>', methods=['GET'])
def get_transaction_by_id(transaction_id):
    """Obtiene transacción por ID"""
    try:
        transaction = blockchain_service.get_transaction_by_id(transaction_id)
        
        if not transaction:
            return jsonify({'error': 'Transacción no encontrada'}), 404
        
        return jsonify({
            'success': True,
            'transaction': transaction
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo transacción por ID: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ai_blockchain_bp.route('/blockchain/recent-transactions', methods=['GET'])
def get_recent_transactions():
    """Obtiene transacciones recientes"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        transactions = blockchain_service.get_recent_transactions(limit)
        
        return jsonify({
            'success': True,
            'transactions': transactions,
            'total_transactions': len(transactions)
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo transacciones recientes: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ai_blockchain_bp.route('/blockchain/verify', methods=['GET'])
def verify_blockchain():
    """Verifica la integridad de la cadena"""
    try:
        is_valid = blockchain_service.verify_chain()
        
        return jsonify({
            'success': True,
            'chain_valid': is_valid,
            'message': 'Cadena válida' if is_valid else 'Cadena inválida'
        })
        
    except Exception as e:
        logger.error(f'Error verificando blockchain: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ai_blockchain_bp.route('/blockchain/export', methods=['GET'])
def export_blockchain():
    """Exporta la cadena completa"""
    try:
        chain_data = blockchain_service.export_chain()
        
        return jsonify({
            'success': True,
            'blockchain_data': chain_data
        })
        
    except Exception as e:
        logger.error(f'Error exportando blockchain: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== TRANSACCIONES BLOCKCHAIN ====================

@ai_blockchain_bp.route('/blockchain/create-product-transaction', methods=['POST'])
def create_product_transaction():
    """Crea transacción de creación de producto"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        user_id = data.get('user_id')
        
        if not product_id:
            return jsonify({'error': 'product_id es requerido'}), 400
        
        success = blockchain_service.create_product_transaction(product_id, user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Transacción de producto creada exitosamente'
            })
        else:
            return jsonify({'error': 'Error creando transacción de producto'}), 400
        
    except Exception as e:
        logger.error(f'Error creando transacción de producto: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ai_blockchain_bp.route('/blockchain/create-inventory-transaction', methods=['POST'])
def create_inventory_transaction():
    """Crea transacción de movimiento de inventario"""
    try:
        data = request.get_json()
        inventory_record_id = data.get('inventory_record_id')
        user_id = data.get('user_id')
        
        if not inventory_record_id:
            return jsonify({'error': 'inventory_record_id es requerido'}), 400
        
        inventory_record = InventoryRecord.query.get(inventory_record_id)
        if not inventory_record:
            return jsonify({'error': 'Registro de inventario no encontrado'}), 404
        
        success = blockchain_service.create_inventory_transaction(inventory_record, user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Transacción de inventario creada exitosamente'
            })
        else:
            return jsonify({'error': 'Error creando transacción de inventario'}), 400
        
    except Exception as e:
        logger.error(f'Error creando transacción de inventario: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@ai_blockchain_bp.route('/blockchain/create-sale-transaction', methods=['POST'])
def create_sale_transaction():
    """Crea transacción de venta"""
    try:
        data = request.get_json()
        sale_record_id = data.get('sale_record_id')
        user_id = data.get('user_id')
        
        if not sale_record_id:
            return jsonify({'error': 'sale_record_id es requerido'}), 400
        
        sale_record = SalesRecord.query.get(sale_record_id)
        if not sale_record:
            return jsonify({'error': 'Registro de venta no encontrado'}), 404
        
        success = blockchain_service.create_sale_transaction(sale_record, user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Transacción de venta creada exitosamente'
            })
        else:
            return jsonify({'error': 'Error creando transacción de venta'}), 400
        
    except Exception as e:
        logger.error(f'Error creando transacción de venta: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== DASHBOARD IA & BLOCKCHAIN ====================

@ai_blockchain_bp.route('/ai-blockchain/dashboard', methods=['GET'])
def get_ai_blockchain_dashboard():
    """Obtiene datos para dashboard de IA y blockchain"""
    try:
        # Información de IA
        ai_performance = advanced_ai_service.get_model_performance()
        ai_insights = advanced_ai_service.get_ai_insights_history()
        
        # Información de blockchain
        blockchain_info = blockchain_service.get_chain_info()
        recent_transactions = blockchain_service.get_recent_transactions(5)
        
        return jsonify({
            'success': True,
            'dashboard': {
                'ai': {
                    'models_trained': ai_performance.get('total_models', 0),
                    'recent_insights': len(ai_insights),
                    'performance': ai_performance.get('models', {})
                },
                'blockchain': {
                    'chain_length': blockchain_info.get('chain_length', 0),
                    'total_transactions': blockchain_info.get('total_transactions', 0),
                    'pending_transactions': blockchain_info.get('pending_transactions', 0),
                    'chain_valid': blockchain_info.get('chain_valid', False),
                    'recent_transactions': recent_transactions
                }
            }
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo dashboard IA & blockchain: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== ANÁLISIS AVANZADO ====================

@ai_blockchain_bp.route('/ai-blockchain/advanced-analysis', methods=['POST'])
def advanced_analysis():
    """Realiza análisis avanzado combinando IA y blockchain"""
    try:
        data = request.get_json() or {}
        product_id = data.get('product_id')
        analysis_type = data.get('analysis_type', 'comprehensive')
        
        results = {}
        
        if analysis_type in ['comprehensive', 'ai']:
            # Análisis con IA
            insights = advanced_ai_service.generate_ai_insights(product_id)
            predictions = advanced_ai_service.predict_with_ai(product_id, 30)
            anomalies = advanced_ai_service.detect_anomalies(product_id)
            
            results['ai_analysis'] = {
                'insights': [
                    {
                        'type': insight.type,
                        'title': insight.title,
                        'description': insight.description,
                        'confidence': insight.confidence,
                        'impact': insight.impact,
                        'recommendations': insight.recommendations
                    } for insight in insights
                ],
                'predictions': predictions,
                'anomalies': anomalies
            }
        
        if analysis_type in ['comprehensive', 'blockchain']:
            # Análisis con blockchain
            product_history = blockchain_service.get_product_history(product_id) if product_id else []
            
            results['blockchain_analysis'] = {
                'product_history': product_history,
                'total_transactions': len(product_history),
                'chain_info': blockchain_service.get_chain_info()
            }
        
        return jsonify({
            'success': True,
            'analysis_type': analysis_type,
            'results': results,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f'Error realizando análisis avanzado: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500



