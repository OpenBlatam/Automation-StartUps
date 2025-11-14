from flask import Blueprint, request, jsonify
from app import db
from models import Product, InventoryRecord, SalesRecord
from services.quality_traceability_service import quality_traceability_service, QualityStatus, ComplianceStatus
from services.sustainability_service import sustainability_service, SustainabilityMetric, EnvironmentalImpact
from datetime import datetime, timedelta
import logging
import json

# Crear blueprint para calidad, trazabilidad y sostenibilidad
quality_sustainability_bp = Blueprint('quality_sustainability', __name__)

# Configurar logging
logger = logging.getLogger(__name__)

# ==================== CALIDAD Y TRAZABILIDAD ====================

@quality_sustainability_bp.route('/quality/create-check', methods=['POST'])
def create_quality_check():
    """Crea verificación de calidad"""
    try:
        data = request.get_json()
        
        required_fields = ['product_id', 'batch_number', 'inspector_id', 'quality_status']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} es requerido'}), 400
        
        # Validar estado de calidad
        try:
            quality_status = QualityStatus(data['quality_status'])
        except ValueError:
            return jsonify({'error': 'Estado de calidad inválido'}), 400
        
        result = quality_traceability_service.create_quality_check(
            product_id=data['product_id'],
            batch_number=data['batch_number'],
            inspector_id=data['inspector_id'],
            quality_status=quality_status,
            temperature=data.get('temperature'),
            humidity=data.get('humidity'),
            weight=data.get('weight'),
            dimensions=data.get('dimensions'),
            defects=data.get('defects', []),
            notes=data.get('notes', '')
        )
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'quality_check': result['quality_check']
        })
        
    except Exception as e:
        logger.error(f'Error creando verificación de calidad: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@quality_sustainability_bp.route('/quality/history', methods=['GET'])
def get_quality_history():
    """Obtiene historial de calidad"""
    try:
        product_id = request.args.get('product_id', type=int)
        batch_number = request.args.get('batch_number')
        
        result = quality_traceability_service.get_quality_history(product_id, batch_number)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'quality_history': result
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo historial de calidad: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@quality_sustainability_bp.route('/traceability/product/<int:product_id>', methods=['GET'])
def get_product_traceability(product_id):
    """Obtiene trazabilidad de un producto"""
    try:
        batch_number = request.args.get('batch_number')
        
        result = quality_traceability_service.get_product_traceability(product_id, batch_number)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'traceability': result
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo trazabilidad: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@quality_sustainability_bp.route('/compliance/status', methods=['GET'])
def get_compliance_status():
    """Obtiene estado de cumplimiento"""
    try:
        product_id = request.args.get('product_id', type=int)
        
        result = quality_traceability_service.get_compliance_status(product_id)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'compliance_status': result
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo estado de cumplimiento: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@quality_sustainability_bp.route('/audit/create', methods=['POST'])
def create_supplier_audit():
    """Crea auditoría de proveedor"""
    try:
        data = request.get_json()
        
        required_fields = ['supplier_id', 'auditor_id', 'audit_type', 'score', 'findings', 'recommendations', 'status']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} es requerido'}), 400
        
        result = quality_traceability_service.create_supplier_audit(
            supplier_id=data['supplier_id'],
            auditor_id=data['auditor_id'],
            audit_type=data['audit_type'],
            score=data['score'],
            findings=data['findings'],
            recommendations=data['recommendations'],
            status=data['status']
        )
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'audit': result['audit']
        })
        
    except Exception as e:
        logger.error(f'Error creando auditoría de proveedor: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@quality_sustainability_bp.route('/quality/report', methods=['POST'])
def generate_quality_report():
    """Genera reporte de calidad"""
    try:
        data = request.get_json() or {}
        
        product_id = data.get('product_id')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Formato de fecha de inicio inválido'}), 400
        
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Formato de fecha de fin inválido'}), 400
        
        result = quality_traceability_service.generate_quality_report(product_id, start_date, end_date)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'quality_report': result['report']
        })
        
    except Exception as e:
        logger.error(f'Error generando reporte de calidad: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@quality_sustainability_bp.route('/quality/dashboard', methods=['GET'])
def get_quality_dashboard():
    """Obtiene datos para dashboard de calidad"""
    try:
        result = quality_traceability_service.get_quality_dashboard()
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'dashboard': result['dashboard']
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo dashboard de calidad: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== SOSTENIBILIDAD ====================

@quality_sustainability_bp.route('/sustainability/record-metric', methods=['POST'])
def record_environmental_metric():
    """Registra métrica ambiental"""
    try:
        data = request.get_json()
        
        required_fields = ['metric_type', 'value', 'unit', 'source', 'location']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} es requerido'}), 400
        
        # Validar tipo de métrica
        try:
            metric_type = SustainabilityMetric(data['metric_type'])
        except ValueError:
            return jsonify({'error': 'Tipo de métrica inválido'}), 400
        
        result = sustainability_service.record_environmental_metric(
            metric_type=metric_type,
            product_id=data.get('product_id'),
            value=data['value'],
            unit=data['unit'],
            source=data['source'],
            location=data['location'],
            verified=data.get('verified', False),
            notes=data.get('notes', '')
        )
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'metric': result['metric']
        })
        
    except Exception as e:
        logger.error(f'Error registrando métrica ambiental: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@quality_sustainability_bp.route('/sustainability/carbon-footprint/<int:product_id>', methods=['POST'])
def calculate_carbon_footprint(product_id):
    """Calcula huella de carbono de un producto"""
    try:
        data = request.get_json() or {}
        scope = data.get('scope', 'scope3')
        
        result = sustainability_service.calculate_carbon_footprint(product_id, scope)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'carbon_footprint': result['carbon_footprint']
        })
        
    except Exception as e:
        logger.error(f'Error calculando huella de carbono: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@quality_sustainability_bp.route('/sustainability/waste-management', methods=['POST'])
def record_waste_management():
    """Registra gestión de residuos"""
    try:
        data = request.get_json()
        
        required_fields = ['product_id', 'waste_type', 'quantity', 'unit', 'disposal_method', 'location']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} es requerido'}), 400
        
        result = sustainability_service.record_waste_management(
            product_id=data['product_id'],
            waste_type=data['waste_type'],
            quantity=data['quantity'],
            unit=data['unit'],
            disposal_method=data['disposal_method'],
            location=data['location'],
            cost=data.get('cost', 0.0)
        )
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'waste_record': result['waste_record']
        })
        
    except Exception as e:
        logger.error(f'Error registrando gestión de residuos: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@quality_sustainability_bp.route('/sustainability/goals', methods=['GET'])
def get_sustainability_goals():
    """Obtiene objetivos de sostenibilidad"""
    try:
        result = sustainability_service.get_sustainability_dashboard()
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'sustainability_goals': result['dashboard']['sustainability_goals']
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo objetivos de sostenibilidad: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@quality_sustainability_bp.route('/sustainability/goals/<goal_id>/update', methods=['POST'])
def update_sustainability_goal(goal_id):
    """Actualiza objetivo de sostenibilidad"""
    try:
        data = request.get_json()
        
        if 'current_value' not in data:
            return jsonify({'error': 'current_value es requerido'}), 400
        
        result = sustainability_service.update_sustainability_goal(goal_id, data['current_value'])
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'goal': result['goal']
        })
        
    except Exception as e:
        logger.error(f'Error actualizando objetivo de sostenibilidad: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@quality_sustainability_bp.route('/sustainability/report', methods=['POST'])
def generate_sustainability_report():
    """Genera reporte de sostenibilidad"""
    try:
        data = request.get_json() or {}
        
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Formato de fecha de inicio inválido'}), 400
        
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Formato de fecha de fin inválido'}), 400
        
        result = sustainability_service.generate_sustainability_report(start_date, end_date)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'sustainability_report': result['report']
        })
        
    except Exception as e:
        logger.error(f'Error generando reporte de sostenibilidad: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

@quality_sustainability_bp.route('/sustainability/dashboard', methods=['GET'])
def get_sustainability_dashboard():
    """Obtiene datos para dashboard de sostenibilidad"""
    try:
        result = sustainability_service.get_sustainability_dashboard()
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'dashboard': result['dashboard']
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo dashboard de sostenibilidad: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== DASHBOARD COMBINADO ====================

@quality_sustainability_bp.route('/quality-sustainability/dashboard', methods=['GET'])
def get_quality_sustainability_dashboard():
    """Obtiene datos para dashboard combinado"""
    try:
        # Obtener datos de calidad
        quality_dashboard = quality_traceability_service.get_quality_dashboard()
        
        # Obtener datos de sostenibilidad
        sustainability_dashboard = sustainability_service.get_sustainability_dashboard()
        
        return jsonify({
            'success': True,
            'dashboard': {
                'quality': quality_dashboard.get('dashboard', {}) if quality_dashboard.get('success') else {},
                'sustainability': sustainability_dashboard.get('dashboard', {}) if sustainability_dashboard.get('success') else {},
                'combined': {
                    'total_quality_checks': quality_dashboard.get('dashboard', {}).get('quality_checks', {}).get('total', 0) if quality_dashboard.get('success') else 0,
                    'total_environmental_metrics': sustainability_dashboard.get('dashboard', {}).get('environmental_metrics', {}).get('total', 0) if sustainability_dashboard.get('success') else 0,
                    'pending_compliance_reviews': quality_dashboard.get('dashboard', {}).get('compliance', {}).get('pending_reviews', 0) if quality_dashboard.get('success') else 0,
                    'sustainability_goals_count': sustainability_dashboard.get('dashboard', {}).get('sustainability_goals', {}).get('total_goals', 0) if sustainability_dashboard.get('success') else 0
                }
            }
        })
        
    except Exception as e:
        logger.error(f'Error obteniendo dashboard combinado: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== ANÁLISIS AVANZADO COMBINADO ====================

@quality_sustainability_bp.route('/quality-sustainability/advanced-analysis', methods=['POST'])
def advanced_combined_analysis():
    """Realiza análisis avanzado combinando calidad y sostenibilidad"""
    try:
        data = request.get_json() or {}
        analysis_type = data.get('analysis_type', 'comprehensive')
        
        results = {}
        
        if analysis_type in ['comprehensive', 'quality']:
            # Análisis de calidad
            quality_history = quality_traceability_service.get_quality_history()
            compliance_status = quality_traceability_service.get_compliance_status()
            
            results['quality_analysis'] = {
                'quality_history': quality_history,
                'compliance_status': compliance_status,
                'total_checks': quality_history.get('total_checks', 0) if quality_history.get('success') else 0,
                'pending_reviews': compliance_status.get('pending_reviews', 0) if compliance_status.get('success') else 0
            }
        
        if analysis_type in ['comprehensive', 'sustainability']:
            # Análisis de sostenibilidad
            sustainability_dashboard = sustainability_service.get_sustainability_dashboard()
            
            results['sustainability_analysis'] = {
                'dashboard': sustainability_dashboard.get('dashboard', {}) if sustainability_dashboard.get('success') else {},
                'total_metrics': sustainability_dashboard.get('dashboard', {}).get('environmental_metrics', {}).get('total', 0) if sustainability_dashboard.get('success') else 0,
                'goals_count': sustainability_dashboard.get('dashboard', {}).get('sustainability_goals', {}).get('total_goals', 0) if sustainability_dashboard.get('success') else 0
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



