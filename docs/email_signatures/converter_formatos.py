#!/usr/bin/env python3
"""
Conversor de Formatos de Firmas
Convierte firmas entre diferentes formatos (HTML, Texto, Markdown, etc.)
"""

import os
import re
from pathlib import Path
from typing import Dict, Optional
from html.parser import HTMLParser

class HTMLToTextParser(HTMLParser):
    """Parser simple para convertir HTML a texto"""
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip_tags = {'script', 'style'}
        self.current_tag = None
    
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        if tag == 'br':
            self.text.append('\n')
        elif tag == 'p':
            self.text.append('\n')
    
    def handle_endtag(self, tag):
        if tag == 'p':
            self.text.append('\n')
        self.current_tag = None
    
    def handle_data(self, data):
        if self.current_tag not in self.skip_tags:
            self.text.append(data)
    
    def get_text(self):
        return ''.join(self.text).strip()


def html_a_texto(html: str) -> str:
    """Convierte HTML a texto plano"""
    parser = HTMLToTextParser()
    parser.feed(html)
    texto = parser.get_text()
    
    # Limpiar espacios múltiples
    texto = re.sub(r'\n\s*\n+', '\n\n', texto)
    texto = re.sub(r' +', ' ', texto)
    
    return texto.strip()


def html_a_markdown(html: str) -> str:
    """Convierte HTML a Markdown básico"""
    # Reemplazos básicos
    md = html
    
    # Enlaces
    md = re.sub(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>([^<]*)</a>', r'[\2](\1)', md)
    
    # Negrita
    md = re.sub(r'<strong[^>]*>([^<]*)</strong>', r'**\1**', md)
    md = re.sub(r'<b[^>]*>([^<]*)</b>', r'**\1**', md)
    
    # Énfasis
    md = re.sub(r'<em[^>]*>([^<]*)</em>', r'*\1*', md)
    md = re.sub(r'<i[^>]*>([^<]*)</i>', r'*\1*', md)
    
    # Saltos de línea
    md = re.sub(r'<br[^>]*>', '\n', md)
    md = re.sub(r'<p[^>]*>', '\n', md)
    md = re.sub(r'</p>', '\n\n', md)
    
    # Eliminar otros tags
    md = re.sub(r'<[^>]+>', '', md)
    
    # Limpiar
    md = re.sub(r'\n\s*\n+', '\n\n', md)
    md = re.sub(r' +', ' ', md)
    
    return md.strip()


def extraer_enlaces(html: str) -> Dict[str, str]:
    """Extrae todos los enlaces del HTML"""
    enlaces = {}
    patron = r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>([^<]*)</a>'
    matches = re.findall(patron, html)
    for url, texto in matches:
        enlaces[texto.strip()] = url.strip()
    return enlaces


def extraer_contacto(html: str) -> Dict[str, Optional[str]]:
    """Extrae información de contacto del HTML"""
    contacto = {
        "email": None,
        "telefono": None,
        "website": None,
        "linkedin": None,
        "twitter": None
    }
    
    # Email
    email_match = re.search(r'mailto:([^\s"\'<>]+)', html)
    if email_match:
        contacto["email"] = email_match.group(1)
    
    # Teléfono
    telefono_match = re.search(r'tel:([^\s"\'<>]+)', html)
    if telefono_match:
        contacto["telefono"] = telefono_match.group(1)
    
    # Website
    website_match = re.search(r'https?://([^\s"\'<>]+)', html)
    if website_match:
        contacto["website"] = website_match.group(0)
    
    # LinkedIn
    linkedin_match = re.search(r'linkedin\.com/[^\s"\'<>]+', html)
    if linkedin_match:
        contacto["linkedin"] = "https://" + linkedin_match.group(0)
    
    # Twitter
    twitter_match = re.search(r'twitter\.com/[^\s"\'<>]+', html)
    if twitter_match:
        contacto["twitter"] = "https://" + twitter_match.group(0)
    
    return contacto


def convertir_archivo(archivo_entrada: str, formato_salida: str, archivo_salida: Optional[str] = None) -> bool:
    """Convierte un archivo de firma a otro formato"""
    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            html = f.read()
        
        if formato_salida == 'txt':
            contenido = html_a_texto(html)
            extension = '.txt'
        elif formato_salida == 'md':
            contenido = html_a_markdown(html)
            extension = '.md'
        elif formato_salida == 'json':
            # Extraer información estructurada
            datos = {
                "html": html,
                "texto": html_a_texto(html),
                "enlaces": extraer_enlaces(html),
                "contacto": extraer_contacto(html)
            }
            import json
            contenido = json.dumps(datos, indent=2, ensure_ascii=False)
            extension = '.json'
        else:
            print(f"❌ Formato no soportado: {formato_salida}")
            return False
        
        if not archivo_salida:
            archivo_salida = Path(archivo_entrada).stem + extension
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Función principal"""
    print("=" * 70)
    print("🔄 Conversor de Formatos de Firmas")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    # Buscar plantillas
    plantillas = sorted(directorio_actual.glob("firma_*.html"))
    plantillas = [str(p) for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name]
    
    if not plantillas:
        print("❌ No se encontraron plantillas")
        return
    
    print("Formatos disponibles:")
    print("  1. TXT - Texto plano")
    print("  2. MD  - Markdown")
    print("  3. JSON - Estructurado con metadatos")
    print()
    
    try:
        formato_seleccionado = input("Formato de salida (1-3, Enter para TXT): ").strip()
        if not formato_seleccionado:
            formato_seleccionado = "1"
        
        formatos = {"1": "txt", "2": "md", "3": "json"}
        formato = formatos.get(formato_seleccionado, "txt")
        
        print()
        print(f"📋 Plantillas encontradas: {len(plantillas)}")
        print("⚡ Convirtiendo todas las plantillas...")
        print()
        
        directorio_salida = directorio_actual / "convertidas"
        directorio_salida.mkdir(exist_ok=True)
        
        exitosos = 0
        for plantilla in plantillas:
            nombre_base = Path(plantilla).stem
            archivo_salida = directorio_salida / f"{nombre_base}.{formato}"
            
            if convertir_archivo(plantilla, formato, str(archivo_salida)):
                exitosos += 1
                print(f"✅ {Path(plantilla).name} → {archivo_salida.name}")
        
        print()
        print("=" * 70)
        print("📊 Resumen")
        print("=" * 70)
        print(f"✅ Archivos convertidos: {exitosos}")
        print(f"📂 Archivos guardados en: {directorio_salida}")
        print()
        print("=" * 70)
    
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada")


if __name__ == "__main__":
    main()






