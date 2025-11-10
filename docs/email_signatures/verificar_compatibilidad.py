#!/usr/bin/env python3
"""
Verificador de Compatibilidad
Verifica compatibilidad específica con diferentes clientes de email
"""

import os
import re
from pathlib import Path
from typing import Dict, List

def verificar_outlook(contenido: str) -> Dict:
    """Verifica compatibilidad con Outlook"""
    tiene_vml = 'xmlns:v=' in contenido
    tiene_mso = '<!--[if mso]' in contenido
    tiene_roundrect = 'v:roundrect' in contenido
    
    problemas = []
    advertencias = []
    
    if not tiene_vml:
        problemas.append("Falta xmlns:v (necesario para VML en Outlook)")
    if not tiene_mso:
        problemas.append("Falta comentarios condicionales MSO")
    if not tiene_roundrect and 'button' in contenido.lower():
        advertencias.append("Botones sin VML roundrect pueden no funcionar en Outlook")
    
    puntuacion = 100
    if problemas:
        puntuacion -= len(problemas) * 30
    if advertencias:
        puntuacion -= len(advertencias) * 10
    
    return {
        "compatible": len(problemas) == 0,
        "problemas": problemas,
        "advertencias": advertencias,
        "puntuacion": max(0, puntuacion)
    }

def verificar_gmail(contenido: str) -> Dict:
    """Verifica compatibilidad con Gmail"""
    tiene_tablas = '<table' in contenido
    tiene_estilos_inline = 'style=' in contenido
    tiene_media_queries = '@media' in contenido
    tiene_divs = '<div' in contenido
    
    problemas = []
    advertencias = []
    
    if not tiene_tablas:
        problemas.append("Gmail requiere tablas para estructura")
    if not tiene_estilos_inline:
        problemas.append("Gmail requiere estilos inline")
    if tiene_divs and tiene_divs > 5:
        advertencias.append("Muchos divs pueden causar problemas en Gmail")
    
    puntuacion = 100
    if problemas:
        puntuacion -= len(problemas) * 25
    if advertencias:
        puntuacion -= len(advertencias) * 5
    
    return {
        "compatible": len(problemas) == 0,
        "problemas": problemas,
        "advertencias": advertencias,
        "puntuacion": max(0, puntuacion)
    }

def verificar_apple_mail(contenido: str) -> Dict:
    """Verifica compatibilidad con Apple Mail"""
    tiene_media_queries = '@media' in contenido
    tiene_webkit = '-webkit-' in contenido
    tiene_tablas = '<table' in contenido
    
    problemas = []
    advertencias = []
    
    if not tiene_tablas:
        problemas.append("Apple Mail requiere tablas para estructura")
    if not tiene_media_queries:
        advertencias.append("Media queries mejoran experiencia en Apple Mail")
    
    puntuacion = 100
    if problemas:
        puntuacion -= len(problemas) * 30
    if advertencias:
        puntuacion -= len(advertencias) * 5
    
    return {
        "compatible": len(problemas) == 0,
        "problemas": problemas,
        "advertencias": advertencias,
        "puntuacion": max(0, puntuacion)
    }

def verificar_movil(contenido: str) -> Dict:
    """Verifica compatibilidad móvil"""
    tiene_media_queries = '@media' in contenido
    tiene_viewport = 'viewport' in contenido
    tiene_mobile_stack = 'mobile-stack' in contenido
    tiene_max_width = 'max-width' in contenido
    
    problemas = []
    advertencias = []
    
    if not tiene_media_queries:
        problemas.append("Faltan media queries para diseño responsive")
    if not tiene_viewport:
        advertencias.append("Falta meta viewport (recomendado para móvil)")
    if not tiene_mobile_stack and not tiene_max_width:
        advertencias.append("Faltan clases o estilos para apilamiento móvil")
    
    puntuacion = 100
    if problemas:
        puntuacion -= len(problemas) * 40
    if advertencias:
        puntuacion -= len(advertencias) * 10
    
    return {
        "compatible": len(problemas) == 0,
        "problemas": problemas,
        "advertencias": advertencias,
        "puntuacion": max(0, puntuacion)
    }

def verificar_archivo(archivo: str) -> Dict:
    """Verifica compatibilidad completa de un archivo"""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        outlook = verificar_outlook(contenido)
        gmail = verificar_gmail(contenido)
        apple_mail = verificar_apple_mail(contenido)
        movil = verificar_movil(contenido)
        
        # Puntuación general
        puntuacion_general = (
            outlook["puntuacion"] * 0.3 +
            gmail["puntuacion"] * 0.3 +
            apple_mail["puntuacion"] * 0.2 +
            movil["puntuacion"] * 0.2
        )
        
        return {
            "archivo": Path(archivo).name,
            "outlook": outlook,
            "gmail": gmail,
            "apple_mail": apple_mail,
            "movil": movil,
            "puntuacion_general": round(puntuacion_general, 1)
        }
    
    except Exception as e:
        return {
            "archivo": Path(archivo).name,
            "error": str(e)
        }

def main():
    """Función principal"""
    print("=" * 70)
    print("🔍 Verificador de Compatibilidad")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    # Buscar plantillas
    plantillas = sorted(directorio_actual.glob("firma_*.html"))
    plantillas = [str(p) for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name]
    
    if not plantillas:
        print("❌ No se encontraron plantillas")
        return
    
    print(f"📋 Verificando {len(plantillas)} plantillas...")
    print()
    
    resultados = []
    for i, plantilla in enumerate(plantillas, 1):
        print(f"[{i}/{len(plantillas)}] {Path(plantilla).name}...", end=" ")
        resultado = verificar_archivo(plantilla)
        resultados.append(resultado)
        
        if "error" not in resultado:
            puntuacion = resultado["puntuacion_general"]
            if puntuacion >= 90:
                print(f"✅ {puntuacion}/100")
            elif puntuacion >= 70:
                print(f"⚠️  {puntuacion}/100")
            else:
                print(f"❌ {puntuacion}/100")
        else:
            print(f"❌ Error: {resultado['error']}")
    
    print()
    print("=" * 70)
    print("📊 Resumen de Compatibilidad")
    print("=" * 70)
    
    exitosos = [r for r in resultados if "error" not in r]
    if exitosos:
        promedio = sum(r["puntuacion_general"] for r in exitosos) / len(exitosos)
        
        # Contar compatibilidad por cliente
        outlook_ok = sum(1 for r in exitosos if r["outlook"]["compatible"])
        gmail_ok = sum(1 for r in exitosos if r["gmail"]["compatible"])
        apple_ok = sum(1 for r in exitosos if r["apple_mail"]["compatible"])
        movil_ok = sum(1 for r in exitosos if r["movil"]["compatible"])
        
        print(f"✅ Plantillas verificadas: {len(exitosos)}")
        print(f"📊 Puntuación promedio: {promedio:.1f}/100")
        print()
        print("Compatibilidad por cliente:")
        print(f"  📧 Outlook: {outlook_ok}/{len(exitosos)} ({outlook_ok*100//len(exitosos)}%)")
        print(f"  📧 Gmail: {gmail_ok}/{len(exitosos)} ({gmail_ok*100//len(exitosos)}%)")
        print(f"  📧 Apple Mail: {apple_ok}/{len(exitosos)} ({apple_ok*100//len(exitosos)}%)")
        print(f"  📱 Móvil: {movil_ok}/{len(exitosos)} ({movil_ok*100//len(exitosos)}%)")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()






