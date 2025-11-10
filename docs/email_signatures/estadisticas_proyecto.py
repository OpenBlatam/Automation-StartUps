#!/usr/bin/env python3
"""
Estadísticas del Proyecto
Genera un reporte completo de estadísticas del proyecto
"""

import os
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import json

def obtener_estadisticas_archivo(archivo: Path) -> Dict:
    """Obtiene estadísticas de un archivo"""
    try:
        stat = archivo.stat()
        tamaño = stat.st_size
        
        # Leer contenido si es texto
        if archivo.suffix in ['.html', '.py', '.md', '.txt', '.json', '.vcf']:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
                lineas = len(contenido.split('\n'))
                caracteres = len(contenido)
        else:
            lineas = 0
            caracteres = 0
        
        return {
            "nombre": archivo.name,
            "tamaño": tamaño,
            "lineas": lineas,
            "caracteres": caracteres,
            "extension": archivo.suffix,
            "modificado": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    except:
        return {
            "nombre": archivo.name,
            "error": "No se pudo leer"
        }

def categorizar_archivos(archivos: List[Path]) -> Dict:
    """Categoriza archivos por tipo"""
    categorias = {
        "plantillas_html": [],
        "scripts_python": [],
        "documentacion": [],
        "herramientas_html": [],
        "otros": []
    }
    
    for archivo in archivos:
        nombre = archivo.name.lower()
        
        if nombre.startswith('firma_') and archivo.suffix == '.html':
            categorias["plantillas_html"].append(archivo)
        elif archivo.suffix == '.py':
            categorias["scripts_python"].append(archivo)
        elif archivo.suffix == '.md':
            categorias["documentacion"].append(archivo)
        elif archivo.suffix == '.html' and 'generador' in nombre or 'test' in nombre or 'preview' in nombre:
            categorias["herramientas_html"].append(archivo)
        else:
            categorias["otros"].append(archivo)
    
    return categorias

def generar_reporte(categorias: Dict, estadisticas: Dict) -> str:
    """Genera un reporte en texto"""
    reporte = "=" * 70 + "\n"
    reporte += "📊 ESTADÍSTICAS DEL PROYECTO - FIRMAS DE EMAIL\n"
    reporte += "=" * 70 + "\n\n"
    
    reporte += f"📅 Fecha del reporte: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    reporte += "=" * 70 + "\n"
    reporte += "📈 RESUMEN GENERAL\n"
    reporte += "=" * 70 + "\n\n"
    
    reporte += f"📁 Total de archivos: {estadisticas['total_archivos']}\n"
    reporte += f"📦 Tamaño total: {estadisticas['tamaño_total']:,} bytes ({estadisticas['tamaño_total'] / 1024:.1f} KB)\n"
    reporte += f"📄 Total de líneas: {estadisticas['total_lineas']:,}\n"
    reporte += f"🔤 Total de caracteres: {estadisticas['total_caracteres']:,}\n\n"
    
    reporte += "=" * 70 + "\n"
    reporte += "📋 DESGLOSE POR CATEGORÍA\n"
    reporte += "=" * 70 + "\n\n"
    
    for categoria, archivos in categorias.items():
        if archivos:
            nombre_categoria = categoria.replace('_', ' ').title()
            total_tamaño = sum(f.stat().st_size for f in archivos)
            total_lineas = sum(len(open(f, 'r', encoding='utf-8').read().split('\n')) for f in archivos if f.suffix in ['.html', '.py', '.md', '.txt'])
            
            reporte += f"📂 {nombre_categoria}:\n"
            reporte += f"   Archivos: {len(archivos)}\n"
            reporte += f"   Tamaño: {total_tamaño:,} bytes ({total_tamaño / 1024:.1f} KB)\n"
            reporte += f"   Líneas: {total_lineas:,}\n"
            reporte += "\n"
    
    reporte += "=" * 70 + "\n"
    reporte += "🏆 TOP 10 ARCHIVOS MÁS GRANDES\n"
    reporte += "=" * 70 + "\n\n"
    
    for i, archivo in enumerate(estadisticas['top_archivos'], 1):
        reporte += f"{i:2d}. {archivo['nombre']:<50} {archivo['tamaño']:>10,} bytes\n"
    
    reporte += "\n"
    reporte += "=" * 70 + "\n"
    reporte += "📊 DISTRIBUCIÓN POR EXTENSIÓN\n"
    reporte += "=" * 70 + "\n\n"
    
    for extension, count in sorted(estadisticas['por_extension'].items(), key=lambda x: x[1], reverse=True):
        if extension:
            reporte += f"   {extension:<10} {count:>3} archivo(s)\n"
    
    reporte += "\n"
    reporte += "=" * 70 + "\n"
    
    return reporte

def main():
    """Función principal"""
    directorio_actual = Path(__file__).parent
    
    # Obtener todos los archivos
    todos_archivos = [f for f in directorio_actual.iterdir() if f.is_file()]
    
    # Categorizar
    categorias = categorizar_archivos(todos_archivos)
    
    # Obtener estadísticas
    estadisticas_archivos = []
    for archivo in todos_archivos:
        stats = obtener_estadisticas_archivo(archivo)
        estadisticas_archivos.append(stats)
    
    # Calcular estadísticas generales
    tamaño_total = sum(s.get('tamaño', 0) for s in estadisticas_archivos)
    total_lineas = sum(s.get('lineas', 0) for s in estadisticas_archivos)
    total_caracteres = sum(s.get('caracteres', 0) for s in estadisticas_archivos)
    
    # Top archivos
    top_archivos = sorted(
        [s for s in estadisticas_archivos if 'tamaño' in s],
        key=lambda x: x['tamaño'],
        reverse=True
    )[:10]
    
    # Por extensión
    por_extension = {}
    for stats in estadisticas_archivos:
        ext = stats.get('extension', '')
        por_extension[ext] = por_extension.get(ext, 0) + 1
    
    estadisticas = {
        "total_archivos": len(todos_archivos),
        "tamaño_total": tamaño_total,
        "total_lineas": total_lineas,
        "total_caracteres": total_caracteres,
        "top_archivos": top_archivos,
        "por_extension": por_extension
    }
    
    # Generar reporte
    reporte_texto = generar_reporte(categorias, estadisticas)
    
    # Guardar reporte
    archivo_reporte = directorio_actual / "ESTADISTICAS_PROYECTO.txt"
    with open(archivo_reporte, 'w', encoding='utf-8') as f:
        f.write(reporte_texto)
    
    # Guardar JSON
    reporte_json = {
        "fecha": datetime.now().isoformat(),
        "estadisticas": estadisticas,
        "categorias": {
            k: [f.name for f in v] for k, v in categorias.items()
        }
    }
    
    archivo_json = directorio_actual / "ESTADISTICAS_PROYECTO.json"
    with open(archivo_json, 'w', encoding='utf-8') as f:
        json.dump(reporte_json, f, indent=2, ensure_ascii=False)
    
    # Mostrar en consola
    print(reporte_texto)
    print(f"📄 Reporte guardado en: {archivo_reporte.name}")
    print(f"📄 JSON guardado en: {archivo_json.name}")

if __name__ == "__main__":
    main()






