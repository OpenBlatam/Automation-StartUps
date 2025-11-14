#!/usr/bin/env python3
"""
Script MEJORADO para organizar carpetas principales con subcarpetas lógicas
Versión mejorada con más carpetas y mejores patrones
Para ejecutar: python3 organize_folders.py
Para dry-run: python3 organize_folders.py --dry-run
"""

import os
import shutil
from pathlib import Path
import re

# Configuración de subcarpetas por carpeta principal
ORGANIZATION_RULES = {
    "01_Marketing": {
        "subfolders": [
            "Guides",
            "Sequences",
            "Content",
            "Automations",
            "Analytics",
            "Affiliate_Programs",
            "Blog_Posts",
            "CTAs",
            "Checklists",
            "Templates",
            "Scripts",
            "Reports",
            "Presentations",
            "Data_Files"
        ],
        "patterns": {
            "Guides": [r".*[Gg]uide.*", r".*[Gg]uía.*", r".*[Mm]anual.*", r".*[Hh]andbook.*"],
            "Sequences": [r".*secuencia.*", r".*sequence.*", r".*campaign.*"],
            "Content": [r".*contenido.*", r".*content.*", r".*blog.*", r".*articulo.*"],
            "Automations": [r".*automatizacion.*", r".*automation.*", r".*workflow.*"],
            "Analytics": [r".*analisis.*", r".*analytics.*", r".*metric.*", r".*dashboard.*"],
            "Affiliate_Programs": [r".*affiliate.*", r".*afiliado.*", r".*partner.*"],
            "Blog_Posts": [r"blog_.*", r".*blog.*\.md"],
            "CTAs": [r"cta.*", r".*call.*action.*"],
            "Checklists": [r".*checklist.*", r".*lista.*verificacion.*"],
            "Templates": [r".*template.*", r".*plantilla.*", r".*modelo.*"],
            "Scripts": [r".*\.py$", r".*\.js$", r".*\.ts$"],
            "Reports": [r".*report.*", r".*reporte.*", r".*analisis.*"],
            "Presentations": [r".*\.pptx$", r".*\.ppt$", r".*presentacion.*"],
            "Data_Files": [r".*\.json$", r".*\.csv$", r".*\.xlsx$", r".*\.xls$"]
        }
    },
    "02_Finance": {
        "subfolders": [
            "Financial_Models",
            "Calculators",
            "Analysis",
            "Dashboards",
            "Strategies",
            "Reports",
            "Automations",
            "Guides",
            "Templates",
            "Data_Files",
            "Scripts",
            "Risk_Management",
            "Investment_Plans",
            "Budget_Planning"
        ],
        "patterns": {
            "Financial_Models": [r".*financial.*model.*", r".*modelo.*financiero.*", r".*proyeccion.*"],
            "Calculators": [r".*calculadora.*", r".*calculator.*", r".*roi.*"],
            "Analysis": [r".*analisis.*financiero.*", r".*financial.*analysis.*", r".*analisis.*"],
            "Dashboards": [r".*dashboard.*", r".*tablero.*"],
            "Strategies": [r".*estrategia.*", r".*strategy.*"],
            "Reports": [r".*report.*", r".*reporte.*"],
            "Automations": [r".*automatizacion.*", r".*automation.*"],
            "Guides": [r".*guide.*", r".*guia.*"],
            "Templates": [r".*template.*", r".*plantilla.*"],
            "Data_Files": [r".*\.json$", r".*\.csv$", r".*\.xlsx$", r".*\.xls$"],
            "Scripts": [r".*\.py$", r".*\.js$", r".*\.ts$", r".*\.html$"],
            "Risk_Management": [r".*risk.*", r".*riesgo.*"],
            "Investment_Plans": [r".*inversion.*", r".*investment.*"],
            "Budget_Planning": [r".*presupuesto.*", r".*budget.*"]
        }
    },
    "05_Technology": {
        "subfolders": [
            "Implementation_Guides",
            "API_Documentation",
            "Architecture",
            "Automation_Scripts",
            "Advanced_Features",
            "Integration_Guides",
            "Best_Practices",
            "Checklists",
            "Case_Studies",
            "Configuration_Files",
            "Test_Files",
            "Presentations",
            "Research_Papers",
            "Tech_Stack_Docs"
        ],
        "patterns": {
            "Implementation_Guides": [r".*implementacion.*", r".*implementation.*guide.*", r".*setup.*"],
            "API_Documentation": [r".*api.*", r".*documentation.*", r".*reference.*"],
            "Architecture": [r".*architect.*", r".*arquitectura.*", r".*system.*design.*"],
            "Automation_Scripts": [r".*automation.*", r".*script.*", r".*\.py$", r".*\.js$"],
            "Advanced_Features": [r".*advanced.*", r".*avanzado.*"],
            "Integration_Guides": [r".*integration.*", r".*integracion.*"],
            "Best_Practices": [r".*best.*practice.*", r".*mejores.*practicas.*"],
            "Checklists": [r".*checklist.*"],
            "Case_Studies": [r".*case.*study.*", r".*caso.*estudio.*"],
            "Configuration_Files": [r".*\.yaml$", r".*\.yml$", r".*\.json$", r".*config.*"],
            "Test_Files": [r".*test.*", r".*prueba.*"],
            "Presentations": [r".*\.pptx$", r".*\.ppt$"],
            "Research_Papers": [r".*research.*", r".*investigacion.*"],
            "Tech_Stack_Docs": [r".*tech.*", r".*technology.*"]
        }
    },
    "06_Documentation": {
        "subfolders": [
            "User_Guides",
            "Master_Documents",
            "Playbooks",
            "Quick_Start_Guides",
            "Checklists",
            "Templates",
            "Financial_Projections",
            "Presentations",
            "Excel_Files",
            "Index_Files",
            "Best_Practices",
            "Troubleshooting",
            "Training_Materials"
        ],
        "patterns": {
            "User_Guides": [r".*user.*guide.*", r".*guia.*usuario.*", r".*GUIA_USUARIO.*"],
            "Master_Documents": [r".*master.*", r".*maestro.*", r".*DOCUMENTACION_MAESTRA.*"],
            "Playbooks": [r".*playbook.*"],
            "Quick_Start_Guides": [r".*quick.*start.*", r".*inicio.*rapido.*"],
            "Checklists": [r".*checklist.*"],
            "Templates": [r".*template.*", r".*plantilla.*"],
            "Financial_Projections": [r".*financial.*projection.*", r".*proyeccion.*financiera.*"],
            "Presentations": [r".*\.pptx$", r".*\.ppt$", r".*presentation.*"],
            "Excel_Files": [r".*\.xlsx$", r".*\.xls$", r".*\.csv$"],
            "Index_Files": [r".*index.*", r".*indice.*"],
            "Best_Practices": [r".*best.*practice.*", r".*mejores.*practicas.*"],
            "Troubleshooting": [r".*troubleshoot.*", r".*soluci[oó]n.*problema.*"],
            "Training_Materials": [r".*training.*", r".*capacitacion.*"]
        }
    }
}

