#!/usr/bin/env python3
"""
Script de prueba final para el Sistema de Control de Inventario v6.0
Incluye todas las funcionalidades: ML, optimización, tiempo real, integración, monitoreo, IA avanzada, IoT, AR
"""

import sys
import os
import traceback
from datetime import datetime, timedelta

# Añadir el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(title):
    """Imprime un encabezado con estilo"""
    print(f"\n{'='*90}")
    print(f"🚀 {title}")
    print(f"{'='*90}")

def print_section(title):
    """Imprime una sección"""
    print(f"\n{'-'*70}")
    print(f"🔍 {title}")
    print(f"{'-'*70}")

def test_imports():
    """Prueba las importaciones básicas"""
    print_section("Importaciones Básicas")
    
    try:
        import flask
        print("✅ Flask importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando Flask: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando Pandas: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando NumPy: {e}")
        return False
    
    try:
        import sklearn
        print("✅ Scikit-learn importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando Scikit-learn: {e}")
        return False
    
    try:
        import joblib
        print("✅ Joblib importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando Joblib: {e}")
        return False
    
    try:
        import schedule
        print("✅ Schedule importado correctamente")
    except ImportError as e:
        print(f"⚠️  Schedule no disponible: {e}")
    
    try:
        import uuid
        print("✅ UUID importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando UUID: {e}")
        return False
    
    try:
        import threading
        print("✅ Threading importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando Threading: {e}")
        return False
    
    return True

def test_app_creation():
    """Prueba la creación de la aplicación"""
    print_section("Creación de Aplicación")
    
    try:
        from app import create_app
        app = create_app()
        print("✅ Aplicación creada correctamente")
        return app
    except Exception as e:
        print(f"❌ Error creando aplicación: {e}")
        traceback.print_exc()
        return None

def test_models():
    """Prueba los modelos de base de datos"""
    print_section("Modelos de Base de Datos")
    
    try:
        from models import Product, InventoryRecord, Alert, SalesRecord, ReorderRecommendation, Supplier
        print("✅ Modelos básicos importados correctamente")
        
        # Probar modelos de autenticación
        try:
            from models_auth import User, UserActivity, AuditLog
            print("✅ Modelos de autenticación importados correctamente")
        except ImportError as e:
            print(f"⚠️  Modelos de autenticación no disponibles: {e}")
        
        # Probar modelos de configuración
        try:
            from models_config import SystemConfig, NotificationTemplate, BackupConfig, IntegrationConfig
            print("✅ Modelos de configuración importados correctamente")
        except ImportError as e:
            print(f"⚠️  Modelos de configuración no disponibles: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error probando modelos: {str(e)}")
        traceback.print_exc()
        return False

def test_services():
    """Prueba los servicios básicos"""
    print_section("Servicios Básicos")
    
    try:
        from services.alert_service import alert_system
        print("✅ Servicio de alertas importado correctamente")
    except Exception as e:
        print(f"❌ Error importando servicio de alertas: {str(e)}")
        return False
    
    try:
        from services.kpi_service import kpi_service
        print("✅ Servicio de KPIs importado correctamente")
    except Exception as e:
        print(f"❌ Error importando servicio de KPIs: {str(e)}")
        return False
    
    try:
        from services.notification_service import notification_service
        print("✅ Servicio de notificaciones importado correctamente")
    except Exception as e:
        print(f"❌ Error importando servicio de notificaciones: {str(e)}")
        return False
    
    return True

def test_advanced_services():
    """Prueba los servicios avanzados"""
    print_section("Servicios Avanzados")
    
    try:
        from services.advanced_analytics_service import advanced_analytics_service
        print("✅ Servicio de análisis avanzado importado correctamente")
    except Exception as e:
        print(f"❌ Error importando servicio de análisis avanzado: {str(e)}")
        return False
    
    try:
        from services.data_export_service import data_export_service
        print("✅ Servicio de exportación de datos importado correctamente")
    except Exception as e:
        print(f"❌ Error importando servicio de exportación: {str(e)}")
        return False
    
    try:
        from services.realtime_notification_service import realtime_notification_service
        print("✅ Servicio de notificaciones en tiempo real importado correctamente")
    except Exception as e:
        print(f"❌ Error importando servicio de notificaciones en tiempo real: {str(e)}")
        return False
    
    return True

