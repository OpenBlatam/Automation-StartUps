#!/usr/bin/env python3
"""
Actualizador de Placeholders
Encuentra y lista todos los placeholders únicos en las plantillas
"""

import os
import re
from pathlib import Path
from typing import Set, Dict, List
from collections import defaultdict

def extraer_placeholders(contenido: str) -> Set[str]:
    """Extrae todos los placeholders del contenido"""
    # Buscar patrones [PLACEHOLDER]
    placeholders = re.findall(r'\[([^\]]+)\]', contenido)
    return set(placeholders)

def analizar_plantillas() -> Dict[str, List[str]]:
    """Analiza todas las plantillas y extrae placeholders"""
    directorio_actual = Path(__file__).parent
    plantillas = sorted(directorio_actual.glob("firma_*.html"))
    plantillas = [str(p) for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name]
    
    todos_placeholders = defaultdict(list)
    
    for plantilla in plantillas:
        try:
            with open(plantilla, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            placeholders = extraer_placeholders(contenido)
            
            for placeholder in placeholders:
                todos_placeholders[placeholder].append(Path(plantilla).name)
        except Exception as e:
            print(f"Error procesando {plantilla}: {e}")
    
    return todos_placeholders

def generar_documentacion_placeholders(placeholders: Dict[str, List[str]]) -> str:
    """Genera documentación de placeholders"""
    doc = "# 📋 Documentación de Placeholders\n\n"
    doc += "Esta documentación lista todos los placeholders utilizados en las plantillas.\n\n"
    doc += "## Placeholders Comunes\n\n"
    
    # Categorizar placeholders
    categorias = {
        "Información Personal": ["Tu Nombre", "Tu Cargo", "tu-email@ejemplo.com"],
        "Empresa": ["Nombre de la Empresa", "Nombre de la Institución", "Nombre del Producto"],
        "Contacto": ["URL_WEBSITE", "URL_LINKEDIN", "URL_TWITTER", "URL_GITHUB", "URL_PRODUCTO", "URL_DEMO"],
        "Específicos": []
    }
    
    comunes = set()
    for categoria, lista in categorias.items():
        comunes.update(lista)
    
    # Agrupar
    comunes_encontrados = {}
    especificos = {}
    
    for placeholder, archivos in sorted(placeholders.items()):
        if placeholder in comunes:
            comunes_encontrados[placeholder] = archivos
        else:
            especificos[placeholder] = archivos
    
    # Documentar comunes
    doc += "### Información Personal\n\n"
    for key in ["Tu Nombre", "Tu Cargo", "tu-email@ejemplo.com"]:
        if key in comunes_encontrados:
            doc += f"- **`[{key}]`** - Usado en {len(comunes_encontrados[key])} plantilla(s)\n"
    
    doc += "\n### Empresa\n\n"
    for key in ["Nombre de la Empresa", "Nombre de la Institución", "Nombre del Producto"]:
        if key in comunes_encontrados:
            doc += f"- **`[{key}]`** - Usado en {len(comunes_encontrados[key])} plantilla(s)\n"
    
    doc += "\n### Contacto y URLs\n\n"
    for key in sorted([k for k in comunes_encontrados.keys() if k.startswith("URL_")]):
        doc += f"- **`[{key}]`** - Usado en {len(comunes_encontrados[key])} plantilla(s)\n"
    
    doc += "\n## Placeholders Específicos\n\n"
    for placeholder, archivos in sorted(especificos.items()):
        doc += f"- **`[{placeholder}]`** - Usado en {len(archivos)} plantilla(s)\n"
        doc += f"  - Archivos: {', '.join(archivos[:3])}"
        if len(archivos) > 3:
            doc += f" y {len(archivos) - 3} más"
        doc += "\n"
    
    doc += "\n## Estadísticas\n\n"
    doc += f"- **Total de placeholders únicos:** {len(placeholders)}\n"
    doc += f"- **Placeholders comunes:** {len(comunes_encontrados)}\n"
    doc += f"- **Placeholders específicos:** {len(especificos)}\n"
    
    return doc

def main():
    """Función principal"""
    print("=" * 70)
    print("📋 Actualizador de Placeholders")
    print("=" * 70)
    print()
    
    print("🔍 Analizando plantillas...")
    print()
    
    placeholders = analizar_plantillas()
    
    if not placeholders:
        print("❌ No se encontraron placeholders")
        return
    
    print(f"✅ Se encontraron {len(placeholders)} placeholders únicos")
    print()
    
    # Mostrar resumen
    print("📊 Resumen de Placeholders:")
    print()
    
    # Contar por frecuencia
    frecuencia = {k: len(v) for k, v in placeholders.items()}
    mas_usados = sorted(frecuencia.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print("Top 10 más usados:")
    for placeholder, count in mas_usados:
        print(f"  [{placeholder}] - {count} plantilla(s)")
    
    print()
    
    # Generar documentación
    directorio_actual = Path(__file__).parent
    archivo_doc = directorio_actual / "PLACEHOLDERS.md"
    
    doc = generar_documentacion_placeholders(placeholders)
    
    with open(archivo_doc, 'w', encoding='utf-8') as f:
        f.write(doc)
    
    print("=" * 70)
    print("✅ Documentación generada")
    print("=" * 70)
    print(f"📄 Archivo: {archivo_doc.name}")
    print()
    print("💡 Revisa PLACEHOLDERS.md para ver la documentación completa")
    print("=" * 70)

if __name__ == "__main__":
    main()






