#!/usr/bin/env python3
"""
Verificador Avanzado de Organización
Calcula puntuación de organización y genera reportes detallados
"""

import os
import json
from datetime import datetime
from pathlib import Path

class AdvancedVerifier:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.categories = [
            "01_Marketing", "02_Finance", "03_Human_Resources", 
            "04_Business_Strategy", "05_Technology", "06_Documentation",
            "07_Risk_Management", "08_AI_Artificial_Intelligence",
            "09_Sales", "10_Customer_Service"
        ]
    
    def calculate_organization_score(self):
        """Calcula la puntuación de organización del proyecto"""
        total_files = 0
        organized_files = 0
        unorganized_files = []
        
        # Contar archivos organizados
        for category in self.categories:
            category_dir = self.project_root / category
            if category_dir.exists():
                for item in category_dir.iterdir():
                    if item.is_file() and not item.name.startswith('.'):
                        organized_files += 1
                        total_files += 1
        
        # Contar archivos desorganizados en raíz
        for item in self.project_root.iterdir():
            if item.is_file() and not item.name.startswith('.'):
                if not any(item.parent.name.startswith(f"{i:02d}_") for i in range(1, 21)):
                    unorganized_files.append(item.name)
                    total_files += 1
        
        # Calcular puntuación
        if total_files == 0:
            return 0, 0, 0, []
        
        score = (organized_files / total_files) * 100
        return score, organized_files, total_files, unorganized_files
    
    def generate_report(self):
        """Genera un reporte detallado de organización"""
        score, organized, total, unorganized = self.calculate_organization_score()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "organization_score": round(score, 2),
            "total_files": total,
            "organized_files": organized,
            "unorganized_files": len(unorganized),
            "unorganized_list": unorganized,
            "categories_status": {}
        }
        
        # Estado de cada categoría
        for category in self.categories:
            category_dir = self.project_root / category
            if category_dir.exists():
                files_count = len([f for f in category_dir.iterdir() if f.is_file() and not f.name.startswith('.')])
                report["categories_status"][category] = {
                    "files_count": files_count,
                    "has_readme": (category_dir / "README.md").exists()
                }
        
        return report
    
    def save_report(self, report):
        """Guarda el reporte en un archivo JSON"""
        report_path = self.project_root / "organization_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        return report_path

if __name__ == "__main__":
    verifier = AdvancedVerifier("/Users/adan/frontier")
    
    print("🔍 Verificando organización del proyecto...")
    report = verifier.generate_report()
    
    print(f"\n📊 REPORTE DE ORGANIZACIÓN")
    print(f"Puntuación: {report['organization_score']}%")
    print(f"Archivos totales: {report['total_files']}")
    print(f"Archivos organizados: {report['organized_files']}")
    print(f"Archivos desorganizados: {report['unorganized_files']}")
    
    if report['unorganized_files'] > 0:
        print(f"\n⚠️  Archivos desorganizados:")
        for file in report['unorganized_list']:
            print(f"  - {file}")
    
    # Guardar reporte
    report_path = verifier.save_report(report)
    print(f"\n💾 Reporte guardado en: {report_path}")



