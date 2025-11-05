#!/usr/bin/env python3
"""
Script de Mantenimiento de Organización para Proyecto Frontier
Mantiene automáticamente la organización del proyecto
"""

import os
import sys
import time
import schedule
from pathlib import Path
from datetime import datetime, timedelta

# Agregar el directorio padre al path para importar los otros scripts
sys.path.append(str(Path(__file__).parent))

from auto_organize import FrontierOrganizer
from verify_organization import OrganizationVerifier

class OrganizationMaintainer:
    def __init__(self, root_path: str = "/Users/adan/frontier"):
        self.root_path = Path(root_path)
        self.organizer = FrontierOrganizer(root_path)
        self.verifier = OrganizationVerifier(root_path)
        self.log_file = self.root_path / "logs" / "organization_maintenance.log"
        
        # Crear directorio de logs si no existe
        self.log_file.parent.mkdir(exist_ok=True)
    
    def log(self, message: str, level: str = "INFO"):
        """Registra un mensaje en el log"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        print(f"[{level}] {message}")
    
    def daily_maintenance(self):
        """Mantenimiento diario de la organización"""
        self.log("Iniciando mantenimiento diario de organización...")
        
        try:
            # Organizar archivos nuevos
            results = self.organizer.organize_directory()
            self.log(f"Organización completada: {results['moved']} archivos movidos, {results['errors']} errores")
            
            # Verificar organización
            verification = self.verifier.verify_organization()
            score = verification['stats']['organization_score']
            
            if score < 80:
                self.log(f"Puntaje de organización bajo: {score:.1f}/100", "WARNING")
                self._fix_organization_issues(verification['issues'])
            else:
                self.log(f"Organización en buen estado: {score:.1f}/100")
            
            # Limpiar archivos temporales
            self._cleanup_temp_files()
            
            self.log("Mantenimiento diario completado exitosamente")
            
        except Exception as e:
            self.log(f"Error en mantenimiento diario: {e}", "ERROR")
    
    def weekly_maintenance(self):
        """Mantenimiento semanal de la organización"""
        self.log("Iniciando mantenimiento semanal de organización...")
        
        try:
            # Generar reporte completo
            report = self.verifier.generate_report("WEEKLY_ORGANIZATION_REPORT.md")
            self.log("Reporte semanal generado")
            
            # Actualizar archivos índice
            self.organizer.create_index_files()
            self.log("Archivos índice actualizados")
            
            # Verificar duplicados
            self._check_duplicates()
            
            # Optimizar estructura
            self._optimize_structure()
            
            self.log("Mantenimiento semanal completado exitosamente")
            
        except Exception as e:
            self.log(f"Error en mantenimiento semanal: {e}", "ERROR")
    
    def monthly_maintenance(self):
        """Mantenimiento mensual de la organización"""
        self.log("Iniciando mantenimiento mensual de organización...")
        
        try:
            # Auditoría completa
            self._full_audit()
            
            # Reorganizar si es necesario
            self._reorganize_if_needed()
            
            # Generar reporte mensual
            report = self.verifier.generate_report("MONTHLY_ORGANIZATION_REPORT.md")
            self.log("Reporte mensual generado")
            
            # Limpiar logs antiguos
            self._cleanup_old_logs()
            
            self.log("Mantenimiento mensual completado exitosamente")
            
        except Exception as e:
            self.log(f"Error en mantenimiento mensual: {e}", "ERROR")
    
    def _fix_organization_issues(self, issues: list):
        """Corrige problemas de organización identificados"""
        self.log("Corrigiendo problemas de organización...")
        
        for issue in issues:
            if issue['type'] == 'loose_files':
                self.log(f"Procesando {len(issue['files'])} archivos sueltos...")
                # Aquí se podría implementar lógica específica para cada archivo
                
            elif issue['type'] == 'missing_index':
                self.log(f"Creando archivo índice para {issue['category']}...")
                category_path = self.root_path / issue['category']
                if category_path.exists():
                    self.organizer._create_category_index(issue['category'], category_path)
    
    def _cleanup_temp_files(self):
        """Limpia archivos temporales"""
        temp_patterns = ['*.tmp', '*.temp', '*.bak', '*.old']
        cleaned = 0
        
        for pattern in temp_patterns:
            for file_path in self.root_path.rglob(pattern):
                try:
                    file_path.unlink()
                    cleaned += 1
                except:
                    pass
        
        if cleaned > 0:
            self.log(f"Limpiados {cleaned} archivos temporales")
    
    def _check_duplicates(self):
        """Verifica archivos duplicados"""
        self.log("Verificando archivos duplicados...")
        
        file_hashes = {}
        duplicates = []
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in ['.md', '.py', '.html', '.pdf', '.docx']:
                try:
                    # Calcular hash simple del archivo
                    file_hash = hash(file_path.read_bytes())
                    
                    if file_hash in file_hashes:
                        duplicates.append((file_hashes[file_hash], file_path))
                    else:
                        file_hashes[file_hash] = file_path
                except:
                    pass
        
        if duplicates:
            self.log(f"Encontrados {len(duplicates)} archivos duplicados", "WARNING")
            # Aquí se podría implementar lógica para manejar duplicados
        else:
            self.log("No se encontraron archivos duplicados")
    
    def _optimize_structure(self):
        """Optimiza la estructura de directorios"""
        self.log("Optimizando estructura de directorios...")
        
        # Verificar si hay categorías con muy pocos archivos que podrían consolidarse
        for category in self.verifier.categories:
            category_path = self.root_path / category
            if category_path.exists():
                files = list(category_path.rglob('*'))
                file_count = len([f for f in files if f.is_file()])
                
                if file_count < 3:
                    self.log(f"Categoría {category} tiene solo {file_count} archivos - considerar consolidación")
    
    def _full_audit(self):
        """Realiza una auditoría completa del sistema"""
        self.log("Iniciando auditoría completa...")
        
        # Verificar integridad de archivos
        self._verify_file_integrity()
        
        # Verificar permisos
        self._verify_permissions()
        
        # Verificar estructura de directorios
        self._verify_directory_structure()
        
        self.log("Auditoría completa finalizada")
    
    def _verify_file_integrity(self):
        """Verifica la integridad de los archivos"""
        self.log("Verificando integridad de archivos...")
        
        corrupted_files = []
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file():
                try:
                    # Intentar leer el archivo
                    file_path.read_bytes()
                except Exception as e:
                    corrupted_files.append((file_path, str(e)))
        
        if corrupted_files:
            self.log(f"Encontrados {len(corrupted_files)} archivos con problemas", "WARNING")
        else:
            self.log("Todos los archivos están íntegros")
    
    def _verify_permissions(self):
        """Verifica permisos de archivos y directorios"""
        self.log("Verificando permisos...")
        
        # Verificar que los directorios sean accesibles
        for category in self.verifier.categories:
            category_path = self.root_path / category
            if category_path.exists():
                if not os.access(category_path, os.R_OK):
                    self.log(f"Directorio {category} no es accesible para lectura", "WARNING")
                if not os.access(category_path, os.W_OK):
                    self.log(f"Directorio {category} no es accesible para escritura", "WARNING")
    
    def _verify_directory_structure(self):
        """Verifica la estructura de directorios"""
        self.log("Verificando estructura de directorios...")
        
        # Verificar que todas las categorías principales existan
        expected_categories = [
            "01_Marketing", "02_Consciousness_Systems", "02_Finance", "03_Human_Resources",
            "04_Business_Strategy", "05_Technology", "06_Documentation", "07_Advanced_Features",
            "07_Risk_Management", "08_AI_Artificial_Intelligence", "09_Sales", "10_Customer_Service",
            "11_Research_Development", "11_System_Architecture", "12_Quality_Assurance",
            "12_User_Guides", "13_Legal_Compliance", "13_Project_Status", "14_Procurement",
            "14_Thought_Leadership", "15_Logistics", "16_Data_Analytics", "17_Innovation",
            "18_Sustainability", "19_International_Business", "20_Project_Management"
        ]
        
        missing_categories = []
        for category in expected_categories:
            if not (self.root_path / category).exists():
                missing_categories.append(category)
        
        if missing_categories:
            self.log(f"Categorías faltantes: {missing_categories}", "WARNING")
        else:
            self.log("Todas las categorías principales existen")
    
    def _reorganize_if_needed(self):
        """Reorganiza si es necesario"""
        verification = self.verifier.verify_organization()
        score = verification['stats']['organization_score']
        
        if score < 70:
            self.log("Puntaje de organización muy bajo - iniciando reorganización...")
            self.organizer.organize_directory()
            self.organizer.create_index_files()
            self.log("Reorganización completada")
    
    def _cleanup_old_logs(self):
        """Limpia logs antiguos"""
        self.log("Limpiando logs antiguos...")
        
        log_dir = self.log_file.parent
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
        
        self.log("Programador iniciado - tareas programadas:")
        self.log("- Mantenimiento diario: 02:00")
        self.log("- Mantenimiento semanal: Domingo 03:00")
        self.log("- Mantenimiento mensual: Primer día del mes")
        
        # Ejecutar tareas programadas
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Mantenedor de Organización del Proyecto Frontier')
    parser.add_argument('--mode', choices=['daily', 'weekly', 'monthly', 'schedule'], 
                       default='daily', help='Modo de ejecución')
    parser.add_argument('--root', default='/Users/adan/frontier', 
                       help='Ruta raíz del proyecto')
    
    args = parser.parse_args()
    
    maintainer = OrganizationMaintainer(args.root)
    
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
