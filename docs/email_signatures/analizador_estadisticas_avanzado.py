#!/usr/bin/env python3
"""
Analizador de Estadísticas Avanzado
Genera estadísticas avanzadas y análisis detallados del proyecto.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set
from collections import Counter, defaultdict
import json
from datetime import datetime

class AnalizadorEstadisticasAvanzado:
    def __init__(self, directorio: str = "."):
        self.directorio = Path(directorio)
        self.plantillas = {}
        self.scripts = {}
    
    def cargar_archivos(self) -> None:
        """Carga todos los archivos del proyecto."""
        # Cargar plantillas
        archivos_html = list(self.directorio.glob("firma_*.html"))
        for archivo in archivos_html:
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    self.plantillas[archivo.name] = contenido
            except Exception as e:
                print(f"Error al cargar {archivo.name}: {e}")
        
        # Cargar scripts
        archivos_py = list(self.directorio.glob("*.py"))
        for archivo in archivos_py:
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    self.scripts[archivo.name] = contenido
            except Exception as e:
                print(f"Error al cargar {archivo.name}: {e}")
    
    def analizar_distribucion_industrias(self) -> Dict:
        """Analiza la distribución de plantillas por industria."""
        distribucion = Counter()
        
        for nombre in self.plantillas.keys():
            nombre_lower = nombre.lower()
            
            # Medicina
            if any(esp in nombre_lower for esp in ['medicina', 'medico', 'doctor', 'cardiologia', 'neurologia', 
                                                   'pediatria', 'ginecologia', 'ortopedia', 'anestesiologia',
                                                   'psiquiatria', 'oftalmologia', 'dermatologia', 'radiologia',
                                                   'enfermeria', 'geriatria', 'familiar', 'deportiva', 'emergencias',
                                                   'preventiva', 'interna']):
                distribucion['Medicina'] += 1
            # Odontología
            elif any(esp in nombre_lower for esp in ['odontologia', 'odontopediatria', 'ortodoncia']):
                distribucion['Odontología'] += 1
            # Terapias
            elif any(esp in nombre_lower for esp in ['fisioterapia', 'terapia_ocupacional', 'logopedia', 
                                                     'podologia', 'psicologia']):
                distribucion['Terapias'] += 1
            # Salud y Bienestar
            elif any(esp in nombre_lower for esp in ['nutricion', 'farmacia', 'estetica', 'veterinaria']):
                distribucion['Salud y Bienestar'] += 1
            # Profesionales
            elif any(esp in nombre_lower for esp in ['tecnologia', 'desarrollador', 'consultor', 'ventas',
                                                     'marketing', 'rrhh', 'legal', 'abogado', 'contabilidad',
                                                     'finanzas', 'educacion', 'profesor', 'ingenieria']):
                distribucion['Profesionales'] += 1
            # Empresas
            elif any(esp in nombre_lower for esp in ['empresa', 'startup', 'corporativa']):
                distribucion['Empresas'] += 1
            else:
                distribucion['Otros'] += 1
        
        return dict(distribucion)
    
    def analizar_complejidad_plantillas(self) -> Dict:
        """Analiza la complejidad de las plantillas."""
        complejidades = {
            'simple': [],
            'moderada': [],
            'avanzada': []
        }
        
        for nombre, contenido in self.plantillas.items():
            num_tablas = len(re.findall(r'<table', contenido, re.IGNORECASE))
            num_estilos = len(re.findall(r'style\s*=', contenido, re.IGNORECASE))
            num_scripts = len(re.findall(r'<script', contenido, re.IGNORECASE))
            num_comentarios_mso = len(re.findall(r'<!--\[if mso\]', contenido, re.IGNORECASE))
            
            complejidad_score = num_tablas + (num_estilos // 10) + (num_scripts * 5) + (num_comentarios_mso * 2)
            
            if complejidad_score < 10:
                complejidades['simple'].append(nombre)
            elif complejidad_score < 25:
                complejidades['moderada'].append(nombre)
            else:
                complejidades['avanzada'].append(nombre)
        
        return complejidades
    
    def analizar_uso_colores(self) -> Dict:
        """Analiza el uso de colores en las plantillas."""
        colores_todos = Counter()
        colores_por_plantilla = {}
        
        for nombre, contenido in self.plantillas.items():
            colores = re.findall(r'#([0-9a-fA-F]{3,6})', contenido, re.IGNORECASE)
            colores_unicos = set(colores)
            colores_por_plantilla[nombre] = list(colores_unicos)
            colores_todos.update(colores_unicos)
        
        return {
            'total_colores_unicos': len(colores_todos),
            'colores_mas_usados': dict(colores_todos.most_common(20)),
            'colores_por_plantilla': colores_por_plantilla,
            'promedio_colores_por_plantilla': round(sum(len(c) for c in colores_por_plantilla.values()) / len(colores_por_plantilla) if colores_por_plantilla else 0, 2)
        }
    
    def analizar_placeholders_comunes(self) -> Dict:
        """Analiza los placeholders más comunes."""
        placeholders_todos = Counter()
        placeholders_por_plantilla = {}
        
        for nombre, contenido in self.plantillas.items():
            placeholders = re.findall(r'\[([^\]]+)\]', contenido)
            placeholders_por_plantilla[nombre] = placeholders
            placeholders_todos.update(placeholders)
        
        return {
            'total_placeholders_unicos': len(placeholders_todos),
            'placeholders_mas_usados': dict(placeholders_todos.most_common(30)),
            'placeholders_por_plantilla': placeholders_por_plantilla,
            'promedio_placeholders_por_plantilla': round(sum(len(p) for p in placeholders_por_plantilla.values()) / len(placeholders_por_plantilla) if placeholders_por_plantilla else 0, 2)
        }
    
    def analizar_compatibilidad_global(self) -> Dict:
        """Analiza la compatibilidad global con clientes de email."""
        compatibilidad = {
            'outlook': {'total': 0, 'porcentaje': 0},
            'gmail': {'total': 0, 'porcentaje': 0},
            'apple_mail': {'total': 0, 'porcentaje': 0},
            'responsive': {'total': 0, 'porcentaje': 0}
        }
        
        total = len(self.plantillas)
        
        for contenido in self.plantillas.values():
            if '<!--[if mso]' in contenido:
                compatibilidad['outlook']['total'] += 1
            if '<table' in contenido and 'style=' in contenido:
                compatibilidad['gmail']['total'] += 1
            if '@media' in contenido:
                compatibilidad['apple_mail']['total'] += 1
                compatibilidad['responsive']['total'] += 1
        
        for cliente in compatibilidad:
            compatibilidad[cliente]['porcentaje'] = round((compatibilidad[cliente]['total'] / total * 100) if total > 0 else 0, 2)
        
        return compatibilidad
    
    def analizar_scripts(self) -> Dict:
        """Analiza los scripts Python."""
        analisis = {
            'total': len(self.scripts),
            'funciones_totales': 0,
            'clases_totales': 0,
            'lineas_totales': 0,
            'tamaño_total': 0,
            'categorias': Counter()
        }
        
        for nombre, contenido in self.scripts.items():
            funciones = len(re.findall(r'def\s+\w+', contenido))
            clases = len(re.findall(r'class\s+\w+', contenido))
            lineas = len(contenido.split('\n'))
            
            analisis['funciones_totales'] += funciones
            analisis['clases_totales'] += clases
            analisis['lineas_totales'] += lineas
            analisis['tamaño_total'] += len(contenido)
            
            # Categorizar
            nombre_lower = nombre.lower()
            if 'validar' in nombre_lower:
                analisis['categorias']['Validación'] += 1
            elif 'generar' in nombre_lower or 'crear' in nombre_lower:
                analisis['categorias']['Generación'] += 1
            elif 'analizar' in nombre_lower:
                analisis['categorias']['Análisis'] += 1
            elif 'optimizar' in nombre_lower:
                analisis['categorias']['Optimización'] += 1
            elif 'convertir' in nombre_lower:
                analisis['categorias']['Conversión'] += 1
            elif 'exportar' in nombre_lower:
                analisis['categorias']['Exportación'] += 1
            else:
                analisis['categorias']['Utilidades'] += 1
        
        analisis['promedio_funciones'] = round(analisis['funciones_totales'] / analisis['total'] if analisis['total'] > 0 else 0, 2)
        analisis['promedio_clases'] = round(analisis['clases_totales'] / analisis['total'] if analisis['total'] > 0 else 0, 2)
        analisis['promedio_lineas'] = round(analisis['lineas_totales'] / analisis['total'] if analisis['total'] > 0 else 0, 2)
        analisis['categorias'] = dict(analisis['categorias'])
        
        return analisis
    
    def generar_reporte_completo(self, archivo_salida: str = "estadisticas_avanzadas.json") -> None:
        """Genera un reporte completo de estadísticas avanzadas."""
        print("🔍 Analizando proyecto...")
        
        self.cargar_archivos()
        
        reporte = {
            'fecha': datetime.now().isoformat(),
            'resumen': {
                'total_plantillas': len(self.plantillas),
                'total_scripts': len(self.scripts),
                'total_archivos': len(self.plantillas) + len(self.scripts)
            },
            'distribucion_industrias': self.analizar_distribucion_industrias(),
            'complejidad_plantillas': self.analizar_complejidad_plantillas(),
            'uso_colores': self.analizar_uso_colores(),
            'placeholders_comunes': self.analizar_placeholders_comunes(),
            'compatibilidad_global': self.analizar_compatibilidad_global(),
            'analisis_scripts': self.analizar_scripts()
        }
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Reporte generado: {archivo_salida}")
        self._imprimir_resumen(reporte)
    
    def _imprimir_resumen(self, reporte: Dict) -> None:
        """Imprime un resumen del reporte."""
        print("\n" + "="*60)
        print("ESTADÍSTICAS AVANZADAS DEL PROYECTO")
        print("="*60)
        
        resumen = reporte['resumen']
        print(f"\n📊 Resumen General:")
        print(f"   - Plantillas HTML: {resumen['total_plantillas']}")
        print(f"   - Scripts Python: {resumen['total_scripts']}")
        print(f"   - Total archivos: {resumen['total_archivos']}")
        
        print(f"\n🏭 Distribución por Industria:")
        for industria, count in sorted(reporte['distribucion_industrias'].items(), key=lambda x: x[1], reverse=True):
            print(f"   - {industria}: {count} plantillas")
        
        print(f"\n📈 Complejidad de Plantillas:")
        complejidad = reporte['complejidad_plantillas']
        print(f"   - Simple: {len(complejidad['simple'])}")
        print(f"   - Moderada: {len(complejidad['moderada'])}")
        print(f"   - Avanzada: {len(complejidad['avanzada'])}")
        
        print(f"\n🎨 Uso de Colores:")
        colores = reporte['uso_colores']
        print(f"   - Colores únicos totales: {colores['total_colores_unicos']}")
        print(f"   - Promedio por plantilla: {colores['promedio_colores_por_plantilla']}")
        
        print(f"\n📝 Placeholders:")
        placeholders = reporte['placeholders_comunes']
        print(f"   - Placeholders únicos totales: {placeholders['total_placeholders_unicos']}")
        print(f"   - Promedio por plantilla: {placeholders['promedio_placeholders_por_plantilla']}")
        
        print(f"\n📧 Compatibilidad Global:")
        compat = reporte['compatibilidad_global']
        print(f"   - Outlook: {compat['outlook']['porcentaje']}% ({compat['outlook']['total']} plantillas)")
        print(f"   - Gmail: {compat['gmail']['porcentaje']}% ({compat['gmail']['total']} plantillas)")
        print(f"   - Apple Mail: {compat['apple_mail']['porcentaje']}% ({compat['apple_mail']['total']} plantillas)")
        print(f"   - Responsive: {compat['responsive']['porcentaje']}% ({compat['responsive']['total']} plantillas)")
        
        print(f"\n🐍 Análisis de Scripts:")
        scripts = reporte['analisis_scripts']
        print(f"   - Total scripts: {scripts['total']}")
        print(f"   - Funciones totales: {scripts['funciones_totales']} (promedio: {scripts['promedio_funciones']})")
        print(f"   - Clases totales: {scripts['clases_totales']} (promedio: {scripts['promedio_clases']})")
        print(f"   - Líneas totales: {scripts['lineas_totales']} (promedio: {scripts['promedio_lineas']})")
        print(f"   - Categorías:")
        for categoria, count in scripts['categorias'].items():
            print(f"     - {categoria}: {count}")
        
        print("\n" + "="*60)

def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Genera estadísticas avanzadas del proyecto')
    parser.add_argument('-d', '--directorio', default='.', 
                       help='Directorio del proyecto (default: actual)')
    parser.add_argument('-o', '--output', default='estadisticas_avanzadas.json',
                       help='Archivo de salida (default: estadisticas_avanzadas.json)')
    
    args = parser.parse_args()
    
    analizador = AnalizadorEstadisticasAvanzado(args.directorio)
    analizador.generar_reporte_completo(args.output)

if __name__ == "__main__":
    main()





