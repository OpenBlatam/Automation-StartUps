#!/usr/bin/env python3
"""
Interfaz web moderna para el sistema de organización empresarial
"""

import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
import webbrowser
import threading
import time

app = Flask(__name__)

class WebInterface:
    def __init__(self, base_path="/Users/adan/frontier"):
        self.base_path = base_path
        self.db_path = os.path.join(base_path, "search_index.db")
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
    
    def get_system_stats(self):
        """Obtener estadísticas del sistema"""
        stats = {
            'total_files': 0,
            'areas': {},
            'last_updated': datetime.now().isoformat()
        }
        
        for area_code, area_name in self.business_areas.items():
            area_path = os.path.join(self.base_path, area_path)
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
                    'code': area_code,
                    'files': file_count,
                    'size': total_size,
                    'size_mb': round(total_size / 1024 / 1024, 2)
                }
                stats['total_files'] += file_count
        
        return stats
    
    def search_documents(self, query, area=None, limit=20):
        """Buscar documentos"""
        if not os.path.exists(self.db_path):
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        where_conditions = []
        params = []
        
        if area:
            where_conditions.append("area = ?")
            params.append(area)
        
        where_conditions.append("(filename LIKE ? OR content LIKE ? OR keywords LIKE ?)")
        params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
        
        where_clause = " AND ".join(where_conditions)
        
        sql = f'''
            SELECT filename, area, path, file_size, last_modified,
                   CASE 
                       WHEN filename LIKE ? THEN 10
                       WHEN keywords LIKE ? THEN 5
                       WHEN content LIKE ? THEN 1
                       ELSE 0
                   END as score
            FROM documents
            WHERE {where_clause}
            ORDER BY score DESC, last_modified DESC
            LIMIT ?
        '''
        
        score_params = [f"%{query}%", f"%{query}%", f"%{query}%"]
        params = score_params + params + [limit]
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        
        search_results = []
        for row in results:
            filename, area, path, file_size, last_modified, score = row
            search_results.append({
                'filename': filename,
                'area': area,
                'path': path,
                'file_size': file_size,
                'last_modified': last_modified,
                'score': score,
                'relative_path': os.path.relpath(path, self.base_path)
            })
        
        conn.close()
        return search_results

# Crear instancia global
web_interface = WebInterface()

@app.route('/')
def index():
    """Página principal"""
    stats = web_interface.get_system_stats()
    return render_template('index.html', stats=stats, areas=web_interface.business_areas)

@app.route('/api/search')
def api_search():
    """API de búsqueda"""
    query = request.args.get('q', '')
    area = request.args.get('area', '')
    limit = int(request.args.get('limit', 20))
    
    if not query:
        return jsonify({'results': [], 'total': 0})
    
    results = web_interface.search_documents(query, area if area else None, limit)
    
    return jsonify({
        'results': results,
        'total': len(results),
        'query': query,
        'area': area
    })

@app.route('/api/stats')
def api_stats():
    """API de estadísticas"""
    stats = web_interface.get_system_stats()
    return jsonify(stats)

@app.route('/api/areas')
def api_areas():
    """API de áreas"""
    return jsonify(web_interface.business_areas)

@app.route('/browse/<area_code>')
def browse_area(area_code):
    """Navegar por área específica"""
    if area_code not in web_interface.business_areas:
        return "Área no encontrada", 404
    
    area_name = web_interface.business_areas[area_code]
    area_path = os.path.join(web_interface.base_path, area_code)
    
    files = []
    if os.path.exists(area_path):
        for root, dirs, filenames in os.walk(area_path):
            for filename in filenames:
                if filename.endswith('.md'):
                    file_path = os.path.join(root, filename)
                    try:
                        file_size = os.path.getsize(file_path)
                        stat = os.stat(file_path)
                        last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
                        
                        files.append({
                            'filename': filename,
                            'path': file_path,
                            'relative_path': os.path.relpath(file_path, web_interface.base_path),
                            'file_size': file_size,
                            'last_modified': last_modified
                        })
                    except:
                        pass
    
    return render_template('browse.html', 
                         area_name=area_name, 
                         area_code=area_code, 
                         files=files)

