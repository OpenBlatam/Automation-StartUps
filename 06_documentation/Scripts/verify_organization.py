#!/usr/bin/env python3
"""
Script para verificar la organización de archivos y generar estadísticas detalladas
"""
import os
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent.parent

def get_file_stats():
    """Obtiene estadísticas detalladas de todos los archivos"""
    stats = {
        'total_files': 0,
        'total_size': 0,
        'by_extension': defaultdict(int),
        'by_folder': defaultdict(int),
        'by_category': defaultdict(int),
        'largest_files': [],
        'folders_with_most_files': [],
        'recent_files': []
    }
    
    # Mapeo de carpetas a categorías
    category_map = {
        '01_marketing': 'Marketing',
        '02_finance': 'Finance',
        '03_human_resources': 'HR',
        '04_business_strategy': 'Business Strategy',
        '04_operations': 'Operations',
        '05_technology': 'Technology',
        '06_documentation': 'Documentation',
        '06_strategy': 'Strategy',
        '07_advanced_features': 'Advanced Features',
        '07_risk_management': 'Risk Management',
        '08_ai_artificial_intelligence': 'AI',
        '08_research_development': 'R&D',
        '09_sales': 'Sales',
        '10_customer_service': 'Customer Service',
        '11_research_development': 'R&D',
        '11_system_architecture': 'System Architecture',
        '12_quality_assurance': 'QA',
        '12_user_guides': 'User Guides',
        '13_legal_compliance': 'Legal/Compliance',
        '14_procurement': 'Procurement',
        '14_product_management': 'Product Management',
        '14_thought_leadership': 'Thought Leadership',
        '15_customer_experience': 'Customer Experience',
        '16_data_analytics': 'Analytics',
        '17_innovation': 'Innovation',
        '18_sustainability': 'Sustainability',
        '19_international_business': 'International Business',
        '20_project_management': 'Project Management',
        '21_supply_chain': 'Supply Chain',
        '22_real_estate': 'Real Estate',
        '23_healthcare': 'Healthcare',
        '24_education': 'Education',
        '25_government': 'Government',
        '26_non_profit': 'Non-Profit',
        '27_entertainment': 'Entertainment',
        '28_sports': 'Sports',
        '29_media': 'Media',
        '30_consulting': 'Consulting',
        '31_professional_services': 'Professional Services',
        '32_manufacturing': 'Manufacturing',
        '33_retail': 'Retail',
        '34_e_commerce': 'E-Commerce',
    }
    
    for root, dirs, files in os.walk(BASE_DIR):
        # Saltar carpetas ocultas y especiales
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
        
        root_path = Path(root)
        rel_path = root_path.relative_to(BASE_DIR)
        
        for file in files:
            if file.startswith('.'):
                continue
                
            file_path = root_path / file
            try:
                size = file_path.stat().st_size
                ext = file_path.suffix.lower() or '(sin extensión)'
                
                stats['total_files'] += 1
                stats['total_size'] += size
                stats['by_extension'][ext] += 1
                stats['by_folder'][str(rel_path)] += 1
                
                # Categoría
                folder_parts = str(rel_path).split('/')
                if folder_parts and folder_parts[0] in category_map:
                    category = category_map[folder_parts[0]]
                    stats['by_category'][category] += 1
                
                # Archivos más grandes
                stats['largest_files'].append((str(rel_path / file), size))
                
                # Archivos recientes
                mtime = file_path.stat().st_mtime
                stats['recent_files'].append((str(rel_path / file), mtime))
                
            except (OSError, PermissionError):
                continue
    
    # Ordenar y limitar
    stats['largest_files'] = sorted(stats['largest_files'], key=lambda x: x[1], reverse=True)[:20]
    stats['recent_files'] = sorted(stats['recent_files'], key=lambda x: x[1], reverse=True)[:20]
    stats['folders_with_most_files'] = sorted(stats['by_folder'].items(), key=lambda x: x[1], reverse=True)[:20]
    
    return stats

def format_size(size_bytes):
    """Formatea el tamaño en bytes a formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def generate_report():
    """Genera un reporte completo de organización"""
    print("🔍 Analizando estructura de archivos...")
    stats = get_file_stats()
    
    print("\n" + "="*80)
    print("📊 REPORTE DE ORGANIZACIÓN DEL PROYECTO")
    print("="*80)
    
    print(f"\n📁 ESTADÍSTICAS GENERALES")
    print(f"  Total de archivos: {stats['total_files']:,}")
    print(f"  Tamaño total: {format_size(stats['total_size'])}")
    print(f"  Carpetas únicas: {len(stats['by_folder'])}")
    
    print(f"\n📂 ARCHIVOS POR EXTENSIÓN (Top 15)")
    for ext, count in sorted(stats['by_extension'].items(), key=lambda x: x[1], reverse=True)[:15]:
        percentage = (count / stats['total_files']) * 100
        print(f"  {ext:20s}: {count:6,} archivos ({percentage:5.1f}%)")
    
    print(f"\n📊 ARCHIVOS POR CATEGORÍA")
    for category, count in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / stats['total_files']) * 100
        print(f"  {category:30s}: {count:6,} archivos ({percentage:5.1f}%)")
    
    print(f"\n📁 CARPETAS CON MÁS ARCHIVOS (Top 20)")
    for folder, count in stats['folders_with_most_files']:
        print(f"  {folder:60s}: {count:6,} archivos")
    
    print(f"\n💾 ARCHIVOS MÁS GRANDES (Top 20)")
    for file_path, size in stats['largest_files']:
        print(f"  {format_size(size):10s} - {file_path}")
    
    print(f"\n🕒 ARCHIVOS MÁS RECIENTES (Top 20)")
    for file_path, mtime in stats['recent_files']:
        date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
        print(f"  {date_str} - {file_path}")
    
    # Guardar reporte JSON
    report = {
        'timestamp': datetime.now().isoformat(),
        'stats': {
            'total_files': stats['total_files'],
            'total_size': stats['total_size'],
            'total_size_formatted': format_size(stats['total_size']),
            'total_folders': len(stats['by_folder']),
        },
        'by_extension': dict(stats['by_extension']),
        'by_category': dict(stats['by_category']),
        'folders_with_most_files': stats['folders_with_most_files'],
        'largest_files': [(f, s, format_size(s)) for f, s in stats['largest_files']],
        'recent_files': [(f, m, datetime.fromtimestamp(m).isoformat()) for f, m in stats['recent_files']]
    }
    
    report_path = BASE_DIR / '06_documentation' / 'estadisticas_organizacion.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Reporte guardado en: {report_path}")
    
    return report

if __name__ == '__main__':
    generate_report()















