from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from models import Product, InventoryRecord, Alert, SalesRecord, ReorderRecommendation
from services.alert_service import alert_system
from services.forecasting_service import demand_forecasting_service
from services.replenishment_service import replenishment_service
from services.kpi_service import kpi_service
from datetime import datetime, timedelta
import logging

# Crear blueprint para las rutas principales
main_bp = Blueprint('main', __name__)

# Configurar logging
logger = logging.getLogger(__name__)

@main_bp.route('/')
def dashboard():
    """Dashboard principal"""
    try:
        # Obtener estadísticas para el dashboard
        total_products = Product.query.count()
        active_alerts_count = Alert.query.filter(Alert.is_resolved == False).count()
        pending_recommendations = ReorderRecommendation.query.filter(
            ReorderRecommendation.is_processed == False
        ).count()
        
        # Ventas de hoy
        today = datetime.utcnow().date()
        today_sales = SalesRecord.query.filter(
            db.func.date(SalesRecord.sale_date) == today
        ).all()
        
        today_revenue = sum(sale.total_amount for sale in today_sales)
        
        # Alertas críticas
        critical_alerts = Alert.query.filter(
            Alert.is_resolved == False,
            Alert.severity == 'critical'
        ).limit(5).all()
        
        # Recomendaciones urgentes
        urgent_recommendations = ReorderRecommendation.query.filter(
            ReorderRecommendation.is_processed == False,
            ReorderRecommendation.urgency.in_(['critical', 'high'])
        ).limit(5).all()
        
        return render_template('dashboard.html',
                             total_products=total_products,
                             active_alerts_count=active_alerts_count,
                             pending_recommendations=pending_recommendations,
                             today_revenue=today_revenue,
                             today_sales_count=len(today_sales),
                             critical_alerts=critical_alerts,
                             urgent_recommendations=urgent_recommendations)
    except Exception as e:
        logger.error(f'Error cargando dashboard: {str(e)}')
        flash('Error cargando el dashboard', 'error')
        return render_template('dashboard.html')

@main_bp.route('/products')
def products():
    """Página de productos"""
    try:
        products = Product.query.all()
        return render_template('products.html', products=products)
    except Exception as e:
        logger.error(f'Error cargando productos: {str(e)}')
        flash('Error cargando productos', 'error')
        return render_template('products.html', products=[])

@main_bp.route('/inventory')
def inventory():
    """Página de inventario"""
    try:
        products = Product.query.all()
        inventory_data = []
        
        for product in products:
            current_stock = alert_system.get_current_stock(product.id)
            inventory_data.append({
                'product': product,
                'current_stock': current_stock,
                'status': 'low' if current_stock <= product.min_stock_level else 'normal'
            })
        
        return render_template('inventory.html', inventory_data=inventory_data)
    except Exception as e:
        logger.error(f'Error cargando inventario: {str(e)}')
        flash('Error cargando inventario', 'error')
        return render_template('inventory.html', inventory_data=[])

@main_bp.route('/alerts')
def alerts():
    """Página de alertas"""
    try:
        severity_filter = request.args.get('severity')
        alerts = alert_system.get_active_alerts(severity_filter)
        return render_template('alerts.html', alerts=alerts)
    except Exception as e:
        logger.error(f'Error cargando alertas: {str(e)}')
        flash('Error cargando alertas', 'error')
        return render_template('alerts.html', alerts=[])

@main_bp.route('/forecasts')
def forecasts():
    """Página de predicciones"""
    try:
        products = Product.query.all()
        forecasts_summary = demand_forecasting_service.get_forecast_summary()
        return render_template('forecasts.html', 
                             products=products,
                             forecasts_summary=forecasts_summary)
    except Exception as e:
        logger.error(f'Error cargando predicciones: {str(e)}')
        flash('Error cargando predicciones', 'error')
        return render_template('forecasts.html', products=[], forecasts_summary={})

