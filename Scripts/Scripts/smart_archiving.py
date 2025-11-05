#!/usr/bin/env python3
"""
Smart Archiving System - Sistema de Archivado Inteligente
Archiva automáticamente archivos basado en patrones de uso y contenido
"""

import os
import shutil
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
import argparse

class SmartArchivingSystem:
    def __init__(self, root_path=".", archive_dir="archives"):
        self.root_path = root_path
        self.archive_dir = archive_dir
        self.archive_results = {
            "timestamp": datetime.now().isoformat(),
            "files_archived": [],
            "archives_created": [],
            "total_size_archived": 0,
            "archiving_rules": []
        }
        
        # Crear directorio de archivos
        os.makedirs(archive_dir, exist_ok=True)
    
    def analyze_file_for_archiving(self, file_path):
        """Analiza un archivo para determinar si debe ser archivado"""
        try:
            stat = os.stat(file_path)
            file_size = stat.st_size
            last_modified = datetime.fromtimestamp(stat.st_mtime)
            last_accessed = datetime.fromtimestamp(stat.st_atime)
            
            # Calcular edad del archivo
            age_days = (datetime.now() - last_modified).days
            access_age_days = (datetime.now() - last_accessed).days
            
            analysis = {
                "file_path": file_path,
                "filename": os.path.basename(file_path),
                "size": file_size,
                "last_modified": last_modified.isoformat(),
                "last_accessed": last_accessed.isoformat(),
                "age_days": age_days,
                "access_age_days": access_age_days,
                "archive_priority": "low",
                "archive_reason": "",
                "archive_category": "general"
            }
            
            # Determinar prioridad de archivado
            priority, reason, category = self.determine_archive_priority(
                file_path, file_size, age_days, access_age_days
            )
            
            analysis["archive_priority"] = priority
            analysis["archive_reason"] = reason
            analysis["archive_category"] = category
            
            return analysis
            
        except Exception as e:
            print(f"Error analizando {file_path}: {e}")
            return None
    
    def determine_archive_priority(self, file_path, file_size, age_days, access_age_days):
        """Determina la prioridad de archivado basada en varios factores"""
        filename = os.path.basename(file_path).lower()
        path_lower = file_path.lower()
        
        # Archivos muy antiguos y no accedidos
        if age_days > 365 and access_age_days > 180:
            return "high", "Archivo muy antiguo y no accedido", "old_unused"
        
        # Archivos grandes y antiguos
        if file_size > 1000000 and age_days > 90:  # > 1MB y > 3 meses
            return "high", "Archivo grande y antiguo", "large_old"
        
        # Archivos de versiones antiguas
        if re.search(r'v\d+\.\d+', filename) or re.search(r'_\d{4}_\d{2}_\d{2}', filename):
            return "medium", "Archivo de versión antigua", "version_old"
        
        # Archivos de backup
        if any(word in filename for word in ['backup', 'old', 'copy', 'temp', 'tmp']):
            return "high", "Archivo de backup temporal", "backup"
        
        # Archivos de documentación antigua
        if any(word in filename for word in ['readme', 'doc', 'manual', 'guide']):
            if age_days > 180:
                return "medium", "Documentación antigua", "old_docs"
        
        # Archivos de logs
        if filename.endswith('.log') or 'log' in filename:
            if age_days > 30:
                return "high", "Archivo de log antiguo", "logs"
        
        # Archivos de configuración antigua
        if any(word in filename for word in ['config', 'conf', 'settings']):
            if age_days > 90:
                return "medium", "Configuración antigua", "old_config"
        
        # Archivos de datos antiguos
        if any(word in filename for word in ['data', 'export', 'dump']):
            if age_days > 60:
                return "medium", "Datos antiguos", "old_data"
        
        # Archivos no accedidos por mucho tiempo
        if access_age_days > 90:
            return "low", "Archivo no accedido recientemente", "unused"
        
        return "none", "No requiere archivado", "active"
    
    def create_archive_structure(self, category, year=None, month=None):
        """Crea la estructura de directorios para el archivo"""
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month
        
        archive_path = os.path.join(self.archive_dir, str(year), f"{month:02d}", category)
        os.makedirs(archive_path, exist_ok=True)
        
        return archive_path
    
    def archive_file(self, file_analysis, move_instead_of_copy=False):
        """Archiva un archivo individual"""
        try:
            file_path = file_analysis["file_path"]
            category = file_analysis["archive_category"]
            
            # Crear estructura de archivo
            archive_path = self.create_archive_structure(category)
            
            # Determinar nombre del archivo en el archivo
            filename = file_analysis["filename"]
            archive_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            archive_file_path = os.path.join(archive_path, archive_filename)
            
            # Mover o copiar archivo
            if move_instead_of_copy:
                shutil.move(file_path, archive_file_path)
                operation = "moved"
            else:
                shutil.copy2(file_path, archive_file_path)
                operation = "copied"
            
            # Crear metadatos del archivo
            metadata = {
                "original_path": file_path,
                "archive_path": archive_file_path,
                "archived_date": datetime.now().isoformat(),
                "file_analysis": file_analysis,
                "operation": operation
            }
            
            metadata_file = archive_file_path + ".metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            result = {
                "original_path": file_path,
                "archive_path": archive_file_path,
                "category": category,
                "size": file_analysis["size"],
                "operation": operation,
                "archived_date": datetime.now().isoformat()
            }
            
            self.archive_results["files_archived"].append(result)
            self.archive_results["total_size_archived"] += file_analysis["size"]
            
            return result
            
        except Exception as e:
            print(f"Error archivando {file_analysis['file_path']}: {e}")
            return None
    
    def archive_directory(self, priority_threshold="medium", move_instead_of_copy=False, dry_run=False):
        """Archiva archivos en un directorio basado en prioridad"""
        print(f"🔍 Analizando archivos para archivado (prioridad >= {priority_threshold})...")
        
        files_to_archive = []
        
        # Encontrar archivos para analizar
        for root, dirs, files in os.walk(self.root_path):
            # Excluir directorios de archivo y backup
            dirs[:] = [d for d in dirs if d not in ['archives', 'backups', 'compressed']]
            
            for file in files:
                if file.endswith('.md') or file.endswith('.txt') or file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    analysis = self.analyze_file_for_archiving(file_path)
                    
                    if analysis and analysis["archive_priority"] != "none":
                        # Verificar si cumple con el umbral de prioridad
                        if self.priority_meets_threshold(analysis["archive_priority"], priority_threshold):
                            files_to_archive.append(analysis)
        
        print(f"📄 Encontrados {len(files_to_archive)} archivos para archivar")
        
        if dry_run:
            print("\n🔍 MODO DRY RUN - No se realizarán cambios:")
            for analysis in files_to_archive:
                print(f"  - {analysis['filename']}: {analysis['archive_priority']} - {analysis['archive_reason']}")
            return
        
        # Archivar archivos
        for analysis in files_to_archive:
            print(f"📦 Archivando: {analysis['filename']} ({analysis['archive_priority']})")
            result = self.archive_file(analysis, move_instead_of_copy)
            if result:
                print(f"   ✅ {result['operation']} a {result['archive_path']}")
        
        return self.archive_results
    
    def priority_meets_threshold(self, priority, threshold):
        """Verifica si la prioridad cumple con el umbral"""
        priority_levels = {"none": 0, "low": 1, "medium": 2, "high": 3}
        return priority_levels.get(priority, 0) >= priority_levels.get(threshold, 0)
    
    def restore_file(self, archive_path, restore_path=None):
        """Restaura un archivo desde el archivo"""
        try:
            # Buscar archivo de metadatos
            metadata_file = archive_path + ".metadata.json"
            
            if not os.path.exists(metadata_file):
                print(f"❌ No se encontraron metadatos para {archive_path}")
                return None
            
            # Leer metadatos
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Determinar ruta de restauración
            if not restore_path:
                restore_path = metadata["original_path"]
            
            # Restaurar archivo
            shutil.copy2(archive_path, restore_path)
            
            print(f"✅ Archivo restaurado: {restore_path}")
            return restore_path
            
        except Exception as e:
            print(f"❌ Error restaurando {archive_path}: {e}")
            return None
    
    def list_archives(self, category=None, year=None):
        """Lista archivos archivados"""
        archives = []
        
        for root, dirs, files in os.walk(self.archive_dir):
            for file in files:
                if file.endswith('.metadata.json'):
                    metadata_file = os.path.join(root, file)
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        # Filtrar por categoría si se especifica
                        if category and metadata["file_analysis"]["archive_category"] != category:
                            continue
                        
                        # Filtrar por año si se especifica
                        if year and not metadata["archived_date"].startswith(str(year)):
                            continue
                        
                        archives.append(metadata)
                    except:
                        continue
        
        # Ordenar por fecha de archivado
        archives.sort(key=lambda x: x["archived_date"], reverse=True)
        
        return archives
    
    def cleanup_old_archives(self, days_threshold=365):
        """Limpia archivos archivados muy antiguos"""
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        cleaned_count = 0
        
        for root, dirs, files in os.walk(self.archive_dir):
            for file in files:
                if file.endswith('.metadata.json'):
                    metadata_file = os.path.join(root, file)
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        archived_date = datetime.fromisoformat(metadata["archived_date"])
                        
                        if archived_date < cutoff_date:
                            # Eliminar archivo y metadatos
                            archive_file = metadata["archive_path"]
                            if os.path.exists(archive_file):
                                os.remove(archive_file)
                            os.remove(metadata_file)
                            cleaned_count += 1
                            
                    except:
                        continue
        
        print(f"🗑️  {cleaned_count} archivos archivados antiguos eliminados")
        return cleaned_count
    
    def save_report(self, output_file="archiving_report.json"):
        """Guarda el reporte de archivado"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.archive_results, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Reporte guardado en {output_file}")
    
    def print_summary(self):
        """Imprime un resumen del archivado"""
        results = self.archive_results
        
        print("\n" + "="*60)
        print("📊 RESUMEN DEL ARCHIVADO INTELIGENTE")
        print("="*60)
        
        print(f"📦 Archivos archivados: {len(results['files_archived'])}")
        print(f"💾 Tamaño total archivado: {results['total_size_archived']:,} bytes")
        print(f"📁 Directorio de archivos: {self.archive_dir}")
        
        if results["files_archived"]:
            print("\n📋 Archivos archivados:")
            for file_info in results["files_archived"][:10]:  # Mostrar solo los primeros 10
                filename = os.path.basename(file_info["original_path"])
                print(f"  - {filename}: {file_info['category']} ({file_info['operation']})")
            
            if len(results["files_archived"]) > 10:
                print(f"  ... y {len(results['files_archived']) - 10} archivos más")

def main():
    parser = argparse.ArgumentParser(description='Sistema de archivado inteligente')
    parser.add_argument('--path', default='.', help='Ruta del directorio a analizar')
    parser.add_argument('--priority', default='medium', choices=['low', 'medium', 'high'], help='Umbral de prioridad para archivado')
    parser.add_argument('--move', action='store_true', help='Mover archivos en lugar de copiarlos')
    parser.add_argument('--dry-run', action='store_true', help='Mostrar qué se archivaría sin hacer cambios')
    parser.add_argument('--list', action='store_true', help='Listar archivos archivados')
    parser.add_argument('--restore', help='Restaurar archivo específico')
    parser.add_argument('--cleanup', type=int, help='Limpiar archivos archivados más antiguos que N días')
    parser.add_argument('--output', default='archiving_report.json', help='Archivo de reporte')
    
    args = parser.parse_args()
    
    archiver = SmartArchivingSystem(args.path)
    
    if args.list:
        archives = archiver.list_archives()
        print("📦 Archivos archivados:")
        for archive in archives[:20]:  # Mostrar solo los primeros 20
            filename = os.path.basename(archive["original_path"])
            archived_date = archive["archived_date"][:10]
            print(f"  - {filename} ({archived_date}) - {archive['file_analysis']['archive_category']}")
    elif args.restore:
        archiver.restore_file(args.restore)
    elif args.cleanup:
        archiver.cleanup_old_archives(args.cleanup)
    else:
        results = archiver.archive_directory(args.priority, args.move, args.dry_run)
        if not args.dry_run:
            archiver.save_report(args.output)
            archiver.print_summary()

if __name__ == "__main__":
    main()














