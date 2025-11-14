#!/usr/bin/env python3
"""
Script de Limpieza y Organización Profunda
Mejora adicional: limpieza de archivos, organización de TypeScript, scripts especializados
"""

import os
import shutil
from pathlib import Path
from collections import defaultdict

ROOT_DIR = Path(__file__).parent

# Archivos temporales y de backup a eliminar
TEMP_FILES = [
    '.bak', '.tmp', '.log', '.swp', '.swo', '.pyc', '.pyo', 
    '__pycache__', '.DS_Store', '.cache', 'node_modules'
]

# Archivos duplicados con timestamps (patrones comunes)
DUPLICATE_PATTERNS = [
    r'_\d{10,}',  # Timestamps Unix
    r'_17593\d+',  # Timestamp específico encontrado
    r'_cpython-\d+',  # Archivos Python compilados
    r'_\d+$'  # Números al final
]

# Mapeo de extensiones a carpetas específicas
EXTENSION_MAPPING = {
    '.ts': {
        'base_folder': '05_Technology',
        'subfolder': 'TypeScript_Scripts/',
        'patterns': {
            'Service': 'Services/',
            'API': 'API_Scripts/',
            'auth': 'Auth_Scripts/',
            'data': 'Data_Scripts/',
            'integration': 'Integration_Scripts/',
            'neural': 'Neural_Networks/',
            'machine': 'Machine_Learning/',
            'ai': 'AI_Scripts/'
        }
    },
    '.bat': {
        'base_folder': '05_Technology',
        'subfolder': 'Windows_Scripts/Batch/'
    },
    '.ps1': {
        'base_folder': '05_Technology',
        'subfolder': 'Windows_Scripts/PowerShell/'
    },
    '.sh': {
        'base_folder': '05_Technology',
        'subfolder': 'Unix_Scripts/'
    }
}

def clean_temp_files():
    """Elimina archivos temporales y de backup"""
    cleaned = []
    errors = []
    
    print("Limpiando archivos temporales y de backup...\n")
    
    for root, dirs, files in os.walk(ROOT_DIR):
        # Saltar directorios especiales
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__']]
        
        for file in files:
            filepath = Path(root) / file
            
            # Verificar si es archivo temporal
            should_delete = False
            reason = None
            
            # Archivos de backup
            if file.endswith('.bak') or file.endswith('.tmp'):
                should_delete = True
                reason = 'archivo de backup'
            
            # Archivos .pyc y .pyo
            elif file.endswith('.pyc') or file.endswith('.pyo'):
                should_delete = True
                reason = 'bytecode Python'
            
            # Archivos .DS_Store
            elif file == '.DS_Store':
                should_delete = True
                reason = 'archivo del sistema macOS'
            
            # Archivos con timestamps sospechosos
            elif any(pattern in file for pattern in ['_17593', '_cpython-']):
                should_delete = True
                reason = 'archivo duplicado con timestamp'
            
            if should_delete:
                try:
                    filepath.unlink()
                    cleaned.append((str(filepath.relative_to(ROOT_DIR)), reason))
                    if len(cleaned) <= 20:  # Mostrar primeros 20
                        print(f"  ✓ Eliminado: {filepath.name} ({reason})")
                except Exception as e:
                    errors.append((str(filepath.relative_to(ROOT_DIR)), str(e)))
    
    print(f"\nTotal eliminados: {len(cleaned)} archivos")
    if errors:
        print(f"Errores: {len(errors)}")
    
    return cleaned, errors

def organize_specialized_files():
    """Organiza archivos TypeScript, scripts de Windows, etc."""
    stats = defaultdict(int)
    moved_files = []
    
    print("\nOrganizando archivos especializados (TypeScript, scripts)...\n")
    
    # Buscar archivos TypeScript
    for root, dirs, files in os.walk(ROOT_DIR):
        # Saltar ciertos directorios
        if '.git' in root or 'node_modules' in root:
            continue
        
        for file in files:
            filepath = Path(root) / file
            
            # Organizar TypeScript
            if file.endswith('.ts'):
                dest_folder = None
                dest_subfolder = None
                
                # Buscar subcarpeta específica según patrones
                file_lower = file.lower()
                for pattern, subfolder in EXTENSION_MAPPING['.ts']['patterns'].items():
                    if pattern.lower() in file_lower:
                        dest_subfolder = subfolder
                        break
                
                # Si no hay patrón específico, usar carpeta general
                if not dest_subfolder:
                    dest_subfolder = 'TypeScript_Scripts/'
                
                base_folder = EXTENSION_MAPPING['.ts']['base_folder']
                dest_path = ROOT_DIR / base_folder / dest_subfolder
                dest_path.mkdir(parents=True, exist_ok=True)
                target = dest_path / file
                
                # Evitar mover si ya está en el destino correcto
                if filepath.parent == dest_path:
                    continue
                
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
                    moved_files.append((file, base_folder, dest_subfolder))
                    stats['TypeScript'] += 1
                    if stats['TypeScript'] <= 10:
                        print(f"  ✓ {file} → {base_folder}/{dest_subfolder}")
                except Exception as e:
                    print(f"  ✗ Error moviendo {file}: {e}")
            
            # Organizar scripts de Windows
            elif file.endswith('.bat'):
                base_folder = EXTENSION_MAPPING['.bat']['base_folder']
                dest_subfolder = EXTENSION_MAPPING['.bat']['subfolder']
                dest_path = ROOT_DIR / base_folder / dest_subfolder
                dest_path.mkdir(parents=True, exist_ok=True)
                target = dest_path / file
                
                if filepath.parent != dest_path and not target.exists():
                    try:
                        shutil.move(str(filepath), str(target))
                        moved_files.append((file, base_folder, dest_subfolder))
                        stats['Batch'] += 1
                        print(f"  ✓ {file} → {base_folder}/{dest_subfolder}")
                    except Exception as e:
                        print(f"  ✗ Error moviendo {file}: {e}")
            
            elif file.endswith('.ps1'):
                base_folder = EXTENSION_MAPPING['.ps1']['base_folder']
                dest_subfolder = EXTENSION_MAPPING['.ps1']['subfolder']
                dest_path = ROOT_DIR / base_folder / dest_subfolder
                dest_path.mkdir(parents=True, exist_ok=True)
                target = dest_path / file
                
                if filepath.parent != dest_path and not target.exists():
                    try:
                        shutil.move(str(filepath), str(target))
                        moved_files.append((file, base_folder, dest_subfolder))
                        stats['PowerShell'] += 1
                        print(f"  ✓ {file} → {base_folder}/{dest_subfolder}")
                    except Exception as e:
                        print(f"  ✗ Error moviendo {file}: {e}")
    
    if stats:
        print(f"\nResumen:")
        for file_type, count in stats.items():
            print(f"  {file_type}: {count} archivos")
    
    return moved_files, stats

