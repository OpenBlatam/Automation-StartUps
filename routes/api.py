from flask import Blueprint, request, jsonify
from app import db
from models import Product, InventoryRecord, Alert, SalesRecord, ReorderRecommendation, KPIMetric
from services.alert_service import alert_system
from services.forecasting_service import demand_forecasting_service
from services.replenishment_service import replenishment_service
from services.kpi_service import kpi_service
from datetime import datetime, timedelta
import logging

# Crear blueprint para la API
api_bp = Blueprint('api', __name__)

# Configurar logging
logger = logging.getLogger(__name__)

# ==================== PRODUCTOS ====================

@api_bp.route('/products', methods=['GET'])
def get_products():
    """Obtiene todos los productos"""
    try:
        products = Product.query.all()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'sku': p.sku,
            'description': p.description,
            'category': p.category,
            'unit_price': p.unit_price,
            'cost_price': p.cost_price,
            'min_stock_level': p.min_stock_level,
            'max_stock_level': p.max_stock_level,
            'reorder_point': p.reorder_point,
            'supplier_id': p.supplier_id,
            'supplier_name': p.supplier.name if p.supplier else None,
            'current_stock': alert_system.get_current_stock(p.id)
        } for p in products])
    except Exception as e:
        logger.error(f'Error obteniendo productos: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@api_bp.route('/products', methods=['POST'])
def create_product():
    """Crea un nuevo producto"""
    try:
        data = request.get_json()
        
        product = Product(
            name=data['name'],
            sku=data['sku'],
            description=data.get('description', ''),
            category=data.get('category', ''),
            unit_price=data['unit_price'],
            cost_price=data['cost_price'],
            min_stock_level=data.get('min_stock_level', 10),
            max_stock_level=data.get('max_stock_level', 100),
            reorder_point=data.get('reorder_point', 20),
            supplier_id=data.get('supplier_id')
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({'id': product.id, 'message': 'Producto creado exitosamente'}), 201
        
    except Exception as e:
        logger.error(f'Error creando producto: {str(e)}')
        db.session.rollback()
        return jsonify({'error': 'Error creando producto'}), 500

@api_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Obtiene un producto específico"""
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify({
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'description': product.description,
            'category': product.category,
            'unit_price': product.unit_price,
            'cost_price': product.cost_price,
            'min_stock_level': product.min_stock_level,
            'max_stock_level': product.max_stock_level,
            'reorder_point': product.reorder_point,
            'supplier_id': product.supplier_id,
            'supplier_name': product.supplier.name if product.supplier else None,
            'current_stock': alert_system.get_current_stock(product.id)
        })
    except Exception as e:
        logger.error(f'Error obteniendo producto {product_id}: {str(e)}')
        return jsonify({'error': 'Producto no encontrado'}), 404

# ==================== INVENTARIO ====================

@api_bp.route('/inventory', methods=['GET'])
def get_inventory():
    """Obtiene estado actual del inventario"""
    try:
        products = Product.query.all()
        inventory = []
        
        for product in products:
            current_stock = alert_system.get_current_stock(product.id)
            inventory.append({
                'product_id': product.id,
                'product_name': product.name,
                'sku': product.sku,
                'current_stock': current_stock,
                'min_stock_level': product.min_stock_level,
                'max_stock_level': product.max_stock_level,
                'reorder_point': product.reorder_point,
                'status': 'low' if current_stock <= product.min_stock_level else 'normal',
                'value': current_stock * product.unit_price
            })
        
        return jsonify(inventory)
    except Exception as e:
        logger.error(f'Error obteniendo inventario: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@api_bp.route('/inventory/movements', methods=['POST'])
def record_inventory_movement():
    """Registra un movimiento de inventario"""
    try:
        data = request.get_json()
        
        movement = InventoryRecord(
            product_id=data['product_id'],
            quantity=data['quantity'],
            movement_type=data['movement_type'],  # 'in', 'out', 'adjustment'
            reference=data.get('reference', ''),
            notes=data.get('notes', '')
        )
        
        db.session.add(movement)
        db.session.commit()
        
        # Verificar alertas después del movimiento
        alert_system.check_low_stock_alerts()
        
        return jsonify({'id': movement.id, 'message': 'Movimiento registrado exitosamente'}), 201
        
    except Exception as e:
        logger.error(f'Error registrando movimiento: {str(e)}')
        db.session.rollback()
        return jsonify({'error': 'Error registrando movimiento'}), 500

# ==================== ALERTAS ====================

@api_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Obtiene todas las alertas"""
    try:
        severity = request.args.get('severity')
        alerts = alert_system.get_active_alerts(severity)
        
        return jsonify([{
            'id': alert.id,
            'product_id': alert.product_id,
            'product_name': alert.product.name,
            'alert_type': alert.alert_type,
            'message': alert.message,
            'severity': alert.severity,
            'is_read': alert.is_read,
            'is_resolved': alert.is_resolved,
            'created_at': alert.created_at.isoformat(),
            'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None
        } for alert in alerts])
    except Exception as e:
        logger.error(f'Error obteniendo alertas: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@api_bp.route('/alerts/<int:alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    """Marca una alerta como resuelta"""
    try:
        success = alert_system.resolve_alert(alert_id)
        if success:
            return jsonify({'message': 'Alerta resuelta exitosamente'})
        else:
            return jsonify({'error': 'Alerta no encontrada'}), 404
    except Exception as e:
        logger.error(f'Error resolviendo alerta {alert_id}: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@api_bp.route('/alerts/check', methods=['POST'])
def check_alerts():
    """Ejecuta verificación manual de alertas"""
    try:
        alerts_created = alert_system.check_low_stock_alerts()
        return jsonify({'message': f'Se crearon {alerts_created} alertas'})
    except Exception as e:
        logger.error(f'Error verificando alertas: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== PREDICCIONES ====================

@api_bp.route('/forecasts/<int:product_id>', methods=['GET'])
def get_forecast(product_id):
    """Obtiene predicción de demanda para un producto"""
    try:
        days_ahead = request.args.get('days', 30, type=int)
        method = request.args.get('method', 'auto')
        
        forecast = demand_forecasting_service.forecast_demand(product_id, days_ahead, method)
        return jsonify(forecast)
    except Exception as e:
        logger.error(f'Error obteniendo predicción para producto {product_id}: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@api_bp.route('/forecasts', methods=['GET'])
def get_all_forecasts():
    """Obtiene resumen de todas las predicciones"""
    try:
        summary = demand_forecasting_service.get_forecast_summary()
        return jsonify(summary)
    except Exception as e:
        logger.error(f'Error obteniendo resumen de predicciones: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== REPOSICIÓN ====================

@api_bp.route('/replenishment/recommendations', methods=['GET'])
def get_reorder_recommendations():
    """Obtiene recomendaciones de reposición"""
    try:
        recommendations = replenishment_service.generate_reorder_recommendations()
        return jsonify(recommendations)
    except Exception as e:
        logger.error(f'Error obteniendo recomendaciones: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@api_bp.route('/replenishment/recommendations/<int:recommendation_id>/process', methods=['POST'])
def process_recommendation(recommendation_id):
    """Procesa una recomendación de reposición"""
    try:
        success = replenishment_service.process_reorder_recommendation(recommendation_id)
        if success:
            return jsonify({'message': 'Recomendación procesada exitosamente'})
        else:
            return jsonify({'error': 'Recomendación no encontrada'}), 404
    except Exception as e:
        logger.error(f'Error procesando recomendación {recommendation_id}: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== KPIs ====================

@api_bp.route('/kpis', methods=['GET'])
def get_kpis():
    """Obtiene todos los KPIs"""
    try:
        kpis = kpi_service.calculate_all_kpis()
        return jsonify(kpis)
    except Exception as e:
        logger.error(f'Error obteniendo KPIs: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@api_bp.route('/kpis/trends', methods=['GET'])
def get_kpi_trends():
    """Obtiene tendencias de KPIs"""
    try:
        days = request.args.get('days', 30, type=int)
        trends = kpi_service.get_kpi_trends(days)
        return jsonify(trends)
    except Exception as e:
        logger.error(f'Error obteniendo tendencias de KPIs: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== VENTAS ====================

@api_bp.route('/sales', methods=['POST'])
def record_sale():
    """Registra una venta"""
    try:
        data = request.get_json()
        
        sale = SalesRecord(
            product_id=data['product_id'],
            quantity_sold=data['quantity_sold'],
            sale_date=datetime.fromisoformat(data['sale_date']),
            unit_price=data['unit_price'],
            total_amount=data['quantity_sold'] * data['unit_price'],
            customer_id=data.get('customer_id')
        )
        
        db.session.add(sale)
        
        # Registrar salida de inventario
        inventory_movement = InventoryRecord(
            product_id=data['product_id'],
            quantity=data['quantity_sold'],
            movement_type='out',
            reference=f'Sale-{sale.id}',
            notes='Venta registrada'
        )
        
        db.session.add(inventory_movement)
        db.session.commit()
        
        # Verificar alertas después de la venta
        alert_system.check_low_stock_alerts()
        
        return jsonify({'id': sale.id, 'message': 'Venta registrada exitosamente'}), 201
        
    except Exception as e:
        logger.error(f'Error registrando venta: {str(e)}')
        db.session.rollback()
        return jsonify({'error': 'Error registrando venta'}), 500

@api_bp.route('/sales', methods=['GET'])
def get_sales():
    """Obtiene registros de ventas"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        sales = SalesRecord.query.filter(
            SalesRecord.sale_date >= start_date
        ).order_by(SalesRecord.sale_date.desc()).all()
        
        return jsonify([{
            'id': sale.id,
            'product_id': sale.product_id,
            'product_name': sale.product.name,
            'quantity_sold': sale.quantity_sold,
            'sale_date': sale.sale_date.isoformat(),
            'unit_price': sale.unit_price,
            'total_amount': sale.total_amount,
            'customer_id': sale.customer_id
        } for sale in sales])
    except Exception as e:
        logger.error(f'Error obteniendo ventas: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== DASHBOARD ====================

@api_bp.route('/dashboard/summary', methods=['GET'])
def get_dashboard_summary():
    """Obtiene resumen para el dashboard"""
    try:
        # Obtener estadísticas rápidas
        total_products = Product.query.count()
        active_alerts = Alert.query.filter(Alert.is_resolved == False).count()
        pending_recommendations = ReorderRecommendation.query.filter(
            ReorderRecommendation.is_processed == False
        ).count()
        
        # Ventas de hoy
        today = datetime.utcnow().date()
        today_sales = SalesRecord.query.filter(
            db.func.date(SalesRecord.sale_date) == today
        ).all()
        
        today_revenue = sum(sale.total_amount for sale in today_sales)
        
        return jsonify({
            'total_products': total_products,
            'active_alerts': active_alerts,
            'pending_recommendations': pending_recommendations,
            'today_revenue': round(today_revenue, 2),
            'today_sales_count': len(today_sales)
        })
    except Exception as e:
        logger.error(f'Error obteniendo resumen del dashboard: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500



