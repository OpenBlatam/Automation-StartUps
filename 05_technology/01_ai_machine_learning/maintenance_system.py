#!/usr/bin/env python3
"""
Sistema de mantenimiento automatizado para el sistema de organización empresarial
"""

import os
import json
import shutil
from datetime import datetime, timedelta
import subprocess
import sys

class MaintenanceSystem:
    def __init__(self, base_path="/Users/adan/frontier"):
        self.base_path = base_path
        self.maintenance_log = os.path.join(base_path, "maintenance_log.json")
        self.business_areas = [
            '01_Marketing', '02_Finance', '03_Human_Resources', '04_Operations',
            '05_Technology', '06_Strategy', '07_Risk_Management', '08_AI_Artificial_Intelligence',
            '09_Sales', '10_Customer_Service', '11_Research_Development', '12_Quality_Assurance',
            '13_Legal_Compliance', '14_Procurement', '15_Logistics', '16_Data_Analytics',
            '17_Innovation', '18_Sustainability', '19_International_Business', '20_Project_Management'
        ]
    
    def log_maintenance(self, action, status, details=None):
        """Registrar actividad de mantenimiento"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'status': status,
            'details': details
        }
        
        # Cargar log existente
        if os.path.exists(self.maintenance_log):
            with open(self.maintenance_log, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_entry)
        
        # Mantener solo los últimos 100 registros
        if len(logs) > 100:
            logs = logs[-100:]
        
        # Guardar log actualizado
        with open(self.maintenance_log, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def check_system_health(self):
        """Verificar salud del sistema"""
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'areas_status': {},
            'total_files': 0,
            'total_size': 0,
            'issues': [],
            'recommendations': []
        }
        
        for area in self.business_areas:
            area_path = os.path.join(self.base_path, area)
            area_status = {
                'exists': os.path.exists(area_path),
                'files': 0,
                'size': 0,
                'subfolders': [],
                'issues': []
            }
            
            if area_status['exists']:
                # Contar archivos y tamaño
                for root, dirs, files in os.walk(area_path):
                    for file in files:
                        if file.endswith('.md'):
                            file_path = os.path.join(root, file)
                            try:
                                file_size = os.path.getsize(file_path)
                                area_status['files'] += 1
                                area_status['size'] += file_size
                                health_report['total_files'] += 1
                                health_report['total_size'] += file_size
                            except Exception as e:
                                area_status['issues'].append(f"Error accediendo a {file}: {e}")
                    
                    # Verificar subcarpetas
                    for dir_name in dirs:
                        if dir_name not in ['Guides', 'Templates', 'Reports', 'Strategies', 'Tools']:
                            area_status['subfolders'].append(dir_name)
                
                # Verificar si tiene subcarpetas estándar
                standard_subfolders = ['Guides', 'Templates', 'Reports', 'Strategies', 'Tools']
                missing_subfolders = []
                for subfolder in standard_subfolders:
                    if not os.path.exists(os.path.join(area_path, subfolder)):
                        missing_subfolders.append(subfolder)
                
                if missing_subfolders:
                    area_status['issues'].append(f"Faltan subcarpetas: {', '.join(missing_subfolders)}")
                
                # Verificar si tiene archivo INDEX.md
                index_file = os.path.join(area_path, 'INDEX.md')
                if not os.path.exists(index_file):
                    area_status['issues'].append("Falta archivo INDEX.md")
            else:
                area_status['issues'].append("Área no existe")
                health_report['issues'].append(f"Área {area} no existe")
            
            health_report['areas_status'][area] = area_status
        
        # Generar recomendaciones
        empty_areas = [area for area, status in health_report['areas_status'].items() 
                      if status['files'] == 0]
        if empty_areas:
            health_report['recommendations'].append(f"Considerar agregar contenido a áreas vacías: {', '.join(empty_areas)}")
        
        # Verificar archivos de sistema
        system_files = ['README.md', 'NAVIGATION.md', 'DASHBOARD.md']
        for file in system_files:
            if not os.path.exists(os.path.join(self.base_path, file)):
                health_report['issues'].append(f"Falta archivo de sistema: {file}")
        
        return health_report
    
    def optimize_structure(self):
        """Optimizar estructura del sistema"""
        optimizations = []
        
        # Crear subcarpetas faltantes
        for area in self.business_areas:
            area_path = os.path.join(self.base_path, area)
            if os.path.exists(area_path):
                standard_subfolders = ['Guides', 'Templates', 'Reports', 'Strategies', 'Tools']
                for subfolder in standard_subfolders:
                    subfolder_path = os.path.join(area_path, subfolder)
                    if not os.path.exists(subfolder_path):
                        os.makedirs(subfolder_path, exist_ok=True)
                        optimizations.append(f"Creada subcarpeta: {area}/{subfolder}")
        
        # Crear archivos INDEX.md faltantes
        for area in self.business_areas:
            area_path = os.path.join(self.base_path, area)
            index_file = os.path.join(area_path, 'INDEX.md')
            if os.path.exists(area_path) and not os.path.exists(index_file):
                # Crear INDEX.md básico
                index_content = f"""# {area.replace('_', ' ')} - Índice de Documentos

