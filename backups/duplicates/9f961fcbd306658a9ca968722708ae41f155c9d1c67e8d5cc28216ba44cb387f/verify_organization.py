#!/usr/bin/env python3
"""
Script de Verificación de Organización para Proyecto Frontier
Verifica que todos los documentos estén correctamente organizados
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

class OrganizationVerifier:
    def __init__(self, root_path: str = "/Users/adan/frontier"):
        self.root_path = Path(root_path)
        self.categories = self._get_categories()
        self.issues = []
        self.stats = {}
        
    def _get_categories(self) -> List[str]:
        """Obtiene las categorías principales"""
        categories = []
        for item in self.root_path.iterdir():
            if item.is_dir() and item.name.startswith(('01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_', '11_', '12_', '13_', '14_', '15_', '16_', '17_', '18_', '19_', '20_')):
                categories.append(item.name)
        return sorted(categories)
    
    def verify_organization(self) -> Dict:
        """Verifica la organización completa del proyecto"""
        print("🔍 Verificando organización del proyecto Frontier...")
        
        # Verificar estructura de categorías
        self._verify_category_structure()
        
        # Verificar archivos sueltos
        self._verify_loose_files()
        
        # Verificar archivos índice
        self._verify_index_files()
        
        # Generar estadísticas
        self._generate_stats()
        
        return {
            "issues": self.issues,
            "stats": self.stats,
            "categories": self.categories,
            "timestamp": datetime.now().isoformat()
        }
    
    def _verify_category_structure(self):
        """Verifica la estructura de las categorías"""
        print("📁 Verificando estructura de categorías...")
        
        for category in self.categories:
            category_path = self.root_path / category
            if not category_path.exists():
                self.issues.append({
                    "type": "missing_category",
                    "category": category,
                    "severity": "high",
                    "message": f"Categoría {category} no existe"
                })
            else:
                # Verificar subcategorías
                subcategories = [item for item in category_path.iterdir() if item.is_dir()]
                if not subcategories:
                    self.issues.append({
                        "type": "empty_category",
                        "category": category,
                        "severity": "medium",
                        "message": f"Categoría {category} no tiene subcategorías"
                    })
    
    def _verify_loose_files(self):
        """Verifica archivos sueltos en el directorio raíz"""
        print("📄 Verificando archivos sueltos...")
        
        loose_files = []
        for item in self.root_path.iterdir():
            if item.is_file() and item.suffix in ['.md', '.py', '.html', '.pdf', '.docx']:
                # Saltar archivos del sistema
                if not item.name.startswith(('.', 'ORGANIZACION_MAESTRA')):
                    loose_files.append(item.name)
        
        if loose_files:
            self.issues.append({
                "type": "loose_files",
                "files": loose_files,
                "severity": "medium",
                "message": f"Se encontraron {len(loose_files)} archivos sueltos en el directorio raíz"
            })
    
    def _verify_index_files(self):
        """Verifica archivos índice en cada categoría"""
        print("📝 Verificando archivos índice...")
        
        for category in self.categories:
            category_path = self.root_path / category
            index_file = category_path / "README.md"
            
            if not index_file.exists():
                self.issues.append({
                    "type": "missing_index",
                    "category": category,
                    "severity": "low",
                    "message": f"Categoría {category} no tiene archivo README.md"
                })
    
    def _generate_stats(self):
        """Genera estadísticas de organización"""
        print("📊 Generando estadísticas...")
        
        total_files = 0
        total_dirs = 0
        category_stats = {}
        
        for category in self.categories:
            category_path = self.root_path / category
            if category_path.exists():
                files = list(category_path.rglob('*'))
                file_count = len([f for f in files if f.is_file()])
                dir_count = len([f for f in files if f.is_dir()])
                
                category_stats[category] = {
                    "files": file_count,
                    "directories": dir_count,
                    "subcategories": len([d for d in category_path.iterdir() if d.is_dir()])
                }
                
                total_files += file_count
                total_dirs += dir_count
        
        self.stats = {
            "total_files": total_files,
            "total_directories": total_dirs,
            "total_categories": len(self.categories),
            "category_stats": category_stats,
            "organization_score": self._calculate_organization_score()
        }
    
    def _calculate_organization_score(self) -> float:
        """Calcula un puntaje de organización (0-100)"""
        score = 100.0
        
        # Penalizar por archivos sueltos
        loose_files = len([f for f in self.root_path.iterdir() if f.is_file() and f.suffix in ['.md', '.py', '.html', '.pdf', '.docx'] and not f.name.startswith('.')])
        score -= min(loose_files * 2, 20)  # Máximo 20 puntos de penalización
        
        # Penalizar por categorías vacías
        empty_categories = 0
        for category in self.categories:
            category_path = self.root_path / category
            if category_path.exists():
                subcategories = [item for item in category_path.iterdir() if item.is_dir()]
                if not subcategories:
                    empty_categories += 1
        
        score -= min(empty_categories * 5, 15)  # Máximo 15 puntos de penalización
        
        # Penalizar por archivos índice faltantes
        missing_indexes = 0
        for category in self.categories:
            category_path = self.root_path / category
            index_file = category_path / "README.md"
            if not index_file.exists():
                missing_indexes += 1
        
        score -= min(missing_indexes * 1, 10)  # Máximo 10 puntos de penalización
        
        return max(score, 0.0)
    
    def generate_report(self, output_file: str = None) -> str:
        """Genera un reporte de verificación"""
        verification_data = self.verify_organization()
        
        report = f"""# 🔍 REPORTE DE VERIFICACIÓN DE ORGANIZACIÓN
