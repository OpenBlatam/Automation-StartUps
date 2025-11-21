#!/usr/bin/env python3
"""
Analizador de Uso de Plantillas
Analiza el uso de placeholders, elementos y patrones en las plantillas.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Counter
from collections import defaultdict, Counter
import json
from datetime import datetime

class AnalizadorUso:
    def __init__(self, directorio: str = "."):
        self.directorio = Path(directorio)
        self.plantillas = {}
        self.analisis = {}
    
    def cargar_plantillas(self) -> None:
        """Carga todas las plantillas HTML del directorio."""
        archivos_html = list(self.directorio.glob("firma_*.html"))
        
        for archivo in archivos_html:
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    self.plantillas[archivo.name] = contenido
            except Exception as e:
                print(f"Error al cargar {archivo.name}: {e}")
    
    def analizar_placeholders(self) -> Dict:
        """Analiza todos los placeholders utilizados."""
        todos_placeholders = Counter()
        placeholders_por_plantilla = {}
        
        for nombre, contenido in self.plantillas.items():
            placeholders = re.findall(r'\[([^\]]+)\]', contenido)
            placeholders_por_plantilla[nombre] = placeholders
            todos_placeholders.update(placeholders)
        
        return {
            'total_unicos': len(todos_placeholders),
            'frecuencia': dict(todos_placeholders.most_common()),
            'por_plantilla': placeholders_por_plantilla,
            'mas_usados': dict(todos_placeholders.most_common(20))
        }
    
    def analizar_elementos_html(self) -> Dict:
        """Analiza el uso de elementos HTML."""
        elementos = Counter()
        atributos = Counter()
        
        for contenido in self.plantillas.values():
            # Elementos HTML
            tags = re.findall(r'<(\w+)', contenido, re.IGNORECASE)
            elementos.update(tags)
            
            # Atributos comunes
            hrefs = re.findall(r'href\s*=\s*["\']([^"\']+)["\']', contenido, re.IGNORECASE)
            clases = re.findall(r'class\s*=\s*["\']([^"\']+)["\']', contenido, re.IGNORECASE)
            ids = re.findall(r'id\s*=\s*["\']([^"\']+)["\']', contenido, re.IGNORECASE)
            
            atributos['href'] += len(hrefs)
            atributos['class'] += len(clases)
            atributos['id'] += len(ids)
        
        return {
            'elementos': dict(elementos.most_common()),
            'atributos': dict(atributos),
            'elementos_unicos': len(elementos)
        }
    
    def analizar_estilos(self) -> Dict:
        """Analiza el uso de estilos CSS."""
        estilos_inline = Counter()
        propiedades_css = Counter()
        colores = Counter()
        fuentes = set()
        
        for contenido in self.plantillas.values():
            # Estilos inline
            estilos = re.findall(r'style\s*=\s*["\']([^"\']+)["\']', contenido, re.IGNORECASE)
            for estilo in estilos:
                # Extraer propiedades
                props = re.findall(r'([^:]+):\s*([^;]+)', estilo)
                for prop, valor in props:
                    propiedades_css[prop.strip()] += 1
                    
                    # Extraer colores
                    if 'color' in prop.lower():
                        hex_colors = re.findall(r'#([0-9a-fA-F]{3,6})', valor, re.IGNORECASE)
                        colores.update(hex_colors)
                    
                    # Extraer fuentes
                    if 'font' in prop.lower():
                        font_families = re.findall(r'font-family\s*:\s*([^;]+)', estilo, re.IGNORECASE)
                        for ff in font_families:
                            fuentes.update([f.strip() for f in ff.split(',')])
        
        return {
            'total_estilos_inline': sum(estilos_inline.values()),
            'propiedades_mas_usadas': dict(propiedades_css.most_common(15)),
            'colores_mas_usados': dict(colores.most_common(10)),
            'fuentes_utilizadas': sorted(list(fuentes))
        }
    
    def analizar_compatibilidad(self) -> Dict:
        """Analiza características de compatibilidad con clientes de email."""
        compatibilidad = {
            'outlook': {'mso': 0, 'vml': 0, 'conditional_comments': 0},
            'gmail': {'tablas': 0, 'estilos_inline': 0},
            'apple_mail': {'media_queries': 0, 'webkit': 0},
            'responsive': {'media_queries': 0, 'mobile_stack': 0}
        }
        
        for contenido in self.plantillas.values():
            # Outlook
            if '<!--[if mso]' in contenido:
                compatibilidad['outlook']['mso'] += 1
            if 'xmlns:v=' in contenido:
                compatibilidad['outlook']['vml'] += 1
            if '<!--[if' in contenido:
                compatibilidad['outlook']['conditional_comments'] += 1
            
            # Gmail
            if '<table' in contenido:
                compatibilidad['gmail']['tablas'] += 1
            if 'style=' in contenido:
                compatibilidad['gmail']['estilos_inline'] += 1
            
            # Apple Mail
            if '@media' in contenido:
                compatibilidad['apple_mail']['media_queries'] += 1
            if '-webkit-' in contenido:
                compatibilidad['apple_mail']['webkit'] += 1
            
            # Responsive
            if '@media' in contenido:
                compatibilidad['responsive']['media_queries'] += 1
            if 'mobile-stack' in contenido or 'mobile-center' in contenido:
                compatibilidad['responsive']['mobile_stack'] += 1
        
        return compatibilidad
    
    def analizar_patrones(self) -> Dict:
        """Analiza patrones comunes en las plantillas."""
        patrones = {
            'estructura_comun': defaultdict(int),
            'ctas': Counter(),
            'enlaces_externos': 0,
            'enlaces_internos': 0
        }
        
        for contenido in self.plantillas.values():
            # CTAs (Call to Actions)
            cta_texts = re.findall(r'>\s*([^<]*Agendar[^<]*)<', contenido, re.IGNORECASE)
            cta_texts += re.findall(r'>\s*([^<]*Contactar[^<]*)<', contenido, re.IGNORECASE)
            cta_texts += re.findall(r'>\s*([^<]*Ver[^<]*)<', contenido, re.IGNORECASE)
            patrones['ctas'].update(cta_texts)
            
            # Enlaces
            enlaces = re.findall(r'href\s*=\s*["\']([^"\']+)["\']', contenido, re.IGNORECASE)
            for enlace in enlaces:
                if enlace.startswith('http://') or enlace.startswith('https://'):
                    patrones['enlaces_externos'] += 1
                elif enlace.startswith('mailto:') or enlace.startswith('tel:'):
                    patrones['enlaces_internos'] += 1
                elif not enlace.startswith('['):
                    patrones['enlaces_internos'] += 1
        
        return patrones
    
    def generar_reporte_completo(self, archivo_salida: str = "reporte_uso.json") -> None:
        """Genera un reporte completo de análisis."""
        print("🔍 Analizando plantillas...")
        
        reporte = {
            'fecha': datetime.now().isoformat(),
            'total_plantillas': len(self.plantillas),
            'placeholders': self.analizar_placeholders(),
            'elementos_html': self.analizar_elementos_html(),
            'estilos': self.analizar_estilos(),
            'compatibilidad': self.analizar_compatibilidad(),
            'patrones': self.analizar_patrones()
        }
        
        # Convertir sets a listas para JSON
        if 'fuentes_utilizadas' in reporte['estilos']:
            reporte['estilos']['fuentes_utilizadas'] = list(reporte['estilos']['fuentes_utilizadas'])
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Reporte generado: {archivo_salida}")
        self._imprimir_resumen(reporte)
    
    def _imprimir_resumen(self, reporte: Dict) -> None:
        """Imprime un resumen del análisis."""
        print("\n" + "="*60)
        print("RESUMEN DE ANÁLISIS")
        print("="*60)
        
        print(f"\n📊 Total de plantillas analizadas: {reporte['total_plantillas']}")
        
        print(f"\n📝 PLACEHOLDERS:")
        print(f"   Total únicos: {reporte['placeholders']['total_unicos']}")
        print(f"   Top 5 más usados:")
        for placeholder, count in list(reporte['placeholders']['mas_usados'].items())[:5]:
            print(f"     - {placeholder}: {count} veces")
        
        print(f"\n🏷️  ELEMENTOS HTML:")
        print(f"   Elementos únicos: {reporte['elementos_html']['elementos_unicos']}")
        print(f"   Top 5 elementos:")
        for elemento, count in list(reporte['elementos_html']['elementos'].items())[:5]:
            print(f"     - <{elemento}>: {count} veces")
        
        print(f"\n🎨 ESTILOS:")
        print(f"   Propiedades más usadas:")
        for prop, count in list(reporte['estilos']['propiedades_mas_usadas'].items())[:5]:
            print(f"     - {prop}: {count} veces")
        
        print(f"\n📧 COMPATIBILIDAD:")
        print(f"   Outlook (MSO): {reporte['compatibilidad']['outlook']['mso']} plantillas")
        print(f"   Gmail (Tablas): {reporte['compatibilidad']['gmail']['tablas']} plantillas")
        print(f"   Apple Mail (Media Queries): {reporte['compatibilidad']['apple_mail']['media_queries']} plantillas")
        print(f"   Responsive: {reporte['compatibilidad']['responsive']['media_queries']} plantillas")

def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analiza el uso de plantillas')
    parser.add_argument('-d', '--directorio', default='.', 
                       help='Directorio con las plantillas (default: actual)')
    parser.add_argument('-o', '--output', default='reporte_uso.json',
                       help='Archivo de salida (default: reporte_uso.json)')
    
    args = parser.parse_args()
    
    analizador = AnalizadorUso(args.directorio)
    analizador.cargar_plantillas()
    
    if not analizador.plantillas:
        print("❌ No se encontraron plantillas HTML en el directorio.")
        return
    
    analizador.generar_reporte_completo(args.output)

if __name__ == "__main__":
    main()





