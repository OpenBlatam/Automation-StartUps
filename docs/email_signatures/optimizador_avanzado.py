#!/usr/bin/env python3
"""
Optimizador Avanzado de Plantillas
Optimiza plantillas HTML para mejor rendimiento, compatibilidad y tamaño.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
import json
from datetime import datetime

class OptimizadorAvanzado:
    def __init__(self):
        self.optimizaciones_aplicadas = []
    
    def optimizar_plantilla(self, contenido: str, opciones: Dict = None) -> Tuple[str, Dict]:
        """Optimiza una plantilla HTML."""
        if opciones is None:
            opciones = {
                'minificar': True,
                'remover_comentarios': False,
                'optimizar_estilos': True,
                'optimizar_estructura': True,
                'validar_compatibilidad': True
            }
        
        original = contenido
        optimizado = contenido
        metricas = {
            'tamaño_original': len(original),
            'tamaño_optimizado': 0,
            'reduccion': 0,
            'optimizaciones': []
        }
        
        # Remover comentarios (excepto condicionales MSO)
        if opciones.get('remover_comentarios', False):
            optimizado = self._remover_comentarios_seguros(optimizado)
            metricas['optimizaciones'].append('Comentarios removidos (excepto MSO)')
        
        # Optimizar estilos inline
        if opciones.get('optimizar_estilos', True):
            optimizado = self._optimizar_estilos(optimizado)
            metricas['optimizaciones'].append('Estilos optimizados')
        
        # Optimizar estructura
        if opciones.get('optimizar_estructura', True):
            optimizado = self._optimizar_estructura(optimizado)
            metricas['optimizaciones'].append('Estructura optimizada')
        
        # Minificar
        if opciones.get('minificar', True):
            optimizado = self._minificar(optimizado)
            metricas['optimizaciones'].append('Código minificado')
        
        # Validar compatibilidad
        if opciones.get('validar_compatibilidad', True):
            problemas = self._validar_compatibilidad(optimizado)
            if problemas:
                metricas['problemas_compatibilidad'] = problemas
            else:
                metricas['optimizaciones'].append('Compatibilidad validada')
        
        metricas['tamaño_optimizado'] = len(optimizado)
        metricas['reduccion'] = metricas['tamaño_original'] - metricas['tamaño_optimizado']
        metricas['porcentaje_reduccion'] = round((metricas['reduccion'] / metricas['tamaño_original']) * 100, 2) if metricas['tamaño_original'] > 0 else 0
        
        return optimizado, metricas
    
    def _remover_comentarios_seguros(self, contenido: str) -> str:
        """Remueve comentarios HTML excepto los condicionales MSO."""
        # Preservar comentarios condicionales MSO
        contenido = re.sub(r'<!--(?!\[if mso\]|\[if !mso\]|\[endif\])[^>]*-->', '', contenido)
        return contenido
    
    def _optimizar_estilos(self, contenido: str) -> str:
        """Optimiza estilos inline."""
        # Remover espacios extra en estilos
        def optimizar_estilo(match):
            estilo = match.group(1)
            # Remover espacios extra
            estilo = re.sub(r'\s+', ' ', estilo)
            # Remover espacios antes de :
            estilo = re.sub(r'\s*:\s*', ':', estilo)
            # Remover espacios después de ;
            estilo = re.sub(r';\s*', ';', estilo)
            return f'style="{estilo.strip()}"'
        
        contenido = re.sub(r'style\s*=\s*["\']([^"\']+)["\']', optimizar_estilo, contenido, flags=re.IGNORECASE)
        return contenido
    
    def _optimizar_estructura(self, contenido: str) -> str:
        """Optimiza la estructura HTML."""
        # Remover espacios entre tags
        contenido = re.sub(r'>\s+<', '><', contenido)
        # Remover espacios al inicio y final de líneas (pero preservar estructura básica)
        lineas = contenido.split('\n')
        lineas_optimizadas = []
        for linea in lineas:
            linea = linea.strip()
            if linea:
                lineas_optimizadas.append(linea)
        return '\n'.join(lineas_optimizadas)
    
    def _minificar(self, contenido: str) -> str:
        """Minifica el código HTML."""
        # Ya optimizado por _optimizar_estructura, solo asegurar una línea
        contenido = re.sub(r'\n\s*\n', '\n', contenido)
        return contenido
    
    def _validar_compatibilidad(self, contenido: str) -> List[str]:
        """Valida compatibilidad con clientes de email."""
        problemas = []
        
        # Verificar uso de tablas (requerido para Gmail)
        if '<table' not in contenido:
            problemas.append('Advertencia: No se encontraron tablas (requerido para Gmail)')
        
        # Verificar estilos inline (requerido para Gmail)
        if 'style=' not in contenido:
            problemas.append('Advertencia: Pocos estilos inline (puede afectar Gmail)')
        
        # Verificar comentarios condicionales MSO (recomendado para Outlook)
        if '<!--[if mso]' not in contenido:
            problemas.append('Advertencia: No se encontraron comentarios condicionales MSO (recomendado para Outlook)')
        
        # Verificar media queries (recomendado para responsive)
        if '@media' not in contenido:
            problemas.append('Advertencia: No se encontraron media queries (recomendado para responsive)')
        
        # Verificar uso de divs (problemático en algunos clientes)
        if '<div' in contenido:
            problemas.append('Advertencia: Se encontraron elementos <div> (puede causar problemas en algunos clientes)')
        
        return problemas
    
    def analizar_plantilla(self, contenido: str) -> Dict:
        """Analiza una plantilla y proporciona recomendaciones."""
        analisis = {
            'tamaño': len(contenido),
            'lineas': len(contenido.split('\n')),
            'tablas': len(re.findall(r'<table', contenido, re.IGNORECASE)),
            'estilos_inline': len(re.findall(r'style\s*=', contenido, re.IGNORECASE)),
            'comentarios_mso': len(re.findall(r'<!--\[if mso\]', contenido, re.IGNORECASE)),
            'media_queries': len(re.findall(r'@media', contenido, re.IGNORECASE)),
            'divs': len(re.findall(r'<div', contenido, re.IGNORECASE)),
            'enlaces': len(re.findall(r'<a\s+[^>]*href', contenido, re.IGNORECASE)),
            'imagenes': len(re.findall(r'<img', contenido, re.IGNORECASE)),
            'recomendaciones': []
        }
        
        # Generar recomendaciones
        if analisis['tamaño'] > 15000:
            analisis['recomendaciones'].append('El tamaño es grande (>15KB). Considera optimizar.')
        
        if analisis['divs'] > 0:
            analisis['recomendaciones'].append('Se encontraron elementos <div>. Considera usar solo tablas para mejor compatibilidad.')
        
        if analisis['comentarios_mso'] == 0:
            analisis['recomendaciones'].append('No se encontraron comentarios condicionales MSO. Agrega soporte para Outlook.')
        
        if analisis['media_queries'] == 0:
            analisis['recomendaciones'].append('No se encontraron media queries. Agrega soporte responsive.')
        
        if analisis['estilos_inline'] < 5:
            analisis['recomendaciones'].append('Pocos estilos inline. Gmail requiere estilos inline para mejor renderizado.')
        
        return analisis
    
    def optimizar_archivo(self, archivo_entrada: str, archivo_salida: str = None, opciones: Dict = None) -> Dict:
        """Optimiza un archivo de plantilla."""
        if archivo_salida is None:
            archivo_salida = archivo_entrada.replace('.html', '_optimizado.html')
        
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        optimizado, metricas = self.optimizar_plantilla(contenido, opciones)
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(optimizado)
        
        print(f"✅ Plantilla optimizada: {archivo_salida}")
        print(f"   Tamaño original: {metricas['tamaño_original']} bytes")
        print(f"   Tamaño optimizado: {metricas['tamaño_optimizado']} bytes")
        print(f"   Reducción: {metricas['reduccion']} bytes ({metricas['porcentaje_reduccion']}%)")
        print(f"   Optimizaciones aplicadas: {', '.join(metricas['optimizaciones'])}")
        
        if 'problemas_compatibilidad' in metricas:
            print(f"\n⚠️  Problemas de compatibilidad encontrados:")
            for problema in metricas['problemas_compatibilidad']:
                print(f"   - {problema}")
        
        return metricas
    
    def optimizar_directorio(self, directorio: str, opciones: Dict = None) -> Dict:
        """Optimiza todas las plantillas en un directorio."""
        directorio_path = Path(directorio)
        archivos_html = list(directorio_path.glob("firma_*.html"))
        
        resultados = {
            'total': len(archivos_html),
            'optimizados': 0,
            'errores': 0,
            'reduccion_total': 0,
            'archivos': []
        }
        
        for archivo in archivos_html:
            try:
                archivo_salida = archivo.parent / f"{archivo.stem}_optimizado.html"
                metricas = self.optimizar_archivo(str(archivo), str(archivo_salida), opciones)
                
                resultados['optimizados'] += 1
                resultados['reduccion_total'] += metricas['reduccion']
                resultados['archivos'].append({
                    'archivo': archivo.name,
                    'metricas': metricas
                })
            except Exception as e:
                print(f"❌ Error al optimizar {archivo.name}: {e}")
                resultados['errores'] += 1
        
        print(f"\n📊 Resumen:")
        print(f"   Total de archivos: {resultados['total']}")
        print(f"   Optimizados: {resultados['optimizados']}")
        print(f"   Errores: {resultados['errores']}")
        print(f"   Reducción total: {resultados['reduccion_total']} bytes")
        
        return resultados

def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Optimiza plantillas HTML')
    parser.add_argument('archivo', nargs='?', help='Archivo a optimizar (o directorio)')
    parser.add_argument('-o', '--output', help='Archivo de salida')
    parser.add_argument('-d', '--directorio', action='store_true',
                       help='Optimizar todos los archivos en el directorio')
    parser.add_argument('--no-minificar', action='store_true',
                       help='No minificar el código')
    parser.add_argument('--remover-comentarios', action='store_true',
                       help='Remover comentarios (excepto MSO)')
    
    args = parser.parse_args()
    
    optimizador = OptimizadorAvanzado()
    
    opciones = {
        'minificar': not args.no_minificar,
        'remover_comentarios': args.remover_comentarios,
        'optimizar_estilos': True,
        'optimizar_estructura': True,
        'validar_compatibilidad': True
    }
    
    if args.directorio or (args.archivo and Path(args.archivo).is_dir()):
        directorio = args.archivo or '.'
        optimizador.optimizar_directorio(directorio, opciones)
    elif args.archivo:
        optimizador.optimizar_archivo(args.archivo, args.output, opciones)
    else:
        print("❌ Especifica un archivo o directorio para optimizar")
        print("   Uso: python optimizador_avanzado.py <archivo> [-o salida.html]")
        print("   O: python optimizador_avanzado.py -d [directorio]")

if __name__ == "__main__":
    main()





