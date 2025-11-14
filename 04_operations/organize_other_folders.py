#!/usr/bin/env python3
"""
Script para organizar archivos en carpetas 'Other' y subdividir carpetas grandes
Mejora adicional de la organización del proyecto
"""

import os
import shutil
from pathlib import Path
from collections import defaultdict

ROOT_DIR = Path(__file__).parent

# Patrones mejorados para organizar carpetas 'Other'
OTHER_FOLDER_PATTERNS = {
    '01_Marketing/Other': {
        'CTAs/': ['ctas_', 'CTA', 'cta'],
        'Blog_Posts/': ['blog_', 'blog'],
        'Templates/': ['version_', 'template', 'plantilla'],
        'Guides/': ['guia_', 'guide', 'GUIA'],
        'Social_Media/': ['linkedin', 'instagram', 'social', 'viral'],
        'Email/': ['email', 'sequence', 'secuencia'],
        'Checklists/': ['checklist', 'CHECKLIST'],
        'SEO/': ['seo', 'SEO', 'keyword', 'meta'],
        'Lead_Generation/': ['lead', 'outreach', 'LEAD'],
        'Automation/': ['automation', 'automatizacion'],
        'DMs/': ['dm_', 'DM_', 'DMs_'],
        'Scripts/': ['.py', '.js', 'script'],
        'Data/': ['.csv', '.json', '.xlsx'],
        'Presentations/': ['.pptx', '.ppt', '.docx'],
        'Strategies/': ['estrategia', 'strategy', 'ESTRATEGIA'],
        'Content/': ['contenido', 'content', 'Content'],
        'Analytics/': ['analytics', 'dashboard', 'metric'],
        'Campaigns/': ['campaign', 'campana', 'calendario'],
        'Variations/': ['variantes', 'variaciones', 'Variantes']
    },
    
    '06_Documentation/Other': {
        'Guides/': ['guide', 'guia', 'manual', 'tutorial'],
        'Indexes/': ['index', 'indice', 'INDICE'],
        'Reports/': ['report', 'reporte', 'RESUMEN'],
        'Templates/': ['template', 'plantilla'],
        'Summaries/': ['summary', 'resumen', 'RESUMEN'],
        'Best_Practices/': ['best_practices', 'mejores_practicas', 'practices'],
        'Technical_Docs/': ['technical', 'tecnico', 'TECHNICAL'],
        'User_Docs/': ['user', 'usuario', 'USER'],
        'API_Docs/': ['api', 'API', 'reference'],
        'Playbooks/': ['playbook', 'PLAYBOOK'],
        'Checklists/': ['checklist', 'CHECKLIST'],
        'Presentations/': ['.pptx', '.ppt'],
        'Excel_Files/': ['.xlsx', '.csv'],
        'Scripts/': ['.py', '.js', 'script']
    },
    
    '04_Business_Strategy/Other': {
        'Plans/': ['plan', 'Plan', 'PLAN'],
        'Analysis/': ['analysis', 'analisis', 'ANALISIS'],
        'Strategies/': ['strategy', 'estrategia', 'Strategy'],
        'Reports/': ['report', 'reporte'],
        'Frameworks/': ['framework', 'Framework'],
        'Guides/': ['guide', 'guia'],
        'Templates/': ['template', 'plantilla'],
        'Models/': ['model', 'Model', 'modelo']
    },
    
    '05_Technology/Other': {
        'Code/': ['.py', '.js', '.ts', 'code'],
        'Documentation/': ['doc', 'documentation', 'DOC'],
        'Scripts/': ['script', 'SCRIPT', '.sh'],
        'Config/': ['config', 'Config', 'CONFIG'],
        'Architecture/': ['architect', 'architecture', 'ARCHITECTURE'],
        'APIs/': ['api', 'API'],
        'Tests/': ['test', 'Test', 'TEST'],
        'Deployment/': ['deploy', 'Deploy', 'DEPLOY'],
        'Automation/': ['automation', 'automatizacion']
    },
    
    '08_AI_Artificial_Intelligence/Other': {
        'AI_Systems/': ['ai_', 'AI_', 'system'],
        'Automation/': ['automation', 'automatizacion'],
        'Machine_Learning/': ['ml', 'ML', 'learning', 'neural'],
        'Guides/': ['guide', 'guia'],
        'Tools/': ['tool', 'Tool', 'TOOL'],
        'Frameworks/': ['framework', 'Framework'],
        'Research/': ['research', 'Research'],
        'Scripts/': ['.py', '.js', 'script']
    },
    
    '02_Finance/Other': {
        'ROI/': ['roi', 'ROI', 'calculadora'],
        'Models/': ['model', 'Model', 'modelo'],
        'Reports/': ['report', 'reporte'],
        'Analysis/': ['analysis', 'analisis'],
        'Dashboards/': ['dashboard', 'Dashboard'],
        'Templates/': ['template', 'plantilla'],
        'Scripts/': ['.py', '.js']
    }
}

