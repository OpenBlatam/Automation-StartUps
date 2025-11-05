#!/usr/bin/env python3
"""
Auto Backup System - Sistema de Backup Automático
Crea backups automáticos e incrementales del sistema de archivos
"""

import os
import shutil
import json
import hashlib
import gzip
import tarfile
from datetime import datetime, timedelta
import argparse
from pathlib import Path

class AutoBackupSystem:
    def __init__(self, root_path=".", backup_dir="backups"):
        self.root_path = root_path
        self.backup_dir = backup_dir
        self.backup_metadata = {
            "timestamp": datetime.now().isoformat(),
            "backups_created": [],
            "total_size": 0,
            "compression_ratio": 0,
            "files_backed_up": 0
        }
        
        # Crear directorio de backups
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_file_hash(self, file_path):
        """Crea un hash MD5 del archivo"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return None
    
    def get_file_metadata(self, file_path):
        """Obtiene metadatos del archivo"""
        try:
            stat = os.stat(file_path)
            return {
                "path": file_path,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "hash": self.create_file_hash(file_path)
            }
        except:
            return None
    
    def create_incremental_backup(self, backup_name=None):
        """Crea un backup incremental"""
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        os.makedirs(backup_path, exist_ok=True)
        
        # Leer metadatos del backup anterior
        previous_metadata = self.load_backup_metadata()
        
        # Crear metadatos del backup actual
        current_metadata = {
            "timestamp": datetime.now().isoformat(),
            "files": {},
            "new_files": [],
            "modified_files": [],
            "deleted_files": []
        }
        
        # Escanear archivos actuales
        current_files = {}
        for root, dirs, files in os.walk(self.root_path):
            # Excluir directorios de backup
            dirs[:] = [d for d in dirs if d != 'backups']
            
            for file in files:
                if file.endswith('.md') or file.endswith('.py') or file.endswith('.sh'):
                    file_path = os.path.join(root, file)
                    metadata = self.get_file_metadata(file_path)
                    if metadata:
                        current_files[file_path] = metadata
        
        # Comparar con backup anterior
        if previous_metadata:
            previous_files = previous_metadata.get("files", {})
            
            # Archivos nuevos
            for file_path, metadata in current_files.items():
                if file_path not in previous_files:
                    current_metadata["new_files"].append(file_path)
                elif metadata["hash"] != previous_files[file_path]["hash"]:
                    current_metadata["modified_files"].append(file_path)
            
            # Archivos eliminados
            for file_path in previous_files:
                if file_path not in current_files:
                    current_metadata["deleted_files"].append(file_path)
        
        current_metadata["files"] = current_files
        
        # Crear backup solo de archivos modificados o nuevos
        files_to_backup = current_metadata["new_files"] + current_metadata["modified_files"]
        
        if not files_to_backup:
            print("📄 No hay cambios para respaldar")
            return None
        
        # Crear archivo de backup
        backup_file = os.path.join(backup_path, f"{backup_name}.tar.gz")
        
        with tarfile.open(backup_file, "w:gz") as tar:
            for file_path in files_to_backup:
                try:
                    # Crear ruta relativa en el backup
                    rel_path = os.path.relpath(file_path, self.root_path)
                    tar.add(file_path, arcname=rel_path)
                except Exception as e:
                    print(f"⚠️  Error respaldando {file_path}: {e}")
        
        # Guardar metadatos
        metadata_file = os.path.join(backup_path, "metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(current_metadata, f, indent=2, ensure_ascii=False)
        
        # Calcular estadísticas
        backup_size = os.path.getsize(backup_file)
        original_size = sum(current_files[f]["size"] for f in files_to_backup)
        compression_ratio = (1 - backup_size / original_size) * 100 if original_size > 0 else 0
        
        backup_info = {
            "name": backup_name,
            "path": backup_file,
            "size": backup_size,
            "original_size": original_size,
            "compression_ratio": compression_ratio,
            "files_count": len(files_to_backup),
            "new_files": len(current_metadata["new_files"]),
            "modified_files": len(current_metadata["modified_files"]),
            "deleted_files": len(current_metadata["deleted_files"])
        }
        
        self.backup_metadata["backups_created"].append(backup_info)
        self.backup_metadata["total_size"] += backup_size
        self.backup_metadata["files_backed_up"] += len(files_to_backup)
        
        print(f"✅ Backup incremental creado: {backup_name}")
        print(f"   📁 Archivos respaldados: {len(files_to_backup)}")
        print(f"   💾 Tamaño: {backup_size:,} bytes")
        print(f"   📊 Compresión: {compression_ratio:.1f}%")
        
        return backup_info
    
    def create_full_backup(self, backup_name=None):
        """Crea un backup completo"""
        if not backup_name:
            backup_name = f"full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        os.makedirs(backup_path, exist_ok=True)
        
        # Crear metadatos del backup
        current_metadata = {
            "timestamp": datetime.now().isoformat(),
            "type": "full",
            "files": {}
        }
        
        # Escanear todos los archivos
        all_files = []
        for root, dirs, files in os.walk(self.root_path):
            # Excluir directorios de backup
            dirs[:] = [d for d in dirs if d != 'backups']
            
            for file in files:
                if file.endswith('.md') or file.endswith('.py') or file.endswith('.sh'):
                    file_path = os.path.join(root, file)
                    metadata = self.get_file_metadata(file_path)
                    if metadata:
                        current_metadata["files"][file_path] = metadata
                        all_files.append(file_path)
        
        # Crear archivo de backup
        backup_file = os.path.join(backup_path, f"{backup_name}.tar.gz")
        
        with tarfile.open(backup_file, "w:gz") as tar:
            for file_path in all_files:
                try:
                    rel_path = os.path.relpath(file_path, self.root_path)
                    tar.add(file_path, arcname=rel_path)
                except Exception as e:
                    print(f"⚠️  Error respaldando {file_path}: {e}")
        
        # Guardar metadatos
        metadata_file = os.path.join(backup_path, "metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(current_metadata, f, indent=2, ensure_ascii=False)
        
        # Calcular estadísticas
        backup_size = os.path.getsize(backup_file)
        original_size = sum(current_metadata["files"][f]["size"] for f in all_files)
        compression_ratio = (1 - backup_size / original_size) * 100 if original_size > 0 else 0
        
        backup_info = {
            "name": backup_name,
            "path": backup_file,
            "size": backup_size,
            "original_size": original_size,
            "compression_ratio": compression_ratio,
            "files_count": len(all_files),
            "type": "full"
        }
        
        self.backup_metadata["backups_created"].append(backup_info)
        self.backup_metadata["total_size"] += backup_size
        self.backup_metadata["files_backed_up"] += len(all_files)
        
        print(f"✅ Backup completo creado: {backup_name}")
        print(f"   📁 Archivos respaldados: {len(all_files)}")
        print(f"   💾 Tamaño: {backup_size:,} bytes")
        print(f"   📊 Compresión: {compression_ratio:.1f}%")
        
        return backup_info
    
    def load_backup_metadata(self):
        """Carga metadatos del último backup"""
        # Buscar el último backup
        backup_dirs = [d for d in os.listdir(self.backup_dir) if os.path.isdir(os.path.join(self.backup_dir, d))]
        if not backup_dirs:
            return None
        
        # Ordenar por fecha de modificación
        backup_dirs.sort(key=lambda x: os.path.getmtime(os.path.join(self.backup_dir, x)), reverse=True)
        
        # Cargar metadatos del último backup
        latest_backup = backup_dirs[0]
        metadata_file = os.path.join(self.backup_dir, latest_backup, "metadata.json")
        
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        
        return None
    
    def restore_backup(self, backup_name, restore_path=None):
        """Restaura un backup"""
        if not restore_path:
            restore_path = self.root_path
        
        backup_dir = os.path.join(self.backup_dir, backup_name)
        backup_file = os.path.join(backup_dir, f"{backup_name}.tar.gz")
        
        if not os.path.exists(backup_file):
            print(f"❌ Backup no encontrado: {backup_name}")
            return False
        
        try:
            with tarfile.open(backup_file, "r:gz") as tar:
                tar.extractall(restore_path)
            
            print(f"✅ Backup restaurado: {backup_name}")
            print(f"   📁 Restaurado en: {restore_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error restaurando backup: {e}")
            return False
    
    def list_backups(self):
        """Lista todos los backups disponibles"""
        backup_dirs = [d for d in os.listdir(self.backup_dir) if os.path.isdir(os.path.join(self.backup_dir, d))]
        
        if not backup_dirs:
            print("📄 No hay backups disponibles")
            return []
        
        # Ordenar por fecha de modificación
        backup_dirs.sort(key=lambda x: os.path.getmtime(os.path.join(self.backup_dir, x)), reverse=True)
        
        print("📋 Backups disponibles:")
        for i, backup_dir in enumerate(backup_dirs, 1):
            backup_path = os.path.join(self.backup_dir, backup_dir)
            backup_file = os.path.join(backup_path, f"{backup_dir}.tar.gz")
            
            if os.path.exists(backup_file):
                size = os.path.getsize(backup_file)
                modified = datetime.fromtimestamp(os.path.getmtime(backup_file))
                
                print(f"  {i}. {backup_dir}")
                print(f"     📅 Fecha: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"     💾 Tamaño: {size:,} bytes")
                print(f"     📁 Archivo: {backup_file}")
                print()
        
        return backup_dirs
    
    def cleanup_old_backups(self, keep_days=30):
        """Limpia backups antiguos"""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        backup_dirs = [d for d in os.listdir(self.backup_dir) if os.path.isdir(os.path.join(self.backup_dir, d))]
        
        removed_count = 0
        for backup_dir in backup_dirs:
            backup_path = os.path.join(self.backup_dir, backup_dir)
            backup_file = os.path.join(backup_path, f"{backup_dir}.tar.gz")
            
            if os.path.exists(backup_file):
                modified = datetime.fromtimestamp(os.path.getmtime(backup_file))
                if modified < cutoff_date:
                    try:
                        shutil.rmtree(backup_path)
                        removed_count += 1
                        print(f"🗑️  Backup eliminado: {backup_dir}")
                    except Exception as e:
                        print(f"⚠️  Error eliminando {backup_dir}: {e}")
        
        print(f"✅ {removed_count} backups antiguos eliminados")
        return removed_count
    
    def save_report(self, output_file="backup_report.json"):
        """Guarda el reporte de backups"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.backup_metadata, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Reporte guardado en {output_file}")
    
    def print_summary(self):
        """Imprime un resumen de los backups"""
        print("\n" + "="*60)
        print("📊 RESUMEN DEL SISTEMA DE BACKUP")
        print("="*60)
        
        print(f"📁 Directorio de backups: {self.backup_dir}")
        print(f"📄 Total backups creados: {len(self.backup_metadata['backups_created'])}")
        print(f"💾 Tamaño total: {self.backup_metadata['total_size']:,} bytes")
        print(f"📊 Archivos respaldados: {self.backup_metadata['files_backed_up']}")
        
        if self.backup_metadata['backups_created']:
            print("\n📋 Últimos backups:")
            for backup in self.backup_metadata['backups_created'][-5:]:
                print(f"  - {backup['name']}: {backup['size']:,} bytes ({backup['files_count']} archivos)")

