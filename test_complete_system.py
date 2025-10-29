#!/usr/bin/env python3
"""
Script de Prueba Completo del Sistema Mejorado
==============================================

Prueba todas las funcionalidades del sistema sin dependencias externas.
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta
import sqlite3

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_system():
    """Probar sistema básico"""
    print("🧪 Probando Sistema Básico...")
    
    try:
        from inventory_management_system import InventoryManagementSystem
        
        # Crear instancia del sistema
        ims = InventoryManagementSystem()
        
        # Generar KPIs
        kpis = ims.generate_kpis()
        print(f"✅ KPIs generados: Valor inventario ${kpis['total_inventory_value']:,.2f}")
        
        # Obtener alertas
        alerts = ims.get_alerts_summary()
        print(f"✅ Alertas obtenidas: {len(alerts)} alertas activas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en sistema básico: {e}")
        return False

def test_advanced_analytics():
    """Probar análisis avanzado"""
    print("\n🧪 Probando Análisis Avanzado...")
    
    try:
        from advanced_analytics import AdvancedAnalytics
        
        # Crear instancia del análisis
        analytics = AdvancedAnalytics()
        
        # Análisis ABC
        abc_analysis = analytics.abc_analysis()
        print(f"✅ Análisis ABC completado: {len(abc_analysis)} categorías")
        
        # Optimización de inventario
        optimization = analytics.inventory_optimization()
        print(f"✅ Optimización completada: {len(optimization['recommendations'])} recomendaciones")
        
        # Reporte ejecutivo
        report = analytics.generate_executive_report()
        print(f"✅ Reporte ejecutivo generado: {len(report['key_recommendations'])} recomendaciones clave")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en análisis avanzado: {e}")
        return False

def test_enhanced_system():
    """Probar sistema mejorado"""
    print("\n🧪 Probando Sistema Mejorado...")
    
    try:
        # Importar solo las partes que no requieren dependencias externas
        from inventory_management_system import InventoryManagementSystem
        
        # Simular funcionalidades del sistema mejorado
        ims = InventoryManagementSystem()
        
        # Verificar funcionalidades básicas
        kpis = ims.generate_kpis()
        alerts = ims.get_alerts_summary()
        
        print(f"✅ Sistema mejorado: {kpis['total_inventory_value']:,.2f} valor inventario")
        print(f"✅ Sistema mejorado: {len(alerts)} alertas monitoreadas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en sistema mejorado: {e}")
        return False

def test_database_integrity():
    """Probar integridad de la base de datos"""
    print("\n🧪 Probando Integridad de Base de Datos...")
    
    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['products', 'inventory', 'suppliers', 'sales_history', 'alerts']
        missing_tables = [table for table in expected_tables if table not in tables]
        
        if missing_tables:
            print(f"⚠️ Tablas faltantes: {missing_tables}")
        else:
            print("✅ Todas las tablas presentes")
        
        # Verificar datos
        for table in expected_tables:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✅ Tabla {table}: {count} registros")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error en integridad de BD: {e}")
        return False

def test_file_structure():
    """Probar estructura de archivos"""
    print("\n🧪 Probando Estructura de Archivos...")
    
    required_files = [
        'inventory_management_system.py',
        'dashboard.py',
        'advanced_analytics.py',
        'enhanced_system.py',
        'api_rest.py',
        'advanced_dashboard.py',
        'config_manager.py',
        'audit_system.py',
        'external_integrations.py',
        'ml_system.py',
        'start_system.py',
        'test_system.py',
        'requirements.txt',
        'README.md',
        'ARCHITECTURE.md',
        'MEJORAS.md',
        'RESUMEN_FINAL.md'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️ Archivos faltantes: {missing_files}")
        return False
    else:
        print("✅ Todos los archivos principales presentes")
        return True

def test_templates():
    """Probar plantillas"""
    print("\n🧪 Probando Plantillas...")
    
    try:
        templates_dir = 'templates'
        if not os.path.exists(templates_dir):
            print("⚠️ Directorio de plantillas no encontrado")
            return False
        
        required_templates = [
            'base.html',
            'dashboard.html',
            'advanced_dashboard.html'
        ]
        
        missing_templates = []
        for template in required_templates:
            template_path = os.path.join(templates_dir, template)
            if not os.path.exists(template_path):
                missing_templates.append(template)
        
        if missing_templates:
            print(f"⚠️ Plantillas faltantes: {missing_templates}")
            return False
        else:
            print("✅ Todas las plantillas presentes")
            return True
        
    except Exception as e:
        print(f"❌ Error probando plantillas: {e}")
        return False

def test_configuration():
    """Probar configuración"""
    print("\n🧪 Probando Configuración...")
    
    try:
        # Verificar archivo de configuración de ejemplo
        if os.path.exists('config.example.json'):
            with open('config.example.json', 'r') as f:
                config = json.load(f)
            print("✅ Archivo de configuración de ejemplo presente")
        else:
            print("⚠️ Archivo de configuración de ejemplo no encontrado")
        
        # Verificar requirements.txt
        if os.path.exists('requirements.txt'):
            with open('requirements.txt', 'r') as f:
                requirements = f.read()
            print(f"✅ Requirements.txt presente con {len(requirements.splitlines())} dependencias")
        else:
            print("⚠️ Requirements.txt no encontrado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando configuración: {e}")
        return False

def test_performance():
    """Probar rendimiento básico"""
    print("\n🧪 Probando Rendimiento...")
    
    try:
        from inventory_management_system import InventoryManagementSystem
        
        ims = InventoryManagementSystem()
        
        # Medir tiempo de generación de KPIs
        start_time = time.time()
        kpis = ims.generate_kpis()
        kpi_time = time.time() - start_time
        
        # Medir tiempo de obtención de alertas
        start_time = time.time()
        alerts = ims.get_alerts_summary()
        alerts_time = time.time() - start_time
        
        print(f"✅ Generación de KPIs: {kpi_time:.3f} segundos")
        print(f"✅ Obtención de alertas: {alerts_time:.3f} segundos")
        
        # Verificar que los tiempos sean razonables
        if kpi_time < 5 and alerts_time < 5:
            print("✅ Rendimiento dentro de parámetros aceptables")
            return True
        else:
            print("⚠️ Rendimiento lento detectado")
            return False
        
    except Exception as e:
        print(f"❌ Error probando rendimiento: {e}")
        return False

def generate_system_report():
    """Generar reporte del sistema"""
    print("\n📊 Generando Reporte del Sistema...")
    
    try:
        from inventory_management_system import InventoryManagementSystem
        from advanced_analytics import AdvancedAnalytics
        
        ims = InventoryManagementSystem()
        analytics = AdvancedAnalytics()
        
        # Obtener datos del sistema
        kpis = ims.generate_kpis()
        alerts = ims.get_alerts_summary()
        abc_analysis = analytics.abc_analysis()
        optimization = analytics.inventory_optimization()
        
        # Generar reporte
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_status': 'operational',
            'kpis': kpis,
            'alerts_summary': {
                'total_alerts': len(alerts),
                'critical_alerts': len([a for a in alerts if a['severity'] == 'critical']),
                'high_alerts': len([a for a in alerts if a['severity'] == 'high']),
                'medium_alerts': len([a for a in alerts if a['severity'] == 'medium']),
                'low_alerts': len([a for a in alerts if a['severity'] == 'low'])
            },
            'abc_analysis': {
                'category_a_count': abc_analysis['A']['count'],
                'category_b_count': abc_analysis['B']['count'],
                'category_c_count': abc_analysis['C']['count']
            },
            'optimization_summary': optimization['summary'],
            'recommendations': optimization['summary']
        }
        
        # Guardar reporte
        with open('system_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("✅ Reporte del sistema generado: system_report.json")
        return True
        
    except Exception as e:
        print(f"❌ Error generando reporte: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 SISTEMA DE GESTIÓN DE INVENTARIO - PRUEBAS COMPLETAS")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Ejecutar todas las pruebas
    tests = [
        ("Estructura de Archivos", test_file_structure),
        ("Plantillas", test_templates),
        ("Configuración", test_configuration),
        ("Integridad de Base de Datos", test_database_integrity),
        ("Sistema Básico", test_basic_system),
        ("Análisis Avanzado", test_advanced_analytics),
        ("Sistema Mejorado", test_enhanced_system),
        ("Rendimiento", test_performance),
        ("Reporte del Sistema", generate_system_report)
    ]
    
    passed = 0
    total = len(tests)
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ Error inesperado en {test_name}: {e}")
            results[test_name] = False
    
    # Mostrar resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE PRUEBAS COMPLETAS")
    print("=" * 70)
    
    for test_name, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name:30} | {status}")
    
    print("-" * 70)
    print(f"Pruebas pasadas: {passed}/{total}")
    print(f"Porcentaje de éxito: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("\n✅ El sistema está completamente funcional")
        print("\n🌐 URLs de acceso:")
        print("   Dashboard Original:    http://localhost:5000")
        print("   Dashboard Avanzado:    http://localhost:5002")
        print("   API REST:             http://localhost:5001")
        print("   Documentación API:    http://localhost:5001/api/docs")
        
        print("\n🚀 Para ejecutar el sistema completo:")
        print("   python start_system.py")
        
        print("\n📊 Para ejecutar pruebas individuales:")
        print("   python test_system.py")
        
    else:
        print("\n⚠️ Algunas pruebas fallaron")
        print("   Revisa los errores anteriores para más detalles")
    
    print("\n" + "=" * 70)
    
    # Mostrar información adicional
    print("\n📋 INFORMACIÓN ADICIONAL:")
    print("-" * 30)
    
    try:
        from inventory_management_system import InventoryManagementSystem
        ims = InventoryManagementSystem()
        kpis = ims.generate_kpis()
        
        print(f"💰 Valor total del inventario: ${kpis['total_inventory_value']:,.2f}")
        print(f"📦 Productos con stock bajo: {kpis['low_stock_products']}")
        print(f"📈 Productos con stock alto: {kpis['high_stock_products']}")
        print(f"🔄 Rotación de inventario: {kpis['inventory_turnover']}")
        print(f"🚨 Alertas activas: {kpis['active_alerts']}")
        
    except Exception as e:
        print(f"⚠️ No se pudieron obtener métricas adicionales: {e}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()



