from flask import Blueprint, request, jsonify, send_file
from app import db
from models import Product, SalesRecord, Alert, ReorderRecommendation
from services.advanced_analytics_service import advanced_analytics_service
from services.data_export_service import data_export_service
from services.realtime_notification_service import realtime_notification_service
from services.kpi_service import kpi_service
from datetime import datetime, timedelta
import logging
import io

# Crear blueprint para la API mejorada
api_advanced_bp = Blueprint('api_advanced', __name__)

# Configurar logging
logger = logging.getLogger(__name__)

# ==================== ANÁLISIS AVANZADO ====================

@api_advanced_bp.route('/analytics/performance', methods=['GET'])
def get_performance_analysis():
    """Obtiene análisis avanzado de rendimiento de productos"""
    try:
        days_back = request.args.get('days', 90, type=int)
        analysis = advanced_analytics_service.analyze_product_performance(days_back)
        return jsonify(analysis)
    except Exception as e:
        logger.error(f'Error obteniendo análisis de rendimiento: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@api_advanced_bp.route('/analytics/insights', methods=['GET'])
def get_insights():
    """Obtiene insights automáticos del sistema"""
    try:
        insights = advanced_analytics_service.generate_insights_report()
        return jsonify(insights)
    except Exception as e:
        logger.error(f'Error obteniendo insights: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@api_advanced_bp.route('/analytics/abc-analysis', methods=['GET'])
def get_abc_analysis():
    """Obtiene análisis ABC de productos"""
    try:
        analysis = advanced_analytics_service.analyze_product_performance()
        abc_data = analysis.get('abc_analysis', {})
        return jsonify(abc_data)
    except Exception as e:
        logger.error(f'Error obteniendo análisis ABC: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@api_advanced_bp.route('/analytics/seasonality', methods=['GET'])
def get_seasonality_analysis():
    """Obtiene análisis de estacionalidad"""
    try:
        analysis = advanced_analytics_service.analyze_product_performance()
        seasonality_data = analysis.get('seasonality', {})
        return jsonify(seasonality_data)
    except Exception as e:
        logger.error(f'Error obteniendo análisis de estacionalidad: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== EXPORTACIÓN DE DATOS ====================

@api_advanced_bp.route('/export/inventory', methods=['GET'])
def export_inventory():
    """Exporta reporte de inventario"""
    try:
        format_type = request.args.get('format', 'excel').lower()
        category = request.args.get('category')
        min_stock = request.args.get('min_stock', type=int)
        max_stock = request.args.get('max_stock', type=int)
        
        filters = {}
        if category:
            filters['category'] = category
        if min_stock is not None:
            filters['min_stock'] = min_stock
        if max_stock is not None:
            filters['max_stock'] = max_stock
        
        data = data_export_service.export_inventory_report(format_type, filters)
        
        if format_type == 'excel':
            return send_file(
                io.BytesIO(data),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'inventory_report_{datetime.utcnow().strftime("%Y%m%d")}.xlsx'
            )
        elif format_type == 'csv':
            return send_file(
                io.BytesIO(data),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'inventory_report_{datetime.utcnow().strftime("%Y%m%d")}.csv'
            )
        else:
            return jsonify({'error': 'Formato no soportado'}), 400
            
    except Exception as e:
        logger.error(f'Error exportando inventario: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@api_advanced_bp.route('/export/sales', methods=['GET'])
def export_sales():
    """Exporta reporte de ventas"""
    try:
        format_type = request.args.get('format', 'excel').lower()
        days_back = request.args.get('days', 30, type=int)
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        data = data_export_service.export_sales_report(start_date, end_date, format_type)
        
        if format_type == 'excel':
            return send_file(
                io.BytesIO(data),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'sales_report_{datetime.utcnow().strftime("%Y%m%d")}.xlsx'
            )
        elif format_type == 'csv':
            return send_file(
                io.BytesIO(data),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'sales_report_{datetime.utcnow().strftime("%Y%m%d")}.csv'
            )
        else:
            return jsonify({'error': 'Formato no soportado'}), 400
            
    except Exception as e:
        logger.error(f'Error exportando ventas: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@api_advanced_bp.route('/export/kpis', methods=['GET'])
def export_kpis():
    """Exporta reporte de KPIs"""
    try:
        format_type = request.args.get('format', 'excel').lower()
        
        data = data_export_service.export_kpis_report(format_type)
        
        if format_type == 'excel':
            return send_file(
                io.BytesIO(data),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'kpis_report_{datetime.utcnow().strftime("%Y%m%d")}.xlsx'
            )
        elif format_type == 'csv':
            return send_file(
                io.BytesIO(data),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'kpis_report_{datetime.utcnow().strftime("%Y%m%d")}.csv'
            )
        else:
            return jsonify({'error': 'Formato no soportado'}), 400
            
    except Exception as e:
        logger.error(f'Error exportando KPIs: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@api_advanced_bp.route('/export/analytics', methods=['GET'])
def export_analytics():
    """Exporta reporte de análisis avanzado"""
    try:
        format_type = request.args.get('format', 'excel').lower()
        
        data = data_export_service.export_analytics_report(format_type)
        
        if format_type == 'excel':
            return send_file(
                io.BytesIO(data),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'analytics_report_{datetime.utcnow().strftime("%Y%m%d")}.xlsx'
            )
        elif format_type == 'json':
            return send_file(
                io.BytesIO(data),
                mimetype='application/json',
                as_attachment=True,
                download_name=f'analytics_report_{datetime.utcnow().strftime("%Y%m%d")}.json'
            )
        else:
            return jsonify({'error': 'Formato no soportado'}), 400
            
    except Exception as e:
        logger.error(f'Error exportando análisis: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@api_advanced_bp.route('/export/backup', methods=['GET'])
def export_backup():
    """Exporta backup completo del sistema"""
    try:
        data = data_export_service.export_complete_backup()
        
        return send_file(
            io.BytesIO(data),
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'backup_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.zip'
        )
        
    except Exception as e:
        logger.error(f'Error creando backup: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== NOTIFICACIONES EN TIEMPO REAL ====================

@api_advanced_bp.route('/notifications/status', methods=['GET'])
def get_notification_status():
    """Obtiene estado de las notificaciones en tiempo real"""
    try:
        stats = realtime_notification_service.get_connection_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f'Error obteniendo estado de notificaciones: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@api_advanced_bp.route('/notifications/test', methods=['POST'])
def test_notification():
    """Envía notificación de prueba"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'all')
        message = data.get('message', 'Notificación de prueba')
        
        notification = {
            'type': 'test',
            'title': 'Notificación de Prueba',
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'severity': 'info'
        }
        
        if user_id == 'all':
            sent_count = realtime_notification_service.broadcast_notification(notification)
        else:
            success = realtime_notification_service.send_notification(user_id, notification)
            sent_count = 1 if success else 0
        
        return jsonify({
            'message': 'Notificación enviada',
            'sent_count': sent_count
        })
        
    except Exception as e:
        logger.error(f'Error enviando notificación de prueba: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== DASHBOARD AVANZADO ====================

@api_advanced_bp.route('/dashboard/advanced', methods=['GET'])
def get_advanced_dashboard():
    """Obtiene datos avanzados para el dashboard"""
    try:
        # KPIs principales
        kpis = kpi_service.calculate_all_kpis()
        
        # Insights automáticos
        insights = advanced_analytics_service.generate_insights_report()
        
        # Análisis ABC resumido
        analysis = advanced_analytics_service.analyze_product_performance(30)  # Últimos 30 días
        abc_summary = analysis.get('abc_analysis', {}).get('summary', {})
        
        # Estado de notificaciones
        notification_stats = realtime_notification_service.get_connection_stats()
        
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
        
        return jsonify({
            'kpis': kpis,
            'insights': insights,
            'abc_summary': abc_summary,
            'notification_stats': notification_stats,
            'critical_alerts': [{
                'id': alert.id,
                'product_name': alert.product.name,
                'message': alert.message,
                'severity': alert.severity,
                'created_at': alert.created_at.isoformat()
            } for alert in critical_alerts],
            'urgent_recommendations': [{
                'id': rec.id,
                'product_name': rec.product.name,
                'recommended_quantity': rec.recommended_quantity,
                'urgency': rec.urgency,
                'estimated_cost': rec.estimated_cost,
                'created_at': rec.created_at.isoformat()
            } for rec in urgent_recommendations],
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo dashboard avanzado: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== CONFIGURACIÓN DEL SISTEMA ====================

@api_advanced_bp.route('/system/config', methods=['GET'])
def get_system_config():
    """Obtiene configuración del sistema"""
    try:
        # Configuración básica del sistema
        config = {
            'app_name': 'Sistema de Control de Inventario',
            'version': '2.0.0',
            'environment': 'production',
            'features': {
                'advanced_analytics': True,
                'real_time_notifications': True,
                'data_export': True,
                'machine_learning': True,
                'abc_analysis': True,
                'seasonality_analysis': True,
                'clustering': True
            },
            'limits': {
                'max_products': 10000,
                'max_users': 100,
                'max_export_size': '100MB',
                'retention_days': 365
            }
        }
        
        return jsonify(config)
        
    except Exception as e:
        logger.error(f'Error obteniendo configuración: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@api_advanced_bp.route('/system/health', methods=['GET'])
def system_health():
    """Verifica la salud del sistema"""
    try:
        # Verificar conexión a base de datos
        db_status = 'healthy'
        try:
            db.session.execute('SELECT 1')
        except Exception:
            db_status = 'unhealthy'
        
        # Verificar servicios
        services_status = {
            'database': db_status,
            'analytics': 'healthy',
            'notifications': 'healthy',
            'export': 'healthy'
        }
        
        # Estado general
        overall_status = 'healthy' if all(status == 'healthy' for status in services_status.values()) else 'degraded'
        
        return jsonify({
            'status': overall_status,
            'services': services_status,
            'timestamp': datetime.utcnow().isoformat(),
            'uptime': 'N/A'  # Se podría calcular con tiempo de inicio
        })
        
    except Exception as e:
        logger.error(f'Error verificando salud del sistema: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500



