#!/usr/bin/env python3
"""
Comparador de Versiones
Compara diferentes versiones de la misma plantilla (completa, compacta, minimalista, etc.)
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
from difflib import unified_diff

def extraer_nombre_base(nombre_archivo: str) -> str:
    """Extrae el nombre base de una plantilla"""
    # Remover prefijo firma_ y sufijos conocidos
    nombre = nombre_archivo.replace('firma_', '').replace('.html', '')
    
    # Remover sufijos de versión
    sufijos = ['_completa', '_compacta', '_simple', '_simplificada', '_minimalista', 
               '_premium', '_tema_oscuro', '_tema_azul', '_tema_rojo', '_tema_purpura',
               '_bilingue', '_qr', '_calendario']
    
    for sufijo in sufijos:
        if nombre.endswith(sufijo):
            nombre = nombre[:-len(sufijo)]
            break
    
    return nombre

def agrupar_por_base(archivos: List[str]) -> Dict[str, List[str]]:
    """Agrupa archivos por nombre base"""
    grupos = {}
    
    for archivo in archivos:
        nombre = Path(archivo).name
        base = extraer_nombre_base(nombre)
        
        if base not in grupos:
            grupos[base] = []
        grupos[base].append(archivo)
    
    return grupos

def detectar_version(nombre_archivo: str) -> str:
    """Detecta la versión de una plantilla"""
    nombre = nombre_archivo.lower()
    
    if 'minimalista' in nombre:
        return 'Minimalista'
    elif 'compacta' in nombre or 'compact' in nombre:
        return 'Compacta'
    elif 'simple' in nombre or 'simplificada' in nombre:
        return 'Simple'
    elif 'premium' in nombre:
        return 'Premium'
    elif 'tema_oscuro' in nombre or 'dark' in nombre:
        return 'Tema Oscuro'
    elif 'tema_azul' in nombre:
        return 'Tema Azul'
    elif 'tema_rojo' in nombre:
        return 'Tema Rojo'
    elif 'tema_purpura' in nombre or 'tema_púrpura' in nombre:
        return 'Tema Púrpura'
    elif 'bilingue' in nombre or 'bilingüe' in nombre:
        return 'Bilingüe'
    elif 'qr' in nombre:
        return 'Con QR'
    elif 'calendario' in nombre or 'calendar' in nombre:
        return 'Con Calendario'
    else:
        return 'Completa'

def comparar_archivos(archivo1: str, archivo2: str) -> Dict:
    """Compara dos archivos"""
    try:
        with open(archivo1, 'r', encoding='utf-8') as f:
            contenido1 = f.read()
        
        with open(archivo2, 'r', encoding='utf-8') as f:
            contenido2 = f.read()
        
        # Estadísticas básicas
        tamaño1 = len(contenido1)
        tamaño2 = len(contenido2)
        lineas1 = len(contenido1.split('\n'))
        lineas2 = len(contenido2.split('\n'))
        
        # Diferencias
        diferencias = list(unified_diff(
            contenido1.splitlines(keepends=True),
            contenido2.splitlines(keepends=True),
            fromfile=Path(archivo1).name,
            tofile=Path(archivo2).name,
            lineterm=''
        ))
        
        return {
            "archivo1": Path(archivo1).name,
            "archivo2": Path(archivo2).name,
            "tamaño1": tamaño1,
            "tamaño2": tamaño2,
            "diferencia_tamaño": tamaño2 - tamaño1,
            "lineas1": lineas1,
            "lineas2": lineas2,
            "diferencia_lineas": lineas2 - lineas1,
            "diferencias": diferencias,
            "num_diferencias": len([d for d in diferencias if d.startswith(('+', '-')) and not d.startswith('+++') and not d.startswith('---')])
        }
    
    except Exception as e:
        return {"error": str(e)}

def main():
    """Función principal"""
    print("=" * 70)
    print("🔍 Comparador de Versiones")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    # Buscar plantillas
    plantillas = sorted(directorio_actual.glob("firma_*.html"))
    plantillas = [str(p) for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name]
    
    if not plantillas:
        print("❌ No se encontraron plantillas")
        return
    
    # Agrupar por base
    grupos = agrupar_por_base(plantillas)
    
    # Filtrar grupos con múltiples versiones
    grupos_multiples = {k: v for k, v in grupos.items() if len(v) > 1}
    
    if not grupos_multiples:
        print("❌ No se encontraron plantillas con múltiples versiones")
        return
    
    print(f"📋 Grupos con múltiples versiones: {len(grupos_multiples)}")
    print()
    
    for base, archivos in sorted(grupos_multiples.items()):
        print(f"📦 {base.upper()}")
        print(f"   Versiones encontradas: {len(archivos)}")
        
        # Detectar versiones
        versiones = {}
        for archivo in archivos:
            version = detectar_version(Path(archivo).name)
            versiones[archivo] = version
            print(f"   - {Path(archivo).name} ({version})")
        
        # Comparar con la primera versión
        if len(archivos) > 1:
            archivo_base = archivos[0]
            print()
            print(f"   Comparando con {Path(archivo_base).name}:")
            
            for archivo in archivos[1:]:
                comparacion = comparar_archivos(archivo_base, archivo)
                
                if "error" not in comparacion:
                    diff_tam = comparacion["diferencia_tamaño"]
                    diff_lin = comparacion["diferencia_lineas"]
                    num_diff = comparacion["num_diferencias"]
                    
                    print(f"   vs {Path(archivo).name}:")
                    print(f"      Tamaño: {comparacion['tamaño1']:,} → {comparacion['tamaño2']:,} bytes ({diff_tam:+,} bytes)")
                    print(f"      Líneas: {comparacion['lineas1']} → {comparacion['lineas2']} ({diff_lin:+,})")
                    print(f"      Diferencias: {num_diff} líneas")
        
        print()
    
    print("=" * 70)
    print("💡 Usa herramientas de diff para ver diferencias detalladas")
    print("=" * 70)

if __name__ == "__main__":
    main()