def organize_duplicates():
    """Identifica y organiza archivos duplicados potenciales"""
    import re
    
    print("\nIdentificando archivos duplicados potenciales...\n")
    
    duplicates = defaultdict(list)
    
    # Buscar archivos con patrones de duplicados
    for root, dirs, files in os.walk(ROOT_DIR):
        if '.git' in root:
            continue
        
        for file in files:
            # Buscar patrones de timestamps o números
            for pattern in DUPLICATE_PATTERNS:
                if re.search(pattern, file):
                    base_name = re.sub(pattern, '', file)
                    duplicates[base_name].append((Path(root) / file, file))
                    break
    
    print(f"Grupos de archivos potencialmente duplicados encontrados: {len(duplicates)}")
    
    # Mostrar algunos ejemplos
    count = 0
    for base_name, files in list(duplicates.items())[:10]:
        if len(files) > 1:
            print(f"\n  {base_name}:")
            for filepath, filename in files:
                print(f"    - {filepath.relative_to(ROOT_DIR)}")
            count += 1
    
    if count > 0:
        print(f"\n  ... y {len(duplicates) - count} grupos más")
        print("\nNota: Revisar manualmente estos archivos para decidir qué mantener.")
    
    return duplicates

def create_readme_files():
    """Crea README.md en carpetas principales para facilitar navegación"""
    print("\nCreando archivos README en carpetas principales...\n")
    
    main_folders = [
        '01_Marketing', '02_Finance', '03_Human_Resources',
        '04_Business_Strategy', '05_Technology', '06_Documentation',
        '08_AI_Artificial_Intelligence', '09_Sales', '10_Customer_Service',
        '20_Project_Management'
    ]
    
    created = 0
    for folder in main_folders:
        folder_path = ROOT_DIR / folder
        if folder_path.exists() and folder_path.is_dir():
            readme_path = folder_path / 'README.md'
            if not readme_path.exists():
                readme_content = f"""# {folder}

Esta carpeta contiene archivos relacionados con {folder.replace('_', ' ')}.

## Estructura

{chr(10).join([f"- `{sub.name}/`" for sub in folder_path.iterdir() if sub.is_dir()][:20])}

## Notas

Este README fue generado automáticamente. Actualizar según sea necesario.
"""
                readme_path.write_text(readme_content, encoding='utf-8')
                created += 1
                print(f"  ✓ README creado en {folder}/")
    
    print(f"\nTotal READMEs creados: {created}")
    return created

def main():
    """Función principal"""
    print("="*80)
    print("LIMPIEZA Y ORGANIZACIÓN PROFUNDA")
    print("="*80 + "\n")
    
    # 1. Limpiar archivos temporales
    cleaned, errors = clean_temp_files()
    
    # 2. Organizar archivos especializados
    moved_files, stats = organize_specialized_files()
    
    # 3. Identificar duplicados
    duplicates = organize_duplicates()
    
    # 4. Crear READMEs
    readmes_created = create_readme_files()
    
    # Resumen final
    print("\n" + "="*80)
    print("RESUMEN DE LIMPIEZA Y ORGANIZACIÓN")
    print("="*80 + "\n")
    
    print(f"Archivos temporales eliminados: {len(cleaned)}")
    print(f"Archivos especializados organizados: {len(moved_files)}")
    print(f"Grupos de duplicados identificados: {len(duplicates)}")
    print(f"READMEs creados: {readmes_created}")
    
    print("\n" + "="*80)
    print("LIMPIEZA Y ORGANIZACIÓN COMPLETADA")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()