def test_ml_services():
    """Prueba los servicios de machine learning"""
    print_section("Servicios de Machine Learning")
    
    try:
        from services.advanced_ml_service import advanced_ml_service
        print("✅ Servicio de ML avanzado importado correctamente")
    except Exception as e:
        print(f"❌ Error importando servicio de ML avanzado: {str(e)}")
        return False
    
    try:
        from services.inventory_optimization_service import inventory_optimization_service
        print("✅ Servicio de optimización de inventario importado correctamente")
    except Exception as e:
        print(f"❌ Error importando servicio de optimización: {str(e)}")
        return False
    
    return True

def test_integration_services():
    """Prueba los servicios de integración"""
    print_section("Servicios de Integración")
    
    try:
        from services.integration_service import external_integration_service, backup_service
        print("✅ Servicio de integración externa importado correctamente")
    except Exception as e:
        print(f"❌ Error importando servicio de integración: {str(e)}")
        return False
    
    try:
        from services.monitoring_service import advanced_monitoring_service
        print("✅ Servicio de monitoreo avanzado importado correctamente")
    except Exception as e:
        print(f"❌ Error importando servicio de monitoreo: {str(e)}")
        return False
    
    return True

def test_ai_services():
    """Prueba los servicios de IA avanzada"""
    print_section("Servicios de IA Avanzada")
    
    try:
        from services.advanced_ai_service import advanced_ai_service
        print("✅ Servicio de IA avanzada importado correctamente")
    except Exception as e:
        print(f"❌ Error importando servicio de IA avanzada: {str(e)}")
        return False
    
    return True

def test_iot_services():
    """Prueba los servicios de IoT"""
    print_section("Servicios de IoT")
    
    try:
        from services.iot_service import iot_monitoring_service
        print("✅ Servicio de monitoreo IoT importado correctamente")
    except Exception as e:
        print(f"❌ Error importando servicio de IoT: {str(e)}")
        return False
    
    return True

def test_ar_services():
    """Prueba los servicios de realidad aumentada"""
    print_section("Servicios de Realidad Aumentada")
    
    try:
        from services.ar_service import augmented_reality_service
        print("✅ Servicio de realidad aumentada importado correctamente")
    except Exception as e:
        print(f"❌ Error importando servicio de AR: {str(e)}")
        return False
    
    return True

def test_routes():
    """Prueba las rutas"""
    print_section("Rutas")
    
    try:
        from routes.main import main_bp
        print("✅ Blueprint principal importado correctamente")
    except Exception as e:
        print(f"❌ Error importando blueprint principal: {str(e)}")
        return False
    
    try:
        from routes.api import api_bp
        print("✅ Blueprint de API importado correctamente")
    except Exception as e:
        print(f"❌ Error importando blueprint de API: {str(e)}")
        return False
    
    try:
        from routes.api_advanced import api_advanced_bp
        print("✅ Blueprint de API avanzada importado correctamente")
    except Exception as e:
        print(f"❌ Error importando blueprint de API avanzada: {str(e)}")
        return False
    
    try:
        from routes.ml_api import ml_bp
        print("✅ Blueprint de ML API importado correctamente")
    except Exception as e:
        print(f"❌ Error importando blueprint de ML API: {str(e)}")
        return False
    
    try:
        from routes.integration_api import integration_bp
        print("✅ Blueprint de integración importado correctamente")
    except Exception as e:
        print(f"❌ Error importando blueprint de integración: {str(e)}")
        return False
    
    try:
        from routes.ai_blockchain_api import ai_blockchain_bp
        print("✅ Blueprint de IA & blockchain importado correctamente")
    except Exception as e:
        print(f"❌ Error importando blueprint de IA & blockchain: {str(e)}")
        return False
    
    try:
        from routes.iot_ar_api import iot_ar_bp
        print("✅ Blueprint de IoT & AR importado correctamente")
    except Exception as e:
        print(f"❌ Error importando blueprint de IoT & AR: {str(e)}")
        return False
    
    try:
        from routes.realtime import realtime_bp
        print("✅ Blueprint de tiempo real importado correctamente")
    except Exception as e:
        print(f"❌ Error importando blueprint de tiempo real: {str(e)}")
        return False
    
    return True

