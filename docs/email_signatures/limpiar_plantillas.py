#!/usr/bin/env python3
"""
Limpiador de Plantillas
Limpia y normaliza todas las plantillas (espacios, formato, etc.)
"""

import os
import re
from pathlib import Path
from typing import Dict

def limpiar_html(contenido: str) -> str:
    """Limpia el HTML manteniendo compatibilidad"""
    # Normalizar saltos de línea
    contenido = contenido.replace('\r\n', '\n').replace('\r', '\n')
    
    # Eliminar espacios múltiples (excepto en atributos)
    # Esto es conservador para no romper nada
    contenido = re.sub(r' +', ' ', contenido)
    
    # Normalizar espacios alrededor de tags
    contenido = re.sub(r'>\s+<', '><', contenido)
    contenido = re.sub(r'>\s+', '>', contenido)
    contenido = re.sub(r'\s+<', '<', contenido)
    
    # Eliminar líneas vacías múltiples (máximo 2 consecutivas)
    contenido = re.sub(r'\n\s*\n\s*\n+', '\n\n', contenido)
    
    # Eliminar espacios al inicio y final
    contenido = contenido.strip()
    
    # Asegurar nueva línea al final
    if not contenido.endswith('\n'):
        contenido += '\n'
    
    return contenido

def normalizar_encoding(archivo: str) -> bool:
    """Normaliza el encoding del archivo"""
    try:
        # Intentar leer con diferentes encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        contenido = None
        
        for encoding in encodings:
            try:
                with open(archivo, 'r', encoding=encoding) as f:
                    contenido = f.read()
                break
            except UnicodeDecodeError:
                continue
        
        if contenido is None:
            return False
        
        # Limpiar contenido
        contenido_limpiado = limpiar_html(contenido)
        
        # Guardar en UTF-8
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(contenido_limpiado)
        
        return True
    
    except Exception as e:
        print(f"Error procesando {archivo}: {e}")
        return False

def verificar_estructura(contenido: str) -> Dict:
    """Verifica la estructura básica del HTML"""
    problemas = []
    
    # Verificar DOCTYPE
    if '<!DOCTYPE' not in contenido:
        problemas.append("Falta DOCTYPE")
    
    # Verificar etiquetas básicas
    if '<html' not in contenido:
        problemas.append("Falta etiqueta <html>")
    
    if '<body' not in contenido:
        problemas.append("Falta etiqueta <body>")
    
    # Verificar tablas (necesarias para email)
    if '<table' not in contenido:
        problemas.append("No se encontraron tablas (necesarias para email)")
    
    # Verificar placeholders comunes
    if '[Tu Nombre]' not in contenido and '[tu-email@ejemplo.com]' not in contenido:
        problemas.append("No se encontraron placeholders comunes")
    
    return {
        "valido": len(problemas) == 0,
        "problemas": problemas
    }

def main():
    """Función principal"""
    print("=" * 70)
    print("🧹 Limpiador de Plantillas")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    # Buscar plantillas
    plantillas = sorted(directorio_actual.glob("firma_*.html"))
    plantillas = [str(p) for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name]
    
    if not plantillas:
        print("❌ No se encontraron plantillas")
        return
    
    print(f"📋 Plantillas encontradas: {len(plantillas)}")
    print()
    print("⚠️  Se limpiarán espacios, normalizará formato y encoding")
    print()
    
    respuesta = input("¿Continuar? (s/n): ").strip().lower()
    if respuesta != 's':
        print("❌ Operación cancelada")
        return
    
    print()
    print("🧹 Limpiando plantillas...")
    print()
    
    exitosos = 0
    fallidos = 0
    problemas_estructura = 0
    
    for plantilla in plantillas:
        nombre = Path(plantilla).name
        print(f"Procesando {nombre}...", end=" ")
        
        # Leer y verificar estructura antes
        try:
            with open(plantilla, 'r', encoding='utf-8') as f:
                contenido_antes = f.read()
            
            estructura = verificar_estructura(contenido_antes)
            
            if not estructura["valido"]:
                print(f"⚠️  Problemas de estructura: {', '.join(estructura['problemas'])}")
                problemas_estructura += 1
                continue
        except:
            pass
        
        # Limpiar
        if normalizar_encoding(plantilla):
            exitosos += 1
            print("✅ Limpiado")
        else:
            fallidos += 1
            print("❌ Error")
    
    print()
    print("=" * 70)
    print("📊 Resumen")
    print("=" * 70)
    print(f"✅ Exitosos: {exitosos}")
    print(f"❌ Fallidos: {fallidos}")
    if problemas_estructura > 0:
        print(f"⚠️  Con problemas de estructura: {problemas_estructura}")
    print()
    print("💡 Las plantillas han sido normalizadas a UTF-8 y limpiadas")
    print("=" * 70)

if __name__ == "__main__":
    main()






