"""
Dashboard Web Interactivo para Gestión de Backups.

Proporciona interfaz web para:
- Visualizar estado de backups
- Gestionar backups
- Ver métricas en tiempo real
- Ejecutar acciones
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Intentar importar Flask
try:
    from flask import Flask, render_template_string, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    Flask = None
    jsonify = None
    request = None


def create_backup_dashboard(
    backup_dir: str = "/tmp/backups",
    port: int = 8080
) -> Optional[Flask]:
    """
    Crea dashboard web para backups.
    
    Args:
        backup_dir: Directorio de backups
        port: Puerto del servidor
    
    Returns:
        Flask app o None si Flask no está disponible
    """
    if not FLASK_AVAILABLE:
        logger.warning("Flask not available, dashboard disabled")
        return None
    
    app = Flask(__name__)
    backup_path = Path(backup_dir)
    
    # HTML template para dashboard
    dashboard_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Backup System Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header h1 { margin-bottom: 0.5rem; }
        .container {
            max-width: 1400px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        .card {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .card h2 {
            font-size: 1.2rem;
            margin-bottom: 1rem;
            color: #667eea;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid #eee;
        }
        .metric:last-child { border-bottom: none; }
        .metric-value {
            font-weight: bold;
            color: #667eea;
        }
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 500;
        }
        .status-healthy { background: #d4edda; color: #155724; }
        .status-warning { background: #fff3cd; color: #856404; }
        .status-critical { background: #f8d7da; color: #721c24; }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1rem;
            margin-top: 1rem;
        }
        .btn:hover { background: #5568d3; }
        .table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        .table th, .table td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        .table th {
            background: #f8f9fa;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ Backup System Dashboard</h1>
        <p>Gestión y Monitoreo de Backups</p>
    </div>
    
    <div class="container">
        <div class="grid">
            <div class="card">
                <h2>📊 Estado General</h2>
                <div class="metric">
                    <span>Estado del Sistema</span>
                    <span class="status-badge status-healthy" id="system-status">Healthy</span>
                </div>
                <div class="metric">
                    <span>Tasa de Éxito</span>
                    <span class="metric-value" id="success-rate">-</span>
                </div>
                <div class="metric">
                    <span>Backups Totales</span>
                    <span class="metric-value" id="total-backups">-</span>
                </div>
                <div class="metric">
                    <span>Tamaño Total</span>
                    <span class="metric-value" id="total-size">-</span>
                </div>
            </div>
            
            <div class="card">
                <h2>💾 Uso de Disco</h2>
                <div class="metric">
                    <span>Espacio Usado</span>
                    <span class="metric-value" id="disk-used">-</span>
                </div>
                <div class="metric">
                    <span>Espacio Libre</span>
                    <span class="metric-value" id="disk-free">-</span>
                </div>
                <div class="metric">
                    <span>Uso (%)</span>
                    <span class="metric-value" id="disk-usage">-</span>
                </div>
            </div>
            
            <div class="card">
                <h2>🔒 Seguridad</h2>
                <div class="metric">
                    <span>Encriptación</span>
                    <span class="status-badge status-healthy" id="encryption-status">Active</span>
                </div>
                <div class="metric">
                    <span>Compliance</span>
                    <span class="status-badge status-healthy" id="compliance-status">Compliant</span>
                </div>
                <div class="metric">
                    <span>Backups Cloud</span>
                    <span class="status-badge status-healthy" id="cloud-status">Synced</span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>📋 Backups Recientes</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Tipo</th>
                        <th>Estado</th>
                        <th>Tamaño</th>
                        <th>Fecha</th>
                    </tr>
                </thead>
                <tbody id="backups-table">
                    <tr><td colspan="5">Cargando...</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        async function loadDashboard() {
            try {
                const response = await fetch('/api/dashboard/metrics');
                const data = await response.json();
                
                // Actualizar métricas
                document.getElementById('success-rate').textContent = (data.success_rate * 100).toFixed(1) + '%';
                document.getElementById('total-backups').textContent = data.total_backups;
                document.getElementById('total-size').textContent = (data.total_size_gb || 0).toFixed(2) + ' GB';
                
                // Actualizar disco
                document.getElementById('disk-used').textContent = (data.disk_used_gb || 0).toFixed(2) + ' GB';
                document.getElementById('disk-free').textContent = (data.disk_free_gb || 0).toFixed(2) + ' GB';
                document.getElementById('disk-usage').textContent = (data.disk_usage_percent || 0).toFixed(1) + '%';
                
                // Actualizar backups
                const table = document.getElementById('backups-table');
                table.innerHTML = data.recent_backups.map(backup => `
                    <tr>
                        <td>${backup.id}</td>
                        <td>${backup.type}</td>
                        <td><span class="status-badge status-${backup.status}">${backup.status}</span></td>
                        <td>${(backup.size_mb || 0).toFixed(2)} MB</td>
                        <td>${new Date(backup.date).toLocaleString()}</td>
                    </tr>
                `).join('');
            } catch (error) {
                console.error('Error loading dashboard:', error);
            }
        }
        
        // Cargar al inicio y cada 30 segundos
        loadDashboard();
        setInterval(loadDashboard, 30000);
    </script>
</body>
</html>
    """
    
    @app.route('/')
    def dashboard():
        """Renderiza dashboard principal."""
        return render_template_string(dashboard_html)
    
    @app.route('/api/dashboard/metrics')
    def get_dashboard_metrics():
        """Obtiene métricas para dashboard."""
        try:
            from data.airflow.plugins.backup_manager import BackupManager
            from data.airflow.plugins.backup_health import BackupHealthChecker
            import psutil
            
            manager = BackupManager(backup_dir=str(backup_path))
            metrics = manager.get_metrics()
            
            # Health check
            health_checker = BackupHealthChecker(backup_dir=str(backup_path))
            health = health_checker.check_all()
            
            # Disk usage
            disk_usage = psutil.disk_usage(str(backup_path))
            
            # Backups recientes
            recent_backups = []
            for backup_file in sorted(backup_path.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)[:10]:
                if backup_file.is_file():
                    recent_backups.append({
                        'id': backup_file.stem[:20],
                        'type': 'database' if 'db' in backup_file.name else 'files',
                        'status': 'completed',
                        'size_mb': backup_file.stat().st_size / (1024**2),
                        'date': datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat()
                    })
            
            return jsonify({
                'success_rate': metrics.get('success_rate', 0),
                'total_backups': metrics.get('total_backups', 0),
                'total_size_gb': metrics.get('total_size_bytes', 0) / (1024**3),
                'disk_used_gb': disk_usage.used / (1024**3),
                'disk_free_gb': disk_usage.free / (1024**3),
                'disk_usage_percent': (disk_usage.used / disk_usage.total) * 100,
                'health_status': health['overall_status'],
                'recent_backups': recent_backups
            })
        except Exception as e:
            logger.error(f"Dashboard metrics error: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    return app

