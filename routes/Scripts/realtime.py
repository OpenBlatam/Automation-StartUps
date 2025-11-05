from flask import Blueprint, request, jsonify, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from app import db
from models import Product, SalesRecord, Alert, ReorderRecommendation
from services.advanced_analytics_service import advanced_analytics_service
from services.kpi_service import kpi_service
from services.realtime_notification_service import realtime_notification_service
from datetime import datetime, timedelta
import logging
import json

# Crear blueprint para dashboard en tiempo real
realtime_bp = Blueprint('realtime', __name__)

# Configurar logging
logger = logging.getLogger(__name__)

# Inicializar SocketIO
socketio = SocketIO(cors_allowed_origins="*")

@realtime_bp.route('/realtime-dashboard')
def realtime_dashboard():
    """Dashboard en tiempo real con WebSockets"""
    return render_template('realtime_dashboard.html')

@socketio.on('connect')
def handle_connect():
    """Maneja la conexión de WebSocket"""
    logger.info(f'Cliente conectado: {request.sid}')
    emit('status', {'message': 'Conectado al dashboard en tiempo real'})

@socketio.on('disconnect')
def handle_disconnect():
    """Maneja la desconexión de WebSocket"""
    logger.info(f'Cliente desconectado: {request.sid}')

@socketio.on('join_dashboard')
def handle_join_dashboard(data):
    """Maneja la unión al dashboard"""
    room = 'dashboard'
    join_room(room)
    logger.info(f'Cliente {request.sid} se unió al dashboard')
    emit('status', {'message': 'Unido al dashboard en tiempo real'}, room=room)

@socketio.on('leave_dashboard')
def handle_leave_dashboard(data):
    """Maneja la salida del dashboard"""
    room = 'dashboard'
    leave_room(room)
    logger.info(f'Cliente {request.sid} salió del dashboard')

@socketio.on('request_kpis')
def handle_request_kpis():
    """Envía KPIs actualizados"""
    try:
        kpis = kpi_service.calculate_all_kpis()
        emit('kpis_update', kpis)
    except Exception as e:
        logger.error(f'Error enviando KPIs: {str(e)}')
        emit('error', {'message': 'Error obteniendo KPIs'})

@socketio.on('request_alerts')
def handle_request_alerts():
    """Envía alertas actualizadas"""
    try:
        alerts = Alert.query.filter(Alert.is_resolved == False).limit(10).all()
        alerts_data = [{
            'id': alert.id,
            'product_name': alert.product.name,
            'message': alert.message,
            'severity': alert.severity,
            'created_at': alert.created_at.isoformat()
        } for alert in alerts]
        emit('alerts_update', alerts_data)
    except Exception as e:
        logger.error(f'Error enviando alertas: {str(e)}')
        emit('error', {'message': 'Error obteniendo alertas'})

@socketio.on('request_analytics')
def handle_request_analytics():
    """Envía análisis actualizados"""
    try:
        analysis = advanced_analytics_service.analyze_product_performance(30)
        emit('analytics_update', analysis)
    except Exception as e:
        logger.error(f'Error enviando análisis: {str(e)}')
        emit('error', {'message': 'Error obteniendo análisis'})

@socketio.on('request_sales_summary')
def handle_request_sales_summary():
    """Envía resumen de ventas"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        sales = SalesRecord.query.filter(
            SalesRecord.sale_date >= start_date,
            SalesRecord.sale_date <= end_date
        ).all()
        
        summary = {
            'total_sales': len(sales),
            'total_revenue': sum(sale.total_amount for sale in sales),
            'total_quantity': sum(sale.quantity_sold for sale in sales),
            'average_ticket': sum(sale.total_amount for sale in sales) / len(sales) if sales else 0
        }
        
        emit('sales_summary_update', summary)
    except Exception as e:
        logger.error(f'Error enviando resumen de ventas: {str(e)}')
        emit('error', {'message': 'Error obteniendo resumen de ventas'})

@socketio.on('request_inventory_status')
def handle_request_inventory_status():
    """Envía estado del inventario"""
    try:
        products = Product.query.all()
        inventory_status = {
            'total_products': len(products),
            'low_stock': 0,
            'out_of_stock': 0,
            'normal_stock': 0
        }
        
        for product in products:
            # Calcular stock actual (simplificado)
            current_stock = product.current_stock if hasattr(product, 'current_stock') else 0
            
            if current_stock <= 0:
                inventory_status['out_of_stock'] += 1
            elif current_stock <= product.min_stock_level:
                inventory_status['low_stock'] += 1
            else:
                inventory_status['normal_stock'] += 1
        
        emit('inventory_status_update', inventory_status)
    except Exception as e:
        logger.error(f'Error enviando estado de inventario: {str(e)}')
        emit('error', {'message': 'Error obteniendo estado de inventario'})

def broadcast_kpis_update():
    """Broadcast de actualización de KPIs"""
    try:
        kpis = kpi_service.calculate_all_kpis()
        socketio.emit('kpis_update', kpis, room='dashboard')
    except Exception as e:
        logger.error(f'Error broadcasting KPIs: {str(e)}')

def broadcast_alert_update(alert):
    """Broadcast de nueva alerta"""
    try:
        alert_data = {
            'id': alert.id,
            'product_name': alert.product.name,
            'message': alert.message,
            'severity': alert.severity,
            'created_at': alert.created_at.isoformat()
        }
        socketio.emit('new_alert', alert_data, room='dashboard')
    except Exception as e:
        logger.error(f'Error broadcasting alerta: {str(e)}')

def broadcast_inventory_update(product_id, old_stock, new_stock):
    """Broadcast de actualización de inventario"""
    try:
        product = Product.query.get(product_id)
        if product:
            update_data = {
                'product_id': product_id,
                'product_name': product.name,
                'old_stock': old_stock,
                'new_stock': new_stock,
                'timestamp': datetime.utcnow().isoformat()
            }
            socketio.emit('inventory_update', update_data, room='dashboard')
    except Exception as e:
        logger.error(f'Error broadcasting actualización de inventario: {str(e)}')

def broadcast_system_status(status, message):
    """Broadcast de estado del sistema"""
    try:
        status_data = {
            'status': status,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        socketio.emit('system_status', status_data, room='dashboard')
    except Exception as e:
        logger.error(f'Error broadcasting estado del sistema: {str(e)}')

# Función para inicializar el sistema de tiempo real
def init_realtime_system(app):
    """Inicializa el sistema de tiempo real"""
    socketio.init_app(app)
    logger.info('Sistema de tiempo real inicializado')
    return socketio