def main():
    parser = argparse.ArgumentParser(description='Sistema de backup automático')
    parser.add_argument('--path', default='.', help='Ruta del directorio a respaldar')
    parser.add_argument('--backup-dir', default='backups', help='Directorio de backups')
    parser.add_argument('--type', choices=['incremental', 'full'], default='incremental', help='Tipo de backup')
    parser.add_argument('--name', help='Nombre del backup')
    parser.add_argument('--list', action='store_true', help='Listar backups disponibles')
    parser.add_argument('--restore', help='Restaurar backup')
    parser.add_argument('--cleanup', type=int, help='Limpiar backups más antiguos que N días')
    parser.add_argument('--output', default='backup_report.json', help='Archivo de reporte')
    
    args = parser.parse_args()
    
    backup_system = AutoBackupSystem(args.path, args.backup_dir)
    
    if args.list:
        backup_system.list_backups()
    elif args.restore:
        backup_system.restore_backup(args.restore)
    elif args.cleanup:
        backup_system.cleanup_old_backups(args.cleanup)
    else:
        if args.type == 'full':
            backup_system.create_full_backup(args.name)
        else:
            backup_system.create_incremental_backup(args.name)
        
        backup_system.save_report(args.output)
        backup_system.print_summary()

if __name__ == "__main__":
    main()














