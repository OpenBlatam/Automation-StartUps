#!/usr/bin/env python3
"""
Validador Completo de Todas las Plantillas
Ejecuta todas las validaciones en todas las plantillas y genera un reporte
"""

import os
import re
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import json

def validar_estructura(contenido: str) -> Dict:
    """Valida la estructura HTML"""
    problemas = []
    advertencias = []
    
    # Verificar DOCTYPE
    if '<!DOCTYPE' not in contenido:
        problemas.append("Falta DOCTYPE")
    
    # Verificar etiquetas básicas
    if '<html' not in contenido:
        problemas.append("Falta etiqueta <html>")
    
    if '<body' not in contenido:
        problemas.append("Falta etiqueta <body>")
    
    # Verificar tablas (necesarias para email)
    num_tablas = contenido.count('<table')
    if num_tablas == 0:
        problemas.append("No se encontraron tablas (necesarias para email)")
    elif num_tablas < 3:
        advertencias.append(f"Solo {num_tablas} tabla(s) encontrada(s) (puede ser insuficiente)")
    
    # Verificar placeholders comunes
    if '[Tu Nombre]' not in contenido and '[tu-email@ejemplo.com]' not in contenido:
        advertencias.append("No se encontraron placeholders comunes")
    
    return {
        "problemas": problemas,
        "advertencias": advertencias,
        "puntuacion": max(0, 100 - len(problemas) * 20 - len(advertencias) * 5)
    }

def validar_compatibilidad(contenido: str) -> Dict:
    """Valida compatibilidad con clientes de email"""
    problemas = []
    advertencias = []
    
    # Outlook
    tiene_vml = 'xmlns:v=' in contenido
    tiene_mso = '<!--[if mso]' in contenido
    if not (tiene_vml and tiene_mso):
        advertencias.append("Falta soporte completo para Outlook (VML/MSO)")
    
    # Responsive
    tiene_media_queries = '@media' in contenido
    if not tiene_media_queries:
        advertencias.append("No se encontraron media queries (puede no ser responsive)")
    
    # Estilos inline
    tiene_estilos_inline = 'style=' in contenido
    if not tiene_estilos_inline:
        problemas.append("No se encontraron estilos inline (necesarios para email)")
    
    # Divs (no recomendados)
    num_divs = contenido.count('<div')
    if num_divs > 5:
        advertencias.append(f"Muchos divs encontrados ({num_divs}), puede causar problemas")
    
    return {
        "problemas": problemas,
        "advertencias": advertencias,
        "puntuacion": max(0, 100 - len(problemas) * 25 - len(advertencias) * 5)
    }

def validar_accesibilidad(contenido: str) -> Dict:
    """Valida accesibilidad"""
    problemas = []
    advertencias = []
    
    # ARIA labels
    num_aria = contenido.count('aria-label')
    if num_aria == 0:
        advertencias.append("No se encontraron aria-label")
    
    # Alt text en imágenes
    num_imagenes = contenido.count('<img')
    num_alt = contenido.count('alt=')
    if num_imagenes > 0 and num_alt < num_imagenes:
        problemas.append(f"Faltan {num_imagenes - num_alt} atributo(s) alt en imagen(es)")
    
    # Roles
    num_roles = contenido.count('role=')
    if num_roles == 0:
        advertencias.append("No se encontraron atributos role")
    
    return {
        "problemas": problemas,
        "advertencias": advertencias,
        "puntuacion": max(0, 100 - len(problemas) * 30 - len(advertencias) * 5)
    }

def validar_seguridad(contenido: str) -> Dict:
    """Valida seguridad"""
    problemas = []
    advertencias = []
    
    # Enlaces externos
    enlaces = re.findall(r'href\s*=\s*["\']([^"\']+)["\']', contenido, re.IGNORECASE)
    enlaces_externos = [e for e in enlaces if e.startswith('http')]
    
    for enlace in enlaces_externos:
        if 'target="_blank"' not in contenido[contenido.find(f'href="{enlace}"'):contenido.find(f'href="{enlace}")')+100]:
            advertencias.append(f"Enlace externo sin target='_blank': {enlace[:50]}")
        
        if 'rel="noopener noreferrer"' not in contenido[contenido.find(f'href="{enlace}"'):contenido.find(f'href="{enlace}")')+100]:
            advertencias.append(f"Enlace externo sin rel='noopener noreferrer': {enlace[:50]}")
    
    # JavaScript (no permitido)
    if '<script' in contenido or 'javascript:' in contenido.lower():
        problemas.append("Se encontró JavaScript (no permitido en emails)")
    
    return {
        "problemas": problemas,
        "advertencias": advertencias,
        "puntuacion": max(0, 100 - len(problemas) * 50 - len(advertencias) * 10)
    }

