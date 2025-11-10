#!/usr/bin/env python3
"""
Exportador de Paquete Completo
Crea un paquete ZIP con todas las plantillas y herramientas seleccionadas
"""

import os
import shutil
from pathlib import Path
from typing import List
from datetime import datetime
import zipfile

def crear_paquete(directorio: Path, archivos_incluir: List[str], nombre_paquete: str):
    """Crea un paquete ZIP con los archivos especificados"""
    archivo_zip = directorio / nombre_paquete
    
    with zipfile.ZipFile(archivo_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for archivo in archivos_incluir:
            ruta_archivo = directorio / archivo
            if ruta_archivo.exists():
                zipf.write(ruta_archivo, archivo)
                print(f"✅ Agregado: {archivo}")
    
    return archivo_zip

def main():
    """Función principal"""
    print("=" * 70)
    print("📦 Exportador de Paquete Completo")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    print("Selecciona qué incluir en el paquete:")
    print()
    print("1. Solo plantillas HTML")
    print("2. Plantillas + Scripts Python")
    print("3. Plantillas + Documentación")
    print("4. Todo el proyecto")
    print()
    
    try:
        opcion = input("Opción (1-4, Enter para opción 4): ").strip()
        if not opcion:
            opcion = "4"
        
        archivos_incluir = []
        
        if opcion == "1":
            # Solo plantillas HTML
            plantillas = sorted(directorio_actual.glob("firma_*.html"))
            archivos_incluir = [p.name for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name]
            nombre_paquete = f"firmas_email_plantillas_{datetime.now().strftime('%Y%m%d')}.zip"
        
        elif opcion == "2":
            # Plantillas + Scripts
            plantillas = sorted(directorio_actual.glob("firma_*.html"))
            scripts = sorted(directorio_actual.glob("*.py"))
            archivos_incluir = [p.name for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name]
            archivos_incluir.extend([s.name for s in scripts])
            nombre_paquete = f"firmas_email_completo_{datetime.now().strftime('%Y%m%d')}.zip"
        
        elif opcion == "3":
            # Plantillas + Documentación
            plantillas = sorted(directorio_actual.glob("firma_*.html"))
            docs = sorted(directorio_actual.glob("*.md"))
            archivos_incluir = [p.name for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name]
            archivos_incluir.extend([d.name for d in docs])
            nombre_paquete = f"firmas_email_documentado_{datetime.now().strftime('%Y%m%d')}.zip"
        
        else:
            # Todo el proyecto (excepto archivos generados y variaciones)
            todos = sorted(directorio_actual.iterdir())
            for archivo in todos:
                if archivo.is_file():
                    nombre = archivo.name
                    # Excluir archivos generados y variaciones
                    if not any(excluir in nombre for excluir in ['variacion', 'personalizada', 'optimizada', 'preview', 'reporte', '.pyc', '__pycache__']):
                        archivos_incluir.append(nombre)
            nombre_paquete = f"firmas_email_proyecto_completo_{datetime.now().strftime('%Y%m%d')}.zip"
        
        if not archivos_incluir:
            print("❌ No se encontraron archivos para incluir")
            return
        
        print()
        print(f"📋 Archivos a incluir: {len(archivos_incluir)}")
        print()
        print("⚡ Creando paquete...")
        print()
        
        archivo_zip = crear_paquete(directorio_actual, archivos_incluir, nombre_paquete)
        
        # Calcular tamaño
        tamaño = archivo_zip.stat().st_size
        
        print()
        print("=" * 70)
        print("✅ Paquete creado exitosamente")
        print("=" * 70)
        print(f"📦 Archivo: {archivo_zip.name}")
        print(f"📊 Tamaño: {tamaño:,} bytes ({tamaño / 1024:.1f} KB)")
        print(f"📁 Ubicación: {archivo_zip.parent}")
        print()
        print("💡 El paquete está listo para compartir o distribuir")
        print("=" * 70)
    
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()






