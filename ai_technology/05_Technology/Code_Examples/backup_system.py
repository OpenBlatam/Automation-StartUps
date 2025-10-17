#!/usr/bin/env python3
"""
Sistema de backup y recuperación para el sistema de organización empresarial
"""

import os
import shutil
import json
import zipfile
from datetime import datetime
import hashlib

class BackupSystem:
    def __init__(self, base_path="/Users/adan/frontier"):
        self.base_path = base_path
        self.backup_dir = os.path.join(base_path, "backups")
        self.metadata_file = os.path.join(self.backup_dir, "backup_metadata.json")
        self.business_areas = [
            '01_Marketing', '02_Finance', '03_Human_Resources', '04_Operations',
            '05_Technology', '06_Strategy', '07_Risk_Management', '08_AI_Artificial_Intelligence',
            '09_Sales', '10_Customer_Service', '11_Research_Development', '12_Quality_Assurance',
            '13_Legal_Compliance', '14_Procurement', '15_Logistics', '16_Data_Analytics',
            '17_Innovation', '18_Sustainability', '19_International_Business', '20_Project_Management'
        ]
        
        # Crear directorio de backups si no existe
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def calculate_file_hash(self, file_path):
        """Calcular hash MD5 de un archivo"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return None
    
    def get_file_stats(self, file_path):
        """Obtener estadísticas de un archivo"""
        try:
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'hash': self.calculate_file_hash(file_path)
            }
        except Exception:
            return None
    
    def create_backup(self, backup_name=None):
        """Crear backup del sistema"""
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            # Crear directorio de backup
            os.makedirs(backup_path, exist_ok=True)
            
            # Backup de archivos de sistema
            system_files = [
                'README.md', 'NAVIGATION.md', 'DASHBOARD.md', 
                'ORGANIZATION_SUMMARY.md', 'FINAL_ORGANIZATION_REPORT.md',
                'search_documents.py', 'auto_organize.py', 'backup_system.py'
            ]
            
            for file in system_files:
                if os.path.exists(os.path.join(self.base_path, file)):
                    shutil.copy2(os.path.join(self.base_path, file), backup_path)
            
            # Backup de áreas de negocio
            backup_stats = {
                'timestamp': datetime.now().isoformat(),
                'backup_name': backup_name,
                'areas': {},
                'total_files': 0,
                'total_size': 0
            }
            
            for area in self.business_areas:
                area_path = os.path.join(self.base_path, area)
                if os.path.exists(area_path):
                    area_backup_path = os.path.join(backup_path, area)
                    shutil.copytree(area_path, area_backup_path)
                    
                    # Calcular estadísticas del área
                    area_stats = {
                        'files': 0,
                        'size': 0,
                        'file_list': []
                    }
                    
                    for root, dirs, files in os.walk(area_backup_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            file_stats = self.get_file_stats(file_path)
                            if file_stats:
                                area_stats['files'] += 1
                                area_stats['size'] += file_stats['size']
                                area_stats['file_list'].append({
                                    'name': file,
                                    'path': os.path.relpath(file_path, backup_path),
                                    'stats': file_stats
                                })
                    
                    backup_stats['areas'][area] = area_stats
                    backup_stats['total_files'] += area_stats['files']
                    backup_stats['total_size'] += area_stats['size']
            
            # Guardar metadata del backup
            metadata_path = os.path.join(backup_path, 'backup_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(backup_stats, f, indent=2)
            
            # Actualizar metadata global
            self.update_global_metadata(backup_name, backup_stats)
            
            print(f"✅ Backup creado exitosamente: {backup_name}")
            print(f"📁 Ubicación: {backup_path}")
            print(f"📊 Archivos: {backup_stats['total_files']}")
            print(f"💾 Tamaño: {backup_stats['total_size'] / 1024 / 1024:.2f} MB")
            
            return True, backup_stats
            
        except Exception as e:
            print(f"❌ Error creando backup: {e}")
            return False, None
    
    def update_global_metadata(self, backup_name, backup_stats):
        """Actualizar metadata global de backups"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                global_metadata = json.load(f)
        else:
            global_metadata = {'backups': []}
        
        global_metadata['backups'].append({
            'name': backup_name,
            'timestamp': backup_stats['timestamp'],
            'total_files': backup_stats['total_files'],
            'total_size': backup_stats['total_size']
        })
        
        # Mantener solo los últimos 10 backups
        if len(global_metadata['backups']) > 10:
            global_metadata['backups'] = global_metadata['backups'][-10:]
        
        with open(self.metadata_file, 'w') as f:
            json.dump(global_metadata, f, indent=2)
    
    def list_backups(self):
        """Listar backups disponibles"""
        if not os.path.exists(self.metadata_file):
            print("📋 No hay backups disponibles.")
            return []
        
        with open(self.metadata_file, 'r') as f:
            global_metadata = json.load(f)
        
        backups = global_metadata.get('backups', [])
        
        if backups:
            print("📋 Backups disponibles:")
            print("=" * 60)
            for i, backup in enumerate(reversed(backups), 1):
                size_mb = backup['total_size'] / 1024 / 1024
                print(f"{i}. {backup['name']}")
                print(f"   📅 Fecha: {backup['timestamp']}")
                print(f"   📊 Archivos: {backup['total_files']}")
                print(f"   💾 Tamaño: {size_mb:.2f} MB")
                print("-" * 60)
        else:
            print("📋 No hay backups disponibles.")
        
        return backups
    
    def restore_backup(self, backup_name):
        """Restaurar desde backup"""
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        if not os.path.exists(backup_path):
            print(f"❌ Backup no encontrado: {backup_name}")
            return False
        
        try:
            print(f"🔄 Restaurando backup: {backup_name}")
            
            # Restaurar archivos de sistema
            system_files = [
                'README.md', 'NAVIGATION.md', 'DASHBOARD.md', 
                'ORGANIZATION_SUMMARY.md', 'FINAL_ORGANIZATION_REPORT.md',
                'search_documents.py', 'auto_organize.py', 'backup_system.py'
            ]
            
            for file in system_files:
                backup_file = os.path.join(backup_path, file)
                if os.path.exists(backup_file):
                    shutil.copy2(backup_file, self.base_path)
            
            # Restaurar áreas de negocio
            for area in self.business_areas:
                area_backup_path = os.path.join(backup_path, area)
                if os.path.exists(area_backup_path):
                    area_path = os.path.join(self.base_path, area)
                    
                    # Eliminar área existente si existe
                    if os.path.exists(area_path):
                        shutil.rmtree(area_path)
                    
                    # Restaurar desde backup
                    shutil.copytree(area_backup_path, area_path)
            
            print(f"✅ Backup restaurado exitosamente: {backup_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error restaurando backup: {e}")
            return False
    
    def create_compressed_backup(self, backup_name=None):
        """Crear backup comprimido"""
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        zip_path = os.path.join(self.backup_dir, f"{backup_name}.zip")
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Comprimir archivos de sistema
                system_files = [
                    'README.md', 'NAVIGATION.md', 'DASHBOARD.md', 
                    'ORGANIZATION_SUMMARY.md', 'FINAL_ORGANIZATION_REPORT.md',
                    'search_documents.py', 'auto_organize.py', 'backup_system.py'
                ]
                
                for file in system_files:
                    file_path = os.path.join(self.base_path, file)
                    if os.path.exists(file_path):
                        zipf.write(file_path, file)
                
                # Comprimir áreas de negocio
                for area in self.business_areas:
                    area_path = os.path.join(self.base_path, area)
                    if os.path.exists(area_path):
                        for root, dirs, files in os.walk(area_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, self.base_path)
                                zipf.write(file_path, arcname)
            
            # Obtener tamaño del archivo comprimido
            compressed_size = os.path.getsize(zip_path)
            
            print(f"✅ Backup comprimido creado: {backup_name}.zip")
            print(f"📁 Ubicación: {zip_path}")
            print(f"💾 Tamaño: {compressed_size / 1024 / 1024:.2f} MB")
            
            return True, zip_path
            
        except Exception as e:
            print(f"❌ Error creando backup comprimido: {e}")
            return False, None

