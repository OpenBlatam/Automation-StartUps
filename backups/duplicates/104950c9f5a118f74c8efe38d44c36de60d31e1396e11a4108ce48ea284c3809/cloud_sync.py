#!/usr/bin/env python3
"""
Sistema de sincronización en la nube para el sistema de organización empresarial
"""

import os
import json
import hashlib
import sqlite3
from datetime import datetime, timedelta
import threading
import time
import requests
from pathlib import Path

class CloudSyncSystem:
    def __init__(self, base_path="/Users/adan/frontier"):
        self.base_path = base_path
        self.sync_db = os.path.join(base_path, "cloud_sync.db")
        self.sync_config = os.path.join(base_path, "sync_config.json")
        self.business_areas = [
            '01_Marketing', '02_Finance', '03_Human_Resources', '04_Operations',
            '05_Technology', '06_Strategy', '07_Risk_Management', '08_AI_Artificial_Intelligence',
            '09_Sales', '10_Customer_Service', '11_Research_Development', '12_Quality_Assurance',
            '13_Legal_Compliance', '14_Procurement', '15_Logistics', '16_Data_Analytics',
            '17_Innovation', '18_Sustainability', '19_International_Business', '20_Project_Management'
        ]
        self.init_sync_database()
        self.load_sync_config()
    
    def init_sync_database(self):
        """Inicializar base de datos de sincronización"""
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        
        # Tabla de archivos sincronizados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS synced_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                local_path TEXT UNIQUE,
                cloud_path TEXT,
                file_hash TEXT,
                last_sync TEXT,
                sync_status TEXT,
                file_size INTEGER,
                area TEXT,
                sync_count INTEGER DEFAULT 0
            )
        ''')
        
        # Tabla de conflictos de sincronización
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_conflicts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                conflict_type TEXT,
                local_version TEXT,
                cloud_version TEXT,
                resolution TEXT,
                created_at TEXT,
                resolved_at TEXT
            )
        ''')
        
        # Tabla de historial de sincronización
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                action TEXT,
                timestamp TEXT,
                details TEXT
            )
        ''')
        
        # Tabla de configuración de nube
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cloud_config (
                id INTEGER PRIMARY KEY,
                provider TEXT,
                endpoint TEXT,
                credentials TEXT,
                last_sync TEXT,
                sync_enabled BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_sync_config(self):
        """Cargar configuración de sincronización"""
        if os.path.exists(self.sync_config):
            with open(self.sync_config, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                'enabled': False,
                'provider': 'local',
                'endpoint': '',
                'credentials': {},
                'sync_interval': 300,  # 5 minutos
                'auto_sync': False,
                'conflict_resolution': 'manual'
            }
            self.save_sync_config()
    
    def save_sync_config(self):
        """Guardar configuración de sincronización"""
        with open(self.sync_config, 'w') as f:
            json.dump(self.config, f, indent=2)
    
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
    
    def scan_files_for_sync(self):
        """Escanear archivos para sincronización"""
        files_to_sync = []
        
        for area in self.business_areas:
            area_path = os.path.join(self.base_path, area)
            if not os.path.exists(area_path):
                continue
            
            for root, dirs, files in os.walk(area_path):
                for file in files:
                    if file.endswith('.md'):
                        file_path = os.path.join(root, file)
                        try:
                            file_hash = self.calculate_file_hash(file_path)
                            file_size = os.path.getsize(file_path)
                            stat = os.stat(file_path)
                            last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
                            
                            files_to_sync.append({
                                'local_path': file_path,
                                'relative_path': os.path.relpath(file_path, self.base_path),
                                'file_hash': file_hash,
                                'file_size': file_size,
                                'last_modified': last_modified,
                                'area': area
                            })
                        except Exception as e:
                            print(f"Error procesando {file_path}: {e}")
        
        return files_to_sync
    
    def check_sync_status(self, file_path):
        """Verificar estado de sincronización de un archivo"""
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT file_hash, last_sync, sync_status, sync_count
            FROM synced_files
            WHERE local_path = ?
        ''', (file_path,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'synced': True,
                'file_hash': result[0],
                'last_sync': result[1],
                'sync_status': result[2],
                'sync_count': result[3]
            }
        else:
            return {'synced': False}
    
    def update_sync_status(self, file_path, file_hash, sync_status='synced'):
        """Actualizar estado de sincronización"""
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        
        # Verificar si existe
        cursor.execute('SELECT id FROM synced_files WHERE local_path = ?', (file_path,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute('''
                UPDATE synced_files
                SET file_hash = ?, last_sync = ?, sync_status = ?, sync_count = sync_count + 1
                WHERE local_path = ?
            ''', (file_hash, datetime.now().isoformat(), sync_status, file_path))
        else:
            # Obtener área del archivo
            area = 'General'
            for business_area in self.business_areas:
                if business_area in file_path:
                    area = business_area
                    break
            
            cursor.execute('''
                INSERT INTO synced_files (local_path, file_hash, last_sync, sync_status, file_size, area)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (file_path, file_hash, datetime.now().isoformat(), sync_status, 
                  os.path.getsize(file_path), area))
        
        # Registrar en historial
        cursor.execute('''
            INSERT INTO sync_history (file_path, action, timestamp, details)
            VALUES (?, ?, ?, ?)
        ''', (file_path, sync_status, datetime.now().isoformat(), f"Hash: {file_hash}"))
        
        conn.commit()
        conn.close()
    
    def detect_conflicts(self):
        """Detectar conflictos de sincronización"""
        conflicts = []
        
        # Simular detección de conflictos (en implementación real, comparar con servidor)
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT local_path, file_hash, last_sync
            FROM synced_files
            WHERE sync_status = 'conflict'
        ''')
        
        conflict_files = cursor.fetchall()
        
        for file_path, file_hash, last_sync in conflict_files:
            if os.path.exists(file_path):
                current_hash = self.calculate_file_hash(file_path)
                if current_hash != file_hash:
                    conflicts.append({
                        'file_path': file_path,
                        'local_hash': current_hash,
                        'cloud_hash': file_hash,
                        'last_sync': last_sync
                    })
        
        conn.close()
        return conflicts
    
    def resolve_conflict(self, file_path, resolution='keep_local'):
        """Resolver conflicto de sincronización"""
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        
        if resolution == 'keep_local':
            # Mantener versión local
            current_hash = self.calculate_file_hash(file_path)
            cursor.execute('''
                UPDATE synced_files
                SET file_hash = ?, sync_status = 'synced', last_sync = ?
                WHERE local_path = ?
            ''', (current_hash, datetime.now().isoformat(), file_path))
            
        elif resolution == 'keep_cloud':
            # Mantener versión de la nube (requiere descarga)
            cursor.execute('''
                UPDATE synced_files
                SET sync_status = 'pending_download'
                WHERE local_path = ?
            ''', (file_path,))
        
        # Registrar resolución
        cursor.execute('''
            INSERT INTO sync_conflicts (file_path, conflict_type, resolution, resolved_at)
            VALUES (?, 'sync_conflict', ?, ?)
        ''', (file_path, resolution, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def sync_to_cloud(self, files_to_sync):
        """Sincronizar archivos a la nube"""
        synced_count = 0
        errors = []
        
        for file_info in files_to_sync:
            file_path = file_info['local_path']
            file_hash = file_info['file_hash']
            
            try:
                # Simular sincronización (en implementación real, subir a servidor)
                print(f"📤 Sincronizando: {os.path.basename(file_path)}")
                
                # Actualizar estado
                self.update_sync_status(file_path, file_hash, 'synced')
                synced_count += 1
                
                # Simular delay de red
                time.sleep(0.1)
                
            except Exception as e:
                error_msg = f"Error sincronizando {file_path}: {e}"
                errors.append(error_msg)
                print(f"❌ {error_msg}")
        
        return synced_count, errors
    
    def sync_from_cloud(self):
        """Sincronizar archivos desde la nube"""
        # Simular descarga desde la nube
        print("📥 Sincronizando desde la nube...")
        
        # En implementación real, descargar archivos del servidor
        # y comparar con versiones locales
        
        return True
    
    def auto_sync(self):
        """Sincronización automática"""
        if not self.config.get('auto_sync', False):
            return
        
        print("🔄 Iniciando sincronización automática...")
        
        # Escanear archivos
        files_to_sync = self.scan_files_for_sync()
        
        # Filtrar archivos que necesitan sincronización
        files_needing_sync = []
        for file_info in files_to_sync:
            file_path = file_info['local_path']
            sync_status = self.check_sync_status(file_path)
            
            if not sync_status['synced'] or sync_status['file_hash'] != file_info['file_hash']:
                files_needing_sync.append(file_info)
        
        if files_needing_sync:
            # Sincronizar a la nube
            synced_count, errors = self.sync_to_cloud(files_needing_sync)
            print(f"✅ Sincronizados {synced_count} archivos")
            
            if errors:
                print(f"❌ {len(errors)} errores durante la sincronización")
        
        # Sincronizar desde la nube
        self.sync_from_cloud()
        
        print("✅ Sincronización automática completada")
    
    def start_auto_sync(self):
        """Iniciar sincronización automática en segundo plano"""
        def sync_loop():
            while self.config.get('auto_sync', False):
                try:
                    self.auto_sync()
                    time.sleep(self.config.get('sync_interval', 300))
                except Exception as e:
                    print(f"Error en sincronización automática: {e}")
                    time.sleep(60)  # Esperar 1 minuto antes de reintentar
        
        sync_thread = threading.Thread(target=sync_loop, daemon=True)
        sync_thread.start()
        print("🔄 Sincronización automática iniciada")
    
    def get_sync_stats(self):
        """Obtener estadísticas de sincronización"""
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        
        # Estadísticas generales
        cursor.execute('SELECT COUNT(*) FROM synced_files')
        total_synced = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM synced_files WHERE sync_status = "synced"')
        successfully_synced = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM synced_files WHERE sync_status = "conflict"')
        conflicts = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM sync_history')
        total_sync_operations = cursor.fetchone()[0]
        
        # Archivos por área
        cursor.execute('''
            SELECT area, COUNT(*) FROM synced_files
            GROUP BY area
            ORDER BY COUNT(*) DESC
        ''')
        area_stats = dict(cursor.fetchall())
        
        # Archivos más sincronizados
        cursor.execute('''
            SELECT local_path, sync_count FROM synced_files
            ORDER BY sync_count DESC
            LIMIT 10
        ''')
        most_synced = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_synced': total_synced,
            'successfully_synced': successfully_synced,
            'conflicts': conflicts,
            'total_sync_operations': total_sync_operations,
            'area_stats': area_stats,
            'most_synced': most_synced,
            'config': self.config
        }
    
    def configure_cloud_provider(self, provider, endpoint, credentials):
        """Configurar proveedor de nube"""
        self.config['provider'] = provider
        self.config['endpoint'] = endpoint
        self.config['credentials'] = credentials
        self.save_sync_config()
        
        # Guardar en base de datos
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO cloud_config (id, provider, endpoint, credentials, last_sync)
            VALUES (1, ?, ?, ?, ?)
        ''', (provider, endpoint, json.dumps(credentials), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Proveedor de nube configurado: {provider}")

def main():
    sync_system = CloudSyncSystem()
    
    print("☁️ Sistema de Sincronización en la Nube")
    print("=" * 50)
    print("1. Configurar proveedor de nube")
    print("2. Sincronizar archivos")
    print("3. Detectar conflictos")
    print("4. Resolver conflictos")
    print("5. Iniciar sincronización automática")
    print("6. Ver estadísticas de sincronización")
    print("7. Salir")
    
    while True:
        choice = input("\nSeleccione una opción (1-7): ").strip()
        
        if choice == '1':
            provider = input("Proveedor (aws, azure, gcp, local): ").strip()
            endpoint = input("Endpoint: ").strip()
            credentials = input("Credenciales (JSON): ").strip()
            
            try:
                creds = json.loads(credentials) if credentials else {}
                sync_system.configure_cloud_provider(provider, endpoint, creds)
            except json.JSONDecodeError:
                print("❌ Credenciales inválidas. Use formato JSON.")
        
        elif choice == '2':
            files_to_sync = sync_system.scan_files_for_sync()
            print(f"📁 Encontrados {len(files_to_sync)} archivos para sincronizar")
            
            if files_to_sync:
                synced_count, errors = sync_system.sync_to_cloud(files_to_sync)
                print(f"✅ Sincronizados {synced_count} archivos")
                if errors:
                    print(f"❌ {len(errors)} errores")
        
        elif choice == '3':
            conflicts = sync_system.detect_conflicts()
            if conflicts:
                print(f"⚠️  Encontrados {len(conflicts)} conflictos:")
                for conflict in conflicts:
                    print(f"  • {os.path.basename(conflict['file_path'])}")
            else:
                print("✅ No hay conflictos de sincronización")
        
        elif choice == '4':
            conflicts = sync_system.detect_conflicts()
            if conflicts:
                for conflict in conflicts:
                    print(f"\n📁 Conflicto: {os.path.basename(conflict['file_path'])}")
                    resolution = input("Resolución (keep_local/keep_cloud): ").strip()
                    sync_system.resolve_conflict(conflict['file_path'], resolution)
                    print("✅ Conflicto resuelto")
            else:
                print("✅ No hay conflictos para resolver")
        
        elif choice == '5':
            auto_sync = input("¿Activar sincronización automática? (y/n): ").strip().lower() == 'y'
            if auto_sync:
                interval = input("Intervalo en segundos (default 300): ").strip()
                interval = int(interval) if interval.isdigit() else 300
                
                sync_system.config['auto_sync'] = True
                sync_system.config['sync_interval'] = interval
                sync_system.save_sync_config()
                
                sync_system.start_auto_sync()
            else:
                sync_system.config['auto_sync'] = False
                sync_system.save_sync_config()
                print("❌ Sincronización automática desactivada")
        
        elif choice == '6':
            stats = sync_system.get_sync_stats()
            print(f"\n📊 Estadísticas de Sincronización:")
            print(f"  📁 Total sincronizados: {stats['total_synced']}")
            print(f"  ✅ Exitosos: {stats['successfully_synced']}")
            print(f"  ⚠️  Conflictos: {stats['conflicts']}")
            print(f"  🔄 Operaciones: {stats['total_sync_operations']}")
            
            if stats['area_stats']:
                print(f"\n📈 Por área:")
                for area, count in stats['area_stats'].items():
                    print(f"  • {area}: {count}")
        
        elif choice == '7':
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()



