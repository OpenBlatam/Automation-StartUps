#!/usr/bin/env python3
"""
Script ULTIMATE para organizar TODAS las carpetas del proyecto
Incluye carpetas numeradas Y carpetas temáticas
"""

import os
import shutil
from pathlib import Path
import re

# REGLAS PARA CARPETAS NUMERADAS (del script anterior)
NUMERADAS_RULES = {
    "01_Marketing": {
        "subfolders": ["Guides", "Sequences", "Content", "Automations", "Analytics",
            "Affiliate_Programs", "Blog_Posts", "CTAs", "Checklists", "Templates",
            "Scripts", "Reports", "Presentations", "Data_Files", "Strategies",
            "Campaigns", "Copywriting", "SEO", "Social_Media"],
        "patterns": {
            "Guides": [r".*[Gg]uide.*", r".*[Gg]uía.*", r".*[Mm]anual.*", r".*[Hh]andbook.*"],
            "Strategies": [r".*estrategia.*", r".*strategy.*", r".*ESTRATEGIA.*"],
            "Content": [r".*content.*", r".*contenido.*", r".*CONTENIDO.*", r".*copy.*"],
            "Analytics": [r".*analisis.*", r".*analysis.*", r".*ANALISIS.*", r".*competitivo.*"],
            "Templates": [r".*template.*", r".*plantilla.*", r".*modelo.*"],
            "Scripts": [r".*\.py$", r".*\.js$", r".*\.ts$"],
            "Reports": [r".*report.*", r".*reporte.*"],
            "Presentations": [r".*\.pptx$", r".*\.ppt$"],
            "Data_Files": [r".*\.json$", r".*\.csv$", r".*\.xlsx$"]
        }
    },
    "04_Business_Strategy": {
        "subfolders": ["Strategic_Plans", "Market_Analysis", "Competitive_Analysis",
            "Business_Plans", "Frameworks", "Case_Studies", "Guides"],
        "patterns": {
            "Strategic_Plans": [r".*strateg.*plan.*"],
            "Market_Analysis": [r".*market.*analysis.*"],
            "Business_Plans": [r".*business.*plan.*"],
            "Templates": [r".*template.*"],
            "Guides": [r".*guide.*"]
        }
    },
    "05_Technology": {
        "subfolders": ["Implementation_Guides", "API_Documentation", "Architecture",
            "Automation_Scripts", "Advanced_Features", "Configuration_Files",
            "Test_Files", "Presentations", "Security", "Performance"],
        "patterns": {
            "API_Documentation": [r".*api.*", r".*documentation.*"],
            "Architecture": [r".*architect.*"],
            "Configuration_Files": [r".*\.yaml$", r".*\.yml$", r".*config.*"],
            "Scripts": [r".*\.py$", r".*\.js$", r".*\.ts$"],
            "Presentations": [r".*\.pptx$", r".*\.ppt$"]
        }
    },
    "06_Documentation": {
        "subfolders": ["User_Guides", "Master_Documents", "Playbooks",
            "Quick_Start_Guides", "Checklists", "Templates", "Presentations"],
        "patterns": {
            "Master_Documents": [r".*master.*"],
            "Playbooks": [r".*playbook.*"],
            "Templates": [r".*template.*"],
            "Presentations": [r".*\.pptx$", r".*\.ppt$"]
        }
    },
    "08_AI_Artificial_Intelligence": {
        "subfolders": ["AI_Models", "Machine_Learning", "Neural_Networks",
            "Research", "Implementation", "Frameworks", "Case_Studies", "Guides"],
        "patterns": {
            "AI_Models": [r".*ai.*model.*"],
            "Machine_Learning": [r".*machine.*learning.*"],
            "Research": [r".*research.*"],
            "Guides": [r".*guide.*"]
        }
    }
}

# REGLAS PARA CARPETAS TEMÁTICAS
TEMATICAS_RULES = {
    "ai_technology": {
        "subfolders": ["AI_Models", "Machine_Learning", "Neural_Networks",
            "Implementation", "Documentation", "Scripts", "Templates", "Guides"],
        "patterns": {
            "AI_Models": [r".*ai.*model.*", r".*model.*"],
            "Machine_Learning": [r".*ml.*", r".*machine.*learning.*"],
            "Scripts": [r".*\.py$", r".*\.js$", r".*\.ts$"],
            "Documentation": [r".*doc.*", r".*readme.*"],
            "Templates": [r".*template.*"]
        }
    },
    "VC_Venture_Capital": {
        "subfolders": ["Financial_Models", "Analysis_Tools", "Investor_Presentations",
            "Negotiation", "Legal_Templates", "Case_Studies", "Anti_VC_Strategies"],
        "patterns": {
            "Financial_Models": [r".*financial.*", r".*model.*", r".*valuation.*"],
            "Analysis_Tools": [r".*analysis.*", r".*tool.*", r".*calculator.*"],
            "Investor_Presentations": [r".*presentation.*", r".*\.pptx$", r".*pitch.*"],
            "Negotiation": [r".*negotiation.*", r".*closing.*"],
            "Legal_Templates": [r".*legal.*", r".*compliance.*"]
        }
    },
    "marketing": {
        "subfolders": ["Content", "Campaigns", "Templates", "Scripts", "Analytics",
            "Guides", "Tools"],
        "patterns": {
            "Content": [r".*content.*"],
            "Campaigns": [r".*campaign.*"],
            "Scripts": [r".*\.py$", r".*\.js$"],
            "Templates": [r".*template.*"],
            "Analytics": [r".*analytics.*", r".*metric.*"]
        }
    }
}

