#!/usr/bin/env python3
"""
🚀 MARKETING BRAIN LAUNCHER
Launcher para el Advanced Marketing Brain System
Permite ejecutar diferentes componentes del sistema
"""

import sys
import subprocess
import os
from pathlib import Path
import argparse

def check_dependencies():
    """Verificar que las dependencias estén instaladas"""
    required_packages = [
        'pandas', 'numpy', 'plotly', 'streamlit', 'flask', 'flask_cors'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Dependencias faltantes:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Instalar dependencias:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ Todas las dependencias están instaladas")
    return True

def launch_core_system():
    """Ejecutar el sistema core"""
    print("🧠 Iniciando Advanced Marketing Brain System...")
    try:
        subprocess.run([sys.executable, "advanced_marketing_brain_system.py"])
    except FileNotFoundError:
        print("❌ Archivo advanced_marketing_brain_system.py no encontrado")
    except Exception as e:
        print(f"❌ Error ejecutando sistema core: {e}")

def launch_dashboard():
    """Ejecutar el dashboard"""
    print("📊 Iniciando Marketing Brain Dashboard...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "marketing_brain_dashboard.py"])
    except FileNotFoundError:
        print("❌ Archivo marketing_brain_dashboard.py no encontrado")
    except Exception as e:
        print(f"❌ Error ejecutando dashboard: {e}")

def launch_api():
    """Ejecutar la API"""
    print("🌐 Iniciando Marketing Brain API...")
    try:
        subprocess.run([sys.executable, "marketing_brain_api.py"])
    except FileNotFoundError:
        print("❌ Archivo marketing_brain_api.py no encontrado")
    except Exception as e:
        print(f"❌ Error ejecutando API: {e}")

def show_menu():
    """Mostrar menú principal"""
    print("\n" + "="*60)
    print("🧠 ADVANCED MARKETING BRAIN SYSTEM - LAUNCHER")
    print("="*60)
    print("Selecciona una opción:")
    print("1. 🧠 Sistema Core (Generación de conceptos)")
    print("2. 📊 Dashboard Interactivo")
    print("3. 🌐 API REST")
    print("4. 📦 Instalar dependencias")
    print("5. ✅ Verificar sistema")
    print("6. 📋 Mostrar documentación")
    print("0. 🚪 Salir")
    print("="*60)

def install_dependencies():
    """Instalar dependencias"""
    print("📦 Instalando dependencias...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencias instaladas correctamente")
    except Exception as e:
        print(f"❌ Error instalando dependencias: {e}")

def verify_system():
    """Verificar que el sistema esté funcionando"""
    print("✅ Verificando sistema...")
    
    # Verificar archivos principales
    required_files = [
        "advanced_marketing_brain_system.py",
        "marketing_brain_dashboard.py", 
        "marketing_brain_api.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Archivos faltantes:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    # Verificar dependencias
    if not check_dependencies():
        return False
    
    # Verificar archivos de datos opcionales
    optional_files = [
        "1000_ai_marketing_campaigns.json",
        "ESTRATEGIAS_CONTENIDO_MASTER_COMPLETO.md"
    ]
    
    missing_optional = []
    for file in optional_files:
        if not Path(file).exists():
            missing_optional.append(file)
    
    if missing_optional:
        print("⚠️ Archivos de datos opcionales faltantes (el sistema usará datos de muestra):")
        for file in missing_optional:
            print(f"   - {file}")
    
    print("✅ Sistema verificado correctamente")
    return True

def show_documentation():
    """Mostrar información de documentación"""
    print("\n📋 DOCUMENTACIÓN DEL SISTEMA")
    print("="*50)
    print("📖 Documentación completa: MARKETING_BRAIN_SYSTEM_DOCUMENTATION.md")
    print("🌐 API Documentation: http://localhost:5000/ (cuando la API esté ejecutándose)")
    print("📊 Dashboard: http://localhost:8501 (cuando el dashboard esté ejecutándose)")
    print("\n🚀 COMANDOS RÁPIDOS:")
    print("   Sistema Core:     python advanced_marketing_brain_system.py")
    print("   Dashboard:        streamlit run marketing_brain_dashboard.py")
    print("   API:              python marketing_brain_api.py")
    print("\n📝 EJEMPLOS DE USO:")
    print("   - Generar conceptos para E-commerce")
    print("   - Analizar documentos de estrategias")
    print("   - Crear sugerencias accionables")
    print("   - Exportar datos a JSON/CSV")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Marketing Brain System Launcher")
    parser.add_argument("--mode", choices=["core", "dashboard", "api", "install", "verify"], 
                       help="Modo de ejecución directa")
    
    args = parser.parse_args()
    
    if args.mode:
        # Modo directo
        if args.mode == "core":
            if check_dependencies():
                launch_core_system()
        elif args.mode == "dashboard":
            if check_dependencies():
                launch_dashboard()
        elif args.mode == "api":
            if check_dependencies():
                launch_api()
        elif args.mode == "install":
            install_dependencies()
        elif args.mode == "verify":
            verify_system()
        return
    
    # Modo interactivo
    while True:
        show_menu()
        
        try:
            choice = input("\nIngresa tu opción (0-6): ").strip()
            
            if choice == "0":
                print("👋 ¡Hasta luego!")
                break
            elif choice == "1":
                if check_dependencies():
                    launch_core_system()
            elif choice == "2":
                if check_dependencies():
                    launch_dashboard()
            elif choice == "3":
                if check_dependencies():
                    launch_api()
            elif choice == "4":
                install_dependencies()
            elif choice == "5":
                verify_system()
            elif choice == "6":
                show_documentation()
            else:
                print("❌ Opción inválida. Intenta de nuevo.")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()








