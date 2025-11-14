#!/usr/bin/env python3
"""
Script para generar índices de archivos organizados por carpeta
"""
import os
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent.parent

def get_files_in_folder(folder_path):
    """Obtiene lista de archivos en una carpeta"""
    files = []
    folders = []
    
    try:
        for item in folder_path.iterdir():
            if item.is_file() and not item.name.startswith('.'):
                size = item.stat().st_size
                files.append({
                    'name': item.name,
                    'size': size,
                    'size_formatted': format_size(size)
                })
            elif item.is_dir() and not item.name.startswith('.'):
                folders.append(item.name)
    except PermissionError:
        pass
    
    return sorted(files, key=lambda x: x['name']), sorted(folders)

def format_size(size_bytes):
    """Formatea el tamaño en bytes"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def generate_folder_index(folder_path, relative_path=""):
    """Genera un índice para una carpeta"""
    files, subfolders = get_files_in_folder(folder_path)
    
    if not files and not subfolders:
        return None
    
    index_content = f"""---
title: "Índice - {relative_path or folder_path.name}"
category: "index"
created: "{datetime.now().strftime('%Y-%m-%d')}"
path: "{relative_path or folder_path.name}/INDEX.md"
---

# 📁 Índice: {relative_path or folder_path.name}

**Generado**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
    
    if files:
        total_size = sum(f['size'] for f in files)
        index_content += f"## 📄 Archivos ({len(files)} archivos, {format_size(total_size)})\n\n"
        
        for file_info in files:
            index_content += f"- [{file_info['name']}](./{file_info['name']}) ({file_info['size_formatted']})\n"
        
        index_content += "\n"
    
    if subfolders:
        index_content += f"## 📂 Subcarpetas ({len(subfolders)} carpetas)\n\n"
        
        for subfolder in subfolders:
            index_content += f"- [{subfolder}/](./{subfolder}/)\n"
        
        index_content += "\n"
    
    return index_content

def generate_all_indices():
    """Genera índices para todas las carpetas principales"""
    main_folders = [
        '01_marketing',
        '02_finance',
        '03_human_resources',
        '04_business_strategy',
        '04_operations',
        '05_technology',
        '06_documentation',
        '06_strategy',
        '07_advanced_features',
        '07_risk_management',
        '08_ai_artificial_intelligence',
        '09_sales',
        '10_customer_service',
        '11_research_development',
        '11_system_architecture',
        '12_quality_assurance',
        '12_user_guides',
        '13_legal_compliance',
        '14_product_management',
        '15_customer_experience',
        '16_data_analytics',
        '17_innovation',
    ]
    
    indices_created = 0
    
    for folder_name in main_folders:
        folder_path = BASE_DIR / folder_name
        if folder_path.exists() and folder_path.is_dir():
            index_content = generate_folder_index(folder_path, folder_name)
            if index_content:
                index_file = folder_path / 'INDEX.md'
                with open(index_file, 'w', encoding='utf-8') as f:
                    f.write(index_content)
                indices_created += 1
                print(f"✓ Índice creado: {folder_name}/INDEX.md")
    
    print(f"\n📊 Total de índices creados: {indices_created}")

if __name__ == '__main__':
    print("📝 Generando índices de carpetas...")
    generate_all_indices()









