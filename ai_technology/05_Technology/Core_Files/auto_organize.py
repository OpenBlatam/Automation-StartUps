#!/usr/bin/env python3
"""
Script de Organización Automática para Proyecto Frontier
Organiza automáticamente los documentos en las categorías apropiadas
"""

import os
import shutil
import re
from pathlib import Path
from typing import Dict, List, Tuple

class FrontierOrganizer:
    def __init__(self, root_path: str = "/Users/adan/frontier"):
        self.root_path = Path(root_path)
        self.categories = self._define_categories()
        self.file_patterns = self._define_file_patterns()
        
    def _define_categories(self) -> Dict[str, str]:
        """Define las categorías principales y sus rutas"""
        return {
            "marketing": "01_Marketing",
            "consciousness": "02_Consciousness_Systems", 
            "finance": "02_Finance",
            "hr": "03_Human_Resources",
            "business": "04_Business_Strategy",
            "technology": "05_Technology",
            "documentation": "06_Documentation",
            "advanced": "07_Advanced_Features",
            "risk": "07_Risk_Management",
            "ai": "08_AI_Artificial_Intelligence",
            "sales": "09_Sales",
            "customer": "10_Customer_Service",
            "research": "11_Research_Development",
            "architecture": "11_System_Architecture",
            "quality": "12_Quality_Assurance",
            "guides": "12_User_Guides",
            "legal": "13_Legal_Compliance",
            "status": "13_Project_Status",
            "procurement": "14_Procurement",
            "thought": "14_Thought_Leadership",
            "logistics": "15_Logistics",
            "analytics": "16_Data_Analytics",
            "innovation": "17_Innovation",
            "sustainability": "18_Sustainability",
            "international": "19_International_Business",
            "project": "20_Project_Management"
        }
    
    def _define_file_patterns(self) -> Dict[str, List[str]]:
        """Define patrones de archivos para cada categoría"""
        return {
            "marketing": [
                "*AI_Marketing*", "*Neural*", "*Consciousness*", "*CopyAI*",
                "*ABM*", "*Gamification*", "*Course*", "*CURSO*", "*Workshop*",
                "*Case*", "*Casos*", "*EXAMPLES*", "*Complete*", "*Ultimate*",
                "*Enhanced*", "*Ecosistema*", "*Playbook*", "*Playbooks*",
                "*Materials*", "*Training*", "*Assessment*", "*Certification*"
            ],
            "consciousness": [
                "*Sistema*", "*Spiritual*", "*Universal*", "*Divine*",
                "*Transcendent*", "*Conscious*", "*Infinite*", "*Cosmic*"
            ],
            "ai": [
                "*Advanced_AI*", "*ai-marketing*", "*Artificial*", "*Blockchain*",
                "*Quantum*", "*Neural*", "*Machine*", "*Deep*", "*Algorithm*"
            ],
            "technology": [
                "*API*", "*ARCHITECTURE*", "*Implementation*", "*DOCUMENTATION*",
                "*Guide*", "*Changelog*", "*CONTRIBUTING*", "*README*",
                "*DASHBOARD*", "*ENTERPRISE*", "*DEVELOPER*", "*Demo*",
                "*Checklist*", "*Summary*", "*Templates*", "*Technical*"
            ],
            "business": [
                "*BUSINESS*", "*COMPETITIVE*", "*ROI*", "*Estrategia*",
                "*calculadora*", "*Market_Research*", "*Strategy*", "*Plan*"
            ],
            "legal": [
                "*Commission*", "*VIP*", "*Legal*", "*Compliance*",
                "*Agreement*", "*Contract*", "*Terms*", "*Policy*"
            ],
            "customer": [
                "*Customer*", "*Success*", "*Metrics*", "*Journey*",
                "*Mapping*", "*Support*", "*Service*"
            ],
            "sales": [
                "*Sales*", "*Venta*", "*Cierre*", "*Pitch*", "*Deck*",
                "*Proposal*", "*Quote*", "*Lead*"
            ],
            "risk": [
                "*Risk*", "*Crisis*", "*Security*", "*Compliance*",
                "*Audit*", "*Assessment*"
            ],
            "analytics": [
                "*Analytics*", "*Dashboard*", "*Metrics*", "*Data*",
                "*Report*", "*Insight*", "*KPI*"
            ],
            "project": [
                "*Project*", "*Timeline*", "*Milestone*", "*Status*",
                "*Progress*", "*Task*", "*Resource*"
            ],
            "research": [
                "*Research*", "*Study*", "*Paper*", "*Analysis*",
                "*Investigation*", "*Discovery*"
            ],
            "innovation": [
                "*Innovation*", "*Future*", "*Vision*", "*Trend*",
                "*Disruptive*", "*Breakthrough*"
            ]
        }
    
    def categorize_file(self, filename: str) -> Tuple[str, str]:
        """
        Categoriza un archivo basado en su nombre
        Retorna: (categoria, subcategoria)
        """
        filename_lower = filename.lower()
        
        # Patrones específicos para subcategorías
        subcategory_patterns = {
            "ai_courses": ["course", "curso", "training", "workshop", "lesson"],
            "consciousness": ["consciousness", "conscious", "spiritual", "divine"],
            "neural": ["neural", "brain", "mind", "cognitive"],
            "copyai": ["copy", "copyai", "copywriting", "content"],
            "abm": ["abm", "account", "based", "marketing"],
            "gamification": ["game", "gamification", "reward", "points"],
            "vip": ["vip", "premium", "exclusive", "membership"],
            "api": ["api", "endpoint", "service", "integration"],
            "architecture": ["architecture", "system", "infrastructure"],
            "implementation": ["implementation", "setup", "install", "deploy"],
            "technical": ["technical", "spec", "documentation", "guide"],
            "business_plans": ["business", "plan", "strategy", "model"],
            "competitive": ["competitive", "competitor", "analysis", "benchmark"],
            "roi": ["roi", "return", "investment", "calculator", "calculadora"],
            "market_research": ["market", "research", "study", "analysis"],
            "commission": ["commission", "agreement", "contract", "deal"],
            "compliance": ["compliance", "legal", "policy", "regulation"],
            "customer_success": ["customer", "success", "journey", "experience"],
            "sales_playbooks": ["sales", "playbook", "script", "pitch"],
            "risk_assessment": ["risk", "crisis", "security", "threat"],
            "analytics_dashboards": ["analytics", "dashboard", "metrics", "kpi"],
            "project_plans": ["project", "timeline", "milestone", "status"],
            "research_papers": ["research", "paper", "study", "analysis"],
            "innovation_labs": ["innovation", "lab", "future", "vision"]
        }
        
        # Determinar categoría principal
        for category, patterns in self.file_patterns.items():
            for pattern in patterns:
                if self._match_pattern(filename, pattern):
                    # Determinar subcategoría
                    for subcat, subcat_patterns in subcategory_patterns.items():
                        if any(pattern in filename_lower for pattern in subcat_patterns):
                            return category, subcat
                    return category, "general"
        
        return "documentation", "general"
    
    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """Verifica si un archivo coincide con un patrón"""
        pattern = pattern.replace("*", ".*")
        return bool(re.search(pattern, filename, re.IGNORECASE))
    
    def get_target_path(self, category: str, subcategory: str) -> Path:
        """Obtiene la ruta objetivo para un archivo"""
        base_path = self.root_path / self.categories[category]
        
        if subcategory == "general":
            return base_path
        
        # Crear subcategorías específicas
        subcategory_mapping = {
            "ai_courses": "AI_Marketing_Courses",
            "consciousness": "Consciousness_Marketing", 
            "neural": "Neural_Marketing",
            "copyai": "CopyAI_Integration",
            "abm": "ABM_Strategy",
            "gamification": "Gamification",
            "vip": "VIP_Programs",
            "api": "API_Documentation",
            "architecture": "System_Architecture",
            "implementation": "Implementation_Guides",
            "technical": "Technical_Specs",
            "business_plans": "Business_Plans",
            "competitive": "Competitive_Analysis",
            "roi": "ROI_Calculations",
            "market_research": "Market_Research",
            "commission": "Commission_Agreements",
            "compliance": "Compliance_Docs",
            "customer_success": "Customer_Success",
            "sales_playbooks": "Sales_Playbooks",
            "risk_assessment": "Risk_Assessments",
            "analytics_dashboards": "Analytics_Dashboards",
            "project_plans": "Project_Plans",
            "research_papers": "Research_Papers",
            "innovation_labs": "Innovation_Labs"
        }
        
        subcategory_folder = subcategory_mapping.get(subcategory, subcategory)
        return base_path / subcategory_folder
    
    def organize_file(self, file_path: Path) -> bool:
        """Organiza un archivo individual"""
        try:
            category, subcategory = self.categorize_file(file_path.name)
            target_path = self.get_target_path(category, subcategory)
            
            # Crear directorio si no existe
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Mover archivo
            new_path = target_path / file_path.name
            if new_path.exists():
                # Si ya existe, agregar timestamp
                stem = file_path.stem
                suffix = file_path.suffix
                timestamp = int(time.time())
                new_path = target_path / f"{stem}_{timestamp}{suffix}"
            
            shutil.move(str(file_path), str(new_path))
            print(f"✅ Movido: {file_path.name} → {target_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error moviendo {file_path.name}: {e}")
            return False
    
    def organize_directory(self, directory: Path = None) -> Dict[str, int]:
        """Organiza todos los archivos en un directorio"""
        if directory is None:
            directory = self.root_path
        
        results = {"moved": 0, "errors": 0, "skipped": 0}
        
        # Archivos a procesar
        files_to_process = []
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix in ['.md', '.py', '.html', '.pdf', '.docx']:
                # Saltar archivos ya organizados
                if not any(file_path.name.startswith(prefix) for prefix in ['01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_', '11_', '12_', '13_', '14_', '15_', '16_', '17_', '18_', '19_', '20_']):
                    files_to_process.append(file_path)
        
        print(f"📁 Procesando {len(files_to_process)} archivos...")
        
        for file_path in files_to_process:
            if self.organize_file(file_path):
                results["moved"] += 1
            else:
                results["errors"] += 1
        
        return results
    
    def create_index_files(self):
        """Crea archivos índice para cada categoría"""
        for category, path in self.categories.items():
            category_path = self.root_path / path
            if category_path.exists():
                index_file = category_path / "README.md"
                if not index_file.exists():
                    self._create_category_index(category, category_path)
    
    def _create_category_index(self, category: str, path: Path):
        """Crea un archivo índice para una categoría"""
        import time
        category_names = {
            "marketing": "Marketing",
            "consciousness": "Consciousness Systems",
            "finance": "Finance", 
            "hr": "Human Resources",
            "business": "Business Strategy",
            "technology": "Technology",
            "documentation": "Documentation",
            "advanced": "Advanced Features",
            "risk": "Risk Management",
            "ai": "AI & Artificial Intelligence",
            "sales": "Sales",
            "customer": "Customer Service",
            "research": "Research & Development",
            "architecture": "System Architecture",
            "quality": "Quality Assurance",
            "guides": "User Guides",
            "legal": "Legal & Compliance",
            "status": "Project Status",
            "procurement": "Procurement",
            "thought": "Thought Leadership",
            "logistics": "Logistics",
            "analytics": "Data Analytics",
            "innovation": "Innovation",
            "sustainability": "Sustainability",
            "international": "International Business",
            "project": "Project Management"
        }
        
        content = f"""# {category_names.get(category, category.title())}

## 📋 Descripción
Esta categoría contiene documentos relacionados con {category_names.get(category, category)}.

## 📁 Subcategorías
"""
        
        # Agregar subcategorías existentes
        for subdir in path.iterdir():
            if subdir.is_dir():
                content += f"- **{subdir.name}**: {subdir.name.replace('_', ' ').title()}\n"
        
        content += f"""
## 🔍 Cómo usar
1. Navega por las subcategorías para encontrar documentos específicos
2. Usa la búsqueda para encontrar contenido específico
3. Consulta el índice maestro para una visión general

## 📊 Estadísticas
- **Total de archivos**: {len(list(path.rglob('*')))} 
- **Última actualización**: {time.strftime('%Y-%m-%d %H:%M:%S')}

---
*Categoría: {category_names.get(category, category)}*
*Mantenido por: Sistema de Organización Automática*
"""
        
        with open(path / "README.md", 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    """Función principal"""
    import time
    
    print("🚀 Iniciando organización automática del proyecto Frontier...")
    
    organizer = FrontierOrganizer()
    
    # Organizar archivos
    results = organizer.organize_directory()
    
    print(f"\n📊 Resultados:")
    print(f"✅ Archivos movidos: {results['moved']}")
    print(f"❌ Errores: {results['errors']}")
    print(f"⏭️  Saltados: {results['skipped']}")
    
    # Crear archivos índice
    print("\n📝 Creando archivos índice...")
    organizer.create_index_files()
    
    print("\n🎉 ¡Organización completada!")

if __name__ == "__main__":
    main()
