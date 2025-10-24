#!/usr/bin/env python3
"""
Script de Validación de Documentación
Repositorio: Documentos Blatam
Autor: Sistema de Optimización Automática
Fecha: 2025
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

class DocumentationValidator:
    def __init__(self, root_path="."):
        self.root_path = Path(root_path)
        self.issues = []
        self.stats = {
            'total_files': 0,
            'valid_files': 0,
            'issues_found': 0,
            'categories': {}
        }
    
    def validate_markdown_file(self, file_path):
        """Valida un archivo Markdown"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues = []
            
            # Verificar estructura básica
            if not content.strip():
                issues.append("Archivo vacío")
                return issues
            
            # Verificar headers
            headers = re.findall(r'^#+\s+.+', content, re.MULTILINE)
            if not headers:
                issues.append("Sin headers de sección")
            
            # Verificar enlaces rotos (básico)
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            for link_text, link_url in links:
                if link_url.startswith('http') and 'github.com' in link_url:
                    # Verificar enlaces de GitHub
                    pass
                elif not link_url.startswith('http') and not link_url.startswith('#'):
                    # Enlace local
                    if not os.path.exists(link_url):
                        issues.append(f"Enlace local roto: {link_url}")
            
            # Verificar imágenes
            images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
            for alt_text, img_url in images:
                if not img_url.startswith('http') and not os.path.exists(img_url):
                    issues.append(f"Imagen no encontrada: {img_url}")
            
            return issues
            
        except Exception as e:
            return [f"Error al leer archivo: {str(e)}"]
    
    def validate_structure(self):
        """Valida la estructura de carpetas"""
        expected_folders = [
            "01_Marketing", "02_Finance", "03_Human_Resources",
            "04_Operations", "05_Technology", "06_Strategy",
            "07_Risk_Management", "08_AI_Artificial_Intelligence",
            "09_Sales", "10_Customer_Service", "11_Research_Development",
            "12_Quality_Assurance", "13_Legal_Compliance",
            "14_Product_Management", "15_Customer_Experience",
            "16_Data_Analytics", "17_Innovation", "18_Sustainability",
            "19_International_Business", "20_Project_Management",
            "21_Supply_Chain", "22_Real_Estate", "23_Healthcare",
            "24_Education", "25_Government", "26_Non_Profit",
            "27_Entertainment", "28_Sports", "29_Media",
            "30_Consulting", "31_Professional_Services",
            "32_Manufacturing", "33_Retail", "34_E_Commerce"
        ]
        
        missing_folders = []
        for folder in expected_folders:
            if not (self.root_path / folder).exists():
                missing_folders.append(folder)
        
        if missing_folders:
            self.issues.append(f"Carpetas faltantes: {', '.join(missing_folders)}")
    
    def validate_readme_files(self):
        """Valida archivos README en cada carpeta principal"""
        for folder in self.root_path.iterdir():
            if folder.is_dir() and folder.name.startswith(('0', '1', '2', '3')):
                readme_path = folder / "README.md"
                if not readme_path.exists():
                    self.issues.append(f"README faltante en {folder.name}")
    
    def scan_documentation(self):
        """Escanea toda la documentación"""
        print("🔍 Iniciando validación de documentación...")
        
        # Validar estructura
        self.validate_structure()
        self.validate_readme_files()
        
        # Escanear archivos
        for file_path in self.root_path.rglob("*.md"):
            if file_path.name.startswith('.'):
                continue
                
            self.stats['total_files'] += 1
            
            # Categorizar archivo
            category = self.get_category(file_path)
            if category not in self.stats['categories']:
                self.stats['categories'][category] = 0
            self.stats['categories'][category] += 1
            
            # Validar archivo
            issues = self.validate_markdown_file(file_path)
            if issues:
                self.stats['issues_found'] += len(issues)
                self.issues.append({
                    'file': str(file_path.relative_to(self.root_path)),
                    'issues': issues
                })
            else:
                self.stats['valid_files'] += 1
    
    def get_category(self, file_path):
        """Obtiene la categoría de un archivo"""
        parts = file_path.parts
        if len(parts) > 1 and parts[0].startswith(('0', '1', '2', '3')):
            return parts[0]
        return "Root"
    
    def generate_report(self):
        """Genera reporte de validación"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'issues': self.issues,
            'summary': {
                'total_files_checked': self.stats['total_files'],
                'valid_files': self.stats['valid_files'],
                'files_with_issues': len(self.issues),
                'total_issues': self.stats['issues_found'],
                'success_rate': (self.stats['valid_files'] / self.stats['total_files'] * 100) if self.stats['total_files'] > 0 else 0
            }
        }
        
        return report
    
    def print_summary(self):
        """Imprime resumen de validación"""
        print("\n" + "="*60)
        print("📊 RESUMEN DE VALIDACIÓN DE DOCUMENTACIÓN")
        print("="*60)
        print(f"📁 Total de archivos analizados: {self.stats['total_files']}")
        print(f"✅ Archivos válidos: {self.stats['valid_files']}")
        print(f"❌ Archivos con problemas: {len(self.issues)}")
        print(f"🔧 Total de problemas encontrados: {self.stats['issues_found']}")
        print(f"📈 Tasa de éxito: {self.stats['valid_files'] / self.stats['total_files'] * 100:.1f}%")
        
        print("\n📂 DISTRIBUCIÓN POR CATEGORÍAS:")
        for category, count in sorted(self.stats['categories'].items()):
            print(f"  {category}: {count} archivos")
        
        if self.issues:
            print("\n⚠️  PROBLEMAS ENCONTRADOS:")
            for issue in self.issues[:10]:  # Mostrar solo los primeros 10
                if isinstance(issue, dict):
                    print(f"  📄 {issue['file']}: {', '.join(issue['issues'])}")
                else:
                    print(f"  🔧 {issue}")
        
        print("\n" + "="*60)

def main():
    """Función principal"""
    print("🚀 Iniciando validación de documentación...")
    
    validator = DocumentationValidator()
    validator.scan_documentation()
    validator.print_summary()
    
    # Guardar reporte
    report = validator.generate_report()
    with open('validation_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Reporte guardado en: validation_report.json")
    
    if validator.stats['issues_found'] == 0:
        print("🎉 ¡Validación exitosa! No se encontraron problemas.")
    else:
        print(f"⚠️  Se encontraron {validator.stats['issues_found']} problemas que requieren atención.")

if __name__ == "__main__":
    main()
