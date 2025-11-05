#!/usr/bin/env python3
"""
Script de Mantenimiento Automático para Organización de Documentos
================================================================

Este script automatiza el mantenimiento de la estructura organizacional:
- Actualiza índices automáticamente
- Verifica integridad de archivos
- Genera reportes de estadísticas
- Mantiene documentación actualizada

Autor: Sistema de Organización Automática
Versión: 1.0
Fecha: 2024
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
import subprocess

class MantenimientoAutomatico:
    def __init__(self, base_path="/Users/adan/frontier/docuementos"):
        self.base_path = Path(base_path)
        self.stats = {
            "total_archivos": 0,
            "total_carpetas": 0,
            "archivos_por_tipo": {},
            "archivos_por_carpeta": {},
            "ultima_actualizacion": datetime.now().isoformat()
        }
    
    def escanear_estructura(self):
        """Escanea toda la estructura de archivos y carpetas"""
        print("🔍 Escaneando estructura de archivos...")
        
        for root, dirs, files in os.walk(self.base_path):
            # Contar carpetas
            if root != str(self.base_path):
                self.stats["total_carpetas"] += 1
            
            # Contar archivos
            for file in files:
                self.stats["total_archivos"] += 1
                
                # Estadísticas por tipo
                extension = Path(file).suffix.lower()
                if extension not in self.stats["archivos_por_tipo"]:
                    self.stats["archivos_por_tipo"][extension] = 0
                self.stats["archivos_por_tipo"][extension] += 1
                
                # Estadísticas por carpeta
                carpeta = Path(root).name
                if carpeta not in self.stats["archivos_por_carpeta"]:
                    self.stats["archivos_por_carpeta"][carpeta] = 0
                self.stats["archivos_por_carpeta"][carpeta] += 1
        
        print(f"✅ Escaneo completado: {self.stats['total_archivos']} archivos en {self.stats['total_carpetas']} carpetas")
    
    def verificar_integridad(self):
        """Verifica la integridad de archivos importantes"""
        print("🔍 Verificando integridad de archivos...")
        
        archivos_criticos = [
            "ORGANIZACION_ARCHIVOS.md",
            "INDICE_BUSQUEDA_GLOBAL.md",
            "ACCESO_RAPIDO.md"
        ]
        
        archivos_faltantes = []
        for archivo in archivos_criticos:
            ruta = self.base_path / archivo
            if not ruta.exists():
                archivos_faltantes.append(archivo)
        
        if archivos_faltantes:
            print(f"⚠️  Archivos críticos faltantes: {archivos_faltantes}")
            return False
        else:
            print("✅ Todos los archivos críticos están presentes")
            return True
    
    def actualizar_indices(self):
        """Actualiza los índices de búsqueda y navegación"""
        print("📝 Actualizando índices...")
        
        # Actualizar estadísticas en ORGANIZACION_ARCHIVOS.md
        self.actualizar_estadisticas_organizacion()
        
        # Actualizar índice de búsqueda
        self.actualizar_indice_busqueda()
        
        print("✅ Índices actualizados")
    
    def actualizar_estadisticas_organizacion(self):
        """Actualiza las estadísticas en el archivo de organización"""
        archivo_org = self.base_path / "ORGANIZACION_ARCHIVOS.md"
        
        if archivo_org.exists():
            with open(archivo_org, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Actualizar estadísticas
            contenido = contenido.replace(
                "*Total de archivos procesados: 755*",
                f"*Total de archivos procesados: {self.stats['total_archivos']}*"
            )
            
            with open(archivo_org, 'w', encoding='utf-8') as f:
                f.write(contenido)
    
    def actualizar_indice_busqueda(self):
        """Actualiza el índice de búsqueda global"""
        archivo_indice = self.base_path / "INDICE_BUSQUEDA_GLOBAL.md"
        
        if archivo_indice.exists():
            with open(archivo_indice, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Actualizar estadísticas
            contenido = contenido.replace(
                "*Total de archivos indexados: 755*",
                f"*Total de archivos indexados: {self.stats['total_archivos']}*"
            )
            
            with open(archivo_indice, 'w', encoding='utf-8') as f:
                f.write(contenido)
    
    def generar_reporte_estadisticas(self):
        """Genera un reporte detallado de estadísticas"""
        print("📊 Generando reporte de estadísticas...")
        
        reporte = f"""# 📊 Reporte de Estadísticas - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📈 Resumen General
