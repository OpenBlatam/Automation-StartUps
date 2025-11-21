#!/usr/bin/env python3
"""
Analizador de Estadísticas Avanzadas
Genera análisis avanzado con gráficos y métricas detalladas
"""

import os
import re
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
from datetime import datetime

def analizar_plantilla_detallada(archivo: Path) -> Dict:
    """Análisis detallado de una plantilla"""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Métricas básicas
        tamaño = len(contenido.encode('utf-8'))
        lineas = len(contenido.split('\n'))
        caracteres = len(contenido)
        palabras = len(re.findall(r'\b\w+\b', contenido))
        
        # Estructura
        num_tablas = contenido.count('<table')
        num_enlaces = len(re.findall(r'href\s*=', contenido, re.IGNORECASE))
        num_imagenes = contenido.count('<img')
        num_botones = len(re.findall(r'button|roundrect|btn', contenido, re.IGNORECASE))
        
        # Placeholders
        placeholders = re.findall(r'\[([^\]]+)\]', contenido)
        placeholders_unicos = list(set(placeholders))
        
        # Compatibilidad
        tiene_vml = 'xmlns:v=' in contenido
        tiene_mso = '<!--[if mso]' in contenido
        tiene_media_queries = '@media' in contenido
        tiene_estilos_inline = 'style=' in contenido
        
        # Accesibilidad
        num_aria = contenido.count('aria-label')
        num_alt = contenido.count('alt=')
        num_roles = contenido.count('role=')
        
        return {
            "nombre": archivo.name,
            "tamaño": tamaño,
            "lineas": lineas,
            "caracteres": caracteres,
            "palabras": palabras,
            "estructura": {
                "tablas": num_tablas,
                "enlaces": num_enlaces,
                "imagenes": num_imagenes,
                "botones": num_botones
            },
            "placeholders": {
                "total": len(placeholders),
                "unicos": len(placeholders_unicos),
                "lista": placeholders_unicos
            },
            "compatibilidad": {
                "outlook": tiene_vml and tiene_mso,
                "responsive": tiene_media_queries,
                "estilos_inline": tiene_estilos_inline
            },
            "accesibilidad": {
                "aria_labels": num_aria,
                "alt_text": num_alt,
                "roles": num_roles
            }
        }
    except Exception as e:
        return {"nombre": archivo.name, "error": str(e)}

