from flask import Blueprint, request, jsonify
from app import db
from models import Product, InventoryRecord
from services.iot_service import iot_monitoring_service
from services.ar_service import augmented_reality_service
from datetime import datetime, timedelta
import logging
import json

# Crear blueprint para IoT y AR
iot_ar_bp = Blueprint('iot_ar', __name__)

# Configurar logging
logger = logging.getLogger(__name__)

# ==================== INTERNET OF THINGS (IoT) ====================

@iot_ar_bp.route('/iot/devices/status', methods=['GET'])
def get_iot_devices_status():
    """Obtiene estado de dispositivos IoT"""
    try:
        status = iot_monitoring_service.get_device_status()
        
        if status['success']:
            return jsonify({
                'success': True,
                'devices': status['devices'],
                'total_devices': status['total_devices'],
                'online_devices': status['online_devices'],
                'offline_devices': status['offline_devices']
            })
        else:
            return jsonify({'error': status['error']}), 400
            
    except Exception as e:
        logger.error(f'Error obteniendo estado de dispositivos IoT: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@iot_ar_bp.route('/iot/sensors/data', methods=['GET'])
def get_iot_sensor_data():
    """Obtiene datos de sensores IoT"""
    try:
        sensor_id = request.args.get('sensor_id')
        hours = request.args.get('hours', 24, type=int)
        
        data = iot_monitoring_service.get_sensor_data(sensor_id, hours)
        
        if data['success']:
            return jsonify({
                'success': True,
                'sensor_data': data['sensor_data'],
                'total_records': data['total_records'],
                'sensor_id': data['sensor_id'],
                'hours': data['hours']
            })
        else:
            return jsonify({'error': data['error']}), 400
            
    except Exception as e:
        logger.error(f'Error obteniendo datos de sensores IoT: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@iot_ar_bp.route('/iot/alerts', methods=['GET'])
def get_iot_alerts():
    """Obtiene alertas IoT"""
    try:
        alerts = iot_monitoring_service.get_alerts()
        
        if alerts['success']:
            return jsonify({
                'success': True,
                'alerts': alerts['alerts'],
                'total_alerts': alerts['total_alerts']
            })
        else:
            return jsonify({'error': alerts['error']}), 400
            
    except Exception as e:
        logger.error(f'Error obteniendo alertas IoT: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@iot_ar_bp.route('/iot/monitoring/start', methods=['POST'])
def start_iot_monitoring():
    """Inicia monitoreo IoT"""
    try:
        iot_monitoring_service.start_monitoring()
        return jsonify({
            'success': True,
            'message': 'Monitoreo IoT iniciado exitosamente'
        })
        
    except Exception as e:
        logger.error(f'Error iniciando monitoreo IoT: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@iot_ar_bp.route('/iot/monitoring/stop', methods=['POST'])
def stop_iot_monitoring():
    """Detiene monitoreo IoT"""
    try:
        iot_monitoring_service.stop_monitoring()
        return jsonify({
            'success': True,
            'message': 'Monitoreo IoT detenido exitosamente'
        })
        
    except Exception as e:
        logger.error(f'Error deteniendo monitoreo IoT: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@iot_ar_bp.route('/iot/dashboard', methods=['GET'])
def get_iot_dashboard():
    """Obtiene datos para dashboard IoT"""
    try:
        dashboard = iot_monitoring_service.get_dashboard_data()
        
        if dashboard['success']:
            return jsonify({
                'success': True,
                'dashboard': dashboard['dashboard']
            })
        else:
            return jsonify({'error': dashboard['error']}), 400
            
    except Exception as e:
        logger.error(f'Error obteniendo dashboard IoT: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== REALIDAD AUMENTADA (AR) ====================

@iot_ar_bp.route('/ar/warehouse/layout', methods=['GET'])
def get_ar_warehouse_layout():
    """Obtiene layout del almacén para AR"""
    try:
        layout_id = request.args.get('layout_id')
        
        layout = augmented_reality_service.get_warehouse_layout(layout_id)
        
        if layout['success']:
            return jsonify({
                'success': True,
                'layout': layout['layout']
            })
        else:
            return jsonify({'error': layout['error']}), 400
            
    except Exception as e:
        logger.error(f'Error obteniendo layout de almacén AR: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@iot_ar_bp.route('/ar/markers', methods=['GET'])
def get_ar_markers():
    """Obtiene marcadores AR"""
    try:
        zone_id = request.args.get('zone_id')
        
        markers = augmented_reality_service.get_ar_markers(zone_id)
        
        if markers['success']:
            return jsonify({
                'success': True,
                'markers': markers['markers'],
                'total_markers': markers['total_markers'],
                'zone_filter': markers['zone_filter']
            })
        else:
            return jsonify({'error': markers['error']}), 400
            
    except Exception as e:
        logger.error(f'Error obteniendo marcadores AR: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@iot_ar_bp.route('/ar/content', methods=['GET'])
def get_ar_content():
    """Obtiene contenido AR"""
    try:
        marker_id = request.args.get('marker_id')
        
        content = augmented_reality_service.get_ar_content(marker_id)
        
        if content['success']:
            return jsonify({
                'success': True,
                'content': content['content'],
                'total_content': content['total_content'],
                'marker_filter': content['marker_filter']
            })
        else:
            return jsonify({'error': content['error']}), 400
            
    except Exception as e:
        logger.error(f'Error obteniendo contenido AR: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@iot_ar_bp.route('/ar/session/create', methods=['POST'])
def create_ar_session():
    """Crea sesión AR"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 'anonymous')
        session_type = data.get('session_type', 'inventory_check')
        
        session = augmented_reality_service.create_ar_session(user_id, session_type)
        
        if session['success']:
            return jsonify({
                'success': True,
                'session_id': session['session_id'],
                'session': session['session']
            })
        else:
            return jsonify({'error': session['error']}), 400
            
    except Exception as e:
        logger.error(f'Error creando sesión AR: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@iot_ar_bp.route('/ar/session/<session_id>/scan', methods=['POST'])
def scan_ar_marker(session_id):
    """Escanea marcador AR"""
    try:
        data = request.get_json() or {}
        marker_id = data.get('marker_id')
        
        if not marker_id:
            return jsonify({'error': 'marker_id es requerido'}), 400
        
        scan_result = augmented_reality_service.scan_marker(session_id, marker_id)
        
        if scan_result['success']:
            return jsonify({
                'success': True,
                'marker': scan_result['marker'],
                'content': scan_result['content'],
                'scan_timestamp': scan_result['scan_timestamp']
            })
        else:
            return jsonify({'error': scan_result['error']}), 400
            
    except Exception as e:
        logger.error(f'Error escaneando marcador AR: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@iot_ar_bp.route('/ar/session/<session_id>/action', methods=['POST'])
def perform_ar_action(session_id):
    """Realiza acción en AR"""
    try:
        data = request.get_json() or {}
        action = data.get('action')
        action_data = data.get('data', {})
        
        if not action:
            return jsonify({'error': 'action es requerido'}), 400
        
        result = augmented_reality_service.perform_ar_action(session_id, action, action_data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result.get('message', 'Acción realizada exitosamente'),
                'data': result
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f'Error realizando acción AR: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@iot_ar_bp.route('/ar/session/<session_id>/end', methods=['POST'])
def end_ar_session(session_id):
    """Termina sesión AR"""
    try:
        result = augmented_reality_service.end_ar_session(session_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'session': result['session']
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f'Error terminando sesión AR: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@iot_ar_bp.route('/ar/dashboard', methods=['GET'])
def get_ar_dashboard():
    """Obtiene datos para dashboard AR"""
    try:
        dashboard = augmented_reality_service.get_ar_dashboard_data()
        
        if dashboard['success']:
            return jsonify({
                'success': True,
                'dashboard': dashboard['dashboard']
            })
        else:
            return jsonify({'error': dashboard['error']}), 400
            
    except Exception as e:
        logger.error(f'Error obteniendo dashboard AR: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== DASHBOARD COMBINADO IoT & AR ====================

@iot_ar_bp.route('/iot-ar/dashboard', methods=['GET'])
def get_iot_ar_dashboard():
    """Obtiene datos para dashboard combinado IoT & AR"""
    try:
        # Obtener datos IoT
        iot_dashboard = iot_monitoring_service.get_dashboard_data()
        
        # Obtener datos AR
        ar_dashboard = augmented_reality_service.get_ar_dashboard_data()
        
        return jsonify({
            'success': True,
            'dashboard': {
                'iot': iot_dashboard.get('dashboard', {}) if iot_dashboard.get('success') else {},
                'ar': ar_dashboard.get('dashboard', {}) if ar_dashboard.get('success') else {},
                'combined': {
                    'total_devices': iot_dashboard.get('dashboard', {}).get('devices', {}).get('total', 0),
                    'total_markers': ar_dashboard.get('dashboard', {}).get('markers', {}).get('total', 0),
                    'active_sessions': ar_dashboard.get('dashboard', {}).get('sessions', {}).get('active', 0),
                    'recent_alerts': iot_dashboard.get('dashboard', {}).get('alerts', {}).get('recent', 0)
                }
            }
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo dashboard combinado IoT & AR: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== ANÁLISIS AVANZADO IoT & AR ====================

@iot_ar_bp.route('/iot-ar/analysis', methods=['POST'])
def iot_ar_analysis():
    """Realiza análisis avanzado combinando IoT y AR"""
    try:
        data = request.get_json() or {}
        analysis_type = data.get('analysis_type', 'comprehensive')
        
        results = {}
        
        if analysis_type in ['comprehensive', 'iot']:
            # Análisis IoT
            iot_data = iot_monitoring_service.get_sensor_data(hours=24)
            iot_alerts = iot_monitoring_service.get_alerts()
            
            results['iot_analysis'] = {
                'sensor_data': iot_data.get('sensor_data', []),
                'alerts': iot_alerts.get('alerts', []),
                'total_sensors': len(iot_data.get('sensor_data', [])),
                'total_alerts': len(iot_alerts.get('alerts', []))
            }
        
        if analysis_type in ['comprehensive', 'ar']:
            # Análisis AR
            ar_markers = augmented_reality_service.get_ar_markers()
            ar_content = augmented_reality_service.get_ar_content()
            
            results['ar_analysis'] = {
                'markers': ar_markers.get('markers', []),
                'content': ar_content.get('content', []),
                'total_markers': len(ar_markers.get('markers', [])),
                'total_content': len(ar_content.get('content', []))
            }
        
        return jsonify({
            'success': True,
            'analysis_type': analysis_type,
            'results': results,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f'Error realizando análisis IoT & AR: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500