@main_bp.route('/replenishment')
def replenishment():
    """Página de reposición"""
    try:
        recommendations = replenishment_service.generate_reorder_recommendations()
        replenishment_summary = replenishment_service.get_reorder_summary()
        return render_template('replenishment.html',
                             recommendations=recommendations,
                             summary=replenishment_summary)
    except Exception as e:
        logger.error(f'Error cargando reposición: {str(e)}')
        flash('Error cargando recomendaciones de reposición', 'error')
        return render_template('replenishment.html', recommendations=[], summary={})

@main_bp.route('/kpis')
def kpis():
    """Página de KPIs"""
    try:
        kpis_data = kpi_service.calculate_all_kpis()
        kpi_trends = kpi_service.get_kpi_trends(30)
        return render_template('kpis.html', kpis=kpis_data, trends=kpi_trends)
    except Exception as e:
        logger.error(f'Error cargando KPIs: {str(e)}')
        flash('Error cargando KPIs', 'error')
        return render_template('kpis.html', kpis={}, trends={})

@main_bp.route('/suppliers')
def suppliers():
    """Página de proveedores"""
    try:
        from models import Supplier
        suppliers = Supplier.query.all()
        return render_template('suppliers.html', suppliers=suppliers)
    except Exception as e:
        logger.error(f'Error cargando proveedores: {str(e)}')
        flash('Error cargando proveedores', 'error')
        return render_template('suppliers.html', suppliers=[])

