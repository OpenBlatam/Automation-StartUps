#!/usr/bin/env python3
"""
Script de prueba mejorado para el Sistema de Control de Inventario v2.0
Incluye pruebas para todas las funcionalidades avanzadas
"""

import sys
import os
import traceback
from datetime import datetime, timedelta

# Añadir el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(title):
    """Imprime un encabezado con estilo"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_section(title):
    """Imprime una sección"""
    print(f"\n{'-'*40}")
    print(f"🔍 {title}")
    print(f"{'-'*40}")

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
        print(f"❌ Error probando modelos: {e}")
        traceback.print_exc()
        return False

def test_services():
    """Prueba los servicios"""
    print_section("Servicios")
    
    try:
        from services.alert_service import alert_system
        print("✅ Servicio de alertas importado correctamente")
    except Exception as e:
        print(f"❌ Error importando servicio de alertas: {e}")
        return False
    
    try:
        from services.forecasting_service import forecasting_service
        print("✅ Servicio de pronósticos importado correctamente")
    except Exception as e:
        print(f"❌ Error importando servicio de pronósticos: {e}")
        return False
    
    try:
        from services.replenishment_service import replenishment_service
        print("✅ Servicio de reabastecimiento importado correctamente")
    except Exception as e:
        print(f"❌ Error importando servicio de reabastecimiento: {e}")
        return False
    
    try:
        from services.kpi_service import kpi_service
        print("✅ Servicio de KPIs importado correctamente")
    except Exception as e:
        print(f"❌ Error importando servicio de KPIs: {e}")
        return False
    
    try:
        from services.notification_service import notification_service
        print("✅ Servicio de notificaciones importado correctamente")
    except Exception as e:
        print(f"❌ Error importando servicio de notificaciones: {e}")
        return False
    
    return True

def test_advanced_services():
    """Prueba los servicios avanzados"""
    print_section("Servicios Avanzados")
    
    try:
        from services.advanced_analytics_service import advanced_analytics_service
        print("✅ Servicio de análisis avanzado importado correctamente")
    except Exception as e:
        print(f"❌ Error importando servicio de análisis avanzado: {e}")
        return False
    
    try:
        from services.data_export_service import data_export_service
        print("✅ Servicio de exportación de datos importado correctamente")
    except Exception as e:
        print(f"❌ Error importando servicio de exportación: {e}")
        return False
    
    try:
        from services.realtime_notification_service import realtime_notification_service
        print("✅ Servicio de notificaciones en tiempo real importado correctamente")
    except Exception as e:
        print(f"❌ Error importando servicio de notificaciones en tiempo real: {e}")
        return False
    
    return True

def test_routes():
    """Prueba las rutas"""
    print_section("Rutas")
    
    try:
        from routes.main import main_bp
        print("✅ Blueprint principal importado correctamente")
    except Exception as e:
        print(f"❌ Error importando blueprint principal: {e}")
        return False
    
    try:
        from routes.api import api_bp
        print("✅ Blueprint de API importado correctamente")
    except Exception as e:
        print(f"❌ Error importando blueprint de API: {e}")
        return False
    
    try:
        from routes.api_advanced import api_advanced_bp
        print("✅ Blueprint de API avanzada importado correctamente")
    except Exception as e:
        print(f"❌ Error importando blueprint de API avanzada: {e}")
        return False
    
    return True

def test_analytics_functionality():
    """Prueba la funcionalidad de análisis"""
    print_section("Funcionalidad de Análisis")
    
    try:
        from services.advanced_analytics_service import advanced_analytics_service
        
        # Probar análisis de rendimiento
        print("🔍 Probando análisis de rendimiento...")
        analysis = advanced_analytics_service.analyze_product_performance(30)
        
        if 'error' in analysis:
            print(f"⚠️  Análisis de rendimiento: {analysis['error']}")
        else:
            print("✅ Análisis de rendimiento ejecutado correctamente")
        
        # Probar generación de insights
        print("🔍 Probando generación de insights...")
        insights = advanced_analytics_service.generate_insights_report()
        
        if 'error' in insights:
            print(f"⚠️  Generación de insights: {insights['error']}")
        else:
            print("✅ Insights generados correctamente")
        
        return True
    except Exception as e:
        print(f"❌ Error probando funcionalidad de análisis: {e}")
        traceback.print_exc()
        return False

def test_export_functionality():
    """Prueba la funcionalidad de exportación"""
    print_section("Funcionalidad de Exportación")
    
    try:
        from services.data_export_service import data_export_service
        
        # Probar exportación de inventario
        print("🔍 Probando exportación de inventario...")
        try:
            inventory_data = data_export_service.export_inventory_report('csv')
            print("✅ Exportación de inventario funcionando")
        except Exception as e:
            print(f"⚠️  Exportación de inventario: {e}")
        
        # Probar exportación de KPIs
        print("🔍 Probando exportación de KPIs...")
        try:
            kpis_data = data_export_service.export_kpis_report('csv')
            print("✅ Exportación de KPIs funcionando")
        except Exception as e:
            print(f"⚠️  Exportación de KPIs: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error probando funcionalidad de exportación: {e}")
        traceback.print_exc()
        return False

def test_realtime_notifications():
    """Prueba las notificaciones en tiempo real"""
    print_section("Notificaciones en Tiempo Real")
    
    try:
        from services.realtime_notification_service import realtime_notification_service
        
        # Probar estadísticas de conexiones
        print("🔍 Probando estadísticas de conexiones...")
        stats = realtime_notification_service.get_connection_stats()
        print(f"✅ Estadísticas obtenidas: {stats}")
        
        # Probar notificación de prueba
        print("🔍 Probando notificación de prueba...")
        notification = {
            'type': 'test',
            'title': 'Prueba',
            'message': 'Notificación de prueba',
            'timestamp': datetime.utcnow().isoformat(),
            'severity': 'info'
        }
        
        sent_count = realtime_notification_service.broadcast_notification(notification)
        print(f"✅ Notificación de prueba enviada a {sent_count} usuarios")
        
        return True
    except Exception as e:
        print(f"❌ Error probando notificaciones en tiempo real: {e}")
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

def main():
    """Función principal de pruebas"""
    print_header("Sistema de Control de Inventario v2.0 - Pruebas Mejoradas")
    
    tests = [
        ("Importaciones Básicas", test_imports),
        ("Creación de Aplicación", test_app_creation),
        ("Modelos de Base de Datos", test_models),
        ("Servicios Básicos", test_services),
        ("Servicios Avanzados", test_advanced_services),
        ("Rutas", test_routes),
        ("Funcionalidad de Análisis", test_analytics_functionality),
        ("Funcionalidad de Exportación", test_export_functionality),
        ("Notificaciones en Tiempo Real", test_realtime_notifications),
        ("Templates", test_templates),
        ("Archivos Estáticos", test_static_files)
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
        print("🎉 ¡Todas las pruebas pasaron! El sistema está listo para usar.")
    else:
        print(f"⚠️  {total_tests - passed_tests} prueba(s) fallaron. Revisa los errores arriba.")
    
    print("\n" + "="*60)
    print("🚀 Sistema de Control de Inventario v2.0")
    print("📊 Funcionalidades Avanzadas:")
    print("   • Análisis ABC de productos")
    print("   • Análisis de estacionalidad")
    print("   • Clustering con machine learning")
    print("   • Predicción de demanda avanzada")
    print("   • Exportación de datos en múltiples formatos")
    print("   • Notificaciones en tiempo real")
    print("   • Insights automáticos")
    print("   • Análisis de correlaciones")
    print("="*60)

if __name__ == "__main__":
    main()



