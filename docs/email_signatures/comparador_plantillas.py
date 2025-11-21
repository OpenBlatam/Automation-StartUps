#!/usr/bin/env python3
"""
Comparador de Plantillas de Firmas de Email
Compara múltiples plantillas HTML y genera un reporte detallado de diferencias.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import json
from datetime import datetime

class ComparadorPlantillas:
    def __init__(self, directorio: str = "."):
        self.directorio = Path(directorio)
        self.plantillas = {}
        self.metricas = {}
        
    def cargar_plantillas(self) -> None:
        """Carga todas las plantillas HTML del directorio."""
        archivos_html = list(self.directorio.glob("firma_*.html"))
        
        for archivo in archivos_html:
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    self.plantillas[archivo.name] = contenido
                    self.metricas[archivo.name] = self._calcular_metricas(contenido)
            except Exception as e:
                print(f"Error al cargar {archivo.name}: {e}")
    
    def _calcular_metricas(self, contenido: str) -> Dict:
        """Calcula métricas de una plantilla."""
        return {
            'tamaño': len(contenido),
            'lineas': len(contenido.split('\n')),
            'placeholders': len(re.findall(r'\[.*?\]', contenido)),
            'enlaces': len(re.findall(r'<a\s+[^>]*href', contenido, re.IGNORECASE)),
            'imagenes': len(re.findall(r'<img', contenido, re.IGNORECASE)),
            'tablas': len(re.findall(r'<table', contenido, re.IGNORECASE)),
            'estilos_inline': len(re.findall(r'style\s*=', contenido, re.IGNORECASE)),
            'comentarios_mso': len(re.findall(r'<!--\[if mso\]', contenido, re.IGNORECASE)),
            'colores': self._extraer_colores(contenido),
            'fuentes': self._extraer_fuentes(contenido),
        }
    
    def _extraer_colores(self, contenido: str) -> Set[str]:
        """Extrae colores únicos de la plantilla."""
        colores = set()
        # Buscar colores hex
        hex_colors = re.findall(r'#([0-9a-fA-F]{3,6})', contenido)
        colores.update(hex_colors)
        # Buscar colores rgb/rgba
        rgb_colors = re.findall(r'rgb\([^)]+\)', contenido)
        colores.update(rgb_colors)
        return colores
    
    def _extraer_fuentes(self, contenido: str) -> Set[str]:
        """Extrae fuentes utilizadas."""
        fuentes = set()
        # Buscar en font-family
        font_matches = re.findall(r'font-family\s*:\s*([^;]+)', contenido, re.IGNORECASE)
        for match in font_matches:
            fuentes.update([f.strip() for f in match.split(',')])
        return fuentes
    
    def comparar_estructura(self) -> Dict:
        """Compara la estructura de todas las plantillas."""
        estructuras = {}
        
        for nombre, contenido in self.plantillas.items():
            # Extraer estructura de tablas
            tablas = re.findall(r'<table[^>]*>', contenido, re.IGNORECASE)
            # Extraer clases CSS
            clases = set(re.findall(r'class\s*=\s*["\']([^"\']+)["\']', contenido))
            # Extraer IDs
            ids = set(re.findall(r'id\s*=\s*["\']([^"\']+)["\']', contenido))
            
            estructuras[nombre] = {
                'num_tablas': len(tablas),
                'clases': clases,
                'ids': ids,
                'estructura_tablas': len(re.findall(r'<tr', contenido, re.IGNORECASE))
            }
        
        return estructuras
    
    def encontrar_similitudes(self) -> List[Tuple[str, str, float]]:
        """Encuentra plantillas similares basándose en métricas."""
        similitudes = []
        nombres = list(self.plantillas.keys())
        
        for i, nombre1 in enumerate(nombres):
            for nombre2 in nombres[i+1:]:
                similitud = self._calcular_similitud(
                    self.metricas[nombre1],
                    self.metricas[nombre2]
                )
                similitudes.append((nombre1, nombre2, similitud))
        
        return sorted(similitudes, key=lambda x: x[2], reverse=True)
    
    def _calcular_similitud(self, metrica1: Dict, metrica2: Dict) -> float:
        """Calcula similitud entre dos métricas."""
        # Comparar métricas numéricas
        similitud = 0.0
        total = 0
        
        metricas_numericas = ['tamaño', 'lineas', 'placeholders', 'enlaces', 
                             'imagenes', 'tablas', 'estilos_inline', 'comentarios_mso']
        
        for metrica in metricas_numericas:
            if metrica1[metrica] == 0 and metrica2[metrica] == 0:
                similitud += 1.0
            elif metrica1[metrica] == 0 or metrica2[metrica] == 0:
                similitud += 0.0
            else:
                ratio = min(metrica1[metrica], metrica2[metrica]) / max(metrica1[metrica], metrica2[metrica])
                similitud += ratio
            total += 1
        
        # Comparar colores
        colores_comunes = len(metrica1['colores'] & metrica2['colores'])
        colores_totales = len(metrica1['colores'] | metrica2['colores'])
        if colores_totales > 0:
            similitud += colores_comunes / colores_totales
            total += 1
        
        # Comparar fuentes
        fuentes_comunes = len(metrica1['fuentes'] & metrica2['fuentes'])
        fuentes_totales = len(metrica1['fuentes'] | metrica2['fuentes'])
        if fuentes_totales > 0:
            similitud += fuentes_comunes / fuentes_totales
            total += 1
        
        return similitud / total if total > 0 else 0.0
    
    def encontrar_diferencias(self, plantilla1: str, plantilla2: str) -> Dict:
        """Encuentra diferencias específicas entre dos plantillas."""
        if plantilla1 not in self.plantillas or plantilla2 not in self.plantillas:
            return {}
        
        contenido1 = self.plantillas[plantilla1]
        contenido2 = self.plantillas[plantilla2]
        metrica1 = self.metricas[plantilla1]
        metrica2 = self.metricas[plantilla2]
        
        diferencias = {
            'tamaño': metrica2['tamaño'] - metrica1['tamaño'],
            'lineas': metrica2['lineas'] - metrica1['lineas'],
            'placeholders': metrica2['placeholders'] - metrica1['placeholders'],
            'enlaces': metrica2['enlaces'] - metrica1['enlaces'],
            'colores_unicos_1': metrica1['colores'] - metrica2['colores'],
            'colores_unicos_2': metrica2['colores'] - metrica1['colores'],
            'colores_comunes': metrica1['colores'] & metrica2['colores'],
        }
        
        return diferencias
    
    def generar_reporte(self, archivo_salida: str = "reporte_comparacion.json") -> None:
        """Genera un reporte completo de comparación."""
        reporte = {
            'fecha': datetime.now().isoformat(),
            'total_plantillas': len(self.plantillas),
            'metricas_individuales': self.metricas,
            'estructuras': self.comparar_estructura(),
            'similitudes': [
                {
                    'plantilla1': p1,
                    'plantilla2': p2,
                    'similitud': round(s * 100, 2)
                }
                for p1, p2, s in self.encontrar_similitudes()
            ],
            'resumen': self._generar_resumen()
        }
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Reporte generado: {archivo_salida}")
        self._imprimir_resumen(reporte['resumen'])
    
    def _generar_resumen(self) -> Dict:
        """Genera un resumen estadístico."""
        if not self.metricas:
            return {}
        
        metricas_numericas = ['tamaño', 'lineas', 'placeholders', 'enlaces', 
                             'imagenes', 'tablas', 'estilos_inline']
        
        resumen = {}
        for metrica in metricas_numericas:
            valores = [m[metrica] for m in self.metricas.values()]
            resumen[metrica] = {
                'min': min(valores),
                'max': max(valores),
                'promedio': round(sum(valores) / len(valores), 2),
                'total': sum(valores)
            }
        
        # Colores únicos
        todos_colores = set()
        for m in self.metricas.values():
            todos_colores.update(m['colores'])
        resumen['colores_unicos_totales'] = len(todos_colores)
        
        # Fuentes únicas
        todas_fuentes = set()
        for m in self.metricas.values():
            todas_fuentes.update(m['fuentes'])
        resumen['fuentes_unicas_totales'] = len(todas_fuentes)
        
        return resumen
    
    def _imprimir_resumen(self, resumen: Dict) -> None:
        """Imprime un resumen en consola."""
        print("\n" + "="*60)
        print("RESUMEN DE COMPARACIÓN")
        print("="*60)
        
        for metrica, valores in resumen.items():
            if isinstance(valores, dict) and 'promedio' in valores:
                print(f"\n{metrica.upper()}:")
                print(f"  Min: {valores['min']}")
                print(f"  Max: {valores['max']}")
                print(f"  Promedio: {valores['promedio']}")
                print(f"  Total: {valores['total']}")
            elif isinstance(valores, int):
                print(f"\n{metrica.replace('_', ' ').title()}: {valores}")
        
        print("\n" + "="*60)

def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Compara plantillas de firmas de email')
    parser.add_argument('-d', '--directorio', default='.', 
                       help='Directorio con las plantillas (default: actual)')
    parser.add_argument('-o', '--output', default='reporte_comparacion.json',
                       help='Archivo de salida (default: reporte_comparacion.json)')
    
    args = parser.parse_args()
    
    comparador = ComparadorPlantillas(args.directorio)
    comparador.cargar_plantillas()
    
    if not comparador.plantillas:
        print("❌ No se encontraron plantillas HTML en el directorio.")
        return
    
    print(f"📊 Analizando {len(comparador.plantillas)} plantillas...")
    comparador.generar_reporte(args.output)

if __name__ == "__main__":
    main()