def create_subfolders(base_path, subfolders):
    """Crea las subcarpetas necesarias"""
    for subfolder in subfolders:
        subfolder_path = base_path / subfolder
        subfolder_path.mkdir(exist_ok=True)
        print(f"  ✓ Subcarpeta creada/verificada: {subfolder}")

def match_file_to_subfolder(filename, patterns):
    """Intenta hacer match del archivo con alguna subcarpeta"""
    filename_lower = filename.lower()
    
    # Primero intenta matches específicos
    for subfolder, pattern_list in patterns.items():
        for pattern in pattern_list:
            if re.search(pattern, filename_lower, re.IGNORECASE):
                return subfolder
    
    # Si no hay match pero tiene extensión conocida, clasificar por tipo
    extensions = {
        '.py': 'Scripts',
        '.js': 'Scripts',
        '.ts': 'Scripts',
        '.json': 'Data_Files',
        '.csv': 'Data_Files',
        '.xlsx': 'Data_Files',
        '.xls': 'Data_Files',
        '.html': 'Templates',
        '.pptx': 'Presentations',
        '.ppt': 'Presentations',
        '.docx': 'Templates',
        '.doc': 'Templates',
        '.pdf': 'Reports'
    }
    
    file_ext = Path(filename).suffix.lower()
    if file_ext in extensions:
        return extensions[file_ext]
    
    return None

def organize_folder(folder_name, base_dir):
    """Organiza una carpeta principal"""
    folder_path = Path(base_dir) / folder_name
    
    if not folder_path.exists():
        print(f"⚠️  La carpeta {folder_name} no existe")
        return
    
    print(f"\n📁 Organizando carpeta: {folder_name}")
    
    if folder_name not in ORGANIZATION_RULES:
        print(f"  ⚠️  No hay reglas de organización para {folder_name}")
        return
    
    rules = ORGANIZATION_RULES[folder_name]
    subfolders = rules["subfolders"]
    patterns = rules["patterns"]
    
    # Añadir carpeta "Other" para archivos sin match
    if "Other" not in subfolders:
        subfolders.append("Other")
    
    # Crear subcarpetas
    create_subfolders(folder_path, subfolders)
    
    # Organizar archivos
    files_organized = 0
    files_skipped = 0
    
    for item in folder_path.iterdir():
        # Saltar si es carpeta o archivos ocultos/system
        if item.is_dir() or item.name.startswith('.') or item.name.startswith('__'):
            continue
        
        # Saltar si el archivo ya está en una subcarpeta
        if any(item.name.startswith(sf) for sf in subfolders):
            continue
        
        target_subfolder = match_file_to_subfolder(item.name, patterns)
        
        if target_subfolder:
            target_path = folder_path / target_subfolder / item.name
            try:
                if not target_path.exists():
                    shutil.move(str(item), str(target_path))
                    print(f"  ✓ Movido: {item.name} → {target_subfolder}/")
                    files_organized += 1
                else:
                    print(f"  ⚠️  Ya existe: {target_subfolder}/{item.name}")
                    files_skipped += 1
            except Exception as e:
                print(f"  ✗ Error moviendo {item.name}: {e}")
        else:
            # Si no hay match, mover a carpeta "Other"
            target_path = folder_path / "Other" / item.name
            try:
                if not target_path.exists():
                    shutil.move(str(item), str(target_path))
                    print(f"  ⊗ Movido a Other: {item.name}")
                    files_organized += 1
                else:
                    print(f"  ⚠️  Ya existe en Other: {item.name}")
                    files_skipped += 1
            except Exception as e:
                print(f"  ✗ Error moviendo {item.name} a Other: {e}")
                files_skipped += 1
    
    print(f"\n  ✅ Completado: {files_organized} archivos organizados, {files_skipped} saltados")

def main():
    base_dir = Path(__file__).parent
    
    print("🚀 Iniciando organización de carpetas...")
    print("=" * 60)
    
    # Organizar cada carpeta principal
    for folder_name in ORGANIZATION_RULES.keys():
        organize_folder(folder_name, base_dir)
    
    print("\n" + "=" * 60)
    print("✅ Organización completada!")

if __name__ == "__main__":
    main()