def generar_analisis_avanzado(directorio: Path) -> str:
    """Genera análisis avanzado"""
    plantillas = sorted(directorio.glob("firma_*.html"))
    plantillas = [p for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name]
    
    analisis_plantillas = []
    for plantilla in plantillas:
        analisis = analizar_plantilla_detallada(plantilla)
        if "error" not in analisis:
            analisis_plantillas.append(analisis)
    
    # Calcular estadísticas agregadas
    total_tamaño = sum(p["tamaño"] for p in analisis_plantillas)
    total_lineas = sum(p["lineas"] for p in analisis_plantillas)
    total_tablas = sum(p["estructura"]["tablas"] for p in analisis_plantillas)
    total_enlaces = sum(p["estructura"]["enlaces"] for p in analisis_plantillas)
    
    # Compatibilidad
    con_outlook = sum(1 for p in analisis_plantillas if p["compatibilidad"]["outlook"])
    con_responsive = sum(1 for p in analisis_plantillas if p["compatibilidad"]["responsive"])
    
    # Placeholders más usados
    todos_placeholders = defaultdict(int)
    for p in analisis_plantillas:
        for placeholder in p["placeholders"]["lista"]:
            todos_placeholders[placeholder] += 1
    
    # Generar reporte
    reporte = "# 📊 Análisis Avanzado de Estadísticas\n\n"
    reporte += f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    reporte += "## 📈 Métricas Generales\n\n"
    reporte += f"- **Total de plantillas analizadas:** {len(analisis_plantillas)}\n"
    reporte += f"- **Tamaño total:** {total_tamaño:,} bytes ({total_tamaño / 1024:.1f} KB)\n"
    reporte += f"- **Líneas totales:** {total_lineas:,}\n"
    reporte += f"- **Tamaño promedio:** {total_tamaño // len(analisis_plantillas):,} bytes\n"
    reporte += f"- **Líneas promedio:** {total_lineas // len(analisis_plantillas)}\n\n"
    
    reporte += "## 🏗️ Estructura\n\n"
    reporte += f"- **Total de tablas:** {total_tablas} (promedio: {total_tablas / len(analisis_plantillas):.1f} por plantilla)\n"
    reporte += f"- **Total de enlaces:** {total_enlaces} (promedio: {total_enlaces / len(analisis_plantillas):.1f} por plantilla)\n\n"
    
    reporte += "## ✨ Compatibilidad\n\n"
    reporte += f"- **Soporte Outlook:** {con_outlook}/{len(analisis_plantillas)} ({con_outlook*100//len(analisis_plantillas)}%)\n"
    reporte += f"- **Responsive:** {con_responsive}/{len(analisis_plantillas)} ({con_responsive*100//len(analisis_plantillas)}%)\n\n"
    
    reporte += "## 📋 Placeholders Más Usados\n\n"
    top_placeholders = sorted(todos_placeholders.items(), key=lambda x: x[1], reverse=True)[:15]
    reporte += "| # | Placeholder | Veces Usado |\n"
    reporte += "|---|-------------|-------------|\n"
    for i, (placeholder, veces) in enumerate(top_placeholders, 1):
        reporte += f"| {i} | `[{placeholder}]` | {veces} |\n"
    
    reporte += "\n"
    
    # Top plantillas
    reporte += "## 🏆 Top 10 Plantillas Más Grandes\n\n"
    top_plantillas = sorted(analisis_plantillas, key=lambda x: x["tamaño"], reverse=True)[:10]
    reporte += "| # | Plantilla | Tamaño | Líneas | Enlaces |\n"
    reporte += "|---|-----------|--------|--------|---------|\n"
    for i, p in enumerate(top_plantillas, 1):
        reporte += f"| {i} | {p['nombre']} | {p['tamaño']:,} bytes | {p['lineas']} | {p['estructura']['enlaces']} |\n"
    
    reporte += "\n"
    
    # Distribución de tamaño
    reporte += "## 📊 Distribución de Tamaño\n\n"
    pequenas = sum(1 for p in analisis_plantillas if p["tamaño"] < 5000)
    medianas = sum(1 for p in analisis_plantillas if 5000 <= p["tamaño"] < 10000)
    grandes = sum(1 for p in analisis_plantillas if p["tamaño"] >= 10000)
    
    reporte += f"- **Pequeñas (<5KB):** {pequenas} plantillas\n"
    reporte += f"- **Medianas (5-10KB):** {medianas} plantillas\n"
    reporte += f"- **Grandes (>10KB):** {grandes} plantillas\n\n"
    
    reporte += "---\n\n"
    reporte += "*Análisis generado automáticamente*\n"
    
    return reporte

def main():
    """Función principal"""
    print("=" * 70)
    print("📊 Analizador de Estadísticas Avanzadas")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    print("🔍 Analizando plantillas en detalle...")
    print()
    
    reporte = generar_analisis_avanzado(directorio_actual)
    
    # Guardar
    archivo_reporte = directorio_actual / "ANALISIS_ESTADISTICAS_AVANZADAS.md"
    with open(archivo_reporte, 'w', encoding='utf-8') as f:
        f.write(reporte)
    
    print("=" * 70)
    print("✅ Análisis avanzado generado exitosamente")
    print("=" * 70)
    print(f"📄 Archivo: {archivo_reporte.name}")
    print()
    print("💡 El análisis incluye:")
    print("   - Métricas generales")
    print("   - Análisis de estructura")
    print("   - Compatibilidad")
    print("   - Placeholders más usados")
    print("   - Top plantillas")
    print("   - Distribución de tamaño")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()