def validar_archivo(archivo: str) -> Dict:
    """Valida un archivo completo"""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        estructura = validar_estructura(contenido)
        compatibilidad = validar_compatibilidad(contenido)
        accesibilidad = validar_accesibilidad(contenido)
        seguridad = validar_seguridad(contenido)
        
        # Puntuación general
        puntuacion_general = (
            estructura["puntuacion"] * 0.25 +
            compatibilidad["puntuacion"] * 0.35 +
            accesibilidad["puntuacion"] * 0.20 +
            seguridad["puntuacion"] * 0.20
        )
        
        # Consolidar problemas y advertencias
        todos_problemas = estructura["problemas"] + compatibilidad["problemas"] + accesibilidad["problemas"] + seguridad["problemas"]
        todas_advertencias = estructura["advertencias"] + compatibilidad["advertencias"] + accesibilidad["advertencias"] + seguridad["advertencias"]
        
        return {
            "archivo": Path(archivo).name,
            "estructura": estructura,
            "compatibilidad": compatibilidad,
            "accesibilidad": accesibilidad,
            "seguridad": seguridad,
            "puntuacion_general": round(puntuacion_general, 1),
            "problemas_totales": len(todos_problemas),
            "advertencias_totales": len(todas_advertencias),
            "problemas": todos_problemas,
            "advertencias": todas_advertencias
        }
    
    except Exception as e:
        return {
            "archivo": Path(archivo).name,
            "error": str(e)
        }

def main():
    """Función principal"""
    print("=" * 70)
    print("✅ Validador Completo de Todas las Plantillas")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    # Buscar plantillas
    plantillas = sorted(directorio_actual.glob("firma_*.html"))
    plantillas = [str(p) for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name]
    
    if not plantillas:
        print("❌ No se encontraron plantillas")
        return
    
    print(f"📋 Validando {len(plantillas)} plantillas...")
    print()
    
    resultados = []
    for i, plantilla in enumerate(plantillas, 1):
        print(f"[{i}/{len(plantillas)}] {Path(plantilla).name}...", end=" ")
        resultado = validar_archivo(plantilla)
        resultados.append(resultado)
        
        if "error" not in resultado:
            puntuacion = resultado["puntuacion_general"]
            problemas = resultado["problemas_totales"]
            advertencias = resultado["advertencias_totales"]
            
            if problemas > 0:
                print(f"❌ {puntuacion}/100 ({problemas} problemas, {advertencias} advertencias)")
            elif advertencias > 0:
                print(f"⚠️  {puntuacion}/100 ({advertencias} advertencias)")
            else:
                print(f"✅ {puntuacion}/100")
        else:
            print(f"❌ Error: {resultado['error']}")
    
    print()
    print("=" * 70)
    print("📊 Resumen de Validación")
    print("=" * 70)
    
    exitosos = [r for r in resultados if "error" not in r]
    if exitosos:
        promedio = sum(r["puntuacion_general"] for r in exitosos) / len(exitosos)
        total_problemas = sum(r["problemas_totales"] for r in exitosos)
        total_advertencias = sum(r["advertencias_totales"] for r in exitosos)
        
        print(f"✅ Plantillas validadas: {len(exitosos)}")
        print(f"📊 Puntuación promedio: {promedio:.1f}/100")
        print(f"❌ Problemas totales: {total_problemas}")
        print(f"⚠️  Advertencias totales: {total_advertencias}")
        print()
        
        # Plantillas con problemas
        con_problemas = [r for r in exitosos if r["problemas_totales"] > 0]
        if con_problemas:
            print("⚠️  Plantillas con problemas:")
            for r in con_problemas:
                print(f"   - {r['archivo']}: {r['problemas_totales']} problema(s)")
            print()
        
        # Guardar reporte JSON
        reporte = {
            "fecha": datetime.now().isoformat(),
            "resumen": {
                "total": len(exitosos),
                "promedio": round(promedio, 1),
                "problemas_totales": total_problemas,
                "advertencias_totales": total_advertencias
            },
            "resultados": resultados
        }
        
        archivo_reporte = directorio_actual / "reporte_validacion.json"
        with open(archivo_reporte, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Reporte completo guardado en: {archivo_reporte.name}")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()