def create_subfolders(base_path, subfolders):
    """Crea las subcarpetas necesarias"""
    for subfolder in subfolders:
        subfolder_path = base_path / subfolder
        subfolder_path.mkdir(exist_ok=True)

def match_file_to_subfolder(filename, patterns, folder_name, all_subfolders):
    """Intenta hacer match del archivo con alguna subcarpeta"""
    filename_lower = filename.lower()
    
    # Primero intenta matches específicos
    for subfolder, pattern_list in patterns.items():
        for pattern in pattern_list:
            if re.search(pattern, filename_lower, re.IGNORECASE):
                return subfolder
    
    # Si no hay match, clasificar por extensión
    extensions = {
        '.py': 'Scripts', '.js': 'Scripts', '.ts': 'Scripts',
        '.json': 'Data_Files', '.csv': 'Data_Files',
        '.xlsx': 'Data_Files', '.xls': 'Data_Files',
        '.html': 'Templates', '.pptx': 'Presentations',
        '.ppt': 'Presentations', '.docx': 'Templates',
        '.doc': 'Templates', '.pdf': 'Reports', '.md': 'Documentation'
    }
    
    file_ext = Path(filename).suffix.lower()
    if file_ext in extensions:
        target = extensions[file_ext]
        if target in all_subfolders:
            return target
    
    return None

def organize_folder(folder_name, base_dir, rules_dict, dry_run=False):
    """Organiza una carpeta"""
    folder_path = Path(base_dir) / folder_name
    
    if not folder_path.exists():
        return 0, 0
    
    if folder_name not in rules_dict:
        return 0, 0
    
    rules = rules_dict[folder_name]
    subfolders = rules["subfolders"].copy()
    patterns = rules["patterns"]
    
    # Añadir carpeta "Other"
    if "Other" not in subfolders:
        subfolders.append("Other")
    
    if not dry_run:
        create_subfolders(folder_path, subfolders)
    
    files_organized = 0
    files_skipped = 0
    
    for item in folder_path.iterdir():
        if item.is_dir() or item.name.startswith('.') or item.name.startswith('__'):
            continue
        
        parent_name = item.parent.name
        if parent_name in subfolders:
            continue
        
        target_subfolder = match_file_to_subfolder(item.name, patterns, folder_name, subfolders)
        
        if target_subfolder:
            target_path = folder_path / target_subfolder / item.name
            if not dry_run:
                try:
                    if not target_path.exists():
                        shutil.move(str(item), str(target_path))
                        files_organized += 1
                    else:
                        files_skipped += 1
                except Exception as e:
                    files_skipped += 1
        else:
            target_path = folder_path / "Other" / item.name
            if not dry_run:
                try:
                    if not target_path.exists():
                        shutil.move(str(item), str(target_path))
                        files_organized += 1
                    else:
                        files_skipped += 1
                except Exception as e:
                    files_skipped += 1
    
    if not dry_run and files_organized > 0:
        print(f"  ✅ {folder_name}: {files_organized} archivos organizados, {files_skipped} saltados")
    
    return files_organized, files_skipped

def main(dry_run=False):
    base_dir = Path(__file__).parent
    
    print("🚀 Iniciando organización ULTIMATE...")
    if dry_run:
        print("🔍 MODO DRY RUN\n")
    print("=" * 70)
    
    total_organized = 0
    total_skipped = 0
    
    # Organizar carpetas numeradas con archivos sueltos
    print("\n📁 Organizando carpetas numeradas (archivos sueltos)...")
    for folder_name in NUMERADAS_RULES.keys():
        organized, skipped = organize_folder(folder_name, base_dir, NUMERADAS_RULES, dry_run)
        total_organized += organized
        total_skipped += skipped
    
    # Organizar carpetas temáticas
    print("\n📁 Organizando carpetas temáticas...")
    for folder_name in TEMATICAS_RULES.keys():
        organized, skipped = organize_folder(folder_name, base_dir, TEMATICAS_RULES, dry_run)
        total_organized += organized
        total_skipped += skipped
    
    print("\n" + "=" * 70)
    print(f"✅ Organización ULTIMATE completada!")
    print(f"   📊 Total organizados: {total_organized}")
    print(f"   ⏭️  Total saltados: {total_skipped}")

if __name__ == "__main__":
    import sys
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    main(dry_run=dry_run)

