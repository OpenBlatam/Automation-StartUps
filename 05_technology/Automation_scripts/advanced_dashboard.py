"""
Dashboard Avanzado con Métricas en Tiempo Real
==============================================

Dashboard mejorado con:
- WebSockets para actualizaciones en tiempo real
- Métricas avanzadas y visualizaciones interactivas
- Sistema de notificaciones push
- Análisis predictivo visual
- Gestión de múltiples ubicaciones
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import threading
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from collections import deque
import logging

# Importar componentes del sistema
from inventory_management_system import InventoryManagementSystem, AlertType
from advanced_analytics import AdvancedAnalytics
from enhanced_system import EnhancedInventorySystem

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask y SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-for-websockets'
socketio = SocketIO(app, cors_allowed_origins="*")

# Inicializar sistemas
ims = InventoryManagementSystem()
analytics = AdvancedAnalytics()
enhanced_system = EnhancedInventorySystem()

# Almacenamiento en memoria para métricas en tiempo real
real_time_metrics = {
    'inventory_value': deque(maxlen=100),
    'active_alerts': deque(maxlen=100),
    'stock_levels': deque(maxlen=100),
    'sales_velocity': deque(maxlen=100),
    'system_performance': deque(maxlen=100)
}

# Clientes conectados
connected_clients = set()

class RealTimeMetricsCollector:
    """Recolector de métricas en tiempo real"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        
    def start(self):
        """Iniciar recolección de métricas"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._collect_metrics)
            self.thread.daemon = True
            self.thread.start()
            logger.info("Recolector de métricas iniciado")
    
    def stop(self):
        """Detener recolección de métricas"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Recolector de métricas detenido")
    
    def _collect_metrics(self):
        """Recolectar métricas continuamente"""
        while self.running:
            try:
                # Obtener métricas del sistema
                kpis = ims.generate_kpis()
                
                # Actualizar métricas en tiempo real
                timestamp = datetime.now().isoformat()
                
                real_time_metrics['inventory_value'].append({
                    'timestamp': timestamp,
                    'value': kpis.get('total_inventory_value', 0)
                })
                
                real_time_metrics['active_alerts'].append({
                    'timestamp': timestamp,
                    'value': kpis.get('active_alerts', 0)
                })
                
                # Calcular velocidad de ventas (simulada)
                sales_velocity = np.random.normal(100, 20)  # Simulado
                real_time_metrics['sales_velocity'].append({
                    'timestamp': timestamp,
                    'value': max(0, sales_velocity)
                })
                
                # Métricas de rendimiento del sistema
                system_perf = {
                    'timestamp': timestamp,
                    'cpu_usage': np.random.uniform(20, 80),
                    'memory_usage': np.random.uniform(30, 70),
                    'response_time': np.random.uniform(0.1, 0.5)
                }
                real_time_metrics['system_performance'].append(system_perf)
                
                # Enviar actualizaciones a clientes conectados
                if connected_clients:
                    socketio.emit('metrics_update', {
                        'inventory_value': list(real_time_metrics['inventory_value'])[-10:],
                        'active_alerts': list(real_time_metrics['active_alerts'])[-10:],
                        'sales_velocity': list(real_time_metrics['sales_velocity'])[-10:],
                        'system_performance': list(real_time_metrics['system_performance'])[-10:]
                    })
                
                time.sleep(5)  # Actualizar cada 5 segundos
                
            except Exception as e:
                logger.error(f"Error recolectando métricas: {e}")
                time.sleep(10)

# Inicializar recolector de métricas
metrics_collector = RealTimeMetricsCollector()

# ==================== RUTAS PRINCIPALES ====================

@app.route('/')
def dashboard():
    """Dashboard principal"""
    return render_template('advanced_dashboard.html')