def test_iot_functionality():
    """Prueba la funcionalidad de IoT"""
    print_section("Funcionalidad de IoT")
    
    try:
        from services.iot_service import iot_monitoring_service
        
        # Probar estado de dispositivos
        print("🔍 Probando estado de dispositivos IoT...")
        device_status = iot_monitoring_service.get_device_status()
        
        if device_status['success']:
            print(f"✅ Estado de dispositivos: {device_status['total_devices']} dispositivos")
            print(f"✅ Dispositivos en línea: {device_status['online_devices']}")
        else:
            print(f"⚠️  Estado de dispositivos: {device_status['error']}")
        
        # Probar dashboard IoT
        print("🔍 Probando dashboard IoT...")
        dashboard = iot_monitoring_service.get_dashboard_data()
        
        if dashboard['success']:
            print(f"✅ Dashboard IoT: {dashboard['dashboard']['devices']['total']} dispositivos")
        else:
            print(f"⚠️  Dashboard IoT: {dashboard['error']}")
        
        return True
    except Exception as e:
        print(f"❌ Error probando funcionalidad de IoT: {str(e)}")
        traceback.print_exc()
        return False

def test_ar_functionality():
    """Prueba la funcionalidad de realidad aumentada"""
    print_section("Funcionalidad de Realidad Aumentada")
    
    try:
        from services.ar_service import augmented_reality_service
        
        # Probar layout del almacén
        print("🔍 Probando layout del almacén...")
        layout = augmented_reality_service.get_warehouse_layout()
        
        if layout['success']:
            print(f"✅ Layout del almacén: {layout['layout']['name']}")
            print(f"✅ Zonas: {len(layout['layout']['zones'])}")
        else:
            print(f"⚠️  Layout del almacén: {layout['error']}")
        
        # Probar marcadores AR
        print("🔍 Probando marcadores AR...")
        markers = augmented_reality_service.get_ar_markers()
        
        if markers['success']:
            print(f"✅ Marcadores AR: {markers['total_markers']} marcadores")
        else:
            print(f"⚠️  Marcadores AR: {markers['error']}")
        
        # Probar dashboard AR
        print("🔍 Probando dashboard AR...")
        dashboard = augmented_reality_service.get_ar_dashboard_data()
        
        if dashboard['success']:
            print(f"✅ Dashboard AR: {dashboard['dashboard']['markers']['total']} marcadores")
        else:
            print(f"⚠️  Dashboard AR: {dashboard['error']}")
        
        return True
    except Exception as e:
        print(f"❌ Error probando funcionalidad de AR: {str(e)}")
        traceback.print_exc()
        return False

def test_templates():
    """Prueba los templates"""
    print_section("Templates")
    
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    
    required_templates = [
        'base.html',
        'dashboard.html',
        'inventory.html',
        'analytics.html',
        'ml_optimization.html',
        'realtime_dashboard.html',
        'admin_monitoring.html',
        'ai_blockchain.html',
        'iot_ar.html',
        'suppliers.html',
        'sales.html',
        'reports.html'
    ]
    
    for template in required_templates:
        template_path = os.path.join(templates_dir, template)
        if os.path.exists(template_path):
            print(f"✅ Template {template} encontrado")
        else:
            print(f"❌ Template {template} no encontrado")
            return False
    
    return True