## 📊 Resumen del Área
- **Última actualización**: {datetime.now().strftime('%d de %B de %Y')}
- **Área principal**: {area.replace('_', ' ')}

## 📁 Documentos Disponibles
*Contenido organizado automáticamente*

---
*Índice generado automáticamente por el sistema de mantenimiento*
"""
                with open(index_file, 'w') as f:
                    f.write(index_content)
                optimizations.append(f"Creado archivo INDEX.md: {area}")
        
        return optimizations
    
    def cleanup_system(self):
        """Limpiar sistema"""
        cleanup_actions = []
        
        # Limpiar archivos temporales
        temp_files = ['.DS_Store', 'Thumbs.db', '*.tmp']
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file in temp_files or file.endswith('.tmp'):
                    try:
                        os.remove(os.path.join(root, file))
                        cleanup_actions.append(f"Eliminado archivo temporal: {file}")
                    except:
                        pass
        
        # Limpiar directorios vacíos (excepto los principales)
        for root, dirs, files in os.walk(self.base_path, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path) and dir_name not in self.business_areas:
                        os.rmdir(dir_path)
                        cleanup_actions.append(f"Eliminado directorio vacío: {dir_path}")
                except:
                    pass
        
        return cleanup_actions
    
    def update_system(self):
        """Actualizar sistema"""
        updates = []
        
        # Verificar y actualizar archivos de sistema
        system_files = {
            'README.md': 'Punto de entrada principal',
            'NAVIGATION.md': 'Navegación del sistema',
            'DASHBOARD.md': 'Métricas y KPIs'
        }
        
        for file, description in system_files.items():
            file_path = os.path.join(self.base_path, file)
            if os.path.exists(file_path):
                # Verificar si necesita actualización
                try:
                    stat = os.stat(file_path)
                    last_modified = datetime.fromtimestamp(stat.st_mtime)
                    if (datetime.now() - last_modified).days > 30:
                        updates.append(f"Archivo {file} necesita actualización (última modificación: {last_modified.strftime('%Y-%m-%d')})")
                except:
                    pass
        
        return updates
    
    def run_full_maintenance(self):
        """Ejecutar mantenimiento completo"""
        print("🔧 Iniciando mantenimiento completo del sistema...")
        print("=" * 50)
        
        # 1. Verificar salud del sistema
        print("1. Verificando salud del sistema...")
        health_report = self.check_system_health()
        self.log_maintenance("health_check", "completed", health_report)
        
        issues_count = len(health_report['issues'])
        if issues_count > 0:
            print(f"⚠️  Encontrados {issues_count} problemas:")
            for issue in health_report['issues']:
                print(f"   • {issue}")
        else:
            print("✅ Sistema saludable")
        
        # 2. Optimizar estructura
        print("\n2. Optimizando estructura...")
        optimizations = self.optimize_structure()
        self.log_maintenance("structure_optimization", "completed", optimizations)
        
        if optimizations:
            print(f"✅ Realizadas {len(optimizations)} optimizaciones:")
            for opt in optimizations:
                print(f"   • {opt}")
        else:
            print("✅ Estructura ya optimizada")
        
        # 3. Limpiar sistema
        print("\n3. Limpiando sistema...")
        cleanup_actions = self.cleanup_system()
        self.log_maintenance("cleanup", "completed", cleanup_actions)
        
        if cleanup_actions:
            print(f"✅ Realizadas {len(cleanup_actions)} limpiezas:")
            for action in cleanup_actions:
                print(f"   • {action}")
        else:
            print("✅ Sistema ya limpio")
        
        # 4. Verificar actualizaciones
        print("\n4. Verificando actualizaciones...")
        updates = self.update_system()
        self.log_maintenance("update_check", "completed", updates)
        
        if updates:
            print(f"⚠️  {len(updates)} archivos necesitan actualización:")
            for update in updates:
                print(f"   • {update}")
        else:
            print("✅ Sistema actualizado")
        
        # Resumen final
        print(f"\n📊 RESUMEN DEL MANTENIMIENTO:")
        print(f"✅ Optimizaciones: {len(optimizations)}")
        print(f"🧹 Limpiezas: {len(cleanup_actions)}")
        print(f"⚠️  Problemas: {issues_count}")
        print(f"🔄 Actualizaciones: {len(updates)}")
        
        return {
            'optimizations': len(optimizations),
            'cleanups': len(cleanup_actions),
            'issues': issues_count,
            'updates': len(updates)
        }

def main():
    maintenance = MaintenanceSystem()
    
    print("🔧 Sistema de Mantenimiento Automatizado")
    print("=" * 40)
    print("1. Verificar salud del sistema")
    print("2. Optimizar estructura")
    print("3. Limpiar sistema")
    print("4. Verificar actualizaciones")
    print("5. Mantenimiento completo")
    print("6. Ver log de mantenimiento")
    print("7. Salir")
    
    choice = input("\nSeleccione una opción (1-7): ").strip()
    
    if choice == '1':
        health_report = maintenance.check_system_health()
        print(f"\n📊 REPORTE DE SALUD DEL SISTEMA:")
        print(f"📁 Total de archivos: {health_report['total_files']}")
        print(f"💾 Tamaño total: {health_report['total_size'] / 1024 / 1024:.2f} MB")
        print(f"⚠️  Problemas encontrados: {len(health_report['issues'])}")
        
        if health_report['issues']:
            print("\n🚨 Problemas:")
            for issue in health_report['issues']:
                print(f"   • {issue}")
        
        if health_report['recommendations']:
            print("\n💡 Recomendaciones:")
            for rec in health_report['recommendations']:
                print(f"   • {rec}")
    
    elif choice == '2':
        optimizations = maintenance.optimize_structure()
        if optimizations:
            print(f"\n✅ Realizadas {len(optimizations)} optimizaciones:")
            for opt in optimizations:
                print(f"   • {opt}")
        else:
            print("\n✅ Estructura ya optimizada")
    
    elif choice == '3':
        cleanup_actions = maintenance.cleanup_system()
        if cleanup_actions:
            print(f"\n🧹 Realizadas {len(cleanup_actions)} limpiezas:")
            for action in cleanup_actions:
                print(f"   • {action}")
        else:
            print("\n✅ Sistema ya limpio")
    
    elif choice == '4':
        updates = maintenance.update_system()
        if updates:
            print(f"\n🔄 {len(updates)} archivos necesitan actualización:")
            for update in updates:
                print(f"   • {update}")
        else:
            print("\n✅ Sistema actualizado")
    
    elif choice == '5':
        results = maintenance.run_full_maintenance()
        print(f"\n🎉 Mantenimiento completado exitosamente!")
    
    elif choice == '6':
        if os.path.exists(maintenance.maintenance_log):
            with open(maintenance.maintenance_log, 'r') as f:
                logs = json.load(f)
            print(f"\n📋 Log de mantenimiento (últimas 10 actividades):")
            for log in logs[-10:]:
                status = "✅" if log['status'] == 'completed' else "❌"
                print(f"  {status} {log['timestamp']}: {log['action']}")
        else:
            print("\n📋 No hay log de mantenimiento disponible.")
    
    elif choice == '7':
        print("👋 ¡Hasta luego!")
    
    else:
        print("❌ Opción no válida.")

if __name__ == "__main__":
    main()