# Carpetas grandes que necesitan subdivisión
LARGE_FOLDERS_TO_SUBDIVIDE = {
    '01_Webinar_Campaign': {
        'Webinar_Scripts/': ['script', 'Script'],
        'Webinar_Presentations/': ['.pptx', '.ppt'],
        'Webinar_Materials/': ['material', 'Material'],
        'Webinar_Guides/': ['guide', 'Guide', 'guia'],
        'Webinar_Checklists/': ['checklist', 'CHECKLIST'],
        'Webinar_Other/': []
    },
    '06_Strategy': {
        'Strategic_Plans/': ['plan', 'Plan', 'PLAN'],
        'Business_Strategies/': ['strategy', 'Strategy', 'estrategia'],
        'Market_Analysis/': ['market', 'Market', 'analisis'],
        'Competitive_Intelligence/': ['competitive', 'Competitive'],
        'Implementation_Guides/': ['implement', 'guide', 'guia'],
        'Strategy_Other/': []
    }
}

def ensure_subfolder_exists(base_folder, subfolder):
    """Asegura que una subcarpeta existe"""
    if base_folder.startswith('./'):
        base_folder = base_folder[2:]
    subfolder_path = ROOT_DIR / base_folder / subfolder
    subfolder_path.mkdir(parents=True, exist_ok=True)
    return subfolder_path

def find_matching_subfolder(filename, base_folder_path):
    """Encuentra la subcarpeta apropiada para un archivo"""
    filename_lower = filename.lower()
    
    # Convertir ruta relativa a clave de diccionario
    base_folder = str(base_folder_path.relative_to(ROOT_DIR))
    
    if base_folder not in OTHER_FOLDER_PATTERNS:
        return None
    
    # Buscar coincidencias
    for subfolder, patterns in OTHER_FOLDER_PATTERNS[base_folder].items():
        for pattern in patterns:
            pattern_lower = pattern.lower()
            if (pattern_lower in filename_lower or 
                filename_lower.startswith(pattern_lower.replace('_', '')) or
                filename_lower.endswith(pattern_lower.replace('_', '')) or
                filename.endswith(pattern)):  # Para extensiones
                return subfolder
    
    return None

def organize_other_folders():
    """Organiza archivos en carpetas 'Other'"""
    stats = defaultdict(lambda: defaultdict(int))
    moved_files = []
    
    print("Organizando carpetas 'Other'...\n")
    
    for base_folder_key, patterns in OTHER_FOLDER_PATTERNS.items():
        base_folder_path = ROOT_DIR / base_folder_key.replace('/', os.sep)
        
        if not base_folder_path.exists():
            continue
        
        print(f"Procesando {base_folder_key}...")
        
        # Obtener archivos en la carpeta Other
        files_in_folder = []
        for item in base_folder_path.iterdir():
            if item.is_file() and not item.name.startswith('.'):
                files_in_folder.append(item)
        
        if not files_in_folder:
            print(f"  (vacía)")
            continue
        
        organized = 0
        for filepath in files_in_folder:
            filename = filepath.name
            subfolder = find_matching_subfolder(filename, base_folder_path)
            
            if subfolder:
                dest_path = ensure_subfolder_exists(base_folder_key.replace('/', os.sep), subfolder)
                target = dest_path / filename
                
                # Evitar sobrescribir
                if target.exists():
                    counter = 1
                    name_parts = filepath.stem, filepath.suffix
                    while target.exists():
                        new_name = f"{name_parts[0]}_{counter}{name_parts[1]}"
                        target = dest_path / new_name
                        counter += 1
                
                try:
                    shutil.move(str(filepath), str(target))
                    moved_files.append((filename, base_folder_key, subfolder))
                    stats[base_folder_key][subfolder] += 1
                    organized += 1
                    if organized <= 10:  # Mostrar primeros 10
                        print(f"  ✓ {filename} → {subfolder}")
                except Exception as e:
                    print(f"  ✗ Error moviendo {filename}: {e}")
        
        if organized > 0:
            print(f"  Total organizados: {organized} archivos\n")
    
    return moved_files, stats

