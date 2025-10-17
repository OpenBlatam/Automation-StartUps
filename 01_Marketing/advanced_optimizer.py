#!/usr/bin/env python3
"""
Optimizador Avanzado Basado en Dependencias
Implementa mejoras basadas en análisis de dependencias y similitud de contenido
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class AdvancedOptimizer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.optimizations_applied = []
        self.dependency_report = None
        
    def load_dependency_report(self):
        """Carga el reporte de análisis de dependencias"""
        report_path = self.project_root / "dependency_analysis_report.json"
        if report_path.exists():
            with open(report_path, 'r', encoding='utf-8') as f:
                self.dependency_report = json.load(f)
                print(f"📊 Reporte de dependencias cargado: {len(self.dependency_report.get('suggestions', []))} sugerencias")
        else:
            print("⚠️  No se encontró reporte de dependencias")
    
    def optimize_similar_files(self):
        """Optimiza archivos altamente similares moviéndolos a la misma categoría"""
        print("🔄 Optimizando archivos similares...")
        
        if not self.dependency_report:
            return
        
        # Agrupar archivos por similitud alta
        similar_groups = defaultdict(list)
        processed_files = set()
        
        for suggestion in self.dependency_report.get('suggestions', []):
            if suggestion['type'] == 'relocation' and suggestion['similarity'] > 0.9:
                files = suggestion['files']
                if len(files) == 2 and all(f not in processed_files for f in files):
                    # Determinar categoría objetivo basada en la mayoría
                    cat1 = self._get_file_category(files[0])
                    cat2 = self._get_file_category(files[1])
                    
                    if cat1 and cat2 and cat1 != cat2:
                        # Usar la categoría con más archivos
                        target_category = cat1 if self._count_files_in_category(cat1) > self._count_files_in_category(cat2) else cat2
                        
                        for file_path in files:
                            if self._get_file_category(file_path) != target_category:
                                self._move_file_to_category(file_path, target_category)
                                processed_files.add(file_path)
    
    def optimize_cross_references(self):
        """Optimiza categorías con muchas referencias cruzadas"""
        print("🔗 Optimizando referencias cruzadas...")
        
        if not self.dependency_report:
            return
        
        for suggestion in self.dependency_report.get('suggestions', []):
            if suggestion['type'] == 'cross_reference' and suggestion['count'] > 50:
                category = suggestion['description'].split()[1]  # Extraer nombre de categoría
                print(f"  📁 Optimizando categoría {category} con {suggestion['count']} referencias cruzadas")
                
                # Crear subcategorías para reducir referencias cruzadas
                self._create_subcategories_for_cross_references(category)
    
    def optimize_orphan_files(self):
        """Optimiza archivos huérfanos"""
        print("👻 Optimizando archivos huérfanos...")
        
        if not self.dependency_report:
            return
        
        for suggestion in self.dependency_report.get('suggestions', []):
            if suggestion['type'] == 'orphan_files':
                orphan_files = suggestion['files']
                print(f"  📄 Procesando {len(orphan_files)} archivos huérfanos")
                
                # Mover archivos huérfanos a categoría de documentación
                for file_path in orphan_files[:50]:  # Limitar a 50 para evitar sobrecarga
                    self._move_file_to_category(file_path, "06_Documentation")
    
    def create_smart_categories(self):
        """Crea categorías inteligentes basadas en patrones de contenido"""
        print("🧠 Creando categorías inteligentes...")
        
        # Crear categoría para archivos de alta similitud
        similar_dir = self.project_root / "99_Similar_Content"
        similar_dir.mkdir(exist_ok=True)
        
        # Crear categoría para archivos relacionados
        related_dir = self.project_root / "98_Related_Files"
        related_dir.mkdir(exist_ok=True)
        
        # Crear categoría para archivos de análisis
        analysis_dir = self.project_root / "97_Analysis_Reports"
        analysis_dir.mkdir(exist_ok=True)
        
        # Mover archivos de análisis
        analysis_files = [
            "dependency_analysis_report.json",
            "pattern_analysis_report.json",
            "organization_report.json"
        ]
        
        for file_name in analysis_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                target_path = analysis_dir / file_name
                if not target_path.exists():
                    shutil.move(str(file_path), str(target_path))
                    self.optimizations_applied.append(f"Moved {file_name} to Analysis Reports")
                    print(f"✅ Movido: {file_name} -> Analysis Reports")
    
    def optimize_category_distribution(self):
        """Optimiza la distribución de archivos entre categorías"""
        print("📊 Optimizando distribución de categorías...")
        
        # Contar archivos por categoría
        category_counts = defaultdict(int)
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                category = self._get_file_category(str(file_path))
                if category:
                    category_counts[category] += 1
        
        # Identificar categorías sobrecargadas (>200 archivos)
        for category, count in category_counts.items():
            if count > 200:
                print(f"  📁 Categoría {category} tiene {count} archivos - creando subcategorías")
                self._create_subcategories_for_large_category(category)
    
    def create_relationship_maps(self):
        """Crea mapas de relaciones entre archivos"""
        print("🗺️  Creando mapas de relaciones...")
        
        # Crear archivo de relaciones principales
        relationships_file = self.project_root / "00_Version_Management" / "FILE_RELATIONSHIPS.md"
        relationships_file.parent.mkdir(exist_ok=True)
        
        with open(relationships_file, 'w', encoding='utf-8') as f:
            f.write("# Mapa de Relaciones entre Archivos\n\n")
            f.write(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if self.dependency_report:
                f.write("## Archivos Altamente Relacionados\n\n")
                
                # Agrupar por similitud
                high_similarity = []
                for suggestion in self.dependency_report.get('suggestions', []):
                    if suggestion['type'] == 'relocation' and suggestion['similarity'] > 0.95:
                        high_similarity.append(suggestion)
                
                f.write(f"### Archivos con Similitud > 95% ({len(high_similarity)} grupos)\n\n")
                for i, suggestion in enumerate(high_similarity[:20], 1):  # Mostrar solo los primeros 20
                    f.write(f"{i}. **Similitud: {suggestion['similarity']:.1%}**\n")
                    for file_path in suggestion['files']:
                        f.write(f"   - `{Path(file_path).name}`\n")
                    f.write("\n")
                
                f.write("## Referencias Cruzadas por Categoría\n\n")
                for suggestion in self.dependency_report.get('suggestions', []):
                    if suggestion['type'] == 'cross_reference':
                        f.write(f"- **{suggestion['description']}**: {suggestion['count']} referencias\n")
    
    def _get_file_category(self, file_path):
        """Obtiene la categoría de un archivo"""
        path = Path(file_path)
        for part in path.parts:
            if part.startswith(('01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_', '97_', '98_', '99_')):
                return part
        return None
    
    def _count_files_in_category(self, category):
        """Cuenta archivos en una categoría"""
        category_dir = self.project_root / category
        if not category_dir.exists():
            return 0
        return len([f for f in category_dir.iterdir() if f.is_file() and not f.name.startswith('.')])
    
    def _move_file_to_category(self, file_path, target_category):
        """Mueve un archivo a una categoría específica"""
        source_path = Path(file_path)
        if not source_path.exists():
            return
        
        target_dir = self.project_root / target_category
        target_dir.mkdir(exist_ok=True)
        
        target_path = target_dir / source_path.name
        if not target_path.exists():
            try:
                shutil.move(str(source_path), str(target_path))
                self.optimizations_applied.append(f"Moved {source_path.name} to {target_category}")
                print(f"✅ Movido: {source_path.name} -> {target_category}")
            except Exception as e:
                print(f"❌ Error moviendo {source_path.name}: {e}")
    
    def _create_subcategories_for_cross_references(self, category):
        """Crea subcategorías para reducir referencias cruzadas"""
        category_dir = self.project_root / category
        if not category_dir.exists():
            return
        
        # Crear subcategorías basadas en patrones comunes
        subcategories = {
            "Core_Files": [],
            "Reference_Files": [],
            "Template_Files": [],
            "Analysis_Files": []
        }
        
        for subcat in subcategories.keys():
            (category_dir / subcat).mkdir(exist_ok=True)
        
        # Mover archivos basados en patrones
        for file_path in category_dir.iterdir():
            if file_path.is_file() and not file_path.name.startswith('.'):
                filename_lower = file_path.name.lower()
                
                if any(keyword in filename_lower for keyword in ['template', 'template', 'model']):
                    target_subcat = "Template_Files"
                elif any(keyword in filename_lower for keyword in ['reference', 'guide', 'manual']):
                    target_subcat = "Reference_Files"
                elif any(keyword in filename_lower for keyword in ['analysis', 'report', 'summary']):
                    target_subcat = "Analysis_Files"
                else:
                    target_subcat = "Core_Files"
                
                target_path = category_dir / target_subcat / file_path.name
                if not target_path.exists():
                    shutil.move(str(file_path), str(target_path))
                    self.optimizations_applied.append(f"Moved {file_path.name} to {category}/{target_subcat}")
                    print(f"✅ Movido: {file_path.name} -> {category}/{target_subcat}")
    
    def _create_subcategories_for_large_category(self, category):
        """Crea subcategorías para categorías con muchos archivos"""
        category_dir = self.project_root / category
        if not category_dir.exists():
            return
        
        # Crear subcategorías por tipo de archivo
        subcategories = {
            "Documents": ['.md', '.txt', '.doc', '.docx'],
            "Code": ['.py', '.js', '.ts', '.html', '.css'],
            "Data": ['.json', '.csv', '.xlsx', '.xml'],
            "Images": ['.png', '.jpg', '.jpeg', '.gif', '.svg'],
            "Other": []
        }
        
        for subcat, extensions in subcategories.items():
            (category_dir / subcat).mkdir(exist_ok=True)
        
        # Mover archivos a subcategorías apropiadas
        for file_path in category_dir.iterdir():
            if file_path.is_file() and not file_path.name.startswith('.'):
                file_ext = file_path.suffix.lower()
                target_subcat = "Other"
                
                for subcat, extensions in subcategories.items():
                    if file_ext in extensions:
                        target_subcat = subcat
                        break
                
                target_path = category_dir / target_subcat / file_path.name
                if not target_path.exists():
                    shutil.move(str(file_path), str(target_path))
                    self.optimizations_applied.append(f"Moved {file_path.name} to {category}/{target_subcat}")
                    print(f"✅ Movido: {file_path.name} -> {category}/{target_subcat}")
    
    def run_optimization(self):
        """Ejecuta todas las optimizaciones"""
        print("🚀 Iniciando optimización avanzada basada en dependencias...")
        
        self.load_dependency_report()
        self.optimize_similar_files()
        self.optimize_cross_references()
        self.optimize_orphan_files()
        self.create_smart_categories()
        self.optimize_category_distribution()
        self.create_relationship_maps()
        
        print(f"\n✅ Optimización avanzada completada!")
        print(f"Mejoras aplicadas: {len(self.optimizations_applied)}")
        
        return self.optimizations_applied

if __name__ == "__main__":
    optimizer = AdvancedOptimizer("/Users/adan/frontier")
    optimizations = optimizer.run_optimization()
    
    print(f"\n📋 RESUMEN DE OPTIMIZACIONES AVANZADAS:")
    for i, opt in enumerate(optimizations, 1):
        print(f"  {i:3d}. {opt}")


