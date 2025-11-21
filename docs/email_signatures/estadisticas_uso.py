#!/usr/bin/env python3
"""
Analizador de Estadísticas de Uso de Plantillas
Analiza qué plantillas se usan más y genera reportes
"""

import os
import json
from pathlib import Path
from collections import Counter
from typing import Dict, List
from datetime import datetime

def analizar_uso_plantillas(directorio: str) -> Dict:
    """Analiza el uso de plantillas basado en archivos personalizados"""
    estadisticas = {
        "plantillas_usadas": Counter(),
        "versiones_populares": Counter(),
        "total_personalizaciones": 0,
        "fechas_uso": [],
        "tamaños_promedio": {},
        "colores_mas_usados": Counter()
    }
    
    directorio_path = Path(directorio)
    
    # Buscar archivos personalizados
    personalizadas = list(directorio_path.glob("**/*personalizada*.html"))
    estadisticas["total_personalizaciones"] = len(personalizadas)
    
    for archivo in personalizadas:
        # Extraer nombre de plantilla base
        nombre = archivo.stem.replace("_personalizada", "")
        
        # Identificar versión
        if "compacta" in nombre:
            version = "compacta"
        elif "minimalista" in nombre:
            version = "minimalista"
        elif "simple" in nombre:
            version = "simple"
        elif "premium" in nombre:
            version = "premium"
        elif "tema" in nombre or "oscuro" in nombre or "azul" in nombre or "rojo" in nombre or "purpura" in nombre:
            version = "temática"
        elif "qr" in nombre:
            version = "qr"
        elif "calendario" in nombre:
            version = "calendario"
        elif "bilingue" in nombre:
            version = "bilingüe"
        else:
            version = "completa"
        
        # Identificar tipo
        if "curso" in nombre or "webinar" in nombre:
            tipo = "curso"
        elif "saas" in nombre or "marketing" in nombre:
            tipo = "saas"
        elif "bulk" in nombre or "documento" in nombre:
            tipo = "bulk"
        elif "consultor" in nombre:
            tipo = "consultor"
        elif "desarrollador" in nombre:
            tipo = "desarrollador"
        elif "evento" in nombre:
            tipo = "evento"
        else:
            tipo = "otro"
        
        estadisticas["plantillas_usadas"][tipo] += 1
        estadisticas["versiones_populares"][version] += 1
        
        # Tamaño del archivo
        tamaño = archivo.stat().st_size
        if tipo not in estadisticas["tamaños_promedio"]:
            estadisticas["tamaños_promedio"][tipo] = []
        estadisticas["tamaños_promedio"][tipo].append(tamaño)
        
        # Fecha de modificación
        fecha_mod = datetime.fromtimestamp(archivo.stat().st_mtime)
        estadisticas["fechas_uso"].append(fecha_mod)
        
        # Colores (básico)
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
                if "#1a73e8" in contenido or "#4285f4" in contenido:
                    estadisticas["colores_mas_usados"]["Azul"] += 1
                elif "#ea4335" in contenido or "#f44336" in contenido:
                    estadisticas["colores_mas_usados"]["Rojo"] += 1
                elif "#9c27b0" in contenido or "#7b1fa2" in contenido:
                    estadisticas["colores_mas_usados"]["Púrpura"] += 1
        except:
            pass
    
    # Calcular promedios
    for tipo, tamaños in estadisticas["tamaños_promedio"].items():
        estadisticas["tamaños_promedio"][tipo] = sum(tamaños) / len(tamaños) if tamaños else 0
    
    return estadisticas


def generar_reporte(estadisticas: Dict, archivo_salida: str):
    """Genera un reporte de estadísticas"""
    reporte = []
    reporte.append("=" * 70)
    reporte.append("📊 Reporte de Estadísticas de Uso de Plantillas")
    reporte.append("=" * 70)
    reporte.append("")
    reporte.append(f"Fecha del reporte: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    reporte.append("")
    
    # Resumen general
    reporte.append("📈 Resumen General")
    reporte.append("-" * 70)
    reporte.append(f"Total de personalizaciones: {estadisticas['total_personalizaciones']}")
    reporte.append("")
    
    # Plantillas más usadas
    reporte.append("🏆 Plantillas Más Usadas (por tipo)")
    reporte.append("-" * 70)
    for tipo, count in estadisticas["plantillas_usadas"].most_common():
        porcentaje = (count / estadisticas["total_personalizaciones"] * 100) if estadisticas["total_personalizaciones"] > 0 else 0
        reporte.append(f"  {tipo.capitalize()}: {count} ({porcentaje:.1f}%)")
    reporte.append("")
    
    # Versiones populares
    reporte.append("⭐ Versiones Más Populares")
    reporte.append("-" * 70)
    for version, count in estadisticas["versiones_populares"].most_common():
        porcentaje = (count / estadisticas["total_personalizaciones"] * 100) if estadisticas["total_personalizaciones"] > 0 else 0
        reporte.append(f"  {version.capitalize()}: {count} ({porcentaje:.1f}%)")
    reporte.append("")
    
    # Colores más usados
    if estadisticas["colores_mas_usados"]:
        reporte.append("🎨 Colores Más Usados")
        reporte.append("-" * 70)
        for color, count in estadisticas["colores_mas_usados"].most_common():
            porcentaje = (count / estadisticas["total_personalizaciones"] * 100) if estadisticas["total_personalizaciones"] > 0 else 0
            reporte.append(f"  {color}: {count} ({porcentaje:.1f}%)")
        reporte.append("")
    
    # Tamaños promedio
    if estadisticas["tamaños_promedio"]:
        reporte.append("📏 Tamaños Promedio por Tipo")
        reporte.append("-" * 70)
        for tipo, tamaño_promedio in estadisticas["tamaños_promedio"].items():
            tamaño_kb = tamaño_promedio / 1024
            reporte.append(f"  {tipo.capitalize()}: {tamaño_kb:.1f} KB")
        reporte.append("")
    
    # Actividad reciente
    if estadisticas["fechas_uso"]:
        fechas_ordenadas = sorted(estadisticas["fechas_uso"], reverse=True)
        reporte.append("📅 Actividad Reciente")
        reporte.append("-" * 70)
        reporte.append(f"  Última personalización: {fechas_ordenadas[0].strftime('%Y-%m-%d %H:%M:%S')}")
        if len(fechas_ordenadas) > 1:
            reporte.append(f"  Primera personalización: {fechas_ordenadas[-1].strftime('%Y-%m-%d %H:%M:%S')}")
        reporte.append("")
    
    reporte.append("=" * 70)
    
    # Guardar reporte
    contenido = "\n".join(reporte)
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    # Mostrar en consola
    print(contenido)
    
    return contenido


def main():
    """Función principal"""
    print("=" * 70)
    print("📊 Analizador de Estadísticas de Uso")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    # Analizar
    print("🔍 Analizando uso de plantillas...")
    estadisticas = analizar_uso_plantillas(str(directorio_actual))
    
    if estadisticas["total_personalizaciones"] == 0:
        print("\n⚠️  No se encontraron archivos personalizados")
        print("💡 Ejecuta primero los scripts de personalización")
        return
    
    # Generar reporte
    directorio_reportes = directorio_actual / "reportes"
    directorio_reportes.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_reporte = directorio_reportes / f"estadisticas_{timestamp}.txt"
    
    print()
    generar_reporte(estadisticas, str(archivo_reporte))
    
    print(f"\n💾 Reporte guardado en: {archivo_reporte}")


if __name__ == "__main__":
    main()






