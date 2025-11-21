#!/usr/bin/env python3
"""
Gestor de Versiones de Plantillas
Gestiona versiones de plantillas HTML con control de cambios y comparación.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime
import hashlib

class GestorVersiones:
    def __init__(self, directorio_base: str = "."):
        self.directorio_base = Path(directorio_base)
        self.directorio_versiones = self.directorio_base / ".versiones"
        self.directorio_versiones.mkdir(exist_ok=True)
    
    def obtener_hash(self, contenido: str) -> str:
        """Obtiene el hash MD5 del contenido."""
        return hashlib.md5(contenido.encode('utf-8')).hexdigest()
    
    def guardar_version(self, archivo: str, contenido: str, descripcion: Optional[str] = None) -> Dict:
        """Guarda una versión de un archivo."""
        archivo_path = Path(archivo)
        nombre_base = archivo_path.stem
        
        # Crear directorio para este archivo
        dir_archivo = self.directorio_versiones / nombre_base
        dir_archivo.mkdir(exist_ok=True)
        
        # Obtener hash
        hash_contenido = self.obtener_hash(contenido)
        
        # Obtener número de versión
        versiones_existentes = list(dir_archivo.glob("v*.html"))
        if versiones_existentes:
            numeros = [int(f.stem[1:]) for f in versiones_existentes if f.stem[1:].isdigit()]
            siguiente_version = max(numeros) + 1 if numeros else 1
        else:
            siguiente_version = 1
        
        # Guardar versión
        archivo_version = dir_archivo / f"v{siguiente_version}.html"
        with open(archivo_version, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        # Guardar metadatos
        metadatos = {
            'version': siguiente_version,
            'fecha': datetime.now().isoformat(),
            'hash': hash_contenido,
            'tamaño': len(contenido),
            'lineas': len(contenido.split('\n')),
            'descripcion': descripcion or f"Versión {siguiente_version}"
        }
        
        archivo_metadatos = dir_archivo / f"v{siguiente_version}.json"
        with open(archivo_metadatos, 'w', encoding='utf-8') as f:
            json.dump(metadatos, f, indent=2, ensure_ascii=False)
        
        # Actualizar índice de versiones
        self._actualizar_indice(nombre_base, siguiente_version, metadatos)
        
        print(f"✅ Versión {siguiente_version} guardada: {archivo_version}")
        return metadatos
    
    def _actualizar_indice(self, nombre_base: str, version: int, metadatos: Dict) -> None:
        """Actualiza el índice de versiones."""
        archivo_indice = self.directorio_versiones / f"{nombre_base}_indice.json"
        
        if archivo_indice.exists():
            with open(archivo_indice, 'r', encoding='utf-8') as f:
                indice = json.load(f)
        else:
            indice = {
                'archivo': nombre_base,
                'versiones': []
            }
        
        indice['versiones'].append({
            'version': version,
            'fecha': metadatos['fecha'],
            'hash': metadatos['hash'],
            'descripcion': metadatos['descripcion']
        })
        
        # Ordenar por versión
        indice['versiones'].sort(key=lambda x: x['version'], reverse=True)
        
        with open(archivo_indice, 'w', encoding='utf-8') as f:
            json.dump(indice, f, indent=2, ensure_ascii=False)
    
    def listar_versiones(self, archivo: str) -> List[Dict]:
        """Lista todas las versiones de un archivo."""
        archivo_path = Path(archivo)
        nombre_base = archivo_path.stem
        archivo_indice = self.directorio_versiones / f"{nombre_base}_indice.json"
        
        if not archivo_indice.exists():
            return []
        
        with open(archivo_indice, 'r', encoding='utf-8') as f:
            indice = json.load(f)
        
        return indice.get('versiones', [])
    
    def obtener_version(self, archivo: str, version: int) -> Optional[str]:
        """Obtiene el contenido de una versión específica."""
        archivo_path = Path(archivo)
        nombre_base = archivo_path.stem
        archivo_version = self.directorio_versiones / nombre_base / f"v{version}.html"
        
        if not archivo_version.exists():
            return None
        
        with open(archivo_version, 'r', encoding='utf-8') as f:
            return f.read()
    
    def comparar_versiones(self, archivo: str, version1: int, version2: int) -> Dict:
        """Compara dos versiones de un archivo."""
        contenido1 = self.obtener_version(archivo, version1)
        contenido2 = self.obtener_version(archivo, version2)
        
        if contenido1 is None or contenido2 is None:
            return {'error': 'Una o ambas versiones no existen'}
        
        diferencias = {
            'version1': version1,
            'version2': version2,
            'tamaño1': len(contenido1),
            'tamaño2': len(contenido2),
            'diferencia_tamaño': len(contenido2) - len(contenido1),
            'lineas1': len(contenido1.split('\n')),
            'lineas2': len(contenido2.split('\n')),
            'diferencia_lineas': len(contenido2.split('\n')) - len(contenido1.split('\n')),
            'hash1': self.obtener_hash(contenido1),
            'hash2': self.obtener_hash(contenido2),
            'son_iguales': contenido1 == contenido2
        }
        
        # Comparar placeholders
        placeholders1 = set(re.findall(r'\[([^\]]+)\]', contenido1))
        placeholders2 = set(re.findall(r'\[([^\]]+)\]', contenido2))
        
        diferencias['placeholders_agregados'] = list(placeholders2 - placeholders1)
        diferencias['placeholders_removidos'] = list(placeholders1 - placeholders2)
        diferencias['placeholders_comunes'] = list(placeholders1 & placeholders2)
        
        # Comparar colores
        colores1 = set(re.findall(r'#([0-9a-fA-F]{3,6})', contenido1, re.IGNORECASE))
        colores2 = set(re.findall(r'#([0-9a-fA-F]{3,6})', contenido2, re.IGNORECASE))
        
        diferencias['colores_agregados'] = list(colores2 - colores1)
        diferencias['colores_removidos'] = list(colores1 - colores2)
        diferencias['colores_comunes'] = list(colores1 & colores2)
        
        return diferencias
    
    def restaurar_version(self, archivo: str, version: int, archivo_salida: Optional[str] = None) -> bool:
        """Restaura una versión específica."""
        contenido = self.obtener_version(archivo, version)
        
        if contenido is None:
            print(f"❌ Versión {version} no encontrada")
            return False
        
        if archivo_salida is None:
            archivo_salida = archivo
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        print(f"✅ Versión {version} restaurada en: {archivo_salida}")
        return True
    
    def eliminar_version(self, archivo: str, version: int) -> bool:
        """Elimina una versión específica."""
        archivo_path = Path(archivo)
        nombre_base = archivo_path.stem
        
        archivo_version = self.directorio_versiones / nombre_base / f"v{version}.html"
        archivo_metadatos = self.directorio_versiones / nombre_base / f"v{version}.json"
        
        if not archivo_version.exists():
            print(f"❌ Versión {version} no encontrada")
            return False
        
        archivo_version.unlink()
        if archivo_metadatos.exists():
            archivo_metadatos.unlink()
        
        # Actualizar índice
        archivo_indice = self.directorio_versiones / f"{nombre_base}_indice.json"
        if archivo_indice.exists():
            with open(archivo_indice, 'r', encoding='utf-8') as f:
                indice = json.load(f)
            
            indice['versiones'] = [v for v in indice['versiones'] if v['version'] != version]
            
            with open(archivo_indice, 'w', encoding='utf-8') as f:
                json.dump(indice, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Versión {version} eliminada")
        return True
    
    def generar_reporte_versiones(self, archivo: str, archivo_salida: str = "reporte_versiones.json") -> None:
        """Genera un reporte de todas las versiones."""
        versiones = self.listar_versiones(archivo)
        
        if not versiones:
            print(f"❌ No se encontraron versiones para {archivo}")
            return
        
        reporte = {
            'archivo': Path(archivo).name,
            'total_versiones': len(versiones),
            'versiones': versiones,
            'comparaciones': []
        }
        
        # Comparar versiones consecutivas
        for i in range(len(versiones) - 1):
            v1 = versiones[i + 1]['version']
            v2 = versiones[i]['version']
            comparacion = self.comparar_versiones(archivo, v1, v2)
            reporte['comparaciones'].append(comparacion)
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Reporte generado: {archivo_salida}")
        self._imprimir_resumen(reporte)
    
    def _imprimir_resumen(self, reporte: Dict) -> None:
        """Imprime un resumen del reporte."""
        print("\n" + "="*60)
        print("RESUMEN DE VERSIONES")
        print("="*60)
        print(f"\n📁 Archivo: {reporte['archivo']}")
        print(f"📊 Total de versiones: {reporte['total_versiones']}")
        
        print(f"\n📋 Versiones:")
        for version in reporte['versiones']:
            print(f"   v{version['version']}: {version['descripcion']} ({version['fecha'][:10]})")
        
        if reporte['comparaciones']:
            print(f"\n🔄 Cambios entre versiones:")
            for comp in reporte['comparaciones']:
                print(f"   v{comp['version1']} -> v{comp['version2']}:")
                print(f"     - Tamaño: {comp['diferencia_tamaño']:+d} bytes")
                print(f"     - Líneas: {comp['diferencia_lineas']:+d}")
                if comp['placeholders_agregados']:
                    print(f"     - Placeholders agregados: {len(comp['placeholders_agregados'])}")
                if comp['placeholders_removidos']:
                    print(f"     - Placeholders removidos: {len(comp['placeholders_removidos'])}")

def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gestiona versiones de plantillas HTML')
    parser.add_argument('archivo', help='Archivo a gestionar')
    parser.add_argument('accion', choices=['guardar', 'listar', 'obtener', 'comparar', 'restaurar', 'eliminar', 'reporte'],
                       help='Acción a realizar')
    parser.add_argument('-v', '--version', type=int, help='Número de versión')
    parser.add_argument('-v1', '--version1', type=int, help='Primera versión para comparar')
    parser.add_argument('-v2', '--version2', type=int, help='Segunda versión para comparar')
    parser.add_argument('-d', '--descripcion', help='Descripción de la versión')
    parser.add_argument('-o', '--output', help='Archivo de salida')
    
    args = parser.parse_args()
    
    gestor = GestorVersiones()
    
    if args.accion == 'guardar':
        with open(args.archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        gestor.guardar_version(args.archivo, contenido, args.descripcion)
    
    elif args.accion == 'listar':
        versiones = gestor.listar_versiones(args.archivo)
        print(f"\n📋 Versiones de {Path(args.archivo).name}:")
        for v in versiones:
            print(f"   v{v['version']}: {v['descripcion']} ({v['fecha'][:10]})")
    
    elif args.accion == 'obtener':
        if not args.version:
            print("❌ Especifica el número de versión con -v")
            return
        contenido = gestor.obtener_version(args.archivo, args.version)
        if contenido:
            archivo_salida = args.output or f"{Path(args.archivo).stem}_v{args.version}.html"
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                f.write(contenido)
            print(f"✅ Versión {args.version} guardada en: {archivo_salida}")
    
    elif args.accion == 'comparar':
        if not args.version1 or not args.version2:
            print("❌ Especifica ambas versiones con -v1 y -v2")
            return
        diferencias = gestor.comparar_versiones(args.archivo, args.version1, args.version2)
        print(f"\n📊 Comparación v{args.version1} vs v{args.version2}:")
        print(json.dumps(diferencias, indent=2, ensure_ascii=False))
    
    elif args.accion == 'restaurar':
        if not args.version:
            print("❌ Especifica el número de versión con -v")
            return
        gestor.restaurar_version(args.archivo, args.version, args.output)
    
    elif args.accion == 'eliminar':
        if not args.version:
            print("❌ Especifica el número de versión con -v")
            return
        gestor.eliminar_version(args.archivo, args.version)
    
    elif args.accion == 'reporte':
        gestor.generar_reporte_versiones(args.archivo, args.output or "reporte_versiones.json")

if __name__ == "__main__":
    main()





