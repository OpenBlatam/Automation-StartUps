#!/usr/bin/env python3
"""
Script EXTENDIDO para organizar TODAS las carpetas principales con subcarpetas lógicas
Incluye todas las carpetas numeradas y principales del proyecto
"""

import os
import shutil
from pathlib import Path
import re

# Configuración EXTENDIDA de subcarpetas por carpeta principal
ORGANIZATION_RULES = {
    "01_Marketing": {
        "subfolders": [
            "Guides", "Sequences", "Content", "Automations", "Analytics",
            "Affiliate_Programs", "Blog_Posts", "CTAs", "Checklists",
            "Templates", "Scripts", "Reports", "Presentations", "Data_Files",
            "Strategies", "Campaigns", "Copywriting", "SEO", "Social_Media"
        ],
        "patterns": {
            "Guides": [r".*[Gg]uide.*", r".*[Gg]uía.*", r".*[Mm]anual.*", r".*[Hh]andbook.*", r".*onboarding.*"],
            "Sequences": [r".*secuencia.*", r".*sequence.*", r".*campaign.*", r".*email.*sequence.*"],
            "Content": [r".*contenido.*", r".*content.*", r".*blog.*", r".*articulo.*", r".*article.*"],
            "Automations": [r".*automatizacion.*", r".*automation.*", r".*workflow.*", r".*zapier.*", r".*make.*"],
            "Analytics": [r".*analisis.*", r".*analytics.*", r".*metric.*", r".*dashboard.*", r".*kpi.*"],
            "Affiliate_Programs": [r".*affiliate.*", r".*afiliado.*", r".*partner.*"],
            "Blog_Posts": [r"blog_.*", r".*blog.*\.md", r".*article.*"],
            "CTAs": [r"cta.*", r".*call.*action.*", r".*cta.*"],
            "Checklists": [r".*checklist.*", r".*lista.*verificacion.*"],
            "Templates": [r".*template.*", r".*plantilla.*", r".*modelo.*"],
            "Scripts": [r".*\.py$", r".*\.js$", r".*\.ts$"],
            "Reports": [r".*report.*", r".*reporte.*"],
            "Presentations": [r".*\.pptx$", r".*\.ppt$", r".*presentacion.*"],
            "Data_Files": [r".*\.json$", r".*\.csv$", r".*\.xlsx$", r".*\.xls$"],
            "Strategies": [r".*estrategia.*", r".*strategy.*", r".*plan.*marketing.*"],
            "Campaigns": [r".*campaign.*", r".*campaña.*"],
            "Copywriting": [r".*copy.*", r".*copywriting.*", r".*sales.*copy.*"],
            "SEO": [r".*seo.*", r".*keyword.*", r".*traffic.*"],
            "Social_Media": [r".*social.*media.*", r".*facebook.*", r".*instagram.*", r".*linkedin.*", r".*tiktok.*"]
        }
    },
    "02_Finance": {
        "subfolders": [
            "Financial_Models", "Calculators", "Analysis", "Dashboards",
            "Strategies", "Reports", "Automations", "Guides", "Templates",
            "Data_Files", "Scripts", "Risk_Management", "Investment_Plans",
            "Budget_Planning", "Forecasting", "ROI_Analysis"
        ],
        "patterns": {
            "Financial_Models": [r".*financial.*model.*", r".*modelo.*financiero.*", r".*proyeccion.*", r".*projection.*"],
            "Calculators": [r".*calculadora.*", r".*calculator.*", r".*roi.*", r".*ltv.*", r".*cac.*"],
            "Analysis": [r".*analisis.*financiero.*", r".*financial.*analysis.*", r".*analisis.*", r".*analysis.*"],
            "Dashboards": [r".*dashboard.*", r".*tablero.*", r".*executive.*dashboard.*"],
            "Strategies": [r".*estrategia.*", r".*strategy.*"],
            "Reports": [r".*report.*", r".*reporte.*"],
            "Automations": [r".*automatizacion.*", r".*automation.*"],
            "Guides": [r".*guide.*", r".*guia.*"],
            "Templates": [r".*template.*", r".*plantilla.*"],
            "Data_Files": [r".*\.json$", r".*\.csv$", r".*\.xlsx$", r".*\.xls$"],
            "Scripts": [r".*\.py$", r".*\.js$", r".*\.ts$", r".*\.html$"],
            "Risk_Management": [r".*risk.*", r".*riesgo.*", r".*mitigation.*"],
            "Investment_Plans": [r".*inversion.*", r".*investment.*", r".*vc.*", r".*venture.*"],
            "Budget_Planning": [r".*presupuesto.*", r".*budget.*", r".*planning.*"],
            "Forecasting": [r".*forecast.*", r".*prediccion.*", r".*forecasting.*"],
            "ROI_Analysis": [r".*roi.*analysis.*", r".*retorno.*inversion.*"]
        }
    },
    "03_Human_Resources": {
        "subfolders": [
            "Guides", "Templates", "Policies", "Training", "Performance",
            "Recruitment", "Onboarding", "Compliance", "Employee_Resources"
        ],
        "patterns": {
            "Guides": [r".*guide.*", r".*guia.*"],
            "Templates": [r".*template.*", r".*plantilla.*"],
            "Policies": [r".*policy.*", r".*politica.*"],
            "Training": [r".*training.*", r".*capacitacion.*"],
            "Performance": [r".*performance.*", r".*rendimiento.*"],
            "Recruitment": [r".*recruitment.*", r".*reclutamiento.*", r".*hiring.*"],
            "Onboarding": [r".*onboarding.*", r".*induccion.*"],
            "Compliance": [r".*compliance.*", r".*cumplimiento.*"],
            "Employee_Resources": [r".*employee.*", r".*empleado.*", r".*handbook.*"]
        }
    },
    "04_Business_Strategy": {
        "subfolders": [
            "Strategic_Plans", "Market_Analysis", "Competitive_Analysis",
            "Business_Plans", "Frameworks", "Case_Studies", "Guides"
        ],
        "patterns": {
            "Strategic_Plans": [r".*strateg.*plan.*", r".*plan.*estrategico.*"],
            "Market_Analysis": [r".*market.*analysis.*", r".*analisis.*mercado.*"],
            "Competitive_Analysis": [r".*competitive.*", r".*competencia.*"],
            "Business_Plans": [r".*business.*plan.*", r".*plan.*negocio.*"],
            "Frameworks": [r".*framework.*", r".*marco.*"],
            "Case_Studies": [r".*case.*study.*", r".*caso.*estudio.*"],
            "Guides": [r".*guide.*", r".*guia.*"]
        }
    },
    "04_Operations": {
        "subfolders": [
            "Process_Optimization", "Workflow_Management", "Operational_Excellence",
            "Supply_Chain", "Quality_Management", "Guides", "Templates", "Scripts"
        ],
        "patterns": {
            "Process_Optimization": [r".*process.*optimization.*", r".*optimizacion.*proceso.*"],
            "Workflow_Management": [r".*workflow.*", r".*flujo.*trabajo.*"],
            "Operational_Excellence": [r".*operational.*excellence.*", r".*excelencia.*operacional.*"],
            "Supply_Chain": [r".*supply.*chain.*", r".*cadena.*suministro.*"],
            "Quality_Management": [r".*quality.*management.*", r".*gestion.*calidad.*"],
            "Guides": [r".*guide.*"],
            "Templates": [r".*template.*"],
            "Scripts": [r".*\.py$", r".*\.js$", r".*\.ts$"]
        }
    },
    "05_Technology": {
        "subfolders": [
            "Implementation_Guides", "API_Documentation", "Architecture",
            "Automation_Scripts", "Advanced_Features", "Integration_Guides",
            "Best_Practices", "Checklists", "Case_Studies", "Configuration_Files",
            "Test_Files", "Presentations", "Research_Papers", "Tech_Stack_Docs",
            "Deployment", "Security", "Performance"
        ],
        "patterns": {
            "Implementation_Guides": [r".*implementacion.*", r".*implementation.*guide.*", r".*setup.*", r".*install.*"],
            "API_Documentation": [r".*api.*", r".*documentation.*", r".*reference.*", r".*endpoint.*"],
            "Architecture": [r".*architect.*", r".*arquitectura.*", r".*system.*design.*", r".*diagram.*"],
            "Automation_Scripts": [r".*automation.*", r".*script.*", r".*\.py$", r".*\.js$", r".*\.sh$"],
            "Advanced_Features": [r".*advanced.*", r".*avanzado.*", r".*feature.*"],
            "Integration_Guides": [r".*integration.*", r".*integracion.*", r".*connect.*"],
            "Best_Practices": [r".*best.*practice.*", r".*mejores.*practicas.*"],
            "Checklists": [r".*checklist.*"],
            "Case_Studies": [r".*case.*study.*", r".*caso.*estudio.*"],
            "Configuration_Files": [r".*\.yaml$", r".*\.yml$", r".*\.json$", r".*config.*", r".*\.env.*"],
            "Test_Files": [r".*test.*", r".*prueba.*", r".*spec\.", r".*\.test\."],
            "Presentations": [r".*\.pptx$", r".*\.ppt$"],
            "Research_Papers": [r".*research.*", r".*investigacion.*", r".*paper.*"],
            "Tech_Stack_Docs": [r".*tech.*", r".*technology.*"],
            "Deployment": [r".*deploy.*", r".*deployment.*", r".*docker.*", r".*kubernetes.*"],
            "Security": [r".*security.*", r".*seguridad.*", r".*cyber.*"],
            "Performance": [r".*performance.*", r".*optimization.*", r".*optimizacion.*"]
        }
    },
    "06_Documentation": {
        "subfolders": [
            "User_Guides", "Master_Documents", "Playbooks", "Quick_Start_Guides",
            "Checklists", "Templates", "Financial_Projections", "Presentations",
            "Excel_Files", "Index_Files", "Best_Practices", "Troubleshooting",
            "Training_Materials", "Reference_Docs"
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
            "Training_Materials": [r".*training.*", r".*capacitacion.*"],
            "Reference_Docs": [r".*reference.*", r".*referencia.*"]
        }
    },
    "07_Risk_Management": {
        "subfolders": [
            "Risk_Assessment", "Mitigation_Strategies", "Compliance", "Reports",
            "Policies", "Tools", "Guides", "Templates"
        ],
        "patterns": {
            "Risk_Assessment": [r".*risk.*assessment.*", r".*evaluacion.*riesgo.*"],
            "Mitigation_Strategies": [r".*mitigation.*", r".*mitigacion.*"],
            "Compliance": [r".*compliance.*", r".*cumplimiento.*"],
            "Reports": [r".*report.*"],
            "Policies": [r".*policy.*", r".*politica.*"],
            "Tools": [r".*tool.*"],
            "Guides": [r".*guide.*"],
            "Templates": [r".*template.*"]
        }
    },
    "08_AI_Artificial_Intelligence": {
        "subfolders": [
            "AI_Models", "Machine_Learning", "Neural_Networks", "Research",
            "Implementation", "Frameworks", "Case_Studies", "Guides"
        ],
        "patterns": {
            "AI_Models": [r".*ai.*model.*", r".*modelo.*ia.*"],
            "Machine_Learning": [r".*machine.*learning.*", r".*ml.*", r".*aprendizaje.*"],
            "Neural_Networks": [r".*neural.*", r".*red.*neuronal.*"],
            "Research": [r".*research.*", r".*investigacion.*"],
            "Implementation": [r".*implement.*", r".*implementacion.*"],
            "Frameworks": [r".*framework.*", r".*marco.*"],
            "Case_Studies": [r".*case.*study.*", r".*caso.*estudio.*"],
            "Guides": [r".*guide.*", r".*guia.*"]
        }
    },
    "09_Sales": {
        "subfolders": [
            "Sales_Strategy", "Closing_Techniques", "CRM", "Lead_Generation",
            "Sales_Automation", "Sales_Analytics", "Templates", "Scripts",
            "Presentations", "Guides", "Reports"
        ],
        "patterns": {
            "Sales_Strategy": [r".*sales.*strategy.*", r".*estrategia.*ventas.*"],
            "Closing_Techniques": [r".*closing.*", r".*cierre.*", r".*close.*sales.*"],
            "CRM": [r".*crm.*", r".*customer.*relationship.*"],
            "Lead_Generation": [r".*lead.*generation.*", r".*leads.*", r".*prospect.*"],
            "Sales_Automation": [r".*sales.*automation.*", r".*automatizacion.*ventas.*"],
            "Sales_Analytics": [r".*sales.*analytics.*", r".*metric.*ventas.*"],
            "Templates": [r".*template.*", r".*plantilla.*"],
            "Scripts": [r".*\.py$", r".*\.js$", r".*\.ts$"],
            "Presentations": [r".*\.pptx$", r".*\.ppt$"],
            "Guides": [r".*guide.*", r".*guia.*"],
            "Reports": [r".*report.*", r".*reporte.*"]
        }
    },
    "10_Customer_Service": {
        "subfolders": [
            "Support_Guides", "Templates", "Scripts", "Analytics", "Training",
            "Best_Practices", "Tools", "Documentation"
        ],
        "patterns": {
            "Support_Guides": [r".*support.*", r".*soporte.*", r".*ayuda.*"],
            "Templates": [r".*template.*"],
            "Scripts": [r".*\.py$", r".*\.js$"],
            "Analytics": [r".*analytics.*", r".*metric.*"],
            "Training": [r".*training.*", r".*capacitacion.*"],
            "Best_Practices": [r".*best.*practice.*"],
            "Tools": [r".*tool.*", r".*herramienta.*"],
            "Documentation": [r".*doc.*", r".*documentacion.*"]
        }
    },
    "13_Legal_Compliance": {
        "subfolders": [
            "Legal_Documents", "Compliance_Docs", "Templates", "Policies",
            "Regulations", "Contracts", "Guides"
        ],
        "patterns": {
            "Legal_Documents": [r".*legal.*", r".*juridico.*"],
            "Compliance_Docs": [r".*compliance.*", r".*cumplimiento.*"],
            "Templates": [r".*template.*", r".*plantilla.*"],
            "Policies": [r".*policy.*", r".*politica.*"],
            "Regulations": [r".*regulation.*", r".*regulacion.*"],
            "Contracts": [r".*contract.*", r".*contrato.*"],
            "Guides": [r".*guide.*", r".*guia.*"]
        }
    },
    "16_Data_Analytics": {
        "subfolders": [
            "Analytics_Reports", "Dashboards", "Data_Models", "Tools",
            "Guides", "Scripts", "Templates"
        ],
        "patterns": {
            "Analytics_Reports": [r".*analytics.*report.*", r".*reporte.*analitico.*"],
            "Dashboards": [r".*dashboard.*", r".*tablero.*"],
            "Data_Models": [r".*data.*model.*", r".*modelo.*datos.*"],
            "Tools": [r".*tool.*"],
            "Guides": [r".*guide.*"],
            "Scripts": [r".*\.py$", r".*\.js$"],
            "Templates": [r".*template.*"]
        }
    },
    "20_Project_Management": {
        "subfolders": [
            "Project_Plans", "Methodologies", "Templates", "Tools",
            "Reports", "Guides", "Best_Practices"
        ],
        "patterns": {
            "Project_Plans": [r".*project.*plan.*", r".*plan.*proyecto.*"],
            "Methodologies": [r".*methodology.*", r".*metodologia.*"],
            "Templates": [r".*template.*"],
            "Tools": [r".*tool.*"],
            "Reports": [r".*report.*"],
            "Guides": [r".*guide.*"],
            "Best_Practices": [r".*best.*practice.*"]
        }
    }
}