- **Total de archivos**: {self.stats['total_archivos']}
- **Total de carpetas**: {self.stats['total_carpetas']}
- **Última actualización**: {self.stats['ultima_actualizacion']}

## 📁 Archivos por Tipo
"""
        
        for extension, cantidad in sorted(self.stats['archivos_por_tipo'].items()):
            reporte += f"- **{extension or 'Sin extensión'}**: {cantidad} archivos\n"
        
        reporte += "\n## 📂 Archivos por Carpeta\n"
        
        for carpeta, cantidad in sorted(self.stats['archivos_por_carpeta'].items()):
            reporte += f"- **{carpeta}**: {cantidad} archivos\n"
        
        reporte += f"""
## 🔍 Análisis de Distribución
- **Archivos más comunes**: {max(self.stats['archivos_por_tipo'].items(), key=lambda x: x[1])}
- **Carpeta con más archivos**: {max(self.stats['archivos_por_carpeta'].items(), key=lambda x: x[1])}
- **Promedio de archivos por carpeta**: {self.stats['total_archivos'] / max(1, self.stats['total_carpetas']):.1f}

---
*Reporte generado automáticamente por el sistema de mantenimiento*
"""
        
        # Guardar reporte
        reporte_path = self.base_path / "REPORTE_ESTADISTICAS.md"
        with open(reporte_path, 'w', encoding='utf-8') as f:
            f.write(reporte)
        
        print(f"✅ Reporte guardado en: {reporte_path}")
    
    def limpiar_archivos_temporales(self):
        """Limpia archivos temporales y duplicados"""
        print("🧹 Limpiando archivos temporales...")
        
        archivos_temporales = [
            "*.tmp", "*.temp", "*.bak", "*.backup", "*.old"
        ]
        
        archivos_eliminados = 0
        for patron in archivos_temporales:
            for archivo in self.base_path.rglob(patron):
                try:
                    archivo.unlink()
                    archivos_eliminados += 1
                    print(f"🗑️  Eliminado: {archivo.name}")
                except Exception as e:
                    print(f"⚠️  Error eliminando {archivo.name}: {e}")
        
        print(f"✅ {archivos_eliminados} archivos temporales eliminados")
    
    def ejecutar_mantenimiento_completo(self):
        """Ejecuta el mantenimiento completo del sistema"""
        print("🚀 Iniciando mantenimiento automático...")
        print("=" * 50)
        
        try:
            # 1. Escanear estructura
            self.escanear_estructura()
            
            # 2. Verificar integridad
            if not self.verificar_integridad():
                print("⚠️  Se encontraron problemas de integridad")
            
            # 3. Actualizar índices
            self.actualizar_indices()
            
            # 4. Generar reporte
            self.generar_reporte_estadisticas()
            
            # 5. Limpiar archivos temporales
            self.limpiar_archivos_temporales()
            
            print("=" * 50)
            print("✅ Mantenimiento automático completado exitosamente")
            
        except Exception as e:
            print(f"❌ Error durante el mantenimiento: {e}")
            return False
        
        return True

def main():
    """Función principal"""
    print("🔧 Sistema de Mantenimiento Automático")
    print("=====================================")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("/Users/adan/frontier/docuementos"):
        print("❌ Error: Directorio de documentos no encontrado")
        sys.exit(1)
    
    # Crear instancia del mantenimiento
    mantenimiento = MantenimientoAutomatico()
    
    # Ejecutar mantenimiento
    if mantenimiento.ejecutar_mantenimiento_completo():
        print("\n🎉 ¡Mantenimiento completado exitosamente!")
        print("📊 Revisa el REPORTE_ESTADISTICAS.md para ver los detalles")
    else:
        print("\n💥 Error durante el mantenimiento")
        sys.exit(1)

if __name__ == "__main__":
    main()






