#!/usr/bin/env python3
"""
Aplicación móvil nativa para el sistema de organización empresarial
"""

import os
import json
import sqlite3
from datetime import datetime
import webbrowser
import threading
import time
from flask import Flask, render_template, request, jsonify, send_file
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)

class MobileApp:
    def __init__(self, base_path="/Users/adan/frontier"):
        self.base_path = base_path
        self.db_path = os.path.join(base_path, "search_index.db")
        self.mobile_db = os.path.join(base_path, "mobile_app.db")
        self.business_areas = {
            '01_Marketing': 'Marketing',
            '02_Finance': 'Finance',
            '03_Human_Resources': 'Human Resources',
            '04_Operations': 'Operations',
            '05_Technology': 'Technology',
            '06_Strategy': 'Strategy',
            '07_Risk_Management': 'Risk Management',
            '08_AI_Artificial_Intelligence': 'AI & Artificial Intelligence',
            '09_Sales': 'Sales',
            '10_Customer_Service': 'Customer Service',
            '11_Research_Development': 'Research & Development',
            '12_Quality_Assurance': 'Quality Assurance',
            '13_Legal_Compliance': 'Legal & Compliance',
            '14_Procurement': 'Procurement',
            '15_Logistics': 'Logistics',
            '16_Data_Analytics': 'Data Analytics',
            '17_Innovation': 'Innovation',
            '18_Sustainability': 'Sustainability',
            '19_International_Business': 'International Business',
            '20_Project_Management': 'Project Management'
        }
        self.init_mobile_database()
    
    def init_mobile_database(self):
        """Inicializar base de datos móvil"""
        conn = sqlite3.connect(self.mobile_db)
        cursor = conn.cursor()
        
        # Tabla de sesiones móviles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mobile_sessions (
                id TEXT PRIMARY KEY,
                device_info TEXT,
                last_access TEXT,
                access_count INTEGER DEFAULT 0,
                preferences TEXT
            )
        ''')
        
        # Tabla de favoritos móviles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mobile_favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                file_path TEXT,
                added_at TEXT,
                FOREIGN KEY (session_id) REFERENCES mobile_sessions (id)
            )
        ''')
        
        # Tabla de notificaciones móviles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mobile_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                title TEXT,
                message TEXT,
                type TEXT,
                created_at TEXT,
                read_at TEXT,
                FOREIGN KEY (session_id) REFERENCES mobile_sessions (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_mobile_session(self, device_info):
        """Crear sesión móvil"""
        session_id = f"mobile_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        conn = sqlite3.connect(self.mobile_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO mobile_sessions (id, device_info, last_access, access_count, preferences)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, device_info, datetime.now().isoformat(), 1, '{}'))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def update_session(self, session_id):
        """Actualizar sesión móvil"""
        conn = sqlite3.connect(self.mobile_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE mobile_sessions
            SET last_access = ?, access_count = access_count + 1
            WHERE id = ?
        ''', (datetime.now().isoformat(), session_id))
        
        conn.commit()
        conn.close()
    
    def get_mobile_stats(self):
        """Obtener estadísticas para móvil"""
        stats = {
            'total_files': 0,
            'areas': {},
            'recent_files': [],
            'popular_files': [],
            'mobile_users': 0
        }
        
        # Contar archivos por área
        for area_code, area_name in self.business_areas.items():
            area_path = os.path.join(self.base_path, area_code)
            if os.path.exists(area_path):
                file_count = 0
                total_size = 0
                
                for root, dirs, files in os.walk(area_path):
                    for file in files:
                        if file.endswith('.md'):
                            file_path = os.path.join(root, file)
                            try:
                                file_size = os.path.getsize(file_path)
                                total_size += file_size
                                file_count += 1
                            except:
                                pass
                
                stats['areas'][area_name] = {
                    'files': file_count,
                    'size_mb': round(total_size / 1024 / 1024, 2)
                }
                stats['total_files'] += file_count
        
        # Obtener archivos recientes
        recent_files = []
        for area_code, area_name in self.business_areas.items():
            area_path = os.path.join(self.base_path, area_code)
            if os.path.exists(area_path):
                for root, dirs, files in os.walk(area_path):
                    for file in files:
                        if file.endswith('.md'):
                            file_path = os.path.join(root, file)
                            try:
                                stat = os.stat(file_path)
                                modified = datetime.fromtimestamp(stat.st_mtime)
                                recent_files.append({
                                    'filename': file,
                                    'area': area_name,
                                    'path': file_path,
                                    'modified': modified.isoformat(),
                                    'size': stat.st_size
                                })
                            except:
                                pass
        
        # Ordenar por fecha de modificación
        recent_files.sort(key=lambda x: x['modified'], reverse=True)
        stats['recent_files'] = recent_files[:10]
        
        # Contar usuarios móviles
        conn = sqlite3.connect(self.mobile_db)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(DISTINCT id) FROM mobile_sessions')
        stats['mobile_users'] = cursor.fetchone()[0]
        conn.close()
        
        return stats
    
    def search_mobile(self, query, area=None, limit=10):
        """Búsqueda optimizada para móvil"""
        if not os.path.exists(self.db_path):
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        where_conditions = []
        params = []
        
        if area:
            where_conditions.append("area = ?")
            params.append(area)
        
        where_conditions.append("(filename LIKE ? OR content LIKE ?)")
        params.extend([f"%{query}%", f"%{query}%"])
        
        where_clause = " AND ".join(where_conditions)
        
        sql = f'''
            SELECT filename, area, path, file_size, last_modified
            FROM documents
            WHERE {where_clause}
            ORDER BY 
                CASE WHEN filename LIKE ? THEN 1 ELSE 2 END,
                last_modified DESC
            LIMIT ?
        '''
        
        params = [f"%{query}%"] + params + [limit]
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        
        search_results = []
        for row in results:
            filename, area, path, file_size, last_modified = row
            search_results.append({
                'filename': filename,
                'area': area,
                'path': path,
                'file_size': file_size,
                'last_modified': last_modified,
                'size_kb': round(file_size / 1024, 1)
            })
        
        conn.close()
        return search_results
    
    def add_favorite(self, session_id, file_path):
        """Agregar a favoritos"""
        conn = sqlite3.connect(self.mobile_db)
        cursor = conn.cursor()
        
        # Verificar si ya existe
        cursor.execute('''
            SELECT id FROM mobile_favorites
            WHERE session_id = ? AND file_path = ?
        ''', (session_id, file_path))
        
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO mobile_favorites (session_id, file_path, added_at)
                VALUES (?, ?, ?)
            ''', (session_id, file_path, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_favorites(self, session_id):
        """Obtener favoritos"""
        conn = sqlite3.connect(self.mobile_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT file_path, added_at FROM mobile_favorites
            WHERE session_id = ?
            ORDER BY added_at DESC
        ''', (session_id,))
        
        favorites = []
        for row in cursor.fetchall():
            file_path, added_at = row
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)
                try:
                    stat = os.stat(file_path)
                    favorites.append({
                        'filename': filename,
                        'path': file_path,
                        'added_at': added_at,
                        'size_kb': round(stat.st_size / 1024, 1)
                    })
                except:
                    pass
        
        conn.close()
        return favorites
    
    def create_qr_code(self, url):
        """Crear código QR para acceso móvil"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()

# Crear instancia global
mobile_app = MobileApp()

@app.route('/mobile')
def mobile_home():
    """Página principal móvil"""
    stats = mobile_app.get_mobile_stats()
    return render_template('mobile/index.html', stats=stats, areas=mobile_app.business_areas)

@app.route('/mobile/api/search')
def mobile_api_search():
    """API de búsqueda móvil"""
    query = request.args.get('q', '')
    area = request.args.get('area', '')
    limit = int(request.args.get('limit', 10))
    
    if not query:
        return jsonify({'results': [], 'total': 0})
    
    results = mobile_app.search_mobile(query, area if area else None, limit)
    
    return jsonify({
        'results': results,
        'total': len(results),
        'query': query,
        'area': area
    })

@app.route('/mobile/api/stats')
def mobile_api_stats():
    """API de estadísticas móviles"""
    stats = mobile_app.get_mobile_stats()
    return jsonify(stats)

@app.route('/mobile/api/favorites', methods=['POST'])
def mobile_api_add_favorite():
    """API para agregar favorito"""
    data = request.get_json()
    session_id = data.get('session_id')
    file_path = data.get('file_path')
    
    if session_id and file_path:
        mobile_app.add_favorite(session_id, file_path)
        return jsonify({'status': 'success'})
    
    return jsonify({'status': 'error'}), 400

@app.route('/mobile/api/favorites/<session_id>')
def mobile_api_get_favorites(session_id):
    """API para obtener favoritos"""
    favorites = mobile_app.get_favorites(session_id)
    return jsonify({'favorites': favorites})

@app.route('/mobile/qr')
def mobile_qr():
    """Generar código QR para acceso móvil"""
    base_url = request.host_url
    mobile_url = f"{base_url}mobile"
    qr_code = mobile_app.create_qr_code(mobile_url)
    
    return render_template('mobile/qr.html', qr_code=qr_code, mobile_url=mobile_url)

def create_mobile_templates():
    """Crear plantillas móviles"""
    mobile_templates_dir = os.path.join(mobile_app.base_path, "templates", "mobile")
    os.makedirs(mobile_templates_dir, exist_ok=True)
    
    # Template base móvil
    mobile_base = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>{% block title %}Sistema Empresarial Móvil{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .mobile-container { max-width: 100%; padding: 0; }
        .mobile-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .mobile-card { border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px; }
        .mobile-btn { border-radius: 25px; padding: 10px 20px; }
        .mobile-search { border-radius: 25px; }
        .mobile-stats { background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%); color: white; }
        .swipe-indicator { text-align: center; color: #666; font-size: 12px; }
        .touch-friendly { min-height: 44px; }
    </style>
</head>
<body class="bg-light">
    <div class="mobile-container">
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''
    
    with open(os.path.join(mobile_templates_dir, 'base.html'), 'w') as f:
        f.write(mobile_base)
    
    # Template principal móvil
    mobile_index = '''{% extends "mobile/base.html" %}

{% block title %}Sistema Empresarial Móvil{% endblock %}

{% block content %}
<div class="mobile-header text-center py-4">
    <h1 class="mb-2">
        <i class="fas fa-mobile-alt me-2"></i>Sistema Empresarial
    </h1>
    <p class="mb-0">Acceso móvil optimizado</p>
</div>

<div class="container py-3">
    <!-- Búsqueda móvil -->
    <div class="mobile-card p-3 mb-3">
        <div class="input-group">
            <input type="text" class="form-control mobile-search" id="mobileSearch" placeholder="Buscar documentos...">
            <button class="btn btn-primary mobile-btn" onclick="performMobileSearch()">
                <i class="fas fa-search"></i>
            </button>
        </div>
        <div class="mt-2">
            <select class="form-select mobile-search" id="mobileArea">
                <option value="">Todas las áreas</option>
                {% for code, name in areas.items() %}
                <option value="{{ code }}">{{ name }}</option>
                {% endfor %}
            </select>
        </div>
    </div>
    
    <!-- Estadísticas móviles -->
    <div class="row mb-3">
        <div class="col-6">
            <div class="mobile-card mobile-stats text-center p-3">
                <i class="fas fa-file-alt fa-2x mb-2"></i>
                <h4>{{ stats.total_files }}</h4>
                <small>Documentos</small>
            </div>
        </div>
        <div class="col-6">
            <div class="mobile-card bg-primary text-white text-center p-3">
                <i class="fas fa-building fa-2x mb-2"></i>
                <h4>{{ stats.areas|length }}</h4>
                <small>Áreas</small>
            </div>
        </div>
    </div>
    
    <!-- Áreas principales -->
    <div class="mobile-card p-3 mb-3">
        <h5 class="mb-3">
            <i class="fas fa-folder-open me-2"></i>Áreas Principales
        </h5>
        <div class="row">
            {% for code, name in areas.items() %}
            {% if loop.index <= 6 %}
            <div class="col-6 mb-2">
                <a href="/mobile/browse/{{ code }}" class="btn btn-outline-primary w-100 mobile-btn">
                    <i class="fas fa-folder me-1"></i>{{ name }}
                </a>
            </div>
            {% endif %}
            {% endfor %}
        </div>
        <div class="text-center mt-2">
            <a href="/mobile/areas" class="btn btn-link">Ver todas las áreas</a>
        </div>
    </div>
    
    <!-- Archivos recientes -->
    <div class="mobile-card p-3 mb-3">
        <h5 class="mb-3">
            <i class="fas fa-clock me-2"></i>Archivos Recientes
        </h5>
        <div id="recentFiles">
            {% for file in stats.recent_files[:5] %}
            <div class="d-flex justify-content-between align-items-center mb-2">
                <div>
                    <strong>{{ file.filename }}</strong>
                    <br><small class="text-muted">{{ file.area }}</small>
                </div>
                <div class="text-end">
                    <small>{{ file.size_kb }} KB</small>
                    <br><small class="text-muted">{{ file.modified[:10] }}</small>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <!-- Resultados de búsqueda -->
    <div id="mobileSearchResults" style="display: none;">
        <div class="mobile-card p-3">
            <h5>Resultados de Búsqueda</h5>
            <div id="mobileResultsContainer"></div>
        </div>
    </div>
    
    <!-- Indicador de deslizar -->
    <div class="swipe-indicator">
        <i class="fas fa-hand-pointer"></i> Desliza para más opciones
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
let mobileSessionId = 'mobile_' + new Date().getTime();

function performMobileSearch() {
    const query = document.getElementById('mobileSearch').value;
    const area = document.getElementById('mobileArea').value;
    
    if (!query.trim()) return;
    
    axios.get('/mobile/api/search', {
        params: { q: query, area: area }
    })
    .then(response => {
        displayMobileResults(response.data.results);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function displayMobileResults(results) {
    const container = document.getElementById('mobileResultsContainer');
    const resultsDiv = document.getElementById('mobileSearchResults');
    
    if (results.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No se encontraron resultados</div>';
    } else {
        let html = '';
        results.forEach(result => {
            html += `
                <div class="d-flex justify-content-between align-items-center mb-2 p-2 border-bottom">
                    <div>
                        <strong>${result.filename}</strong>
                        <br><small class="text-muted">${result.area}</small>
                    </div>
                    <div class="text-end">
                        <small>${result.size_kb} KB</small>
                        <br><button class="btn btn-sm btn-primary" onclick="viewMobileFile('${result.path}')">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                </div>
            `;
        });
        container.innerHTML = html;
    }
    
    resultsDiv.style.display = 'block';
}

function viewMobileFile(filePath) {
    // Implementar visualización de archivo
    alert('Visualizando: ' + filePath);
}

// Event listeners para móvil
document.getElementById('mobileSearch').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        performMobileSearch();
    }
});

// Touch events para mejor experiencia móvil
let startY = 0;
document.addEventListener('touchstart', function(e) {
    startY = e.touches[0].clientY;
});

document.addEventListener('touchend', function(e) {
    const endY = e.changedTouches[0].clientY;
    const diff = startY - endY;
    
    if (Math.abs(diff) > 50) {
        if (diff > 0) {
            // Swipe up - mostrar más opciones
            console.log('Swipe up detected');
        } else {
            // Swipe down - ocultar opciones
            console.log('Swipe down detected');
        }
    }
});
</script>
{% endblock %}'''
    
    with open(os.path.join(mobile_templates_dir, 'index.html'), 'w') as f:
        f.write(mobile_index)
    
    # Template QR
    mobile_qr = '''{% extends "mobile/base.html" %}

{% block title %}Código QR - Acceso Móvil{% endblock %}

{% block content %}
<div class="mobile-header text-center py-4">
    <h1 class="mb-2">
        <i class="fas fa-qrcode me-2"></i>Código QR
    </h1>
    <p class="mb-0">Acceso rápido desde móvil</p>
</div>

<div class="container py-4">
    <div class="mobile-card p-4 text-center">
        <h5 class="mb-3">Escanea con tu móvil</h5>
        <img src="data:image/png;base64,{{ qr_code }}" class="img-fluid mb-3" style="max-width: 200px;">
        <p class="text-muted mb-3">{{ mobile_url }}</p>
        <div class="alert alert-info">
            <i class="fas fa-info-circle me-2"></i>
            Usa la cámara de tu móvil para escanear este código
        </div>
    </div>
</div>
{% endblock %}'''
    
    with open(os.path.join(mobile_templates_dir, 'qr.html'), 'w') as f:
        f.write(mobile_qr)

def start_mobile_server(port=5001):
    """Iniciar servidor móvil"""
    print(f"📱 Iniciando servidor móvil en puerto {port}...")
    print(f"🌐 Accede a: http://localhost:{port}/mobile")
    print(f"📱 QR Code: http://localhost:{port}/mobile/qr")
    
    # Crear plantillas móviles
    create_mobile_templates()
    
    # Abrir navegador automáticamente
    def open_mobile_browser():
        time.sleep(2)
        webbrowser.open(f'http://localhost:{port}/mobile')
    
    threading.Thread(target=open_mobile_browser).start()
    
    # Iniciar servidor Flask
    app.run(host='0.0.0.0', port=port, debug=False)

def main():
    print("📱 Aplicación Móvil del Sistema Empresarial")
    print("=" * 50)
    print("1. Iniciar servidor móvil")
    print("2. Crear plantillas móviles")
    print("3. Generar código QR")
    print("4. Salir")
    
    choice = input("\nSeleccione una opción (1-4): ").strip()
    
    if choice == '1':
        port = input("Puerto (default 5001): ").strip()
        port = int(port) if port.isdigit() else 5001
        start_mobile_server(port)
    
    elif choice == '2':
        create_mobile_templates()
        print("✅ Plantillas móviles creadas exitosamente")
    
    elif choice == '3':
        base_url = input("URL base (default http://localhost:5001): ").strip()
        if not base_url:
            base_url = "http://localhost:5001"
        
        mobile_url = f"{base_url}/mobile"
        qr_code = mobile_app.create_qr_code(mobile_url)
        
        print(f"\n📱 Código QR generado para: {mobile_url}")
        print("💡 Usa este código QR para acceso rápido desde móvil")
    
    elif choice == '4':
        print("👋 ¡Hasta luego!")
    
    else:
        print("❌ Opción no válida")

if __name__ == "__main__":
    main()



