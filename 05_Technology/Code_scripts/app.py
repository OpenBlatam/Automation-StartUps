#!/usr/bin/env python3
"""
Punto de entrada principal para el Sistema de Control de Inventario Inteligente.
Este archivo permite ejecutar la aplicación desde la raíz del proyecto.
"""
import sys
import os

# Agregar el directorio actual y 05_Technology al path para que los imports funcionen
current_dir = os.path.dirname(os.path.abspath(__file__))
tech_dir = os.path.join(current_dir, '05_Technology')
sys.path.insert(0, current_dir)
sys.path.insert(0, tech_dir)

# Importar y ejecutar la aplicación desde 05_Technology
if __name__ == '__main__':
    # Cambiar al directorio raíz para que los imports relativos funcionen
    os.chdir(current_dir)
    
    # Importar directamente (ya que agregamos al path)
    from app import create_app
    
    # Crear la aplicación
    app = create_app()
    
    # Ejecutar la aplicación
    app.run(debug=True, host='0.0.0.0', port=5000)