def main():
    backup_system = BackupSystem()
    
    print("💾 Sistema de Backup y Recuperación")
    print("=" * 40)
    print("1. Crear backup completo")
    print("2. Crear backup comprimido")
    print("3. Listar backups")
    print("4. Restaurar backup")
    print("5. Salir")
    
    choice = input("\nSeleccione una opción (1-5): ").strip()
    
    if choice == '1':
        backup_name = input("Nombre del backup (opcional): ").strip()
        if not backup_name:
            backup_name = None
        
        success, stats = backup_system.create_backup(backup_name)
        if success:
            print(f"\n🎉 ¡Backup completado exitosamente!")
    
    elif choice == '2':
        backup_name = input("Nombre del backup (opcional): ").strip()
        if not backup_name:
            backup_name = None
        
        success, zip_path = backup_system.create_compressed_backup(backup_name)
        if success:
            print(f"\n🎉 ¡Backup comprimido creado exitosamente!")
    
    elif choice == '3':
        backup_system.list_backups()
    
    elif choice == '4':
        backups = backup_system.list_backups()
        if backups:
            backup_name = input("Nombre del backup a restaurar: ").strip()
            if backup_name:
                backup_system.restore_backup(backup_name)
    
    elif choice == '5':
        print("👋 ¡Hasta luego!")
    
    else:
        print("❌ Opción no válida.")

if __name__ == "__main__":
    main()



