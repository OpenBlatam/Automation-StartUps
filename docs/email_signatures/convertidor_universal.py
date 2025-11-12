#!/usr/bin/env python3
"""
Convertidor Universal de Formatos
Convierte plantillas HTML entre diferentes formatos y estilos.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime

class ConvertidorUniversal:
    def __init__(self):
        self.formatos_soportados = ['html', 'txt', 'md', 'json', 'vcf']
    
    def convertir_html_a_txt(self, contenido_html: str) -> str:
        """Convierte HTML a texto plano."""
        # Remover scripts y estilos
        contenido = re.sub(r'<script[^>]*>.*?</script>', '', contenido, flags=re.DOTALL | re.IGNORECASE)
        contenido = re.sub(r'<style[^>]*>.*?</style>', '', contenido, flags=re.DOTALL | re.IGNORECASE)
        
        # Remover comentarios
        contenido = re.sub(r'<!--.*?-->', '', contenido, flags=re.DOTALL)
        
        # Extraer texto de elementos
        texto = []
        
        # Nombre
        nombre_match = re.search(r'<td[^>]*>.*?(\[.*?Nombre.*?\])', contenido, re.DOTALL | re.IGNORECASE)
        if nombre_match:
            texto.append(nombre_match.group(1).strip())
        
        # Título
        titulo_match = re.search(r'<td[^>]*>.*?(\[.*?Título.*?\])', contenido, re.DOTALL | re.IGNORECASE)
        if titulo_match:
            texto.append(titulo_match.group(1).strip())
        
        # Email
        email_match = re.search(r'mailto:(\[.*?\])', contenido, re.IGNORECASE)
        if email_match:
            texto.append(f"Email: {email_match.group(1)}")
        
        # Teléfono
        telefono_match = re.search(r'tel:(\[.*?\])', contenido, re.IGNORECASE)
        if telefono_match:
            texto.append(f"Teléfono: {telefono_match.group(1)}")
        
        # Remover HTML tags y limpiar
        texto_limpio = re.sub(r'<[^>]+>', '', contenido)
        texto_limpio = re.sub(r'\s+', ' ', texto_limpio)
        texto_limpio = re.sub(r'\[.*?\]', lambda m: m.group(0), texto_limpio)
        
        # Extraer información estructurada
        lineas = []
        for match in re.finditer(r'<td[^>]*>([^<]+)</td>', contenido, re.IGNORECASE):
            texto_td = match.group(1).strip()
            if texto_td and len(texto_td) > 2 and not texto_td.startswith('<!--'):
                lineas.append(texto_td)
        
        return '\n'.join(lineas[:10])  # Primeras 10 líneas relevantes
    
    def convertir_html_a_md(self, contenido_html: str) -> str:
        """Convierte HTML a Markdown."""
        md = []
        
        # Nombre como título
        nombre_match = re.search(r'<td[^>]*>.*?(\[.*?Nombre.*?\])', contenido, re.DOTALL | re.IGNORECASE)
        if nombre_match:
            md.append(f"# {nombre_match.group(1).strip()}\n")
        
        # Título como subtítulo
        titulo_match = re.search(r'<td[^>]*>.*?(\[.*?Título.*?\])', contenido, re.DOTALL | re.IGNORECASE)
        if titulo_match:
            md.append(f"## {titulo_match.group(1).strip()}\n")
        
        # Información de contacto
        md.append("### Contacto\n")
        
        email_match = re.search(r'mailto:(\[.*?\])', contenido, re.IGNORECASE)
        if email_match:
            md.append(f"- **Email:** {email_match.group(1)}")
        
        telefono_match = re.search(r'tel:(\[.*?\])', contenido, re.IGNORECASE)
        if telefono_match:
            md.append(f"- **Teléfono:** {telefono_match.group(1)}")
        
        return '\n'.join(md)
    
    def convertir_html_a_json(self, contenido_html: str) -> Dict:
        """Convierte HTML a JSON estructurado."""
        datos = {
            'tipo': 'firma_email',
            'formato': 'html',
            'campos': {}
        }
        
        # Extraer nombre
        nombre_match = re.search(r'<td[^>]*>.*?(\[.*?Nombre.*?\])', contenido, re.DOTALL | re.IGNORECASE)
        if nombre_match:
            datos['campos']['nombre'] = nombre_match.group(1).strip()
        
        # Extraer título
        titulo_match = re.search(r'<td[^>]*>.*?(\[.*?Título.*?\])', contenido, re.DOTALL | re.IGNORECASE)
        if titulo_match:
            datos['campos']['titulo'] = titulo_match.group(1).strip()
        
        # Extraer email
        email_match = re.search(r'mailto:(\[.*?\])', contenido, re.IGNORECASE)
        if email_match:
            datos['campos']['email'] = email_match.group(1)
        
        # Extraer teléfono
        telefono_match = re.search(r'tel:(\[.*?\])', contenido, re.IGNORECASE)
        if telefono_match:
            datos['campos']['telefono'] = telefono_match.group(1)
        
        # Extraer placeholders
        placeholders = re.findall(r'\[([^\]]+)\]', contenido)
        datos['placeholders'] = list(set(placeholders))
        
        # Extraer colores
        colores = re.findall(r'#([0-9a-fA-F]{3,6})', contenido, re.IGNORECASE)
        datos['colores'] = list(set(colores))
        
        return datos
    
    def convertir_html_a_vcf(self, contenido_html: str, nombre_archivo: str = "contacto") -> str:
        """Convierte HTML a formato vCard."""
        vcf = ["BEGIN:VCARD", "VERSION:3.0"]
        
        # Nombre
        nombre_match = re.search(r'<td[^>]*>.*?(\[.*?Nombre.*?\])', contenido, re.DOTALL | re.IGNORECASE)
        if nombre_match:
            nombre = nombre_match.group(1).strip().replace('[', '').replace(']', '')
            vcf.append(f"FN:{nombre}")
            vcf.append(f"N:{nombre};;;;")
        
        # Email
        email_match = re.search(r'mailto:(\[.*?\])', contenido, re.IGNORECASE)
        if email_match:
            email = email_match.group(1).replace('[', '').replace(']', '')
            vcf.append(f"EMAIL;TYPE=INTERNET:{email}")
        
        # Teléfono
        telefono_match = re.search(r'tel:(\[.*?\])', contenido, re.IGNORECASE)
        if telefono_match:
            telefono = telefono_match.group(1).replace('[', '').replace(']', '')
            vcf.append(f"TEL;TYPE=CELL:{telefono}")
        
        vcf.append("END:VCARD")
        return '\n'.join(vcf)
    
    def convertir_archivo(self, archivo_entrada: str, formato_salida: str, archivo_salida: Optional[str] = None) -> None:
        """Convierte un archivo a otro formato."""
        if formato_salida not in self.formatos_soportados:
            raise ValueError(f"Formato no soportado: {formato_salida}")
        
        # Leer archivo HTML
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            contenido_html = f.read()
        
        # Convertir
        if formato_salida == 'txt':
            contenido_convertido = self.convertir_html_a_txt(contenido_html)
        elif formato_salida == 'md':
            contenido_convertido = self.convertir_html_a_md(contenido_html)
        elif formato_salida == 'json':
            datos = self.convertir_html_a_json(contenido_html)
            contenido_convertido = json.dumps(datos, indent=2, ensure_ascii=False)
        elif formato_salida == 'vcf':
            contenido_convertido = self.convertir_html_a_vcf(contenido_html, Path(archivo_entrada).stem)
        else:
            raise ValueError(f"Conversión no implementada: HTML -> {formato_salida}")
        
        # Determinar archivo de salida
        if archivo_salida is None:
            archivo_salida = Path(archivo_entrada).stem + f'.{formato_salida}'
        
        # Guardar
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(contenido_convertido)
        
        print(f"✅ Convertido: {archivo_entrada} -> {archivo_salida}")
    
    def convertir_directorio(self, directorio: str, formato_salida: str) -> None:
        """Convierte todas las plantillas HTML en un directorio."""
        directorio_path = Path(directorio)
        archivos_html = list(directorio_path.glob("firma_*.html"))
        
        print(f"📁 Convirtiendo {len(archivos_html)} archivos a {formato_salida}...")
        
        for archivo in archivos_html:
            try:
                archivo_salida = archivo.parent / f"{archivo.stem}.{formato_salida}"
                self.convertir_archivo(str(archivo), formato_salida, str(archivo_salida))
            except Exception as e:
                print(f"❌ Error al convertir {archivo.name}: {e}")
        
        print(f"✅ Conversión completada: {len(archivos_html)} archivos")

def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convierte plantillas HTML entre formatos')
    parser.add_argument('archivo', nargs='?', help='Archivo a convertir (o directorio)')
    parser.add_argument('-f', '--formato', choices=['txt', 'md', 'json', 'vcf'],
                       required=True, help='Formato de salida')
    parser.add_argument('-o', '--output', help='Archivo de salida')
    parser.add_argument('-d', '--directorio', action='store_true',
                       help='Convertir todos los archivos en el directorio')
    
    args = parser.parse_args()
    
    convertidor = ConvertidorUniversal()
    
    if args.directorio or (args.archivo and Path(args.archivo).is_dir()):
        directorio = args.archivo or '.'
        convertidor.convertir_directorio(directorio, args.formato)
    elif args.archivo:
        convertidor.convertir_archivo(args.archivo, args.formato, args.output)
    else:
        print("❌ Especifica un archivo o directorio para convertir")
        print("   Uso: python convertidor_universal.py <archivo> -f <formato>")
        print("   Formatos disponibles: txt, md, json, vcf")

if __name__ == "__main__":
    main()





