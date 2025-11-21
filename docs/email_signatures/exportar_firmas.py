#!/usr/bin/env python3
"""
Exportador de Firmas de Email
Exporta firmas a diferentes formatos y prepara para diferentes usos
"""

import os
import json
import base64
from pathlib import Path
from typing import Dict, List
import re

def exportar_a_texto(archivo_html: str, archivo_salida: str) -> bool:
    """Exporta una firma HTML a texto plano"""
    try:
        with open(archivo_html, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Remover tags HTML
        texto = re.sub(r'<[^>]+>', '', contenido)
        
        # Limpiar espacios múltiples
        texto = re.sub(r'\s+', ' ', texto)
        texto = re.sub(r'\n\s*\n', '\n\n', texto)
        
        # Remover placeholders de comentarios
        texto = re.sub(r'<!--.*?-->', '', texto, flags=re.DOTALL)
        
        # Limpiar
        lineas = [linea.strip() for linea in texto.split('\n') if linea.strip()]
        texto_final = '\n'.join(lineas)
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(texto_final)
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def exportar_a_json(archivo_html: str, archivo_salida: str) -> Dict:
    """Extrae información de una firma y la exporta a JSON"""
    try:
        with open(archivo_html, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Extraer información
        info = {
            "archivo": Path(archivo_html).name,
            "placeholders": [],
            "enlaces": [],
            "colores": [],
            "redes_sociales": []
        }
        
        # Placeholders
        placeholders = re.findall(r'\[.*?\]', contenido)
        info["placeholders"] = list(set(placeholders))
        
        # Enlaces
        enlaces = re.findall(r'href=["\']([^"\']+)["\']', contenido)
        info["enlaces"] = list(set(enlaces))
        
        # Colores
        colores = re.findall(r'#([0-9a-fA-F]{6})', contenido)
        info["colores"] = list(set(colores))
        
        # Redes sociales
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
        info["redes_sociales"] = redes
        
        # Guardar JSON
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        
        return info
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}


def exportar_a_base64(archivo_html: str, archivo_salida: str) -> bool:
    """Exporta HTML codificado en Base64 (útil para algunos clientes)"""
    try:
        with open(archivo_html, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Codificar a base64
        contenido_bytes = contenido.encode('utf-8')
        base64_encoded = base64.b64encode(contenido_bytes).decode('utf-8')
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(base64_encoded)
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def crear_paquete_completo(archivo_html: str, directorio_salida: str) -> bool:
    """Crea un paquete completo con todas las exportaciones"""
    try:
        nombre_base = Path(archivo_html).stem
        directorio_paquete = Path(directorio_salida) / nombre_base
        directorio_paquete.mkdir(parents=True, exist_ok=True)
        
        # Copiar HTML original
        import shutil
        shutil.copy(archivo_html, directorio_paquete / f"{nombre_base}.html")
        
        # Exportar a texto
        exportar_a_texto(archivo_html, str(directorio_paquete / f"{nombre_base}.txt"))
        
        # Exportar a JSON
        exportar_a_json(archivo_html, str(directorio_paquete / f"{nombre_base}.json"))
        
        # Exportar a Base64
        exportar_a_base64(archivo_html, str(directorio_paquete / f"{nombre_base}.base64.txt"))
        
        # Crear README del paquete
        readme = f"""# Paquete de Exportación - {nombre_base}

Este paquete contiene la firma de email en múltiples formatos:

- `{nombre_base}.html` - Versión HTML original
- `{nombre_base}.txt` - Versión texto plano
- `{nombre_base}.json` - Metadatos en JSON
- `{nombre_base}.base64.txt` - HTML codificado en Base64

## Uso

### HTML
Copia el contenido de `{nombre_base}.html` y pégalo en tu cliente de email.

### Texto Plano
Úsalo como fallback o para clientes que no soportan HTML.

### JSON
Contiene información estructurada sobre la firma (placeholders, enlaces, colores).

### Base64
Algunos sistemas requieren el HTML codificado en Base64.

---
Generado automáticamente por exportar_firmas.py
"""
        
        with open(directorio_paquete / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme)
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Función principal"""
    print("=" * 70)
    print("📦 Exportador de Firmas de Email")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    # Buscar plantillas
    plantillas = sorted(directorio_actual.glob("firma_*.html"))
    plantillas = [str(p) for p in plantillas if "personalizada" not in p.name]
    
    if not plantillas:
        print("❌ No se encontraron plantillas")
        return
    
    print(f"📋 Plantillas encontradas: {len(plantillas)}")
    print()
    print("Formatos de exportación disponibles:")
    print("  1. Texto plano (.txt)")
    print("  2. JSON con metadatos (.json)")
    print("  3. Base64 (.base64.txt)")
    print("  4. Paquete completo (todos los formatos)")
    print()
    
    try:
        opcion = input("Selecciona formato (1-4) o 'todos' para todas las plantillas: ").strip().lower()
    except KeyboardInterrupt:
        print("\n❌ Cancelado")
        return
    
    directorio_salida = directorio_actual / "exportadas"
    directorio_salida.mkdir(exist_ok=True)
    
    exitosos = 0
    fallidos = 0
    
    plantillas_a_procesar = plantillas if opcion == 'todos' else [plantillas[0]] if plantillas else []
    
    if opcion == 'todos':
        plantillas_a_procesar = plantillas
    
    print(f"\n🔄 Procesando {len(plantillas_a_procesar)} plantilla(s)...\n")
    
    for plantilla in plantillas_a_procesar:
        nombre_base = Path(plantilla).stem
        
        if opcion == '1' or opcion == 'todos':
            archivo_salida = directorio_salida / f"{nombre_base}.txt"
            if exportar_a_texto(plantilla, str(archivo_salida)):
                print(f"✅ Texto: {archivo_salida.name}")
                exitosos += 1
            else:
                fallidos += 1
        
        if opcion == '2' or opcion == 'todos':
            archivo_salida = directorio_salida / f"{nombre_base}.json"
            if exportar_a_json(plantilla, str(archivo_salida)):
                print(f"✅ JSON: {archivo_salida.name}")
                exitosos += 1
            else:
                fallidos += 1
        
        if opcion == '3' or opcion == 'todos':
            archivo_salida = directorio_salida / f"{nombre_base}.base64.txt"
            if exportar_a_base64(plantilla, str(archivo_salida)):
                print(f"✅ Base64: {archivo_salida.name}")
                exitosos += 1
            else:
                fallidos += 1
        
        if opcion == '4':
            if crear_paquete_completo(plantilla, str(directorio_salida)):
                print(f"✅ Paquete completo: {nombre_base}/")
                exitosos += 1
            else:
                fallidos += 1
    
    # Resumen
    print()
    print("=" * 70)
    print("📊 Resumen")
    print("=" * 70)
    print(f"✅ Exitosos: {exitosos}")
    print(f"❌ Fallidos: {fallidos}")
    print(f"📂 Archivos guardados en: {directorio_salida}")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()






