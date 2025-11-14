#!/usr/bin/env python3
"""
Script para abrir los documentos generados
"""

import os
import subprocess
import sys
from pathlib import Path

def open_documents():
    """Abre los documentos generados"""
    
    # Archivos generados
    files = {
        "HTML": "/Users/adan/frontier/frases-populares-busqueda-google-2024.html",
        "PDF": "/Users/adan/frontier/frases-populares-busqueda-google-2024.pdf",
        "Word": "/Users/adan/frontier/frases-populares-busqueda-google-2024.docx",
        "Markdown": "/Users/adan/frontier/frases-populares-busqueda-google-2024.md"
    }
    
    print("📁 Archivos generados:")
    print("=" * 50)
    
    for file_type, file_path in files.items():
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_type}: {file_path}")
            print(f"   Tamaño: {size:,} bytes")
        else:
            print(f"❌ {file_type}: No encontrado")
        print()
    
    print("🚀 Abriendo documentos...")
    
    # Abrir archivos en sus aplicaciones por defecto
    try:
        # Abrir HTML en el navegador
        if os.path.exists(files["HTML"]):
            subprocess.run(["open", files["HTML"]], check=True)
            print("✅ HTML abierto en el navegador")
        
        # Abrir PDF en el visor por defecto
        if os.path.exists(files["PDF"]):
            subprocess.run(["open", files["PDF"]], check=True)
            print("✅ PDF abierto en el visor por defecto")
        
        # Abrir Word en la aplicación por defecto
        if os.path.exists(files["Word"]):
            subprocess.run(["open", files["Word"]], check=True)
            print("✅ Word abierto en la aplicación por defecto")
        
        # Abrir Markdown en el editor por defecto
        if os.path.exists(files["Markdown"]):
            subprocess.run(["open", files["Markdown"]], check=True)
            print("✅ Markdown abierto en el editor por defecto")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al abrir archivos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def main():
    """Función principal"""
    print("🎯 Abriendo documentos generados...")
    open_documents()
    print("\n✨ ¡Proceso completado!")

if __name__ == "__main__":
    main()










