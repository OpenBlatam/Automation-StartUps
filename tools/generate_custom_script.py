#!/usr/bin/env python3
"""
Generador de Scripts Personalizados
Crea scripts personalizados basados en templates y necesidades específicas
"""
import sys
from pathlib import Path
from datetime import datetime

TEMPLATES = {
    'basic_analysis': {
        'name': 'Análisis Básico Personalizado',
        'description': 'Template para análisis básico de creativos',
        'code': '''#!/usr/bin/env python3
"""
Análisis Básico Personalizado
Generado automáticamente: {timestamp}
"""
import csv
from pathlib import Path

def load_creatives():
    """Carga creativos desde CSV Master"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    csv_path = root_dir / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'
    
    if not csv_path.exists():
        return None
    
    creatives = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            creatives.append(row)
    
    return creatives

def main():
    print("=" * 80)
    print("📊 Análisis Personalizado")
    print("=" * 80)
    print()
    
    creatives = load_creatives()
    if not creatives:
        print("❌ No se encontró CSV Master")
        return
    
    print(f"✅ Analizando {{len(creatives)}} creativos...")
    print()
    
    # Tu lógica personalizada aquí
    # Ejemplo: filtrar por formato
    # filtered = [c for c in creatives if c.get('formato') == '1200x627']
    
    print("✅ Análisis completado")

if __name__ == '__main__':
    main()
'''
    },
    'metric_calculator': {
        'name': 'Calculadora de Métricas Personalizada',
        'description': 'Template para cálculos de métricas personalizadas',
        'code': '''#!/usr/bin/env python3
"""
Calculadora de Métricas Personalizada
Generado automáticamente: {timestamp}
"""
import csv
from pathlib import Path

def load_creatives():
    """Carga creativos desde CSV Master"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    csv_path = root_dir / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'
    
    if not csv_path.exists():
        return None
    
    creatives = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            creatives.append(row)
    
    return creatives

def calculate_custom_metric(creative):
    """Calcula tu métrica personalizada"""
    # Ejemplo: calcula una métrica basada en tus necesidades
    impressions = float(creative.get('impressions', 0) or 0)
    clicks = float(creative.get('clicks', 0) or 0)
    
    if impressions == 0:
        return None
    
    # Tu fórmula personalizada aquí
    custom_metric = (clicks / impressions * 100) if impressions > 0 else 0
    
    return custom_metric

def main():
    print("=" * 80)
    print("📊 Calculadora de Métricas Personalizada")
    print("=" * 80)
    print()
    
    creatives = load_creatives()
    if not creatives:
        print("❌ No se encontró CSV Master")
        return
    
    results = []
    for creative in creatives:
        metric_value = calculate_custom_metric(creative)
        if metric_value is not None:
            results.append({
                'creative': creative.get('creative_file', ''),
                'metric': metric_value
            })
    
    print(f"✅ Calculadas métricas para {{len(results)}} creativos")
    
    # Mostrar resultados
    for result in results[:10]:
        print(f"  {{result['creative']}}: {{result['metric']:.2f}}")

if __name__ == '__main__':
    main()
'''
    },
    'data_export': {
        'name': 'Exportador de Datos Personalizado',
        'description': 'Template para exportar datos en formatos personalizados',
        'code': '''#!/usr/bin/env python3
"""
Exportador de Datos Personalizado
Generado automáticamente: {timestamp}
"""
import csv
import json
from pathlib import Path
from datetime import datetime

def load_creatives():
    """Carga creativos desde CSV Master"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    csv_path = root_dir / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'
    
    if not csv_path.exists():
        return None
    
    creatives = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            creatives.append(row)
    
    return creatives

def export_data(creatives, format_type='json'):
    """Exporta datos en formato personalizado"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    exports_dir = root_dir / 'exports'
    exports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format_type == 'json':
        output_path = exports_dir / f'custom_export_{{timestamp}}.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(creatives, f, indent=2, ensure_ascii=False)
    elif format_type == 'csv':
        output_path = exports_dir / f'custom_export_{{timestamp}}.csv'
        if creatives:
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=creatives[0].keys())
                writer.writeheader()
                writer.writerows(creatives)
    
    return output_path

def main():
    print("=" * 80)
    print("📤 Exportador de Datos Personalizado")
    print("=" * 80)
    print()
    
    creatives = load_creatives()
    if not creatives:
        print("❌ No se encontró CSV Master")
        return
    
    # Filtrar o procesar según necesites
    # filtered_creatives = [c for c in creatives if condition]
    
    # Exportar
    output_path = export_data(creatives, format_type='json')
    print(f"✅ Datos exportados: {{output_path}}")

if __name__ == '__main__':
    main()
'''
    }
}

def list_templates():
    """Lista templates disponibles"""
    print("=" * 80)
    print("📋 Templates Disponibles")
    print("=" * 80)
    print()
    
    for i, (template_id, template) in enumerate(TEMPLATES.items(), 1):
        print(f"{i}. {template['name']}")
        print(f"   ID: {template_id}")
        print(f"   {template['description']}")
        print()

def generate_script(template_id, output_name=None):
    """Genera script desde template"""
    if template_id not in TEMPLATES:
        print(f"❌ Template '{template_id}' no encontrado")
        return False
    
    template = TEMPLATES[template_id]
    
    if not output_name:
        output_name = f"custom_{template_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    script_dir = Path(__file__).parent
    output_path = script_dir / output_name
    
    if output_path.exists():
        response = input(f"⚠️  {output_name} ya existe. ¿Sobrescribir? (s/n): ")
        if response.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
            print("❌ Cancelado")
            return False
    
    # Generar código
    code = template['code'].format(timestamp=datetime.now().isoformat())
    
    # Guardar
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(code)
    
    # Hacer ejecutable
    import os
    os.chmod(output_path, 0o755)
    
    print(f"✅ Script generado: {output_path}")
    print()
    print("💡 Próximos pasos:")
    print(f"   1. Edita {output_name} para personalizar")
    print(f"   2. Ejecuta: python3 tools/{output_name}")
    print()
    
    return True

def main():
    print("=" * 80)
    print("🔧 Generador de Scripts Personalizados")
    print("=" * 80)
    print()
    
    if len(sys.argv) < 2:
        list_templates()
        print()
        print("Uso:")
        print("  python3 generate_custom_script.py list")
        print("  python3 generate_custom_script.py <template_id> [output_name]")
        print()
        return
    
    command = sys.argv[1]
    
    if command == 'list':
        list_templates()
    
    elif command in TEMPLATES:
        output_name = sys.argv[2] if len(sys.argv) > 2 else None
        generate_script(command, output_name)
    
    else:
        print(f"❌ Template desconocido: {command}")
        print()
        list_templates()

if __name__ == '__main__':
    main()

