#!/usr/bin/env python3
"""
API REST Completa - Sistema de Organización de Documentos
========================================================

API REST moderna con Flask que proporciona endpoints para:
- Gestión de documentos
- Búsqueda avanzada con IA
- Sistema de colaboración
- Analytics en tiempo real
- Integración con servicios externos

Autor: Sistema de Organización Enterprise
Versión: 1.0
Fecha: 2024
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.utils import secure_filename
import os
import json
import sqlite3
import hashlib
import jwt
import datetime
from functools import wraps
from pathlib import Path
import threading
import time
from typing import Dict, List, Optional
import logging

# Importar módulos del sistema
import sys
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

from busqueda_avanzada_ia import BuscadorIA
from sistema_respaldo import SistemaRespaldo
from analytics_sistema import AnalyticsSistema

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
app.config['UPLOAD_FOLDER'] = '/Users/adan/frontier/docuementos/uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Inicializar componentes del sistema
buscador_ia = BuscadorIA()
sistema_respaldo = SistemaRespaldo()
analytics = AnalyticsSistema()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base de datos para usuarios y sesiones
def init_auth_db():
    """Inicializa base de datos de autenticación"""
    conn = sqlite3.connect('auth.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            token TEXT UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Decorador para autenticación JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token de acceso requerido'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['user_id']
        except:
            return jsonify({'message': 'Token inválido'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# ==================== ENDPOINTS DE AUTENTICACIÓN ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Registro de nuevos usuarios"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'error': 'Datos incompletos'}), 400
        
        # Hash de contraseña
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect('auth.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', (username, email, password_hash))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            # Generar token JWT
            token = jwt.encode({
                'user_id': user_id,
                'username': username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                'message': 'Usuario registrado exitosamente',
                'token': token,
                'user_id': user_id
            }), 201
            
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Usuario o email ya existe'}), 409
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"Error en registro: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Inicio de sesión de usuarios"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect('auth.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, role FROM users
            WHERE username = ? AND password_hash = ? AND is_active = 1
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        
        if user:
            user_id, username, email, role = user
            
            # Actualizar último login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (user_id,))
            
            # Generar token JWT
            token = jwt.encode({
                'user_id': user_id,
                'username': username,
                'role': role,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'message': 'Login exitoso',
                'token': token,
                'user': {
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'role': role
                }
            }), 200
        else:
            conn.close()
            return jsonify({'error': 'Credenciales inválidas'}), 401
            
    except Exception as e:
        logger.error(f"Error en login: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== ENDPOINTS DE DOCUMENTOS ====================

@app.route('/api/documents', methods=['GET'])
@token_required
def get_documents(current_user):
    """Obtener lista de documentos con filtros"""
    try:
        # Parámetros de consulta
        category = request.args.get('category')
        search = request.args.get('search')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Construir consulta
        query = "SELECT * FROM accesos_archivos WHERE 1=1"
        params = []
        
        if category:
            query += " AND ruta LIKE ?"
            params.append(f"%{category}%")
        
        if search:
            query += " AND (archivo LIKE ? OR ruta LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        conn = sqlite3.connect(analytics.db_path)
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        documents = cursor.fetchall()
        
        # Convertir a formato JSON
        result = []
        for doc in documents:
            result.append({
                'id': doc[0],
                'archivo': doc[1],
                'ruta': doc[2],
                'tipo_archivo': doc[3],
                'tamaño': doc[4],
                'timestamp': doc[5],
                'usuario': doc[6],
                'accion': doc[7],
                'duracion_segundos': doc[8]
            })
        
        conn.close()
        
        return jsonify({
            'documents': result,
            'total': len(result),
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo documentos: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/documents/upload', methods=['POST'])
@token_required
def upload_document(current_user):
    """Subir nuevo documento"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se proporcionó archivo'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nombre de archivo vacío'}), 400
        
        if file:
            filename = secure_filename(file.filename)
            category = request.form.get('category', 'uploads')
            
            # Crear directorio si no existe
            upload_dir = Path(app.config['UPLOAD_FOLDER']) / category
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Guardar archivo
            file_path = upload_dir / filename
            file.save(str(file_path))
            
            # Registrar en analytics
            analytics.registrar_acceso_archivo(
                str(file_path),
                f"{category}/{filename}",
                "upload",
                0,
                str(current_user)
            )
            
            return jsonify({
                'message': 'Archivo subido exitosamente',
                'filename': filename,
                'path': f"{category}/{filename}",
                'size': file_path.stat().st_size
            }), 201
            
    except Exception as e:
        logger.error(f"Error subiendo archivo: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/documents/<path:file_path>', methods=['GET'])
@token_required
def download_document(current_user, file_path):
    """Descargar documento"""
    try:
        # Registrar acceso
        analytics.registrar_acceso_archivo(
            file_path,
            file_path,
            "download",
            0,
            str(current_user)
        )
        
        # Enviar archivo
        return send_from_directory(
            '/Users/adan/frontier/docuementos',
            file_path,
            as_attachment=True
        )
        
    except Exception as e:
        logger.error(f"Error descargando archivo: {e}")
        return jsonify({'error': 'Archivo no encontrado'}), 404

# ==================== ENDPOINTS DE BÚSQUEDA ====================

@app.route('/api/search', methods=['POST'])
@token_required
def search_documents(current_user):
    """Búsqueda avanzada con IA"""
    try:
        data = request.get_json()
        query = data.get('query')
        limit = data.get('limit', 10)
        
        if not query:
            return jsonify({'error': 'Consulta de búsqueda requerida'}), 400
        
        # Ejecutar búsqueda con IA
        start_time = time.time()
        resultados = buscador_ia.buscar_semantica(query, limit)
        search_time = int((time.time() - start_time) * 1000)
        
        # Registrar búsqueda en analytics
        analytics.registrar_busqueda(
            query,
            len(resultados),
            search_time,
            "",
            str(current_user)
        )
        
        return jsonify({
            'query': query,
            'results': resultados,
            'total': len(resultados),
            'search_time_ms': search_time
        }), 200
        
    except Exception as e:
        logger.error(f"Error en búsqueda: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/search/suggestions', methods=['GET'])
@token_required
def get_search_suggestions(current_user):
    """Obtener sugerencias de búsqueda"""
    try:
        query = request.args.get('q', '')
        
        if len(query) < 2:
            return jsonify({'suggestions': []}), 200
        
        suggestions = buscador_ia.sugerir_terminos(query)
        
        return jsonify({
            'query': query,
            'suggestions': suggestions
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo sugerencias: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== ENDPOINTS DE ANALYTICS ====================

@app.route('/api/analytics/overview', methods=['GET'])
@token_required
def get_analytics_overview(current_user):
    """Obtener resumen de analytics"""
    try:
        # Obtener métricas básicas
        archivos_populares = analytics.obtener_archivos_mas_accedidos(dias=7, limite=5)
        busquedas_populares = analytics.obtener_busquedas_populares(dias=7, limite=5)
        tendencias = analytics.analizar_tendencias_uso(dias=7)
        
        return jsonify({
            'archivos_populares': archivos_populares,
            'busquedas_populares': busquedas_populares,
            'tendencias': tendencias,
            'timestamp': datetime.datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo analytics: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/analytics/recommendations', methods=['GET'])
@token_required
def get_recommendations(current_user):
    """Obtener recomendaciones del sistema"""
    try:
        recomendaciones = analytics.generar_recomendaciones()
        
        return jsonify({
            'recommendations': recomendaciones,
            'timestamp': datetime.datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo recomendaciones: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== ENDPOINTS DE RESPALDOS ====================

@app.route('/api/backups', methods=['GET'])
@token_required
def get_backups(current_user):
    """Obtener lista de respaldos"""
    try:
        respaldos = sistema_respaldo.listar_respaldos()
        
        return jsonify({
            'backups': respaldos,
            'total': len(respaldos)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo respaldos: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/backups/create', methods=['POST'])
@token_required
def create_backup(current_user):
    """Crear respaldo manual"""
    try:
        respaldo = sistema_respaldo.crear_respaldo_completo()
        
        if respaldo:
            return jsonify({
                'message': 'Respaldo creado exitosamente',
                'backup_path': str(respaldo)
            }), 201
        else:
            return jsonify({'error': 'Error creando respaldo'}), 500
            
    except Exception as e:
        logger.error(f"Error creando respaldo: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/backups/<backup_name>/restore', methods=['POST'])
@token_required
def restore_backup(current_user, backup_name):
    """Restaurar respaldo específico"""
    try:
        data = request.get_json()
        destination = data.get('destination')
        
        success = sistema_respaldo.restaurar_respaldo(backup_name, destination)
        
        if success:
            return jsonify({
                'message': 'Respaldo restaurado exitosamente',
                'backup_name': backup_name
            }), 200
        else:
            return jsonify({'error': 'Error restaurando respaldo'}), 500
            
    except Exception as e:
        logger.error(f"Error restaurando respaldo: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== WEBSOCKETS PARA COLABORACIÓN ====================

@socketio.on('join_room')
def on_join(data):
    """Unirse a sala de colaboración"""
    room = data['room']
    join_room(room)
    emit('status', {'msg': f'Usuario se unió a la sala {room}'}, room=room)

@socketio.on('leave_room')
def on_leave(data):
    """Salir de sala de colaboración"""
    room = data['room']
    leave_room(room)
    emit('status', {'msg': f'Usuario salió de la sala {room}'}, room=room)

@socketio.on('document_edit')
def on_document_edit(data):
    """Notificar edición de documento"""
    room = data['room']
    document = data['document']
    changes = data['changes']
    
    emit('document_updated', {
        'document': document,
        'changes': changes,
        'timestamp': datetime.datetime.now().isoformat()
    }, room=room, include_self=False)

@socketio.on('user_typing')
def on_user_typing(data):
    """Notificar que usuario está escribiendo"""
    room = data['room']
    user = data['user']
    
    emit('typing', {
        'user': user,
        'is_typing': data['is_typing']
    }, room=room, include_self=False)

# ==================== ENDPOINTS DE SISTEMA ====================

@app.route('/api/system/status', methods=['GET'])
@token_required
def get_system_status(current_user):
    """Obtener estado del sistema"""
    try:
        # Obtener métricas del sistema
        total_archivos = len(list(Path('/Users/adan/frontier/docuementos').rglob('*')))
        total_carpetas = len(list(Path('/Users/adan/frontier/docuementos').rglob('*/')))
        
        # Calcular espacio usado
        espacio_usado = sum(f.stat().st_size for f in Path('/Users/adan/frontier/docuementos').rglob('*') if f.is_file())
        espacio_mb = espacio_usado / (1024 * 1024)
        
        return jsonify({
            'status': 'operational',
            'total_files': total_archivos,
            'total_folders': total_carpetas,
            'space_used_mb': round(espacio_mb, 2),
            'uptime': 'N/A',  # En producción, calcular uptime real
            'timestamp': datetime.datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del sistema: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/system/maintenance', methods=['POST'])
@token_required
def run_maintenance(current_user):
    """Ejecutar mantenimiento del sistema"""
    try:
        # Ejecutar mantenimiento en hilo separado
        def run_maintenance_task():
            from mantenimiento_automatico import MantenimientoAutomatico
            mantenimiento = MantenimientoAutomatico()
            mantenimiento.ejecutar_mantenimiento_completo()
        
        thread = threading.Thread(target=run_maintenance_task)
        thread.start()
        
        return jsonify({
            'message': 'Mantenimiento iniciado en segundo plano',
            'status': 'running'
        }), 202
        
    except Exception as e:
        logger.error(f"Error ejecutando mantenimiento: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== ENDPOINTS DE CONFIGURACIÓN ====================

@app.route('/api/config', methods=['GET'])
@token_required
def get_config(current_user):
    """Obtener configuración del sistema"""
    try:
        config_files = {
            'main': 'config.json',
            'backup': 'backup_config.json',
            'analytics': 'analytics_config.json'
        }
        
        configs = {}
        for name, filename in config_files.items():
            config_path = Path('/Users/adan/frontier/docuementos') / filename
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    configs[name] = json.load(f)
        
        return jsonify({
            'configs': configs,
            'timestamp': datetime.datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo configuración: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/config/<config_name>', methods=['PUT'])
@token_required
def update_config(current_user, config_name):
    """Actualizar configuración del sistema"""
    try:
        data = request.get_json()
        
        config_files = {
            'main': 'config.json',
            'backup': 'backup_config.json',
            'analytics': 'analytics_config.json'
        }
        
        if config_name not in config_files:
            return jsonify({'error': 'Configuración no encontrada'}), 404
        
        config_path = Path('/Users/adan/frontier/docuementos') / config_files[config_name]
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'message': f'Configuración {config_name} actualizada exitosamente',
            'config': data
        }), 200
        
    except Exception as e:
        logger.error(f"Error actualizando configuración: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== MANEJO DE ERRORES ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

@app.errorhandler(413)
def too_large(error):
    return jsonify({'error': 'Archivo demasiado grande'}), 413

# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """Función principal para ejecutar la API"""
    print("🚀 Iniciando API REST del Sistema de Organización de Documentos")
    print("=============================================================")
    
    # Inicializar base de datos de autenticación
    init_auth_db()
    
    # Crear directorio de uploads
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
    
    # Inicializar componentes del sistema
    print("🔧 Inicializando componentes del sistema...")
    buscador_ia.indexar_documentos()
    print("✅ Sistema inicializado correctamente")
    
    print("\n📋 Endpoints disponibles:")
    print("  🔐 /api/auth/register - Registro de usuarios")
    print("  🔐 /api/auth/login - Inicio de sesión")
    print("  📁 /api/documents - Gestión de documentos")
    print("  🔍 /api/search - Búsqueda avanzada con IA")
    print("  📊 /api/analytics - Analytics y métricas")
    print("  💾 /api/backups - Gestión de respaldos")
    print("  ⚙️  /api/system - Estado del sistema")
    print("  🔧 /api/config - Configuración")
    
    print("\n🌐 Servidor iniciando en http://localhost:5000")
    print("📡 WebSocket disponible para colaboración en tiempo real")
    
    # Ejecutar servidor
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()