def create_subfolders(base_path, subfolders):
    """Crea las subcarpetas necesarias"""
    for subfolder in subfolders:
        subfolder_path = base_path / subfolder
        subfolder_path.mkdir(exist_ok=True)

def match_file_to_subfolder(filename, patterns, folder_name):
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
        target = extensions[file_ext]
        if folder_name in ORGANIZATION_RULES and target in ORGANIZATION_RULES[folder_name]["subfolders"]:
            return target
    
    return None

def organize_folder(folder_name, base_dir, dry_run=False):
    """Organiza una carpeta principal"""
    folder_path = Path(base_dir) / folder_name
    
    if not folder_path.exists():
        if not dry_run:
            print(f"⚠️  La carpeta {folder_name} no existe")
        return 0, 0
    
    if folder_name not in ORGANIZATION_RULES:
        if not dry_run:
            print(f"  ⚠️  No hay reglas de organización para {folder_name}")
        return 0, 0
    
    rules = ORGANIZATION_RULES[folder_name]
    subfolders = rules["subfolders"]
    patterns = rules["patterns"]
    
    # Añadir carpeta "Other" para archivos sin match
    if "Other" not in subfolders:
        subfolders.append("Other")
    
    # Crear subcarpetas
    if not dry_run:
        create_subfolders(folder_path, subfolders)
    
    # Organizar archivos
    files_organized = 0
    files_skipped = 0
    
    for item in folder_path.iterdir():
        # Saltar si es carpeta o archivos ocultos/system
        if item.is_dir() or item.name.startswith('.') or item.name.startswith('__'):
            continue
        
        # Saltar si el archivo ya está en una subcarpeta
        parent_name = item.parent.name
        if parent_name in subfolders:
            continue
        
        target_subfolder = match_file_to_subfolder(item.name, patterns, folder_name)
        
        if target_subfolder:
            target_path = folder_path / target_subfolder / item.name
            if dry_run:
                files_organized += 1
            else:
                try:
                    if not target_path.exists():
                        shutil.move(str(item), str(target_path))
                        files_organized += 1
                    else:
                        files_skipped += 1
                except Exception as e:
                    files_skipped += 1
        else:
            # Si no hay match, mover a carpeta "Other"
            target_path = folder_path / "Other" / item.name
            if dry_run:
                files_organized += 1
            else:
                try:
                    if not target_path.exists():
                        shutil.move(str(item), str(target_path))
                        files_organized += 1
                    else:
                        files_skipped += 1
                except Exception as e:
                    files_skipped += 1
    
    if not dry_run:
        print(f"  ✅ {folder_name}: {files_organized} archivos organizados, {files_skipped} saltados")
    
    return files_organized, files_skipped

def main(dry_run=False):
    base_dir = Path(__file__).parent
    
    print("🚀 Iniciando organización EXTENDIDA de TODAS las carpetas...")
    if dry_run:
        print("🔍 MODO DRY RUN - No se moverán archivos\n")
    print("=" * 70)
    
    total_organized = 0
    total_skipped = 0
    
    # Organizar cada carpeta principal en orden
    folders_to_organize = sorted(ORGANIZATION_RULES.keys())
    
    for folder_name in folders_to_organize:
        print(f"\n📁 Organizando carpeta: {folder_name}")
        organized, skipped = organize_folder(folder_name, base_dir, dry_run)
        total_organized += organized
        total_skipped += skipped
    
    print("\n" + "=" * 70)
    print(f"✅ Organización EXTENDIDA completada!")
    print(f"   📊 Total organizados: {total_organized}")
    print(f"   ⏭️  Total saltados: {total_skipped}")
    print(f"   📁 Carpetas procesadas: {len(folders_to_organize)}")

if __name__ == "__main__":
    import sys
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    main(dry_run=dry_run)




