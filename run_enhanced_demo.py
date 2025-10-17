#!/usr/bin/env python3
"""
RUN ENHANCED DEMO
================

Script para ejecutar el Ultimate Enhanced Launch Planning System Demo
con todas las funcionalidades avanzadas de IA generativa, optimización
cuántica, sistema de recomendaciones y análisis de sentimientos.

Autor: Sistema de IA Avanzado
Versión: 2.1.0
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def check_python_installation():
    """Verificar si Python está instalado"""
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Python encontrado: {result.stdout.strip()}")
            return True
    except Exception as e:
        print(f"❌ Error verificando Python: {e}")
    
    return False

def check_dependencies():
    """Verificar dependencias básicas"""
    required_modules = ['numpy', 'pandas', 'matplotlib', 'seaborn']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} - Disponible")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module} - No disponible")
    
    return missing_modules

def install_dependencies():
    """Instalar dependencias básicas"""
    print("\n🔧 Instalando dependencias básicas...")
    
    try:
        # Instalar dependencias básicas
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "numpy", "pandas", "matplotlib", "seaborn", "plotly"
        ], check=True, timeout=300)
        
        print("✅ Dependencias básicas instaladas correctamente")
        return True
        
    except subprocess.TimeoutExpired:
        print("⏰ Timeout durante la instalación de dependencias")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def run_enhanced_demo():
    """Ejecutar el demo mejorado"""
    demo_file = Path("ultimate_enhanced_demo.py")
    
    if not demo_file.exists():
        print(f"❌ Archivo de demo no encontrado: {demo_file}")
        return False
    
    print(f"\n🚀 Ejecutando Ultimate Enhanced Demo...")
    print("=" * 60)
    
    try:
        # Ejecutar el demo
        result = subprocess.run([
            sys.executable, str(demo_file)
        ], timeout=600)  # 10 minutos timeout
        
        if result.returncode == 0:
            print("\n✅ Demo ejecutado exitosamente")
            return True
        else:
            print(f"\n❌ Demo terminó con código de error: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n⏰ Demo interrumpido por timeout (10 minutos)")
        return False
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrumpido por el usuario")
        return False
    except Exception as e:
        print(f"\n❌ Error ejecutando demo: {e}")
        return False

def main():
    """Función principal"""
    print("🚀" + "="*60)
    print("   ULTIMATE ENHANCED LAUNCH PLANNING SYSTEM")
    print("   Ejecutor de Demo Mejorado v2.1.0")
    print("="*62)
    print()
    
    # Verificar Python
    if not check_python_installation():
        print("❌ Python no está disponible. Por favor instala Python 3.8+")
        print("   Descarga desde: https://www.python.org/downloads/")
        return 1
    
    # Verificar dependencias
    print("\n🔍 Verificando dependencias...")
    missing = check_dependencies()
    
    if missing:
        print(f"\n⚠️ Dependencias faltantes: {', '.join(missing)}")
        
        response = input("\n¿Deseas instalar las dependencias faltantes? (s/n): ").lower().strip()
        if response in ['s', 'si', 'sí', 'y', 'yes']:
            if not install_dependencies():
                print("❌ No se pudieron instalar las dependencias")
                return 1
        else:
            print("❌ Demo no puede ejecutarse sin las dependencias necesarias")
            return 1
    
    # Ejecutar demo
    print("\n🎯 Todo listo para ejecutar el demo mejorado")
    input("Presiona Enter para continuar...")
    
    success = run_enhanced_demo()
    
    if success:
        print("\n🎉 ¡Demo completado exitosamente!")
        print("   Gracias por usar el Ultimate Enhanced Launch Planning System")
    else:
        print("\n❌ Demo no se completó correctamente")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️ Ejecución interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)







