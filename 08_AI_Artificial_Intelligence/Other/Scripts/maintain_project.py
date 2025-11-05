#!/usr/bin/env python3
"""
Sistema de Mantenimiento Automático para Proyecto Frontier
Mantiene la organización del proyecto de forma continua
"""

import os
import schedule
import time
from pathlib import Path
from datetime import datetime, timedelta
from organize_project import FrontierOrganizer

class ProjectMaintainer:
    def __init__(self, root_path: str = "/Users/adan/frontier"):
        self.root_path = Path(root_path)
        self.organizer = FrontierOrganizer(root_path)
        self.maintenance_log = self.root_path / "logs" / "maintenance.log"
        
        # Crear directorio de logs
        self.maintenance_log.parent.mkdir(exist_ok=True)
    
    def log(self, message: str, level: str = "INFO"):
        """Registra mensaje en log de mantenimiento"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.maintenance_log, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        print(f"[{level}] {message}")
    
    def daily_maintenance(self):
        """Mantenimiento diario del proyecto"""
        self.log("Iniciando mantenimiento diario...")
        
        try:
            # Organizar archivos nuevos
            results = self.organizer.organize_files()
            self.log(f"Organización diaria: {results['organized']} archivos organizados")
            
            # Verificar organización
            verification = self.organizer.verify_organization()
            
            if verification['score'] < 80:
                self.log(f"Puntaje bajo: {verification['score']}/100 - Ejecutando optimización", "WARNING")
                self.optimize_organization()
            else:
                self.log(f"Organización en buen estado: {verification['score']}/100")
            
            # Limpiar archivos temporales
            self.cleanup_temp_files()
            
            self.log("Mantenimiento diario completado")
            
        except Exception as e:
            self.log(f"Error en mantenimiento diario: {e}", "ERROR")
    
    def weekly_maintenance(self):
        """Mantenimiento semanal del proyecto"""
        self.log("Iniciando mantenimiento semanal...")
        
        try:
            # Generar reporte completo
            verification = self.organizer.verify_organization()
            report = self.organizer.generate_report(verification)
            
            report_file = self.root_path / "WEEKLY_MAINTENANCE_REPORT.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            self.log("Reporte semanal generado")
            
            # Actualizar archivos índice
            self.organizer.create_index_files()
            self.log("Archivos índice actualizados")
            
            # Verificar duplicados
            self.check_duplicates()
            
            # Optimizar estructura
            self.optimize_structure()
            
            self.log("Mantenimiento semanal completado")
            
        except Exception as e:
            self.log(f"Error en mantenimiento semanal: {e}", "ERROR")
    
    def monthly_maintenance(self):
        """Mantenimiento mensual del proyecto"""
        self.log("Iniciando mantenimiento mensual...")
        
        try:
            # Auditoría completa
            self.full_audit()
            
            # Reorganizar si es necesario
            self.reorganize_if_needed()
            
            # Generar reporte mensual
            verification = self.organizer.verify_organization()
            report = self.organizer.generate_report(verification)
            
            report_file = self.root_path / "MONTHLY_MAINTENANCE_REPORT.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            self.log("Reporte mensual generado")
            
            # Limpiar logs antiguos
            self.cleanup_old_logs()
            
            self.log("Mantenimiento mensual completado")
            
        except Exception as e:
            self.log(f"Error en mantenimiento mensual: {e}", "ERROR")
    
    def optimize_organization(self):
        """Optimiza la organización del proyecto"""
        self.log("Optimizando organización...")
        
        # Ejecutar organización completa
        results = self.organizer.organize_files()
        self.log(f"Optimización: {results['organized']} archivos reorganizados")
        
        # Actualizar índices
        self.organizer.create_index_files()
        self.log("Índices actualizados")
    
    def cleanup_temp_files(self):
        """Limpia archivos temporales"""
        self.log("Limpiando archivos temporales...")
        
        temp_patterns = ['*.tmp', '*.temp', '*.bak', '*.old', '*.log']
        cleaned = 0
        
        for pattern in temp_patterns:
            for file_path in self.root_path.rglob(pattern):
                try:
                    if file_path.name not in ['organization.log', 'maintenance.log']:
                        file_path.unlink()
                        cleaned += 1
                except:
                    pass
        
        if cleaned > 0:
            self.log(f"Limpiados {cleaned} archivos temporales")
    
    def check_duplicates(self):
        """Verifica archivos duplicados"""
        self.log("Verificando archivos duplicados...")
        
        file_hashes = {}
        duplicates = []
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.md', '.py', '.js', '.ts']:
                try:
                    file_hash = hash(file_path.read_bytes())
                    
                    if file_hash in file_hashes:
                        duplicates.append((file_hashes[file_hash], file_path))
                    else:
                        file_hashes[file_hash] = file_path
                except:
                    pass
        
        if duplicates:
            self.log(f"Encontrados {len(duplicates)} archivos duplicados", "WARNING")
        else:
            self.log("No se encontraron archivos duplicados")
    
    def optimize_structure(self):
        """Optimiza la estructura de directorios"""
        self.log("Optimizando estructura...")
        
        # Verificar categorías con pocos archivos
        for category_id in self.organizer.config["categories"]:
            category_path = self.root_path / category_id
            if category_path.exists():
                files = list(category_path.rglob('*'))
                file_count = len([f for f in files if f.is_file()])
                
                if file_count < 3:
                    self.log(f"Categoría {category_id} tiene solo {file_count} archivos")
    
    def full_audit(self):
        """Realiza auditoría completa del sistema"""
        self.log("Iniciando auditoría completa...")
        
        # Verificar integridad de archivos
        self.verify_file_integrity()
        
        # Verificar permisos
        self.verify_permissions()
        
        # Verificar estructura
        self.verify_structure()
        
        self.log("Auditoría completa finalizada")
    
    def verify_file_integrity(self):
        """Verifica integridad de archivos"""
        self.log("Verificando integridad de archivos...")
        
        corrupted_files = []
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file():
                try:
                    file_path.read_bytes()
                except Exception as e:
                    corrupted_files.append((file_path, str(e)))
        
        if corrupted_files:
            self.log(f"Encontrados {len(corrupted_files)} archivos con problemas", "WARNING")
        else:
            self.log("Todos los archivos están íntegros")
    
    def verify_permissions(self):
        """Verifica permisos de archivos"""
        self.log("Verificando permisos...")
        
        for category_id in self.organizer.config["categories"]:
            category_path = self.root_path / category_id
            if category_path.exists():
                if not os.access(category_path, os.R_OK):
                    self.log(f"Directorio {category_id} no es accesible para lectura", "WARNING")
                if not os.access(category_path, os.W_OK):
                    self.log(f"Directorio {category_id} no es accesible para escritura", "WARNING")
    
    def verify_structure(self):
        """Verifica estructura de directorios"""
        self.log("Verificando estructura...")
        
        missing_categories = []
        for category_id in self.organizer.config["categories"]:
            if not (self.root_path / category_id).exists():
                missing_categories.append(category_id)
        
        if missing_categories:
            self.log(f"Categorías faltantes: {missing_categories}", "WARNING")
        else:
            self.log("Todas las categorías existen")
    
    def reorganize_if_needed(self):
        """Reorganiza si es necesario"""
        verification = self.organizer.verify_organization()
        
        if verification['score'] < 70:
            self.log("Puntaje muy bajo - iniciando reorganización...")
            self.organizer.organize_files()
            self.organizer.create_index_files()
            self.log("Reorganización completada")
    
    def cleanup_old_logs(self):
        """Limpia logs antiguos"""
        self.log("Limpiando logs antiguos...")
        
        log_dir = self.maintenance_log.parent
        cutoff_date = datetime.now() - timedelta(days=30)
        
        cleaned = 0
        for log_file in log_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                try:
                    log_file.unlink()
                    cleaned += 1
                except:
                    pass
        
        if cleaned > 0:
            self.log(f"Limpiados {cleaned} logs antiguos")
    
    def start_scheduler(self):
        """Inicia el programador de tareas"""
        self.log("Iniciando programador de mantenimiento...")
        
        # Programar tareas
        schedule.every().day.at("02:00").do(self.daily_maintenance)
        schedule.every().sunday.at("03:00").do(self.weekly_maintenance)
        schedule.every().month.do(self.monthly_maintenance)
        
        self.log("Programador iniciado:")
        self.log("- Mantenimiento diario: 02:00")
        self.log("- Mantenimiento semanal: Domingo 03:00")
        self.log("- Mantenimiento mensual: Primer día del mes")
        
        # Ejecutar tareas programadas
        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Mantenedor del Proyecto Frontier')
    parser.add_argument('--mode', choices=['daily', 'weekly', 'monthly', 'schedule'], 
                       default='daily', help='Modo de ejecución')
    parser.add_argument('--root', default='/Users/adan/frontier', 
                       help='Ruta raíz del proyecto')
    
    args = parser.parse_args()
    
    maintainer = ProjectMaintainer(args.root)
    
    if args.mode == 'daily':
        maintainer.daily_maintenance()
    elif args.mode == 'weekly':
        maintainer.weekly_maintenance()
    elif args.mode == 'monthly':
        maintainer.monthly_maintenance()
    elif args.mode == 'schedule':
        maintainer.start_scheduler()

if __name__ == "__main__":
    main()
