#!/usr/bin/env python3
"""
Analizador de Rendimiento de Firmas
Analiza el rendimiento, tamaño y eficiencia de las firmas
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
import json

def analizar_tamaño(contenido: str) -> Dict:
    """Analiza el tamaño del contenido"""
    return {
        "bytes": len(contenido.encode('utf-8')),
        "caracteres": len(contenido),
        "lineas": len(contenido.split('\n')),
        "palabras": len(re.findall(r'\b\w+\b', contenido))
    }


def analizar_estructura(contenido: str) -> Dict:
    """Analiza la estructura HTML"""
    return {
        "tablas": len(re.findall(r'<table', contenido, re.IGNORECASE)),
        "enlaces": len(re.findall(r'<a\s+[^>]*href', contenido, re.IGNORECASE)),
        "imagenes": len(re.findall(r'<img', contenido, re.IGNORECASE)),
        "estilos_inline": len(re.findall(r'style\s*=', contenido, re.IGNORECASE)),
        "comentarios_mso": len(re.findall(r'<!--\[if mso\]', contenido, re.IGNORECASE))
    }


def analizar_optimizacion(contenido: str) -> Dict:
    """Analiza la optimización del código"""
    espacios_multiples = len(re.findall(r'  +', contenido))
    lineas_vacias = len(re.findall(r'\n\s*\n\s*\n', contenido))
    comentarios_html = len(re.findall(r'<!--(?!\[if mso\]|\[if !mso\]|\[endif\]).*?-->', contenido, re.DOTALL))
    
    # Calcular puntuación de optimización (0-100)
    puntuacion = 100
    if espacios_multiples > 10:
        puntuacion -= min(20, espacios_multiples // 5)
    if lineas_vacias > 5:
        puntuacion -= min(15, lineas_vacias * 2)
    if comentarios_html > 3:
        puntuacion -= min(10, comentarios_html * 2)
    
    return {
        "espacios_multiples": espacios_multiples,
        "lineas_vacias": lineas_vacias,
        "comentarios_html": comentarios_html,
        "puntuacion_optimizacion": max(0, puntuacion)
    }


def analizar_compatibilidad(contenido: str) -> Dict:
    """Analiza la compatibilidad con diferentes clientes"""
    tiene_vml = 'xmlns:v=' in contenido
    tiene_mso = '<!--[if mso]' in contenido
    tiene_media_queries = '@media' in contenido
    tiene_tablas = '<table' in contenido
    tiene_divs = '<div' in contenido
    tiene_estilos_inline = 'style=' in contenido
    
    # Calcular puntuación de compatibilidad
    puntuacion = 0
    if tiene_tablas:
        puntuacion += 30
    if tiene_estilos_inline:
        puntuacion += 25
    if tiene_vml and tiene_mso:
        puntuacion += 25  # Outlook
    if tiene_media_queries:
        puntuacion += 20  # Responsive
    
    if tiene_divs:
        puntuacion -= 10  # Divs no son ideales para email
    
    return {
        "soporte_outlook": tiene_vml and tiene_mso,
        "soporte_responsive": tiene_media_queries,
        "usa_tablas": tiene_tablas,
        "usa_divs": tiene_divs,
        "estilos_inline": tiene_estilos_inline,
        "puntuacion_compatibilidad": min(100, max(0, puntuacion))
    }


def analizar_accesibilidad(contenido: str) -> Dict:
    """Analiza la accesibilidad"""
    tiene_aria_labels = len(re.findall(r'aria-label\s*=', contenido, re.IGNORECASE))
    tiene_alt_text = len(re.findall(r'alt\s*=', contenido, re.IGNORECASE))
    tiene_role = len(re.findall(r'role\s*=', contenido, re.IGNORECASE))
    imagenes = len(re.findall(r'<img', contenido, re.IGNORECASE))
    
    # Calcular puntuación de accesibilidad
    puntuacion = 50  # Base
    puntuacion += min(30, tiene_aria_labels * 5)
    if imagenes > 0:
        if tiene_alt_text >= imagenes:
            puntuacion += 20
        else:
            puntuacion -= (imagenes - tiene_alt_text) * 10
    puntuacion += min(20, tiene_role * 3)
    
    return {
        "aria_labels": tiene_aria_labels,
        "alt_text": tiene_alt_text,
        "roles": tiene_role,
        "imagenes": imagenes,
        "puntuacion_accesibilidad": min(100, max(0, puntuacion))
    }


def analizar_archivo(archivo: str) -> Dict:
    """Analiza un archivo completo"""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        tamaño = analizar_tamaño(contenido)
        estructura = analizar_estructura(contenido)
        optimizacion = analizar_optimizacion(contenido)
        compatibilidad = analizar_compatibilidad(contenido)
        accesibilidad = analizar_accesibilidad(contenido)
        
        # Puntuación general
        puntuacion_general = (
            optimizacion["puntuacion_optimizacion"] * 0.2 +
            compatibilidad["puntuacion_compatibilidad"] * 0.4 +
            accesibilidad["puntuacion_accesibilidad"] * 0.4
        )
        
        return {
            "archivo": Path(archivo).name,
            "tamaño": tamaño,
            "estructura": estructura,
            "optimizacion": optimizacion,
            "compatibilidad": compatibilidad,
            "accesibilidad": accesibilidad,
            "puntuacion_general": round(puntuacion_general, 1)
        }
    
    except Exception as e:
        return {"archivo": Path(archivo).name, "error": str(e)}


def main():
    """Función principal"""
    print("=" * 70)
    print("📊 Analizador de Rendimiento de Firmas")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    # Buscar plantillas
    plantillas = sorted(directorio_actual.glob("firma_*.html"))
    plantillas = [str(p) for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name]
    
    if not plantillas:
        print("❌ No se encontraron plantillas")
        return
    
    print(f"📋 Analizando {len(plantillas)} plantillas...")
    print()
    
    resultados = []
    for plantilla in plantillas:
        resultado = analizar_archivo(plantilla)
        resultados.append(resultado)
        
        if "error" not in resultado:
            print(f"✅ {resultado['archivo']}")
            print(f"   Tamaño: {resultado['tamaño']['bytes']:,} bytes")
            print(f"   Puntuación: {resultado['puntuacion_general']}/100")
            print(f"   - Optimización: {resultado['optimizacion']['puntuacion_optimizacion']}/100")
            print(f"   - Compatibilidad: {resultado['compatibilidad']['puntuacion_compatibilidad']}/100")
            print(f"   - Accesibilidad: {resultado['accesibilidad']['puntuacion_accesibilidad']}/100")
        else:
            print(f"❌ {resultado['archivo']}: {resultado['error']}")
        print()
    
    # Estadísticas generales
    exitosos = [r for r in resultados if "error" not in r]
    if exitosos:
        promedio_puntuacion = sum(r["puntuacion_general"] for r in exitosos) / len(exitosos)
        promedio_tamaño = sum(r["tamaño"]["bytes"] for r in exitosos) / len(exitosos)
        mejor = max(exitosos, key=lambda x: x["puntuacion_general"])
        peor = min(exitosos, key=lambda x: x["puntuacion_general"])
        
        print("=" * 70)
        print("📊 Estadísticas Generales")
        print("=" * 70)
        print(f"✅ Plantillas analizadas: {len(exitosos)}")
        print(f"📊 Puntuación promedio: {promedio_puntuacion:.1f}/100")
        print(f"📦 Tamaño promedio: {promedio_tamaño:,.0f} bytes")
        print(f"🏆 Mejor puntuación: {mejor['archivo']} ({mejor['puntuacion_general']}/100)")
        print(f"⚠️  Menor puntuación: {peor['archivo']} ({peor['puntuacion_general']}/100)")
        print()
        
        # Guardar reporte JSON
        reporte = {
            "resumen": {
                "total": len(exitosos),
                "promedio_puntuacion": round(promedio_puntuacion, 1),
                "promedio_tamaño": round(promedio_tamaño, 0)
            },
            "resultados": resultados
        }
        
        archivo_reporte = directorio_actual / "reporte_rendimiento.json"
        with open(archivo_reporte, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Reporte completo guardado en: {archivo_reporte.name}")
        print()
        print("=" * 70)


if __name__ == "__main__":
    main()

