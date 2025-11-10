"""
API REST para Gestión de Backups.

Proporciona endpoints HTTP para:
- Crear backups manualmente
- Listar backups
- Restaurar backups
- Verificar backups
- Obtener métricas
- Gestionar configuración
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from flask import Flask, jsonify, request
from functools import wraps
import os

from data.airflow.plugins.backup_manager import BackupManager, BackupConfig, BackupType
from data.airflow.plugins.backup_restore import BackupRestorer
from data.airflow.plugins.backup_verification import BackupVerifier
from data.airflow.plugins.backup_analytics import BackupAnalyticsEngine
from data.airflow.plugins.backup_health import BackupHealthChecker
from data.airflow.plugins.backup_encryption import BackupEncryption

logger = logging.getLogger(__name__)

# Intentar importar Flask
try:
    from flask import Flask, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    Flask = None
    jsonify = None
    request = None


def create_backup_api(
    backup_dir: str = "/tmp/backups",
    encryption_key: Optional[bytes] = None,
    api_key: Optional[str] = None
) -> Optional[Flask]:
    """
    Crea aplicación Flask para API de backups.
    
    Args:
        backup_dir: Directorio de backups
        encryption_key: Clave de encriptación
        api_key: API key para autenticación (opcional)
    
    Returns:
        Flask app o None si Flask no está disponible
    """
    if not FLASK_AVAILABLE:
        logger.warning("Flask not available, API disabled")
        return None
    
    app = Flask(__name__)
    
    # Inicializar componentes
    manager = BackupManager(backup_dir=backup_dir, encryption_key=encryption_key)
    restorer = BackupRestorer(backup_dir=backup_dir, encryption_key=encryption_key)
    verifier = BackupVerifier(backup_dir=backup_dir, encryption_key=encryption_key)
    analytics = BackupAnalyticsEngine(backup_dir=backup_dir)
    health_checker = BackupHealthChecker(backup_dir=backup_dir)
    
    def require_auth(f):
        """Decorador para autenticación."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if api_key:
                provided_key = request.headers.get('X-API-Key')
                if not provided_key or provided_key != api_key:
                    return jsonify({'error': 'Unauthorized'}), 401
            return f(*args, **kwargs)
        return decorated_function
    
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint."""
        return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})
    
    @app.route('/api/v1/backups', methods=['POST'])
    @require_auth
    def create_backup():
        """Crea un backup."""
        try:
            data = request.get_json()
            backup_type = data.get('type', 'database')  # 'database' or 'files'
            
            if backup_type == 'database':
                connection_string = data.get('connection_string')
                db_type = data.get('db_type', 'postgresql')
                
                if not connection_string:
                    return jsonify({'error': 'connection_string required'}), 400
                
                config = BackupConfig(
                    encrypt=data.get('encrypt', True),
                    compress=data.get('compress', True),
                    cloud_sync=data.get('cloud_sync', False)
                )
                
                result = manager.backup_database(
                    connection_string=connection_string,
                    db_type=db_type,
                    config=config
                )
                
            elif backup_type == 'files':
                source_paths = data.get('source_paths', [])
                
                if not source_paths:
                    return jsonify({'error': 'source_paths required'}), 400
                
                config = BackupConfig(
                    encrypt=data.get('encrypt', True),
                    compress=data.get('compress', True)
                )
                
                result = manager.backup_files(
                    source_paths=source_paths,
                    config=config
                )
            else:
                return jsonify({'error': 'Invalid backup type'}), 400
            
            return jsonify({
                'backup_id': result.backup_id,
                'status': result.status.value,
                'file_path': result.file_path,
                'cloud_path': result.cloud_path,
                'size_bytes': result.size_bytes,
                'duration_seconds': result.duration_seconds,
                'error': result.error
            }), 201
            
        except Exception as e:
            logger.error(f"Create backup error: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/backups', methods=['GET'])
    @require_auth
    def list_backups():
        """Lista backups disponibles."""
        try:
            backup_type = request.args.get('type')  # 'db', 'files', or None
            days = int(request.args.get('days', 30))
            
            backups = restorer.list_available_backups(
                backup_type=backup_type,
                days=days
            )
            
            return jsonify({
                'backups': backups,
                'count': len(backups)
            })
        except Exception as e:
            logger.error(f"List backups error: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/backups/<backup_id>/restore', methods=['POST'])
    @require_auth
    def restore_backup(backup_id: str):
        """Restaura un backup."""
        try:
            data = request.get_json()
            
            # Buscar backup
            backups = restorer.list_available_backups(days=365)
            backup = next((b for b in backups if backup_id in b['name']), None)
            
            if not backup:
                return jsonify({'error': 'Backup not found'}), 404
            
            backup_path = backup['path']
            
            if backup['type'] == 'db':
                connection_string = data.get('connection_string')
                db_type = data.get('db_type', 'postgresql')
                
                if not connection_string:
                    return jsonify({'error': 'connection_string required'}), 400
                
                result = restorer.restore_database(
                    backup_path=backup_path,
                    connection_string=connection_string,
                    db_type=db_type,
                    drop_existing=data.get('drop_existing', False)
                )
            else:
                target_dir = data.get('target_dir')
                if not target_dir:
                    return jsonify({'error': 'target_dir required'}), 400
                
                result = restorer.restore_files(
                    backup_path=backup_path,
                    target_dir=target_dir
                )
            
            return jsonify({
                'restore_id': result.restore_id,
                'status': result.status.value,
                'duration_seconds': result.duration_seconds,
                'error': result.error
            })
            
        except Exception as e:
            logger.error(f"Restore backup error: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/backups/<backup_id>/verify', methods=['POST'])
    @require_auth
    def verify_backup(backup_id: str):
        """Verifica un backup."""
        try:
            backups = restorer.list_available_backups(days=365)
            backup = next((b for b in backups if backup_id in b['name']), None)
            
            if not backup:
                return jsonify({'error': 'Backup not found'}), 404
            
            result = verifier.verify_backup(
                backup_path=backup['path'],
                verify_checksum=True,
                verify_encryption=True,
                verify_compression=True
            )
            
            return jsonify({
                'status': result.status.value,
                'checksum_valid': result.checksum_valid,
                'encryption_valid': result.encryption_valid,
                'compression_valid': result.compression_valid,
                'errors': result.errors,
                'warnings': result.warnings
            })
            
        except Exception as e:
            logger.error(f"Verify backup error: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/metrics', methods=['GET'])
    @require_auth
    def get_metrics():
        """Obtiene métricas de backups."""
        try:
            metrics = manager.get_metrics()
            return jsonify(metrics)
        except Exception as e:
            logger.error(f"Get metrics error: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/analytics/daily', methods=['GET'])
    @require_auth
    def get_daily_report():
        """Obtiene reporte diario."""
        try:
            date_str = request.args.get('date')
            date = datetime.fromisoformat(date_str) if date_str else None
            
            report = analytics.generate_daily_report(date=date)
            return jsonify(report)
        except Exception as e:
            logger.error(f"Get daily report error: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/health', methods=['GET'])
    @require_auth
    def get_health():
        """Obtiene health check completo."""
        try:
            health = health_checker.check_all()
            return jsonify(health)
        except Exception as e:
            logger.error(f"Get health error: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/predictions/space', methods=['GET'])
    @require_auth
    def predict_space():
        """Predice necesidades de espacio."""
        try:
            days = int(request.args.get('days', 30))
            prediction = analytics.predict_space_needs(days=days)
            return jsonify(prediction)
        except Exception as e:
            logger.error(f"Predict space error: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    return app

