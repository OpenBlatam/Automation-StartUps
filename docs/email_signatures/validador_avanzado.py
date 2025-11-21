#!/usr/bin/env python3
"""
Validador Avanzado de Plantillas
Valida plantillas HTML de firmas de email con múltiples criterios y genera reportes detallados.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
import json
from datetime import datetime

class ValidadorAvanzado:
    def __init__(self):
        self.errores = []
        self.advertencias = []
        self.sugerencias = []
        self.validaciones_pasadas = []
    
    def validar_plantilla(self, contenido: str, nombre_archivo: str = None) -> Dict:
        """Valida una plantilla HTML completa."""
        self.errores = []
        self.advertencias = []
        self.sugerencias = []
        self.validaciones_pasadas = []
        
        # Validaciones básicas
        self._validar_estructura_html(contenido)
        self._validar_doctype(contenido)
        self._validar_charset(contenido)
        
        # Validaciones de compatibilidad
        self._validar_compatibilidad_outlook(contenido)
        self._validar_compatibilidad_gmail(contenido)
        self._validar_compatibilidad_apple_mail(contenido)
        
        # Validaciones de estructura
        self._validar_uso_tablas(contenido)
        self._validar_estilos_inline(contenido)
        self._validar_responsive(contenido)
        
        # Validaciones de contenido
        self._validar_placeholders(contenido)
        self._validar_enlaces(contenido)
        self._validar_imagenes(contenido)
        
        # Validaciones de accesibilidad
        self._validar_accesibilidad(contenido)
        
        # Validaciones de rendimiento
        self._validar_rendimiento(contenido)
        
        # Validaciones de seguridad
        self._validar_seguridad(contenido)
        
        # Calcular puntuación
        puntuacion = self._calcular_puntuacion()
        
        return {
            'archivo': nombre_archivo or 'plantilla',
            'puntuacion': puntuacion,
            'errores': self.errores,
            'advertencias': self.advertencias,
            'sugerencias': self.sugerencias,
            'validaciones_pasadas': self.validaciones_pasadas,
            'total_errores': len(self.errores),
            'total_advertencias': len(self.advertencias),
            'total_sugerencias': len(self.sugerencias),
            'total_validaciones': len(self.validaciones_pasadas)
        }
    
    def _validar_estructura_html(self, contenido: str) -> None:
        """Valida la estructura básica HTML."""
        if '<html' not in contenido:
            self.errores.append('No se encontró la etiqueta <html>')
        else:
            self.validaciones_pasadas.append('Estructura HTML básica presente')
        
        if '<body' not in contenido:
            self.errores.append('No se encontró la etiqueta <body>')
        
        # Verificar etiquetas cerradas
        tags_abiertas = re.findall(r'<(\w+)', contenido)
        tags_cerradas = re.findall(r'</(\w+)', contenido)
        
        if len(tags_abiertas) - len(tags_cerradas) > 10:  # Permitir algunas diferencias
            self.advertencias.append('Posibles etiquetas no cerradas')
    
    def _validar_doctype(self, contenido: str) -> None:
        """Valida el DOCTYPE."""
        if '<!DOCTYPE' not in contenido:
            self.advertencias.append('No se encontró DOCTYPE (recomendado)')
        else:
            self.validaciones_pasadas.append('DOCTYPE presente')
    
    def _validar_charset(self, contenido: str) -> None:
        """Valida el charset UTF-8."""
        if 'charset="UTF-8"' not in contenido and "charset='UTF-8'" not in contenido:
            self.advertencias.append('Charset UTF-8 no especificado explícitamente')
        else:
            self.validaciones_pasadas.append('Charset UTF-8 presente')
    
    def _validar_compatibilidad_outlook(self, contenido: str) -> None:
        """Valida compatibilidad con Outlook."""
        if '<!--[if mso]' not in contenido:
            self.advertencias.append('No se encontraron comentarios condicionales MSO (recomendado para Outlook)')
        else:
            self.validaciones_pasadas.append('Soporte MSO para Outlook presente')
        
        if 'xmlns:v=' not in contenido:
            self.advertencias.append('No se encontró xmlns:v (recomendado para VML en Outlook)')
        
        if 'xmlns:o=' not in contenido:
            self.advertencias.append('No se encontró xmlns:o (recomendado para Office en Outlook)')
    
    def _validar_compatibilidad_gmail(self, contenido: str) -> None:
        """Valida compatibilidad con Gmail."""
        if '<table' not in contenido:
            self.errores.append('No se encontraron tablas (requerido para Gmail)')
        else:
            self.validaciones_pasadas.append('Uso de tablas para Gmail presente')
        
        if 'style=' not in contenido:
            self.advertencias.append('Pocos estilos inline (Gmail requiere estilos inline)')
        else:
            num_estilos = len(re.findall(r'style\s*=', contenido, re.IGNORECASE))
            if num_estilos < 5:
                self.advertencias.append('Muy pocos estilos inline (Gmail funciona mejor con estilos inline)')
            else:
                self.validaciones_pasadas.append('Estilos inline suficientes para Gmail')
    
    def _validar_compatibilidad_apple_mail(self, contenido: str) -> None:
        """Valida compatibilidad con Apple Mail."""
        if '@media' not in contenido:
            self.advertencias.append('No se encontraron media queries (recomendado para Apple Mail responsive)')
        else:
            self.validaciones_pasadas.append('Media queries presentes para Apple Mail')
    
    def _validar_uso_tablas(self, contenido: str) -> None:
        """Valida el uso correcto de tablas."""
        if '<div' in contenido:
            self.advertencias.append('Se encontraron elementos <div> (puede causar problemas en algunos clientes de email)')
        else:
            self.validaciones_pasadas.append('No se usan elementos <div> (mejor compatibilidad)')
        
        # Verificar role="presentation" en tablas
        tablas = re.findall(r'<table[^>]*>', contenido, re.IGNORECASE)
        tablas_con_role = [t for t in tablas if 'role="presentation"' in t or "role='presentation'" in t]
        
        if len(tablas) > 0 and len(tablas_con_role) < len(tablas) * 0.8:
            self.sugerencias.append('Considera agregar role="presentation" a más tablas para mejor accesibilidad')
        elif len(tablas_con_role) > 0:
            self.validaciones_pasadas.append('Tablas con role="presentation" para accesibilidad')
    
    def _validar_estilos_inline(self, contenido: str) -> None:
        """Valida el uso de estilos inline."""
        # Verificar que no haya estilos en <style> tags (excepto media queries y MSO)
        estilos_en_tags = re.findall(r'<style[^>]*>([^<]+)</style>', contenido, re.IGNORECASE | re.DOTALL)
        estilos_problematicos = [s for s in estilos_en_tags if '@media' not in s and 'mso' not in s.lower()]
        
        if estilos_problematicos:
            self.advertencias.append('Se encontraron estilos en tags <style> (algunos clientes de email los ignoran)')
        else:
            self.validaciones_pasadas.append('Estilos correctamente implementados')
    
    def _validar_responsive(self, contenido: str) -> None:
        """Valida características responsive."""
        if '@media' in contenido:
            self.validaciones_pasadas.append('Media queries presentes para responsive')
            
            # Verificar viewport
            if 'viewport' not in contenido:
                self.sugerencias.append('Considera agregar meta viewport para mejor responsive')
        else:
            self.advertencias.append('No se encontraron media queries (responsive puede no funcionar)')
    
    def _validar_placeholders(self, contenido: str) -> None:
        """Valida placeholders."""
        placeholders = re.findall(r'\[([^\]]+)\]', contenido)
        
        if not placeholders:
            self.sugerencias.append('No se encontraron placeholders (puede ser intencional)')
        else:
            self.validaciones_pasadas.append(f'Placeholders encontrados: {len(placeholders)}')
            
            # Verificar placeholders comunes
            placeholders_comunes = ['nombre', 'email', 'telefono', 'empresa', 'titulo']
            encontrados = [p for p in placeholders if any(c in p.lower() for c in placeholders_comunes)]
            
            if len(encontrados) == 0:
                self.sugerencias.append('No se encontraron placeholders comunes (nombre, email, teléfono)')
    
    def _validar_enlaces(self, contenido: str) -> None:
        """Valida enlaces."""
        enlaces = re.findall(r'<a\s+[^>]*href\s*=\s*["\']([^"\']+)["\']', contenido, re.IGNORECASE)
        
        if not enlaces:
            self.sugerencias.append('No se encontraron enlaces')
        else:
            self.validaciones_pasadas.append(f'Enlaces encontrados: {len(enlaces)}')
            
            # Verificar target="_blank" y rel="noopener noreferrer"
            enlaces_sin_seguridad = []
            for enlace in re.finditer(r'<a\s+[^>]*href\s*=\s*["\']([^"\']+)["\']', contenido, re.IGNORECASE):
                tag = enlace.group(0)
                url = enlace.group(1)
                
                if url.startswith('http://') or url.startswith('https://'):
                    if 'target="_blank"' in tag or "target='_blank'" in tag:
                        if 'rel=' not in tag or ('noopener' not in tag and 'noreferrer' not in tag):
                            enlaces_sin_seguridad.append(url)
            
            if enlaces_sin_seguridad:
                self.advertencias.append(f'Enlaces externos sin rel="noopener noreferrer" encontrados: {len(enlaces_sin_seguridad)}')
            else:
                self.validaciones_pasadas.append('Enlaces externos con seguridad correcta')
    
    def _validar_imagenes(self, contenido: str) -> None:
        """Valida imágenes."""
        imagenes = re.findall(r'<img[^>]*>', contenido, re.IGNORECASE)
        
        if imagenes:
            imagenes_sin_alt = [img for img in imagenes if 'alt=' not in img]
            
            if imagenes_sin_alt:
                self.advertencias.append(f'Imágenes sin atributo alt encontradas: {len(imagenes_sin_alt)}')
            else:
                self.validaciones_pasadas.append('Todas las imágenes tienen atributo alt')
    
    def _validar_accesibilidad(self, contenido: str) -> None:
        """Valida características de accesibilidad."""
        # Verificar estructura semántica
        if 'role=' in contenido:
            self.validaciones_pasadas.append('Atributos role presentes para accesibilidad')
        else:
            self.sugerencias.append('Considera agregar atributos role para mejor accesibilidad')
        
        # Verificar contraste (básico - solo verificar colores)
        colores = re.findall(r'color\s*:\s*#([0-9a-fA-F]{3,6})', contenido, re.IGNORECASE)
        if colores:
            self.validaciones_pasadas.append('Colores definidos (verificar contraste manualmente)')
    
    def _validar_rendimiento(self, contenido: str) -> None:
        """Valida rendimiento."""
        tamaño = len(contenido)
        
        if tamaño > 20000:
            self.advertencias.append(f'Tamaño grande ({tamaño} bytes). Considera optimizar.')
        elif tamaño > 15000:
            self.sugerencias.append(f'Tamaño moderado ({tamaño} bytes). Puede optimizarse.')
        else:
            self.validaciones_pasadas.append(f'Tamaño adecuado ({tamaño} bytes)')
        
        # Verificar espacios en blanco excesivos
        lineas_vacias = len([l for l in contenido.split('\n') if l.strip() == ''])
        if lineas_vacias > len(contenido.split('\n')) * 0.3:
            self.sugerencias.append('Muchas líneas vacías. Considera minificar.')
    
    def _validar_seguridad(self, contenido: str) -> None:
        """Valida aspectos de seguridad."""
        # Verificar scripts
        if '<script' in contenido:
            self.errores.append('Se encontraron elementos <script> (no recomendado en emails)')
        else:
            self.validaciones_pasadas.append('No se encontraron scripts (seguro)')
        
        # Verificar iframes
        if '<iframe' in contenido:
            self.advertencias.append('Se encontraron elementos <iframe> (puede ser bloqueado por clientes de email)')
        else:
            self.validaciones_pasadas.append('No se encontraron iframes (mejor compatibilidad)')
    
    def _calcular_puntuacion(self) -> int:
        """Calcula una puntuación de 0-100."""
        total_validaciones = len(self.validaciones_pasadas) + len(self.errores) + len(self.advertencias) + len(self.sugerencias)
        
        if total_validaciones == 0:
            return 0
        
        puntos = len(self.validaciones_pasadas) * 10
        puntos -= len(self.errores) * 20
        puntos -= len(self.advertencias) * 5
        puntos -= len(self.sugerencias) * 2
        
        return max(0, min(100, puntos))
    
    def validar_archivo(self, archivo: str) -> Dict:
        """Valida un archivo de plantilla."""
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        return self.validar_plantilla(contenido, Path(archivo).name)
    
    def validar_directorio(self, directorio: str) -> Dict:
        """Valida todas las plantillas en un directorio."""
        directorio_path = Path(directorio)
        archivos_html = list(directorio_path.glob("firma_*.html"))
        
        resultados = {
            'total': len(archivos_html),
            'validados': 0,
            'errores': 0,
            'archivos': [],
            'resumen': {
                'puntuacion_promedio': 0,
                'total_errores': 0,
                'total_advertencias': 0,
                'total_sugerencias': 0
            }
        }
        
        puntuaciones = []
        total_errores = 0
        total_advertencias = 0
        total_sugerencias = 0
        
        for archivo in archivos_html:
            try:
                resultado = self.validar_archivo(str(archivo))
                resultados['archivos'].append(resultado)
                resultados['validados'] += 1
                
                puntuaciones.append(resultado['puntuacion'])
                total_errores += resultado['total_errores']
                total_advertencias += resultado['total_advertencias']
                total_sugerencias += resultado['total_sugerencias']
            except Exception as e:
                print(f"❌ Error al validar {archivo.name}: {e}")
                resultados['errores'] += 1
        
        if puntuaciones:
            resultados['resumen']['puntuacion_promedio'] = round(sum(puntuaciones) / len(puntuaciones), 2)
        resultados['resumen']['total_errores'] = total_errores
        resultados['resumen']['total_advertencias'] = total_advertencias
        resultados['resumen']['total_sugerencias'] = total_sugerencias
        
        return resultados
    
    def generar_reporte(self, resultados: Dict, archivo_salida: str = "reporte_validacion.json") -> None:
        """Genera un reporte de validación."""
        reporte = {
            'fecha': datetime.now().isoformat(),
            'resultados': resultados
        }
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Reporte generado: {archivo_salida}")
        self._imprimir_resumen(resultados)
    
    def _imprimir_resumen(self, resultados: Dict) -> None:
        """Imprime un resumen de la validación."""
        print("\n" + "="*60)
        print("RESUMEN DE VALIDACIÓN")
        print("="*60)
        
        if 'resumen' in resultados:
            resumen = resultados['resumen']
            print(f"\n📊 Puntuación promedio: {resumen['puntuacion_promedio']}/100")
            print(f"❌ Total de errores: {resumen['total_errores']}")
            print(f"⚠️  Total de advertencias: {resumen['total_advertencias']}")
            print(f"💡 Total de sugerencias: {resumen['total_sugerencias']}")
        
        print(f"\n📁 Archivos validados: {resultados.get('validados', 0)}/{resultados.get('total', 0)}")
        
        if 'archivos' in resultados:
            print(f"\n📋 Top 5 archivos con mejor puntuación:")
            top_5 = sorted(resultados['archivos'], key=lambda x: x['puntuacion'], reverse=True)[:5]
            for i, archivo in enumerate(top_5, 1):
                print(f"   {i}. {archivo['archivo']}: {archivo['puntuacion']}/100")

def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Valida plantillas HTML de firmas de email')
    parser.add_argument('archivo', nargs='?', help='Archivo a validar (o directorio)')
    parser.add_argument('-d', '--directorio', action='store_true',
                       help='Validar todos los archivos en el directorio')
    parser.add_argument('-o', '--output', default='reporte_validacion.json',
                       help='Archivo de salida para el reporte')
    
    args = parser.parse_args()
    
    validador = ValidadorAvanzado()
    
    if args.directorio or (args.archivo and Path(args.archivo).is_dir()):
        directorio = args.archivo or '.'
        resultados = validador.validar_directorio(directorio)
        validador.generar_reporte(resultados, args.output)
    elif args.archivo:
        resultado = validador.validar_archivo(args.archivo)
        print(f"\n📊 Puntuación: {resultado['puntuacion']}/100")
        print(f"❌ Errores: {resultado['total_errores']}")
        print(f"⚠️  Advertencias: {resultado['total_advertencias']}")
        print(f"💡 Sugerencias: {resultado['total_sugerencias']}")
        
        if resultado['errores']:
            print(f"\n❌ Errores encontrados:")
            for error in resultado['errores']:
                print(f"   - {error}")
        
        if resultado['advertencias']:
            print(f"\n⚠️  Advertencias:")
            for advertencia in resultado['advertencias']:
                print(f"   - {advertencia}")
    else:
        print("❌ Especifica un archivo o directorio para validar")
        print("   Uso: python validador_avanzado.py <archivo>")
        print("   O: python validador_avanzado.py -d [directorio]")

if __name__ == "__main__":
    main()





