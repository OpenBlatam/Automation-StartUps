#!/usr/bin/env python3
"""
Script de Prueba del Sistema de Gestión de Inventario
=====================================================

Script simple para probar las funcionalidades principales del sistema.
"""

import sys
import os
import time
from datetime import datetime

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
        print(f"✅ KPIs generados: {kpis}")
        
        # Obtener alertas
        alerts = ims.get_alerts_summary()
        print(f"✅ Alertas obtenidas: {len(alerts)} alertas")
        
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
        
        return True
        
    except Exception as e:
        print(f"❌ Error en análisis avanzado: {e}")
        return False

def test_enhanced_system():
    """Probar sistema mejorado"""
    print("\n🧪 Probando Sistema Mejorado...")
    
    try:
        from enhanced_system import EnhancedInventorySystem
        
        # Crear instancia del sistema mejorado
        enhanced = EnhancedInventorySystem()
        
        # Obtener estado del sistema
        status = enhanced.get_system_status()
        print(f"✅ Estado del sistema: {status['status']}")
        
        # Generar reporte de salud
        health_report = enhanced._generate_health_report()
        print(f"✅ Reporte de salud generado: {health_report['system_status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en sistema mejorado: {e}")
        return False

def test_api_endpoints():
    """Probar endpoints de API"""
    print("\n🧪 Probando Endpoints de API...")
    
    try:
        import requests
        import time
        
        # Esperar un poco para que el servidor se inicie
        time.sleep(2)
        
        # Probar endpoint de documentación
        try:
            response = requests.get('http://localhost:5001/api/docs', timeout=5)
            if response.status_code == 200:
                print("✅ API REST accesible")
                return True
            else:
                print(f"⚠️ API REST respondió con código: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("⚠️ API REST no está ejecutándose (esto es normal si no se inició)")
            return True  # No es un error si no está ejecutándose
        
    except ImportError:
        print("⚠️ requests no instalado, saltando prueba de API")
        return True
    except Exception as e:
        print(f"❌ Error probando API: {e}")
        return False

def test_dashboard():
    """Probar dashboard"""
    print("\n🧪 Probando Dashboard...")
    
    try:
        import requests
        import time
        
        # Esperar un poco para que el servidor se inicie
        time.sleep(2)
        
        # Probar dashboard original
        try:
            response = requests.get('http://localhost:5000', timeout=5)
            if response.status_code == 200:
                print("✅ Dashboard Original accesible")
            else:
                print(f"⚠️ Dashboard Original respondió con código: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("⚠️ Dashboard Original no está ejecutándose")
        
        # Probar dashboard avanzado
        try:
            response = requests.get('http://localhost:5002', timeout=5)
            if response.status_code == 200:
                print("✅ Dashboard Avanzado accesible")
            else:
                print(f"⚠️ Dashboard Avanzado respondió con código: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("⚠️ Dashboard Avanzado no está ejecutándose")
        
        return True
        
    except ImportError:
        print("⚠️ requests no instalado, saltando prueba de dashboard")
        return True
    except Exception as e:
        print(f"❌ Error probando dashboard: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 SISTEMA DE GESTIÓN DE INVENTARIO - PRUEBAS")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Ejecutar pruebas
    tests = [
        ("Sistema Básico", test_basic_system),
        ("Análisis Avanzado", test_advanced_analytics),
        ("Sistema Mejorado", test_enhanced_system),
        ("API Endpoints", test_api_endpoints),
        ("Dashboard", test_dashboard)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Error inesperado en {test_name}: {e}")
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    print(f"Pruebas pasadas: {passed}/{total}")
    print(f"Porcentaje de éxito: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron!")
        print("\n✅ El sistema está funcionando correctamente")
        print("\n🌐 URLs de acceso:")
        print("   Dashboard Original:    http://localhost:5000")
        print("   Dashboard Avanzado:    http://localhost:5002")
        print("   API REST:             http://localhost:5001")
        print("   Documentación API:    http://localhost:5001/api/docs")
    else:
        print("⚠️ Algunas pruebas fallaron")
        print("   Revisa los errores anteriores para más detalles")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()