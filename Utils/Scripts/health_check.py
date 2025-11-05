"""
Health check utilities para verificar el estado del sistema
"""
import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple

def check_database_connection(app) -> Tuple[bool, str]:
    """Verifica la conexión a la base de datos"""
    try:
        from app import db
        with app.app_context():
            # Intentar una consulta simple
            db.session.execute('SELECT 1')
            return True, "Conexión a base de datos OK"
    except Exception as e:
        return False, f"Error de conexión: {str(e)}"

def check_models_loaded() -> Tuple[bool, str]:
    """Verifica que los modelos estén cargados correctamente"""
    try:
        from models import Product, InventoryRecord, Alert
        return True, "Modelos cargados correctamente"
    except ImportError as e:
        return False, f"Error cargando modelos: {str(e)}"

def check_services_available() -> Tuple[bool, str, List[str]]:
    """Verifica que los servicios estén disponibles"""
    available = []
    missing = []
    
    try:
        from services.alert_service import alert_system
        available.append("alert_service")
    except ImportError:
        missing.append("alert_service")
    
    try:
        from services.forecasting_service import demand_forecasting_service
        available.append("forecasting_service")
    except ImportError:
        missing.append("forecasting_service")
    
    try:
        from services.replenishment_service import replenishment_service
        available.append("replenishment_service")
    except ImportError:
        missing.append("replenishment_service")
    
    try:
        from services.kpi_service import kpi_service
        available.append("kpi_service")
    except ImportError:
        missing.append("kpi_service")
    
    if missing:
        return False, f"Servicios faltantes: {', '.join(missing)}", available
    return True, "Todos los servicios disponibles", available

def check_file_permissions() -> Tuple[bool, str]:
    """Verifica permisos de archivos críticos"""
    required_files = [
        'app.py',
        'models.py',
        'requirements.txt',
        '05_Technology/models.py'
    ]
    
    missing = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing.append(file_path)
    
    if missing:
        return False, f"Archivos faltantes: {', '.join(missing)}"
    return True, "Todos los archivos críticos presentes"

def full_health_check(app) -> Dict:
    """Realiza un health check completo del sistema"""
    results = {
        'timestamp': datetime.now().isoformat(),
        'status': 'healthy',
        'checks': {}
    }
    
    # Check database
    db_ok, db_msg = check_database_connection(app)
    results['checks']['database'] = {
        'status': 'ok' if db_ok else 'error',
        'message': db_msg
    }
    
    # Check models
    models_ok, models_msg = check_models_loaded()
    results['checks']['models'] = {
        'status': 'ok' if models_ok else 'error',
        'message': models_msg
    }
    
    # Check services
    services_ok, services_msg, services_list = check_services_available()
    results['checks']['services'] = {
        'status': 'ok' if services_ok else 'warning',
        'message': services_msg,
        'available': services_list
    }
    
    # Check files
    files_ok, files_msg = check_file_permissions()
    results['checks']['files'] = {
        'status': 'ok' if files_ok else 'error',
        'message': files_msg
    }
    
    # Determinar estado general
    has_errors = any(
        check['status'] == 'error' 
        for check in results['checks'].values()
    )
    
    if has_errors:
        results['status'] = 'unhealthy'
    elif any(check['status'] == 'warning' for check in results['checks'].values()):
        results['status'] = 'degraded'
    
    return results

def print_health_report(results: Dict):
    """Imprime un reporte de health check formateado"""
    print("\n" + "="*60)
    print("REPORTE DE HEALTH CHECK DEL SISTEMA")
    print("="*60)
    print(f"Fecha: {results['timestamp']}")
    print(f"Estado General: {results['status'].upper()}")
    print("\n" + "-"*60)
    
    for check_name, check_data in results['checks'].items():
        status_icon = "✓" if check_data['status'] == 'ok' else "⚠" if check_data['status'] == 'warning' else "✗"
        print(f"{status_icon} {check_name.upper()}: {check_data['status']}")
        print(f"   {check_data['message']}")
        if 'available' in check_data:
            print(f"   Servicios disponibles: {len(check_data['available'])}")
        print()
    
    print("="*60 + "\n")

if __name__ == '__main__':
    from app import create_app
    
    app = create_app()
    with app.app_context():
        results = full_health_check(app)
        print_health_report(results)
        
        # Exit code basado en estado
        sys.exit(0 if results['status'] == 'healthy' else 1)

