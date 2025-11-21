#!/usr/bin/env python3
"""
Validador de Firmas de Email
Verifica que las firmas cumplan con mejores prácticas y estándares
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Tuple
from html.parser import HTMLParser

class EmailSignatureValidator(HTMLParser):
    """Parser HTML para validar firmas de email"""
    
    def __init__(self):
        super().__init__()
        self.errors = []
        self.warnings = []
        self.info = []
        self.has_tables = False
        self.has_divs = False
        self.has_inline_styles = False
        self.has_external_css = False
        self.has_scripts = False
        self.links = []
        self.images = []
        self.has_vml = False
        self.has_mso = False
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == 'table':
            self.has_tables = True
        elif tag == 'div':
            self.has_divs = True
        elif tag == 'script':
            self.has_scripts = True
            self.errors.append("❌ Se encontró JavaScript (no compatible con emails)")
        elif tag == 'link' and attrs_dict.get('rel') == 'stylesheet':
            self.has_external_css = True
            self.errors.append("❌ CSS externo detectado (no compatible con emails)")
        elif tag == 'a':
            href = attrs_dict.get('href', '')
            if href:
                self.links.append({
                    'href': href,
                    'target': attrs_dict.get('target'),
                    'rel': attrs_dict.get('rel', '')
                })
        elif tag == 'img':
            self.images.append({
                'src': attrs_dict.get('src', ''),
                'alt': attrs_dict.get('alt', '')
            })
        elif tag.startswith('v:'):
            self.has_vml = True
        elif 'style' in attrs_dict:
            self.has_inline_styles = True
            
    def handle_comment(self, data):
        if 'mso' in data.lower() or 'if mso' in data.lower():
            self.has_mso = True


def validar_email(email: str) -> Tuple[bool, str]:
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, "✅ Email válido"
    return False, "❌ Email inválido"


def validar_url(url: str) -> Tuple[bool, str]:
    """Valida formato de URL"""
    if not url:
        return False, "⚠️  URL vacía"
    
    if url.startswith('http://') or url.startswith('https://') or url.startswith('mailto:') or url.startswith('tel:'):
        return True, "✅ URL válida"
    return False, "❌ URL debe comenzar con http://, https://, mailto: o tel:"


def validar_archivo(archivo: str) -> Dict:
    """Valida un archivo de firma de email"""
    resultado = {
        'archivo': archivo,
        'valido': True,
        'errores': [],
        'advertencias': [],
        'info': [],
        'puntuacion': 100
    }
    
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Validar estructura HTML
        parser = EmailSignatureValidator()
        parser.feed(contenido)
        
        # Verificar uso de tablas
        if not parser.has_tables:
            resultado['errores'].append("❌ No se encontraron tablas HTML (requerido para emails)")
            resultado['puntuacion'] -= 20
        
        # Verificar divs complejos
        if parser.has_divs:
            resultado['advertencias'].append("⚠️  Se encontraron divs (mejor usar solo tablas)")
            resultado['puntuacion'] -= 5
        
        # Verificar estilos inline
        if not parser.has_inline_styles:
            resultado['advertencias'].append("⚠️  Pocos estilos inline (algunos clientes requieren estilos inline)")
            resultado['puntuacion'] -= 5
        
        # Verificar JavaScript
        if parser.has_scripts:
            resultado['valido'] = False
            resultado['puntuacion'] -= 30
        
        # Verificar CSS externo
        if parser.has_external_css:
            resultado['valido'] = False
            resultado['puntuacion'] -= 30
        
        # Validar enlaces
        for link in parser.links:
            href = link['href']
            if href.startswith('http') and not link.get('target') == '_blank':
                resultado['advertencias'].append(f"⚠️  Enlace externo sin target='_blank': {href[:50]}")
                resultado['puntuacion'] -= 2
            
            if href.startswith('http') and 'noopener' not in link.get('rel', ''):
                resultado['advertencias'].append(f"⚠️  Enlace externo sin rel='noopener': {href[:50]}")
                resultado['puntuacion'] -= 2
            
            valid, msg = validar_url(href)
            if not valid:
                resultado['errores'].append(f"❌ {msg}: {href[:50]}")
                resultado['puntuacion'] -= 5
        
        # Validar imágenes
        for img in parser.images:
            if not img.get('alt'):
                resultado['advertencias'].append("⚠️  Imagen sin atributo alt (accesibilidad)")
                resultado['puntuacion'] -= 2
            
            src = img.get('src', '')
            if src and not (src.startswith('http://') or src.startswith('https://')):
                resultado['errores'].append(f"❌ Imagen con URL relativa (usar URL absoluta): {src[:50]}")
                resultado['puntuacion'] -= 5
        
        # Verificar soporte Outlook
        if parser.has_vml or parser.has_mso:
            resultado['info'].append("✅ Soporte Outlook detectado (VML/MSO)")
        else:
            resultado['advertencias'].append("⚠️  No se detectó soporte específico para Outlook")
            resultado['puntuacion'] -= 10
        
        # Verificar placeholders
        placeholders = re.findall(r'\[.*?\]', contenido)
        if placeholders:
            resultado['advertencias'].append(f"⚠️  Se encontraron {len(placeholders)} placeholders sin reemplazar")
            resultado['puntuacion'] -= len(placeholders) * 2
        
        # Verificar max-width
        if 'max-width' not in contenido.lower():
            resultado['advertencias'].append("⚠️  No se encontró max-width (importante para responsive)")
            resultado['puntuacion'] -= 5
        
        # Verificar media queries
        if '@media' not in contenido:
            resultado['advertencias'].append("⚠️  No se encontraron media queries (responsive)")
            resultado['puntuacion'] -= 5
        
        # Asegurar puntuación mínima
        resultado['puntuacion'] = max(0, resultado['puntuacion'])
        
        if resultado['errores']:
            resultado['valido'] = False
        
    except Exception as e:
        resultado['valido'] = False
        resultado['errores'].append(f"❌ Error al procesar archivo: {str(e)}")
        resultado['puntuacion'] = 0
    
    return resultado


def main():
    """Función principal"""
    print("=" * 70)
    print("🔍 Validador de Firmas de Email")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    # Buscar archivos HTML de firmas
    archivos = list(directorio_actual.glob("firma_*.html"))
    
    if not archivos:
        print("❌ No se encontraron archivos de firma")
        return
    
    print(f"📋 Archivos encontrados: {len(archivos)}\n")
    
    resultados = []
    total_puntuacion = 0
    
    for archivo in sorted(archivos):
        print(f"🔍 Validando: {archivo.name}")
        resultado = validar_archivo(str(archivo))
        resultados.append(resultado)
        total_puntuacion += resultado['puntuacion']
        
        # Mostrar resultados
        if resultado['valido']:
            print(f"   ✅ Válido (Puntuación: {resultado['puntuacion']}/100)")
        else:
            print(f"   ❌ Inválido (Puntuación: {resultado['puntuacion']}/100)")
        
        if resultado['errores']:
            for error in resultado['errores']:
                print(f"      {error}")
        
        if resultado['advertencias']:
            for warning in resultado['advertencias'][:3]:  # Mostrar solo las primeras 3
                print(f"      {warning}")
            if len(resultado['advertencias']) > 3:
                print(f"      ... y {len(resultado['advertencias']) - 3} advertencias más")
        
        if resultado['info']:
            for info in resultado['info']:
                print(f"      {info}")
        
        print()
    
    # Resumen
    print("=" * 70)
    print("📊 Resumen")
    print("=" * 70)
    
    validos = sum(1 for r in resultados if r['valido'])
    promedio = total_puntuacion / len(resultados) if resultados else 0
    
    print(f"✅ Archivos válidos: {validos}/{len(resultados)}")
    print(f"📈 Puntuación promedio: {promedio:.1f}/100")
    print()
    
    # Top 3 mejores
    mejores = sorted(resultados, key=lambda x: x['puntuacion'], reverse=True)[:3]
    print("🏆 Top 3 mejores firmas:")
    for i, resultado in enumerate(mejores, 1):
        print(f"   {i}. {Path(resultado['archivo']).name} ({resultado['puntuacion']}/100)")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()