@app.route('/view/<path:file_path>')
def view_file(file_path):
    """Ver contenido de archivo"""
    full_path = os.path.join(web_interface.base_path, file_path)
    
    if not os.path.exists(full_path) or not full_path.endswith('.md'):
        return "Archivo no encontrado", 404
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filename = os.path.basename(full_path)
        return render_template('view.html', 
                             filename=filename, 
                             content=content, 
                             file_path=file_path)
    except Exception as e:
        return f"Error leyendo archivo: {e}", 500

def create_templates():
    """Crear plantillas HTML"""
    templates_dir = os.path.join(web_interface.base_path, "templates")
    os.makedirs(templates_dir, exist_ok=True)
    
    # Template base
    base_template = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Sistema de Organización Empresarial{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .search-container { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card-hover:hover { transform: translateY(-5px); transition: all 0.3s ease; }
        .area-card { min-height: 200px; }
        .stats-card { background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%); }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-building me-2"></i>Sistema Empresarial
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">Inicio</a>
                <a class="nav-link" href="/stats">Estadísticas</a>
            </div>
        </div>
    </nav>
    
    <main class="container-fluid">
        {% block content %}{% endblock %}
    </main>
    
    <footer class="bg-dark text-light text-center py-3 mt-5">
        <p>&copy; 2024 Sistema de Organización Empresarial</p>
    </footer>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''
    
    with open(os.path.join(templates_dir, 'base.html'), 'w') as f:
        f.write(base_template)
    
    # Template principal
    index_template = '''{% extends "base.html" %}

{% block title %}Inicio - Sistema Empresarial{% endblock %}

{% block content %}
<div class="search-container text-white py-5">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <h1 class="text-center mb-4">
                    <i class="fas fa-search me-3"></i>Búsqueda Inteligente
                </h1>
                <div class="input-group input-group-lg">
                    <input type="text" class="form-control" id="searchInput" placeholder="Buscar documentos...">
                    <select class="form-select" id="areaSelect" style="max-width: 200px;">
                        <option value="">Todas las áreas</option>
                        {% for code, name in areas.items() %}
                        <option value="{{ code }}">{{ name }}</option>
                        {% endfor %}
                    </select>
                    <button class="btn btn-light" type="button" onclick="performSearch()">
                        <i class="fas fa-search"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="container py-5">
    <div class="row">
        <div class="col-md-3">
            <div class="card stats-card text-white">
                <div class="card-body text-center">
                    <i class="fas fa-file-alt fa-3x mb-3"></i>
                    <h3>{{ stats.total_files }}</h3>
                    <p class="mb-0">Documentos</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-primary text-white">
                <div class="card-body text-center">
                    <i class="fas fa-building fa-3x mb-3"></i>
                    <h3>{{ stats.areas|length }}</h3>
                    <p class="mb-0">Áreas</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-success text-white">
                <div class="card-body text-center">
                    <i class="fas fa-chart-line fa-3x mb-3"></i>
                    <h3>100%</h3>
                    <p class="mb-0">Organizado</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-warning text-white">
                <div class="card-body text-center">
                    <i class="fas fa-robot fa-3x mb-3"></i>
                    <h3>AI</h3>
                    <p class="mb-0">Powered</p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row mt-5">
        <div class="col-12">
            <h2 class="mb-4">Áreas de Negocio</h2>
            <div class="row" id="areasGrid">
                {% for code, name in areas.items() %}
                <div class="col-md-4 col-lg-3 mb-4">
                    <div class="card area-card card-hover">
                        <div class="card-body">
                            <h5 class="card-title">{{ name }}</h5>
                            <p class="card-text">
                                <small class="text-muted">{{ stats.areas[name].files if name in stats.areas else 0 }} archivos</small>
                            </p>
                            <a href="/browse/{{ code }}" class="btn btn-outline-primary btn-sm">
                                <i class="fas fa-folder-open me-1"></i>Explorar
                            </a>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <div class="row mt-5" id="searchResults" style="display: none;">
        <div class="col-12">
            <h3>Resultados de Búsqueda</h3>
            <div id="resultsContainer"></div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
function performSearch() {
    const query = document.getElementById('searchInput').value;
    const area = document.getElementById('areaSelect').value;
    
    if (!query.trim()) return;
    
    axios.get('/api/search', {
        params: { q: query, area: area }
    })
    .then(response => {
        displayResults(response.data.results);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function displayResults(results) {
    const container = document.getElementById('resultsContainer');
    const resultsDiv = document.getElementById('searchResults');
    
    if (results.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No se encontraron resultados</div>';
    } else {
        let html = '<div class="list-group">';
        results.forEach(result => {
            html += `
                <div class="list-group-item">
                    <div class="d-flex w-100 justify-content-between">
                        <h5 class="mb-1">${result.filename}</h5>
                        <small>Score: ${result.score}</small>
                    </div>
                    <p class="mb-1">${result.area}</p>
                    <small>${result.relative_path}</small>
                    <div class="mt-2">
                        <a href="/view/${result.relative_path}" class="btn btn-sm btn-outline-primary">Ver</a>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        container.innerHTML = html;
    }
    
    resultsDiv.style.display = 'block';
}

document.getElementById('searchInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        performSearch();
    }
});
</script>
{% endblock %}'''
    
    with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
        f.write(index_template)
    
    # Template de navegación por área
    browse_template = '''{% extends "base.html" %}

{% block title %}{{ area_name }} - Sistema Empresarial{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="row">
        <div class="col-12">
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="/">Inicio</a></li>
                    <li class="breadcrumb-item active">{{ area_name }}</li>
                </ol>
            </nav>
            
            <h1 class="mb-4">
                <i class="fas fa-folder-open me-2"></i>{{ area_name }}
            </h1>
            
            <div class="row">
                {% for file in files %}
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="card card-hover">
                        <div class="card-body">
                            <h6 class="card-title">{{ file.filename }}</h6>
                            <p class="card-text">
                                <small class="text-muted">
                                    {{ file.file_size // 1024 }} KB<br>
                                    {{ file.last_modified[:10] }}
                                </small>
                            </p>
                            <a href="/view/{{ file.relative_path }}" class="btn btn-primary btn-sm">
                                <i class="fas fa-eye me-1"></i>Ver
                            </a>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    with open(os.path.join(templates_dir, 'browse.html'), 'w') as f:
        f.write(browse_template)
    
    # Template de visualización de archivos
    view_template = '''{% extends "base.html" %}

{% block title %}{{ filename }} - Sistema Empresarial{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="row">
        <div class="col-12">
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="/">Inicio</a></li>
                    <li class="breadcrumb-item active">{{ filename }}</li>
                </ol>
            </nav>
            
            <div class="card">
                <div class="card-header">
                    <h4 class="mb-0">
                        <i class="fas fa-file-alt me-2"></i>{{ filename }}
                    </h4>
                </div>
                <div class="card-body">
                    <pre style="white-space: pre-wrap; font-family: 'Courier New', monospace;">{{ content }}</pre>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    with open(os.path.join(templates_dir, 'view.html'), 'w') as f:
        f.write(view_template)

def start_web_server(port=5000):
    """Iniciar servidor web"""
    print(f"🌐 Iniciando servidor web en puerto {port}...")
    print(f"📱 Accede a: http://localhost:{port}")
    
    # Crear plantillas si no existen
    create_templates()
    
    # Abrir navegador automáticamente
    def open_browser():
        time.sleep(2)
        webbrowser.open(f'http://localhost:{port}')
    
    threading.Thread(target=open_browser).start()
    
    # Iniciar servidor Flask
    app.run(host='0.0.0.0', port=port, debug=False)

def main():
    print("🌐 Sistema de Interfaz Web")
    print("=" * 40)
    print("1. Iniciar servidor web")
    print("2. Crear plantillas HTML")
    print("3. Salir")
    
    choice = input("\nSeleccione una opción (1-3): ").strip()
    
    if choice == '1':
        port = input("Puerto (default 5000): ").strip()
        port = int(port) if port.isdigit() else 5000
        start_web_server(port)
    
    elif choice == '2':
        create_templates()
        print("✅ Plantillas HTML creadas exitosamente")
    
    elif choice == '3':
        print("👋 ¡Hasta luego!")
    
    else:
        print("❌ Opción no válida")

if __name__ == "__main__":
    main()



