#!/usr/bin/env python3
"""
Script de Inicio del Servidor API
================================

Script para iniciar el servidor API con configuraciones optimizadas
para producción y desarrollo.

Autor: Sistema de Organización Enterprise
Versión: 1.0
"""

import os
import sys
from pathlib import Path

# Agregar el directorio padre al path para importar módulos
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

def main():
    """Función principal para iniciar el servidor"""
    print("🚀 Iniciando Servidor API del Sistema de Organización")
    print("=====================================================")
    
    # Verificar que estamos en el directorio correcto
    current_dir = Path(__file__).parent
    os.chdir(current_dir)
    
    # Configurar variables de entorno
    os.environ['FLASK_APP'] = 'app.py'
    os.environ['FLASK_ENV'] = 'development'  # Cambiar a 'production' en producción
    
    print("📁 Directorio de trabajo:", current_dir)
    print("🔧 Variables de entorno configuradas")
    
    # Importar y ejecutar la aplicación
    try:
        from app import main as app_main
        app_main()
    except ImportError as e:
        print(f"❌ Error importando la aplicación: {e}")
        print("💡 Asegúrate de que todas las dependencias estén instaladas:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error iniciando el servidor: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()


