#!/usr/bin/env python3
"""
Verificador de Enlaces
Verifica que todos los enlaces en las plantillas sean válidos
"""

import os
import re
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlparse

def extraer_enlaces(contenido: str) -> List[Dict]:
    """Extrae todos los enlaces del contenido"""
    enlaces = []
    
    # Buscar href="..."
    patron_href = r'href\s*=\s*["\']([^"\']+)["\']'
    matches = re.finditer(patron_href, contenido, re.IGNORECASE)
    
    for match in matches:
        url = match.group(1)
        # Omitir placeholders y enlaces especiales
        if not url.startswith('[') and not url.startswith('mailto:[') and not url.startswith('tel:['):
            enlaces.append({
                "url": url,
                "tipo": "href",
                "posicion": match.start()
            })
    
    # Buscar src="..." (para imágenes)
    patron_src = r'src\s*=\s*["\']([^"\']+)["\']'
    matches = re.finditer(patron_src, contenido, re.IGNORECASE)
    
    for match in matches:
        url = match.group(1)
        if not url.startswith('['):
            enlaces.append({
                "url": url,
                "tipo": "src",
                "posicion": match.start()
            })
    
    return enlaces

def verificar_enlace(url: str, timeout: int = 5) -> Tuple[bool, str]:
    """Verifica si un enlace es accesible"""
    # Enlaces especiales que no necesitan verificación HTTP
    if url.startswith('mailto:') or url.startswith('tel:') or url.startswith('#'):
        return True, "Enlace especial (mailto/tel/ancla)"
    
    # Verificar formato de URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            return False, "URL sin esquema (http/https)"
        
        if parsed.scheme not in ['http', 'https']:
            return True, f"Esquema especial: {parsed.scheme}"
        
        # Intentar conectar
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status = response.getcode()
                if 200 <= status < 400:
                    return True, f"OK ({status})"
                else:
                    return False, f"Error HTTP {status}"
        except urllib.error.HTTPError as e:
            return False, f"Error HTTP {e.code}"
        except urllib.error.URLError as e:
            return False, f"Error de conexión: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    except Exception as e:
        return False, f"URL inválida: {str(e)}"

def verificar_archivo(archivo: str) -> Dict:
    """Verifica todos los enlaces de un archivo"""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        enlaces = extraer_enlaces(contenido)
        
        resultados = {
            "archivo": Path(archivo).name,
            "total_enlaces": len(enlaces),
            "enlaces_validos": 0,
            "enlaces_invalidos": 0,
            "enlaces_especiales": 0,
            "detalles": []
        }
        
        for enlace in enlaces:
            url = enlace["url"]
            es_valido, mensaje = verificar_enlace(url)
            
            detalle = {
                "url": url,
                "tipo": enlace["tipo"],
                "valido": es_valido,
                "mensaje": mensaje
            }
            
            resultados["detalles"].append(detalle)
            
            if url.startswith('mailto:') or url.startswith('tel:'):
                resultados["enlaces_especiales"] += 1
            elif es_valido:
                resultados["enlaces_validos"] += 1
            else:
                resultados["enlaces_invalidos"] += 1
        
        return resultados
    
    except Exception as e:
        return {
            "archivo": Path(archivo).name,
            "error": str(e)
        }

def main():
    """Función principal"""
    print("=" * 70)
    print("🔗 Verificador de Enlaces")
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
    print("⚠️  Nota: Esto puede tardar varios minutos dependiendo del número de enlaces")
    print()
    
    todos_resultados = []
    total_validos = 0
    total_invalidos = 0
    total_especiales = 0
    
    for i, plantilla in enumerate(plantillas, 1):
        print(f"[{i}/{len(plantillas)}] Verificando {Path(plantilla).name}...", end=" ")
        
        resultado = verificar_archivo(plantilla)
        todos_resultados.append(resultado)
        
        if "error" not in resultado:
            total_validos += resultado["enlaces_validos"]
            total_invalidos += resultado["enlaces_invalidos"]
            total_especiales += resultado["enlaces_especiales"]
            
            if resultado["enlaces_invalidos"] > 0:
                print(f"❌ {resultado['enlaces_invalidos']} enlace(s) inválido(s)")
            else:
                print(f"✅ OK ({resultado['total_enlaces']} enlaces)")
        else:
            print(f"❌ Error: {resultado['error']}")
    
    print()
    print("=" * 70)
    print("📊 Resumen de Verificación")
    print("=" * 70)
    print(f"✅ Enlaces válidos: {total_validos}")
    print(f"❌ Enlaces inválidos: {total_invalidos}")
    print(f"📧 Enlaces especiales (mailto/tel): {total_especiales}")
    print()
    
    # Mostrar enlaces inválidos
    enlaces_invalidos = []
    for resultado in todos_resultados:
        if "error" not in resultado and resultado["enlaces_invalidos"] > 0:
            for detalle in resultado["detalles"]:
                if not detalle["valido"] and not detalle["url"].startswith(('mailto:', 'tel:')):
                    enlaces_invalidos.append({
                        "archivo": resultado["archivo"],
                        "url": detalle["url"],
                        "mensaje": detalle["mensaje"]
                    })
    
    if enlaces_invalidos:
        print("⚠️  Enlaces inválidos encontrados:")
        print()
        for invalido in enlaces_invalidos:
            print(f"  📄 {invalido['archivo']}")
            print(f"     URL: {invalido['url']}")
            print(f"     Error: {invalido['mensaje']}")
            print()
    
    print("=" * 70)
    print()
    print("💡 Nota: Los placeholders ([URL_...]) no se verifican")
    print("   ya que deben ser reemplazados antes de usar la plantilla.")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()






