#!/usr/bin/env python3
"""
Generador de Variaciones de Firmas
Genera múltiples variaciones de una plantilla base con diferentes configuraciones
"""

import os
import re
from pathlib import Path
from typing import Dict, List
import json

def reemplazar_placeholders(contenido: str, configuracion: Dict) -> str:
    """Reemplaza placeholders en el contenido"""
    resultado = contenido
    for key, value in configuracion.items():
        # Buscar [KEY] y reemplazar
        resultado = resultado.replace(f"[{key}]", str(value))
    return resultado


def generar_variacion(plantilla_base: str, configuracion: Dict, nombre_salida: str) -> bool:
    """Genera una variación de la plantilla"""
    try:
        with open(plantilla_base, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Reemplazar placeholders
        contenido_personalizado = reemplazar_placeholders(contenido, configuracion)
        
        # Guardar
        with open(nombre_salida, 'w', encoding='utf-8') as f:
            f.write(contenido_personalizado)
        
        return True
    except Exception as e:
        print(f"Error generando variación: {e}")
        return False


def generar_variaciones_automaticas(plantilla_base: str, directorio_salida: str):
    """Genera variaciones automáticas de una plantilla"""
    directorio_salida = Path(directorio_salida)
    directorio_salida.mkdir(exist_ok=True)
    
    nombre_base = Path(plantilla_base).stem
    
    # Configuraciones de ejemplo
    variaciones = [
        {
            "nombre": f"{nombre_base}_variacion_1",
            "config": {
                "Tu Nombre": "Juan Pérez",
                "Tu Cargo": "Director de Marketing",
                "Nombre de la Empresa": "Tech Solutions",
                "tu-email@ejemplo.com": "juan.perez@techsolutions.com",
                "URL_WEBSITE": "https://www.techsolutions.com",
                "URL_LINKEDIN": "https://linkedin.com/in/juanperez",
                "URL_TWITTER": "https://twitter.com/juanperez"
            }
        },
        {
            "nombre": f"{nombre_base}_variacion_2",
            "config": {
                "Tu Nombre": "María García",
                "Tu Cargo": "CEO",
                "Nombre de la Empresa": "Innovation Labs",
                "tu-email@ejemplo.com": "maria.garcia@innovationlabs.com",
                "URL_WEBSITE": "https://www.innovationlabs.com",
                "URL_LINKEDIN": "https://linkedin.com/in/mariagarcia",
                "URL_TWITTER": "https://twitter.com/mariagarcia"
            }
        },
        {
            "nombre": f"{nombre_base}_variacion_3",
            "config": {
                "Tu Nombre": "Carlos Rodríguez",
                "Tu Cargo": "CTO",
                "Nombre de la Empresa": "Digital Ventures",
                "tu-email@ejemplo.com": "carlos.rodriguez@digitalventures.com",
                "URL_WEBSITE": "https://www.digitalventures.com",
                "URL_LINKEDIN": "https://linkedin.com/in/carlosrodriguez",
                "URL_TWITTER": "https://twitter.com/carlosrodriguez"
            }
        }
    ]
    
    exitosos = 0
    for variacion in variaciones:
        archivo_salida = directorio_salida / f"{variacion['nombre']}.html"
        if generar_variacion(plantilla_base, variacion['config'], str(archivo_salida)):
            exitosos += 1
            print(f"✅ Generada: {archivo_salida.name}")
    
    return exitosos


def main():
    """Función principal"""
    print("=" * 70)
    print("🎨 Generador de Variaciones de Firmas")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    # Buscar plantillas
    plantillas = sorted(directorio_actual.glob("firma_*.html"))
    plantillas = [str(p) for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name]
    
    if not plantillas:
        print("❌ No se encontraron plantillas")
        return
    
    print(f"📋 Plantillas encontradas: {len(plantillas)}")
    print()
    
    # Seleccionar plantilla
    print("Selecciona una plantilla para generar variaciones:")
    print()
    for i, plantilla in enumerate(plantillas[:10], 1):  # Mostrar solo las primeras 10
        print(f"{i}. {Path(plantilla).name}")
    
    if len(plantillas) > 10:
        print(f"... y {len(plantillas) - 10} más")
    
    print()
    try:
        seleccion = input("Número de plantilla (Enter para usar la primera): ").strip()
        if seleccion:
            indice = int(seleccion) - 1
            if indice < 0 or indice >= len(plantillas):
                print("❌ Selección inválida")
                return
            plantilla_seleccionada = plantillas[indice]
        else:
            plantilla_seleccionada = plantillas[0]
    except (ValueError, KeyboardInterrupt):
        print("\n❌ Operación cancelada")
        return
    
    print()
    print(f"📄 Plantilla seleccionada: {Path(plantilla_seleccionada).name}")
    print()
    print("⚡ Generando variaciones...")
    print()
    
    directorio_salida = directorio_actual / "variaciones"
    exitosos = generar_variaciones_automaticas(plantilla_seleccionada, str(directorio_salida))
    
    print()
    print("=" * 70)
    print("📊 Resumen")
    print("=" * 70)
    print(f"✅ Variaciones generadas: {exitosos}")
    print(f"📂 Archivos guardados en: {directorio_salida}")
    print()
    print("💡 Puedes editar las variaciones generadas o usar como base")
    print("   para crear tus propias personalizaciones.")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()






