#!/usr/bin/env python3
"""
Script rápido para obtener estadísticas del proyecto
"""
import os
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).parent.parent.parent

def quick_stats():
    """Genera estadísticas rápidas"""
    stats = {
        'files': 0,
        'folders': 0,
        'size': 0,
        'extensions': Counter(),
        'by_category': Counter()
    }
    
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
        '09_sales': 'Sales',
        '10_customer_service': 'Customer Service',
        '11_research_development': 'R&D',
        '11_system_architecture': 'System Architecture',
        '12_quality_assurance': 'QA',
        '13_legal_compliance': 'Legal/Compliance',
        '14_product_management': 'Product Management',
        '15_customer_experience': 'Customer Experience',
        '16_data_analytics': 'Analytics',
        '17_innovation': 'Innovation',
    }
    
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        stats['folders'] += len(dirs)
        
        for file in files:
            if file.startswith('.'):
                continue
            
            file_path = Path(root) / file
            try:
                size = file_path.stat().st_size
                stats['files'] += 1
                stats['size'] += size
                stats['extensions'][file_path.suffix.lower() or '(sin ext)'] += 1
                
                # Categoría
                rel_path = file_path.relative_to(BASE_DIR)
                folder_parts = str(rel_path).split('/')
                if folder_parts and folder_parts[0] in category_map:
                    stats['by_category'][category_map[folder_parts[0]]] += 1
            except:
                pass
    
    return stats

def format_size(size_bytes):
    """Formatea tamaño"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

if __name__ == '__main__':
    stats = quick_stats()
    
    print("📊 ESTADÍSTICAS RÁPIDAS")
    print("=" * 50)
    print(f"Archivos: {stats['files']:,}")
    print(f"Carpetas: {stats['folders']:,}")
    print(f"Tamaño: {format_size(stats['size'])}")
    print(f"\nTop 5 extensiones:")
    for ext, count in stats['extensions'].most_common(5):
        print(f"  {ext:15s}: {count:,}")
    print(f"\nTop 5 categorías:")
    for cat, count in stats['by_category'].most_common(5):
        print(f"  {cat:25s}: {count:,}")








