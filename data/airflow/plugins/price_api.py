"""
API REST para Automatización de Precios

Expone endpoints para consultar y gestionar precios
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from flask import Flask, jsonify, request
import json

logger = logging.getLogger(__name__)


class PriceAPI:
    """API REST para gestión de precios"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.app = Flask(__name__)
        self.history = None
        self.metrics = None
        self.alerting = None
        self.report_generator = None
        self._setup_routes()
    
    def set_dependencies(
        self,
        history=None,
        metrics=None,
        alerting=None,
        report_generator=None
    ):
        """Configura dependencias"""
        self.history = history
        self.metrics = metrics
        self.alerting = alerting
        self.report_generator = report_generator
    
    def _setup_routes(self):
        """Configura rutas de la API"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check"""
            return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
        
        @self.app.route('/api/v1/prices/history/<product_id>', methods=['GET'])
        def get_price_history(product_id):
            """Obtiene historial de precios de un producto"""
            if not self.history:
                return jsonify({'error': 'History not available'}), 503
            
            days = request.args.get('days', 30, type=int)
            history_data = self.history.get_product_history(product_id, days)
            
            return jsonify({
                'product_id': product_id,
                'days': days,
                'changes': history_data
            })
        
        @self.app.route('/api/v1/prices/trends', methods=['GET'])
        def get_price_trends():
            """Obtiene tendencias de precios"""
            if not self.history:
                return jsonify({'error': 'History not available'}), 503
            
            days = request.args.get('days', 30, type=int)
            trends = self.history.get_price_trends(days)
            
            return jsonify(trends)
        
        @self.app.route('/api/v1/metrics', methods=['GET'])
        def get_metrics():
            """Obtiene métricas de rendimiento"""
            if not self.metrics:
                return jsonify({'error': 'Metrics not available'}), 503
            
            operation = request.args.get('operation')
            if operation:
                summary = self.metrics.get_operation_summary(operation)
            else:
                summary = self.metrics.get_performance_report()
            
            return jsonify(summary)
        
        @self.app.route('/api/v1/alerts', methods=['GET'])
        def get_alerts():
            """Obtiene alertas"""
            if not self.alerting:
                return jsonify({'error': 'Alerting not available'}), 503
            
            summary = self.alerting.get_alerts_summary()
            return jsonify(summary)
        
        @self.app.route('/api/v1/reports/execution/<date>', methods=['GET'])
        def get_execution_report(date):
            """Obtiene reporte de ejecución"""
            if not self.report_generator:
                return jsonify({'error': 'Reports not available'}), 503
            
            try:
                report_date = datetime.strptime(date, '%Y-%m-%d')
                report_file = self.report_generator.reports_dir / f"execution_report_{date}.json"
                
                if report_file.exists():
                    with open(report_file, 'r', encoding='utf-8') as f:
                        report = json.load(f)
                    return jsonify(report)
                else:
                    return jsonify({'error': 'Report not found'}), 404
            except ValueError:
                return jsonify({'error': 'Invalid date format (use YYYY-MM-DD)'}), 400
        
        @self.app.route('/api/v1/reports/trends', methods=['GET'])
        def get_trend_report():
            """Obtiene reporte de tendencias"""
            if not self.report_generator:
                return jsonify({'error': 'Reports not available'}), 503
            
            days = request.args.get('days', 30, type=int)
            report = self.report_generator.generate_trend_report(days)
            
            return jsonify(report)
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Ejecuta el servidor API"""
        logger.info(f"Starting Price API on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)