@app.route('/api/dashboard/overview')
def get_dashboard_overview():
    """Obtener resumen del dashboard"""
    try:
        # Obtener KPIs básicos
        kpis = ims.generate_kpis()
        
        # Obtener alertas críticas
        alerts = ims.get_alerts_summary()
        critical_alerts = [a for a in alerts if a['severity'] in ['critical', 'high']]
        
        # Obtener productos con stock bajo
        import sqlite3
        conn = sqlite3.connect(ims.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.name, COALESCE(SUM(i.quantity), 0) as stock, p.reorder_point
            FROM products p
            LEFT JOIN inventory i ON p.id = i.product_id
            GROUP BY p.id
            HAVING stock <= p.reorder_point
        ''')
        
        low_stock_products = []
        for row in cursor.fetchall():
            low_stock_products.append({
                'name': row[0],
                'current_stock': row[1],
                'reorder_point': row[2],
                'urgency': 'critical' if row[1] <= row[2] * 0.5 else 'high'
            })
        
        conn.close()
        
        # Obtener análisis ABC
        abc_analysis = analytics.abc_analysis()
        
        # Obtener recomendaciones de optimización
        optimization = analytics.inventory_optimization()
        
        return jsonify({
            'kpis': kpis,
            'critical_alerts': critical_alerts[:5],
            'low_stock_products': low_stock_products[:5],
            'abc_summary': {
                'category_a_count': abc_analysis['A']['count'],
                'category_b_count': abc_analysis['B']['count'],
                'category_c_count': abc_analysis['C']['count']
            },
            'optimization_summary': optimization['summary'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen del dashboard: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/dashboard/charts/inventory-trend')
def get_inventory_trend():
    """Obtener datos para gráfico de tendencia de inventario"""
    try:
        # Simular datos históricos de inventario
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        inventory_values = []
        
        base_value = 100000
        for i, date in enumerate(dates):
            # Simular tendencia con variación aleatoria
            trend = np.sin(i * 0.1) * 10000
            noise = np.random.normal(0, 5000)
            value = base_value + trend + noise
            inventory_values.append(max(0, value))
        
        chart_data = {
            'labels': [d.strftime('%Y-%m-%d') for d in dates],
            'datasets': [{
                'label': 'Valor del Inventario',
                'data': inventory_values,
                'borderColor': 'rgb(75, 192, 192)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'fill': True
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        logger.error(f"Error obteniendo tendencia de inventario: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/dashboard/charts/stock-levels')
def get_stock_levels_chart():
    """Obtener datos para gráfico de niveles de stock"""
    try:
        import sqlite3
        
        conn = sqlite3.connect(ims.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.name, COALESCE(SUM(i.quantity), 0) as stock, 
                   p.min_stock_level, p.max_stock_level, p.reorder_point
            FROM products p
            LEFT JOIN inventory i ON p.id = i.product_id
            GROUP BY p.id
            ORDER BY stock DESC
            LIMIT 10
        ''')
        
        products = []
        current_stocks = []
        reorder_points = []
        max_stocks = []
        
        for row in cursor.fetchall():
            products.append(row[0])
            current_stocks.append(row[1])
            reorder_points.append(row[4])
            max_stocks.append(row[3])
        
        conn.close()
        
        chart_data = {
            'labels': products,
            'datasets': [
                {
                    'label': 'Stock Actual',
                    'data': current_stocks,
                    'backgroundColor': 'rgba(54, 162, 235, 0.8)'
                },
                {
                    'label': 'Punto de Reorden',
                    'data': reorder_points,
                    'backgroundColor': 'rgba(255, 99, 132, 0.8)'
                },
                {
                    'label': 'Stock Máximo',
                    'data': max_stocks,
                    'backgroundColor': 'rgba(255, 205, 86, 0.8)'
                }
            ]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        logger.error(f"Error obteniendo niveles de stock: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/dashboard/charts/sales-forecast')
def get_sales_forecast():
    """Obtener predicción de ventas"""
    try:
        # Simular datos históricos y predicción
        historical_dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        future_dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
        
        # Datos históricos simulados
        historical_sales = []
        base_sales = 50
        for i, date in enumerate(historical_dates):
            trend = np.sin(i * 0.1) * 10
            seasonality = np.sin(i * 0.2) * 5
            noise = np.random.normal(0, 5)
            sales = base_sales + trend + seasonality + noise
            historical_sales.append(max(0, sales))
        
        # Predicción simulada
        forecast_sales = []
        for i, date in enumerate(future_dates):
            trend = np.sin((i + 30) * 0.1) * 10
            seasonality = np.sin((i + 30) * 0.2) * 5
            noise = np.random.normal(0, 3)  # Menos ruido en predicción
            sales = base_sales + trend + seasonality + noise
            forecast_sales.append(max(0, sales))
        
        chart_data = {
            'labels': [d.strftime('%Y-%m-%d') for d in list(historical_dates) + list(future_dates)],
            'datasets': [
                {
                    'label': 'Ventas Históricas',
                    'data': historical_sales + [None] * len(future_dates),
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'fill': False
                },
                {
                    'label': 'Predicción',
                    'data': [None] * len(historical_dates) + forecast_sales,
                    'borderColor': 'rgb(255, 99, 132)',
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderDash': [5, 5],
                    'fill': False
                }
            ]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        logger.error(f"Error obteniendo predicción de ventas: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== WEBSOCKETS ====================

@socketio.on('connect')
def handle_connect():
    """Manejar conexión de cliente"""
    connected_clients.add(request.sid)
    logger.info(f"Cliente conectado: {request.sid}")
    
    # Enviar métricas actuales al cliente recién conectado
    emit('metrics_update', {
        'inventory_value': list(real_time_metrics['inventory_value'])[-10:],
        'active_alerts': list(real_time_metrics['active_alerts'])[-10:],
        'sales_velocity': list(real_time_metrics['sales_velocity'])[-10:],
        'system_performance': list(real_time_metrics['system_performance'])[-10:]
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Manejar desconexión de cliente"""
    connected_clients.discard(request.sid)
    logger.info(f"Cliente desconectado: {request.sid}")

@socketio.on('join_room')
def handle_join_room(data):
    """Unirse a una sala específica"""
    room = data.get('room', 'default')
    join_room(room)
    logger.info(f"Cliente {request.sid} se unió a la sala {room}")

@socketio.on('leave_room')
def handle_leave_room(data):
    """Salir de una sala específica"""
    room = data.get('room', 'default')
    leave_room(room)
    logger.info(f"Cliente {request.sid} salió de la sala {room}")

@socketio.on('request_update')
def handle_request_update():
    """Solicitar actualización de métricas"""
    try:
        kpis = ims.generate_kpis()
        alerts = ims.get_alerts_summary()
        
        emit('data_update', {
            'kpis': kpis,
            'alerts': alerts[:5],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error enviando actualización: {e}")
        emit('error', {'message': 'Error obteniendo datos actualizados'})

@socketio.on('subscribe_alerts')
def handle_subscribe_alerts():
    """Suscribirse a alertas en tiempo real"""
    join_room('alerts')
    logger.info(f"Cliente {request.sid} suscrito a alertas")

@socketio.on('unsubscribe_alerts')
def handle_unsubscribe_alerts():
    """Desuscribirse de alertas"""
    leave_room('alerts')
    logger.info(f"Cliente {request.sid} desuscrito de alertas")

# ==================== FUNCIONES DE UTILIDAD ====================

def broadcast_alert(alert_data):
    """Transmitir alerta a todos los clientes suscritos"""
    socketio.emit('new_alert', alert_data, room='alerts')

def broadcast_system_status(status_data):
    """Transmitir estado del sistema"""
    socketio.emit('system_status', status_data)

# ==================== FUNCIÓN PRINCIPAL ====================

if __name__ == '__main__':
    logger.info("Iniciando Dashboard Avanzado con WebSockets")
    
    try:
        # Iniciar recolector de métricas
        metrics_collector.start()
        
        # Ejecutar servidor con SocketIO
        socketio.run(
            app,
            debug=True,
            host='0.0.0.0',
            port=5002,  # Puerto diferente para el dashboard avanzado
            allow_unsafe_werkzeug=True
        )
        
    except KeyboardInterrupt:
        logger.info("Deteniendo servidor...")
        metrics_collector.stop()
    except Exception as e:
        logger.error(f"Error ejecutando servidor: {e}")
        metrics_collector.stop()



