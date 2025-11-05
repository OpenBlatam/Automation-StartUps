#!/usr/bin/env python3
"""
Comparador de Versiones de Creativos

Compara diferentes versiones de creativos y identifica cambios, mejoras y regresiones.
"""
import sys
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

CSV_MASTER = Path(__file__).parent.parent / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'

def load_csv() -> List[Dict]:
    """Carga el CSV Master"""
    if not CSV_MASTER.exists():
        print(f"❌ CSV Master no encontrado: {CSV_MASTER}")
        return []
    
    with open(CSV_MASTER, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def compare_field(old_value: str, new_value: str) -> Tuple[str, bool]:
    """
    Compara dos valores y retorna (diff_type, is_change)
    diff_type: 'unchanged', 'modified', 'added', 'removed'
    """
    if not old_value and new_value:
        return ('added', True)
    elif old_value and not new_value:
        return ('removed', True)
    elif old_value != new_value:
        return ('modified', True)
    else:
        return ('unchanged', False)

def analyze_performance_changes(creatives: List[Dict]) -> Dict:
    """Analiza cambios en performance"""
    performance_changes = {
        'improved': [],
        'degraded': [],
        'new_with_metrics': [],
        'lost_metrics': []
    }
    
    for creative in creatives:
        utm_content = creative.get('utm_content', '')
        current_ctr = creative.get('ctr', '')
        previous_ctr = creative.get('previous_ctr', '')
        
        # Parse CTR si es posible
        try:
            current = float(current_ctr.replace('%', '')) if current_ctr else None
            previous = float(previous_ctr.replace('%', '')) if previous_ctr else None
            
            if current is not None and previous is not None:
                change = current - previous
                if change > 0.5:  # Mejora significativa
                    performance_changes['improved'].append({
                        'creative': utm_content,
                        'change': f"+{change:.2f}%",
                        'from': f"{previous:.2f}%",
                        'to': f"{current:.2f}%"
                    })
                elif change < -0.5:  # Degradación significativa
                    performance_changes['degraded'].append({
                        'creative': utm_content,
                        'change': f"{change:.2f}%",
                        'from': f"{previous:.2f}%",
                        'to': f"{current:.2f}%"
                    })
            elif current is not None and previous is None:
                performance_changes['new_with_metrics'].append({
                    'creative': utm_content,
                    'ctr': f"{current:.2f}%"
                })
            elif current is None and previous is not None:
                performance_changes['lost_metrics'].append({
                    'creative': utm_content,
                    'previous_ctr': f"{previous:.2f}%"
                })
        except:
            pass
    
    return performance_changes

def compare_creatives(current: List[Dict], previous: List[Dict]) -> Dict:
    """Compara dos versiones de creativos"""
    # Crear índices por utm_content
    current_index = {c.get('utm_content', ''): c for c in current if c.get('utm_content')}
    previous_index = {c.get('utm_content', ''): c for c in previous if c.get('utm_content')}
    
    # Encontrar creativos
    current_ids = set(current_index.keys())
    previous_ids = set(previous_index.keys())
    
    added = current_ids - previous_ids
    removed = previous_ids - current_ids
    common = current_ids & previous_ids
    
    # Analizar cambios en campos
    field_changes = defaultdict(list)
    
    for creative_id in common:
        current_c = current_index[creative_id]
        previous_c = previous_index[creative_id]
        
        # Comparar campos clave
        key_fields = ['format', 'angle', 'cta', 'product', 'utm_source', 'utm_medium']
        
        for field in key_fields:
            old_val = previous_c.get(field, '')
            new_val = current_c.get(field, '')
            
            diff_type, is_change = compare_field(old_val, new_val)
            
            if is_change:
                field_changes[field].append({
                    'creative': creative_id,
                    'from': old_val,
                    'to': new_val,
                    'type': diff_type
                })
    
    return {
        'added': list(added),
        'removed': list(removed),
        'common': list(common),
        'field_changes': dict(field_changes),
        'total_current': len(current),
        'total_previous': len(previous),
        'performance_changes': analyze_performance_changes(current)
    }

def load_backup(backup_name: str) -> Optional[List[Dict]]:
    """Carga una versión de backup"""
    backups_dir = Path(__file__).parent.parent / 'backups'
    
    if not backup_name.endswith('.csv'):
        backup_name += '.csv'
    
    backup_path = backups_dir / backup_name
    
    if not backup_path.exists():
        print(f"❌ Backup no encontrado: {backup_path}")
        return None
    
    with open(backup_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def generate_comparison_report(comparison: Dict, output_file: Path):
    """Genera reporte de comparación en Markdown"""
    report = f"""# Comparación de Versiones de Creativos

**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Resumen

- **Versión actual:** {comparison['total_current']} creativos
- **Versión anterior:** {comparison['total_previous']} creativos
- **Nuevos:** {len(comparison['added'])} creativos
- **Eliminados:** {len(comparison['removed'])} creativos
- **Comunes:** {len(comparison['common'])} creativos

## ➕ Creativos Nuevos

"""
    
    if comparison['added']:
        for creative_id in comparison['added'][:10]:  # Primeros 10
            report += f"- `{creative_id}`\n"
        if len(comparison['added']) > 10:
            report += f"\n*... y {len(comparison['added']) - 10} más*\n"
    else:
        report += "*No hay creativos nuevos*\n"
    
    report += "\n## ➖ Creativos Eliminados\n\n"
    
    if comparison['removed']:
        for creative_id in comparison['removed'][:10]:
            report += f"- `{creative_id}`\n"
        if len(comparison['removed']) > 10:
            report += f"\n*... y {len(comparison['removed']) - 10} más*\n"
    else:
        report += "*No hay creativos eliminados*\n"
    
    report += "\n## 🔄 Cambios en Campos\n\n"
    
    if comparison['field_changes']:
        for field, changes in comparison['field_changes'].items():
            report += f"### {field}\n\n"
            for change in changes[:5]:  # Primeros 5
                report += f"- **{change['creative']}:** `{change['from']}` → `{change['to']}`\n"
            if len(changes) > 5:
                report += f"\n*... y {len(changes) - 5} cambios más*\n"
            report += "\n"
    else:
        report += "*No hay cambios en campos*\n"
    
    report += "\n## 📈 Cambios en Performance\n\n"
    
    perf = comparison['performance_changes']
    
    report += "### ⬆️ Mejoras\n\n"
    if perf['improved']:
        for item in perf['improved'][:5]:
            report += f"- **{item['creative']}:** {item['change']} ({item['from']} → {item['to']})\n"
        if len(perf['improved']) > 5:
            report += f"\n*... y {len(perf['improved']) - 5} mejoras más*\n"
    else:
        report += "*No hay mejoras detectadas*\n"
    
    report += "\n### ⬇️ Degradaciones\n\n"
    if perf['degraded']:
        for item in perf['degraded'][:5]:
            report += f"- **{item['creative']}:** {item['change']} ({item['from']} → {item['to']})\n"
        if len(perf['degraded']) > 5:
            report += f"\n*... y {len(perf['degraded']) - 5} degradaciones más*\n"
    else:
        report += "*No hay degradaciones detectadas*\n"
    
    report += "\n### ✨ Nuevos con Métricas\n\n"
    if perf['new_with_metrics']:
        for item in perf['new_with_metrics'][:5]:
            report += f"- **{item['creative']}:** {item['ctr']}\n"
    else:
        report += "*No hay nuevos creativos con métricas*\n"
    
    output_file.write_text(report, encoding='utf-8')
    print(f"📄 Reporte guardado: {output_file}")

def main():
    print("=" * 80)
    print("🔄 Comparador de Versiones de Creativos")
    print("=" * 80)
    print()
    
    # Cargar versión actual
    current = load_csv()
    
    if not current:
        print("❌ No se pudo cargar el CSV Master")
        return
    
    print(f"✅ Versión actual: {len(current)} creativos")
    
    # Buscar backups disponibles
    backups_dir = Path(__file__).parent.parent / 'backups'
    backups = []
    
    if backups_dir.exists():
        backups = sorted([f.name for f in backups_dir.glob('*.csv')], reverse=True)
    
    if len(sys.argv) > 1:
        backup_name = sys.argv[1]
    else:
        if backups:
            print("\n📦 Backups disponibles:")
            for i, backup in enumerate(backups[:10], 1):
                print(f"  {i}. {backup}")
            
            choice = input("\nSelecciona backup (número o nombre): ").strip()
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(backups):
                    backup_name = backups[idx]
                else:
                    backup_name = choice
            except:
                backup_name = choice
        else:
            print("\n⚠️  No se encontraron backups")
            print("   Crea un backup primero con: python3 tools/backup_restore_system.py create")
            return
    
    # Cargar versión anterior
    previous = load_backup(backup_name)
    
    if not previous:
        return
    
    print(f"✅ Versión anterior: {len(previous)} creativos ({backup_name})")
    
    # Comparar
    print("\n🔄 Comparando versiones...")
    comparison = compare_creatives(current, previous)
    
    # Generar reporte
    reports_dir = Path(__file__).parent.parent / 'reports'
    reports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = reports_dir / f'version_comparison_{timestamp}.md'
    
    generate_comparison_report(comparison, output_file)
    
    # Resumen en consola
    print("\n" + "=" * 80)
    print("📊 Resumen de Comparación")
    print("=" * 80)
    print(f"  ➕ Nuevos: {len(comparison['added'])}")
    print(f"  ➖ Eliminados: {len(comparison['removed'])}")
    print(f"  🔄 Modificados: {sum(len(changes) for changes in comparison['field_changes'].values())}")
    print(f"  ⬆️  Mejoras: {len(comparison['performance_changes']['improved'])}")
    print(f"  ⬇️  Degradaciones: {len(comparison['performance_changes']['degraded'])}")
    print()

if __name__ == '__main__':
    main()

