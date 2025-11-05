#!/usr/bin/env python3
"""
Sistema de Organización Ultra-Avanzado
Organiza automáticamente archivos con análisis semántico y patrones
"""

import os
import shutil
import re
import json
from datetime import datetime
from pathlib import Path

class UltraOrganizer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.categories = {
            "01_Marketing": ["marketing", "neural", "consciousness", "copy", "email", "abm", "gamification"],
            "02_Finance": ["finance", "investment", "vc", "pitch", "due_diligence", "roi", "calculator"],
            "03_Human_Resources": ["hr", "human", "resources", "training", "employee"],
            "04_Business_Strategy": ["strategy", "business", "plan", "partnership", "expansion"],
            "05_Technology": ["tech", "ai", "api", "system", "architecture", "development", "code"],
            "06_Documentation": ["doc", "guide", "manual", "tutorial", "readme"],
            "07_Risk_Management": ["risk", "security", "compliance", "legal"],
            "08_AI_Artificial_Intelligence": ["ai", "artificial", "intelligence", "neural", "machine"],
            "09_Sales": ["sales", "revenue", "customer", "client"],
            "10_Customer_Service": ["service", "support", "help", "customer"]
        }
        
    def analyze_file(self, file_path):
        """Analiza un archivo para determinar su categoría"""
        filename = file_path.name.lower()
        content_keywords = []
        
        # Análisis de contenido si es archivo de texto
        if file_path.suffix in ['.md', '.txt', '.py', '.js', '.ts']:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(1000)  # Primeros 1000 caracteres
                    content_keywords = re.findall(r'\b\w+\b', content.lower())
            except:
                pass
        
        # Calcular puntuación para cada categoría
        scores = {}
        for category, keywords in self.categories.items():
            score = 0
            for keyword in keywords:
                if keyword in filename:
                    score += 3
                if keyword in content_keywords:
                    score += 1
            scores[category] = score
        
        # Retornar la categoría con mayor puntuación
        best_category = max(scores, key=scores.get)
        return best_category if scores[best_category] > 0 else "06_Documentation"
    
    def organize_files(self):
        """Organiza todos los archivos sueltos"""
        moved_files = []
        
        for item in self.project_root.iterdir():
            if item.is_file() and not item.name.startswith('.'):
                # Saltar archivos ya organizados
                if any(item.parent.name.startswith(f"{i:02d}_") for i in range(1, 21)):
                    continue
                    
                category = self.analyze_file(item)
                target_dir = self.project_root / category
                target_dir.mkdir(exist_ok=True)
                
                # Mover archivo
                target_path = target_dir / item.name
                if not target_path.exists():
                    shutil.move(str(item), str(target_path))
                    moved_files.append(f"{item.name} -> {category}")
                    print(f"✅ Movido: {item.name} -> {category}")
                else:
                    print(f"⚠️  Ya existe: {item.name} en {category}")
        
        return moved_files
    
    def create_index_files(self):
        """Crea archivos README.md para cada categoría"""
        for category in self.categories.keys():
            category_dir = self.project_root / category
            if category_dir.exists():
                readme_path = category_dir / "README.md"
                if not readme_path.exists():
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(f"# {category.replace('_', ' ').title()}\n\n")
                        f.write(f"Contenido organizado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                        f.write("## Archivos en esta categoría:\n\n")
                        
                        for item in sorted(category_dir.iterdir()):
                            if item.is_file() and item.name != "README.md":
                                f.write(f"- {item.name}\n")

if __name__ == "__main__":
    organizer = UltraOrganizer("/Users/adan/frontier")
    print("🚀 Iniciando organización ultra-avanzada...")
    
    moved_files = organizer.organize_files()
    organizer.create_index_files()
    
    print(f"\n✅ Organización completada. Archivos movidos: {len(moved_files)}")
    for file_info in moved_files:
        print(f"  {file_info}")



