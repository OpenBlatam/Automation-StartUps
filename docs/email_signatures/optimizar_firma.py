#!/usr/bin/env python3
"""
Optimizador Automático de Firmas de Email
Optimiza firmas para mejor rendimiento, tamaño y compatibilidad
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

def optimizar_html(contenido: str) -> Tuple[str, Dict]:
    """Optimiza el HTML de una firma"""
    optimizaciones = {
        "espacios_eliminados": 0,
        "comentarios_eliminados": 0,
        "atributos_redundantes": 0,
        "tamaño_original": len(contenido),
        "tamaño_optimizado": 0
    }
    
    original = contenido
    
    # Eliminar comentarios HTML (excepto condicionales MSO)
    contenido = re.sub(r'<!--(?!\[if mso\]|\[if !mso\]|\[endif\]).*?-->', '', contenido, flags=re.DOTALL)
    optimizaciones["comentarios_eliminados"] = len(re.findall(r'<!--.*?-->', original, re.DOTALL)) - len(re.findall(r'<!--.*?-->', contenido, re.DOTALL))
    
    # Eliminar espacios múltiples
    contenido_antes = contenido
    contenido = re.sub(r' +', ' ', contenido)
    contenido = re.sub(r'\n\s*\n+', '\n', contenido)
    optimizaciones["espacios_eliminados"] = len(contenido_antes) - len(contenido)
    
    # Eliminar atributos redundantes (mantener solo los necesarios)
    # Esto es más conservador para no romper compatibilidad
    
    # Eliminar líneas vacías al final
    contenido = contenido.rstrip()
    
    optimizaciones["tamaño_optimizado"] = len(contenido)
    optimizaciones["reduccion"] = optimizaciones["tamaño_original"] - optimizaciones["tamaño_optimizado"]
    optimizaciones["porcentaje_reduccion"] = (optimizaciones["reduccion"] / optimizaciones["tamaño_original"] * 100) if optimizaciones["tamaño_original"] > 0 else 0
    
    return contenido, optimizaciones


def validar_optimizacion(contenido_original: str, contenido_optimizado: str) -> bool:
    """Valida que la optimización no haya roto nada crítico"""
    # Verificar que elementos críticos sigan presentes
    elementos_criticos = [
        '<table',
        '</table>',
        '[Tu Nombre]',
        'href=',
    ]
    
    for elemento in elementos_criticos:
        if elemento in contenido_original and elemento not in contenido_optimizado:
            return False
    
    return True


def optimizar_archivo(archivo_entrada: str, archivo_salida: str) -> Tuple[bool, Dict]:
    """Optimiza un archivo de firma"""
    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            contenido_original = f.read()
        
        contenido_optimizado, optimizaciones = optimizar_html(contenido_original)
        
        # Validar
        if not validar_optimizacion(contenido_original, contenido_optimizado):
            return False, {"error": "La optimización rompió elementos críticos"}
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(archivo_salida), exist_ok=True)
        
        # Guardar
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(contenido_optimizado)
        
        return True, optimizaciones
    
    except Exception as e:
        return False, {"error": str(e)}


def main():
    """Función principal"""
    print("=" * 70)
    print("⚡ Optimizador Automático de Firmas de Email")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    # Buscar plantillas
    plantillas = sorted(directorio_actual.glob("firma_*.html"))
    plantillas = [str(p) for p in plantillas if "personalizada" not in p.name and "optimizada" not in p.name]
    
    if not plantillas:
        print("❌ No se encontraron plantillas")
        return
    
    print(f"📋 Plantillas encontradas: {len(plantillas)}")
    print()
    print("⚡ Optimizando plantillas...")
    print()
    
    directorio_salida = directorio_actual / "optimizadas"
    directorio_salida.mkdir(exist_ok=True)
    
    exitosos = 0
    fallidos = 0
    total_reduccion = 0
    total_original = 0
    
    for plantilla in plantillas:
        nombre_base = Path(plantilla).stem
        archivo_salida = directorio_salida / f"{nombre_base}_optimizada.html"
        
        success, resultado = optimizar_archivo(plantilla, str(archivo_salida))
        
        if success and "error" not in resultado:
            reduccion = resultado.get("reduccion", 0)
            porcentaje = resultado.get("porcentaje_reduccion", 0)
            print(f"✅ {Path(plantilla).name}")
            print(f"   Reducción: {reduccion:,} bytes ({porcentaje:.1f}%)")
            print(f"   Tamaño: {resultado['tamaño_original']:,} → {resultado['tamaño_optimizado']:,} bytes")
            exitosos += 1
            total_reduccion += reduccion
            total_original += resultado['tamaño_original']
        else:
            print(f"❌ {Path(plantilla).name}: {resultado.get('error', 'Error desconocido')}")
            fallidos += 1
        print()
    
    # Resumen
    print("=" * 70)
    print("📊 Resumen de Optimización")
    print("=" * 70)
    print(f"✅ Exitosos: {exitosos}")
    print(f"❌ Fallidos: {fallidos}")
    if total_original > 0:
        porcentaje_total = (total_reduccion / total_original * 100)
        print(f"📉 Reducción total: {total_reduccion:,} bytes ({porcentaje_total:.1f}%)")
    print(f"📂 Archivos guardados en: {directorio_salida}")
    print()
    print("💡 Las versiones optimizadas son más pequeñas pero mantienen")
    print("   toda la funcionalidad y compatibilidad.")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()






