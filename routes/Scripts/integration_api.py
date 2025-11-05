from flask import Blueprint, request, jsonify, send_file
from app import db
from models import Product, SalesRecord, Alert
from services.integration_service import external_integration_service, backup_service
from services.monitoring_service import advanced_monitoring_service, AlertType, AlertSeverity
from datetime import datetime, timedelta
import logging
import os

# Crear blueprint para integración y monitoreo
integration_bp = Blueprint('integration', __name__)

# Configurar logging
logger = logging.getLogger(__name__)

# ==================== INTEGRACIÓN EXTERNA ====================

@integration_bp.route('/integration/market-prices/sync', methods=['POST'])
def sync_market_prices():
    """Sincroniza precios de mercado"""
    try:
        result = external_integration_service.sync_market_prices()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Precios de mercado sincronizados exitosamente',
                'updated_products': result['updated_products'],
                'sync_time': result['sync_time']
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f'Error sincronizando precios de mercado: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@integration_bp.route('/integration/supplier-data/sync', methods=['POST'])
def sync_supplier_data():
    """Sincroniza datos de proveedores"""
    try:
        result = external_integration_service.sync_supplier_data()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Datos de proveedores sincronizados exitosamente',
                'updated_products': result['updated_products'],
                'sync_time': result['sync_time']
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f'Error sincronizando datos de proveedores: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@integration_bp.route('/integration/market-forecast/<product_sku>', methods=['GET'])
def get_market_forecast(product_sku):
    """Obtiene pronóstico de mercado para un producto"""
    try:
        result = external_integration_service.get_market_forecast(product_sku)
        
        if result['success']:
            return jsonify({
                'success': True,
                'forecast': result['forecast']
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f'Error obteniendo pronóstico de mercado: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@integration_bp.route('/integration/competitor-analysis/<category>', methods=['GET'])
def get_competitor_analysis(category):
    """Obtiene análisis de competidores"""
    try:
        result = external_integration_service.get_competitor_analysis(category)
        
        if result['success']:
            return jsonify({
                'success': True,
                'analysis': result['analysis']
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f'Error obteniendo análisis de competidores: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@integration_bp.route('/integration/status', methods=['GET'])
def get_integration_status():
    """Obtiene estado de las integraciones"""
    try:
        status = external_integration_service.get_integration_status()
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo estado de integraciones: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@integration_bp.route('/integration/auto-sync/start', methods=['POST'])
def start_auto_sync():
    """Inicia sincronización automática"""
    try:
        external_integration_service.start_auto_sync()
        return jsonify({
            'success': True,
            'message': 'Sincronización automática iniciada'
        })
        
    except Exception as e:
        logger.error(f'Error iniciando sincronización automática: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@integration_bp.route('/integration/auto-sync/stop', methods=['POST'])
def stop_auto_sync():
    """Detiene sincronización automática"""
    try:
        external_integration_service.stop_auto_sync()
        return jsonify({
            'success': True,
            'message': 'Sincronización automática detenida'
        })
        
    except Exception as e:
        logger.error(f'Error deteniendo sincronización automática: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== RESPALDOS ====================

@integration_bp.route('/backup/create-full', methods=['POST'])
def create_full_backup():
    """Crea respaldo completo del sistema"""
    try:
        result = backup_service.create_full_backup()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Respaldo completo creado exitosamente',
                'backup_file': result['backup_file'],
                'file_size': result['file_size'],
                'created_at': result['created_at']
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f'Error creando respaldo completo: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@integration_bp.route('/backup/create-data', methods=['POST'])
def create_data_backup():
    """Crea respaldo solo de datos"""
    try:
        result = backup_service.create_data_backup()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Respaldo de datos creado exitosamente',
                'backup_file': result['backup_file'],
                'file_size': result['file_size'],
                'records_backed_up': result['records_backed_up'],
                'created_at': result['created_at']
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f'Error creando respaldo de datos: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@integration_bp.route('/backup/download/<filename>', methods=['GET'])
def download_backup(filename):
    """Descarga archivo de respaldo"""
    try:
        backup_path = os.path.join(backup_service.backup_dir, filename)
        
        if not os.path.exists(backup_path):
            return jsonify({'error': 'Archivo de respaldo no encontrado'}), 404
        
        return send_file(
            backup_path,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f'Error descargando respaldo: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@integration_bp.route('/backup/restore', methods=['POST'])
def restore_backup():
    """Restaura sistema desde respaldo"""
    try:
        data = request.get_json()
        backup_file = data.get('backup_file')
        
        if not backup_file:
            return jsonify({'error': 'Archivo de respaldo no especificado'}), 400
        
        result = backup_service.restore_from_backup(backup_file)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Sistema restaurado exitosamente',
                'restored_products': result.get('restored_products', 0),
                'restored_at': result['restored_at']
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f'Error restaurando respaldo: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@integration_bp.route('/backup/cleanup', methods=['POST'])
def cleanup_backups():
    """Limpia respaldos antiguos"""
    try:
        result = backup_service.cleanup_old_backups()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': f'Limpiados {result["deleted_count"]} respaldos antiguos'
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f'Error limpiando respaldos: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@integration_bp.route('/backup/status', methods=['GET'])
def get_backup_status():
    """Obtiene estado de los respaldos"""
    try:
        status = backup_service.get_backup_status()
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo estado de respaldos: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== MONITOREO AVANZADO ====================

@integration_bp.route('/monitoring/start', methods=['POST'])
def start_monitoring():
    """Inicia monitoreo del sistema"""
    try:
        advanced_monitoring_service.start_monitoring()
        return jsonify({
            'success': True,
            'message': 'Monitoreo del sistema iniciado'
        })
        
    except Exception as e:
        logger.error(f'Error iniciando monitoreo: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@integration_bp.route('/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """Detiene monitoreo del sistema"""
    try:
        advanced_monitoring_service.stop_monitoring()
        return jsonify({
            'success': True,
            'message': 'Monitoreo del sistema detenido'
        })
        
    except Exception as e:
        logger.error(f'Error deteniendo monitoreo: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@integration_bp.route('/monitoring/health', methods=['GET'])
def get_system_health():
    """Obtiene estado de salud del sistema"""
    try:
        health = advanced_monitoring_service.get_system_health()
        
        return jsonify({
            'success': True,
            'health': {
                'overall_status': health.overall_status,
                'alerts_count': health.alerts_count,
                'uptime': health.uptime,
                'performance_score': health.performance_score,
                'last_check': health.last_check.isoformat(),
                'metrics': [
                    {
                        'name': metric.name,
                        'value': metric.value,
                        'unit': metric.unit,
                        'trend': metric.trend,
                        'timestamp': metric.timestamp.isoformat()
                    } for metric in health.metrics
                ]
            }
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo estado de salud: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@integration_bp.route('/monitoring/metrics/history', methods=['GET'])
def get_metrics_history():
    """Obtiene historial de métricas"""
    try:
        metric_name = request.args.get('metric_name')
        hours = request.args.get('hours', 24, type=int)
        
        history = advanced_monitoring_service.get_metrics_history(metric_name, hours)
        
        return jsonify({
            'success': True,
            'history': history,
            'metric_name': metric_name,
            'hours': hours
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo historial de métricas: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@integration_bp.route('/monitoring/alerts/rules', methods=['GET'])
def get_alert_rules():
    """Obtiene reglas de alertas"""
    try:
        rules = advanced_monitoring_service.get_alert_rules()
        
        # Convertir enum keys a strings para JSON
        rules_dict = {}
        for alert_type, rule in rules.items():
            rules_dict[alert_type.value] = {
                'enabled': rule['enabled'],
                'severity': rule['severity'].value,
                'threshold': rule['threshold'],
                'cooldown_minutes': rule['cooldown_minutes']
            }
        
        return jsonify({
            'success': True,
            'rules': rules_dict
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo reglas de alertas: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@integration_bp.route('/monitoring/alerts/rules', methods=['POST'])
def update_alert_rules():
    """Actualiza reglas de alertas"""
    try:
        data = request.get_json()
        
        for alert_type_str, rule_config in data.items():
            try:
                alert_type = AlertType(alert_type_str)
                severity = AlertSeverity(rule_config['severity'])
                
                rule_config['severity'] = severity
                advanced_monitoring_service.update_alert_rule(alert_type, rule_config)
                
            except ValueError as e:
                logger.warning(f'Tipo de alerta inválido: {alert_type_str}')
                continue
        
        return jsonify({
            'success': True,
            'message': 'Reglas de alertas actualizadas exitosamente'
        })
        
    except Exception as e:
        logger.error(f'Error actualizando reglas de alertas: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@integration_bp.route('/monitoring/alerts/active', methods=['GET'])
def get_active_alerts():
    """Obtiene alertas activas"""
    try:
        alerts = Alert.query.filter(Alert.is_resolved == False).order_by(Alert.created_at.desc()).all()
        
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'type': alert.alert_type,
                'message': alert.message,
                'severity': alert.severity,
                'created_at': alert.created_at.isoformat(),
                'product_name': alert.product.name if alert.product else 'Sistema'
            })
        
        return jsonify({
            'success': True,
            'alerts': alerts_data,
            'total_count': len(alerts_data)
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo alertas activas: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@integration_bp.route('/monitoring/alerts/resolve/<int:alert_id>', methods=['POST'])
def resolve_alert(alert_id):
    """Resuelve una alerta"""
    try:
        alert = Alert.query.get(alert_id)
        
        if not alert:
            return jsonify({'error': 'Alerta no encontrada'}), 404
        
        alert.is_resolved = True
        alert.resolved_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Alerta resuelta exitosamente'
        })
        
    except Exception as e:
        logger.error(f'Error resolviendo alerta: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== DASHBOARD DE MONITOREO ====================

@integration_bp.route('/monitoring/dashboard', methods=['GET'])
def get_monitoring_dashboard():
    """Obtiene datos para dashboard de monitoreo"""
    try:
        # Estado de salud del sistema
        health = advanced_monitoring_service.get_system_health()
        
        # Estado de integraciones
        integration_status = external_integration_service.get_integration_status()
        
        # Estado de respaldos
        backup_status = backup_service.get_backup_status()
        
        # Alertas activas
        active_alerts = Alert.query.filter(Alert.is_resolved == False).count()
        
        # Métricas recientes
        recent_metrics = advanced_monitoring_service.get_metrics_history(hours=1)
        
        return jsonify({
            'success': True,
            'dashboard': {
                'system_health': {
                    'status': health.overall_status,
                    'performance_score': health.performance_score,
                    'uptime': health.uptime,
                    'alerts_count': health.alerts_count
                },
                'integrations': {
                    'total': integration_status['total_integrations'],
                    'active': len([i for i in integration_status['integrations'].values() if i['status'] == 'active']),
                    'auto_sync_running': integration_status['auto_sync_running']
                },
                'backups': {
                    'total': backup_status['total_backups'],
                    'total_size': backup_status['total_size'],
                    'retention_days': backup_status['retention_days']
                },
                'monitoring': {
                    'active_alerts': active_alerts,
                    'metrics_collected': len(recent_metrics),
                    'last_check': health.last_check.isoformat()
                }
            }
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo dashboard de monitoreo: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500