@main_bp.route('/sales')
def sales():
    """Página de ventas"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        sales = SalesRecord.query.filter(
            SalesRecord.sale_date >= start_date
        ).order_by(SalesRecord.sale_date.desc()).all()
        
        return render_template('sales.html', sales=sales, days=days)
    except Exception as e:
        logger.error(f'Error cargando ventas: {str(e)}')
        flash('Error cargando ventas', 'error')
        return render_template('sales.html', sales=[], days=30)

@main_bp.route('/analytics')
def analytics():
    """Página de análisis avanzado"""
    return render_template('analytics.html')

@main_bp.route('/ml-optimization')
def ml_optimization():
    """Página de machine learning y optimización"""
    return render_template('ml_optimization.html')

@main_bp.route('/realtime-dashboard')
def realtime_dashboard():
    """Dashboard en tiempo real"""
    return render_template('realtime_dashboard.html')

@main_bp.route('/admin-monitoring')
def admin_monitoring():
    """Página de monitoreo y administración"""
    return render_template('admin_monitoring.html')

@main_bp.route('/ai-blockchain')
def ai_blockchain():
    """Página de IA avanzada y blockchain"""
    return render_template('ai_blockchain.html')

@main_bp.route('/iot-ar')
def iot_ar():
    """Página de IoT y realidad aumentada"""
    return render_template('iot_ar.html')

@main_bp.route('/predictive-logistics')
def predictive_logistics():
    """Página de análisis predictivo y logística"""
    return render_template('predictive_logistics.html')

@main_bp.route('/quality-sustainability')
def quality_sustainability():
    """Página de calidad y sostenibilidad"""
    return render_template('quality_sustainability.html')

@main_bp.route('/reports')
def reports():
    """Página de reportes"""
    try:
        # Obtener datos para reportes
        kpis = kpi_service.calculate_all_kpis()
        return render_template('reports.html', kpis=kpis)
    except Exception as e:
        logger.error(f'Error cargando reportes: {str(e)}')
        flash('Error cargando reportes', 'error')
        return render_template('reports.html', kpis={})

# ==================== ACCIONES ====================

@main_bp.route('/resolve_alert/<int:alert_id>', methods=['POST'])
def resolve_alert(alert_id):
    """Resuelve una alerta"""
    try:
        success = alert_system.resolve_alert(alert_id)
        if success:
            flash('Alerta resuelta exitosamente', 'success')
        else:
            flash('Error resolviendo alerta', 'error')
    except Exception as e:
        logger.error(f'Error resolviendo alerta {alert_id}: {str(e)}')
        flash('Error resolviendo alerta', 'error')
    
    return redirect(url_for('main.alerts'))

@main_bp.route('/process_recommendation/<int:recommendation_id>', methods=['POST'])
def process_recommendation(recommendation_id):
    """Procesa una recomendación de reposición"""
    try:
        success = replenishment_service.process_reorder_recommendation(recommendation_id)
        if success:
            flash('Recomendación procesada exitosamente', 'success')
        else:
            flash('Error procesando recomendación', 'error')
    except Exception as e:
        logger.error(f'Error procesando recomendación {recommendation_id}: {str(e)}')
        flash('Error procesando recomendación', 'error')
    
    return redirect(url_for('main.replenishment'))

@main_bp.route('/add_inventory_movement', methods=['POST'])
def add_inventory_movement():
    """Añade un movimiento de inventario"""
    try:
        product_id = request.form.get('product_id', type=int)
        quantity = request.form.get('quantity', type=int)
        movement_type = request.form.get('movement_type')
        reference = request.form.get('reference', '')
        notes = request.form.get('notes', '')
        
        movement = InventoryRecord(
            product_id=product_id,
            quantity=quantity,
            movement_type=movement_type,
            reference=reference,
            notes=notes
        )
        
        db.session.add(movement)
        db.session.commit()
        
        # Verificar alertas después del movimiento
        alert_system.check_low_stock_alerts()
        
        flash('Movimiento de inventario registrado exitosamente', 'success')
        
    except Exception as e:
        logger.error(f'Error añadiendo movimiento de inventario: {str(e)}')
        db.session.rollback()
        flash('Error registrando movimiento de inventario', 'error')
    
    return redirect(url_for('main.inventory'))

@main_bp.route('/record_sale', methods=['POST'])
def record_sale():
    """Registra una venta"""
    try:
        product_id = request.form.get('product_id', type=int)
        quantity_sold = request.form.get('quantity_sold', type=int)
        unit_price = request.form.get('unit_price', type=float)
        sale_date = request.form.get('sale_date')
        customer_id = request.form.get('customer_id', type=int)
        
        sale = SalesRecord(
            product_id=product_id,
            quantity_sold=quantity_sold,
            sale_date=datetime.fromisoformat(sale_date),
            unit_price=unit_price,
            total_amount=quantity_sold * unit_price,
            customer_id=customer_id
        )
        
        db.session.add(sale)
        
        # Registrar salida de inventario
        inventory_movement = InventoryRecord(
            product_id=product_id,
            quantity=quantity_sold,
            movement_type='out',
            reference=f'Sale-{sale.id}',
            notes='Venta registrada'
        )
        
        db.session.add(inventory_movement)
        db.session.commit()
        
        # Verificar alertas después de la venta
        alert_system.check_low_stock_alerts()
        
        flash('Venta registrada exitosamente', 'success')
        
    except Exception as e:
        logger.error(f'Error registrando venta: {str(e)}')
        db.session.rollback()
        flash('Error registrando venta', 'error')
    
    return redirect(url_for('main.sales'))

# ==================== AJAX ENDPOINTS ====================

@main_bp.route('/api/get_product_forecast/<int:product_id>')
def get_product_forecast(product_id):
    """Obtiene predicción para un producto específico (AJAX)"""
    try:
        days = request.args.get('days', 30, type=int)
        forecast = demand_forecasting_service.forecast_demand(product_id, days)
        return jsonify(forecast)
    except Exception as e:
        logger.error(f'Error obteniendo predicción para producto {product_id}: {str(e)}')
        return jsonify({'error': 'Error obteniendo predicción'}), 500

@main_bp.route('/api/check_alerts', methods=['POST'])
def check_alerts_ajax():
    """Verifica alertas manualmente (AJAX)"""
    try:
        alerts_created = alert_system.check_low_stock_alerts()
        return jsonify({'message': f'Se crearon {alerts_created} alertas'})
    except Exception as e:
        logger.error(f'Error verificando alertas: {str(e)}')
        return jsonify({'error': 'Error verificando alertas'}), 500
