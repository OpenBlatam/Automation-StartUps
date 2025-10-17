#!/usr/bin/env python3
"""
Mantenedor Automático del Proyecto
Ejecuta tareas de mantenimiento y optimización automáticamente
"""

import os
import subprocess
import schedule
import time
from datetime import datetime
from pathlib import Path

class AutoMaintainer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.scripts_dir = self.project_root / "scripts"
    
    def run_organization(self):
        """Ejecuta el organizador ultra-avanzado"""
        print(f"[{datetime.now()}] 🔄 Ejecutando organización automática...")
        try:
            result = subprocess.run([
                "python3", str(self.scripts_dir / "ultra_organizer.py")
            ], capture_output=True, text=True, cwd=str(self.project_root))
            
            if result.returncode == 0:
                print(f"[{datetime.now()}] ✅ Organización completada")
            else:
                print(f"[{datetime.now()}] ❌ Error en organización: {result.stderr}")
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Error ejecutando organización: {e}")
    
    def run_verification(self):
        """Ejecuta el verificador avanzado"""
        print(f"[{datetime.now()}] 🔍 Ejecutando verificación...")
        try:
            result = subprocess.run([
                "python3", str(self.scripts_dir / "advanced_verifier.py")
            ], capture_output=True, text=True, cwd=str(self.project_root))
            
            if result.returncode == 0:
                print(f"[{datetime.now()}] ✅ Verificación completada")
            else:
                print(f"[{datetime.now()}] ❌ Error en verificación: {result.stderr}")
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Error ejecutando verificación: {e}")
    
    def cleanup_temp_files(self):
        """Limpia archivos temporales"""
        print(f"[{datetime.now()}] 🧹 Limpiando archivos temporales...")
        temp_patterns = ["*.tmp", "*.log", "*.cache", "__pycache__"]
        cleaned = 0
        
        for pattern in temp_patterns:
            for file_path in self.project_root.rglob(pattern):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        cleaned += 1
                    elif file_path.is_dir():
                        import shutil
                        shutil.rmtree(file_path)
                        cleaned += 1
                except Exception as e:
                    print(f"Error limpiando {file_path}: {e}")
        
        print(f"[{datetime.now()}] ✅ Limpieza completada: {cleaned} archivos")
    
    def update_index_files(self):
        """Actualiza archivos de índice"""
        print(f"[{datetime.now()}] 📝 Actualizando archivos de índice...")
        try:
            result = subprocess.run([
                "python3", str(self.scripts_dir / "ultra_organizer.py")
            ], capture_output=True, text=True, cwd=str(self.project_root))
            print(f"[{datetime.now()}] ✅ Índices actualizados")
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Error actualizando índices: {e}")
    
    def run_daily_maintenance(self):
        """Ejecuta mantenimiento diario"""
        print(f"\n{'='*50}")
        print(f"🚀 MANTENIMIENTO DIARIO - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        
        self.run_organization()
        self.run_verification()
        self.cleanup_temp_files()
        self.update_index_files()
        
        print(f"\n✅ Mantenimiento diario completado")
        print(f"{'='*50}\n")
    
    def start_scheduler(self):
        """Inicia el programador de tareas"""
        print("🕐 Iniciando mantenedor automático...")
        print("Tareas programadas:")
        print("  - Organización: Cada 6 horas")
        print("  - Verificación: Cada 12 horas")
        print("  - Limpieza: Diariamente a las 2:00 AM")
        print("  - Mantenimiento completo: Diariamente a las 6:00 AM")
        
        # Programar tareas
        schedule.every(6).hours.do(self.run_organization)
        schedule.every(12).hours.do(self.run_verification)
        schedule.every().day.at("02:00").do(self.cleanup_temp_files)
        schedule.every().day.at("06:00").do(self.run_daily_maintenance)
        
        # Ejecutar mantenimiento inicial
        self.run_daily_maintenance()
        
        # Bucle principal
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto

if __name__ == "__main__":
    maintainer = AutoMaintainer("/Users/adan/frontier")
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
        maintainer.start_scheduler()
    else:
        maintainer.run_daily_maintenance()