**Proyecto**: Frontier  
**Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Puntaje de Organización**: {verification_data['stats']['organization_score']:.1f}/100

## 📊 ESTADÍSTICAS GENERALES

- **Total de archivos**: {verification_data['stats']['total_files']}
- **Total de directorios**: {verification_data['stats']['total_directories']}
- **Total de categorías**: {verification_data['stats']['total_categories']}

## 📁 ESTADÍSTICAS POR CATEGORÍA

"""
        
        for category, stats in verification_data['stats']['category_stats'].items():
            report += f"### {category}\n"
            report += f"- **Archivos**: {stats['files']}\n"
            report += f"- **Directorios**: {stats['directories']}\n"
            report += f"- **Subcategorías**: {stats['subcategories']}\n\n"
        
        if verification_data['issues']:
            report += "## ⚠️ PROBLEMAS ENCONTRADOS\n\n"
            
            # Agrupar problemas por severidad
            high_issues = [i for i in verification_data['issues'] if i['severity'] == 'high']
            medium_issues = [i for i in verification_data['issues'] if i['severity'] == 'medium']
            low_issues = [i for i in verification_data['issues'] if i['severity'] == 'low']
            
            if high_issues:
                report += "### 🔴 Problemas Críticos\n"
                for issue in high_issues:
                    report += f"- **{issue['type']}**: {issue['message']}\n"
                report += "\n"
            
            if medium_issues:
                report += "### 🟡 Problemas Moderados\n"
                for issue in medium_issues:
                    report += f"- **{issue['type']}**: {issue['message']}\n"
                report += "\n"
            
            if low_issues:
                report += "### 🟢 Problemas Menores\n"
                for issue in low_issues:
                    report += f"- **{issue['type']}**: {issue['message']}\n"
                report += "\n"
        else:
            report += "## ✅ ¡ORGANIZACIÓN PERFECTA!\n\nNo se encontraron problemas en la organización del proyecto.\n\n"
        
        report += "## 🚀 RECOMENDACIONES\n\n"
        
        if verification_data['stats']['organization_score'] < 80:
            report += "1. **Ejecutar script de organización automática** para corregir problemas\n"
            report += "2. **Revisar archivos sueltos** y moverlos a categorías apropiadas\n"
            report += "3. **Crear archivos índice** para categorías que no los tienen\n"
        else:
            report += "1. **Mantener la organización actual** - está funcionando bien\n"
            report += "2. **Ejecutar verificaciones regulares** para mantener la calidad\n"
            report += "3. **Actualizar archivos índice** cuando se agreguen nuevos documentos\n"
        
        report += "\n---\n*Reporte generado automáticamente por el Sistema de Verificación de Organización*"
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Reporte guardado en: {output_file}")
        
        return report

def main():
    """Función principal"""
    verifier = OrganizationVerifier()
    
    # Generar reporte
    report = verifier.generate_report("ORGANIZACION_VERIFICATION_REPORT.md")
    
    # Mostrar resumen
    print("\n" + "="*50)
    print("📋 RESUMEN DE VERIFICACIÓN")
    print("="*50)
    print(report.split("## 📊 ESTADÍSTICAS GENERALES")[0])
    
    # Mostrar puntaje
    verification_data = verifier.verify_organization()
    score = verification_data['stats']['organization_score']
    
    if score >= 90:
        print(f"🎉 ¡EXCELENTE! Puntaje: {score:.1f}/100")
    elif score >= 80:
        print(f"✅ ¡BUENO! Puntaje: {score:.1f}/100")
    elif score >= 70:
        print(f"⚠️  REGULAR. Puntaje: {score:.1f}/100")
    else:
        print(f"❌ NECESITA MEJORAS. Puntaje: {score:.1f}/100")

if __name__ == "__main__":
    main()
