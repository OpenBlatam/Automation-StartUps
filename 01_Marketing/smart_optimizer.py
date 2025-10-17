#!/usr/bin/env python3
"""
Optimizador Inteligente
Implementa mejoras basadas en análisis de patrones
"""

import os
import shutil
import re
from pathlib import Path
from datetime import datetime

class SmartOptimizer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.optimizations_applied = []
        
    def create_marketing_subcategories(self):
        """Crea subcategorías para Marketing (37.8% de archivos)"""
        print("📁 Creando subcategorías para Marketing...")
        
        marketing_dir = self.project_root / "01_Marketing"
        if not marketing_dir.exists():
            return
        
        # Subcategorías basadas en análisis de patrones
        subcategories = {
            "Neural_Marketing": ["neural", "consciousness", "transcendent"],
            "AI_Marketing": ["ai", "artificial", "intelligence", "machine"],
            "Content_Marketing": ["content", "copy", "email", "social"],
            "Strategy_Marketing": ["strategy", "campaign", "planning"],
            "Analytics_Marketing": ["analytics", "metrics", "dashboard", "report"],
            "Courses_Training": ["course", "training", "tutorial", "guide"]
        }
        
        for subcat, keywords in subcategories.items():
            subcat_dir = marketing_dir / subcat
            subcat_dir.mkdir(exist_ok=True)
            
            # Mover archivos basados en palabras clave
            for file_path in marketing_dir.iterdir():
                if file_path.is_file() and not file_path.name.startswith('.'):
                    filename_lower = file_path.name.lower()
                    if any(keyword in filename_lower for keyword in keywords):
                        target_path = subcat_dir / file_path.name
                        if not target_path.exists():
                            shutil.move(str(file_path), str(target_path))
                            self.optimizations_applied.append(f"Moved {file_path.name} to Marketing/{subcat}")
                            print(f"✅ Movido: {file_path.name} -> Marketing/{subcat}")
    
    def standardize_filenames(self):
        """Estandariza nombres de archivos en mayúsculas"""
        print("📝 Estandarizando nombres de archivos...")
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                old_name = file_path.name
                
                # Convertir archivos completamente en mayúsculas
                if old_name.isupper() and '_' in old_name:
                    new_name = old_name.lower().replace('_', '_')
                    new_path = file_path.parent / new_name
                    
                    if not new_path.exists():
                        file_path.rename(new_path)
                        self.optimizations_applied.append(f"Renamed {old_name} -> {new_name}")
                        print(f"✅ Renombrado: {old_name} -> {new_name}")
    
    def create_technology_subcategories(self):
        """Crea subcategorías para Technology"""
        print("🔧 Creando subcategorías para Technology...")
        
        tech_dir = self.project_root / "05_Technology"
        if not tech_dir.exists():
            return
        
        subcategories = {
            "AI_Systems": ["ai", "neural", "machine", "intelligence"],
            "Development_Tools": ["development", "code", "script", "tool"],
            "APIs_Integrations": ["api", "integration", "service", "endpoint"],
            "Dashboards_Analytics": ["dashboard", "analytics", "metrics", "report"],
            "Automation": ["automation", "bot", "script", "workflow"]
        }
        
        for subcat, keywords in subcategories.items():
            subcat_dir = tech_dir / subcat
            subcat_dir.mkdir(exist_ok=True)
            
            for file_path in tech_dir.iterdir():
                if file_path.is_file() and not file_path.name.startswith('.'):
                    filename_lower = file_path.name.lower()
                    if any(keyword in filename_lower for keyword in keywords):
                        target_path = subcat_dir / file_path.name
                        if not target_path.exists():
                            shutil.move(str(file_path), str(target_path))
                            self.optimizations_applied.append(f"Moved {file_path.name} to Technology/{subcat}")
                            print(f"✅ Movido: {file_path.name} -> Technology/{subcat}")
    
    def create_documentation_structure(self):
        """Crea estructura mejorada para documentación"""
        print("📚 Optimizando estructura de documentación...")
        
        doc_dir = self.project_root / "06_Documentation"
        if not doc_dir.exists():
            return
        
        # Crear subcategorías para documentación
        doc_subcategories = {
            "User_Guides": ["guide", "tutorial", "how-to", "manual"],
            "API_Documentation": ["api", "reference", "endpoint"],
            "Business_Docs": ["business", "strategy", "plan", "proposal"],
            "Technical_Docs": ["technical", "specification", "architecture"],
            "Reports_Analytics": ["report", "analysis", "summary", "dashboard"]
        }
        
        for subcat, keywords in doc_subcategories.items():
            subcat_dir = doc_dir / subcat
            subcat_dir.mkdir(exist_ok=True)
            
            for file_path in doc_dir.iterdir():
                if file_path.is_file() and not file_path.name.startswith('.'):
                    filename_lower = file_path.name.lower()
                    if any(keyword in filename_lower for keyword in keywords):
                        target_path = subcat_dir / file_path.name
                        if not target_path.exists():
                            shutil.move(str(file_path), str(target_path))
                            self.optimizations_applied.append(f"Moved {file_path.name} to Documentation/{subcat}")
                            print(f"✅ Movido: {file_path.name} -> Documentation/{subcat}")
    
    def create_version_management_system(self):
        """Crea sistema de gestión de versiones"""
        print("🔄 Creando sistema de gestión de versiones...")
        
        versions_dir = self.project_root / "00_Version_Management"
        versions_dir.mkdir(exist_ok=True)
        
        # Crear subcategorías para versiones
        version_subcategories = {
            "Current_Versions": [],
            "Archived_Versions": [],
            "Draft_Versions": []
        }
        
        for subcat in version_subcategories.keys():
            (versions_dir / subcat).mkdir(exist_ok=True)
        
        # Mover archivos versionados
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                filename = file_path.name
                
                # Identificar archivos versionados
                if re.search(r'v\d+|\d{4}', filename):
                    # Determinar si es versión actual o archivada
                    if 'current' in filename.lower() or 'latest' in filename.lower():
                        target_dir = versions_dir / "Current_Versions"
                    elif 'draft' in filename.lower() or 'temp' in filename.lower():
                        target_dir = versions_dir / "Draft_Versions"
                    else:
                        target_dir = versions_dir / "Archived_Versions"
                    
                    target_path = target_dir / filename
                    if not target_path.exists():
                        shutil.move(str(file_path), str(target_path))
                        self.optimizations_applied.append(f"Moved {filename} to Version Management")
                        print(f"✅ Movido: {filename} -> Version Management")
    
    def create_index_files(self):
        """Crea archivos README.md para todas las subcategorías"""
        print("📝 Creando archivos de índice...")
        
        for category_dir in self.project_root.iterdir():
            if category_dir.is_dir() and category_dir.name.startswith(('01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_', '00_')):
                # Crear README principal de categoría
                readme_path = category_dir / "README.md"
                if not readme_path.exists():
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(f"# {category_dir.name.replace('_', ' ').title()}\n\n")
                        f.write(f"Contenido organizado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                        f.write("## Subcategorías:\n\n")
                        
                        for subdir in sorted(category_dir.iterdir()):
                            if subdir.is_dir() and not subdir.name.startswith('.'):
                                f.write(f"- [{subdir.name}](./{subdir.name}/)\n")
                
                # Crear README para subcategorías
                for subdir in category_dir.iterdir():
                    if subdir.is_dir() and not subdir.name.startswith('.'):
                        sub_readme = subdir / "README.md"
                        if not sub_readme.exists():
                            with open(sub_readme, 'w', encoding='utf-8') as f:
                                f.write(f"# {subdir.name.replace('_', ' ').title()}\n\n")
                                f.write(f"Subcategoría de {category_dir.name}\n\n")
                                f.write("## Archivos:\n\n")
                                
                                for file in sorted(subdir.iterdir()):
                                    if file.is_file() and not file.name.startswith('.'):
                                        f.write(f"- {file.name}\n")
    
    def run_optimization(self):
        """Ejecuta todas las optimizaciones"""
        print("🚀 Iniciando optimización inteligente...")
        
        self.create_marketing_subcategories()
        self.create_technology_subcategories()
        self.create_documentation_structure()
        self.create_version_management_system()
        self.standardize_filenames()
        self.create_index_files()
        
        print(f"\n✅ Optimización completada!")
        print(f"Mejoras aplicadas: {len(self.optimizations_applied)}")
        
        return self.optimizations_applied

if __name__ == "__main__":
    optimizer = SmartOptimizer("/Users/adan/frontier")
    optimizations = optimizer.run_optimization()
    
    print(f"\n📋 RESUMEN DE OPTIMIZACIONES:")
    for i, opt in enumerate(optimizations, 1):
        print(f"  {i:2d}. {opt}")