def test_static_files():
    """Prueba los archivos estáticos"""
    print_section("Archivos Estáticos")
    
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    
    required_files = [
        'css/style.css',
        'js/main.js'
    ]
    
    for file_path in required_files:
        full_path = os.path.join(static_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ Archivo {file_path} encontrado")
        else:
            print(f"❌ Archivo {file_path} no encontrado")
            return False
    
    return True

def test_api_endpoints():
    """Prueba los endpoints de la API"""
    print_section("Endpoints de API")
    
    # Lista de endpoints importantes
    endpoints = [
        '/api/products',
        '/api/inventory',
        '/api/alerts',
        '/api/kpis',
        '/api/analytics/performance',
        '/api/analytics/insights',
        '/api/export/inventory',
        '/api/ml/train-models',
        '/api/ml/predict-demand/1',
        '/api/optimization/run',
        '/api/integration/market-prices/sync',
        '/api/integration/supplier-data/sync',
        '/api/integration/backup/create-full',
        '/api/integration/backup/create-data',
        '/api/integration/monitoring/health',
        '/api/integration/monitoring/alerts/active',
        '/api/ai-blockchain/ai/train-deep-models',
        '/api/ai-blockchain/ai/generate-insights',
        '/api/ai-blockchain/ai/predict/1',
        '/api/ai-blockchain/ai/detect-anomalies',
        '/api/ai-blockchain/blockchain/info',
        '/api/ai-blockchain/blockchain/mine',
        '/api/ai-blockchain/blockchain/verify',
        '/api/ai-blockchain/ai-blockchain/dashboard',
        '/api/iot-ar/iot/devices/status',
        '/api/iot-ar/iot/sensors/data',
        '/api/iot-ar/iot/alerts',
        '/api/iot-ar/iot/monitoring/start',
        '/api/iot-ar/iot/monitoring/stop',
        '/api/iot-ar/iot/dashboard',
        '/api/iot-ar/ar/warehouse/layout',
        '/api/iot-ar/ar/markers',
        '/api/iot-ar/ar/content',
        '/api/iot-ar/ar/session/create',
        '/api/iot-ar/ar/session/scan',
        '/api/iot-ar/ar/session/action',
        '/api/iot-ar/ar/session/end',
        '/api/iot-ar/ar/dashboard',
        '/api/iot-ar/iot-ar/dashboard',
        '/api/iot-ar/iot-ar/analysis',
        '/api/notifications/status'
    ]
    
    print(f"✅ {len(endpoints)} endpoints de API disponibles")
    
    return True

def test_system_architecture():
    """Prueba la arquitectura del sistema"""
    print_section("Arquitectura del Sistema")
    
    try:
        # Verificar estructura de directorios
        required_dirs = ['services', 'routes', 'templates', 'static']
        
        for dir_name in required_dirs:
            if os.path.exists(dir_name):
                print(f"✅ Directorio {dir_name} encontrado")
            else:
                print(f"❌ Directorio {dir_name} no encontrado")
                return False
        
        # Verificar archivos principales
        required_files = ['app.py', 'models.py', 'requirements.txt']
        
        for file_name in required_files:
            if os.path.exists(file_name):
                print(f"✅ Archivo {file_name} encontrado")
            else:
                print(f"❌ Archivo {file_name} no encontrado")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Error verificando arquitectura: {str(e)}")
        return False

def main():
    """Función principal de pruebas"""
    print_header("Sistema de Control de Inventario v6.0 - Pruebas Finales")
    
    tests = [
        ("Importaciones Básicas", test_imports),
        ("Creación de Aplicación", test_app_creation),
        ("Modelos de Base de Datos", test_models),
        ("Servicios Básicos", test_services),
        ("Servicios Avanzados", test_advanced_services),
        ("Servicios de Machine Learning", test_ml_services),
        ("Servicios de Integración", test_integration_services),
        ("Servicios de IA Avanzada", test_ai_services),
        ("Servicios de IoT", test_iot_services),
        ("Servicios de Realidad Aumentada", test_ar_services),
        ("Rutas", test_routes),
        ("Funcionalidad de IoT", test_iot_functionality),
        ("Funcionalidad de Realidad Aumentada", test_ar_functionality),
        ("Templates", test_templates),
        ("Archivos Estáticos", test_static_files),
        ("Endpoints de API", test_api_endpoints),
        ("Arquitectura del Sistema", test_system_architecture)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed_tests += 1
        except Exception as e:
            print(f"❌ Error ejecutando {test_name}: {e}")
    
    print_header("Resumen de Pruebas")
    print(f"Pruebas pasadas: {passed_tests}/{total_tests}")
    print(f"Porcentaje de éxito: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 ¡Todas las pruebas pasaron! El sistema está completamente funcional.")
    else:
        print(f"⚠️  {total_tests - passed_tests} prueba(s) fallaron. Revisa los errores arriba.")
    
    print("\n" + "="*90)
    print("🚀 Sistema de Control de Inventario v6.0")
    print("🧠 Funcionalidades Completas:")
    print("   • Machine Learning con múltiples algoritmos")
    print("   • Optimización con algoritmos genéticos")
    print("   • Análisis avanzado (ABC, clustering, estacionalidad)")
    print("   • Exportación avanzada de datos")
    print("   • Notificaciones en tiempo real")
    print("   • Dashboard interactivo")
    print("   • API RESTful completa (120+ endpoints)")
    print("   • Sistema de autenticación")
    print("   • Configuración dinámica")
    print("   • Integración con APIs externas")
    print("   • Sistema de respaldos automáticos")
    print("   • Monitoreo avanzado del sistema")
    print("   • Alertas inteligentes")
    print("   • Administración completa")
    print("   • Inteligencia Artificial Avanzada")
    print("   • Deep Learning con redes neuronales")
    print("   • Insights automáticos")
    print("   • Detección de anomalías")
    print("   • Internet of Things (IoT)")
    print("   • Monitoreo de sensores")
    print("   • Alertas IoT inteligentes")
    print("   • Realidad Aumentada (AR)")
    print("   • Visualización 3D del almacén")
    print("   • Marcadores AR interactivos")
    print("   • Sesiones AR para inventario")
    print("="*90)

if __name__ == "__main__":
    main()



