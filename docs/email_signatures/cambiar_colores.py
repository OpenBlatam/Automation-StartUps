#!/usr/bin/env python3
"""
Cambiador de Colores de Firmas
Cambia los colores de una plantilla manteniendo la estructura
"""

import re
import os
from pathlib import Path
from typing import Dict, List

# Esquemas de colores predefinidos
ESQUEMAS_COLOR = {
    "azul": {
        "principal": "#1a73e8",
        "secundario": "#34a853",
        "texto": "#202124",
        "gris": "#5f6368",
        "gris_claro": "#80868b"
    },
    "rojo": {
        "principal": "#ea4335",
        "secundario": "#fbbc04",
        "texto": "#202124",
        "gris": "#5f6368",
        "gris_claro": "#80868b"
    },
    "púrpura": {
        "principal": "#9c27b0",
        "secundario": "#7b1fa2",
        "texto": "#202124",
        "gris": "#5f6368",
        "gris_claro": "#80868b"
    },
    "verde": {
        "principal": "#0f9d58",
        "secundario": "#34a853",
        "texto": "#202124",
        "gris": "#5f6368",
        "gris_claro": "#80868b"
    },
    "naranja": {
        "principal": "#ff9800",
        "secundario": "#f57c00",
        "texto": "#202124",
        "gris": "#5f6368",
        "gris_claro": "#80868b"
    },
    "teal": {
        "principal": "#009688",
        "secundario": "#00796b",
        "texto": "#202124",
        "gris": "#5f6368",
        "gris_claro": "#80868b"
    },
    "oscuro": {
        "principal": "#2c3e50",
        "secundario": "#34495e",
        "texto": "#ffffff",
        "gris": "#b0b0b0",
        "gris_claro": "#808080"
    }
}


def detectar_colores_actuales(contenido: str) -> Dict[str, List[str]]:
    """Detecta los colores principales usados en la plantilla"""
    colores = {
        "principales": [],
        "secundarios": [],
        "texto": [],
        "grises": []
    }
    
    # Buscar colores hexadecimales
    hex_colors = re.findall(r'#([0-9a-fA-F]{6})', contenido)
    colores_unicos = list(set(hex_colors))
    
    # Clasificar colores comunes
    for color in colores_unicos:
        color_upper = color.upper()
        if color_upper in ["1A73E8", "EA4335", "9C27B0", "0F9D58"]:
            colores["principales"].append(f"#{color_upper}")
        elif color_upper in ["34A853", "FBBC04", "7B1FA2"]:
            colores["secundarios"].append(f"#{color_upper}")
        elif color_upper in ["202124", "333333", "2C3E50"]:
            colores["texto"].append(f"#{color_upper}")
        elif color_upper in ["5F6368", "80868B", "808080"]:
            colores["grises"].append(f"#{color_upper}")
    
    return colores


def cambiar_colores(archivo_entrada: str, archivo_salida: str, esquema: Dict[str, str]) -> tuple[bool, int]:
    """Cambia los colores de una plantilla"""
    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Detectar colores actuales
        colores_actuales = detectar_colores_actuales(contenido)
        
        # Mapeo de reemplazo
        reemplazos = {
            # Colores principales comunes
            "#1a73e8": esquema["principal"],
            "#ea4335": esquema["principal"],
            "#9c27b0": esquema["principal"],
            "#0f9d58": esquema["principal"],
            "#ff9800": esquema["principal"],
            "#009688": esquema["principal"],
            "#2c3e50": esquema["principal"],
            
            # Colores secundarios comunes
            "#34a853": esquema["secundario"],
            "#fbbc04": esquema["secundario"],
            "#7b1fa2": esquema["secundario"],
            
            # Colores de texto
            "#202124": esquema["texto"],
            "#333333": esquema["texto"],
            
            # Colores grises
            "#5f6368": esquema["gris"],
            "#80868b": esquema["gris_claro"],
            "#808080": esquema["gris_claro"],
        }
        
        # Reemplazar (case insensitive)
        cambios = 0
        for color_antiguo, color_nuevo in reemplazos.items():
            # Reemplazar en minúsculas
            patron = re.compile(re.escape(color_antiguo), re.IGNORECASE)
            matches = len(patron.findall(contenido))
            if matches > 0:
                contenido = patron.sub(color_nuevo, contenido)
                cambios += matches
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(archivo_salida), exist_ok=True)
        
        # Guardar
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        return True, cambios
    
    except Exception as e:
        return False, 0


def main():
    """Función principal"""
    print("=" * 70)
    print("🎨 Cambiador de Colores de Firmas de Email")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    # Buscar plantillas
    plantillas = sorted(directorio_actual.glob("firma_*.html"))
    plantillas = [str(p) for p in plantillas if "personalizada" not in p.name and "tema" not in p.name]
    
    if not plantillas:
        print("❌ No se encontraron plantillas")
        return
    
    print(f"📋 Plantillas encontradas: {len(plantillas)}")
    print()
    print("🎨 Esquemas de color disponibles:")
    for i, (nombre, esquema) in enumerate(ESQUEMAS_COLOR.items(), 1):
        print(f"   {i}. {nombre.capitalize()} (Principal: {esquema['principal']})")
    print()
    
    # Seleccionar esquema
    try:
        seleccion = input("Selecciona un esquema (número o nombre): ").strip().lower()
        
        if seleccion.isdigit():
            indice = int(seleccion) - 1
            esquema_nombre = list(ESQUEMAS_COLOR.keys())[indice]
        else:
            esquema_nombre = seleccion
        
        if esquema_nombre not in ESQUEMAS_COLOR:
            print(f"❌ Esquema '{esleccion}' no encontrado")
            return
        
        esquema = ESQUEMAS_COLOR[esquema_nombre]
        print(f"\n✅ Esquema seleccionado: {esquema_nombre.capitalize()}")
        print(f"   Principal: {esquema['principal']}")
        print(f"   Secundario: {esquema['secundario']}")
        print()
    
    except (ValueError, IndexError, KeyboardInterrupt):
        print("\n❌ Selección inválida o cancelada")
        return
    
    # Procesar plantillas
    directorio_salida = directorio_actual / "plantillas_colores"
    directorio_salida.mkdir(exist_ok=True)
    
    print("🔄 Procesando plantillas...\n")
    
    exitosos = 0
    fallidos = 0
    total_cambios = 0
    
    for plantilla in plantillas:
        nombre_plantilla = Path(plantilla).stem
        archivo_salida = directorio_salida / f"{nombre_plantilla}_{esquema_nombre}.html"
        
        success, cambios = cambiar_colores(plantilla, str(archivo_salida), esquema)
        
        if success:
            print(f"✅ {Path(plantilla).name} → {archivo_salida.name} ({cambios} cambios)")
            exitosos += 1
            total_cambios += cambios
        else:
            print(f"❌ Error procesando {Path(plantilla).name}")
            fallidos += 1
    
    # Resumen
    print()
    print("=" * 70)
    print("📊 Resumen")
    print("=" * 70)
    print(f"✅ Exitosos: {exitosos}")
    print(f"❌ Fallidos: {fallidos}")
    print(f"🎨 Total de cambios de color: {total_cambios}")
    print(f"📂 Archivos guardados en: {directorio_salida}")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()






