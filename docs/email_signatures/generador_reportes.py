#!/usr/bin/env python3
"""
Generador de Reportes Completo
Genera reportes completos del proyecto con múltiples métricas y análisis.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set
from collections import Counter, defaultdict
import json
from datetime import datetime

class GeneradorReportes:
    def __init__(self, directorio: str = "."):
        self.directorio = Path(directorio)
        self.plantillas = {}
        self.scripts = {}
    
    def cargar_archivos(self) -> None:
        """Carga todos los archivos del proyecto."""
        # Cargar plantillas HTML
        archivos_html = list(self.directorio.glob("firma_*.html"))
        for archivo in archivos_html:
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    self.plantillas[archivo.name] = {
                        'archivo': archivo.name,
                        'contenido': contenido,
                        'tamaño': len(contenido),
                        'lineas': len(contenido.split('\n'))
                    }
            except Exception as e:
                print(f"Error al cargar {archivo.name}: {e}")
        
        # Cargar scripts Python
        archivos_py = list(self.directorio.glob("*.py"))
        for archivo in archivos_py:
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    self.scripts[archivo.name] = {
                        'archivo': archivo.name,
                        'contenido': contenido,
                        'tamaño': len(contenido),
                        'lineas': len(contenido.split('\n'))
                    }
            except Exception as e:
                print(f"Error al cargar {archivo.name}: {e}")
    
    def analizar_plantillas(self) -> Dict:
        """Analiza todas las plantillas."""
        analisis = {
            'total': len(self.plantillas),
            'tamaños': [],
            'lineas': [],
            'placeholders': Counter(),
            'colores': Counter(),
            'industrias': Counter(),
            'compatibilidad': {
                'outlook': 0,
                'gmail': 0,
                'apple_mail': 0,
                'responsive': 0
            },
            'caracteristicas': {
                'con_calendario': 0,
                'con_redes_sociales': 0,
                'con_badge': 0,
                'con_imagenes': 0
            }
        }
        
        for nombre, datos in self.plantillas.items():
            contenido = datos['contenido']
            
            # Tamaños y líneas
            analisis['tamaños'].append(datos['tamaño'])
            analisis['lineas'].append(datos['lineas'])
            
            # Placeholders
            placeholders = re.findall(r'\[([^\]]+)\]', contenido)
            analisis['placeholders'].update(placeholders)
            
            # Colores
            colores = re.findall(r'#([0-9a-fA-F]{3,6})', contenido, re.IGNORECASE)
            analisis['colores'].update(colores)
            
            # Industria (del nombre del archivo)
            nombre_lower = nombre.lower()
            if 'medico' in nombre_lower or 'doctor' in nombre_lower or any(esp in nombre_lower for esp in ['oftalmologia', 'dermatologia', 'cardiologia', 'neurologia', 'pediatria', 'ginecologia', 'ortopedia']):
                analisis['industrias']['medicina'] += 1
            elif 'tecnologia' in nombre_lower or 'desarrollador' in nombre_lower:
                analisis['industrias']['tecnologia'] += 1
            elif 'educacion' in nombre_lower or 'profesor' in nombre_lower:
                analisis['industrias']['educacion'] += 1
            elif 'legal' in nombre_lower or 'abogado' in nombre_lower:
                analisis['industrias']['legal'] += 1
            elif 'ventas' in nombre_lower or 'comercial' in nombre_lower:
                analisis['industrias']['ventas'] += 1
            elif 'marketing' in nombre_lower:
                analisis['industrias']['marketing'] += 1
            else:
                analisis['industrias']['otras'] += 1
            
            # Compatibilidad
            if '<!--[if mso]' in contenido:
                analisis['compatibilidad']['outlook'] += 1
            if '<table' in contenido:
                analisis['compatibilidad']['gmail'] += 1
            if '@media' in contenido:
                analisis['compatibilidad']['apple_mail'] += 1
                analisis['compatibilidad']['responsive'] += 1
            
            # Características
            if '[URL_CALENDARIO]' in contenido or 'calendario' in contenido.lower():
                analisis['caracteristicas']['con_calendario'] += 1
            if 'linkedin' in contenido.lower() or 'twitter' in contenido.lower() or 'facebook' in contenido.lower():
                analisis['caracteristicas']['con_redes_sociales'] += 1
            if 'badge' in contenido.lower() or 'gradient' in contenido.lower():
                analisis['caracteristicas']['con_badge'] += 1
            if '<img' in contenido:
                analisis['caracteristicas']['con_imagenes'] += 1
        
        # Calcular estadísticas
        if analisis['tamaños']:
            analisis['tamaño_promedio'] = round(sum(analisis['tamaños']) / len(analisis['tamaños']), 2)
            analisis['tamaño_min'] = min(analisis['tamaños'])
            analisis['tamaño_max'] = max(analisis['tamaños'])
        
        if analisis['lineas']:
            analisis['lineas_promedio'] = round(sum(analisis['lineas']) / len(analisis['lineas']), 2)
            analisis['lineas_min'] = min(analisis['lineas'])
            analisis['lineas_max'] = max(analisis['lineas'])
        
        return analisis
    
    def analizar_scripts(self) -> Dict:
        """Analiza todos los scripts Python."""
        analisis = {
            'total': len(self.scripts),
            'tamaños': [],
            'lineas': [],
            'funciones': Counter(),
            'clases': Counter(),
            'imports': Counter(),
            'categorias': {
                'validacion': 0,
                'generacion': 0,
                'analisis': 0,
                'optimizacion': 0,
                'utilidades': 0
            }
        }
        
        for nombre, datos in self.scripts.items():
            contenido = datos['contenido']
            
            # Tamaños y líneas
            analisis['tamaños'].append(datos['tamaño'])
            analisis['lineas'].append(datos['lineas'])
            
            # Funciones
            funciones = re.findall(r'def\s+(\w+)', contenido)
            analisis['funciones'].update(funciones)
            
            # Clases
            clases = re.findall(r'class\s+(\w+)', contenido)
            analisis['clases'].update(clases)
            
            # Imports
            imports = re.findall(r'^import\s+(\w+)|^from\s+(\w+)', contenido, re.MULTILINE)
            for imp in imports:
                mod = imp[0] or imp[1]
                if mod:
                    analisis['imports'][mod] += 1
            
            # Categorías
            nombre_lower = nombre.lower()
            if 'validar' in nombre_lower:
                analisis['categorias']['validacion'] += 1
            elif 'generar' in nombre_lower or 'crear' in nombre_lower:
                analisis['categorias']['generacion'] += 1
            elif 'analizar' in nombre_lower or 'analisis' in nombre_lower:
                analisis['categorias']['analisis'] += 1
            elif 'optimizar' in nombre_lower:
                analisis['categorias']['optimizacion'] += 1
            else:
                analisis['categorias']['utilidades'] += 1
        
        # Calcular estadísticas
        if analisis['tamaños']:
            analisis['tamaño_promedio'] = round(sum(analisis['tamaños']) / len(analisis['tamaños']), 2)
            analisis['tamaño_min'] = min(analisis['tamaños'])
            analisis['tamaño_max'] = max(analisis['tamaños'])
        
        if analisis['lineas']:
            analisis['lineas_promedio'] = round(sum(analisis['lineas']) / len(analisis['lineas']), 2)
            analisis['lineas_min'] = min(analisis['lineas'])
            analisis['lineas_max'] = max(analisis['lineas'])
        
        return analisis
    
    def generar_reporte_completo(self, archivo_salida: str = "reporte_completo.json") -> None:
        """Genera un reporte completo del proyecto."""
        print("🔍 Analizando proyecto...")
        
        self.cargar_archivos()
        
        reporte = {
            'fecha': datetime.now().isoformat(),
            'resumen': {
                'total_plantillas': len(self.plantillas),
                'total_scripts': len(self.scripts),
                'total_archivos': len(self.plantillas) + len(self.scripts)
            },
            'plantillas': self.analizar_plantillas(),
            'scripts': self.analizar_scripts(),
            'recomendaciones': self._generar_recomendaciones()
        }
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Reporte generado: {archivo_salida}")
        self._imprimir_resumen(reporte)
    
    def _generar_recomendaciones(self) -> List[str]:
        """Genera recomendaciones basadas en el análisis."""
        recomendaciones = []
        
        if len(self.plantillas) < 50:
            recomendaciones.append('Considera agregar más plantillas para cubrir más industrias')
        
        if len(self.scripts) < 20:
            recomendaciones.append('Considera agregar más herramientas de automatización')
        
        # Verificar compatibilidad
        analisis_plantillas = self.analizar_plantillas()
        total = analisis_plantillas['total']
        
        if analisis_plantillas['compatibilidad']['outlook'] < total * 0.9:
            recomendaciones.append('Mejora el soporte para Outlook en más plantillas')
        
        if analisis_plantillas['compatibilidad']['responsive'] < total * 0.9:
            recomendaciones.append('Agrega soporte responsive a más plantillas')
        
        return recomendaciones
    
    def _imprimir_resumen(self, reporte: Dict) -> None:
        """Imprime un resumen del reporte."""
        print("\n" + "="*60)
        print("RESUMEN DEL PROYECTO")
        print("="*60)
        
        resumen = reporte['resumen']
        print(f"\n📊 Total de archivos: {resumen['total_archivos']}")
        print(f"   - Plantillas HTML: {resumen['total_plantillas']}")
        print(f"   - Scripts Python: {resumen['total_scripts']}")
        
        # Plantillas
        plantillas = reporte['plantillas']
        print(f"\n📄 PLANTILLAS:")
        print(f"   Tamaño promedio: {plantillas.get('tamaño_promedio', 0)} bytes")
        print(f"   Líneas promedio: {plantillas.get('lineas_promedio', 0)}")
        print(f"   Compatibilidad Outlook: {plantillas['compatibilidad']['outlook']}/{plantillas['total']}")
        print(f"   Compatibilidad Gmail: {plantillas['compatibilidad']['gmail']}/{plantillas['total']}")
        print(f"   Responsive: {plantillas['compatibilidad']['responsive']}/{plantillas['total']}")
        
        print(f"\n   Industrias:")
        for industria, count in plantillas['industrias'].most_common():
            print(f"     - {industria}: {count}")
        
        # Scripts
        scripts = reporte['scripts']
        print(f"\n🐍 SCRIPTS:")
        print(f"   Tamaño promedio: {scripts.get('tamaño_promedio', 0)} bytes")
        print(f"   Líneas promedio: {scripts.get('lineas_promedio', 0)}")
        print(f"   Total de funciones: {sum(scripts['funciones'].values())}")
        print(f"   Total de clases: {sum(scripts['clases'].values())}")
        
        print(f"\n   Categorías:")
        for categoria, count in scripts['categorias'].items():
            print(f"     - {categoria}: {count}")
        
        # Recomendaciones
        if reporte['recomendaciones']:
            print(f"\n💡 RECOMENDACIONES:")
            for rec in reporte['recomendaciones']:
                print(f"   - {rec}")
        
        print("\n" + "="*60)

def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Genera reportes completos del proyecto')
    parser.add_argument('-d', '--directorio', default='.', 
                       help='Directorio del proyecto (default: actual)')
    parser.add_argument('-o', '--output', default='reporte_completo.json',
                       help='Archivo de salida (default: reporte_completo.json)')
    
    args = parser.parse_args()
    
    generador = GeneradorReportes(args.directorio)
    generador.generar_reporte_completo(args.output)

if __name__ == "__main__":
    main()





