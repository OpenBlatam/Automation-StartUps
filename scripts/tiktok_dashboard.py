#!/usr/bin/env python3
"""
Dashboard web para monitoreo y gestión de videos de TikTok
Interfaz web para ver estadísticas, cola de trabajos y resultados
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS

from tiktok_analytics import TikTokAnalytics
from tiktok_queue_manager import TikTokQueueManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

analytics = TikTokAnalytics()
queue_manager = TikTokQueueManager()

# HTML Template para el dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TikTok Auto Edit - Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .header h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-card h3 {
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        .stat-card .value {
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
        }
        .stat-card .change {
            font-size: 12px;
            color: #28a745;
            margin-top: 5px;
        }
        .section {
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }
        .status-badge {
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .status-completed { background: #d4edda; color: #155724; }
        .status-pending { background: #fff3cd; color: #856404; }
        .status-processing { background: #cce5ff; color: #004085; }
        .status-failed { background: #f8d7da; color: #721c24; }
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-primary:hover {
            background: #5568d3;
        }
        .refresh-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            transition: transform 0.3s;
        }
        .refresh-btn:hover {
            transform: rotate(180deg);
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 TikTok Auto Edit Dashboard</h1>
            <p>Monitoreo en tiempo real del sistema de procesamiento</p>
        </div>

        <div class="stats-grid" id="statsGrid">
            <div class="stat-card">
                <h3>Total Procesados</h3>
                <div class="value" id="totalProcessed">-</div>
            </div>
            <div class="stat-card">
                <h3>Tasa de Éxito</h3>
                <div class="value" id="successRate">-</div>
            </div>
            <div class="stat-card">
                <h3>Tiempo Promedio</h3>
                <div class="value" id="avgTime">-</div>
            </div>
            <div class="stat-card">
                <h3>Cache Hit Rate</h3>
                <div class="value" id="cacheRate">-</div>
            </div>
        </div>

        <div class="section">
            <h2>📊 Estadísticas de la Cola</h2>
            <div id="queueStats">
                <div class="loading">Cargando...</div>
            </div>
        </div>

        <div class="section">
            <h2>🔝 Top URLs Procesadas</h2>
            <div id="topUrls">
                <div class="loading">Cargando...</div>
            </div>
        </div>

        <div class="section">
            <h2>📈 Actividad Reciente</h2>
            <div id="recentActivity">
                <div class="loading">Cargando...</div>
            </div>
        </div>
    </div>

    <button class="refresh-btn" onclick="loadDashboard()">🔄</button>

    <script>
        async function loadDashboard() {
            try {
                // Cargar estadísticas
                const statsRes = await fetch('/api/dashboard/stats?days=7');
                const stats = await statsRes.json();
                
                document.getElementById('totalProcessed').textContent = stats.total_processed || 0;
                document.getElementById('successRate').textContent = 
                    (stats.success_rate || 0).toFixed(1) + '%';
                document.getElementById('avgTime').textContent = 
                    (stats.avg_processing_time || 0).toFixed(1) + 's';
                document.getElementById('cacheRate').textContent = 
                    (stats.cache_hit_rate || 0).toFixed(1) + '%';

                // Cargar estadísticas de cola
                const queueRes = await fetch('/api/dashboard/queue');
                const queueStats = await queueRes.json();
                
                document.getElementById('queueStats').innerHTML = `
                    <div class="stats-grid">
                        <div class="stat-card">
                            <h3>Pendientes</h3>
                            <div class="value">${queueStats.pending || 0}</div>
                        </div>
                        <div class="stat-card">
                            <h3>Procesando</h3>
                            <div class="value">${queueStats.processing || 0}</div>
                        </div>
                        <div class="stat-card">
                            <h3>Completados</h3>
                            <div class="value">${queueStats.completed || 0}</div>
                        </div>
                        <div class="stat-card">
                            <h3>Fallidos</h3>
                            <div class="value">${queueStats.failed || 0}</div>
                        </div>
                    </div>
                `;

                // Cargar top URLs
                const topRes = await fetch('/api/dashboard/top?limit=10');
                const topUrls = await topRes.json();
                
                if (topUrls.length > 0) {
                    let table = '<table><tr><th>URL</th><th>Procesada</th><th>Exitosas</th></tr>';
                    topUrls.forEach(item => {
                        table += `<tr>
                            <td>${item.url.substring(0, 50)}...</td>
                            <td>${item.count}</td>
                            <td>${item.successful}</td>
                        </tr>`;
                    });
                    table += '</table>';
                    document.getElementById('topUrls').innerHTML = table;
                } else {
                    document.getElementById('topUrls').innerHTML = '<p>No hay datos aún</p>';
                }

            } catch (error) {
                console.error('Error cargando dashboard:', error);
            }
        }

        // Cargar al inicio
        loadDashboard();

        // Auto-refresh cada 30 segundos
        setInterval(loadDashboard, 30000);
    </script>
</body>
</html>
"""


@app.route('/')
def dashboard():
    """Renderiza el dashboard principal"""
    return render_template_string(DASHBOARD_HTML)


@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    """Obtiene estadísticas para el dashboard"""
    try:
        days = int(request.args.get('days', 7))
        stats = analytics.get_stats(days)
        
        return jsonify({
            'total_processed': stats.get('total_processed', 0),
            'success_rate': stats.get('success_rate', 0),
            'avg_processing_time': stats.get('avg_processing_time', 0),
            'cache_hit_rate': stats.get('cache_hit_rate', 0),
            'successful': stats.get('successful', 0),
            'failed': stats.get('failed', 0)
        })
    except Exception as e:
        logger.error(f"Error obteniendo stats: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard/queue')
def get_queue_stats():
    """Obtiene estadísticas de la cola"""
    try:
        stats = queue_manager.get_queue_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error obteniendo queue stats: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard/top')
def get_top_urls():
    """Obtiene top URLs"""
    try:
        limit = int(request.args.get('limit', 10))
        top = analytics.get_top_urls(limit)
        return jsonify(top)
    except Exception as e:
        logger.error(f"Error obteniendo top URLs: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard/recent')
def get_recent_activity():
    """Obtiene actividad reciente"""
    try:
        # Obtener trabajos recientes de la cola
        conn = queue_manager.db_path
        import sqlite3
        db = sqlite3.connect(conn)
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT id, url, status, created_at, completed_at
            FROM jobs
            ORDER BY created_at DESC
            LIMIT 20
        """)
        
        jobs = [
            {
                'id': row[0],
                'url': row[1],
                'status': row[2],
                'created_at': row[3],
                'completed_at': row[4]
            }
            for row in cursor.fetchall()
        ]
        
        db.close()
        return jsonify(jobs)
    except Exception as e:
        logger.error(f"Error obteniendo actividad reciente: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Dashboard web para TikTok Auto Edit')
    parser.add_argument('-p', '--port', type=int, default=5002, help='Puerto (default: 5002)')
    parser.add_argument('-h', '--host', default='0.0.0.0', help='Host (default: 0.0.0.0)')
    parser.add_argument('--debug', action='store_true', help='Modo debug')
    
    args = parser.parse_args()
    
    logger.info(f"Iniciando dashboard en {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)