def subdivide_large_folders():
    """Subdivide carpetas grandes en subcarpetas más específicas"""
    stats = defaultdict(lambda: defaultdict(int))
    moved_files = []
    
    print("\nSubdividiendo carpetas grandes...\n")
    
    for base_folder, subfolders in LARGE_FOLDERS_TO_SUBDIVIDE.items():
        base_folder_path = ROOT_DIR / base_folder
        
        if not base_folder_path.exists():
            continue
        
        print(f"Procesando {base_folder}...")
        
        # Obtener archivos directamente en la carpeta (no en subcarpetas)
        files_in_folder = []
        for item in base_folder_path.iterdir():
            if item.is_file() and not item.name.startswith('.'):
                files_in_folder.append(item)
        
        if not files_in_folder:
            print(f"  (sin archivos directos)")
            continue
        
        organized = 0
        for filepath in files_in_folder:
            filename = filepath.name
            filename_lower = filename.lower()
            subfolder = None
            
            # Buscar subcarpeta apropiada
            for subfolder_name, patterns in subfolders.items():
                if subfolder == None:  # Solo si aún no se asignó
                    for pattern in patterns:
                        pattern_lower = pattern.lower()
                        if (pattern_lower in filename_lower or 
                            filename.endswith(pattern)):  # Para extensiones
                            subfolder = subfolder_name
                            break
                    if subfolder:
                        break
            
            # Si no coincide, usar carpeta "Other"
            if not subfolder:
                subfolder = [k for k in subfolders.keys() if 'Other' in k][0] if any('Other' in k for k in subfolders.keys()) else 'Other'
            
            dest_path = ensure_subfolder_exists(base_folder, subfolder)
            target = dest_path / filename
            
            if target.exists():
                counter = 1
                name_parts = filepath.stem, filepath.suffix
                while target.exists():
                    new_name = f"{name_parts[0]}_{counter}{name_parts[1]}"
                    target = dest_path / new_name
                    counter += 1
            
            try:
                shutil.move(str(filepath), str(target))
                moved_files.append((filename, base_folder, subfolder))
                stats[base_folder][subfolder] += 1
                organized += 1
            except Exception as e:
                print(f"  ✗ Error moviendo {filename}: {e}")
        
        if organized > 0:
            print(f"  Total organizados: {organized} archivos\n")
    
    return moved_files, stats

def main():
    """Función principal"""
    print("="*80)
    print("ORGANIZACIÓN ADICIONAL: Carpetas 'Other' y Subdivisión")
    print("="*80 + "\n")
    
    # Organizar carpetas Other
    other_moved, other_stats = organize_other_folders()
    
    # Subdividir carpetas grandes
    large_moved, large_stats = subdivide_large_folders()
    
    # Mostrar resumen
    print("\n" + "="*80)
    print("RESUMEN DE ORGANIZACIÓN ADICIONAL")
    print("="*80 + "\n")
    
    total_moved = len(other_moved) + len(large_moved)
    print(f"Total de archivos reorganizados: {total_moved}\n")
    
    if other_stats:
        print("Carpetas 'Other' organizadas:")
        for folder in sorted(other_stats.keys()):
            print(f"\n  {folder}:")
            for subfolder in sorted(other_stats[folder].keys()):
                print(f"    {subfolder}: {other_stats[folder][subfolder]} archivos")
            total = sum(other_stats[folder].values())
            print(f"    Total: {total} archivos")
    
    if large_stats:
        print("\nCarpetas grandes subdivididas:")
        for folder in sorted(large_stats.keys()):
            print(f"\n  {folder}:")
            for subfolder in sorted(large_stats[folder].keys()):
                print(f"    {subfolder}: {large_stats[folder][subfolder]} archivos")
            total = sum(large_stats[folder].values())
            print(f"    Total: {total} archivos")
    
    print("\n" + "="*80)
    print("ORGANIZACIÓN ADICIONAL COMPLETADA")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()




