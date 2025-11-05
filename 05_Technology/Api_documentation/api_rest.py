"""
API REST Completa para Sistema de Gestión de Inventario
======================================================

API RESTful completa con autenticación, rate limiting, documentación automática
y endpoints para todas las funcionalidades del sistema.
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import json

# Importar componentes del sistema
from inventory_management_system import InventoryManagementSystem, AlertType
from advanced_analytics import AdvancedAnalytics
from enhanced_system import EnhancedInventorySystem

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-super-secret-jwt-key-change-in-production'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Configurar CORS
CORS(app, origins=['http://localhost:3000', 'http://localhost:5000'])

# Configurar rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour"]
)

# Inicializar sistemas
ims = InventoryManagementSystem()
analytics = AdvancedAnalytics()
enhanced_system = EnhancedInventorySystem()

# Base de datos de usuarios (en producción usar una BD real)
USERS_DB = {
    'admin': {
        'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
        'role': 'admin',
        'permissions': ['read', 'write', 'delete', 'admin']
    },
    'manager': {
        'password_hash': hashlib.sha256('manager123'.encode()).hexdigest(),
        'role': 'manager',
        'permissions': ['read', 'write']
    },
    'viewer': {
        'password_hash': hashlib.sha256('viewer123'.encode()).hexdigest(),
        'role': 'viewer',
        'permissions': ['read']
    }
}

def require_auth(f):
    """Decorador para requerir autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token de autorización requerido'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            g.current_user = data['username']
            g.user_role = data['role']
            g.user_permissions = data['permissions']
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def require_permission(permission):
    """Decorador para requerir permisos específicos"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if permission not in g.user_permissions:
                return jsonify({'error': 'Permisos insuficientes'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_json_data(required_fields):
    """Decorador para validar datos JSON"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type debe ser application/json'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Datos JSON requeridos'}), 400
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    'error': 'Campos requeridos faltantes',
                    'missing_fields': missing_fields
                }), 400
            
            g.json_data = data
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==================== ENDPOINTS DE AUTENTICACIÓN ====================

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """Iniciar sesión y obtener token JWT"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
        
        if username not in USERS_DB:
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if USERS_DB[username]['password_hash'] != password_hash:
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        # Generar token JWT
        token_payload = {
            'username': username,
            'role': USERS_DB[username]['role'],
            'permissions': USERS_DB[username]['permissions'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(token_payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user': {
                'username': username,
                'role': USERS_DB[username]['role'],
                'permissions': USERS_DB[username]['permissions']
            },
            'expires_in': 86400  # 24 horas en segundos
        })
        
    except Exception as e:
        logger.error(f"Error en login: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/auth/refresh', methods=['POST'])
@require_auth
def refresh_token():
    """Renovar token JWT"""
    try:
        token_payload = {
            'username': g.current_user,
            'role': g.user_role,
            'permissions': g.user_permissions,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        new_token = jwt.encode(token_payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'token': new_token,
            'expires_in': 86400
        })
        
    except Exception as e:
        logger.error(f"Error renovando token: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== ENDPOINTS DE PRODUCTOS ====================

@app.route('/api/products', methods=['GET'])
@require_auth
@require_permission('read')
def get_products():
    """Obtener lista de productos"""
    try:
        import sqlite3
        
        conn = sqlite3.connect(ims.db_path)
        cursor = conn.cursor()
        
        # Obtener productos con información de stock
        query = '''
            SELECT p.*, COALESCE(SUM(i.quantity), 0) as current_stock
            FROM products p
            LEFT JOIN inventory i ON p.id = i.product_id
            GROUP BY p.id
            ORDER BY p.name
        '''
        
        cursor.execute(query)
        products = []
        
        for row in cursor.fetchall():
            products.append({
                'id': row[0],
                'name': row[1],
                'category': row[2],
                'sku': row[3],
                'unit_cost': row[4],
                'selling_price': row[5],
                'supplier_id': row[6],
                'lead_time_days': row[7],
                'min_stock_level': row[8],
                'max_stock_level': row[9],
                'reorder_point': row[10],
                'reorder_quantity': row[11],
                'shelf_life_days': row[12],
                'storage_requirements': row[13],
                'current_stock': row[14]
            })
        
        conn.close()
        
        return jsonify({
            'products': products,
            'total': len(products),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo productos: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/products', methods=['POST'])
@require_auth
@require_permission('write')
@validate_json_data(['name', 'category', 'sku', 'unit_cost', 'selling_price'])
def create_product():
    """Crear nuevo producto"""
    try:
        from inventory_management_system import Product
        
        data = g.json_data
        
        # Generar ID único
        product_id = f"PROD_{secrets.token_hex(4).upper()}"
        
        product = Product(
            id=product_id,
            name=data['name'],
            category=data['category'],
            sku=data['sku'],
            unit_cost=float(data['unit_cost']),
            selling_price=float(data['selling_price']),
            supplier_id=data.get('supplier_id', 'SUP001'),
            lead_time_days=int(data.get('lead_time_days', 7)),
            min_stock_level=int(data.get('min_stock_level', 10)),
            max_stock_level=int(data.get('max_stock_level', 100)),
            reorder_point=int(data.get('reorder_point', 20)),
            reorder_quantity=int(data.get('reorder_quantity', 50)),
            shelf_life_days=data.get('shelf_life_days'),
            storage_requirements=data.get('storage_requirements')
        )
        
        ims.add_product(product)
        
        return jsonify({
            'message': 'Producto creado exitosamente',
            'product_id': product_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando producto: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/products/<product_id>', methods=['GET'])
@require_auth
@require_permission('read')
def get_product(product_id):
    """Obtener producto específico"""
    try:
        import sqlite3
        
        conn = sqlite3.connect(ims.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        # Obtener stock actual
        cursor.execute('SELECT SUM(quantity) FROM inventory WHERE product_id = ?', (product_id,))
        current_stock = cursor.fetchone()[0] or 0
        
        conn.close()
        
        product = {
            'id': row[0],
            'name': row[1],
            'category': row[2],
            'sku': row[3],
            'unit_cost': row[4],
            'selling_price': row[5],
            'supplier_id': row[6],
            'lead_time_days': row[7],
            'min_stock_level': row[8],
            'max_stock_level': row[9],
            'reorder_point': row[10],
            'reorder_quantity': row[11],
            'shelf_life_days': row[12],
            'storage_requirements': row[13],
            'current_stock': current_stock
        }
        
        return jsonify(product)
        
    except Exception as e:
        logger.error(f"Error obteniendo producto: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/products/<product_id>', methods=['PUT'])
@require_auth
@require_permission('write')
def update_product(product_id):
    """Actualizar producto"""
    try:
        data = request.get_json()
        
        import sqlite3
        conn = sqlite3.connect(ims.db_path)
        cursor = conn.cursor()
        
        # Verificar que el producto existe
        cursor.execute('SELECT id FROM products WHERE id = ?', (product_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        # Actualizar campos permitidos
        update_fields = []
        update_values = []
        
        allowed_fields = ['name', 'category', 'sku', 'unit_cost', 'selling_price',
                         'supplier_id', 'lead_time_days', 'min_stock_level',
                         'max_stock_level', 'reorder_point', 'reorder_quantity',
                         'shelf_life_days', 'storage_requirements']
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = ?")
                update_values.append(data[field])
        
        if update_fields:
            update_values.append(product_id)
            query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, update_values)
            conn.commit()
        
        conn.close()
        
        return jsonify({'message': 'Producto actualizado exitosamente'})
        
    except Exception as e:
        logger.error(f"Error actualizando producto: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/products/<product_id>', methods=['DELETE'])
@require_auth
@require_permission('delete')
def delete_product(product_id):
    """Eliminar producto"""
    try:
        import sqlite3
        
        conn = sqlite3.connect(ims.db_path)
        cursor = conn.cursor()
        
        # Verificar que el producto existe
        cursor.execute('SELECT id FROM products WHERE id = ?', (product_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        # Eliminar registros relacionados
        cursor.execute('DELETE FROM inventory WHERE product_id = ?', (product_id,))
        cursor.execute('DELETE FROM alerts WHERE product_id = ?', (product_id,))
        cursor.execute('DELETE FROM sales_history WHERE product_id = ?', (product_id,))
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Producto eliminado exitosamente'})
        
    except Exception as e:
        logger.error(f"Error eliminando producto: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== ENDPOINTS DE INVENTARIO ====================

@app.route('/api/inventory', methods=['GET'])
@require_auth
@require_permission('read')
def get_inventory():
    """Obtener inventario completo"""
    try:
        import sqlite3
        
        conn = sqlite3.connect(ims.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT i.*, p.name as product_name, p.category
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            ORDER BY p.name, i.location
        '''
        
        cursor.execute(query)
        inventory_items = []
        
        for row in cursor.fetchall():
            inventory_items.append({
                'id': row[0],
                'product_id': row[1],
                'product_name': row[6],
                'category': row[7],
                'quantity': row[2],
                'location': row[3],
                'batch_number': row[4],
                'expiry_date': row[5],
                'last_updated': row[5]
            })
        
        conn.close()
        
        return jsonify({
            'inventory': inventory_items,
            'total_items': len(inventory_items),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo inventario: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/inventory/update', methods=['POST'])
@require_auth
@require_permission('write')
@validate_json_data(['product_id', 'quantity_change'])
def update_inventory():
    """Actualizar inventario"""
    try:
        data = g.json_data
        
        product_id = data['product_id']
        quantity_change = int(data['quantity_change'])
        location = data.get('location', 'main_warehouse')
        batch_number = data.get('batch_number')
        expiry_date = data.get('expiry_date')
        
        # Convertir fecha de vencimiento si se proporciona
        if expiry_date:
            expiry_date = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
        
        ims.update_inventory(
            product_id=product_id,
            quantity_change=quantity_change,
            location=location,
            batch_number=batch_number,
            expiry_date=expiry_date
        )
        
        return jsonify({'message': 'Inventario actualizado exitosamente'})
        
    except Exception as e:
        logger.error(f"Error actualizando inventario: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== ENDPOINTS DE ALERTAS ====================

@app.route('/api/alerts', methods=['GET'])
@require_auth
@require_permission('read')
def get_alerts():
    """Obtener alertas activas"""
    try:
        alerts = ims.get_alerts_summary()
        
        return jsonify({
            'alerts': alerts,
            'total': len(alerts),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo alertas: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/alerts/<alert_id>/resolve', methods=['POST'])
@require_auth
@require_permission('write')
def resolve_alert(alert_id):
    """Resolver alerta"""
    try:
        import sqlite3
        
        conn = sqlite3.connect(ims.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE alerts SET resolved = TRUE WHERE id = ?', (alert_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Alerta no encontrada'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Alerta resuelta exitosamente'})
        
    except Exception as e:
        logger.error(f"Error resolviendo alerta: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== ENDPOINTS DE ANÁLISIS ====================

@app.route('/api/analytics/kpis', methods=['GET'])
@require_auth
@require_permission('read')
def get_kpis():
    """Obtener KPIs del sistema"""
    try:
        kpis = ims.generate_kpis()
        return jsonify(kpis)
        
    except Exception as e:
        logger.error(f"Error obteniendo KPIs: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/analytics/abc', methods=['GET'])
@require_auth
@require_permission('read')
def get_abc_analysis():
    """Obtener análisis ABC"""
    try:
        abc_analysis = analytics.abc_analysis()
        return jsonify(abc_analysis)
        
    except Exception as e:
        logger.error(f"Error obteniendo análisis ABC: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/analytics/optimization', methods=['GET'])
@require_auth
@require_permission('read')
def get_optimization():
    """Obtener recomendaciones de optimización"""
    try:
        optimization = analytics.inventory_optimization()
        return jsonify(optimization)
        
    except Exception as e:
        logger.error(f"Error obteniendo optimización: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/analytics/forecast/<product_id>', methods=['GET'])
@require_auth
@require_permission('read')
def get_forecast(product_id):
    """Obtener predicción de demanda para un producto"""
    try:
        days_ahead = request.args.get('days', 30, type=int)
        
        # Predicción básica
        basic_forecast = ims.predict_demand(product_id, days_ahead)
        
        # Predicción con ML si hay suficientes datos
        try:
            ml_forecast = analytics.demand_forecasting_ml(product_id, days_ahead)
        except:
            ml_forecast = None
        
        return jsonify({
            'product_id': product_id,
            'days_ahead': days_ahead,
            'basic_forecast': basic_forecast,
            'ml_forecast': ml_forecast,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo predicción: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== ENDPOINTS DEL SISTEMA ====================

@app.route('/api/system/status', methods=['GET'])
@require_auth
@require_permission('read')
def get_system_status():
    """Obtener estado del sistema"""
    try:
        status = enhanced_system.get_system_status()
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del sistema: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/system/health', methods=['GET'])
@require_auth
@require_permission('read')
def get_system_health():
    """Obtener reporte de salud del sistema"""
    try:
        health_report = enhanced_system._generate_health_report()
        return jsonify(health_report)
        
    except Exception as e:
        logger.error(f"Error obteniendo salud del sistema: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/system/backup', methods=['POST'])
@require_auth
@require_permission('admin')
def create_backup():
    """Crear respaldo manual"""
    try:
        enhanced_system.backup_database()
        return jsonify({'message': 'Respaldo creado exitosamente'})
        
    except Exception as e:
        logger.error(f"Error creando respaldo: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== ENDPOINTS DE DOCUMENTACIÓN ====================

@app.route('/api/docs', methods=['GET'])
def get_api_docs():
    """Obtener documentación de la API"""
    docs = {
        'title': 'API Sistema de Gestión de Inventario',
        'version': '1.0.0',
        'description': 'API REST completa para gestión de inventario y cadena de suministro',
        'authentication': {
            'type': 'JWT Bearer Token',
            'login_endpoint': '/api/auth/login',
            'refresh_endpoint': '/api/auth/refresh'
        },
        'endpoints': {
            'products': {
                'GET /api/products': 'Obtener lista de productos',
                'POST /api/products': 'Crear nuevo producto',
                'GET /api/products/{id}': 'Obtener producto específico',
                'PUT /api/products/{id}': 'Actualizar producto',
                'DELETE /api/products/{id}': 'Eliminar producto'
            },
            'inventory': {
                'GET /api/inventory': 'Obtener inventario completo',
                'POST /api/inventory/update': 'Actualizar inventario'
            },
            'alerts': {
                'GET /api/alerts': 'Obtener alertas activas',
                'POST /api/alerts/{id}/resolve': 'Resolver alerta'
            },
            'analytics': {
                'GET /api/analytics/kpis': 'Obtener KPIs',
                'GET /api/analytics/abc': 'Análisis ABC',
                'GET /api/analytics/optimization': 'Recomendaciones de optimización',
                'GET /api/analytics/forecast/{id}': 'Predicción de demanda'
            },
            'system': {
                'GET /api/system/status': 'Estado del sistema',
                'GET /api/system/health': 'Salud del sistema',
                'POST /api/system/backup': 'Crear respaldo'
            }
        },
        'rate_limits': {
            'default': '1000 per day, 100 per hour',
            'login': '5 per minute'
        },
        'permissions': {
            'read': 'Lectura de datos',
            'write': 'Escritura de datos',
            'delete': 'Eliminación de datos',
            'admin': 'Administración del sistema'
        }
    }
    
    return jsonify(docs)

# ==================== MANEJO DE ERRORES ====================

@app.errorhandler(429)
def handle_rate_limit(e):
    """Manejar límites de tasa"""
    return jsonify({
        'error': 'Límite de tasa excedido',
        'message': 'Demasiadas solicitudes. Intente más tarde.',
        'retry_after': e.retry_after
    }), 429

@app.errorhandler(404)
def handle_not_found(e):
    """Manejar errores 404"""
    return jsonify({
        'error': 'Endpoint no encontrado',
        'message': 'El endpoint solicitado no existe'
    }), 404

@app.errorhandler(500)
def handle_internal_error(e):
    """Manejar errores internos"""
    logger.error(f"Error interno: {e}")
    return jsonify({
        'error': 'Error interno del servidor',
        'message': 'Se produjo un error inesperado'
    }), 500

# ==================== FUNCIÓN PRINCIPAL ====================

if __name__ == '__main__':
    logger.info("Iniciando API REST del Sistema de Gestión de Inventario")
    
    # Crear tablas si no existen
    try:
        ims.init_database()
        logger.info("Base de datos inicializada")
    except Exception as e:
        logger.error(f"Error inicializando base de datos: {e}")
    
    # Ejecutar servidor
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5001,  # Puerto diferente al dashboard
        threaded=True
    )



