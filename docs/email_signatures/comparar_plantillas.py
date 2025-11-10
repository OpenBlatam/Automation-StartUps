#!/usr/bin/env python3
"""
Comparador de Plantillas de Email
Compara diferentes plantillas y muestra diferencias, estadísticas y recomendaciones
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter

def analizar_plantilla(archivo: str) -> Dict:
    """Analiza una plantilla y extrae estadísticas"""
    stats = {
        'archivo': Path(archivo).name,
        'tamaño': 0,
        'lineas': 0,
        'placeholders': 0,
        'enlaces': 0,
        'imagenes': 0,
        'botones': 0,
        'tiene_vml': False,
        'tiene_mso': False,
        'tiene_media_queries': False,
        'tiene_tablas': False,
        'tiene_divs': False,
        'colores': [],
        'redes_sociales': [],
    }
    
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        stats['tamaño'] = len(contenido)
        stats['lineas'] = len(contenido.split('\n'))
        stats['placeholders'] = len(re.findall(r'\[.*?\]', contenido))
        stats['enlaces'] = len(re.findall(r'<a\s+href=', contenido, re.IGNORECASE))
        stats['imagenes'] = len(re.findall(r'<img', contenido, re.IGNORECASE))
        stats['botones'] = len(re.findall(r'background-color.*button|btn|cta', contenido, re.IGNORECASE))
        stats['tiene_vml'] = 'v:roundrect' in contenido or 'xmlns:v=' in contenido
        stats['tiene_mso'] = '<!--[if mso]' in contenido or '<!--[if !mso]' in contenido
        stats['tiene_media_queries'] = '@media' in contenido
        stats['tiene_tablas'] = '<table' in contenido
        stats['tiene_divs'] = '<div' in contenido
        
        # Extraer colores
        colores = re.findall(r'#([0-9a-fA-F]{6})', contenido)
        stats['colores'] = list(set(colores))
        
        # Extraer redes sociales
        redes = []
        if 'linkedin' in contenido.lower():
            redes.append('LinkedIn')
        if 'twitter' in contenido.lower():
            redes.append('Twitter')
        if 'youtube' in contenido.lower():
            redes.append('YouTube')
        if 'facebook' in contenido.lower():
            redes.append('Facebook')
        if 'github' in contenido.lower():
            redes.append('GitHub')
        stats['redes_sociales'] = redes
        
    except Exception as e:
        stats['error'] = str(e)
    
    return stats


def calcular_puntuacion(stats: Dict) -> Tuple[int, List[str]]:
    """Calcula una puntuación de calidad y razones"""
    puntuacion = 100
    razones = []
    
    # Puntos por características positivas
    if stats.get('tiene_tablas'):
        razones.append("✅ Usa tablas HTML")
    else:
        puntuacion -= 20
        razones.append("❌ No usa tablas HTML")
    
    if stats.get('tiene_vml') or stats.get('tiene_mso'):
        puntuacion += 10
        razones.append("✅ Soporte Outlook")
    else:
        razones.append("⚠️  Sin soporte específico Outlook")
    
    if stats.get('tiene_media_queries'):
        puntuacion += 10
        razones.append("✅ Responsive design")
    else:
        puntuacion -= 10
        razones.append("❌ Sin media queries")
    
    if not stats.get('tiene_divs'):
        puntuacion += 5
        razones.append("✅ Sin divs (mejor compatibilidad)")
    else:
        razones.append("⚠️  Usa divs")
    
    # Penalizaciones
    if stats.get('placeholders', 0) > 20:
        razones.append("⚠️  Muchos placeholders sin reemplazar")
    
    if stats.get('tamaño', 0) > 50000:
        puntuacion -= 5
        razones.append("⚠️  Archivo grande")
    
    return max(0, min(100, puntuacion)), razones


def comparar_plantillas(archivos: List[str]) -> Dict:
    """Compara múltiples plantillas"""
    resultados = []
    
    for archivo in archivos:
        stats = analizar_plantilla(archivo)
        puntuacion, razones = calcular_puntuacion(stats)
        stats['puntuacion'] = puntuacion
        stats['razones'] = razones
        resultados.append(stats)
    
    return resultados


def generar_recomendacion(stats: Dict) -> str:
    """Genera una recomendación basada en las estadísticas"""
    nombre = stats['archivo']
    
    if 'compacta' in nombre.lower():
        return "💡 Ideal para: Firmas cortas, espacio limitado, ejecutivos"
    elif 'minimalista' in nombre.lower():
        return "💡 Ideal para: Profesionales que prefieren diseño limpio, consultores"
    elif 'simple' in nombre.lower():
        return "💡 Ideal para: Máxima compatibilidad, clientes básicos"
    elif 'premium' in nombre.lower():
        return "💡 Ideal para: Instructores, educadores, mostrar credibilidad"
    elif 'qr' in nombre.lower():
        return "💡 Ideal para: Marketing, eventos, fácil acceso a información"
    elif 'calendario' in nombre.lower():
        return "💡 Ideal para: Eventos, webinars, reuniones programadas"
    elif 'bilingue' in nombre.lower():
        return "💡 Ideal para: Audiencias internacionales, empresas globales"
    elif 'oscuro' in nombre.lower() or 'dark' in nombre.lower():
        return "💡 Ideal para: Clientes con dark mode, diseño moderno"
    else:
        return "💡 Ideal para: Uso general, máxima funcionalidad"


def main():
    """Función principal"""
    print("=" * 80)
    print("📊 Comparador de Plantillas de Email")
    print("=" * 80)
    print()
    
    directorio_actual = Path(__file__).parent
    
    # Buscar todas las plantillas HTML
    plantillas = sorted(directorio_actual.glob("firma_*.html"))
    
    if len(plantillas) < 2:
        print("❌ Se necesitan al menos 2 plantillas para comparar")
        return
    
    print(f"🔍 Analizando {len(plantillas)} plantillas...\n")
    
    # Analizar todas
    resultados = comparar_plantillas([str(p) for p in plantillas])
    
    # Ordenar por puntuación
    resultados.sort(key=lambda x: x.get('puntuacion', 0), reverse=True)
    
    # Mostrar resultados
    print("=" * 80)
    print("📈 RESULTADOS DE COMPARACIÓN")
    print("=" * 80)
    print()
    
    for i, stats in enumerate(resultados, 1):
        print(f"{i}. {stats['archivo']}")
        print(f"   Puntuación: {stats.get('puntuacion', 0)}/100")
        print(f"   Tamaño: {stats.get('tamaño', 0):,} bytes")
        print(f"   Líneas: {stats.get('lineas', 0)}")
        print(f"   Enlaces: {stats.get('enlaces', 0)}")
        print(f"   Placeholders: {stats.get('placeholders', 0)}")
        print(f"   Redes sociales: {', '.join(stats.get('redes_sociales', [])) or 'Ninguna'}")
        print(f"   {generar_recomendacion(stats)}")
        print()
    
    # Estadísticas generales
    print("=" * 80)
    print("📊 ESTADÍSTICAS GENERALES")
    print("=" * 80)
    print()
    
    total_plantillas = len(resultados)
    promedio_puntuacion = sum(s.get('puntuacion', 0) for s in resultados) / total_plantillas
    total_enlaces = sum(s.get('enlaces', 0) for s in resultados)
    total_placeholders = sum(s.get('placeholders', 0) for s in resultados)
    
    print(f"Total de plantillas: {total_plantillas}")
    print(f"Puntuación promedio: {promedio_puntuacion:.1f}/100")
    print(f"Total de enlaces: {total_enlaces}")
    print(f"Total de placeholders: {total_placeholders}")
    print()
    
    # Top 3
    print("=" * 80)
    print("🏆 TOP 3 PLANTILLAS")
    print("=" * 80)
    print()
    
    for i, stats in enumerate(resultados[:3], 1):
        print(f"{i}. {stats['archivo']} ({stats.get('puntuacion', 0)}/100)")
        for razon in stats.get('razones', [])[:3]:
            print(f"   {razon}")
        print()
    
    # Recomendación final
    mejor = resultados[0]
    print("=" * 80)
    print("💡 RECOMENDACIÓN")
    print("=" * 80)
    print()
    print(f"Para la mayoría de casos, recomendamos: {mejor['archivo']}")
    print(f"Puntuación: {mejor.get('puntuacion', 0)}/100")
    print(generar_recomendacion(mejor))
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()






