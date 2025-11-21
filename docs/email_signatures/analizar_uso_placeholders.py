#!/usr/bin/env python3
"""
Analizador de Uso de Placeholders
Analiza qué placeholders se usan más y en qué plantillas
"""

import os
import re
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

def extraer_placeholders(contenido: str) -> List[str]:
    """Extrae todos los placeholders del contenido"""
    placeholders = re.findall(r'\[([^\]]+)\]', contenido)
    return list(set(placeholders))

def analizar_uso_placeholders(directorio: Path) -> Dict:
    """Analiza el uso de placeholders en todas las plantillas"""
    plantillas = sorted(directorio.glob("firma_*.html"))
    plantillas = [p for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name]
    
    # Contadores
    uso_placeholders = defaultdict(lambda: {"veces": 0, "plantillas": []})
    plantillas_analizadas = {}
    
    for plantilla in plantillas:
        try:
            with open(plantilla, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            placeholders = extraer_placeholders(contenido)
            plantillas_analizadas[plantilla.name] = placeholders
            
            for placeholder in placeholders:
                uso_placeholders[placeholder]["veces"] += 1
                if plantilla.name not in uso_placeholders[placeholder]["plantillas"]:
                    uso_placeholders[placeholder]["plantillas"].append(plantilla.name)
        
        except Exception as e:
            print(f"Error procesando {plantilla.name}: {e}")
    
    return {
        "uso_placeholders": dict(uso_placeholders),
        "plantillas_analizadas": plantillas_analizadas
    }

def generar_reporte(analisis: Dict) -> str:
    """Genera un reporte del análisis"""
    reporte = "# 📊 Análisis de Uso de Placeholders\n\n"
    reporte += "Este reporte muestra qué placeholders se usan más frecuentemente en las plantillas.\n\n"
    
    uso = analisis["uso_placeholders"]
    
    # Ordenar por frecuencia
    placeholders_ordenados = sorted(uso.items(), key=lambda x: x[1]["veces"], reverse=True)
    
    reporte += "## 🏆 Top 20 Placeholders Más Usados\n\n"
    reporte += "| # | Placeholder | Veces Usado | Plantillas |\n"
    reporte += "|---|-------------|-------------|------------|\n"
    
    for i, (placeholder, datos) in enumerate(placeholders_ordenados[:20], 1):
        veces = datos["veces"]
        num_plantillas = len(datos["plantillas"])
        reporte += f"| {i} | `[{placeholder}]` | {veces} | {num_plantillas} |\n"
    
    reporte += "\n"
    
    # Placeholders por categoría
    reporte += "## 📋 Placeholders por Categoría\n\n"
    
    categorias = {
        "Información Personal": ["Tu Nombre", "Tu Cargo", "tu-email@ejemplo.com"],
        "Empresa": ["Nombre de la Empresa", "Nombre de la Institución", "Nombre del Producto"],
        "URLs": [k for k in uso.keys() if k.startswith("URL_")],
        "Contacto": ["tel:", "mailto:"],
        "Otros": []
    }
    
    otros = set(uso.keys())
    for categoria, lista in categorias.items():
        if categoria != "Otros":
            otros -= set(lista)
    categorias["Otros"] = list(otros)
    
    for categoria, lista in categorias.items():
        if lista:
            reporte += f"### {categoria}\n\n"
            for placeholder in sorted(lista):
                if placeholder in uso:
                    datos = uso[placeholder]
                    reporte += f"- **`[{placeholder}]`** - Usado {datos['veces']} vez(ces) en {len(datos['plantillas'])} plantilla(s)\n"
            reporte += "\n"
    
    # Estadísticas
    reporte += "## 📊 Estadísticas\n\n"
    reporte += f"- **Total de placeholders únicos:** {len(uso)}\n"
    reporte += f"- **Total de plantillas analizadas:** {len(analisis['plantillas_analizadas'])}\n"
    
    # Placeholders más comunes (en >50% de plantillas)
    total_plantillas = len(analisis['plantillas_analizadas'])
    umbral = total_plantillas * 0.5
    
    comunes = [(k, v) for k, v in uso.items() if len(v["plantillas"]) >= umbral]
    if comunes:
        reporte += f"\n### Placeholders Comunes (en >50% de plantillas)\n\n"
        for placeholder, datos in sorted(comunes, key=lambda x: len(x[1]["plantillas"]), reverse=True):
            porcentaje = (len(datos["plantillas"]) / total_plantillas) * 100
            reporte += f"- **`[{placeholder}]`** - {len(datos['plantillas'])} plantillas ({porcentaje:.1f}%)\n"
    
    reporte += "\n---\n\n"
    reporte += "*Reporte generado automáticamente*\n"
    
    return reporte

def main():
    """Función principal"""
    print("=" * 70)
    print("📊 Analizador de Uso de Placeholders")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    print("🔍 Analizando uso de placeholders...")
    print()
    
    analisis = analizar_uso_placeholders(directorio_actual)
    
    # Generar reporte
    reporte = generar_reporte(analisis)
    
    # Guardar
    archivo_reporte = directorio_actual / "ANALISIS_PLACEHOLDERS.md"
    with open(archivo_reporte, 'w', encoding='utf-8') as f:
        f.write(reporte)
    
    print("=" * 70)
    print("✅ Análisis completado")
    print("=" * 70)
    print(f"📄 Reporte guardado en: {archivo_reporte.name}")
    print()
    print(f"📊 Placeholders únicos encontrados: {len(analisis['uso_placeholders'])}")
    print(f"📋 Plantillas analizadas: {len(analisis['plantillas_analizadas'])}")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()






