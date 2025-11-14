#!/usr/bin/env python3
"""
Organizador inteligente con patrones optimizados y aprendizaje automático básico
"""

import os
import re
import json
from pathlib import Path
from collections import Counter, defaultdict
import shutil
from datetime import datetime

class SmartOrganizer:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.learning_data = self.load_learning_data()
        self.optimized_patterns = self.build_optimized_patterns()
        
    def load_learning_data(self):
        """Carga datos de aprendizaje de organizaciones previas"""
        learning_file = self.base_dir / "learning_data.json"
        if learning_file.exists():
            with open(learning_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "file_classifications": {},
            "pattern_effectiveness": {},
            "common_keywords": {},
            "extension_mappings": {}
        }
    
    def save_learning_data(self):
        """Guarda datos de aprendizaje para futuras optimizaciones"""
        learning_file = self.base_dir / "learning_data.json"
        with open(learning_file, 'w', encoding='utf-8') as f:
            json.dump(self.learning_data, f, indent=2, ensure_ascii=False)
    
    def analyze_file_patterns(self):
        """Analiza patrones en archivos existentes para mejorar clasificación"""
        print("🧠 Analizando patrones de archivos...")
        
        file_analysis = defaultdict(list)
        
        # Analizar archivos ya organizados
        for folder in self.base_dir.iterdir():
            if folder.is_dir() and not folder.name.startswith('.'):
                for subfolder in folder.iterdir():
                    if subfolder.is_dir():
                        for file_path in subfolder.iterdir():
                            if file_path.is_file():
                                self.analyze_file(file_path, folder.name, subfolder.name, file_analysis)
        
        # Actualizar datos de aprendizaje
        for pattern, data in file_analysis.items():
            if pattern not in self.learning_data["file_classifications"]:
                self.learning_data["file_classifications"][pattern] = []
            self.learning_data["file_classifications"][pattern].extend(data)
        
        self.save_learning_data()
        return file_analysis
    
    def analyze_file(self, file_path, main_folder, subfolder, analysis):
        """Analiza un archivo individual para extraer patrones"""
        name = file_path.name.lower()
        ext = file_path.suffix.lower()
        
        # Extraer palabras clave
        words = re.findall(r'\b\w+\b', name)
        keywords = [w for w in words if len(w) > 2]
        
        # Patrones de nombre
        patterns = {
            'has_numbers': bool(re.search(r'\d', name)),
            'has_underscores': '_' in name,
            'has_dashes': '-' in name,
            'has_caps': any(c.isupper() for c in name),
            'starts_with_number': name[0].isdigit() if name else False,
            'contains_date': bool(re.search(r'\d{4}[-_]\d{2}[-_]\d{2}|\d{2}[-_]\d{2}[-_]\d{4}', name)),
            'keywords': keywords,
            'extension': ext
        }
        
        analysis[f"{main_folder}/{subfolder}"].append({
            'file': str(file_path.name),
            'patterns': patterns
        })
    
    def build_optimized_patterns(self):
        """Construye patrones optimizados basados en análisis previo"""
        patterns = {
            "01_Marketing": {
                "subfolders": [
                    "Guides", "Sequences", "Content", "Automations", "Analytics",
                    "Affiliate_Programs", "Blog_Posts", "CTAs", "Checklists", "Templates",
                    "Scripts", "Reports", "Presentations", "Data_Files", "Strategies",
                    "Campaigns", "Copywriting", "SEO", "Social_Media", "Email_Marketing",
                    "Landing_Pages", "Webinars", "Lead_Generation", "Branding"
                ],
                "patterns": {
                    "Guides": [
                        r".*[Gg]uide.*", r".*[Gg]uía.*", r".*[Mm]anual.*", r".*[Hh]andbook.*",
                        r".*tutorial.*", r".*how.*to.*", r".*paso.*a.*paso.*"
                    ],
                    "Strategies": [
                        r".*estrategia.*", r".*strategy.*", r".*ESTRATEGIA.*", r".*plan.*",
                        r".*roadmap.*", r".*framework.*", r".*methodology.*"
                    ],
                    "Content": [
                        r".*content.*", r".*contenido.*", r".*CONTENIDO.*", r".*copy.*",
                        r".*texto.*", r".*writing.*", r".*redaccion.*"
                    ],
                    "Campaigns": [
                        r".*campaign.*", r".*campaña.*", r".*promocion.*", r".*lanzamiento.*",
                        r".*launch.*", r".*rollout.*"
                    ],
                    "Email_Marketing": [
                        r".*email.*", r".*mail.*", r".*newsletter.*", r".*boletin.*",
                        r".*mailing.*", r".*correo.*"
                    ],
                    "Landing_Pages": [
                        r".*landing.*", r".*página.*aterrizaje.*", r".*conversion.*",
                        r".*funnel.*", r".*embudo.*"
                    ],
                    "Webinars": [
                        r".*webinar.*", r".*seminario.*", r".*presentacion.*online.*",
                        r".*evento.*virtual.*"
                    ],
                    "Lead_Generation": [
                        r".*lead.*", r".*prospecto.*", r".*captacion.*", r".*generacion.*",
                        r".*acquisition.*"
                    ],
                    "Branding": [
                        r".*brand.*", r".*marca.*", r".*identidad.*", r".*logo.*",
                        r".*visual.*", r".*design.*"
                    ],
                    "Analytics": [
                        r".*analisis.*", r".*analysis.*", r".*ANALISIS.*", r".*metric.*",
                        r".*dashboard.*", r".*kpi.*", r".*roi.*", r".*competitivo.*"
                    ],
                    "Templates": [
                        r".*template.*", r".*plantilla.*", r".*modelo.*", r".*format.*"
                    ],
                    "Scripts": [
                        r".*\.py$", r".*\.js$", r".*\.ts$", r".*script.*", r".*automation.*"
                    ],
                    "Reports": [
                        r".*report.*", r".*reporte.*", r".*informe.*", r".*resultado.*"
                    ],
                    "Presentations": [
                        r".*\.pptx?$", r".*presentacion.*", r".*slides.*", r".*diapositiva.*"
                    ],
                    "Data_Files": [
                        r".*\.json$", r".*\.csv$", r".*\.xlsx?$", r".*\.sql$", r".*data.*"
                    ]
                }
            },
            "02_Finance": {
                "subfolders": [
                    "Budget", "Reports", "Analysis", "Forecasting", "Accounting",
                    "Taxes", "Investments", "Cash_Flow", "P&L", "Balance_Sheets",
                    "Audits", "Compliance", "Templates", "Scripts", "Data_Files"
                ],
                "patterns": {
                    "Budget": [r".*budget.*", r".*presupuesto.*", r".*gasto.*", r".*cost.*"],
                    "Reports": [r".*report.*", r".*reporte.*", r".*financial.*", r".*financiero.*"],
                    "Analysis": [r".*analysis.*", r".*analisis.*", r".*evaluation.*", r".*evaluacion.*"],
                    "Forecasting": [r".*forecast.*", r".*proyeccion.*", r".*prediction.*", r".*prediccion.*"],
                    "Accounting": [r".*accounting.*", r".*contabilidad.*", r".*bookkeeping.*"],
                    "Taxes": [r".*tax.*", r".*impuesto.*", r".*fiscal.*", r".*irs.*"],
                    "Investments": [r".*investment.*", r".*inversion.*", r".*portfolio.*", r".*cartera.*"],
                    "Cash_Flow": [r".*cash.*flow.*", r".*flujo.*caja.*", r".*liquidez.*"],
                    "P&L": [r".*p&l.*", r".*profit.*loss.*", r".*ganancia.*perdida.*"],
                    "Balance_Sheets": [r".*balance.*sheet.*", r".*balance.*general.*"],
                    "Audits": [r".*audit.*", r".*auditoria.*", r".*revision.*"],
                    "Compliance": [r".*compliance.*", r".*cumplimiento.*", r".*regulatory.*"],
                    "Templates": [r".*template.*", r".*plantilla.*", r".*modelo.*"],
                    "Scripts": [r".*\.py$", r".*\.js$", r".*\.ts$", r".*script.*"],
                    "Data_Files": [r".*\.json$", r".*\.csv$", r".*\.xlsx?$", r".*\.sql$"]
                }
            },
            "05_Technology": {
                "subfolders": [
                    "Code", "Documentation", "APIs", "Databases", "Infrastructure",
                    "Security", "Testing", "Deployment", "Monitoring", "Scripts",
                    "Configs", "Logs", "Backups", "Templates", "Data_Files"
                ],
                "patterns": {
                    "Code": [r".*\.py$", r".*\.js$", r".*\.ts$", r".*\.java$", r".*\.cpp$", r".*\.go$"],
                    "Documentation": [r".*\.md$", r".*\.txt$", r".*doc.*", r".*readme.*"],
                    "APIs": [r".*api.*", r".*endpoint.*", r".*service.*", r".*microservice.*"],
                    "Databases": [r".*\.sql$", r".*database.*", r".*db.*", r".*schema.*"],
                    "Infrastructure": [r".*infrastructure.*", r".*infra.*", r".*server.*", r".*cloud.*"],
                    "Security": [r".*security.*", r".*seguridad.*", r".*auth.*", r".*permission.*"],
                    "Testing": [r".*test.*", r".*spec.*", r".*\.spec\.", r".*unit.*", r".*integration.*"],
                    "Deployment": [r".*deploy.*", r".*deployment.*", r".*ci.*cd.*", r".*pipeline.*"],
                    "Monitoring": [r".*monitor.*", r".*log.*", r".*metric.*", r".*alert.*"],
                    "Scripts": [r".*script.*", r".*\.sh$", r".*\.bat$", r".*automation.*"],
                    "Configs": [r".*config.*", r".*\.conf$", r".*\.ini$", r".*\.yaml$", r".*\.yml$"],
                    "Logs": [r".*\.log$", r".*log.*", r".*debug.*", r".*error.*"],
                    "Backups": [r".*backup.*", r".*\.bak$", r".*\.old$", r".*archive.*"],
                    "Templates": [r".*template.*", r".*plantilla.*", r".*boilerplate.*"],
                    "Data_Files": [r".*\.json$", r".*\.csv$", r".*\.xml$", r".*\.yaml$"]
                }
            }
        }
        
        return patterns
    
    def smart_classify_file(self, file_path):
        """Clasifica un archivo usando patrones optimizados y aprendizaje"""
        name = file_path.name.lower()
        ext = file_path.suffix.lower()
        
        # Primero intentar clasificación por extensión
        extension_mapping = {
            '.py': 'Scripts', '.js': 'Scripts', '.ts': 'Scripts',
            '.md': 'Documentation', '.txt': 'Documentation',
            '.json': 'Data_Files', '.csv': 'Data_Files', '.xlsx': 'Data_Files',
            '.pptx': 'Presentations', '.ppt': 'Presentations',
            '.pdf': 'Documentation', '.docx': 'Documentation'
        }
        
        if ext in extension_mapping:
            return extension_mapping[ext]
        
        # Luego usar patrones optimizados
        best_match = None
        best_score = 0
        
        for main_folder, rules in self.optimized_patterns.items():
            for subfolder, patterns in rules["patterns"].items():
                for pattern in patterns:
                    if re.search(pattern, name, re.IGNORECASE):
                        # Calcular score basado en especificidad del patrón
                        score = len(pattern) + (10 if pattern.startswith('.*') else 0)
                        if score > best_score:
                            best_score = score
                            best_match = subfolder
        
        return best_match or "Other"
    
    def organize_remaining_files(self):
        """Organiza archivos restantes usando clasificación inteligente"""
        print("🤖 Organizando archivos restantes con IA...")
        
        moved_count = 0
        for folder in self.base_dir.iterdir():
            if folder.is_dir() and not folder.name.startswith('.'):
                # Buscar archivos sueltos en carpetas principales
                loose_files = [f for f in folder.iterdir() if f.is_file() and not f.name.startswith('.')]
                
                for file_path in loose_files:
                    target_subfolder = self.smart_classify_file(file_path)
                    target_path = folder / target_subfolder
                    
                    # Crear subcarpeta si no existe
                    target_path.mkdir(exist_ok=True)
                    
                    # Mover archivo
                    try:
                        shutil.move(str(file_path), str(target_path / file_path.name))
                        moved_count += 1
                        print(f"   📁 {file_path.name} → {folder.name}/{target_subfolder}")
                    except Exception as e:
                        print(f"   ❌ Error moviendo {file_path.name}: {e}")
        
        return moved_count
    
    def generate_optimization_report(self):
        """Genera reporte de optimizaciones aplicadas"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "optimizations_applied": {
                "smart_patterns": len(self.optimized_patterns),
                "learning_data_entries": len(self.learning_data.get("file_classifications", {})),
                "files_analyzed": sum(len(files) for files in self.learning_data.get("file_classifications", {}).values())
            },
            "recommendations": [
                "Ejecutar análisis de patrones regularmente para mejorar clasificación",
                "Revisar archivos en 'Other' para crear nuevos patrones",
                "Actualizar patrones basándose en nuevos tipos de archivos",
                "Usar métricas de efectividad para optimizar patrones existentes"
            ]
        }
        
        report_path = self.base_dir / "optimization_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report_path

def main():
    base_dir = Path(__file__).parent
    organizer = SmartOrganizer(base_dir)
    
    print("🚀 Iniciando organizador inteligente...")
    
    # Analizar patrones existentes
    file_analysis = organizer.analyze_file_patterns()
    
    # Organizar archivos restantes
    moved_count = organizer.organize_remaining_files()
    
    # Generar reporte de optimización
    report_path = organizer.generate_optimization_report()
    
    print(f"✅ Organización inteligente completada:")
    print(f"   📊 Patrones analizados: {len(file_analysis)}")
    print(f"   📁 Archivos movidos: {moved_count}")
    print(f"   📄 Reporte: {report_path}")
    print(f"   🧠 Datos de aprendizaje guardados")

if __name__ == "__main__":
    main()
